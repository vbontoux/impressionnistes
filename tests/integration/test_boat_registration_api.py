"""
Integration tests for boat registration API endpoints
Tests Lambda handlers with mock DynamoDB (no authentication)
"""
import json
import pytest


@pytest.fixture
def test_crew_members(dynamodb_table, test_team_manager_id):
    """Create test crew members for boat registration tests"""
    crew_members = [
        {
            'crew_member_id': 'crew-1',
            'first_name': 'Alice',
            'last_name': 'Rower',
            'date_of_birth': '1990-01-15',
            'gender': 'F',
            'license_number': 'LIC001',
            'club_affiliation': 'RCPM'
        },
        {
            'crew_member_id': 'crew-2',
            'first_name': 'Bob',
            'last_name': 'Rower',
            'date_of_birth': '1985-05-20',
            'gender': 'M',
            'license_number': 'LIC002',
            'club_affiliation': 'RCPM'
        },
        {
            'crew_member_id': 'crew-3',
            'first_name': 'Charlie',
            'last_name': 'Rower',
            'date_of_birth': '1992-08-10',
            'gender': 'M',
            'license_number': 'LIC003',
            'club_affiliation': 'RCPM'
        },
        {
            'crew_member_id': 'crew-4',
            'first_name': 'Diana',
            'last_name': 'Rower',
            'date_of_birth': '1988-12-05',
            'gender': 'F',
            'license_number': 'LIC004',
            'club_affiliation': 'RCPM'
        }
    ]
    
    for cm in crew_members:
        dynamodb_table.put_item(Item={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'CREW#{cm["crew_member_id"]}',
            **cm
        })
    
    return crew_members


def test_create_boat_registration(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_crew_members):
    """Test creating a boat registration"""
    from boat.create_boat_registration import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'seats': [
                {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},
                {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},
                {'position': 3, 'type': 'rower', 'crew_member_id': 'crew-3'},
                {'position': 4, 'type': 'rower', 'crew_member_id': 'crew-4'}
            ]
        }),
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 201
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'boat_registration_id' in body['data']
    assert body['data']['event_type'] == '21km'
    assert body['data']['boat_type'] == '4-'
    assert len(body['data']['seats']) == 4
    
    # Verify data was saved to DynamoDB
    boat_id = body['data']['boat_registration_id']
    item = dynamodb_table.get_item(
        Key={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'BOAT#{boat_id}'
        }
    )
    
    assert 'Item' in item
    assert item['Item']['event_type'] == '21km'
    assert len(item['Item']['seats']) == 4


def test_list_boat_registrations(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test listing boat registrations"""
    # Create test boat
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'BOAT#boat-1',
        'boat_registration_id': 'boat-1',
        'event_type': '21km',
        'boat_type': '4-',
        'registration_status': 'incomplete',
        'seats': []
    })
    
    from boat.list_boat_registrations import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='GET',
        path='/boat',
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'boat_registrations' in body['data']
    assert len(body['data']['boat_registrations']) >= 1
    
    # Check boat is returned
    boat_ids = [b['boat_registration_id'] for b in body['data']['boat_registrations']]
    assert 'boat-1' in boat_ids


def test_update_boat_registration(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_crew_members):
    """Test updating a boat registration"""
    # Create a boat first
    boat_id = 'boat-update-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '21km',
        'boat_type': '4-',
        'registration_status': 'incomplete',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},
            {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None}
        ]
    })
    
    from boat.update_boat_registration import lambda_handler
    
    # Update to add more crew members
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        body=json.dumps({
            'seats': [
                {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},
                {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},
                {'position': 3, 'type': 'rower', 'crew_member_id': 'crew-3'},
                {'position': 4, 'type': 'rower', 'crew_member_id': 'crew-4'}
            ]
        }),
        path_parameters={'boat_registration_id': boat_id},
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert len(body['data']['seats']) == 4
    assert all(seat['crew_member_id'] is not None for seat in body['data']['seats'])


def test_delete_boat_registration(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test deleting a boat registration"""
    # Create a boat first
    boat_id = 'boat-delete-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '21km',
        'boat_type': '4-',
        'registration_status': 'incomplete',
        'seats': []
    })
    
    from boat.delete_boat_registration import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='DELETE',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    
    # Verify data was deleted from DynamoDB
    item = dynamodb_table.get_item(
        Key={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'BOAT#{boat_id}'
        }
    )
    
    assert 'Item' not in item


def test_cannot_delete_paid_boat(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test that paid boats cannot be deleted"""
    # Create a paid boat
    boat_id = 'boat-paid-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '21km',
        'boat_type': '4-',
        'registration_status': 'paid',  # Paid status
        'seats': []
    })
    
    from boat.delete_boat_registration import lambda_handler
    
    # Try to delete
    event = mock_api_gateway_event(
        http_method='DELETE',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert error response
    assert response['statusCode'] == 403
    
    body = json.loads(response['body'])
    assert body['success'] is False
    
    # Verify boat still exists in DynamoDB
    item = dynamodb_table.get_item(
        Key={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'BOAT#{boat_id}'
        }
    )
    
    assert 'Item' in item



def test_create_boat_initializes_club_fields(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """
    Test that creating a boat initializes club fields with team manager's club
    
    **Validates: Requirements 3.5**
    """
    # Create team manager profile with club affiliation
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': 'RCPM',
        'mobile_number': '+33612345678'
    })
    
    from boat.create_boat_registration import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4+',
        }),
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Debug: print response if not 201
    if response['statusCode'] != 201:
        print(f"Response: {json.dumps(json.loads(response['body']), indent=2)}")
    
    # Assert response
    assert response['statusCode'] == 201
    
    body = json.loads(response['body'])
    assert body['success'] is True
    
    # Verify club fields are initialized
    boat_data = body['data']
    assert 'boat_club_display' in boat_data
    assert 'club_list' in boat_data
    
    # Should show team manager's club (no crew assigned yet)
    assert boat_data['boat_club_display'] == 'RCPM'
    assert boat_data['club_list'] == ['RCPM']
    
    # Verify data was saved to DynamoDB with club fields
    boat_id = boat_data['boat_registration_id']
    item = dynamodb_table.get_item(
        Key={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'BOAT#{boat_id}'
        }
    )
    
    assert 'Item' in item
    assert item['Item']['boat_club_display'] == 'RCPM'
    assert item['Item']['club_list'] == ['RCPM']


def test_create_boat_with_empty_team_manager_club(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """
    Test that creating a boat handles empty team manager club gracefully
    
    **Validates: Requirements 3.5**
    """
    # Create team manager profile with empty club affiliation
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': '',  # Empty club
        'mobile_number': '+33612345678'
    })
    
    from boat.create_boat_registration import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '42km',
            'boat_type': 'skiff',
        }),
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 201
    
    body = json.loads(response['body'])
    assert body['success'] is True
    
    # Verify club fields handle empty club
    boat_data = body['data']
    assert boat_data['boat_club_display'] == ''
    assert boat_data['club_list'] == []


def test_create_boat_with_different_team_manager_clubs(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """
    Test that boat club fields reflect different team manager clubs
    
    **Validates: Requirements 3.5**
    """
    # Test with Club Elite
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': 'Club Elite',
        'mobile_number': '+33612345678'
    })
    
    from boat.create_boat_registration import lambda_handler
    
    # Create boat
    event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '8+',
        }),
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    
    # Should show Club Elite
    assert body['data']['boat_club_display'] == 'Club Elite'
    assert body['data']['club_list'] == ['Club Elite']



# ============================================================================
# Seat Assignment and Club Recalculation Tests
# ============================================================================

def test_assign_seat_recalculates_club_single_club(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """
    Test that assigning crew from single club updates club display correctly
    
    **Validates: Requirements 3.3**
    """
    # Create team manager profile
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': 'RCPM',
        'mobile_number': '+33612345678'
    })
    
    # Create crew members from RCPM
    crew_members = [
        {
            'crew_member_id': 'crew-1',
            'first_name': 'Alice',
            'last_name': 'Rower',
            'date_of_birth': '1990-01-15',
            'gender': 'F',
            'license_number': 'LIC001',
            'club_affiliation': 'RCPM'
        },
        {
            'crew_member_id': 'crew-2',
            'first_name': 'Bob',
            'last_name': 'Rower',
            'date_of_birth': '1985-05-20',
            'gender': 'M',
            'license_number': 'LIC002',
            'club_affiliation': 'RCPM'
        }
    ]
    
    for cm in crew_members:
        dynamodb_table.put_item(Item={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'CREW#{cm["crew_member_id"]}',
            **cm
        })
    
    # Create a boat
    boat_id = 'boat-assign-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '21km',
        'boat_type': '4-',
        'registration_status': 'incomplete',
        'boat_club_display': 'RCPM',  # Initial value
        'club_list': ['RCPM'],
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None}
        ]
    })
    
    from boat.assign_seat import lambda_handler
    
    # Assign first crew member
    event = mock_api_gateway_event(
        http_method='POST',
        path=f'/boat/{boat_id}/seat',
        body=json.dumps({
            'position': 1,
            'crew_member_id': 'crew-1'
        }),
        path_parameters={'boat_registration_id': boat_id},
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    
    # Should still show RCPM (single club)
    assert body['data']['boat_club_display'] == 'RCPM'
    assert body['data']['club_list'] == ['RCPM']
    assert body['data']['is_multi_club_crew'] is False


def test_assign_seat_recalculates_club_multi_club(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """
    Test that assigning crew from multiple clubs shows Multi-Club
    
    **Validates: Requirements 3.3**
    """
    # Create team manager profile
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': 'RCPM',
        'mobile_number': '+33612345678'
    })
    
    # Create crew members from different clubs
    crew_members = [
        {
            'crew_member_id': 'crew-1',
            'first_name': 'Alice',
            'last_name': 'Rower',
            'date_of_birth': '1990-01-15',
            'gender': 'F',
            'license_number': 'LIC001',
            'club_affiliation': 'RCPM'
        },
        {
            'crew_member_id': 'crew-2',
            'first_name': 'Bob',
            'last_name': 'Rower',
            'date_of_birth': '1985-05-20',
            'gender': 'M',
            'license_number': 'LIC002',
            'club_affiliation': 'Club Elite'
        }
    ]
    
    for cm in crew_members:
        dynamodb_table.put_item(Item={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'CREW#{cm["crew_member_id"]}',
            **cm
        })
    
    # Create a boat
    boat_id = 'boat-multiclub-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '21km',
        'boat_type': '4-',
        'registration_status': 'incomplete',
        'boat_club_display': 'RCPM',
        'club_list': ['RCPM'],
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},  # RCPM
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None}
        ]
    })
    
    from boat.assign_seat import lambda_handler
    
    # Assign second crew member from different club
    event = mock_api_gateway_event(
        http_method='POST',
        path=f'/boat/{boat_id}/seat',
        body=json.dumps({
            'position': 2,
            'crew_member_id': 'crew-2'
        }),
        path_parameters={'boat_registration_id': boat_id},
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    
    # Should show simplified comma-separated format
    assert body['data']['boat_club_display'] == 'Club Elite, RCPM'  # Alphabetically sorted
    assert len(body['data']['club_list']) == 2
    assert 'RCPM' in body['data']['club_list']
    assert 'Club Elite' in body['data']['club_list']
    assert body['data']['is_multi_club_crew'] is True


def test_unassign_seat_recalculates_club(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """
    Test that removing a crew member recalculates club display
    
    **Validates: Requirements 3.3**
    """
    # Create team manager profile
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': 'RCPM',
        'mobile_number': '+33612345678'
    })
    
    # Create crew members
    crew_members = [
        {
            'crew_member_id': 'crew-1',
            'first_name': 'Alice',
            'last_name': 'Rower',
            'date_of_birth': '1990-01-15',
            'gender': 'F',
            'license_number': 'LIC001',
            'club_affiliation': 'RCPM',
            'assigned_boat_id': 'boat-unassign-test'
        },
        {
            'crew_member_id': 'crew-2',
            'first_name': 'Bob',
            'last_name': 'Rower',
            'date_of_birth': '1985-05-20',
            'gender': 'M',
            'license_number': 'LIC002',
            'club_affiliation': 'Club Elite',
            'assigned_boat_id': 'boat-unassign-test'
        }
    ]
    
    for cm in crew_members:
        dynamodb_table.put_item(Item={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'CREW#{cm["crew_member_id"]}',
            **cm
        })
    
    # Create a boat with multi-club crew
    boat_id = 'boat-unassign-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '21km',
        'boat_type': '4-',
        'registration_status': 'incomplete',
        'boat_club_display': 'RCPM (Multi-Club)',
        'club_list': ['Club Elite', 'RCPM'],
        'is_multi_club_crew': True,
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},  # RCPM
            {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},  # Club Elite
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None}
        ]
    })
    
    from boat.assign_seat import lambda_handler
    
    # Remove crew member from Club Elite
    event = mock_api_gateway_event(
        http_method='POST',
        path=f'/boat/{boat_id}/seat',
        body=json.dumps({
            'position': 2,
            'crew_member_id': None  # Unassign
        }),
        path_parameters={'boat_registration_id': boat_id},
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    
    # Should now show single club (RCPM only)
    assert body['data']['boat_club_display'] == 'RCPM'
    assert body['data']['club_list'] == ['RCPM']
    assert body['data']['is_multi_club_crew'] is False


# ============================================================================
# Task 5.2: Integration tests for update_boat_registration club recalculation
# ============================================================================

def test_update_boat_seats_recalculates_club_single_club(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """
    Test that updating boat seats with single club crew updates club display correctly
    
    **Validates: Requirements 3.4**
    """
    # Create team manager profile
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': 'RCPM',
        'mobile_number': '+33612345678'
    })
    
    # Create crew members from same club
    crew_members = [
        {
            'crew_member_id': 'crew-1',
            'first_name': 'Alice',
            'last_name': 'Rower',
            'date_of_birth': '1990-01-15',
            'gender': 'F',
            'license_number': 'LIC001',
            'club_affiliation': 'RCPM',
            'assigned_boat_id': None
        },
        {
            'crew_member_id': 'crew-2',
            'first_name': 'Bob',
            'last_name': 'Rower',
            'date_of_birth': '1985-05-20',
            'gender': 'M',
            'license_number': 'LIC002',
            'club_affiliation': 'RCPM',
            'assigned_boat_id': None
        }
    ]
    
    for cm in crew_members:
        dynamodb_table.put_item(Item={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'CREW#{cm["crew_member_id"]}',
            **cm
        })
    
    # Create a boat with empty seats
    boat_id = 'boat-update-single-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '21km',
        'boat_type': '4-',
        'registration_status': 'incomplete',
        'boat_club_display': 'RCPM',
        'club_list': ['RCPM'],
        'is_multi_club_crew': False,
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None}
        ]
    })
    
    from boat.update_boat_registration import lambda_handler
    
    # Update boat with crew from same club
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        body=json.dumps({
            'seats': [
                {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},
                {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},
                {'position': 3, 'type': 'rower', 'crew_member_id': None},
                {'position': 4, 'type': 'rower', 'crew_member_id': None}
            ]
        }),
        path_parameters={'boat_registration_id': boat_id},
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    
    # Should show single club (RCPM)
    assert body['data']['boat_club_display'] == 'RCPM'
    assert body['data']['club_list'] == ['RCPM']
    assert body['data']['is_multi_club_crew'] is False


def test_update_boat_seats_recalculates_club_multi_club(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """
    Test that updating boat seats with multi-club crew shows Multi-Club
    
    **Validates: Requirements 3.4**
    """
    # Create team manager profile
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': 'RCPM',
        'mobile_number': '+33612345678'
    })
    
    # Create crew members from different clubs
    crew_members = [
        {
            'crew_member_id': 'crew-1',
            'first_name': 'Alice',
            'last_name': 'Rower',
            'date_of_birth': '1990-01-15',
            'gender': 'F',
            'license_number': 'LIC001',
            'club_affiliation': 'RCPM',
            'assigned_boat_id': None
        },
        {
            'crew_member_id': 'crew-2',
            'first_name': 'Bob',
            'last_name': 'Rower',
            'date_of_birth': '1985-05-20',
            'gender': 'M',
            'license_number': 'LIC002',
            'club_affiliation': 'Club Elite',
            'assigned_boat_id': None
        },
        {
            'crew_member_id': 'crew-3',
            'first_name': 'Charlie',
            'last_name': 'Rower',
            'date_of_birth': '1992-03-10',
            'gender': 'M',
            'license_number': 'LIC003',
            'club_affiliation': 'Aviron Paris',
            'assigned_boat_id': None
        }
    ]
    
    for cm in crew_members:
        dynamodb_table.put_item(Item={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'CREW#{cm["crew_member_id"]}',
            **cm
        })
    
    # Create a boat with empty seats
    boat_id = 'boat-update-multi-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '21km',
        'boat_type': '4-',
        'registration_status': 'incomplete',
        'boat_club_display': 'RCPM',
        'club_list': ['RCPM'],
        'is_multi_club_crew': False,
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None}
        ]
    })
    
    from boat.update_boat_registration import lambda_handler
    
    # Update boat with crew from multiple clubs
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        body=json.dumps({
            'seats': [
                {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},  # RCPM
                {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},  # Club Elite
                {'position': 3, 'type': 'rower', 'crew_member_id': 'crew-3'},  # Aviron Paris
                {'position': 4, 'type': 'rower', 'crew_member_id': None}
            ]
        }),
        path_parameters={'boat_registration_id': boat_id},
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    
    # Should show simplified comma-separated format
    assert body['data']['boat_club_display'] == 'Aviron Paris, Club Elite, RCPM'  # Alphabetically sorted
    assert len(body['data']['club_list']) == 3
    assert 'RCPM' in body['data']['club_list']
    assert 'Club Elite' in body['data']['club_list']
    assert 'Aviron Paris' in body['data']['club_list']
    assert body['data']['is_multi_club_crew'] is True


def test_update_boat_seats_bulk_unassign_recalculates_club(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """
    Test that bulk updating seats (removing crew members) recalculates club display
    
    **Validates: Requirements 3.4**
    """
    # Create team manager profile
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': 'RCPM',
        'mobile_number': '+33612345678'
    })
    
    # Create crew members
    crew_members = [
        {
            'crew_member_id': 'crew-1',
            'first_name': 'Alice',
            'last_name': 'Rower',
            'date_of_birth': '1990-01-15',
            'gender': 'F',
            'license_number': 'LIC001',
            'club_affiliation': 'RCPM',
            'assigned_boat_id': 'boat-bulk-update-test'
        },
        {
            'crew_member_id': 'crew-2',
            'first_name': 'Bob',
            'last_name': 'Rower',
            'date_of_birth': '1985-05-20',
            'gender': 'M',
            'license_number': 'LIC002',
            'club_affiliation': 'Club Elite',
            'assigned_boat_id': 'boat-bulk-update-test'
        }
    ]
    
    for cm in crew_members:
        dynamodb_table.put_item(Item={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'CREW#{cm["crew_member_id"]}',
            **cm
        })
    
    # Create a boat with multi-club crew
    boat_id = 'boat-bulk-update-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '21km',
        'boat_type': '4-',
        'registration_status': 'incomplete',
        'boat_club_display': 'RCPM (Multi-Club)',
        'club_list': ['Club Elite', 'RCPM'],
        'is_multi_club_crew': True,
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},  # RCPM
            {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},  # Club Elite
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None}
        ]
    })
    
    from boat.update_boat_registration import lambda_handler
    
    # Remove crew member from Club Elite via bulk update
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        body=json.dumps({
            'seats': [
                {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},  # Keep RCPM
                {'position': 2, 'type': 'rower', 'crew_member_id': None},      # Remove Club Elite
                {'position': 3, 'type': 'rower', 'crew_member_id': None},
                {'position': 4, 'type': 'rower', 'crew_member_id': None}
            ]
        }),
        path_parameters={'boat_registration_id': boat_id},
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    
    # Should now show single club (RCPM only)
    assert body['data']['boat_club_display'] == 'RCPM'
    assert body['data']['club_list'] == ['RCPM']
    assert body['data']['is_multi_club_crew'] is False



def test_update_team_manager_club_recalculates_empty_boats(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test that updating team manager's club recalculates club info for empty boats only"""
    from unittest.mock import patch
    
    # Seed team manager profile (using correct SK format)
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',  # Correct SK format
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': 'RCPM',
        'mobile_number': '+33612345678'  # Required field
    })
    
    # Create an empty boat (no crew assigned)
    empty_boat_id = 'boat-empty-123'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{empty_boat_id}',
        'boat_registration_id': empty_boat_id,
        'team_manager_id': test_team_manager_id,
        'boat_club_display': 'RCPM',
        'club_list': ['RCPM'],
        'is_multi_club_crew': False,
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None}
        ]
    })
    
    # Create a boat with crew assigned
    crew_member_id = 'crew-123'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'CREW#{crew_member_id}',
        'crew_member_id': crew_member_id,
        'first_name': 'Test',
        'last_name': 'Rower',
        'date_of_birth': '1990-01-01',
        'gender': 'M',
        'license_number': 'LIC999',
        'club_affiliation': 'Club Elite'
    })
    
    boat_with_crew_id = 'boat-with-crew-456'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_with_crew_id}',
        'boat_registration_id': boat_with_crew_id,
        'team_manager_id': test_team_manager_id,
        'boat_club_display': 'RCPM (Club Elite)',
        'club_list': ['Club Elite'],
        'is_multi_club_crew': False,
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': crew_member_id}
        ]
    })
    
    # Import Lambda handler
    from auth.update_profile import lambda_handler
    
    # Mock Cognito client to avoid actual AWS calls
    with patch('auth.update_profile.cognito') as mock_cognito:
        mock_cognito.admin_update_user_attributes.return_value = {}
        
        # Update team manager's club
        event = mock_api_gateway_event(
            http_method='PUT',
            path='/auth/profile',
            body=json.dumps({
                'first_name': 'Test',
                'last_name': 'Manager',
                'club_affiliation': 'SN Versailles'  # Changed from RCPM
            }),
            user_id=test_team_manager_id
        )
        
        # Set USER_POOL_ID environment variable
        with patch.dict('os.environ', {'USER_POOL_ID': 'test-pool-id'}):
            # Call Lambda handler
            response = lambda_handler(event, mock_lambda_context)
        
        # Assert response
        assert response['statusCode'] == 200
        
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['data']['club_affiliation'] == 'SN Versailles'
    
    # Verify empty boat club info was recalculated
    empty_boat_item = dynamodb_table.get_item(
        Key={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'BOAT#{empty_boat_id}'
        }
    )
    
    assert 'Item' in empty_boat_item
    empty_boat = empty_boat_item['Item']
    assert empty_boat['boat_club_display'] == 'SN Versailles'
    assert 'SN Versailles' in empty_boat['club_list']
    
    # Verify boat with crew was NOT recalculated (should still show external crew)
    boat_with_crew_item = dynamodb_table.get_item(
        Key={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'BOAT#{boat_with_crew_id}'
        }
    )
    
    assert 'Item' in boat_with_crew_item
    boat_with_crew = boat_with_crew_item['Item']
    # Should still show the crew's club, not the updated team manager club
    assert boat_with_crew['boat_club_display'] == 'RCPM (Club Elite)'
    assert 'Club Elite' in boat_with_crew['club_list']



# ============================================================================
# Integration Tests for Race Assignment and Boat Number Generation (Task 4.3)
# ============================================================================

def test_race_assignment_generates_boat_number(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile, test_crew_members, test_races):
    """
    Integration Test: Assign race to boat, verify boat_number is generated
    
    **Validates: Requirements 2.6, 2.7, 2.8, 2.9, 3.1**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.update_boat_registration import lambda_handler as update_handler
    
    # Create a boat without a race
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-'
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Verify boat has no boat_number initially
    assert create_body['data'].get('boat_number') is None
    
    # Assign a race to the boat
    update_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        body=json.dumps({
            'race_id': 'race-15'  # First 21km race
        }),
        user_id=test_team_manager_id
    )
    
    update_response = update_handler(update_event, mock_lambda_context)
    assert update_response['statusCode'] == 200
    
    update_body = json.loads(update_response['body'])
    
    # Verify boat_number was generated
    assert update_body['data']['boat_number'] is not None
    assert update_body['data']['boat_number'].startswith('SM.15.')
    assert update_body['data']['boat_number'] == 'SM.15.1'  # First boat in this race


def test_race_change_updates_boat_number(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile, test_crew_members, test_races):
    """
    Integration Test: Change boat's race, verify boat_number updates
    
    **Validates: Requirements 2.6, 2.7, 2.8, 2.9, 3.1**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.update_boat_registration import lambda_handler as update_handler
    
    # Create a boat with a race
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'race_id': 'race-15'
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    initial_boat_number = create_body['data'].get('boat_number')
    
    # Verify initial boat_number
    assert initial_boat_number is not None
    assert initial_boat_number.startswith('SM.15.')
    
    # Change to a different race
    update_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        body=json.dumps({
            'race_id': 'race-20'  # Different 21km race
        }),
        user_id=test_team_manager_id
    )
    
    update_response = update_handler(update_event, mock_lambda_context)
    assert update_response['statusCode'] == 200
    
    update_body = json.loads(update_response['body'])
    new_boat_number = update_body['data']['boat_number']
    
    # Verify boat_number was regenerated
    assert new_boat_number is not None
    assert new_boat_number.startswith('SM.20.')
    assert new_boat_number != initial_boat_number
    assert new_boat_number == 'SM.20.1'  # First boat in race-20


def test_race_removal_clears_boat_number(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile, test_crew_members, test_races):
    """
    Integration Test: Remove race from boat, verify boat_number is null
    
    **Validates: Requirements 2.6, 2.7, 2.8, 2.9, 3.1**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.update_boat_registration import lambda_handler as update_handler
    
    # Create a boat with a race
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'race_id': 'race-15'
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Verify boat has boat_number
    assert create_body['data'].get('boat_number') is not None
    
    # Remove the race
    update_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        body=json.dumps({
            'race_id': None  # Clear the race
        }),
        user_id=test_team_manager_id
    )
    
    update_response = update_handler(update_event, mock_lambda_context)
    assert update_response['statusCode'] == 200
    
    update_body = json.loads(update_response['body'])
    
    # Verify boat_number was cleared
    assert update_body['data'].get('boat_number') is None


def test_multiple_boats_same_race_unique_sequences(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile, test_crew_members, test_races):
    """
    Integration Test: Assign multiple boats to same race, verify unique sequences
    
    **Validates: Requirements 2.6, 2.7, 2.8, 2.9, 3.1**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    
    boat_numbers = []
    
    # Create 5 boats in the same race
    for i in range(5):
        create_event = mock_api_gateway_event(
            http_method='POST',
            path='/boat',
            body=json.dumps({
                'event_type': '21km',
                'boat_type': '4-',
                'race_id': 'race-15'
            }),
            user_id=test_team_manager_id
        )
        
        create_response = create_handler(create_event, mock_lambda_context)
        assert create_response['statusCode'] == 201
        
        create_body = json.loads(create_response['body'])
        boat_number = create_body['data'].get('boat_number')
        
        # Verify boat_number was generated
        assert boat_number is not None
        assert boat_number.startswith('SM.15.')
        
        boat_numbers.append(boat_number)
    
    # Verify all boat_numbers are unique
    assert len(boat_numbers) == len(set(boat_numbers))
    
    # Verify sequences are sequential
    expected_numbers = ['SM.15.1', 'SM.15.2', 'SM.15.3', 'SM.15.4', 'SM.15.5']
    assert boat_numbers == expected_numbers


def test_boat_number_persists_across_updates(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile, test_crew_members, test_races):
    """
    Integration Test: Boat number persists when updating other fields
    
    Verify that boat_number doesn't change when updating fields other than race_id
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.update_boat_registration import lambda_handler as update_handler
    
    # Create a boat with a race
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'race_id': 'race-15'
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    original_boat_number = create_body['data'].get('boat_number')
    
    assert original_boat_number is not None
    
    # Update seats (not race_id)
    update_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        body=json.dumps({
            'seats': [
                {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},
                {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},
                {'position': 3, 'type': 'rower', 'crew_member_id': 'crew-3'},
                {'position': 4, 'type': 'rower', 'crew_member_id': 'crew-4'}
            ]
        }),
        user_id=test_team_manager_id
    )
    
    update_response = update_handler(update_event, mock_lambda_context)
    assert update_response['statusCode'] == 200
    
    update_body = json.loads(update_response['body'])
    updated_boat_number = update_body['data'].get('boat_number')
    
    # Verify boat_number didn't change
    assert updated_boat_number == original_boat_number


# ============================================================================
# Boat Request Comment Validation Tests (Task 1.2)
# ============================================================================

def test_boat_request_comment_valid_length(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile):
    """
    Test that boat_request_comment up to 500 characters is accepted
    
    **Validates: Requirements 2.2 - Property 4: Boat Request Comment Length Validation**
    """
    from boat.create_boat_registration import lambda_handler
    
    # Create comment with exactly 500 characters
    comment_500 = 'a' * 500
    
    event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4+',
            'boat_request_enabled': True,
            'boat_request_comment': comment_500
        }),
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be accepted
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['boat_request_comment'] == comment_500


def test_boat_request_comment_exceeds_max_length(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile):
    """
    Test that boat_request_comment over 500 characters is rejected
    
    **Validates: Requirements 2.2 - Property 4: Boat Request Comment Length Validation**
    """
    from boat.create_boat_registration import lambda_handler
    
    # Create comment with 501 characters
    comment_501 = 'a' * 501
    
    event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4+',
            'boat_request_enabled': True,
            'boat_request_comment': comment_501
        }),
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be rejected
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'boat_request_comment' in body['error']['details']


def test_boat_request_comment_empty_string(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile):
    """
    Test that empty boat_request_comment is accepted (optional field)
    
    **Validates: Requirements 2.2, 2.5 - Property 4: Boat Request Comment Length Validation**
    """
    from boat.create_boat_registration import lambda_handler
    
    event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4+',
            'boat_request_enabled': True,
            'boat_request_comment': ''
        }),
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be accepted
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert body['success'] is True


def test_boat_request_comment_null(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile):
    """
    Test that null boat_request_comment is accepted (optional field)
    
    **Validates: Requirements 2.2, 2.5 - Property 4: Boat Request Comment Length Validation**
    """
    from boat.create_boat_registration import lambda_handler
    
    event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4+',
            'boat_request_enabled': True,
            'boat_request_comment': None
        }),
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be accepted
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert body['success'] is True


def test_boat_request_comment_with_special_characters(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile):
    """
    Test that boat_request_comment with special characters is accepted
    
    **Validates: Requirements 2.2, 2.6 - Property 4: Boat Request Comment Length Validation**
    """
    from boat.create_boat_registration import lambda_handler
    
    comment = "Beginner level, need stable boat! Prefer #42 if available. Contact: john@example.com"
    
    event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4+',
            'boat_request_enabled': True,
            'boat_request_comment': comment
        }),
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be accepted
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['boat_request_comment'] == comment


def test_boat_request_comment_with_line_breaks(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile):
    """
    Test that boat_request_comment with line breaks is accepted
    
    **Validates: Requirements 2.2, 2.6 - Property 4: Boat Request Comment Length Validation**
    """
    from boat.create_boat_registration import lambda_handler
    
    comment = "Requirements:\n- Beginner level\n- Stable boat\n- Prefer boat #42"
    
    event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4+',
            'boat_request_enabled': True,
            'boat_request_comment': comment
        }),
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be accepted
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert body['success'] is True
    # Line breaks should be preserved
    assert '\n' in body['data']['boat_request_comment']


def test_boat_request_comment_boundary_499_chars(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile):
    """
    Test that boat_request_comment with 499 characters is accepted (boundary test)
    
    **Validates: Requirements 2.2 - Property 4: Boat Request Comment Length Validation**
    """
    from boat.create_boat_registration import lambda_handler
    
    comment_499 = 'a' * 499
    
    event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4+',
            'boat_request_enabled': True,
            'boat_request_comment': comment_499
        }),
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be accepted
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert body['success'] is True
    assert len(body['data']['boat_request_comment']) == 499


# ============================================================================
# Task 1.2: Assigned Boat Identifier Validation Tests
# ============================================================================

def test_assigned_boat_identifier_exactly_100_chars(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id, test_team_manager_profile):
    """
    Test that assigned_boat_identifier with exactly 100 characters is accepted (boundary test)
    
    **Validates: Requirements 5.3 - Assigned Boat Name Length Validation**
    """
    # Create a boat with boat request enabled
    boat_id = 'boat-assign-100-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '42km',
        'boat_type': '4+',
        'registration_status': 'incomplete',
        'boat_request_enabled': True,
        'boat_request_comment': 'Need a boat',
        'assigned_boat_identifier': None,
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ]
    })
    
    from admin.admin_update_boat import lambda_handler
    
    boat_name_100 = 'a' * 100
    
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/admin/teams/{test_team_manager_id}/boats/{boat_id}',
        body=json.dumps({
            'assigned_boat_identifier': boat_name_100
        }),
        path_parameters={
            'team_manager_id': test_team_manager_id,
            'boat_registration_id': boat_id
        },
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be accepted
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert len(body['data']['assigned_boat_identifier']) == 100


def test_assigned_boat_identifier_101_chars_rejected(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id, test_team_manager_profile):
    """
    Test that assigned_boat_identifier with 101 characters is rejected (boundary test)
    
    **Validates: Requirements 5.3 - Assigned Boat Name Length Validation**
    """
    # Create a boat with boat request enabled
    boat_id = 'boat-assign-101-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '42km',
        'boat_type': '4+',
        'registration_status': 'incomplete',
        'boat_request_enabled': True,
        'boat_request_comment': 'Need a boat',
        'assigned_boat_identifier': None,
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ]
    })
    
    from admin.admin_update_boat import lambda_handler
    
    boat_name_101 = 'a' * 101
    
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/admin/teams/{test_team_manager_id}/boats/{boat_id}',
        body=json.dumps({
            'assigned_boat_identifier': boat_name_101
        }),
        path_parameters={
            'team_manager_id': test_team_manager_id,
            'boat_registration_id': boat_id
        },
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be rejected
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'assigned_boat_identifier' in body['error']['details']


def test_assigned_boat_identifier_empty_string_accepted(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id, test_team_manager_profile):
    """
    Test that empty string for assigned_boat_identifier is accepted (clears assignment)
    
    **Validates: Requirements 5.3 - Assigned Boat Name Length Validation**
    """
    # Create a boat with boat request enabled and already assigned
    boat_id = 'boat-assign-empty-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '42km',
        'boat_type': '4+',
        'registration_status': 'incomplete',
        'boat_request_enabled': True,
        'boat_request_comment': 'Need a boat',
        'assigned_boat_identifier': 'Boat 42',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ]
    })
    
    from admin.admin_update_boat import lambda_handler
    
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/admin/teams/{test_team_manager_id}/boats/{boat_id}',
        body=json.dumps({
            'assigned_boat_identifier': ''
        }),
        path_parameters={
            'team_manager_id': test_team_manager_id,
            'boat_registration_id': boat_id
        },
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be accepted (clears assignment)
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    # Empty string should be converted to None
    assert body['data']['assigned_boat_identifier'] is None or body['data']['assigned_boat_identifier'] == ''


def test_assigned_boat_identifier_null_accepted(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id, test_team_manager_profile):
    """
    Test that null for assigned_boat_identifier is accepted (no assignment)
    
    **Validates: Requirements 5.3 - Assigned Boat Name Length Validation**
    """
    # Create a boat with boat request enabled
    boat_id = 'boat-assign-null-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '42km',
        'boat_type': '4+',
        'registration_status': 'incomplete',
        'boat_request_enabled': True,
        'boat_request_comment': 'Need a boat',
        'assigned_boat_identifier': None,
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ]
    })
    
    from admin.admin_update_boat import lambda_handler
    
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/admin/teams/{test_team_manager_id}/boats/{boat_id}',
        body=json.dumps({
            'assigned_boat_identifier': None
        }),
        path_parameters={
            'team_manager_id': test_team_manager_id,
            'boat_registration_id': boat_id
        },
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be accepted
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['assigned_boat_identifier'] is None


def test_assigned_boat_identifier_with_alphanumeric(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id, test_team_manager_profile):
    """
    Test that boat names with alphanumeric characters are accepted
    
    **Validates: Requirements 5.3, 8.9 - Assigned Boat Name Character Acceptance**
    """
    # Create a boat with boat request enabled
    boat_id = 'boat-assign-alphanum-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '42km',
        'boat_type': '4+',
        'registration_status': 'incomplete',
        'boat_request_enabled': True,
        'boat_request_comment': 'Need a boat',
        'assigned_boat_identifier': None,
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ]
    })
    
    from admin.admin_update_boat import lambda_handler
    
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/admin/teams/{test_team_manager_id}/boats/{boat_id}',
        body=json.dumps({
            'assigned_boat_identifier': 'Boat42'
        }),
        path_parameters={
            'team_manager_id': test_team_manager_id,
            'boat_registration_id': boat_id
        },
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be accepted
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['assigned_boat_identifier'] == 'Boat42'


def test_assigned_boat_identifier_with_special_characters(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id, test_team_manager_profile):
    """
    Test that boat names with common punctuation are accepted
    
    **Validates: Requirements 5.3, 8.9 - Assigned Boat Name Character Acceptance**
    """
    # Create a boat with boat request enabled
    boat_id = 'boat-assign-special-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '42km',
        'boat_type': '4+',
        'registration_status': 'incomplete',
        'boat_request_enabled': True,
        'boat_request_comment': 'Need a boat',
        'assigned_boat_identifier': None,
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ]
    })
    
    from admin.admin_update_boat import lambda_handler
    
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/admin/teams/{test_team_manager_id}/boats/{boat_id}',
        body=json.dumps({
            'assigned_boat_identifier': 'Elite Shell #42 - Rack A/3'
        }),
        path_parameters={
            'team_manager_id': test_team_manager_id,
            'boat_registration_id': boat_id
        },
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be accepted
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['assigned_boat_identifier'] == 'Elite Shell #42 - Rack A/3'


def test_assigned_boat_identifier_with_spaces(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id, test_team_manager_profile):
    """
    Test that boat names with spaces are accepted
    
    **Validates: Requirements 5.3, 8.9 - Assigned Boat Name Character Acceptance**
    """
    # Create a boat with boat request enabled
    boat_id = 'boat-assign-spaces-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_id}',
        'boat_registration_id': boat_id,
        'event_type': '42km',
        'boat_type': '4+',
        'registration_status': 'incomplete',
        'boat_request_enabled': True,
        'boat_request_comment': 'Need a boat',
        'assigned_boat_identifier': None,
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': None},
            {'position': 2, 'type': 'rower', 'crew_member_id': None},
            {'position': 3, 'type': 'rower', 'crew_member_id': None},
            {'position': 4, 'type': 'rower', 'crew_member_id': None},
            {'position': 5, 'type': 'cox', 'crew_member_id': None}
        ]
    })
    
    from admin.admin_update_boat import lambda_handler
    
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/admin/teams/{test_team_manager_id}/boats/{boat_id}',
        body=json.dumps({
            'assigned_boat_identifier': 'Racing Shell 42'
        }),
        path_parameters={
            'team_manager_id': test_team_manager_id,
            'boat_registration_id': boat_id
        },
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be accepted
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['assigned_boat_identifier'] == 'Racing Shell 42'



# ============================================================================
# Task 2.2: Completion Status Tests for Boat Request
# ============================================================================

def test_completion_status_boat_request_enabled_no_assignment_incomplete(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile, test_crew_members, test_races):
    """
    Test that crew with boat_request_enabled=true and no assignment is incomplete
    
    **Validates: Requirements 4.1, 4.2 - Boat request enabled but no boat assigned**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.update_boat_registration import lambda_handler as update_handler
    
    # Create a boat with boat request enabled
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'boat_request_enabled': True,
            'boat_request_comment': 'Need a boat please'
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Fill all seats and select a race
    update_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        body=json.dumps({
            'race_id': 'race-15',
            'seats': [
                {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},
                {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},
                {'position': 3, 'type': 'rower', 'crew_member_id': 'crew-3'},
                {'position': 4, 'type': 'rower', 'crew_member_id': 'crew-4'}
            ]
        }),
        user_id=test_team_manager_id
    )
    
    update_response = update_handler(update_event, mock_lambda_context)
    assert update_response['statusCode'] == 200
    
    update_body = json.loads(update_response['body'])
    
    # Should be incomplete because boat_request_enabled=true but no assigned_boat_identifier
    assert update_body['data']['registration_status'] == 'incomplete'
    assert update_body['data']['boat_request_enabled'] is True
    assert update_body['data'].get('assigned_boat_identifier') is None


def test_completion_status_boat_request_enabled_with_assignment_complete(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile, test_crew_members, test_races, test_admin_id):
    """
    Test that crew with boat_request_enabled=true and assignment can be complete
    
    **Validates: Requirements 4.1, 4.3 - Boat request enabled with boat assigned**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.update_boat_registration import lambda_handler as update_handler
    from admin.admin_update_boat import lambda_handler as admin_handler
    
    # Create a boat with boat request enabled
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'boat_request_enabled': True,
            'boat_request_comment': 'Need a boat please'
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Fill all seats and select a race
    update_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        body=json.dumps({
            'race_id': 'race-15',
            'seats': [
                {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},
                {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},
                {'position': 3, 'type': 'rower', 'crew_member_id': 'crew-3'},
                {'position': 4, 'type': 'rower', 'crew_member_id': 'crew-4'}
            ]
        }),
        user_id=test_team_manager_id
    )
    
    update_response = update_handler(update_event, mock_lambda_context)
    assert update_response['statusCode'] == 200
    
    # Should be incomplete before assignment
    update_body = json.loads(update_response['body'])
    assert update_body['data']['registration_status'] == 'incomplete'
    
    # Admin assigns a boat
    admin_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/admin/teams/{test_team_manager_id}/boats/{boat_id}',
        path_parameters={
            'team_manager_id': test_team_manager_id,
            'boat_registration_id': boat_id
        },
        body=json.dumps({
            'assigned_boat_identifier': 'Racing Shell 42',
            'assigned_boat_comment': 'Stable boat for beginners'
        }),
        user_id=test_admin_id,
        groups=['admins']
    )
    
    admin_response = admin_handler(admin_event, mock_lambda_context)
    assert admin_response['statusCode'] == 200
    
    admin_body = json.loads(admin_response['body'])
    
    # Should now be complete (or 'free' if all RCPM members)
    assert admin_body['data']['registration_status'] in ['complete', 'free']
    assert admin_body['data']['boat_request_enabled'] is True
    assert admin_body['data']['assigned_boat_identifier'] == 'Racing Shell 42'


def test_completion_status_boat_request_disabled_ignores_assignment(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile, test_crew_members, test_races):
    """
    Test that crew with boat_request_enabled=false ignores assignment status
    
    **Validates: Requirements 4.2, 4.3 - Boat request disabled, assignment not required**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.update_boat_registration import lambda_handler as update_handler
    
    # Create a boat with boat request disabled (using own boat)
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'boat_request_enabled': False  # Using own boat
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Fill all seats and select a race
    update_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        body=json.dumps({
            'race_id': 'race-15',
            'seats': [
                {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},
                {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},
                {'position': 3, 'type': 'rower', 'crew_member_id': 'crew-3'},
                {'position': 4, 'type': 'rower', 'crew_member_id': 'crew-4'}
            ]
        }),
        user_id=test_team_manager_id
    )
    
    update_response = update_handler(update_event, mock_lambda_context)
    assert update_response['statusCode'] == 200
    
    update_body = json.loads(update_response['body'])
    
    # Should be complete (or 'free' if all RCPM) even without assigned_boat_identifier
    # because boat_request_enabled=false
    assert update_body['data']['registration_status'] in ['complete', 'free']
    assert update_body['data']['boat_request_enabled'] is False
    assert update_body['data'].get('assigned_boat_identifier') is None



# ============================================================================
# Task 3.2: Pricing Tests for Boat Request
# ============================================================================

def test_pricing_boat_request_disabled_own_boat(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile, test_crew_members, test_races):
    """
    Test pricing for crew with boat_request_enabled=false (using own boat) - participation fee only
    
    **Validates: Requirements 10.1, 10.2 - Own boat, no rental fee**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.update_boat_registration import lambda_handler as update_handler
    from functions.shared.pricing import calculate_boat_pricing
    
    # Create a boat with boat request disabled (using own boat)
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'boat_request_enabled': False  # Using own boat
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Fill all seats with external (non-RCPM) members
    # Create external crew members
    external_crew = [
        {
            'crew_member_id': 'ext-crew-1',
            'first_name': 'External',
            'last_name': 'Rower1',
            'date_of_birth': '1990-01-15',
            'gender': 'F',
            'license_number': 'EXT001',
            'club_affiliation': 'Club Elite'
        },
        {
            'crew_member_id': 'ext-crew-2',
            'first_name': 'External',
            'last_name': 'Rower2',
            'date_of_birth': '1985-05-20',
            'gender': 'M',
            'license_number': 'EXT002',
            'club_affiliation': 'Club Elite'
        },
        {
            'crew_member_id': 'ext-crew-3',
            'first_name': 'External',
            'last_name': 'Rower3',
            'date_of_birth': '1992-08-10',
            'gender': 'M',
            'license_number': 'EXT003',
            'club_affiliation': 'Club Elite'
        },
        {
            'crew_member_id': 'ext-crew-4',
            'first_name': 'External',
            'last_name': 'Rower4',
            'date_of_birth': '1988-12-05',
            'gender': 'F',
            'license_number': 'EXT004',
            'club_affiliation': 'Club Elite'
        }
    ]
    
    for cm in external_crew:
        dynamodb_table.put_item(Item={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'CREW#{cm["crew_member_id"]}',
            **cm
        })
    
    # Update boat with external crew
    update_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        body=json.dumps({
            'seats': [
                {'position': 1, 'type': 'rower', 'crew_member_id': 'ext-crew-1'},
                {'position': 2, 'type': 'rower', 'crew_member_id': 'ext-crew-2'},
                {'position': 3, 'type': 'rower', 'crew_member_id': 'ext-crew-3'},
                {'position': 4, 'type': 'rower', 'crew_member_id': 'ext-crew-4'}
            ]
        }),
        user_id=test_team_manager_id
    )
    
    update_response = update_handler(update_event, mock_lambda_context)
    assert update_response['statusCode'] == 200
    
    # Get boat from database
    boat_item = dynamodb_table.get_item(
        Key={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'BOAT#{boat_id}'
        }
    )
    boat = boat_item['Item']
    
    # Calculate pricing
    pricing = calculate_boat_pricing(boat, external_crew)
    
    # Should have participation fee (4 external seats × €20) but NO rental fee
    from decimal import Decimal
    assert pricing['base_price'] == Decimal('80.00')  # 4 × €20
    assert pricing['rental_fee'] == Decimal('0.00')  # No rental
    assert pricing['total'] == Decimal('80.00')


def test_pricing_boat_request_enabled_no_assignment_no_pricing(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile, test_crew_members, test_races):
    """
    Test pricing for crew with boat_request_enabled=true but no assignment - incomplete, no pricing calculated
    
    **Validates: Requirements 10.2, 10.3 - Incomplete registration, no pricing**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.update_boat_registration import lambda_handler as update_handler
    from functions.shared.pricing import calculate_boat_pricing
    
    # Create a boat with boat request enabled
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'boat_request_enabled': True,
            'boat_request_comment': 'Need a boat'
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Create external crew members
    external_crew = [
        {
            'crew_member_id': 'ext-crew-1',
            'first_name': 'External',
            'last_name': 'Rower1',
            'date_of_birth': '1990-01-15',
            'gender': 'F',
            'license_number': 'EXT001',
            'club_affiliation': 'Club Elite'
        },
        {
            'crew_member_id': 'ext-crew-2',
            'first_name': 'External',
            'last_name': 'Rower2',
            'date_of_birth': '1985-05-20',
            'gender': 'M',
            'license_number': 'EXT002',
            'club_affiliation': 'Club Elite'
        },
        {
            'crew_member_id': 'ext-crew-3',
            'first_name': 'External',
            'last_name': 'Rower3',
            'date_of_birth': '1992-08-10',
            'gender': 'M',
            'license_number': 'EXT003',
            'club_affiliation': 'Club Elite'
        },
        {
            'crew_member_id': 'ext-crew-4',
            'first_name': 'External',
            'last_name': 'Rower4',
            'date_of_birth': '1988-12-05',
            'gender': 'F',
            'license_number': 'EXT004',
            'club_affiliation': 'Club Elite'
        }
    ]
    
    for cm in external_crew:
        dynamodb_table.put_item(Item={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'CREW#{cm["crew_member_id"]}',
            **cm
        })
    
    # Update boat with external crew
    update_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        body=json.dumps({
            'seats': [
                {'position': 1, 'type': 'rower', 'crew_member_id': 'ext-crew-1'},
                {'position': 2, 'type': 'rower', 'crew_member_id': 'ext-crew-2'},
                {'position': 3, 'type': 'rower', 'crew_member_id': 'ext-crew-3'},
                {'position': 4, 'type': 'rower', 'crew_member_id': 'ext-crew-4'}
            ]
        }),
        user_id=test_team_manager_id
    )
    
    update_response = update_handler(update_event, mock_lambda_context)
    assert update_response['statusCode'] == 200
    
    # Get boat from database
    boat_item = dynamodb_table.get_item(
        Key={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'BOAT#{boat_id}'
        }
    )
    boat = boat_item['Item']
    
    # Calculate pricing
    pricing = calculate_boat_pricing(boat, external_crew)
    
    # Should have participation fee but NO rental fee (boat not assigned yet)
    from decimal import Decimal
    assert pricing['base_price'] == Decimal('80.00')  # 4 × €20
    assert pricing['rental_fee'] == Decimal('0.00')  # No rental (not assigned)
    assert pricing['total'] == Decimal('80.00')


def test_pricing_boat_request_enabled_with_assignment_includes_rental(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile, test_crew_members, test_races):
    """
    Test pricing for crew with boat_request_enabled=true and boat assigned - participation + rental
    
    **Validates: Requirements 10.3, 10.4 - RCPM boat assigned, includes rental fee**
    """
    from functions.shared.pricing import calculate_boat_pricing
    
    # Create external crew members
    external_crew = [
        {
            'crew_member_id': 'ext-crew-1',
            'first_name': 'External',
            'last_name': 'Rower1',
            'date_of_birth': '1990-01-15',
            'gender': 'F',
            'license_number': 'EXT001',
            'club_affiliation': 'Club Elite'
        },
        {
            'crew_member_id': 'ext-crew-2',
            'first_name': 'External',
            'last_name': 'Rower2',
            'date_of_birth': '1985-05-20',
            'gender': 'M',
            'license_number': 'EXT002',
            'club_affiliation': 'Club Elite'
        },
        {
            'crew_member_id': 'ext-crew-3',
            'first_name': 'External',
            'last_name': 'Rower3',
            'date_of_birth': '1992-08-10',
            'gender': 'M',
            'license_number': 'EXT003',
            'club_affiliation': 'Club Elite'
        },
        {
            'crew_member_id': 'ext-crew-4',
            'first_name': 'External',
            'last_name': 'Rower4',
            'date_of_birth': '1988-12-05',
            'gender': 'F',
            'license_number': 'EXT004',
            'club_affiliation': 'Club Elite'
        }
    ]
    
    for cm in external_crew:
        dynamodb_table.put_item(Item={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'CREW#{cm["crew_member_id"]}',
            **cm
        })
    
    # Create a boat with boat request enabled AND assigned
    boat_id = 'boat-pricing-rental-test'
    boat = {
        'boat_registration_id': boat_id,
        'event_type': '21km',
        'boat_type': '4-',
        'boat_request_enabled': True,
        'boat_request_comment': 'Need a boat',
        'assigned_boat_identifier': 'Racing Shell 42',  # Boat assigned!
        'assigned_boat_comment': 'Stable boat',
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': 'ext-crew-1'},
            {'position': 2, 'type': 'rower', 'crew_member_id': 'ext-crew-2'},
            {'position': 3, 'type': 'rower', 'crew_member_id': 'ext-crew-3'},
            {'position': 4, 'type': 'rower', 'crew_member_id': 'ext-crew-4'}
        ]
    }
    
    # Calculate pricing
    pricing = calculate_boat_pricing(boat, external_crew)
    
    # Should have BOTH participation fee AND rental fee
    from decimal import Decimal
    assert pricing['base_price'] == Decimal('80.00')  # 4 × €20 participation
    assert pricing['rental_fee'] == Decimal('80.00')  # 4 × €20 rental
    assert pricing['total'] == Decimal('160.00')  # Total


def test_pricing_rcpm_members_pay_zero(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile, test_crew_members, test_races):
    """
    Test that RCPM members pay €0 for both Participation Fee and Boat Rental
    
    **Validates: Requirements 10.4, 10.8 - RCPM members pay nothing**
    """
    from functions.shared.pricing import calculate_boat_pricing
    
    # Create a boat with boat request enabled AND assigned, all RCPM crew
    boat_id = 'boat-pricing-rcpm-test'
    boat = {
        'boat_registration_id': boat_id,
        'event_type': '21km',
        'boat_type': '4-',
        'boat_request_enabled': True,
        'boat_request_comment': 'Need a boat',
        'assigned_boat_identifier': 'Racing Shell 42',  # Boat assigned!
        'seats': [
            {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},  # RCPM
            {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},  # RCPM
            {'position': 3, 'type': 'rower', 'crew_member_id': 'crew-3'},  # RCPM
            {'position': 4, 'type': 'rower', 'crew_member_id': 'crew-4'}   # RCPM
        ]
    }
    
    # Calculate pricing with RCPM crew members
    pricing = calculate_boat_pricing(boat, test_crew_members)
    
    # RCPM members pay €0 for both fees
    from decimal import Decimal
    assert pricing['base_price'] == Decimal('0.00')  # No participation fee
    assert pricing['rental_fee'] == Decimal('0.00')  # No rental fee
    assert pricing['total'] == Decimal('0.00')  # Total is zero



# ============================================================================
# Task 4.3: Boat Request Field Tests
# ============================================================================

def test_disable_boat_request_clears_related_fields(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile):
    """
    Test that disabling boat_request clears boat_request_comment
    
    **Validates: Requirements 1.4, 2.3, 2.4**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.update_boat_registration import lambda_handler as update_handler
    
    # Create boat with boat request enabled and comment
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '42km',
            'boat_type': 'skiff',
            'boat_request_enabled': True,
            'boat_request_comment': 'Need a lightweight boat'
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Verify boat request fields are set
    assert create_body['data']['boat_request_enabled'] is True
    assert create_body['data']['boat_request_comment'] == 'Need a lightweight boat'
    
    # Update boat to disable boat request
    update_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        body=json.dumps({
            'boat_request_enabled': False
        }),
        user_id=test_team_manager_id
    )
    
    update_response = update_handler(update_event, mock_lambda_context)
    assert update_response['statusCode'] == 200
    
    update_body = json.loads(update_response['body'])
    
    # Verify boat_request_comment was cleared
    assert update_body['data']['boat_request_enabled'] is False
    assert update_body['data']['boat_request_comment'] is None


def test_boat_request_enabled_round_trip(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile):
    """
    Test round-trip persistence of boat_request_enabled
    
    **Validates: Requirements 1.4, 1.5, 5.4**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.list_boat_registrations import lambda_handler as list_handler
    
    # Create boat with boat_request_enabled=true
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '8+',
            'boat_request_enabled': True
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Verify field is set
    assert create_body['data']['boat_request_enabled'] is True
    
    # Retrieve boat via list endpoint
    list_event = mock_api_gateway_event(
        http_method='GET',
        path='/boat',
        user_id=test_team_manager_id
    )
    
    list_response = list_handler(list_event, mock_lambda_context)
    assert list_response['statusCode'] == 200
    
    list_body = json.loads(list_response['body'])
    boats = list_body['data']['boat_registrations']
    
    # Find our boat
    boat = next((b for b in boats if b['boat_registration_id'] == boat_id), None)
    assert boat is not None
    
    # Verify field persisted
    assert boat['boat_request_enabled'] is True


def test_boat_request_comment_round_trip(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile):
    """
    Test round-trip persistence of boat_request_comment
    
    **Validates: Requirements 1.4, 1.6, 2.6, 5.4**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.list_boat_registrations import lambda_handler as list_handler
    
    comment = 'We need a stable boat suitable for mixed crew. Prefer newer models.'
    
    # Create boat with boat request comment
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4+',
            'boat_request_enabled': True,
            'boat_request_comment': comment
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Verify comment is set
    assert create_body['data']['boat_request_comment'] == comment
    
    # Retrieve boat via list endpoint
    list_event = mock_api_gateway_event(
        http_method='GET',
        path='/boat',
        user_id=test_team_manager_id
    )
    
    list_response = list_handler(list_event, mock_lambda_context)
    assert list_response['statusCode'] == 200
    
    list_body = json.loads(list_response['body'])
    boats = list_body['data']['boat_registrations']
    
    # Find our boat
    boat = next((b for b in boats if b['boat_registration_id'] == boat_id), None)
    assert boat is not None
    
    # Verify comment persisted
    assert boat['boat_request_comment'] == comment


def test_team_manager_cannot_modify_assigned_boat_identifier(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile):
    """
    Test that team managers cannot modify assigned_boat_identifier
    
    **Validates: Requirements 3.4, 8.1**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.update_boat_registration import lambda_handler as update_handler
    
    # Create boat
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'boat_request_enabled': True
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Verify assigned_boat_identifier is null (only admins can set)
    assert create_body['data']['assigned_boat_identifier'] is None
    
    # Try to update assigned_boat_identifier as team manager
    update_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        body=json.dumps({
            'assigned_boat_identifier': 'Hacker Boat 123'
        }),
        user_id=test_team_manager_id
    )
    
    update_response = update_handler(update_event, mock_lambda_context)
    
    # Should be forbidden
    assert update_response['statusCode'] == 403
    
    update_body = json.loads(update_response['body'])
    assert update_body['success'] is False
    assert 'administrator' in update_body['error']['message'].lower()


def test_team_manager_cannot_modify_assigned_boat_comment(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile):
    """
    Test that team managers cannot modify assigned_boat_comment
    
    **Validates: Requirements 3.4, 8.2**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.update_boat_registration import lambda_handler as update_handler
    
    # Create boat
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '42km',
            'boat_type': 'skiff',
            'boat_request_enabled': True
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Verify assigned_boat_comment is null (only admins can set)
    assert create_body['data']['assigned_boat_comment'] is None
    
    # Try to update assigned_boat_comment as team manager
    update_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        body=json.dumps({
            'assigned_boat_comment': 'This is my comment'
        }),
        user_id=test_team_manager_id
    )
    
    update_response = update_handler(update_event, mock_lambda_context)
    
    # Should be forbidden
    assert update_response['statusCode'] == 403
    
    update_body = json.loads(update_response['body'])
    assert update_body['success'] is False
    assert 'administrator' in update_body['error']['message'].lower()



# ============================================================================
# Payment Prevention Tests
# ============================================================================

def test_payment_blocked_when_boat_request_enabled_no_assignment(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile, test_crew_members, test_races):
    """
    Test that payment is blocked when boat_request_enabled=true and no assignment
    
    **Validates: Requirements 4.6, 10.2, 10.7**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.update_boat_registration import lambda_handler as update_handler
    from payment.create_payment_intent import validate_boat_registrations
    
    # Create boat with boat request enabled
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'boat_request_enabled': True,
            'boat_request_comment': 'Need a boat for beginners',
            'seats': [
                {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},
                {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},
                {'position': 3, 'type': 'rower', 'crew_member_id': 'crew-3'},
                {'position': 4, 'type': 'rower', 'crew_member_id': 'crew-4'}
            ]
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Verify boat request is enabled but no assignment
    assert create_body['data']['boat_request_enabled'] is True
    assert create_body['data']['assigned_boat_identifier'] is None
    
    # Select a race to make crew otherwise complete
    race_id = test_races[0]['race_id']
    update_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        body=json.dumps({
            'race_id': race_id
        }),
        user_id=test_team_manager_id
    )
    
    update_response = update_handler(update_event, mock_lambda_context)
    assert update_response['statusCode'] == 200
    
    update_body = json.loads(update_response['body'])
    # Status should be incomplete due to pending boat request
    assert update_body['data']['registration_status'] == 'incomplete'
    
    # Test validation function directly (without calling Stripe)
    from database import get_db_client
    db = get_db_client()
    
    boats, error = validate_boat_registrations([boat_id], test_team_manager_id, db)
    
    # Validation should fail with pending boat request error
    assert boats is None
    assert error is not None
    assert 'pending boat assignment request' in error.lower()


def test_payment_allowed_when_boat_request_enabled_with_assignment(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile, test_crew_members, test_races, test_admin_id):
    """
    Test that payment is allowed when boat_request_enabled=true and boat is assigned
    
    **Validates: Requirements 4.6**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.update_boat_registration import lambda_handler as update_handler
    from admin.admin_update_boat import lambda_handler as admin_update_handler
    from payment.create_payment_intent import validate_boat_registrations
    
    # Create boat with boat request enabled
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'boat_request_enabled': True,
            'boat_request_comment': 'Need a boat for beginners',
            'seats': [
                {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},
                {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},
                {'position': 3, 'type': 'rower', 'crew_member_id': 'crew-3'},
                {'position': 4, 'type': 'rower', 'crew_member_id': 'crew-4'}
            ]
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Select a race
    race_id = test_races[0]['race_id']
    update_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        body=json.dumps({
            'race_id': race_id
        }),
        user_id=test_team_manager_id
    )
    
    update_response = update_handler(update_event, mock_lambda_context)
    assert update_response['statusCode'] == 200
    
    # Admin assigns boat
    admin_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/admin/boat/{test_team_manager_id}/{boat_id}',
        path_parameters={
            'team_manager_id': test_team_manager_id,
            'boat_registration_id': boat_id
        },
        body=json.dumps({
            'assigned_boat_identifier': 'Boat 42',
            'assigned_boat_comment': 'Hull in rack 3'
        }),
        user_id=test_admin_id,
        groups=['admins']
    )
    
    admin_response = admin_update_handler(admin_event, mock_lambda_context)
    assert admin_response['statusCode'] == 200
    
    admin_body = json.loads(admin_response['body'])
    # Status should now be complete
    assert admin_body['data']['registration_status'] == 'complete'
    assert admin_body['data']['assigned_boat_identifier'] == 'Boat 42'
    
    # Test validation function directly (without calling Stripe)
    from database import get_db_client
    db = get_db_client()
    
    boats, error = validate_boat_registrations([boat_id], test_team_manager_id, db)
    
    # Validation should pass
    assert boats is not None
    assert error is None
    assert len(boats) == 1
    assert boats[0]['assigned_boat_identifier'] == 'Boat 42'


def test_payment_allowed_when_boat_request_disabled(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_team_manager_profile, test_crew_members, test_races):
    """
    Test that payment is allowed when boat_request_enabled=false (using own boat)
    
    **Validates: Requirements 4.6**
    """
    from boat.create_boat_registration import lambda_handler as create_handler
    from boat.update_boat_registration import lambda_handler as update_handler
    from payment.create_payment_intent import validate_boat_registrations
    
    # Create boat with boat request disabled (using own boat)
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'boat_request_enabled': False,
            'seats': [
                {'position': 1, 'type': 'rower', 'crew_member_id': 'crew-1'},
                {'position': 2, 'type': 'rower', 'crew_member_id': 'crew-2'},
                {'position': 3, 'type': 'rower', 'crew_member_id': 'crew-3'},
                {'position': 4, 'type': 'rower', 'crew_member_id': 'crew-4'}
            ]
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Verify boat request is disabled
    assert create_body['data']['boat_request_enabled'] is False
    
    # Select a race to make crew complete
    race_id = test_races[0]['race_id']
    update_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boat/{boat_id}',
        path_parameters={'boat_registration_id': boat_id},
        body=json.dumps({
            'race_id': race_id
        }),
        user_id=test_team_manager_id
    )
    
    update_response = update_handler(update_event, mock_lambda_context)
    assert update_response['statusCode'] == 200
    
    update_body = json.loads(update_response['body'])
    # Status should be complete (boat request disabled, so no boat assignment needed)
    assert update_body['data']['registration_status'] == 'complete'
    
    # Test validation function directly (without calling Stripe)
    from database import get_db_client
    db = get_db_client()
    
    boats, error = validate_boat_registrations([boat_id], test_team_manager_id, db)
    
    # Validation should pass
    assert boats is not None
    assert error is None
    assert len(boats) == 1
    assert boats[0]['boat_request_enabled'] is False



def test_xss_sanitization_boat_request_comment(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_crew_members):
    """
    Test XSS sanitization for boat_request_comment
    Validates: Requirements 9.6, 9.7
    """
    from functions.boat.create_boat_registration import lambda_handler as create_handler
    
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': 'Test Club'
    })
    
    # Test with XSS attack in boat_request_comment
    xss_comment = 'Need beginner boat <script>alert("XSS")</script> with stable hull'
    
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',  # Changed from 'skiff' which is only valid for 42km
            'boat_request_enabled': True,
            'boat_request_comment': xss_comment
        }),
        user_id=test_team_manager_id
    )
    
    response = create_handler(create_event, mock_lambda_context)
    if response['statusCode'] != 201:
        print(f"ERROR Response: {json.dumps(json.loads(response['body']), indent=2)}")
    assert response['statusCode'] == 201
    
    body = json.loads(response['body'])
    sanitized_comment = body['data']['boat_request_comment']
    
    # Script tags should be removed
    assert '<script>' not in sanitized_comment
    assert '</script>' not in sanitized_comment
    assert 'alert' not in sanitized_comment
    
    # Safe content should be preserved
    assert 'Need beginner boat' in sanitized_comment
    assert 'with stable hull' in sanitized_comment


def test_xss_sanitization_preserves_special_chars(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_crew_members):
    """
    Test that XSS sanitization preserves non-dangerous special characters
    Validates: Requirements 9.6, 9.7
    """
    from functions.boat.create_boat_registration import lambda_handler as create_handler
    
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': 'Test Club'
    })
    
    # Test with special characters that should be preserved
    comment_with_special_chars = 'Boat #42, weight: 70-80kg, "Elite" level, 50% discount'
    
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'boat_request_enabled': True,
            'boat_request_comment': comment_with_special_chars
        }),
        user_id=test_team_manager_id
    )
    
    response = create_handler(create_event, mock_lambda_context)
    assert response['statusCode'] == 201
    
    body = json.loads(response['body'])
    sanitized_comment = body['data']['boat_request_comment']
    
    # Special characters should be preserved
    assert '#42' in sanitized_comment
    assert '70-80kg' in sanitized_comment
    assert '"Elite"' in sanitized_comment or 'Elite' in sanitized_comment
    assert '50%' in sanitized_comment


def test_xss_sanitization_preserves_newlines(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_crew_members):
    """
    Test that XSS sanitization preserves newlines in comments
    Validates: Requirements 2.6, 9.6, 9.7
    """
    from functions.boat.create_boat_registration import lambda_handler as create_handler
    
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': 'Test Club'
    })
    
    # Test with newlines
    comment_with_newlines = 'Requirements:\n- Beginner level\n- Stable hull\n- Weight: 70-80kg'
    
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'boat_request_enabled': True,
            'boat_request_comment': comment_with_newlines
        }),
        user_id=test_team_manager_id
    )
    
    response = create_handler(create_event, mock_lambda_context)
    assert response['statusCode'] == 201
    
    body = json.loads(response['body'])
    sanitized_comment = body['data']['boat_request_comment']
    
    # Newlines should be preserved
    assert '\n' in sanitized_comment
    assert 'Requirements:' in sanitized_comment
    assert 'Beginner level' in sanitized_comment
    assert 'Stable hull' in sanitized_comment


def test_xss_sanitization_admin_assigned_boat_comment(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_crew_members):
    """
    Test XSS sanitization for assigned_boat_comment (admin field)
    Validates: Requirements 9.6, 9.7
    """
    from functions.boat.create_boat_registration import lambda_handler as create_handler
    from functions.admin.admin_update_boat import lambda_handler as admin_update_handler
    
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': 'Test Club'
    })
    
    # Create boat with boat request enabled
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'boat_request_enabled': True,
            'boat_request_comment': 'Need beginner boat'
        }),
        user_id=test_team_manager_id
    )
    
    create_response = create_handler(create_event, mock_lambda_context)
    assert create_response['statusCode'] == 201
    
    create_body = json.loads(create_response['body'])
    boat_id = create_body['data']['boat_registration_id']
    
    # Admin assigns boat with XSS in comment
    xss_comment = 'Hull in rack 3 <img src=x onerror="alert(1)"> oars in locker B'
    
    admin_event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/admin/boat/{test_team_manager_id}/{boat_id}',
        path_parameters={
            'team_manager_id': test_team_manager_id,
            'boat_registration_id': boat_id
        },
        body=json.dumps({
            'assigned_boat_identifier': 'Boat 42',
            'assigned_boat_comment': xss_comment
        }),
        user_id='admin-user-id',
        groups=['admins']  # Changed from is_admin=True to groups=['admins']
    )
    
    admin_response = admin_update_handler(admin_event, mock_lambda_context)
    assert admin_response['statusCode'] == 200
    
    admin_body = json.loads(admin_response['body'])
    sanitized_comment = admin_body['data']['assigned_boat_comment']
    
    # XSS should be removed
    assert '<img' not in sanitized_comment
    assert 'onerror' not in sanitized_comment
    assert 'alert' not in sanitized_comment
    
    # Safe content should be preserved
    assert 'Hull in rack 3' in sanitized_comment
    assert 'oars in locker B' in sanitized_comment


def test_xss_sanitization_removes_javascript_protocol(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_crew_members):
    """
    Test that XSS sanitization removes javascript: protocol
    Validates: Requirements 9.6, 9.7
    """
    from functions.boat.create_boat_registration import lambda_handler as create_handler
    
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': 'Test Club'
    })
    
    # Test with javascript: protocol
    xss_comment = 'Click here: javascript:alert("XSS") for details'
    
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'boat_request_enabled': True,
            'boat_request_comment': xss_comment
        }),
        user_id=test_team_manager_id
    )
    
    response = create_handler(create_event, mock_lambda_context)
    assert response['statusCode'] == 201
    
    body = json.loads(response['body'])
    sanitized_comment = body['data']['boat_request_comment']
    
    # javascript: protocol should be removed
    assert 'javascript:' not in sanitized_comment.lower()
    # The word 'alert' by itself is not dangerous, only the javascript: protocol is removed
    # Safe content should be preserved
    assert 'Click here:' in sanitized_comment
    assert 'for details' in sanitized_comment


def test_xss_sanitization_removes_style_tags(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_crew_members):
    """
    Test that XSS sanitization removes <style> tags
    Validates: Requirements 9.6, 9.7
    """
    from functions.boat.create_boat_registration import lambda_handler as create_handler
    
    # Add team manager
    dynamodb_table.put_item(Item={
        'PK': f'USER#{test_team_manager_id}',
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Manager',
        'club_affiliation': 'Test Club'
    })
    
    # Test with style tags
    xss_comment = 'Need boat <style>body{display:none}</style> for race'
    
    create_event = mock_api_gateway_event(
        http_method='POST',
        path='/boat',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4-',
            'boat_request_enabled': True,
            'boat_request_comment': xss_comment
        }),
        user_id=test_team_manager_id
    )
    
    response = create_handler(create_event, mock_lambda_context)
    assert response['statusCode'] == 201
    
    body = json.loads(response['body'])
    sanitized_comment = body['data']['boat_request_comment']
    
    # Style tags should be removed
    assert '<style>' not in sanitized_comment
    assert '</style>' not in sanitized_comment
    assert 'display:none' not in sanitized_comment
    
    # Safe content should be preserved
    assert 'Need boat' in sanitized_comment
    assert 'for race' in sanitized_comment
