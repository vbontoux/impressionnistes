"""
Lambda function for admin to update any boat registration
Admin only - can update boats regardless of date limits
"""
import json
import logging

from responses import (
    success_response,
    validation_error,
    not_found_error,
    handle_exceptions
)
from validation import validate_boat_registration, sanitize_dict, boat_registration_schema
from database import get_db_client, get_timestamp
from auth_utils import require_admin
from boat_registration_utils import (
    calculate_registration_status,
    detect_multi_club_crew,
    get_assigned_crew_members
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Update a boat registration (admin only)
    Admin can update any boat at any time, including setting forfait status
    
    Path parameters:
        team_manager_id: Team manager ID
        boat_registration_id: Boat registration ID
    
    Request body:
        - Any boat registration fields to update
        - forfait: Boolean to mark boat as forfait (out)
    
    Returns:
        Updated boat registration object
    """
    logger.info("Admin update boat request")
    
    # Get path parameters
    path_params = event.get('pathParameters', {})
    team_manager_id = path_params.get('team_manager_id')
    boat_registration_id = path_params.get('boat_registration_id')
    
    if not team_manager_id or not boat_registration_id:
        return validation_error({
            'path': 'team_manager_id and boat_registration_id are required'
        })
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error({'body': 'Invalid JSON'})
    
    if not body:
        return validation_error({'body': 'Request body is required'})
    
    # Get existing boat registration
    db = get_db_client()
    
    existing_boat = db.get_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'BOAT#{boat_registration_id}'
    )
    
    if not existing_boat:
        return not_found_error('Boat registration not found')
    
    # Prepare update data
    update_data = {}
    
    # Allow updating these fields
    updatable_fields = [
        'event_type', 'boat_type', 'race_id', 'seats',
        'is_boat_rental', 'registration_status', 'forfait'
    ]
    
    for field in updatable_fields:
        if field in body:
            update_data[field] = body[field]
    
    # If seats are updated, recalculate multi-club crew status
    if 'seats' in update_data:
        # Get crew members for this team manager
        crew_members = db.query_by_pk(
            pk=f'TEAM#{team_manager_id}',
            sk_prefix='CREW#'
        )
        
        # Create temporary boat object for calculation
        temp_boat = {**existing_boat, **update_data}
        is_multi_club = detect_multi_club_crew(temp_boat, crew_members)
        update_data['is_multi_club_crew'] = is_multi_club
        
        # Recalculate registration status
        registration_status = calculate_registration_status(temp_boat)
        update_data['registration_status'] = registration_status
    
    # Update timestamp
    update_data['updated_at'] = get_timestamp()
    
    # Update boat registration in DynamoDB
    updated_boat = db.update_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'BOAT#{boat_registration_id}',
        updates=update_data
    )
    
    logger.info(f"Admin updated boat registration: {boat_registration_id}")
    
    # Return success response
    return success_response(data=updated_boat)
