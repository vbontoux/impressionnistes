"""
Lambda function for bulk updating crew member license verification status
Admin only - allows marking multiple licenses as verified in one request
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
    Bulk update license verification status for multiple crew members
    
    Request body:
        - verifications: Array of verification objects
          - crew_member_id: Crew member ID (required)
          - team_manager_id: Team manager ID (required)
          - status: Verification status (required)
          - details: Verification details (optional)
    
    Returns:
        Summary with success_count, failure_count, and results array
    """
    logger.info("Bulk update license verification request")
    
    # Get admin user ID from event
    user_info = get_user_from_event(event)
    admin_user_id = user_info.get('user_id') if user_info else None
    if not admin_user_id:
        return validation_error({'admin_user_id': 'Unable to identify admin user'})
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error({'body': 'Invalid JSON'})
    
    # Get verifications array
    verifications = body.get('verifications', [])
    
    if not verifications:
        return validation_error({'verifications': 'Verifications array is required'})
    
    if not isinstance(verifications, list):
        return validation_error({'verifications': 'Verifications must be an array'})
    
    # Limit batch size
    if len(verifications) > 100:
        return validation_error({'verifications': 'Maximum 100 verifications per request'})
    
    # Get database client
    db = get_db_client()
    current_timestamp = get_timestamp()
    
    # Process each verification
    results = []
    success_count = 0
    failure_count = 0
    
    for idx, verification in enumerate(verifications):
        result = {
            'crew_member_id': verification.get('crew_member_id'),
            'success': False
        }
        
        try:
            # Validate verification object
            crew_member_id = verification.get('crew_member_id', '').strip()
            team_manager_id = verification.get('team_manager_id', '').strip()
            status = verification.get('status', '').strip()
            details = verification.get('details', '').strip()
            
            # Validate required fields
            if not crew_member_id:
                result['error'] = 'Crew member ID is required'
                failure_count += 1
                results.append(result)
                continue
            
            if not team_manager_id:
                result['error'] = 'Team manager ID is required'
                failure_count += 1
                results.append(result)
                continue
            
            if not status:
                result['error'] = 'Verification status is required'
                failure_count += 1
                results.append(result)
                continue
            
            if status not in VALID_STATUSES:
                result['error'] = f'Invalid status: {status}'
                failure_count += 1
                results.append(result)
                continue
            
            # Validate details length
            if details and len(details) > 500:
                result['error'] = 'Details must be 500 characters or less'
                failure_count += 1
                results.append(result)
                continue
            
            # Get crew member
            crew_member = db.get_item(
                pk=f'TEAM#{team_manager_id}',
                sk=f'CREW#{crew_member_id}'
            )
            
            if not crew_member:
                result['error'] = 'Crew member not found'
                failure_count += 1
                results.append(result)
                continue
            
            # Update crew member with verification fields
            crew_member['license_verification_status'] = status
            crew_member['license_verification_date'] = current_timestamp
            crew_member['license_verification_details'] = details if details else None
            crew_member['license_verified_by'] = admin_user_id
            crew_member['updated_at'] = current_timestamp
            
            # Save to database
            db.put_item(crew_member)
            
            # Success
            result['success'] = True
            result['status'] = status
            result['date'] = current_timestamp
            result['verified_by'] = admin_user_id
            result['details'] = details if details else None
            success_count += 1
            results.append(result)
            
            logger.info(f"License verification updated for crew member {crew_member_id}")
            
        except Exception as e:
            logger.error(f"Error updating crew member {verification.get('crew_member_id')}: {str(e)}")
            result['error'] = str(e)
            failure_count += 1
            results.append(result)
    
    logger.info(f"Bulk verification complete: {success_count} succeeded, {failure_count} failed")
    
    return success_response(
        data={
            'success_count': success_count,
            'failure_count': failure_count,
            'results': results
        }
    )
