"""
Rate Limits API Endpoints
Manage user tiers, rate limits, and events with ML optimization
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import logging

from app.core.database import get_db
from app.models.request_log import RequestLog
from app.models.user_rate_limit_config import UserRateLimitConfig
from app.schemas.ml import UserFeatures, RateLimitOptimizationRequest
from app.services.cloud_ml_service import cloud_ml_client
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rate-limits", tags=["Rate Limits"])


# ============ Schemas ============

class TierSummary(BaseModel):
    """Summary of a subscription tier"""
    name: str
    limit: int
    users: int
    total_usage: int
    features: List[str]


class UserRateLimit(BaseModel):
    """Rate limit details for a user"""
    user_id: str
    user_email: Optional[str]
    tier: str
    limit: int
    current_usage: int
    usage_percentage: float
    ml_recommended_limit: Optional[int] = None
    ml_confidence: Optional[float] = None
    last_active: Optional[str] = None


class RateLimitEvent(BaseModel):
    """Rate limit event (warning, breach, reset)"""
    event_id: str
    user_id: str
    user_email: Optional[str]
    event_type: str
    timestamp: str
    usage_percentage: float
    current_limit: int


class UpdateRateLimitRequest(BaseModel):
    """Request to update user rate limit"""
    limit: int
    tier: str


class MLRecommendationResponse(BaseModel):
    """ML-based rate limit recommendation"""
    user_id: str
    current_limit: int
    recommended_limit: int
    confidence: float
    reasoning: str
    potential_savings: Optional[int] = None
    recommendation_type: str  # 'increase', 'decrease', 'maintain'


# ============ Tier Configuration ============

TIER_CONFIG = {
    "free": {
        "limit": 50,  # 50 requests per hour
        "features": ["Basic analytics", "24h data retention", "Email support"]
    },
    "pro": {
        "limit": 1000,  # 1000 requests per hour
        "features": ["Advanced analytics", "30d data retention", "Priority support", "Custom alerts"]
    },
    "enterprise": {
        "limit": -1,  # Unlimited (no rate limiting)
        "features": ["Full analytics suite", "Unlimited retention", "24/7 support", "Custom integrations", "SLA guarantee"]
    }
}


# ============ Helper Functions ============

def determine_user_tier(total_requests: int) -> str:
    """Determine user tier based on usage patterns"""
    if total_requests > 50000:
        return "enterprise"
    elif total_requests > 5000:
        return "pro"
    else:
        return "free"


def calculate_usage_features(db: Session, user_id: str, tier: str):
    """Calculate features for ML rate limit optimization"""
    # Get requests from last 7 days
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    
    requests = db.query(RequestLog).filter(
        and_(
            RequestLog.user_id == user_id,
            RequestLog.timestamp >= cutoff
        )
    ).all()
    
    if not requests:
        return None
    
    # Calculate historical average requests per hour
    hours_active = max(1, len(set(r.timestamp.replace(minute=0, second=0, microsecond=0) for r in requests)))
    historical_avg_requests = len(requests) / hours_active
    
    # Calculate behavioral consistency (lower variance = more consistent)
    hourly_counts = {}
    for req in requests:
        hour = req.timestamp.replace(minute=0, second=0, microsecond=0)
        hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
    
    counts = list(hourly_counts.values())
    if len(counts) > 1:
        mean = sum(counts) / len(counts)
        variance = sum((x - mean) ** 2 for x in counts) / len(counts)
        std_dev = variance ** 0.5
        behavioral_consistency = max(0, 1 - (std_dev / (mean + 1)))
    else:
        behavioral_consistency = 1.0
    
    # Calculate endpoint diversity
    unique_endpoints = len(set(req.endpoint for req in requests if req.endpoint))
    endpoint_usage_patterns = min(1.0, unique_endpoints / 10)
    
    # Calculate time of day patterns (how consistent are request times)
    hour_of_day = [r.timestamp.hour for r in requests]
    if hour_of_day:
        hour_variance = len(set(hour_of_day)) / 24
        time_of_day_patterns = 1.0 - hour_variance
    else:
        time_of_day_patterns = 0.5
    
    # Calculate burst frequency
    if len(requests) > 1:
        time_diffs = []
        sorted_requests = sorted(requests, key=lambda x: x.timestamp)
        for i in range(1, len(sorted_requests)):
            diff = (sorted_requests[i].timestamp - sorted_requests[i-1].timestamp).total_seconds()
            time_diffs.append(diff)
        
        # If many requests are <1 second apart, high burst frequency
        very_close_requests = sum(1 for d in time_diffs if d < 1)
        burst_frequency = very_close_requests / len(time_diffs)
    else:
        burst_frequency = 0.0
    
    return UserFeatures(
        user_tier=tier,
        historical_avg_requests=historical_avg_requests,
        behavioral_consistency=behavioral_consistency,
        endpoint_usage_patterns=endpoint_usage_patterns,
        time_of_day_patterns=time_of_day_patterns,
        burst_frequency=burst_frequency
    )


# ============ Endpoints ============

@router.get("/tiers")
async def get_tier_summary(db: Session = Depends(get_db)):
    """
    Get summary of all tiers with user counts and usage
    """
    try:
        # Get all users with their stats
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        
        user_stats = db.query(
            RequestLog.user_id,
            func.count(RequestLog.id).label('total_requests')
        ).filter(
            RequestLog.timestamp >= cutoff
        ).group_by(
            RequestLog.user_id
        ).all()
        
        # Categorize users into tiers
        tier_data = {
            "free": {"users": [], "total_usage": 0},
            "pro": {"users": [], "total_usage": 0},
            "enterprise": {"users": [], "total_usage": 0}
        }
        
        for user in user_stats:
            tier = determine_user_tier(user.total_requests)
            tier_data[tier]["users"].append(user.user_id)
            tier_data[tier]["total_usage"] += user.total_requests
        
        # Build tier summaries
        tiers = []
        for tier_name, config in TIER_CONFIG.items():
            tiers.append(TierSummary(
                name=tier_name.capitalize(),
                limit=config["limit"],
                users=len(tier_data[tier_name]["users"]),
                total_usage=tier_data[tier_name]["total_usage"],
                features=config["features"]
            ))
        
        return {"tiers": tiers}
    
    except Exception as e:
        logger.error(f"Error fetching tier summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/users")
async def get_user_rate_limits(
    db: Session = Depends(get_db),
    tier: Optional[str] = Query(None, description="Filter by tier")
):
    """
    Get detailed rate limit information for all users
    """
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Get user stats
        user_stats = db.query(
            RequestLog.user_id,
            RequestLog.user_email,
            func.count(RequestLog.id).label('total_requests'),
            func.max(RequestLog.timestamp).label('last_active')
        ).filter(
            RequestLog.timestamp >= cutoff
        ).group_by(
            RequestLog.user_id,
            RequestLog.user_email
        ).all()
        
        # Get all custom rate limit configs
        custom_configs = db.query(UserRateLimitConfig).all()
        custom_config_map = {config.user_id: config for config in custom_configs}
        
        users = []
        for user in user_stats:
            # Check if user has custom config
            if user.user_id in custom_config_map:
                config = custom_config_map[user.user_id]
                user_tier = config.tier
                tier_limit = config.custom_limit
            else:
                # Use default tier-based limit
                user_tier = determine_user_tier(user.total_requests)
                tier_limit = TIER_CONFIG[user_tier]["limit"]
            
            # Skip if tier filter is applied
            if tier and user_tier != tier:
                continue
            
            usage_pct = (user.total_requests / tier_limit) * 100
            
            users.append(UserRateLimit(
                user_id=user.user_id,
                user_email=user.user_email,
                tier=user_tier,
                limit=tier_limit,
                current_usage=user.total_requests,
                usage_percentage=round(usage_pct, 2),
                last_active=user.last_active.isoformat() if user.last_active else None
            ))
        
        # Sort by usage percentage descending
        users.sort(key=lambda x: x.usage_percentage, reverse=True)
        
        return {"users": users, "total_users": len(users)}
    
    except Exception as e:
        logger.error(f"Error fetching user rate limits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events")
async def get_rate_limit_events(
    db: Session = Depends(get_db),
    limit: int = Query(20, description="Max number of events to return"),
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    Get recent rate limit events (warnings and breaches)
    """
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        
        # Get users approaching or exceeding limits
        user_stats = db.query(
            RequestLog.user_id,
            RequestLog.user_email,
            func.count(RequestLog.id).label('total_requests'),
            func.max(RequestLog.timestamp).label('last_request')
        ).filter(
            RequestLog.timestamp >= cutoff
        )
        
        if user_id:
            user_stats = user_stats.filter(RequestLog.user_id == user_id)
        
        user_stats = user_stats.group_by(
            RequestLog.user_id,
            RequestLog.user_email
        ).all()
        
        events = []
        for user in user_stats:
            user_tier = determine_user_tier(user.total_requests)
            tier_limit = TIER_CONFIG[user_tier]["limit"]
            usage_pct = (user.total_requests / tier_limit) * 100
            
            # Generate events based on usage
            if usage_pct >= 100:
                event_type = "breach"
            elif usage_pct >= 90:
                event_type = "warning"
            elif usage_pct < 10:
                event_type = "reset"
            else:
                continue  # Skip users with normal usage
            
            events.append(RateLimitEvent(
                event_id=f"evt_{user.user_id}_{int(user.last_request.timestamp())}",
                user_id=user.user_id,
                user_email=user.user_email,
                event_type=event_type,
                timestamp=user.last_request.isoformat(),
                usage_percentage=round(usage_pct, 1),
                current_limit=tier_limit
            ))
        
        # Sort by timestamp descending
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return {"events": events[:limit], "total_events": len(events)}
    
    except Exception as e:
        logger.error(f"Error fetching rate limit events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/ml-recommendation")
async def get_ml_recommendation(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get ML-based rate limit recommendation for a specific user
    """
    try:
        # Get user's current statistics
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        
        user_stats = db.query(
            func.count(RequestLog.id).label('total_requests')
        ).filter(
            and_(
                RequestLog.user_id == user_id,
                RequestLog.timestamp >= cutoff
            )
        ).first()
        
        if not user_stats or user_stats.total_requests == 0:
            raise HTTPException(status_code=404, detail="User not found or no recent activity")
        
        # Determine current tier and limit
        current_tier = determine_user_tier(user_stats.total_requests)
        current_limit = TIER_CONFIG[current_tier]["limit"]
        
        # Calculate usage features
        features = calculate_usage_features(db, user_id, current_tier)
        
        if not features:
            raise HTTPException(status_code=400, detail="Insufficient data for ML recommendation")
        
        # Get ML recommendation
        result = await cloud_ml_client.optimize_rate_limit(
            user_features=features.model_dump(),
            use_cache=True
        )
        
        recommended_limit = result["recommended_limit"]
        
        # Additional safety check: Ensure minimum limit of 1 request/hour
        if recommended_limit < 1:
            logger.warning(f"ML recommended very low limit ({recommended_limit}), setting to minimum of 1")
            recommended_limit = 1
            result["confidence"] = max(0.5, result.get("confidence", 0.85))
        
        # Determine recommendation type
        if recommended_limit > current_limit * 1.1:
            rec_type = "increase"
            savings = None
        elif recommended_limit < current_limit * 0.9:
            rec_type = "decrease"
            savings = current_limit - recommended_limit
        else:
            rec_type = "maintain"
            savings = None
        
        return MLRecommendationResponse(
            user_id=user_id,
            current_limit=current_limit,
            recommended_limit=recommended_limit,
            confidence=result["confidence"],
            reasoning=result.get("reasoning", "ML-based optimization"),
            potential_savings=savings,
            recommendation_type=rec_type
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ML recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/user/{user_id}")
async def update_user_rate_limit(
    user_id: str,
    request: UpdateRateLimitRequest,
    db: Session = Depends(get_db)
):
    """
    Update rate limit for a specific user
    
    Saves custom rate limit configuration to database.
    """
    try:
        # Validate tier
        if request.tier not in TIER_CONFIG:
            raise HTTPException(status_code=400, detail="Invalid tier")
        
        # Validate limit
        # Allow -1 for unlimited enterprise tier
        # Minimum 1 for hourly limits (at least 1 request/hour)
        if request.limit != -1 and request.limit < 1:
            raise HTTPException(status_code=400, detail="Limit must be at least 1 request per hour, or -1 for unlimited")
        
        # Check if user exists
        user_exists = db.query(RequestLog).filter(
            RequestLog.user_id == user_id
        ).first()
        
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Save/Update custom rate limit configuration
        existing_config = db.query(UserRateLimitConfig).filter(
            UserRateLimitConfig.user_id == user_id
        ).first()
        
        if existing_config:
            # Update existing config
            existing_config.tier = request.tier
            existing_config.custom_limit = request.limit
            logger.info(f"Updated existing config for user {user_id}")
        else:
            # Create new config
            new_config = UserRateLimitConfig(
                user_id=user_id,
                tier=request.tier,
                custom_limit=request.limit
            )
            db.add(new_config)
            logger.info(f"Created new config for user {user_id}")
        
        db.commit()
        
        # Log the rate limit update action
        try:
            log_entry = RequestLog(
                user_id=user_id,
                endpoint=f"/rate-limits/user/{user_id}",
                method="PUT",
                status_code=200,
                success=True,
                message_count=0,
                # Store the update details in a custom way
                model=f"rate_limit_update_{request.tier}_{request.limit}"
            )
            db.add(log_entry)
            db.commit()
        except Exception as log_error:
            logger.warning(f"Failed to log rate limit update: {str(log_error)}")
        
        logger.info(f"✓ Persisted rate limit for user {user_id}: tier={request.tier}, limit={request.limit}")
        
        return {
            "success": True,
            "message": f"Rate limit updated for user {user_id}",
            "user_id": user_id,
            "new_tier": request.tier,
            "new_limit": request.limit
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rate limit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


