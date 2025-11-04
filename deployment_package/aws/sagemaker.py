"""
SageMaker deployment logic
Handles model deployment to AWS SageMaker
"""

import boto3
import time
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class SageMakerDeployer:
    """Deploy models to AWS SageMaker"""
    
    def __init__(self, region: str = "eu-central-1"):
        self.sagemaker = boto3.client('sagemaker', region_name=region)
        self.region = region
    
    def deploy_sagemaker_endpoint(self, config) -> Dict[str, Any]:
        """
        Deploy or update SageMaker endpoint
        
        Args:
            config: DeploymentConfig object
            
        Returns:
            Dictionary with endpoint information
        """
        model_name = config.name
        endpoint_name = f"{model_name}-endpoint-{config.environment}"
        
        logger.info(f"Deploying SageMaker endpoint: {endpoint_name}")
        
        # Get ECR image URI
        ecr_image_uri = self._get_ecr_image_uri(model_name)
        
        # Create or update model
        self._create_or_update_model(
            model_name=model_name,
            image_uri=ecr_image_uri,
            config=config
        )
        
        # Create endpoint configuration
        endpoint_config_name = self._create_endpoint_config(
            model_name=model_name,
            config=config
        )
        
        # Deploy endpoint
        endpoint_arn = self._deploy_endpoint(
            endpoint_name=endpoint_name,
            endpoint_config_name=endpoint_config_name
        )
        
        # Wait for endpoint to be in service
        self._wait_for_endpoint(endpoint_name)
        
        logger.info(f"✅ Endpoint deployed successfully: {endpoint_name}")
        
        return {
            "endpoint_name": endpoint_name,
            "endpoint_arn": endpoint_arn,
            "model_name": model_name,
            "status": "InService"
        }
    
    def _get_ecr_image_uri(self, model_name: str) -> str:
        """Get ECR image URI from environment or construct it"""
        import os
        ecr_registry = os.getenv("AWS_ECR_REGISTRY")
        commit_sha = os.getenv("CIRCLE_SHA1", "latest")
        
        if not ecr_registry:
            raise ValueError("AWS_ECR_REGISTRY environment variable not set")
        
        return f"{ecr_registry}/{model_name}:{commit_sha}"
    
    def _create_or_update_model(self, model_name: str, image_uri: str, config):
        """Create or update SageMaker model"""
        import os
        execution_role = os.getenv("SAGEMAKER_EXECUTION_ROLE")
        
        try:
            self.sagemaker.describe_model(ModelName=model_name)
            logger.info(f"Model {model_name} already exists, skipping creation")
        except self.sagemaker.exceptions.ClientError:
            logger.info(f"Creating SageMaker model: {model_name}")
            self.sagemaker.create_model(
                ModelName=model_name,
                PrimaryContainer={
                    'Image': image_uri,
                    'Mode': 'SingleModel',
                    'Environment': {
                        'MODEL_NAME': model_name,
                        'ENVIRONMENT': config.environment
                    }
                },
                ExecutionRoleArn=execution_role,
                Tags=[
                    {'Key': 'Environment', 'Value': config.environment},
                    {'Key': 'ManagedBy', 'Value': 'CircleCI'},
                    {'Key': 'Project', 'Value': 'InsightEngine2.0'}
                ]
            )
    
    def _create_endpoint_config(self, model_name: str, config) -> str:
        """Create endpoint configuration"""
        endpoint_config_name = f"{model_name}-config-{int(time.time())}"
        
        logger.info(f"Creating endpoint configuration: {endpoint_config_name}")
        
        self.sagemaker.create_endpoint_config(
            EndpointConfigName=endpoint_config_name,
            ProductionVariants=[
                {
                    'VariantName': 'AllTraffic',
                    'ModelName': model_name,
                    'InstanceType': config.instance.type,
                    'InitialInstanceCount': config.instance.count,
                    'InitialVariantWeight': 1.0
                }
            ],
            Tags=[
                {'Key': 'Environment', 'Value': config.environment},
                {'Key': 'ManagedBy', 'Value': 'CircleCI'}
            ]
        )
        
        return endpoint_config_name
    
    def _deploy_endpoint(self, endpoint_name: str, endpoint_config_name: str) -> str:
        """Deploy or update endpoint"""
        try:
            # Check if endpoint exists
            response = self.sagemaker.describe_endpoint(EndpointName=endpoint_name)
            
            # Update existing endpoint
            logger.info(f"Updating existing endpoint: {endpoint_name}")
            self.sagemaker.update_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_config_name
            )
            return response['EndpointArn']
            
        except self.sagemaker.exceptions.ClientError:
            # Create new endpoint
            logger.info(f"Creating new endpoint: {endpoint_name}")
            response = self.sagemaker.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_config_name,
                Tags=[
                    {'Key': 'ManagedBy', 'Value': 'CircleCI'}
                ]
            )
            return response['EndpointArn']
    
    def _wait_for_endpoint(self, endpoint_name: str, timeout: int = 900):
        """Wait for endpoint to be in service"""
        logger.info(f"Waiting for endpoint to be InService (timeout: {timeout}s)...")
        
        start_time = time.time()
        while True:
            response = self.sagemaker.describe_endpoint(EndpointName=endpoint_name)
            status = response['EndpointStatus']
            
            logger.info(f"Endpoint status: {status}")
            
            if status == 'InService':
                logger.info("✅ Endpoint is InService")
                return
            elif status in ['Failed', 'RolledBack']:
                raise RuntimeError(f"Endpoint deployment failed: {status}")
            
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Endpoint deployment timeout after {timeout}s")
            
            time.sleep(30)


def deploy_sagemaker_endpoint(config):
    """Deploy SageMaker endpoint (entry point)"""
    deployer = SageMakerDeployer(region=config.instance.region)
    return deployer.deploy_sagemaker_endpoint(config)
