"""
Complete deployment script for all 3 ML models to Google Cloud Vertex AI
Usage: python deploy_to_cloud.py --model all --project-id YOUR_PROJECT_ID --bucket YOUR_BUCKET
"""
import os
import sys
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from google.cloud import aiplatform, storage
    from google.cloud.aiplatform import Model, Endpoint
    import joblib
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    logger.warning("Google Cloud libraries not available. Install with: pip install google-cloud-aiplatform google-cloud-storage")
    GOOGLE_CLOUD_AVAILABLE = False


class VertexAIDeployer:
    """Deployer for ML models to Google Cloud Vertex AI"""
    
    def __init__(self, project_id: str, region: str, bucket_name: str):
        if not GOOGLE_CLOUD_AVAILABLE:
            raise Exception("Google Cloud libraries not installed")
        
        self.project_id = project_id
        self.region = region
        self.bucket_name = bucket_name
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=region)
        
        # Initialize Cloud Storage client
        self.storage_client = storage.Client(project=project_id)
        
        try:
            self.bucket = self.storage_client.bucket(bucket_name)
        except:
            logger.warning(f"Bucket {bucket_name} may not exist. Creating...")
            self.bucket = self.storage_client.create_bucket(bucket_name, location=region)
            logger.info(f"✓ Created bucket: {bucket_name}")
        
        logger.info(f"✓ Initialized deployer for project: {project_id}")
    
    def deploy_isolation_forest(self, model_path: str) -> str:
        """Deploy Isolation Forest model to Vertex AI"""
        logger.info("🚀 Deploying Isolation Forest...")
        
        # 1. Upload model to Cloud Storage
        gcs_path = self._upload_model_to_gcs(
            local_path=model_path,
            gcs_folder="isolation_forest"
        )
        logger.info(f"✓ Model uploaded to: {gcs_path}")
        
        # 2. Create or get pre-built container image
        image_uri = "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-2:latest"
        logger.info(f"✓ Using container: {image_uri}")
        
        # 3. Create Vertex AI Model
        display_name = f"isolation-forest-v{int(os.time())}"
        
        try:
            model = Model.upload(
                display_name=display_name,
                artifact_uri=os.path.dirname(gcs_path),
                serving_container_image_uri=image_uri,
                serving_container_predict_route="/predict",
                serving_container_health_route="/health",
            )
            logger.info(f"✓ Model created: {model.resource_name}")
        except Exception as e:
            logger.error(f"Model creation failed: {str(e)}")
            raise
        
        # 4. Deploy to endpoint
        try:
            endpoint = Endpoint.create(display_name=f"{display_name}-endpoint")
            endpoint.deploy(
                model=model,
                machine_type="n1-standard-2",
                min_replica_count=0,  # Scale to zero when idle
                max_replica_count=10,
                traffic_percentage=100,
            )
            logger.info(f"✓ Deployed to endpoint: {endpoint.resource_name}")
        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            raise
        
        return endpoint.resource_name
    
    def deploy_xgboost(self, model_path: str) -> str:
        """Deploy XGBoost model to Vertex AI"""
        logger.info("🚀 Deploying XGBoost...")
        
        gcs_path = self._upload_model_to_gcs(
            local_path=model_path,
            gcs_folder="xgboost"
        )
        logger.info(f"✓ Model uploaded to: {gcs_path}")
        
        image_uri = "us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-6:latest"
        
        display_name = f"xgboost-limiter-v{int(os.time())}"
        
        try:
            model = Model.upload(
                display_name=display_name,
                artifact_uri=os.path.dirname(gcs_path),
                serving_container_image_uri=image_uri,
                serving_container_predict_route="/predict",
                serving_container_health_route="/health",
            )
            
            endpoint = Endpoint.create(display_name=f"{display_name}-endpoint")
            endpoint.deploy(
                model=model,
                machine_type="n1-standard-2",
                min_replica_count=0,
                max_replica_count=10,
                traffic_percentage=100,
            )
            
            logger.info(f"✓ XGBoost deployed: {endpoint.resource_name}")
            return endpoint.resource_name
        except Exception as e:
            logger.error(f"XGBoost deployment failed: {str(e)}")
            raise
    
    def deploy_prophet(self, model_path: str) -> str:
        """Deploy Prophet model to Vertex AI"""
        logger.info("🚀 Deploying Prophet...")
        
        gcs_path = self._upload_model_to_gcs(
            local_path=model_path,
            gcs_folder="prophet"
        )
        logger.info(f"✓ Model uploaded to: {gcs_path}")
        
        # Prophet needs sklearn container
        image_uri = "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-2:latest"
        
        display_name = f"prophet-forecaster-v{int(os.time())}"
        
        try:
            model = Model.upload(
                display_name=display_name,
                artifact_uri=os.path.dirname(gcs_path),
                serving_container_image_uri=image_uri,
                serving_container_predict_route="/predict",
                serving_container_health_route="/health",
            )
            
            endpoint = Endpoint.create(display_name=f"{display_name}-endpoint")
            endpoint.deploy(
                model=model,
                machine_type="n1-standard-2",
                min_replica_count=1,  # Keep 1 instance warm for time-series
                max_replica_count=5,
                traffic_percentage=100,
            )
            
            logger.info(f"✓ Prophet deployed: {endpoint.resource_name}")
            return endpoint.resource_name
        except Exception as e:
            logger.error(f"Prophet deployment failed: {str(e)}")
            raise
    
    def _upload_model_to_gcs(self, local_path: str, gcs_folder: str) -> str:
        """Upload model file to Google Cloud Storage"""
        blob_name = f"models/{gcs_folder}/model.pkl"
        blob = self.bucket.blob(blob_name)
        
        logger.info(f"Uploading {local_path} to gs://{self.bucket_name}/{blob_name}...")
        blob.upload_from_filename(local_path)
        
        gcs_uri = f"gs://{self.bucket_name}/{blob_name}"
        return gcs_uri


def main():
    parser = argparse.ArgumentParser(description="Deploy ML models to Google Cloud Vertex AI")
    parser.add_argument("--model", choices=["isolation_forest", "xgboost", "prophet", "all"], required=True)
    parser.add_argument("--project-id", required=True, help="GCP Project ID")
    parser.add_argument("--region", default="us-central1", help="GCP Region")
    parser.add_argument("--bucket", required=True, help="GCS Bucket for models")
    
    args = parser.parse_args()
    
    if not GOOGLE_CLOUD_AVAILABLE:
        logger.error("Google Cloud libraries not installed!")
        logger.error("Install with: pip install google-cloud-aiplatform google-cloud-storage")
        sys.exit(1)
    
    try:
        deployer = VertexAIDeployer(
            project_id=args.project_id,
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
        
        # Print endpoint IDs for .env file
        print("\n" + "="*60)
        print("✅ DEPLOYMENT COMPLETE!")
        print("="*60)
        print("\nAdd these to your .env file:\n")
        
        for model_name, endpoint_id in endpoints.items():
            env_var = f"{model_name.upper()}_ENDPOINT_ID"
            print(f"{env_var}={endpoint_id}")
        
        print("\n" + "="*60)
        
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
