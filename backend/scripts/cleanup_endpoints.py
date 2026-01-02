"""
Delete failed SageMaker endpoints to allow fresh deployment
"""
import os
import boto3
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Credentials are loaded from environment variables automatically by boto3
# Make sure these are set in your .env file:
# AWS_ACCESS_KEY_ID=your_key_here
# AWS_SECRET_ACCESS_KEY=your_secret_here
# AWS_DEFAULT_REGION=us-east-1


client = boto3.client('sagemaker', region_name='us-east-1')

endpoints_to_delete = [
    'isolation-forest-endpoint',
    'xgboost-limiter-endpoint',
    'prophet-forecaster-endpoint'
]

for endpoint_name in endpoints_to_delete:
    try:
        print(f"Deleting endpoint: {endpoint_name}")
        client.delete_endpoint(EndpointName=endpoint_name)
        print(f"✓ Deleted: {endpoint_name}")
    except client.exceptions.ClientError as e:
        if 'Could not find endpoint' in str(e):
            print(f"  (Endpoint {endpoint_name} does not exist)")
        else:
            print(f"  Error: {e}")

print("\n✅ Cleanup complete. You can now redeploy.")
