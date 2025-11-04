"""
Utility functions for deployment progress tracking and reporting.
"""

import subprocess
import sys
from typing import Dict, Any
from datetime import datetime


def show_progress(msg: str):
    """Display progress message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    sys.stdout.flush()


def create_feature_branch(branch_name: str):
    """Create and checkout a feature branch"""
    try:
        # Check if we're in a git repo
        subprocess.run(["git", "rev-parse", "--git-dir"], 
                      check=True, capture_output=True)
        
        # Create and checkout branch
        subprocess.run(["git", "checkout", "-b", branch_name], 
                      check=True, capture_output=True)
        show_progress(f"✅ Created feature branch: {branch_name}")
    except subprocess.CalledProcessError:
        show_progress("⚠️  Not a git repository. Skipping branch creation.")
    except Exception as e:
        show_progress(f"⚠️  Could not create branch: {str(e)}")


class UserInputCollector:
    """Collect user inputs for deployment configuration"""
    
    INSTANCE_TYPES = {
        "1": ("ml.t3.medium", "Dev/Test - 2 vCPU, 4GB RAM"),
        "2": ("ml.m5.large", "General Purpose - 2 vCPU, 8GB RAM"),
        "3": ("ml.m5.xlarge", "Recommended - 4 vCPU, 16GB RAM"),
        "4": ("ml.m5.2xlarge", "Medium Load - 8 vCPU, 32GB RAM"),
        "5": ("ml.c5.xlarge", "Compute Optimized - 4 vCPU, 8GB RAM"),
        "6": ("ml.c5.2xlarge", "High Performance - 8 vCPU, 16GB RAM"),
        "7": ("ml.r5.xlarge", "Memory Optimized - 4 vCPU, 32GB RAM"),
        "8": ("ml.g4dn.xlarge", "GPU Accelerated - 4 vCPU, 16GB RAM, 1 GPU"),
    }
    
    def collect_all_inputs(self, model_name: str) -> Dict[str, Any]:
        """Collect all user inputs interactively"""
        print("\n" + "="*60)
        print(f"🚀 ML Model Deployment Configuration: {model_name}")
        print("="*60 + "\n")
        
        config = {
            "model_name": model_name
        }
        
        # Environment
        config["environment"] = self._ask_environment()
        
        # Instance type
        config["instance_type"] = self._ask_instance_type()
        
        # Instance count
        config["instance_count"] = self._ask_instance_count(config["environment"])
        
        # Auto-scaling
        if config["environment"] in ["staging", "prod"]:
            config.update(self._ask_autoscaling())
        else:
            config["enable_autoscaling"] = False
        
        # Cache settings
        config.update(self._ask_cache_settings())
        
        # AWS Region
        config["aws_region"] = self._ask_region()
        
        # Team name
        config["team_name"] = self._ask_team_name()
        
        # Volume size
        config["volume_size"] = self._ask_volume_size()
        
        # Display summary
        self._display_summary(config)
        
        return config
    
    def _ask_environment(self) -> str:
        """Ask for deployment environment"""
        print("Select deployment environment:")
        print("  1. dev (Development)")
        print("  2. qa (Quality Assurance)")
        print("  3. staging (Staging)")
        print("  4. prod (Production)")
        
        env_map = {"1": "dev", "2": "qa", "3": "staging", "4": "prod"}
        choice = input("Enter choice [1-4] (default: 1): ").strip() or "1"
        return env_map.get(choice, "dev")
    
    def _ask_instance_type(self) -> str:
        """Ask for SageMaker instance type"""
        print("\nSelect SageMaker instance type:")
        for key, (instance, desc) in self.INSTANCE_TYPES.items():
            print(f"  {key}. {instance:20s} - {desc}")
        
        choice = input("\nEnter choice [1-8] (default: 3): ").strip() or "3"
        instance_type, _ = self.INSTANCE_TYPES.get(choice, self.INSTANCE_TYPES["3"])
        return instance_type
    
    def _ask_instance_count(self, environment: str) -> int:
        """Ask for number of instances"""
        default = 1 if environment == "dev" else 2
        count = input(f"\nNumber of instances (default: {default}): ").strip()
        
        try:
            return int(count) if count else default
        except ValueError:
            return default
    
    def _ask_autoscaling(self) -> Dict[str, Any]:
        """Ask for auto-scaling configuration"""
        enable = input("\nEnable auto-scaling? (y/n, default: n): ").strip().lower()
        
        if enable == 'y':
            min_instances = int(input("  Minimum instances (default: 1): ").strip() or "1")
            max_instances = int(input("  Maximum instances (default: 4): ").strip() or "4")
            target = int(input("  Target invocations per instance (default: 100): ").strip() or "100")
            
            return {
                "enable_autoscaling": True,
                "min_instances": min_instances,
                "max_instances": max_instances,
                "target_invocations": target
            }
        
        return {"enable_autoscaling": False}
    
    def _ask_cache_settings(self) -> Dict[str, Any]:
        """Ask for cache configuration"""
        enable = input("\nEnable Redis caching? (y/n, default: y): ").strip().lower()
        
        if enable != 'n':
            ttl = input("  Cache TTL in seconds (default: 3600): ").strip()
            return {
                "enable_cache": True,
                "cache_ttl": int(ttl) if ttl else 3600
            }
        
        return {"enable_cache": False}
    
    def _ask_region(self) -> str:
        """Ask for AWS region"""
        print("\nAWS Region (common options):")
        print("  1. eu-central-1 (Frankfurt)")
        print("  2. us-east-1 (N. Virginia)")
        print("  3. us-west-2 (Oregon)")
        print("  4. ap-southeast-1 (Singapore)")
        
        region_map = {
            "1": "eu-central-1",
            "2": "us-east-1",
            "3": "us-west-2",
            "4": "ap-southeast-1"
        }
        
        choice = input("Enter choice [1-4] or custom region (default: 1): ").strip() or "1"
        return region_map.get(choice, choice)
    
    def _ask_team_name(self) -> str:
        """Ask for team name"""
        team = input("\nTeam name (for tagging, default: ml-team): ").strip()
        return team if team else "ml-team"
    
    def _ask_volume_size(self) -> int:
        """Ask for EBS volume size"""
        size = input("\nEBS volume size in GB (default: 50): ").strip()
        try:
            return int(size) if size else 50
        except ValueError:
            return 50
    
    def _display_summary(self, config: Dict[str, Any]):
        """Display configuration summary"""
        print("\n" + "="*60)
        print("📋 Configuration Summary")
        print("="*60)
        print(f"Model Name:         {config['model_name']}")
        print(f"Environment:        {config['environment']}")
        print(f"Instance Type:      {config['instance_type']}")
        print(f"Instance Count:     {config['instance_count']}")
        print(f"Auto-scaling:       {'Enabled' if config.get('enable_autoscaling') else 'Disabled'}")
        if config.get('enable_autoscaling'):
            print(f"  Min Instances:    {config.get('min_instances')}")
            print(f"  Max Instances:    {config.get('max_instances')}")
        print(f"Caching:            {'Enabled' if config.get('enable_cache') else 'Disabled'}")
        if config.get('enable_cache'):
            print(f"  Cache TTL:        {config.get('cache_ttl')}s")
        print(f"AWS Region:         {config['aws_region']}")
        print(f"Team:               {config['team_name']}")
        print(f"Volume Size:        {config['volume_size']} GB")
        print("="*60 + "\n")
        
        confirm = input("Proceed with this configuration? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Aborted.")
            sys.exit(0)
