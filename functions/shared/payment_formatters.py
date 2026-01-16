"""
Payment formatting utilities
Shared formatting logic for payment-related Lambda functions
"""
import logging
from decimal import Decimal

logger = logging.getLogger()


def format_payment_list_response(payments):
    """
    Format payment records for API response
    
    Args:
        payments: List of payment records from DynamoDB
    
    Returns:
        list: Formatted payment records
    """
    formatted = []
    
    for payment in payments:
        formatted_payment = {
            'payment_id': payment.get('payment_id'),
            'stripe_payment_intent_id': payment.get('stripe_payment_intent_id'),
            'amount': float(payment.get('amount', 0)),
            'currency': payment.get('currency', 'EUR'),
            'status': payment.get('status', 'unknown'),
            'paid_at': payment.get('paid_at'),
            'stripe_receipt_url': payment.get('stripe_receipt_url'),
            'boat_registration_ids': payment.get('boat_registration_ids', []),
            'boat_count': len(payment.get('boat_registration_ids', [])),
            'boat_details': payment.get('boat_details', [])  # Include boat details snapshot
        }
        
        formatted.append(formatted_payment)
    
    return formatted


def format_payment_summary_response(total_paid, outstanding_balance, unpaid_boats):
    """
    Format payment summary for API response
    
    Args:
        total_paid: Decimal total amount paid
        outstanding_balance: Decimal outstanding balance
        unpaid_boats: List of unpaid boat records
    
    Returns:
        dict: Formatted summary
    """
    formatted_boats = []
    
    for boat in unpaid_boats:
        # Get estimated amount from pricing or calculate
        if 'pricing' in boat and boat['pricing']:
            estimated_amount = boat['pricing'].get('total_amount', 0)
        else:
            estimated_amount = 150.00  # Default estimate
        
        formatted_boats.append({
            'boat_registration_id': boat.get('boat_registration_id'),
            'event_type': boat.get('event_type'),
            'boat_type': boat.get('boat_type'),
            'estimated_amount': float(estimated_amount),
            'registration_status': boat.get('registration_status')
        })
    
    return {
        'total_paid': float(total_paid),
        'outstanding_balance': float(outstanding_balance),
        'currency': 'EUR',
        'unpaid_boats': formatted_boats
    }


def format_admin_payment_response(payments, team_manager_cache):
    """
    Format payment records for admin API response (includes team manager info)
    
    Args:
        payments: List of payment records
        team_manager_cache: Dict mapping team_manager_id to team manager info
    
    Returns:
        list: Formatted payment records with team manager info
    """
    formatted = []
    
    for payment in payments:
        team_manager_id = payment.get('team_manager_id')
        team_manager = team_manager_cache.get(team_manager_id, {})
        
        formatted_payment = {
            'payment_id': payment.get('payment_id'),
            'team_manager_id': team_manager_id,
            'team_manager_name': f"{team_manager.get('first_name', '')} {team_manager.get('last_name', '')}".strip(),
            'team_manager_email': team_manager.get('email'),
            'club_affiliation': team_manager.get('club_affiliation'),
            'amount': float(payment.get('amount', 0)),
            'currency': payment.get('currency', 'EUR'),
            'status': payment.get('status', 'unknown'),
            'paid_at': payment.get('paid_at'),
            'boat_count': len(payment.get('boat_registration_ids', []))
        }
        
        formatted.append(formatted_payment)
    
    return formatted


def format_analytics_response(summary, timeline, top_payers, team_manager_cache):
    """
    Format analytics data for API response
    
    Args:
        summary: Analytics summary dict
        timeline: List of time period data
        top_payers: List of top payer data
        team_manager_cache: Dict mapping team_manager_id to team manager info
    
    Returns:
        dict: Formatted analytics response
    """
    # Format top payers with team manager info
    formatted_top_payers = []
    for payer in top_payers:
        team_manager_id = payer['team_manager_id']
        team_manager = team_manager_cache.get(team_manager_id, {})
        
        formatted_top_payers.append({
            'team_manager_id': team_manager_id,
            'team_manager_name': f"{team_manager.get('first_name', '')} {team_manager.get('last_name', '')}".strip(),
            'club_affiliation': team_manager.get('club_affiliation'),
            'total_paid': payer['total_paid'],
            'payment_count': payer['payment_count'],
            'boat_count': payer['boat_count']
        })
    
    return {
        'summary': summary,
        'timeline': timeline,
        'top_payers': formatted_top_payers
    }


def sort_payments_by_field(payments, field='paid_at', reverse=True):
    """
    Sort payments by a specific field
    
    Args:
        payments: List of payment records
        field: Field name to sort by
        reverse: If True, sort descending; if False, sort ascending
    
    Returns:
        list: Sorted payment records
    """
    try:
        return sorted(payments, key=lambda x: x.get(field, ''), reverse=reverse)
    except Exception as e:
        logger.warning(f"Failed to sort payments by {field}: {str(e)}")
        return payments


def format_currency(amount, currency='EUR'):
    """
    Format amount as currency string
    
    Args:
        amount: Numeric amount
        currency: Currency code
    
    Returns:
        str: Formatted currency string
    """
    if isinstance(amount, Decimal):
        amount = float(amount)
    
    return f"{amount:.2f}"


def format_unpaid_boat_list(boats):
    """
    Format unpaid boats for display
    
    Args:
        boats: List of boat registration records
    
    Returns:
        list: Formatted boat records
    """
    formatted = []
    
    for boat in boats:
        # Get estimated amount
        if 'pricing' in boat and boat['pricing']:
            estimated_amount = boat['pricing'].get('total_amount', 0)
        else:
            estimated_amount = 150.00  # Default
        
        formatted.append({
            'boat_registration_id': boat.get('boat_registration_id'),
            'event_type': boat.get('event_type'),
            'boat_type': boat.get('boat_type'),
            'estimated_amount': float(estimated_amount),
            'registration_status': boat.get('registration_status'),
            'created_at': boat.get('created_at')
        })
    
    return formatted
