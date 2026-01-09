"""
Lambda function for admins to update assignment details
Admin only - updates assignment details for an accepted rental request without changing status
"""
import json
import logging
from datetime import datetime

from responses import success_response, not_found_error, handle_exceptions
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
    Update assignment details for an accepted rental request
    
    Path parameters:
        rental_request_id: ID of the rental request to update
    
    Expected body:
    {
        "assignment_details": str  # Required: max 1000 chars
    }
    
    Returns:
        Updated rental request with new assignment details
    """
    logger.info("Update assignment details")
    
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
        
        # Validate current status is "accepted"
        current_status = rental_request.get('status')
        if current_status != 'accepted':
            logger.warning(
                f"Cannot update assignment details for request {rental_request_id} "
                f"with status '{current_status}'"
            )
            from responses import error_response
            return error_response(
                status_code=400,
                error_code='VALIDATION_ERROR',
                message=f"Cannot update assignment details for request with status '{current_status}'. "
                        f"Only accepted requests can have assignment details updated."
            )
        
        # Update assignment details without changing status
        current_time = datetime.utcnow().isoformat() + 'Z'
        updates = {
            'assignment_details': assignment_details.strip(),
            'updated_at': current_time,
            'updated_by': admin_user_id
        }
        
        updated_request = db.update_item(
            rental_request_id,
            'METADATA',
            updates
        )
        
        logger.info(
            f"Assignment details updated for request {rental_request_id} by admin {admin_user_id}"
        )
        
        # Strip RENTAL_REQUEST# prefix from ID for frontend
        clean_id = rental_request_id.replace('RENTAL_REQUEST#', '')
        
        # Return updated request
        return success_response(
            data={
                'rental_request_id': clean_id,
                'boat_type': updated_request.get('boat_type'),
                'status': updated_request.get('status'),
                'assignment_details': updated_request.get('assignment_details'),
                'updated_at': updated_request.get('updated_at'),
                'updated_by': updated_request.get('updated_by')
            },
            message='Assignment details updated successfully.'
        )
        
    except Exception as e:
        logger.error(f"Failed to update assignment details: {str(e)}")
        from responses import error_response
        return error_response(
            status_code=500,
            error_code='INTERNAL_ERROR',
            message=f'Failed to update assignment details: {str(e)}'
        )
