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
from auth_utils import get_user_from_event, require_team_manager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager
def lambda_handler(event, context):
    """
    List all boat registrations for the authenticated team manager
    
    Returns:
        List of boat registration objects
    """
    logger.info("List boat registrations request")
    
    # Get authenticated user
    user = get_user_from_event(event)
    team_manager_id = user['user_id']
    
    # Query DynamoDB for boat registrations
    db = get_db_client()
    
    boat_registrations = db.query_by_pk(
        pk=f'TEAM#{team_manager_id}',
        sk_prefix='BOAT#'
    )
    
    logger.info(f"Found {len(boat_registrations)} boat registrations for team manager {team_manager_id}")
    
    # Return success response
    return success_response(
        data={'boat_registrations': boat_registrations}
    )
