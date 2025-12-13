"""
Lambda function to cancel a rental boat request
Team manager can cancel their own rental requests (requested or confirmed status)
The boat will return to 'available' status
"""
import json
import logging
from datetime import datetime
from urllib.parse import unquote

from responses import success_response, validation_error, not_found_error, handle_exceptions
from auth_utils import require_team_manager, get_user_from_event
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager
def lambda_handler(event, context):
    """
    Cancel a rental boat request
    
    Path parameter:
        rental_boat_id: ID of the rental boat to cancel
    
    Returns:
        Success message
    """
    logger.info("Cancel rental request")
    
    # Get authenticated user
    user_info = get_user_from_event(event)
    team_manager_email = user_info.get('email')
    
    # Get rental_boat_id from path parameters and URL-decode it
    rental_boat_id = event.get('pathParameters', {}).get('rental_boat_id')
    if not rental_boat_id:
        return validation_error('rental_boat_id is required in path')
    
    # URL-decode the ID
    rental_boat_id = unquote(rental_boat_id)
    
    # Get existing rental boat
    db = get_db_client()
    
    try:
        rental_boat = db.get_item(rental_boat_id, 'METADATA')
        if not rental_boat:
            return not_found_error('rental_boat', rental_boat_id)
    except Exception as e:
        logger.error(f"Failed to get rental boat: {str(e)}")
        return validation_error(f'Failed to get rental boat: {str(e)}')
    
    # Verify the rental belongs to this team manager
    if rental_boat.get('requester') != team_manager_email:
        return validation_error('You can only cancel your own rental requests')
    
    # Check if rental can be cancelled
    current_status = rental_boat.get('status')
    
    if current_status == 'paid':
        return validation_error('Cannot cancel a paid rental. Please contact the administrator.')
    
    if current_status not in ['requested', 'confirmed']:
        return validation_error(f'Cannot cancel rental with status: {current_status}')
    
    # Update rental boat to available status
    current_time = datetime.utcnow().isoformat() + 'Z'
    
    rental_boat['status'] = 'available'
    rental_boat['requester'] = None
    rental_boat['requested_at'] = None
    rental_boat['confirmed_at'] = None
    rental_boat['updated_at'] = current_time
    
    # Save to database
    try:
        db.put_item(rental_boat)
        logger.info(f"Rental request cancelled: {rental_boat_id} - {rental_boat['boat_name']}")
    except Exception as e:
        logger.error(f"Failed to cancel rental request: {str(e)}")
        return validation_error(f'Failed to cancel rental request: {str(e)}')
    
    return success_response(
        data=rental_boat,
        message='Rental request cancelled successfully'
    )
