"""
Lambda function for admin to create a boat registration for any team manager
Admin only - can create boats regardless of date limits
"""
import json
import logging
import uuid

from responses import (
    success_response,
    validation_error,
    handle_exceptions
)
from validation import validate_boat_registration, sanitize_dict, boat_registration_schema
from database import get_db_client, get_timestamp
from auth_utils import require_admin
from boat_registration_utils import (
    get_required_seats_for_boat_type,
    validate_boat_type_for_event,
    calculate_registration_status
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Create a new boat registration for a team manager (admin only)
    
    Request body:
        - team_manager_id: Team manager ID (required)
        - event_type: Event type (21km or 42km) (required)
        - boat_type: Boat type (skiff, 4-, 4+, 8+) (required)
        - race_id: Race ID (optional)
        - seats: List of seat assignments (optional)
        - is_boat_rental: Boolean indicating if boat is rented (optional)
        - forfait: Boolean to mark boat as forfait (optional)
    
    Returns:
        Boat registration object with boat_registration_id
    """
    logger.info("Admin create boat request")
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error({'body': 'Invalid JSON'})
    
    # Extract required fields
    team_manager_id = body.get('team_manager_id', '').strip()
    event_type = body.get('event_type', '').strip()
    boat_type = body.get('boat_type', '').strip()
    
    if not team_manager_id:
        return validation_error({'team_manager_id': 'Team manager ID is required'})
    
    if not event_type or not boat_type:
        return validation_error({
            'event_type': 'Event type is required' if not event_type else None,
            'boat_type': 'Boat type is required' if not boat_type else None
        })
    
    # Validate boat type for event
    if not validate_boat_type_for_event(event_type, boat_type):
        return validation_error({
            'boat_type': f"Boat type '{boat_type}' is not valid for event '{event_type}'"
        })
    
    # Verify team manager exists
    db = get_db_client()
    team_manager = db.get_item(
        pk=f'USER#{team_manager_id}',
        sk='PROFILE'
    )
    
    if not team_manager:
        return validation_error({'team_manager_id': 'Team manager not found'})
    
    # Get or create seat structure
    seats = body.get('seats')
    if not seats:
        # Create default seat structure for boat type
        seats = get_required_seats_for_boat_type(boat_type)
    
    # Prepare boat registration data
    boat_data = {
        'event_type': event_type,
        'boat_type': boat_type,
        'race_id': body.get('race_id'),
        'seats': seats,
        'is_boat_rental': body.get('is_boat_rental', False),
        'is_multi_club_crew': False,
        'registration_status': 'incomplete',
        'forfait': body.get('forfait', False),
        'flagged_issues': []
    }
    
    # Sanitize data
    boat_data = sanitize_dict(boat_data, boat_registration_schema)
    
    # Validate boat registration data
    is_valid, errors = validate_boat_registration(boat_data)
    if not is_valid:
        return validation_error(errors)
    
    # Generate boat registration ID
    boat_registration_id = str(uuid.uuid4())
    
    # Calculate registration status
    registration_status = calculate_registration_status(boat_data)
    
    # Store boat registration in DynamoDB
    boat_registration_item = {
        'PK': f'TEAM#{team_manager_id}',
        'SK': f'BOAT#{boat_registration_id}',
        'boat_registration_id': boat_registration_id,
        'team_manager_id': team_manager_id,
        'event_type': boat_data['event_type'],
        'boat_type': boat_data['boat_type'],
        'race_id': boat_data.get('race_id'),
        'seats': boat_data['seats'],
        'is_boat_rental': boat_data['is_boat_rental'],
        'is_multi_club_crew': boat_data['is_multi_club_crew'],
        'registration_status': registration_status,
        'forfait': boat_data.get('forfait', False),
        'flagged_issues': boat_data.get('flagged_issues', []),
        'created_at': get_timestamp(),
        'updated_at': get_timestamp()
    }
    
    db.put_item(boat_registration_item)
    logger.info(f"Admin created boat registration: {boat_registration_id} for team manager: {team_manager_id}")
    
    # Return success response
    return success_response(
        data=boat_registration_item,
        status_code=201
    )
