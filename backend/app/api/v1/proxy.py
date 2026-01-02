"""
Groq Proxy API Endpoint
Routes Analyzer traffic through IntelliRate for traffic capture and rate limiting
"""
from fastapi import APIRouter, HTTPException, Header, Request, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import time
import logging

from app.core.database import get_db
from app.models.request_log import RequestLog
from app.services.groq_service import groq_service, GroqAPIError
from app.schemas.analyze import AnalyzeRequest
from app.middleware.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/proxy", tags=["Proxy"])


@router.post("/groq")
async def proxy_groq_request(
    request_body: dict,
    request: Request,
    x_user_id: str = Header(None, alias="X-User-ID"),
    db: Session = Depends(get_db)
):
    """
    Proxy endpoint for Groq API requests
    
    This endpoint:
    1. Validates user ID
    2. Checks rate limits (ENFORCED!)
    3. Captures incoming request metadata
    4. Logs to database (start time)
    5. Proxies request to Groq API
    6. Updates log with response data
    7. Returns Groq response to caller
    
    Headers:
    - X-User-ID: User identifier (required)
    - Authorization: Firebase token (optional, for future auth)
    """
    start_time = time.time()
    
    # Validate user ID
    if not x_user_id:
        raise HTTPException(
            status_code=400,
            detail="X-User-ID header is required"
        )
    
    # ✅ ENFORCE RATE LIMITING
    try:
        # Determine user tier based on recent activity
        from app.api.v1.rate_limits import determine_user_tier
        from datetime import timedelta, timezone
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        user_request_count = db.query(RequestLog).filter(
            RequestLog.user_id == x_user_id,
            RequestLog.timestamp >= cutoff
        ).count()
        
        user_tier = determine_user_tier(user_request_count)
        
        # Check rate limit (passes db for custom limit lookup)
        await RateLimiter.check_rate_limit(x_user_id, user_tier, db)
        logger.info(f"✓ Rate limit check passed for user {x_user_id}")
    except HTTPException:
        # Re-raise rate limit exceeded errors
        raise
    except Exception as e:
        logger.warning(f"Rate limit check encountered error (allowing request): {str(e)}")
    
    # Create initial log entry
    log_entry = None
    db_available = True
    
    try:
        log_entry = RequestLog(
            user_id=x_user_id,
            endpoint="/proxy/groq",
            method="POST",
            model=request_body.get("model"),
            temperature=request_body.get("temperature"),
            max_tokens=request_body.get("max_tokens"),
            message_count=len(request_body.get("messages", [])),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        # Save initial log
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        logger.info(f"✓ Logged request to database for user {x_user_id}")
    except Exception as db_error:
        logger.warning(f"Database unavailable, proceeding without logging: {str(db_error)}")
        db_available = False
    
    # Proxy to Groq (MUST be outside the except block!)
    try:
        logger.info(f"Proxying request for user {x_user_id} to Groq API")
        response_data, status_code, groq_latency = await groq_service.proxy_to_groq(request_body)
        
        # Calculate total latency
        total_latency = int((time.time() - start_time) * 1000)
        
        # Extract token usage from response
        usage = response_data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        
        # Update log entry with success data (if database is available)
        if db_available and log_entry:
            try:
                log_entry.completed_at = datetime.utcnow()
                log_entry.status_code = status_code
                log_entry.success = True
                log_entry.prompt_tokens = prompt_tokens
                log_entry.completion_tokens = completion_tokens
                log_entry.total_tokens = total_tokens
                log_entry.latency_ms = total_latency
                log_entry.groq_latency_ms = groq_latency
                db.commit()
                logger.info(f"✓ Updated database log for user {x_user_id}")
            except Exception as db_error:
                logger.warning(f"Failed to update database: {str(db_error)}")
        
        logger.info(f"✓ Request completed for user {x_user_id} - {total_latency}ms, {total_tokens} tokens")
        
        # Return Groq response
        return response_data
    
    except GroqAPIError as e:
        # Update log with error (if database is available)
        if db_available and log_entry:
            try:
                log_entry.completed_at = datetime.utcnow()
                log_entry.status_code = e.groq_status or e.status_code
                log_entry.success = False
                log_entry.error = str(e)
                log_entry.latency_ms = int((time.time() - start_time) * 1000)
                db.commit()
            except Exception:
                pass  # Ignore database errors
        
        logger.error(f"Groq API error for user {x_user_id}: {str(e)}")
        raise HTTPException(
            status_code=e.status_code,
            detail=str(e)
        )
    
    except Exception as e:
        # Update log with unexpected error (if database is available)
        if db_available and log_entry:
            try:
                log_entry.completed_at = datetime.utcnow()
                log_entry.status_code = 500
                log_entry.success = False
                log_entry.error = str(e)
                log_entry.latency_ms = int((time.time() - start_time) * 1000)
                db.commit()
            except Exception:
                pass  # Ignore database errors
        
        logger.error(f"Unexpected error for user {x_user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
