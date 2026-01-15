"""
Integration tests for temporary access grant APIs
Tests grant creation, revocation, listing, and permission bypass functionality
"""
import json
import pytest
from datetime import datetime, timedelta


def test_grant_temporary_access_success(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id
):
    """Test granting temporary access succeeds"""
    from admin.grant_temporary_access import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='POST',
        path='/admin/temporary-access/grant',
        body=json.dumps({
            'user_id': test_team_manager_id,
            'hours': 24,
            'notes': 'Test grant'
        }),
        user_id=test_admin_id,
        groups=['admins']
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert success
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['user_id'] == test_team_manager_id
    assert body['data']['status'] == 'active'
    assert body['data']['hours'] == 24
    assert 'expiration_timestamp' in body['data']
    
    # Verify grant was created in database
    grant = dynamodb_table.get_item(
        Key={'PK': 'TEMP_ACCESS', 'SK': f'USER#{test_team_manager_id}'}
    )
    assert 'Item' in grant
    assert grant['Item']['status'] == 'active'


def test_grant_temporary_access_uses_default_hours(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id
):
    """Test granting temporary access uses default hours from config"""
    from admin.grant_temporary_access import lambda_handler
    
    # Create API Gateway event without hours parameter
    event = mock_api_gateway_event(
        http_method='POST',
        path='/admin/temporary-access/grant',
        body=json.dumps({
            'user_id': test_team_manager_id
        }),
        user_id=test_admin_id,
        groups=['admins']
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert success with default hours (48 from config)
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['hours'] == 48


def test_grant_temporary_access_missing_user_id(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id
):
    """Test granting temporary access fails without user_id"""
    from admin.grant_temporary_access import lambda_handler
    
    # Create API Gateway event without user_id
    event = mock_api_gateway_event(
        http_method='POST',
        path='/admin/temporary-access/grant',
        body=json.dumps({
            'hours': 24
        }),
        user_id=test_admin_id,
        groups=['admins']
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert validation error
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'user_id is required' in str(body['error'])


def test_user_with_active_grant_bypasses_phase_restrictions(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id
):
    """Test user with active grant can bypass event phase restrictions"""
    # Set registration period to be closed
    today = datetime.now().date()
    start_date = (today - timedelta(days=35)).isoformat()
    end_date = (today - timedelta(days=5)).isoformat()
    payment_deadline = (today + timedelta(days=5)).isoformat()
    
    dynamodb_table.update_item(
        Key={'PK': 'CONFIG', 'SK': 'SYSTEM'},
        UpdateExpression='SET registration_start_date = :start, registration_end_date = :end, payment_deadline = :deadline',
        ExpressionAttributeValues={
            ':start': start_date,
            ':end': end_date,
            ':deadline': payment_deadline
        }
    )
    
    # Create active temporary access grant
    grant_timestamp = datetime.utcnow()
    expiration_timestamp = grant_timestamp + timedelta(hours=24)
    
    dynamodb_table.put_item(
        Item={
            'PK': 'TEMP_ACCESS',
            'SK': f'USER#{test_team_manager_id}',
            'user_id': test_team_manager_id,
            'grant_timestamp': grant_timestamp.isoformat() + 'Z',
            'expiration_timestamp': expiration_timestamp.isoformat() + 'Z',
            'granted_by_admin_id': 'admin-123',
            'status': 'active',
            'hours': 24
        }
    )
    
    # Try to create crew member (should succeed with grant)
    from crew.create_crew_member import lambda_handler
    
    event = mock_api_gateway_event(
        http_method='POST',
        path='/crew',
        body=json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'license_number': 'ABC789',
            'club_affiliation': 'Test Club'
        }),
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert success (grant bypassed phase restriction)
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert body['success'] is True


def test_expired_grant_does_not_bypass_restrictions(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id
):
    """Test expired grant does not provide access"""
    # Set registration period to be closed
    today = datetime.now().date()
    start_date = (today - timedelta(days=35)).isoformat()
    end_date = (today - timedelta(days=5)).isoformat()
    payment_deadline = (today + timedelta(days=5)).isoformat()
    
    dynamodb_table.update_item(
        Key={'PK': 'CONFIG', 'SK': 'SYSTEM'},
        UpdateExpression='SET registration_start_date = :start, registration_end_date = :end, payment_deadline = :deadline',
        ExpressionAttributeValues={
            ':start': start_date,
            ':end': end_date,
            ':deadline': payment_deadline
        }
    )
    
    # Create expired temporary access grant
    grant_timestamp = datetime.utcnow() - timedelta(hours=48)
    expiration_timestamp = datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
    
    dynamodb_table.put_item(
        Item={
            'PK': 'TEMP_ACCESS',
            'SK': f'USER#{test_team_manager_id}',
            'user_id': test_team_manager_id,
            'grant_timestamp': grant_timestamp.isoformat() + 'Z',
            'expiration_timestamp': expiration_timestamp.isoformat() + 'Z',
            'granted_by_admin_id': 'admin-123',
            'status': 'active',  # Still marked active but expired
            'hours': 24
        }
    )
    
    # Try to create crew member (should fail - grant expired)
    from crew.create_crew_member import lambda_handler
    
    event = mock_api_gateway_event(
        http_method='POST',
        path='/crew',
        body=json.dumps({
            'first_name': 'Jane',
            'last_name': 'Smith',
            'date_of_birth': '1992-05-15',
            'gender': 'F',
            'license_number': 'XYZ123',
            'club_affiliation': 'Test Club'
        }),
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert denied (expired grant does not bypass)
    assert response['statusCode'] == 403
    body = json.loads(response['body'])
    assert body['success'] is False


def test_revoke_temporary_access_success(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id
):
    """Test revoking temporary access succeeds"""
    # Create active grant first
    grant_timestamp = datetime.utcnow()
    expiration_timestamp = grant_timestamp + timedelta(hours=24)
    
    dynamodb_table.put_item(
        Item={
            'PK': 'TEMP_ACCESS',
            'SK': f'USER#{test_team_manager_id}',
            'user_id': test_team_manager_id,
            'grant_timestamp': grant_timestamp.isoformat() + 'Z',
            'expiration_timestamp': expiration_timestamp.isoformat() + 'Z',
            'granted_by_admin_id': 'admin-123',
            'status': 'active',
            'hours': 24
        }
    )
    
    # Revoke the grant
    from admin.revoke_temporary_access import lambda_handler
    
    event = mock_api_gateway_event(
        http_method='POST',
        path='/admin/temporary-access/revoke',
        body=json.dumps({
            'user_id': test_team_manager_id
        }),
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert success
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['status'] == 'revoked'
    
    # Verify grant was revoked in database
    grant = dynamodb_table.get_item(
        Key={'PK': 'TEMP_ACCESS', 'SK': f'USER#{test_team_manager_id}'}
    )
    assert grant['Item']['status'] == 'revoked'
    assert 'revoked_at' in grant['Item']
    assert grant['Item']['revoked_by_admin_id'] == test_admin_id


def test_revoked_grant_does_not_bypass_restrictions(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id
):
    """Test revoked grant does not provide access"""
    # Set registration period to be closed
    today = datetime.now().date()
    start_date = (today - timedelta(days=35)).isoformat()
    end_date = (today - timedelta(days=5)).isoformat()
    payment_deadline = (today + timedelta(days=5)).isoformat()
    
    dynamodb_table.update_item(
        Key={'PK': 'CONFIG', 'SK': 'SYSTEM'},
        UpdateExpression='SET registration_start_date = :start, registration_end_date = :end, payment_deadline = :deadline',
        ExpressionAttributeValues={
            ':start': start_date,
            ':end': end_date,
            ':deadline': payment_deadline
        }
    )
    
    # Create revoked grant
    grant_timestamp = datetime.utcnow()
    expiration_timestamp = grant_timestamp + timedelta(hours=24)
    
    dynamodb_table.put_item(
        Item={
            'PK': 'TEMP_ACCESS',
            'SK': f'USER#{test_team_manager_id}',
            'user_id': test_team_manager_id,
            'grant_timestamp': grant_timestamp.isoformat() + 'Z',
            'expiration_timestamp': expiration_timestamp.isoformat() + 'Z',
            'granted_by_admin_id': 'admin-123',
            'status': 'revoked',
            'hours': 24,
            'revoked_at': datetime.utcnow().isoformat() + 'Z',
            'revoked_by_admin_id': 'admin-456'
        }
    )
    
    # Try to create crew member (should fail - grant revoked)
    from crew.create_crew_member import lambda_handler
    
    event = mock_api_gateway_event(
        http_method='POST',
        path='/crew',
        body=json.dumps({
            'first_name': 'Bob',
            'last_name': 'Wilson',
            'date_of_birth': '1988-03-20',
            'gender': 'M',
            'license_number': 'DEF456',
            'club_affiliation': 'Test Club'
        }),
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert denied (revoked grant does not bypass)
    assert response['statusCode'] == 403
    body = json.loads(response['body'])
    assert body['success'] is False


def test_list_temporary_access_grants_success(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id
):
    """Test listing temporary access grants succeeds"""
    # Create multiple grants with different statuses
    now = datetime.utcnow()
    
    # Active grant
    dynamodb_table.put_item(
        Item={
            'PK': 'TEMP_ACCESS',
            'SK': f'USER#{test_team_manager_id}',
            'user_id': test_team_manager_id,
            'grant_timestamp': now.isoformat() + 'Z',
            'expiration_timestamp': (now + timedelta(hours=24)).isoformat() + 'Z',
            'granted_by_admin_id': 'admin-123',
            'status': 'active',
            'hours': 24
        }
    )
    
    # Revoked grant
    dynamodb_table.put_item(
        Item={
            'PK': 'TEMP_ACCESS',
            'SK': 'USER#user-456',
            'user_id': 'user-456',
            'grant_timestamp': (now - timedelta(days=2)).isoformat() + 'Z',
            'expiration_timestamp': (now + timedelta(hours=12)).isoformat() + 'Z',
            'granted_by_admin_id': 'admin-123',
            'status': 'revoked',
            'hours': 48,
            'revoked_at': now.isoformat() + 'Z',
            'revoked_by_admin_id': test_admin_id
        }
    )
    
    # List all grants
    from admin.list_temporary_access_grants import lambda_handler
    
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/temporary-access/list',
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert success
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['count'] == 2
    assert len(body['data']['grants']) == 2
    
    # Verify grant details
    grants = body['data']['grants']
    active_grant = next(g for g in grants if g['user_id'] == test_team_manager_id)
    assert active_grant['status'] == 'active'
    assert active_grant['remaining_hours'] > 0
    
    revoked_grant = next(g for g in grants if g['user_id'] == 'user-456')
    assert revoked_grant['status'] == 'revoked'


def test_list_temporary_access_grants_filters_by_status(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id
):
    """Test listing grants can filter by status"""
    # Create grants with different statuses
    now = datetime.utcnow()
    
    dynamodb_table.put_item(
        Item={
            'PK': 'TEMP_ACCESS',
            'SK': f'USER#{test_team_manager_id}',
            'user_id': test_team_manager_id,
            'grant_timestamp': now.isoformat() + 'Z',
            'expiration_timestamp': (now + timedelta(hours=24)).isoformat() + 'Z',
            'granted_by_admin_id': 'admin-123',
            'status': 'active',
            'hours': 24
        }
    )
    
    dynamodb_table.put_item(
        Item={
            'PK': 'TEMP_ACCESS',
            'SK': 'USER#user-789',
            'user_id': 'user-789',
            'grant_timestamp': (now - timedelta(days=2)).isoformat() + 'Z',
            'expiration_timestamp': (now + timedelta(hours=12)).isoformat() + 'Z',
            'granted_by_admin_id': 'admin-123',
            'status': 'revoked',
            'hours': 48
        }
    )
    
    # List only active grants
    from admin.list_temporary_access_grants import lambda_handler
    
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/temporary-access/list?status=active',
        user_id=test_admin_id,
        groups=['admins'],
        query_parameters={'status': 'active'}
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert only active grants returned
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['count'] == 1
    assert body['data']['grants'][0]['status'] == 'active'
    assert body['data']['grants'][0]['user_id'] == test_team_manager_id


def test_list_grants_marks_expired_grants(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id
):
    """Test listing grants automatically marks expired grants"""
    # Create grant that should be expired
    now = datetime.utcnow()
    
    dynamodb_table.put_item(
        Item={
            'PK': 'TEMP_ACCESS',
            'SK': 'USER#user-expired',
            'user_id': 'user-expired',
            'grant_timestamp': (now - timedelta(hours=48)).isoformat() + 'Z',
            'expiration_timestamp': (now - timedelta(hours=1)).isoformat() + 'Z',
            'granted_by_admin_id': 'admin-123',
            'status': 'active',  # Still marked active
            'hours': 24
        }
    )
    
    # List grants
    from admin.list_temporary_access_grants import lambda_handler
    
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/temporary-access/list',
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert grant was marked as expired
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    grants = body['data']['grants']
    expired_grant = next(g for g in grants if g['user_id'] == 'user-expired')
    assert expired_grant['status'] == 'expired'
    assert expired_grant['remaining_hours'] == 0
    
    # Verify database was updated
    grant = dynamodb_table.get_item(
        Key={'PK': 'TEMP_ACCESS', 'SK': 'USER#user-expired'}
    )
    assert grant['Item']['status'] == 'expired'
