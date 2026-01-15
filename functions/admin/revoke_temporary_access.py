"""
Lambda function to revoke temporary access from a team manager
Admin only - immediately revokes an active temporary access grant
"""
import json
import logging
from datetime import datetime

from responses import success_response, validation_error, not_found_error, handle_exceptions
from auth_utils import require_admin, get_user_from_event
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Revoke temporary access from a team manager
    
    Request body:
        {
            "user_id": "user-123"
        }
    
    Returns:
        Confirmation of revocation
    """
    logger.info("Revoke temporary access request")
    
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
        # Get the existing grant
        response = db.table.get_item(
            Key={
                'PK': 'TEMP_ACCESS',
                'SK': f'USER#{user_id}'
            }
        )
        
        grant = response.get('Item')
        if not grant:
            return not_found_error(f'No temporary access grant found for user {user_id}')
        
        # Check if already revoked or expired
        if grant.get('status') == 'revoked':
            return validation_error('Grant is already revoked')
        
        if grant.get('status') == 'expired':
            return validation_error('Grant has already expired')
        
        # Update grant status to revoked
        revoked_at = datetime.utcnow()
        
        db.table.update_item(
            Key={
                'PK': 'TEMP_ACCESS',
                'SK': f'USER#{user_id}'
            },
            UpdateExpression='SET #status = :status, revoked_at = :revoked_at, revoked_by_admin_id = :admin_id',
            ExpressionAttributeNames={
                '#status': 'status'
            },
            ExpressionAttributeValues={
                ':status': 'revoked',
                ':revoked_at': revoked_at.isoformat() + 'Z',
                ':admin_id': admin_user_id
            }
        )
        
        logger.info(f"Revoked temporary access for user {user_id} by admin {admin_user_id}")
        
        # Log the revocation to audit log
        audit_item = {
            'PK': 'AUDIT#TEMP_ACCESS_REVOKE',
            'SK': f'{revoked_at.isoformat()}Z#{user_id}',
            'user_id': user_id,
            'revoked_by_admin_id': admin_user_id,
            'revoked_at': revoked_at.isoformat() + 'Z',
            'action': 'grant_revoked',
            'original_grant_timestamp': grant.get('grant_timestamp'),
            'original_expiration_timestamp': grant.get('expiration_timestamp')
        }
        
        try:
            db.table.put_item(Item=audit_item)
        except Exception as e:
            logger.warning(f"Failed to write audit log: {str(e)}")
        
        return success_response(
            data={
                'user_id': user_id,
                'status': 'revoked',
                'revoked_at': revoked_at.isoformat() + 'Z',
                'revoked_by_admin_id': admin_user_id
            },
            message='Temporary access revoked successfully'
        )
        
    except Exception as e:
        logger.error(f"Failed to revoke temporary access: {str(e)}", exc_info=True)
        return validation_error(f'Failed to revoke temporary access: {str(e)}')
