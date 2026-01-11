"""
Lambda function for admin to list all team managers
Admin only - retrieves all users who have created boats or crew members
"""
import json
import logging
import os
from decimal import Decimal
import boto3

from responses import success_response, validation_error, handle_exceptions
from auth_utils import require_admin
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cognito = boto3.client('cognito-idp')


def decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    List all team managers
    
    A team manager is defined as a user who has created at least one boat registration
    or crew member. This endpoint is used by admins to select which team manager to
    impersonate.
    
    Returns:
        List of team managers with user_id, first_name, last_name, email, phone_number, club_affiliation, is_admin
    """
    logger.info("List team managers request")
    
    db = get_db_client()
    user_pool_id = os.environ.get('USER_POOL_ID')
    
    try:
        # Query all user profiles
        # User profiles are stored with PK=USER#{user_id}, SK=PROFILE
        response = db.table.scan(
            FilterExpression='begins_with(SK, :profile)',
            ExpressionAttributeValues={':profile': 'PROFILE'}
        )
        
        users = response.get('Items', [])
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            response = db.table.scan(
                FilterExpression='begins_with(SK, :profile)',
                ExpressionAttributeValues={':profile': 'PROFILE'},
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            users.extend(response.get('Items', []))
        
        logger.info(f"Found {len(users)} total users")
        
        # Get admin group members from Cognito
        admin_user_ids = set()
        try:
            admin_response = cognito.list_users_in_group(
                UserPoolId=user_pool_id,
                GroupName='admins'
            )
            admin_user_ids = {user['Username'] for user in admin_response.get('Users', [])}
            logger.info(f"Found {len(admin_user_ids)} admin users")
        except Exception as e:
            logger.warning(f"Failed to fetch admin group members: {str(e)}")
        
        # Filter for team managers (those who have created boats or crew)
        team_managers = []
        for user in users:
            user_id = user.get('user_id')
            if not user_id:
                continue
            
            # Check if user has any boats or crew members
            # Data is stored with PK=TEAM#{user_id}, SK=BOAT#... or SK=CREW#...
            has_boats = db.query_by_pk(
                pk=f'TEAM#{user_id}',
                sk_prefix='BOAT#',
                limit=1
            )
            
            has_crew = db.query_by_pk(
                pk=f'TEAM#{user_id}',
                sk_prefix='CREW#',
                limit=1
            )
            
            if has_boats or has_crew:
                team_managers.append({
                    'user_id': user_id,
                    'first_name': user.get('first_name', ''),
                    'last_name': user.get('last_name', ''),
                    'email': user.get('email', ''),
                    'phone_number': user.get('mobile_number', ''),
                    'club_affiliation': user.get('club_affiliation', ''),
                    'is_admin': user_id in admin_user_ids
                })
        
        # Sort by last name, then first name
        team_managers.sort(key=lambda x: (x['last_name'], x['first_name']))
        
        logger.info(f"Retrieved {len(team_managers)} team managers for admin")
        
        return success_response(
            data={
                'team_managers': json.loads(json.dumps(team_managers, default=decimal_to_float)),
                'count': len(team_managers)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to list team managers: {str(e)}", exc_info=True)
        return validation_error(f'Failed to list team managers: {str(e)}')
