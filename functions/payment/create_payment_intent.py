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
from auth_utils import get_user_from_event, require_team_manager
from pricing import calculate_boat_pricing, calculate_rental_request_pricing
from configuration import ConfigurationManager
from stripe_client import create_payment_intent as stripe_create_payment_intent

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
        
        # Check if boat is in 'complete' status
        if boat.get('registration_status') != 'complete':
            return None, f"Boat registration {boat_id} is not ready for payment (status: {boat.get('registration_status')})"
        
        boats.append(boat)
    
    return boats, None


def calculate_total_amount(
    boats: List[Dict[str, Any]],
    crew_members: List[Dict[str, Any]],
    pricing_config: Dict[str, Any]
) -> Decimal:
    """
    Calculate total amount for all boats
    Server-side calculation - never trust frontend
    
    Returns:
        Total amount as Decimal
    """
    total = Decimal('0')
    
    for boat in boats:
        pricing = calculate_boat_pricing(boat, crew_members, pricing_config)
        total += pricing['total']
    
    return total


def validate_rental_requests(
    rental_request_ids: List[str],
    team_manager_id: str,
    db
) -> tuple[List[Dict[str, Any]], str]:
    """
    Validate that all rental requests exist, belong to the team manager,
    and are in 'accepted' status
    """
    requests = []
    
    for request_id_param in rental_request_ids:
        # Reconstruct full DynamoDB key (frontend sends only UUID)
        request_id = f"RENTAL_REQUEST#{request_id_param}"
        
        # Get rental request
        request = db.get_item(
            pk=request_id,
            sk='METADATA'
        )
        
        if not request:
            return None, f"Rental request {request_id_param} not found"
        
        # Check if request belongs to this team manager (requester stores user_id)
        if request.get('requester_id') != team_manager_id:
            return None, f"Rental request {request_id_param} does not belong to you"
        
        # Check if request is accepted
        if request.get('status') != 'accepted':
            return None, f"Rental request {request_id_param} is not accepted (status: {request.get('status')})"
        
        requests.append(request)
    
    return requests, None


@handle_exceptions
@require_team_manager
def lambda_handler(event, context):
    """
    Create a Stripe Payment Intent for selected boat registrations and/or rental requests
    
    Request body:
        {
            "boat_registration_ids": ["boat_id_1", "boat_id_2", ...],
            "rental_request_ids": ["RENTAL_REQUEST#id_1", "RENTAL_REQUEST#id_2", ...]
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
    
    # Get authenticated user
    user = get_user_from_event(event)
    team_manager_id = user['user_id']
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return validation_error({'body': 'Invalid JSON in request body'})
    
    # Validate input
    boat_registration_ids = body.get('boat_registration_ids', [])
    rental_request_ids = body.get('rental_request_ids', [])
    
    if not boat_registration_ids and not rental_request_ids:
        return validation_error({'payment': 'At least one boat registration or rental request is required'})
    
    if not isinstance(boat_registration_ids, list):
        return validation_error({'boat_registration_ids': 'Must be an array of boat registration IDs'})
    
    if not isinstance(rental_request_ids, list):
        return validation_error({'rental_request_ids': 'Must be an array of rental request IDs'})
    
    # Get database client
    db = get_db_client()
    
    # Get team manager email for receipt
    team_manager_email = user.get('email')  # Email from Cognito token
    logger.info(f"Team manager email for receipt: {team_manager_email}")
    
    # Get pricing configuration
    config_manager = ConfigurationManager()
    pricing_config = config_manager.get_pricing_config()
    base_seat_price = Decimal(str(pricing_config.get('base_seat_price', 20)))
    
    # Validate boat registrations
    boats = []
    if boat_registration_ids:
        boats, error = validate_boat_registrations(boat_registration_ids, team_manager_id, db)
        if error:
            return validation_error({'boat_registration_ids': error})
    
    # Validate rental requests
    requests = []
    if rental_request_ids:
        requests, error = validate_rental_requests(rental_request_ids, team_manager_id, db)
        if error:
            return validation_error({'rental_request_ids': error})
    
    # Calculate total amount (server-side - never trust frontend)
    total_amount = Decimal('0')
    
    # Add boat registration fees
    if boats:
        crew_members = db.query_by_pk(
            pk=f'TEAM#{team_manager_id}',
            sk_prefix='CREW#'
        )
        total_amount += calculate_total_amount(boats, crew_members, pricing_config)
    
    # Add rental fees
    for request in requests:
        boat_type = request.get('boat_type', 'skiff')
        pricing = calculate_rental_request_pricing(boat_type, pricing_config)
        total_amount += pricing['total']
    
    logger.info(f"Calculated total amount: {total_amount} EUR ({len(boats)} boats, {len(requests)} rental requests)")
    
    # Create metadata for Stripe
    # Reconstruct full DynamoDB keys for metadata (frontend sends only UUIDs)
    full_rental_request_ids = [f"RENTAL_REQUEST#{rid}" for rid in rental_request_ids] if rental_request_ids else []
    
    metadata = {
        'team_manager_id': team_manager_id,
        'boat_count': str(len(boats)),
        'rental_count': str(len(requests)),
        'boat_registration_ids': ','.join(boat_registration_ids) if boat_registration_ids else '',
        'rental_request_ids': ','.join(full_rental_request_ids)
    }
    
    # Create description
    description_parts = []
    if boats:
        boat_types = [boat.get('boat_type', 'unknown') for boat in boats]
        description_parts.append(f"{len(boats)} boat(s): {', '.join(boat_types)}")
    if requests:
        request_types = [request.get('boat_type', 'unknown') for request in requests]
        description_parts.append(f"{len(requests)} rental(s): {', '.join(request_types)}")
    description = f"Course des Impressionnistes - {' + '.join(description_parts)}"
    
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
            'boat_count': len(boats),
            'rental_count': len(requests)
        })
        
    except Exception as e:
        logger.error(f"Failed to create payment intent: {str(e)}")
        return internal_error(f"Failed to create payment intent: {str(e)}")
