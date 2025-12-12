"""
Lambda function to get rental requests for the authenticated team manager
Team manager accessible - shows their own rental requests
"""
import json
import logging

from responses import success_response, validation_error, handle_exceptions
from auth_utils import require_auth, get_user_from_event
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_auth
def lambda_handler(event, context):
    """
    Get rental requests for the authenticated team manager
    
    Returns:
        List of rental requests for this team manager
    """
    logger.info("Get my rental requests")
    
    # Get authenticated user
    user_info = get_user_from_event(event)
    team_manager_id = user_info['user_id']
    team_manager_email = user_info.get('email', team_manager_id)
    
    # Query database for rental boats requested by this team manager
    db = get_db_client()
    
    try:
        # Query all rental boats where requester matches this team manager
        response = db.table.scan(
            FilterExpression='begins_with(PK, :pk_prefix) AND SK = :sk AND requester = :requester',
            ExpressionAttributeValues={
                ':pk_prefix': 'RENTAL_BOAT#',
                ':sk': 'METADATA',
                ':requester': team_manager_email
            }
        )
        
        rental_requests = response.get('Items', [])
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            response = db.table.scan(
                FilterExpression='begins_with(PK, :pk_prefix) AND SK = :sk AND requester = :requester',
                ExpressionAttributeValues={
                    ':pk_prefix': 'RENTAL_BOAT#',
                    ':sk': 'METADATA',
                    ':requester': team_manager_email
                },
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            rental_requests.extend(response.get('Items', []))
        
        # Sort by requested_at (most recent first)
        rental_requests.sort(key=lambda r: r.get('requested_at', ''), reverse=True)
        
        # Return relevant fields for team managers
        result_requests = []
        for request in rental_requests:
            result_requests.append({
                'rental_boat_id': request.get('rental_boat_id') or request.get('PK'),
                'boat_type': request.get('boat_type'),
                'boat_name': request.get('boat_name'),
                'rower_weight_range': request.get('rower_weight_range'),
                'status': request.get('status'),
                'requested_at': request.get('requested_at'),
                'confirmed_at': request.get('confirmed_at'),
                'confirmed_by': request.get('confirmed_by')
            })
        
        logger.info(f"Retrieved {len(result_requests)} rental requests for team manager {team_manager_id}")
        
        return success_response(
            data={
                'rental_requests': result_requests,
                'count': len(result_requests)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get rental requests: {str(e)}")
        return validation_error(f'Failed to get rental requests: {str(e)}')