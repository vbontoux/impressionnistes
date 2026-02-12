"""
Unit tests for shared payment utilities
Tests payment_queries, payment_calculations, and payment_formatters
"""
import pytest
from decimal import Decimal
from datetime import datetime

# Import utilities from Lambda layer
import sys
sys.path.insert(0, 'functions/layer/python')

from payment_calculations import (
    calculate_total_paid,
    calculate_payment_summary_stats,
    count_boats_in_payments
)
from payment_formatters import (
    format_payment_list_response,
    format_currency,
    sort_payments_by_field
)


class TestPaymentCalculations:
    """Test payment calculation functions"""
    
    def test_calculate_total_paid_basic(self):
        """Test total paid calculation with basic case"""
        payments = [
            {'amount': Decimal('100.00'), 'status': 'succeeded'},
            {'amount': Decimal('50.00'), 'status': 'succeeded'},
            {'amount': Decimal('25.50'), 'status': 'succeeded'}
        ]
        
        total = calculate_total_paid(payments)
        
        assert total == Decimal('175.50')
    
    def test_calculate_total_paid_empty(self):
        """Test total paid with empty list"""
        payments = []
        
        total = calculate_total_paid(payments)
        
        assert total == Decimal('0')
    
    def test_count_boats_in_payments(self):
        """Test counting boats across payments"""
        payments = [
            {'boat_registration_ids': ['boat-1', 'boat-2'], 'status': 'succeeded'},
            {'boat_registration_ids': ['boat-3'], 'status': 'succeeded'},
            {'boat_registration_ids': [], 'status': 'succeeded'}
        ]
        
        count = count_boats_in_payments(payments)
        
        assert count == 3


class TestPaymentFormatters:
    """Test payment formatting functions"""
    
    def test_format_payment_response(self):
        """Test formatting a single payment record"""
        payment = {
            'payment_id': 'pay-123',
            'stripe_payment_intent_id': 'pi_xxx',
            'amount': Decimal('100.00'),
            'currency': 'EUR',
            'paid_at': '2026-01-15T10:30:00Z',
            'boat_registration_ids': ['boat-1', 'boat-2'],
            'stripe_receipt_url': 'https://stripe.com/receipt',
            'status': 'succeeded'
        }
        
        formatted = format_payment_list_response([payment])[0]
        
        assert formatted['payment_id'] == 'pay-123'
        assert formatted['amount'] == 100.00
        assert formatted['boat_count'] == 2
        assert formatted['currency'] == 'EUR'
    
    def test_format_currency(self):
        """Test currency formatting"""
        assert format_currency(Decimal('100.00')) == '100.00'
        assert format_currency(Decimal('100.5')) == '100.50'
        assert format_currency(100.123) == '100.12'
    
    def test_sort_payments_by_field(self):
        """Test sorting payments by date"""
        payments = [
            {'paid_at': '2026-01-15T10:00:00Z', 'amount': 100},
            {'paid_at': '2026-01-14T10:00:00Z', 'amount': 50},
            {'paid_at': '2026-01-16T10:00:00Z', 'amount': 75}
        ]
        
        sorted_payments = sort_payments_by_field(payments, 'paid_at', reverse=True)
        
        assert sorted_payments[0]['paid_at'] == '2026-01-16T10:00:00Z'
        assert sorted_payments[1]['paid_at'] == '2026-01-15T10:00:00Z'
        assert sorted_payments[2]['paid_at'] == '2026-01-14T10:00:00Z'
