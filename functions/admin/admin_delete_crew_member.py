"""
Lambda function for admin to delete crew members for any team manager
Admin only - bypasses registration period restrictions
"""
import json
import logging

from responses import success_response, validation_error, not_found_error, handle_exceptions
from auth_utils import require_admin
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Admin deletes a crew member for any team manager
    Bypasses registration period restrictions
    
    Path parameters:
        team_manager_id: ID of the team manager
        crew_member_id: ID of the crew member to delete
    
    Returns:
        Success message
    """
    logger.info("Admin delete crew member request")
    
    # Get path parameters
    path_params = event.get('pathParameters', {})
    team_manager_id = path_params.get('team_manager_id')
    crew_member_id = path_params.get('crew_member_id')
    
    if not team_manager_id or not crew_member_id:
        return validation_error('team_manager_id and crew_member_id are required')
    
    # Get database client
    db = get_db_client()
    
    try:
        # Check if crew member exists
        response = db.table.get_item(
            Key={
                'PK': f'TEAM#{team_manager_id}',
                'SK': f'CREW#{crew_member_id}'
            }
        )
        
        if 'Item' not in response:
            return not_found_error(f'Crew member {crew_member_id} not found')
        
        crew_member = response['Item']
        
        # Check if crew member is assigned to any boat
        assigned_boat_id = crew_member.get('assigned_boat_id')
        if assigned_boat_id:
            return validation_error(
                f'Cannot delete crew member: assigned to boat {assigned_boat_id}',
                {'assigned_boat_id': 'Crew member must be unassigned from boat before deletion'}
            )
        
        # Delete crew member
        db.table.delete_item(
            Key={
                'PK': f'TEAM#{team_manager_id}',
                'SK': f'CREW#{crew_member_id}'
            }
        )
        
        logger.info(f"Admin deleted crew member {crew_member_id} for team manager {team_manager_id}")
        
        return success_response(
            data={
                'message': 'Crew member deleted successfully',
                'crew_member_id': crew_member_id
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to delete crew member: {str(e)}", exc_info=True)
        return validation_error(f'Failed to delete crew member: {str(e)}')
