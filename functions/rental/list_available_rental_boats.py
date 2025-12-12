"""
Lambda function to list available rental boats for team managers
Team manager accessible - shows only boats available for rental
"""
import json
import logging

from responses import success_response, validation_error, handle_exceptions
from auth_utils import require_auth, get_user_from_event
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Valid boat types for filtering
VALID_BOAT_TYPES = ['skiff', '4-', '4+', '4x-', '4x+', '8+', '8x+']


@handle_exceptions
@require_auth
def lambda_handler(event, context):
    """
    List available rental boats for team managers
    
    Query parameters:
        boat_type: Filter by boat type (optional)
    
    Returns:
        List of available rental boats
    """
    logger.info("List available rental boats request")
    
    # Get authenticated user
    user_info = get_user_from_event(event)
    team_manager_id = user_info['user_id']
    
    # Get query parameters
    query_params = event.get('queryStringParameters') or {}
    filter_boat_type = query_params.get('boat_type')
    
    # Validate filter
    if filter_boat_type and filter_boat_type not in VALID_BOAT_TYPES:
        return validation_error(f"Invalid boat_type. Must be one of: {', '.join(VALID_BOAT_TYPES)}")
    
    # Query database for available rental boats
    db = get_db_client()
    
    try:
        # Query all rental boats
        response = db.table.scan(
            FilterExpression='begins_with(PK, :pk_prefix) AND SK = :sk',
            ExpressionAttributeValues={
                ':pk_prefix': 'RENTAL_BOAT#',
                ':sk': 'METADATA'
            }
        )
        
        rental_boats = response.get('Items', [])
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            response = db.table.scan(
                FilterExpression='begins_with(PK, :pk_prefix) AND SK = :sk',
                ExpressionAttributeValues={
                    ':pk_prefix': 'RENTAL_BOAT#',
                    ':sk': 'METADATA'
                },
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            rental_boats.extend(response.get('Items', []))
        
        # Filter to only available boats (status "available" only)
        available_boats = []
        for boat in rental_boats:
            status = boat.get('status', 'new')
            if status == 'available':
                available_boats.append(boat)
        
        # Apply boat type filter if provided
        if filter_boat_type:
            available_boats = [b for b in available_boats if b.get('boat_type') == filter_boat_type]
        
        # Sort by boat_type, then boat_name
        available_boats.sort(key=lambda b: (b.get('boat_type', ''), b.get('boat_name', '')))
        
        # Return only relevant fields for team managers
        result_boats = []
        for boat in available_boats:
            result_boats.append({
                'rental_boat_id': boat.get('rental_boat_id') or boat.get('PK'),
                'boat_type': boat.get('boat_type'),
                'boat_name': boat.get('boat_name'),
                'rower_weight_range': boat.get('rower_weight_range'),
                'status': boat.get('status')
            })
        
        logger.info(f"Retrieved {len(result_boats)} available rental boats for team manager {team_manager_id}")
        
        return success_response(
            data={
                'rental_boats': result_boats,
                'count': len(result_boats)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to list available rental boats: {str(e)}")
        return validation_error(f'Failed to list available rental boats: {str(e)}')