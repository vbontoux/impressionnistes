"""
Lambda function for listing boat registrations
Team managers can view all their boat registrations
"""
import json
import logging

# Import from Lambda layer
from responses import (
    success_response,
    internal_error,
    handle_exceptions
)
from database import get_db_client
from auth_utils import get_user_from_event, require_team_manager_or_admin_override
from pricing import calculate_boat_pricing
from configuration import ConfigurationManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager_or_admin_override
def lambda_handler(event, context):
    """
    List all boat registrations for the authenticated team manager
    
    Returns:
        List of boat registration objects with enriched crew data
    """
    logger.info("List boat registrations request")
    
    # Get effective user ID (impersonated or real)
    team_manager_id = event['_effective_user_id']
    is_admin_override = event['_is_admin_override']
    
    # Audit logging for admin override
    if is_admin_override:
        admin_id = event['_admin_user_id']
        logger.info(f"Admin {admin_id} listing boat registrations for team manager {team_manager_id}")
    
    # Query DynamoDB for boat registrations
    db = get_db_client()
    
    boat_registrations = db.query_by_pk(
        pk=f'TEAM#{team_manager_id}',
        sk_prefix='BOAT#'
    )
    
    logger.info(f"Found {len(boat_registrations)} boat registrations for team manager {team_manager_id}")
    
    # Get crew members once for all pricing calculations
    crew_members = db.query_by_pk(
        pk=f'TEAM#{team_manager_id}',
        sk_prefix='CREW#'
    )
    
    # Get pricing configuration once
    config_manager = ConfigurationManager()
    pricing_config = config_manager.get_pricing_config()
    
    # Calculate pricing for each boat
    for boat in boat_registrations:
        if boat.get('seats') and any(seat.get('crew_member_id') for seat in boat['seats']):
            pricing = calculate_boat_pricing(boat, crew_members, pricing_config)
            boat['pricing'] = pricing
        else:
            boat['pricing'] = None
    
    # Return success response
    return success_response(
        data={'boat_registrations': boat_registrations}
    )
