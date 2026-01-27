"""
Lambda function for updating crew member license verification status
Admin only - allows marking licenses as verified (valid or invalid)
"""
import json
import os
import logging

# Import from Lambda layer
from responses import success_response, validation_error, handle_exceptions
from database import get_db_client, get_timestamp
from auth_utils import require_admin, get_user_from_event
from access_control import require_permission

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Valid verification status values
VALID_STATUSES = [
    'verified_valid',
    'verified_invalid',
    'manually_verified_valid',
    'manually_verified_invalid'
]


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Update license verification status for a single crew member
    
    Path parameters:
        - crew_member_id: Crew member ID
    
    Request body:
        - team_manager_id: Team manager ID (required)
        - status: Verification status (required)
        - details: Verification details (optional)
    
    Returns:
        Updated crew member verification fields
    """
    logger.info("Update crew member license verification request")
    
    # Get admin user ID from event
    user_info = get_user_from_event(event)
    admin_user_id = user_info.get('user_id') if user_info else None
    if not admin_user_id:
        return validation_error({'admin_user_id': 'Unable to identify admin user'})
    
    # Get crew member ID from path
    crew_member_id = event.get('pathParameters', {}).get('crew_member_id')
    if not crew_member_id:
        return validation_error({'crew_member_id': 'Crew member ID is required'})
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error({'body': 'Invalid JSON'})
    
    # Extract and validate data
    team_manager_id = body.get('team_manager_id', '').strip()
    status = body.get('status', '').strip()
    details = body.get('details', '').strip()
    
    # Validate required fields
    errors = {}
    if not team_manager_id:
        errors['team_manager_id'] = 'Team manager ID is required'
    if not status:
        errors['status'] = 'Verification status is required'
    elif status not in VALID_STATUSES:
        errors['status'] = f'Status must be one of: {", ".join(VALID_STATUSES)}'
    
    if errors:
        return validation_error(errors)
    
    # Validate details length
    if details and len(details) > 500:
        return validation_error({'details': 'Details must be 500 characters or less'})
    
    # Get database client
    db = get_db_client()
    
    # Verify crew member exists
    crew_member = db.get_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'CREW#{crew_member_id}'
    )
    
    if not crew_member:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            'body': json.dumps({
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Crew member not found',
                    'details': {
                        'crew_member_id': crew_member_id,
                        'team_manager_id': team_manager_id
                    }
                }
            })
        }
    
    # Update crew member with verification fields
    current_timestamp = get_timestamp()
    
    crew_member['license_verification_status'] = status
    crew_member['license_verification_date'] = current_timestamp
    crew_member['license_verification_details'] = details if details else None
    crew_member['license_verified_by'] = admin_user_id
    crew_member['updated_at'] = current_timestamp
    
    # Save to database
    db.put_item(crew_member)
    
    logger.info(f"License verification updated for crew member {crew_member_id} by admin {admin_user_id}")
    
    # Return verification fields only
    return success_response(
        data={
            'crew_member_id': crew_member_id,
            'license_verification_status': status,
            'license_verification_date': current_timestamp,
            'license_verified_by': admin_user_id,
            'license_verification_details': details if details else None
        }
    )
