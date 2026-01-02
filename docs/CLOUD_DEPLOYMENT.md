# AWS SageMaker Deployment Guide

## Prerequisites

1. **AWS Account** with billing enabled
2. **AWS CLI** installed: https://aws.amazon.com/cli/
3. **Authenticated CLI**: `aws configure`
4. **Python 3.11+** with virtual environment

---

## Step 1: AWS Account Setup

### Install AWS CLI

**Windows:**
```powershell
# Download installer
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Verify installation
aws --version
```

**Linux/Mac:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify
aws --version
```

### Configure AWS Credentials

```bash
aws configure

# You'll be prompted for:
AWS Access Key ID: <your-access-key>
AWS Secret Access Key: <your-secret-key>
Default region name: us-east-1
Default output format: json
```

> [!TIP]
> Get your credentials from AWS IAM Console: https://console.aws.amazon.com/iam/home#/security_credentials

---

## Step 2: Create IAM User for SageMaker

### Create IAM User

1. Go to IAM Console: https://console.aws.amazon.com/iam/
2. Click **Users** → **Add users**
3. Username: `intellirate-ml-user`
4. Access type: ✅ **Programmatic access**
5. Click **Next: Permissions**

### Attach Policies

Attach these managed policies:
- ✅ **AmazonSageMakerFullAccess**
- ✅ **AmazonS3FullAccess**
- ✅ **IAMFullAccess** (for role creation)

6. Click **Next** → **Create user**
7. **IMPORTANT:** Download the credentials CSV file
   - Copy **Access Key ID**
   - Copy **Secret Access Key**

---

## Step 3: Create S3 Bucket

```bash
# Set your bucket name (must be globally unique)
export BUCKET_NAME="intellirate-ml-models-$(date +%s)"
export REGION="us-east-1"

# Create S3 bucket
aws s3 mb s3://$BUCKET_NAME --region $REGION

# Verify bucket
aws s3 ls | grep intellirate

# Expected output:
# 2024-12-10 14:05:00 intellirate-ml-models-1733835900
```

> [!NOTE]
> S3 bucket names must be globally unique. The command above adds a timestamp to ensure uniqueness.

---

## Step 4: Train Models Locally

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Train all models (takes 2-3 minutes)
python app/ml/training/train_all_models.py

# Test models locally
python scripts/test_local_models.py

# Expected output:
# ✅ ALL MODELS TRAINED SUCCESSFULLY
# Models saved to: ml-models/
```

---

## Step 5: Deploy Models to SageMaker

```bash
# Deploy all models (takes 20-30 minutes)
python scripts/deploy_to_aws.py \
    --model all \
    --region $REGION \
    --bucket $BUCKET_NAME

# The script will:
# 1. Create IAM execution role for SageMaker
# 2. Package models as tar.gz files
# 3. Upload to S3
# 4. Create SageMaker models
# 5. Create endpoint configurations
# 6. Deploy endpoints

# Output will show endpoint names:
# ✅ DEPLOYMENT COMPLETE!
# ISOLATION_FOREST_ENDPOINT_NAME=isolation-forest-endpoint
# XGBOOST_ENDPOINT_NAME=xgboost-limiter-endpoint
# PROPHET_ENDPOINT_NAME=prophet-forecaster-endpoint
```

> [!IMPORTANT]
> **Cost Alert:** SageMaker endpoints cost ~$0.05/hour per instance (~$35/month per endpoint). The deployment uses `ml.t2.medium` instances to minimize costs.

---

## Step 6: Update Environment Variables

```bash
# Copy .env.example to .env
cd backend
cp .env.example .env

# Edit .env file
notepad .env  # Windows
nano .env     # Linux/Mac

# Update these lines with your actual values:
AWS_ACCESS_KEY_ID=your-actual-access-key
AWS_SECRET_ACCESS_KEY=your-actual-secret-key
AWS_DEFAULT_REGION=us-east-1

# Paste the endpoint names from previous step:
ISOLATION_FOREST_ENDPOINT_NAME=isolation-forest-endpoint
XGBOOST_ENDPOINT_NAME=xgboost-limiter-endpoint
PROPHET_ENDPOINT_NAME=prophet-forecaster-endpoint

# Enable cloud ML
USE_CLOUD_ML=true
ENABLE_ML_FALLBACK=true

# Update S3 bucket
S3_BUCKET_NAME=your-actual-bucket-name
```

---

## Step 7: Start Application

```bash
# Return to project root
cd ..

# Start all services with Docker Compose
docker-compose up -d

# Check backend logs
docker-compose logs -f backend

# You should see:
# ✓ Redis connected
# ✓ Initialized AWS SageMaker Client for region: us-east-1
# ✓ Application started successfully
```

---

## Step 8: Test Deployment

### Test via API Documentation

1. Open browser: http://localhost:8000/docs
2. Navigate to `/api/v1/ml/detect-abuse`
3. Click **Try it out**
4. Use sample request:

```json
{
  "features": {
    "requests_per_minute": 150,
    "unique_endpoints_accessed": 20,
    "error_rate_percentage": 15.5,
    "request_timing_patterns": 0.8,
    "ip_reputation_score": 0.3,
    "endpoint_diversity_score": 0.6
  }
}
```

5. Click **Execute**
6. Check response - `"source"` should be `"cloud"`

### Test via cURL

```bash
curl -X POST "http://localhost:8000/api/v1/ml/detect-abuse" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "requests_per_minute": 150,
      "unique_endpoints_accessed": 20,
      "error_rate_percentage": 15.5,
      "request_timing_patterns": 0.8,
      "ip_reputation_score": 0.3,
      "endpoint_diversity_score": 0.6
    }
  }'
```

---

## Monitoring & Management

### View Endpoints in AWS Console

**SageMaker Console:**
1. Navigate to: https://console.aws.amazon.com/sagemaker/
2. Click **Endpoints** in left sidebar
3. View each endpoint:
   - **Status**: InService / Creating / Failed
   - **Instance type**: ml.t2.medium
   - **Invocations**: Request count
   - **Latency**: P50, P90, P99

### AWS CLI Commands

```bash
# List all endpoints
aws sagemaker list-endpoints --region $REGION

# Get endpoint details
aws sagemaker describe-endpoint \
    --endpoint-name isolation-forest-endpoint \
    --region $REGION

# View CloudWatch metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/SageMaker \
    --metric-name ModelLatency \
    --dimensions Name=EndpointName,Value=isolation-forest-endpoint \
    --start-time 2024-12-10T00:00:00Z \
    --end-time 2024-12-10T23:59:59Z \
    --period 3600 \
    --statistics Average
```

### Monitor Costs

```bash
# View current month costs
aws ce get-cost-and-usage \
    --time-period Start=2024-12-01,End=2024-12-31 \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --group-by Type=SERVICE

# Set up billing alerts in AWS Console:
# Navigation > Billing > Budgets > Create budget
# Recommended: $100/month alert threshold
```

### CloudWatch Dashboard

1. Navigate to: https://console.aws.amazon.com/cloudwatch/
2. Click **Dashboards** → **Create dashboard**
3. Add widgets for:
   - **Invocations**: SageMaker endpoint invocation count
   - **Model Latency**: P50, P90, P99 latency
   - **4XX Errors**: Client errors
   - **5XX Errors**: Server errors

---

## Rollback Plan

If AWS deployment fails, switch to local models:

```bash
# 1. Update .env
USE_CLOUD_ML=false

# 2. Restart backend
docker-compose restart backend

# 3. Verify local models work
docker-compose exec backend python scripts/test_local_models.py
```

---

## Cost Optimization

### Auto-Scaling Configuration

Update endpoint configuration for auto-scaling:

```bash
# Create scaling policy
aws application-autoscaling register-scalable-target \
    --service-namespace sagemaker \
    --resource-id endpoint/isolation-forest-endpoint/variant/AllTraffic \
    --scalable-dimension sagemaker:variant:DesiredInstanceCount \
    --min-capacity 0 \
    --max-capacity 10

# Set scaling policy
aws application-autoscaling put-scaling-policy \
    --service-namespace sagemaker \
    --scalable-dimension sagemaker:variant:DesiredInstanceCount \
    --resource-id endpoint/isolation-forest-endpoint/variant/AllTraffic \
    --policy-name scale-on-invocations \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
        "TargetValue": 1000.0,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "SageMakerVariantInvocationsPerInstance"
        },
        "ScaleInCooldown": 300,
        "ScaleOutCooldown": 60
    }'
```

### Estimated Monthly Costs

For 1M predictions/month with `ml.t2.medium` instances:

| Service | Cost |
|---------|------|
| SageMaker Endpoints (3 endpoints × 24/7) | ~$105/month |
| Prediction API calls | ~$0.50 |
| S3 Storage | ~$1.00 |
| Data Transfer | ~$5.00 |
| **Total** | **~$111.50/month** |

### Cost Reduction Tips

1. **Use Serverless Endpoints** (for low-traffic):
   ```python
   # In deploy_to_aws.py, use ServerlessConfig instead of instance count
   ```

2. **Delete unused endpoints**:
   ```bash
   aws sagemaker delete-endpoint --endpoint-name endpoint-name
   ```

3. **Use Spot Instances** for training:
   - 70% cost savings on model training

---

## Troubleshooting

### Issue: "Endpoint creation failed"

```bash
# Check endpoint status
aws sagemaker describe-endpoint --endpoint-name isolation-forest-endpoint

# Check CloudWatch logs
aws logs tail /aws/sagemaker/Endpoints/isolation-forest-endpoint --follow
```

**Common causes:**
- Insufficient IAM permissions
- Model artifact not found in S3
- Invalid container image

### Issue: "Authentication failed"

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Expected output: Account ID and User ARN
# If error: re-run aws configure
```

### Issue: "Timeout on predictions"

```bash
# Increase timeout in .env
ML_PREDICTION_TIMEOUT=10  # Increase from 5 to 10 seconds

# Restart
docker-compose restart backend
```

### Issue: "Throttling errors"

```bash
# Check service quotas
aws service-quotas list-service-quotas \
    --service-code sagemaker

# Request quota increase:
# Console > Service Quotas > AWS services > SageMaker
# Select quota > Request quota increase
```

---

## Next Steps

- ✅ **Set up CloudWatch alarms**: Create alerts for endpoint failures
- ✅ **Enable VPC endpoints**: Improve security and reduce costs
- ✅ **Model versioning**: Deploy multiple versions for A/B testing
- ✅ **Automate retraining**: Set up scheduled Lambda for retraining
- ✅ **Cost optimization**: Implement auto-scaling and serverless endpoints

---

## Additional Resources

- [AWS SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [SageMaker Pricing](https://aws.amazon.com/sagemaker/pricing/)
- [AWS Free Tier](https://aws.amazon.com/free/)
- [SageMaker Examples](https://github.com/aws/amazon-sagemaker-examples)
- [AWS Support](https://aws.amazon.com/support/)

---

## Comparison: GCP vs AWS

| Feature | Google Cloud (Vertex AI) | AWS (SageMaker) |
|---------|-------------------------|-----------------|
| **Endpoint Cost** | ~$0.04/hour | ~$0.05/hour |
| **Auto-scaling** | 0-100 instances | 0-unlimited |
| **Free Tier** | $300 credit (90 days) | 250 hours/month (2 months) |
| **Container Support** | Pre-built + Custom | Pre-built + Custom |
| **Monitoring** | Cloud Monitoring | CloudWatch |
| **Storage** | Cloud Storage (GCS) | S3 |

**Migration Benefits:**
✅ More mature ML platform  
✅ Better integration with AWS services  
✅ Larger community and examples  
✅ Superior auto-scaling options
