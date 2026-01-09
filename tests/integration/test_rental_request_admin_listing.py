"""
Integration tests for admin rental request listing and filtering
Tests Properties 9, 10, and 11 from the boat-rental-refactoring design
"""
import pytest
import sys
import os
import json
from datetime import datetime, timedelta

# Add functions paths to system path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/admin'))

# Set environment variables before importing Lambda functions
os.environ['TABLE_NAME'] = 'test-impressionnistes-table'
os.environ['AWS_DEFAULT_REGION'] = 'eu-west-3'

from list_rental_requests import lambda_handler


@pytest.fixture
def admin_event():
    """Create a mock API Gateway event for an admin"""
    return {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'admin-user-123',
                    'email': 'admin@example.com',
                    'cognito:groups': 'admins'
                }
            }
        },
        'queryStringParameters': None
    }


@pytest.fixture
def context():
    """Create a mock Lambda context"""
    class MockContext:
        function_name = 'list_rental_requests'
        memory_limit_in_mb = 128
        invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:list_rental_requests'
        aws_request_id = 'test-request-id'
    
    return MockContext()


def create_rental_request(dynamodb_table, requester_id, requester_email, boat_type='skiff', 
                         status='pending', created_at=None, assignment_details=None,
                         accepted_at=None, accepted_by=None, paid_at=None, 
                         cancelled_at=None, cancelled_by=None, rejection_reason=None):
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
    if accepted_by:
        item['accepted_by'] = accepted_by
    if paid_at:
        item['paid_at'] = paid_at
    if cancelled_at:
        item['cancelled_at'] = cancelled_at
    if cancelled_by:
        item['cancelled_by'] = cancelled_by
    if rejection_reason:
        item['rejection_reason'] = rejection_reason
    
    dynamodb_table.put_item(Item=item)
    return rental_request_id


# Feature: boat-rental-refactoring, Property 9: Admin Sees All Requests
# For any admin querying rental requests without filters, the returned list should
# contain requests from all team managers.


@pytest.mark.parametrize("num_team_managers,requests_per_manager", [
    (2, 1),
    (3, 2),
    (5, 3),
    (1, 5),
])
def test_property_9_admin_sees_all_requests(dynamodb_table, admin_event, context, 
                                           num_team_managers, requests_per_manager):
    """
    Property 9: Admin Sees All Requests
    Validates: Requirements 3.1
    
    Test that admins see all rental requests from all team managers when no filters are applied.
    """
    # Arrange - Create requests from multiple team managers
    all_request_ids = []
    team_manager_ids = []
    
    for tm_index in range(num_team_managers):
        user_id = f'team-manager-{tm_index}'
        email = f'tm{tm_index}@example.com'
        team_manager_ids.append(user_id)
        
        for req_index in range(requests_per_manager):
            request_id = create_rental_request(
                dynamodb_table,
                user_id,
                email,
                boat_type='skiff' if req_index % 2 == 0 else '4-',
                status='pending'
            )
            all_request_ids.append(request_id)
    
    # Act - Admin queries without filters
    response = lambda_handler(admin_event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    returned_requests = body['data']['rental_requests']
    expected_count = num_team_managers * requests_per_manager
    
    assert body['data']['count'] == expected_count, \
        f"Admin should see all {expected_count} requests"
    assert len(returned_requests) == expected_count
    
    # Verify all requests are returned
    returned_ids = [r['rental_request_id'] for r in returned_requests]
    for request_id in all_request_ids:
        assert request_id in returned_ids, \
            "Admin should see requests from all team managers"
    
    # Verify requests from all team managers are present
    returned_requester_ids = set(r['requester_id'] for r in returned_requests)
    for tm_id in team_manager_ids:
        assert tm_id in returned_requester_ids, \
            f"Admin should see requests from team manager {tm_id}"
    
    # Verify requester information is included
    for request in returned_requests:
        assert 'requester_id' in request, "Admin view must include requester_id"
        assert 'requester_email' in request, "Admin view must include requester_email"
        assert request['requester_id'] is not None
        assert request['requester_email'] is not None


# Feature: boat-rental-refactoring, Property 10: Status Filtering Works Correctly
# For any admin query with a status filter, all returned requests should have that
# exact status, and no requests with that status should be excluded.


@pytest.mark.parametrize("filter_status,num_matching,num_non_matching", [
    ('pending', 3, 2),
    ('accepted', 2, 3),
    ('paid', 1, 4),
    ('cancelled', 2, 2),
])
def test_property_10_status_filtering(dynamodb_table, admin_event, context,
                                     filter_status, num_matching, num_non_matching):
    """
    Property 10: Status Filtering Works Correctly
    Validates: Requirements 3.3
    
    Test that status filtering returns only requests with the specified status.
    """
    # Arrange - Create requests with matching and non-matching statuses
    matching_request_ids = []
    non_matching_request_ids = []
    
    # Create requests with the filter status
    for i in range(num_matching):
        request_id = create_rental_request(
            dynamodb_table,
            f'user-{i}',
            f'user{i}@example.com',
            boat_type='skiff',
            status=filter_status,
            assignment_details='Boat #1' if filter_status in ['accepted', 'paid'] else None,
            accepted_at=datetime.utcnow().isoformat() + 'Z' if filter_status in ['accepted', 'paid'] else None,
            paid_at=datetime.utcnow().isoformat() + 'Z' if filter_status == 'paid' else None,
            cancelled_at=datetime.utcnow().isoformat() + 'Z' if filter_status == 'cancelled' else None
        )
        matching_request_ids.append(request_id)
    
    # Create requests with different statuses
    other_statuses = [s for s in ['pending', 'accepted', 'paid', 'cancelled'] if s != filter_status]
    for i in range(num_non_matching):
        other_status = other_statuses[i % len(other_statuses)]
        request_id = create_rental_request(
            dynamodb_table,
            f'other-user-{i}',
            f'other{i}@example.com',
            boat_type='4-',
            status=other_status,
            assignment_details='Boat #2' if other_status in ['accepted', 'paid'] else None,
            accepted_at=datetime.utcnow().isoformat() + 'Z' if other_status in ['accepted', 'paid'] else None,
            paid_at=datetime.utcnow().isoformat() + 'Z' if other_status == 'paid' else None,
            cancelled_at=datetime.utcnow().isoformat() + 'Z' if other_status == 'cancelled' else None
        )
        non_matching_request_ids.append(request_id)
    
    # Act - Admin queries with status filter
    event = admin_event.copy()
    event['queryStringParameters'] = {'status': filter_status}
    
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    returned_requests = body['data']['rental_requests']
    assert body['data']['count'] == num_matching, \
        f"Should return exactly {num_matching} requests with status '{filter_status}'"
    assert len(returned_requests) == num_matching
    
    # Verify all returned requests have the filter status
    for request in returned_requests:
        assert request['status'] == filter_status, \
            f"All returned requests must have status '{filter_status}'"
    
    # Verify all matching requests are included
    returned_ids = [r['rental_request_id'] for r in returned_requests]
    for request_id in matching_request_ids:
        assert request_id in returned_ids, \
            f"All requests with status '{filter_status}' must be included"
    
    # Verify non-matching requests are excluded
    for request_id in non_matching_request_ids:
        assert request_id not in returned_ids, \
            f"Requests with other statuses must be excluded"


# Feature: boat-rental-refactoring, Property 11: Boat Type Filtering Works Correctly
# For any admin query with a boat_type filter, all returned requests should have that
# exact boat_type, and no requests with that boat_type should be excluded.


@pytest.mark.parametrize("filter_boat_type,num_matching,num_non_matching", [
    ('skiff', 3, 2),
    ('4-', 2, 3),
    ('4+', 1, 4),
    ('8+', 2, 2),
])
def test_property_11_boat_type_filtering(dynamodb_table, admin_event, context,
                                        filter_boat_type, num_matching, num_non_matching):
    """
    Property 11: Boat Type Filtering Works Correctly
    Validates: Requirements 3.4
    
    Test that boat_type filtering returns only requests with the specified boat type.
    """
    # Arrange - Create requests with matching and non-matching boat types
    matching_request_ids = []
    non_matching_request_ids = []
    
    # Create requests with the filter boat type
    for i in range(num_matching):
        request_id = create_rental_request(
            dynamodb_table,
            f'user-{i}',
            f'user{i}@example.com',
            boat_type=filter_boat_type,
            status='pending'
        )
        matching_request_ids.append(request_id)
    
    # Create requests with different boat types
    other_boat_types = [bt for bt in ['skiff', '4-', '4+', '4x-', '4x+', '8+', '8x+'] 
                       if bt != filter_boat_type]
    for i in range(num_non_matching):
        other_boat_type = other_boat_types[i % len(other_boat_types)]
        request_id = create_rental_request(
            dynamodb_table,
            f'other-user-{i}',
            f'other{i}@example.com',
            boat_type=other_boat_type,
            status='pending'
        )
        non_matching_request_ids.append(request_id)
    
    # Act - Admin queries with boat_type filter
    event = admin_event.copy()
    event['queryStringParameters'] = {'boat_type': filter_boat_type}
    
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    returned_requests = body['data']['rental_requests']
    assert body['data']['count'] == num_matching, \
        f"Should return exactly {num_matching} requests with boat_type '{filter_boat_type}'"
    assert len(returned_requests) == num_matching
    
    # Verify all returned requests have the filter boat type
    for request in returned_requests:
        assert request['boat_type'] == filter_boat_type, \
            f"All returned requests must have boat_type '{filter_boat_type}'"
    
    # Verify all matching requests are included
    returned_ids = [r['rental_request_id'] for r in returned_requests]
    for request_id in matching_request_ids:
        assert request_id in returned_ids, \
            f"All requests with boat_type '{filter_boat_type}' must be included"
    
    # Verify non-matching requests are excluded
    for request_id in non_matching_request_ids:
        assert request_id not in returned_ids, \
            f"Requests with other boat types must be excluded"


def test_combined_status_and_boat_type_filtering(dynamodb_table, admin_event, context):
    """
    Test that both status and boat_type filters can be applied together
    """
    # Arrange - Create various requests
    # Matching both filters
    matching_id = create_rental_request(
        dynamodb_table, 'user-1', 'user1@example.com',
        boat_type='skiff', status='pending'
    )
    
    # Matching boat_type only
    boat_only_id = create_rental_request(
        dynamodb_table, 'user-2', 'user2@example.com',
        boat_type='skiff', status='accepted',
        assignment_details='Boat #1',
        accepted_at=datetime.utcnow().isoformat() + 'Z'
    )
    
    # Matching status only
    status_only_id = create_rental_request(
        dynamodb_table, 'user-3', 'user3@example.com',
        boat_type='4-', status='pending'
    )
    
    # Matching neither
    neither_id = create_rental_request(
        dynamodb_table, 'user-4', 'user4@example.com',
        boat_type='8+', status='paid',
        assignment_details='Boat #2',
        accepted_at=datetime.utcnow().isoformat() + 'Z',
        paid_at=datetime.utcnow().isoformat() + 'Z'
    )
    
    # Act - Admin queries with both filters
    event = admin_event.copy()
    event['queryStringParameters'] = {
        'status': 'pending',
        'boat_type': 'skiff'
    }
    
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    returned_requests = body['data']['rental_requests']
    assert body['data']['count'] == 1, "Should return only requests matching both filters"
    
    returned_ids = [r['rental_request_id'] for r in returned_requests]
    assert matching_id in returned_ids, "Request matching both filters must be included"
    assert boat_only_id not in returned_ids, "Request matching only boat_type must be excluded"
    assert status_only_id not in returned_ids, "Request matching only status must be excluded"
    assert neither_id not in returned_ids, "Request matching neither filter must be excluded"


def test_invalid_status_filter_rejected(dynamodb_table, admin_event, context):
    """
    Test that invalid status filter values are rejected
    """
    # Act - Admin queries with invalid status
    event = admin_event.copy()
    event['queryStringParameters'] = {'status': 'invalid_status'}
    
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'Invalid status' in body['error']['details']


def test_invalid_boat_type_filter_rejected(dynamodb_table, admin_event, context):
    """
    Test that invalid boat_type filter values are rejected
    """
    # Act - Admin queries with invalid boat_type
    event = admin_event.copy()
    event['queryStringParameters'] = {'boat_type': 'invalid_boat'}
    
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'Invalid boat_type' in body['error']['details']


def test_empty_list_when_no_matching_requests(dynamodb_table, admin_event, context):
    """
    Test that an empty list is returned when no requests match the filters
    """
    # Arrange - Create some requests that won't match
    create_rental_request(
        dynamodb_table, 'user-1', 'user1@example.com',
        boat_type='skiff', status='pending'
    )
    
    # Act - Admin queries with filters that don't match
    event = admin_event.copy()
    event['queryStringParameters'] = {'status': 'paid'}
    
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
        'requestContext': {},
        'queryStringParameters': None
    }
    
    # Act
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 401
    body = json.loads(response['body'])
    assert body['success'] is False


def test_non_admin_rejected(dynamodb_table, context):
    """
    Test that users without admin role are rejected
    """
    # Arrange - user without admins group
    event = {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'test-user-123',
                    'email': 'user@example.com',
                    'cognito:groups': 'team_managers'
                }
            }
        },
        'queryStringParameters': None
    }
    
    # Act
    response = lambda_handler(event, context)
    
    # Assert
    assert response['statusCode'] == 403
    body = json.loads(response['body'])
    assert body['success'] is False


def test_admin_sees_all_fields_including_admin_specific(dynamodb_table, admin_event, context):
    """
    Test that admin view includes admin-specific fields like accepted_by, cancelled_by, rejection_reason
    """
    # Arrange - Create requests with admin-specific fields
    admin_id = 'admin-123'
    
    # Accepted request
    create_rental_request(
        dynamodb_table, 'user-1', 'user1@example.com',
        boat_type='skiff', status='accepted',
        assignment_details='Boat #1',
        accepted_at=datetime.utcnow().isoformat() + 'Z',
        accepted_by=admin_id
    )
    
    # Rejected request
    create_rental_request(
        dynamodb_table, 'user-2', 'user2@example.com',
        boat_type='4-', status='cancelled',
        cancelled_at=datetime.utcnow().isoformat() + 'Z',
        cancelled_by=admin_id,
        rejection_reason='Insufficient inventory'
    )
    
    # Act
    response = lambda_handler(admin_event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    returned_requests = body['data']['rental_requests']
    assert len(returned_requests) == 2
    
    # Find the accepted request
    accepted_request = next(r for r in returned_requests if r['status'] == 'accepted')
    assert 'accepted_by' in accepted_request
    assert accepted_request['accepted_by'] == admin_id
    
    # Find the cancelled request
    cancelled_request = next(r for r in returned_requests if r['status'] == 'cancelled')
    assert 'cancelled_by' in cancelled_request
    assert cancelled_request['cancelled_by'] == admin_id
    assert 'rejection_reason' in cancelled_request
    assert cancelled_request['rejection_reason'] == 'Insufficient inventory'


def test_requests_sorted_by_created_at_descending(dynamodb_table, admin_event, context):
    """
    Test that admin view also sorts requests by created_at descending (Property 6)
    """
    # Arrange - Create requests with different timestamps
    base_time = datetime.utcnow()
    request_times = []
    
    for i in range(3):
        created_at = (base_time - timedelta(hours=i)).isoformat() + 'Z'
        request_times.append(created_at)
        create_rental_request(
            dynamodb_table,
            f'user-{i}',
            f'user{i}@example.com',
            boat_type='skiff',
            status='pending',
            created_at=created_at
        )
    
    # Act
    response = lambda_handler(admin_event, context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    returned_requests = body['data']['rental_requests']
    returned_times = [r['created_at'] for r in returned_requests]
    expected_times = sorted(request_times, reverse=True)
    
    assert returned_times == expected_times, "Requests must be sorted by created_at descending"
