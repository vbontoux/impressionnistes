"""
Lambda function for creating a Stripe Payment Intent
Team managers can create a payment intent for selected boat registrations
"""
import json
import logging
from decimal import Decimal
from typing import List, Dict, Any

# Import from Lambda layer
from responses import (
    success_response,
    validation_error,
    not_found_error,
    internal_error,
    handle_exceptions
)
from database import get_db_client
from auth_utils import get_user_from_event, require_team_manager, require_team_manager_or_admin_override
from pricing import calculate_boat_pricing
from configuration import ConfigurationManager
from stripe_client import create_payment_intent as stripe_create_payment_intent
from access_control import require_permission

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validate_boat_registrations(
    boat_registration_ids: List[str],
    team_manager_id: str,
    db
) -> tuple[List[Dict[str, Any]], str]:
    """
    Validate that all boat registrations exist, belong to the team manager,
    and are in 'complete' status
    
    Returns:
        Tuple of (list of boat registrations, error message or None)
    """
    boats = []
    
    for boat_id in boat_registration_ids:
        # Get boat registration
        boat = db.get_item(
            pk=f'TEAM#{team_manager_id}',
            sk=f'BOAT#{boat_id}'
        )
        
        if not boat:
            return None, f"Boat registration {boat_id} not found"
        
        # Check if boat request is pending (enabled but not assigned)
        boat_request_enabled = boat.get('boat_request_enabled', False)
        assigned_boat_identifier = boat.get('assigned_boat_identifier')
        
        if boat_request_enabled and (not assigned_boat_identifier or not assigned_boat_identifier.strip()):
            return None, f"Boat registration {boat_id} has a pending boat assignment request. Payment cannot be processed until a boat is assigned."
        
        # Check if boat is in 'complete' status
        if boat.get('registration_status') != 'complete':
            return None, f"Boat registration {boat_id} is not ready for payment (status: {boat.get('registration_status')})"
        
        boats.append(boat)
    
    return boats, None


def calculate_total_amount(
    boats: List[Dict[str, Any]],
    crew_members: List[Dict[str, Any]],
    pricing_config: Dict[str, Any],
    db=None
) -> Decimal:
    """
    Calculate total amount for all boats
    Server-side calculation - never trust frontend
    
    Args:
        boats: List of boat registrations
        crew_members: List of crew members
        pricing_config: Pricing configuration
        db: Database client (optional) - if provided, will store pricing in boat records
    
    Returns:
        Total amount as Decimal
    """
    total = Decimal('0')
    
    for boat in boats:
        pricing = calculate_boat_pricing(boat, crew_members, pricing_config)
        total += pricing['total']
        
        # Store pricing in boat record if db client provided
        if db and 'PK' in boat and 'SK' in boat:
            boat['pricing'] = pricing
            db.put_item(boat)
            logger.info(f"Stored pricing for boat {boat.get('boat_registration_id')}: {pricing['total']} EUR")
    
    return total


def validate_rental_requests(
    rental_request_ids: List[str],
    team_manager_id: str,
    db
) -> tuple[List[Dict[str, Any]], str]:
    """
    DEPRECATED: Rental requests feature has been removed.
    This function is kept for backward compatibility but will always return empty list.
    """
    if rental_request_ids:
        return None, "Rental requests feature is no longer available"
    return [], None


@handle_exceptions
@require_team_manager_or_admin_override
@require_permission('process_payment')
def lambda_handler(event, context):
    """
    Create a Stripe Payment Intent for selected boat registrations and/or rental requests
    
    Request body:
        {
            "boat_registration_ids": ["boat_id_1", "boat_id_2", ...]
        }
    
    Returns:
        {
            "payment_intent_id": "pi_xxx",
            "client_secret": "pi_xxx_secret_xxx",
            "amount": 100.00,
            "currency": "EUR"
        }
    """
    logger.info("Create payment intent request")
    
    # Get authenticated user (respects admin impersonation via _effective_user_id)
    team_manager_id = event.get('_effective_user_id')
    if not team_manager_id:
        user = get_user_from_event(event)
        team_manager_id = user['user_id']
    
    # Get user for email (always use actual user, not impersonated)
    user = get_user_from_event(event)
    team_manager_email = user.get('email')
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error({'body': 'Invalid JSON in request body'})
    
    # Validate input
    boat_registration_ids = body.get('boat_registration_ids', [])
    
    if not boat_registration_ids:
        return validation_error({'payment': 'At least one boat registration is required'})
    
    if not isinstance(boat_registration_ids, list):
        return validation_error({'boat_registration_ids': 'Must be an array of boat registration IDs'})
    
    # Get database client
    db = get_db_client()
    
    logger.info(f"Team manager email for receipt: {team_manager_email}")
    
    # Get pricing configuration
    config_manager = ConfigurationManager()
    pricing_config = config_manager.get_pricing_config()
    base_seat_price = Decimal(str(pricing_config.get('base_seat_price', 20)))
    
    # Validate boat registrations
    boats, error = validate_boat_registrations(boat_registration_ids, team_manager_id, db)
    if error:
        return validation_error({'boat_registration_ids': error})
    
    # Calculate total amount (server-side - never trust frontend)
    crew_members = db.query_by_pk(
        pk=f'TEAM#{team_manager_id}',
        sk_prefix='CREW#'
    )
    total_amount = calculate_total_amount(boats, crew_members, pricing_config, db)
    
    logger.info(f"Calculated total amount: {total_amount} EUR ({len(boats)} boats)")
    
    # Create metadata for Stripe
    metadata = {
        'team_manager_id': team_manager_id,
        'boat_count': str(len(boats)),
        'boat_registration_ids': ','.join(boat_registration_ids)
    }
    
    # Create description
    boat_types = [boat.get('boat_type', 'unknown') for boat in boats]
    description = f"Course des Impressionnistes - {len(boats)} boat(s): {', '.join(boat_types)}"
    
    try:
        # Create Stripe Payment Intent
        payment_intent = stripe_create_payment_intent(
            amount=total_amount,
            currency='EUR',
            metadata=metadata,
            description=description,
            receipt_email=team_manager_email  # Send receipt to team manager
        )
        
        logger.info(f"Created Payment Intent: {payment_intent['id']}")
        
        # Return success response
        return success_response(data={
            'payment_intent_id': payment_intent['id'],
            'client_secret': payment_intent['client_secret'],
            'amount': float(total_amount),
            'currency': 'EUR',
            'boat_count': len(boats)
        })
        
    except Exception as e:
        logger.error(f"Failed to create payment intent: {str(e)}")
        return internal_error(f"Failed to create payment intent: {str(e)}")
