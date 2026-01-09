"""
Property-based tests for rental request state transitions

Feature: boat-rental-refactoring
Property 25: Valid Status Transitions

For any rental request, status transitions should only occur in these valid paths:
- pending → accepted (via admin accept)
- pending → cancelled (via team manager cancel or admin reject)
- accepted → paid (via payment completion)
- accepted → cancelled (via team manager cancel)
All other transitions should be rejected.

Validates: Appendix A (Status Transitions)
"""
import pytest
import json
from decimal import Decimal
from moto import mock_dynamodb
from functions.shared.rental_request_state import (
    is_valid_transition,
    validate_transition,
    validate_accept_transition,
    validate_payment_transition,
    validate_cancellation_transition,
    validate_update_assignment_details,
    VALID_TRANSITIONS
)


# Test data for all possible status combinations
ALL_STATUSES = ['pending', 'accepted', 'paid', 'cancelled', 'rejected']


class TestStateTransitionValidation:
    """Test the state transition validation functions"""
    
    @pytest.mark.parametrize('from_status,to_status,expected', [
        # Valid transitions
        ('pending', 'accepted', True),
        ('pending', 'cancelled', True),
        ('pending', 'rejected', True),
        ('accepted', 'paid', True),
        ('accepted', 'cancelled', True),
        
        # Invalid transitions - from pending
        ('pending', 'paid', False),
        ('pending', 'pending', False),
        
        # Invalid transitions - from accepted
        ('accepted', 'pending', False),
        ('accepted', 'accepted', False),
        ('accepted', 'rejected', False),
        
        # Invalid transitions - from paid (final state)
        ('paid', 'pending', False),
        ('paid', 'accepted', False),
        ('paid', 'cancelled', False),
        ('paid', 'rejected', False),
        ('paid', 'paid', False),
        
        # Invalid transitions - from cancelled (final state)
        ('cancelled', 'pending', False),
        ('cancelled', 'accepted', False),
        ('cancelled', 'paid', False),
        ('cancelled', 'rejected', False),
        ('cancelled', 'cancelled', False),
        
        # Invalid transitions - from rejected (final state)
        ('rejected', 'pending', False),
        ('rejected', 'accepted', False),
        ('rejected', 'paid', False),
        ('rejected', 'cancelled', False),
        ('rejected', 'rejected', False),
    ])
    def test_property_25_valid_status_transitions(self, from_status, to_status, expected):
        """
        Property 25: Valid Status Transitions
        
        Test that is_valid_transition correctly identifies valid and invalid transitions
        """
        result = is_valid_transition(from_status, to_status)
        assert result == expected, (
            f"Transition {from_status} → {to_status} should be "
            f"{'valid' if expected else 'invalid'}"
        )
    
    @pytest.mark.parametrize('from_status,to_status', [
        ('pending', 'accepted'),
        ('pending', 'cancelled'),
        ('pending', 'rejected'),
        ('accepted', 'paid'),
        ('accepted', 'cancelled'),
    ])
    def test_valid_transitions_have_no_error(self, from_status, to_status):
        """Valid transitions should return (True, None)"""
        is_valid, error_message = validate_transition(from_status, to_status)
        assert is_valid is True
        assert error_message is None
    
    @pytest.mark.parametrize('from_status,to_status', [
        ('pending', 'paid'),
        ('accepted', 'pending'),
        ('accepted', 'rejected'),
        ('paid', 'accepted'),
        ('paid', 'cancelled'),
        ('paid', 'rejected'),
        ('cancelled', 'pending'),
        ('cancelled', 'accepted'),
        ('rejected', 'pending'),
        ('rejected', 'accepted'),
    ])
    def test_invalid_transitions_have_error_message(self, from_status, to_status):
        """Invalid transitions should return (False, error_message)"""
        is_valid, error_message = validate_transition(from_status, to_status)
        assert is_valid is False
        assert error_message is not None
        assert isinstance(error_message, str)
        assert len(error_message) > 0
    
    def test_paid_requests_are_immutable(self):
        """Paid requests cannot transition to any other status"""
        for to_status in ALL_STATUSES:
            is_valid, error_message = validate_transition('paid', to_status)
            assert is_valid is False
            assert 'immutable' in error_message.lower() or 'no transitions' in error_message.lower()
    
    def test_cancelled_requests_are_immutable(self):
        """Cancelled requests cannot transition to any other status"""
        for to_status in ALL_STATUSES:
            is_valid, error_message = validate_transition('cancelled', to_status)
            assert is_valid is False
    
    def test_rejected_requests_are_immutable(self):
        """Rejected requests cannot transition to any other status"""
        for to_status in ALL_STATUSES:
            is_valid, error_message = validate_transition('rejected', to_status)
            assert is_valid is False


class TestAcceptTransitionValidation:
    """Test validation for accept transitions (pending → accepted)"""
    
    def test_accept_valid_from_pending(self):
        """Accept should be valid from pending status"""
        is_valid, error_message = validate_accept_transition('pending')
        assert is_valid is True
        assert error_message is None
    
    @pytest.mark.parametrize('status', ['accepted', 'paid', 'cancelled', 'rejected'])
    def test_accept_invalid_from_other_statuses(self, status):
        """Accept should be invalid from non-pending statuses"""
        is_valid, error_message = validate_accept_transition(status)
        assert is_valid is False
        assert error_message is not None
        assert 'accept' in error_message.lower()


class TestPaymentTransitionValidation:
    """Test validation for payment transitions (accepted → paid)"""
    
    def test_payment_valid_from_accepted(self):
        """Payment should be valid from accepted status"""
        is_valid, error_message = validate_payment_transition('accepted')
        assert is_valid is True
        assert error_message is None
    
    @pytest.mark.parametrize('status', ['pending', 'paid', 'cancelled', 'rejected'])
    def test_payment_invalid_from_other_statuses(self, status):
        """Payment should be invalid from non-accepted statuses"""
        is_valid, error_message = validate_payment_transition(status)
        assert is_valid is False
        assert error_message is not None


class TestCancellationTransitionValidation:
    """Test validation for cancellation transitions"""
    
    @pytest.mark.parametrize('status', ['pending', 'accepted'])
    def test_cancellation_valid_from_pending_or_accepted(self, status):
        """Cancellation should be valid from pending or accepted"""
        is_valid, error_message = validate_cancellation_transition(status)
        assert is_valid is True
        assert error_message is None
    
    @pytest.mark.parametrize('status', ['paid', 'cancelled', 'rejected'])
    def test_cancellation_invalid_from_final_statuses(self, status):
        """Cancellation should be invalid from paid, cancelled, or rejected"""
        is_valid, error_message = validate_cancellation_transition(status)
        assert is_valid is False
        assert error_message is not None
        assert 'cancel' in error_message.lower()


class TestAssignmentDetailsUpdateValidation:
    """Test validation for updating assignment details"""
    
    def test_update_assignment_valid_from_accepted(self):
        """Assignment details update should be valid from accepted status"""
        is_valid, error_message = validate_update_assignment_details('accepted')
        assert is_valid is True
        assert error_message is None
    
    @pytest.mark.parametrize('status', ['pending', 'paid', 'cancelled', 'rejected'])
    def test_update_assignment_invalid_from_other_statuses(self, status):
        """Assignment details update should be invalid from non-accepted statuses"""
        is_valid, error_message = validate_update_assignment_details(status)
        assert is_valid is False
        assert error_message is not None
        assert 'assignment details' in error_message.lower()


# Note: End-to-end tests for state transitions are covered by existing
# Lambda function tests in:
# - test_rental_request_acceptance.py (Property 14: Accept Only Works on Pending Requests)
# - test_rental_request_assignment_update.py (Property 15: Assignment Update Preserves Status)
# - test_rental_request_cancellation.py (Property 20: Cancellation Only for Pending or Accepted)
# - test_rental_request_payment.py (Property 16, 17, 19: Payment transitions and immutability)
# - test_rental_request_rejection.py (Property 23: Rejection Only for Pending)
#
# The unit tests above provide comprehensive coverage of the state transition validation logic
