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


def test_export_crewtimer_with_complete_boats(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test CrewTimer export with complete boats"""
    # Create system config
    dynamodb_table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'competition_date': '2025-05-01',
        'registration_start_date': '2025-03-01',
        'registration_end_date': '2025-04-15'
    })
    
    # Create races
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'M01',
        'race_id': 'M01',
        'name': '1X SENIOR MAN',
        'distance': 42,
        'event_type': '42km',
        'boat_type': 'skiff'
    })
    
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'SM01A',
        'race_id': 'SM01A',
        'name': 'WOMEN-JUNIOR J16-COXED SWEEP FOUR',
        'distance': 21,
        'event_type': '21km',
        'boat_type': '4+'
    })
    
    # Create team manager
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'first_name': 'John',
        'last_name': 'Doe',
        'club_affiliation': 'RCPM'
    })
    
    # Create crew members
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
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-2',
        'crew_member_id': 'crew-2',
        'first_name': 'Bob',
        'last_name': 'Jones',
        'date_of_birth': '1985-05-20',
        'gender': 'M',
        'license_number': 'LIC002',
        'club_affiliation': 'RCPM'
    })
    
    # Create complete boat (should be included)
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-1',
        'boat_registration_id': 'boat-1',
        'event_type': '42km',
        'boat_type': 'skiff',
        'race_id': 'M01',
        'registration_status': 'complete',
        'crew_assignments': [
            {
                'seat_number': 1,
                'seat_type': 'rower',
                'crew_member_id': 'CREW#crew-1'
            }
        ]
    })
    
    # Create paid boat (should be included)
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-2',
        'boat_registration_id': 'boat-2',
        'event_type': '21km',
        'boat_type': '4+',
        'race_id': 'SM01A',
        'registration_status': 'paid',
        'crew_assignments': [
            {
                'seat_number': 1,
                'seat_type': 'rower',
                'crew_member_id': 'CREW#crew-2'
            }
        ]
    })
    
    from admin.export_crewtimer import lambda_handler
    
    # Create admin API Gateway event
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/crewtimer'
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'data' in body
    assert 'rows' in body['data']
    assert 'total_races' in body['data']
    assert 'total_boats' in body['data']
    assert len(body['data']['rows']) == 2  # Two boats
    assert body['data']['total_boats'] == 2


def test_export_crewtimer_excludes_forfait_boats(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test CrewTimer export excludes forfait boats"""
    # Create system config
    dynamodb_table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'competition_date': '2025-05-01'
    })
    
    # Create race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'M01',
        'race_id': 'M01',
        'name': '1X SENIOR MAN',
        'distance': 42,
        'event_type': '42km',
        'boat_type': 'skiff'
    })
    
    # Create team manager
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'club_affiliation': 'RCPM'
    })
    
    # Create crew member
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-1',
        'crew_member_id': 'crew-1',
        'first_name': 'Alice',
        'last_name': 'Smith',
        'date_of_birth': '1990-01-15',
        'gender': 'F',
        'license_number': 'LIC001'
    })
    
    # Create forfait boat (should be excluded)
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-forfait',
        'boat_registration_id': 'boat-forfait',
        'event_type': '42km',
        'boat_type': 'skiff',
        'race_id': 'M01',
        'registration_status': 'complete',
        'forfait': True,
        'crew_assignments': [
            {
                'seat_number': 1,
                'seat_type': 'rower',
                'crew_member_id': 'CREW#crew-1'
            }
        ]
    })
    
    # Create complete boat (should be included)
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-complete',
        'boat_registration_id': 'boat-complete',
        'event_type': '42km',
        'boat_type': 'skiff',
        'race_id': 'M01',
        'registration_status': 'complete',
        'forfait': False,
        'crew_assignments': [
            {
                'seat_number': 1,
                'seat_type': 'rower',
                'crew_member_id': 'CREW#crew-1'
            }
        ]
    })
    
    from admin.export_crewtimer import lambda_handler
    
    # Create admin API Gateway event
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/crewtimer'
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'data' in body
    assert len(body['data']['rows']) == 1  # Only one boat (forfait excluded)
    assert body['data']['total_boats'] == 1


def test_export_crewtimer_excludes_incomplete_boats(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test CrewTimer export excludes incomplete boats"""
    # Create system config
    dynamodb_table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'competition_date': '2025-05-01'
    })
    
    # Create race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'M01',
        'race_id': 'M01',
        'name': '1X SENIOR MAN',
        'distance': 42,
        'event_type': '42km',
        'boat_type': 'skiff'
    })
    
    # Create team manager
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'club_affiliation': 'RCPM'
    })
    
    # Create incomplete boat (should be excluded)
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-incomplete',
        'boat_registration_id': 'boat-incomplete',
        'event_type': '42km',
        'boat_type': 'skiff',
        'race_id': 'M01',
        'registration_status': 'incomplete',
        'crew_assignments': []
    })
    
    from admin.export_crewtimer import lambda_handler
    
    # Create admin API Gateway event
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/crewtimer'
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response - should succeed but with no boats
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'data' in body
    assert len(body['data']['rows']) == 0  # No boats (incomplete excluded)
    assert body['data']['total_boats'] == 0


def test_export_crewtimer_sorts_races_correctly(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test CrewTimer export sorts marathon races before semi-marathon races"""
    # Create system config
    dynamodb_table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'competition_date': '2025-05-01'
    })
    
    # Create semi-marathon race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'SM01A',
        'race_id': 'SM01A',
        'name': 'WOMEN-JUNIOR J16-COXED SWEEP FOUR',
        'distance': 21,
        'event_type': '21km',
        'boat_type': '4+',
        'age_category': 'j16',
        'gender_category': 'women'
    })
    
    # Create marathon race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'M01',
        'race_id': 'M01',
        'name': '1X SENIOR MAN',
        'distance': 42,
        'event_type': '42km',
        'boat_type': 'skiff'
    })
    
    # Create team manager
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'club_affiliation': 'RCPM'
    })
    
    # Create crew member
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-1',
        'crew_member_id': 'crew-1',
        'first_name': 'Alice',
        'last_name': 'Smith',
        'date_of_birth': '1990-01-15',
        'gender': 'F',
        'license_number': 'LIC001'
    })
    
    # Create boat for semi-marathon
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-semi',
        'boat_registration_id': 'boat-semi',
        'event_type': '21km',
        'boat_type': '4+',
        'race_id': 'SM01A',
        'registration_status': 'complete',
        'crew_assignments': [
            {
                'seat_number': 1,
                'seat_type': 'rower',
                'crew_member_id': 'CREW#crew-1'
            }
        ]
    })
    
    # Create boat for marathon
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-marathon',
        'boat_registration_id': 'boat-marathon',
        'event_type': '42km',
        'boat_type': 'skiff',
        'race_id': 'M01',
        'registration_status': 'complete',
        'crew_assignments': [
            {
                'seat_number': 1,
                'seat_type': 'rower',
                'crew_member_id': 'CREW#crew-1'
            }
        ]
    })
    
    from admin.export_crewtimer import lambda_handler
    
    # Create admin API Gateway event
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/crewtimer'
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'data' in body
    assert len(body['data']['rows']) == 2
    
    # Check that marathon race comes before semi-marathon
    rows = body['data']['rows']
    assert rows[0]['Event Num'] == 1  # Marathon should be first
    assert rows[0]['Event'] == '1X SENIOR MAN'
    assert rows[1]['Event Num'] == 2  # Semi-marathon should be second
    assert rows[1]['Event'] == '4+ J16 WOMAN'  # Semi-marathon uses formatted name
    # Marathon races should come first (Event Num 1), then semi-marathon (Event Num 2)
    # We can't easily verify the order without decoding the Excel, but we verify it succeeds



def test_export_crewtimer(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test CrewTimer export returns JSON data with correct structure"""
    # Set up test data
    # Add system config
    dynamodb_table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'competition_date': '2025-05-01'
    })
    
    # Add a race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'SM01A',
        'race_id': 'SM01A',
        'name': 'WOMEN-JUNIOR J16-COXED SWEEP FOUR',
        'distance': 21,
        'event_type': '21km',
        'boat_type': '4+',
        'age_category': 'j16',
        'gender_category': 'women'
    })
    
    # Add a team manager (stored with USER# prefix for profile)
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'club_affiliation': 'Test Rowing Club',
        'email': 'test@example.com'
    })
    
    # Add crew members
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-1',
        'crew_member_id': 'crew-1',
        'first_name': 'John',
        'last_name': 'Doe',
        'date_of_birth': '2008-01-15',
        'gender': 'M'
    })
    
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-2',
        'crew_member_id': 'crew-2',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'date_of_birth': '2008-03-20',
        'gender': 'F'
    })
    
    # Add a complete boat registration
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-1',
        'boat_registration_id': 'boat-1',
        'event_type': '21km',
        'boat_type': '4+',
        'race_id': 'SM01A',
        'registration_status': 'complete',
        'forfait': False,
        'crew_assignments': [
            {
                'seat_number': 1,
                'seat_type': 'rower',
                'crew_member_id': 'CREW#crew-1'
            },
            {
                'seat_number': 4,
                'seat_type': 'rower',
                'crew_member_id': 'CREW#crew-2'
            }
        ]
    })
    
    # Add a paid boat registration
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-2',
        'boat_registration_id': 'boat-2',
        'event_type': '21km',
        'boat_type': '4+',
        'race_id': 'SM01A',
        'registration_status': 'paid',
        'forfait': False,
        'crew_assignments': [
            {
                'seat_number': 1,
                'seat_type': 'rower',
                'crew_member_id': 'CREW#crew-1'
            }
        ]
    })
    
    # Add a forfait boat (should be excluded)
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-3',
        'boat_registration_id': 'boat-3',
        'event_type': '21km',
        'boat_type': '4+',
        'race_id': 'SM01A',
        'registration_status': 'complete',
        'forfait': True,
        'crew_assignments': []
    })
    
    from admin.export_crewtimer import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/crewtimer'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Verify response structure
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert 'data' in body
    
    data = body['data']
    assert 'rows' in data
    assert 'total_races' in data
    assert 'total_boats' in data
    
    # Verify data content
    rows = data['rows']
    assert len(rows) == 2  # Should have 2 boats (complete and paid, not forfait)
    
    # Verify row structure
    first_row = rows[0]
    assert 'Event Time' in first_row
    assert 'Event Num' in first_row
    assert 'Event' in first_row
    assert 'Event Abbrev' in first_row
    assert 'Crew' in first_row
    assert 'Crew Abbrev' in first_row
    assert 'Stroke' in first_row
    assert 'Bow' in first_row
    assert 'Race Info' in first_row
    assert 'Status' in first_row
    assert 'Age' in first_row
    
    # Verify specific values
    assert first_row['Event'] == '4+ J16 WOMAN'  # Semi-marathon uses formatted name
    assert first_row['Crew'] == 'Test Rowing Club'
    assert first_row['Race Info'] == 'Head'
    assert first_row['Event Num'] == 1
    
    # Verify stats
    assert data['total_boats'] == 2
    assert data['total_races'] == 1


def test_export_crewtimer_no_boats(dynamodb_table, mock_admin_event, mock_lambda_context):
    """Test CrewTimer export with no eligible boats"""
    # Set up minimal config
    dynamodb_table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'competition_date': '2025-05-01'
    })
    
    from admin.export_crewtimer import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/crewtimer'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should still return success with empty data
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    data = body['data']
    
    assert data['rows'] == []
    assert data['total_boats'] == 0
    assert data['total_races'] == 0


def test_export_crewtimer_marathon_then_semi_marathon_order(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test that marathon races come before semi-marathon races in export"""
    # Set up config
    dynamodb_table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'competition_date': '2025-05-01'
    })
    
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'club_affiliation': 'Test Club'
    })
    
    # Add semi-marathon race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'SM01A',
        'race_id': 'SM01A',
        'name': 'Semi Marathon Race',
        'distance': 21,
        'event_type': '21km',
        'boat_type': '4+',
        'age_category': 'senior',
        'gender_category': 'mixed'
    })
    
    # Add marathon race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'M01',
        'race_id': 'M01',
        'name': 'Marathon Race',
        'distance': 42,
        'event_type': '42km',
        'boat_type': 'skiff'
    })
    
    # Add boat for semi-marathon
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-semi',
        'boat_registration_id': 'boat-semi',
        'race_id': 'SM01A',
        'registration_status': 'complete',
        'forfait': False,
        'seats': []
    })
    
    # Add boat for marathon
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-marathon',
        'boat_registration_id': 'boat-marathon',
        'race_id': 'M01',
        'registration_status': 'complete',
        'forfait': False,
        'seats': []
    })
    
    from admin.export_crewtimer import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/crewtimer'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    body = json.loads(response['body'])
    rows = body['data']['rows']
    
    # Marathon should come first (Event Num 1), then semi-marathon (Event Num 2)
    assert len(rows) == 2
    assert rows[0]['Event'] == 'Marathon Race'
    assert rows[0]['Event Num'] == 1
    assert rows[1]['Event'] == '4+ SENIOR MIXED'  # Semi-marathon uses formatted name
    assert rows[1]['Event Num'] == 2


def test_export_crewtimer_stroke_name_and_bow_numbers(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test that stroke names are correctly extracted and bow numbers are globally sequential"""
    # Set up config
    dynamodb_table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'competition_date': '2025-05-01'
    })
    
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'club_affiliation': 'Test Club'
    })
    
    # Add race
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'SM01A',
        'race_id': 'SM01A',
        'name': 'Test Race',
        'distance': 21,
        'event_type': '21km',
        'boat_type': '4-'
    })
    
    # Add crew members
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-1',
        'crew_member_id': 'crew-1',
        'first_name': 'Alice',
        'last_name': 'Stroke',  # This will be the stroke (position 4)
        'date_of_birth': '1990-01-01',
        'gender': 'F'
    })
    
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-2',
        'crew_member_id': 'crew-2',
        'first_name': 'Bob',
        'last_name': 'Bow',  # This will be bow (position 1)
        'date_of_birth': '1990-01-01',
        'gender': 'M'
    })
    
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-3',
        'crew_member_id': 'crew-3',
        'first_name': 'Charlie',
        'last_name': 'Middle',
        'date_of_birth': '1990-01-01',
        'gender': 'M'
    })
    
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-4',
        'crew_member_id': 'crew-4',
        'first_name': 'Diana',
        'last_name': 'Three',
        'date_of_birth': '1990-01-01',
        'gender': 'F'
    })
    
    # Add first boat with all seats filled
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-1',
        'boat_registration_id': 'boat-1',
        'race_id': 'SM01A',
        'registration_status': 'complete',
        'forfait': False,
        'boat_type': '4-',
        'event_type': '21km',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-2'},  # Bow
            {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-3'},
            {'position': 3, 'type': 'rower', 'crew_member_id': 'crew-4'},
            {'position': 4, 'type': 'rower', 'crew_member_id': 'crew-1'}   # Stroke
        ]
    })
    
    # Add second boat in same race
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-2',
        'boat_registration_id': 'boat-2',
        'race_id': 'SM01A',
        'registration_status': 'complete',
        'forfait': False,
        'boat_type': '4-',
        'event_type': '21km',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-3'},
            {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-4'},
            {'position': 3, 'type': 'rower', 'crew_member_id': 'crew-1'},
            {'position': 4, 'type': 'rower', 'crew_member_id': 'crew-2'}   # Stroke for boat 2
        ]
    })
    
    from admin.export_crewtimer import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/crewtimer'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    body = json.loads(response['body'])
    rows = body['data']['rows']
    
    # Should have 2 boats
    assert len(rows) == 2
    
    # First boat should have stroke name "Stroke" and bow number 1
    assert rows[0]['Stroke'] == 'Stroke', f"Expected 'Stroke' but got '{rows[0]['Stroke']}'"
    assert rows[0]['Bow'] == 1, f"Expected bow 1 but got {rows[0]['Bow']}"
    
    # Second boat should have stroke name "Bow" and bow number 2
    assert rows[1]['Stroke'] == 'Bow', f"Expected 'Bow' but got '{rows[1]['Stroke']}'"
    assert rows[1]['Bow'] == 2, f"Expected bow 2 but got {rows[1]['Bow']}"


def test_export_crewtimer_semi_marathon_race_name_formatting(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test that semi-marathon race names are formatted as: boat_type [Y] age_category gender_category"""
    # Set up config
    dynamodb_table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'competition_date': '2025-05-01'
    })
    
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'club_affiliation': 'Test Club'
    })
    
    # Add semi-marathon race with yolette
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'SM19A',
        'race_id': 'SM19A',
        'name': 'WOMEN-MASTER-COXED QUAD SCULL YOLETTE',
        'distance': 21,
        'event_type': '21km',
        'boat_type': '4x+',
        'age_category': 'master',
        'gender_category': 'women'
    })
    
    # Add semi-marathon race without yolette
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'SM01A',
        'race_id': 'SM01A',
        'name': 'WOMEN-JUNIOR J16-COXED SWEEP FOUR',
        'distance': 21,
        'event_type': '21km',
        'boat_type': '4+',
        'age_category': 'j16',
        'gender_category': 'women'
    })
    
    # Add marathon race (should keep original name)
    dynamodb_table.put_item(Item={
        'PK': 'RACE',
        'SK': 'M01',
        'race_id': 'M01',
        'name': '1X SENIOR WOMAN',
        'distance': 42,
        'event_type': '42km',
        'boat_type': 'skiff',
        'age_category': 'senior',
        'gender_category': 'women'
    })
    
    # Add crew member
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-1',
        'crew_member_id': 'crew-1',
        'first_name': 'Alice',
        'last_name': 'Smith',
        'date_of_birth': '1990-01-01',
        'gender': 'F'
    })
    
    # Add boats for each race
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-yolette',
        'boat_registration_id': 'boat-yolette',
        'race_id': 'SM19A',
        'registration_status': 'complete',
        'forfait': False,
        'boat_type': '4x+',
        'event_type': '21km',
        'seats': [{'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'}]
    })
    
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-j16',
        'boat_registration_id': 'boat-j16',
        'race_id': 'SM01A',
        'registration_status': 'complete',
        'forfait': False,
        'boat_type': '4+',
        'event_type': '21km',
        'seats': [{'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'}]
    })
    
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-marathon',
        'boat_registration_id': 'boat-marathon',
        'race_id': 'M01',
        'registration_status': 'complete',
        'forfait': False,
        'boat_type': 'skiff',
        'event_type': '42km',
        'seats': [{'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'}]
    })
    
    from admin.export_crewtimer import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/crewtimer'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    body = json.loads(response['body'])
    rows = body['data']['rows']
    
    # Should have 3 boats
    assert len(rows) == 3
    
    # Marathon race should keep original name (Event Num 1)
    marathon_row = [r for r in rows if r['Event Num'] == 1][0]
    assert marathon_row['Event'] == '1X SENIOR WOMAN'
    
    # Semi-marathon races should have Event Num 2 and 3 (one per race, not per boat)
    # Find by Event name since boats in same race have same Event Num
    j16_row = [r for r in rows if r['Event'] == '4+ J16 WOMAN'][0]
    assert j16_row['Event Num'] == 2  # Second race
    
    yolette_row = [r for r in rows if r['Event'] == '4X+ Y MASTER WOMAN'][0]
    assert yolette_row['Event Num'] == 3  # Third race


def test_export_crew_members_csv(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test crew members CSV export"""
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
    
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-2',
        'crew_member_id': 'crew-2',
        'first_name': 'Bob',
        'last_name': 'Jones',
        'gender': 'M',
        'date_of_birth': '1985-05-20',
        'age': 40,
        'license_number': 'LIC002',
        'club_affiliation': 'Test Club',
        'created_at': '2025-01-02T00:00:00Z',
        'updated_at': '2025-01-02T00:00:00Z'
    })
    
    from admin.export_crew_members import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/crew-members'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Verify response
    assert response['statusCode'] == 200
    assert response['headers']['Content-Type'] == 'text/csv'
    assert 'Content-Disposition' in response['headers']
    assert 'crew_members_export_' in response['headers']['Content-Disposition']
    
    # Verify CSV content
    csv_content = response['body']
    assert 'Crew Member ID' in csv_content
    assert 'First Name' in csv_content
    assert 'Last Name' in csv_content
    assert 'Alice' in csv_content
    assert 'Bob' in csv_content
    assert 'LIC001' in csv_content
    assert 'LIC002' in csv_content


def test_export_boat_registrations_csv_with_race_names(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id):
    """Test boat registrations CSV export includes race names"""
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
        'PK': 'CONFIG',
        'SK': 'RACE#M01',
        'race_id': 'M01',
        'name': 'Marathon Men Senior',
        'event_type': '42km',
        'boat_type': 'skiff'
    })
    
    dynamodb_table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'RACE#SM01A',
        'race_id': 'SM01A',
        'name': 'Semi-Marathon Women Junior',
        'event_type': '21km',
        'boat_type': '4+'
    })
    
    # Add boat registrations
    from decimal import Decimal
    
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-1',
        'boat_registration_id': 'boat-1',
        'event_type': '42km',
        'boat_type': 'skiff',
        'race_id': 'M01',
        'registration_status': 'complete',
        'seats': [
            {'crew_member_id': 'crew-1', 'position': 1}
        ],
        'crew_composition': {
            'gender_category': 'men',
            'avg_age': Decimal('35.5')
        },
        'is_multi_club_crew': False,
        'created_at': '2025-01-01T00:00:00Z',
        'updated_at': '2025-01-01T00:00:00Z'
    })
    
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-2',
        'boat_registration_id': 'boat-2',
        'event_type': '21km',
        'boat_type': '4+',
        'race_id': 'SM01A',
        'registration_status': 'paid',
        'seats': [
            {'crew_member_id': 'crew-1', 'position': 1},
            {'crew_member_id': 'crew-2', 'position': 2},
            {'crew_member_id': None, 'position': 3},
            {'crew_member_id': None, 'position': 4}
        ],
        'crew_composition': {
            'gender_category': 'women',
            'avg_age': Decimal('28.0')
        },
        'is_multi_club_crew': True,
        'created_at': '2025-01-02T00:00:00Z',
        'updated_at': '2025-01-02T00:00:00Z',
        'paid_at': '2025-01-03T00:00:00Z'
    })
    
    from admin.export_boat_registrations import lambda_handler
    
    event = mock_admin_event(
        http_method='GET',
        path='/admin/export/boat-registrations'
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Verify response
    assert response['statusCode'] == 200
    assert response['headers']['Content-Type'] == 'text/csv'
    assert 'Content-Disposition' in response['headers']
    assert 'boat_registrations_export_' in response['headers']['Content-Disposition']
    
    # Verify CSV content includes race names
    csv_content = response['body']
    assert 'Boat Registration ID' in csv_content
    assert 'Race Name' in csv_content
    assert 'Marathon Men Senior' in csv_content
    assert 'Semi-Marathon Women Junior' in csv_content
    assert 'boat-1' in csv_content
    assert 'boat-2' in csv_content
    assert '1/1' in csv_content  # Filled seats for boat-1
    assert '2/4' in csv_content  # Filled seats for boat-2
