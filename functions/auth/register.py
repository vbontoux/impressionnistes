"""
Lambda function for team manager registration
Creates Cognito user and stores profile in DynamoDB
"""
import json
import os
import boto3
import logging
from datetime import datetime

# Import from Lambda layer (shared modules are in /opt/python/)
from responses import (
    success_response,
    validation_error,
    conflict_error,
    internal_error,
    handle_exceptions
)
from validation import validate_team_manager, sanitize_dict
from database import get_db_client, get_timestamp

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cognito = boto3.client('cognito-idp')


@handle_exceptions
def lambda_handler(event, context):
    """
    Register a new team manager
    
    Request body:
        - email: Email address
        - password: Password
        - first_name: First name
        - last_name: Last name
        - club_affiliation: Rowing club
        - mobile_number: Mobile phone number
    
    Returns:
        User profile with user_id
    """
    logger.info("Team manager registration request")
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error({'body': 'Invalid JSON'})
    
    # Extract and sanitize data
    email = body.get('email', '').strip().lower()
    password = body.get('password', '')
    first_name = body.get('first_name', '').strip()
    last_name = body.get('last_name', '').strip()
    club_affiliation = body.get('club_affiliation', '').strip()
    mobile_number = body.get('mobile_number', '').strip()
    
    # Validate profile data
    profile_data = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'club_affiliation': club_affiliation,
        'mobile_number': mobile_number
    }
    
    is_valid, errors = validate_team_manager(profile_data)
    if not is_valid:
        return validation_error(errors)
    
    # Validate password
    if not password or len(password) < 8:
        return validation_error({'password': 'Password must be at least 8 characters'})
    
    # Get User Pool ID from environment
    user_pool_id = os.environ.get('USER_POOL_ID')
    if not user_pool_id:
        logger.error("USER_POOL_ID not configured")
        return internal_error("Authentication service not configured")
    
    try:
        # Create user in Cognito
        logger.info(f"Creating Cognito user: {email}")
        cognito_response = cognito.sign_up(
            ClientId=os.environ.get('USER_POOL_CLIENT_ID'),
            Username=email,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'given_name', 'Value': first_name},
                {'Name': 'family_name', 'Value': last_name},
                {'Name': 'phone_number', 'Value': mobile_number},
                {'Name': 'custom:club_affiliation', 'Value': club_affiliation},
                {'Name': 'custom:role', 'Value': 'team_manager'}
            ]
        )
        
        user_sub = cognito_response['UserSub']
        logger.info(f"Cognito user created: {user_sub}")
        
        # Add user to team_managers group
        try:
            cognito.admin_add_user_to_group(
                UserPoolId=user_pool_id,
                Username=email,
                GroupName='team_managers'
            )
            logger.info(f"User added to team_managers group")
        except Exception as e:
            logger.warning(f"Failed to add user to group: {e}")
        
        # Store profile in DynamoDB
        db = get_db_client()
        
        profile_item = {
            'PK': f'USER#{user_sub}',
            'SK': 'PROFILE',
            'user_id': user_sub,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'club_affiliation': club_affiliation,
            'mobile_number': mobile_number,
            'role': 'team_manager',
            'created_at': get_timestamp(),
            'updated_at': get_timestamp()
        }
        
        db.put_item(profile_item)
        logger.info(f"Profile stored in DynamoDB: {user_sub}")
        
        # Return success response
        return success_response(
            data={
                'user_id': user_sub,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'club_affiliation': club_affiliation,
                'message': 'Registration successful. Please check your email to verify your account.'
            },
            status_code=201
        )
        
    except cognito.exceptions.UsernameExistsException:
        logger.warning(f"User already exists: {email}")
        return conflict_error('An account with this email already exists')
    
    except cognito.exceptions.InvalidPasswordException as e:
        logger.warning(f"Invalid password: {e}")
        return validation_error({'password': str(e)})
    
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        return internal_error("Registration failed. Please try again.")
