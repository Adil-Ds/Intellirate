"""
User Statistics API Endpoints
Provide real-time user data for the Users panel
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.models.request_log import RequestLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/stats")
async def get_user_stats(db: Session = Depends(get_db)):
    """
    Get statistics for all users who have made requests
    
    Returns user_id, API key (masked), request rate, status, and activity metrics
    """
    try:
        # Get all unique users with their stats
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Query for user statistics
        user_stats = db.query(
            RequestLog.user_id,
            RequestLog.user_email,
            func.count(RequestLog.id).label('total_requests'),
            func.avg(RequestLog.latency_ms).label('avg_latency'),
            func.max(RequestLog.timestamp).label('last_active'),
            func.count(func.distinct(func.date_trunc('hour', RequestLog.timestamp))).label('active_hours')
        ).group_by(
            RequestLog.user_id,
            RequestLog.user_email
        ).all()
        
        users = []
        for user in user_stats:
            # Calculate metrics
            total_requests = user.total_requests
            last_active = user.last_active
            
            # Calculate request rate (RPM) based on activity
            time_span_hours = max(1, user.active_hours or 1)
            requests_per_hour = total_requests / time_span_hours
            rpm = round(requests_per_hour / 60, 1) if requests_per_hour > 0 else 0
            
            # Determine status based on last activity
            if last_active:
                # Make current time timezone-aware to match last_active
                from datetime import timezone
                current_time = datetime.now(timezone.utc)
                time_diff = (current_time - last_active).total_seconds()
                
                if time_diff < 300:  # Active within 5 minutes
                    status = "NORMAL"
                    is_online = True
                elif time_diff < 3600:  # Within 1 hour
                    status = "NORMAL"
                    is_online = False
                else:
                    status = "NORMAL"
                    is_online = False
            else:
                status = "NORMAL"
                is_online = False
            
            # Determine risk level based on request rate
            if rpm > 200:
                status = "RISKY"
            elif rpm > 100:
                status = "RISKY"
            
            # Mock anomaly score (0-100) - in production would come from ML model
            # For now, base it on request rate
            anomaly_score = min(100, int((rpm / 500) * 100)) if rpm > 0 else 0
            
            # Mask API key (show first 8 chars + ...)
            api_key_display = f"pk_live_{user.user_id[:8]}..." if user.user_id else "N/A"
            
            users.append({
                "user_id": user.user_id,
                "user_name": user.user_email or f"User {user.user_id[:8]}",
                "api_key": api_key_display,
                "request_rate": rpm,
                "status": status,
                "is_online": is_online,
                "anomaly_score": anomaly_score,
                "total_requests": total_requests,
                "avg_latency": round(user.avg_latency, 2) if user.avg_latency else 0,
                "last_active": last_active.isoformat() if last_active else None
            })
        
        return {
            "users": users,
            "total_users": len(users)
        }
    
    except Exception as e:
        logger.error(f"Error fetching user stats: {str(e)}")
        return {
            "users": [],
            "total_users": 0,
            "error": str(e)
        }
