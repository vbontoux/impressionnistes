"""
Lambda function to get event configuration
Admin only - retrieves event dates and registration periods
"""
import json
import logging

from responses import success_response, handle_exceptions
from auth_utils import require_admin
from configuration import ConfigurationManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Get event configuration including dates and registration periods
    
    Returns:
        Event configuration data
    """
    logger.info("Get event configuration request")
    
    # Get system configuration
    config_manager = ConfigurationManager()
    system_config = config_manager.get_system_config()
    
    # Extract event-related configuration
    event_config = {
        'event_date': system_config.get('event_date', '2025-05-01'),
        'registration_start_date': system_config.get('registration_start_date'),
        'registration_end_date': system_config.get('registration_end_date'),
        'payment_deadline': system_config.get('payment_deadline'),
        'rental_priority_days': system_config.get('rental_priority_days', 15),
    }
    
    logger.info(f"Retrieved event configuration: {event_config}")
    
    return success_response(data=event_config)
