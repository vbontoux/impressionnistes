"""
Lambda function to get public event information
No authentication required - provides event dates for home page
"""
import json
import logging

from responses import success_response, handle_exceptions
from configuration import ConfigurationManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
def lambda_handler(event, context):
    """
    Get public event information including dates
    No authentication required - this is public information for the home page
    
    Returns:
        Public event information including dates
    """
    logger.info("Get public event info request")
    
    # Get system configuration
    config_manager = ConfigurationManager()
    system_config = config_manager.get_system_config()
    
    # Extract public event information
    event_info = {
        'event_date': system_config.get('event_date', '2025-05-01'),
        'registration_start_date': system_config.get('registration_start_date'),
        'registration_end_date': system_config.get('registration_end_date'),
        'payment_deadline': system_config.get('payment_deadline'),
    }
    
    logger.info(f"Retrieved public event info: {event_info}")
    
    return success_response(data=event_info)
