"""
Test locally trained ML models
Usage: python test_local_models.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import logging
from app.services.ml_fallback_service import ml_fallback
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_abuse_detection():
    """Test Isolation Forest for abuse detection"""
    logger.info("\n" + "="*60)
    logger.info("Testing Abuse Detection (Isolation Forest)")
    logger.info("="*60)
    
    # Test normal behavior
    normal_features = {
        "requests_per_minute": 50,
        "unique_endpoints_accessed": 5,
        "error_rate_percentage": 2,
        "request_timing_patterns": 0.8,
        "ip_reputation_score": 0.9,
        "endpoint_diversity_score": 0.3
    }
    
    result = await ml_fallback.predict_abuse(normal_features)
    logger.info(f"\n Normal Behavior:")
    logger.info(f"  - Anomaly Score: {result['anomaly_score']:.3f}")
    logger.info(f"  - Is Abusive: {result['is_abusive']}")
    logger.info(f"  - Confidence: {result['confidence']:.3f}")
    
    # Test abusive behavior
    abusive_features = {
        "requests_per_minute": 250,
        "unique_endpoints_accessed": 25,
        "error_rate_percentage": 35,
        "request_timing_patterns": 0.2,
        "ip_reputation_score": 0.1,
        "endpoint_diversity_score": 0.9
    }
    
    result = await ml_fallback.predict_abuse(abusive_features)
    logger.info(f"\n Abusive Behavior:")
    logger.info(f"  - Anomaly Score: {result['anomaly_score']:.3f}")
    logger.info(f"  - Is Abusive: {result['is_abusive']}")
    logger.info(f"  - Confidence: {result['confidence']:.3f}")


async def test_rate_limit_optimization():
    """Test XGBoost for rate limit optimization"""
    logger.info("\n" + "="*60)
    logger.info("Testing Rate Limit Optimization (XGBoost)")
    logger.info("="*60)
    
    tiers = [
        ("free", 40, 0.6),
        ("premium", 120, 0.85),
        ("enterprise", 350, 0.92)
    ]
    
    for tier, avg_requests, consistency in tiers:
        user_features = {
            "user_tier": tier,
            "historical_avg_requests": avg_requests,
            "behavioral_consistency": consistency,
            "endpoint_usage_patterns": 0.7,
            "time_of_day_patterns": 0.6,
            "burst_frequency": 0.4
        }
        
        result = await ml_fallback.optimize_rate_limit(user_features)
        logger.info(f"\n{tier.capitalize()} Tier:")
        logger.info(f"  - Recommended Limit: {result['recommended_limit']} req/hr")
        logger.info(f"  - Confidence: {result['confidence']:.3f}")
        logger.info(f"  - Reasoning: {result['reasoning']}")


async def test_traffic_forecasting():
    """Test Prophet for traffic forecasting"""
    logger.info("\n" + "="*60)
    logger.info("Testing Traffic Forecasting (Prophet)")
    logger.info("="*60)
    
    # Generate sample historical data
    historical_data = []
    base_time = datetime.utcnow() - timedelta(hours=2)
    
    for i in range(24):  # Last 2 hours (24 * 5min intervals)
        timestamp = base_time + timedelta(minutes=5*i)
        # Simulate traffic pattern
        hour = timestamp.hour
        base_requests = 100 + 50 * (0.5 + 0.5 * (hour >= 9 and hour <= 17))
        
        historical_data.append({
            "timestamp": timestamp.isoformat(),
            "requests": int(base_requests + (i % 3) * 10)
        })
    
    result = await ml_fallback.forecast_traffic(historical_data, periods_ahead=6)
    
    logger.info(f"\nHistorical data points: {len(historical_data)}")
    logger.info(f"Forecast periods: {len(result['predictions'])}")
    logger.info(f"Trend: {result['trend']}")
    logger.info(f"Confidence: {result['confidence']:.3f}")
    
    logger.info("\nForecasted traffic (next 30 minutes):")
    for pred in result['predictions'][:3]:  # Show first 3 predictions
        logger.info(f"  {pred['timestamp']}: {pred['requests']} requests (±{pred['upper']-pred['lower']} range)")


async def main():
    """Run all tests"""
    logger.info("\n" + "="*80)
    logger.info(" ML MODELS LOCAL TESTING SUITE")
    logger.info("="*80)
    
    try:
        await test_abuse_detection()
        await test_rate_limit_optimization()
        await test_traffic_forecasting()
        
        logger.info("\n" + "="*80)
        logger.info("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        logger.info("\nModels are ready for:")
        logger.info("1. Local usage (set USE_CLOUD_ML=false)")
        logger.info("2. Cloud deployment (python scripts/deploy_to_cloud.py)")
        
    except Exception as e:
        logger.error(f"\n❌ Testing failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
