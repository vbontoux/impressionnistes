"""
Lambda function for team managers to create a rental request
Team manager accessible - creates a new rental request with pending status
"""
import json
import logging
import uuid
from datetime import datetime

from responses import success_response, validation_error, handle_exceptions
from auth_utils import require_team_manager, get_user_from_event
from database import get_db_client
from validation import validate_rental_request

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager
def lambda_handler(event, context):
    """
    Create a new rental request
    
    Expected body:
    {
        "boat_type": str,  # Required: skiff, 4-, 4+, 4x-, 4x+, 8+, 8x+
        "desired_weight_range": str,  # Required: e.g., "70-90kg"
        "request_comment": str  # Required: max 500 chars
    }
    
    Returns:
        Confirmation with rental request details
    """
    logger.info("Create rental request")
    
    # Get authenticated user
    user_info = get_user_from_event(event)
    requester_id = user_info['user_id']
    requester_email = user_info.get('email', requester_id)
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error('Invalid JSON in request body')
    
    # Validate request data using Cerberus schema
    is_valid, errors = validate_rental_request(body)
    if not is_valid:
        logger.warning(f"Validation failed for rental request: {errors}")
        return validation_error(errors)
    
    # Generate rental_request_id
    rental_request_id = f"RENTAL_REQUEST#{uuid.uuid4()}"
    current_time = datetime.utcnow().isoformat() + 'Z'
    
    # Create rental request record
    rental_request = {
        'PK': rental_request_id,
        'SK': 'METADATA',
        'rental_request_id': rental_request_id,
        
        # Request details (provided by team manager)
        'boat_type': body['boat_type'],
        'desired_weight_range': body['desired_weight_range'],
        'request_comment': body['request_comment'],
        
        # Status and workflow
        'status': 'pending',
        
        # Requester information
        'requester_id': requester_id,
        'requester_email': requester_email,
        
        # Timestamps
        'created_at': current_time,
        'updated_at': current_time,
        
        # Assignment details (will be added by admin when accepting)
        'assignment_details': None,
        'accepted_at': None,
        'accepted_by': None,
        'paid_at': None,
        'cancelled_at': None,
        'cancelled_by': None,
        'rejection_reason': None
    }
    
    # Save to DynamoDB
    db = get_db_client()
    try:
        db.put_item(rental_request)
        logger.info(
            f"Rental request created: {rental_request_id} by team manager "
            f"{requester_id} ({requester_email}) - {body['boat_type']}"
        )
    except Exception as e:
        logger.error(f"Failed to create rental request: {str(e)}")
        return validation_error(f'Failed to create rental request: {str(e)}')
    
    # Return confirmation with request details
    # Strip RENTAL_REQUEST# prefix from ID for frontend
    clean_id = rental_request_id.replace('RENTAL_REQUEST#', '')
    
    return success_response(
        data={
            'rental_request_id': clean_id,
            'boat_type': rental_request['boat_type'],
            'desired_weight_range': rental_request['desired_weight_range'],
            'request_comment': rental_request['request_comment'],
            'status': rental_request['status'],
            'requester_id': rental_request['requester_id'],
            'requester_email': rental_request['requester_email'],
            'created_at': rental_request['created_at']
        },
        message='Rental request created successfully. An admin will review your request.'
    )
