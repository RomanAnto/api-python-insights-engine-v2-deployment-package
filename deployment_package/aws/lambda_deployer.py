"""
Lambda function deployment
Creates Lambda function for caching and proxy layer
"""

import boto3
import json
import os
import zipfile
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class LambdaDeployer:
    """Deploy Lambda function for model inference"""
    
    def __init__(self, region: str = "eu-central-1"):
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.region = region
    
    def deploy_lambda_function(self, config, endpoint_name: str) -> Dict[str, Any]:
        """
        Deploy Lambda function
        
        Args:
            config: DeploymentConfig object
            endpoint_name: SageMaker endpoint name
            
        Returns:
            Dictionary with Lambda function information
        """
        function_name = f"{config.name}-lambda-{config.environment}"
        
        logger.info(f"Deploying Lambda function: {function_name}")
        
        # Create Lambda package
        lambda_zip = self._create_lambda_package(config, endpoint_name)
        
        # Get execution role
        execution_role = os.getenv("LAMBDA_EXECUTION_ROLE")
        if not execution_role:
            raise ValueError("LAMBDA_EXECUTION_ROLE environment variable not set")
        
        # Deploy function
        try:
            # Update existing function
            response = self.lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=lambda_zip
            )
            logger.info(f"Updated existing Lambda function: {function_name}")
            
            # Update configuration
            self.lambda_client.update_function_configuration(
                FunctionName=function_name,
                Environment={
                    'Variables': {
                        'SAGEMAKER_ENDPOINT': endpoint_name,
                        'CACHE_ENABLED': str(config.cache.enabled),
                        'CACHE_TTL': str(config.cache.ttl),
                        'MODEL_NAME': config.name
                    }
                }
            )
            
        except self.lambda_client.exceptions.ResourceNotFoundException:
            # Create new function
            logger.info(f"Creating new Lambda function: {function_name}")
            response = self.lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.11',
                Role=execution_role,
                Handler='lambda_handler.lambda_handler',
                Code={'ZipFile': lambda_zip},
                Timeout=900,  # 15 minutes
                MemorySize=512,
                Environment={
                    'Variables': {
                        'SAGEMAKER_ENDPOINT': endpoint_name,
                        'CACHE_ENABLED': str(config.cache.enabled),
                        'CACHE_TTL': str(config.cache.ttl),
                        'MODEL_NAME': config.name
                    }
                },
                Tags={
                    'Environment': config.environment,
                    'ManagedBy': 'CircleCI',
                    'Project': 'InsightEngine2.0'
                }
            )
        
        logger.info(f"✅ Lambda function deployed: {function_name}")
        
        return {
            "function_name": function_name,
            "function_arn": response['FunctionArn'],
            "status": "Active"
        }
    
    def _create_lambda_package(self, config, endpoint_name: str) -> bytes:
        """Create Lambda deployment package"""
        import tempfile
        import shutil
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Write Lambda handler
            handler_code = self._generate_lambda_handler(config, endpoint_name)
            handler_path = os.path.join(temp_dir, "lambda_handler.py")
            
            with open(handler_path, 'w') as f:
                f.write(handler_code)
            
            # Create zip file
            zip_path = os.path.join(temp_dir, "lambda.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(handler_path, "lambda_handler.py")
            
            # Read zip file
            with open(zip_path, 'rb') as f:
                return f.read()
        
        finally:
            shutil.rmtree(temp_dir)
    
    def _generate_lambda_handler(self, config, endpoint_name: str) -> str:
        """Generate Lambda handler code"""
        return f'''"""
Lambda handler for {config.name}
Handles caching and SageMaker invocation
"""

import json
import boto3
import os
import hashlib
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize clients
sagemaker_runtime = boto3.client('sagemaker-runtime')
cache_enabled = os.environ.get('CACHE_ENABLED', 'False') == 'True'

# Redis client initialization (if cache enabled)
if cache_enabled:
    try:
        import redis
        redis_endpoint = os.environ.get('REDIS_ENDPOINT')
        redis_client = redis.Redis.from_url(redis_endpoint) if redis_endpoint else None
    except ImportError:
        cache_enabled = False
        redis_client = None
        logger.warning("Redis not available, caching disabled")

def lambda_handler(event, context):
    """
    Lambda handler function
    Checks cache, invokes SageMaker endpoint, returns result
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{{}}'))
        endpoint_name = os.environ['SAGEMAKER_ENDPOINT']
        
        logger.info(f"Processing request for endpoint: {{endpoint_name}}")
        
        # Check cache
        if cache_enabled and redis_client:
            cache_key = _generate_cache_key(body)
            cached_result = redis_client.get(cache_key)
            
            if cached_result:
                logger.info("Cache hit!")
                return {{
                    'statusCode': 200,
                    'headers': {{'Content-Type': 'application/json'}},
                    'body': cached_result.decode('utf-8')
                }}
        
        # Invoke SageMaker endpoint
        logger.info("Cache miss, invoking SageMaker endpoint")
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=json.dumps(body)
        )
        
        # Parse response
        result = json.loads(response['Body'].read())
        result_json = json.dumps(result)
        
        # Store in cache
        if cache_enabled and redis_client:
            ttl = int(os.environ.get('CACHE_TTL', '3600'))
            redis_client.setex(cache_key, ttl, result_json)
            logger.info(f"Result cached with TTL: {{ttl}}s")
        
        return {{
            'statusCode': 200,
            'headers': {{'Content-Type': 'application/json'}},
            'body': result_json
        }}
    
    except Exception as e:
        logger.error(f"Error: {{str(e)}}", exc_info=True)
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'application/json'}},
            'body': json.dumps({{'error': 'Internal server error'}})
        }}

def _generate_cache_key(data):
    """Generate cache key from request data"""
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_str.encode()).hexdigest()
'''


def deploy_lambda_function(config, endpoint_name: str):
    """Deploy Lambda function (entry point)"""
    deployer = LambdaDeployer(region=config.instance.region)
    return deployer.deploy_lambda_function(config, endpoint_name)
