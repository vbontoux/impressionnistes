"""
End-to-end test for admin rental request workflow.

This test validates the complete admin journey:
1. View all requests
2. Filter by status and boat_type
3. Accept request with assignment details
4. Update assignment details
5. Reject request

Feature: boat-rental-refactoring
"""

import pytest
import json
from datetime import datetime
from moto import mock_dynamodb
import boto3
from functions.rental.create_rental_request import lambda_handler as create_request
from functions.admin.list_rental_requests import lambda_handler as list_requests
from functions.admin.accept_rental_request import lambda_handler as accept_request
from functions.admin.update_assignment_details import lambda_handler as update_assignment
from functions.admin.reject_rental_request import lambda_handler as reject_request


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


def test_admin_complete_workflow(dynamodb_table, team_manager_context, admin_context):
    """
    Test the complete admin workflow for managing rental requests.
    
    Workflow:
    1. Create multiple rental requests (as team manager)
    2. Admin views all requests
    3. Admin filters by status
    4. Admin filters by boat_type
    5. Admin accepts a request
    6. Admin updates assignment details
    7. Admin rejects a request
    """
    
    # Step 1: Create multiple rental requests
    print("\n=== Step 1: Create Multiple Rental Requests ===")
    requests = []
    
    # Request 1: 4+ pending
    create_event_1 = {
        'body': json.dumps({
            'boat_type': '4+',
            'desired_weight_range': '70-85kg',
            'request_comment': 'Need a four for training'
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
    response_1 = create_request(create_event_1, None)
    request_1_id = json.loads(response_1['body'])['data']['rental_request_id']
    requests.append(('4+', 'pending', request_1_id))
    
    # Request 2: 8+ pending
    create_event_2 = {
        'body': json.dumps({
            'boat_type': '8+',
            'desired_weight_range': '75-90kg',
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
    response_2 = create_request(create_event_2, None)
    request_2_id = json.loads(response_2['body'])['data']['rental_request_id']
    requests.append(('8+', 'pending', request_2_id))
    
    # Request 3: skiff pending
    create_event_3 = {
        'body': json.dumps({
            'boat_type': 'skiff',
            'desired_weight_range': '75-80kg',
            'request_comment': 'Solo training'
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
    response_3 = create_request(create_event_3, None)
    request_3_id = json.loads(response_3['body'])['data']['rental_request_id']
    requests.append(('skiff', 'pending', request_3_id))
    
    print(f"✓ Created {len(requests)} rental requests")
    
    # Step 2: Admin views all requests
    print("\n=== Step 2: Admin Views All Requests ===")
    list_event = {
        'queryStringParameters': None,
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
    
    list_response = list_requests(list_event, None)
    assert list_response['statusCode'] == 200
    
    response_body = json.loads(list_response['body'])
    all_requests = response_body['data']
    assert all_requests['count'] >= 3
    
    print(f"✓ Admin sees {all_requests['count']} total requests")
    
    # Step 3: Admin filters by status (pending)
    print("\n=== Step 3: Admin Filters by Status ===")
    filter_status_event = {
        'queryStringParameters': {'status': 'pending'},
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
    
    filter_status_response = list_requests(filter_status_event, None)
    assert filter_status_response['statusCode'] == 200
    
    response_body = json.loads(filter_status_response['body'])
    pending_requests = response_body['data']
    assert pending_requests['count'] >= 3
    
    # Verify all returned requests have status 'pending'
    for req in pending_requests['rental_requests']:
        assert req['status'] == 'pending'
    
    print(f"✓ Found {pending_requests['count']} pending requests")
    
    # Step 4: Admin filters by boat_type (8+)
    print("\n=== Step 4: Admin Filters by Boat Type ===")
    filter_boat_event = {
        'queryStringParameters': {'boat_type': '8+'},
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
    
    filter_boat_response = list_requests(filter_boat_event, None)
    assert filter_boat_response['statusCode'] == 200
    
    response_body = json.loads(filter_boat_response['body'])
    eight_requests = response_body['data']
    assert eight_requests['count'] >= 1
    
    # Verify all returned requests have boat_type '8+'
    for req in eight_requests['rental_requests']:
        assert req['boat_type'] == '8+'
    
    print(f"✓ Found {eight_requests['count']} requests for 8+")
    
    # Step 5: Admin accepts a request
    print("\n=== Step 5: Admin Accepts Request ===")
    accept_event = {
        'pathParameters': {'id': request_1_id},
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
    
    print("✓ Request accepted with assignment details")
    
    # Step 6: Admin updates assignment details
    print("\n=== Step 6: Admin Updates Assignment Details ===")
    update_event = {
        'pathParameters': {'id': request_1_id},
        'body': json.dumps({
            'assignment_details': 'UPDATED: Boat #43, Oars in locker B2, Meet at dock 3 at 9am'
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
    
    update_response = update_assignment(update_event, None)
    assert update_response['statusCode'] == 200
    
    response_body = json.loads(update_response['body'])
    updated_request = response_body['data']
    assert updated_request['assignment_details'] == 'UPDATED: Boat #43, Oars in locker B2, Meet at dock 3 at 9am'
    assert updated_request['status'] == 'accepted'  # Status should remain accepted
    
    print("✓ Assignment details updated successfully")
    
    # Step 7: Admin rejects a request
    print("\n=== Step 7: Admin Rejects Request ===")
    reject_event = {
        'pathParameters': {'id': request_3_id},
        'body': json.dumps({
            'rejection_reason': 'No skiffs available for the requested date'
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
    
    reject_response = reject_request(reject_event, None)
    assert reject_response['statusCode'] == 200
    
    response_body = json.loads(reject_response['body'])
    rejected_request = response_body['data']
    assert rejected_request['status'] == 'cancelled'
    assert 'cancelled_at' in rejected_request
    assert rejected_request['cancelled_by'] == admin_context['user_id']
    assert rejected_request['rejection_reason'] == 'No skiffs available for the requested date'
    
    print("✓ Request rejected with reason")
    
    # Step 8: Verify final state
    print("\n=== Step 8: Verify Final State ===")
    final_list_response = list_requests(list_event, None)
    response_body = json.loads(final_list_response['body'])
    final_requests = response_body['data']['rental_requests']
    
    # Find our requests
    req1 = next((r for r in final_requests if r['rental_request_id'] == request_1_id), None)
    req3 = next((r for r in final_requests if r['rental_request_id'] == request_3_id), None)
    
    assert req1 is not None
    assert req1['status'] == 'accepted'
    assert 'UPDATED' in req1['assignment_details']
    
    assert req3 is not None
    assert req3['status'] == 'cancelled'
    assert req3['rejection_reason'] == 'No skiffs available for the requested date'
    
    print("✓ All admin operations verified")
    print("\n=== Admin Workflow Complete ===")


def test_admin_combined_filters(dynamodb_table, team_manager_context, admin_context):
    """
    Test admin filtering with combined status and boat_type filters.
    """
    
    # Create requests with different combinations
    print("\n=== Creating Test Requests ===")
    
    # Create 4+ pending
    create_event = {
        'body': json.dumps({
            'boat_type': '4+',
            'desired_weight_range': '70-85kg',
            'request_comment': 'Test request'
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
    response = create_request(create_event, None)
    request_id = json.loads(response['body'])['data']['rental_request_id']
    
    # Accept it
    accept_event = {
        'pathParameters': {'id': request_id},
        'body': json.dumps({'assignment_details': 'Boat #1'}),
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
    
    # Create another 4+ pending
    response2 = create_request(create_event, None)
    
    print("✓ Created test requests")
    
    # Test combined filter: status=accepted AND boat_type=4+
    print("\n=== Testing Combined Filters ===")
    filter_event = {
        'queryStringParameters': {
            'status': 'accepted',
            'boat_type': '4+'
        },
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
    
    filter_response = list_requests(filter_event, None)
    assert filter_response['statusCode'] == 200
    
    response_body = json.loads(filter_response['body'])
    filtered_requests = response_body['data']
    
    # Verify all results match both filters
    for req in filtered_requests['rental_requests']:
        assert req['status'] == 'accepted'
        assert req['boat_type'] == '4+'
    
    print(f"✓ Found {filtered_requests['count']} requests matching both filters")
    print("\n=== Combined Filter Test Complete ===")
