"""
Lambda function to grant temporary access to a team manager
Admin only - allows team managers to bypass event phase restrictions temporarily
"""
import json
import logging
from datetime import datetime, timedelta

from responses import success_response, validation_error, handle_exceptions
from auth_utils import require_admin, get_user_from_event
from database import get_db_client
from configuration import ConfigurationManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Grant temporary access to a team manager
    
    Request body:
        {
            "user_id": "user-123",
            "hours": 48  # Optional, defaults to config value
        }
    
    Returns:
        Grant details with expiration timestamp
    """
    logger.info("Grant temporary access request")
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error('Invalid JSON in request body')
    
    # Validate required fields
    user_id = body.get('user_id')
    if not user_id:
        return validation_error('user_id is required')
    
    # Get admin user ID from event
    user_info = get_user_from_event(event)
    admin_user_id = user_info.get('user_id') if user_info else None
    if not admin_user_id:
        return validation_error('Unable to determine admin user ID')
    
    db = get_db_client()
    
    try:
        # Get system configuration for default hours
        config_manager = ConfigurationManager(db.table)
        config = config_manager.get_system_config()
        default_hours = config.get('temporary_editing_access_hours', 48)
        
        # Use provided hours or default
        hours = body.get('hours', default_hours)
        if not isinstance(hours, (int, float)) or hours <= 0:
            return validation_error('hours must be a positive number')
        
        # Calculate timestamps
        grant_timestamp = datetime.utcnow()
        expiration_timestamp = grant_timestamp + timedelta(hours=hours)
        
        # Create grant in DynamoDB
        grant_item = {
            'PK': 'TEMP_ACCESS',
            'SK': f'USER#{user_id}',
            'user_id': user_id,
            'grant_timestamp': grant_timestamp.isoformat() + 'Z',
            'expiration_timestamp': expiration_timestamp.isoformat() + 'Z',
            'granted_by_admin_id': admin_user_id,
            'status': 'active',
            'hours': hours,
            'notes': body.get('notes', '')
        }
        
        db.table.put_item(Item=grant_item)
        
        logger.info(f"Granted temporary access to user {user_id} for {hours} hours by admin {admin_user_id}")
        
        # Log the grant creation to audit log
        audit_item = {
            'PK': 'AUDIT#TEMP_ACCESS_GRANT',
            'SK': f'{grant_timestamp.isoformat()}Z#{user_id}',
            'user_id': user_id,
            'granted_by_admin_id': admin_user_id,
            'grant_timestamp': grant_timestamp.isoformat() + 'Z',
            'expiration_timestamp': expiration_timestamp.isoformat() + 'Z',
            'hours': hours,
            'action': 'grant_created',
            'notes': body.get('notes', '')
        }
        
        try:
            db.table.put_item(Item=audit_item)
        except Exception as e:
            logger.warning(f"Failed to write audit log: {str(e)}")
        
        return success_response(
            data={
                'user_id': user_id,
                'grant_timestamp': grant_timestamp.isoformat() + 'Z',
                'expiration_timestamp': expiration_timestamp.isoformat() + 'Z',
                'hours': hours,
                'granted_by_admin_id': admin_user_id,
                'status': 'active'
            },
            message='Temporary access granted successfully'
        )
        
    except Exception as e:
        logger.error(f"Failed to grant temporary access: {str(e)}", exc_info=True)
        return validation_error(f'Failed to grant temporary access: {str(e)}')
