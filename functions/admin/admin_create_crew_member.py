"""
Lambda function for admin to create crew members for any team manager
Admin only - bypasses registration period restrictions
"""
import json
import logging
import uuid
from datetime import datetime

from responses import success_response, validation_error, handle_exceptions
from auth_utils import require_admin
from database import get_db_client
from validation import validate_crew_member

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Admin creates a crew member for a specified team manager
    Bypasses registration period restrictions
    
    Request body:
        team_manager_id: ID of the team manager (required)
        first_name: Crew member first name (required)
        last_name: Crew member last name (required)
        date_of_birth: Date of birth in YYYY-MM-DD format (required)
        gender: M or F (required)
        license_number: FFA license number (required)
        club_affiliation: Club name (optional, defaults to team manager's club)
    
    Returns:
        Created crew member object
    """
    logger.info("Admin create crew member request")
    
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error('Invalid JSON in request body')
    
    # Validate required fields
    team_manager_id = body.get('team_manager_id')
    if not team_manager_id:
        return validation_error('team_manager_id is required')
    
    # Validate crew member data
    validation_errors = validate_crew_member(body)
    if validation_errors:
        return validation_error('Validation failed', validation_errors)
    
    # Get database client
    db = get_db_client()
    
    try:
        # Verify team manager exists
        tm_response = db.table.get_item(
            Key={
                'PK': f'TEAM#{team_manager_id}',
                'SK': 'PROFILE'
            }
        )
        
        if 'Item' not in tm_response:
            return validation_error(f'Team manager {team_manager_id} not found')
        
        team_manager = tm_response['Item']
        
        # Check for duplicate license number using GSI3
        license_number = body['license_number']
        existing_crew = db.table.query(
            IndexName='GSI3',
            KeyConditionExpression='license_number = :license',
            ExpressionAttributeValues={
                ':license': license_number
            }
        )
        
        if existing_crew.get('Items'):
            return validation_error(
                f'License number {license_number} is already in use',
                {'license_number': 'This license number is already registered'}
            )
        
        # Generate crew member ID
        crew_id = str(uuid.uuid4())
        current_time = datetime.utcnow().isoformat() + 'Z'
        
        # Determine club affiliation
        club_affiliation = body.get('club_affiliation') or team_manager.get('club_affiliation', '')
        
        # Create crew member item
        crew_member = {
            'PK': f'TEAM#{team_manager_id}',
            'SK': f'CREW#{crew_id}',
            'crew_id': crew_id,
            'team_manager_id': team_manager_id,
            'first_name': body['first_name'],
            'last_name': body['last_name'],
            'date_of_birth': body['date_of_birth'],
            'gender': body['gender'],
            'license_number': license_number,
            'club_affiliation': club_affiliation,
            'created_at': current_time,
            'updated_at': current_time,
            'created_by_admin': True  # Flag to indicate admin creation
        }
        
        # Save to DynamoDB
        db.table.put_item(Item=crew_member)
        
        logger.info(f"Admin created crew member {crew_id} for team manager {team_manager_id}")
        
        return success_response(
            data={'crew_member': crew_member},
            status_code=201
        )
        
    except Exception as e:
        logger.error(f"Failed to create crew member: {str(e)}", exc_info=True)
        return validation_error(f'Failed to create crew member: {str(e)}')
