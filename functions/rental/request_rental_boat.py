"""
Lambda function for team managers to request a rental boat
Team manager accessible - creates a rental request

⚠️ DEPRECATED: This endpoint is part of the old inventory-based rental system.
Use create_rental_request.py instead for the new request-based system.
This endpoint will be removed after migration is complete.
See: .kiro/specs/boat-rental-refactoring/design.md
"""
import json
import logging
from datetime import datetime

from responses import success_response, validation_error, not_found_error, handle_exceptions
from auth_utils import require_auth, get_user_from_event
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validate_request_data(data):
    """
    Validate rental boat request data
    
    Args:
        data: Dictionary with request data
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Validate rental_boat_id
    if 'rental_boat_id' not in data:
        return False, "rental_boat_id is required"
    
    if not data['rental_boat_id'].strip():
        return False, "rental_boat_id cannot be empty"
    
    return True, None


@handle_exceptions
@require_auth
def lambda_handler(event, context):
    """
    Request a rental boat for a team manager
    
    Expected body:
    {
        "rental_boat_id": "RENTAL_BOAT#uuid"
    }
    
    Returns:
        Confirmation with boat details
    """
    logger.info("Request rental boat")
    
    # Get authenticated user
    user_info = get_user_from_event(event)
    team_manager_id = user_info['user_id']
    team_manager_email = user_info.get('email', team_manager_id)
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error('Invalid JSON in request body')
    
    # Validate request data
    is_valid, error_message = validate_request_data(body)
    if not is_valid:
        return validation_error(error_message)
    
    rental_boat_id = body['rental_boat_id'].strip()
    
    # Get the rental boat and check availability
    db = get_db_client()
    
    try:
        rental_boat = db.get_item(rental_boat_id, 'METADATA')
        if not rental_boat:
            return not_found_error('rental_boat', rental_boat_id)
    except Exception as e:
        logger.error(f"Failed to get rental boat: {str(e)}")
        return validation_error(f'Failed to get rental boat: {str(e)}')
    
    # Check if boat is available
    current_status = rental_boat.get('status', 'new')
    if current_status not in ['available', 'new']:
        return validation_error(f'Boat is not available for rental. Current status: {current_status}')
    
    # Check if boat already has a requester
    if rental_boat.get('requester'):
        return validation_error('Boat is already requested by another team manager')
    
    # Update boat status to "requested" and set requester
    current_time = datetime.utcnow().isoformat() + 'Z'
    
    rental_boat['status'] = 'requested'
    rental_boat['requester'] = team_manager_email
    rental_boat['requested_at'] = current_time
    rental_boat['updated_at'] = current_time
    rental_boat['updated_by'] = team_manager_id
    
    # Save updated boat to database
    try:
        db.put_item(rental_boat)
        logger.info(f"Rental boat requested: {rental_boat_id} by team manager {team_manager_id} ({team_manager_email})")
    except Exception as e:
        logger.error(f"Failed to update rental boat: {str(e)}")
        return validation_error(f'Failed to request rental boat: {str(e)}')
    
    # Return confirmation with boat details
    return success_response(
        data={
            'rental_boat_id': rental_boat_id,
            'boat_type': rental_boat.get('boat_type'),
            'boat_name': rental_boat.get('boat_name'),
            'rower_weight_range': rental_boat.get('rower_weight_range'),
            'status': rental_boat.get('status'),
            'requested_at': rental_boat.get('requested_at'),
            'requester': rental_boat.get('requester')
        },
        message='Rental boat request submitted successfully. An admin will review your request.'
    )