"""
Redis client for caching ML predictions and features
"""
import json
import logging
from typing import Any, Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Async Redis client for caching"""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self._pool: Optional[aioredis.ConnectionPool] = None
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self._pool = aioredis.ConnectionPool.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding="utf-8"
            )
            self.redis = aioredis.Redis(connection_pool=self._pool)
            await self.redis.ping()
            logger.info("✓ Redis connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")
    
    async def get(self, key: str) -> Optional[dict]:
        """Get cached value by key"""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Redis GET error for key {key}: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value with TTL (time to live in seconds)"""
        try:
            serialized = json.dumps(value)
            await self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Redis SET error for key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete a key"""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis DELETE error for key {key}: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.warning(f"Redis EXISTS error for key {key}: {str(e)}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Redis CLEAR_PATTERN error for pattern {pattern}: {str(e)}")
            return 0


# Global instance
redis_client = RedisClient()
