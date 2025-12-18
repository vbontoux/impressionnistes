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
