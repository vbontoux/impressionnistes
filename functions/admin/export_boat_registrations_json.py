"""
Lambda function to export all boat registrations as JSON
Admin only - returns raw JSON data for frontend formatting
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
    Export all boat registrations as JSON with race names and team manager information
    
    Returns:
        JSON response with boat registration data including all boats regardless of status
    """
    logger.info("Admin export boat registrations JSON request")
    
    db = get_db_client()
    
    try:
        # Scan all boat registrations across all team managers
        # Include ALL boats regardless of status (no filtering)
        response = db.table.scan(
            FilterExpression='begins_with(SK, :sk_prefix)',
            ExpressionAttributeValues={
                ':sk_prefix': 'BOAT#'
            }
        )
        
        boats = response.get('Items', [])
        
        # Handle pagination for large datasets
        while 'LastEvaluatedKey' in response:
            logger.info(f"Paginating boat registrations scan, current count: {len(boats)}")
            response = db.table.scan(
                FilterExpression='begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':sk_prefix': 'BOAT#'
                },
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            boats.extend(response.get('Items', []))
        
        logger.info(f"Found {len(boats)} boat registrations")
        
        # Get all races to map race_id to race name
        races_response = db.table.query(
            KeyConditionExpression='PK = :pk',
            ExpressionAttributeValues={
                ':pk': 'RACE'
            }
        )
        races = races_response.get('Items', [])
        
        # Create race lookup dictionary
        race_lookup = {race['race_id']: race.get('name', '') for race in races}
        logger.info(f"Loaded {len(race_lookup)} races for lookup")
        
        # Cache team manager and crew member lookups to minimize database queries
        team_manager_cache = {}
        crew_member_cache = {}
        
        for boat in boats:
            team_manager_id = boat.get('PK', '').replace('TEAM#', '')
            
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
            
            # Add team manager info to boat
            tm_info = team_manager_cache[team_manager_id]
            boat['team_manager_id'] = team_manager_id
            boat['team_manager_name'] = f"{tm_info.get('first_name', '')} {tm_info.get('last_name', '')}".strip() or 'Unknown'
            boat['team_manager_email'] = tm_info.get('email', '')
            boat['team_manager_club'] = tm_info.get('club_affiliation', '')
            
            # Fetch crew member details for each seat
            seats = boat.get('seats', [])
            crew_details = []
            
            for seat in seats:
                crew_member_id = seat.get('crew_member_id')
                
                if crew_member_id:
                    # Cache crew member info to avoid repeated queries
                    if crew_member_id not in crew_member_cache:
                        try:
                            crew_response = db.table.get_item(
                                Key={
                                    'PK': f'TEAM#{team_manager_id}',
                                    'SK': f'CREW#{crew_member_id}'
                                }
                            )
                            crew_member_cache[crew_member_id] = crew_response.get('Item', {})
                        except Exception as e:
                            logger.warning(f"Could not fetch crew member {crew_member_id}: {str(e)}")
                            crew_member_cache[crew_member_id] = {}
                    
                    crew_info = crew_member_cache[crew_member_id]
                    
                    # Calculate age using centralized function
                    age = None
                    if crew_info.get('date_of_birth'):
                        try:
                            age = calculate_age(crew_info['date_of_birth'])
                        except (ValueError, Exception) as e:
                            logger.warning(f"Could not calculate age for crew member {crew_member_id}: {str(e)}")
                    
                    crew_details.append({
                        'position': seat.get('position'),
                        'type': seat.get('type'),
                        'crew_member_id': crew_member_id,
                        'first_name': crew_info.get('first_name', ''),
                        'last_name': crew_info.get('last_name', ''),
                        'gender': crew_info.get('gender', ''),
                        'date_of_birth': crew_info.get('date_of_birth', ''),
                        'age': age,
                        'license_number': crew_info.get('license_number', ''),
                        'club_affiliation': crew_info.get('club_affiliation', '')
                    })
                else:
                    # Empty seat
                    crew_details.append({
                        'position': seat.get('position'),
                        'type': seat.get('type'),
                        'crew_member_id': None,
                        'first_name': '',
                        'last_name': '',
                        'gender': '',
                        'date_of_birth': '',
                        'age': '',
                        'license_number': '',
                        'club_affiliation': ''
                    })
            
            # Add crew details to boat
            boat['crew_details'] = crew_details
            
            # Ensure club fields are present (for backward compatibility during migration)
            if 'boat_club_display' not in boat:
                boat['boat_club_display'] = boat.get('team_manager_club', '')
            if 'club_list' not in boat:
                boat['club_list'] = [boat.get('team_manager_club', '')] if boat.get('team_manager_club') else []
            
            # Ensure boat_number is present (for backward compatibility during migration)
            if 'boat_number' not in boat:
                boat['boat_number'] = None
            
            # Add race name from lookup
            race_id = boat.get('race_id')
            boat['race_name'] = race_lookup.get(race_id, '') if race_id else ''
            
            # Calculate filled seats
            seats = boat.get('seats', [])
            filled_seats = sum(1 for seat in seats if seat.get('crew_member_id'))
            total_seats = len(seats)
            
            # Add crew composition details
            crew_comp = boat.get('crew_composition', {})
            if not crew_comp:
                crew_comp = {}
            
            # Ensure crew_composition has filled_seats and total_seats
            crew_comp['filled_seats'] = filled_seats
            crew_comp['total_seats'] = total_seats
            boat['crew_composition'] = crew_comp
        
        # Sort by team manager name, then by event type, then by boat type
        boats.sort(key=lambda b: (
            b.get('team_manager_name', ''),
            b.get('event_type', ''),
            b.get('boat_type', '')
        ))
        
        # Convert Decimal types to float for JSON serialization
        boats = decimal_to_float(boats)
        
        logger.info(f"Successfully exported {len(boats)} boat registrations as JSON")
        
        # Return JSON response with metadata
        return success_response(data={
            'boats': boats,
            'total_count': len(boats),
            'exported_at': datetime.utcnow().isoformat() + 'Z'
        })
        
    except Exception as e:
        logger.error(f"Failed to export boat registrations: {str(e)}", exc_info=True)
        return internal_error(message='Failed to export boat registrations')
