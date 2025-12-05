"""
Lambda function to get admin dashboard statistics
Admin only - retrieves counts for crew members, boat registrations, payments, and rental boats
"""
import json
import logging

from responses import success_response, handle_exceptions
from auth_utils import require_admin
from database import get_db_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    Get admin dashboard statistics
    
    Returns:
        Statistics object with counts
    """
    logger.info("Get admin stats request")
    
    db = get_db_client()
    
    try:
        # Count total crew members
        crew_response = db.table.scan(
            FilterExpression='begins_with(SK, :sk_prefix)',
            ExpressionAttributeValues={
                ':sk_prefix': 'CREW#'
            },
            Select='COUNT'
        )
        total_crew_members = crew_response.get('Count', 0)
        
        # Count total boat registrations (stored as TEAM#xxx / BOAT#xxx)
        boat_response = db.table.scan(
            FilterExpression='begins_with(SK, :sk_prefix)',
            ExpressionAttributeValues={
                ':sk_prefix': 'BOAT#'
            },
            Select='COUNT'
        )
        total_boat_registrations = boat_response.get('Count', 0)
        
        # Count total payments (paid boat registrations)
        payment_response = db.table.scan(
            FilterExpression='begins_with(SK, :sk_prefix) AND registration_status = :status',
            ExpressionAttributeValues={
                ':sk_prefix': 'BOAT#',
                ':status': 'paid'
            },
            Select='COUNT'
        )
        total_payments = payment_response.get('Count', 0)
        
        # Count reserved rental boats (requested, confirmed, or paid)
        rental_response = db.table.scan(
            FilterExpression='begins_with(PK, :pk_prefix) AND SK = :sk AND (#status = :requested OR #status = :confirmed OR #status = :paid)',
            ExpressionAttributeValues={
                ':pk_prefix': 'RENTAL_BOAT#',
                ':sk': 'METADATA',
                ':requested': 'requested',
                ':confirmed': 'confirmed',
                ':paid': 'paid'
            },
            ExpressionAttributeNames={
                '#status': 'status'
            },
            Select='COUNT'
        )
        rental_boats_reserved = rental_response.get('Count', 0)
        
        stats = {
            'total_crew_members': total_crew_members,
            'total_boat_registrations': total_boat_registrations,
            'total_payments': total_payments,
            'rental_boats_reserved': rental_boats_reserved
        }
        
        logger.info(f"Retrieved stats: {stats}")
        
        return success_response(data=stats)
        
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        return success_response(data={
            'total_crew_members': 0,
            'total_boat_registrations': 0,
            'total_payments': 0,
            'rental_boats_reserved': 0
        })
