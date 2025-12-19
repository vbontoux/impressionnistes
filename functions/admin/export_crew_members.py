"""
Lambda function to export all crew members to CSV format
Admin only - exports crew member data for all team managers
"""
import json
import logging
import csv
import io
import base64
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
    Export all crew members to CSV format
    
    Returns:
        CSV file with all crew member data
    """
    logger.info("Admin export crew members request")
    
    # Query database for all crew members
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
            member['team_manager_name'] = f"{tm_info.get('first_name', '')} {tm_info.get('last_name', '')}".strip()
            member['team_manager_email'] = tm_info.get('email', '')
            member['team_manager_club'] = tm_info.get('club_affiliation', '')
        
        # Sort by team manager, then by last name
        crew_members.sort(key=lambda m: (
            m.get('team_manager_name', ''),
            m.get('last_name', ''),
            m.get('first_name', '')
        ))
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Crew Member ID',
            'First Name',
            'Last Name',
            'Gender',
            'Date of Birth',
            'Age',
            'License Number',
            'Club Affiliation',
            'Team Manager Name',
            'Team Manager Email',
            'Team Manager Club',
            'Created At',
            'Updated At'
        ])
        
        # Write data rows
        for member in crew_members:
            writer.writerow([
                member.get('crew_member_id', ''),
                member.get('first_name', ''),
                member.get('last_name', ''),
                member.get('gender', ''),
                member.get('date_of_birth', ''),
                decimal_to_float(member.get('age', '')),
                member.get('license_number', ''),
                member.get('club_affiliation', ''),
                member.get('team_manager_name', ''),
                member.get('team_manager_email', ''),
                member.get('team_manager_club', ''),
                member.get('created_at', ''),
                member.get('updated_at', '')
            ])
        
        # Get CSV content
        csv_content = output.getvalue()
        output.close()
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        filename = f'crew_members_export_{timestamp}.csv'
        
        logger.info(f"Exported {len(crew_members)} crew members to CSV")
        
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
        logger.error(f"Failed to export crew members: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': {
                    'message': f'Failed to export crew members: {str(e)}'
                }
            })
        }
