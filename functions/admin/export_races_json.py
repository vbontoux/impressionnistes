"""
Lambda function to export races with all related data as JSON
Admin only - returns comprehensive JSON data for CrewTimer and other exports
"""
import json
import logging
from datetime import datetime

from responses import success_response, handle_exceptions, internal_error
from auth_utils import require_admin
from database import get_db_client, decimal_to_float
from race_eligibility import calculate_age

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Export all races, boats, crew members, and team managers as JSON
    
    Returns:
        JSON response with comprehensive race data including:
        - System configuration (competition date)
        - All races
        - All boats (regardless of status)
        - All crew members
        - All team managers
    """
    logger.info("Admin export races JSON request")
    
    db = get_db_client()
    
    try:
        # Get system configuration (competition date)
        config_response = db.table.get_item(
            Key={'PK': 'CONFIG', 'SK': 'SYSTEM'}
        )
        config = config_response.get('Item', {})
        competition_date = config.get('competition_date', '2025-05-01')
        logger.info(f"Competition date: {competition_date}")
        
        # Get all races
        races_response = db.table.query(
            KeyConditionExpression='PK = :pk',
            ExpressionAttributeValues={
                ':pk': 'RACE'
            }
        )
        races = races_response.get('Items', [])
        logger.info(f"Found {len(races)} races")
        
        # Get all boat registrations (include ALL boats regardless of status)
        boats_response = db.table.scan(
            FilterExpression='begins_with(SK, :sk_prefix)',
            ExpressionAttributeValues={
                ':sk_prefix': 'BOAT#'
            }
        )
        boats = boats_response.get('Items', [])
        
        # Handle pagination for boats
        while 'LastEvaluatedKey' in boats_response:
            logger.info(f"Paginating boats scan, current count: {len(boats)}")
            boats_response = db.table.scan(
                FilterExpression='begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':sk_prefix': 'BOAT#'
                },
                ExclusiveStartKey=boats_response['LastEvaluatedKey']
            )
            boats.extend(boats_response.get('Items', []))
        
        logger.info(f"Found {len(boats)} boat registrations (all statuses)")
        
        # Get all crew members
        crew_response = db.table.scan(
            FilterExpression='begins_with(SK, :sk_prefix)',
            ExpressionAttributeValues={
                ':sk_prefix': 'CREW#'
            }
        )
        crew_members = crew_response.get('Items', [])
        
        # Handle pagination for crew members
        while 'LastEvaluatedKey' in crew_response:
            logger.info(f"Paginating crew members scan, current count: {len(crew_members)}")
            crew_response = db.table.scan(
                FilterExpression='begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':sk_prefix': 'CREW#'
                },
                ExclusiveStartKey=crew_response['LastEvaluatedKey']
            )
            crew_members.extend(crew_response.get('Items', []))
        
        logger.info(f"Found {len(crew_members)} crew members")
        
        # Get all team managers (users with PROFILE)
        users_response = db.table.scan(
            FilterExpression='SK = :sk',
            ExpressionAttributeValues={
                ':sk': 'PROFILE'
            }
        )
        team_managers = users_response.get('Items', [])
        
        # Handle pagination for team managers
        while 'LastEvaluatedKey' in users_response:
            logger.info(f"Paginating team managers scan, current count: {len(team_managers)}")
            users_response = db.table.scan(
                FilterExpression='SK = :sk',
                ExpressionAttributeValues={
                    ':sk': 'PROFILE'
                },
                ExclusiveStartKey=users_response['LastEvaluatedKey']
            )
            team_managers.extend(users_response.get('Items', []))
        
        logger.info(f"Found {len(team_managers)} team managers")
        
        # Cache team manager lookups for performance
        team_manager_cache = {}
        for tm in team_managers:
            user_id = tm.get('PK', '').replace('USER#', '')
            team_manager_cache[user_id] = {
                'user_id': user_id,
                'club_affiliation': tm.get('club_affiliation', ''),
                'email': tm.get('email', ''),
                'first_name': tm.get('first_name', ''),
                'last_name': tm.get('last_name', '')
            }
        
        # Simplify boat data for export (keep essential fields)
        simplified_boats = []
        for boat in boats:
            team_manager_id = boat.get('PK', '').replace('TEAM#', '')
            
            simplified_boat = {
                'boat_registration_id': boat.get('boat_registration_id'),
                'race_id': boat.get('race_id'),
                'event_type': boat.get('event_type'),
                'boat_type': boat.get('boat_type'),
                'registration_status': boat.get('registration_status'),
                'forfait': boat.get('forfait', False),
                'team_manager_id': team_manager_id,
                'club_affiliation': team_manager_cache.get(team_manager_id, {}).get('club_affiliation', ''),
                'seats': boat.get('seats', []),
                'crew_composition': boat.get('crew_composition', {}),
                'is_multi_club_crew': boat.get('is_multi_club_crew', False),
                'created_at': boat.get('created_at'),
                'updated_at': boat.get('updated_at'),
                'paid_at': boat.get('paid_at')
            }
            simplified_boats.append(simplified_boat)
        
        # Simplify crew member data for export
        simplified_crew = []
        for crew in crew_members:
            # Calculate age using centralized function
            age = None
            if crew.get('date_of_birth'):
                try:
                    age = calculate_age(crew['date_of_birth'])
                except (ValueError, Exception) as e:
                    logger.warning(f"Could not calculate age for crew member {crew.get('crew_member_id')}: {str(e)}")
            
            simplified_crew.append({
                'crew_member_id': crew.get('crew_member_id'),
                'first_name': crew.get('first_name'),
                'last_name': crew.get('last_name'),
                'date_of_birth': crew.get('date_of_birth'),
                'gender': crew.get('gender'),
                'license_number': crew.get('license_number'),
                'club_affiliation': crew.get('club_affiliation'),
                'age': age
            })
        
        # Simplify race data for export
        simplified_races = []
        for race in races:
            simplified_races.append({
                'race_id': race.get('race_id'),
                'name': race.get('name'),
                'distance': race.get('distance'),
                'event_type': race.get('event_type'),
                'boat_type': race.get('boat_type'),
                'age_category': race.get('age_category'),
                'gender_category': race.get('gender_category')
            })
        
        # Convert Decimal types to float for JSON serialization
        simplified_boats = decimal_to_float(simplified_boats)
        simplified_crew = decimal_to_float(simplified_crew)
        simplified_races = decimal_to_float(simplified_races)
        team_managers_list = decimal_to_float(list(team_manager_cache.values()))
        
        logger.info(f"Successfully exported races data as JSON")
        
        # Return comprehensive JSON response
        return success_response(data={
            'config': {
                'competition_date': competition_date
            },
            'races': simplified_races,
            'boats': simplified_boats,
            'crew_members': simplified_crew,
            'team_managers': team_managers_list,
            'total_races': len(simplified_races),
            'total_boats': len(simplified_boats),
            'total_crew_members': len(simplified_crew),
            'exported_at': datetime.utcnow().isoformat() + 'Z'
        })
        
    except Exception as e:
        logger.error(f"Failed to export races data: {str(e)}", exc_info=True)
        return internal_error(message='Failed to export races data')
