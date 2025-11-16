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
from validation import validate_crew_member, sanitize_dict, crew_member_schema
from database import get_db_client, get_timestamp
from auth_utils import get_user_from_event, require_team_manager
from configuration import ConfigurationManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager
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
        - license_number: Alphanumeric 6-12 characters (optional)
        - club_affiliation: Rowing club (optional)
    
    Returns:
        Updated crew member object
    """
    logger.info("Update crew member request")
    
    # Get authenticated user
    user = get_user_from_event(event)
    team_manager_id = user['user_id']
    
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
    
    # TODO: Add registration period check when configuration is fully implemented
    # For now, allow updates
    
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
    
    # Recalculate is_rcpm_member if club_affiliation changed
    if 'club_affiliation' in update_data:
        crew_data['is_rcpm_member'] = crew_data['club_affiliation'].upper() == 'RCPM'
    
    # Update timestamp
    crew_data['updated_at'] = get_timestamp()
    
    # Update crew member in DynamoDB
    db.put_item(crew_data)
    logger.info(f"Crew member updated: {crew_member_id}")
    
    # Return success response
    return success_response(data=crew_data)
