"""
Main entry point for ML deployment package.
Handles deployment to AWS (SageMaker/EKS), Lambda, Redis, API Gateway, ApigeeX.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from config import load_release_config, DeploymentConfig, save_release_config
from fastapi_generator import generate_fastapi_wrapper
from circleci_generator import generate_circleci_config
from utils import show_progress, create_feature_branch, UserInputCollector


def deploy_to_sagemaker(config: DeploymentConfig):
    """Deploy model to SageMaker"""
    from aws.sagemaker import deploy_sagemaker_endpoint
    show_progress(f"Deploying {config.name} to SageMaker...")
    return deploy_sagemaker_endpoint(config)


def deploy_lambda(config: DeploymentConfig, endpoint_name: str):
    """Deploy Lambda function"""
    from aws.lambda_deployer import deploy_lambda_function
    show_progress("Deploying Lambda function...")
    return deploy_lambda_function(config, endpoint_name)


def setup_api_gateway(config: DeploymentConfig, lambda_arn: str):
    """Setup API Gateway (Dev only)"""
    from aws.apigateway import setup_api_gateway_with_cognito
    show_progress("Setting up API Gateway...")
    return setup_api_gateway_with_cognito(config, lambda_arn)


def setup_apigeex(config: DeploymentConfig):
    """Setup ApigeeX proxy (Stage/Prod)"""
    from apigeex.proxy import setup_apigeex_proxy
    show_progress("Setting up ApigeeX proxy...")
    return setup_apigeex_proxy(config)


def initialize_project(model_name: str, output_path: str = "."):
    """
    Initialize a new ML deployment project
    Creates FastAPI wrapper and CircleCI config based on user inputs
    """
    show_progress(f"Initializing project: {model_name}")
    
    # Collect user inputs
    collector = UserInputCollector()
    user_config = collector.collect_all_inputs(model_name)
    
    # Create feature branch
    branch_name = f"feature/deploy-{model_name}"
    create_feature_branch(branch_name)
    
    # Generate FastAPI wrapper
    show_progress("Generating FastAPI wrapper...")
    generate_fastapi_wrapper(model_name, output_path)
    
    # Generate release.yaml
    show_progress("Generating release.yaml...")
    from config import DeploymentConfig, InstanceConfig, CacheConfig, AutoScalingConfig
    
    deployment_config = DeploymentConfig(
        name=model_name,
        type="sagemaker",
        version={"major": 1, "minor": 0},
        instance=InstanceConfig(
            type=user_config.get("instance_type", "ml.m5.xlarge"),
            count=user_config.get("instance_count", 1),
            volume_size_gb=user_config.get("volume_size", 50),
            region=user_config.get("aws_region", "eu-central-1"),
            tags={
                "managedby": "terraform",
                "project": "insight-engine-2.0",
                "team": user_config.get("team_name", "ml-team")
            }
        ),
        cache=CacheConfig(
            enabled=user_config.get("enable_cache", True),
            ttl=user_config.get("cache_ttl", 3600)
        ),
        autoscaling=AutoScalingConfig(
            enabled=user_config.get("enable_autoscaling", False),
            min_instances=user_config.get("min_instances", 1),
            max_instances=user_config.get("max_instances", 4),
            target_invocations_per_instance=user_config.get("target_invocations", 100)
        ),
        environment=user_config.get("environment", "dev")
    )
    
    save_release_config(deployment_config, os.path.join(output_path, "release.yaml"))
    
    # Generate CircleCI config
    show_progress("Generating CircleCI configuration...")
    circleci_path = os.path.join(output_path, ".circleci", "config.yml")
    generate_circleci_config(model_name, user_config, circleci_path)
    
    show_progress("✅ Project initialization complete!")
    show_progress(f"📋 Next steps:")
    show_progress(f"  1. Review generated files in {output_path}")
    show_progress(f"  2. Add your model files to src/model_loader.py")
    show_progress(f"  3. Customize src/prediction.py for your input/output")
    show_progress(f"  4. Test locally: docker build -t {model_name}:local .")
    show_progress(f"  5. Commit and push to trigger deployment")
    show_progress(f"     git add .")
    show_progress(f"     git commit -m 'feat: Add {model_name} deployment'")
    show_progress(f"     git push origin {branch_name}")


def deploy(config_path: str = "release.yaml", environment: str = "dev"):
    """
    Deploy ML model using configuration file
    """
    show_progress(f"Starting deployment for environment: {environment}")
    
    # Load configuration
    config = load_release_config(config_path)
    config.environment = environment
    
    # Deploy SageMaker endpoint
    endpoint_info = deploy_to_sagemaker(config)
    endpoint_name = endpoint_info["endpoint_name"]
    
    # Deploy Lambda
    lambda_info = deploy_lambda(config, endpoint_name)
    lambda_arn = lambda_info["function_arn"]
    
    # Setup API Gateway or ApigeeX
    if environment == "dev":
        api_info = setup_api_gateway(config, lambda_arn)
        show_progress("=" * 50)
        show_progress("🎉 Deployment Complete!")
        show_progress("=" * 50)
        show_progress(f"API Endpoint: {api_info['endpoint_url']}")
        show_progress(f"API Key: {api_info['api_key']}")
        show_progress(f"Environment: {environment}")
        show_progress("=" * 50)
    else:
        apigeex_info = setup_apigeex(config)
        show_progress("=" * 50)
        show_progress("🎉 Deployment Complete!")
        show_progress("=" * 50)
        show_progress(f"ApigeeX Endpoint: {apigeex_info['proxy_url']}")
        show_progress(f"Environment: {environment}")
        show_progress("Auth: Integrated with internal auth service")
        show_progress("=" * 50)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ML Deployment Package - Deploy models to SageMaker"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize new ML deployment project")
    init_parser.add_argument("model_name", help="Name of the model")
    init_parser.add_argument("--output", default=".", help="Output directory")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy ML model")
    deploy_parser.add_argument("--config", default="release.yaml", help="Configuration file")
    deploy_parser.add_argument("--environment", default="dev", 
                              choices=["dev", "qa", "staging", "prod"],
                              help="Deployment environment")
    
    args = parser.parse_args()
    
    if args.command == "init":
        initialize_project(args.model_name, args.output)
    elif args.command == "deploy":
        deploy(args.config, args.environment)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
