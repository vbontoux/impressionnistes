"""
Lambda function to export all crew members as JSON
Admin only - returns raw JSON data for frontend formatting
"""
import json
import logging
from datetime import datetime

from responses import success_response, handle_exceptions, internal_error
from auth_utils import require_admin
from database import get_db_client, decimal_to_float

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Export all crew members as JSON
    
    Returns:
        JSON response with crew member data and team manager information
    """
    logger.info("Admin export crew members JSON request")
    
    db = get_db_client()
    
    try:
        # Scan all crew members across all team managers
        response = db.table.scan(
            FilterExpression='begins_with(SK, :sk_prefix)',
            ExpressionAttributeValues={
                ':sk_prefix': 'CREW#'
            }
        )
        
        crew_members = response.get('Items', [])
        
        # Handle pagination for large datasets
        while 'LastEvaluatedKey' in response:
            logger.info(f"Paginating crew members scan, current count: {len(crew_members)}")
            response = db.table.scan(
                FilterExpression='begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':sk_prefix': 'CREW#'
                },
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            crew_members.extend(response.get('Items', []))
        
        logger.info(f"Found {len(crew_members)} crew members")
        
        # Cache team manager lookups to minimize database queries
        team_manager_cache = {}
        
        for member in crew_members:
            team_manager_id = member.get('PK', '').replace('TEAM#', '')
            
            # Cache team manager info to avoid repeated queries
            if team_manager_id not in team_manager_cache:
                try:
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
            member['team_manager_id'] = team_manager_id
            member['team_manager_name'] = f"{tm_info.get('first_name', '')} {tm_info.get('last_name', '')}".strip() or 'Unknown'
            member['team_manager_email'] = tm_info.get('email', '')
            member['team_manager_club'] = tm_info.get('club_affiliation', '')
        
        # Sort by team manager name, then by crew member last name
        crew_members.sort(key=lambda m: (
            m.get('team_manager_name', ''),
            m.get('last_name', ''),
            m.get('first_name', '')
        ))
        
        # Convert Decimal types to float for JSON serialization
        crew_members = decimal_to_float(crew_members)
        
        logger.info(f"Successfully exported {len(crew_members)} crew members as JSON")
        
        # Return JSON response with metadata
        return success_response(data={
            'crew_members': crew_members,
            'total_count': len(crew_members),
            'exported_at': datetime.utcnow().isoformat() + 'Z'
        })
        
    except Exception as e:
        logger.error(f"Failed to export crew members: {str(e)}", exc_info=True)
        return internal_error(message='Failed to export crew members')
