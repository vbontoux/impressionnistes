"""
Lambda function for updating crew members
Team managers can edit crew member information during registration period
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
from validation import validate_crew_member, sanitize_dict, crew_member_schema, is_rcpm_member
from database import get_db_client, get_timestamp
from auth_utils import get_user_from_event, require_team_manager_or_admin_override
from configuration import ConfigurationManager
from boat_registration_utils import calculate_boat_club_info
from access_control import require_permission

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager_or_admin_override
@require_permission('edit_crew_member')
def lambda_handler(event, context):
    """
    Update an existing crew member
    
    Path parameters:
        - crew_member_id: ID of the crew member to update
    
    Request body:
        - first_name: First name (optional)
        - last_name: Last name (optional)
        - date_of_birth: Date of birth in YYYY-MM-DD format (optional)
        - gender: M or F (optional)
        - license_number: 6-24 characters (letters, numbers, special characters accepted) (optional)
        - club_affiliation: Rowing club (optional)
    
    Returns:
        Updated crew member object
    """
    logger.info("Update crew member request")
    
    # Get effective user ID (impersonated or real)
    team_manager_id = event['_effective_user_id']
    is_admin_override = event['_is_admin_override']
    
    # Audit logging for admin override
    if is_admin_override:
        admin_id = event['_admin_user_id']
        logger.info(f"Admin {admin_id} updating crew member for team manager {team_manager_id}")
    
    # Get crew member ID from path
    crew_member_id = event.get('pathParameters', {}).get('crew_member_id')
    if not crew_member_id:
        return validation_error({'crew_member_id': 'Crew member ID is required'})
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error({'body': 'Invalid JSON'})
    
    # Get existing crew member
    db = get_db_client()
    
    existing_crew = db.get_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'CREW#{crew_member_id}'
    )
    
    if not existing_crew:
        return not_found_error('Crew member not found')
    
    # Check if registration period is active or if user has editing access
    config_manager = ConfigurationManager()
    system_config = config_manager.get_system_config()
    
    # Prepare update data
    update_data = {}
    
    if 'first_name' in body:
        update_data['first_name'] = body['first_name'].strip()
    if 'last_name' in body:
        update_data['last_name'] = body['last_name'].strip()
    if 'date_of_birth' in body:
        update_data['date_of_birth'] = body['date_of_birth'].strip()
    if 'gender' in body:
        update_data['gender'] = body['gender'].strip().upper()
    if 'license_number' in body:
        update_data['license_number'] = body['license_number'].strip().upper()
    if 'club_affiliation' in body:
        update_data['club_affiliation'] = body['club_affiliation'].strip()
    
    # Sanitize update data
    update_data = sanitize_dict(update_data, crew_member_schema)
    
    # Merge with existing data for validation
    crew_data = {**existing_crew, **update_data}
    
    # Validate updated crew member data (validator allows unknown fields like PK, SK)
    is_valid, errors = validate_crew_member(crew_data)
    if not is_valid:
        logger.error(f"Validation failed for crew data: {errors}")
        logger.error(f"Crew data being validated: {crew_data}")
        return validation_error(errors)
    
    # Check for duplicate license number if license is being changed
    if 'license_number' in update_data and update_data['license_number'] != existing_crew.get('license_number'):
        if db.check_license_number_exists(update_data['license_number']):
            logger.warning(f"Duplicate license number attempted during update: {update_data['license_number']}")
            return {
                'statusCode': 409,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True,
                },
                'body': json.dumps({
                    'error': {
                        'code': 'DUPLICATE_LICENSE',
                        'message': 'License number already in use',
                        'details': {
                            'license_number': f'The license number {update_data["license_number"]} is already registered in the competition'
                        }
                    }
                })
            }
    
    # Recalculate is_rcpm_member if club_affiliation changed
    # Uses case-insensitive matching for "RCPM", "Port-Marly", "Port Marly"
    if 'club_affiliation' in update_data:
        crew_data['is_rcpm_member'] = is_rcpm_member(crew_data['club_affiliation'])
    
    # Update timestamp
    crew_data['updated_at'] = get_timestamp()
    
    # Update crew member in DynamoDB
    db.put_item(crew_data)
    logger.info(f"Crew member updated: {crew_member_id}")
    
    # If club_affiliation was updated, recalculate boat club info for all assigned boats
    if 'club_affiliation' in update_data:
        assigned_boat_id = existing_crew.get('assigned_boat_id')
        
        if assigned_boat_id:
            logger.info(f"Crew member club changed, recalculating boat club info for boat: {assigned_boat_id}")
            
            # Get the boat registration
            boat = db.get_item(
                pk=f'TEAM#{team_manager_id}',
                sk=f'BOAT#{assigned_boat_id}'
            )
            
            if boat:
                # Get all assigned crew members for this boat
                assigned_crew_members = []
                for seat in boat.get('seats', []):
                    if seat.get('crew_member_id'):
                        crew = db.get_item(
                            pk=f'TEAM#{team_manager_id}',
                            sk=f'CREW#{seat["crew_member_id"]}'
                        )
                        if crew:
                            assigned_crew_members.append(crew)
                
                # Get team manager's club
                team_manager = db.get_item(
                    pk=f'USER#{team_manager_id}',
                    sk=f'PROFILE#{team_manager_id}'
                )
                team_manager_club = team_manager.get('club_affiliation', '') if team_manager else ''
                
                # Calculate new club info
                club_info = calculate_boat_club_info(assigned_crew_members, team_manager_club)
                
                # Update boat with new club info
                boat['boat_club_display'] = club_info['boat_club_display']
                boat['club_list'] = club_info['club_list']
                boat['is_multi_club_crew'] = club_info['is_multi_club_crew']
                boat['updated_at'] = get_timestamp()
                
                db.put_item(boat)
                logger.info(f"Boat club info recalculated: {assigned_boat_id} -> {club_info['boat_club_display']}")
    
    # Return success response
    return success_response(data=crew_data)
