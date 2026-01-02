"""
Request/Response Logging Service
Captures all traffic for analytics
"""
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.request_log import RequestLog
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


class LoggingService:
    """Service for logging all API requests and responses"""
    
    @staticmethod
    def log_request(
        user_id: str,
        user_email: Optional[str],
        request_body: dict,
        ip_address: str,
        user_agent: str,
        endpoint: str = "/api/v1/analyze"
    ) -> str:
        """
        Log incoming request to database
        
        Args:
            user_id: Firebase user ID
            user_email: User email address
            request_body: Groq API request body
            ip_address: Client IP address
            user_agent: Client user agent
            endpoint: API endpoint
            
        Returns:
            str: Unique request ID
        """
        request_id = str(uuid.uuid4())
        
        try:
            db = SessionLocal()
            
            # Extract request parameters
            model = request_body.get("model", "")
            temperature = request_body.get("temperature")
            max_tokens = request_body.get("max_tokens")
            messages = request_body.get("messages", [])
            message_count = len(messages)
            
            # Create log entry
            log_entry = RequestLog(
                request_id=request_id,
                user_id=user_id,
                user_email=user_email,
                timestamp=datetime.utcnow(),
                endpoint=endpoint,
                method="POST",
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                message_count=message_count,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.add(log_entry)
            db.commit()
            
            logger.info(f"✓ Request logged: {request_id} - User: {user_id}")
            
            db.close()
            return request_id
        
        except Exception as e:
            logger.error(f"Failed to log request: {str(e)}")
            # Return request ID even if logging fails (don't block the request)
            return request_id
    
    @staticmethod
    def log_response(
        request_id: str,
        status_code: int,
        success: bool,
        response_data: Optional[dict] = None,
        error: Optional[str] = None,
        latency_ms: int = 0,
        groq_latency_ms: int = 0
    ) -> None:
        """
        Update request log with response data
        
        Args:
            request_id: Unique request ID
            status_code: HTTP status code
            success: Whether request was successful
            response_data: Groq API response (if successful)
            error: Error message (if failed)
            latency_ms: Total request latency
            groq_latency_ms: Groq API latency
        """
        try:
            db = SessionLocal()
            
            # Find the request log entry
            log_entry = db.query(RequestLog).filter(
                RequestLog.request_id == request_id
            ).first()
            
            if not log_entry:
                logger.warning(f"Request log not found for ID: {request_id}")
                db.close()
                return
            
            # Update with response data
            log_entry.status_code = status_code
            log_entry.success = success
            log_entry.error = error
            log_entry.latency_ms = latency_ms
            log_entry.groq_latency_ms = groq_latency_ms
            log_entry.completed_at = datetime.utcnow()
            
            # Extract token usage if successful
            if success and response_data:
                usage = response_data.get("usage", {})
                log_entry.prompt_tokens = usage.get("prompt_tokens", 0)
                log_entry.completion_tokens = usage.get("completion_tokens", 0)
                log_entry.total_tokens = usage.get("total_tokens", 0)
            
            db.commit()
            
            logger.info(f"✓ Response logged: {request_id} - Status: {status_code}, Tokens: {log_entry.total_tokens}")
            
            db.close()
        
        except Exception as e:
            logger.error(f"Failed to log response: {str(e)}")
            # Don't raise exception - logging failures shouldn't affect the response
    
    @staticmethod
    def get_user_analytics(user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get analytics for a specific user
        
        Args:
            user_id: Firebase user ID
            days: Number of days to look back
            
        Returns:
            dict: User analytics
        """
        try:
            db = SessionLocal()
            
            # Query user's requests
            from sqlalchemy import func
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            stats = db.query(
                func.count(RequestLog.id).label('total_requests'),
                func.sum(RequestLog.total_tokens).label('total_tokens'),
                func.avg(RequestLog.latency_ms).label('avg_latency'),
                func.sum(func.cast(RequestLog.success, db.Integer)).label('successful_requests'),
                func.max(RequestLog.timestamp).label('last_request')
            ).filter(
                RequestLog.user_id == user_id,
                RequestLog.timestamp >= cutoff_date
            ).first()
            
            total_requests = stats.total_requests or 0
            successful_requests = stats.successful_requests or 0
            
            db.close()
            
            return {
                "user_id": user_id,
                "total_requests": total_requests,
                "total_tokens": int(stats.total_tokens or 0),
                "avg_latency_ms": round(float(stats.avg_latency or 0), 2),
                "success_rate": round(successful_requests / total_requests, 4) if total_requests > 0 else 0,
                "last_request": stats.last_request.isoformat() if stats.last_request else None,
                "period_days": days
            }
        
        except Exception as e:
            logger.error(f"Failed to get user analytics: {str(e)}")
            return {
                "user_id": user_id,
                "error": str(e)
            }
    
    @staticmethod
    def get_system_analytics(days: int = 30) -> Dict[str, Any]:
        """
        Get system-wide analytics
        
        Args:
            days: Number of days to look back
            
        Returns:
            dict: System analytics
        """
        try:
            db = SessionLocal()
            
            from sqlalchemy import func, distinct
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            stats = db.query(
                func.count(RequestLog.id).label('total_requests'),
                func.sum(RequestLog.total_tokens).label('total_tokens'),
                func.count(distinct(RequestLog.user_id)).label('unique_users'),
                func.avg(RequestLog.total_tokens).label('avg_tokens_per_request')
            ).filter(
                RequestLog.timestamp >= cutoff_date
            ).first()
            
            db.close()
            
            return {
                "period": f"last_{days}_days",
                "total_requests": stats.total_requests or 0,
                "total_tokens": int(stats.total_tokens or 0),
                "unique_users": stats.unique_users or 0,
                "avg_tokens_per_request": round(float(stats.avg_tokens_per_request or 0), 2)
            }
        
        except Exception as e:
            logger.error(f"Failed to get system analytics: {str(e)}")
            return {
                "period": f"last_{days}_days",
                "error": str(e)
            }


# Global instance
logging_service = LoggingService()
