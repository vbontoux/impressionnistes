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
    
    # Should show Multi-Club
    assert body['data']['boat_club_display'] == 'RCPM (Multi-Club)'
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
    
    # Should show Multi-Club
    assert body['data']['boat_club_display'] == 'RCPM (Multi-Club)'
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
