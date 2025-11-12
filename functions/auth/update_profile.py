"""
Lambda function for team manager profile updates
Updates profile in both Cognito and DynamoDB
"""
import json
import os
import boto3
import logging

# Import from Lambda layer (shared modules are in /opt/python/)
from responses import (
    success_response,
    validation_error,
    not_found_error,
    internal_error,
    handle_exceptions,
    parse_request_body
)
from validation import validate_team_manager, sanitize_dict
from database import get_db_client, get_timestamp
from auth_utils import require_auth, get_user_from_event

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cognito = boto3.client('cognito-idp')


@handle_exceptions
@require_auth
def lambda_handler(event, context):
    """
    Update team manager profile
    
    Request body (all fields optional):
        - first_name: First name
        - last_name: Last name
        - club_affiliation: Rowing club
        - mobile_number: Mobile phone number
    
    Returns:
        Updated user profile
    """
    logger.info("Profile update request")
    
    # Get authenticated user
    user_info = get_user_from_event(event)
    user_id = user_info['user_id']
    email = user_info['email']
    
    # Parse request body
    try:
        body = parse_request_body(event)
    except ValueError as e:
        return validation_error({'body': str(e)})
    
    # Extract and sanitize updatable fields
    updates = {}
    cognito_updates = []
    
    if 'first_name' in body:
        first_name = body['first_name'].strip()
        if first_name:
            updates['first_name'] = first_name
            cognito_updates.append({
                'Name': 'given_name',
                'Value': first_name
            })
    
    if 'last_name' in body:
        last_name = body['last_name'].strip()
        if last_name:
            updates['last_name'] = last_name
            cognito_updates.append({
                'Name': 'family_name',
                'Value': last_name
            })
    
    if 'club_affiliation' in body:
        club_affiliation = body['club_affiliation'].strip()
        if club_affiliation:
            updates['club_affiliation'] = club_affiliation
            cognito_updates.append({
                'Name': 'custom:club_affiliation',
                'Value': club_affiliation
            })
    
    if 'mobile_number' in body:
        mobile_number = body['mobile_number'].strip()
        if mobile_number:
            updates['mobile_number'] = mobile_number
            cognito_updates.append({
                'Name': 'phone_number',
                'Value': mobile_number
            })
    
    if not updates:
        return validation_error({'updates': 'No valid fields to update'})
    
    # Validate the updates
    # Get current profile to merge with updates for validation
    db = get_db_client()
    current_profile = db.get_item(f'USER#{user_id}', 'PROFILE')
    
    if not current_profile:
        return not_found_error('profile')
    
    # Merge current profile with updates for validation
    profile_to_validate = {
        'email': current_profile.get('email'),
        'first_name': updates.get('first_name', current_profile.get('first_name')),
        'last_name': updates.get('last_name', current_profile.get('last_name')),
        'club_affiliation': updates.get('club_affiliation', current_profile.get('club_affiliation')),
        'mobile_number': updates.get('mobile_number', current_profile.get('mobile_number'))
    }
    
    is_valid, errors = validate_team_manager(profile_to_validate)
    if not is_valid:
        return validation_error(errors)
    
    # Get User Pool ID from environment
    user_pool_id = os.environ.get('USER_POOL_ID')
    if not user_pool_id:
        logger.error("USER_POOL_ID not configured")
        return internal_error("Authentication service not configured")
    
    try:
        # Update Cognito user attributes
        if cognito_updates:
            logger.info(f"Updating Cognito attributes for user: {email}")
            cognito.admin_update_user_attributes(
                UserPoolId=user_pool_id,
                Username=email,
                UserAttributes=cognito_updates
            )
            logger.info("Cognito attributes updated successfully")
        
        # Update DynamoDB profile
        updates['updated_at'] = get_timestamp()
        
        updated_profile = db.update_item(
            pk=f'USER#{user_id}',
            sk='PROFILE',
            updates=updates
        )
        
        logger.info(f"Profile updated in DynamoDB: {user_id}")
        
        # Return updated profile
        return success_response(
            data={
                'user_id': updated_profile.get('user_id'),
                'email': updated_profile.get('email'),
                'first_name': updated_profile.get('first_name'),
                'last_name': updated_profile.get('last_name'),
                'club_affiliation': updated_profile.get('club_affiliation'),
                'mobile_number': updated_profile.get('mobile_number'),
                'updated_at': updated_profile.get('updated_at')
            },
            message='Profile updated successfully'
        )
        
    except cognito.exceptions.UserNotFoundException:
        logger.error(f"Cognito user not found: {email}")
        return not_found_error('user')
    
    except Exception as e:
        logger.error(f"Profile update failed: {str(e)}", exc_info=True)
        return internal_error("Profile update failed. Please try again.")
