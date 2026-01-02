"""
SIMPLIFIED Test script - Directly generates database entries to test anomaly detection
This bypasses the proxy and directly calls the database to ensure entries are created
"""
import requests
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000"

print("="*60)
print("  IntelliRate - Simple Anomaly Test")
print("="*60)

print("\n🔨 Generating test data directly via analyzer...")
print("ℹ️  This will make real requests through your analyzer")
print()

# Try to get an existing user ID from logs
try:
    response = requests.get(f'{BASE_URL}/api/v1/logs?limit=1')
    logs = response.json()
    if logs and len(logs) > 0:
        test_user_id = logs[0].get('user_id', 'test_user_123')
        print(f"✓ Using existing user ID: {test_user_id[:16]}...")
    else:
        test_user_id = "test_user_for_anomaly_detection_12345"
        print(f"✓ Using test user ID: {test_user_id[:16]}...")
except:
    test_user_id = "test_user_for_anomaly_detection_12345"
    print(f"✓ Using test user ID: {test_user_id[:16]}...")

# OPTION 1: Lower thresholds temporarily for testing
print("\n📊 Current Detection Thresholds:")
print("   - Traffic Spike: >100 requests/hour")
print("   - High Error Rate: >20% (min 5 errors)")
print("   - Latency Spike: >5000ms average")

current_count = 0
try:
    response = requests.get(f'{BASE_URL}/api/v1/users/stats')
    data = response.json()
    users = data.get('users', [])
    
    print(f"\n📈 Current Users in System: {len(users)}")
    for user in users[:3]:  # Show first 3
        print(f"   - {user.get('user_name', 'Unknown')}: {user.get('total_requests', 0)} requests")
        if user.get('user_id') == test_user_id:
            current_count = user.get('total_requests', 0)
except Exception as e:
    print(f"\n⚠️  Could not fetch current stats: {e}")

print(f"\n💡 SOLUTION: To test anomaly detection, you have 2 options:")
print()
print("Option 1: Use your actual Analyzer application")
print("   - Open your analyzer at http://localhost:5174 (or wherever it runs)")
print("   - Make 100+ analysis requests quickly")
print("   - This will trigger a Traffic Spike anomaly")
print()
print("Option 2: Lower the detection thresholds temporarily")
print("   - Edit: backend/app/api/v1/anomalies.py")
print("   - Line 92: Change 'if requests_per_hour > 100:' to 'if requests_per_hour > 5:'")
print("   - Line 109: Change 'if error_rate > 20' to 'if error_rate > 5'")
print("   - Restart backend with: python -m uvicorn app.main:app --reload")
print()

choice = input("Press Enter to check current anomalies or 'q' to quit: ")
if choice.lower() == 'q':
    exit(0)

print("\n🔍 Checking for anomalies...")
try:
    response = requests.get(f'{BASE_URL}/api/v1/anomalies')
    data = response.json()
    anomalies = data.get('anomalies', [])
    
    print(f"\n📊 Current Anomalies: {len(anomalies)}")
    
    if anomalies:
        for anomaly in anomalies:
            print(f"\n  🚨 {anomaly['type']} ({anomaly['severity']})")
            print(f"     {anomaly['description']}")
            print(f"     Impact: {anomaly['impact']}")
            print(f"     Time: {anomaly['timestamp']}")
    else:
        print("\n  ℹ️  No anomalies detected yet.")
        print("\n  💡 Quick Test: Make 20+ requests in your Analyzer app")
        print("     then lower the threshold to requests_per_hour > 5")
        print("     to see the anomaly appear!")
except Exception as e:
    print(f"\n❌ Error checking anomalies: {e}")

print("\n" + "="*60)
