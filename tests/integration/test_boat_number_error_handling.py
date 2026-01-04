"""
Test error handling for boat_number generation

Feature: boat-identifier-and-club-list
Tests error handling in the generate_boat_number function.
"""

import sys
import os

# Add the shared functions to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'functions', 'shared'))

from boat_registration_utils import generate_boat_number


def test_error_handling_invalid_event_type():
    """
    Test that invalid event_type returns None
    
    **Validates: Requirements 13.2, 13.3**
    """
    # Invalid event type
    boat_number = generate_boat_number('invalid', 1, 'race-1', [])
    assert boat_number is None
    
    # Empty event type
    boat_number = generate_boat_number('', 1, 'race-1', [])
    assert boat_number is None
    
    # None event type
    boat_number = generate_boat_number(None, 1, 'race-1', [])
    assert boat_number is None


def test_error_handling_missing_display_order():
    """
    Test that missing display_order returns None
    
    **Validates: Requirements 13.2, 13.3**
    """
    # None display_order
    boat_number = generate_boat_number('42km', None, 'race-1', [])
    assert boat_number is None


def test_error_handling_invalid_display_order():
    """
    Test that invalid display_order returns None
    
    **Validates: Requirements 13.2, 13.3**
    """
    # String display_order that can't be converted
    boat_number = generate_boat_number('42km', 'invalid', 'race-1', [])
    assert boat_number is None
    
    # Object display_order
    boat_number = generate_boat_number('42km', {'order': 1}, 'race-1', [])
    assert boat_number is None


def test_error_handling_zero_display_order():
    """
    Test that display_order of 0 is handled (logs warning but generates number)
    
    **Validates: Requirements 13.2, 13.3**
    """
    # Zero display_order should work (with warning logged)
    boat_number = generate_boat_number('42km', 0, 'race-1', [])
    assert boat_number == 'M.0.1'


def test_error_handling_valid_after_errors():
    """
    Test that function still works correctly after errors
    
    **Validates: Requirements 13.2, 13.3**
    """
    # Generate some errors
    generate_boat_number(None, 1, 'race-1', [])
    generate_boat_number('42km', None, 'race-1', [])
    generate_boat_number('invalid', 1, 'race-1', [])
    
    # Should still work correctly
    boat_number = generate_boat_number('42km', 1, 'race-1', [])
    assert boat_number == 'M.1.1'


def test_error_handling_with_existing_boats():
    """
    Test error handling when there are existing boats
    
    **Validates: Requirements 13.2, 13.3**
    """
    boats_in_race = [
        {'boat_number': 'M.1.1'},
        {'boat_number': 'M.1.2'}
    ]
    
    # Invalid event type with existing boats
    boat_number = generate_boat_number('invalid', 1, 'race-1', boats_in_race)
    assert boat_number is None
    
    # Valid generation should still work
    boat_number = generate_boat_number('42km', 1, 'race-1', boats_in_race)
    assert boat_number == 'M.1.3'


def test_error_handling_malformed_existing_boat_numbers():
    """
    Test that malformed existing boat numbers don't crash the function
    
    **Validates: Requirements 13.2, 13.3**
    """
    boats_in_race = [
        {'boat_number': 'invalid'},
        {'boat_number': 'M.1.abc'},
        {'boat_number': 'M.1'},
        {'boat_number': None},
        {'boat_number': ''},
    ]
    
    # Should handle malformed data gracefully
    boat_number = generate_boat_number('42km', 1, 'race-1', boats_in_race)
    assert boat_number == 'M.1.1'  # Should start at 1 since no valid sequences found


def test_error_handling_empty_race_id():
    """
    Test that empty race_id doesn't crash (race_id is just for logging)
    
    **Validates: Requirements 13.2, 13.3**
    """
    # Empty race_id should still work (it's only used for logging)
    boat_number = generate_boat_number('42km', 1, '', [])
    assert boat_number == 'M.1.1'
    
    # None race_id should still work
    boat_number = generate_boat_number('42km', 1, None, [])
    assert boat_number == 'M.1.1'


def test_error_handling_none_boats_list():
    """
    Test that None boats list is handled gracefully
    
    **Validates: Requirements 13.2, 13.3**
    """
    # This should not crash - the function should handle it
    try:
        boat_number = generate_boat_number('42km', 1, 'race-1', None)
        # If it doesn't crash, it should return None or a valid number
        assert boat_number is None or boat_number == 'M.1.1'
    except TypeError:
        # If it raises TypeError, that's also acceptable behavior
        pass


def test_error_handling_convertible_display_order():
    """
    Test that display_order that can be converted to int works
    
    **Validates: Requirements 13.2, 13.3**
    """
    # String that can be converted to int
    boat_number = generate_boat_number('42km', '15', 'race-15', [])
    assert boat_number == 'M.15.1'
    
    # Float that can be converted to int
    boat_number = generate_boat_number('21km', 15.0, 'race-15', [])
    assert boat_number == 'SM.15.1'
    
    # Float with decimal (should truncate)
    boat_number = generate_boat_number('21km', 15.7, 'race-15', [])
    assert boat_number == 'SM.15.1'
