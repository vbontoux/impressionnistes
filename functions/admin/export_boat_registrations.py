"""
Lambda function to export all boat registrations to CSV format
Admin only - exports boat registration data for all team managers with race names
"""
import json
import logging
import csv
import io
from datetime import datetime
from decimal import Decimal

from responses import handle_exceptions
from auth_utils import require_admin
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    return obj


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Export all boat registrations to CSV format with race names
    
    Returns:
        CSV file with all boat registration data including race names
    """
    logger.info("Admin export boat registrations request")
    
    # Query database for all boat registrations
    db = get_db_client()
    
    try:
        # Scan all boat registrations across all team managers
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
        
        # Get all races to map race_id to race name
        races_response = db.table.query(
            KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
            ExpressionAttributeValues={
                ':pk': 'CONFIG',
                ':sk_prefix': 'RACE#'
            }
        )
        races = races_response.get('Items', [])
        
        # Create race lookup dictionary
        race_lookup = {race['race_id']: race.get('name', '') for race in races}
        
        # Get team manager information for each boat
        team_manager_cache = {}
        
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
            boat['team_manager_name'] = f"{tm_info.get('first_name', '')} {tm_info.get('last_name', '')}".strip()
            boat['team_manager_email'] = tm_info.get('email', '')
            boat['team_manager_club'] = tm_info.get('club_affiliation', '')
            
            # Add race name from lookup
            race_id = boat.get('race_id')
            boat['race_name'] = race_lookup.get(race_id, '') if race_id else ''
            
            # Calculate filled seats
            seats = boat.get('seats', [])
            filled_seats = sum(1 for seat in seats if seat.get('crew_member_id'))
            total_seats = len(seats)
            boat['filled_seats'] = f"{filled_seats}/{total_seats}"
            
            # Get crew composition
            crew_comp = boat.get('crew_composition', {})
            boat['gender_category'] = crew_comp.get('gender_category', '')
            boat['avg_age'] = decimal_to_float(crew_comp.get('avg_age', ''))
        
        # Sort by team manager, then by event type, then by boat type
        boats.sort(key=lambda b: (
            b.get('team_manager_name', ''),
            b.get('event_type', ''),
            b.get('boat_type', '')
        ))
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Boat Registration ID',
            'Event Type',
            'Boat Type',
            'Race Name',
            'Registration Status',
            'Filled Seats',
            'Gender Category',
            'Average Age',
            'Is Multi-Club Crew',
            'Team Manager Name',
            'Team Manager Email',
            'Team Manager Club',
            'Created At',
            'Updated At',
            'Paid At'
        ])
        
        # Write data rows
        for boat in boats:
            writer.writerow([
                boat.get('boat_registration_id', ''),
                boat.get('event_type', ''),
                boat.get('boat_type', ''),
                boat.get('race_name', ''),
                boat.get('registration_status', ''),
                boat.get('filled_seats', ''),
                boat.get('gender_category', ''),
                boat.get('avg_age', ''),
                'Yes' if boat.get('is_multi_club_crew') else 'No',
                boat.get('team_manager_name', ''),
                boat.get('team_manager_email', ''),
                boat.get('team_manager_club', ''),
                boat.get('created_at', ''),
                boat.get('updated_at', ''),
                boat.get('paid_at', '')
            ])
        
        # Get CSV content
        csv_content = output.getvalue()
        output.close()
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        filename = f'boat_registrations_export_{timestamp}.csv'
        
        logger.info(f"Exported {len(boats)} boat registrations to CSV")
        
        # Return CSV as binary response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': csv_content,
            'isBase64Encoded': False
        }
        
    except Exception as e:
        logger.error(f"Failed to export boat registrations: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': {
                    'message': f'Failed to export boat registrations: {str(e)}'
                }
            })
        }
