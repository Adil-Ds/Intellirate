"""
Schemas for analytics endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional


class UserAnalytics(BaseModel):
    """Per-user analytics response"""
    user_id: str
    total_requests: int
    total_tokens: int
    avg_latency_ms: float
    success_rate: float
    last_request: Optional[str] = None
    period_days: int


class SystemAnalytics(BaseModel):
    """System-wide analytics response"""
    period: str
    total_requests: int
    total_tokens: int
    unique_users: int
    avg_tokens_per_request: float


class RateLimitQuota(BaseModel):
    """Rate limit quota information"""
    limit: int
    used: int
    remaining: int
    window_seconds: int
    tier: str
