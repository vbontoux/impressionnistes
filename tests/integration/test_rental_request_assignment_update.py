"""
Integration tests for rental request assignment details update
Tests Property 15 from the boat-rental-refactoring design
"""
import pytest
import sys
import os
import json
from datetime import datetime

# Add functions paths to system path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/admin'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/rental'))

# Set environment variables before importing Lambda functions
os.environ['TABLE_NAME'] = 'test-impressionnistes-table'
os.environ['AWS_DEFAULT_REGION'] = 'eu-west-3'

from update_assignment_details import lambda_handler as update_handler
from accept_rental_request import lambda_handler as accept_handler
from create_rental_request import lambda_handler as create_handler


@pytest.fixture
def admin_event_factory():
    """Factory to create admin events with custom rental_request_id and body"""
    def _create_event(rental_request_id, assignment_details, admin_id='admin-user-123'):
        return {
            'pathParameters': {
                'id': rental_request_id
            },
            'body': json.dumps({
                'assignment_details': assignment_details
            }),
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'sub': admin_id,
                        'email': f'{admin_id}@example.com',
                        'cognito:groups': 'admins'
                    }
                }
            }
        }
    return _create_event


@pytest.fixture
def context():
    """Create a mock Lambda context"""
    class MockContext:
        function_name = 'update_assignment_details'
        memory_limit_in_mb = 128
        invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:update_assignment_details'
        aws_request_id = 'test-request-id'
    
    return MockContext()


def create_accepted_request(dynamodb_table, context, boat_type='skiff'):
    """Helper function to create an accepted rental request"""
    # First create a pending request
    create_event = {
        'body': json.dumps({
            'boat_type': boat_type,
            'desired_weight_range': '70-90kg',
            'request_comment': 'Need a boat for testing'
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'test-user-123',
                    'email': 'teammanager@example.com',
                    'cognito:groups': 'team_managers'
                }
            }
        }
    }
    
    response = create_handler(create_event, context)
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    rental_request_id = body['data']['rental_request_id']
    
    # Accept the request
    accept_event = {
        'pathParameters': {'id': rental_request_id},
        'body': json.dumps({
            'assignment_details': 'Initial assignment: Boat #1'
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'admin-123',
                    'email': 'admin@example.com',
                    'cognito:groups': 'admins'
                }
            }
        }
    }
    
    response = accept_handler(accept_event, context)
    assert response['statusCode'] == 200
    
    return rental_request_id


# Feature: boat-rental-refactoring, Property 15: Assignment Details Update Preserves Status
# For any rental request with status "accepted", updating assignment_details should preserve
# the status as "accepted".


@pytest.mark.parametrize("initial_details,updated_details", [
    ('Boat #1, dock A', 'Boat #2, dock B'),
    ('Initial assignment', 'Updated assignment with more details'),
    ('Short', 'A' * 1000),  # Max length
    ('Boat: 001\nOars: Yes', 'Boat: 002\nOars: No\nLocation: Changed'),
])
def test_property_15_assignment_update_preserves_status(
    dynamodb_table, context, admin_event_factory, initial_details, updated_details
):
    """
    Property 15: Assignment Details Update Preserves Status
    Validates: Requirements 4.7
    
    Test that updating assignment details preserves the "accepted" status.
    """
    # Arrange - create an accepted request
    rental_request_id = create_accepted_request(dynamodb_table, context)
    
    # Verify initial state
    item = dynamodb_table.get_item(Key={'PK': rental_request_id, 'SK': 'METADATA'})
    assert item['Item']['status'] == 'accepted'
    initial_assignment = item['Item']['assignment_details']
    
    # Create admin event to update assignment details
    event = admin_event_factory(rental_request_id, updated_details)
    
    # Act
    response = update_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    # Verify status is still "accepted"
    assert body['data']['status'] == 'accepted', "Status must remain 'accepted' after update"
    
    # Verify assignment_details was updated
    assert body['data']['assignment_details'] == updated_details.strip()
    assert body['data']['assignment_details'] != initial_assignment
    
    # Verify updated_at and updated_by are present
    assert 'updated_at' in body['data']
    assert 'updated_by' in body['data']
    
    # Verify in database
    item = dynamodb_table.get_item(Key={'PK': rental_request_id, 'SK': 'METADATA'})
    db_item = item['Item']
    assert db_item['status'] == 'accepted', "Status must remain 'accepted' in database"
    assert db_item['assignment_details'] == updated_details.strip()
    assert 'updated_at' in db_item
    assert 'updated_by' in db_item


@pytest.mark.parametrize("admin_id", [
    'admin-123',
    'admin-456',
    'superadmin-789',
])
def test_assignment_update_records_admin(
    dynamodb_table, context, admin_event_factory, admin_id
):
    """
    Test that updating assignment details records which admin made the update
    """
    # Arrange
    rental_request_id = create_accepted_request(dynamodb_table, context)
    event = admin_event_factory(rental_request_id, 'Updated by specific admin', admin_id)
    
    # Act
    response = update_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['data']['updated_by'] == admin_id
    
    # Verify in database
    item = dynamodb_table.get_item(Key={'PK': rental_request_id, 'SK': 'METADATA'})
    assert item['Item']['updated_by'] == admin_id


def test_assignment_update_multiple_times(dynamodb_table, context, admin_event_factory):
    """
    Test that assignment details can be updated multiple times
    """
    # Arrange
    rental_request_id = create_accepted_request(dynamodb_table, context)
    
    # Act - update multiple times
    updates = [
        'First update',
        'Second update',
        'Third update with more details'
    ]
    
    for update_text in updates:
        event = admin_event_factory(rental_request_id, update_text)
        response = update_handler(event, context)
        
        # Assert each update succeeds
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['data']['assignment_details'] == update_text
        assert body['data']['status'] == 'accepted'


@pytest.mark.parametrize("initial_status,setup_function", [
    ('pending', lambda table, req_id: table.update_item(
        Key={'PK': req_id, 'SK': 'METADATA'},
        UpdateExpression='SET #status = :status',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={':status': 'pending'}
    )),
    ('paid', lambda table, req_id: table.update_item(
        Key={'PK': req_id, 'SK': 'METADATA'},
        UpdateExpression='SET #status = :status, paid_at = :time',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': 'paid',
            ':time': datetime.utcnow().isoformat() + 'Z'
        }
    )),
    ('cancelled', lambda table, req_id: table.update_item(
        Key={'PK': req_id, 'SK': 'METADATA'},
        UpdateExpression='SET #status = :status, cancelled_at = :time',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': 'cancelled',
            ':time': datetime.utcnow().isoformat() + 'Z'
        }
    )),
])
def test_assignment_update_only_for_accepted(
    dynamodb_table, context, admin_event_factory, initial_status, setup_function
):
    """
    Test that assignment details can only be updated for accepted requests
    """
    # Arrange - create an accepted request then change its status
    rental_request_id = create_accepted_request(dynamodb_table, context)
    setup_function(dynamodb_table, rental_request_id)
    
    # Verify status was changed
    item = dynamodb_table.get_item(Key={'PK': rental_request_id, 'SK': 'METADATA'})
    assert item['Item']['status'] == initial_status
    
    # Create event to update assignment details
    event = admin_event_factory(rental_request_id, 'Trying to update non-accepted request')
    
    # Act
    response = update_handler(event, context)
    
    # Assert - should be rejected
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] is False
    assert initial_status in body['error']['message'].lower() or 'accepted' in body['error']['message'].lower()


@pytest.mark.parametrize("assignment_details,should_succeed", [
    ('Valid assignment', True),
    ('', False),  # Empty
    ('   ', False),  # Whitespace only
    ('A' * 1001, False),  # Too long
])
def test_assignment_update_validation(
    dynamodb_table, context, admin_event_factory, assignment_details, should_succeed
):
    """
    Test that assignment details validation works correctly
    """
    # Arrange
    rental_request_id = create_accepted_request(dynamodb_table, context)
    
    if assignment_details is None:
        event = {
            'pathParameters': {'id': rental_request_id},
            'body': json.dumps({}),
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'sub': 'admin-user-123',
                        'email': 'admin@example.com',
                        'cognito:groups': 'admins'
                    }
                }
            }
        }
    else:
        event = admin_event_factory(rental_request_id, assignment_details)
    
    # Act
    response = update_handler(event, context)
    
    # Assert
    if should_succeed:
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
    else:
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['success'] is False


def test_assignment_update_nonexistent_request(dynamodb_table, context, admin_event_factory):
    """
    Test that updating a non-existent request returns 404
    """
    # Arrange
    event = admin_event_factory('RENTAL_REQUEST#nonexistent', 'Some details')
    
    # Act
    response = update_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert body['success'] is False


def test_assignment_update_without_admin_role(dynamodb_table, context):
    """
    Test that non-admin users cannot update assignment details
    """
    # Arrange
    rental_request_id = create_accepted_request(dynamodb_table, context)
    
    event = {
        'pathParameters': {'id': rental_request_id},
        'body': json.dumps({
            'assignment_details': 'Trying to update as team manager'
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'user-123',
                    'email': 'teammanager@example.com',
                    'cognito:groups': 'team_managers'
                }
            }
        }
    }
    
    # Act
    response = update_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 403
    body = json.loads(response['body'])
    assert body['success'] is False


def test_assignment_update_without_authentication(dynamodb_table, context):
    """
    Test that unauthenticated requests are rejected
    """
    # Arrange
    rental_request_id = create_accepted_request(dynamodb_table, context)
    
    event = {
        'pathParameters': {'id': rental_request_id},
        'body': json.dumps({
            'assignment_details': 'Trying without auth'
        }),
        'requestContext': {}
    }
    
    # Act
    response = update_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 401
    body = json.loads(response['body'])
    assert body['success'] is False


def test_assignment_update_missing_path_parameter(dynamodb_table, context):
    """
    Test that missing rental_request_id returns validation error
    """
    # Arrange
    event = {
        'pathParameters': {},
        'body': json.dumps({
            'assignment_details': 'Some details'
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'admin-user-123',
                    'email': 'admin@example.com',
                    'cognito:groups': 'admins'
                }
            }
        }
    }
    
    # Act
    response = update_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] is False


def test_assignment_update_invalid_json(dynamodb_table, context):
    """
    Test that invalid JSON returns validation error
    """
    # Arrange
    rental_request_id = create_accepted_request(dynamodb_table, context)
    
    event = {
        'pathParameters': {'id': rental_request_id},
        'body': 'invalid json {',
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'admin-user-123',
                    'email': 'admin@example.com',
                    'cognito:groups': 'admins'
                }
            }
        }
    }
    
    # Act
    response = update_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] is False
