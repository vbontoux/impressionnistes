"""
Lambda function to list all temporary access grants
Admin only - retrieves all grants with their status and remaining time
"""
import json
import logging
from datetime import datetime
from decimal import Decimal

from responses import success_response, validation_error, handle_exceptions
from auth_utils import require_admin
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def calculate_remaining_time(expiration_timestamp_str):
    """
    Calculate remaining time in hours for a grant
    
    Args:
        expiration_timestamp_str: ISO format timestamp string
    
    Returns:
        Remaining hours (float), or 0 if expired
    """
    try:
        # Parse the timestamp - handle both with and without 'Z'
        expiration_str = expiration_timestamp_str.replace('Z', '')
        expiration = datetime.fromisoformat(expiration_str)
        now = datetime.utcnow()
        
        if now >= expiration:
            return 0
        
        remaining = expiration - now
        return remaining.total_seconds() / 3600  # Convert to hours
    except Exception as e:
        logger.warning(f"Failed to calculate remaining time: {str(e)}")
        return 0


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    List all temporary access grants
    
    Query parameters:
        status: Filter by status (active, expired, revoked) - optional
    
    Returns:
        List of grants with details and remaining time
    """
    logger.info("List temporary access grants request")
    
    # Parse query parameters
    query_params = event.get('queryStringParameters') or {}
    status_filter = query_params.get('status')
    
    db = get_db_client()
    
    try:
        # Query all temporary access grants
        response = db.table.query(
            KeyConditionExpression='PK = :pk',
            ExpressionAttributeValues={
                ':pk': 'TEMP_ACCESS'
            }
        )
        
        grants = response.get('Items', [])
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            response = db.table.query(
                KeyConditionExpression='PK = :pk',
                ExpressionAttributeValues={
                    ':pk': 'TEMP_ACCESS'
                },
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            grants.extend(response.get('Items', []))
        
        logger.info(f"Found {len(grants)} total grants")
        
        # Process grants and calculate remaining time
        processed_grants = []
        now = datetime.utcnow()
        
        for grant in grants:
            # Check if grant has expired and update status if needed
            expiration_str = grant.get('expiration_timestamp', '')
            current_status = grant.get('status', 'active')
            
            try:
                # Parse timestamp - handle both with and without 'Z'
                expiration_str = expiration_str.replace('Z', '')
                expiration = datetime.fromisoformat(expiration_str)
                if current_status == 'active' and now >= expiration:
                    # Mark as expired
                    db.table.update_item(
                        Key={
                            'PK': grant['PK'],
                            'SK': grant['SK']
                        },
                        UpdateExpression='SET #status = :status',
                        ExpressionAttributeNames={
                            '#status': 'status'
                        },
                        ExpressionAttributeValues={
                            ':status': 'expired'
                        }
                    )
                    current_status = 'expired'
                    logger.info(f"Marked grant {grant['SK']} as expired")
            except Exception as e:
                logger.warning(f"Failed to check/update expiration for grant {grant.get('SK')}: {str(e)}")
            
            # Calculate remaining time
            remaining_hours = calculate_remaining_time(expiration_str)
            
            grant_data = {
                'user_id': grant.get('user_id'),
                'grant_timestamp': grant.get('grant_timestamp'),
                'expiration_timestamp': grant.get('expiration_timestamp'),
                'granted_by_admin_id': grant.get('granted_by_admin_id'),
                'status': current_status,
                'hours': grant.get('hours'),
                'remaining_hours': round(remaining_hours, 2),
                'notes': grant.get('notes', ''),
                'revoked_at': grant.get('revoked_at'),
                'revoked_by_admin_id': grant.get('revoked_by_admin_id')
            }
            
            # Apply status filter if provided
            if status_filter and current_status != status_filter:
                continue
            
            processed_grants.append(grant_data)
        
        # Sort by grant timestamp (most recent first)
        processed_grants.sort(key=lambda x: x['grant_timestamp'], reverse=True)
        
        logger.info(f"Returning {len(processed_grants)} grants (filtered by status: {status_filter or 'all'})")
        
        return success_response(
            data={
                'grants': json.loads(json.dumps(processed_grants, default=decimal_to_float)),
                'count': len(processed_grants)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to list temporary access grants: {str(e)}", exc_info=True)
        return validation_error(f'Failed to list temporary access grants: {str(e)}')
