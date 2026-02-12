"""
Integration tests for payment history endpoints

Tests verify that:
1. GET /payment/history returns payment list with authentication
2. GET /payment/summary returns payment summary with authentication
3. Team managers can only see their own payments (access control)
"""
import pytest
import json
from decimal import Decimal
from datetime import datetime


@pytest.fixture
def payment_records(dynamodb_table, test_team_manager_id):
    """Create test payment records"""
    payments = []
    
    # Create 3 payment records
    for i in range(3):
        payment = {
            'PK': f"TEAM#{test_team_manager_id}",
            'SK': f"PAYMENT#payment_{i:03d}",
            'payment_id': f'payment_{i:03d}',
            'stripe_payment_intent_id': f'pi_test_{i:03d}',
            'amount': Decimal(str(50.00 * (i + 1))),
            'currency': 'EUR',
            'paid_at': f'2026-01-{15 + i:02d}T10:00:00Z',
            'boat_registration_ids': [f'boat_{i:03d}'],
            'stripe_receipt_url': f'https://stripe.com/receipt_{i}',
            'status': 'succeeded'
        }
        dynamodb_table.put_item(Item=payment)
        payments.append(payment)
    
    return payments


@pytest.fixture
def unpaid_boats(dynamodb_table, test_team_manager_id):
    """Create unpaid boat registrations"""
    boats = []
    
    # Create 2 unpaid boats
    for i in range(2):
        boat = {
            'PK': f"TEAM#{test_team_manager_id}",
            'SK': f"BOAT#unpaid_boat_{i:03d}",
            'boat_registration_id': f'unpaid_boat_{i:03d}',
            'event_type': 'Course',
            'boat_type': '4+',
            'registration_status': 'complete',
            'pricing': {
                'total': Decimal('50.00'),
                'base_price': Decimal('40.00'),
                'additional_fees': Decimal('10.00')
            }
        }
        dynamodb_table.put_item(Item=boat)
        boats.append(boat)
    
    return boats


def test_get_payment_history_with_authentication(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_team_manager_id, payment_records
):
    """Test GET /payment/history returns payment list with authentication"""
    from payment.list_payments import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='GET',
        path='/payment/history',
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Verify response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'data' in body
    assert 'payments' in body['data']
    assert 'summary' in body['data']
    
    # Verify payments are returned
    payments = body['data']['payments']
    assert len(payments) == 3
    
    # Verify payment structure
    for payment in payments:
        assert 'payment_id' in payment
        assert 'amount' in payment
        assert 'paid_at' in payment
        assert 'boat_count' in payment
    
    # Verify summary
    summary = body['data']['summary']
    assert 'total_payments' in summary
    assert 'total_amount' in summary
    assert summary['total_payments'] == 3


def test_get_payment_summary_with_authentication(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_team_manager_id, payment_records, unpaid_boats
):
    """Test GET /payment/summary returns payment summary with authentication"""
    from payment.get_payment_summary import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='GET',
        path='/payment/summary',
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Verify response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'data' in body
    
    # Verify paid section
    assert 'paid' in body['data']
    paid = body['data']['paid']
    assert 'total_amount' in paid
    assert 'payment_count' in paid
    assert 'boat_count' in paid
    assert paid['payment_count'] == 3
    
    # Verify outstanding section
    assert 'outstanding' in body['data']
    outstanding = body['data']['outstanding']
    assert 'total_amount' in outstanding
    assert 'boat_count' in outstanding
    assert 'boats' in outstanding
    assert outstanding['boat_count'] == 2


def test_access_control_team_manager_only_sees_own_payments(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_team_manager_id, payment_records
):
    """Test that team manager can only see their own payments"""
    # Create another team manager with payments
    other_team_manager_id = 'other_team_manager'
    other_payment = {
        'PK': f"TEAM#{other_team_manager_id}",
        'SK': 'PAYMENT#other_payment',
        'payment_id': 'other_payment',
        'stripe_payment_intent_id': 'pi_other',
        'amount': Decimal('100.00'),
        'currency': 'EUR',
        'paid_at': '2026-01-20T10:00:00Z',
        'boat_registration_ids': ['other_boat'],
        'stripe_receipt_url': 'https://stripe.com/receipt_other',
        'status': 'succeeded'
    }
    dynamodb_table.put_item(Item=other_payment)
    
    from payment.list_payments import lambda_handler
    
    # Team manager requests their payments
    event = mock_api_gateway_event(
        http_method='GET',
        path='/payment/history',
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Verify response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    payments = body['data']['payments']
    
    # Verify only own payments are returned
    assert len(payments) == 3
    for payment in payments:
        assert payment['payment_id'] in ['payment_000', 'payment_001', 'payment_002']
        assert payment['payment_id'] != 'other_payment'


def test_payment_history_without_authentication_fails(
    mock_api_gateway_event, mock_lambda_context
):
    """Test that payment history requires authentication"""
    from payment.list_payments import lambda_handler
    
    # Create event without authentication
    event = mock_api_gateway_event(
        http_method='GET',
        path='/payment/history'
    )
    # Remove authorization
    event['requestContext']['authorizer'] = {}
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Should return error (401 or 403)
    assert response['statusCode'] in [401, 403]



def test_get_payment_invoice_returns_pdf(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_team_manager_id, payment_records
):
    """Test GET /payment/invoice/{id} returns PDF (1 test case)"""
    from payment.get_payment_invoice import lambda_handler
    import base64
    
    # Create team manager profile
    team_manager = {
        'PK': f"USER#{test_team_manager_id}",
        'SK': 'PROFILE',
        'user_id': test_team_manager_id,
        'first_name': 'John',
        'last_name': 'Doe',
        'club_affiliation': 'Test Club',
        'email': 'john@example.com'
    }
    dynamodb_table.put_item(Item=team_manager)
    
    # Create boat for the payment
    boat = {
        'PK': f"TEAM#{test_team_manager_id}",
        'SK': 'BOAT#boat_000',
        'boat_registration_id': 'boat_000',
        'event_type': 'Course',
        'boat_type': '4+',
        'locked_pricing': {
            'total': Decimal('50.00'),
            'base_price': Decimal('40.00'),
            'additional_fees': Decimal('10.00')
        }
    }
    dynamodb_table.put_item(Item=boat)
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='GET',
        path='/payment/invoice/payment_000',
        user_id=test_team_manager_id
    )
    event['pathParameters'] = {'payment_id': 'payment_000'}
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Verify response
    assert response['statusCode'] == 200
    assert response['headers']['Content-Type'] == 'text/plain; charset=utf-8'
    assert 'Content-Disposition' in response['headers']
    assert 'invoice-payment-payment_000' in response['headers']['Content-Disposition']
    # Text invoices are not base64 encoded
    assert response.get('isBase64Encoded', False) is False
    
    # Verify text content contains key information
    invoice_text = response['body']
    assert 'Course des Impressionnistes' in invoice_text
    assert 'payment_000' in invoice_text
    assert '50.00' in invoice_text  # Amount


def test_access_control_team_manager_can_only_download_own_invoices(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_team_manager_id
):
    """Test access control - team manager can only download own invoices (1 test case)"""
    from payment.get_payment_invoice import lambda_handler
    
    # Create another team manager with a payment
    other_team_manager_id = 'other_team_manager'
    other_payment = {
        'PK': f"TEAM#{other_team_manager_id}",
        'SK': 'PAYMENT#other_payment',
        'payment_id': 'other_payment',
        'stripe_payment_intent_id': 'pi_other',
        'amount': Decimal('100.00'),
        'currency': 'EUR',
        'paid_at': '2026-01-20T10:00:00Z',
        'boat_registration_ids': ['other_boat'],
        'stripe_receipt_url': 'https://stripe.com/receipt_other',
        'status': 'succeeded'
    }
    dynamodb_table.put_item(Item=other_payment)
    
    # Team manager tries to access another team manager's payment invoice
    event = mock_api_gateway_event(
        http_method='GET',
        path='/payment/invoice/other_payment',
        user_id=test_team_manager_id
    )
    event['pathParameters'] = {'payment_id': 'other_payment'}
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Should return 404 (payment not found for this team manager)
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'not found' in body['error']['message'].lower()
