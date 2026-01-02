"""
Test suite for cloud ML service
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.cloud_ml_service import GoogleCloudMLClient


@pytest.mark.asyncio
class TestCloudMLIntegration:
    
    async def test_abuse_detection_local_fallback(self):
        """Test that local fallback works correctly"""
        ml_client = GoogleCloudMLClient()
        ml_client.use_cloud = False  # Force local mode
        
        features = {
            "requests_per_minute": 150,
            "unique_endpoints_accessed": 20,
            "error_rate_percentage": 15.5,
            "request_timing_patterns": 0.8,
            "ip_reputation_score": 0.3,
            "endpoint_diversity_score": 0.6
        }
        
        result = await ml_client.predict_abuse(features)
        
        assert "anomaly_score" in result
        assert "is_abusive" in result
        assert result["source"] == "fallback"
        assert 0 <= result["anomaly_score"] <= 1
    
    async def test_rate_limit_optimization_fallback(self):
        """Test rate limit optimization with fallback"""
        ml_client = GoogleCloudMLClient()
        ml_client.use_cloud = False
        
        user_features = {
            "user_tier": "premium",
            "historical_avg_requests": 120,
            "behavioral_consistency": 0.85,
        }
        
        result = await ml_client.optimize_rate_limit(user_features)
        
        assert "recommended_limit" in result
        assert result["recommended_limit"] > 0
        assert result["source"] == "fallback"
    
    async def test_traffic_forecast_fallback(self):
        """Test traffic forecasting with fallback"""
        ml_client = GoogleCloudMLClient()
        ml_client.use_cloud = False
        
        from datetime import datetime, timedelta
        
        historical_data = []
        for i in range(12):
            historical_data.append({
                "timestamp": (datetime.utcnow() - timedelta(minutes=5*(12-i))).isoformat(),
                "requests": 100 + i * 5
            })
        
        result = await ml_client.forecast_traffic(historical_data, periods_ahead=6)
        
        assert "predictions" in result
        assert len(result["predictions"]) == 6
        assert "trend" in result
        assert result["source"] == "fallback"


@pytest.mark.asyncio
class TestMLFallbackService:
    
    async def test_abuse_detection_without_model(self):
        """Test that service handles missing model gracefully"""
        from app.services.ml_fallback_service import ml_fallback
        
        # Force model to None
        ml_fallback._isolation_forest_model = None
        
        features = {
            "requests_per_minute": 50,
            "unique_endpoints_accessed": 5,
            "error_rate_percentage": 2,
            "request_timing_patterns": 0.8,
            "ip_reputation_score": 0.9,
            "endpoint_diversity_score": 0.3
        }
        
        result = await ml_fallback.predict_abuse(features)
        
        # Should return safe default
        assert result["anomaly_score"] == 0.5
        assert result["is_abusive"] == False
