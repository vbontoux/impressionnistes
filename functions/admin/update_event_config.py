"""
Lambda function to update event configuration
Admin only - updates event dates and registration periods
"""
import json
import logging
from datetime import datetime

from responses import success_response, validation_error, handle_exceptions
from auth_utils import require_admin, get_user_from_event
from configuration import ConfigurationManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validate_event_dates(updates, current_config):
    """
    Validate event date configuration
    
    Args:
        updates: Dictionary of date updates
        current_config: Current configuration to merge with updates
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Merge current config with updates to validate complete date set
    merged = {
        'event_date': updates.get('event_date', current_config.get('event_date')),
        'registration_start_date': updates.get('registration_start_date', current_config.get('registration_start_date')),
        'registration_end_date': updates.get('registration_end_date', current_config.get('registration_end_date')),
        'payment_deadline': updates.get('payment_deadline', current_config.get('payment_deadline')),
    }
    
    # Parse dates if they exist
    dates = {}
    for field, value in merged.items():
        if value:
            try:
                dates[field] = datetime.fromisoformat(value)
            except (ValueError, TypeError):
                return False, f"Invalid date format for {field}. Use YYYY-MM-DD format."
    
    # Validate date logic only if both dates exist
    if 'registration_start_date' in dates and 'registration_end_date' in dates:
        if dates['registration_start_date'] >= dates['registration_end_date']:
            return False, "Registration start date must be before end date"
    
    if 'registration_end_date' in dates and 'payment_deadline' in dates:
        if dates['registration_end_date'] > dates['payment_deadline']:
            return False, "Payment deadline must be on or after registration end date"
    
    if 'registration_end_date' in dates and 'event_date' in dates:
        if dates['registration_end_date'] >= dates['event_date']:
            return False, "Registration must close before the event date"
    
    if 'payment_deadline' in dates and 'event_date' in dates:
        if dates['payment_deadline'] >= dates['event_date']:
            return False, "Payment deadline must be before the event date"
    
    return True, None


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Update event configuration
    
    Expected body:
    {
        "event_date": "2025-05-01",
        "registration_start_date": "2025-03-19",
        "registration_end_date": "2025-04-19",
        "payment_deadline": "2025-04-25",
        "rental_priority_days": 15
    }
    
    Returns:
        Updated event configuration
    """
    logger.info("Update event configuration request")
    
    # Get authenticated user
    user_info = get_user_from_event(event)
    admin_user_id = user_info['user_id']
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error('Invalid JSON in request body')
    
    # Validate that at least one field is provided
    allowed_fields = ['event_date', 'registration_start_date', 'registration_end_date', 
                     'payment_deadline', 'rental_priority_days']
    updates = {k: v for k, v in body.items() if k in allowed_fields}
    
    if not updates:
        return validation_error('No valid fields provided for update')
    
    # Get current configuration for validation
    config_manager = ConfigurationManager()
    current_config = config_manager.get_system_config()
    
    # Validate date logic
    is_valid, error_message = validate_event_dates(updates, current_config)
    if not is_valid:
        return validation_error(error_message)
    
    # Validate rental_priority_days if provided
    if 'rental_priority_days' in updates:
        try:
            days = int(updates['rental_priority_days'])
            if days < 0 or days > 90:
                return validation_error('Rental priority days must be between 0 and 90')
            updates['rental_priority_days'] = days
        except (ValueError, TypeError):
            return validation_error('Rental priority days must be a valid number')
    
    # Update configuration
    try:
        config_manager.update_config('SYSTEM', updates, admin_user_id)
        logger.info(f"Event configuration updated by admin {admin_user_id}: {updates}")
    except Exception as e:
        logger.error(f"Failed to update event configuration: {str(e)}")
        return validation_error(f'Failed to update configuration: {str(e)}')
    
    # Get updated configuration
    system_config = config_manager.get_system_config()
    event_config = {
        'event_date': system_config.get('event_date', '2025-05-01'),
        'registration_start_date': system_config.get('registration_start_date'),
        'registration_end_date': system_config.get('registration_end_date'),
        'payment_deadline': system_config.get('payment_deadline'),
        'rental_priority_days': system_config.get('rental_priority_days', 15),
    }
    
    return success_response(
        data=event_config,
        message='Event configuration updated successfully'
    )
