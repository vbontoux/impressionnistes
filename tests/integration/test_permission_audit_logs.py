"""
Integration tests for permission audit log viewer API
Tests loading audit logs with filtering and pagination
"""
import json
import pytest
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key


def test_load_audit_logs_success(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id
):
    """Test loading audit logs succeeds"""
    from admin.get_permission_audit_logs import lambda_handler
    
    # Create some test audit logs
    timestamp1 = datetime.utcnow().isoformat() + 'Z'
    timestamp2 = (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z'
    
    dynamodb_table.put_item(Item={
        'PK': 'AUDIT#PERMISSION_DENIAL',
        'SK': f'{timestamp1}#{test_team_manager_id}',
        'user_id': test_team_manager_id,
        'action': 'edit_crew_member',
        'resource_type': 'crew_member',
        'resource_id': 'crew-123',
        'denial_reason': 'after_registration_closed',
        'event_phase': 'after_registration',
        'timestamp': timestamp1
    })
    
    dynamodb_table.put_item(Item={
        'PK': 'AUDIT#PERMISSION_BYPASS',
        'SK': f'{timestamp2}#{test_admin_id}',
        'user_id': test_admin_id,
        'action': 'edit_crew_member',
        'resource_type': 'crew_member',
        'resource_id': 'crew-456',
        'bypass_reason': 'impersonation',
        'impersonated_user_id': test_team_manager_id,
        'event_phase': 'after_registration',
        'timestamp': timestamp2
    })
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/permissions/audit-logs',
        query_parameters={},
        user_id=test_admin_id,
        groups=['admins']
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert success
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'logs' in body
    assert len(body['logs']) >= 2
    assert body['total_count'] >= 2
    
    # Verify logs contain expected data
    logs = body['logs']
    denial_log = next((log for log in logs if log['log_type'] == 'denial'), None)
    bypass_log = next((log for log in logs if log['log_type'] == 'bypass'), None)
    
    assert denial_log is not None
    assert denial_log['user_id'] == test_team_manager_id
    assert denial_log['action'] == 'edit_crew_member'
    assert denial_log['denial_reason'] == 'after_registration_closed'
    
    assert bypass_log is not None
    assert bypass_log['user_id'] == test_admin_id
    assert bypass_log['bypass_reason'] == 'impersonation'
    assert bypass_log['impersonated_user_id'] == test_team_manager_id


def test_filter_audit_logs_by_user(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id
):
    """Test filtering audit logs by user_id returns correct results"""
    from admin.get_permission_audit_logs import lambda_handler
    
    # Create audit logs for different users
    timestamp1 = datetime.utcnow().isoformat() + 'Z'
    timestamp2 = (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z'
    
    dynamodb_table.put_item(Item={
        'PK': 'AUDIT#PERMISSION_DENIAL',
        'SK': f'{timestamp1}#{test_team_manager_id}',
        'user_id': test_team_manager_id,
        'action': 'edit_crew_member',
        'denial_reason': 'after_registration_closed',
        'timestamp': timestamp1
    })
    
    dynamodb_table.put_item(Item={
        'PK': 'AUDIT#PERMISSION_DENIAL',
        'SK': f'{timestamp2}#{test_admin_id}',
        'user_id': test_admin_id,
        'action': 'delete_boat_registration',
        'denial_reason': 'boat_paid',
        'timestamp': timestamp2
    })
    
    # Filter by team manager user_id
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/permissions/audit-logs',
        query_parameters={'user_id': test_team_manager_id},
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert only team manager logs returned
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body['logs']) >= 1
    
    for log in body['logs']:
        assert log['user_id'] == test_team_manager_id


def test_filter_audit_logs_by_action(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id
):
    """Test filtering audit logs by action returns correct results"""
    from admin.get_permission_audit_logs import lambda_handler
    
    # Create audit logs with different actions
    timestamp1 = datetime.utcnow().isoformat() + 'Z'
    timestamp2 = (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z'
    
    dynamodb_table.put_item(Item={
        'PK': 'AUDIT#PERMISSION_DENIAL',
        'SK': f'{timestamp1}#{test_team_manager_id}',
        'user_id': test_team_manager_id,
        'action': 'edit_crew_member',
        'denial_reason': 'after_registration_closed',
        'timestamp': timestamp1
    })
    
    dynamodb_table.put_item(Item={
        'PK': 'AUDIT#PERMISSION_DENIAL',
        'SK': f'{timestamp2}#{test_team_manager_id}',
        'user_id': test_team_manager_id,
        'action': 'delete_boat_registration',
        'denial_reason': 'boat_paid',
        'timestamp': timestamp2
    })
    
    # Filter by action
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/permissions/audit-logs',
        query_parameters={'action': 'edit_crew_member'},
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert only edit_crew_member logs returned
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body['logs']) >= 1
    
    for log in body['logs']:
        assert log['action'] == 'edit_crew_member'


def test_filter_audit_logs_by_date_range(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id
):
    """Test filtering audit logs by date range returns correct results"""
    from admin.get_permission_audit_logs import lambda_handler
    
    # Create audit logs at different times
    now = datetime.utcnow()
    timestamp_recent = now.isoformat() + 'Z'
    timestamp_old = (now - timedelta(days=7)).isoformat() + 'Z'
    
    dynamodb_table.put_item(Item={
        'PK': 'AUDIT#PERMISSION_DENIAL',
        'SK': f'{timestamp_recent}#{test_team_manager_id}',
        'user_id': test_team_manager_id,
        'action': 'edit_crew_member',
        'denial_reason': 'after_registration_closed',
        'timestamp': timestamp_recent
    })
    
    dynamodb_table.put_item(Item={
        'PK': 'AUDIT#PERMISSION_DENIAL',
        'SK': f'{timestamp_old}#{test_team_manager_id}',
        'user_id': test_team_manager_id,
        'action': 'delete_boat_registration',
        'denial_reason': 'boat_paid',
        'timestamp': timestamp_old
    })
    
    # Filter by date range (last 3 days)
    start_date = (now - timedelta(days=3)).isoformat().split('T')[0]
    end_date = now.isoformat().split('T')[0]
    
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/permissions/audit-logs',
        query_parameters={
            'start_date': start_date,
            'end_date': end_date
        },
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert only recent logs returned
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body['logs']) >= 1
    
    # Verify all logs are within date range
    for log in body['logs']:
        log_date = log['SK'].split('#')[0].split('T')[0]
        assert log_date >= start_date
        assert log_date <= end_date


def test_filter_audit_logs_by_log_type(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id
):
    """Test filtering audit logs by log type returns correct results"""
    from admin.get_permission_audit_logs import lambda_handler
    
    # Create different types of audit logs
    timestamp1 = datetime.utcnow().isoformat() + 'Z'
    timestamp2 = (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z'
    
    dynamodb_table.put_item(Item={
        'PK': 'AUDIT#PERMISSION_DENIAL',
        'SK': f'{timestamp1}#{test_team_manager_id}',
        'user_id': test_team_manager_id,
        'action': 'edit_crew_member',
        'denial_reason': 'after_registration_closed',
        'timestamp': timestamp1
    })
    
    dynamodb_table.put_item(Item={
        'PK': 'AUDIT#PERMISSION_BYPASS',
        'SK': f'{timestamp2}#{test_admin_id}',
        'user_id': test_admin_id,
        'action': 'edit_crew_member',
        'bypass_reason': 'impersonation',
        'timestamp': timestamp2
    })
    
    # Filter by denial logs only
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/permissions/audit-logs',
        query_parameters={'log_type': 'denial'},
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert only denial logs returned
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body['logs']) >= 1
    
    for log in body['logs']:
        assert log['log_type'] == 'denial'
    
    # Filter by bypass logs only
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/permissions/audit-logs',
        query_parameters={'log_type': 'bypass'},
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert only bypass logs returned
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body['logs']) >= 1
    
    for log in body['logs']:
        assert log['log_type'] == 'bypass'


def test_audit_logs_pagination(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id
):
    """Test pagination works correctly for audit logs"""
    from admin.get_permission_audit_logs import lambda_handler
    
    # Create multiple audit logs
    for i in range(10):
        timestamp = (datetime.utcnow() - timedelta(hours=i)).isoformat() + 'Z'
        dynamodb_table.put_item(Item={
            'PK': 'AUDIT#PERMISSION_DENIAL',
            'SK': f'{timestamp}#{test_team_manager_id}',
            'user_id': test_team_manager_id,
            'action': 'edit_crew_member',
            'denial_reason': 'after_registration_closed',
            'timestamp': timestamp
        })
    
    # Request first page with limit
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/permissions/audit-logs',
        query_parameters={'limit': '5'},
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert first page returned
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body['logs']) <= 5
    
    # If there are more results, next_token should be present
    if body.get('has_more'):
        assert body.get('next_token') is not None
        
        # Request second page
        event = mock_api_gateway_event(
            http_method='GET',
            path='/admin/permissions/audit-logs',
            query_parameters={
                'limit': '5',
                'next_token': body['next_token']
            },
            user_id=test_admin_id,
            groups=['admins']
        )
        
        response = lambda_handler(event, mock_lambda_context)
        
        # Assert second page returned
        assert response['statusCode'] == 200
        body2 = json.loads(response['body'])
        assert len(body2['logs']) > 0


def test_audit_logs_empty_result(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id
):
    """Test loading audit logs with no results returns empty list"""
    from admin.get_permission_audit_logs import lambda_handler
    
    # Request logs with filter that matches nothing
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/permissions/audit-logs',
        query_parameters={'user_id': 'nonexistent-user'},
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert empty result
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['logs'] == []
    assert body['total_count'] == 0
    assert body['has_more'] is False


def test_audit_logs_sorted_by_timestamp_descending(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id
):
    """Test audit logs are sorted by timestamp in descending order (newest first)"""
    from admin.get_permission_audit_logs import lambda_handler
    
    # Create audit logs at different times
    now = datetime.utcnow()
    timestamps = [
        (now - timedelta(hours=3)).isoformat() + 'Z',
        (now - timedelta(hours=1)).isoformat() + 'Z',
        now.isoformat() + 'Z'
    ]
    
    for i, timestamp in enumerate(timestamps):
        dynamodb_table.put_item(Item={
            'PK': 'AUDIT#PERMISSION_DENIAL',
            'SK': f'{timestamp}#{test_team_manager_id}',
            'user_id': test_team_manager_id,
            'action': f'action_{i}',
            'denial_reason': 'after_registration_closed',
            'timestamp': timestamp
        })
    
    # Request logs
    event = mock_api_gateway_event(
        http_method='GET',
        path='/admin/permissions/audit-logs',
        query_parameters={},
        user_id=test_admin_id,
        groups=['admins']
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert logs are sorted descending
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    logs = body['logs']
    
    # Verify timestamps are in descending order
    for i in range(len(logs) - 1):
        current_timestamp = logs[i]['SK'].split('#')[0]
        next_timestamp = logs[i + 1]['SK'].split('#')[0]
        assert current_timestamp >= next_timestamp
