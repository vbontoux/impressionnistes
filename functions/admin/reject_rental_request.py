"""
Lambda function for admins to reject a rental request
Admin only - rejects a pending rental request with optional rejection reason
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
    Reject a rental request
    
    Path parameters:
        rental_request_id: ID of the rental request to reject
    
    Expected body (optional):
    {
        "rejection_reason": str  # Optional: reason for rejection
    }
    
    Returns:
        Updated rental request with cancelled status
    """
    logger.info("Reject rental request")
    
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
    
    # Parse request body (rejection_reason is optional)
    rejection_reason = None
    try:
        body = json.loads(event.get('body', '{}'))
        rejection_reason = body.get('rejection_reason')
    except json.JSONDecodeError:
        # Empty body is acceptable since rejection_reason is optional
        pass
    
    # Get rental request from database
    db = get_db_client()
    try:
        rental_request = db.get_item(rental_request_id, 'METADATA')
        
        if not rental_request:
            logger.warning(f"Rental request not found: {rental_request_id}")
            return not_found_error(f'Rental request not found: {rental_request_id}')
        
        # Validate status is "pending" or "accepted" (but not "paid")
        current_status = rental_request.get('status')
        if current_status not in ['pending', 'accepted']:
            logger.warning(
                f"Cannot reject request {rental_request_id} with status '{current_status}'"
            )
            from responses import error_response
            return error_response(
                status_code=400,
                error_code='VALIDATION_ERROR',
                message=f"Cannot reject request with status '{current_status}'. "
                        f"Only pending or accepted requests can be rejected (not yet paid)."
            )
        
        # Update status to "rejected" instead of deleting
        now = datetime.utcnow().isoformat() + 'Z'
        rental_request['status'] = 'rejected'
        rental_request['rejected_at'] = now
        rental_request['rejected_by'] = admin_user_id
        
        if rejection_reason:
            rental_request['rejection_reason'] = rejection_reason
        
        # Save updated request to database
        db.put_item(rental_request)
        
        logger.info(
            f"Rental request rejected: {rental_request_id} by admin {admin_user_id} - "
            f"{rental_request.get('boat_type')} for {rental_request.get('requester_email')}"
            f"{' - Reason: ' + rejection_reason if rejection_reason else ''}"
        )
        
        # Strip RENTAL_REQUEST# prefix from ID for frontend
        clean_id = rental_request_id.replace('RENTAL_REQUEST#', '')
        
        # Return confirmation with updated request data
        return success_response(
            data={
                'rental_request_id': clean_id,
                'status': 'rejected',
                'rejected_at': now,
                'rejected_by': admin_user_id,
                'rejection_reason': rejection_reason
            },
            message='Rental request rejected successfully.'
        )
        
    except Exception as e:
        logger.error(f"Failed to reject rental request: {str(e)}")
        from responses import error_response
        return error_response(
            status_code=500,
            error_code='INTERNAL_ERROR',
            message=f'Failed to reject rental request: {str(e)}'
        )
