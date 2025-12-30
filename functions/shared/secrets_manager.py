"""
Centralized secrets management utility
Retrieves secrets from AWS Secrets Manager with caching
"""
import json
import logging
import boto3
from typing import Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize Secrets Manager client
secrets_client = boto3.client('secretsmanager')

# Cache for secrets to avoid repeated API calls
_secrets_cache = {}


def get_secret(secret_name: str, key: Optional[str] = None) -> str:
    """
    Get a secret from AWS Secrets Manager with caching
    
    Args:
        secret_name: Name of the secret in Secrets Manager
        key: Optional key within the secret JSON (if secret is a JSON object)
    
    Returns:
        Secret value as string
    
    Raises:
        Exception: If secret cannot be retrieved
    """
    # Check cache first
    cache_key = f"{secret_name}:{key}" if key else secret_name
    if cache_key in _secrets_cache:
        return _secrets_cache[cache_key]
    
    try:
        logger.info(f"Retrieving secret: {secret_name}")
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret_string = response['SecretString']
        
        # If key is specified, parse JSON and extract the key
        if key:
            secret_data = json.loads(secret_string)
            value = secret_data.get(key, '')
        else:
            value = secret_string
        
        # Cache the value
        _secrets_cache[cache_key] = value
        logger.info(f"Successfully retrieved secret: {secret_name}")
        
        return value
        
    except Exception as e:
        logger.error(f"Failed to retrieve secret {secret_name}: {str(e)}")
        raise


def get_stripe_api_key() -> str:
    """
    Get Stripe API key from AWS Secrets Manager
    
    Returns:
        Stripe API key
    """
    return get_secret('impressionnistes/stripe/api_key', 'api_key')


def get_stripe_webhook_secret() -> str:
    """
    Get Stripe webhook secret from AWS Secrets Manager
    
    Returns:
        Stripe webhook secret
    """
    return get_secret('impressionnistes/stripe/webhook_secret', 'webhook_secret')


def get_slack_admin_webhook() -> str:
    """
    Get Slack admin webhook URL from AWS Secrets Manager
    
    Returns:
        Slack admin webhook URL (empty string if not configured)
    """
    try:
        return get_secret('impressionnistes/slack/admin_webhook', 'webhook_url')
    except Exception as e:
        logger.warning(f"Slack admin webhook not configured: {e}")
        return ''


def get_slack_devops_webhook() -> str:
    """
    Get Slack devops webhook URL from AWS Secrets Manager
    
    Returns:
        Slack devops webhook URL (empty string if not configured)
    """
    try:
        return get_secret('impressionnistes/slack/devops_webhook', 'webhook_url')
    except Exception as e:
        logger.warning(f"Slack devops webhook not configured: {e}")
        return ''


def clear_cache():
    """Clear the secrets cache (useful for testing)"""
    global _secrets_cache
    _secrets_cache = {}
