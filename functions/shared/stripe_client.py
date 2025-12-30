"""
Stripe Client Utility
Handles Stripe API initialization and common operations
"""
import stripe
import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
from secrets_manager import get_stripe_api_key, get_stripe_webhook_secret

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def initialize_stripe():
    """
    Initialize Stripe with API key from Secrets Manager
    """
    api_key = get_stripe_api_key()
    stripe.api_key = api_key
    logger.info("Stripe client initialized")


def create_payment_intent(
    amount: Decimal,
    currency: str,
    metadata: Dict[str, Any],
    description: Optional[str] = None,
    receipt_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a Stripe Payment Intent
    
    Args:
        amount: Amount in the currency's smallest unit (e.g., cents for EUR)
        currency: Three-letter ISO currency code (e.g., 'eur')
        metadata: Dictionary of metadata to attach to the payment intent
        description: Optional description of the payment
        receipt_email: Optional email address to send receipt to
    
    Returns:
        Payment Intent object
    """
    initialize_stripe()
    
    try:
        # Convert Decimal to int (cents)
        amount_cents = int(amount * 100)
        
        # Build payment intent parameters
        payment_intent_params = {
            'amount': amount_cents,
            'currency': currency.lower(),
            'metadata': metadata,
            'description': description,
            'automatic_payment_methods': {'enabled': True},
        }
        
        # Add receipt_email if provided
        if receipt_email:
            payment_intent_params['receipt_email'] = receipt_email
            logger.info(f"Receipt will be sent to: {receipt_email}")
        
        payment_intent = stripe.PaymentIntent.create(**payment_intent_params)
        
        logger.info(f"Created Payment Intent: {payment_intent.id} for {amount} {currency}")
        
        return {
            'id': payment_intent.id,
            'client_secret': payment_intent.client_secret,
            'amount': payment_intent.amount,
            'currency': payment_intent.currency,
            'status': payment_intent.status,
            'metadata': payment_intent.metadata
        }
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating payment intent: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        raise


def retrieve_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
    """
    Retrieve a Stripe Payment Intent
    
    Args:
        payment_intent_id: ID of the payment intent
    
    Returns:
        Payment Intent object
    """
    initialize_stripe()
    
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        return {
            'id': payment_intent.id,
            'amount': payment_intent.amount,
            'currency': payment_intent.currency,
            'status': payment_intent.status,
            'metadata': payment_intent.metadata,
            'charges': payment_intent.charges.data if payment_intent.charges else []
        }
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error retrieving payment intent: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error retrieving payment intent: {str(e)}")
        raise


def verify_webhook_signature(payload: str, signature: str, webhook_secret: str) -> Dict[str, Any]:
    """
    Verify Stripe webhook signature and construct event
    
    Args:
        payload: Raw request body
        signature: Stripe-Signature header value
        webhook_secret: Webhook signing secret from Stripe
    
    Returns:
        Stripe Event object
    
    Raises:
        stripe.error.SignatureVerificationError: If signature is invalid
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
        
        logger.info(f"Verified webhook event: {event['type']}")
        return event
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid webhook signature: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error verifying webhook: {str(e)}")
        raise


def get_webhook_secret() -> str:
    """
    Get Stripe webhook secret from AWS Secrets Manager
    
    Returns:
        Webhook signing secret
    """
    return get_stripe_webhook_secret()


def get_charge_receipt_url(payment_intent_id: str) -> Optional[str]:
    """
    Get the receipt URL from a successful payment intent
    
    Args:
        payment_intent_id: ID of the payment intent
    
    Returns:
        Receipt URL or None if not available
    """
    initialize_stripe()
    
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if payment_intent.charges and len(payment_intent.charges.data) > 0:
            charge = payment_intent.charges.data[0]
            return charge.receipt_url
        
        return None
    except Exception as e:
        logger.error(f"Error getting receipt URL: {str(e)}")
        return None


def format_amount_for_display(amount_cents: int, currency: str) -> str:
    """
    Format amount from cents to display format
    
    Args:
        amount_cents: Amount in cents
        currency: Currency code
    
    Returns:
        Formatted amount string
    """
    amount = Decimal(amount_cents) / 100
    
    if currency.upper() == 'EUR':
        return f"{amount:.2f} €"
    else:
        return f"{currency.upper()} {amount:.2f}"


def format_amount_for_stripe(amount: Decimal) -> int:
    """
    Format amount from decimal to Stripe format (cents)
    
    Args:
        amount: Amount as Decimal
    
    Returns:
        Amount in cents as integer
    """
    return int(amount * 100)
