"""
Anomaly Detection API Endpoints
Detect unusual patterns in API usage
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta, timezone
import logging

from app.core.database import get_db
from app.models.request_log import RequestLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])


@router.get("/stats")
async def get_anomaly_stats(db: Session = Depends(get_db)):
    """
    Get overall anomaly detection statistics
    """
    try:
        # For now, return hardcoded stats
        # In production, this would come from ML model predictions
        return {
            "active_anomalies": 0,
            "resolved_today": 0,
            "avg_response_time": "0ms"
        }
    except Exception as e:
        logger.error(f"Error fetching anomaly stats: {str(e)}")
        return {
            "active_anomalies": 0,
            "resolved_today": 0,
            "avg_response_time": "0ms  "
        }


@router.get("")
async def get_anomalies(
    limit: int = Query(50, description="Maximum number of anomalies to return"),
    db: Session = Depends(get_db)
):
    """
    Get detected anomalies based on request patterns
    
    Returns anomalies detected from:
    - Traffic spikes
    - Rate limit breaches  
    - Unusual latency patterns
    - Error rate anomalies
    """
    try:
        current_time = datetime.now(timezone.utc)
        
        # Analyze last 24 hours of data
        cutoff_time = current_time - timedelta(hours=24)
        
        # Get user statistics
        user_stats = db.query(
            RequestLog.user_id,
            RequestLog.user_email,
            func.count(RequestLog.id).label('request_count'),
            func.avg(RequestLog.latency_ms).label('avg_latency'),
            func.max(RequestLog.timestamp).label('last_request')
        ).filter(
            RequestLog.timestamp >= cutoff_time
        ).group_by(
            RequestLog.user_id,
            RequestLog.user_email
        ).all()
        
        anomalies = []
        
        for user in user_stats:
            request_count = user.request_count
            avg_latency = user.avg_latency or 0
            last_request = user.last_request
            
            # Calculate error count separately
            error_count = db.query(func.count(RequestLog.id)).filter(
                RequestLog.user_id == user.user_id,
                RequestLog.timestamp >= cutoff_time,
                RequestLog.success == False
            ).scalar() or 0
            
            # Calculate request rate (requests per hour)
            time_diff = (current_time - cutoff_time).total_seconds() / 3600
            requests_per_hour = request_count / time_diff if time_diff > 0 else 0
            
            # Calculate error rate
            error_rate = (error_count / request_count * 100) if request_count > 0 else 0
            
            # Detect traffic spike (>10 requests/hour for testing)
            if requests_per_hour > 10:
                time_ago = get_time_ago(last_request) if last_request else "Unknown"
                anomalies.append({
                    "id": f"traffic_{user.user_id[:8]}",
                    "type": "Traffic Spike",
                    "severity": "High" if requests_per_hour > 20 else "Medium",
                    "description": f"Unusual traffic from user {user.user_email or user.user_id[:8]}",
                    "timestamp": time_ago,
                    "impact": f"+{int((requests_per_hour / 50 - 1) * 100)}% above baseline",
                    "user_id": user.user_id,
                    "details": {
                        "requests_per_hour": round(requests_per_hour, 1),
                        "total_requests": request_count
                    }
                })
            
            # Detect high error rate (>20%)
            if error_rate > 20 and error_count > 5:
                time_ago = get_time_ago(last_request) if last_request else "Unknown"
                anomalies.append({
                    "id": f"error_{user.user_id[:8]}",
                    "type": "High Error Rate",
                    "severity": "High" if error_rate > 50 else "Medium",
                    "description": f"Elevated error rate for user {user.user_email or user.user_id[:8]}",
                    "timestamp": time_ago,
                    "impact": f"{int(error_rate)}% error rate ({error_count} errors)",
                    "user_id": user.user_id,
                    "details": {
                        "error_rate": round(error_rate, 1),
                        "error_count": error_count
                    }
                })
            
            # Detect latency anomaly (>5000ms average)
            if avg_latency > 5000:
                time_ago = get_time_ago(last_request) if last_request else "Unknown"
                anomalies.append({
                    "id": f"latency_{user.user_id[:8]}",
                    "type": "Latency Anomaly",
                    "severity": "Medium" if avg_latency < 10000 else "High",
                    "description": f"High response time for user {user.user_email or user.user_id[:8]}",
                    "timestamp": time_ago,
                    "impact": f"Average {int(avg_latency)}ms",
                    "user_id": user.user_id,
                    "details": {
                        "avg_latency": round(avg_latency, 1)
                    }
                })
        
        # Sort by severity (High > Medium > Low) and limit results
        severity_order = {"High": 0, "Medium": 1, "Low": 2}
        anomalies.sort(key=lambda x: severity_order.get(x["severity"], 3))
        
        return {
            "anomalies": anomalies[:limit],
            "total_count": len(anomalies),
            "last_updated": current_time.isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        return {
            "anomalies": [],
            "total_count": 0,
            "error": str(e)
        }


def get_time_ago(timestamp):
    """Convert timestamp to relative time string"""
    if not timestamp:
        return "Unknown"
    
    current_time = datetime.now(timezone.utc)
    diff = (current_time - timestamp).total_seconds()
    
    if diff < 60:
        return f"{int(diff)} secs ago"
    elif diff < 3600:
        return f"{int(diff / 60)} mins ago"
    elif diff < 86400:
        return f"{int(diff / 3600)} hours ago"
    else:
        return f"{int(diff / 86400)} days ago"
