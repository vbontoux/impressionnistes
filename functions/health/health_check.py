"""
Health check Lambda function
Returns system health status
"""
import json
import os
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')


def lambda_handler(event, context):
    """
    Health check endpoint
    
    Returns:
        dict: Health status of system components
    """
    table_name = os.environ.get('TABLE_NAME', 'impressionnistes-registration-dev')
    
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'environment': os.environ.get('ENVIRONMENT', 'dev'),
        'components': {}
    }
    
    # Check DynamoDB table
    try:
        table = dynamodb.Table(table_name)
        table.table_status
        health_status['components']['dynamodb'] = {
            'status': 'healthy',
            'table_name': table_name
        }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['components']['dynamodb'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Check configuration
    try:
        table = dynamodb.Table(table_name)
        response = table.get_item(
            Key={'PK': 'CONFIG', 'SK': 'SYSTEM'}
        )
        if response.get('Item'):
            health_status['components']['configuration'] = {
                'status': 'healthy',
                'message': 'Configuration loaded'
            }
        else:
            health_status['status'] = 'degraded'
            health_status['components']['configuration'] = {
                'status': 'warning',
                'message': 'Configuration not found'
            }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['components']['configuration'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Determine HTTP status code
    status_code = 200
    if health_status['status'] == 'degraded':
        status_code = 200  # Still operational
    elif health_status['status'] == 'unhealthy':
        status_code = 503  # Service unavailable
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        },
        'body': json.dumps(health_status, indent=2)
    }
