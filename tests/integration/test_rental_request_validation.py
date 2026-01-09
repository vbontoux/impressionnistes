"""
Integration tests for rental request validation
Feature: boat-rental-refactoring, Property 1: Request Creation Validation
Validates: Requirements 1.1, 1.5, 1.6, 1.7
"""
import pytest
import sys
import os

# Add functions/shared to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/shared'))

from validation import validate_rental_request


# Feature: boat-rental-refactoring, Property 1: Request Creation Validation
# For any rental request creation attempt, the system should accept it if and only if
# all required fields (boat_type, desired_weight_range, request_comment) are present,
# boat_type is valid, request_comment is non-empty and ≤500 chars, and
# desired_weight_range is ≤50 chars.


@pytest.mark.parametrize("boat_type,desired_weight_range,request_comment,expected_valid", [
    # Valid cases
    ('skiff', '70-90kg', 'Need a skiff for race', True),
    ('4-', '75-85kg', 'Looking for a 4- boat', True),
    ('4+', '70-90kg', 'Need 4+ with cox', True),
    ('4x-', '80-95kg', 'Quad scull needed', True),
    ('4x+', '75-90kg', 'Quad with cox', True),
    ('8+', '70-85kg', 'Eight needed for race', True),
    ('8x+', '75-90kg', 'Octuple scull', True),
    
    # Valid edge cases - maximum lengths
    ('skiff', '70-90kg', 'x' * 500, True),  # Max comment length
    ('skiff', 'x' * 50, 'Valid comment', True),  # Max weight range length
    
    # Invalid boat types
    ('invalid', '70-90kg', 'Comment', False),
    ('2x', '70-90kg', 'Comment', False),
    ('8-', '70-90kg', 'Comment', False),
    ('', '70-90kg', 'Comment', False),
    
    # Invalid request_comment - empty or too long
    ('skiff', '70-90kg', '', False),
    ('skiff', '70-90kg', 'x' * 501, False),  # Over max length
    
    # Invalid desired_weight_range - too long
    ('skiff', 'x' * 51, 'Comment', False),  # Over max length
])
def test_property_1_request_creation_validation(boat_type, desired_weight_range, request_comment, expected_valid):
    """
    Property 1: Request Creation Validation
    
    Test that rental request validation accepts valid requests and rejects invalid ones
    based on required fields, boat_type validity, and length constraints.
    """
    # Arrange
    request_data = {
        'boat_type': boat_type,
        'desired_weight_range': desired_weight_range,
        'request_comment': request_comment
    }
    
    # Act
    is_valid, errors = validate_rental_request(request_data)
    
    # Assert
    assert is_valid == expected_valid, f"Expected valid={expected_valid}, got {is_valid}. Errors: {errors}"
    
    if expected_valid:
        assert errors == {}, f"Valid request should have no errors, got: {errors}"
    else:
        assert errors != {}, f"Invalid request should have errors"


@pytest.mark.parametrize("missing_field", ['boat_type', 'desired_weight_range', 'request_comment'])
def test_property_1_missing_required_fields(missing_field):
    """
    Property 1: Request Creation Validation - Missing Required Fields
    
    Test that validation fails when any required field is missing.
    """
    # Arrange
    request_data = {
        'boat_type': 'skiff',
        'desired_weight_range': '70-90kg',
        'request_comment': 'Need a boat'
    }
    
    # Remove the field being tested
    del request_data[missing_field]
    
    # Act
    is_valid, errors = validate_rental_request(request_data)
    
    # Assert
    assert is_valid is False, f"Request missing '{missing_field}' should be invalid"
    assert missing_field in errors, f"Error should mention missing field '{missing_field}'"


def test_property_1_all_fields_present():
    """
    Property 1: Request Creation Validation - All Valid Fields
    
    Test that a request with all valid fields passes validation.
    """
    # Arrange
    request_data = {
        'boat_type': '4+',
        'desired_weight_range': '75-85kg',
        'request_comment': 'Looking for a 4+ boat for the 21km race'
    }
    
    # Act
    is_valid, errors = validate_rental_request(request_data)
    
    # Assert
    assert is_valid is True, f"Valid request should pass. Errors: {errors}"
    assert errors == {}


def test_property_1_optional_fields_allowed():
    """
    Property 1: Request Creation Validation - Optional Fields
    
    Test that optional fields (status, assignment_details) are allowed but not required.
    """
    # Arrange
    request_data = {
        'boat_type': 'skiff',
        'desired_weight_range': '70-90kg',
        'request_comment': 'Need a skiff',
        'status': 'pending',
        'assignment_details': 'Boat #5, oars included'
    }
    
    # Act
    is_valid, errors = validate_rental_request(request_data)
    
    # Assert
    assert is_valid is True, f"Request with optional fields should be valid. Errors: {errors}"
    assert errors == {}
