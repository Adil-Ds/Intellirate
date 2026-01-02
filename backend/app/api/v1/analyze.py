"""
Groq API Analyze Endpoint
Main gateway endpoint that proxies requests to Groq API
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends
from typing import Dict
import logging
import time

from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse, ErrorResponse
from app.middleware.firebase_auth import FirebaseAuthMiddleware
from app.middleware.rate_limiter import RateLimiter
from app.services.groq_service import groq_service, GroqAPIError
from app.services.logging_service import logging_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["AI Analysis"])


async def get_current_user(request: Request) -> dict:
    """Dependency to get authenticated user"""
    return await FirebaseAuthMiddleware.verify_token(request)


@router.post("", response_model=AnalyzeResponse, responses={
    401: {"model": ErrorResponse, "description": "Unauthorized"},
    403: {"model": ErrorResponse, "description": "Forbidden"},
    429: {"model": ErrorResponse, "description": "Rate Limit Exceeded"},
    502: {"model": ErrorResponse, "description": "Bad Gateway"},
    504: {"model": ErrorResponse, "description": "Gateway Timeout"}
})
async def analyze(
    request: Request,
    body: AnalyzeRequest,
    user: dict = Depends(get_current_user)
):
    """
    Analyze endpoint - Proxy to Groq API with authentication and logging
    
    This endpoint:
    1. Validates Firebase authentication
    2. Checks rate limits
    3. Logs the request
    4. Proxies to Groq API
    5. Logs the response
    6. Returns Groq's response
    
    **Authentication Required:**
    - Authorization: Bearer <firebase-token>
    - X-User-Id: <firebase-uid>
    - X-User-Email: <user-email>
    """
    start_time = time.time()
    request_id = None
    
    try:
        # Get user info
        user_id = user["uid"]
        user_email = user["email"]
        user_tier = FirebaseAuthMiddleware.get_user_tier(user)
        
        # Check rate limits
        await RateLimiter.check_rate_limit(user_id, user_tier)
        
        # Get client metadata
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log request
        request_id = logging_service.log_request(
            user_id=user_id,
            user_email=user_email,
            request_body=body.model_dump(),
            ip_address=client_ip,
            user_agent=user_agent,
            endpoint="/api/v1/analyze"
        )
        
        logger.info(f"Processing request {request_id} for user {user_id}")
        
        # Proxy to Groq API
        response_data, status_code, groq_latency = await groq_service.proxy_to_groq(
            body.model_dump()
        )
        
        # Calculate total latency
        total_latency = int((time.time() - start_time) * 1000)
        
        # Log successful response
        logging_service.log_response(
            request_id=request_id,
            status_code=status_code,
            success=True,
            response_data=response_data,
            latency_ms=total_latency,
            groq_latency_ms=groq_latency
        )
        
        logger.info(f"✓ Request {request_id} completed successfully - {total_latency}ms")
        
        # Return Groq response
        return response_data
    
    except GroqAPIError as e:
        # Groq API specific errors
        total_latency = int((time.time() - start_time) * 1000)
        
        if request_id:
            logging_service.log_response(
                request_id=request_id,
                status_code=e.status_code,
                success=False,
                error=e.message,
                latency_ms=total_latency
            )
        
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error": e.message,
                "code": "UPSTREAM_ERROR"
            }
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (auth, rate limit, etc.)
        raise
    
    except Exception as e:
        # Unexpected errors
        total_latency = int((time.time() - start_time) * 1000)
        
        if request_id:
            logging_service.log_response(
                request_id=request_id,
                status_code=500,
                success=False,
                error=str(e),
                latency_ms=total_latency
            )
        
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "code": "INTERNAL_ERROR"
            }
        )
