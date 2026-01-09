"""
Integration tests for rental request creation
Tests Properties 2, 3, and 4 from the boat-rental-refactoring design
"""
import pytest
import sys
import os
import json
from datetime import datetime

# Add functions paths to system path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/rental'))

# Set environment variables before importing Lambda functions
os.environ['TABLE_NAME'] = 'test-impressionnistes-table'
os.environ['AWS_DEFAULT_REGION'] = 'eu-west-3'

from create_rental_request import lambda_handler


def get_db_key(rental_request_id):
    """Convert API response ID to DynamoDB key"""
    if rental_request_id.startswith('RENTAL_REQUEST#'):
        return rental_request_id
    return f"RENTAL_REQUEST#{rental_request_id}"


@pytest.fixture
def team_manager_event():
    """Create a mock API Gateway event for a team manager"""
    return {
        'body': json.dumps({
            'boat_type': 'skiff',
            'desired_weight_range': '70-90kg',
            'request_comment': 'Need a skiff for the 21km race'
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


@pytest.fixture
def context():
    """Create a mock Lambda context"""
    class MockContext:
        function_name = 'create_rental_request'
        memory_limit_in_mb = 128
        invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:create_rental_request'
        aws_request_id = 'test-request-id'
    
    return MockContext()


# Feature: boat-rental-refactoring, Property 2: Initial Status is Pending
# For any newly created rental request, the status should always be "pending".


@pytest.mark.parametrize("boat_type,desired_weight_range,request_comment", [
    ('skiff', '70-90kg', 'Need a skiff'),
    ('4-', '75-85kg', 'Looking for a 4-'),
    ('4+', '70-90kg', 'Need 4+ with cox'),
    ('4x-', '80-95kg', 'Quad scull needed'),
    ('4x+', '75-90kg', 'Quad with cox'),
    ('8+', '70-85kg', 'Eight needed'),
    ('8x+', '75-90kg', 'Octuple scull'),
])
def test_property_2_initial_status_pending(dynamodb_table, context, boat_type, desired_weight_range, request_comment):
    """
    Property 2: Initial Status is Pending
    Validates: Requirements 1.2
    
    Test that all newly created rental requests have status "pending".
    """
    # Arrange
    event = {
        'body': json.dumps({
            'boat_type': boat_type,
            'desired_weight_range': desired_weight_range,
            'request_comment': request_comment
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
    
    # Act
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['status'] == 'pending', "Newly created request must have status 'pending'"
    
    # Verify in database
    rental_request_id = body['data']['rental_request_id']
    db_key = get_db_key(rental_request_id)
    item = dynamodb_table.get_item(Key={'PK': db_key, 'SK': 'METADATA'})
    assert 'Item' in item
    assert item['Item']['status'] == 'pending'


# Feature: boat-rental-refactoring, Property 3: Requester Information Recorded
# For any newly created rental request, the requester_id and requester_email fields
# should be populated with the authenticated user's information.


@pytest.mark.parametrize("user_id,user_email", [
    ('user-123', 'user1@example.com'),
    ('user-456', 'user2@example.com'),
    ('user-789', 'teammanager@club.com'),
])
def test_property_3_requester_information_recorded(dynamodb_table, context, user_id, user_email):
    """
    Property 3: Requester Information Recorded
    Validates: Requirements 1.3
    
    Test that requester_id and requester_email are correctly recorded from authenticated user.
    """
    # Arrange
    event = {
        'body': json.dumps({
            'boat_type': 'skiff',
            'desired_weight_range': '70-90kg',
            'request_comment': 'Need a boat'
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': user_id,
                    'email': user_email,
                    'cognito:groups': 'team_managers'
                }
            }
        }
    }
    
    # Act
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['requester_id'] == user_id, "requester_id must match authenticated user_id"
    assert body['data']['requester_email'] == user_email, "requester_email must match authenticated email"
    
    # Verify in database
    rental_request_id = body['data']['rental_request_id']
    db_key = get_db_key(rental_request_id)
    item = dynamodb_table.get_item(Key={'PK': db_key, 'SK': 'METADATA'})
    assert 'Item' in item
    assert item['Item']['requester_id'] == user_id
    assert item['Item']['requester_email'] == user_email


# Feature: boat-rental-refactoring, Property 4: Creation Timestamp Recorded
# For any newly created rental request, the created_at field should be present
# and contain a valid ISO 8601 timestamp.


@pytest.mark.parametrize("boat_type", ['skiff', '4-', '4+', '4x-', '4x+', '8+', '8x+'])
def test_property_4_creation_timestamp_recorded(dynamodb_table, context, boat_type):
    """
    Property 4: Creation Timestamp Recorded
    Validates: Requirements 1.4
    
    Test that created_at timestamp is present and valid ISO 8601 format.
    """
    # Arrange
    event = {
        'body': json.dumps({
            'boat_type': boat_type,
            'desired_weight_range': '70-90kg',
            'request_comment': 'Need a boat'
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
    
    # Act
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'created_at' in body['data'], "created_at field must be present"
    
    # Validate ISO 8601 format
    created_at_str = body['data']['created_at']
    try:
        # Parse ISO 8601 timestamp (with 'Z' suffix)
        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
    except ValueError:
        pytest.fail(f"created_at is not valid ISO 8601 format: {created_at_str}")
    
    # Verify timestamp is reasonable (should be recent - within last minute)
    from datetime import timezone, timedelta
    now = datetime.now(timezone.utc)
    time_diff = abs((now - created_at).total_seconds())
    assert time_diff < 60, f"created_at should be recent (within 60 seconds), but was {time_diff} seconds ago"
    
    # Verify in database
    rental_request_id = body['data']['rental_request_id']
    db_key = get_db_key(rental_request_id)
    item = dynamodb_table.get_item(Key={'PK': db_key, 'SK': 'METADATA'})
    assert 'Item' in item
    assert 'created_at' in item['Item']
    assert item['Item']['created_at'] == created_at_str


def test_property_2_3_4_combined(dynamodb_table, team_manager_event, context):
    """
    Combined test for Properties 2, 3, and 4
    
    Test that a newly created request has:
    - status = "pending" (Property 2)
    - requester_id and requester_email populated (Property 3)
    - created_at timestamp present and valid (Property 4)
    """
    # Act
    response = lambda_handler(team_manager_event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    data = body['data']
    
    # Property 2: Initial status is pending
    assert data['status'] == 'pending'
    
    # Property 3: Requester information recorded
    assert data['requester_id'] == 'test-user-123'
    assert data['requester_email'] == 'teammanager@example.com'
    
    # Property 4: Creation timestamp recorded
    assert 'created_at' in data
    try:
        datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
    except ValueError:
        pytest.fail(f"created_at is not valid ISO 8601 format: {data['created_at']}")
    
    # Verify all properties in database
    rental_request_id = data['rental_request_id']
    db_key = get_db_key(rental_request_id)
    item = dynamodb_table.get_item(Key={'PK': db_key, 'SK': 'METADATA'})
    assert 'Item' in item
    db_item = item['Item']
    
    assert db_item['status'] == 'pending'
    assert db_item['requester_id'] == 'test-user-123'
    assert db_item['requester_email'] == 'teammanager@example.com'
    assert 'created_at' in db_item


def test_request_id_format(dynamodb_table, team_manager_event, context):
    """
    Test that rental_request_id returned from API is a clean UUID (without RENTAL_REQUEST# prefix)
    but stored in database with the prefix.
    """
    # Act
    response = lambda_handler(team_manager_event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    rental_request_id = body['data']['rental_request_id']
    
    # API should return clean UUID (no prefix)
    assert not rental_request_id.startswith('RENTAL_REQUEST#'), "API should return clean UUID without prefix"
    assert len(rental_request_id) == 36, "UUID should be 36 characters"
    assert rental_request_id.count('-') == 4, "UUID should have 4 hyphens"
    
    # Database should store with prefix
    db_key = get_db_key(rental_request_id)
    assert db_key.startswith('RENTAL_REQUEST#'), "Database key must have RENTAL_REQUEST# prefix"
    item = dynamodb_table.get_item(Key={'PK': db_key, 'SK': 'METADATA'})
    assert 'Item' in item


def test_unauthorized_access_rejected(dynamodb_table, context):
    """
    Test that requests without authentication are rejected
    """
    # Arrange - event without authentication
    event = {
        'body': json.dumps({
            'boat_type': 'skiff',
            'desired_weight_range': '70-90kg',
            'request_comment': 'Need a boat'
        }),
        'requestContext': {}
    }
    
    # Act
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 401
    body = json.loads(response['body'])
    assert body['success'] is False


def test_non_team_manager_rejected(dynamodb_table, context):
    """
    Test that users without team_manager role are rejected
    """
    # Arrange - user without team_managers group
    event = {
        'body': json.dumps({
            'boat_type': 'skiff',
            'desired_weight_range': '70-90kg',
            'request_comment': 'Need a boat'
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'test-user-123',
                    'email': 'user@example.com',
                    'cognito:groups': 'regular_users'
                }
            }
        }
    }
    
    # Act
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 403
    body = json.loads(response['body'])
    assert body['success'] is False
