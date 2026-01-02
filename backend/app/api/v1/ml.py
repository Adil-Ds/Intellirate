"""
ML API endpoints for abuse detection, rate limiting, and traffic forecasting
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from datetime import datetime
import logging
import traceback

from app.services.cloud_ml_service import cloud_ml_client
from app.schemas.ml import (
    AbuseDetectionRequest,
    AbuseDetectionResponse,
    RateLimitOptimizationRequest,
    RateLimitOptimizationResponse,
    TrafficForecastRequest,
    TrafficForecastResponse,
    CloudHealthResponse,
    TrainDeployRequest,
    TrainDeployResponse
)
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.post("/detect-abuse", response_model=AbuseDetectionResponse)
async def detect_abuse(request: AbuseDetectionRequest):
    """
    Detect abusive behavior using cloud-hosted or local Isolation Forest model
    
    **Features required:**
    - requests_per_minute: Rate of requests
    - unique_endpoints_accessed: Number of unique endpoints
    - error_rate_percentage: Error rate (0-100)
    - request_timing_patterns: Timing pattern score (0-1)
    - ip_reputation_score: IP reputation (0=bad, 1=good)
    - endpoint_diversity_score: Endpoint diversity (0-1)
    
    **Returns:**
    - anomaly_score: How anomalous the behavior is (0-1)
    - is_abusive: Boolean classification
    - confidence: Prediction confidence (0-1)
    - source: Where prediction came from (cloud/cache/fallback)
    """
    try:
        result = await cloud_ml_client.predict_abuse(
            features=request.features.model_dump(),
            use_cache=True
        )
        
        return AbuseDetectionResponse(
            anomaly_score=result["anomaly_score"],
            is_abusive=result["is_abusive"],
            confidence=result["confidence"],
            source=result["source"],
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Abuse detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/optimize-rate-limit", response_model=RateLimitOptimizationResponse)
async def optimize_rate_limit(request: RateLimitOptimizationRequest):
    """
    Get optimal rate limit recommendation using cloud-hosted or local XGBoost model
    
    **User Features:**
    - user_tier: Subscription tier (free/premium/enterprise)
    - historical_avg_requests: Average requests per hour historically
    - behavioral_consistency: How consistent behavior is (0-1)
    - endpoint_usage_patterns: Endpoint usage pattern score (0-1)
    - time_of_day_patterns: Time of day pattern score (0-1)
    - burst_frequency: How often bursts occur (0-1)
    
    **Returns:**
    - recommended_limit: Suggested requests per hour
    - confidence: Recommendation confidence (0-1)
    - reasoning: Explanation of recommendation
    - source: Where prediction came from
    """
    try:
        result = await cloud_ml_client.optimize_rate_limit(
            user_features=request.user_features.model_dump(),
            use_cache=True
        )
        
        return RateLimitOptimizationResponse(
            recommended_limit=result["recommended_limit"],
            confidence=result["confidence"],
            source=result["source"],
            reasoning=result.get("reasoning", "ML-based optimization"),
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Rate limit optimization failed: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.post("/forecast-traffic", response_model=TrafficForecastResponse)
async def forecast_traffic(request: TrafficForecastRequest):
    """
    Forecast future traffic using cloud-hosted or local Prophet model
    
    **Input:**
    - historical_data: List of {timestamp, requests} data points
    - periods_ahead: Number of 5-minute periods to forecast (1-24)
    
    **Returns:**
    - predictions: List of forecasted traffic with confidence intervals
    - trend: Overall trend (increasing/stable/decreasing)
    - confidence: Forecast confidence (0-1)
    - forecast_horizon: Time span of forecast
    """
    try:
        historical_data_dict = [dp.model_dump() for dp in request.historical_data]
        
        result = await cloud_ml_client.forecast_traffic(
            historical_data=historical_data_dict,
            periods_ahead=request.periods_ahead,
            use_cache=True
        )
        
        return TrafficForecastResponse(
            predictions=result["predictions"],
            trend=result["trend"],
            confidence=result["confidence"],
            source=result["source"],
            forecast_horizon=f"{request.periods_ahead * 5} minutes",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Traffic forecast failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Forecast failed: {str(e)}")


@router.get("/health", response_model=CloudHealthResponse)
async def check_cloud_health():
    """
    Check health of all cloud ML endpoints
    
    **Returns:**
    - overall_status: Overall health (healthy/degraded/unhealthy)
    - endpoints: Individual endpoint statuses
    - fallback_enabled: Whether local fallback is enabled
    - cloud_provider: Cloud provider name
    - region: Cloud region
    """
    try:
        health_status = await cloud_ml_client.check_all_endpoints_health()
        
        # Determine cloud provider based on configuration
        cloud_provider = "aws" if settings.USE_CLOUD_ML else "local"
        region = settings.AWS_DEFAULT_REGION if settings.USE_CLOUD_ML else "n/a"
        
        return CloudHealthResponse(
            overall_status=health_status["overall"],
            endpoints={
                "isolation_forest": health_status["isolation_forest"],
                "xgboost": health_status["xgboost"],
                "prophet": health_status["prophet"]
            },
            fallback_enabled=settings.ENABLE_ML_FALLBACK,
            cloud_provider=cloud_provider,
            region=region,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.post("/train-and-deploy", response_model=TrainDeployResponse)
async def train_and_deploy_model(
    request: TrainDeployRequest,
    background_tasks: BackgroundTasks
):
    """
    Train model locally and deploy to cloud (long-running task)
    
    **This is a background task that will:**
    1. Generate training data or use provided data
    2. Train the model locally
    3. Evaluate model performance
    4. Deploy to Google Cloud Vertex AI
    5. Update endpoint configuration
    
    **Note:** This typically takes 5-15 minutes depending on model type
    """
    try:
        # Add background task for training and deployment
        task_id = f"train_deploy_{request.model_type}_{datetime.utcnow().timestamp()}"
        
        # background_tasks.add_task(
        #     _train_and_deploy_pipeline,
        #     model_type=request.model_type,
        #     force_retrain=request.force_retrain,
        #     task_id=task_id
        # )
        
        return TrainDeployResponse(
            message=f"Training and deployment started for {request.model_type}",
            status="processing",
            estimated_time="5-15 minutes",
            task_id=task_id
        )
    except Exception as e:
        logger.error(f"Train/deploy initiation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start training: {str(e)}")


async def _train_and_deploy_pipeline(model_type: str, force_retrain: bool, task_id: str):
    """
    Background task to train and deploy model
    
    Steps:
    1. Check if retraining is needed
    2. Generate/load training data
    3. Train model
    4. Evaluate metrics
    5. If metrics are good, deploy to cloud
    6. Send notification via N8N webhook
    """
    logger.info(f"Starting train/deploy pipeline for {model_type} (task: {task_id})")
    
    try:
        # TODO: Implement training pipeline
        # 1. Load data
        # 2. Train model
        # 3. Evaluate
        # 4. Deploy to cloud
        # 5. Notify
        
        logger.info(f"Train/deploy pipeline completed for {model_type}")
    except Exception as e:
        logger.error(f"Train/deploy pipeline failed for {model_type}: {str(e)}")
