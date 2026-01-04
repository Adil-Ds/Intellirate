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
from app.models.user_rate_limit_config import UserRateLimitConfig

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
    - Traffic spikes (tier-aware thresholds)
    - Rate limit breaches  
    - Unusual latency patterns
    - Error rate anomalies
    """
    try:
        current_time = datetime.now(timezone.utc)
        
        # Analyze last 24 hours of data
        cutoff_time = current_time - timedelta(hours=24)
        
        # Define tier-based thresholds
        TIER_THRESHOLDS = {
            'free': {
                'daily_limit': 50,
                'anomaly_at_requests': 40,      # Trigger anomaly at 40 requests (80% of limit)
                'hourly_threshold': 40 / 24,    # 1.67 requests/hour
            },
            'pro': {
                'daily_limit': 1000,
                'anomaly_at_requests': 800,     # Trigger at 80% of limit
                'hourly_threshold': 800 / 24,   # 33.33 requests/hour
            },
            'enterprise': {
                'daily_limit': None,            # Unlimited
                'anomaly_at_requests': None,    # No traffic spike detection
                'hourly_threshold': None,
            }
        }
        
        # Get user statistics with tier info
        user_stats = db.query(
            RequestLog.user_id,
            RequestLog.user_email,
            func.count(RequestLog.id).label('request_count'),
            func.avg(RequestLog.latency_ms).label('avg_latency'),
            func.max(RequestLog.timestamp).label('last_request'),
            UserRateLimitConfig.tier,
            UserRateLimitConfig.custom_limit
        ).outerjoin(
            UserRateLimitConfig, 
            RequestLog.user_id == UserRateLimitConfig.user_id
        ).filter(
            RequestLog.timestamp >= cutoff_time
        ).group_by(
            RequestLog.user_id,
            RequestLog.user_email,
            UserRateLimitConfig.tier,
            UserRateLimitConfig.custom_limit
        ).all()
        
        anomalies = []
        
        for user in user_stats:
            # Determine user tier (default to 'free' if not set)
            user_tier = user.tier or 'free'
            tier_config = TIER_THRESHOLDS.get(user_tier, TIER_THRESHOLDS['free'])
            
            request_count = user.request_count
            avg_latency = user.avg_latency or 0
            last_request = user.last_request
            
            # Calculate requests per hour
            time_diff = (current_time - cutoff_time).total_seconds() / 3600
            requests_per_hour = request_count / time_diff if time_diff > 0 else 0
            
            # Calculate error count separately
            error_count = db.query(func.count(RequestLog.id)).filter(
                RequestLog.user_id == user.user_id,
                RequestLog.timestamp >= cutoff_time,
                RequestLog.success == False
            ).scalar() or 0
            
            # Calculate error rate
            error_rate = (error_count / request_count * 100) if request_count > 0 else 0
            
            # TIER-AWARE TRAFFIC SPIKE DETECTION
            # Skip traffic spike detection for Enterprise users (unlimited)
            if tier_config['hourly_threshold'] is not None:
                hourly_threshold = tier_config['hourly_threshold']
                
                if requests_per_hour > hourly_threshold:
                    # Calculate severity based on how much they exceeded
                    daily_limit = tier_config['daily_limit']
                    daily_equivalent = requests_per_hour * 24
                    
                    # High severity if 50% over anomaly threshold
                    if daily_equivalent > (tier_config['anomaly_at_requests'] * 1.5):
                        severity = "High"
                    else:
                        severity = "Medium"
                    
                    # Calculate percentage over limit
                    percentage_over = ((daily_equivalent - daily_limit) / daily_limit) * 100
                    
                    time_ago = get_time_ago(last_request) if last_request else "Unknown"
                    anomalies.append({
                        "id": f"traffic_{user.user_id[:8]}",
                        "type": "Traffic Spike",
                        "severity": severity,
                        "description": f"Unusual traffic from {user.user_email or user.user_id[:8]} ({user_tier.upper()} tier)",
                        "timestamp": time_ago,
                        "impact": f"+{int(percentage_over)}% over {user_tier.upper()} tier limit ({daily_limit}/day)",
                        "user_id": user.user_id,
                        "details": {
                            "tier": user_tier,
                            "requests_per_hour": round(requests_per_hour, 2),
                            "total_requests_24h": request_count,
                            "tier_daily_limit": daily_limit,
                            "anomaly_threshold": tier_config['anomaly_at_requests'],
                            "projected_daily": int(daily_equivalent),
                            "hourly_threshold": round(hourly_threshold, 2)
                        }
                    })
            
            # Detect high error rate (>20%) - same for all tiers
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
                        "error_count": error_count,
                        "total_requests": request_count
                    }
                })
            
            # Detect latency anomaly (>5000ms average) - same for all tiers
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
