"""
Integration tests for rental request listing
Tests Properties 5, 6, 7, and 8 from the boat-rental-refactoring design
"""
import pytest
import sys
import os
import json
from datetime import datetime, timedelta

# Add functions paths to system path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/rental'))

# Set environment variables before importing Lambda functions
os.environ['TABLE_NAME'] = 'test-impressionnistes-table'
os.environ['AWS_DEFAULT_REGION'] = 'eu-west-3'

from get_my_rental_requests import lambda_handler


@pytest.fixture
def team_manager_event():
    """Create a mock API Gateway event for a team manager"""
    return {
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
        function_name = 'get_my_rental_requests'
        memory_limit_in_mb = 128
        invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:get_my_rental_requests'
        aws_request_id = 'test-request-id'
    
    return MockContext()


def create_rental_request(dynamodb_table, requester_id, requester_email, boat_type='skiff', 
                         status='pending', created_at=None, assignment_details=None,
                         accepted_at=None, paid_at=None, cancelled_at=None):
    """Helper function to create a rental request in the database"""
    import uuid
    
    rental_request_id = f"RENTAL_REQUEST#{uuid.uuid4()}"
    if created_at is None:
        created_at = datetime.utcnow().isoformat() + 'Z'
    
    item = {
        'PK': rental_request_id,
        'SK': 'METADATA',
        'rental_request_id': rental_request_id,
        'boat_type': boat_type,
        'desired_weight_range': '70-90kg',
        'request_comment': 'Test request',
        'status': status,
        'requester_id': requester_id,
        'requester_email': requester_email,
        'created_at': created_at,
        'updated_at': created_at
    }
    
    # Add conditional fields
    if assignment_details:
        item['assignment_details'] = assignment_details
    if accepted_at:
        item['accepted_at'] = accepted_at
    if paid_at:
        item['paid_at'] = paid_at
    if cancelled_at:
        item['cancelled_at'] = cancelled_at
    
    dynamodb_table.put_item(Item=item)
    return rental_request_id


# Feature: boat-rental-refactoring, Property 5: Team Manager Request Isolation
# For any team manager querying their rental requests, the returned list should contain
# only requests where requester_id matches that team manager's user_id.


@pytest.mark.parametrize("num_own_requests,num_other_requests", [
    (1, 1),
    (3, 2),
    (5, 5),
    (0, 3),  # No own requests
])
def test_property_5_team_manager_isolation(dynamodb_table, context, num_own_requests, num_other_requests):
    """
    Property 5: Team Manager Request Isolation
    Validates: Requirements 2.1
    
    Test that team managers only see their own requests, not requests from other team managers.
    """
    # Arrange - Create requests for this team manager
    own_user_id = 'test-user-123'
    own_email = 'teammanager@example.com'
    
    own_request_ids = []
    for i in range(num_own_requests):
        request_id = create_rental_request(
            dynamodb_table, 
            own_user_id, 
            own_email,
            boat_type='skiff' if i % 2 == 0 else '4-'
        )
        own_request_ids.append(request_id)
    
    # Create requests for other team managers
    other_request_ids = []
    for i in range(num_other_requests):
        request_id = create_rental_request(
            dynamodb_table,
            f'other-user-{i}',
            f'other{i}@example.com',
            boat_type='8+'
        )
        other_request_ids.append(request_id)
    
    # Arrange - Create event for this team manager
    event = {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': own_user_id,
                    'email': own_email,
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
    
    returned_requests = body['data']['rental_requests']
    assert body['data']['count'] == num_own_requests, f"Should return exactly {num_own_requests} requests"
    assert len(returned_requests) == num_own_requests
    
    # Verify all returned requests belong to this team manager
    returned_ids = [r['rental_request_id'] for r in returned_requests]
    # Strip prefixes from own_request_ids for comparison
    own_clean_ids = [rid.replace('RENTAL_REQUEST#', '') for rid in own_request_ids]
    for request_id in returned_ids:
        assert request_id in own_clean_ids, "Returned request must belong to this team manager"
    
    # Verify no requests from other team managers are returned
    other_clean_ids = [rid.replace('RENTAL_REQUEST#', '') for rid in other_request_ids]
    for request_id in other_clean_ids:
        assert request_id not in returned_ids, "Should not return requests from other team managers"


# Feature: boat-rental-refactoring, Property 6: Request List Sorting
# For any list of rental requests (team manager or admin view), the requests should be
# sorted by created_at in descending order (most recent first).


@pytest.mark.parametrize("num_requests", [2, 3, 5])
def test_property_6_request_list_sorting(dynamodb_table, context, num_requests):
    """
    Property 6: Request List Sorting
    Validates: Requirements 2.4
    
    Test that requests are sorted by created_at descending (most recent first).
    """
    # Arrange - Create requests with different timestamps
    user_id = 'test-user-123'
    email = 'teammanager@example.com'
    
    base_time = datetime.utcnow()
    request_times = []
    
    for i in range(num_requests):
        # Create requests with timestamps 1 hour apart
        created_at = (base_time - timedelta(hours=i)).isoformat() + 'Z'
        request_times.append(created_at)
        create_rental_request(
            dynamodb_table,
            user_id,
            email,
            boat_type='skiff',
            created_at=created_at
        )
    
    # Arrange - Create event
    event = {
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
    
    # Act
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    returned_requests = body['data']['rental_requests']
    assert len(returned_requests) == num_requests
    
    # Verify sorting - most recent first (descending order)
    returned_times = [r['created_at'] for r in returned_requests]
    expected_times = sorted(request_times, reverse=True)
    
    assert returned_times == expected_times, "Requests must be sorted by created_at descending"
    
    # Verify each subsequent request is older than the previous
    for i in range(len(returned_times) - 1):
        assert returned_times[i] > returned_times[i + 1], \
            f"Request {i} should be more recent than request {i+1}"


# Feature: boat-rental-refactoring, Property 7: Required Fields Present in Response
# For any rental request in a response, the following fields should always be present:
# rental_request_id, boat_type, desired_weight_range, request_comment, status,
# requester_id, requester_email, created_at.


@pytest.mark.parametrize("boat_type,status", [
    ('skiff', 'pending'),
    ('4-', 'accepted'),
    ('4+', 'paid'),
    ('8+', 'cancelled'),
])
def test_property_7_required_fields_present(dynamodb_table, context, boat_type, status):
    """
    Property 7: Required Fields Present in Response
    Validates: Requirements 2.2
    
    Test that all required fields are present in every rental request response.
    """
    # Arrange - Create a request
    user_id = 'test-user-123'
    email = 'teammanager@example.com'
    
    create_rental_request(
        dynamodb_table,
        user_id,
        email,
        boat_type=boat_type,
        status=status
    )
    
    # Arrange - Create event
    event = {
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
    
    # Act
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    returned_requests = body['data']['rental_requests']
    assert len(returned_requests) > 0
    
    # Verify required fields are present in each request
    required_fields = [
        'rental_request_id',
        'boat_type',
        'desired_weight_range',
        'request_comment',
        'status',
        'created_at'
    ]
    
    for request in returned_requests:
        for field in required_fields:
            assert field in request, f"Required field '{field}' must be present in response"
            assert request[field] is not None, f"Required field '{field}' must not be None"


# Feature: boat-rental-refactoring, Property 8: Conditional Fields Present Based on Status
# For any rental request with status "accepted", the assignment_details and accepted_at
# fields should be present; for status "paid", the paid_at field should be present;
# for status "cancelled", the cancelled_at field should be present.


@pytest.mark.parametrize("status,conditional_fields", [
    ('pending', []),
    ('accepted', ['assignment_details', 'accepted_at']),
    ('paid', ['assignment_details', 'accepted_at', 'paid_at']),
    ('cancelled', ['cancelled_at']),
])
def test_property_8_conditional_fields_based_on_status(dynamodb_table, context, status, conditional_fields):
    """
    Property 8: Conditional Fields Present Based on Status
    Validates: Requirements 2.3, 2.5, 2.6
    
    Test that conditional fields are present based on request status.
    """
    # Arrange - Create a request with appropriate fields for the status
    user_id = 'test-user-123'
    email = 'teammanager@example.com'
    
    kwargs = {
        'requester_id': user_id,
        'requester_email': email,
        'boat_type': 'skiff',
        'status': status
    }
    
    # Add conditional fields based on status
    if status in ['accepted', 'paid']:
        kwargs['assignment_details'] = 'Boat #42, oars included, dock A'
        kwargs['accepted_at'] = datetime.utcnow().isoformat() + 'Z'
    
    if status == 'paid':
        kwargs['paid_at'] = datetime.utcnow().isoformat() + 'Z'
    
    if status == 'cancelled':
        kwargs['cancelled_at'] = datetime.utcnow().isoformat() + 'Z'
    
    create_rental_request(dynamodb_table, **kwargs)
    
    # Arrange - Create event
    event = {
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
    
    # Act
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    returned_requests = body['data']['rental_requests']
    assert len(returned_requests) > 0
    
    request = returned_requests[0]
    
    # Verify conditional fields are present when expected
    for field in conditional_fields:
        assert field in request, f"Field '{field}' must be present for status '{status}'"
        assert request[field] is not None, f"Field '{field}' must not be None for status '{status}'"
    
    # Verify status-specific logic
    if status == 'pending':
        # Pending requests should not have assignment_details, accepted_at, paid_at, or cancelled_at
        assert 'assignment_details' not in request or request.get('assignment_details') is None
        assert 'accepted_at' not in request or request.get('accepted_at') is None
        assert 'paid_at' not in request or request.get('paid_at') is None
        assert 'cancelled_at' not in request or request.get('cancelled_at') is None


def test_empty_list_when_no_requests(dynamodb_table, context):
    """
    Test that an empty list is returned when team manager has no requests
    """
    # Arrange - Create event for a team manager with no requests
    event = {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'new-user-999',
                    'email': 'newuser@example.com',
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
    assert body['data']['rental_requests'] == []
    assert body['data']['count'] == 0


def test_unauthorized_access_rejected(dynamodb_table, context):
    """
    Test that requests without authentication are rejected
    """
    # Arrange - event without authentication
    event = {
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


def test_multiple_statuses_in_list(dynamodb_table, context):
    """
    Test that requests with different statuses are all returned correctly
    """
    # Arrange - Create requests with different statuses
    user_id = 'test-user-123'
    email = 'teammanager@example.com'
    
    # Create pending request
    create_rental_request(dynamodb_table, user_id, email, status='pending')
    
    # Create accepted request
    create_rental_request(
        dynamodb_table, user_id, email, status='accepted',
        assignment_details='Boat #1',
        accepted_at=datetime.utcnow().isoformat() + 'Z'
    )
    
    # Create paid request
    create_rental_request(
        dynamodb_table, user_id, email, status='paid',
        assignment_details='Boat #2',
        accepted_at=datetime.utcnow().isoformat() + 'Z',
        paid_at=datetime.utcnow().isoformat() + 'Z'
    )
    
    # Create cancelled request
    create_rental_request(
        dynamodb_table, user_id, email, status='cancelled',
        cancelled_at=datetime.utcnow().isoformat() + 'Z'
    )
    
    # Arrange - Create event
    event = {
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
    
    # Act
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['count'] == 4
    
    # Verify all statuses are present
    statuses = [r['status'] for r in body['data']['rental_requests']]
    assert 'pending' in statuses
    assert 'accepted' in statuses
    assert 'paid' in statuses
    assert 'cancelled' in statuses
