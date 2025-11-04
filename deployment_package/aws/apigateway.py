"""
API Gateway setup with Cognito authentication
Dev environment only
"""

import boto3
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class APIGatewaySetup:
    """Setup API Gateway with Cognito authentication"""
    
    def __init__(self, region: str = "eu-central-1"):
        self.apigateway = boto3.client('apigateway', region_name=region)
        self.cognito = boto3.client('cognito-idp', region_name=region)
        self.region = region
    
    def setup_api_gateway_with_cognito(self, config, lambda_arn: str) -> Dict[str, Any]:
        """
        Setup API Gateway with Cognito authorizer
        
        Args:
            config: DeploymentConfig object
            lambda_arn: Lambda function ARN
            
        Returns:
            Dictionary with API Gateway information
        """
        api_name = f"{config.name}-api-{config.environment}"
        
        logger.info(f"Setting up API Gateway: {api_name}")
        
        # Create or get Cognito User Pool
        user_pool_id = self._get_or_create_user_pool(config)
        
        # Create Cognito App Client
        app_client_id = self._create_app_client(user_pool_id, config)
        
        # Create REST API
        api_id = self._create_rest_api(api_name, config)
        
        # Create Cognito authorizer
        authorizer_id = self._create_cognito_authorizer(
            api_id, user_pool_id, config
        )
        
        # Create resources and methods
        resource_id = self._create_resources(api_id, lambda_arn, authorizer_id)
        
        # Deploy API
        endpoint_url = self._deploy_api(api_id, config.environment)
        
        # Generate API key
        api_key = self._create_api_key(api_id, config)
        
        logger.info(f"✅ API Gateway setup complete: {endpoint_url}")
        
        return {
            "api_id": api_id,
            "endpoint_url": endpoint_url,
            "api_key": api_key,
            "user_pool_id": user_pool_id,
            "app_client_id": app_client_id
        }
    
    def _get_or_create_user_pool(self, config) -> str:
        """Get existing or create new Cognito User Pool"""
        pool_name = f"ie2-user-pool-{config.environment}"
        
        try:
            # List existing pools
            response = self.cognito.list_user_pools(MaxResults=50)
            for pool in response.get('UserPools', []):
                if pool['Name'] == pool_name:
                    logger.info(f"Using existing user pool: {pool['Id']}")
                    return pool['Id']
        except Exception as e:
            logger.warning(f"Error listing user pools: {e}")
        
        # Create new pool
        logger.info(f"Creating new user pool: {pool_name}")
        response = self.cognito.create_user_pool(
            PoolName=pool_name,
            Policies={
                'PasswordPolicy': {
                    'MinimumLength': 8,
                    'RequireUppercase': True,
                    'RequireLowercase': True,
                    'RequireNumbers': True,
                    'RequireSymbols': False
                }
            },
            AutoVerifiedAttributes=['email'],
            Schema=[
                {
                    'Name': 'email',
                    'AttributeDataType': 'String',
                    'Required': True,
                    'Mutable': True
                }
            ]
        )
        
        return response['UserPool']['Id']
    
    def _create_app_client(self, user_pool_id: str, config) -> str:
        """Create Cognito App Client"""
        client_name = f"{config.name}-client"
        
        response = self.cognito.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName=client_name,
            GenerateSecret=False,
            ExplicitAuthFlows=[
                'ALLOW_USER_PASSWORD_AUTH',
                'ALLOW_REFRESH_TOKEN_AUTH'
            ]
        )
        
        logger.info(f"Created app client: {response['UserPoolClient']['ClientId']}")
        return response['UserPoolClient']['ClientId']
    
    def _create_rest_api(self, api_name: str, config) -> str:
        """Create REST API"""
        try:
            # Check if API exists
            response = self.apigateway.get_rest_apis()
            for api in response.get('items', []):
                if api['name'] == api_name:
                    logger.info(f"Using existing API: {api['id']}")
                    return api['id']
        except Exception as e:
            logger.warning(f"Error checking existing APIs: {e}")
        
        # Create new API
        logger.info(f"Creating REST API: {api_name}")
        response = self.apigateway.create_rest_api(
            name=api_name,
            description=f"API for {config.name} model",
            endpointConfiguration={'types': ['REGIONAL']}
        )
        
        return response['id']
    
    def _create_cognito_authorizer(self, api_id: str, user_pool_id: str, 
                                   config) -> str:
        """Create Cognito authorizer"""
        authorizer_name = f"{config.name}-cognito-auth"
        
        response = self.apigateway.create_authorizer(
            restApiId=api_id,
            name=authorizer_name,
            type='COGNITO_USER_POOLS',
            providerARNs=[
                f"arn:aws:cognito-idp:{self.region}:{self._get_account_id()}:userpool/{user_pool_id}"
            ],
            identitySource='method.request.header.Authorization'
        )
        
        logger.info(f"Created Cognito authorizer: {response['id']}")
        return response['id']
    
    def _create_resources(self, api_id: str, lambda_arn: str, 
                         authorizer_id: str) -> str:
        """Create API resources and methods"""
        # Get root resource
        resources = self.apigateway.get_resources(restApiId=api_id)
        root_id = resources['items'][0]['id']
        
        # Create /invoke resource
        resource = self.apigateway.create_resource(
            restApiId=api_id,
            parentId=root_id,
            pathPart='invoke'
        )
        resource_id = resource['id']
        
        # Create POST method
        self.apigateway.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            authorizationType='COGNITO_USER_POOLS',
            authorizerId=authorizer_id
        )
        
        # Set Lambda integration
        self.apigateway.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f"arn:aws:apigateway:{self.region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        )
        
        logger.info("Created API resources and methods")
        return resource_id
    
    def _deploy_api(self, api_id: str, environment: str) -> str:
        """Deploy API to stage"""
        self.apigateway.create_deployment(
            restApiId=api_id,
            stageName=environment
        )
        
        endpoint_url = f"https://{api_id}.execute-api.{self.region}.amazonaws.com/{environment}"
        logger.info(f"API deployed to: {endpoint_url}")
        
        return endpoint_url
    
    def _create_api_key(self, api_id: str, config) -> str:
        """Create API key for testing"""
        key_name = f"{config.name}-key-{config.environment}"
        
        response = self.apigateway.create_api_key(
            name=key_name,
            enabled=True
        )
        
        return response['value']
    
    def _get_account_id(self) -> str:
        """Get AWS account ID"""
        sts = boto3.client('sts')
        return sts.get_caller_identity()['Account']


def setup_api_gateway_with_cognito(config, lambda_arn: str):
    """Setup API Gateway (entry point)"""
    setup = APIGatewaySetup(region=config.instance.region)
    return setup.setup_api_gateway_with_cognito(config, lambda_arn)
