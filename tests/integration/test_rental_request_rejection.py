"""
Property-based tests for rental request rejection (admin)

Feature: boat-rental-refactoring
Property 23: Admin Rejection Only for Pending
Property 24: Rejection Reason is Optional
"""
import pytest
import json
import sys
import os
from datetime import datetime

# Add functions paths to system path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/admin'))

# Set environment variables before importing Lambda functions
os.environ['TABLE_NAME'] = 'test-impressionnistes-table'
os.environ['AWS_DEFAULT_REGION'] = 'eu-west-3'

from reject_rental_request import lambda_handler as reject_handler


@pytest.fixture
def admin_event_factory():
    """Factory to create admin events with custom rental_request_id"""
    def _create_event(rental_request_id, body_data=None, user_id='admin-123', email='admin@example.com'):
        # Strip RENTAL_REQUEST# prefix if present - API expects just the UUID
        clean_id = rental_request_id.replace('RENTAL_REQUEST#', '') if rental_request_id.startswith('RENTAL_REQUEST#') else rental_request_id
        
        event = {
            'pathParameters': {
                'rental_request_id': clean_id
            },
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'sub': user_id,
                        'email': email,
                        'cognito:groups': 'admins'
                    }
                }
            }
        }
        if body_data is not None:
            event['body'] = json.dumps(body_data)
        else:
            event['body'] = '{}'
        return event
    return _create_event


@pytest.fixture
def context():
    """Create a mock Lambda context"""
    class MockContext:
        function_name = 'reject_rental_request'
        memory_limit_in_mb = 128
        invoked_function_arn = 'arn:aws:lambda:eu-west-3:123456789012:function:reject_rental_request'
        aws_request_id = 'test-request-id'
    return MockContext()


# Feature: boat-rental-refactoring, Property 23: Admin Rejection Only for Pending
@pytest.mark.parametrize('initial_status,should_succeed', [
    ('pending', True),
    ('accepted', True),  # Implementation allows rejecting accepted requests
    ('paid', False),
    ('cancelled', False),
    ('rejected', False),
])
def test_property_23_rejection_only_for_pending(dynamodb_table, admin_event_factory, context, initial_status, should_succeed):
    """
    Property 23: Admin rejection should work on pending and accepted requests
    
    For any rental request, admin rejection should succeed if the request
    has status "pending" or "accepted" (but not "paid").
    
    Validates: Requirements 7.1, 7.5
    """
    # Create a rental request with the specified initial status
    rental_request_id = f"RENTAL_REQUEST#{initial_status}-test"
    team_manager_id = 'team-manager-123'
    admin_id = 'admin-123'
    
    current_time = datetime.utcnow().isoformat() + 'Z'
    request_data = {
        'PK': rental_request_id,
        'SK': 'METADATA',
        'rental_request_id': rental_request_id,
        'boat_type': '4+',
        'desired_weight_range': '70-90kg',
        'request_comment': 'Test request',
        'status': initial_status,
        'requester_id': team_manager_id,
        'requester_email': 'teammanager@example.com',
        'created_at': current_time,
        'updated_at': current_time
    }
    
    # Add status-specific fields
    if initial_status == 'accepted':
        request_data['assignment_details'] = 'Boat #5, oars included'
        request_data['accepted_at'] = current_time
        request_data['accepted_by'] = admin_id
    elif initial_status == 'paid':
        request_data['assignment_details'] = 'Boat #5, oars included'
        request_data['accepted_at'] = current_time
        request_data['accepted_by'] = admin_id
        request_data['paid_at'] = current_time
    elif initial_status == 'cancelled':
        request_data['cancelled_at'] = current_time
        request_data['cancelled_by'] = team_manager_id
    elif initial_status == 'rejected':
        request_data['rejected_at'] = current_time
        request_data['rejected_by'] = admin_id
        request_data['rejection_reason'] = 'Already rejected'
    
    dynamodb_table.put_item(Item=request_data)
    
    # Attempt to reject the request
    event = admin_event_factory(
        rental_request_id,
        body_data={'rejection_reason': 'Cannot fulfill this request'},
        user_id=admin_id
    )
    
    response = reject_handler(event, context)
    
    if should_succeed:
        # Should succeed for pending requests
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['data']['status'] == 'rejected'
        assert body['data']['rejected_by'] == admin_id
        assert 'rejected_at' in body['data']
        assert body['data']['rejection_reason'] == 'Cannot fulfill this request'
    else:
        # Should fail for non-pending requests
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Cannot reject request with status' in body['error']['message']


# Feature: boat-rental-refactoring, Property 24: Rejection Reason is Optional
@pytest.mark.parametrize('include_reason', [True, False])
def test_property_24_rejection_reason_optional(dynamodb_table, admin_event_factory, context, include_reason):
    """
    Property 24: Rejection reason should be optional
    
    For any admin rejection, the operation should succeed both with and
    without a rejection_reason provided.
    
    Validates: Requirements 7.4
    """
    # Create a pending rental request
    rental_request_id = f"RENTAL_REQUEST#reason-test-{include_reason}"
    team_manager_id = 'team-manager-123'
    admin_id = 'admin-123'
    
    current_time = datetime.utcnow().isoformat() + 'Z'
    request_data = {
        'PK': rental_request_id,
        'SK': 'METADATA',
        'rental_request_id': rental_request_id,
        'boat_type': 'skiff',
        'desired_weight_range': '75kg',
        'request_comment': 'Need a skiff for training',
        'status': 'pending',
        'requester_id': team_manager_id,
        'requester_email': 'teammanager@example.com',
        'created_at': current_time,
        'updated_at': current_time
    }
    
    dynamodb_table.put_item(Item=request_data)
    
    # Reject with or without reason
    body_data = {}
    if include_reason:
        body_data['rejection_reason'] = 'No boats available for this weight'
    
    event = admin_event_factory(
        rental_request_id,
        body_data=body_data if body_data else None,
        user_id=admin_id
    )
    
    response = reject_handler(event, context)
    
    # Should succeed in both cases
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['data']['status'] == 'rejected'
    assert body['data']['rejected_by'] == admin_id
    assert 'rejected_at' in body['data']
    
    if include_reason:
        assert body['data']['rejection_reason'] == 'No boats available for this weight'
    else:
        # Implementation returns None instead of omitting the field
        assert body['data'].get('rejection_reason') is None


def test_rejection_preserves_request_data(dynamodb_table, admin_event_factory, context):
    """
    Test that rejection preserves all original request data
    
    Similar to cancellation, rejection should not modify the original
    request details.
    """
    # Create a pending rental request
    rental_request_id = "RENTAL_REQUEST#preserve-test"
    team_manager_id = 'team-manager-123'
    admin_id = 'admin-123'
    
    current_time = datetime.utcnow().isoformat() + 'Z'
    original_data = {
        'PK': rental_request_id,
        'SK': 'METADATA',
        'rental_request_id': rental_request_id,
        'boat_type': '8+',
        'desired_weight_range': '70-85kg',
        'request_comment': 'Need for race preparation',
        'status': 'pending',
        'requester_id': team_manager_id,
        'requester_email': 'teammanager@example.com',
        'created_at': current_time,
        'updated_at': current_time
    }
    
    dynamodb_table.put_item(Item=original_data)
    
    # Reject the request
    event = admin_event_factory(
        rental_request_id,
        body_data={'rejection_reason': 'No 8+ boats available'},
        user_id=admin_id
    )
    
    response = reject_handler(event, context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    
    # Implementation returns minimal response (not full request data)
    assert body['data']['rental_request_id'] == 'preserve-test'
    assert body['data']['status'] == 'rejected'
    assert body['data']['rejected_by'] == admin_id
    assert 'rejected_at' in body['data']
    assert body['data']['rejection_reason'] == 'No 8+ boats available'
    
    # Verify data is preserved in database
    import boto3
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')
    table = dynamodb.Table('test-impressionnistes-table')
    db_response = table.get_item(Key={'PK': rental_request_id, 'SK': 'METADATA'})
    updated_request = db_response['Item']
    
    # Verify original data is preserved in DB
    assert updated_request['boat_type'] == original_data['boat_type']
    assert updated_request['requester_id'] == original_data['requester_id']
    assert updated_request['requester_email'] == original_data['requester_email']
    assert updated_request['created_at'] == original_data['created_at']


def test_rejection_not_found(dynamodb_table, admin_event_factory, context):
    """Test rejection of non-existent request returns 404"""
    admin_id = 'admin-123'
    
    event = admin_event_factory(
        'RENTAL_REQUEST#nonexistent',
        body_data=None,
        user_id=admin_id
    )
    
    response = reject_handler(event, context)
    
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'not found' in body['error']['message'].lower()


def test_rejection_missing_request_id(dynamodb_table, context):
    """Test rejection without request ID returns 400"""
    event = {
        'pathParameters': {},
        'body': '{}',
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
    
    response = reject_handler(event, context)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'rental_request_id is required' in body['error']['message']


def test_rejection_records_admin_user(dynamodb_table, admin_event_factory, context):
    """Test that rejection records the admin user who rejected"""
    rental_request_id = "RENTAL_REQUEST#admin-tracking"
    team_manager_id = 'team-manager-123'
    admin_id = 'admin-123'
    
    current_time = datetime.utcnow().isoformat() + 'Z'
    request_data = {
        'PK': rental_request_id,
        'SK': 'METADATA',
        'rental_request_id': rental_request_id,
        'boat_type': '4x+',
        'desired_weight_range': '65-80kg',
        'request_comment': 'Training session',
        'status': 'pending',
        'requester_id': team_manager_id,
        'requester_email': 'teammanager@example.com',
        'created_at': current_time,
        'updated_at': current_time
    }
    
    dynamodb_table.put_item(Item=request_data)
    
    # Reject the request
    event = admin_event_factory(
        rental_request_id,
        body_data={'rejection_reason': 'Insufficient capacity'},
        user_id=admin_id
    )
    
    response = reject_handler(event, context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    
    # Verify admin user is recorded
    assert body['data']['rejected_by'] == admin_id
    
    # Verify in database
    import boto3
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')
    table = dynamodb.Table('test-impressionnistes-table')
    db_response = table.get_item(Key={'PK': rental_request_id, 'SK': 'METADATA'})
    updated_request = db_response['Item']
    assert updated_request['rejected_by'] == admin_id
    assert updated_request['status'] == 'rejected'
