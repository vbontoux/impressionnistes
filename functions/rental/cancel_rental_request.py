"""
Lambda function for team managers to cancel their own rental request
Team manager accessible - cancels a pending or accepted rental request
"""
import json
import logging
from datetime import datetime

from responses import success_response, not_found_error, handle_exceptions
from auth_utils import require_team_manager, get_user_from_event
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager
def lambda_handler(event, context):
    """
    Cancel a rental request
    
    Path parameters:
        rental_request_id: ID of the rental request to cancel
    
    Returns:
        Updated rental request with cancelled status
    """
    logger.info("Cancel rental request")
    
    # Get authenticated team manager user
    user_info = get_user_from_event(event)
    team_manager_id = user_info['user_id']
    
    # Get rental_request_id from path parameters
    path_params = event.get('pathParameters') or {}
    rental_request_id_param = path_params.get('rental_request_id')  # Match API Gateway parameter name
    
    if not rental_request_id_param:
        from responses import error_response
        return error_response(
            status_code=400,
            error_code='VALIDATION_ERROR',
            message='rental_request_id is required in path'
        )
    
    # Reconstruct full DynamoDB key (frontend sends only UUID)
    rental_request_id = f"RENTAL_REQUEST#{rental_request_id_param}"
    
    # Get rental request from database
    db = get_db_client()
    try:
        rental_request = db.get_item(rental_request_id, 'METADATA')
        
        if not rental_request:
            logger.warning(f"Rental request not found: {rental_request_id}")
            return not_found_error(f'Rental request not found: {rental_request_id}')
        
        # Validate requester_id matches authenticated user
        requester_id = rental_request.get('requester_id')
        if requester_id != team_manager_id:
            logger.warning(
                f"Team manager {team_manager_id} attempted to cancel request "
                f"{rental_request_id} owned by {requester_id}"
            )
            from responses import error_response
            return error_response(
                status_code=403,
                error_code='FORBIDDEN',
                message='You can only cancel your own rental requests'
            )
        
        # Validate status is "pending" or "accepted"
        current_status = rental_request.get('status')
        if current_status not in ['pending', 'accepted']:
            logger.warning(
                f"Cannot cancel request {rental_request_id} with status '{current_status}'"
            )
            from responses import error_response
            return error_response(
                status_code=400,
                error_code='VALIDATION_ERROR',
                message=f"Cannot cancel request with status '{current_status}'. "
                        f"Only pending or accepted requests can be cancelled."
            )
        
        # Delete the rental request (no need to keep cancelled requests)
        db.delete_item(rental_request_id, 'METADATA')
        
        logger.info(
            f"Rental request deleted: {rental_request_id} by team manager {team_manager_id} - "
            f"previous status was '{current_status}'"
        )
        
        # Strip RENTAL_REQUEST# prefix from ID for frontend
        clean_id = rental_request_id.replace('RENTAL_REQUEST#', '')
        
        # Return confirmation
        return success_response(
            data={
                'rental_request_id': clean_id,
                'message': 'Rental request cancelled and removed'
            },
            message='Rental request cancelled successfully.'
        )
        
    except Exception as e:
        logger.error(f"Failed to cancel rental request: {str(e)}")
        from responses import error_response
        return error_response(
            status_code=500,
            error_code='INTERNAL_ERROR',
            message=f'Failed to cancel rental request: {str(e)}'
        )
