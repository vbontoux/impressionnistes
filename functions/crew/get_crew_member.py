"""
Lambda function for getting a single crew member
Team managers can view details of their crew members
"""
import logging

# Import from Lambda layer
from responses import (
    success_response,
    validation_error,
    not_found_error,
    handle_exceptions
)
from database import get_db_client
from auth_utils import get_user_from_event, require_team_manager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager
def lambda_handler(event, context):
    """
    Get a single crew member by ID
    
    Path parameters:
        - crew_member_id: ID of the crew member to retrieve
    
    Returns:
        Crew member object
    """
    logger.info("Get crew member request")
    
    # Get authenticated user
    user = get_user_from_event(event)
    team_manager_id = user['user_id']
    
    # Get crew member ID from path
    crew_member_id = event.get('pathParameters', {}).get('crew_member_id')
    if not crew_member_id:
        return validation_error({'crew_member_id': 'Crew member ID is required'})
    
    # Get crew member from DynamoDB
    db = get_db_client()
    
    crew_member = db.get_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'CREW#{crew_member_id}'
    )
    
    if not crew_member:
        return not_found_error('Crew member not found')
    
    logger.info(f"Retrieved crew member: {crew_member_id}")
    
    # Return success response
    return success_response(data=crew_member)
