"""
Unit Tests for Boat Club Calculation

Feature: boat-club-display
Tests the calculate_boat_club_info function with various scenarios.

Option A: Always show team manager's club first with crew composition context
"""

import sys
import os

# Add the functions/shared directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'functions', 'shared'))

from boat_registration_utils import calculate_boat_club_info


# Property 1: Single Club Display - Team Manager's Club
def test_property_1_single_club_display_team_manager():
    """
    Property 1: Single Club Display - Team Manager's Club
    
    When all crew members are from the team manager's club,
    display should show just the club name (no suffix)
    
    **Validates: Requirements 1.1**
    """
    # Test with RCPM
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': 'RCPM'},
        {'crew_member_id': 'member-2', 'club_affiliation': 'RCPM'},
        {'crew_member_id': 'member-3', 'club_affiliation': 'RCPM'}
    ]
    result = calculate_boat_club_info(crew_members, 'RCPM')
    assert result['boat_club_display'] == 'RCPM'
    assert result['club_list'] == ['RCPM']
    
    # Test with Club Elite
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': 'Club Elite'},
        {'crew_member_id': 'member-2', 'club_affiliation': 'Club Elite'}
    ]
    result = calculate_boat_club_info(crew_members, 'Club Elite')
    assert result['boat_club_display'] == 'Club Elite'
    assert result['club_list'] == ['Club Elite']


def test_property_1_case_insensitive():
    """
    Property 1: Case Insensitive Variant
    
    When crew members have the same club in different cases,
    they should be treated as the same club
    
    **Validates: Requirements 1.1, 1.5**
    """
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': 'RCPM'},
        {'crew_member_id': 'member-2', 'club_affiliation': 'rcpm'},
        {'crew_member_id': 'member-3', 'club_affiliation': 'Rcpm'}
    ]
    result = calculate_boat_club_info(crew_members, 'RCPM')
    
    # Should treat as single club
    assert result['boat_club_display'] == 'RCPM'
    assert len(result['club_list']) == 1
    assert result['club_list'][0].upper() == 'RCPM'


# Property 2: Multi-Club Display
def test_property_2_multi_club_display():
    """
    Property 2: Multi-Club Display
    
    When crew members are from multiple clubs,
    display should show comma-separated list of clubs
    
    **Validates: Requirements 1.1, 1.2**
    """
    # Test with 2 clubs
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': 'RCPM'},
        {'crew_member_id': 'member-2', 'club_affiliation': 'Club Elite'}
    ]
    result = calculate_boat_club_info(crew_members, 'RCPM')
    assert result['boat_club_display'] == 'Club Elite, RCPM'  # Alphabetically sorted
    assert len(result['club_list']) == 2
    assert 'RCPM' in result['club_list']
    assert 'Club Elite' in result['club_list']
    assert result['is_multi_club_crew'] is True
    
    # Test with 3 clubs
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': 'RCPM'},
        {'crew_member_id': 'member-2', 'club_affiliation': 'Club Elite'},
        {'crew_member_id': 'member-3', 'club_affiliation': 'SN Versailles'}
    ]
    result = calculate_boat_club_info(crew_members, 'RCPM')
    assert result['boat_club_display'] == 'Club Elite, RCPM, SN Versailles'  # Alphabetically sorted
    assert len(result['club_list']) == 3
    assert result['is_multi_club_crew'] is True


# Property 3: External Crew Display
def test_property_3_external_crew_display():
    """
    Property 3: Single Club Display - External Crew
    
    When all crew are from one club different from team manager,
    display should show that club (not team manager's club)
    
    **Validates: Requirements 1.1, 1.3**
    """
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': 'Club Elite'},
        {'crew_member_id': 'member-2', 'club_affiliation': 'Club Elite'},
        {'crew_member_id': 'member-3', 'club_affiliation': 'Club Elite'}
    ]
    result = calculate_boat_club_info(crew_members, 'RCPM')
    
    assert result['boat_club_display'] == 'Club Elite'
    assert result['club_list'] == ['Club Elite']
    assert result['is_multi_club_crew'] is False


# Property 4: Empty Boat Fallback
def test_property_4_empty_boat_fallback():
    """
    Property 4: Empty Boat Fallback
    
    When no crew members are assigned,
    display should show team manager's club
    
    **Validates: Requirements 1.4**
    """
    crew_members = []
    result = calculate_boat_club_info(crew_members, 'RCPM')
    
    assert result['boat_club_display'] == 'RCPM'
    assert result['club_list'] == ['RCPM']
    
    # Test with different club
    result = calculate_boat_club_info([], 'Club Elite')
    assert result['boat_club_display'] == 'Club Elite'
    assert result['club_list'] == ['Club Elite']


# Property 5: Club List Uniqueness
def test_property_5_club_list_uniqueness():
    """
    Property 5: Club List Uniqueness
    
    Club list should contain each club exactly once,
    even if multiple crew members are from the same club
    
    **Validates: Requirements 2.1, 2.2**
    """
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': 'RCPM'},
        {'crew_member_id': 'member-2', 'club_affiliation': 'Club Elite'},
        {'crew_member_id': 'member-3', 'club_affiliation': 'RCPM'},  # Duplicate
        {'crew_member_id': 'member-4', 'club_affiliation': 'Club Elite'},  # Duplicate
        {'crew_member_id': 'member-5', 'club_affiliation': 'SN Versailles'}
    ]
    result = calculate_boat_club_info(crew_members, 'RCPM')
    
    # Should have exactly 3 unique clubs
    assert len(result['club_list']) == 3
    assert result['club_list'].count('RCPM') == 1
    assert result['club_list'].count('Club Elite') == 1
    assert result['club_list'].count('SN Versailles') == 1


# Property 6: Club List Sorting
def test_property_6_club_list_sorting():
    """
    Property 6: Club List Sorting
    
    Club list should be sorted alphabetically (case-insensitive)
    
    **Validates: Requirements 2.4**
    """
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': 'SN Versailles'},
        {'crew_member_id': 'member-2', 'club_affiliation': 'Aviron Bayonnais'},
        {'crew_member_id': 'member-3', 'club_affiliation': 'RCPM'},
        {'crew_member_id': 'member-4', 'club_affiliation': 'Club Elite'}
    ]
    result = calculate_boat_club_info(crew_members, 'RCPM')
    
    # Should be sorted alphabetically
    expected_order = ['Aviron Bayonnais', 'Club Elite', 'RCPM', 'SN Versailles']
    assert result['club_list'] == expected_order


# Property 10: Case Insensitive Comparison
def test_property_10_case_insensitive_comparison():
    """
    Property 10: Case Insensitive Comparison
    
    Clubs that differ only in case should be treated as the same club
    
    **Validates: Requirements 1.5**
    """
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': 'RCPM'},
        {'crew_member_id': 'member-2', 'club_affiliation': 'rcpm'},
        {'crew_member_id': 'member-3', 'club_affiliation': 'Rcpm'},
        {'crew_member_id': 'member-4', 'club_affiliation': 'RcPm'}
    ]
    result = calculate_boat_club_info(crew_members, 'RCPM')
    
    # All should be treated as same club
    assert result['boat_club_display'] == 'RCPM'
    assert len(result['club_list']) == 1


# Edge Cases
def test_empty_club_affiliations():
    """Test that empty and null club affiliations are excluded"""
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': 'RCPM'},
        {'crew_member_id': 'member-2', 'club_affiliation': ''},  # Empty
        {'crew_member_id': 'member-3', 'club_affiliation': None},  # Null
        {'crew_member_id': 'member-4', 'club_affiliation': '   '}  # Whitespace
    ]
    result = calculate_boat_club_info(crew_members, 'RCPM')
    
    # Should only count RCPM
    assert result['boat_club_display'] == 'RCPM'
    assert result['club_list'] == ['RCPM']


def test_whitespace_handling():
    """Test that whitespace is trimmed from club names"""
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': '  RCPM  '},
        {'crew_member_id': 'member-2', 'club_affiliation': 'RCPM'}
    ]
    result = calculate_boat_club_info(crew_members, '  RCPM  ')
    
    # Should treat as same club after trimming
    assert result['boat_club_display'] == 'RCPM'
    assert len(result['club_list']) == 1



# ============================================================================
# Unit Tests for Edge Cases
# ============================================================================

def test_edge_case_all_empty_clubs():
    """
    Edge Case: All crew members have empty club affiliations
    
    When all crew members have empty or null club_affiliation, the system
    should use the team manager's club
    
    **Validates: Requirements 9.3**
    """
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': ''},
        {'crew_member_id': 'member-2', 'club_affiliation': None},
        {'crew_member_id': 'member-3', 'club_affiliation': '   '},  # Whitespace only
    ]
    
    result = calculate_boat_club_info(crew_members, 'RCPM')
    
    assert result['boat_club_display'] == 'RCPM'
    assert result['club_list'] == ['RCPM']


def test_edge_case_null_vs_empty_string():
    """
    Edge Case: Null vs empty string handling
    
    The system should treat null and empty string as equivalent (both excluded)
    
    **Validates: Requirements 9.3**
    """
    # Mix of null and empty strings
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': None},
        {'crew_member_id': 'member-2', 'club_affiliation': ''},
        {'crew_member_id': 'member-3', 'club_affiliation': 'Club Elite'},
    ]
    
    result = calculate_boat_club_info(crew_members, 'RCPM')
    
    # Should show only Club Elite (simplified format)
    assert result['boat_club_display'] == 'Club Elite'
    assert result['club_list'] == ['Club Elite']
    assert result['is_multi_club_crew'] is False


def test_edge_case_whitespace_trimming():
    """
    Edge Case: Whitespace trimming
    
    The system should trim whitespace from club names
    
    **Validates: Requirements 9.3**
    """
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': '  RCPM  '},
        {'crew_member_id': 'member-2', 'club_affiliation': 'RCPM'},
        {'crew_member_id': 'member-3', 'club_affiliation': '   RCPM'},
    ]
    
    result = calculate_boat_club_info(crew_members, 'RCPM')
    
    # All should be treated as the same club (RCPM)
    assert result['boat_club_display'] == 'RCPM'
    assert len(result['club_list']) == 1
    assert result['club_list'][0].strip() == 'RCPM'


def test_edge_case_single_crew_member():
    """
    Edge Case: Single crew member (e.g., only a coxswain)
    
    When a boat has only one crew member assigned, the system should
    calculate club based on that single member
    
    **Validates: Requirements 9.5**
    """
    # Single crew member from Club Elite
    crew_members = [
        {'crew_member_id': 'cox-1', 'club_affiliation': 'Club Elite'},
    ]
    
    result = calculate_boat_club_info(crew_members, 'RCPM')
    
    # Should show only Club Elite (simplified format)
    assert result['boat_club_display'] == 'Club Elite'
    assert result['club_list'] == ['Club Elite']
    assert result['is_multi_club_crew'] is False


def test_edge_case_empty_team_manager_club():
    """
    Edge Case: Team manager has no club affiliation
    
    When team manager has empty club and no crew assigned
    """
    crew_members = []
    
    result = calculate_boat_club_info(crew_members, '')
    
    # Should handle empty team manager club gracefully
    assert result['boat_club_display'] == ''
    assert result['club_list'] == []


def test_edge_case_whitespace_only_team_manager_club():
    """
    Edge Case: Team manager club is whitespace only
    
    When team manager has whitespace-only club
    """
    crew_members = []
    
    result = calculate_boat_club_info(crew_members, '   ')
    
    # Should trim and handle empty
    assert result['boat_club_display'] == ''
    assert result['club_list'] == []


def test_edge_case_mixed_case_with_team_manager():
    """
    Edge Case: Mixed case clubs matching team manager
    
    Crew members with different case variations of team manager's club
    should all be treated as the same club
    
    **Validates: Requirements 9.4**
    """
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': 'rcpm'},
        {'crew_member_id': 'member-2', 'club_affiliation': 'RCPM'},
        {'crew_member_id': 'member-3', 'club_affiliation': 'Rcpm'},
    ]
    
    result = calculate_boat_club_info(crew_members, 'RCPM')
    
    # All should be treated as the same club, preserving first occurrence's case
    assert len(result['club_list']) == 1
    assert result['club_list'][0] == 'rcpm'  # First occurrence's case is preserved
    assert result['boat_club_display'] == 'rcpm'
    assert result['is_multi_club_crew'] is False


def test_edge_case_special_characters_in_club_names():
    """
    Edge Case: Club names with special characters
    
    Club names may contain hyphens, apostrophes, or other characters
    """
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': "Club d'Aviron"},
        {'crew_member_id': 'member-2', 'club_affiliation': 'Rowing-Club-Paris'},
    ]
    
    result = calculate_boat_club_info(crew_members, 'RCPM')
    
    # Should handle special characters correctly (simplified format)
    assert result['boat_club_display'] == "Club d'Aviron, Rowing-Club-Paris"
    assert len(result['club_list']) == 2
    assert "Club d'Aviron" in result['club_list']
    assert 'Rowing-Club-Paris' in result['club_list']
    assert result['is_multi_club_crew'] is True


def test_edge_case_very_long_club_name():
    """
    Edge Case: Very long club name
    
    System should handle long club names without truncation
    """
    long_club_name = 'Association Sportive de Rowing et Aviron de la Ville de Paris'
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': long_club_name},
    ]
    
    result = calculate_boat_club_info(crew_members, 'RCPM')
    
    # Should preserve full club name (simplified format)
    assert result['boat_club_display'] == long_club_name
    assert result['club_list'] == [long_club_name]
    assert result['is_multi_club_crew'] is False


def test_edge_case_numeric_club_names():
    """
    Edge Case: Club names with numbers
    
    Some clubs may have numbers in their names
    """
    crew_members = [
        {'crew_member_id': 'member-1', 'club_affiliation': 'Club 42'},
        {'crew_member_id': 'member-2', 'club_affiliation': 'Aviron 2000'},
    ]
    
    result = calculate_boat_club_info(crew_members, 'RCPM')
    
    # Should handle numeric club names (simplified format)
    assert result['boat_club_display'] == 'Aviron 2000, Club 42'  # Alphabetically sorted
    assert len(result['club_list']) == 2
    assert result['is_multi_club_crew'] is True
    # Should be sorted alphabetically
    assert result['club_list'] == ['Aviron 2000', 'Club 42']



# ============================================================================
# Schema Validation Tests
# ============================================================================

from validation import validate_boat_registration


def test_schema_boat_club_display_accepts_string():
    """
    Test that boat_club_display field accepts string values
    
    **Validates: Requirements 3.1**
    """
    boat_data = {
        'event_type': '42km',
        'boat_type': '4+',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ],
        'boat_club_display': 'RCPM'
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"
    assert 'boat_club_display' not in errors


def test_schema_boat_club_display_accepts_multi_club():
    """
    Test that boat_club_display accepts "Multi-Club" format
    
    **Validates: Requirements 3.1**
    """
    boat_data = {
        'event_type': '42km',
        'boat_type': '4+',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ],
        'boat_club_display': 'RCPM (Multi-Club)'
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"


def test_schema_boat_club_display_accepts_external_crew():
    """
    Test that boat_club_display accepts external crew format
    
    **Validates: Requirements 3.1**
    """
    boat_data = {
        'event_type': '42km',
        'boat_type': '4+',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ],
        'boat_club_display': 'RCPM (Club Elite)'
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"


def test_schema_club_list_accepts_array_of_strings():
    """
    Test that club_list field accepts array of strings
    
    **Validates: Requirements 3.2**
    """
    boat_data = {
        'event_type': '42km',
        'boat_type': '4+',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ],
        'club_list': ['RCPM', 'Club Elite', 'SN Versailles']
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"
    assert 'club_list' not in errors


def test_schema_club_list_accepts_single_club():
    """
    Test that club_list accepts single club in array
    
    **Validates: Requirements 3.2**
    """
    boat_data = {
        'event_type': '42km',
        'boat_type': '4+',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ],
        'club_list': ['RCPM']
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"


def test_schema_club_list_accepts_empty_array():
    """
    Test that club_list accepts empty array
    
    **Validates: Requirements 3.2**
    """
    boat_data = {
        'event_type': '42km',
        'boat_type': '4+',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ],
        'club_list': []
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"


def test_schema_fields_are_optional():
    """
    Test that boat_club_display and club_list are optional fields
    
    Boat registrations should validate successfully without these fields
    for backward compatibility
    
    **Validates: Requirements 3.1, 3.2**
    """
    boat_data = {
        'event_type': '42km',
        'boat_type': '4+',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ]
        # boat_club_display and club_list are omitted
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"


def test_schema_fields_accept_null():
    """
    Test that boat_club_display and club_list accept null values
    
    **Validates: Requirements 3.1, 3.2**
    """
    boat_data = {
        'event_type': '42km',
        'boat_type': '4+',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ],
        'boat_club_display': None,
        'club_list': None
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"


def test_schema_boat_club_display_respects_max_length():
    """
    Test that boat_club_display respects maxlength constraint (200 chars)
    
    **Validates: Requirements 3.1**
    """
    # Test with exactly 200 characters (should pass)
    boat_data = {
        'event_type': '42km',
        'boat_type': '4+',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ],
        'boat_club_display': 'A' * 200
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"
    
    # Test with 201 characters (should fail)
    boat_data['boat_club_display'] = 'A' * 201
    is_valid, errors = validate_boat_registration(boat_data)
    assert not is_valid
    assert 'boat_club_display' in errors


def test_schema_club_list_items_respect_max_length():
    """
    Test that club_list items respect maxlength constraint (100 chars each)
    
    **Validates: Requirements 3.2**
    """
    # Test with club name exactly 100 characters (should pass)
    boat_data = {
        'event_type': '42km',
        'boat_type': '4+',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ],
        'club_list': ['A' * 100, 'RCPM']
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"
    
    # Test with club name 101 characters (should fail)
    boat_data['club_list'] = ['A' * 101, 'RCPM']
    is_valid, errors = validate_boat_registration(boat_data)
    assert not is_valid
    assert 'club_list' in errors


# ============================================================================
# Schema Validation Tests - Boat Number
# ============================================================================

def test_schema_boat_number_accepts_valid_marathon_format():
    """
    Test that boat_number accepts valid marathon format
    
    **Validates: Requirements 4.1**
    """
    boat_data = {
        'event_type': '42km',
        'boat_type': 'skiff',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None}
        ],
        'boat_number': 'M.1.1'
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"
    assert 'boat_number' not in errors


def test_schema_boat_number_accepts_valid_semi_marathon_format():
    """
    Test that boat_number accepts valid semi-marathon format
    
    **Validates: Requirements 4.1**
    """
    boat_data = {
        'event_type': '21km',
        'boat_type': '4-',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None}
        ],
        'boat_number': 'SM.15.42'
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"
    assert 'boat_number' not in errors


def test_schema_boat_number_accepts_double_digit_display_order():
    """
    Test that boat_number accepts double-digit display orders
    
    **Validates: Requirements 4.1**
    """
    boat_data = {
        'event_type': '21km',
        'boat_type': '4-',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None}
        ],
        'boat_number': 'SM.55.999'
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"
    assert 'boat_number' not in errors


def test_schema_boat_number_accepts_four_digit_sequence():
    """
    Test that boat_number accepts up to 4-digit sequence numbers
    
    **Validates: Requirements 4.1**
    """
    boat_data = {
        'event_type': '42km',
        'boat_type': 'skiff',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None}
        ],
        'boat_number': 'M.1.9999'
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"
    assert 'boat_number' not in errors


def test_schema_boat_number_rejects_invalid_prefix():
    """
    Test that boat_number rejects invalid prefixes
    
    **Validates: Requirements 4.1**
    """
    boat_data = {
        'event_type': '42km',
        'boat_type': 'skiff',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None}
        ],
        'boat_number': 'X.1.1'  # Invalid prefix
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert not is_valid
    assert 'boat_number' in errors


def test_schema_boat_number_rejects_missing_components():
    """
    Test that boat_number rejects formats with missing components
    
    **Validates: Requirements 4.1**
    """
    boat_data = {
        'event_type': '42km',
        'boat_type': 'skiff',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None}
        ],
        'boat_number': 'M.1'  # Missing sequence
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert not is_valid
    assert 'boat_number' in errors


def test_schema_boat_number_rejects_non_numeric_components():
    """
    Test that boat_number rejects non-numeric display order or sequence
    
    **Validates: Requirements 4.1**
    """
    boat_data = {
        'event_type': '42km',
        'boat_type': 'skiff',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None}
        ],
        'boat_number': 'M.A.1'  # Non-numeric display order
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert not is_valid
    assert 'boat_number' in errors


def test_schema_boat_number_is_optional():
    """
    Test that boat_number is optional (can be null or omitted)
    
    **Validates: Requirements 4.1**
    """
    # Test with null
    boat_data = {
        'event_type': '42km',
        'boat_type': 'skiff',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None}
        ],
        'boat_number': None
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"
    assert 'boat_number' not in errors
    
    # Test without boat_number field
    boat_data = {
        'event_type': '42km',
        'boat_type': 'skiff',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None}
        ]
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"
    assert 'boat_number' not in errors


def test_schema_boat_number_respects_max_length():
    """
    Test that boat_number respects maximum length of 20 characters
    
    **Validates: Requirements 4.1**
    """
    boat_data = {
        'event_type': '42km',
        'boat_type': 'skiff',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None}
        ],
        'boat_number': 'M.1.1'  # 5 characters (valid)
    }
    
    is_valid, errors = validate_boat_registration(boat_data)
    assert is_valid, f"Validation failed: {errors}"
    
    # Test with 21 characters (should fail)
    boat_data['boat_number'] = 'M' * 21
    is_valid, errors = validate_boat_registration(boat_data)
    assert not is_valid
    assert 'boat_number' in errors
