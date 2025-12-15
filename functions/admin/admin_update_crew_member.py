"""
Lambda function for admin to update crew members for any team manager
Admin only - bypasses registration period restrictions
"""
import json
import logging
from datetime import datetime

from responses import success_response, validation_error, not_found_error, handle_exceptions
from auth_utils import require_admin
from database import get_db_client
from validation import validate_crew_member

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Admin updates a crew member for any team manager
    Bypasses registration period restrictions
    
    Path parameters:
        team_manager_id: ID of the team manager
        crew_member_id: ID of the crew member to update
    
    Request body:
        first_name: Crew member first name (optional)
        last_name: Crew member last name (optional)
        date_of_birth: Date of birth in YYYY-MM-DD format (optional)
        gender: M or F (optional)
        license_number: FFA license number (optional)
        club_affiliation: Club name (optional)
    
    Returns:
        Updated crew member object
    """
    logger.info("Admin update crew member request")
    
    # Get path parameters
    path_params = event.get('pathParameters', {})
    team_manager_id = path_params.get('team_manager_id')
    crew_member_id = path_params.get('crew_member_id')
    
    if not team_manager_id or not crew_member_id:
        return validation_error('team_manager_id and crew_member_id are required')
    
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error('Invalid JSON in request body')
    
    # Validate crew member data if provided
    if body:
        validation_errors = validate_crew_member(body, partial=True)
        if validation_errors:
            return validation_error('Validation failed', validation_errors)
    
    # Get database client
    db = get_db_client()
    
    try:
        # Get existing crew member
        response = db.table.get_item(
            Key={
                'PK': f'TEAM#{team_manager_id}',
                'SK': f'CREW#{crew_member_id}'
            }
        )
        
        if 'Item' not in response:
            return not_found_error(f'Crew member {crew_member_id} not found')
        
        crew_member = response['Item']
        
        # Check for duplicate license number if license is being changed
        if 'license_number' in body and body['license_number'] != crew_member.get('license_number'):
            existing_crew = db.table.query(
                IndexName='GSI3',
                KeyConditionExpression='license_number = :license',
                ExpressionAttributeValues={
                    ':license': body['license_number']
                }
            )
            
            if existing_crew.get('Items'):
                return validation_error(
                    f'License number {body["license_number"]} is already in use',
                    {'license_number': 'This license number is already registered'}
                )
        
        # Update fields
        current_time = datetime.utcnow().isoformat() + 'Z'
        
        update_expression_parts = ['#updated_at = :updated_at', '#updated_by_admin = :updated_by_admin']
        expression_attribute_names = {
            '#updated_at': 'updated_at',
            '#updated_by_admin': 'updated_by_admin'
        }
        expression_attribute_values = {
            ':updated_at': current_time,
            ':updated_by_admin': True
        }
        
        # Add fields to update
        updatable_fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 'license_number', 'club_affiliation']
        for field in updatable_fields:
            if field in body:
                attr_name = f'#{field}'
                attr_value = f':{field}'
                update_expression_parts.append(f'{attr_name} = {attr_value}')
                expression_attribute_names[attr_name] = field
                expression_attribute_values[attr_value] = body[field]
        
        # Update in DynamoDB
        update_response = db.table.update_item(
            Key={
                'PK': f'TEAM#{team_manager_id}',
                'SK': f'CREW#{crew_member_id}'
            },
            UpdateExpression='SET ' + ', '.join(update_expression_parts),
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'
        )
        
        updated_crew = update_response['Attributes']
        
        logger.info(f"Admin updated crew member {crew_member_id} for team manager {team_manager_id}")
        
        return success_response(
            data={'crew_member': updated_crew}
        )
        
    except Exception as e:
        logger.error(f"Failed to update crew member: {str(e)}", exc_info=True)
        return validation_error(f'Failed to update crew member: {str(e)}')
