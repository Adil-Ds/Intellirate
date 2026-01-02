# 🚀 Quick Start Guide

Get IntelliRate Gateway running in **5 minutes** (local mode) or **30 minutes** (with AWS SageMaker).

---

## Option 1: Local Development (No Cloud - 5 Minutes)

Perfect for testing and development without AWS.

### Step 1: Clone & Configure
```bash
cd Intelli_Rate
cp .env.example .env
```

### Step 2: Update .env
```bash
# Edit .env file:
nano .env  # Or use your preferred editor

# Set these values:
USE_CLOUD_ML=false              # Disable cloud ML
ENABLE_ML_FALLBACK=true         # Enable local models
SECRET_KEY=change-this-secret   # Any random string
```

### Step 3: Train Local Models
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Train models (2-3 minutes)
python app/ml/training/train_all_models.py

# Test models
python scripts/test_local_models.py
```

### Step 4: Start Services
```bash
# Return to root directory
cd ..

# Start with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

### Step 5: Access & Test
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **N8N Automation**: http://localhost:5678 (admin/admin)

**Test Abuse Detection:**
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

Expected response: `"source": "fallback"` (using local models)

---

## Option 2: AWS SageMaker Deployment (30 Minutes)

Full production setup with AWS SageMaker.

### Prerequisites
- AWS account with billing enabled
- AWS CLI installed: https://aws.amazon.com/cli/

### Step 1: AWS Setup
```bash
export BUCKET_NAME="intellirate-ml-models-$(date +%s)"
export REGION="us-east-1"

# Configure AWS CLI
aws configure
# Enter Access Key ID
# Enter Secret Access Key  
# Enter region: us-east-1
# Enter output format: json
```

### Step 2: Create S3 Bucket
```bash
# Create S3 bucket
aws s3 mb s3://$BUCKET_NAME --region $REGION

# Verify
aws s3 ls | grep intellirate
```

### Step 3: Train Local Models
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Train models
python app/ml/training/train_all_models.py
```

### Step 4: Deploy to SageMaker
```bash
# Deploy all models (20-30 minutes)
python scripts/deploy_to_aws.py \
    --model all \
    --region $REGION \
    --bucket $BUCKET_NAME

# Copy the endpoint names from output!
```

### Step 5: Configure .env
```bash
cd ..
cp .env.example .env
nano .env

# Update these values:
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1

# Paste endpoint names from previous step:
ISOLATION_FOREST_ENDPOINT_NAME=isolation-forest-endpoint
XGBOOST_ENDPOINT_NAME=xgboost-limiter-endpoint
PROPHET_ENDPOINT_NAME=prophet-forecaster-endpoint

# Update S3 bucket:
S3_BUCKET_NAME=your-bucket-name

# Enable cloud ML:
USE_CLOUD_ML=true
ENABLE_ML_FALLBACK=true
```

### Step 6: Start Application
```bash
docker-compose up -d
docker-compose logs -f backend
```

### Step 7: Test Cloud Integration
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

Expected response: `"source": "cloud"` ✅

---

## Troubleshooting

### Issue: Docker build fails
```bash
# Restart Docker Desktop
# Try with --no-cache:
docker-compose build --no-cache
```

### Issue: Models not training
```bash
# Check Python version (must be 3.11+)
python --version

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Issue: Cloud deployment fails
```bash
# Check authentication
aws sts get-caller-identity

# Check SageMaker endpoints
aws sagemaker list-endpoints --region us-east-1

# Check CloudWatch logs
aws logs tail /aws/sagemaker/Endpoints/isolation-forest-endpoint --follow
```

### Issue: API returns 500 errors
```bash
# Check backend logs
docker-compose logs backend

# Restart services
docker-compose restart backend
```

---

## Next Steps

- 📚 **Full Documentation**: See [README.md](README.md)
- ☁️ **Cloud Guide**: See [docs/CLOUD_DEPLOYMENT.md](docs/CLOUD_DEPLOYMENT.md)
- 🔧 **API Reference**: http://localhost:8000/docs
- 📊 **Monitor Cloud**: https://console.aws.amazon.com/sagemaker/home#/endpoints

---

## Support

- **Documentation**: `/docs` directory
- **Issues**: Create GitHub issue
- **Cloud Help**: AWS Support Console

**Estimated Costs (Cloud Mode):**
- Development: ~$35/month
- Production (1M predictions): ~$106/month
- **Free tier**: 250 hours/month for 2 months
