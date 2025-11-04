"""
CircleCI configuration generator
Updates .circleci/config.yml based on user inputs
"""

from typing import Dict, Any, Optional
import yaml

class CircleCIGenerator:
    """Generate and update CircleCI configuration"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    def generate_config(self, 
                       instance_type: str = "ml.m5.xlarge",
                       instance_count: int = 1,
                       enable_autoscaling: bool = False,
                       enable_cache: bool = True,
                       aws_region: str = "eu-central-1",
                       environment: str = "dev") -> Dict[str, Any]:
        """
        Generate CircleCI configuration
        
        Args:
            instance_type: SageMaker instance type
            instance_count: Number of instances
            enable_autoscaling: Enable auto-scaling
            enable_cache: Enable Redis caching
            aws_region: AWS region
            environment: Deployment environment
        """
        
        config = {
            "version": 2.1,
            "orbs": {
                "aws-cli": "circleci/aws-cli@4.1.0",
                "aws-ecr": "circleci/aws-ecr@9.0.0",
                "sonarcloud": "sonarsource/sonarcloud@2.0.0",
                "python": "circleci/python@2.1.1"
            },
            "parameters": {
                "model-name": {
                    "type": "string",
                    "default": self.model_name
                },
                "instance-type": {
                    "type": "string",
                    "default": instance_type
                },
                "instance-count": {
                    "type": "integer",
                    "default": instance_count
                },
                "aws-region": {
                    "type": "string",
                    "default": aws_region
                },
                "environment": {
                    "type": "string",
                    "default": environment
                }
            },
            "jobs": {
                "code-quality-scan": {
                    "docker": [{"image": "cimg/python:3.11"}],
                    "steps": [
                        "checkout",
                        {
                            "python/install-packages": {
                                "pkg-manager": "pip"
                            }
                        },
                        {
                            "run": {
                                "name": "Run tests",
                                "command": "pytest tests/ -v --cov=src --cov-report=xml"
                            }
                        },
                        {
                            "sonarcloud/scan": {
                                "sonar_token_variable_name": "SONAR_TOKEN"
                            }
                        }
                    ]
                },
                "build-and-push-image": {
                    "docker": [{"image": "cimg/python:3.11"}],
                    "steps": [
                        "checkout",
                        "setup_remote_docker",
                        {
                            "aws-ecr/build-and-push-image": {
                                "repo": f"${{AWS_ECR_REGISTRY}}/{self.model_name}",
                                "tag": "$CIRCLE_SHA1,latest",
                                "region": "$AWS_REGION",
                                "extra-build-args": "--build-arg FURY_TOKEN=$FURY_TOKEN"
                            }
                        },
                        {
                            "run": {
                                "name": "Save image info",
                                "command": f'''
echo "export ECR_IMAGE_URI=${{AWS_ECR_REGISTRY}}/{self.model_name}:$CIRCLE_SHA1" >> $BASH_ENV
echo "Image built: ${{AWS_ECR_REGISTRY}}/{self.model_name}:$CIRCLE_SHA1"
'''
                            }
                        }
                    ]
                },
                "deploy-sagemaker": {
                    "docker": [{"image": "cimg/python:3.11"}],
                    "steps": [
                        "checkout",
                        {
                            "aws-cli/setup": {
                                "role_arn": "$AWS_ROLE_ARN",
                                "region": "$AWS_REGION"
                            }
                        },
                        {
                            "run": {
                                "name": "Install deployment dependencies",
                                "command": "pip install boto3 pyyaml"
                            }
                        },
                        {
                            "run": {
                                "name": "Deploy to SageMaker",
                                "command": f"python deployment_package/deploy.py --environment << pipeline.parameters.environment >>"
                            }
                        }
                    ]
                },
                "deploy-lambda": {
                    "docker": [{"image": "cimg/python:3.11"}],
                    "steps": [
                        "checkout",
                        {
                            "aws-cli/setup": {
                                "role_arn": "$AWS_ROLE_ARN",
                                "region": "$AWS_REGION"
                            }
                        },
                        {
                            "run": {
                                "name": "Create Lambda package",
                                "command": '''
mkdir -p lambda_package
cp deployment_package/aws/lambda_handler.py lambda_package/
pip install -r deployment_package/aws/lambda_requirements.txt -t lambda_package/
cd lambda_package && zip -r ../lambda.zip . && cd ..
'''
                            }
                        },
                        {
                            "run": {
                                "name": "Deploy Lambda function",
                                "command": "python deployment_package/aws/lambda.py"
                            }
                        }
                    ]
                },
                "setup-api-gateway": {
                    "docker": [{"image": "cimg/python:3.11"}],
                    "steps": [
                        "checkout",
                        {
                            "aws-cli/setup": {
                                "role_arn": "$AWS_ROLE_ARN",
                                "region": "$AWS_REGION"
                            }
                        },
                        {
                            "run": {
                                "name": "Setup API Gateway (Dev)",
                                "command": "python deployment_package/aws/apigateway.py"
                            }
                        },
                        {
                            "run": {
                                "name": "Output API details",
                                "command": '''
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo "API Endpoint: $API_ENDPOINT_URL"
echo "API Key: $API_KEY"
echo "Environment: << pipeline.parameters.environment >>"
echo "========================================="
'''
                            }
                        }
                    ]
                },
                "setup-apigeex": {
                    "docker": [{"image": "cimg/python:3.11"}],
                    "steps": [
                        "checkout",
                        {
                            "run": {
                                "name": "Setup ApigeeX Proxy",
                                "command": "python deployment_package/apigeex/proxy.py"
                            }
                        }
                    ]
                }
            },
            "workflows": {
                "build-test-deploy": {
                    "jobs": [
                        "code-quality-scan",
                        {
                            "build-and-push-image": {
                                "requires": ["code-quality-scan"],
                                "context": ["aws-credentials", "docker-hub"]
                            }
                        },
                        {
                            "approve-dev-deploy": {
                                "type": "approval",
                                "requires": ["build-and-push-image"],
                                "filters": {
                                    "branches": {
                                        "only": ["main", "develop"]
                                    }
                                }
                            }
                        },
                        {
                            "deploy-sagemaker": {
                                "requires": ["approve-dev-deploy"],
                                "context": ["aws-credentials"]
                            }
                        },
                        {
                            "deploy-lambda": {
                                "requires": ["deploy-sagemaker"],
                                "context": ["aws-credentials"]
                            }
                        }
                    ]
                }
            }
        }
        
        # Add API Gateway for dev, ApigeeX for stage/prod
        if environment == "dev":
            config["workflows"]["build-test-deploy"]["jobs"].append({
                "setup-api-gateway": {
                    "requires": ["deploy-lambda"],
                    "context": ["aws-credentials"]
                }
            })
        else:
            config["workflows"]["build-test-deploy"]["jobs"].append({
                "setup-apigeex": {
                    "requires": ["deploy-lambda"],
                    "context": ["gcp-credentials"]
                }
            })
        
        return config
    
    def save_config(self, config: Dict[str, Any], output_path: str = ".circleci/config.yml"):
        """Save CircleCI configuration to file"""
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        print(f"✅ CircleCI config saved to {output_path}")
    
    def update_config_from_user_input(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update CircleCI config based on user input
        
        Args:
            user_config: Dictionary with user configuration
                {
                    "model_name": str,
                    "instance_type": str,
                    "instance_count": int,
                    "enable_autoscaling": bool,
                    "min_instances": int,
                    "max_instances": int,
                    "enable_cache": bool,
                    "cache_ttl": int,
                    "aws_region": str,
                    "environment": str
                }
        """
        return self.generate_config(
            instance_type=user_config.get("instance_type", "ml.m5.xlarge"),
            instance_count=user_config.get("instance_count", 1),
            enable_autoscaling=user_config.get("enable_autoscaling", False),
            enable_cache=user_config.get("enable_cache", True),
            aws_region=user_config.get("aws_region", "eu-central-1"),
            environment=user_config.get("environment", "dev")
        )


def generate_circleci_config(model_name: str, user_config: Dict[str, Any], 
                            output_path: str = ".circleci/config.yml"):
    """
    Generate CircleCI configuration from user inputs
    
    Args:
        model_name: Name of the model
        user_config: User configuration dictionary
        output_path: Output path for config file
    """
    generator = CircleCIGenerator(model_name)
    config = generator.update_config_from_user_input(user_config)
    generator.save_config(config, output_path)
    return config
