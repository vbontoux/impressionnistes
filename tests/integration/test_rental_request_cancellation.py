"""
Integration tests for rental request cancellation
Tests Properties 20, 21, and 22 from the boat-rental-refactoring design
"""
import pytest
import sys
import os
import json
from datetime import datetime

# Add functions paths to system path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/rental'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/admin'))

# Set environment variables before importing Lambda functions
os.environ['TABLE_NAME'] = 'test-impressionnistes-table'
os.environ['AWS_DEFAULT_REGION'] = 'eu-west-3'

from cancel_rental_request import lambda_handler as cancel_handler
from create_rental_request import lambda_handler as create_handler
from accept_rental_request import lambda_handler as accept_handler


@pytest.fixture
def team_manager_event_factory():
    """Factory to create team manager events with custom rental_request_id"""
    def _create_event(rental_request_id, user_id='test-user-123', email='teammanager@example.com'):
        return {
            'pathParameters': {
                'id': rental_request_id
            },
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'sub': user_id,
                        'email': email,
                        'cognito:groups': 'team_managers'
                    }
                }
            }
        }
    return _create_event


@pytest.fixture
def context():
    """Create a mock Lambda context"""
    class MockContext:
        function_name = 'cancel_rental_request'
        memory_limit_in_mb = 128
        invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:cancel_rental_request'
        aws_request_id = 'test-request-id'
    
    return MockContext()


def create_pending_request(dynamodb_table, context, user_id='test-user-123', email='teammanager@example.com', boat_type='skiff'):
    """Helper function to create a pending rental request"""
    event = {
        'body': json.dumps({
            'boat_type': boat_type,
            'desired_weight_range': '70-90kg',
            'request_comment': 'Need a boat for testing'
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': user_id,
                    'email': email,
                    'cognito:groups': 'team_managers'
                }
            }
        }
    }
    
    response = create_handler(event, context)
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    return body['data']['rental_request_id']


def create_accepted_request(dynamodb_table, context, user_id='test-user-123', email='teammanager@example.com'):
    """Helper function to create an accepted rental request"""
    rental_request_id = create_pending_request(dynamodb_table, context, user_id, email)
    
    # Accept the request
    accept_event = {
        'pathParameters': {'id': rental_request_id},
        'body': json.dumps({
            'assignment_details': 'Boat #1, dock A'
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


# Feature: boat-rental-refactoring, Property 20: Cancellation Only for Pending or Accepted
# For any team manager cancellation attempt, the operation should succeed if and only if
# the request has status "pending" or "accepted".


@pytest.mark.parametrize("initial_status,should_succeed", [
    ('pending', True),
    ('accepted', True),
])
def test_property_20_cancellation_only_pending_accepted(
    dynamodb_table, context, team_manager_event_factory, initial_status, should_succeed
):
    """
    Property 20: Cancellation Only for Pending or Accepted
    Validates: Requirements 6.1, 6.4
    
    Test that only pending or accepted requests can be cancelled.
    """
    # Arrange - create request with appropriate status
    if initial_status == 'pending':
        rental_request_id = create_pending_request(dynamodb_table, context)
    else:  # accepted
        rental_request_id = create_accepted_request(dynamodb_table, context)
    
    # Verify initial status
    item = dynamodb_table.get_item(Key={'PK': rental_request_id, 'SK': 'METADATA'})
    assert item['Item']['status'] == initial_status
    
    # Create event to cancel
    event = team_manager_event_factory(rental_request_id)
    
    # Act
    response = cancel_handler(event, context)
    
    # Assert
    if should_succeed:
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['data']['status'] == 'cancelled'
    else:
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['success'] is False


@pytest.mark.parametrize("initial_status,setup_function", [
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
def test_property_20_cannot_cancel_paid_or_cancelled(
    dynamodb_table, context, team_manager_event_factory, initial_status, setup_function
):
    """
    Property 20: Cancellation Only for Pending or Accepted (negative test)
    
    Test that paid or already cancelled requests cannot be cancelled.
    """
    # Arrange - create accepted request then change status
    rental_request_id = create_accepted_request(dynamodb_table, context)
    setup_function(dynamodb_table, rental_request_id)
    
    # Verify status was changed
    item = dynamodb_table.get_item(Key={'PK': rental_request_id, 'SK': 'METADATA'})
    assert item['Item']['status'] == initial_status
    
    # Create event to cancel
    event = team_manager_event_factory(rental_request_id)
    
    # Act
    response = cancel_handler(event, context)
    
    # Assert - should be rejected
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] is False
    assert initial_status in body['error']['message'].lower() or 'pending' in body['error']['message'].lower() or 'accepted' in body['error']['message'].lower()


# Feature: boat-rental-refactoring, Property 21: Cancellation Transitions Status Correctly
# For any rental request being cancelled, the status should change to "cancelled",
# cancelled_at timestamp should be recorded, and cancelled_by should be set to the user_id
# of the cancelling user.


@pytest.mark.parametrize("initial_status,user_id,user_email", [
    ('pending', 'user-123', 'user1@example.com'),
    ('pending', 'user-456', 'user2@example.com'),
    ('accepted', 'user-789', 'user3@example.com'),
    ('accepted', 'user-abc', 'manager@club.com'),
])
def test_property_21_cancellation_transitions_status(
    dynamodb_table, context, team_manager_event_factory, initial_status, user_id, user_email
):
    """
    Property 21: Cancellation Transitions Status Correctly
    Validates: Requirements 6.2, 6.3
    
    Test that cancellation correctly transitions status and records metadata.
    """
    # Arrange - create request with appropriate status
    if initial_status == 'pending':
        rental_request_id = create_pending_request(dynamodb_table, context, user_id, user_email)
    else:  # accepted
        rental_request_id = create_accepted_request(dynamodb_table, context, user_id, user_email)
    
    # Verify initial status
    item = dynamodb_table.get_item(Key={'PK': rental_request_id, 'SK': 'METADATA'})
    assert item['Item']['status'] == initial_status
    
    # Create event to cancel
    event = team_manager_event_factory(rental_request_id, user_id, user_email)
    
    # Act
    response = cancel_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    # Verify status transition
    assert body['data']['status'] == 'cancelled', "Status must transition to 'cancelled'"
    
    # Verify cancelled_at timestamp is present and valid
    assert 'cancelled_at' in body['data'], "cancelled_at timestamp must be recorded"
    cancelled_at_str = body['data']['cancelled_at']
    try:
        cancelled_at = datetime.fromisoformat(cancelled_at_str.replace('Z', '+00:00'))
    except ValueError:
        pytest.fail(f"cancelled_at is not valid ISO 8601 format: {cancelled_at_str}")
    
    # Verify timestamp is recent (within last minute)
    from datetime import timezone
    now = datetime.now(timezone.utc)
    time_diff = abs((now - cancelled_at).total_seconds())
    assert time_diff < 60, f"cancelled_at should be recent (within 60 seconds)"
    
    # Verify cancelled_by is recorded
    assert body['data']['cancelled_by'] == user_id, "cancelled_by must record team manager user_id"
    
    # Verify in database
    item = dynamodb_table.get_item(Key={'PK': rental_request_id, 'SK': 'METADATA'})
    db_item = item['Item']
    assert db_item['status'] == 'cancelled'
    assert db_item['cancelled_at'] == cancelled_at_str
    assert db_item['cancelled_by'] == user_id


# Feature: boat-rental-refactoring, Property 22: Cancellation Preserves Request Data
# For any rental request being cancelled, all original fields (boat_type, desired_weight_range,
# request_comment, requester_id, requester_email, created_at) should remain unchanged.


@pytest.mark.parametrize("boat_type,weight_range,comment", [
    ('skiff', '70-90kg', 'Need a skiff'),
    ('4-', '75-85kg', 'Four without cox'),
    ('8+', '70-80kg', 'Eight with cox for race'),
])
def test_property_22_cancellation_preserves_data(
    dynamodb_table, context, team_manager_event_factory, boat_type, weight_range, comment
):
    """
    Property 22: Cancellation Preserves Request Data
    Validates: Requirements 6.5
    
    Test that cancellation preserves all original request data.
    """
    # Arrange - create request with specific data
    event = {
        'body': json.dumps({
            'boat_type': boat_type,
            'desired_weight_range': weight_range,
            'request_comment': comment
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
    
    response = create_handler(event, context)
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    rental_request_id = body['data']['rental_request_id']
    
    # Store original data
    original_data = {
        'boat_type': body['data']['boat_type'],
        'desired_weight_range': body['data']['desired_weight_range'],
        'request_comment': body['data']['request_comment'],
        'requester_id': body['data']['requester_id'],
        'requester_email': body['data']['requester_email'],
        'created_at': body['data']['created_at']
    }
    
    # Act - cancel the request
    cancel_event = team_manager_event_factory(rental_request_id)
    response = cancel_handler(cancel_event, context)
    
    # Assert
    assert response['statusCode'] == 200
    
    # Verify in database that original data is preserved
    item = dynamodb_table.get_item(Key={'PK': rental_request_id, 'SK': 'METADATA'})
    db_item = item['Item']
    
    assert db_item['boat_type'] == original_data['boat_type'], "boat_type must be preserved"
    assert db_item['desired_weight_range'] == original_data['desired_weight_range'], "desired_weight_range must be preserved"
    assert db_item['request_comment'] == original_data['request_comment'], "request_comment must be preserved"
    assert db_item['requester_id'] == original_data['requester_id'], "requester_id must be preserved"
    assert db_item['requester_email'] == original_data['requester_email'], "requester_email must be preserved"
    assert db_item['created_at'] == original_data['created_at'], "created_at must be preserved"
    
    # Verify status changed to cancelled
    assert db_item['status'] == 'cancelled'


def test_cancellation_preserves_assignment_details(dynamodb_table, context, team_manager_event_factory):
    """
    Test that cancelling an accepted request preserves assignment details
    """
    # Arrange - create accepted request with assignment details
    rental_request_id = create_accepted_request(dynamodb_table, context)
    
    # Get assignment details before cancellation
    item = dynamodb_table.get_item(Key={'PK': rental_request_id, 'SK': 'METADATA'})
    original_assignment = item['Item']['assignment_details']
    assert original_assignment  # Should have assignment details
    
    # Act - cancel the request
    event = team_manager_event_factory(rental_request_id)
    response = cancel_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    
    # Verify assignment details preserved
    item = dynamodb_table.get_item(Key={'PK': rental_request_id, 'SK': 'METADATA'})
    assert item['Item']['assignment_details'] == original_assignment


def test_cannot_cancel_other_users_request(dynamodb_table, context, team_manager_event_factory):
    """
    Test that team managers can only cancel their own requests
    """
    # Arrange - create request for user1
    rental_request_id = create_pending_request(dynamodb_table, context, 'user-1', 'user1@example.com')
    
    # Try to cancel as user2
    event = team_manager_event_factory(rental_request_id, 'user-2', 'user2@example.com')
    
    # Act
    response = cancel_handler(event, context)
    
    # Assert - should be forbidden
    assert response['statusCode'] == 403
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'own' in body['error']['message'].lower()
    
    # Verify status unchanged
    item = dynamodb_table.get_item(Key={'PK': rental_request_id, 'SK': 'METADATA'})
    assert item['Item']['status'] == 'pending'


def test_cancel_nonexistent_request(dynamodb_table, context, team_manager_event_factory):
    """
    Test that cancelling a non-existent request returns 404
    """
    # Arrange
    event = team_manager_event_factory('RENTAL_REQUEST#nonexistent')
    
    # Act
    response = cancel_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert body['success'] is False


def test_cancel_without_team_manager_role(dynamodb_table, context):
    """
    Test that non-team-manager users cannot cancel requests
    """
    # Arrange
    rental_request_id = create_pending_request(dynamodb_table, context)
    
    event = {
        'pathParameters': {'id': rental_request_id},
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'regular-user-123',
                    'email': 'user@example.com',
                    'cognito:groups': 'regular_users'
                }
            }
        }
    }
    
    # Act
    response = cancel_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 403
    body = json.loads(response['body'])
    assert body['success'] is False


def test_cancel_without_authentication(dynamodb_table, context):
    """
    Test that unauthenticated requests are rejected
    """
    # Arrange
    rental_request_id = create_pending_request(dynamodb_table, context)
    
    event = {
        'pathParameters': {'id': rental_request_id},
        'requestContext': {}
    }
    
    # Act
    response = cancel_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 401
    body = json.loads(response['body'])
    assert body['success'] is False


def test_cancel_missing_path_parameter(dynamodb_table, context):
    """
    Test that missing rental_request_id returns validation error
    """
    # Arrange
    event = {
        'pathParameters': {},
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
    
    # Act
    response = cancel_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] is False
