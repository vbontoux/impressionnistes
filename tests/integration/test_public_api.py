"""
Integration tests for public API endpoints (no authentication required)
"""
import json
import pytest


def test_get_public_event_info(dynamodb_table, mock_api_gateway_event, mock_lambda_context):
    """Test getting public event information"""
    from health.get_public_event_info import lambda_handler
    
    # Create API Gateway event (no user_id - public endpoint)
    event = mock_api_gateway_event(
        http_method='GET',
        path='/public/event-info'
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'event_date' in body['data']
    assert 'registration_start_date' in body['data']
    assert 'registration_end_date' in body['data']
    assert 'payment_deadline' in body['data']
    
    # Verify dates match configuration
    assert body['data']['event_date'] == '2025-05-01'
    assert body['data']['registration_start_date'] == '2025-03-19'
    assert body['data']['registration_end_date'] == '2025-04-19'
    assert body['data']['payment_deadline'] == '2025-04-25'


def test_list_clubs_public(dynamodb_table, mock_api_gateway_event, mock_lambda_context):
    """Test listing clubs (public endpoint)"""
    # Seed some clubs
    clubs = [
        {'club_id': 'rcpm', 'name': 'RCPM', 'url': 'https://rcpm.example.com'},
        {'club_id': 'club-a', 'name': 'Club A', 'url': 'https://cluba.example.com'},
        {'club_id': 'club-b', 'name': 'Club B', 'url': 'https://clubb.example.com'}
    ]
    for club in clubs:
        dynamodb_table.put_item(Item={
            'PK': 'CLUB',
            'SK': f'CLUB#{club["club_id"]}',
            'club_id': club['club_id'],
            'name': club['name'],
            'url': club['url']
        })
    
    from club.list_clubs import lambda_handler
    
    # Create API Gateway event (no user_id - public endpoint)
    event = mock_api_gateway_event(
        http_method='GET',
        path='/clubs'
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'clubs' in body['data']
    assert len(body['data']['clubs']) >= 3
    
    club_names = [c['name'] for c in body['data']['clubs']]
    assert 'RCPM' in club_names
    assert 'Club A' in club_names
    assert 'Club B' in club_names
