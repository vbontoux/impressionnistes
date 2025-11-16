"""
Lambda function for deleting crew members
Team managers can delete crew members if they are not assigned to a boat
"""
import logging

# Import from Lambda layer
from responses import (
    success_response,
    validation_error,
    not_found_error,
    conflict_error,
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
    Delete a crew member
    
    Path parameters:
        - crew_member_id: ID of the crew member to delete
    
    Returns:
        Success message
    """
    logger.info("Delete crew member request")
    
    # Get authenticated user
    user = get_user_from_event(event)
    team_manager_id = user['user_id']
    
    # Get crew member ID from path
    crew_member_id = event.get('pathParameters', {}).get('crew_member_id')
    if not crew_member_id:
        return validation_error({'crew_member_id': 'Crew member ID is required'})
    
    # Get existing crew member
    db = get_db_client()
    
    existing_crew = db.get_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'CREW#{crew_member_id}'
    )
    
    if not existing_crew:
        return not_found_error('Crew member not found')
    
    # Check if crew member is assigned to a boat
    if existing_crew.get('assigned_boat_id'):
        return conflict_error(
            'Cannot delete crew member who is assigned to a boat. '
            'Please remove them from the boat first.'
        )
    
    # Delete crew member from DynamoDB
    db.delete_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'CREW#{crew_member_id}'
    )
    
    logger.info(f"Crew member deleted: {crew_member_id}")
    
    # Return success response
    return success_response(
        data={'message': 'Crew member deleted successfully'},
        status_code=200
    )
