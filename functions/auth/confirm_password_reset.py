"""
Lambda function to confirm password reset
Confirms password reset with verification code
"""
import json
import os
import boto3
import logging

# Add parent directory to path for shared imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.responses import (
    success_response,
    validation_error,
    internal_error,
    handle_exceptions,
    parse_request_body
)
from shared.validation import validate_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cognito = boto3.client('cognito-idp')


@handle_exceptions
def lambda_handler(event, context):
    """
    Confirm password reset with verification code
    
    Request body:
        - email: Email address of the user
        - code: Verification code from email
        - new_password: New password
    
    Returns:
        Success message
    """
    logger.info("Confirm password reset request")
    
    # Parse request body
    try:
        body = parse_request_body(event)
    except ValueError as e:
        return validation_error({'body': str(e)})
    
    # Extract and validate fields
    email = body.get('email', '').strip().lower()
    code = body.get('code', '').strip()
    new_password = body.get('new_password', '')
    
    errors = {}
    
    if not email:
        errors['email'] = 'Email is required'
    elif not validate_email(email):
        errors['email'] = 'Invalid email format'
    
    if not code:
        errors['code'] = 'Verification code is required'
    
    if not new_password:
        errors['new_password'] = 'New password is required'
    elif len(new_password) < 8:
        errors['new_password'] = 'Password must be at least 8 characters'
    
    if errors:
        return validation_error(errors)
    
    # Get User Pool Client ID from environment
    client_id = os.environ.get('USER_POOL_CLIENT_ID')
    if not client_id:
        logger.error("USER_POOL_CLIENT_ID not configured")
        return internal_error("Authentication service not configured")
    
    try:
        # Confirm password reset
        logger.info(f"Confirming password reset for: {email}")
        cognito.confirm_forgot_password(
            ClientId=client_id,
            Username=email,
            ConfirmationCode=code,
            Password=new_password
        )
        
        logger.info(f"Password reset confirmed for: {email}")
        
        return success_response(
            data={
                'message': 'Password has been reset successfully. You can now log in with your new password.'
            }
        )
        
    except cognito.exceptions.CodeMismatchException:
        logger.warning(f"Invalid verification code for: {email}")
        return validation_error({
            'code': 'Invalid or expired verification code'
        })
    
    except cognito.exceptions.ExpiredCodeException:
        logger.warning(f"Expired verification code for: {email}")
        return validation_error({
            'code': 'Verification code has expired. Please request a new one.'
        })
    
    except cognito.exceptions.InvalidPasswordException as e:
        logger.warning(f"Invalid password for: {email}")
        return validation_error({
            'new_password': 'Password does not meet requirements. Must be at least 8 characters with uppercase, lowercase, and numbers.'
        })
    
    except cognito.exceptions.UserNotFoundException:
        logger.warning(f"User not found for password reset: {email}")
        return validation_error({
            'email': 'User not found'
        })
    
    except cognito.exceptions.LimitExceededException:
        logger.warning(f"Rate limit exceeded for password reset confirmation: {email}")
        return validation_error({
            'code': 'Too many attempts. Please try again later.'
        })
    
    except Exception as e:
        logger.error(f"Password reset confirmation failed: {str(e)}", exc_info=True)
        return internal_error("Password reset failed. Please try again.")
