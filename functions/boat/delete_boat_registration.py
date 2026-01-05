"""
Lambda function for deleting boat registrations
Team managers can delete boat registrations during registration period
"""
import json
import logging

# Import from Lambda layer
from responses import (
    success_response,
    validation_error,
    not_found_error,
    forbidden_error,
    internal_error,
    handle_exceptions
)
from database import get_db_client, get_timestamp
from auth_utils import get_user_from_event, require_team_manager_or_admin_override
from configuration import ConfigurationManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager_or_admin_override
def lambda_handler(event, context):
    """
    Delete a boat registration
    
    Path parameters:
        - boat_registration_id: ID of the boat registration to delete
    
    Returns:
        Success message
    """
    logger.info("Delete boat registration request")
    
    # Get effective user ID (impersonated or real)
    team_manager_id = event['_effective_user_id']
    is_admin_override = event['_is_admin_override']
    
    # Audit logging for admin override
    if is_admin_override:
        admin_id = event['_admin_user_id']
        logger.info(f"Admin {admin_id} deleting boat registration for team manager {team_manager_id}")
    
    # Get boat registration ID from path
    boat_registration_id = event.get('pathParameters', {}).get('boat_registration_id')
    if not boat_registration_id:
        return validation_error({'boat_registration_id': 'Boat registration ID is required'})
    
    # Get existing boat registration
    db = get_db_client()
    
    existing_boat = db.get_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'BOAT#{boat_registration_id}'
    )
    
    if not existing_boat:
        return not_found_error('Boat registration not found')
    
    # Prevent deletion of paid boats
    if existing_boat.get('registration_status') == 'paid':
        return forbidden_error('Cannot delete a paid boat registration. Please contact support if you need to make changes.')
    
    # Check if registration period is active
    config_manager = ConfigurationManager()
    system_config = config_manager.get_system_config()
    
    # TODO: Add registration period check when configuration is fully implemented
    # For now, allow deletions
    
    # Unassign crew members from this boat
    seats = existing_boat.get('seats', [])
    crew_member_ids = [seat.get('crew_member_id') for seat in seats if seat.get('crew_member_id')]
    
    if crew_member_ids:
        # Update crew members to remove boat assignment
        for crew_member_id in crew_member_ids:
            crew_member = db.get_item(
                pk=f'TEAM#{team_manager_id}',
                sk=f'CREW#{crew_member_id}'
            )
            
            if crew_member and crew_member.get('assigned_boat_id') == boat_registration_id:
                crew_member['assigned_boat_id'] = None
                crew_member['updated_at'] = get_timestamp()
                db.put_item(crew_member)
                logger.info(f"Unassigned crew member {crew_member_id} from boat {boat_registration_id}")
    
    # Delete boat registration from DynamoDB
    db.delete_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'BOAT#{boat_registration_id}'
    )
    
    logger.info(f"Boat registration deleted: {boat_registration_id}")
    
    # Return success response
    return success_response(
        data={'message': 'Boat registration deleted successfully'},
        status_code=200
    )
