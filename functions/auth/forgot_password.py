"""
Lambda function to initiate password reset
Sends password reset code via email using Cognito
"""
import json
import os
import boto3
import logging

# Import from Lambda layer (shared modules are in /opt/python/)
from responses import (
    success_response,
    validation_error,
    internal_error,
    handle_exceptions,
    parse_request_body
)
from validation import validate_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cognito = boto3.client('cognito-idp')


@handle_exceptions
def lambda_handler(event, context):
    """
    Initiate password reset process
    
    Request body:
        - email: Email address of the user
    
    Returns:
        Success message (always returns success for security)
    """
    logger.info("Forgot password request")
    
    # Parse request body
    try:
        body = parse_request_body(event)
    except ValueError as e:
        return validation_error({'body': str(e)})
    
    # Extract and validate email
    email = body.get('email', '').strip().lower()
    
    if not email:
        return validation_error({'email': 'Email is required'})
    
    if not validate_email(email):
        return validation_error({'email': 'Invalid email format'})
    
    # Get User Pool Client ID from environment
    client_id = os.environ.get('USER_POOL_CLIENT_ID')
    if not client_id:
        logger.error("USER_POOL_CLIENT_ID not configured")
        return internal_error("Authentication service not configured")
    
    try:
        # Initiate forgot password flow
        logger.info(f"Initiating password reset for: {email}")
        cognito.forgot_password(
            ClientId=client_id,
            Username=email
        )
        
        logger.info(f"Password reset code sent to: {email}")
        
        # Always return success for security (don't reveal if user exists)
        return success_response(
            data={
                'message': 'If an account exists with this email, a password reset code has been sent.'
            }
        )
        
    except cognito.exceptions.UserNotFoundException:
        # Don't reveal that user doesn't exist
        logger.info(f"Password reset requested for non-existent user: {email}")
        return success_response(
            data={
                'message': 'If an account exists with this email, a password reset code has been sent.'
            }
        )
    
    except cognito.exceptions.LimitExceededException:
        logger.warning(f"Rate limit exceeded for password reset: {email}")
        return validation_error({
            'email': 'Too many password reset attempts. Please try again later.'
        })
    
    except cognito.exceptions.InvalidParameterException as e:
        logger.error(f"Invalid parameter for password reset: {str(e)}")
        return validation_error({'email': 'Invalid email address'})
    
    except Exception as e:
        logger.error(f"Password reset initiation failed: {str(e)}", exc_info=True)
        return internal_error("Password reset failed. Please try again.")
