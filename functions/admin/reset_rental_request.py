"""
Lambda function for admins to reset an accepted rental request back to pending
Admin only - resets an accepted rental request back to pending status
"""
import json
import logging
from datetime import datetime

from responses import success_response, not_found_error, handle_exceptions
from auth_utils import require_admin, get_user_from_event
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Reset an accepted rental request back to pending status
    
    Path parameters:
        rental_request_id: ID of the rental request to reset
    
    Returns:
        Updated rental request with pending status
    """
    logger.info("Reset rental request to pending")
    
    # Get authenticated admin user
    user_info = get_user_from_event(event)
    admin_user_id = user_info['user_id']
    
    # Get rental_request_id from path parameters
    path_params = event.get('pathParameters') or {}
    rental_request_id_param = path_params.get('rental_request_id')
    
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
        
        # Validate current status is "accepted"
        current_status = rental_request.get('status')
        if current_status != 'accepted':
            logger.warning(
                f"Cannot reset request {rental_request_id} with status '{current_status}'"
            )
            from responses import error_response
            return error_response(
                status_code=400,
                error_code='VALIDATION_ERROR',
                message=f"Cannot reset request with status '{current_status}'. "
                        f"Only accepted requests can be reset to pending."
            )
        
        # Update rental request - reset to pending and clear acceptance fields
        current_time = datetime.utcnow().isoformat() + 'Z'
        updates = {
            'status': 'pending',
            'assignment_details': None,
            'accepted_at': None,
            'accepted_by': None,
            'updated_at': current_time
        }
        
        updated_request = db.update_item(
            rental_request_id,
            'METADATA',
            updates
        )
        
        logger.info(
            f"Rental request reset to pending: {rental_request_id} by admin {admin_user_id} - "
            f"{rental_request.get('boat_type')} for {rental_request.get('requester_email')}"
        )
        
        # Strip RENTAL_REQUEST# prefix from ID for frontend
        clean_id = rental_request_id.replace('RENTAL_REQUEST#', '')
        
        # Return updated request
        return success_response(
            data={
                'rental_request_id': clean_id,
                'boat_type': updated_request.get('boat_type'),
                'desired_weight_range': updated_request.get('desired_weight_range'),
                'request_comment': updated_request.get('request_comment'),
                'status': updated_request.get('status'),
                'requester_id': updated_request.get('requester_id'),
                'requester_email': updated_request.get('requester_email'),
                'created_at': updated_request.get('created_at')
            },
            message='Rental request reset to pending successfully.'
        )
        
    except Exception as e:
        logger.error(f"Failed to reset rental request: {str(e)}")
        from responses import error_response
        return error_response(
            status_code=500,
            error_code='INTERNAL_ERROR',
            message=f'Failed to reset rental request: {str(e)}'
        )
