"""
Rate Limiting Middleware using Redis
Implements per-user tier-based rate limiting with custom limit support
"""
from fastapi import Request, HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session
import logging
import time

from app.core.config import settings
from app.core.redis_client import redis_client
from app.core.database import get_db

logger = logging.getLogger(__name__)


class RateLimiter:
    """Redis-based rate limiter with tier support and custom limit integration"""
    
    @staticmethod
    async def check_rate_limit(user_id: str, tier: str = "free", db: Session = None) -> None:
        """
        Check if user has exceeded their rate limit
        
        Args:
            user_id: User's unique identifier
            tier: User's subscription tier (free/pro/enterprise)
            db: Optional database session for checking custom limits
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        # Try to get custom limit from database first
        custom_limit = None
        if db:
            try:
                from app.models.user_rate_limit_config import UserRateLimitConfig
                config = db.query(UserRateLimitConfig).filter(
                    UserRateLimitConfig.user_id == user_id
                ).first()
                
                if config:
                    # Custom limits are stored as hourly limits
                    custom_limit = config.custom_limit
                    tier = config.tier
                    logger.info(f"Using custom rate limit for {user_id}: {custom_limit} req/hour")
            except Exception as e:
                logger.warning(f"Failed to fetch custom rate limit: {str(e)}")
        
        # Get rate limit for tier (fallback if no custom limit)
        if custom_limit is None:
            limits = {
                "free": settings.RATE_LIMIT_FREE,
                "pro": settings.RATE_LIMIT_PRO,
                "enterprise": settings.RATE_LIMIT_ENTERPRISE
            }
            limit = limits.get(tier, settings.RATE_LIMIT_FREE)
        else:
            limit = custom_limit
        
        # Skip rate limiting for unlimited tiers (limit = -1)
        if limit == -1:
            logger.debug(f"Unlimited tier for {user_id}, skipping rate limit")
            return
        
        window_seconds = settings.RATE_LIMIT_WINDOW_SECONDS  # 3600 seconds = 1 hour
        
        # Create Redis key with current hour timestamp
        current_window = int(time.time() / window_seconds)
        redis_key = f"ratelimit:{user_id}:{current_window}"
        
        try:
            # Get current request count
            count = await redis_client.get(redis_key)
            current_count = int(count) if count else 0
            
            # Check if limit exceeded
            if current_count >= limit:
                retry_after = window_seconds - (int(time.time()) % window_seconds)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "code": "RATE_LIMIT",
                        "retry_after": retry_after,
                        "limit": limit,
                        "window": f"{window_seconds} seconds (1 hour)",
                        "tier": tier
                    },
                    headers={"Retry-After": str(retry_after)}
                )
            
            # Increment counter
            await redis_client.incr(redis_key)
            
            # Set expiration on first increment
            if current_count == 0:
                await redis_client.expire(redis_key, window_seconds)
            
            logger.debug(f"Rate limit check: {user_id} - {current_count + 1}/{limit} ({tier}) - window resets in {window_seconds - (int(time.time()) % window_seconds)}s")
            
        except HTTPException:
            # Re-raise rate limit exceptions
            raise
        except Exception as e:
            # Log error but don't block request if Redis fails
            logger.warning(f"Rate limit check failed (allowing request): {str(e)}")
    
    @staticmethod
    async def get_remaining_quota(user_id: str, tier: str = "free", db: Session = None) -> dict:
        """
        Get remaining quota for user
        
        Args:
            user_id: User's unique identifier
            tier: User's subscription tier
            db: Optional database session for checking custom limits
            
        Returns:
            dict: Quota information
        """
        # Try to get custom limit from database first
        custom_limit = None
        if db:
            try:
                from app.models.user_rate_limit_config import UserRateLimitConfig
                config = db.query(UserRateLimitConfig).filter(
                    UserRateLimitConfig.user_id == user_id
                ).first()
                
                if config:
                    custom_limit = config.custom_limit
                    tier = config.tier
            except Exception as e:
                logger.warning(f"Failed to fetch custom rate limit for quota: {str(e)}")
        
        # Get rate limit for tier
        if custom_limit is None:
            limits = {
                "free": settings.RATE_LIMIT_FREE,
                "pro": settings.RATE_LIMIT_PRO,
                "enterprise": settings.RATE_LIMIT_ENTERPRISE
            }
            limit = limits.get(tier, settings.RATE_LIMIT_FREE)
        else:
            limit = custom_limit
        
        # Handle unlimited tier
        if limit == -1:
            return {
                "limit": -1,
                "used": 0,
                "remaining": -1,  # -1 indicates unlimited
                "window_seconds": settings.RATE_LIMIT_WINDOW_SECONDS,
                "tier": tier,
                "unlimited": True
            }
        
        window_seconds = settings.RATE_LIMIT_WINDOW_SECONDS
        
        current_window = int(time.time() / window_seconds)
        redis_key = f"ratelimit:{user_id}:{current_window}"
        
        try:
            count = await redis_client.get(redis_key)
            used = int(count) if count else 0
            remaining = max(0, limit - used)
            
            return {
                "limit": limit,
                "used": used,
                "remaining": remaining,
                "window_seconds": window_seconds,
                "tier": tier,
                "unlimited": False
            }
        except Exception as e:
            logger.error(f"Failed to get quota: {str(e)}")
            return {
                "limit": limit,
                "used": 0,
                "remaining": limit,
                "window_seconds": window_seconds,
                "tier": tier,
                "unlimited": False
            }
