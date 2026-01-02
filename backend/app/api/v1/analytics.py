"""
Analytics API Endpoints
Query usage statistics and metrics
"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import logging

from app.core.database import get_db
from app.models.request_log import RequestLog
from app.models.user_rate_limit_config import UserRateLimitConfig
from app.schemas.analytics import UserAnalytics, SystemAnalytics, RateLimitQuota
from app.services.logging_service import logging_service
from app.middleware.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/user/{user_id}", response_model=UserAnalytics)
async def get_user_analytics(
    user_id: str,
    days: int = Query(30, description="Number of days to look back", ge=1, le=365)
):
    """
    Get usage analytics for a specific user
    
    Returns:
    - Total requests
    - Total tokens consumed
    - Average latency
    - Success rate
    - Last request timestamp
    """
    try:
        analytics = logging_service.get_user_analytics(user_id, days)
        
        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch analytics: {analytics['error']}"
            )
        
        return analytics
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user analytics"
        )


@router.get("/usage", response_model=SystemAnalytics)
async def get_system_usage(
    days: int = Query(30, description="Number of days to look back", ge=1, le=365)
):
    """
    Get system-wide usage statistics
    
    Returns:
    - Total requests
    - Total tokens consumed
    - Unique users
    - Average tokens per request
    """
    try:
        analytics = logging_service.get_system_analytics(days)
        
        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch analytics: {analytics['error']}"
            )
        
        return analytics
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching system analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch system analytics"
        )


@router.get("/quota/{user_id}", response_model=RateLimitQuota)
async def get_rate_limit_quota(
    user_id: str,
    tier: str = Query("free", description="User tier (free/pro/enterprise)")
):
    """
    Get current rate limit quota for a user
    
    Returns:
    - Total limit
    - Used requests
    - Remaining requests
    - Window duration
    - User tier
    """
    try:
        if tier not in ["free", "pro", "enterprise"]:
            tier = "free"
        
        quota = await RateLimiter.get_remaining_quota(user_id, tier)
        return quota
    
    except Exception as e:
        logger.error(f"Error fetching quota: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch rate limit quota"
        )


@router.get("/ml-insights-summary")
async def get_ml_insights_summary(db: Session = Depends(get_db)):
    """
    Get ML insights summary for dashboard
    
    Returns:
    - Pending recommendations count
    - Applied recommendations count  
    - Total savings estimate
    - Average confidence
    """
    try:
        # Count custom configs (applied recommendations)
        applied_count = db.query(UserRateLimitConfig).count()
        
        # Count users with recent activity (potential for recommendations)
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        total_active_users = db.query(func.count(func.distinct(RequestLog.user_id))).filter(
            RequestLog.timestamp >= cutoff
        ).scalar() or 0
        
        # Pending = active users without custom config
        pending_count = max(0, total_active_users - applied_count)
        
        # Estimate savings (assume $0.05 saved per optimized user per month)
        total_savings = applied_count * 0.05
        
        return {
            "pending_recommendations": pending_count,
            "applied_recommendations": applied_count,
            "total_savings_usd": round(total_savings, 2),
            "avg_confidence": 0.85 if applied_count > 0 else 0.0
        }
    
    except Exception as e:
        logger.error(f"Error fetching ML insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch ML insights: {str(e)}"
        )


@router.get("/activity-feed")
async def get_activity_feed(
    limit: int = Query(10, description="Number of events to return", ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get recent activity feed for dashboard
    
    Returns list of recent events with:
    - Timestamp
    - Event type (request, error, rate_limit, etc.)
    - Severity (success, warning, danger)
    - Description
    - User ID
    """
    try:
        # Get recent logs
        recent_logs = db.query(RequestLog).order_by(desc(RequestLog.timestamp)).limit(limit).all()
        
        events = []
        for log in recent_logs:
            # Determine event type and severity
            if log.endpoint and "rate-limits" in log.endpoint:
                event_type = "rate_limit_update"
                severity = "info"
                description = f"Rate limit updated for user"
            elif not log.success:
                event_type = "error"
                severity = "danger"
                description = f"Request failed: {log.error[:50] if log.error else 'Unknown error'}"
            elif log.latency_ms and log.latency_ms > 1000:
                event_type = "high_latency"
                severity = "warning"
                description = f"High latency detected: {log.latency_ms}ms"
            else:
                event_type = "request"
                severity = "success"
                description = f"Request completed successfully"
            
            events.append({
                "id": log.id,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "type": event_type,
                "severity": severity,
                "description": description,
                "user_id": log.user_id,
                "metadata": {
                    "endpoint": log.endpoint,
                    "method": log.method,
                    "status_code": log.status_code
                }
            })
        
        return events
    
    except Exception as e:
        logger.error(f"Error fetching activity feed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch activity feed: {str(e)}"
        )


@router.get("/cost-summary")
async def get_cost_summary(db: Session = Depends(get_db)):
    """
    Get cost summary for dashboard
    
    Returns:
    - Monthly cost estimate
    - Cost per request
    - Trend percentage
    - Daily costs for last 30 days
    """
    try:
        # Get current month data
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        current_month_requests = db.query(func.count(RequestLog.id)).filter(
            RequestLog.timestamp >= month_start
        ).scalar() or 0
        
        current_month_tokens = db.query(func.sum(RequestLog.total_tokens)).filter(
            RequestLog.timestamp >= month_start
        ).scalar() or 0
        
        # Estimate cost (example: $0.001 per request + $0.00002 per token)
        monthly_cost = (current_month_requests * 0.001) + (current_month_tokens * 0.00002)
        cost_per_request = monthly_cost / current_month_requests if current_month_requests > 0 else 0
        
        # Get last month data for trend
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)
        last_month_requests = db.query(func.count(RequestLog.id)).filter(
            RequestLog.timestamp >= last_month_start,
            RequestLog.timestamp < month_start
        ).scalar() or 0
        
        last_month_tokens = db.query(func.sum(RequestLog.total_tokens)).filter(
            RequestLog.timestamp >= last_month_start,
            RequestLog.timestamp < month_start
        ).scalar() or 0
        
        last_month_cost = (last_month_requests * 0.001) + (last_month_tokens * 0.00002)
        
        # Calculate trend
        if last_month_cost > 0:
            trend_percent = ((monthly_cost - last_month_cost) / last_month_cost) * 100
        else:
            trend_percent = 0
        
        # Get daily costs for last 30 days (simplified)
        daily_costs = []
        for i in range(30):
            day_start = now - timedelta(days=i)
            day_start = day_start.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_requests = db.query(func.count(RequestLog.id)).filter(
                RequestLog.timestamp >= day_start,
                RequestLog.timestamp < day_end
            ).scalar() or 0
            
            day_cost = day_requests * 0.001
            daily_costs.append(round(day_cost, 2))
        
        daily_costs.reverse()  # Oldest to newest
        
        return {
            "monthly_cost_usd": round(monthly_cost, 2),
            "cost_per_request": round(cost_per_request, 4),
            "trend_percent": round(trend_percent, 1),
            "daily_costs": daily_costs
        }
    
    except Exception as e:
        logger.error(f"Error fetching cost summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch cost summary: {str(e)}"
        )


@router.get("/system-status")
async def get_system_status():
    """
    Get system status information for dashboard
    
    Returns:
    - Overall status (operational, degraded, offline)
    - Cloud provider (AWS, GCP, local)
    - Region (if cloud)
    - Fallback status (enabled/disabled)
    """
    try:
        from app.core.config import settings
        
        # Check if cloud ML is configured (safely)
        try:
            aws_region = getattr(settings, 'AWS_REGION', None)
            aws_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
            cloud_enabled = bool(aws_region and aws_key)
        except Exception:
            cloud_enabled = False
        
        # Determine overall status
        if cloud_enabled:
            overall_status = "operational"
            cloud_provider = "AWS"
            region = aws_region or "us-east-1"
        else:
            overall_status = "cloud_disabled"
            cloud_provider = "local"
            region = "n/a"
        
        # Fallback is always enabled (local models)
        fallback_enabled = True
        
        return {
            "overall_status": overall_status,
            "cloud_provider": cloud_provider,
            "region": region,
            "fallback_enabled": fallback_enabled
        }
    
    except Exception as e:
        logger.error(f"Error fetching system status: {str(e)}")
        # Return safe defaults instead of 500 error
        return {
            "overall_status": "cloud_disabled",
            "cloud_provider": "local",
            "region": "n/a",
            "fallback_enabled": True
        }
