# 🚀 Intelligent Rate Limiter - ML Model Deployment Guide

This guide details the complete process for training the machine learning models locally and deploying them to AWS SageMaker.

## 📋 Prerequisites

Before starting, ensure you have:
1. **Python 3.10+** installed.
2. **AWS Account** with permissions to create S3 buckets and SageMaker endpoints.
3. **AWS Credentials** (Access Key ID and Secret Access Key).

---

## 🛠️ Step 1: Environment Setup

We have created a dedicated requirements file for ML operations to avoid conflicts with backend dependencies.

```bash
cd Intelli_Rate
# Create virtual environment (if not exists)
python -m venv backend/venv

# Activate virtual environment
# Windows:
backend\venv\Scripts\activate
# Mac/Linux:
source backend/venv/bin/activate

# Install ML dependencies
pip install -r backend/requirements-ml.txt
```

---

## 🤖 Step 2: Train Models Locally

The training script generates synthetic data and trains three key models:
- **Isolation Forest**: For abuse detection.
- **XGBoost**: For optimizing rate limits.
- **Prophet**: For traffic forecasting.

**Run the training script:**
```bash
python backend/app/ml/training/train_all_models.py
```

✅ **Success Criteria:**
- Output shows "ALL MODELS TRAINED SUCCESSFULLY".
- Models are saved in the `ml-models/` directory.

---

## 🧹 Step 2.5: Clean Up Previous SageMaker Deployments (Optional)

If you have existing SageMaker endpoints from a previous deployment, you should clean them up before deploying new ones to avoid conflicts and unnecessary costs.

### 1. Preview What Will Be Deleted (Dry Run)
First, run the cleanup script in dry-run mode to see what resources exist:

```bash
python backend/scripts/cleanup_sagemaker.py --region us-east-1 --dry-run --all
```

This will show you all IntelliRate-related endpoints without deleting anything.

### 2. Delete Old Resources
Once you've confirmed what will be deleted, run the actual cleanup:

```bash
python backend/scripts/cleanup_sagemaker.py --region us-east-1 --all
```

**What this does:**
- Lists all IntelliRate endpoints in your AWS account
- Shows you what will be deleted and asks for confirmation
- Deletes endpoints (e.g., `isolation-forest-endpoint`)
- Deletes endpoint configurations
- Deletes SageMaker models

⚠️ **Note:** The script will prompt for confirmation before deleting anything (unless in dry-run mode).

### 3. Optional: Clean S3 Bucket
If you also want to remove old model artifacts from S3:

```bash
python backend/scripts/cleanup_sagemaker.py --region us-east-1 --all --clean-s3 your-bucket-name
```

---

## ☁️ Step 3: Deploy to AWS SageMaker

We use a custom script to upload models to S3 and properly configure SageMaker endpoints.

### 1. Configure Credentials
Set your AWS credentials in the terminal (Windows CMD example):
```cmd
set AWS_ACCESS_KEY_ID=your_access_key
set AWS_SECRET_ACCESS_KEY=your_secret_key
set AWS_DEFAULT_REGION=us-east-1
```

### 2. Run Deployment
Execute the deployment script. Replace `your-unique-bucket-name` with a unique name (e.g., `intellirate-models-2025`).

```bash
python backend/scripts/deploy_to_aws.py --model all --bucket your-unique-bucket-name
```

**What this script does:**
1. Creates an S3 bucket (if it doesn't exist).
2. Creates an IAM Role `IntelliRateSageMakerRole` for SageMaker.
3. Uploads trained model artifacts (`.tar.gz`) to S3.
4. Creates SageMaker Model definitions.
5. Deploys Endpoints (Configuration + Endpoint).

⏳ **Note:** Deployment takes **15-20 minutes** as AWS provisions the instances.

---

## ⚙️ Step 4: Configure Application

Once deployment completes, the script will output the **Endpoint Names**. Update your `.env` file with these values:

```ini
# .env file
USE_CLOUD_ML=true
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1

ISOLATION_FOREST_ENDPOINT_NAME=isolation-forest-endpoint
XGBOOST_ENDPOINT_NAME=xgboost-limiter-endpoint
PROPHET_ENDPOINT_NAME=prophet-forecaster-endpoint
```

---

## 🔍 Step 5: Troubleshooting

### Common Issues

1. **"MalformedPolicyDocument" Error**:
   - **Cause**: Incorrect JSON format in IAM role creation.
   - **Fix**: We have patched `deploy_to_aws.py` to use `json.dumps()`. Ensure you are using the latest version of the script.

2. **"Region not supported" Error**:
   - **Cause**: Trailing spaces in environment variables (e.g., `set REGION=us-east-1 `).
   - **Fix**: Run commands without spaces before `&&` or use `set "VAR=VAL"` syntax.

3. **SageMaker Dependency Issues**:
   - SageMaker SDK requires PyTorch 2.x and other large libraries. Ensure you are on a stable internet connection when installing dependencies.

4. **"Endpoint already exists" Error**:
   - **Cause**: An endpoint with the same name already exists.
   - **Fix**: Run the cleanup script first: `python backend/scripts/cleanup_sagemaker.py --region us-east-1 --all`

5. **Cleanup Script Issues**:
   - If cleanup fails partway through, you can manually delete resources in AWS Console:
     - Navigate to SageMaker → Endpoints
     - Delete endpoints, then endpoint configurations, then models
