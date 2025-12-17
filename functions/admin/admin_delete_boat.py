"""
Lambda function for admin to delete any boat registration
Admin only - can delete boats regardless of date limits (except paid boats)
"""
import json
import logging

from responses import (
    success_response,
    validation_error,
    not_found_error,
    handle_exceptions
)
from database import get_db_client
from auth_utils import require_admin

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Delete a boat registration (admin only)
    Admin can delete any boat at any time, except paid boats
    
    Path parameters:
        team_manager_id: Team manager ID
        boat_registration_id: Boat registration ID
    
    Returns:
        Success message
    """
    logger.info("Admin delete boat request")
    
    # Get path parameters
    path_params = event.get('pathParameters', {})
    team_manager_id = path_params.get('team_manager_id')
    boat_registration_id = path_params.get('boat_registration_id')
    
    if not team_manager_id or not boat_registration_id:
        return validation_error({
            'path': 'team_manager_id and boat_registration_id are required'
        })
    
    # Get existing boat registration
    db = get_db_client()
    
    existing_boat = db.get_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'BOAT#{boat_registration_id}'
    )
    
    if not existing_boat:
        return not_found_error('Boat registration not found')
    
    # Check if boat is paid - even admin cannot delete paid boats
    if existing_boat.get('registration_status') == 'paid':
        return validation_error({
            'boat': 'Cannot delete paid boat registration'
        })
    
    # Unassign crew members from this boat
    seats = existing_boat.get('seats', [])
    crew_member_ids = [seat.get('crew_member_id') for seat in seats if seat.get('crew_member_id')]
    
    if crew_member_ids:
        # Update crew members to remove boat assignment
        from database import get_timestamp
        
        for crew_member_id in crew_member_ids:
            crew_member = db.get_item(
                pk=f'TEAM#{team_manager_id}',
                sk=f'CREW#{crew_member_id}'
            )
            
            if crew_member and crew_member.get('assigned_boat_id') == boat_registration_id:
                crew_member['assigned_boat_id'] = None
                crew_member['updated_at'] = get_timestamp()
                db.put_item(crew_member)
                logger.info(f"Admin unassigned crew member {crew_member_id} from boat {boat_registration_id}")
    
    # Delete boat registration
    db.delete_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'BOAT#{boat_registration_id}'
    )
    
    logger.info(f"Admin deleted boat registration: {boat_registration_id}")
    
    # Return success response
    return success_response(
        data={
            'message': 'Boat registration deleted successfully',
            'boat_registration_id': boat_registration_id
        }
    )
