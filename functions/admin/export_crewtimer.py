"""
Lambda function to export data in CrewTimer.com format
Admin only - exports races and boats for timing management
"""
import json
import logging
from datetime import datetime

from responses import success_response, handle_exceptions
from auth_utils import require_admin
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_boat_type_display(boat_type):
    """Convert boat type to display format"""
    type_map = {
        'skiff': '1X',
        '4-': '4-',
        '4+': '4+',
        '4x-': '4X-',
        '4x+': '4X+',
        '8+': '8+',
        '8x+': '8X+'
    }
    return type_map.get(boat_type, boat_type)


def format_semi_marathon_race_name(race):
    """Format semi-marathon race name as: [boat_type] [Y if yolette] [age_category] [gender_category]
    
    Args:
        race: Race dictionary with boat_type, name, age_category, gender_category
    
    Returns:
        Formatted race name string
    """
    boat_type = get_boat_type_display(race.get('boat_type', ''))
    
    # Check if "yolette" is in the race name (case insensitive)
    race_name = race.get('name', '').lower()
    yolette_marker = 'Y' if 'yolette' in race_name else ''
    
    # Get age category (j16, j18, senior, master)
    age_category = race.get('age_category', '').upper()
    
    # Get gender category (men, women, mixed)
    gender_category = race.get('gender_category', '')
    gender_map = {
        'men': 'MAN',
        'women': 'WOMAN',
        'mixed': 'MIXED'
    }
    gender_display = gender_map.get(gender_category, gender_category.upper())
    
    # Compose the name - filter out empty strings and join with single space
    parts = [boat_type, yolette_marker, age_category, gender_display]
    return ' '.join(part for part in parts if part).strip()


def calculate_average_age(crew_members, competition_date):
    """Calculate average age of crew members
    
    Note: Includes all crew members (including coxswains if present)
    because crew members don't have role fields in the database.
    """
    if not crew_members:
        return 0
    
    try:
        comp_year = int(competition_date.split('-')[0])
        ages = []
        
        for member in crew_members:
            dob = member.get('date_of_birth')
            if dob:
                birth_year = int(dob.split('-')[0])
                age = comp_year - birth_year
                ages.append(age)
        
        if ages:
            return round(sum(ages) / len(ages))
        return 0
    except Exception as e:
        logger.error(f"Error calculating average age: {str(e)}")
        return 0


def get_stroke_seat_name(seats, crew_members_dict):
    """Get the last name of the stroke seat rower
    
    The stroke seat is the highest position rower (not cox).
    For example, in a 4-, the stroke is position 4.
    
    Args:
        seats: List of seat dictionaries with position, type, crew_member_id
        crew_members_dict: Dictionary mapping crew_member_id to crew member data
    
    Returns:
        Last name of stroke seat rower, or empty string if not found
    """
    if not seats or not crew_members_dict:
        return ""
    
    # Find all rower seats (exclude cox)
    rower_seats = [s for s in seats if s.get('type') == 'rower' and s.get('crew_member_id')]
    
    if not rower_seats:
        return ""
    
    # Find the highest position rower (stroke seat)
    stroke_seat = max(rower_seats, key=lambda s: s.get('position', 0))
    crew_member_id = stroke_seat.get('crew_member_id')
    
    if not crew_member_id:
        return ""
    
    # Get crew member data
    crew_member = crew_members_dict.get(crew_member_id)
    if not crew_member:
        return ""
    
    return crew_member.get('last_name', '')


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Export races and boats in CrewTimer format
    
    Returns:
        Excel file with CrewTimer format
    """
    logger.info("CrewTimer export request")
    
    db = get_db_client()
    
    try:
        # Get competition date from config
        config_response = db.table.get_item(
            Key={'PK': 'CONFIG', 'SK': 'SYSTEM'}
        )
        config = config_response.get('Item', {})
        competition_date = config.get('competition_date', '2025-05-01')
        
        # Get all races
        races_response = db.table.query(
            KeyConditionExpression='PK = :pk',
            ExpressionAttributeValues={
                ':pk': 'RACE'
            }
        )
        races = races_response.get('Items', [])
        logger.info(f"Found {len(races)} races")
        
        # Get all boat registrations that are complete, paid, or free (not forfait)
        boats_response = db.table.scan(
            FilterExpression='begins_with(SK, :sk_prefix) AND (registration_status = :complete OR registration_status = :paid OR registration_status = :free) AND (attribute_not_exists(forfait) OR forfait = :not_forfait)',
            ExpressionAttributeValues={
                ':sk_prefix': 'BOAT#',
                ':complete': 'complete',
                ':paid': 'paid',
                ':free': 'free',
                ':not_forfait': False
            }
        )
        boats = boats_response.get('Items', [])
        logger.info(f"Found {len(boats)} eligible boats")
        
        # Get all crew members and create a lookup dictionary
        crew_response = db.table.scan(
            FilterExpression='begins_with(SK, :sk_prefix)',
            ExpressionAttributeValues={
                ':sk_prefix': 'CREW#'
            }
        )
        all_crew = crew_response.get('Items', [])
        
        # Create crew member lookup dictionary by crew_member_id
        crew_members_dict = {crew['crew_member_id']: crew for crew in all_crew}
        
        logger.info(f"Found {len(all_crew)} crew members")
        
        # Get all team managers for club names
        users_response = db.table.scan(
            FilterExpression='SK = :sk',
            ExpressionAttributeValues={
                ':sk': 'PROFILE'
            }
        )
        users = users_response.get('Items', [])
        users_by_id = {user['PK']: user for user in users}
        logger.info(f"Found {len(users)} team managers. Sample keys: {list(users_by_id.keys())[:3] if users_by_id else 'none'}")
        
        # Group boats by race
        boats_by_race = {}
        for boat in boats:
            race_id = boat.get('race_id')
            if race_id:
                if race_id not in boats_by_race:
                    boats_by_race[race_id] = []
                boats_by_race[race_id].append(boat)
        
        logger.info(f"Boats grouped by race: {[(race_id, len(boats)) for race_id, boats in boats_by_race.items()]}")
        
        # Sort races: marathon first, then semi-marathon
        marathon_races = [r for r in races if r.get('distance') == 42]
        semi_marathon_races = [r for r in races if r.get('distance') == 21]
        sorted_races = marathon_races + semi_marathon_races
        
        # Build CrewTimer data
        crewtimer_data = []
        event_num = 0  # Will increment when we start a new race
        bow_num = 1  # Global bow number across ALL races
        
        for race in sorted_races:
            race_id = race.get('race_id')
            race_boats = boats_by_race.get(race_id, [])
            
            if not race_boats:
                continue  # Skip races with no boats
            
            # Increment event number for this race (same for all boats in this race)
            event_num += 1
            
            # Format race name based on distance
            distance = race.get('distance', 0)
            if distance == 21:
                # Semi-marathon: use formatted name
                race_name = format_semi_marathon_race_name(race)
            else:
                # Marathon: use original name
                race_name = race.get('name', '')
            
            logger.info(f"Processing race {race_id} ({race_name}) with {len(race_boats)} boats")
            for boat in race_boats:
                # Get team manager and club
                # Boat PK is TEAM#user_id, but users_by_id has USER#user_id
                team_manager_pk = boat.get('PK')
                user_pk = team_manager_pk.replace('TEAM#', 'USER#') if team_manager_pk else None
                team_manager = users_by_id.get(user_pk, {})
                if not team_manager:
                    logger.warning(f"Team manager not found for boat: {boat.get('boat_registration_id')}, PK: {team_manager_pk}, converted to: {user_pk}")
                club_name = team_manager.get('club_affiliation', 'Unknown')
                
                # Get crew members for this boat from seats
                seats = boat.get('seats', [])
                crew_members = []
                for seat in seats:
                    crew_member_id = seat.get('crew_member_id')
                    if crew_member_id and crew_member_id in crew_members_dict:
                        crew_members.append(crew_members_dict[crew_member_id])
                
                # Calculate average age
                avg_age = calculate_average_age(crew_members, competition_date)
                
                # Get stroke seat name
                stroke_name = get_stroke_seat_name(seats, crew_members_dict)
                
                # Build row
                row = {
                    'Event Time': '',  # Empty for now as specified
                    'Event Num': event_num,
                    'Event': race_name,
                    'Event Abbrev': race_name,  # Use full name instead of abbreviation
                    'Crew': club_name,
                    'Crew Abbrev': club_name,  # Use full name instead of abbreviation
                    'Stroke': stroke_name,
                    'Bow': bow_num,  # Incremental number for each boat in race
                    'Race Info': 'Head',  # Always "Head" as specified
                    'Status': '',  # Empty as specified
                    'Age': avg_age
                }
                
                crewtimer_data.append(row)
                logger.info(f"Added boat {boat.get('boat_registration_id')} to race {race_id}: Event Num={event_num}, Bow={bow_num}, Stroke={stroke_name}")
                bow_num += 1  # Increment bow number for next boat (global across all races)
        
        logger.info(f"Generated {len(crewtimer_data)} CrewTimer entries")
        
        # Return JSON data - frontend will generate the Excel file
        return success_response(data={
            'rows': crewtimer_data,
            'total_races': len(set(row['Event'] for row in crewtimer_data)),
            'total_boats': len(crewtimer_data)
        })
        
    except Exception as e:
        logger.error(f"Failed to export CrewTimer data: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': {
                    'code': 'EXPORT_ERROR',
                    'message': 'Failed to export CrewTimer data'
                }
            })
        }

