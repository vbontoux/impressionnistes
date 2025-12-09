"""
Lambda function to create a new rental boat hull in inventory
Admin only - adds physical boat hulls available for rental
Note: This is different from boat_registration which is a team's race registration
"""
import json
import logging
import uuid
from datetime import datetime

from responses import success_response, validation_error, handle_exceptions
from auth_utils import require_admin, get_user_from_event
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Valid boat types
VALID_BOAT_TYPES = ['skiff', '4-', '4+', '4x-', '4x+', '8+', '8x+']

# Valid statuses
VALID_STATUSES = ['new', 'available', 'requested', 'confirmed', 'paid']


def validate_rental_boat_data(data):
    """
    Validate boat creation data
    
    Args:
        data: Dictionary with boat data
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Validate boat_type
    if 'boat_type' not in data:
        return False, "boat_type is required"
    
    if data['boat_type'] not in VALID_BOAT_TYPES:
        return False, f"boat_type must be one of: {', '.join(VALID_BOAT_TYPES)}"
    
    # Validate boat_name
    if 'boat_name' not in data:
        return False, "boat_name is required"
    
    boat_name = data['boat_name'].strip()
    if not boat_name:
        return False, "boat_name cannot be empty"
    
    if len(boat_name) > 100:
        return False, "boat_name must be 100 characters or less"
    
    # Validate status (optional, defaults to 'new')
    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            return False, f"status must be one of: {', '.join(VALID_STATUSES)}"
    
    # Validate rower_weight_range (optional)
    if 'rower_weight_range' in data and data['rower_weight_range']:
        weight_range = data['rower_weight_range'].strip()
        if len(weight_range) > 50:
            return False, "rower_weight_range must be 50 characters or less"
    
    return True, None


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Create a new rental boat hull in inventory
    
    Expected body:
    {
        "boat_type": "skiff",
        "boat_name": "Blue Lightning",
        "status": "new"  // optional, defaults to 'new'
    }
    
    Returns:
        Created rental boat object
    """
    logger.info("Create rental boat request")
    
    # Get authenticated user
    user_info = get_user_from_event(event)
    admin_user_id = user_info['user_id']
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error('Invalid JSON in request body')
    
    # Validate rental boat data
    is_valid, error_message = validate_rental_boat_data(body)
    if not is_valid:
        return validation_error(error_message)
    
    # Generate rental boat ID
    rental_boat_id = f"RENTAL_BOAT#{str(uuid.uuid4())}"
    
    # Prepare rental boat object
    current_time = datetime.utcnow().isoformat() + 'Z'
    rental_boat = {
        'PK': rental_boat_id,
        'SK': 'METADATA',
        'rental_boat_id': rental_boat_id,
        'boat_type': body['boat_type'],
        'boat_name': body['boat_name'].strip(),
        'status': body.get('status', 'new'),
        'rower_weight_range': body.get('rower_weight_range', '').strip() if body.get('rower_weight_range') else None,
        'requester': None,  # No requester initially
        'paid_at': None,  # Will be set when payment is completed
        'created_by': admin_user_id,
        'created_at': current_time,
        'updated_at': current_time
    }
    
    # Save to database
    db = get_db_client()
    
    try:
        db.put_item(rental_boat)
        logger.info(f"Rental boat created: {rental_boat_id} - {rental_boat['boat_name']} ({rental_boat['boat_type']})")
    except Exception as e:
        logger.error(f"Failed to create rental boat: {str(e)}")
        return validation_error(f'Failed to create rental boat: {str(e)}')
    
    return success_response(
        data=rental_boat,
        message='Rental boat created successfully'
    )
