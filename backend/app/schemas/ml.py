"""
Pydantic schemas for ML endpoints
"""
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============ Abuse Detection Schemas ============

class AbuseFeatures(BaseModel):
    """Features for abuse detection"""
    requests_per_minute: float = Field(..., ge=0, description="Requests per minute")
    unique_endpoints_accessed: int = Field(..., ge=0, description="Number of unique endpoints")
    error_rate_percentage: float = Field(..., ge=0, le=100, description="Error rate percentage")
    request_timing_patterns: float = Field(..., ge=0, le=1, description="Timing pattern score")
    ip_reputation_score: float = Field(..., ge=0, le=1, description="IP reputation (0=bad, 1=good)")
    endpoint_diversity_score: float = Field(..., ge=0, le=1, description="Endpoint diversity")


class AbuseDetectionRequest(BaseModel):
    """Request for abuse detection"""
    features: AbuseFeatures


class AbuseDetectionResponse(BaseModel):
    """Response from abuse detection"""
    anomaly_score: float = Field(..., description="Anomaly score (0-1, higher=more anomalous)")
    is_abusive: bool = Field(..., description="Whether behavior is classified as abusive")
    confidence: float = Field(..., description="Confidence of prediction (0-1)")
    source: Literal["cloud", "cache", "fallback", "default"] = Field(..., description="Prediction source")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============ Rate Limit Optimization Schemas ============

class UserFeatures(BaseModel):
    """Features for rate limit optimization"""
    user_tier: Literal["free", "premium", "enterprise"] = Field(..., description="User subscription tier")
    historical_avg_requests: float = Field(..., ge=0, description="Historical average requests per hour")
    behavioral_consistency: float = Field(..., ge=0, le=1, description="Behavioral consistency score")
    endpoint_usage_patterns: Optional[float] = Field(0.5, ge=0, le=1, description="Endpoint usage pattern score")
    time_of_day_patterns: Optional[float] = Field(0.5, ge=0, le=1, description="Time of day pattern score")
    burst_frequency: Optional[float] = Field(0.5, ge=0, le=1, description="Request burst frequency")


class RateLimitOptimizationRequest(BaseModel):
    """Request for rate limit optimization"""
    user_features: UserFeatures


class RateLimitOptimizationResponse(BaseModel):
    """Response from rate limit optimization"""
    recommended_limit: int = Field(..., ge=0, description="Recommended requests per hour")
    confidence: float = Field(..., description="Confidence of recommendation (0-1)")
    source: Literal["cloud", "cache", "fallback", "default"] = Field(..., description="Prediction source")
    reasoning: str = Field(..., description="Explanation of recommendation")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============ Traffic Forecasting Schemas ============

class TrafficDataPoint(BaseModel):
    """Single traffic data point"""
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    requests: int = Field(..., ge=0, description="Number of requests")


class TrafficPrediction(BaseModel):
    """Single traffic prediction"""
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    requests: int = Field(..., description="Predicted requests")
    lower: int = Field(..., description="Lower bound of prediction")
    upper: int = Field(..., description="Upper bound of prediction")


class TrafficForecastRequest(BaseModel):
    """Request for traffic forecast"""
    historical_data: List[TrafficDataPoint] = Field(..., min_length=1, description="Historical traffic data")
    periods_ahead: int = Field(6, ge=1, le=24, description="Number of 5-min periods to forecast")


class TrafficForecastResponse(BaseModel):
    """Response from traffic forecast"""
    predictions: List[TrafficPrediction] = Field(..., description="Traffic predictions")
    trend: Literal["increasing", "stable", "decreasing"] = Field(..., description="Overall trend")
    confidence: float = Field(..., description="Confidence of forecast (0-1)")
    source: Literal["cloud", "cache", "fallback", "default"] = Field(..., description="Prediction source")
    forecast_horizon: str = Field(..., description="Forecast time horizon")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============ Health Check Schemas ============

class EndpointHealth(BaseModel):
    """Health status of a single endpoint"""
    status: Literal["healthy", "unhealthy", "unknown", "not_configured"] = Field(..., description="Health status")
    latency_ms: Optional[float] = Field(None, description="Last prediction latency in milliseconds")


class CloudHealthResponse(BaseModel):
    """Response from cloud health check"""
    overall_status: Literal["healthy", "degraded", "unhealthy", "cloud_disabled"] = Field(..., description="Overall health")
    endpoints: Dict[str, Any] = Field(..., description="Individual endpoint statuses")
    fallback_enabled: bool = Field(..., description="Whether fallback is enabled")
    cloud_provider: str = Field("google_cloud", description="Cloud provider name")
    region: str = Field(..., description="Cloud region")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============ Training & Deployment Schemas ============

class TrainDeployRequest(BaseModel):
    """Request to train and deploy a model"""
    model_type: Literal["isolation_forest", "xgboost", "prophet"] = Field(..., description="Model to train/deploy")
    force_retrain: bool = Field(False, description="Force retraining even if recent model exists")


class TrainDeployResponse(BaseModel):
    """Response from train/deploy request"""
    message: str = Field(..., description="Status message")
    status: Literal["processing", "completed", "failed"] = Field(..., description="Processing status")
    estimated_time: Optional[str] = Field(None, description="Estimated completion time")
    task_id: Optional[str] = Field(None, description="Background task ID")
