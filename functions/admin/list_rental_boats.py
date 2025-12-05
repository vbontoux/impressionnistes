"""
Lambda function to list all rental boat hulls in inventory
Admin only - retrieves all rental boats with optional filtering
Note: This is different from boat_registration which is a team's race registration
"""
import json
import logging

from responses import success_response, validation_error, handle_exceptions
from auth_utils import require_admin
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Valid boat types
VALID_BOAT_TYPES = ['skiff', '4-', '4+', '4x-', '4x+', '8+', '8x+']

# Valid statuses
VALID_STATUSES = ['new', 'available', 'requested', 'confirmed', 'paid']


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    List all rental boat hulls in inventory with optional filtering
    
    Query parameters:
        boat_type: Filter by boat type (optional)
        status: Filter by status (optional)
    
    Returns:
        List of rental boats
    """
    logger.info("List rental boats request")
    
    # Get query parameters
    query_params = event.get('queryStringParameters') or {}
    filter_boat_type = query_params.get('boat_type')
    filter_status = query_params.get('status')
    
    # Validate filters
    if filter_boat_type and filter_boat_type not in VALID_BOAT_TYPES:
        return validation_error(f"Invalid boat_type. Must be one of: {', '.join(VALID_BOAT_TYPES)}")
    
    if filter_status and filter_status not in VALID_STATUSES:
        return validation_error(f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")
    
    # Query database for all rental boats
    db = get_db_client()
    
    try:
        # Query all items with PK starting with 'RENTAL_BOAT#'
        rental_boats = []
        
        # Use scan to get all rental boats
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
        
        # Apply filters
        if filter_boat_type:
            rental_boats = [b for b in rental_boats if b.get('boat_type') == filter_boat_type]
        
        if filter_status:
            rental_boats = [b for b in rental_boats if b.get('status') == filter_status]
        
        # Add rental_boat_id field if not present (for consistency with create response)
        for boat in rental_boats:
            if 'rental_boat_id' not in boat:
                boat['rental_boat_id'] = boat['PK']
        
        # Sort by boat_type, then boat_name
        rental_boats.sort(key=lambda b: (b.get('boat_type', ''), b.get('boat_name', '')))
        
        logger.info(f"Retrieved {len(rental_boats)} rental boats")
        
        return success_response(
            data={
                'rental_boats': rental_boats,
                'count': len(rental_boats)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to list rental boats: {str(e)}")
        return validation_error(f'Failed to list rental boats: {str(e)}')
