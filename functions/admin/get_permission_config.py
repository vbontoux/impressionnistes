"""
Lambda function to get the current permission configuration.
Admin only.
"""
import json
import os
import sys
import boto3
from botocore.exceptions import ClientError

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.access_control import get_default_permissions

def lambda_handler(event, context):
    """
    Get current permission configuration.
    
    Returns:
        200: Permission configuration retrieved successfully
        500: Internal server error
    """
    try:
        # Initialize DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table_name = os.environ.get('DYNAMODB_TABLE') or os.environ.get('TABLE_NAME')
        table = dynamodb.Table(table_name)
        
        # Get permission configuration from DynamoDB
        response = table.get_item(
            Key={
                'PK': 'CONFIG',
                'SK': 'PERMISSIONS'
            }
        )
        
        if 'Item' not in response:
            # Return default permissions if not found
            permissions = get_default_permissions()
        else:
            permissions = response['Item'].get('permissions', {})
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            'body': json.dumps({
                'permissions': permissions
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
                    'message': 'Failed to retrieve permission configuration'
                }
            })
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            'body': json.dumps({
                'error': {
                    'message': f'Internal server error: {str(e)}'
                }
            })
        }
