"""
ML Fallback Service - Local model execution when cloud is unavailable
"""
import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MLFallbackService:
    """Local ML model execution for fallback scenarios"""
    
    def __init__(self):
        self.models_dir = Path("ml-models")
        self._isolation_forest_model = None
        self._xgboost_model = None
        self._prophet_model = None
        
        logger.info("ML Fallback Service initialized")
    
    @property
    def isolation_forest_model(self):
        """Lazy load Isolation Forest model"""
        if self._isolation_forest_model is None:
            try:
                model_path = self.models_dir / "isolation_forest" / "model_v1.pkl"
                if model_path.exists():
                    self._isolation_forest_model = joblib.load(model_path)
                    logger.info(f"✓ Loaded local Isolation Forest model from {model_path}")
                else:
                    logger.warning(f"Isolation Forest model not found at {model_path}")
            except Exception as e:
                logger.error(f"Failed to load Isolation Forest model: {str(e)}")
        return self._isolation_forest_model
    
    @property
    def xgboost_model(self):
        """Lazy load XGBoost model"""
        if self._xgboost_model is None:
            try:
                model_path = self.models_dir / "xgboost" / "model_v1.pkl"
                if model_path.exists():
                    self._xgboost_model = joblib.load(model_path)
                    logger.info(f"✓ Loaded local XGBoost model from {model_path}")
                else:
                    logger.warning(f"XGBoost model not found at {model_path}")
            except Exception as e:
                logger.error(f"Failed to load XGBoost model: {str(e)}")
        return self._xgboost_model
    
    @property
    def prophet_model(self):
        """Lazy load Prophet model"""
        if self._prophet_model is None:
            try:
                model_path = self.models_dir / "prophet" / "model_v1.pkl"
                if model_path.exists():
                    self._prophet_model = joblib.load(model_path)
                    logger.info(f"✓ Loaded local Prophet model from {model_path}")
                else:
                    logger.warning(f"Prophet model not found at {model_path}")
            except Exception as e:
                logger.error(f"Failed to load Prophet model: {str(e)}")
        return self._prophet_model
    
    async def predict_abuse(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Predict abuse using local Isolation Forest model
        """
        if self.isolation_forest_model is None:
            # Return safe default if model not available
            logger.warning("Isolation Forest model not available, returning default")
            return {
                "anomaly_score": 0.5,
                "is_abusive": False,
                "confidence": 0.3,
                "source": "default"
            }
        
        # Prepare features
        feature_vector = np.array([[
            features.get("requests_per_minute", 0),
            features.get("unique_endpoints_accessed", 0),
            features.get("error_rate_percentage", 0),
            features.get("request_timing_patterns", 0),
            features.get("ip_reputation_score", 0),
            features.get("endpoint_diversity_score", 0)
        ]])
        
        try:
            # Get anomaly score
            anomaly_score = self.isolation_forest_model.score_samples(feature_vector)[0]
            # Convert to 0-1 range (more negative = more anomalous)
            normalized_score = 1 / (1 + np.exp(anomaly_score))
            
            
            # Threshold set to 0.65 for better normal/abusive separation
            is_abusive = normalized_score > 0.65
            confidence = abs(normalized_score - 0.5) * 2
            
            return {
                "anomaly_score": float(normalized_score),
                "is_abusive": bool(is_abusive),
                "confidence": float(confidence)
            }
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                "anomaly_score": 0.5,
                "is_abusive": False,
                "confidence": 0.3,
                "error": str(e)
            }
    
    async def optimize_rate_limit(self, user_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize rate limit using local XGBoost model
        """
        if self.xgboost_model is None:
            # Return tier-based defaults
            tier = user_features.get("user_tier", "free")
            default_limits = {"free": 60, "premium": 150, "enterprise": 500}
            
            return {
                "recommended_limit": default_limits.get(tier, 60),
                "confidence": 0.5,
                "reasoning": f"Default limit for {tier} tier (model unavailable)"
            }
        
        # Prepare features
        tier_map = {"free": 0, "premium": 1, "enterprise": 2}
        feature_vector = np.array([[
            tier_map.get(user_features.get("user_tier", "free"), 0),
            user_features.get("historical_avg_requests", 50),
            user_features.get("behavioral_consistency", 0.5),
            user_features.get("endpoint_usage_patterns", 0.5),
            user_features.get("time_of_day_patterns", 0.5),
            user_features.get("burst_frequency", 0.5)
        ]])
        
        try:
            # Predict optimal limit
            predicted_limit = self.xgboost_model.predict(feature_vector)[0]
            
            # Get feature importance for confidence
            confidence = 0.85  # XGBoost is typically reliable
            
            # Safety check: Ensure minimum limit of 1 request/hour
            # If model predicts negative or very low values, default to 1
            recommended_limit = int(predicted_limit)
            if recommended_limit < 1:
                logger.warning(f"Model predicted very low limit ({recommended_limit}), setting to minimum of 1")
                recommended_limit = 1
                confidence = 0.6  # Lower confidence for clamped values
            
            return {
                "recommended_limit": recommended_limit,
                "confidence": float(confidence),
                "reasoning": "ML-based optimization using historical patterns"
            }
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            tier = user_features.get("user_tier", "free")
            default_limits = {"free": 60, "premium": 150, "enterprise": 500}
            
            return {
                "recommended_limit": default_limits.get(tier, 60),
                "confidence": 0.5,
                "reasoning": f"Fallback to default (error: {str(e)})"
            }
    
    async def forecast_traffic(
        self,
        historical_data: List[Dict[str, Any]],
        periods_ahead: int = 6
    ) -> Dict[str, Any]:
        """
        Forecast traffic using local Prophet model
        """
        if self.prophet_model is None:
            # Return simple trend-based forecast
            logger.warning("Prophet model not available, using simple forecast")
            
            if not historical_data:
                return {
                    "predictions": [],
                    "trend": "unknown",
                    "confidence": 0.2
                }
            
            # Simple moving average forecast
            recent_values = [d.get("requests", 0) for d in historical_data[-10:]]
            avg = np.mean(recent_values) if recent_values else 100
            
            predictions = []
            for i in range(periods_ahead):
                predictions.append({
                    "timestamp": (datetime.utcnow() + timedelta(minutes=5*(i+1))).isoformat(),
                    "requests": int(avg),
                    "lower": int(avg * 0.8),
                    "upper": int(avg * 1.2)
                })
            
            return {
                "predictions": predictions,
                "trend": "stable",
                "confidence": 0.4
            }
        
        try:
            # Prepare data for Prophet
            df = pd.DataFrame(historical_data)
            if 'timestamp' in df.columns and 'requests' in df.columns:
                df = df.rename(columns={'timestamp': 'ds', 'requests': 'y'})
                df['ds'] = pd.to_datetime(df['ds'])
            else:
                raise ValueError("historical_data must have 'timestamp' and 'requests' fields")
            
            # Make forecast
            future = self.prophet_model.make_future_dataframe(periods=periods_ahead, freq='5min')
            forecast = self.prophet_model.predict(future)
            
            # Extract predictions
            predictions = []
            for idx in range(-periods_ahead, 0):
                row = forecast.iloc[idx]
                predictions.append({
                    "timestamp": row['ds'].isoformat(),
                    "requests": int(row['yhat']),
                    "lower": int(row['yhat_lower']),
                    "upper": int(row['yhat_upper'])
                })
            
            # Determine trend
            trend_values = forecast['trend'].tail(periods_ahead).values
            if trend_values[-1] > trend_values[0] * 1.1:
                trend = "increasing"
            elif trend_values[-1] < trend_values[0] * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
            
            return {
                "predictions": predictions,
                "trend": trend,
                "confidence": 0.80
            }
        except Exception as e:
            logger.error(f"Forecast error: {str(e)}")
            
            # Fallback to simple forecast
            recent_values = [d.get("requests", 0) for d in historical_data[-10:]]
            avg = np.mean(recent_values) if recent_values else 100
            
            predictions = []
            for i in range(periods_ahead):
                predictions.append({
                    "timestamp": (datetime.utcnow() + timedelta(minutes=5*(i+1))).isoformat(),
                    "requests": int(avg),
                    "lower": int(avg * 0.8),
                    "upper": int(avg * 1.2)
                })
            
            return {
                "predictions": predictions,
                "trend": "stable",
                "confidence": 0.3,
                "error": str(e)
            }


# Global instance
ml_fallback = MLFallbackService()
