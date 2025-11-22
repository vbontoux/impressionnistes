"""
Lambda function for retrieving payment receipt details
Team managers can view their payment receipts
"""
import json
import logging

# Import from Lambda layer
from responses import (
    success_response,
    validation_error,
    not_found_error,
    internal_error,
    handle_exceptions
)
from database import get_db_client
from auth_utils import get_user_from_event, require_team_manager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_team_manager
def lambda_handler(event, context):
    """
    Get payment receipt details
    
    Path parameters:
        - payment_id: ID of the payment
    
    Returns:
        Payment record with receipt details
    """
    logger.info("Get payment receipt request")
    
    # Get authenticated user
    user = get_user_from_event(event)
    team_manager_id = user['user_id']
    
    # Get payment ID from path
    payment_id = event.get('pathParameters', {}).get('payment_id')
    if not payment_id:
        return validation_error({'payment_id': 'Payment ID is required'})
    
    # Get payment record from DynamoDB
    db = get_db_client()
    
    payment = db.get_item(
        pk=f'TEAM#{team_manager_id}',
        sk=f'PAYMENT#{payment_id}'
    )
    
    if not payment:
        return not_found_error('Payment not found')
    
    logger.info(f"Retrieved payment: {payment_id}")
    
    # Get boat registrations for this payment
    boat_registration_ids = payment.get('boat_registration_ids', [])
    boats = []
    
    for boat_id in boat_registration_ids:
        boat = db.get_item(
            pk=f'TEAM#{team_manager_id}',
            sk=f'BOAT#{boat_id}'
        )
        if boat:
            boats.append({
                'boat_registration_id': boat.get('boat_registration_id'),
                'event_type': boat.get('event_type'),
                'boat_type': boat.get('boat_type'),
                'race_id': boat.get('race_id'),
                'pricing': boat.get('locked_pricing') or boat.get('pricing')
            })
    
    # Build response
    receipt_data = {
        'payment_id': payment.get('payment_id'),
        'stripe_payment_intent_id': payment.get('stripe_payment_intent_id'),
        'amount': float(payment.get('amount', 0)),
        'currency': payment.get('currency'),
        'status': payment.get('status'),
        'paid_at': payment.get('paid_at'),
        'stripe_receipt_url': payment.get('stripe_receipt_url'),
        'boats': boats
    }
    
    # Return success response
    return success_response(data=receipt_data)
