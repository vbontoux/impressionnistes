"""
Lambda function for getting a single boat registration
Team managers can view details of a specific boat registration
"""
import json
import logging

# Import from Lambda layer
from responses import (
    success_response,
    validation_error,
    not_found_error,
    internal_error,
    handle_exceptions
)
from database import get_db_client
from auth_utils import get_user_from_event, require_team_manager
from pricing import calculate_boat_pricing
from configuration import ConfigurationManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager
def lambda_handler(event, context):
    """
    Get a single boat registration by ID
    
    Path parameters:
        - boat_registration_id: ID of the boat registration to retrieve
    
    Returns:
        Boat registration object
    """
    logger.info("Get boat registration request")
    
    # Get authenticated user
    user = get_user_from_event(event)
    team_manager_id = user['user_id']
    
    # Get boat registration ID from path
    boat_registration_id = event.get('pathParameters', {}).get('boat_registration_id')
    if not boat_registration_id:
        return validation_error({'boat_registration_id': 'Boat registration ID is required'})
    
    # Get boat registration from DynamoDB
    db = get_db_client()
    
    boat_registration = db.get_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'BOAT#{boat_registration_id}'
    )
    
    if not boat_registration:
        return not_found_error('Boat registration not found')
    
    logger.info(f"Retrieved boat registration: {boat_registration_id}")
    
    # Calculate pricing if boat has crew assigned
    if boat_registration.get('seats') and any(seat.get('crew_member_id') for seat in boat_registration['seats']):
        # Get crew members for pricing calculation
        crew_members = db.query_by_pk(
            pk=f'TEAM#{team_manager_id}',
            sk_prefix='CREW#'
        )
        
        # Get pricing configuration
        config_manager = ConfigurationManager()
        pricing_config = config_manager.get_pricing_config()
        
        # Calculate and add pricing
        pricing = calculate_boat_pricing(boat_registration, crew_members, pricing_config)
        boat_registration['pricing'] = pricing
    else:
        boat_registration['pricing'] = None
    
    # Return success response
    return success_response(data=boat_registration)
