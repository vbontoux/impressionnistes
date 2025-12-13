"""
Lambda function to get confirmed rental boats ready for payment
Team managers can see their confirmed rentals that need payment
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
from configuration import ConfigurationManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def calculate_rental_price(boat_type: str, base_seat_price: Decimal) -> Decimal:
    """
    Calculate rental price based on boat type
    - Skiffs: 2.5x Base_Seat_Price
    - Crew boats: Base_Seat_Price per seat
    """
    # Skiff pricing
    if boat_type == 'skiff':
        return base_seat_price * Decimal('2.5')
    
    # Crew boat pricing - Base_Seat_Price per seat
    seat_counts = {
        '4-': 4,
        '4+': 5,  # 4 rowers + 1 cox
        '4x-': 4,
        '4x+': 5,  # 4 rowers + 1 cox
        '8+': 9,  # 8 rowers + 1 cox
        '8x+': 9   # 8 rowers + 1 cox
    }
    
    seats = seat_counts.get(boat_type, 1)
    return base_seat_price * Decimal(str(seats))


@handle_exceptions
@require_team_manager
def lambda_handler(event, context):
    """
    Get confirmed rental boats for the authenticated team manager
    Only returns rentals with status 'confirmed' (ready for payment)
    
    Returns:
        List of confirmed rental boats with pricing information
    """
    logger.info("Get rentals for payment request")
    
    # Get authenticated user
    user = get_user_from_event(event)
    team_manager_id = user['user_id']
    team_manager_email = user.get('email')
    
    logger.info(f"Getting rentals for payment for team manager: {team_manager_id} ({team_manager_email})")
    
    # Get database client
    db = get_db_client()
    
    # Get pricing configuration
    config_manager = ConfigurationManager()
    pricing_config = config_manager.get_pricing_config()
    base_seat_price = Decimal(str(pricing_config.get('base_seat_price', 20)))
    
    # Query all rental boats using scan
    try:
        response = db.table.scan(
            FilterExpression='begins_with(PK, :pk_prefix) AND SK = :sk',
            ExpressionAttributeValues={
                ':pk_prefix': 'RENTAL_BOAT#',
                ':sk': 'METADATA'
            }
        )
        
        all_rentals = response.get('Items', [])
        
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
            all_rentals.extend(response.get('Items', []))
    except Exception as e:
        logger.error(f"Failed to query rental boats: {str(e)}")
        return internal_error(f"Failed to query rental boats: {str(e)}")
    
    # Filter for confirmed rentals belonging to this team manager
    # Note: requester is stored as email, not user_id
    confirmed_rentals = []
    for rental in all_rentals:
        if (rental.get('status') == 'confirmed' and 
            rental.get('requester') == team_manager_email):
            
            # Calculate rental price
            boat_type = rental.get('boat_type', 'skiff')
            rental_price = calculate_rental_price(boat_type, base_seat_price)
            
            # Add pricing information
            rental['pricing'] = {
                'rental_fee': float(rental_price),
                'total': float(rental_price),
                'currency': 'EUR'
            }
            
            confirmed_rentals.append(rental)
    
    logger.info(f"Found {len(confirmed_rentals)} confirmed rentals for payment")
    
    return success_response(data={
        'rental_boats': confirmed_rentals,
        'count': len(confirmed_rentals)
    })
