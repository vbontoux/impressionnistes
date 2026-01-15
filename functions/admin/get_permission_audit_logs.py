"""
Lambda function to retrieve permission audit logs with filtering and pagination.

This function queries audit logs from DynamoDB and supports:
- Filtering by user_id, action, date range, and log type
- Pagination with next_token
- Returns both denial logs and bypass logs
"""

import json
import os
from datetime import datetime
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr
import boto3


def decimal_default(obj):
    """JSON serializer for Decimal objects."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    """
    Get permission audit logs with filtering and pagination.
    
    Query Parameters:
    - user_id: Filter by user ID
    - action: Filter by action (e.g., 'edit_crew_member')
    - log_type: Filter by log type ('denial', 'bypass', 'all')
    - start_date: Filter by start date (ISO format)
    - end_date: Filter by end date (ISO format)
    - limit: Number of results per page (default: 50, max: 100)
    - next_token: Pagination token from previous response
    
    Returns:
    - logs: List of audit log entries
    - next_token: Token for next page (if more results exist)
    - total_count: Total number of logs matching filters
    """
    # Initialize DynamoDB table
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ.get('DYNAMODB_TABLE') or os.environ.get('TABLE_NAME')
    table = dynamodb.Table(table_name)
    
    try:
        # Extract query parameters
        query_params = event.get('queryStringParameters') or {}
        user_id = query_params.get('user_id')
        action = query_params.get('action')
        log_type = query_params.get('log_type', 'all')  # 'denial', 'bypass', 'all'
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        limit = min(int(query_params.get('limit', 50)), 100)
        next_token = query_params.get('next_token')
        
        # Determine which log types to query
        log_types = []
        if log_type in ['denial', 'all']:
            log_types.append('AUDIT#PERMISSION_DENIAL')
        if log_type in ['bypass', 'all']:
            log_types.append('AUDIT#PERMISSION_BYPASS')
        if log_type == 'config':
            log_types.append('AUDIT#PERMISSION_CONFIG')
        
        # Query logs for each type
        all_logs = []
        for pk in log_types:
            # Build query
            key_condition = Key('PK').eq(pk)
            
            # Add date range to sort key condition if provided
            if start_date and end_date:
                key_condition = key_condition & Key('SK').between(start_date, end_date + 'Z')
            elif start_date:
                key_condition = key_condition & Key('SK').gte(start_date)
            elif end_date:
                key_condition = key_condition & Key('SK').lte(end_date + 'Z')
            
            # Build filter expression for additional filters
            filter_expression = None
            if user_id:
                filter_expression = Attr('user_id').eq(user_id)
            if action:
                action_filter = Attr('action').eq(action)
                filter_expression = action_filter if filter_expression is None else filter_expression & action_filter
            
            # Execute query
            query_kwargs = {
                'KeyConditionExpression': key_condition,
                'ScanIndexForward': False,  # Sort descending (newest first)
                'Limit': limit
            }
            
            if filter_expression:
                query_kwargs['FilterExpression'] = filter_expression
            
            if next_token:
                try:
                    query_kwargs['ExclusiveStartKey'] = json.loads(next_token)
                except:
                    pass  # Invalid token, ignore
            
            response = table.query(**query_kwargs)
            
            # Add log type to each item
            for item in response.get('Items', []):
                item['log_type'] = pk.replace('AUDIT#PERMISSION_', '').lower()
            
            all_logs.extend(response.get('Items', []))
        
        # Sort all logs by timestamp (SK) descending
        all_logs.sort(key=lambda x: x.get('SK', ''), reverse=True)
        
        # Apply limit
        logs = all_logs[:limit]
        has_more = len(all_logs) > limit
        
        # Generate next token if there are more results
        response_next_token = None
        if has_more and logs:
            last_item = logs[-1]
            response_next_token = json.dumps({
                'PK': last_item['PK'],
                'SK': last_item['SK']
            })
        
        # Format response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps({
                'logs': logs,
                'next_token': response_next_token,
                'total_count': len(logs),
                'has_more': has_more
            }, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error retrieving audit logs: {str(e)}")
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
                'error': 'Failed to retrieve audit logs',
                'message': str(e)
            })
        }
