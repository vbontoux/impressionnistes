"""
Rental request state transition validation

This module provides centralized validation for rental request status transitions
to ensure all state changes follow the allowed paths defined in the requirements.

Valid transitions (Appendix A):
- pending → accepted (admin accepts)
- pending → cancelled (team manager cancels)
- pending → rejected (admin rejects)
- accepted → paid (team manager completes payment)
- accepted → cancelled (team manager cancels)
- accepted → rejected (admin rejects if not yet paid)
- paid → (no transitions - final state)
- cancelled → (no transitions - final state)
- rejected → (no transitions - final state)
"""
import logging

logger = logging.getLogger()


# Valid status values
VALID_STATUSES = ['pending', 'accepted', 'paid', 'cancelled', 'rejected']

# Valid status transitions: {from_status: [to_status1, to_status2, ...]}
VALID_TRANSITIONS = {
    'pending': ['accepted', 'cancelled', 'rejected'],
    'accepted': ['paid', 'cancelled', 'rejected'],
    'paid': [],  # Final state - no transitions allowed
    'cancelled': [],  # Final state - no transitions allowed
    'rejected': []  # Final state - no transitions allowed
}


def is_valid_status(status: str) -> bool:
    """
    Check if a status value is valid
    
    Args:
        status: Status string to validate
        
    Returns:
        True if status is valid, False otherwise
    """
    return status in VALID_STATUSES


def is_valid_transition(from_status: str, to_status: str) -> bool:
    """
    Check if a status transition is valid
    
    Args:
        from_status: Current status
        to_status: Desired new status
        
    Returns:
        True if transition is valid, False otherwise
    """
    if not is_valid_status(from_status) or not is_valid_status(to_status):
        return False
    
    return to_status in VALID_TRANSITIONS.get(from_status, [])


def validate_transition(from_status: str, to_status: str, action: str = None) -> tuple:
    """
    Validate a status transition and return error message if invalid
    
    Args:
        from_status: Current status
        to_status: Desired new status
        action: Optional action description for better error messages
        
    Returns:
        tuple: (is_valid, error_message)
            is_valid: True if transition is valid
            error_message: None if valid, descriptive error message if invalid
    """
    # Check if statuses are valid
    if not is_valid_status(from_status):
        return False, f"Invalid current status: '{from_status}'"
    
    if not is_valid_status(to_status):
        return False, f"Invalid target status: '{to_status}'"
    
    # Check if transition is allowed
    if not is_valid_transition(from_status, to_status):
        # Provide specific error messages for common cases
        if from_status == 'paid':
            return False, f"Cannot {action or 'modify'} request with status 'paid'. Paid requests are immutable."
        elif from_status == 'cancelled':
            return False, f"Cannot {action or 'modify'} request with status 'cancelled'. Cancelled requests cannot be modified."
        elif from_status == 'rejected':
            return False, f"Cannot {action or 'modify'} request with status 'rejected'. Rejected requests cannot be modified."
        else:
            allowed = VALID_TRANSITIONS.get(from_status, [])
            if allowed:
                return False, f"Cannot transition from '{from_status}' to '{to_status}'. Allowed transitions: {', '.join(allowed)}"
            else:
                return False, f"Cannot transition from '{from_status}' to '{to_status}'. No transitions allowed from '{from_status}'."
    
    return True, None


def validate_accept_transition(current_status: str) -> tuple:
    """
    Validate that a request can be accepted (pending → accepted)
    
    Args:
        current_status: Current status of the request
        
    Returns:
        tuple: (is_valid, error_message)
    """
    return validate_transition(current_status, 'accepted', 'accept')


def validate_payment_transition(current_status: str) -> tuple:
    """
    Validate that a request can be paid (accepted → paid)
    
    Args:
        current_status: Current status of the request
        
    Returns:
        tuple: (is_valid, error_message)
    """
    return validate_transition(current_status, 'paid', 'pay for')


def validate_cancellation_transition(current_status: str) -> tuple:
    """
    Validate that a request can be cancelled (pending/accepted → cancelled)
    
    Args:
        current_status: Current status of the request
        
    Returns:
        tuple: (is_valid, error_message)
    """
    return validate_transition(current_status, 'cancelled', 'cancel')


def validate_update_assignment_details(current_status: str) -> tuple:
    """
    Validate that assignment details can be updated (must be accepted)
    
    Args:
        current_status: Current status of the request
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if current_status != 'accepted':
        if current_status == 'paid':
            return False, "Cannot update assignment details for request with status 'paid'. Paid requests are immutable."
        elif current_status == 'cancelled':
            return False, "Cannot update assignment details for request with status 'cancelled'."
        elif current_status == 'rejected':
            return False, "Cannot update assignment details for request with status 'rejected'."
        else:
            return False, f"Cannot update assignment details for request with status '{current_status}'. Only accepted requests can have assignment details updated."
    
    return True, None


def get_allowed_transitions(current_status: str) -> list:
    """
    Get list of allowed transitions from current status
    
    Args:
        current_status: Current status
        
    Returns:
        List of allowed target statuses
    """
    return VALID_TRANSITIONS.get(current_status, [])
