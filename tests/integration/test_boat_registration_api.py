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
