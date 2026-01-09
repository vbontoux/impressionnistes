"""
Integration tests for rental request acceptance
Tests Properties 12, 13, and 14 from the boat-rental-refactoring design
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

from accept_rental_request import lambda_handler as accept_handler
from create_rental_request import lambda_handler as create_handler


def get_rental_request_db_key(rental_request_id):
    """Convert a rental_request_id (clean UUID) into the full DynamoDB key format"""
    if rental_request_id.startswith('RENTAL_REQUEST#'):
        return rental_request_id
    return f"RENTAL_REQUEST#{rental_request_id}"


@pytest.fixture
def admin_event_factory():
    """Factory to create admin events with custom rental_request_id and body"""
    def _create_event(rental_request_id, assignment_details):
        # Strip RENTAL_REQUEST# prefix if present (API expects just UUID)
        clean_id = rental_request_id.replace('RENTAL_REQUEST#', '')
        return {
            'pathParameters': {
                'rental_request_id': clean_id
            },
            'body': json.dumps({
                'assignment_details': assignment_details
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
    return _create_event


@pytest.fixture
def context():
    """Create a mock Lambda context"""
    class MockContext:
        function_name = 'accept_rental_request'
        memory_limit_in_mb = 128
        invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:accept_rental_request'
        aws_request_id = 'test-request-id'
    
    return MockContext()


def create_pending_request(dynamodb_table, context, boat_type='skiff'):
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
    return body['data']['rental_request_id']


# Feature: boat-rental-refactoring, Property 12: Accept Requires Assignment Details
# For any attempt to accept a rental request, the operation should succeed if and only if
# assignment_details is provided, is non-empty, and is ≤1000 characters.


@pytest.mark.parametrize("assignment_details,should_succeed", [
    # Valid assignment details
    ('Boat #42, oars included, dock A', True),
    ('Boat: Skiff-001\nOars: Yes\nLocation: Dock B\nContact: +33123456789', True),
    ('A' * 1000, True),  # Exactly 1000 chars
    ('   Valid with spaces   ', True),  # Whitespace trimmed
    
    # Invalid assignment details
    ('', False),  # Empty string
    ('   ', False),  # Only whitespace
    (None, False),  # None value
    ('A' * 1001, False),  # Too long (1001 chars)
])
def test_property_12_accept_requires_assignment_details(
    dynamodb_table, context, admin_event_factory, assignment_details, should_succeed
):
    """
    Property 12: Accept Requires Assignment Details
    Validates: Requirements 4.1, 4.5
    
    Test that accepting a request requires valid assignment_details.
    """
    # Arrange - create a pending request
    rental_request_id = create_pending_request(dynamodb_table, context)
    
    # Create admin event with test assignment_details
    if assignment_details is None:
        # Test missing assignment_details
        clean_id = rental_request_id.replace('RENTAL_REQUEST#', '')
        event = {
            'pathParameters': {'rental_request_id': clean_id},
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
    response = accept_handler(event, context)
    
    # Assert
    if should_succeed:
        assert response['statusCode'] == 200, f"Should succeed with assignment_details: {assignment_details[:50] if assignment_details else None}"
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['data']['status'] == 'accepted'
        assert 'assignment_details' in body['data']
        # Verify whitespace is trimmed
        if assignment_details:
            assert body['data']['assignment_details'] == assignment_details.strip()
    else:
        assert response['statusCode'] == 400, f"Should fail with assignment_details: {assignment_details[:50] if assignment_details else None}"
        body = json.loads(response['body'])
        assert body['success'] is False
        assert 'assignment_details' in body['error']['message'].lower()


# Feature: boat-rental-refactoring, Property 13: Accept Transitions Status Correctly
# For any rental request with status "pending", accepting it should change the status to "accepted",
# record accepted_at timestamp, and record accepted_by with the admin's user_id.


@pytest.mark.parametrize("boat_type,admin_id,admin_email", [
    ('skiff', 'admin-123', 'admin1@example.com'),
    ('4-', 'admin-456', 'admin2@example.com'),
    ('4+', 'admin-789', 'admin3@example.com'),
    ('8+', 'admin-abc', 'superadmin@example.com'),
])
def test_property_13_accept_transitions_status_correctly(
    dynamodb_table, context, boat_type, admin_id, admin_email
):
    """
    Property 13: Accept Transitions Status Correctly
    Validates: Requirements 4.2, 4.3, 4.4
    
    Test that accepting a pending request correctly transitions status and records metadata.
    """
    # Arrange - create a pending request
    rental_request_id = create_pending_request(dynamodb_table, context, boat_type)
    
    # Verify initial status is pending (convert clean UUID to DB key format)
    db_key = get_rental_request_db_key(rental_request_id)
    item = dynamodb_table.get_item(Key={'PK': db_key, 'SK': 'METADATA'})
    assert item['Item']['status'] == 'pending'
    
    # Create admin event
    clean_id = rental_request_id.replace('RENTAL_REQUEST#', '')
    event = {
        'pathParameters': {'rental_request_id': clean_id},
        'body': json.dumps({
            'assignment_details': f'Boat assigned for {boat_type}'
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': admin_id,
                    'email': admin_email,
                    'cognito:groups': 'admins'
                }
            }
        }
    }
    
    # Act
    response = accept_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    # Verify status transition
    assert body['data']['status'] == 'accepted', "Status must transition to 'accepted'"
    
    # Verify accepted_at timestamp is present and valid
    assert 'accepted_at' in body['data'], "accepted_at timestamp must be recorded"
    accepted_at_str = body['data']['accepted_at']
    try:
        accepted_at = datetime.fromisoformat(accepted_at_str.replace('Z', '+00:00'))
    except ValueError:
        pytest.fail(f"accepted_at is not valid ISO 8601 format: {accepted_at_str}")
    
    # Verify timestamp is recent (within last minute)
    from datetime import timezone
    now = datetime.now(timezone.utc)
    time_diff = abs((now - accepted_at).total_seconds())
    assert time_diff < 60, f"accepted_at should be recent (within 60 seconds)"
    
    # Verify accepted_by is recorded
    assert body['data']['accepted_by'] == admin_id, "accepted_by must record admin user_id"
    
    # Verify in database (convert clean UUID to DB key format)
    db_key = get_rental_request_db_key(rental_request_id)
    item_response = dynamodb_table.get_item(Key={'PK': db_key, 'SK': 'METADATA'})
    assert 'Item' in item_response, f"Item should exist in database after acceptance"
    db_item = item_response['Item']
    assert db_item['status'] == 'accepted'
    assert db_item['accepted_at'] == accepted_at_str
    assert db_item['accepted_by'] == admin_id
    assert db_item['assignment_details'] == f'Boat assigned for {boat_type}'


# Feature: boat-rental-refactoring, Property 14: Accept Only Works on Pending Requests
# For any rental request with status other than "pending", attempting to accept it should be rejected.


@pytest.mark.parametrize("initial_status,setup_function", [
    ('accepted', lambda table, req_id: table.update_item(
        Key={'PK': req_id, 'SK': 'METADATA'},
        UpdateExpression='SET #status = :status, assignment_details = :details, accepted_at = :time, accepted_by = :admin',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': 'accepted',
            ':details': 'Already assigned',
            ':time': datetime.utcnow().isoformat() + 'Z',
            ':admin': 'admin-123'
        }
    )),
    ('paid', lambda table, req_id: table.update_item(
        Key={'PK': req_id, 'SK': 'METADATA'},
        UpdateExpression='SET #status = :status, assignment_details = :details, accepted_at = :atime, paid_at = :ptime',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': 'paid',
            ':details': 'Already assigned',
            ':atime': datetime.utcnow().isoformat() + 'Z',
            ':ptime': datetime.utcnow().isoformat() + 'Z'
        }
    )),
    ('cancelled', lambda table, req_id: table.update_item(
        Key={'PK': req_id, 'SK': 'METADATA'},
        UpdateExpression='SET #status = :status, cancelled_at = :time, cancelled_by = :user',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': 'cancelled',
            ':time': datetime.utcnow().isoformat() + 'Z',
            ':user': 'user-123'
        }
    )),
])
def test_property_14_accept_only_pending_requests(
    dynamodb_table, context, admin_event_factory, initial_status, setup_function
):
    """
    Property 14: Accept Only Works on Pending Requests
    Validates: Requirements 4.6
    
    Test that only pending requests can be accepted.
    """
    # Arrange - create a pending request
    rental_request_id = create_pending_request(dynamodb_table, context)
    
    # Change status to non-pending (convert clean UUID to DB key format)
    db_key = get_rental_request_db_key(rental_request_id)
    setup_function(dynamodb_table, db_key)
    
    # Verify status was changed
    item_response = dynamodb_table.get_item(Key={'PK': db_key, 'SK': 'METADATA'})
    assert 'Item' in item_response
    assert item_response['Item']['status'] == initial_status
    
    # Create admin event to accept
    event = admin_event_factory(rental_request_id, 'Trying to accept non-pending request')
    
    # Act
    response = accept_handler(event, context)
    
    # Assert - should be rejected
    assert response['statusCode'] == 400, f"Should reject accepting request with status '{initial_status}'"
    body = json.loads(response['body'])
    assert body['success'] is False
    assert initial_status in body['error']['message'].lower() or 'pending' in body['error']['message'].lower()
    
    # Verify status unchanged in database (convert clean UUID to DB key format)
    db_key = get_rental_request_db_key(rental_request_id)
    item_response = dynamodb_table.get_item(Key={'PK': db_key, 'SK': 'METADATA'})
    assert 'Item' in item_response
    assert item_response['Item']['status'] == initial_status, "Status should remain unchanged after failed accept"


def test_accept_pending_request_success(dynamodb_table, context, admin_event_factory):
    """
    Test successful acceptance of a pending request (happy path)
    """
    # Arrange
    rental_request_id = create_pending_request(dynamodb_table, context)
    event = admin_event_factory(
        rental_request_id,
        'Boat #42, oars included, dock A, contact: +33123456789'
    )
    
    # Act
    response = accept_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['status'] == 'accepted'
    assert body['data']['assignment_details'] == 'Boat #42, oars included, dock A, contact: +33123456789'
    assert 'accepted_at' in body['data']
    assert 'accepted_by' in body['data']


def test_accept_nonexistent_request(dynamodb_table, context, admin_event_factory):
    """
    Test that accepting a non-existent request returns 404
    """
    # Arrange
    event = admin_event_factory('RENTAL_REQUEST#nonexistent', 'Some assignment details')
    
    # Act
    response = accept_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'not found' in body['error']['message'].lower()


def test_accept_without_admin_role(dynamodb_table, context):
    """
    Test that non-admin users cannot accept requests
    """
    # Arrange
    rental_request_id = create_pending_request(dynamodb_table, context)
    clean_id = rental_request_id.replace('RENTAL_REQUEST#', '')
    
    # Create event with team_manager role (not admin)
    event = {
        'pathParameters': {'rental_request_id': clean_id},
        'body': json.dumps({
            'assignment_details': 'Trying to accept as team manager'
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
    response = accept_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 403
    body = json.loads(response['body'])
    assert body['success'] is False


def test_accept_without_authentication(dynamodb_table, context):
    """
    Test that unauthenticated requests are rejected
    """
    # Arrange
    rental_request_id = create_pending_request(dynamodb_table, context)
    clean_id = rental_request_id.replace('RENTAL_REQUEST#', '')
    
    event = {
        'pathParameters': {'rental_request_id': clean_id},
        'body': json.dumps({
            'assignment_details': 'Trying to accept without auth'
        }),
        'requestContext': {}
    }
    
    # Act
    response = accept_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 401
    body = json.loads(response['body'])
    assert body['success'] is False


def test_accept_missing_path_parameter(dynamodb_table, context):
    """
    Test that missing rental_request_id in path returns validation error
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
    response = accept_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'rental_request_id' in body['error']['message'].lower()


def test_accept_invalid_json_body(dynamodb_table, context):
    """
    Test that invalid JSON in request body returns validation error
    """
    # Arrange
    rental_request_id = create_pending_request(dynamodb_table, context)
    clean_id = rental_request_id.replace('RENTAL_REQUEST#', '')
    
    event = {
        'pathParameters': {'rental_request_id': clean_id},
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
    response = accept_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'json' in body['error']['message'].lower()
