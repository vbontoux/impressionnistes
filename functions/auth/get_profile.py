"""
Lambda function to get team manager profile
Retrieves profile from DynamoDB
"""
import json
import os
import logging

# Import from Lambda layer (shared modules are in /opt/python/)
from responses import (
    success_response,
    not_found_error,
    handle_exceptions
)
from database import get_db_client
from auth_utils import require_auth, get_user_from_event

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_auth
def lambda_handler(event, context):
    """
    Get team manager profile
    
    Returns:
        User profile data
    """
    logger.info("Get profile request")
    
    # Get authenticated user
    user_info = get_user_from_event(event)
    user_id = user_info['user_id']
    
    # Get profile from DynamoDB
    db = get_db_client()
    profile = db.get_item(f'USER#{user_id}', 'PROFILE')
    
    if not profile:
        logger.warning(f"Profile not found for user: {user_id}")
        return not_found_error('profile')
    
    # Return profile data
    return success_response(
        data={
            'user_id': profile.get('user_id'),
            'email': profile.get('email'),
            'first_name': profile.get('first_name'),
            'last_name': profile.get('last_name'),
            'club_affiliation': profile.get('club_affiliation'),
            'mobile_number': profile.get('mobile_number'),
            'role': profile.get('role'),
            'created_at': profile.get('created_at'),
            'updated_at': profile.get('updated_at')
        }
    )
