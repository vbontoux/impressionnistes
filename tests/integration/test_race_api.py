"""
Integration tests for race API endpoints
Tests Lambda handlers with mock DynamoDB
"""
import json
import pytest


def test_list_races(dynamodb_table, mock_api_gateway_event, mock_lambda_context):
    """Test listing available races"""
    # Seed some races
    races = [
        {
            'race_id': 'race-21km-4minus-sm-m',
            'event_type': '21km',
            'boat_type': '4-',
            'age_category': 'SM',
            'gender_category': 'M',
            'race_name': '21km 4- Senior Men',
            'start_time': '09:00'
        },
        {
            'race_id': 'race-21km-4minus-sm-f',
            'event_type': '21km',
            'boat_type': '4-',
            'age_category': 'SM',
            'gender_category': 'F',
            'race_name': '21km 4- Senior Women',
            'start_time': '09:15'
        },
        {
            'race_id': 'race-42km-2x-sm-mx',
            'event_type': '42km',
            'boat_type': '2x',
            'age_category': 'SM',
            'gender_category': 'MX',
            'race_name': '42km 2x Senior Mixed',
            'start_time': '10:00'
        }
    ]
    
    for race in races:
        dynamodb_table.put_item(Item={
            'PK': 'RACE',
            'SK': f'RACE#{race["race_id"]}',
            **race
        })
    
    from race.list_races import lambda_handler
    
    # Create API Gateway event (public endpoint)
    event = mock_api_gateway_event(
        http_method='GET',
        path='/races'
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'races' in body['data']
    assert len(body['data']['races']) >= 3
    
    # Check races are returned
    race_ids = [r['race_id'] for r in body['data']['races']]
    assert 'race-21km-4minus-sm-m' in race_ids
    assert 'race-21km-4minus-sm-f' in race_ids
    assert 'race-42km-2x-sm-mx' in race_ids


def test_list_races_filtered_by_event_type(dynamodb_table, mock_api_gateway_event, mock_lambda_context):
    """Test listing races filtered by event type"""
    # Seed races for different event types
    races = [
        {
            'race_id': 'race-21km-1',
            'event_type': '21km',
            'boat_type': '4-',
            'age_category': 'SM',
            'gender_category': 'M',
            'race_name': '21km Race'
        },
        {
            'race_id': 'race-42km-1',
            'event_type': '42km',
            'boat_type': '2x',
            'age_category': 'SM',
            'gender_category': 'MX',
            'race_name': '42km Race'
        }
    ]
    
    for race in races:
        dynamodb_table.put_item(Item={
            'PK': 'RACE',
            'SK': f'RACE#{race["race_id"]}',
            **race
        })
    
    from race.list_races import lambda_handler
    
    # Create API Gateway event with event_type filter
    event = mock_api_gateway_event(
        http_method='GET',
        path='/races',
        query_parameters={'event_type': '21km'}
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'races' in body['data']
    
    # All returned races should be 21km
    for race in body['data']['races']:
        assert race['event_type'] == '21km'
