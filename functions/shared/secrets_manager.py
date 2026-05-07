"""
Centralized secrets management utility
Retrieves secrets from S3 bucket with caching
"""
import json
import logging
import os
import boto3
from typing import Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Cache for secrets to avoid repeated API calls
_secrets_cache = {}

# Lazy-initialized S3 client (avoids import-time issues in test environments)
_s3_client = None


def _get_s3_client():
    """Get or create the S3 client (lazy initialization)"""
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client('s3')
    return _s3_client


def get_secret(object_key: str, field: Optional[str] = None) -> str:
    """
    Get a secret from S3 bucket with caching

    Args:
        object_key: S3 object key (e.g., 'stripe/api_key')
        field: Optional field within the secret JSON (if secret is a JSON object)

    Returns:
        Secret value as string

    Raises:
        Exception: If secret cannot be retrieved
    """
    # Check cache first
    cache_key = f"{object_key}:{field}" if field else object_key
    if cache_key in _secrets_cache:
        return _secrets_cache[cache_key]

    bucket = os.environ.get('SECRETS_BUCKET', '')

    try:
        logger.info(f"Retrieving secret: {object_key}")
        client = _get_s3_client()
        response = client.get_object(Bucket=bucket, Key=object_key)
        secret_string = response['Body'].read().decode('utf-8')

        # If field is specified, parse JSON and extract the field
        if field:
            secret_data = json.loads(secret_string)
            value = secret_data.get(field, '')
        else:
            value = secret_string

        # Cache the value
        _secrets_cache[cache_key] = value
        logger.info(f"Successfully retrieved secret: {object_key}")

        return value

    except Exception as e:
        logger.error(f"Failed to retrieve secret {object_key}: {str(e)}")
        raise


def get_stripe_api_key() -> str:
    """
    Get Stripe API key from S3 secrets bucket

    Returns:
        Stripe API key
    """
    return get_secret('stripe/api_key', 'api_key')


def get_stripe_webhook_secret() -> str:
    """
    Get Stripe webhook secret from S3 secrets bucket

    Returns:
        Stripe webhook secret
    """
    return get_secret('stripe/webhook_secret', 'webhook_secret')


def get_slack_admin_webhook() -> str:
    """
    Get Slack admin webhook URL from S3 secrets bucket

    Returns:
        Slack admin webhook URL (empty string if not configured)
    """
    try:
        return get_secret('slack/admin_webhook', 'webhook_url')
    except Exception as e:
        logger.warning(f"Slack admin webhook not configured: {e}")
        return ''


def get_slack_devops_webhook() -> str:
    """
    Get Slack devops webhook URL from S3 secrets bucket

    Returns:
        Slack devops webhook URL (empty string if not configured)
    """
    try:
        return get_secret('slack/devops_webhook', 'webhook_url')
    except Exception as e:
        logger.warning(f"Slack devops webhook not configured: {e}")
        return ''


def clear_cache():
    """Clear the secrets cache (useful for testing)"""
    global _secrets_cache
    _secrets_cache = {}
