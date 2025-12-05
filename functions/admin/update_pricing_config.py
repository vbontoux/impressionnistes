"""
Lambda function to update pricing configuration
Admin only - updates pricing settings
"""
import json
import logging
from decimal import Decimal

from responses import success_response, validation_error, handle_exceptions
from auth_utils import require_admin, get_user_from_event
from configuration import ConfigurationManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validate_pricing(updates):
    """
    Validate pricing configuration
    
    Args:
        updates: Dictionary of pricing updates
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Validate base_seat_price
    if 'base_seat_price' in updates:
        try:
            price = float(updates['base_seat_price'])
            if price <= 0:
                return False, "Base seat price must be greater than 0"
            if price > 1000:
                return False, "Base seat price must be less than 1000 euros"
        except (ValueError, TypeError):
            return False, "Base seat price must be a valid number"
    
    # Validate boat_rental_multiplier_skiff
    if 'boat_rental_multiplier_skiff' in updates:
        try:
            multiplier = float(updates['boat_rental_multiplier_skiff'])
            if multiplier <= 0:
                return False, "Boat rental multiplier must be greater than 0"
            if multiplier > 10:
                return False, "Boat rental multiplier must be less than 10"
        except (ValueError, TypeError):
            return False, "Boat rental multiplier must be a valid number"
    
    # Validate boat_rental_price_crew
    if 'boat_rental_price_crew' in updates:
        try:
            price = float(updates['boat_rental_price_crew'])
            if price < 0:
                return False, "Boat rental price must be 0 or greater"
            if price > 1000:
                return False, "Boat rental price must be less than 1000 euros"
        except (ValueError, TypeError):
            return False, "Boat rental price must be a valid number"
    
    return True, None


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Update pricing configuration
    
    Expected body:
    {
        "base_seat_price": 20.00,
        "boat_rental_multiplier_skiff": 2.5,
        "boat_rental_price_crew": 20.00
    }
    
    Returns:
        Updated pricing configuration
    """
    logger.info("Update pricing configuration request")
    
    # Get authenticated user
    user_info = get_user_from_event(event)
    admin_user_id = user_info['user_id']
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error('Invalid JSON in request body')
    
    # Validate that at least one field is provided
    allowed_fields = ['base_seat_price', 'boat_rental_multiplier_skiff', 'boat_rental_price_crew']
    updates = {k: v for k, v in body.items() if k in allowed_fields}
    
    if not updates:
        return validation_error('No valid fields provided for update')
    
    # Validate pricing values
    is_valid, error_message = validate_pricing(updates)
    if not is_valid:
        return validation_error(error_message)
    
    # Convert to Decimal for DynamoDB
    decimal_updates = {}
    for key, value in updates.items():
        try:
            decimal_updates[key] = Decimal(str(value))
        except Exception as e:
            return validation_error(f'Invalid value for {key}: {str(e)}')
    
    # Update configuration
    config_manager = ConfigurationManager()
    
    try:
        config_manager.update_config('PRICING', decimal_updates, admin_user_id)
        logger.info(f"Pricing configuration updated by admin {admin_user_id}: {decimal_updates}")
    except Exception as e:
        logger.error(f"Failed to update pricing configuration: {str(e)}")
        return validation_error(f'Failed to update configuration: {str(e)}')
    
    # Get updated configuration
    pricing_config = config_manager.get_pricing_config()
    
    # Convert Decimal to float for JSON response
    pricing_data = {
        'base_seat_price': float(pricing_config.get('base_seat_price', 20.00)),
        'boat_rental_multiplier_skiff': float(pricing_config.get('boat_rental_multiplier_skiff', 2.5)),
        'boat_rental_price_crew': float(pricing_config.get('boat_rental_price_crew', 20.00)),
    }
    
    return success_response(
        data=pricing_data,
        message='Pricing configuration updated successfully'
    )
