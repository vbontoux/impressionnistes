"""
Lambda function for updating boat registrations
Team managers can edit boat registration information during registration period
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
from validation import validate_boat_registration, sanitize_dict, boat_registration_schema
from database import get_db_client, get_timestamp
from auth_utils import get_user_from_event, require_team_manager
from configuration import ConfigurationManager
from boat_registration_utils import (
    validate_boat_type_for_event,
    calculate_registration_status,
    detect_multi_club_crew,
    get_assigned_crew_members,
    validate_seat_assignment
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager
def lambda_handler(event, context):
    """
    Update an existing boat registration
    
    Path parameters:
        - boat_registration_id: ID of the boat registration to update
    
    Request body:
        - event_type: Event type (optional)
        - boat_type: Boat type (optional)
        - race_id: Race ID (optional)
        - seats: List of seat assignments (optional)
        - is_boat_rental: Boolean indicating if boat is rented (optional)
    
    Returns:
        Updated boat registration object
    """
    logger.info("Update boat registration request")
    
    # Get authenticated user
    user = get_user_from_event(event)
    team_manager_id = user['user_id']
    
    # Get boat registration ID from path
    boat_registration_id = event.get('pathParameters', {}).get('boat_registration_id')
    if not boat_registration_id:
        return validation_error({'boat_registration_id': 'Boat registration ID is required'})
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error({'body': 'Invalid JSON'})
    
    # Get existing boat registration
    db = get_db_client()
    
    existing_boat = db.get_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'BOAT#{boat_registration_id}'
    )
    
    if not existing_boat:
        return not_found_error('Boat registration not found')
    
    # Check if registration period is active
    config_manager = ConfigurationManager()
    system_config = config_manager.get_system_config()
    
    # TODO: Add registration period check when configuration is fully implemented
    # For now, allow updates
    
    # Prepare update data
    update_data = {}
    
    if 'event_type' in body:
        update_data['event_type'] = body['event_type'].strip()
    if 'boat_type' in body:
        update_data['boat_type'] = body['boat_type'].strip()
    if 'race_id' in body:
        update_data['race_id'] = body['race_id']
    if 'seats' in body:
        update_data['seats'] = body['seats']
    if 'is_boat_rental' in body:
        update_data['is_boat_rental'] = body['is_boat_rental']
    
    # Validate boat type for event if both are being updated
    event_type = update_data.get('event_type', existing_boat.get('event_type'))
    boat_type = update_data.get('boat_type', existing_boat.get('boat_type'))
    
    if not validate_boat_type_for_event(event_type, boat_type):
        return validation_error({
            'boat_type': f"Boat type '{boat_type}' is not valid for event '{event_type}'"
        })
    
    # Extract only the boat registration fields for validation
    boat_fields_to_validate = {
        'event_type': existing_boat.get('event_type'),
        'boat_type': existing_boat.get('boat_type'),
        'race_id': existing_boat.get('race_id'),
        'seats': existing_boat.get('seats', []),
        'is_boat_rental': existing_boat.get('is_boat_rental', False),
        'is_multi_club_crew': existing_boat.get('is_multi_club_crew', False),
        'registration_status': existing_boat.get('registration_status', 'incomplete'),
        'flagged_issues': existing_boat.get('flagged_issues', [])
    }
    
    # Merge with update data
    boat_fields_to_validate.update(update_data)
    boat_fields_to_validate = sanitize_dict(boat_fields_to_validate, boat_registration_schema)
    
    # Validate updated boat registration data
    is_valid, errors = validate_boat_registration(boat_fields_to_validate)
    if not is_valid:
        return validation_error(errors)
    
    # Calculate multi-club crew status if seats were updated
    if 'seats' in update_data:
        # Get all crew members for this team
        all_crew_members = db.query_by_pk(
            pk=f'TEAM#{team_manager_id}',
            sk_prefix='CREW#'
        )
        
        # Get all boat registrations for validation
        all_boats = db.query_by_pk(
            pk=f'TEAM#{team_manager_id}',
            sk_prefix='BOAT#'
        )
        
        # Create a map of crew members for easy lookup
        crew_member_map = {member['crew_member_id']: member for member in all_crew_members}
        
        # Validate seat assignments
        # Add boat_registration_id to the validation dict so it can skip itself
        validation_dict = {**boat_fields_to_validate, 'boat_registration_id': boat_registration_id}
        
        for seat in boat_fields_to_validate['seats']:
            crew_member_id = seat.get('crew_member_id')
            if crew_member_id:
                validation = validate_seat_assignment(
                    validation_dict,
                    crew_member_id,
                    seat['position'],
                    all_boats
                )
                if not validation['valid']:
                    # Add crew member name to error message
                    crew_member = crew_member_map.get(crew_member_id)
                    if crew_member:
                        member_name = f"{crew_member.get('first_name', '')} {crew_member.get('last_name', '')}".strip()
                        error_msg = f"{member_name}: {validation['reason']}"
                    else:
                        error_msg = validation['reason']
                    return validation_error({'assignment': error_msg})
        
        # Update crew member assigned_boat_id fields
        # First, get the old seat assignments to know who to unassign
        old_assigned_ids = set()
        for seat in existing_boat.get('seats', []):
            if seat.get('crew_member_id'):
                old_assigned_ids.add(seat.get('crew_member_id'))
        
        # Get new assigned IDs
        new_assigned_ids = set()
        for seat in boat_fields_to_validate['seats']:
            if seat.get('crew_member_id'):
                new_assigned_ids.add(seat.get('crew_member_id'))
        
        # Unassign crew members who were removed
        for crew_member_id in old_assigned_ids - new_assigned_ids:
            crew_member = db.get_item(
                pk=f'TEAM#{team_manager_id}',
                sk=f'CREW#{crew_member_id}'
            )
            if crew_member:
                crew_member['assigned_boat_id'] = None
                crew_member['updated_at'] = get_timestamp()
                db.put_item(crew_member)
        
        # Assign new crew members
        for crew_member_id in new_assigned_ids:
            crew_member = db.get_item(
                pk=f'TEAM#{team_manager_id}',
                sk=f'CREW#{crew_member_id}'
            )
            if crew_member:
                crew_member['assigned_boat_id'] = boat_registration_id
                crew_member['updated_at'] = get_timestamp()
                db.put_item(crew_member)
        
        # Get assigned crew members
        assigned_members = get_assigned_crew_members(
            boat_fields_to_validate['seats'],
            all_crew_members
        )
        
        # Detect multi-club crew
        boat_fields_to_validate['is_multi_club_crew'] = detect_multi_club_crew(assigned_members)
    
    # Calculate registration status
    registration_status = calculate_registration_status(boat_fields_to_validate)
    boat_fields_to_validate['registration_status'] = registration_status
    
    # Merge validated fields back into the full database record
    updated_boat = {**existing_boat, **boat_fields_to_validate}
    updated_boat['updated_at'] = get_timestamp()
    
    # Update boat registration in DynamoDB
    db.put_item(updated_boat)
    logger.info(f"Boat registration updated: {boat_registration_id}")
    
    # Return success response
    return success_response(data=updated_boat)
