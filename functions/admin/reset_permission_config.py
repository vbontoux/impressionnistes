"""
Lambda function to reset permission configuration to defaults.
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

def lambda_handler(event, context):
    """
    Reset permission configuration to defaults.
    
    Returns:
        200: Configuration reset successfully
        500: Internal server error
    """
    try:
        # Initialize DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table_name = os.environ.get('DYNAMODB_TABLE') or os.environ.get('TABLE_NAME')
        table = dynamodb.Table(table_name)
        
        # Get default permissions
        from shared.access_control import get_default_permissions
        default_permissions = get_default_permissions()
        
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
                'permissions': default_permissions,
                'updated_at': timestamp,
                'updated_by': admin_email
            }
        )
        
        # Log configuration reset
        table.put_item(
            Item={
                'PK': 'AUDIT#PERMISSION_CONFIG',
                'SK': f"{timestamp}#{admin_email}",
                'action': 'reset_permission_config',
                'admin_email': admin_email,
                'timestamp': timestamp,
                'permissions': default_permissions
            }
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            'body': json.dumps({
                'message': 'Permission configuration reset to defaults',
                'permissions': default_permissions,
                'updated_at': timestamp,
                'updated_by': admin_email
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
                    'message': 'Failed to reset permission configuration'
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
