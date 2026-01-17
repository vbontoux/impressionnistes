"""
Payment calculation utilities
Shared calculation logic for payment-related Lambda functions
"""
import logging
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger()


def calculate_total_paid(payments):
    """
    Calculate total amount paid across all payments
    
    Args:
        payments: List of payment records
    
    Returns:
        Decimal: Total amount paid
    """
    total = Decimal('0')
    for payment in payments:
        if payment.get('status') == 'succeeded':
            amount = payment.get('amount', 0)
            if isinstance(amount, (int, float)):
                amount = Decimal(str(amount))
            total += amount
    
    return total


def count_boats_in_payments(payments):
    """
    Count total number of boats across all payments
    
    Args:
        payments: List of payment records
    
    Returns:
        int: Total number of boats paid for
    """
    total_boats = 0
    for payment in payments:
        if payment.get('status') == 'succeeded':
            boat_ids = payment.get('boat_registration_ids', [])
            total_boats += len(boat_ids)
    
    return total_boats


def calculate_outstanding_balance(boats, pricing_config=None):
    """
    Calculate outstanding balance from unpaid boats
    
    Args:
        boats: List of boat registration records (status='complete')
        pricing_config: Optional pricing configuration (if not using locked pricing)
    
    Returns:
        Decimal: Total outstanding balance
    """
    total = Decimal('0')
    
    for boat in boats:
        # Use locked pricing if available, otherwise use current pricing
        if 'pricing' in boat and boat['pricing']:
            amount = boat['pricing'].get('total_amount', 0)
        elif pricing_config:
            # Calculate from pricing config (fallback)
            amount = _calculate_boat_price(boat, pricing_config)
        else:
            amount = 0
        
        if isinstance(amount, (int, float)):
            amount = Decimal(str(amount))
        
        total += amount
    
    return total


def _calculate_boat_price(boat, pricing_config):
    """
    Calculate boat price from pricing configuration
    
    Args:
        boat: Boat registration record
        pricing_config: Pricing configuration
    
    Returns:
        Decimal: Calculated price
    """
    # This is a simplified calculation - actual pricing logic may be more complex
    event_type = boat.get('event_type')
    boat_type = boat.get('boat_type')
    is_rental = boat.get('is_boat_rental', False)
    
    # Get base price from config
    base_price = Decimal('150.00')  # Default
    
    # Add rental fee if applicable
    rental_fee = Decimal('50.00') if is_rental else Decimal('0')
    
    return base_price + rental_fee


def calculate_payment_summary_stats(payments):
    """
    Calculate summary statistics for a list of payments
    
    Args:
        payments: List of payment records
    
    Returns:
        dict: Summary statistics
    """
    if not payments:
        return {
            'total_payments': 0,
            'total_amount': 0.00,
            'currency': 'EUR'
        }
    
    total_amount = calculate_total_paid(payments)
    currency = payments[0].get('currency', 'EUR') if payments else 'EUR'
    
    # Find date range
    paid_dates = [p.get('paid_at') for p in payments if p.get('paid_at')]
    date_range = None
    
    if paid_dates:
        sorted_dates = sorted(paid_dates)
        date_range = {
            'first_payment': sorted_dates[0],
            'last_payment': sorted_dates[-1]
        }
    
    summary = {
        'total_payments': len(payments),
        'total_amount': float(total_amount),
        'currency': currency
    }
    
    if date_range:
        summary['date_range'] = date_range
    
    return summary


def calculate_analytics_summary(payments, unpaid_boats):
    """
    Calculate analytics summary for admin dashboard
    
    Args:
        payments: List of all payment records
        unpaid_boats: List of all unpaid boat records
    
    Returns:
        dict: Analytics summary
    """
    total_revenue = calculate_total_paid(payments)
    outstanding_balance = calculate_outstanding_balance(unpaid_boats)
    
    # Count unique payers
    unique_payers = set()
    total_boats_paid = 0
    
    for payment in payments:
        if payment.get('status') == 'succeeded':
            team_manager_id = payment.get('team_manager_id')
            if team_manager_id:
                unique_payers.add(team_manager_id)
            
            boat_ids = payment.get('boat_registration_ids', [])
            total_boats_paid += len(boat_ids)
    
    return {
        'total_revenue': float(total_revenue),
        'total_payments': len(payments),
        'total_boats_paid': total_boats_paid,
        'unique_payers': len(unique_payers),
        'outstanding_balance': float(outstanding_balance),
        'currency': 'EUR'
    }


def group_payments_by_period(payments, group_by='day'):
    """
    Group payments by time period
    
    Args:
        payments: List of payment records
        group_by: 'day', 'week', or 'month'
    
    Returns:
        list: Grouped payment data
    """
    from collections import defaultdict
    
    grouped = defaultdict(lambda: {'payment_count': 0, 'total_amount': Decimal('0')})
    
    for payment in payments:
        if payment.get('status') != 'succeeded':
            continue
        
        paid_at = payment.get('paid_at')
        if not paid_at:
            continue
        
        # Parse date
        try:
            dt = datetime.fromisoformat(paid_at.replace('Z', '+00:00'))
        except:
            continue
        
        # Determine period key
        if group_by == 'day':
            period = dt.strftime('%Y-%m-%d')
        elif group_by == 'week':
            period = dt.strftime('%Y-W%W')
        elif group_by == 'month':
            period = dt.strftime('%Y-%m')
        else:
            period = dt.strftime('%Y-%m-%d')
        
        # Aggregate
        amount = payment.get('amount', 0)
        if isinstance(amount, (int, float)):
            amount = Decimal(str(amount))
        
        grouped[period]['payment_count'] += 1
        grouped[period]['total_amount'] += amount
    
    # Convert to list and sort
    result = []
    for period, data in sorted(grouped.items()):
        result.append({
            'period': period,
            'payment_count': data['payment_count'],
            'total_amount': float(data['total_amount'])
        })
    
    return result


def rank_top_payers(payments, limit=10):
    """
    Rank team managers by total amount paid
    
    Args:
        payments: List of payment records
        limit: Maximum number of top payers to return
    
    Returns:
        list: Top payers with rankings
    """
    from collections import defaultdict
    
    payers = defaultdict(lambda: {
        'total_paid': Decimal('0'),
        'payment_count': 0,
        'boat_count': 0
    })
    
    for payment in payments:
        if payment.get('status') != 'succeeded':
            continue
        
        team_manager_id = payment.get('team_manager_id')
        if not team_manager_id:
            continue
        
        amount = payment.get('amount', 0)
        if isinstance(amount, (int, float)):
            amount = Decimal(str(amount))
        
        boat_ids = payment.get('boat_registration_ids', [])
        
        payers[team_manager_id]['total_paid'] += amount
        payers[team_manager_id]['payment_count'] += 1
        payers[team_manager_id]['boat_count'] += len(boat_ids)
    
    # Convert to list and sort by total paid
    result = []
    for team_manager_id, data in payers.items():
        result.append({
            'team_manager_id': team_manager_id,
            'total_paid': float(data['total_paid']),
            'payment_count': data['payment_count'],
            'boat_count': data['boat_count']
        })
    
    result.sort(key=lambda x: x['total_paid'], reverse=True)
    
    return result[:limit]
