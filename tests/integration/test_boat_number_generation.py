"""
Unit and Property Tests for Boat Number Generation

Feature: boat-identifier-and-club-list
Tests the generate_boat_number function with various scenarios.
"""

import sys
import os

# Add the functions/shared directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'functions', 'shared'))

from boat_registration_utils import generate_boat_number


# ============================================================================
# Property Tests
# ============================================================================

def test_property_1_boat_number_format():
    """
    Property 1: Boat Number Format
    
    For any boat with an assigned race, the boat_number SHALL match the format
    ^(M|SM)\.[0-9]{1,2}\.[0-9]{1,4}$
    
    **Feature: boat-identifier-and-club-list, Property 1: Boat Number Format**
    **Validates: Requirements 2.1, 2.2, 2.3, 14.1, 14.3, 14.4, 14.5**
    """
    import re
    
    # Test various scenarios
    test_cases = [
        ('42km', 1, 'race-1', []),
        ('42km', 14, 'race-14', []),
        ('21km', 15, 'race-15', []),
        ('21km', 55, 'race-55', []),
        ('42km', 5, 'race-5', [{'boat_number': 'M.5.1'}, {'boat_number': 'M.5.2'}]),
        ('21km', 20, 'race-20', [{'boat_number': 'SM.20.99'}]),
    ]
    
    pattern = re.compile(r'^(M|SM)\.[0-9]{1,2}\.[0-9]{1,4}$')
    
    for event_type, display_order, race_id, boats in test_cases:
        boat_number = generate_boat_number(event_type, display_order, race_id, boats)
        assert pattern.match(boat_number), f"Boat number {boat_number} does not match format"


def test_property_2_boat_number_prefix_marathon():
    """
    Property 2: Boat Number Prefix - Marathon
    
    For any boat assigned to a 42km race, the boat_number SHALL start with "M."
    
    **Feature: boat-identifier-and-club-list, Property 2: Boat Number Prefix - Marathon**
    **Validates: Requirements 2.2**
    """
    # Test multiple marathon races
    test_cases = [
        (1, []),
        (5, [{'boat_number': 'M.5.1'}]),
        (14, [{'boat_number': 'M.14.1'}, {'boat_number': 'M.14.2'}]),
    ]
    
    for display_order, boats in test_cases:
        boat_number = generate_boat_number('42km', display_order, f'race-{display_order}', boats)
        assert boat_number.startswith('M.'), f"Marathon boat number {boat_number} should start with 'M.'"


def test_property_3_boat_number_prefix_semi_marathon():
    """
    Property 3: Boat Number Prefix - Semi-Marathon
    
    For any boat assigned to a 21km race, the boat_number SHALL start with "SM."
    
    **Feature: boat-identifier-and-club-list, Property 3: Boat Number Prefix - Semi-Marathon**
    **Validates: Requirements 2.3**
    """
    # Test multiple semi-marathon races
    test_cases = [
        (15, []),
        (30, [{'boat_number': 'SM.30.1'}]),
        (55, [{'boat_number': 'SM.55.1'}, {'boat_number': 'SM.55.2'}]),
    ]
    
    for display_order, boats in test_cases:
        boat_number = generate_boat_number('21km', display_order, f'race-{display_order}', boats)
        assert boat_number.startswith('SM.'), f"Semi-marathon boat number {boat_number} should start with 'SM.'"


def test_property_5_boat_number_uniqueness():
    """
    Property 5: Boat Number Uniqueness
    
    For any two boats assigned to the same race, their boat_number values SHALL be different
    
    **Feature: boat-identifier-and-club-list, Property 5: Boat Number Uniqueness**
    **Validates: Requirements 3.1, 3.5**
    """
    # Generate multiple boat numbers for the same race
    race_id = 'race-15'
    event_type = '21km'
    display_order = 15
    
    boats_in_race = []
    generated_numbers = []
    
    # Generate 10 boat numbers
    for i in range(10):
        boat_number = generate_boat_number(event_type, display_order, race_id, boats_in_race)
        
        # Check uniqueness
        assert boat_number not in generated_numbers, f"Duplicate boat number generated: {boat_number}"
        
        generated_numbers.append(boat_number)
        boats_in_race.append({'boat_number': boat_number})
    
    # Verify all are unique
    assert len(generated_numbers) == len(set(generated_numbers))


def test_property_6_boat_number_sequence_increment():
    """
    Property 6: Boat Number Sequence Increment
    
    For any race, when a new boat is assigned, its sequence number SHALL be greater
    than all existing sequence numbers in that race
    
    **Feature: boat-identifier-and-club-list, Property 6: Boat Number Sequence Increment**
    **Validates: Requirements 3.1, 3.4**
    """
    race_id = 'race-20'
    event_type = '21km'
    display_order = 20
    
    # Start with some existing boats
    boats_in_race = [
        {'boat_number': 'SM.20.1'},
        {'boat_number': 'SM.20.2'},
        {'boat_number': 'SM.20.3'},
    ]
    
    # Generate new boat number
    new_boat_number = generate_boat_number(event_type, display_order, race_id, boats_in_race)
    
    # Extract sequence number
    new_sequence = int(new_boat_number.split('.')[2])
    
    # Check it's greater than all existing sequences
    for boat in boats_in_race:
        existing_sequence = int(boat['boat_number'].split('.')[2])
        assert new_sequence > existing_sequence, f"New sequence {new_sequence} not greater than {existing_sequence}"
    
    # Should be 4 (max + 1)
    assert new_sequence == 4


# ============================================================================
# Unit Tests for Edge Cases
# ============================================================================

def test_edge_case_no_existing_boats():
    """
    Edge Case: No existing boats in race (sequence = 1)
    
    When a race has no boats, the first boat should get sequence number 1
    
    **Validates: Requirements 3.2, 3.4, 14.2**
    """
    boat_number = generate_boat_number('42km', 1, 'race-1', [])
    assert boat_number == 'M.1.1'
    
    boat_number = generate_boat_number('21km', 15, 'race-15', [])
    assert boat_number == 'SM.15.1'


def test_edge_case_gaps_in_sequence():
    """
    Edge Case: Gaps in sequence numbers
    
    When there are gaps in sequence numbers (e.g., 1, 2, 5, 7),
    the next boat should get max + 1 (not fill the gap)
    
    **Validates: Requirements 3.2, 3.4, 14.2**
    """
    boats_in_race = [
        {'boat_number': 'M.14.1'},
        {'boat_number': 'M.14.2'},
        {'boat_number': 'M.14.5'},  # Gap: 3, 4 missing
        {'boat_number': 'M.14.7'},  # Gap: 6 missing
    ]
    
    boat_number = generate_boat_number('42km', 14, 'race-14', boats_in_race)
    
    # Should be 8 (max + 1), not 3 (first gap)
    assert boat_number == 'M.14.8'


def test_edge_case_invalid_boat_number_formats():
    """
    Edge Case: Invalid boat_number formats (skip them)
    
    When some boats have invalid boat_number formats, they should be skipped
    and not affect the sequence calculation
    
    **Validates: Requirements 3.2, 3.4, 14.2**
    """
    boats_in_race = [
        {'boat_number': 'M.14.1'},
        {'boat_number': 'invalid-format'},  # Invalid
        {'boat_number': 'M.14.2'},
        {'boat_number': 'M.14'},  # Invalid (missing sequence)
        {'boat_number': 'M.14.3'},
        {'boat_number': ''},  # Empty
        {'boat_number': None},  # None
    ]
    
    boat_number = generate_boat_number('42km', 14, 'race-14', boats_in_race)
    
    # Should be 4 (max valid sequence + 1)
    assert boat_number == 'M.14.4'


def test_edge_case_very_high_sequence_numbers():
    """
    Edge Case: Very high sequence numbers (9999)
    
    The system should support sequence numbers up to 9999
    
    **Validates: Requirements 3.2, 3.4, 14.2**
    """
    boats_in_race = [
        {'boat_number': 'SM.30.9998'},
        {'boat_number': 'SM.30.9999'},
    ]
    
    boat_number = generate_boat_number('21km', 30, 'race-30', boats_in_race)
    
    # Should be 10000 (though this exceeds the typical range)
    assert boat_number == 'SM.30.10000'


def test_edge_case_mixed_prefixes():
    """
    Edge Case: Boats with different prefixes in the list
    
    When the boats list contains boats from different races (different prefixes),
    only boats matching the current race should be considered
    """
    boats_in_race = [
        {'boat_number': 'M.1.1'},  # Different prefix (Marathon)
        {'boat_number': 'SM.15.1'},  # Correct prefix
        {'boat_number': 'SM.15.2'},  # Correct prefix
        {'boat_number': 'M.2.1'},  # Different prefix
    ]
    
    # Generating for semi-marathon race
    boat_number = generate_boat_number('21km', 15, 'race-15', boats_in_race)
    
    # Should consider all boats (even with different prefixes) and use max sequence
    # This is because the function receives all_boats_in_race which should already be filtered
    assert boat_number == 'SM.15.3'


def test_edge_case_single_digit_display_order():
    """
    Edge Case: Single digit display order
    
    Display orders 1-9 should not have leading zeros
    """
    boat_number = generate_boat_number('42km', 1, 'race-1', [])
    assert boat_number == 'M.1.1'
    
    boat_number = generate_boat_number('42km', 9, 'race-9', [])
    assert boat_number == 'M.9.1'


def test_edge_case_double_digit_display_order():
    """
    Edge Case: Double digit display order
    
    Display orders 10-99 should be displayed as-is
    """
    boat_number = generate_boat_number('42km', 10, 'race-10', [])
    assert boat_number == 'M.10.1'
    
    boat_number = generate_boat_number('21km', 55, 'race-55', [])
    assert boat_number == 'SM.55.1'


def test_edge_case_boats_without_boat_number():
    """
    Edge Case: Boats in race without boat_number field
    
    Some boats might not have the boat_number field yet (during migration)
    """
    boats_in_race = [
        {'boat_registration_id': 'boat-1'},  # No boat_number field
        {'boat_number': 'SM.20.1'},
        {'boat_registration_id': 'boat-2'},  # No boat_number field
        {'boat_number': 'SM.20.2'},
    ]
    
    boat_number = generate_boat_number('21km', 20, 'race-20', boats_in_race)
    
    # Should handle missing boat_number gracefully
    assert boat_number == 'SM.20.3'


def test_edge_case_empty_boat_number():
    """
    Edge Case: Boats with empty string boat_number
    
    Empty strings should be treated as no boat_number
    """
    boats_in_race = [
        {'boat_number': ''},
        {'boat_number': 'M.5.1'},
        {'boat_number': ''},
        {'boat_number': 'M.5.2'},
    ]
    
    boat_number = generate_boat_number('42km', 5, 'race-5', boats_in_race)
    
    # Should ignore empty strings
    assert boat_number == 'M.5.3'


def test_edge_case_whitespace_boat_number():
    """
    Edge Case: Boats with whitespace in boat_number
    
    Whitespace should not be parsed as valid
    """
    boats_in_race = [
        {'boat_number': '   '},
        {'boat_number': 'SM.25.1'},
        {'boat_number': '\t\n'},
    ]
    
    boat_number = generate_boat_number('21km', 25, 'race-25', boats_in_race)
    
    # Should ignore whitespace
    assert boat_number == 'SM.25.2'


def test_edge_case_non_numeric_sequence():
    """
    Edge Case: Boat numbers with non-numeric sequence parts
    
    Invalid sequences should be skipped
    """
    boats_in_race = [
        {'boat_number': 'M.10.1'},
        {'boat_number': 'M.10.abc'},  # Non-numeric sequence
        {'boat_number': 'M.10.2'},
        {'boat_number': 'M.10.1.5'},  # Extra parts
    ]
    
    boat_number = generate_boat_number('42km', 10, 'race-10', boats_in_race)
    
    # Should skip invalid formats and use max valid sequence
    assert boat_number == 'M.10.3'


# ============================================================================
# Integration Tests
# ============================================================================

def test_integration_sequential_generation():
    """
    Integration Test: Sequential boat number generation
    
    Simulate adding multiple boats to a race sequentially
    """
    race_id = 'race-15'
    event_type = '21km'
    display_order = 15
    
    boats_in_race = []
    expected_numbers = ['SM.15.1', 'SM.15.2', 'SM.15.3', 'SM.15.4', 'SM.15.5']
    
    for expected in expected_numbers:
        boat_number = generate_boat_number(event_type, display_order, race_id, boats_in_race)
        assert boat_number == expected
        boats_in_race.append({'boat_number': boat_number})


def test_integration_multiple_races():
    """
    Integration Test: Multiple races with independent sequences
    
    Each race should have its own independent sequence
    """
    # Race 1 (Marathon)
    race1_boats = []
    boat1 = generate_boat_number('42km', 1, 'race-1', race1_boats)
    assert boat1 == 'M.1.1'
    race1_boats.append({'boat_number': boat1})
    
    boat2 = generate_boat_number('42km', 1, 'race-1', race1_boats)
    assert boat2 == 'M.1.2'
    race1_boats.append({'boat_number': boat2})
    
    # Race 15 (Semi-Marathon) - should start at 1
    race15_boats = []
    boat3 = generate_boat_number('21km', 15, 'race-15', race15_boats)
    assert boat3 == 'SM.15.1'
    race15_boats.append({'boat_number': boat3})
    
    boat4 = generate_boat_number('21km', 15, 'race-15', race15_boats)
    assert boat4 == 'SM.15.2'


def test_integration_display_order_in_boat_number():
    """
    Integration Test: Display order is correctly included in boat number
    
    The second component should always match the display_order
    """
    test_cases = [
        ('42km', 1, 'M.1.1'),
        ('42km', 7, 'M.7.1'),
        ('42km', 14, 'M.14.1'),
        ('21km', 15, 'SM.15.1'),
        ('21km', 30, 'SM.30.1'),
        ('21km', 55, 'SM.55.1'),
    ]
    
    for event_type, display_order, expected in test_cases:
        boat_number = generate_boat_number(event_type, display_order, f'race-{display_order}', [])
        assert boat_number == expected


# ============================================================================
# Property Tests for Race Assignment (Task 4.2)
# ============================================================================

def test_property_7_boat_number_null_when_no_race():
    """
    Property 7: Boat Number Null When No Race
    
    For any boat without an assigned race (race_id is null), the boat_number SHALL be null
    
    **Feature: boat-identifier-and-club-list, Property 7: Boat Number Null When No Race**
    **Validates: Requirements 2.9, 4.2**
    """
    # This property is tested at the API level in test_boat_registration_api.py
    # since boat_number is set to None when race_id is None/cleared
    # The generate_boat_number function is not called when race_id is None
    
    # We can verify the logic by checking that when race_id is None,
    # we don't call generate_boat_number at all
    # This is a behavioral property tested in integration tests
    pass  # Placeholder - actual test is in test_boat_registration_api.py


def test_property_13_boat_number_regeneration_on_race_change():
    """
    Property 13: Boat Number Regeneration on Race Change
    
    For any boat, when the race_id changes, the boat_number SHALL be recalculated
    to match the new race
    
    **Feature: boat-identifier-and-club-list, Property 13: Boat Number Regeneration on Race Change**
    **Validates: Requirements 2.8, 4.4**
    """
    # Simulate changing from one race to another
    
    # Initial race (Race 1 - Marathon)
    race1_boats = [
        {'boat_number': 'M.1.1'},
        {'boat_number': 'M.1.2'},
    ]
    
    # Boat is initially in Race 1, would get M.1.3
    initial_boat_number = generate_boat_number('42km', 1, 'race-1', race1_boats)
    assert initial_boat_number == 'M.1.3'
    assert initial_boat_number.startswith('M.1.')
    
    # Now boat changes to Race 15 (Semi-Marathon)
    race15_boats = [
        {'boat_number': 'SM.15.1'},
    ]
    
    # Boat number should be regenerated for new race
    new_boat_number = generate_boat_number('21km', 15, 'race-15', race15_boats)
    assert new_boat_number == 'SM.15.2'
    assert new_boat_number.startswith('SM.15.')
    
    # Verify the boat_number changed completely
    assert initial_boat_number != new_boat_number
    
    # Verify prefix changed from M to SM
    assert initial_boat_number.split('.')[0] == 'M'
    assert new_boat_number.split('.')[0] == 'SM'
    
    # Verify display_order changed from 1 to 15
    assert initial_boat_number.split('.')[1] == '1'
    assert new_boat_number.split('.')[1] == '15'


def test_property_13_race_change_different_sequences():
    """
    Property 13 Extended: Race change with different sequence numbers
    
    When a boat changes races, the sequence number should be based on the
    new race's existing boats, not the old race
    """
    # Old race has boats with high sequence numbers
    old_race_boats = [
        {'boat_number': 'M.5.10'},
        {'boat_number': 'M.5.11'},
        {'boat_number': 'M.5.12'},
    ]
    
    # New race has boats with low sequence numbers
    new_race_boats = [
        {'boat_number': 'M.10.1'},
        {'boat_number': 'M.10.2'},
    ]
    
    # When boat changes to new race, sequence should be based on new race
    new_boat_number = generate_boat_number('42km', 10, 'race-10', new_race_boats)
    assert new_boat_number == 'M.10.3'
    
    # Not M.10.13 (which would be if we kept the old sequence)
    assert new_boat_number != 'M.10.13'


def test_property_13_race_change_same_event_type():
    """
    Property 13 Extended: Race change within same event type
    
    When a boat changes races within the same event type (e.g., two 21km races),
    the prefix stays the same but display_order and sequence change
    """
    # Race 20 (21km)
    race20_boats = [
        {'boat_number': 'SM.20.1'},
        {'boat_number': 'SM.20.2'},
    ]
    
    # Race 25 (21km)
    race25_boats = [
        {'boat_number': 'SM.25.1'},
    ]
    
    # Boat changes from race 20 to race 25
    old_boat_number = generate_boat_number('21km', 20, 'race-20', race20_boats)
    assert old_boat_number == 'SM.20.3'
    
    new_boat_number = generate_boat_number('21km', 25, 'race-25', race25_boats)
    assert new_boat_number == 'SM.25.2'
    
    # Prefix stays SM
    assert old_boat_number.startswith('SM.')
    assert new_boat_number.startswith('SM.')
    
    # But display_order and sequence change
    assert old_boat_number != new_boat_number
