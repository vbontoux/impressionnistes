"""
Lambda function to update the permission configuration.
Admin only.
"""
import json
import os
import sys
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def validate_permission_matrix(permissions):
    """
    Validate the permission matrix for consistency.
    
    Args:
        permissions: Dictionary of permissions
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_actions = [
        'create_crew_member',
        'edit_crew_member',
        'delete_crew_member',
        'create_boat_registration',
        'edit_boat_registration',
        'delete_boat_registration',
        'process_payment',
        'view_data',
        'export_data'
    ]
    
    required_phases = [
        'before_registration',
        'during_registration',
        'after_registration',
        'after_payment_deadline'
    ]
    
    # Check all required actions are present
    for action in required_actions:
        if action not in permissions:
            return False, f"Missing action: {action}"
        
        # Check all required phases are present for each action
        for phase in required_phases:
            if phase not in permissions[action]:
                return False, f"Missing phase '{phase}' for action '{action}'"
            
            # Check phase value is boolean
            if not isinstance(permissions[action][phase], bool):
                return False, f"Phase '{phase}' for action '{action}' must be boolean"
    
    # Validate data state restrictions if present
    for action in permissions:
        if 'requires_not_assigned' in permissions[action]:
            if not isinstance(permissions[action]['requires_not_assigned'], bool):
                return False, f"requires_not_assigned for '{action}' must be boolean"
        
        if 'requires_not_paid' in permissions[action]:
            if not isinstance(permissions[action]['requires_not_paid'], bool):
                return False, f"requires_not_paid for '{action}' must be boolean"
    
    return True, None

def lambda_handler(event, context):
    """
    Update permission configuration.
    
    Expected body:
        {
            "permissions": {
                "action_name": {
                    "before_registration": bool,
                    "during_registration": bool,
                    "after_registration": bool,
                    "after_payment_deadline": bool,
                    "requires_not_assigned": bool (optional),
                    "requires_not_paid": bool (optional)
                },
                ...
            }
        }
    
    Returns:
        200: Configuration updated successfully
        400: Invalid request
        500: Internal server error
    """
    try:
        # Initialize DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table_name = os.environ.get('DYNAMODB_TABLE') or os.environ.get('TABLE_NAME')
        table = dynamodb.Table(table_name)
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        permissions = body.get('permissions')
        
        if not permissions:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True,
                },
                'body': json.dumps({
                    'error': {
                        'message': 'Missing permissions in request body'
                    }
                })
            }
        
        # Validate permission matrix
        is_valid, error_message = validate_permission_matrix(permissions)
        if not is_valid:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True,
                },
                'body': json.dumps({
                    'error': {
                        'message': f'Invalid permission matrix: {error_message}'
                    }
                })
            }
        
        # Get admin user ID from request context
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})
        claims = authorizer.get('claims', {})
        admin_email = claims.get('email', 'unknown')
        
        # Update permission configuration in DynamoDB
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        table.put_item(
            Item={
                'PK': 'CONFIG',
                'SK': 'PERMISSIONS',
                'permissions': permissions,
                'updated_at': timestamp,
                'updated_by': admin_email
            }
        )
        
        # Log configuration change
        table.put_item(
            Item={
                'PK': 'AUDIT#PERMISSION_CONFIG',
                'SK': f"{timestamp}#{admin_email}",
                'action': 'update_permission_config',
                'admin_email': admin_email,
                'timestamp': timestamp,
                'permissions': permissions
            }
        )
        
        # Invalidate permission cache (handled by access_control module on next request)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            'body': json.dumps({
                'message': 'Permission configuration updated successfully',
                'permissions': permissions,
                'updated_at': timestamp,
                'updated_by': admin_email
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            'body': json.dumps({
                'error': {
                    'message': 'Invalid JSON in request body'
                }
            })
        }
    except ClientError as e:
        print(f"DynamoDB error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            'body': json.dumps({
                'error': {
                    'message': 'Failed to update permission configuration'
                }
            })
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            'body': json.dumps({
                'error': {
                    'message': 'Internal server error'
                }
            })
        }
