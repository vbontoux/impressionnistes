"""
Lambda function for getting eligible coxswain substitutes
Returns crew members who can substitute as coxswain while maintaining race eligibility
"""
import json
import logging

# Import from Lambda layer
from responses import (
    success_response,
    validation_error,
    not_found_error,
    internal_error,
    handle_exceptions
)
from database import get_db_client
from auth_utils import get_user_from_event, require_team_manager_or_admin_override
from boat_registration_utils import get_coxswain_substitutes

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager_or_admin_override
def lambda_handler(event, context):
    """
    Get eligible coxswain substitutes for a boat registration
    
    Path parameters:
        - boat_registration_id: ID of the boat registration
    
    Query parameters (admin only):
        - team_manager_id: Override to view another team manager's boat (admin only)
    
    Returns:
        List of crew members who can substitute as coxswain
    """
    logger.info("Get coxswain substitutes request")
    
    # Get effective user ID (may be overridden by admin impersonation)
    team_manager_id = event.get('_effective_user_id')
    
    if not team_manager_id:
        # Fallback to authenticated user if no override
        user = get_user_from_event(event)
        team_manager_id = user['user_id']
    
    # Get boat registration ID from path
    boat_registration_id = event.get('pathParameters', {}).get('boat_registration_id')
    if not boat_registration_id:
        return validation_error({'boat_registration_id': 'Boat registration ID is required'})
    
    # Get boat registration
    db = get_db_client()
    
    boat_registration = db.get_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'BOAT#{boat_registration_id}'
    )
    
    if not boat_registration:
        return not_found_error('Boat registration not found')
    
    # Check if boat has a coxswain seat
    has_cox = any(seat.get('type') == 'cox' for seat in boat_registration.get('seats', []))
    if not has_cox:
        return success_response(data={'substitutes': [], 'message': 'This boat type does not have a coxswain'})
    
    # Check if race is selected
    race_id = boat_registration.get('race_id')
    if not race_id:
        return validation_error({'race_id': 'Race must be selected before finding substitutes'})
    
    # Get the selected race
    # TODO: Implement race lookup from DynamoDB when races are seeded
    # For now, return empty list with message
    selected_race = None
    
    if not selected_race:
        return success_response(data={
            'substitutes': [],
            'message': 'Race data not yet available. This feature will be enabled after race seeding.'
        })
    
    # Get all crew members
    all_crew_members = db.query_by_pk(
        pk=f'TEAM#{team_manager_id}',
        sk_prefix='CREW#'
    )
    
    # Get eligible substitutes
    substitutes = get_coxswain_substitutes(
        boat_registration,
        all_crew_members,
        selected_race
    )
    
    logger.info(f"Found {len(substitutes)} eligible coxswain substitutes for boat {boat_registration_id}")
    
    # Return success response
    return success_response(data={'substitutes': substitutes})
