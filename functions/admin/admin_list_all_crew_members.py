"""
Lambda function for admin to list all crew members across all team managers
Admin only - retrieves all crew members with filtering and sorting options
"""
import json
import logging
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


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    List all crew members across all team managers with optional filtering
    
    Query parameters:
        team_manager_id: Filter by specific team manager (optional)
        club: Filter by club affiliation (optional)
        search: Search by name or license number (optional)
    
    Returns:
        List of all crew members with team manager information
    """
    logger.info("Admin list all crew members request")
    
    # Get query parameters
    query_params = event.get('queryStringParameters') or {}
    filter_team_manager = query_params.get('team_manager_id')
    filter_club = query_params.get('club')
    search_term = query_params.get('search', '').lower()
    
    # Query database for all crew members
    db = get_db_client()
    
    try:
        crew_members = []
        
        if filter_team_manager:
            # Query specific team manager's crew members
            response = db.table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':pk': f'TEAM#{filter_team_manager}',
                    ':sk_prefix': 'CREW#'
                }
            )
            crew_members = response.get('Items', [])
        else:
            # Scan all crew members across all team managers
            response = db.table.scan(
                FilterExpression='begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':sk_prefix': 'CREW#'
                }
            )
            
            crew_members = response.get('Items', [])
            
            # Handle pagination if needed
            while 'LastEvaluatedKey' in response:
                response = db.table.scan(
                    FilterExpression='begins_with(SK, :sk_prefix)',
                    ExpressionAttributeValues={
                        ':sk_prefix': 'CREW#'
                    },
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                crew_members.extend(response.get('Items', []))
        
        # Get team manager information for each crew member
        # Note: Crew members include license verification fields if present:
        # - license_verification_status
        # - license_verification_date
        # - license_verification_details
        # - license_verified_by
        team_manager_cache = {}
        for crew in crew_members:
            team_manager_id = crew.get('PK', '').replace('TEAM#', '')
            
            # Cache team manager info to avoid repeated queries
            if team_manager_id not in team_manager_cache:
                try:
                    # Team manager profiles are stored with USER# prefix, not TEAM#
                    tm_response = db.table.get_item(
                        Key={
                            'PK': f'USER#{team_manager_id}',
                            'SK': 'PROFILE'
                        }
                    )
                    team_manager_cache[team_manager_id] = tm_response.get('Item', {})
                except Exception as e:
                    logger.warning(f"Could not fetch team manager {team_manager_id}: {str(e)}")
                    team_manager_cache[team_manager_id] = {}
            
            # Add team manager info to crew member
            tm_info = team_manager_cache[team_manager_id]
            crew['team_manager_name'] = f"{tm_info.get('first_name', '')} {tm_info.get('last_name', '')}".strip()
            crew['team_manager_email'] = tm_info.get('email', '')
            crew['team_manager_club'] = tm_info.get('club_affiliation', '')
            crew['team_manager_id'] = team_manager_id
        
        # Apply filters
        if filter_club:
            crew_members = [
                c for c in crew_members 
                if filter_club.lower() in c.get('club_affiliation', '').lower() or
                   filter_club.lower() in c.get('team_manager_club', '').lower()
            ]
        
        if search_term:
            crew_members = [
                c for c in crew_members
                if search_term in c.get('first_name', '').lower() or
                   search_term in c.get('last_name', '').lower() or
                   search_term in c.get('license_number', '').lower() or
                   search_term in c.get('team_manager_name', '').lower()
            ]
        
        # Sort by team manager, then by last name
        crew_members.sort(key=lambda c: (
            c.get('team_manager_name', ''),
            c.get('last_name', ''),
            c.get('first_name', '')
        ))
        
        logger.info(f"Retrieved {len(crew_members)} crew members for admin")
        
        return success_response(
            data={
                'crew_members': json.loads(json.dumps(crew_members, default=decimal_to_float)),
                'count': len(crew_members)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to list crew members: {str(e)}", exc_info=True)
        return validation_error(f'Failed to list crew members: {str(e)}')
