"""
Configuration Manager for DynamoDB-based configuration
Handles system, pricing, and notification configuration with caching
"""
import os
import boto3
import logging
from functools import lru_cache
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from decimal import Decimal

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Default configuration values
DEFAULT_SYSTEM_CONFIG = {
    'PK': 'CONFIG',
    'SK': 'SYSTEM',
    'registration_start_date': '2024-03-19',
    'registration_end_date': '2024-04-19',
    'payment_deadline': '2024-04-25',
    'rental_priority_days': 15,
    'competition_date': '2024-05-01',
    'temporary_editing_access_hours': 48,
    'created_at': '2024-01-01T00:00:00Z',
    'updated_at': '2024-01-01T00:00:00Z'
}

DEFAULT_PRICING_CONFIG = {
    'PK': 'CONFIG',
    'SK': 'PRICING',
    'base_seat_price': Decimal('20.00'),
    'boat_rental_multiplier_skiff': Decimal('2.5'),
    'boat_rental_price_crew': Decimal('20.00'),
    'currency': 'EUR',
    'created_at': '2024-01-01T00:00:00Z',
    'updated_at': '2024-01-01T00:00:00Z'
}

DEFAULT_NOTIFICATION_CONFIG = {
    'PK': 'CONFIG',
    'SK': 'NOTIFICATION',
    'notification_frequency_days': 7,
    'session_timeout_minutes': 30,
    'notification_channels': ['email', 'in_app', 'slack'],
    'email_from': 'impressionnistes@rcpm-aviron.fr',
    'slack_webhook_admin': '',
    'slack_webhook_devops': '',
    'created_at': '2024-01-01T00:00:00Z',
    'updated_at': '2024-01-01T00:00:00Z'
}


class ConfigurationManager:
    """
    Manages configuration stored in DynamoDB with caching
    """
    
    def __init__(self, table_name=None):
        """
        Initialize configuration manager
        
        Args:
            table_name: DynamoDB table name (defaults to TABLE_NAME env var)
        """
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = table_name or os.environ.get('TABLE_NAME', 'impressionnistes-registration-dev')
        self.table = self.dynamodb.Table(self.table_name)
        self._cache = {}
        self._cache_ttl = timedelta(minutes=5)
        logger.info(f"ConfigurationManager initialized with table: {self.table_name}")
    
    def get_system_config(self):
        """
        Get system configuration from DynamoDB with caching
        
        Returns:
            dict: System configuration
        """
        return self._get_config('SYSTEM', DEFAULT_SYSTEM_CONFIG)
    
    def get_pricing_config(self):
        """
        Get pricing configuration from DynamoDB with caching
        
        Returns:
            dict: Pricing configuration
        """
        return self._get_config('PRICING', DEFAULT_PRICING_CONFIG)
    
    def get_notification_config(self):
        """
        Get notification configuration from DynamoDB with caching
        
        Returns:
            dict: Notification configuration
        """
        return self._get_config('NOTIFICATION', DEFAULT_NOTIFICATION_CONFIG)
    
    def _get_config(self, config_type, default_config):
        """
        Get configuration with caching
        
        Args:
            config_type: Type of configuration (SYSTEM, PRICING, NOTIFICATION)
            default_config: Default configuration to return if not found
            
        Returns:
            dict: Configuration
        """
        cache_key = f'CONFIG#{config_type}'
        
        # Check cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if datetime.now() - cached_time < self._cache_ttl:
                logger.debug(f"Returning cached {config_type} configuration")
                return cached_data
        
        # Fetch from DynamoDB
        try:
            response = self.table.get_item(
                Key={'PK': 'CONFIG', 'SK': config_type}
            )
            config = response.get('Item')
            
            if not config:
                logger.warning(f"{config_type} configuration not found, using defaults")
                config = default_config.copy()
            
            # Cache the result
            self._cache[cache_key] = (config, datetime.now())
            logger.info(f"Fetched {config_type} configuration from DynamoDB")
            return config
            
        except Exception as e:
            logger.error(f"Failed to get {config_type} config: {str(e)}")
            return default_config.copy()
    
    def update_config(self, config_type, updates, admin_user_id):
        """
        Update configuration with audit trail
        
        Args:
            config_type: Type of configuration (SYSTEM, PRICING, NOTIFICATION)
            updates: Dictionary of fields to update
            admin_user_id: ID of admin making the change
            
        Returns:
            dict: Updated configuration
        """
        current_time = datetime.utcnow().isoformat() + 'Z'
        
        # Build update expression dynamically
        update_expression_parts = ['#updated_at = :time', '#updated_by = :user']
        expression_attribute_names = {
            '#updated_at': 'updated_at',
            '#updated_by': 'updated_by'
        }
        expression_attribute_values = {
            ':time': current_time,
            ':user': admin_user_id
        }
        
        # Add updates to expression
        for key, value in updates.items():
            attr_name = f'#{key}'
            attr_value = f':{key}'
            update_expression_parts.append(f'{attr_name} = {attr_value}')
            expression_attribute_names[attr_name] = key
            expression_attribute_values[attr_value] = value
        
        try:
            # Update DynamoDB
            response = self.table.update_item(
                Key={'PK': 'CONFIG', 'SK': config_type.upper()},
                UpdateExpression='SET ' + ', '.join(update_expression_parts),
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            
            # Clear cache
            cache_key = f'CONFIG#{config_type.upper()}'
            if cache_key in self._cache:
                del self._cache[cache_key]
            
            logger.info(f"Updated {config_type} configuration: {list(updates.keys())}")
            return response['Attributes']
            
        except Exception as e:
            logger.error(f"Failed to update {config_type} config: {str(e)}")
            raise
    
    def clear_cache(self):
        """Clear all cached configuration"""
        self._cache.clear()
        logger.info("Configuration cache cleared")


# Global configuration instance
_config_manager = None


def get_config_manager():
    """
    Get global configuration manager instance
    
    Returns:
        ConfigurationManager: Global configuration manager
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


# Helper functions for common operations
def get_base_seat_price():
    """
    Get current base seat price
    
    Returns:
        Decimal: Base seat price
    """
    config_manager = get_config_manager()
    pricing_config = config_manager.get_pricing_config()
    return pricing_config.get('base_seat_price', Decimal('20.00'))


def get_registration_period():
    """
    Get registration period dates
    
    Returns:
        dict: Registration period with start, end, and payment_deadline
    """
    config_manager = get_config_manager()
    system_config = config_manager.get_system_config()
    return {
        'start': system_config.get('registration_start_date'),
        'end': system_config.get('registration_end_date'),
        'payment_deadline': system_config.get('payment_deadline')
    }


def is_registration_active():
    """
    Check if registration period is currently active
    
    Returns:
        bool: True if registration is active
    """
    period = get_registration_period()
    today = datetime.now().date()
    
    try:
        start_date = datetime.fromisoformat(period['start']).date()
        end_date = datetime.fromisoformat(period['end']).date()
        return start_date <= today <= end_date
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid date format in registration period: {e}")
        return False


def is_payment_active():
    """
    Check if payment period is currently active
    
    Returns:
        bool: True if payment is active
    """
    period = get_registration_period()
    today = datetime.now().date()
    
    try:
        start_date = datetime.fromisoformat(period['start']).date()
        payment_deadline = datetime.fromisoformat(period['payment_deadline']).date()
        return start_date <= today <= payment_deadline
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid date format in payment period: {e}")
        return False
