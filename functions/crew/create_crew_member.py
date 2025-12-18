"""
Lambda function for creating crew members
Team managers can add crew members to their roster
"""
import json
import os
import boto3
import logging
from datetime import datetime
import uuid

# Import from Lambda layer
from responses import (
    success_response,
    validation_error,
    internal_error,
    handle_exceptions 
)
from validation import validate_crew_member, sanitize_dict, crew_member_schema, is_rcpm_member
from database import get_db_client, get_timestamp
from auth_utils import get_user_from_event, require_team_manager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager
def lambda_handler(event, context):
    """
    Create a new crew member
    
    Request body:
        - first_name: First name (required)
        - last_name: Last name (required)
        - date_of_birth: Date of birth in YYYY-MM-DD format (required)
        - gender: M or F (required)
        - license_number: Alphanumeric 6-12 characters (required)
        - club_affiliation: Rowing club (optional, defaults to team manager's club)
    
    Returns:
        Crew member object with crew_member_id
    """
    logger.info("Create crew member request")
    
    # Get authenticated user
    user = get_user_from_event(event)
    team_manager_id = user['user_id']
    team_manager_club = user.get('club_affiliation', '')
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error({'body': 'Invalid JSON'})
    
    # Extract and sanitize data
    crew_data = sanitize_dict({ 
        'first_name': body.get('first_name', '').strip(),
        'last_name': body.get('last_name', '').strip(),
        'date_of_birth': body.get('date_of_birth', '').strip(),
        'gender': body.get('gender', '').strip().upper(),
        'license_number': body.get('license_number', '').strip().upper(),
        'club_affiliation': body.get('club_affiliation', '').strip() or team_manager_club,
    }, crew_member_schema)
    
    # Validate crew member data
    is_valid, errors = validate_crew_member(crew_data)
    if not is_valid:
        return validation_error(errors)
    
    # Check for duplicate license number using GSI3
    db = get_db_client()
    if db.check_license_number_exists(crew_data['license_number']):
        logger.warning(f"Duplicate license number attempted: {crew_data['license_number']}")
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
                        'license_number': f'The license number {crew_data["license_number"]} is already registered in the competition'
                    }
                }
            })
        }
    
    # Calculate is_rcpm_member based on club_affiliation
    # Uses case-insensitive matching for "RCPM", "Port-Marly", "Port Marly"
    rcpm_member = is_rcpm_member(crew_data['club_affiliation'])
    
    # Generate crew member ID
    crew_member_id = str(uuid.uuid4())
    
    # Store crew member in DynamoDB
    crew_member_item = {
        'PK': f'TEAM#{team_manager_id}',
        'SK': f'CREW#{crew_member_id}',
        'crew_member_id': crew_member_id,
        'team_manager_id': team_manager_id,
        'first_name': crew_data['first_name'],
        'last_name': crew_data['last_name'],
        'date_of_birth': crew_data['date_of_birth'],
        'gender': crew_data['gender'],
        'license_number': crew_data['license_number'],  # GSI3 partition key
        'club_affiliation': crew_data['club_affiliation'],
        'is_rcpm_member': rcpm_member,
        'assigned_boat_id': None,
        'flagged_issues': [],
        'created_at': get_timestamp(),
        'updated_at': get_timestamp()
    }
    
    db.put_item(crew_member_item)
    logger.info(f"Crew member created: {crew_member_id}")
    
    # Return success response
    return success_response(
        data=crew_member_item,
        status_code=201
    )
