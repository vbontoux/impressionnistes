"""
Integration tests for crew member API endpoints
Tests Lambda handlers with mock DynamoDB (no authentication)
"""
import json
import pytest


def test_create_crew_member(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test creating a crew member"""
    # Import Lambda handler
    from crew.create_crew_member import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='POST',
        path='/crew',
        body=json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'license_number': 'ABC123',
            'club_affiliation': 'Test Club'
        }),
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 201
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'crew_member_id' in body['data']
    assert body['data']['first_name'] == 'John'
    assert body['data']['last_name'] == 'Doe'
    
    # Verify data was saved to DynamoDB
    crew_member_id = body['data']['crew_member_id']
    item = dynamodb_table.get_item(
        Key={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'CREW#{crew_member_id}'
        }
    )
    
    assert 'Item' in item
    assert item['Item']['first_name'] == 'John'
    assert item['Item']['license_number'] == 'ABC123'


def test_list_crew_members(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test listing crew members"""
    # Create a crew member
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-1',
        'crew_member_id': 'crew-1',
        'first_name': 'Alice',
        'last_name': 'Smith',
        'date_of_birth': '1985-05-15',
        'gender': 'F',
        'license_number': 'LIC001'
    })
    
    # Import Lambda handler
    from crew.list_crew_members import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='GET',
        path='/crew',
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'crew_members' in body['data']
    assert len(body['data']['crew_members']) >= 1
    
    # Check crew member is returned
    crew_member_ids = [cm['crew_member_id'] for cm in body['data']['crew_members']]
    assert 'crew-1' in crew_member_ids


def test_update_crew_member(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test updating a crew member"""
    # Create a crew member first
    crew_member_id = 'crew-update-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'CREW#{crew_member_id}',
        'crew_member_id': crew_member_id,
        'first_name': 'Charlie',
        'last_name': 'Brown',
        'date_of_birth': '1988-03-10',
        'gender': 'M',
        'license_number': 'LIC003',
        'club_affiliation': 'Test Club'
    })
    
    # Import Lambda handler
    from crew.update_crew_member import lambda_handler
    
    # Create API Gateway event to update
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/crew/{crew_member_id}',
        body=json.dumps({
            'first_name': 'Charles',  # Changed
            'last_name': 'Brown',
            'date_of_birth': '1988-03-10',
            'gender': 'M',
            'license_number': 'LIC003UPD',  # Changed (alphanumeric only)
            'club_affiliation': 'Test Club'
        }),
        path_parameters={'crew_member_id': crew_member_id},
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['first_name'] == 'Charles'
    assert body['data']['license_number'] == 'LIC003UPD'
    
    # Verify data was updated in DynamoDB
    item = dynamodb_table.get_item(
        Key={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'CREW#{crew_member_id}'
        }
    )
    
    assert item['Item']['first_name'] == 'Charles'
    assert item['Item']['license_number'] == 'LIC003UPD'


def test_delete_crew_member(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test deleting a crew member"""
    # Create a crew member first
    crew_member_id = 'crew-delete-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'CREW#{crew_member_id}',
        'crew_member_id': crew_member_id,
        'first_name': 'Delete',
        'last_name': 'Me',
        'date_of_birth': '1990-01-01',
        'gender': 'M',
        'license_number': 'LIC999'
    })
    
    # Import Lambda handler
    from crew.delete_crew_member import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='DELETE',
        path=f'/crew/{crew_member_id}',
        path_parameters={'crew_member_id': crew_member_id},
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
            'SK': f'CREW#{crew_member_id}'
        }
    )
    
    assert 'Item' not in item


def test_create_crew_member_validation_error(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test that validation errors are returned correctly"""
    from crew.create_crew_member import lambda_handler
    
    # Create event with missing required fields
    event = mock_api_gateway_event(
        http_method='POST',
        path='/crew',
        body=json.dumps({
            'first_name': 'John'
            # Missing required fields
        }),
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert validation error response
    assert response['statusCode'] == 400
    
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'error' in body or 'message' in body
