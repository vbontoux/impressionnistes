"""
Lambda function to clear all permission audit logs.

This function:
1. Deletes all audit log entries from DynamoDB
2. Creates a meta-audit log entry recording this action
3. Returns count of deleted logs

IMPORTANT: This is a destructive operation. The frontend should export logs
before calling this endpoint.
"""

import json
import os
from datetime import datetime
from decimal import Decimal
from boto3.dynamodb.conditions import Key
import boto3


def decimal_default(obj):
    """JSON serializer for Decimal objects."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    """
    Clear all permission audit logs.
    
    This endpoint should only be called by admins and should be preceded
    by an export operation to preserve the logs.
    
    Returns:
    - deleted_count: Number of logs deleted
    - timestamp: When the operation was performed
    """
    # Initialize DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ.get('DYNAMODB_TABLE') or os.environ.get('TABLE_NAME')
    table = dynamodb.Table(table_name)
    
    try:
        # Get user info from request context
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})
        claims = authorizer.get('claims', {})
        user_id = claims.get('sub', 'unknown')
        user_email = claims.get('email', 'unknown')
        
        # Count and collect all audit logs
        log_types = [
            'AUDIT#PERMISSION_DENIAL',
            'AUDIT#PERMISSION_BYPASS',
            'AUDIT#PERMISSION_CONFIG'
        ]
        
        total_deleted = 0
        
        # Delete logs for each type
        for pk in log_types:
            # Query all logs of this type
            response = table.query(
                KeyConditionExpression=Key('PK').eq(pk),
                ProjectionExpression='PK, SK'
            )
            
            items = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = table.query(
                    KeyConditionExpression=Key('PK').eq(pk),
                    ProjectionExpression='PK, SK',
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                items.extend(response.get('Items', []))
            
            # Delete items in batches
            with table.batch_writer() as batch:
                for item in items:
                    batch.delete_item(
                        Key={
                            'PK': item['PK'],
                            'SK': item['SK']
                        }
                    )
                    total_deleted += 1
        
        # Create meta-audit log entry
        timestamp = datetime.utcnow().isoformat() + 'Z'
        meta_log_sk = f"{timestamp}#{user_id}"
        
        table.put_item(
            Item={
                'PK': 'AUDIT#PERMISSION_CONFIG',
                'SK': meta_log_sk,
                'user_id': user_id,
                'user_email': user_email,
                'action': 'clear_audit_logs',
                'timestamp': timestamp,
                'deleted_count': total_deleted,
                'description': f'Cleared all audit logs ({total_deleted} entries)'
            }
        )
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps({
                'deleted_count': total_deleted,
                'timestamp': timestamp,
                'message': f'Successfully cleared {total_deleted} audit log entries'
            }, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error clearing audit logs: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps({
                'error': 'Failed to clear audit logs',
                'message': str(e)
            })
        }
