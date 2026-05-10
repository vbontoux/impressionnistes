"""
Configuration helper for environment-specific settings
"""
from typing import Dict, Any


class EnvironmentConfig:
    """Helper class to manage environment-specific configuration"""
    
    DEV_CONFIG = {
        "region": "eu-west-3",
        "table_name": "impressionnistes-registration-dev",
        "enable_point_in_time_recovery": False,
        "removal_policy": "DESTROY",
        "log_retention_days": 7,
        "enable_xray_tracing": False,
        "lambda_memory_size": 256,
        "api_throttle_rate_limit": 100,
        "api_throttle_burst_limit": 200,
        # CloudFront custom domain configuration
        "custom_domain": "impressionnistes-dev.aviron-rcpm.fr",
        # Wildcard certificate (*.aviron-rcpm.fr) shared across all environments.
        # Created in us-east-1 (required for CloudFront) in the prod account.
        "certificate_arn": "arn:aws:acm:us-east-1:206478392268:certificate/38b35b2f-317e-48e6-9e1a-08a625f9fd62",
    }
    
    PROD_CONFIG = {
        "region": "eu-west-3",
        "table_name": "impressionnistes-registration-prod",
        "enable_point_in_time_recovery": True,
        "removal_policy": "RETAIN",
        "log_retention_days": 90,
        "enable_xray_tracing": True,
        "lambda_memory_size": 512,
        "api_throttle_rate_limit": 1000,
        "api_throttle_burst_limit": 2000,
        # CloudFront custom domain configuration
        "custom_domain": "impressionnistes.aviron-rcpm.fr",
        # Wildcard certificate (*.aviron-rcpm.fr) shared across all environments
        "certificate_arn": "arn:aws:acm:us-east-1:206478392268:certificate/38b35b2f-317e-48e6-9e1a-08a625f9fd62",
    }
    
    @classmethod
    def get_config(cls, env: str) -> Dict[str, Any]:
        """
        Get configuration for specified environment
        
        Args:
            env: Environment name ('dev' or 'prod')
            
        Returns:
            Dictionary of configuration values
        """
        if env == "prod":
            return cls.PROD_CONFIG.copy()
        return cls.DEV_CONFIG.copy()
    
    @classmethod
    def get_value(cls, env: str, key: str, default: Any = None) -> Any:
        """
        Get specific configuration value
        
        Args:
            env: Environment name
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        config = cls.get_config(env)
        return config.get(key, default)
