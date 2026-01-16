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
        
        # Get race timing configuration
        race_timing_response = db.table.get_item(
            Key={'PK': 'CONFIG', 'SK': 'RACE_TIMING'}
        )
        race_timing = race_timing_response.get('Item', {})
        marathon_start_time = race_timing.get('marathon_start_time', '07:45')
        semi_marathon_start_time = race_timing.get('semi_marathon_start_time', '09:00')
        semi_marathon_interval_seconds = race_timing.get('semi_marathon_interval_seconds', 30)
        marathon_bow_start = race_timing.get('marathon_bow_start', 1)
        semi_marathon_bow_start = race_timing.get('semi_marathon_bow_start', 41)
        logger.info(f"Race timing - Marathon: {marathon_start_time}, Semi-Marathon: {semi_marathon_start_time}, Interval: {semi_marathon_interval_seconds}s, Bow starts: M={marathon_bow_start}, SM={semi_marathon_bow_start}")
        
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
        
        # Calculate payment balance for each team manager
        logger.info("Calculating payment balances for team managers")
        for user_id in team_manager_cache.keys():
            # Query payments for this team manager
            payments_response = db.table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':pk': f'TEAM#{user_id}',
                    ':sk_prefix': 'PAYMENT#'
                }
            )
            payments = payments_response.get('Items', [])
            
            # Calculate total paid
            total_paid = sum(float(p.get('amount', 0)) for p in payments)
            
            # Query unpaid boats (status='complete')
            unpaid_boats_response = db.table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
                FilterExpression='registration_status = :status',
                ExpressionAttributeValues={
                    ':pk': f'TEAM#{user_id}',
                    ':sk_prefix': 'BOAT#',
                    ':status': 'complete'
                }
            )
            unpaid_boats = unpaid_boats_response.get('Items', [])
            
            # Calculate outstanding balance
            outstanding_balance = 0.0
            for boat in unpaid_boats:
                # Use locked_pricing if available, otherwise pricing
                if boat.get('locked_pricing') and boat['locked_pricing'].get('total'):
                    outstanding_balance += float(boat['locked_pricing']['total'])
                elif boat.get('pricing') and boat['pricing'].get('total'):
                    outstanding_balance += float(boat['pricing']['total'])
            
            # Determine payment status
            if outstanding_balance == 0 and total_paid > 0:
                payment_status = 'Paid in Full'
            elif total_paid > 0 and outstanding_balance > 0:
                payment_status = 'Partial Payment'
            else:
                payment_status = 'No Payment'
            
            # Add payment fields to team manager cache
            team_manager_cache[user_id]['total_paid'] = round(total_paid, 2)
            team_manager_cache[user_id]['outstanding_balance'] = round(outstanding_balance, 2)
            team_manager_cache[user_id]['payment_status'] = payment_status
        
        logger.info(f"Calculated payment balances for {len(team_manager_cache)} team managers")
        
        # Simplify boat data for export (keep essential fields)
        simplified_boats = []
        for boat in boats:
            team_manager_id = boat.get('PK', '').replace('TEAM#', '')
            
            simplified_boat = {
                'boat_registration_id': boat.get('boat_registration_id'),
                'boat_number': boat.get('boat_number'),
                'race_id': boat.get('race_id'),
                'event_type': boat.get('event_type'),
                'boat_type': boat.get('boat_type'),
                'registration_status': boat.get('registration_status'),
                'forfait': boat.get('forfait', False),
                'team_manager_id': team_manager_id,
                'club_affiliation': team_manager_cache.get(team_manager_id, {}).get('club_affiliation', ''),
                'boat_club_display': boat.get('boat_club_display', ''),
                'club_list': boat.get('club_list', []),
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
                'gender_category': race.get('gender_category'),
                'display_order': race.get('display_order'),
                'short_name': race.get('short_name')
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
                'competition_date': competition_date,
                'marathon_start_time': marathon_start_time,
                'semi_marathon_start_time': semi_marathon_start_time,
                'semi_marathon_interval_seconds': semi_marathon_interval_seconds,
                'marathon_bow_start': marathon_bow_start,
                'semi_marathon_bow_start': semi_marathon_bow_start
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
