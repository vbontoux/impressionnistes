"""
Integration tests for admin payment endpoints

Tests verify that:
1. GET /admin/payments returns all payments with admin authentication
2. GET /admin/payments/analytics returns analytics with admin authentication
3. Non-admin users get 403 error
"""
import pytest
import json
from decimal import Decimal


@pytest.fixture
def multi_team_payments(dynamodb_table, test_team_manager_id, test_admin_id):
    """Create payment records for multiple team managers"""
    # Create payments for test team manager
    for i in range(2):
        payment = {
            'PK': f"TEAM#{test_team_manager_id}",
            'SK': f"PAYMENT#payment_{i:03d}",
            'payment_id': f'payment_{i:03d}',
            'team_manager_id': test_team_manager_id,
            'stripe_payment_intent_id': f'pi_test_{i:03d}',
            'amount': Decimal(str(50.00 * (i + 1))),
            'currency': 'EUR',
            'paid_at': f'2026-01-{15 + i:02d}T10:00:00Z',
            'boat_registration_ids': [f'boat_{i:03d}'],
            'stripe_receipt_url': f'https://stripe.com/receipt_{i}',
            'status': 'succeeded'
        }
        dynamodb_table.put_item(Item=payment)
    
    # Create payments for another team manager
    other_tm_id = 'other_team_manager'
    for i in range(2):
        payment = {
            'PK': f"TEAM#{other_tm_id}",
            'SK': f"PAYMENT#other_payment_{i:03d}",
            'payment_id': f'other_payment_{i:03d}',
            'team_manager_id': other_tm_id,
            'stripe_payment_intent_id': f'pi_other_{i:03d}',
            'amount': Decimal(str(75.00 * (i + 1))),
            'currency': 'EUR',
            'paid_at': f'2026-01-{17 + i:02d}T10:00:00Z',
            'boat_registration_ids': [f'other_boat_{i:03d}'],
            'stripe_receipt_url': f'https://stripe.com/receipt_other_{i}',
            'status': 'succeeded'
        }
        dynamodb_table.put_item(Item=payment)
    
    # Create profiles for team managers
    dynamodb_table.put_item(Item={
        'PK': f"TEAM#{test_team_manager_id}",
        'SK': 'PROFILE',
        'first_name': 'Test',
        'last_name': 'Manager',
        'email': 'test@example.com',
        'club_affiliation': 'Test Club'
    })
    
    dynamodb_table.put_item(Item={
        'PK': f"TEAM#{other_tm_id}",
        'SK': 'PROFILE',
        'first_name': 'Other',
        'last_name': 'Manager',
        'email': 'other@example.com',
        'club_affiliation': 'Other Club'
    })
    
    return {
        'test_tm_count': 2,
        'other_tm_count': 2,
        'total_count': 4
    }


def test_admin_list_all_payments(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_admin_id, multi_team_payments
):
    """Test GET /admin/payments returns all payments with admin authentication"""
    from admin.list_all_payments import lambda_handler
    
    # Create API Gateway event with admin user
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/payments',
        user_id=test_admin_id,
        groups=['admins']
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Verify response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'data' in body
    
    # Verify all payments are returned
    payments = body['data']['payments']
    assert len(payments) == 4
    
    # Verify payment structure includes team manager info
    for payment in payments:
        assert 'payment_id' in payment
        assert 'team_manager_id' in payment
        assert 'team_manager_name' in payment
        assert 'team_manager_email' in payment
        assert 'club_affiliation' in payment
        assert 'amount' in payment
        assert 'paid_at' in payment
    
    # Verify totals
    assert body['data']['total_count'] == 4
    assert body['data']['total_amount'] > 0


def test_admin_get_payment_analytics(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_admin_id, multi_team_payments
):
    """Test GET /admin/payments/analytics returns analytics with admin authentication"""
    from admin.get_payment_analytics import lambda_handler
    
    # Create API Gateway event with admin user
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/payments/analytics',
        user_id=test_admin_id,
        groups=['admins']
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Verify response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'data' in body
    
    data = body['data']
    
    # Verify analytics structure
    assert 'total_revenue' in data
    assert 'total_payments' in data
    assert 'total_boats_paid' in data
    assert 'total_team_managers' in data
    assert 'outstanding_balance' in data
    assert 'outstanding_boats' in data
    assert 'payment_timeline' in data
    assert 'top_team_managers' in data
    
    # Verify counts
    assert data['total_payments'] == 4
    assert data['total_team_managers'] == 2
    
    # Verify timeline is a list
    assert isinstance(data['payment_timeline'], list)
    
    # Verify top team managers is a list
    assert isinstance(data['top_team_managers'], list)


def test_non_admin_cannot_access_admin_payments(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_team_manager_id, multi_team_payments
):
    """Test that non-admin users get 403 error"""
    from admin.list_all_payments import lambda_handler
    
    # Create API Gateway event with team manager (not admin)
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/payments',
        user_id=test_team_manager_id
        # No 'admins' group
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Should return 403 Forbidden
    assert response['statusCode'] == 403
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'error' in body
