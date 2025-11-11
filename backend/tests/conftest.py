"""
Pytest configuration and shared fixtures
"""
import os
import sys
import pytest
from pathlib import Path

# Add parent directory to path so we can import from functions and shared
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


@pytest.fixture
def mock_env_vars():
    """Fixture to set mock environment variables for testing"""
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-3'
    os.environ['TABLE_NAME'] = 'test-table'
    os.environ['ENVIRONMENT'] = 'test'
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_crew_member():
    """Fixture providing sample crew member data"""
    return {
        'crew_id': 'crew-123',
        'first_name': 'Jean',
        'last_name': 'Dupont',
        'date_of_birth': '1990-05-15',
        'gender': 'M',
        'license_number': 'ABC123456',
        'club_affiliation': 'RCPM',
        'is_rcpm_member': True
    }


@pytest.fixture
def sample_boat_registration():
    """Fixture providing sample boat registration data"""
    return {
        'boat_id': 'boat-456',
        'event_type': '21km',
        'boat_type': '4+',
        'race_id': 'race-789',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-123'},
            {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-124'},
            {'position': 3, 'type': 'rower', 'crew_member_id': 'crew-125'},
            {'position': 4, 'type': 'rower', 'crew_member_id': 'crew-126'},
            {'position': 5, 'type': 'cox', 'crew_member_id': 'crew-127'}
        ],
        'status': 'complete'
    }
