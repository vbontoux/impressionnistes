"""
Lambda function to get pricing configuration
Admin only - retrieves pricing settings
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
    Get pricing configuration
    
    Returns:
        Pricing configuration data
    """
    logger.info("Get pricing configuration request")
    
    # Get pricing configuration
    config_manager = ConfigurationManager()
    pricing_config = config_manager.get_pricing_config()
    
    # Convert Decimal to float for JSON serialization
    pricing_data = {
        'base_seat_price': float(pricing_config.get('base_seat_price', 20.00)),
        'boat_rental_multiplier_skiff': float(pricing_config.get('boat_rental_multiplier_skiff', 2.5)),
        'boat_rental_price_crew': float(pricing_config.get('boat_rental_price_crew', 20.00)),
    }
    
    logger.info(f"Retrieved pricing configuration: {pricing_data}")
    
    return success_response(data=pricing_data)
