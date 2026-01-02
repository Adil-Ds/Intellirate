"""
Test all ML models to ensure they're working
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/ml"

def test_abuse_detection():
    print("\n=== Testing Abuse Detection ===")
    data = {
        "features": {
            "requests_per_minute": 150,
            "unique_endpoints_accessed": 25,
            "error_rate_percentage": 20.5,
            "request_timing_patterns": 0.9,
            "ip_reputation_score": 0.2,
            "endpoint_diversity_score": 0.7
        }
    }
    response = requests.post(f"{BASE_URL}/detect-abuse", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_rate_limit_optimization():
    print("\n=== Testing Rate Limit Optimization ===")
    data = {
        "user_features": {
            "user_tier": "premium",
            "historical_avg_requests": 75.0,
            "behavioral_consistency": 0.85,
            "endpoint_usage_patterns": 0.7,
            "time_of_day_patterns": 0.6,
            "burst_frequency": 0.3
        }
    }
    response = requests.post(f"{BASE_URL}/optimize-rate-limit", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_traffic_forecast():
    print("\n=== Testing Traffic Forecasting ===")
    data = {
        "historical_data": [
            {"timestamp": "2024-01-01T00:00:00Z", "requests": 100},
            {"timestamp": "2024-01-01T01:00:00Z", "requests": 120},
            {"timestamp": "2024-01-01T02:00:00Z", "requests": 110},
            {"timestamp": "2024-01-01T03:00:00Z", "requests": 130},
            {"timestamp": "2024-01-01T04:00:00Z", "requests": 115}
        ],
        "periods_ahead": 6
    }
    response = requests.post(f"{BASE_URL}/forecast-traffic", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_health():
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

if __name__ == "__main__":
    print("Testing ML API Endpoints...")
    print("="*50)
    
    try:
        # Test health first
        health = test_health()
        
        # Test all models
        abuse_result = test_abuse_detection()
        rate_limit_result = test_rate_limit_optimization()
        traffic_result = test_traffic_forecast()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS COMPLETED")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
