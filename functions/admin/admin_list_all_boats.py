"""
Lambda function for admin to list all boat registrations across all team managers
Admin only - retrieves all boats with filtering and sorting options
"""
import json
import logging
from decimal import Decimal

from responses import success_response, validation_error, handle_exceptions
from auth_utils import require_admin
from database import get_db_client
from pricing import calculate_boat_pricing
from configuration import ConfigurationManager

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
    List all boat registrations across all team managers with optional filtering
    
    Query parameters:
        team_manager_id: Filter by specific team manager (optional)
        club: Filter by club affiliation (optional)
        status: Filter by registration status (optional)
        search: Search by boat details (optional)
    
    Returns:
        List of all boat registrations with team manager information and pricing
    """
    logger.info("Admin list all boats request")
    
    # Get query parameters
    query_params = event.get('queryStringParameters') or {}
    filter_team_manager = query_params.get('team_manager_id')
    filter_club = query_params.get('club')
    filter_status = query_params.get('status')
    search_term = query_params.get('search', '').lower()
    
    # Query database for all boat registrations
    db = get_db_client()
    
    try:
        boats = []
        
        if filter_team_manager:
            # Query specific team manager's boats
            response = db.table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':pk': f'TEAM#{filter_team_manager}',
                    ':sk_prefix': 'BOAT#'
                }
            )
            boats = response.get('Items', [])
        else:
            # Scan all boats across all team managers
            response = db.table.scan(
                FilterExpression='begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':sk_prefix': 'BOAT#'
                }
            )
            
            boats = response.get('Items', [])
            
            # Handle pagination if needed
            while 'LastEvaluatedKey' in response:
                response = db.table.scan(
                    FilterExpression='begins_with(SK, :sk_prefix)',
                    ExpressionAttributeValues={
                        ':sk_prefix': 'BOAT#'
                    },
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                boats.extend(response.get('Items', []))
        
        # Get pricing configuration once
        config_manager = ConfigurationManager()
        pricing_config = config_manager.get_pricing_config()
        
        # Get team manager information and crew members for each boat
        team_manager_cache = {}
        crew_members_cache = {}
        
        for boat in boats:
            team_manager_id = boat.get('PK', '').replace('TEAM#', '')
            
            # Cache team manager info to avoid repeated queries
            if team_manager_id not in team_manager_cache:
                try:
                    # Team manager profiles are stored with USER# prefix
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
            
            # Cache crew members for pricing calculation
            if team_manager_id not in crew_members_cache:
                crew_response = db.table.query(
                    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
                    ExpressionAttributeValues={
                        ':pk': f'TEAM#{team_manager_id}',
                        ':sk_prefix': 'CREW#'
                    }
                )
                crew_members_cache[team_manager_id] = crew_response.get('Items', [])
            
            # Add team manager info to boat
            tm_info = team_manager_cache[team_manager_id]
            boat['team_manager_name'] = f"{tm_info.get('first_name', '')} {tm_info.get('last_name', '')}".strip()
            boat['team_manager_email'] = tm_info.get('email', '')
            boat['team_manager_club'] = tm_info.get('club_affiliation', '')
            boat['team_manager_id'] = team_manager_id
            
            # Calculate pricing for boat
            crew_members = crew_members_cache[team_manager_id]
            if boat.get('seats') and any(seat.get('crew_member_id') for seat in boat['seats']):
                pricing = calculate_boat_pricing(boat, crew_members, pricing_config)
                boat['pricing'] = pricing
            else:
                boat['pricing'] = None
        
        # Apply filters
        if filter_club:
            boats = [
                b for b in boats 
                if filter_club.lower() in b.get('team_manager_club', '').lower()
            ]
        
        if filter_status:
            boats = [
                b for b in boats
                if b.get('registration_status') == filter_status
            ]
        
        if search_term:
            boats = [
                b for b in boats
                if search_term in b.get('event_type', '').lower() or
                   search_term in b.get('boat_type', '').lower() or
                   search_term in b.get('team_manager_name', '').lower() or
                   search_term in b.get('boat_registration_id', '').lower()
            ]
        
        # Sort by team manager, then by event type, then by boat type
        boats.sort(key=lambda b: (
            b.get('team_manager_name', ''),
            b.get('event_type', ''),
            b.get('boat_type', '')
        ))
        
        logger.info(f"Retrieved {len(boats)} boats for admin")
        
        return success_response(
            data={
                'boats': json.loads(json.dumps(boats, default=decimal_to_float)),
                'count': len(boats)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to list boats: {str(e)}", exc_info=True)
        return validation_error(f'Failed to list boats: {str(e)}')
