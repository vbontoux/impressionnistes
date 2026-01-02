"""
Lambda function for assigning crew members to boat seats
Handles seat assignment with validation and audit logging
"""
import json
import logging

# Import from Lambda layer
from responses import (
    success_response,
    validation_error,
    not_found_error,
    conflict_error,
    internal_error,
    handle_exceptions
)
from database import get_db_client, get_timestamp
from auth_utils import get_user_from_event, require_team_manager
from boat_registration_utils import (
    validate_seat_assignment,
    get_assigned_crew_members,
    detect_multi_club_crew,
    calculate_registration_status,
    calculate_boat_club_info
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager
def lambda_handler(event, context):
    """
    Assign a crew member to a boat seat
    
    Path parameters:
        - boat_registration_id: ID of the boat registration
    
    Request body:
        - position: Seat position (1-9)
        - crew_member_id: ID of crew member to assign (or null to clear)
    
    Returns:
        Updated boat registration object
    """
    logger.info("Assign seat request")
    
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
    
    position = body.get('position')
    crew_member_id = body.get('crew_member_id')
    
    if position is None:
        return validation_error({'position': 'Position is required'})
    
    # Get existing boat registration
    db = get_db_client()
    
    boat_registration = db.get_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'BOAT#{boat_registration_id}'
    )
    
    if not boat_registration:
        return not_found_error('Boat registration not found')
    
    # Get all boat registrations for validation
    all_boats = db.query_by_pk(
        pk=f'TEAM#{team_manager_id}',
        sk_prefix='BOAT#'
    )
    
    # If assigning a crew member (not clearing)
    if crew_member_id:
        # Get crew member to verify it exists and for validation
        crew_member = db.get_item(
            pk=f'TEAM#{team_manager_id}',
            sk=f'CREW#{crew_member_id}'
        )
        
        if not crew_member:
            return not_found_error('Crew member not found')
        
        # Validate seat assignment (including J14 restriction)
        validation = validate_seat_assignment(
            boat_registration,
            crew_member_id,
            position,
            all_boats,
            crew_member
        )
        
        if not validation['valid']:
            return conflict_error(validation['reason'])
    
    # Find and update the seat
    seats = boat_registration.get('seats', [])
    seat_found = False
    old_crew_member_id = None
    
    for seat in seats:
        if seat['position'] == position:
            old_crew_member_id = seat.get('crew_member_id')
            seat['crew_member_id'] = crew_member_id
            seat_found = True
            break
    
    if not seat_found:
        return validation_error({'position': f'Invalid position {position} for this boat type'})
    
    # Update crew member assignment status
    if old_crew_member_id and old_crew_member_id != crew_member_id:
        # Unassign old crew member
        old_crew = db.get_item(
            pk=f'TEAM#{team_manager_id}',
            sk=f'CREW#{old_crew_member_id}'
        )
        if old_crew:
            old_crew['assigned_boat_id'] = None
            old_crew['updated_at'] = get_timestamp()
            db.put_item(old_crew)
            logger.info(f"Unassigned crew member {old_crew_member_id} from boat {boat_registration_id}")
    
    if crew_member_id:
        # Assign new crew member
        new_crew = db.get_item(
            pk=f'TEAM#{team_manager_id}',
            sk=f'CREW#{crew_member_id}'
        )
        if new_crew:
            new_crew['assigned_boat_id'] = boat_registration_id
            new_crew['updated_at'] = get_timestamp()
            db.put_item(new_crew)
            logger.info(f"Assigned crew member {crew_member_id} to boat {boat_registration_id} position {position}")
    
    # Get all crew members for multi-club detection
    all_crew_members = db.query_by_pk(
        pk=f'TEAM#{team_manager_id}',
        sk_prefix='CREW#'
    )
    
    # Get assigned crew members
    assigned_members = get_assigned_crew_members(seats, all_crew_members)
    
    # Detect multi-club crew (for backward compatibility)
    boat_registration['is_multi_club_crew'] = detect_multi_club_crew(assigned_members)
    
    # Get team manager's club affiliation for club field calculation
    team_manager = db.get_item(
        pk=f'USER#{team_manager_id}',
        sk='PROFILE'
    )
    team_manager_club = team_manager.get('club_affiliation', '') if team_manager else ''
    
    # Recalculate club display fields based on assigned crew
    club_info = calculate_boat_club_info(assigned_members, team_manager_club)
    boat_registration['boat_club_display'] = club_info['boat_club_display']
    boat_registration['club_list'] = club_info['club_list']
    
    # Calculate registration status
    boat_registration['registration_status'] = calculate_registration_status(boat_registration)
    
    # Update boat registration
    boat_registration['seats'] = seats
    boat_registration['updated_at'] = get_timestamp()
    
    # Audit log
    audit_entry = {
        'action': 'seat_assignment',
        'boat_registration_id': boat_registration_id,
        'position': position,
        'old_crew_member_id': old_crew_member_id,
        'new_crew_member_id': crew_member_id,
        'performed_by': team_manager_id,
        'timestamp': get_timestamp()
    }
    logger.info(f"Seat assignment audit: {json.dumps(audit_entry)}")
    
    db.put_item(boat_registration)
    
    # Return success response
    return success_response(data=boat_registration)
