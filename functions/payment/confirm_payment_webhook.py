"""
Lambda function for handling Stripe webhook events
Processes payment confirmations and updates boat registration status
"""
import json
import logging
from datetime import datetime
from decimal import Decimal
import uuid

# Import from Lambda layer
from responses import success_response, validation_error, internal_error
from database import get_db_client
from stripe_client import verify_webhook_signature, get_webhook_secret, get_charge_receipt_url
from email_utils import send_payment_confirmation_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_payment_record(
    payment_intent_id: str,
    team_manager_id: str,
    boat_registration_ids: list,
    amount: Decimal,
    currency: str,
    receipt_url: str,
    db
) -> str:
    """
    Create a payment record in DynamoDB
    
    Returns:
        Payment ID
    """
    payment_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    payment_record = {
        'PK': f'TEAM#{team_manager_id}',
        'SK': f'PAYMENT#{payment_id}',
        'payment_id': payment_id,
        'stripe_payment_intent_id': payment_intent_id,
        'team_manager_id': team_manager_id,
        'boat_registration_ids': boat_registration_ids,
        'amount': amount,
        'currency': currency,
        'status': 'succeeded',
        'paid_at': timestamp,
        'stripe_receipt_url': receipt_url,
        'created_at': timestamp,
        'updated_at': timestamp
    }
    
    db.put_item(payment_record)
    logger.info(f"Created payment record: {payment_id} ({len(boat_registration_ids)} boats)")
    
    return payment_id


def update_boat_status_to_paid(
    team_manager_id: str,
    boat_registration_ids: list,
    payment_id: str,
    db
):
    """
    Update boat registration status to 'paid'
    """
    timestamp = datetime.utcnow().isoformat()
    
    for boat_id in boat_registration_ids:
        # Get current boat registration
        pk = f'TEAM#{team_manager_id}'
        sk = f'BOAT#{boat_id}'
        
        boat = db.get_item(pk=pk, sk=sk)
        
        if boat:
            # Ensure PK and SK are present (uppercase as required by DynamoDB)
            boat['PK'] = pk
            boat['SK'] = sk
            
            # Update status to paid
            boat['registration_status'] = 'paid'
            boat['payment_id'] = payment_id
            boat['paid_at'] = timestamp
            boat['updated_at'] = timestamp
            
            # Lock the pricing
            if 'pricing' in boat:
                boat['locked_pricing'] = boat['pricing']
            
            db.put_item(boat)
            logger.info(f"Updated boat {boat_id} status to 'paid'")
        else:
            logger.warning(f"Boat {boat_id} not found when updating to paid status")


def update_rental_request_status_to_paid(
    rental_request_ids: list,
    payment_id: str,
    db
):
    """
    DEPRECATED: Rental requests feature has been removed.
    This function is kept for backward compatibility but does nothing.
    """
    if rental_request_ids:
        logger.warning(f"Attempted to update rental requests but feature is deprecated: {rental_request_ids}")
    return


def handle_payment_succeeded(event_data: dict, db):
    """
    Handle payment_intent.succeeded event
    """
    payment_intent = event_data['object']
    payment_intent_id = payment_intent['id']
    amount_cents = payment_intent['amount']
    currency = payment_intent['currency']
    metadata = payment_intent.get('metadata', {})
    receipt_email = payment_intent.get('receipt_email')
    
    # Extract metadata
    team_manager_id = metadata.get('team_manager_id')
    boat_registration_ids_str = metadata.get('boat_registration_ids', '')
    boat_registration_ids = [bid for bid in boat_registration_ids_str.split(',') if bid] if boat_registration_ids_str else []
    
    if not team_manager_id or not boat_registration_ids:
        logger.error(f"Missing metadata in payment intent {payment_intent_id}")
        return
    
    # Convert amount from cents to decimal
    amount = Decimal(amount_cents) / 100
    
    logger.info(f"Processing successful payment: {payment_intent_id} for {amount} {currency}")
    
    # Get receipt URL
    receipt_url = get_charge_receipt_url(payment_intent_id)
    
    # Create payment record
    payment_id = create_payment_record(
        payment_intent_id=payment_intent_id,
        team_manager_id=team_manager_id,
        boat_registration_ids=boat_registration_ids,
        amount=amount,
        currency=currency.upper(),
        receipt_url=receipt_url or '',
        db=db
    )
    
    # Get boat details for email
    boat_details = []
    for boat_id in boat_registration_ids:
        boat = db.get_item(pk=f'TEAM#{team_manager_id}', sk=f'BOAT#{boat_id}')
        if boat:
            boat_details.append(boat)
    
    # Get team manager details
    team_manager = db.get_item(pk=f'TEAM#{team_manager_id}', sk='METADATA')
    team_manager_name = 'Cher membre'
    if team_manager:
        first_name = team_manager.get('first_name', '')
        last_name = team_manager.get('last_name', '')
        if first_name or last_name:
            team_manager_name = f"{first_name} {last_name}".strip()
    
    # Update boat registrations to 'paid' status
    update_boat_status_to_paid(
        team_manager_id=team_manager_id,
        boat_registration_ids=boat_registration_ids,
        payment_id=payment_id,
        db=db
    )
    
    logger.info(f"Successfully processed payment {payment_id} for {len(boat_registration_ids)} boats")
    
    # Send Slack notification for successful payment
    try:
        import os
        from slack_utils import notify_payment_completed, set_webhook_urls
        from secrets_manager import get_slack_admin_webhook
        
        # Get Slack webhook from Secrets Manager
        slack_webhook = get_slack_admin_webhook()
        
        if slack_webhook and receipt_email:
            set_webhook_urls(admin_webhook=slack_webhook)
            environment = os.environ.get('ENVIRONMENT', 'dev')
            notify_payment_completed(
                user_name=team_manager_name,
                user_email=receipt_email,
                amount=float(amount),
                currency=currency.upper(),
                boat_count=len(boat_registration_ids),
                payment_id=payment_id,
                environment=environment
            )
            logger.info("Slack notification sent for successful payment")
        else:
            logger.info("Slack webhook not configured or no receipt email - skipping notification")
    except Exception as e:
        # Don't fail payment processing if Slack notification fails
        logger.warning(f"Failed to send Slack notification: {e}")
    
    # Send confirmation email
    if receipt_email:
        payment_details = {
            'payment_id': payment_id,
            'amount': amount,
            'currency': currency.upper(),
            'paid_at': datetime.utcnow().isoformat()
        }
        
        email_sent = send_payment_confirmation_email(
            recipient_email=receipt_email,
            team_manager_name=team_manager_name,
            payment_details=payment_details,
            boat_registrations=boat_details,
            rental_boats=[],  # Rental feature removed
            receipt_url=receipt_url
        )
        
        if email_sent:
            logger.info(f"Confirmation email sent to {receipt_email}")
        else:
            logger.warning(f"Failed to send confirmation email to {receipt_email}")
    else:
        logger.warning("No receipt_email found in payment intent")


def handle_payment_failed(event_data: dict, db):
    """
    Handle payment_intent.payment_failed event
    """
    payment_intent = event_data['object']
    payment_intent_id = payment_intent['id']
    amount_cents = payment_intent.get('amount', 0)
    currency = payment_intent.get('currency', 'eur')
    metadata = payment_intent.get('metadata', {})
    receipt_email = payment_intent.get('receipt_email')
    last_payment_error = payment_intent.get('last_payment_error', {})
    error_message = last_payment_error.get('message', 'Unknown error')
    
    team_manager_id = metadata.get('team_manager_id')
    
    # Convert amount from cents to decimal
    amount = Decimal(amount_cents) / 100
    
    logger.warning(f"Payment failed for payment intent {payment_intent_id}, team manager {team_manager_id}: {error_message}")
    
    # Get team manager details for notification
    team_manager_name = 'Unknown User'
    if team_manager_id:
        team_manager = db.get_item(pk=f'TEAM#{team_manager_id}', sk='METADATA')
        if team_manager:
            first_name = team_manager.get('first_name', '')
            last_name = team_manager.get('last_name', '')
            if first_name or last_name:
                team_manager_name = f"{first_name} {last_name}".strip()
    
    # Send Slack notification for failed payment
    try:
        import os
        from slack_utils import notify_payment_failed, set_webhook_urls
        from secrets_manager import get_slack_admin_webhook
        
        # Get Slack webhook from Secrets Manager
        slack_webhook = get_slack_admin_webhook()
        
        if slack_webhook and receipt_email:
            set_webhook_urls(admin_webhook=slack_webhook)
            environment = os.environ.get('ENVIRONMENT', 'dev')
            notify_payment_failed(
                user_name=team_manager_name,
                user_email=receipt_email,
                amount=float(amount),
                currency=currency.upper(),
                error_message=error_message,
                payment_id=payment_intent_id,
                environment=environment
            )
            logger.info("Slack notification sent for failed payment")
        else:
            logger.info("Slack webhook not configured or no receipt email - skipping notification")
    except Exception as e:
        # Don't fail if Slack notification fails
        logger.warning(f"Failed to send Slack notification: {e}")
    
    # Optionally: Create a failed payment record or send notification
    # For now, we just log it


def lambda_handler(event, context):
    """
    Handle Stripe webhook events
    
    Supported events:
        - payment_intent.succeeded: Payment was successful
        - payment_intent.payment_failed: Payment failed
    """
    logger.info("Stripe webhook received")
    
    try:
        # Get webhook signature
        signature = event.get('headers', {}).get('Stripe-Signature')
        if not signature:
            logger.error("Missing Stripe-Signature header")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing signature'})
            }
        
        # Get raw body
        body = event.get('body', '')
        
        # Get webhook secret
        webhook_secret = get_webhook_secret()
        
        # Verify webhook signature
        stripe_event = verify_webhook_signature(body, signature, webhook_secret)
        
        event_type = stripe_event['type']
        event_data = stripe_event['data']
        
        logger.info(f"Processing webhook event: {event_type}")
        
        # Get database client
        db = get_db_client()
        
        # Handle different event types
        if event_type == 'payment_intent.succeeded':
            handle_payment_succeeded(event_data, db)
        elif event_type == 'payment_intent.payment_failed':
            handle_payment_failed(event_data, db)
        else:
            logger.info(f"Unhandled event type: {event_type}")
        
        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({'received': True})
        }
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
