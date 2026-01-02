"""
Complete deployment script for all 3 ML models to AWS SageMaker
Usage: python deploy_to_aws.py --model all --region us-east-1 --bucket your-s3-bucket
"""
import os
import sys
import argparse
import logging
import time
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import ClientError
    import joblib
    AWS_AVAILABLE = True
except ImportError:
    logger.warning("AWS SDK not available. Install with: pip install boto3 sagemaker")
    AWS_AVAILABLE = False


class SageMakerDeployer:
    """Deployer for ML models to AWS SageMaker"""
    
    def __init__(self, region: str, bucket_name: str):
        if not AWS_AVAILABLE:
            raise Exception("AWS SDK (boto3) not installed")
        
        self.region = region
        self.bucket_name = bucket_name
        
        # Initialize AWS clients
        self.s3_client = boto3.client('s3', region_name=region)
        self.sagemaker_client = boto3.client('sagemaker', region_name=region)
        self.iam_client = boto3.client('iam')
        
        # Ensure bucket exists
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
            logger.info(f"✓ Using S3 bucket: {bucket_name}")
        except ClientError:
            logger.info(f"Creating S3 bucket: {bucket_name}")
            try:
                if region == 'us-east-1':
                    self.s3_client.create_bucket(Bucket=bucket_name)
                else:
                    self.s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': region}
                    )
                logger.info(f"✓ Created bucket: {bucket_name}")
            except Exception as e:
                logger.error(f"Failed to create bucket: {str(e)}")
                raise
        
        # Get or create SageMaker execution role
        self.execution_role_arn = self._get_or_create_execution_role()
        
        logger.info(f"✓ Initialized deployer for region: {region}")
    
    def _get_or_create_execution_role(self) -> str:
        """Get or create IAM role for SageMaker"""
        role_name = "IntelliRateSageMakerRole"
        
        try:
            # Try to get existing role
            response = self.iam_client.get_role(RoleName=role_name)
            logger.info(f"✓ Using existing role: {role_name}")
            
            # Ensure S3 policy is attached (in case it was missing from previous deployment)
            try:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
                )
                logger.info(f"✓ Attached S3 policy to existing role")
            except self.iam_client.exceptions.from_code('PolicyNotAttachableException'):
                pass  # Already attached
            
            return response['Role']['Arn']
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create new role
            logger.info(f"Creating IAM role: {role_name}")
            
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "sagemaker.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Execution role for IntelliRate SageMaker models"
            )
            
            # Attach necessary policies
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/AmazonSageMakerFullAccess'
            )
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
            )
            
            # Wait for role to propagate
            time.sleep(10)
            
            logger.info(f"✓ Created role: {role_name}")
            return response['Role']['Arn']
    
    def deploy_isolation_forest(self, model_path: str) -> str:
        """Deploy Isolation Forest model to SageMaker"""
        logger.info("🚀 Deploying Isolation Forest...")
        
        # 1. Upload model to S3
        s3_path = self._upload_model_to_s3(
            local_path=model_path,
            s3_folder="isolation_forest"
        )
        logger.info(f"✓ Model uploaded to: {s3_path}")
        
        # 2. Create SageMaker Model
        model_name = f"isolation-forest-{int(time.time())}"
        
        # Use scikit-learn container
        account_id = boto3.client('sts').get_caller_identity()['Account']
        image_uri = f"{account_id}.dkr.ecr.{self.region}.amazonaws.com/sagemaker-scikit-learn:1.0-1-cpu-py3"
        
        # Try using pre-built container if custom image not available
        try:
            image_uri = sagemaker.image_uris.retrieve(
                framework='sklearn',
                region=self.region,
                version='1.0-1',
                py_version='py3',
                instance_type='ml.m5.large'
            )
        except:
            # Fallback to public sklearn container
            image_uri = f"683313688378.dkr.ecr.{self.region}.amazonaws.com/sagemaker-scikit-learn:1.0-1-cpu-py3"
        
        logger.info(f"✓ Using container: {image_uri}")
        
        try:
            self.sagemaker_client.create_model(
                ModelName=model_name,
                PrimaryContainer={
                    'Image': image_uri,
                    'ModelDataUrl': s3_path,
                    'Environment': {
                        'SAGEMAKER_PROGRAM': 'inference.py',
                        'SAGEMAKER_SUBMIT_DIRECTORY': s3_path
                    }
                },
                ExecutionRoleArn=self.execution_role_arn
            )
            logger.info(f"✓ Model created: {model_name}")
        except Exception as e:
            logger.error(f"Model creation failed: {str(e)}")
            raise
        
        # 3. Create Endpoint Configuration
        endpoint_config_name = f"{model_name}-config"
        
        try:
            self.sagemaker_client.create_endpoint_config(
                EndpointConfigName=endpoint_config_name,
                ProductionVariants=[{
                    'VariantName': 'AllTraffic',
                    'ModelName': model_name,
                    'InstanceType': 'ml.m5.large',
                    'InitialInstanceCount': 1,
                    'InitialVariantWeight': 1.0
                }]
            )
            logger.info(f"✓ Endpoint config created: {endpoint_config_name}")
        except Exception as e:
            logger.error(f"Endpoint config creation failed: {str(e)}")
            raise
        
        # 4. Create Endpoint
        endpoint_name = f"isolation-forest-endpoint"
        
        try:
            self.sagemaker_client.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_config_name
            )
            logger.info(f"✓ Creating endpoint: {endpoint_name}")
            logger.info("⏳ Waiting for endpoint to be in service (this may take 5-10 minutes)...")
            
            # Wait for endpoint to be in service
            waiter = self.sagemaker_client.get_waiter('endpoint_in_service')
            waiter.wait(EndpointName=endpoint_name)
            
            logger.info(f"✓ Endpoint deployed: {endpoint_name}")
            return endpoint_name
            
        except Exception as e:
            logger.error(f"Endpoint creation failed: {str(e)}")
            raise
    
    def deploy_xgboost(self, model_path: str) -> str:
        """Deploy XGBoost model to SageMaker"""
        logger.info("🚀 Deploying XGBoost...")
        
        s3_path = self._upload_model_to_s3(
            local_path=model_path,
            s3_folder="xgboost"
        )
        logger.info(f"✓ Model uploaded to: {s3_path}")
        
        model_name = f"xgboost-limiter-{int(time.time())}"
        
        # Use XGBoost container
        try:
            import sagemaker
            image_uri = sagemaker.image_uris.retrieve(
                framework='xgboost',
                region=self.region,
                version='1.5-1'
            )
        except:
            image_uri = f"683313688378.dkr.ecr.{self.region}.amazonaws.com/sagemaker-xgboost:1.5-1"
        
        try:
            self.sagemaker_client.create_model(
                ModelName=model_name,
                PrimaryContainer={
                    'Image': image_uri,
                    'ModelDataUrl': s3_path
                },
                ExecutionRoleArn=self.execution_role_arn
            )
            
            endpoint_config_name = f"{model_name}-config"
            self.sagemaker_client.create_endpoint_config(
                EndpointConfigName=endpoint_config_name,
                ProductionVariants=[{
                    'VariantName': 'AllTraffic',
                    'ModelName': model_name,
                    'InstanceType': 'ml.m5.large',
                    'InitialInstanceCount': 1,
                    'InitialVariantWeight': 1.0
                }]
            )
            
            endpoint_name = "xgboost-limiter-endpoint"
            self.sagemaker_client.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_config_name
            )
            
            logger.info(f"⏳ Waiting for endpoint to be in service...")
            waiter = self.sagemaker_client.get_waiter('endpoint_in_service')
            waiter.wait(EndpointName=endpoint_name)
            
            logger.info(f"✓ XGBoost deployed: {endpoint_name}")
            return endpoint_name
            
        except Exception as e:
            logger.error(f"XGBoost deployment failed: {str(e)}")
            raise
    
    def deploy_prophet(self, model_path: str) -> str:
        """Deploy Prophet model to SageMaker"""
        logger.info("🚀 Deploying Prophet...")
        
        s3_path = self._upload_model_to_s3(
            local_path=model_path,
            s3_folder="prophet"
        )
        logger.info(f"✓ Model uploaded to: {s3_path}")
        
        model_name = f"prophet-forecaster-{int(time.time())}"
        
        # Prophet uses sklearn container
        try:
            import sagemaker
            image_uri = sagemaker.image_uris.retrieve(
                framework='sklearn',
                region=self.region,
                version='1.0-1',
                py_version='py3',
                instance_type='ml.m5.large'
            )
        except:
            image_uri = f"683313688378.dkr.ecr.{self.region}.amazonaws.com/sagemaker-scikit-learn:1.0-1-cpu-py3"
        
        try:
            self.sagemaker_client.create_model(
                ModelName=model_name,
                PrimaryContainer={
                    'Image': image_uri,
                    'ModelDataUrl': s3_path
                },
                ExecutionRoleArn=self.execution_role_arn
            )
            
            endpoint_config_name = f"{model_name}-config"
            self.sagemaker_client.create_endpoint_config(
                EndpointConfigName=endpoint_config_name,
                ProductionVariants=[{
                    'VariantName': 'AllTraffic',
                    'ModelName': model_name,
                    'InstanceType': 'ml.m5.large',
                    'InitialInstanceCount': 1,
                    'InitialVariantWeight': 1.0
                }]
            )
            
            endpoint_name = "prophet-forecaster-endpoint"
            self.sagemaker_client.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_config_name
            )
            
            logger.info(f"⏳ Waiting for endpoint to be in service...")
            waiter = self.sagemaker_client.get_waiter('endpoint_in_service')
            waiter.wait(EndpointName=endpoint_name)
            
            logger.info(f"✓ Prophet deployed: {endpoint_name}")
            return endpoint_name
            
        except Exception as e:
            logger.error(f"Prophet deployment failed: {str(e)}")
            raise
    
    def _upload_model_to_s3(self, local_path: str, s3_folder: str) -> str:
        """Upload model file to S3"""
        s3_key = f"models/{s3_folder}/model.tar.gz"
        
        # Package model as tar.gz (SageMaker requirement)
        import tarfile
        tar_path = f"/tmp/{s3_folder}_model.tar.gz"
        
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(local_path, arcname="model.pkl")
        
        logger.info(f"Uploading {tar_path} to s3://{self.bucket_name}/{s3_key}...")
        self.s3_client.upload_file(tar_path, self.bucket_name, s3_key)
        
        s3_uri = f"s3://{self.bucket_name}/{s3_key}"
        return s3_uri


def main():
    parser = argparse.ArgumentParser(description="Deploy ML models to AWS SageMaker")
    parser.add_argument("--model", choices=["isolation_forest", "xgboost", "prophet", "all"], required=True)
    parser.add_argument("--region", default="us-east-1", help="AWS Region")
    parser.add_argument("--bucket", required=True, help="S3 Bucket for models")
    
    args = parser.parse_args()
    
    if not AWS_AVAILABLE:
        logger.error("AWS SDK not installed!")
        logger.error("Install with: pip install boto3 sagemaker")
        sys.exit(1)
    
    try:
        deployer = SageMakerDeployer(
            region=args.region,
            bucket_name=args.bucket
        )
    except Exception as e:
        logger.error(f"Failed to initialize deployer: {str(e)}")
        sys.exit(1)
    
    ml_models_dir = Path("ml-models")
    
    if not ml_models_dir.exists():
        logger.error(f"Models directory not found: {ml_models_dir}")
        logger.error("Run training first: python app/ml/training/train_all_models.py")
        sys.exit(1)
    
    endpoints = {}
    
    try:
        if args.model in ["isolation_forest", "all"]:
            model_path = ml_models_dir / "isolation_forest" / "model_v1.pkl"
            if not model_path.exists():
                logger.error(f"Model not found: {model_path}")
                sys.exit(1)
            endpoints["isolation_forest"] = deployer.deploy_isolation_forest(str(model_path))
        
        if args.model in ["xgboost", "all"]:
            model_path = ml_models_dir / "xgboost" / "model_v1.pkl"
            if not model_path.exists():
                logger.error(f"Model not found: {model_path}")
                sys.exit(1)
            endpoints["xgboost"] = deployer.deploy_xgboost(str(model_path))
        
        if args.model in ["prophet", "all"]:
            model_path = ml_models_dir / "prophet" / "model_v1.pkl"
            if not model_path.exists():
                logger.error(f"Model not found: {model_path}")
                sys.exit(1)
            endpoints["prophet"] = deployer.deploy_prophet(str(model_path))
        
        # Print endpoint names for .env file
        print("\n" + "="*60)
        print("✅ DEPLOYMENT COMPLETE!")
        print("="*60)
        print("\nAdd these to your .env file:\n")
        
        for model_name, endpoint_name in endpoints.items():
            env_var = f"{model_name.upper()}_ENDPOINT_NAME"
            print(f"{env_var}={endpoint_name}")
        
        print("\n" + "="*60)
        
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
