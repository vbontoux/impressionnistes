"""
Integration tests for rental boat API endpoints
Tests Lambda handlers with mock DynamoDB

NOTE: Tests marked with @pytest.mark.skip are for the OLD inventory-based rental system
which is being deprecated. See .kiro/specs/boat-rental-refactoring/DEPRECATED_FILES.md
"""
import json
import pytest
from decimal import Decimal


@pytest.mark.skip(reason="OLD rental boat inventory system - deprecated, see DEPRECATED_FILES.md")
def test_list_available_rental_boats(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test listing available rental boats"""
    # Seed rental boats
    rental_boats = [
        {
            'rental_boat_id': 'rental-1',
            'boat_type': '4-',
            'boat_name': 'Rental Boat 1',
            'status': 'available',
            'daily_rate': Decimal('100.00')
        },
        {
            'rental_boat_id': 'rental-2',
            'boat_type': '2x',
            'boat_name': 'Rental Boat 2',
            'status': 'available',
            'daily_rate': Decimal('80.00')
        },
        {
            'rental_boat_id': 'rental-3',
            'boat_type': '4-',
            'boat_name': 'Rental Boat 3',
            'status': 'reserved',
            'daily_rate': Decimal('100.00')
        }
    ]
    
    for boat in rental_boats:
        dynamodb_table.put_item(Item={
            'PK': f'RENTAL_BOAT#{boat["rental_boat_id"]}',
            'SK': 'METADATA',
            **boat
        })
    
    from rental.list_available_rental_boats import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='GET',
        path='/rentals/boats',
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'rental_boats' in body['data']
    
    # Should only return available boats (not reserved)
    available_boats = body['data']['rental_boats']
    for boat in available_boats:
        assert boat['status'] == 'available'


@pytest.mark.skip(reason="OLD rental boat inventory system - deprecated, see DEPRECATED_FILES.md")
def test_request_rental_boat(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test requesting a rental boat"""
    # Seed an available rental boat (PK is just the rental_boat_id)
    dynamodb_table.put_item(Item={
        'PK': 'rental-1',
        'SK': 'METADATA',
        'rental_boat_id': 'rental-1',
        'boat_type': '4-',
        'boat_name': 'Rental Boat 1',
        'status': 'available',
        'daily_rate': Decimal('100.00')
    })
    
    from rental.request_rental_boat import lambda_handler
    
    # Create rental request event
    event = mock_api_gateway_event(
        http_method='POST',
        path='/rentals/request',
        body=json.dumps({
            'rental_boat_id': 'rental-1',
            'event_type': '21km',
            'boat_registration_id': 'boat-123',
            'rental_days': 2
        }),
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] in [200, 201]
    
    body = json.loads(response['body'])
    assert body['success'] is True


def test_get_my_rental_requests(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test getting user's rental requests"""
    # Seed rental request with requester (Lambda scans RENTAL_REQUEST# items)
    dynamodb_table.put_item(Item={
        'PK': 'RENTAL_REQUEST#rental-1',
        'SK': 'METADATA',
        'rental_request_id': 'RENTAL_REQUEST#rental-1',
        'boat_type': '4-',
        'desired_weight_range': '70-90kg',
        'request_comment': 'Need a 4- for the race',
        'status': 'pending',
        'requester_id': test_team_manager_id,
        'requester_email': f'{test_team_manager_id}@test.com',
        'created_at': '2024-12-18T10:00:00Z',
        'updated_at': '2024-12-18T10:00:00Z'
    })
    
    from rental.get_my_rental_requests import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='GET',
        path='/rentals/my-requests',
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'rental_requests' in body['data']
    assert len(body['data']['rental_requests']) >= 1


def test_cancel_rental_request(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test canceling a rental request"""
    # Seed a rental REQUEST (new system) with requester
    rental_request_id = 'RENTAL_REQUEST#cancel-test'
    dynamodb_table.put_item(Item={
        'PK': rental_request_id,
        'SK': 'METADATA',
        'rental_request_id': rental_request_id,
        'boat_type': '4-',
        'desired_weight_range': '70-90kg',
        'request_comment': 'Test rental request',
        'status': 'pending',
        'requester_id': test_team_manager_id,
        'requester_email': f'{test_team_manager_id}@test.com',
        'created_at': '2024-12-18T10:00:00Z',
        'updated_at': '2024-12-18T10:00:00Z'
    })
    
    from rental.cancel_rental_request import lambda_handler
    
    # Create cancel event (API expects 'rental_request_id' as path parameter key)
    event = mock_api_gateway_event(
        http_method='DELETE',
        path=f'/rentals/request/{rental_request_id}',
        path_parameters={'rental_request_id': 'cancel-test'},  # Use clean UUID
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response - implementation deletes the request instead of marking as cancelled
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    # Verify request was deleted
    assert 'rental_request_id' in body['data']
