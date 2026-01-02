
import boto3
import sys

def check_creds():
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"SUCCESS: Connected as {identity['Arn']}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to connect to AWS: {str(e)}")
        print("\nPlease configure AWS credentials via environment variables or ~/.aws/credentials")
        return False

if __name__ == "__main__":
    success = check_creds()
    sys.exit(0 if success else 1)
