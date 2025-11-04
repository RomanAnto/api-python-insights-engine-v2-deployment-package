"""
Configuration management for deployment package.
Handles environment variables and deployment flags.
"""

import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class InstanceConfig:
    """SageMaker instance configuration"""
    type: str = "ml.m5.xlarge"
    count: int = 1
    volume_size_gb: int = 50
    region: str = "eu-central-1"
    tags: Dict[str, str] = None

@dataclass
class CacheConfig:
    """Redis/Valkey cache configuration"""
    enabled: bool = True
    ttl: int = 3600

@dataclass
class AutoScalingConfig:
    """Auto-scaling configuration"""
    enabled: bool = False
    min_instances: int = 1
    max_instances: int = 4
    target_invocations_per_instance: int = 100

@dataclass
class DeploymentConfig:
    """Main deployment configuration"""
    name: str
    type: str = "sagemaker"
    version: Dict[str, int] = None
    instance: InstanceConfig = None
    cache: CacheConfig = None
    autoscaling: AutoScalingConfig = None
    deploy_timeout: int = 900
    environment: str = "dev"
    
    def __post_init__(self):
        if self.instance is None:
            self.instance = InstanceConfig()
        if self.cache is None:
            self.cache = CacheConfig()
        if self.autoscaling is None:
            self.autoscaling = AutoScalingConfig()
        if self.version is None:
            self.version = {"major": 1, "minor": 0}

def get_env(var: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable"""
    return os.getenv(var, default)

def load_release_config(config_path: str = "release.yaml") -> DeploymentConfig:
    """Load configuration from release.yaml"""
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    return DeploymentConfig(
        name=config_data.get('name'),
        type=config_data.get('type', 'sagemaker'),
        version=config_data.get('version', {"major": 1, "minor": 0}),
        instance=InstanceConfig(**config_data.get('instance', {})),
        cache=CacheConfig(**config_data.get('cache', {})),
        autoscaling=AutoScalingConfig(**config_data.get('autoscaling', {})),
        deploy_timeout=config_data.get('deployTimeout', 900),
        environment=get_env('ENVIRONMENT', 'dev')
    )

def save_release_config(config: DeploymentConfig, config_path: str = "release.yaml"):
    """Save configuration to release.yaml"""
    config_dict = {
        'name': config.name,
        'type': config.type,
        'version': config.version,
        'instance': {
            'type': config.instance.type,
            'count': config.instance.count,
            'volumeSizeInGB': config.instance.volume_size_gb,
            'region': config.instance.region,
            'tags': config.instance.tags or {}
        },
        'cache': {
            'enabled': config.cache.enabled,
            'ttl': config.cache.ttl
        },
        'autoscaling': {
            'enabled': config.autoscaling.enabled,
            'minInstances': config.autoscaling.min_instances,
            'maxInstances': config.autoscaling.max_instances,
            'targetInvocationsPerInstance': config.autoscaling.target_invocations_per_instance
        },
        'deployTimeout': config.deploy_timeout,
        'sagemaker': {
            'bucket': 'insights-engine-sagemaker-models',
            'model_name': config.name,
            'endpoint_name': f"{config.name}-endpoint",
            'model_desc': f"{config.name} ML model",
            'instance_type': config.instance.type,
            'instance_count': config.instance.count
        }
    }
    
    with open(config_path, 'w') as f:
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
