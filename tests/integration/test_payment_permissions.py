"""
Integration tests for payment permission enforcement

Tests verify that:
1. Payments are allowed during registration period
2. Payments are allowed after registration closes (before payment deadline)
3. Payments are denied after payment deadline
4. Admin impersonation bypasses phase restrictions
"""
import pytest
import json
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock


@pytest.fixture
def complete_boat_registration(dynamodb_table, test_team_manager_id):
    """Create a complete boat registration ready for payment"""
    # Create crew members
    crew_members = []
    for i in range(4):
        crew_member = {
            'PK': f"TEAM#{test_team_manager_id}",
            'SK': f"CREW#crew_{i:03d}",
            'crew_member_id': f'crew_{i:03d}',
            'first_name': f'Rower{i}',
            'last_name': 'Test',
            'email': f'rower{i}@example.com',
            'phone': '1234567890',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'role': 'Rameur'
        }
        dynamodb_table.put_item(Item=crew_member)
        crew_members.append(crew_member)
    
    # Create complete boat registration
    boat = {
        'PK': f"TEAM#{test_team_manager_id}",
        'SK': 'BOAT#boat_001',
        'boat_registration_id': 'boat_001',
        'event_type': '4x',
        'boat_type': '4x',
        'registration_status': 'complete',
        'payment_status': 'unpaid',
        'crew_assignments': {
            'seat_1': crew_members[0]['crew_member_id'],
            'seat_2': crew_members[1]['crew_member_id'],
            'seat_3': crew_members[2]['crew_member_id'],
            'seat_4': crew_members[3]['crew_member_id']
        }
    }
    dynamodb_table.put_item(Item=boat)
    
    return boat


def test_payment_during_registration_success(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, 
    test_team_manager_id, complete_boat_registration
):
    """Test that payment is allowed during registration period"""
    # Set dates: registration period is active
    today = datetime.now().date()
    config = {
        'registration_start_date': (today - timedelta(days=7)).isoformat(),
        'registration_end_date': (today + timedelta(days=7)).isoformat(),
        'payment_deadline': (today + timedelta(days=14)).isoformat()
    }
    dynamodb_table.update_item(
        Key={'PK': 'CONFIG', 'SK': 'SYSTEM'},
        UpdateExpression='SET registration_start_date = :start, registration_end_date = :end, payment_deadline = :deadline',
        ExpressionAttributeValues={
            ':start': config['registration_start_date'],
            ':end': config['registration_end_date'],
            ':deadline': config['payment_deadline']
        }
    )
    
    # Mock Stripe payment intent creation
    with patch('payment.create_payment_intent.stripe_create_payment_intent') as mock_stripe:
        mock_stripe.return_value = {
            'id': 'pi_test_123',
            'client_secret': 'pi_test_123_secret_456',
            'amount': 8000,
            'currency': 'eur'
        }
        
        # Import Lambda handler
        from payment.create_payment_intent import lambda_handler
        
        # Create API Gateway event
        event = mock_api_gateway_event(
            http_method='POST',
            path='/payment/create-intent',
            body=json.dumps({'boat_registration_ids': ['boat_001']}),
            user_id=test_team_manager_id
        )
        
        # Attempt payment
        response = lambda_handler(event, mock_lambda_context)
        
        # Should succeed
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert 'data' in body
        assert 'payment_intent_id' in body['data']
        assert 'client_secret' in body['data']


def test_payment_after_registration_success(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_team_manager_id, complete_boat_registration
):
    """Test that payment is allowed after registration closes but before payment deadline"""
    # Set dates: registration closed, but payment deadline not reached
    today = datetime.now().date()
    config = {
        'registration_start_date': (today - timedelta(days=14)).isoformat(),
        'registration_end_date': (today - timedelta(days=7)).isoformat(),
        'payment_deadline': (today + timedelta(days=7)).isoformat()
    }
    dynamodb_table.update_item(
        Key={'PK': 'CONFIG', 'SK': 'SYSTEM'},
        UpdateExpression='SET registration_start_date = :start, registration_end_date = :end, payment_deadline = :deadline',
        ExpressionAttributeValues={
            ':start': config['registration_start_date'],
            ':end': config['registration_end_date'],
            ':deadline': config['payment_deadline']
        }
    )
    
    # Mock Stripe payment intent creation
    with patch('payment.create_payment_intent.stripe_create_payment_intent') as mock_stripe:
        mock_stripe.return_value = {
            'id': 'pi_test_456',
            'client_secret': 'pi_test_456_secret_789',
            'amount': 8000,
            'currency': 'eur'
        }
        
        # Import Lambda handler
        from payment.create_payment_intent import lambda_handler
        
        # Create API Gateway event
        event = mock_api_gateway_event(
            http_method='POST',
            path='/payment/create-intent',
            body=json.dumps({'boat_registration_ids': ['boat_001']}),
            user_id=test_team_manager_id
        )
        
        # Attempt payment
        response = lambda_handler(event, mock_lambda_context)
        
        # Should succeed - payments allowed after registration closes
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert 'data' in body
        assert 'payment_intent_id' in body['data']


def test_payment_after_deadline_denied(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_team_manager_id, complete_boat_registration
):
    """Test that payment is denied after payment deadline"""
    # Set dates: payment deadline has passed
    today = datetime.now().date()
    config = {
        'registration_start_date': (today - timedelta(days=21)).isoformat(),
        'registration_end_date': (today - timedelta(days=14)).isoformat(),
        'payment_deadline': (today - timedelta(days=7)).isoformat()
    }
    dynamodb_table.update_item(
        Key={'PK': 'CONFIG', 'SK': 'SYSTEM'},
        UpdateExpression='SET registration_start_date = :start, registration_end_date = :end, payment_deadline = :deadline',
        ExpressionAttributeValues={
            ':start': config['registration_start_date'],
            ':end': config['registration_end_date'],
            ':deadline': config['payment_deadline']
        }
    )
    
    # Import Lambda handler
    from payment.create_payment_intent import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='POST',
        path='/payment/create-intent',
        body=json.dumps({'boat_registration_ids': ['boat_001']}),
        user_id=test_team_manager_id
    )
    
    # Attempt payment
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be denied
    assert response['statusCode'] == 403
    body = json.loads(response['body'])
    assert 'error' in body
    # Permission system denies the action
    assert body['success'] is False


def test_payment_before_registration_denied(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_team_manager_id, complete_boat_registration
):
    """Test that payment is denied before registration opens"""
    # Set dates: registration hasn't started yet
    today = datetime.now().date()
    config = {
        'registration_start_date': (today + timedelta(days=7)).isoformat(),
        'registration_end_date': (today + timedelta(days=14)).isoformat(),
        'payment_deadline': (today + timedelta(days=21)).isoformat()
    }
    dynamodb_table.update_item(
        Key={'PK': 'CONFIG', 'SK': 'SYSTEM'},
        UpdateExpression='SET registration_start_date = :start, registration_end_date = :end, payment_deadline = :deadline',
        ExpressionAttributeValues={
            ':start': config['registration_start_date'],
            ':end': config['registration_end_date'],
            ':deadline': config['payment_deadline']
        }
    )
    
    # Import Lambda handler
    from payment.create_payment_intent import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='POST',
        path='/payment/create-intent',
        body=json.dumps({'boat_registration_ids': ['boat_001']}),
        user_id=test_team_manager_id
    )
    
    # Attempt payment
    response = lambda_handler(event, mock_lambda_context)
    
    # Should be denied
    assert response['statusCode'] == 403
    body = json.loads(response['body'])
    assert 'error' in body


def test_admin_impersonation_bypasses_payment_deadline(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context,
    test_admin_id, test_team_manager_id, complete_boat_registration
):
    """Test that admin impersonation allows payment even after deadline"""
    # Set dates: payment deadline has passed
    today = datetime.now().date()
    config = {
        'registration_start_date': (today - timedelta(days=21)).isoformat(),
        'registration_end_date': (today - timedelta(days=14)).isoformat(),
        'payment_deadline': (today - timedelta(days=7)).isoformat()
    }
    dynamodb_table.update_item(
        Key={'PK': 'CONFIG', 'SK': 'SYSTEM'},
        UpdateExpression='SET registration_start_date = :start, registration_end_date = :end, payment_deadline = :deadline',
        ExpressionAttributeValues={
            ':start': config['registration_start_date'],
            ':end': config['registration_end_date'],
            ':deadline': config['payment_deadline']
        }
    )
    
    # Mock Stripe payment intent creation
    with patch('payment.create_payment_intent.stripe_create_payment_intent') as mock_stripe:
        mock_stripe.return_value = {
            'id': 'pi_test_789',
            'client_secret': 'pi_test_789_secret_012',
            'amount': 8000,
            'currency': 'eur'
        }
        
        # Import Lambda handler
        from payment.create_payment_intent import lambda_handler
        
        # Admin impersonating team manager - create event with admin user
        event = mock_api_gateway_event(
            http_method='POST',
            path='/payment/create-intent',
            body=json.dumps({'boat_registration_ids': ['boat_001']}),
            user_id=test_admin_id,
            groups=['admins']  # Set admin group
        )
        
        # Add impersonation context (same pattern as other impersonation tests)
        event['requestContext']['authorizer']['claims']['custom:impersonated_user_id'] = test_team_manager_id
        
        # Attempt payment
        response = lambda_handler(event, mock_lambda_context)
        
        # Should succeed due to impersonation bypass
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert 'data' in body
        assert 'payment_intent_id' in body['data']
        
        # Verify audit log was created
        from boto3.dynamodb.conditions import Key
        audit_logs = dynamodb_table.query(
            KeyConditionExpression=Key('PK').eq('AUDIT#PERMISSION_BYPASS')
        )['Items']
        assert len(audit_logs) > 0
        latest_log = audit_logs[-1]
        assert latest_log['action'] == 'process_payment'
        assert latest_log['bypass_reason'] == 'impersonation'
        assert latest_log['impersonated_user_id'] == test_team_manager_id

