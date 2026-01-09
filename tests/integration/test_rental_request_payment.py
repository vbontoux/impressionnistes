"""
Integration tests for rental request payment functionality
Tests Lambda handlers with mock DynamoDB

Feature: boat-rental-refactoring
Properties tested:
- Property 16: Payment Only for Accepted Requests
- Property 17: Payment Transitions Status Correctly
- Property 19: Paid Requests are Immutable
"""
import json
import pytest
from datetime import datetime
from decimal import Decimal


# Feature: boat-rental-refactoring, Property 16: Payment Only for Accepted Requests
@pytest.mark.parametrize("status,should_succeed", [
    ('pending', False),
    ('accepted', True),
    ('paid', False),
    ('cancelled', False),
])
def test_property_16_payment_only_for_accepted_requests(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_team_manager_id, status, should_succeed
):
    """
    Property 16: Payment Only for Accepted Requests
    For any payment attempt, the operation should succeed if and only if 
    the rental request has status "accepted".
    
    Validates: Requirements 5.1, 5.6
    """
    from rental.get_rentals_for_payment import lambda_handler
    
    # Create rental request with specified status
    rental_request_id = f'RENTAL_REQUEST#payment-test-{status}'
    current_time = datetime.utcnow().isoformat() + 'Z'
    
    request_data = {
        'PK': rental_request_id,
        'SK': 'METADATA',
        'rental_request_id': rental_request_id,
        'boat_type': 'skiff',
        'desired_weight_range': '70-90kg',
        'request_comment': 'Test request',
        'status': status,
        'requester_id': test_team_manager_id,
        'requester_email': f'{test_team_manager_id}@test.com',
        'created_at': current_time,
        'updated_at': current_time
    }
    
    # Add status-specific fields
    if status in ['accepted', 'paid']:
        request_data['assignment_details'] = 'Boat #1, dock A'
        request_data['accepted_at'] = current_time
        request_data['accepted_by'] = 'admin-123'
    
    if status == 'paid':
        request_data['paid_at'] = current_time
        request_data['payment_id'] = 'payment-123'
    
    if status == 'cancelled':
        request_data['cancelled_at'] = current_time
        request_data['cancelled_by'] = test_team_manager_id
    
    dynamodb_table.put_item(Item=request_data)
    
    # Call get_rentals_for_payment
    event = mock_api_gateway_event(
        http_method='GET',
        path='/rental/requests-for-payment',
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    rental_requests = body['data']['rental_requests']
    
    if should_succeed:
        # Should find the accepted request
        assert len(rental_requests) == 1
        assert rental_requests[0]['status'] == 'accepted'
        assert 'pricing' in rental_requests[0]
    else:
        # Should not find requests with other statuses
        assert len(rental_requests) == 0


# Feature: boat-rental-refactoring, Property 17: Payment Transitions Status Correctly
@pytest.mark.parametrize("boat_type", [
    'skiff',
    '4-',
    '4+',
    '8+',
])
def test_property_17_payment_transitions_status_correctly(
    dynamodb_table, boat_type
):
    """
    Property 17: Payment Transitions Status Correctly
    For any rental request with status "accepted", completing payment should 
    change the status to "paid" and record paid_at timestamp.
    
    Validates: Requirements 5.2, 5.3
    """
    from payment.confirm_payment_webhook import update_rental_request_status_to_paid
    from database import get_db_client
    
    db = get_db_client()
    
    # Create accepted rental request
    rental_request_id = f'RENTAL_REQUEST#payment-transition-{boat_type}'
    current_time = datetime.utcnow().isoformat() + 'Z'
    
    request_data = {
        'PK': rental_request_id,
        'SK': 'METADATA',
        'rental_request_id': rental_request_id,
        'boat_type': boat_type,
        'desired_weight_range': '70-90kg',
        'request_comment': 'Test request',
        'status': 'accepted',
        'requester_id': 'user-123',
        'requester_email': 'user@test.com',
        'assignment_details': 'Boat #1, dock A',
        'created_at': current_time,
        'accepted_at': current_time,
        'accepted_by': 'admin-123',
        'updated_at': current_time
    }
    
    dynamodb_table.put_item(Item=request_data)
    
    # Process payment
    payment_id = 'payment-test-123'
    update_rental_request_status_to_paid(
        rental_request_ids=[rental_request_id],
        payment_id=payment_id,
        db=db
    )
    
    # Verify status transition
    updated_request = db.get_item(pk=rental_request_id, sk='METADATA')
    
    assert updated_request is not None
    assert updated_request['status'] == 'paid'
    assert updated_request['payment_id'] == payment_id
    assert 'paid_at' in updated_request
    assert updated_request['paid_at'] is not None
    
    # Verify original data preserved
    assert updated_request['boat_type'] == boat_type
    assert updated_request['requester_id'] == 'user-123'
    assert updated_request['assignment_details'] == 'Boat #1, dock A'
    assert updated_request['accepted_at'] == current_time


# Feature: boat-rental-refactoring, Property 19: Paid Requests are Immutable
@pytest.mark.parametrize("operation", [
    'cancel',
    'accept',
    'update_assignment',
])
def test_property_19_paid_requests_immutable(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_team_manager_id, test_admin_id, operation
):
    """
    Property 19: Paid Requests are Immutable
    For any rental request with status "paid", all modification attempts 
    (update, cancel, accept) should be rejected.
    
    Validates: Requirements 5.5
    """
    # Create paid rental request
    rental_request_id = f'RENTAL_REQUEST#immutable-test-{operation}'
    current_time = datetime.utcnow().isoformat() + 'Z'
    
    request_data = {
        'PK': rental_request_id,
        'SK': 'METADATA',
        'rental_request_id': rental_request_id,
        'boat_type': 'skiff',
        'desired_weight_range': '70-90kg',
        'request_comment': 'Test request',
        'status': 'paid',
        'requester_id': test_team_manager_id,
        'requester_email': f'{test_team_manager_id}@test.com',
        'assignment_details': 'Boat #1, dock A',
        'created_at': current_time,
        'accepted_at': current_time,
        'accepted_by': 'admin-123',
        'paid_at': current_time,
        'payment_id': 'payment-123',
        'updated_at': current_time
    }
    
    dynamodb_table.put_item(Item=request_data)
    
    # Attempt modification based on operation
    if operation == 'cancel':
        from rental.cancel_rental_request import lambda_handler
        event = mock_api_gateway_event(
            http_method='DELETE',
            path=f'/rental/request/{rental_request_id}',
            path_parameters={'id': rental_request_id},
            user_id=test_team_manager_id
        )
        response = lambda_handler(event, mock_lambda_context)
        
    elif operation == 'accept':
        from admin.accept_rental_request import lambda_handler
        event = mock_api_gateway_event(
            http_method='PUT',
            path=f'/admin/rental-requests/{rental_request_id}/accept',
            path_parameters={'id': rental_request_id},
            body=json.dumps({'assignment_details': 'New assignment'}),
            user_id=test_admin_id,
            groups=['admins']
        )
        response = lambda_handler(event, mock_lambda_context)
        
    elif operation == 'update_assignment':
        from admin.update_assignment_details import lambda_handler
        event = mock_api_gateway_event(
            http_method='PUT',
            path=f'/admin/rental-requests/{rental_request_id}/assignment',
            path_parameters={'id': rental_request_id},
            body=json.dumps({'assignment_details': 'Updated assignment'}),
            user_id=test_admin_id,
            groups=['admins']
        )
        response = lambda_handler(event, mock_lambda_context)
    
    # All operations should fail
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'paid' in body['error']['message'].lower()


def test_get_rentals_for_payment_includes_pricing(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_team_manager_id
):
    """
    Test that get_rentals_for_payment includes pricing information
    """
    from rental.get_rentals_for_payment import lambda_handler
    
    # Create accepted rental request
    rental_request_id = 'RENTAL_REQUEST#pricing-test'
    current_time = datetime.utcnow().isoformat() + 'Z'
    
    request_data = {
        'PK': rental_request_id,
        'SK': 'METADATA',
        'rental_request_id': rental_request_id,
        'boat_type': '4-',
        'desired_weight_range': '70-90kg',
        'request_comment': 'Test request',
        'status': 'accepted',
        'requester_id': test_team_manager_id,
        'requester_email': f'{test_team_manager_id}@test.com',
        'assignment_details': 'Boat #1, dock A',
        'created_at': current_time,
        'accepted_at': current_time,
        'accepted_by': 'admin-123',
        'updated_at': current_time
    }
    
    dynamodb_table.put_item(Item=request_data)
    
    # Call get_rentals_for_payment
    event = mock_api_gateway_event(
        http_method='GET',
        path='/rental/requests-for-payment',
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    rental_requests = body['data']['rental_requests']
    assert len(rental_requests) == 1
    
    request = rental_requests[0]
    assert 'pricing' in request
    assert 'rental_fee' in request['pricing']
    assert 'total' in request['pricing']
    assert 'currency' in request['pricing']
    assert request['pricing']['currency'] == 'EUR'
    assert request['pricing']['rental_fee'] > 0


def test_payment_only_for_own_requests(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_team_manager_id
):
    """
    Test that team managers can only see their own accepted requests for payment
    """
    from rental.get_rentals_for_payment import lambda_handler
    
    current_time = datetime.utcnow().isoformat() + 'Z'
    
    # Create accepted request for this team manager
    own_request_id = 'RENTAL_REQUEST#own-request'
    dynamodb_table.put_item(Item={
        'PK': own_request_id,
        'SK': 'METADATA',
        'rental_request_id': own_request_id,
        'boat_type': 'skiff',
        'desired_weight_range': '70-90kg',
        'request_comment': 'Own request',
        'status': 'accepted',
        'requester_id': test_team_manager_id,
        'requester_email': f'{test_team_manager_id}@test.com',
        'assignment_details': 'Boat #1',
        'created_at': current_time,
        'accepted_at': current_time,
        'accepted_by': 'admin-123',
        'updated_at': current_time
    })
    
    # Create accepted request for another team manager
    other_request_id = 'RENTAL_REQUEST#other-request'
    dynamodb_table.put_item(Item={
        'PK': other_request_id,
        'SK': 'METADATA',
        'rental_request_id': other_request_id,
        'boat_type': '4-',
        'desired_weight_range': '75-85kg',
        'request_comment': 'Other request',
        'status': 'accepted',
        'requester_id': 'other-user-456',
        'requester_email': 'other@test.com',
        'assignment_details': 'Boat #2',
        'created_at': current_time,
        'accepted_at': current_time,
        'accepted_by': 'admin-123',
        'updated_at': current_time
    })
    
    # Call get_rentals_for_payment
    event = mock_api_gateway_event(
        http_method='GET',
        path='/rental/requests-for-payment',
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    rental_requests = body['data']['rental_requests']
    assert len(rental_requests) == 1
    assert rental_requests[0]['rental_request_id'] == own_request_id
    assert rental_requests[0]['requester_id'] == test_team_manager_id
