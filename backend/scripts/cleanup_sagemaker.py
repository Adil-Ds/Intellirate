"""
AWS SageMaker Cleanup Script - Remove old endpoints, configurations, and models
Usage:
  python cleanup_sagemaker.py --region us-east-1 --dry-run  # Preview what will be deleted
  python cleanup_sagemaker.py --region us-east-1 --all      # Delete all IntelliRate resources
  python cleanup_sagemaker.py --region us-east-1 --endpoints isolation-forest-endpoint xgboost-limiter-endpoint
"""
import os
import sys
import argparse
import logging
import time
from typing import List, Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    logger.error("AWS SDK not available. Install with: pip install boto3")
    AWS_AVAILABLE = False
    sys.exit(1)


class SageMakerCleaner:
    """Clean up SageMaker resources"""
    
    def __init__(self, region: str, dry_run: bool = False):
        self.region = region
        self.dry_run = dry_run
        self.sagemaker_client = boto3.client('sagemaker', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        
        logger.info(f"✓ Initialized SageMaker Cleaner for region: {region}")
        if dry_run:
            logger.info("🔍 DRY RUN MODE - No resources will be deleted")
    
    def list_all_endpoints(self) -> List[Dict[str, Any]]:
        """List all SageMaker endpoints in the region"""
        try:
            response = self.sagemaker_client.list_endpoints(MaxResults=100)
            endpoints = response.get('Endpoints', [])
            
            logger.info(f"Found {len(endpoints)} endpoint(s) in {self.region}")
            return endpoints
        except ClientError as e:
            logger.error(f"Failed to list endpoints: {str(e)}")
            return []
    
    def list_intellirate_endpoints(self) -> List[str]:
        """List only IntelliRate-related endpoints"""
        all_endpoints = self.list_all_endpoints()
        
        # Filter for IntelliRate endpoints
        patterns = [
            'isolation-forest-endpoint',
            'xgboost-limiter-endpoint',
            'prophet-forecaster-endpoint',
            'intellirate'  # Catch any with 'intellirate' in name
        ]
        
        intellirate_endpoints = []
        for endpoint in all_endpoints:
            endpoint_name = endpoint['EndpointName']
            if any(pattern in endpoint_name.lower() for pattern in patterns):
                intellirate_endpoints.append(endpoint_name)
        
        return intellirate_endpoints
    
    def delete_endpoint(self, endpoint_name: str) -> bool:
        """Delete a SageMaker endpoint"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would delete endpoint: {endpoint_name}")
            return True
        
        try:
            logger.info(f"🗑️  Deleting endpoint: {endpoint_name}")
            self.sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
            logger.info(f"✓ Endpoint deleted: {endpoint_name}")
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'ResourceNotFound':
                logger.warning(f"Endpoint not found (already deleted?): {endpoint_name}")
                return True
            else:
                logger.error(f"Failed to delete endpoint {endpoint_name}: {str(e)}")
                return False
    
    def get_endpoint_config_name(self, endpoint_name: str) -> Optional[str]:
        """Get the endpoint configuration name for an endpoint"""
        try:
            response = self.sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
            return response.get('EndpointConfigName')
        except ClientError:
            return None
    
    def delete_endpoint_config(self, config_name: str) -> bool:
        """Delete a SageMaker endpoint configuration"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would delete endpoint config: {config_name}")
            return True
        
        try:
            logger.info(f"🗑️  Deleting endpoint config: {config_name}")
            self.sagemaker_client.delete_endpoint_config(EndpointConfigName=config_name)
            logger.info(f"✓ Endpoint config deleted: {config_name}")
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'ResourceNotFound':
                logger.warning(f"Endpoint config not found: {config_name}")
                return True
            else:
                logger.error(f"Failed to delete endpoint config {config_name}: {str(e)}")
                return False
    
    def get_models_for_endpoint_config(self, config_name: str) -> List[str]:
        """Get model names associated with an endpoint configuration"""
        try:
            response = self.sagemaker_client.describe_endpoint_config(
                EndpointConfigName=config_name
            )
            
            model_names = []
            for variant in response.get('ProductionVariants', []):
                model_name = variant.get('ModelName')
                if model_name:
                    model_names.append(model_name)
            
            return model_names
        except ClientError:
            return []
    
    def delete_model(self, model_name: str) -> bool:
        """Delete a SageMaker model"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would delete model: {model_name}")
            return True
        
        try:
            logger.info(f"🗑️  Deleting model: {model_name}")
            self.sagemaker_client.delete_model(ModelName=model_name)
            logger.info(f"✓ Model deleted: {model_name}")
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'ResourceNotFound':
                logger.warning(f"Model not found: {model_name}")
                return True
            else:
                logger.error(f"Failed to delete model {model_name}: {str(e)}")
                return False
    
    def cleanup_endpoint_and_dependencies(self, endpoint_name: str) -> Dict[str, bool]:
        """Delete an endpoint and all its dependencies"""
        results = {
            'endpoint': False,
            'endpoint_config': False,
            'models': []
        }
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Cleaning up: {endpoint_name}")
        logger.info(f"{'='*60}")
        
        # Get endpoint config name before deleting endpoint
        config_name = self.get_endpoint_config_name(endpoint_name)
        
        # Get model names before deleting config
        model_names = []
        if config_name:
            model_names = self.get_models_for_endpoint_config(config_name)
        
        # 1. Delete endpoint
        results['endpoint'] = self.delete_endpoint(endpoint_name)
        
        # Wait a bit for endpoint deletion to propagate
        if not self.dry_run and results['endpoint']:
            logger.info("⏳ Waiting for endpoint deletion to complete...")
            time.sleep(5)
        
        # 2. Delete endpoint configuration
        if config_name:
            results['endpoint_config'] = self.delete_endpoint_config(config_name)
        else:
            logger.warning("No endpoint config found")
            results['endpoint_config'] = True  # Not an error
        
        # 3. Delete models
        for model_name in model_names:
            model_deleted = self.delete_model(model_name)
            results['models'].append({
                'name': model_name,
                'deleted': model_deleted
            })
        
        return results
    
    def cleanup_s3_bucket(self, bucket_name: str, prefix: str = "models/") -> bool:
        """Clean up old model artifacts from S3 bucket"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would clean S3 bucket: s3://{bucket_name}/{prefix}")
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=prefix
                )
                objects = response.get('Contents', [])
                logger.info(f"[DRY RUN] Found {len(objects)} object(s) that would be deleted")
                for obj in objects[:5]:  # Show first 5
                    logger.info(f"  - {obj['Key']}")
                if len(objects) > 5:
                    logger.info(f"  ... and {len(objects) - 5} more")
            except ClientError:
                logger.warning(f"Could not list objects in bucket")
            return True
        
        try:
            logger.info(f"🗑️  Cleaning S3 bucket: s3://{bucket_name}/{prefix}")
            
            # List all objects with the prefix
            response = self.s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix
            )
            
            objects = response.get('Contents', [])
            if not objects:
                logger.info("No objects to delete in S3")
                return True
            
            # Delete objects
            delete_keys = [{'Key': obj['Key']} for obj in objects]
            self.s3_client.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': delete_keys}
            )
            
            logger.info(f"✓ Deleted {len(delete_keys)} object(s) from S3")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to clean S3 bucket: {str(e)}")
            return False
    
    def cleanup_all_intellirate_resources(self) -> Dict[str, Any]:
        """Clean up all IntelliRate-related resources"""
        logger.info("\n" + "="*60)
        logger.info("SCANNING FOR INTELLIRATE RESOURCES")
        logger.info("="*60 + "\n")
        
        endpoints = self.list_intellirate_endpoints()
        
        if not endpoints:
            logger.info("✓ No IntelliRate endpoints found to clean up")
            return {'endpoints_cleaned': 0, 'success': True}
        
        logger.info(f"\nFound {len(endpoints)} IntelliRate endpoint(s):")
        for i, endpoint_name in enumerate(endpoints, 1):
            logger.info(f"  {i}. {endpoint_name}")
        
        if not self.dry_run:
            logger.info("\n⚠️  WARNING: This will DELETE the above resources!")
            response = input("\nProceed with deletion? (yes/no): ").strip().lower()
            if response != 'yes':
                logger.info("Cleanup cancelled by user")
                return {'endpoints_cleaned': 0, 'success': False, 'cancelled': True}
        
        logger.info("\n" + "="*60)
        logger.info("STARTING CLEANUP")
        logger.info("="*60)
        
        results = []
        for endpoint_name in endpoints:
            result = self.cleanup_endpoint_and_dependencies(endpoint_name)
            results.append({
                'endpoint_name': endpoint_name,
                'result': result
            })
        
        logger.info("\n" + "="*60)
        logger.info("CLEANUP SUMMARY")
        logger.info("="*60)
        
        total_cleaned = 0
        for item in results:
            endpoint_name = item['endpoint_name']
            result = item['result']
            
            if result['endpoint']:
                logger.info(f"✓ {endpoint_name}: Successfully cleaned")
                total_cleaned += 1
            else:
                logger.info(f"✗ {endpoint_name}: Cleanup failed")
        
        logger.info(f"\nTotal endpoints cleaned: {total_cleaned}/{len(endpoints)}")
        
        return {
            'endpoints_cleaned': total_cleaned,
            'total_endpoints': len(endpoints),
            'success': total_cleaned == len(endpoints),
            'details': results
        }


def main():
    parser = argparse.ArgumentParser(
        description="Clean up AWS SageMaker resources for IntelliRate"
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS Region (default: us-east-1)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be deleted without actually deleting"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Clean up all IntelliRate resources"
    )
    parser.add_argument(
        "--endpoints",
        nargs="+",
        help="Specific endpoint names to delete"
    )
    parser.add_argument(
        "--clean-s3",
        help="Also clean S3 bucket (specify bucket name)"
    )
    parser.add_argument(
        "--s3-prefix",
        default="models/",
        help="S3 prefix for model artifacts (default: models/)"
    )
    
    args = parser.parse_args()
    
    if not AWS_AVAILABLE:
        logger.error("AWS SDK not installed!")
        logger.error("Install with: pip install boto3")
        sys.exit(1)
    
    # Validate arguments
    if not args.all and not args.endpoints:
        logger.error("Must specify either --all or --endpoints")
        parser.print_help()
        sys.exit(1)
    
    try:
        cleaner = SageMakerCleaner(region=args.region, dry_run=args.dry_run)
        
        if args.all:
            # Clean up all IntelliRate resources
            result = cleaner.cleanup_all_intellirate_resources()
            
            # Clean S3 if requested
            if args.clean_s3 and result.get('success'):
                logger.info("\n" + "="*60)
                logger.info("CLEANING S3 BUCKET")
                logger.info("="*60)
                cleaner.cleanup_s3_bucket(args.clean_s3, args.s3_prefix)
            
            if result.get('success'):
                logger.info("\n✅ Cleanup completed successfully!")
                sys.exit(0)
            else:
                logger.error("\n❌ Cleanup completed with errors")
                sys.exit(1)
        
        elif args.endpoints:
            # Clean up specific endpoints
            logger.info(f"Cleaning up {len(args.endpoints)} endpoint(s)")
            
            if not args.dry_run:
                logger.info("\n⚠️  WARNING: This will DELETE the specified endpoints!")
                response = input("\nProceed with deletion? (yes/no): ").strip().lower()
                if response != 'yes':
                    logger.info("Cleanup cancelled by user")
                    sys.exit(0)
            
            success_count = 0
            for endpoint_name in args.endpoints:
                result = cleaner.cleanup_endpoint_and_dependencies(endpoint_name)
                if result['endpoint']:
                    success_count += 1
            
            logger.info(f"\n✅ Cleaned {success_count}/{len(args.endpoints)} endpoint(s)")
            sys.exit(0 if success_count == len(args.endpoints) else 1)
    
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
