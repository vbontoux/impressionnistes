"""
Integration tests for rental boat API endpoints
Tests Lambda handlers with mock DynamoDB
"""
import json
import pytest
from decimal import Decimal


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
    # Seed rental boat with requester (Lambda scans RENTAL_BOAT# items)
    dynamodb_table.put_item(Item={
        'PK': 'RENTAL_BOAT#rental-1',
        'SK': 'METADATA',
        'rental_boat_id': 'rental-1',
        'boat_type': '4-',
        'boat_name': 'Rental Boat 1',
        'status': 'requested',
        'requester': f'{test_team_manager_id}@test.com',  # Matches mock email
        'requested_at': '2024-12-18T10:00:00Z'
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
    # Seed a rental boat with requester (PK is just rental_boat_id)
    rental_boat_id = 'rental-cancel-test'
    dynamodb_table.put_item(Item={
        'PK': rental_boat_id,
        'SK': 'METADATA',
        'rental_boat_id': rental_boat_id,
        'boat_type': '4-',
        'boat_name': 'Rental Boat Cancel Test',
        'status': 'requested',
        'requester': f'{test_team_manager_id}@test.com',  # Matches mock email
        'requested_at': '2024-12-18T10:00:00Z'
    })
    
    from rental.cancel_rental_request import lambda_handler
    
    # Create cancel event
    event = mock_api_gateway_event(
        http_method='DELETE',
        path=f'/rentals/request/{rental_boat_id}',
        path_parameters={'rental_boat_id': rental_boat_id},
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
