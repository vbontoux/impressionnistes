"""
Pricing Calculation Engine
Calculates registration fees based on crew composition, boat rental, and multi-club status
"""
from decimal import Decimal
from typing import Dict, List, Any, Optional
import logging
from validation import is_rcpm_member

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Default pricing configuration (can be overridden from DynamoDB)
DEFAULT_BASE_SEAT_PRICE = Decimal('20.00')  # EUR per seat
DEFAULT_RENTAL_MULTIPLIER_SKIFF = Decimal('2.5')
DEFAULT_RENTAL_PRICE_CREW = Decimal('20.00')  # EUR per seat for crew boats (Base_Seat_Price)


def calculate_boat_pricing(
    boat_registration: Dict[str, Any],
    crew_members: List[Dict[str, Any]],
    pricing_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate complete pricing for a boat registration
    
    Args:
        boat_registration: Boat registration object with seats and rental info
        crew_members: List of all crew members for the team
        pricing_config: Optional pricing configuration from DynamoDB
    
    Returns:
        Dictionary with detailed price breakdown
    """
    # Get pricing configuration
    base_seat_price = Decimal(str(pricing_config.get('base_seat_price', DEFAULT_BASE_SEAT_PRICE))) if pricing_config else DEFAULT_BASE_SEAT_PRICE
    rental_multiplier_skiff = Decimal(str(pricing_config.get('boat_rental_multiplier_skiff', DEFAULT_RENTAL_MULTIPLIER_SKIFF))) if pricing_config else DEFAULT_RENTAL_MULTIPLIER_SKIFF
    rental_price_crew = Decimal(str(pricing_config.get('boat_rental_price_crew', DEFAULT_RENTAL_PRICE_CREW))) if pricing_config else DEFAULT_RENTAL_PRICE_CREW
    
    # Initialize pricing breakdown
    pricing = {
        'base_price': Decimal('0'),
        'rental_fee': Decimal('0'),
        'total': Decimal('0'),
        'currency': 'EUR',
        'breakdown': []
    }
    
    # Get boat details
    boat_type = boat_registration.get('boat_type')
    is_boat_rental = boat_registration.get('is_boat_rental', False)
    is_multi_club_crew = boat_registration.get('is_multi_club_crew', False)
    seats = boat_registration.get('seats', [])
    
    # Count filled seats and check RCPM membership
    filled_seats = [seat for seat in seats if seat.get('crew_member_id')]
    seat_count = len(filled_seats)
    
    if seat_count == 0:
        return pricing
    
    # Create crew member lookup
    crew_lookup = {crew['crew_member_id']: crew for crew in crew_members}
    
    # Calculate base price per seat, checking RCPM membership
    rcpm_seats = 0
    external_seats = 0
    
    for seat in filled_seats:
        crew_id = seat.get('crew_member_id')
        crew = crew_lookup.get(crew_id)
        
        if crew:
            club = crew.get('club_affiliation', '')
            # Check if RCPM member using centralized detection logic
            if is_rcpm_member(club):
                rcpm_seats += 1
            else:
                external_seats += 1
    
    # Calculate base price (only for external members)
    base_price = base_seat_price * external_seats
    pricing['base_price'] = base_price
    
    if rcpm_seats > 0:
        pricing['breakdown'].append({
            'item': f'{rcpm_seats} RCPM seat(s)',
            'unit_price': Decimal('0'),
            'quantity': rcpm_seats,
            'amount': Decimal('0')
        })
    
    if external_seats > 0:
        pricing['breakdown'].append({
            'item': f'{external_seats} external seat(s)',
            'unit_price': base_seat_price,
            'quantity': external_seats,
            'amount': base_price
        })
    
    # Calculate rental fee if applicable
    if is_boat_rental:
        if boat_type == 'skiff':
            # Skiff rental: 2.5x base price
            rental_fee = base_seat_price * rental_multiplier_skiff
            pricing['rental_fee'] = rental_fee
            pricing['breakdown'].append({
                'item': 'Skiff rental',
                'unit_price': base_seat_price * rental_multiplier_skiff,
                'quantity': 1,
                'amount': rental_fee
            })
        else:
            # Crew boat rental: base price per seat
            rental_fee = rental_price_crew * seat_count
            pricing['rental_fee'] = rental_fee
            pricing['breakdown'].append({
                'item': f'Boat rental ({seat_count} seats)',
                'unit_price': rental_price_crew,
                'quantity': seat_count,
                'amount': rental_fee
            })
    
    # Note: Multi-club crew seat rental is already included in base_price
    # External members pay Base_Seat_Price, RCPM members pay zero
    # No additional surcharge is applied for multi-club crews
    
    # Calculate total
    pricing['total'] = pricing['base_price'] + pricing['rental_fee']
    
    logger.info(f"Calculated pricing for boat {boat_registration.get('boat_registration_id')}: {pricing['total']} EUR")
    
    return pricing


def calculate_batch_pricing(
    boat_registrations: List[Dict[str, Any]],
    crew_members: List[Dict[str, Any]],
    pricing_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate total pricing for multiple boat registrations (for batch payment)
    
    Args:
        boat_registrations: List of boat registration objects
        crew_members: List of all crew members for the team
        pricing_config: Optional pricing configuration from DynamoDB
    
    Returns:
        Dictionary with total and per-boat breakdown
    """
    batch_pricing = {
        'boats': [],
        'total': Decimal('0'),
        'currency': 'EUR'
    }
    
    for boat in boat_registrations:
        boat_pricing = calculate_boat_pricing(boat, crew_members, pricing_config)
        batch_pricing['boats'].append({
            'boat_registration_id': boat.get('boat_registration_id'),
            'boat_type': boat.get('boat_type'),
            'event_type': boat.get('event_type'),
            'pricing': boat_pricing
        })
        batch_pricing['total'] += boat_pricing['total']
    
    logger.info(f"Calculated batch pricing for {len(boat_registrations)} boats: {batch_pricing['total']} EUR")
    
    return batch_pricing


def format_price_for_display(amount: Decimal, currency: str = 'EUR') -> str:
    """
    Format price for display
    
    Args:
        amount: Price amount as Decimal
        currency: Currency code
    
    Returns:
        Formatted price string
    """
    if currency == 'EUR':
        return f"{amount:.2f} €"
    else:
        return f"{currency} {amount:.2f}"


def validate_pricing_config(config: Dict[str, Any]) -> bool:
    """
    Validate pricing configuration
    
    Args:
        config: Pricing configuration dictionary
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['base_seat_price', 'boat_rental_multiplier_skiff', 'boat_rental_price_crew']
    
    for field in required_fields:
        if field not in config:
            logger.error(f"Missing required pricing field: {field}")
            return False
        
        try:
            value = Decimal(str(config[field]))
            if value < 0:
                logger.error(f"Pricing field {field} must be non-negative")
                return False
        except (ValueError, TypeError):
            logger.error(f"Invalid pricing value for {field}: {config[field]}")
            return False
    
    return True
