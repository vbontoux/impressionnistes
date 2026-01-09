"""
Lambda function to get accepted rental requests ready for payment
Team managers can see their accepted rental requests that need payment
"""
import json
import logging
from decimal import Decimal

# Import from Lambda layer
from responses import (
    success_response,
    internal_error,
    handle_exceptions
)
from database import get_db_client
from auth_utils import get_user_from_event, require_team_manager
from pricing import calculate_rental_request_pricing

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager
def lambda_handler(event, context):
    """
    Get accepted rental requests for the authenticated team manager
    Only returns requests with status 'accepted' (ready for payment)
    
    Returns:
        List of accepted rental requests with pricing information
    """
    logger.info("Get rental requests for payment")
    
    # Get authenticated user
    user = get_user_from_event(event)
    team_manager_id = user['user_id']
    team_manager_email = user.get('email')
    
    logger.info(f"Getting rental requests for payment for team manager: {team_manager_id} ({team_manager_email})")
    
    # Get database client
    db = get_db_client()
    
    # Query all rental requests using scan
    try:
        response = db.table.scan(
            FilterExpression='begins_with(PK, :pk_prefix) AND SK = :sk',
            ExpressionAttributeValues={
                ':pk_prefix': 'RENTAL_REQUEST#',
                ':sk': 'METADATA'
            }
        )
        
        all_requests = response.get('Items', [])
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            response = db.table.scan(
                FilterExpression='begins_with(PK, :pk_prefix) AND SK = :sk',
                ExpressionAttributeValues={
                    ':pk_prefix': 'RENTAL_REQUEST#',
                    ':sk': 'METADATA'
                },
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            all_requests.extend(response.get('Items', []))
    except Exception as e:
        logger.error(f"Failed to query rental requests: {str(e)}")
        return internal_error(f"Failed to query rental requests: {str(e)}")
    
    # Filter for accepted requests belonging to this team manager
    accepted_requests = []
    for request in all_requests:
        if (request.get('status') == 'accepted' and 
            request.get('requester_id') == team_manager_id):
            
            # Calculate rental price
            boat_type = request.get('boat_type', 'skiff')
            pricing = calculate_rental_request_pricing(boat_type)
            
            # Strip RENTAL_REQUEST# prefix from ID for frontend
            full_id = request.get('rental_request_id', '')
            clean_id = full_id.replace('RENTAL_REQUEST#', '') if full_id else ''
            
            # Build response object with clean ID
            request_data = {
                'rental_request_id': clean_id,
                'boat_type': request.get('boat_type'),
                'desired_weight_range': request.get('desired_weight_range'),
                'request_comment': request.get('request_comment'),
                'status': request.get('status'),
                'assignment_details': request.get('assignment_details'),
                'accepted_at': request.get('accepted_at'),
                'created_at': request.get('created_at'),
                'pricing': {
                    'rental_fee': float(pricing['rental_fee']),
                    'total': float(pricing['total']),
                    'currency': pricing['currency']
                }
            }
            
            accepted_requests.append(request_data)
    
    logger.info(f"Found {len(accepted_requests)} accepted rental requests for payment")
    
    return success_response(data={
        'rental_requests': accepted_requests,
        'count': len(accepted_requests)
    })
