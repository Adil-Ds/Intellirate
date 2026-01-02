# AWS SageMaker Setup

This directory contains files for AWS SageMaker deployment.

## Contents

- `aws-credentials.json.example` - Template for AWS credentials (deprecated - use environment variables instead)
- `deployment/` - Model deployment configurations
- `monitoring/` - CloudWatch dashboards and alert policies
- `terraform/` - Infrastructure as Code (optional)

## Quick Setup

1. **Configure AWS credentials:**
   ```bash
   aws configure
   # Enter your Access Key ID
   # Enter your Secret Access Key
   # Default region: us-east-1
   # Default output: json
   ```

2. **Update .env file:**
   ```bash
   cd ../backend
   cp .env.example .env
   nano .env
   ```
   
   Update these variables:
   ```bash
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_DEFAULT_REGION=us-east-1
   ```

3. **Deploy models:**
   ```bash
   cd backend
   python scripts/deploy_to_aws.py --model all --region us-east-1 --bucket your-bucket-name
   ```

## Security

⚠️ **NEVER commit AWS credentials to version control!**

Best practices:
- Use AWS CLI configuration (`aws configure`)
- Use environment variables in `.env` file
- Use IAM roles when running on EC2/ECS
- Enable MFA on your AWS account

The `.gitignore` file is configured to exclude:
- `secrets/`
- `.env`
- `aws-credentials.json`

## Next Steps

See [../docs/CLOUD_DEPLOYMENT.md](../docs/CLOUD_DEPLOYMENT.md) for complete deployment guide.
