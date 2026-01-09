"""
Lambda function for admins to accept a rental request
Admin only - accepts a pending rental request and provides assignment details
"""
import json
import logging
from datetime import datetime
from boto3.dynamodb.conditions import Attr

from responses import success_response, validation_error, not_found_error, handle_exceptions
from auth_utils import require_admin, get_user_from_event
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validate_assignment_details(assignment_details):
    """
    Validate assignment details
    
    Args:
        assignment_details: Assignment details string to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not assignment_details:
        return False, "assignment_details is required"
    
    if not isinstance(assignment_details, str):
        return False, "assignment_details must be a string"
    
    if not assignment_details.strip():
        return False, "assignment_details cannot be empty"
    
    if len(assignment_details) > 1000:
        return False, "assignment_details must be 1000 characters or less"
    
    return True, None


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Accept a rental request and provide assignment details
    
    Path parameters:
        rental_request_id: ID of the rental request to accept
    
    Expected body:
    {
        "assignment_details": str  # Required: max 1000 chars
    }
    
    Returns:
        Updated rental request with accepted status
    """
    logger.info("Accept rental request")
    
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
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        from responses import error_response
        return error_response(
            status_code=400,
            error_code='VALIDATION_ERROR',
            message='Invalid JSON in request body'
        )
    
    # Validate assignment_details
    assignment_details = body.get('assignment_details')
    is_valid, error_message = validate_assignment_details(assignment_details)
    if not is_valid:
        logger.warning(f"Validation failed for assignment_details: {error_message}")
        from responses import error_response
        return error_response(
            status_code=400,
            error_code='VALIDATION_ERROR',
            message=error_message
        )
    
    # Get rental request from database
    db = get_db_client()
    try:
        rental_request = db.get_item(rental_request_id, 'METADATA')
        
        if not rental_request:
            logger.warning(f"Rental request not found: {rental_request_id}")
            return not_found_error(f'Rental request not found: {rental_request_id}')
        
        # Validate current status is "pending"
        current_status = rental_request.get('status')
        if current_status != 'pending':
            logger.warning(
                f"Cannot accept request {rental_request_id} with status '{current_status}'"
            )
            from responses import error_response
            return error_response(
                status_code=400,
                error_code='VALIDATION_ERROR',
                message=f"Cannot accept request with status '{current_status}'. "
                        f"Only pending requests can be accepted."
            )
        
        # Update rental request
        current_time = datetime.utcnow().isoformat() + 'Z'
        updates = {
            'status': 'accepted',
            'assignment_details': assignment_details.strip(),
            'accepted_at': current_time,
            'accepted_by': admin_user_id,
            'updated_at': current_time
        }
        
        updated_request = db.update_item(
            rental_request_id,
            'METADATA',
            updates
        )
        
        logger.info(
            f"Rental request accepted: {rental_request_id} by admin {admin_user_id} - "
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
                'assignment_details': updated_request.get('assignment_details'),
                'accepted_at': updated_request.get('accepted_at'),
                'accepted_by': updated_request.get('accepted_by'),
                'requester_id': updated_request.get('requester_id'),
                'requester_email': updated_request.get('requester_email'),
                'created_at': updated_request.get('created_at')
            },
            message='Rental request accepted successfully. Team manager can now proceed with payment.'
        )
        
    except Exception as e:
        logger.error(f"Failed to accept rental request: {str(e)}")
        from responses import error_response
        return error_response(
            status_code=500,
            error_code='INTERNAL_ERROR',
            message=f'Failed to accept rental request: {str(e)}'
        )
