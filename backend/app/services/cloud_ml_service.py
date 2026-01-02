"""
AWS SageMaker ML Service - Handles all SageMaker interactions
"""
import os
import logging
import hashlib
import json
import asyncio
from typing import Dict, List, Optional, Any
from functools import lru_cache

try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    logging.warning("AWS SDK (boto3) not available. Cloud ML features disabled.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy not available.")

from app.core.config import settings
from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)


class AWSCloudMLClient:
    """Client for interacting with AWS SageMaker endpoints"""
    
    def __init__(self):
        self.region = settings.AWS_DEFAULT_REGION
        self.timeout = settings.ML_PREDICTION_TIMEOUT
        self.retry_attempts = settings.ML_RETRY_ATTEMPTS
        self.use_cloud = settings.USE_CLOUD_ML and AWS_AVAILABLE
        
        if self.use_cloud:
            try:
                # Initialize SageMaker Runtime client
                self.sagemaker_runtime = boto3.client(
                    'sagemaker-runtime',
                    region_name=self.region,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
                logger.info(f"✓ Initialized AWS SageMaker Client for region: {self.region}")
            except Exception as e:
                logger.error(f"Failed to initialize SageMaker client: {str(e)}")
                self.use_cloud = False
        
        # Endpoint names
        self._isolation_forest_endpoint = settings.ISOLATION_FOREST_ENDPOINT_NAME
        self._xgboost_endpoint = settings.XGBOOST_ENDPOINT_NAME
        self._prophet_endpoint = settings.PROPHET_ENDPOINT_NAME
    
    @property
    def isolation_forest_endpoint(self) -> Optional[str]:
        """Get Isolation Forest endpoint name"""
        if not self.use_cloud:
            return None
        if self._isolation_forest_endpoint:
            logger.debug(f"Using Isolation Forest endpoint: {self._isolation_forest_endpoint}")
        return self._isolation_forest_endpoint
    
    @property
    def xgboost_endpoint(self) -> Optional[str]:
        """Get XGBoost endpoint name"""
        if not self.use_cloud:
            return None
        if self._xgboost_endpoint:
            logger.debug(f"Using XGBoost endpoint: {self._xgboost_endpoint}")
        return self._xgboost_endpoint
    
    @property
    def prophet_endpoint(self) -> Optional[str]:
        """Get Prophet endpoint name"""
        if not self.use_cloud:
            return None
        if self._prophet_endpoint:
            logger.debug(f"Using Prophet endpoint: {self._prophet_endpoint}")
        return self._prophet_endpoint
    
    async def predict_abuse(
        self, 
        features: Dict[str, float],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Predict if user behavior is abusive using Isolation Forest
        
        Args:
            features: Dictionary with behavioral features
            use_cache: Whether to use cached predictions
        
        Returns:
            {
                "anomaly_score": 0.85,
                "is_abusive": True,
                "confidence": 0.92,
                "source": "cloud" | "cache" | "fallback"
            }
        """
        model_type = "isolation_forest"
        
        # Check cache first
        if use_cache:
            cache_key = self._generate_cache_key(model_type, features)
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for {model_type}")
                cached["source"] = "cache"
                return cached
        
        # Try cloud prediction
        if self.use_cloud and self.isolation_forest_endpoint:
            try:
                # Prepare input for SageMaker
                payload = self._format_features_for_isolation_forest(features)
                
                # Call SageMaker endpoint with retry logic
                prediction = await self._call_endpoint_with_retry(
                    endpoint_name=self.isolation_forest_endpoint,
                    payload=payload,
                    model_type=model_type
                )
                
                # Parse response
                result = self._parse_isolation_forest_response(prediction)
                result["source"] = "cloud"
                
                # Cache result
                if use_cache:
                    await redis_client.set(
                        cache_key,
                        result,
                        ttl=settings.ML_PREDICTION_CACHE_TTL
                    )
                
                logger.info(f"Abuse prediction: score={result['anomaly_score']:.2f} (cloud)")
                return result
                
            except Exception as e:
                logger.error(f"Cloud prediction failed for {model_type}: {str(e)}")
        
        # Fallback to local model
        if settings.ENABLE_ML_FALLBACK:
            logger.warning(f"Using local fallback for {model_type}")
            from app.services.ml_fallback_service import ml_fallback
            result = await ml_fallback.predict_abuse(features)
            result["source"] = "fallback"
            return result
        else:
            raise Exception(f"Cloud ML unavailable and fallback disabled")
    
    async def optimize_rate_limit(
        self,
        user_features: Dict[str, Any],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Predict optimal rate limit for user using XGBoost
        
        Returns:
            {
                "recommended_limit": 150,
                "confidence": 0.88,
                "source": "cloud" | "cache" | "fallback"
            }
        """
        model_type = "xgboost"
        
        # Check cache
        if use_cache:
            cache_key = self._generate_cache_key(model_type, user_features)
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for {model_type}")
                cached["source"] = "cache"
                return cached
        
        # Try cloud prediction
        if self.use_cloud and self.xgboost_endpoint:
            try:
                payload = self._format_features_for_xgboost(user_features)
                
                prediction = await self._call_endpoint_with_retry(
                    endpoint_name=self.xgboost_endpoint,
                    payload=payload,
                    model_type=model_type
                )
                
                result = self._parse_xgboost_response(prediction)
                result["source"] = "cloud"
                
                if use_cache:
                    await redis_client.set(
                        cache_key,
                        result,
                        ttl=settings.ML_PREDICTION_CACHE_TTL
                    )
                
                logger.info(f"Rate limit optimization: {result['recommended_limit']} req/hr (cloud)")
                return result
                
            except Exception as e:
                logger.error(f"Cloud prediction failed for {model_type}: {str(e)}")
        
        # Fallback
        if settings.ENABLE_ML_FALLBACK:
            logger.warning(f"Using local fallback for {model_type}")
            from app.services.ml_fallback_service import ml_fallback
            result = await ml_fallback.optimize_rate_limit(user_features)
            result["source"] = "fallback"
            return result
        else:
            raise Exception(f"Cloud ML unavailable and fallback disabled")
    
    async def forecast_traffic(
        self,
        historical_data: List[Dict[str, Any]],
        periods_ahead: int = 6,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Forecast future traffic using Prophet
        
        Returns:
            {
                "predictions": [...],
                "trend": "increasing" | "stable" | "decreasing",
                "confidence": 0.85,
                "source": "cloud" | "cache" | "fallback"
            }
        """
        model_type = "prophet"
        
        # Check cache (shorter TTL for time-series)
        if use_cache:
            cache_key = self._generate_cache_key(model_type, {"periods": periods_ahead, "data_len": len(historical_data)})
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for {model_type}")
                cached["source"] = "cache"
                return cached
        
        # Try cloud prediction
        if self.use_cloud and self.prophet_endpoint:
            try:
                payload = self._format_data_for_prophet(historical_data, periods_ahead)
                
                prediction = await self._call_endpoint_with_retry(
                    endpoint_name=self.prophet_endpoint,
                    payload=payload,
                    model_type=model_type
                )
                
                result = self._parse_prophet_response(prediction)
                result["source"] = "cloud"
                
                if use_cache:
                    await redis_client.set(
                        cache_key,
                        result,
                        ttl=60  # 1 minute cache for forecasts
                    )
                
                logger.info(f"Traffic forecast: {len(result['predictions'])} periods, trend={result['trend']} (cloud)")
                return result
                
            except Exception as e:
                logger.error(f"Cloud prediction failed for {model_type}: {str(e)}")
        
        # Fallback
        if settings.ENABLE_ML_FALLBACK:
            logger.warning(f"Using local fallback for {model_type}")
            from app.services.ml_fallback_service import ml_fallback
            result = await ml_fallback.forecast_traffic(historical_data, periods_ahead)
            result["source"] = "fallback"
            return result
        else:
            raise Exception(f"Cloud ML unavailable and fallback disabled")
    
    async def check_all_endpoints_health(self) -> Dict[str, Any]:
        """Check health of all cloud ML endpoints"""
        health_status = {
            "overall": "healthy",
            "isolation_forest": "unknown",
            "xgboost": "unknown",
            "prophet": "unknown"
        }
        
        if not self.use_cloud:
            health_status["overall"] = "cloud_disabled"
            return health_status
        
        # Check each endpoint
        endpoints = {
            "isolation_forest": self.isolation_forest_endpoint,
            "xgboost": self.xgboost_endpoint,
            "prophet": self.prophet_endpoint
        }
        
        for name, endpoint_name in endpoints.items():
            if endpoint_name:
                try:
                    # Simple health check - verify endpoint exists
                    sagemaker_client = boto3.client('sagemaker', region_name=self.region)
                    response = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
                    if response['EndpointStatus'] == 'InService':
                        health_status[name] = "healthy"
                    else:
                        health_status[name] = f"status_{response['EndpointStatus'].lower()}"
                        health_status["overall"] = "degraded"
                except Exception as e:
                    logger.error(f"Health check failed for {name}: {str(e)}")
                    health_status[name] = "unhealthy"
                    health_status["overall"] = "degraded"
            else:
                health_status[name] = "not_configured"
        
        return health_status
    
    async def _call_endpoint_with_retry(
        self,
        endpoint_name: str,
        payload: Dict,
        model_type: str
    ) -> Dict[str, Any]:
        """Call SageMaker endpoint with retry logic"""
        if not AWS_AVAILABLE:
            raise Exception("AWS SDK (boto3) not available")
        
        for attempt in range(self.retry_attempts):
            try:
                # Convert payload to JSON
                payload_json = json.dumps(payload)
                
                # Call SageMaker endpoint
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.sagemaker_runtime.invoke_endpoint(
                        EndpointName=endpoint_name,
                        ContentType='application/json',
                        Body=payload_json
                    )
                )
                
                # Parse response
                result = json.loads(response['Body'].read().decode())
                return result
                
            except (ClientError, BotoCoreError) as e:
                error_code = e.response.get('Error', {}).get('Code', '') if hasattr(e, 'response') else ''
                
                if error_code in ['ThrottlingException', 'ServiceUnavailable'] and attempt < self.retry_attempts - 1:
                    # Retry with exponential backoff
                    wait_time = (2 ** attempt) * settings.ML_RETRY_BACKOFF
                    logger.warning(f"Retrying {model_type} after {wait_time}s (attempt {attempt + 1}/{self.retry_attempts})")
                    await asyncio.sleep(wait_time)
                else:
                    raise Exception(f"SageMaker endpoint call failed: {str(e)}")
            except asyncio.TimeoutError:
                if attempt < self.retry_attempts - 1:
                    logger.warning(f"Timeout on {model_type}, retrying...")
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise Exception(f"Prediction timeout for {model_type} after {self.timeout}s")
        
        raise Exception(f"Max retries exceeded for {model_type}")
    
    def _generate_cache_key(self, model_type: str, data: Dict) -> str:
        """Generate Redis cache key from model type and input data"""
        data_str = json.dumps(data, sort_keys=True)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()
        return f"ml_prediction:{model_type}:{data_hash}"
    
    def _format_features_for_isolation_forest(self, features: Dict) -> Dict:
        """Format features for Isolation Forest model"""
        return {
            "instances": [[
                features.get("requests_per_minute", 0),
                features.get("unique_endpoints_accessed", 0),
                features.get("error_rate_percentage", 0),
                features.get("request_timing_patterns", 0),
                features.get("ip_reputation_score", 0),
                features.get("endpoint_diversity_score", 0)
            ]]
        }
    
    def _parse_isolation_forest_response(self, prediction: Dict) -> Dict:
        """Parse SageMaker response for Isolation Forest"""
        # Extract predictions from SageMaker response
        predictions = prediction.get("predictions", [{}])
        pred = predictions[0] if predictions else {}
        
        anomaly_score = float(pred.get("anomaly_score", 0.5))
        is_abusive = anomaly_score > 0.8
        confidence = abs(anomaly_score - 0.5) * 2
        
        return {
            "anomaly_score": anomaly_score,
            "is_abusive": is_abusive,
            "confidence": confidence
        }
    
    def _format_features_for_xgboost(self, user_features: Dict) -> Dict:
        """Format features for XGBoost model"""
        tier_map = {"free": 0, "premium": 1, "enterprise": 2}
        
        return {
            "instances": [[
                tier_map.get(user_features.get("user_tier", "free"), 0),
                user_features.get("historical_avg_requests", 50),
                user_features.get("behavioral_consistency", 0.5),
                user_features.get("endpoint_usage_patterns", 0.5),
                user_features.get("time_of_day_patterns", 0.5),
                user_features.get("burst_frequency", 0.5)
            ]]
        }
    
    def _parse_xgboost_response(self, prediction: Dict) -> Dict:
        """Parse SageMaker response for XGBoost"""
        predictions = prediction.get("predictions", [{}])
        pred = predictions[0] if predictions else {}
        
        recommended_limit = int(pred.get("recommended_limit", 100))
        confidence = float(pred.get("confidence", 0.85))
        
        # Safety check: Ensure minimum limit of 1 request/hour
        # If model predicts negative or very low values, default to 1
        if recommended_limit < 1:
            logger.warning(f"Model predicted very low limit ({recommended_limit}), setting to minimum of 1")
            recommended_limit = 1
            confidence = max(0.5, confidence)  # Lower confidence for clamped values
        
        return {
            "recommended_limit": recommended_limit,
            "confidence": confidence,
            "reasoning": f"ML-based optimization with {confidence:.0%} confidence"
        }
    
    def _format_data_for_prophet(self, historical_data: List[Dict], periods_ahead: int) -> Dict:
        """Format data for Prophet model"""
        return {
            "instances": [{
                "historical_data": historical_data,
                "periods_ahead": periods_ahead
            }]
        }
    
    def _parse_prophet_response(self, prediction: Dict) -> Dict:
        """Parse SageMaker response for Prophet"""
        predictions = prediction.get("predictions", [{}])
        pred = predictions[0] if predictions else {}
        
        forecast_predictions = pred.get("predictions", [])
        trend = pred.get("trend", "stable")
        confidence = float(pred.get("confidence", 0.80))
        
        return {
            "predictions": forecast_predictions,
            "trend": trend,
            "confidence": confidence
        }


# Global instance
cloud_ml_client = AWSCloudMLClient()
