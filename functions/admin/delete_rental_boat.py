"""
Lambda function to delete a rental boat hull from inventory
Admin only - removes rental boat hulls from the inventory
Note: This is different from boat_registration which is a team's race registration
"""
import json
import logging
from urllib.parse import unquote

from responses import success_response, validation_error, not_found_error, handle_exceptions
from auth_utils import require_admin, get_user_from_event
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Delete a rental boat hull from inventory
    
    Path parameter:
        rental_boat_id: ID of the rental boat to delete
    
    Returns:
        Success message
    """
    logger.info("Delete rental boat request")
    
    # Get authenticated user
    user_info = get_user_from_event(event)
    admin_user_id = user_info['user_id']
    
    # Get rental_boat_id from path parameters and URL-decode it
    rental_boat_id = event.get('pathParameters', {}).get('rental_boat_id')
    if not rental_boat_id:
        return validation_error('rental_boat_id is required in path')
    
    # URL-decode the ID (API Gateway doesn't decode path parameters)
    rental_boat_id = unquote(rental_boat_id)
    
    # Get existing rental boat to verify it exists
    db = get_db_client()
    
    try:
        rental_boat = db.get_item(rental_boat_id, 'METADATA')
        if not rental_boat:
            return not_found_error('rental_boat', rental_boat_id)
    except Exception as e:
        logger.error(f"Failed to get rental boat: {str(e)}")
        return validation_error(f'Failed to get rental boat: {str(e)}')
    
    # Check if rental boat is paid or confirmed
    status = rental_boat.get('status')
    if status == 'paid':
        return validation_error(
            'Cannot delete a rental boat that has been paid for. '
            'This rental is locked and cannot be deleted.'
        )
    
    if status == 'confirmed':
        return validation_error(
            'Cannot delete a rental boat that is confirmed for a team manager. '
            'Please change status to available or new first.'
        )
    
    # Delete from database
    try:
        db.delete_item(rental_boat_id, 'METADATA')
        logger.info(f"Rental boat deleted: {rental_boat_id} - {rental_boat.get('boat_name')} by admin {admin_user_id}")
    except Exception as e:
        logger.error(f"Failed to delete rental boat: {str(e)}")
        return validation_error(f'Failed to delete rental boat: {str(e)}')
    
    return success_response(
        data={'rental_boat_id': rental_boat_id},
        message='Rental boat deleted successfully'
    )
