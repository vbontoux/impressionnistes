"""
End-to-end test for team manager rental request workflow.

This test validates the complete team manager journey:
1. Create rental request
2. View own requests
3. Cancel request
4. Pay for accepted request

Feature: boat-rental-refactoring
"""

import pytest
import json
from datetime import datetime
from moto import mock_dynamodb
import boto3
from functions.rental.create_rental_request import lambda_handler as create_request
from functions.rental.get_my_rental_requests import lambda_handler as get_my_requests
from functions.rental.cancel_rental_request import lambda_handler as cancel_request
from functions.rental.get_rentals_for_payment import lambda_handler as get_rentals_for_payment
from functions.admin.accept_rental_request import lambda_handler as accept_request


@pytest.fixture
def team_manager_context():
    """Context for team manager user."""
    return {
        'user_id': 'tm-test-001',
        'email': 'teammanager@test.com',
        'groups': ['team_managers']
    }


@pytest.fixture
def admin_context():
    """Context for admin user."""
    return {
        'user_id': 'admin-test-001',
        'email': 'admin@test.com',
        'groups': ['admins']
    }


def test_team_manager_complete_workflow(dynamodb_table, team_manager_context, admin_context):
    """
    Test the complete team manager workflow from request creation to payment.
    
    Workflow:
    1. Team manager creates a rental request
    2. Team manager views their requests
    3. Admin accepts the request
    4. Team manager views requests ready for payment
    5. Team manager completes payment
    6. Verify final state
    """
    
    # Step 1: Create rental request
    print("\n=== Step 1: Create Rental Request ===")
    create_event = {
        'body': json.dumps({
            'boat_type': '4+',
            'desired_weight_range': '70-85kg',
            'request_comment': 'Need a boat for our team training session'
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': team_manager_context['user_id'],
                    'email': team_manager_context['email'],
                    'cognito:groups': ','.join(team_manager_context['groups'])
                }
            }
        }
    }
    
    create_response = create_request(create_event, None)
    assert create_response['statusCode'] == 200
    
    response_body = json.loads(create_response['body'])
    created_request = response_body['data']
    rental_request_id = created_request['rental_request_id']
    
    print(f"✓ Created rental request: {rental_request_id}")
    assert created_request['status'] == 'pending'
    assert created_request['boat_type'] == '4+'
    assert created_request['requester_id'] == team_manager_context['user_id']
    
    # Step 2: View own requests
    print("\n=== Step 2: View Own Requests ===")
    view_event = {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': team_manager_context['user_id'],
                    'email': team_manager_context['email'],
                    'cognito:groups': ','.join(team_manager_context['groups'])
                }
            }
        }
    }
    
    view_response = get_my_requests(view_event, None)
    assert view_response['statusCode'] == 200
    
    response_body = json.loads(view_response['body'])
    my_requests = response_body['data']
    assert my_requests['count'] == 1
    assert my_requests['rental_requests'][0]['rental_request_id'] == rental_request_id
    assert my_requests['rental_requests'][0]['status'] == 'pending'
    
    print(f"✓ Found {my_requests['count']} request(s)")
    
    # Step 3: Admin accepts the request
    print("\n=== Step 3: Admin Accepts Request ===")
    accept_event = {
        'pathParameters': {
            'id': rental_request_id
        },
        'body': json.dumps({
            'assignment_details': 'Boat #42, Oars in locker A3, Meet at dock 2 at 8am'
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': admin_context['user_id'],
                    'email': admin_context['email'],
                    'cognito:groups': ','.join(admin_context['groups'])
                }
            }
        }
    }
    
    accept_response = accept_request(accept_event, None)
    assert accept_response['statusCode'] == 200
    
    response_body = json.loads(accept_response['body'])
    accepted_request = response_body['data']
    assert accepted_request['status'] == 'accepted'
    assert accepted_request['assignment_details'] == 'Boat #42, Oars in locker A3, Meet at dock 2 at 8am'
    assert 'accepted_at' in accepted_request
    assert accepted_request['accepted_by'] == admin_context['user_id']
    
    print("✓ Request accepted by admin")
    
    # Step 4: View requests ready for payment
    print("\n=== Step 4: View Requests Ready for Payment ===")
    payment_view_event = {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': team_manager_context['user_id'],
                    'email': team_manager_context['email'],
                    'cognito:groups': ','.join(team_manager_context['groups'])
                }
            }
        }
    }
    
    payment_view_response = get_rentals_for_payment(payment_view_event, None)
    assert payment_view_response['statusCode'] == 200
    
    response_body = json.loads(payment_view_response['body'])
    payment_requests = response_body['data']
    assert payment_requests['count'] == 1
    assert payment_requests['rental_requests'][0]['rental_request_id'] == rental_request_id
    assert payment_requests['rental_requests'][0]['status'] == 'accepted'
    assert 'pricing' in payment_requests['rental_requests'][0]
    
    pricing = payment_requests['rental_requests'][0]['pricing']
    assert pricing['rental_fee'] == 100.0  # 4+ = 5 seats * 20 EUR base price
    
    print(f"✓ Found request ready for payment: {pricing['rental_fee']} EUR")
    
    # Step 5: Complete payment (simulate payment by directly updating status)
    print("\n=== Step 5: Complete Payment ===")
    # In a real scenario, payment would go through Stripe webhook
    # For E2E testing, we directly update the rental request status
    from database import get_db_client
    db = get_db_client()
    current_time = datetime.utcnow().isoformat() + 'Z'
    db.update_item(
        pk=rental_request_id,
        sk='METADATA',
        updates={
            'status': 'paid',
            'paid_at': current_time,
            'updated_at': current_time
        }
    )
    
    print("✓ Payment completed")
    
    # Step 6: Verify final state
    print("\n=== Step 6: Verify Final State ===")
    final_view_response = get_my_requests(view_event, None)
    assert final_view_response['statusCode'] == 200
    
    response_body = json.loads(final_view_response['body'])
    final_requests = response_body['data']
    paid_request = final_requests['rental_requests'][0]
    
    assert paid_request['status'] == 'paid'
    assert 'paid_at' in paid_request
    assert paid_request['assignment_details'] == 'Boat #42, Oars in locker A3, Meet at dock 2 at 8am'
    
    print("✓ Request is now in 'paid' status")
    print("\n=== Workflow Complete ===")
    print(f"Final request state: {paid_request['status']}")


def test_team_manager_cancel_workflow(dynamodb_table, team_manager_context):
    """
    Test team manager cancelling their own request.
    
    Workflow:
    1. Create rental request
    2. View own requests
    3. Cancel the request
    4. Verify cancellation
    """
    
    # Step 1: Create rental request
    print("\n=== Step 1: Create Rental Request ===")
    create_event = {
        'body': json.dumps({
            'boat_type': 'skiff',
            'desired_weight_range': '75-80kg',
            'request_comment': 'Solo training session'
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': team_manager_context['user_id'],
                    'email': team_manager_context['email'],
                    'cognito:groups': ','.join(team_manager_context['groups'])
                }
            }
        }
    }
    
    create_response = create_request(create_event, None)
    assert create_response['statusCode'] == 200
    
    response_body = json.loads(create_response['body'])
    created_request = response_body['data']
    rental_request_id = created_request['rental_request_id']
    
    print(f"✓ Created rental request: {rental_request_id}")
    
    # Step 2: View own requests
    print("\n=== Step 2: View Own Requests ===")
    view_event = {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': team_manager_context['user_id'],
                    'email': team_manager_context['email'],
                    'cognito:groups': ','.join(team_manager_context['groups'])
                }
            }
        }
    }
    
    view_response = get_my_requests(view_event, None)
    assert view_response['statusCode'] == 200
    
    response_body = json.loads(view_response['body'])
    my_requests = response_body['data']
    assert my_requests['count'] == 1
    
    print(f"✓ Found {my_requests['count']} request(s)")
    
    # Step 3: Cancel the request
    print("\n=== Step 3: Cancel Request ===")
    cancel_event = {
        'pathParameters': {
            'id': rental_request_id
        },
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': team_manager_context['user_id'],
                    'email': team_manager_context['email'],
                    'cognito:groups': ','.join(team_manager_context['groups'])
                }
            }
        }
    }
    
    cancel_response = cancel_request(cancel_event, None)
    assert cancel_response['statusCode'] == 200
    
    response_body = json.loads(cancel_response['body'])
    cancelled_request = response_body['data']
    assert cancelled_request['status'] == 'cancelled'
    assert 'cancelled_at' in cancelled_request
    assert cancelled_request['cancelled_by'] == team_manager_context['user_id']
    
    print("✓ Request cancelled")
    
    # Step 4: Verify cancellation
    print("\n=== Step 4: Verify Cancellation ===")
    final_view_response = get_my_requests(view_event, None)
    assert final_view_response['statusCode'] == 200
    
    response_body = json.loads(final_view_response['body'])
    final_requests = response_body['data']
    cancelled_req = final_requests['rental_requests'][0]
    
    assert cancelled_req['status'] == 'cancelled'
    assert cancelled_req['boat_type'] == 'skiff'  # Original data preserved
    assert cancelled_req['request_comment'] == 'Solo training session'  # Original data preserved
    
    print("✓ Cancellation verified, original data preserved")
    print("\n=== Cancel Workflow Complete ===")


def test_team_manager_cannot_cancel_paid_request(dynamodb_table, team_manager_context, admin_context):
    """
    Test that team manager cannot cancel a paid request.
    """
    
    # Create and accept request
    create_event = {
        'body': json.dumps({
            'boat_type': '8+',
            'desired_weight_range': '70-90kg',
            'request_comment': 'Eight for competition'
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': team_manager_context['user_id'],
                    'email': team_manager_context['email'],
                    'cognito:groups': ','.join(team_manager_context['groups'])
                }
            }
        }
    }
    
    create_response = create_request(create_event, None)
    response_body = json.loads(create_response['body'])
    rental_request_id = response_body['data']['rental_request_id']
    
    # Admin accepts
    accept_event = {
        'pathParameters': {'id': rental_request_id},
        'body': json.dumps({'assignment_details': 'Boat #8'}),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': admin_context['user_id'],
                    'email': admin_context['email'],
                    'cognito:groups': ','.join(admin_context['groups'])
                }
            }
        }
    }
    accept_request(accept_event, None)
    
    # Complete payment (simulate by directly updating status)
    from database import get_db_client
    db = get_db_client()
    current_time = datetime.utcnow().isoformat() + 'Z'
    db.update_item(
        pk=rental_request_id,
        sk='METADATA',
        updates={
            'status': 'paid',
            'paid_at': current_time,
            'updated_at': current_time
        }
    )
    
    # Try to cancel paid request
    cancel_event = {
        'pathParameters': {'id': rental_request_id},
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': team_manager_context['user_id'],
                    'email': team_manager_context['email'],
                    'cognito:groups': ','.join(team_manager_context['groups'])
                }
            }
        }
    }
    
    cancel_response = cancel_request(cancel_event, None)
    assert cancel_response['statusCode'] == 400
    
    error = json.loads(cancel_response['body'])
    assert 'error' in error
    error_details = error['error']
    assert 'message' in error_details
    assert 'Cannot cancel' in error_details['message'] and 'paid' in error_details['message']
    
    print("✓ Correctly prevented cancellation of paid request")
