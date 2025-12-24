"""
Integration tests for admin API endpoints
Tests Lambda handlers with mock DynamoDB (requires admin group)
"""
import json
import pytest


@pytest.fixture
def admin_user_id():
    """Return a test admin user ID"""
    return 'test-admin-user-123'


@pytest.fixture
def mock_admin_event(mock_api_gateway_event, admin_user_id):
    """Factory fixture to create admin API Gateway events"""
    def _create_admin_event(**kwargs):
        # Override groups to include admins
        kwargs['groups'] = ['admins']
        kwargs['user_id'] = kwargs.get('user_id', admin_user_id)
        return mock_api_gateway_event(**kwargs)
    return _create_admin_event


def test_admin_list_all_boats(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test admin listing all boats across all teams"""
    # Create boats for different teams
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-1',
        'boat_registration_id': 'boat-1',
        'event_type': '21km',
        'boat_type': '4-',
        'registration_status': 'incomplete',
        'seats': []
    })
    
    dynamodb_table.put_item(Item={
        'PK': 'TEAM#another-team',
        'SK': 'BOAT#boat-2',
        'boat_registration_id': 'boat-2',
        'event_type': '42km',
        'boat_type': '2x',
        'registration_status': 'paid',
        'seats': []
    })
    
    from admin.admin_list_all_boats import lambda_handler
    
    # Create admin API Gateway event
    event = mock_admin_event(
        http_method='GET',
        path='/admin/boats'
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'boats' in body['data']
    assert len(body['data']['boats']) >= 2


def test_admin_list_all_crew_members(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test admin listing all crew members across all teams"""
    # Create crew members for different teams
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-1',
        'crew_member_id': 'crew-1',
        'first_name': 'Alice',
        'last_name': 'Smith',
        'date_of_birth': '1990-01-15',
        'gender': 'F',
        'license_number': 'LIC001',
        'club_affiliation': 'RCPM'
    })
    
    dynamodb_table.put_item(Item={
        'PK': 'TEAM#another-team',
        'SK': 'CREW#crew-2',
        'crew_member_id': 'crew-2',
        'first_name': 'Bob',
        'last_name': 'Jones',
        'date_of_birth': '1985-05-20',
        'gender': 'M',
        'license_number': 'LIC002',
        'club_affiliation': 'Club A'
    })
    
    from admin.admin_list_all_crew_members import lambda_handler
    
    # Create admin API Gateway event
    event = mock_admin_event(
        http_method='GET',
        path='/admin/crew'
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'crew_members' in body['data']
    assert len(body['data']['crew_members']) >= 2


def test_admin_get_stats(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test admin getting event statistics"""
    # Seed some data
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-1',
        'boat_registration_id': 'boat-1',
        'event_type': '21km',
        'boat_type': '4-',
        'registration_status': 'paid',
        'seats': []
    })
    
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-1',
        'crew_member_id': 'crew-1',
        'first_name': 'Alice',
        'last_name': 'Smith',
        'date_of_birth': '1990-01-15',
        'gender': 'F',
        'license_number': 'LIC001',
        'club_affiliation': 'RCPM'
    })
    
    from admin.get_stats import lambda_handler
    
    # Create admin API Gateway event
    event = mock_admin_event(
        http_method='GET',
        path='/admin/stats'
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    # Stats are returned directly in data
    assert 'total_crew_members' in body['data']
    assert 'total_boat_registrations' in body['data']
    assert 'total_payments' in body['data']
    assert 'rental_boats_reserved' in body['data']


def test_admin_get_event_config(dynamodb_table, mock_admin_event, mock_lambda_context):
    """Test admin getting event configuration"""
    from admin.get_event_config import lambda_handler
    
    # Create admin API Gateway event
    event = mock_admin_event(
        http_method='GET',
        path='/admin/config/event'
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'event_date' in body['data']
    assert 'registration_start_date' in body['data']


def test_admin_update_event_config(dynamodb_table, mock_admin_event, mock_lambda_context):
    """Test admin updating event configuration"""
    from admin.update_event_config import lambda_handler
    
    # Create admin API Gateway event
    event = mock_admin_event(
        http_method='PUT',
        path='/admin/config/event',
        body=json.dumps({
            'event_date': '2025-06-01',
            'registration_start_date': '2025-04-01',
            'registration_end_date': '2025-05-15',
            'payment_deadline': '2025-05-20'
        })
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['event_date'] == '2025-06-01'


def test_race_timing_config_initialized(dynamodb_table, mock_admin_event, mock_lambda_context):
    """Test that race timing configuration is properly initialized"""
    # Seed race timing config (simulating what init_config.py does)
    dynamodb_table.put_item(
        Item={
            'PK': 'CONFIG',
            'SK': 'RACE_TIMING',
            'marathon_start_time': '07:45',
            'semi_marathon_start_time': '09:00',
            'semi_marathon_interval_seconds': 30,
            'marathon_bow_start': 1,
            'semi_marathon_bow_start': 41,
            'created_at': '2025-01-01T00:00:00Z',
            'updated_at': '2025-01-01T00:00:00Z',
            'updated_by': 'system'
        }
    )
    
    # Retrieve the config
    response = dynamodb_table.get_item(
        Key={'PK': 'CONFIG', 'SK': 'RACE_TIMING'}
    )
    
    # Assert config exists and has correct values
    assert 'Item' in response
    config = response['Item']
    assert config['marathon_start_time'] == '07:45'
    assert config['semi_marathon_start_time'] == '09:00'
    assert config['semi_marathon_interval_seconds'] == 30
    assert config['marathon_bow_start'] == 1
    assert config['semi_marathon_bow_start'] == 41


def test_get_event_config_includes_race_timing(dynamodb_table, mock_admin_event, mock_lambda_context):
    """Test that get event config includes race timing fields"""
    # Seed system config
    dynamodb_table.put_item(
        Item={
            'PK': 'CONFIG',
            'SK': 'SYSTEM',
            'event_date': '2025-05-01',
            'registration_start_date': '2025-03-19',
            'registration_end_date': '2025-04-19',
            'payment_deadline': '2025-04-25',
            'rental_priority_days': 15
        }
    )
    
    # Seed race timing config
    dynamodb_table.put_item(
        Item={
            'PK': 'CONFIG',
            'SK': 'RACE_TIMING',
            'marathon_start_time': '07:45',
            'semi_marathon_start_time': '09:00',
            'semi_marathon_interval_seconds': 30,
            'marathon_bow_start': 1,
            'semi_marathon_bow_start': 41
        }
    )
    
    from admin.get_event_config import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/event-config'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    config = body['data']
    assert config['event_date'] == '2025-05-01'
    assert config['marathon_start_time'] == '07:45'
    assert config['semi_marathon_start_time'] == '09:00'
    assert config['semi_marathon_interval_seconds'] == 30


def test_update_race_timing_config(dynamodb_table, mock_admin_event, mock_lambda_context, admin_user_id):
    """Test updating race timing configuration"""
    # Seed initial configs
    dynamodb_table.put_item(
        Item={
            'PK': 'CONFIG',
            'SK': 'SYSTEM',
            'event_date': '2025-05-01',
            'registration_start_date': '2025-03-19',
            'registration_end_date': '2025-04-19',
            'payment_deadline': '2025-04-25',
            'rental_priority_days': 15
        }
    )
    
    dynamodb_table.put_item(
        Item={
            'PK': 'CONFIG',
            'SK': 'RACE_TIMING',
            'marathon_start_time': '07:45',
            'semi_marathon_start_time': '09:00',
            'semi_marathon_interval_seconds': 30,
            'marathon_bow_start': 1,
            'semi_marathon_bow_start': 41
        }
    )
    
    from admin.update_event_config import lambda_handler
    
    # Update race timing
    event = mock_admin_event(
        http_method='PUT',
        path='/admin/event-config',
        body=json.dumps({
            'marathon_start_time': '08:00',
            'semi_marathon_start_time': '09:30',
            'semi_marathon_interval_seconds': 45
        })
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    config = body['data']
    assert config['marathon_start_time'] == '08:00'
    assert config['semi_marathon_start_time'] == '09:30'
    assert config['semi_marathon_interval_seconds'] == 45
    
    # Verify in database
    db_response = dynamodb_table.get_item(
        Key={'PK': 'CONFIG', 'SK': 'RACE_TIMING'}
    )
    assert db_response['Item']['marathon_start_time'] == '08:00'
    assert db_response['Item']['semi_marathon_interval_seconds'] == 45


def test_update_race_timing_validates_time_format(dynamodb_table, mock_admin_event, mock_lambda_context):
    """Test that race timing update validates time format"""
    # Seed initial configs
    dynamodb_table.put_item(
        Item={
            'PK': 'CONFIG',
            'SK': 'SYSTEM',
            'event_date': '2025-05-01'
        }
    )
    
    dynamodb_table.put_item(
        Item={
            'PK': 'CONFIG',
            'SK': 'RACE_TIMING',
            'marathon_start_time': '07:45',
            'semi_marathon_start_time': '09:00',
            'semi_marathon_interval_seconds': 30,
            'marathon_bow_start': 1,
            'semi_marathon_bow_start': 41
        }
    )
    
    from admin.update_event_config import lambda_handler
    
    # Try invalid time format
    event = mock_admin_event(
        http_method='PUT',
        path='/admin/event-config',
        body=json.dumps({
            'marathon_start_time': '25:00'  # Invalid hour
        })
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] is False
    # The validation error is returned
    assert 'error' in body


def test_update_bow_start_numbers(dynamodb_table, mock_admin_event, mock_lambda_context, admin_user_id):
    """Test updating bow start numbers"""
    # Seed initial configs
    dynamodb_table.put_item(
        Item={
            'PK': 'CONFIG',
            'SK': 'SYSTEM',
            'event_date': '2025-05-01'
        }
    )
    
    dynamodb_table.put_item(
        Item={
            'PK': 'CONFIG',
            'SK': 'RACE_TIMING',
            'marathon_start_time': '07:45',
            'semi_marathon_start_time': '09:00',
            'semi_marathon_interval_seconds': 30,
            'marathon_bow_start': 1,
            'semi_marathon_bow_start': 41
        }
    )
    
    from admin.update_event_config import lambda_handler
    
    # Update bow start numbers
    event = mock_admin_event(
        http_method='PUT',
        path='/admin/event-config',
        body=json.dumps({
            'marathon_bow_start': 100,
            'semi_marathon_bow_start': 200
        })
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    config = body['data']
    assert config['marathon_bow_start'] == 100
    assert config['semi_marathon_bow_start'] == 200
    
    # Verify in database
    db_response = dynamodb_table.get_item(
        Key={'PK': 'CONFIG', 'SK': 'RACE_TIMING'}
    )
    assert db_response['Item']['marathon_bow_start'] == 100
    assert db_response['Item']['semi_marathon_bow_start'] == 200


def test_update_bow_start_validates_positive_integers(dynamodb_table, mock_admin_event, mock_lambda_context):
    """Test that bow start numbers must be positive integers"""
    # Seed initial configs
    dynamodb_table.put_item(
        Item={
            'PK': 'CONFIG',
            'SK': 'SYSTEM',
            'event_date': '2025-05-01'
        }
    )
    
    dynamodb_table.put_item(
        Item={
            'PK': 'CONFIG',
            'SK': 'RACE_TIMING',
            'marathon_start_time': '07:45',
            'semi_marathon_start_time': '09:00',
            'semi_marathon_interval_seconds': 30,
            'marathon_bow_start': 1,
            'semi_marathon_bow_start': 41
        }
    )
    
    from admin.update_event_config import lambda_handler
    
    # Try invalid bow start (negative number)
    event = mock_admin_event(
        http_method='PUT',
        path='/admin/event-config',
        body=json.dumps({
            'marathon_bow_start': -5
        })
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'error' in body


def test_non_admin_cannot_access_admin_endpoints(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test that non-admin users cannot access admin endpoints"""
    from admin.admin_list_all_boats import lambda_handler
    
    # Create regular team manager event (not admin)
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/boats',
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert forbidden response
    assert response['statusCode'] == 403
    
    body = json.loads(response['body'])
    assert body['success'] is False


# JSON Export API Tests (Export API Refactoring)
# ============================================================================

def test_export_crew_members_json_structure(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test crew members JSON export returns correct structure"""
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'first_name': 'John',
        'last_name': 'Manager',
        'email': 'john@example.com',
        'club_affiliation': 'Test Club'
    })
    
    # Add crew members
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-1',
        'crew_member_id': 'crew-1',
        'first_name': 'Alice',
        'last_name': 'Smith',
        'gender': 'F',
        'date_of_birth': '1990-01-15',
        'age': 35,
        'license_number': 'LIC001',
        'club_affiliation': 'Test Club',
        'created_at': '2025-01-01T00:00:00Z',
        'updated_at': '2025-01-01T00:00:00Z'
    })
    
    from admin.export_crew_members_json import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/crew-members'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Verify response structure
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'data' in body
    
    data = body['data']
    assert 'crew_members' in data
    assert 'total_count' in data
    assert 'exported_at' in data
    
    # Verify crew member structure
    crew_members = data['crew_members']
    assert len(crew_members) == 1
    
    member = crew_members[0]
    assert member['crew_member_id'] == 'crew-1'
    assert member['first_name'] == 'Alice'
    assert member['last_name'] == 'Smith'
    assert member['gender'] == 'F'
    assert member['date_of_birth'] == '1990-01-15'
    assert member['age'] == 35
    assert member['license_number'] == 'LIC001'
    assert member['club_affiliation'] == 'Test Club'


def test_export_crew_members_json_includes_team_manager_info(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test crew members JSON export includes team manager information"""
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'first_name': 'John',
        'last_name': 'Manager',
        'email': 'john@example.com',
        'club_affiliation': 'RCPM'
    })
    
    # Add crew member
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-1',
        'crew_member_id': 'crew-1',
        'first_name': 'Alice',
        'last_name': 'Smith',
        'gender': 'F',
        'date_of_birth': '1990-01-15',
        'license_number': 'LIC001'
    })
    
    from admin.export_crew_members_json import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/crew-members'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    body = json.loads(response['body'])
    member = body['data']['crew_members'][0]
    
    # Verify team manager information is included
    assert member['team_manager_id'] == test_team_manager_id
    assert member['team_manager_name'] == 'John Manager'
    assert member['team_manager_email'] == 'john@example.com'
    assert member['team_manager_club'] == 'RCPM'


def test_export_crew_members_json_sorting(dynamodb_table, mock_admin_event, mock_lambda_context):
    """Test crew members JSON export sorts by team manager name, then crew member last name"""
    # Add team managers
    dynamodb_table.put_item(Item={
        'PK': 'USER#tm-1',
        'SK': 'PROFILE',
        'first_name': 'Alice',
        'last_name': 'Manager',
        'email': 'alice@example.com',
        'club_affiliation': 'Club A'
    })
    
    dynamodb_table.put_item(Item={
        'PK': 'USER#tm-2',
        'SK': 'PROFILE',
        'first_name': 'Bob',
        'last_name': 'Manager',
        'email': 'bob@example.com',
        'club_affiliation': 'Club B'
    })
    
    # Add crew members for first team manager
    dynamodb_table.put_item(Item={
        'PK': 'TEAM#tm-1',
        'SK': 'CREW#crew-1',
        'crew_member_id': 'crew-1',
        'first_name': 'Zoe',
        'last_name': 'Smith',
        'gender': 'F',
        'date_of_birth': '1990-01-15'
    })
    
    dynamodb_table.put_item(Item={
        'PK': 'TEAM#tm-1',
        'SK': 'CREW#crew-2',
        'crew_member_id': 'crew-2',
        'first_name': 'Alice',
        'last_name': 'Adams',
        'gender': 'F',
        'date_of_birth': '1990-01-15'
    })
    
    # Add crew member for second team manager
    dynamodb_table.put_item(Item={
        'PK': 'TEAM#tm-2',
        'SK': 'CREW#crew-3',
        'crew_member_id': 'crew-3',
        'first_name': 'Charlie',
        'last_name': 'Brown',
        'gender': 'M',
        'date_of_birth': '1990-01-15'
    })
    
    from admin.export_crew_members_json import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/crew-members'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    body = json.loads(response['body'])
    crew_members = body['data']['crew_members']
    
    # Verify sorting: Alice Manager's crew (Adams, Smith), then Bob Manager's crew (Brown)
    assert len(crew_members) == 3
    assert crew_members[0]['crew_member_id'] == 'crew-2'  # Alice Manager -> Adams
    assert crew_members[1]['crew_member_id'] == 'crew-1'  # Alice Manager -> Smith
    assert crew_members[2]['crew_member_id'] == 'crew-3'  # Bob Manager -> Brown


def test_export_crew_members_json_pagination(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test crew members JSON export handles pagination for large datasets"""
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'first_name': 'John',
        'last_name': 'Manager',
        'email': 'john@example.com',
        'club_affiliation': 'Test Club'
    })
    
    # Add many crew members (more than typical page size)
    for i in range(50):
        dynamodb_table.put_item(Item={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'CREW#crew-{i}',
            'crew_member_id': f'crew-{i}',
            'first_name': f'Member{i}',
            'last_name': f'Last{i}',
            'gender': 'M' if i % 2 == 0 else 'F',
            'date_of_birth': '1990-01-15'
        })
    
    from admin.export_crew_members_json import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/crew-members'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    body = json.loads(response['body'])
    crew_members = body['data']['crew_members']
    
    # Verify all crew members are returned
    assert len(crew_members) == 50
    assert body['data']['total_count'] == 50


def test_export_crew_members_json_empty_database(dynamodb_table, mock_admin_event, mock_lambda_context):
    """Test crew members JSON export handles empty database"""
    from admin.export_crew_members_json import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/crew-members'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should return success with empty data
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['crew_members'] == []
    assert body['data']['total_count'] == 0



def test_export_boat_registrations_json_structure(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test boat registrations JSON export returns correct structure"""
    from decimal import Decimal
    
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'first_name': 'John',
        'last_name': 'Manager',
        'email': 'john@example.com',
        'club_affiliation': 'Test Club'
    })
    
    # Add race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'M01',
        'race_id': 'M01',
        'name': 'Marathon Men Senior',
        'event_type': '42km',
        'boat_type': 'skiff'
    })
    
    # Add boat registration
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-1',
        'boat_registration_id': 'boat-1',
        'event_type': '42km',
        'boat_type': 'skiff',
        'race_id': 'M01',
        'registration_status': 'complete',
        'forfait': False,
        'seats': [
            {'crew_member_id': 'crew-1', 'position': 1, 'type': 'rower'}
        ],
        'crew_composition': {
            'gender_category': 'men',
            'age_category': 'senior',
            'avg_age': Decimal('35.5')
        },
        'is_multi_club_crew': False,
        'created_at': '2025-01-01T00:00:00Z',
        'updated_at': '2025-01-01T00:00:00Z'
    })
    
    from admin.export_boat_registrations_json import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/boat-registrations'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Verify response structure
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'data' in body
    
    data = body['data']
    assert 'boats' in data
    assert 'total_count' in data
    assert 'exported_at' in data
    
    # Verify boat structure
    boats = data['boats']
    assert len(boats) == 1
    
    boat = boats[0]
    assert boat['boat_registration_id'] == 'boat-1'
    assert boat['event_type'] == '42km'
    assert boat['boat_type'] == 'skiff'
    assert boat['race_id'] == 'M01'
    assert boat['registration_status'] == 'complete'
    assert boat['forfait'] is False
    assert 'seats' in boat
    assert 'crew_composition' in boat


def test_export_boat_registrations_json_includes_all_boats(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test boat registrations JSON export includes all boats regardless of status"""
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'first_name': 'John',
        'last_name': 'Manager',
        'email': 'john@example.com',
        'club_affiliation': 'Test Club'
    })
    
    # Add race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'M01',
        'race_id': 'M01',
        'name': 'Test Race',
        'event_type': '42km',
        'boat_type': 'skiff'
    })
    
    # Add boats with different statuses
    statuses = ['incomplete', 'complete', 'paid', 'free']
    for i, status in enumerate(statuses):
        dynamodb_table.put_item(Item={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'BOAT#boat-{i}',
            'boat_registration_id': f'boat-{i}',
            'event_type': '42km',
            'boat_type': 'skiff',
            'race_id': 'M01',
            'registration_status': status,
            'forfait': False,
            'seats': []
        })
    
    # Add a forfait boat
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-forfait',
        'boat_registration_id': 'boat-forfait',
        'event_type': '42km',
        'boat_type': 'skiff',
        'race_id': 'M01',
        'registration_status': 'complete',
        'forfait': True,
        'seats': []
    })
    
    from admin.export_boat_registrations_json import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/boat-registrations'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    body = json.loads(response['body'])
    boats = body['data']['boats']
    
    # Verify all boats are included (no status filtering)
    assert len(boats) == 5
    assert body['data']['total_count'] == 5
    
    # Verify all statuses are present
    returned_statuses = [b['registration_status'] for b in boats]
    assert 'incomplete' in returned_statuses
    assert 'complete' in returned_statuses
    assert 'paid' in returned_statuses
    assert 'free' in returned_statuses
    
    # Verify forfait boat is included
    forfait_boats = [b for b in boats if b.get('forfait') is True]
    assert len(forfait_boats) == 1


def test_export_boat_registrations_json_includes_race_names(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test boat registrations JSON export includes race names"""
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'first_name': 'John',
        'last_name': 'Manager',
        'email': 'john@example.com',
        'club_affiliation': 'Test Club'
    })
    
    # Add races
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'M01',
        'race_id': 'M01',
        'name': 'Marathon Men Senior',
        'event_type': '42km',
        'boat_type': 'skiff'
    })
    
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'SM01A',
        'race_id': 'SM01A',
        'name': 'Semi-Marathon Women Junior',
        'event_type': '21km',
        'boat_type': '4+'
    })
    
    # Add boat registrations
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-1',
        'boat_registration_id': 'boat-1',
        'event_type': '42km',
        'boat_type': 'skiff',
        'race_id': 'M01',
        'registration_status': 'complete',
        'seats': []
    })
    
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-2',
        'boat_registration_id': 'boat-2',
        'event_type': '21km',
        'boat_type': '4+',
        'race_id': 'SM01A',
        'registration_status': 'paid',
        'seats': []
    })
    
    from admin.export_boat_registrations_json import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/boat-registrations'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    body = json.loads(response['body'])
    boats = body['data']['boats']
    
    # Verify race names are included
    boat1 = [b for b in boats if b['boat_registration_id'] == 'boat-1'][0]
    assert boat1['race_name'] == 'Marathon Men Senior'
    
    boat2 = [b for b in boats if b['boat_registration_id'] == 'boat-2'][0]
    assert boat2['race_name'] == 'Semi-Marathon Women Junior'


def test_export_boat_registrations_json_includes_crew_composition(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test boat registrations JSON export includes crew composition details"""
    from decimal import Decimal
    
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'first_name': 'John',
        'last_name': 'Manager',
        'email': 'john@example.com',
        'club_affiliation': 'Test Club'
    })
    
    # Add race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'M01',
        'race_id': 'M01',
        'name': 'Test Race',
        'event_type': '21km',
        'boat_type': '4+'
    })
    
    # Add boat with crew composition
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-1',
        'boat_registration_id': 'boat-1',
        'event_type': '21km',
        'boat_type': '4+',
        'race_id': 'M01',
        'registration_status': 'complete',
        'seats': [
            {'crew_member_id': 'crew-1', 'position': 1, 'type': 'rower'},
            {'crew_member_id': 'crew-2', 'position': 2, 'type': 'rower'},
            {'crew_member_id': None, 'position': 3, 'type': 'rower'},
            {'crew_member_id': None, 'position': 4, 'type': 'rower'},
            {'crew_member_id': 'crew-3', 'position': 5, 'type': 'cox'}
        ],
        'crew_composition': {
            'gender_category': 'women',
            'age_category': 'j16',
            'avg_age': Decimal('16.5')
        }
    })
    
    from admin.export_boat_registrations_json import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/boat-registrations'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    body = json.loads(response['body'])
    boat = body['data']['boats'][0]
    
    # Verify crew composition details
    crew_comp = boat['crew_composition']
    assert crew_comp['gender_category'] == 'women'
    assert crew_comp['age_category'] == 'j16'
    assert crew_comp['avg_age'] == 16.5  # Decimal converted to float
    assert crew_comp['filled_seats'] == 3  # 2 rowers + 1 cox
    assert crew_comp['total_seats'] == 5


def test_export_boat_registrations_json_sorting(dynamodb_table, mock_admin_event, mock_lambda_context):
    """Test boat registrations JSON export sorts by team manager, event type, boat type"""
    # Add team managers
    dynamodb_table.put_item(Item={
        'PK': 'USER#tm-1',
        'SK': 'PROFILE',
        'first_name': 'Alice',
        'last_name': 'Manager',
        'email': 'alice@example.com',
        'club_affiliation': 'Club A'
    })
    
    dynamodb_table.put_item(Item={
        'PK': 'USER#tm-2',
        'SK': 'PROFILE',
        'first_name': 'Bob',
        'last_name': 'Manager',
        'email': 'bob@example.com',
        'club_affiliation': 'Club B'
    })
    
    # Add race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'M01',
        'race_id': 'M01',
        'name': 'Test Race',
        'event_type': '42km',
        'boat_type': 'skiff'
    })
    
    # Add boats for first team manager (different event types and boat types)
    dynamodb_table.put_item(Item={
        'PK': 'TEAM#tm-1',
        'SK': 'BOAT#boat-1',
        'boat_registration_id': 'boat-1',
        'event_type': '42km',
        'boat_type': 'skiff',
        'race_id': 'M01',
        'registration_status': 'complete',
        'seats': []
    })
    
    dynamodb_table.put_item(Item={
        'PK': 'TEAM#tm-1',
        'SK': 'BOAT#boat-2',
        'boat_registration_id': 'boat-2',
        'event_type': '21km',
        'boat_type': '4+',
        'race_id': 'M01',
        'registration_status': 'complete',
        'seats': []
    })
    
    dynamodb_table.put_item(Item={
        'PK': 'TEAM#tm-1',
        'SK': 'BOAT#boat-3',
        'boat_registration_id': 'boat-3',
        'event_type': '21km',
        'boat_type': '2x',
        'race_id': 'M01',
        'registration_status': 'complete',
        'seats': []
    })
    
    # Add boat for second team manager
    dynamodb_table.put_item(Item={
        'PK': 'TEAM#tm-2',
        'SK': 'BOAT#boat-4',
        'boat_registration_id': 'boat-4',
        'event_type': '42km',
        'boat_type': 'skiff',
        'race_id': 'M01',
        'registration_status': 'complete',
        'seats': []
    })
    
    from admin.export_boat_registrations_json import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/boat-registrations'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    body = json.loads(response['body'])
    boats = body['data']['boats']
    
    # Verify sorting: Alice Manager (21km/2x, 21km/4+, 42km/skiff), then Bob Manager (42km/skiff)
    assert len(boats) == 4
    assert boats[0]['boat_registration_id'] == 'boat-3'  # Alice -> 21km -> 2x
    assert boats[1]['boat_registration_id'] == 'boat-2'  # Alice -> 21km -> 4+
    assert boats[2]['boat_registration_id'] == 'boat-1'  # Alice -> 42km -> skiff
    assert boats[3]['boat_registration_id'] == 'boat-4'  # Bob -> 42km -> skiff



def test_export_races_json_includes_all_entities(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test races JSON export includes all entities (races, boats, crew, managers)"""
    # Add system config
    dynamodb_table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'competition_date': '2025-05-01'
    })
    
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'first_name': 'John',
        'last_name': 'Manager',
        'email': 'john@example.com',
        'club_affiliation': 'Test Club'
    })
    
    # Add race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'M01',
        'race_id': 'M01',
        'name': 'Marathon Men Senior',
        'distance': 42,
        'event_type': '42km',
        'boat_type': 'skiff',
        'age_category': 'senior',
        'gender_category': 'men'
    })
    
    # Add crew member
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-1',
        'crew_member_id': 'crew-1',
        'first_name': 'Alice',
        'last_name': 'Smith',
        'date_of_birth': '1990-01-15',
        'gender': 'F',
        'license_number': 'LIC001',
        'club_affiliation': 'Test Club',
        'age': 35
    })
    
    # Add boat
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-1',
        'boat_registration_id': 'boat-1',
        'event_type': '42km',
        'boat_type': 'skiff',
        'race_id': 'M01',
        'registration_status': 'complete',
        'forfait': False,
        'seats': [
            {'crew_member_id': 'crew-1', 'position': 1, 'type': 'rower'}
        ]
    })
    
    from admin.export_races_json import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/races'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Verify response structure
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    
    data = body['data']
    
    # Verify all entities are present
    assert 'config' in data
    assert 'races' in data
    assert 'boats' in data
    assert 'crew_members' in data
    assert 'team_managers' in data
    assert 'total_races' in data
    assert 'total_boats' in data
    assert 'total_crew_members' in data
    assert 'exported_at' in data
    
    # Verify config
    assert data['config']['competition_date'] == '2025-05-01'
    
    # Verify races
    assert len(data['races']) == 1
    race = data['races'][0]
    assert race['race_id'] == 'M01'
    assert race['name'] == 'Marathon Men Senior'
    assert race['distance'] == 42
    assert race['event_type'] == '42km'
    
    # Verify boats
    assert len(data['boats']) == 1
    boat = data['boats'][0]
    assert boat['boat_registration_id'] == 'boat-1'
    assert boat['race_id'] == 'M01'
    
    # Verify crew members
    assert len(data['crew_members']) == 1
    crew = data['crew_members'][0]
    assert crew['crew_member_id'] == 'crew-1'
    assert crew['first_name'] == 'Alice'
    
    # Verify team managers
    assert len(data['team_managers']) == 1
    tm = data['team_managers'][0]
    assert tm['user_id'] == test_team_manager_id
    assert tm['club_affiliation'] == 'Test Club'


def test_export_races_json_includes_all_boat_statuses(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test races JSON export includes boats with all statuses (complete, paid, free, incomplete, forfait)"""
    # Add system config
    dynamodb_table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'competition_date': '2025-05-01'
    })
    
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'first_name': 'John',
        'last_name': 'Manager',
        'email': 'john@example.com',
        'club_affiliation': 'Test Club'
    })
    
    # Add race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'M01',
        'race_id': 'M01',
        'name': 'Test Race',
        'distance': 42,
        'event_type': '42km',
        'boat_type': 'skiff'
    })
    
    # Add boats with all statuses
    statuses = ['incomplete', 'complete', 'paid', 'free']
    for i, status in enumerate(statuses):
        dynamodb_table.put_item(Item={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'BOAT#boat-{status}',
            'boat_registration_id': f'boat-{status}',
            'event_type': '42km',
            'boat_type': 'skiff',
            'race_id': 'M01',
            'registration_status': status,
            'forfait': False,
            'seats': []
        })
    
    # Add a forfait boat
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-forfait',
        'boat_registration_id': 'boat-forfait',
        'event_type': '42km',
        'boat_type': 'skiff',
        'race_id': 'M01',
        'registration_status': 'complete',
        'forfait': True,
        'seats': []
    })
    
    from admin.export_races_json import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/races'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    body = json.loads(response['body'])
    boats = body['data']['boats']
    
    # Verify all boats are included (no filtering)
    assert len(boats) == 5
    assert body['data']['total_boats'] == 5
    
    # Verify all statuses are present
    returned_statuses = [b['registration_status'] for b in boats]
    assert 'incomplete' in returned_statuses
    assert 'complete' in returned_statuses
    assert 'paid' in returned_statuses
    assert 'free' in returned_statuses
    
    # Verify forfait boat is included
    forfait_boats = [b for b in boats if b.get('forfait') is True]
    assert len(forfait_boats) == 1
    assert forfait_boats[0]['boat_registration_id'] == 'boat-forfait'


def test_export_races_json_converts_decimals(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test races JSON export converts Decimal types to numbers"""
    from decimal import Decimal
    
    # Add system config
    dynamodb_table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'competition_date': '2025-05-01'
    })
    
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'first_name': 'John',
        'last_name': 'Manager',
        'email': 'john@example.com',
        'club_affiliation': 'Test Club'
    })
    
    # Add race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'M01',
        'race_id': 'M01',
        'name': 'Test Race',
        'distance': 42,
        'event_type': '42km',
        'boat_type': 'skiff'
    })
    
    # Add crew member with age as Decimal
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-1',
        'crew_member_id': 'crew-1',
        'first_name': 'Alice',
        'last_name': 'Smith',
        'date_of_birth': '1990-01-15',
        'gender': 'F',
        'age': Decimal('35')
    })
    
    # Add boat with Decimal values in crew_composition
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-1',
        'boat_registration_id': 'boat-1',
        'event_type': '42km',
        'boat_type': 'skiff',
        'race_id': 'M01',
        'registration_status': 'complete',
        'forfait': False,
        'seats': [],
        'crew_composition': {
            'avg_age': Decimal('35.5'),
            'filled_seats': Decimal('1'),
            'total_seats': Decimal('1')
        }
    })
    
    from admin.export_races_json import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/races'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    body = json.loads(response['body'])
    
    # Verify Decimal values are converted to numbers (not strings)
    crew = body['data']['crew_members'][0]
    assert isinstance(crew['age'], (int, float))
    assert crew['age'] == 35
    
    boat = body['data']['boats'][0]
    crew_comp = boat['crew_composition']
    assert isinstance(crew_comp['avg_age'], (int, float))
    assert crew_comp['avg_age'] == 35.5
    assert isinstance(crew_comp['filled_seats'], (int, float))
    assert isinstance(crew_comp['total_seats'], (int, float))


def test_export_races_json_handles_missing_team_manager(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test races JSON export handles missing team manager gracefully"""
    # Add system config
    dynamodb_table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'competition_date': '2025-05-01'
    })
    
    # Add race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'M01',
        'race_id': 'M01',
        'name': 'Test Race',
        'distance': 42,
        'event_type': '42km',
        'boat_type': 'skiff'
    })
    
    # Add boat WITHOUT adding team manager profile
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-1',
        'boat_registration_id': 'boat-1',
        'event_type': '42km',
        'boat_type': 'skiff',
        'race_id': 'M01',
        'registration_status': 'complete',
        'forfait': False,
        'seats': []
    })
    
    from admin.export_races_json import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/races'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should still succeed
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    boats = body['data']['boats']
    
    # Verify boat is included with empty team manager info
    assert len(boats) == 1
    boat = boats[0]
    assert boat['team_manager_id'] == test_team_manager_id
    assert boat['club_affiliation'] == ''  # Empty when team manager not found


def test_export_races_json_empty_database(dynamodb_table, mock_admin_event, mock_lambda_context):
    """Test races JSON export handles empty database"""
    # Add only system config
    dynamodb_table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'competition_date': '2025-05-01'
    })
    
    from admin.export_races_json import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/races'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should return success with empty data
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    data = body['data']
    
    assert data['races'] == []
    assert data['boats'] == []
    assert data['crew_members'] == []
    assert data['team_managers'] == []
    assert data['total_races'] == 0
    assert data['total_boats'] == 0
    assert data['total_crew_members'] == 0
    assert data['config']['competition_date'] == '2025-05-01'
