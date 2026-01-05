"""
Lambda function for listing crew members
Team managers can view all their crew members
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

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager_or_admin_override
def lambda_handler(event, context):
    """
    List all crew members for the authenticated team manager
    
    Returns:
        List of crew member objects
    """
    logger.info("List crew members request")
    
    # Get effective user ID (impersonated or real)
    team_manager_id = event['_effective_user_id']
    is_admin_override = event['_is_admin_override']
    
    # Audit logging for admin override
    if is_admin_override:
        admin_id = event['_admin_user_id']
        logger.info(f"Admin {admin_id} listing crew members for team manager {team_manager_id}")
    
    # Query DynamoDB for crew members
    db = get_db_client()
    
    crew_members = db.query_by_pk(
        pk=f'TEAM#{team_manager_id}',
        sk_prefix='CREW#'
    )
    
    logger.info(f"Found {len(crew_members)} crew members for team manager {team_manager_id}")
    
    # Return success response
    return success_response(
        data={'crew_members': crew_members}
    )
