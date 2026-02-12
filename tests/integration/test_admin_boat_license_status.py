"""
Integration tests for admin boat license status feature.

Tests the calculate_crew_license_status function and the admin boats endpoint
to ensure combined license verification status is calculated correctly.
"""
import pytest
import sys
import os

# Add functions directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions'))

from admin.admin_list_all_boats import calculate_crew_license_status


class TestCalculateCrewLicenseStatus:
    """Unit tests for calculate_crew_license_status function."""
    
    def test_all_verified_crew(self):
        """Test boat with all verified crew returns 'verified'."""
        boat = {
            'seats': [
                {
                    'crew_member_id': '1',
                    'crew_member_license_verification_status': 'verified_valid'
                },
                {
                    'crew_member_id': '2',
                    'crew_member_license_verification_status': 'verified_valid'
                }
            ]
        }
        assert calculate_crew_license_status(boat) == 'verified'
    
    def test_all_manually_verified_crew(self):
        """Test boat with all manually verified crew returns 'verified'."""
        boat = {
            'seats': [
                {
                    'crew_member_id': '1',
                    'crew_member_license_verification_status': 'manually_verified_valid'
                },
                {
                    'crew_member_id': '2',
                    'crew_member_license_verification_status': 'manually_verified_valid'
                }
            ]
        }
        assert calculate_crew_license_status(boat) == 'verified'
    
    def test_mixed_manual_auto_verified(self):
        """Test boat with mixed manual and auto verified crew returns 'verified'."""
        boat = {
            'seats': [
                {
                    'crew_member_id': '1',
                    'crew_member_license_verification_status': 'verified_valid'
                },
                {
                    'crew_member_id': '2',
                    'crew_member_license_verification_status': 'manually_verified_valid'
                },
                {
                    'crew_member_id': '3',
                    'crew_member_license_verification_status': 'verified_valid'
                }
            ]
        }
        assert calculate_crew_license_status(boat) == 'verified'
    
    def test_one_unverified_crew(self):
        """Test boat with one unverified crew returns 'invalid'."""
        boat = {
            'seats': [
                {
                    'crew_member_id': '1',
                    'crew_member_license_verification_status': 'verified_valid'
                },
                {
                    'crew_member_id': '2',
                    'crew_member_license_verification_status': None
                }
            ]
        }
        assert calculate_crew_license_status(boat) == 'invalid'
    
    def test_one_invalid_crew(self):
        """Test boat with one invalid crew returns 'invalid'."""
        boat = {
            'seats': [
                {
                    'crew_member_id': '1',
                    'crew_member_license_verification_status': 'verified_valid'
                },
                {
                    'crew_member_id': '2',
                    'crew_member_license_verification_status': 'verified_invalid'
                }
            ]
        }
        assert calculate_crew_license_status(boat) == 'invalid'
    
    def test_manually_verified_invalid(self):
        """Test boat with manually verified invalid crew returns 'invalid'."""
        boat = {
            'seats': [
                {
                    'crew_member_id': '1',
                    'crew_member_license_verification_status': 'verified_valid'
                },
                {
                    'crew_member_id': '2',
                    'crew_member_license_verification_status': 'manually_verified_invalid'
                }
            ]
        }
        assert calculate_crew_license_status(boat) == 'invalid'
    
    def test_no_crew_assigned(self):
        """Test boat with no crew assigned returns None."""
        boat = {
            'seats': [
                {'position': 1, 'type': 'rower'},
                {'position': 2, 'type': 'rower'}
            ]
        }
        assert calculate_crew_license_status(boat) is None
    
    def test_empty_seats(self):
        """Test boat with empty seats array returns None."""
        boat = {'seats': []}
        assert calculate_crew_license_status(boat) is None
    
    def test_no_seats_key(self):
        """Test boat with no seats key returns None."""
        boat = {}
        assert calculate_crew_license_status(boat) is None
    
    def test_partial_crew_assignment(self):
        """Test boat with some seats filled and some empty."""
        boat = {
            'seats': [
                {
                    'crew_member_id': '1',
                    'crew_member_license_verification_status': 'verified_valid'
                },
                {'position': 2, 'type': 'rower'},  # Empty seat
                {
                    'crew_member_id': '3',
                    'crew_member_license_verification_status': 'verified_valid'
                }
            ]
        }
        # Only considers assigned crew members
        assert calculate_crew_license_status(boat) == 'verified'
    
    def test_large_crew_all_verified(self):
        """Test boat with 8+ crew members all verified."""
        boat = {
            'seats': [
                {
                    'crew_member_id': str(i),
                    'crew_member_license_verification_status': 'verified_valid'
                }
                for i in range(9)  # 8 rowers + 1 cox
            ]
        }
        assert calculate_crew_license_status(boat) == 'verified'
    
    def test_large_crew_one_invalid(self):
        """Test boat with 8+ crew members where one is invalid."""
        seats = [
            {
                'crew_member_id': str(i),
                'crew_member_license_verification_status': 'verified_valid'
            }
            for i in range(8)
        ]
        # Add one invalid crew member
        seats.append({
            'crew_member_id': '9',
            'crew_member_license_verification_status': 'verified_invalid'
        })
        boat = {'seats': seats}
        assert calculate_crew_license_status(boat) == 'invalid'
