"""
Lambda function to update a rental boat hull in inventory
Admin only - updates boat name, status, or requester
Note: This is different from boat_registration which is a team's race registration
"""
import json
import logging
from datetime import datetime
from urllib.parse import unquote

from responses import success_response, validation_error, not_found_error, handle_exceptions
from auth_utils import require_admin, get_user_from_event
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Valid boat types
VALID_BOAT_TYPES = ['skiff', '4-', '4+', '4x-', '4x+', '8+', '8x+']

# Valid statuses
# Note: 'requested' and 'paid' are system-only
# - 'requested': set when team manager requests boat
# - 'paid': set when team manager completes payment
VALID_STATUSES = ['new', 'available', 'requested', 'confirmed', 'paid']
ADMIN_SETTABLE_STATUSES = ['new', 'available', 'confirmed']  # Admin cannot manually set 'requested' or 'paid'


def validate_update_data(data):
    """
    Validate rental boat update data
    
    Args:
        data: Dictionary with update data
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # At least one field must be provided
    allowed_fields = ['boat_name', 'status', 'requester']
    if not any(field in data for field in allowed_fields):
        return False, "At least one field must be provided for update"
    
    # Validate boat_name if provided
    if 'boat_name' in data:
        boat_name = data['boat_name'].strip()
        if not boat_name:
            return False, "boat_name cannot be empty"
        if len(boat_name) > 100:
            return False, "boat_name must be 100 characters or less"
    
    # Validate status if provided
    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            return False, f"status must be one of: {', '.join(VALID_STATUSES)}"
        
        # Admin cannot manually set system-only statuses
        if data['status'] == 'requested':
            return False, "Status 'requested' can only be set by the system when a team manager requests a boat"
        
        if data['status'] == 'paid':
            return False, "Status 'paid' can only be set by the system when a team manager completes payment"
    
    # Validate requester if provided (can be None or email string)
    if 'requester' in data:
        if data['requester'] is not None and not isinstance(data['requester'], str):
            return False, "requester must be a string or null"
    
    return True, None


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Update a rental boat hull in inventory
    
    Path parameter:
        rental_boat_id: ID of the rental boat to update
    
    Expected body:
    {
        "boat_name": "New Name",  // optional
        "status": "available",     // optional
        "requester": "user@example.com"  // optional
    }
    
    Returns:
        Updated rental boat object
    """
    logger.info("Update rental boat request")
    
    # Get authenticated user
    user_info = get_user_from_event(event)
    admin_user_id = user_info['user_id']
    
    # Get rental_boat_id from path parameters and URL-decode it
    rental_boat_id = event.get('pathParameters', {}).get('rental_boat_id')
    if not rental_boat_id:
        return validation_error('rental_boat_id is required in path')
    
    # URL-decode the ID (API Gateway doesn't decode path parameters)
    rental_boat_id = unquote(rental_boat_id)
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error('Invalid JSON in request body')
    
    # Validate update data
    is_valid, error_message = validate_update_data(body)
    if not is_valid:
        return validation_error(error_message)
    
    # Get existing rental boat
    db = get_db_client()
    
    try:
        rental_boat = db.get_item(rental_boat_id, 'METADATA')
        if not rental_boat:
            return not_found_error('rental_boat', rental_boat_id)
    except Exception as e:
        logger.error(f"Failed to get rental boat: {str(e)}")
        return validation_error(f'Failed to get rental boat: {str(e)}')
    
    # Update fields
    current_time = datetime.utcnow().isoformat() + 'Z'
    
    if 'boat_name' in body:
        rental_boat['boat_name'] = body['boat_name'].strip()
    
    if 'status' in body:
        new_status = body['status']
        
        # Cannot confirm without a requester
        if new_status == 'confirmed' and not rental_boat.get('requester'):
            return validation_error('Cannot confirm rental boat without a requester. Status must be "requested" first.')
        
        # Cannot change status if already paid
        if rental_boat.get('status') == 'paid':
            return validation_error('Cannot change status of a paid rental boat')
        
        rental_boat['status'] = new_status
        # Clear requester if status is set to 'new' or 'available' (rejecting/cancelling)
        if new_status in ['new', 'available']:
            rental_boat['requester'] = None
            logger.info(f"Cleared requester when changing status to {new_status}")
    
    if 'requester' in body:
        rental_boat['requester'] = body['requester']
    
    rental_boat['updated_at'] = current_time
    rental_boat['updated_by'] = admin_user_id
    
    # Save to database
    try:
        db.put_item(rental_boat)
        logger.info(f"Rental boat updated: {rental_boat_id} - {rental_boat['boat_name']}")
    except Exception as e:
        logger.error(f"Failed to update rental boat: {str(e)}")
        return validation_error(f'Failed to update rental boat: {str(e)}')
    
    return success_response(
        data=rental_boat,
        message='Rental boat updated successfully'
    )
