"""
Test script to generate anomalies for testing the Anomaly Detection system
This will create different types of anomalies by making requests to your backend
"""
import requests
import time
import random

BASE_URL = "http://localhost:8000"

def generate_traffic_spike(num_requests=150):
    """
    Generate a traffic spike anomaly (>100 requests/hour)
    """
    print(f"🚦 Generating traffic spike with {num_requests} requests...")
    success = 0
    
    for i in range(num_requests):
        try:
            # Make request through proxy endpoint
            response = requests.post(
                f'{BASE_URL}/api/v1/proxy/groq',
                json={
                    "model": "mixtral-8x7b-32768",
                    "messages": [{"role": "user", "content": f"Test message {i}"}],
                    "max_tokens": 10
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            success += 1
            if (i + 1) % 20 == 0:
                print(f"  ✓ Sent {i + 1}/{num_requests} requests (Success: {success})")
                time.sleep(0.1)  # Small delay to not overwhelm
        except Exception as e:
            if (i + 1) % 20 == 0:
                print(f"  ✗ Request {i + 1} failed: {str(e)[:50]}")
    
    print(f"✅ Traffic spike complete! ({success}/{num_requests} successful)")
    return success


def generate_high_error_rate(num_requests=50):
    """
    Generate high error rate anomaly (>20% errors)
    """
    print(f"❌ Generating high error rate with {num_requests} failed requests...")
    errors = 0
    
    for i in range(num_requests):
        try:
            # Try invalid endpoints to trigger errors
            endpoints = [
                '/api/v1/invalid-endpoint',
                '/api/v1/nonexistent',
                '/api/v1/test/error'
            ]
            response = requests.get(
                f'{BASE_URL}{random.choice(endpoints)}',
                timeout=5
            )
            errors += 1
        except:
            errors += 1
        
        if (i + 1) % 10 == 0:
            print(f"  ✗ Generated {i + 1}/{num_requests} errors")
            time.sleep(0.05)
    
    print(f"✅ Error generation complete! ({errors} errors)")
    return errors


def generate_latency_spike():
    """
    Generate latency anomaly by making resource-intensive requests
    """
    print("⏱️  Generating latency spike...")
    
    for i in range(30):
        try:
            # Make large requests that might cause latency
            response = requests.post(
                f'{BASE_URL}/api/v1/proxy/groq',
                json={
                    "model": "mixtral-8x7b-32768",
                    "messages": [
                        {"role": "user", "content": "Write a very long detailed essay" * 50}
                    ],
                    "max_tokens": 1000
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            if (i + 1) % 5 == 0:
                print(f"  ⏱️  Sent {i + 1}/30 large requests")
                time.sleep(0.2)
        except Exception as e:
            pass
    
    print("✅ Latency spike generation complete!")


def check_anomalies():
    """
    Check current anomalies
    """
    try:
        response = requests.get(f'{BASE_URL}/api/v1/anomalies')
        data = response.json()
        anomalies = data.get('anomalies', [])
        
        print(f"\n📊 Current Anomalies: {len(anomalies)}")
        for anomaly in anomalies:
            print(f"  - {anomaly['type']} ({anomaly['severity']}): {anomaly['description']}")
        
        return anomalies
    except Exception as e:
        print(f"❌ Failed to check anomalies: {e}")
        return []


def main():
    print("=" * 60)
    print("  IntelliRate Anomaly Testing Tool")
    print("=" * 60)
    print("\nSelect test type:")
    print("1. Traffic Spike (150 requests)")
    print("2. High Error Rate (50 failed requests)")
    print("3. Latency Spike (30 large requests)")
    print("4. All of the above")
    print("5. Check current anomalies")
    print("=" * 60)
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == '1':
        generate_traffic_spike()
    elif choice == '2':
        generate_high_error_rate()
    elif choice == '3':
        generate_latency_spike()
    elif choice == '4':
        print("\n🚀 Running all tests...\n")
        generate_traffic_spike(200)
        time.sleep(1)
        generate_high_error_rate(60)
        time.sleep(1)
        generate_latency_spike()
    elif choice == '5':
        check_anomalies()
        return
    else:
        print("❌ Invalid choice!")
        return
    
    # Wait a moment for data to be processed
    print("\n⏳ Waiting 2 seconds for data processing...")
    time.sleep(2)
    
    # Check anomalies
    print("\n" + "=" * 60)
    anomalies = check_anomalies()
    print("=" * 60)
    
    if anomalies:
        print(f"\n✅ SUCCESS! Generated {len(anomalies)} anomal{'y' if len(anomalies) == 1 else 'ies'}!")
        print(f"\n👉 Check http://localhost:5173/anomalies to see them!")
    else:
        print("\n⚠️  No anomalies detected yet. Try option 4 (All tests) or wait a moment.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
