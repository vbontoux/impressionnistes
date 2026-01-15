"""
Unit tests for access control audit logging.

Tests the audit logging functions for permission denials and bypasses.
"""

import pytest
from moto import mock_dynamodb
import boto3
from datetime import datetime

from functions.shared.access_control import (
    UserContext,
    ResourceContext,
    log_permission_denial,
    log_permission_grant_with_bypass
)


@pytest.fixture
def dynamodb_table():
    """Create a mock DynamoDB table for testing."""
    with mock_dynamodb():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Create table
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        yield dynamodb


def test_log_permission_denial_creates_correct_entry(dynamodb_table):
    """Test that denial logging creates correct DynamoDB entry."""
    # Create test contexts
    user_context = UserContext(
        user_id='user-123',
        role='team_manager',
        is_impersonating=False,
        has_temporary_access=False
    )
    
    resource_context = ResourceContext(
        resource_type='crew_member',
        resource_id='crew-456',
        resource_state={'assigned': True}
    )
    
    # Log denial
    log_permission_denial(
        user_context=user_context,
        action='edit_crew_member',
        resource_context=resource_context,
        reason='crew_member_assigned',
        db_client=dynamodb_table,
        table_name='test-table'
    )
    
    # Verify entry was created
    table = dynamodb_table.Table('test-table')
    response = table.query(
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={
            ':pk': 'AUDIT#PERMISSION_DENIAL'
        }
    )
    
    assert response['Count'] == 1
    
    item = response['Items'][0]
    assert item['PK'] == 'AUDIT#PERMISSION_DENIAL'
    assert 'user-123' in item['SK']
    assert item['user_id'] == 'user-123'
    assert item['action'] == 'edit_crew_member'
    assert item['resource_type'] == 'crew_member'
    assert item['resource_id'] == 'crew-456'
    assert item['denial_reason'] == 'crew_member_assigned'
    assert 'timestamp' in item
    assert item['resource_state'] == {'assigned': True}


def test_log_permission_denial_without_resource_id(dynamodb_table):
    """Test denial logging when resource_id is None."""
    user_context = UserContext(
        user_id='user-789',
        role='team_manager'
    )
    
    resource_context = ResourceContext(
        resource_type='boat_registration',
        resource_id=None,
        resource_state={'paid': False}
    )
    
    # Log denial
    log_permission_denial(
        user_context=user_context,
        action='create_boat_registration',
        resource_context=resource_context,
        reason='after_registration_closed',
        db_client=dynamodb_table,
        table_name='test-table'
    )
    
    # Verify entry was created
    table = dynamodb_table.Table('test-table')
    response = table.query(
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={
            ':pk': 'AUDIT#PERMISSION_DENIAL'
        }
    )
    
    assert response['Count'] == 1
    item = response['Items'][0]
    assert item['resource_id'] == 'N/A'


def test_log_permission_bypass_with_impersonation(dynamodb_table):
    """Test bypass logging includes impersonation details."""
    # Create test contexts with impersonation
    user_context = UserContext(
        user_id='admin-123',
        role='admin',
        is_impersonating=True,
        has_temporary_access=False,
        team_manager_id='manager-456'
    )
    
    resource_context = ResourceContext(
        resource_type='crew_member',
        resource_id='crew-789',
        resource_state={'assigned': False}
    )
    
    # Log bypass
    log_permission_grant_with_bypass(
        user_context=user_context,
        action='create_crew_member',
        resource_context=resource_context,
        bypass_reason='impersonation',
        db_client=dynamodb_table,
        table_name='test-table'
    )
    
    # Verify entry was created
    table = dynamodb_table.Table('test-table')
    response = table.query(
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={
            ':pk': 'AUDIT#PERMISSION_BYPASS'
        }
    )
    
    assert response['Count'] == 1
    
    item = response['Items'][0]
    assert item['PK'] == 'AUDIT#PERMISSION_BYPASS'
    assert 'admin-123' in item['SK']
    assert item['user_id'] == 'admin-123'
    assert item['action'] == 'create_crew_member'
    assert item['resource_type'] == 'crew_member'
    assert item['resource_id'] == 'crew-789'
    assert item['bypass_reason'] == 'impersonation'
    assert item['impersonated_user_id'] == 'manager-456'
    assert 'timestamp' in item


def test_log_permission_bypass_with_temporary_access(dynamodb_table):
    """Test bypass logging for temporary access grants."""
    # Create test contexts with temporary access
    user_context = UserContext(
        user_id='manager-123',
        role='team_manager',
        is_impersonating=False,
        has_temporary_access=True
    )
    
    resource_context = ResourceContext(
        resource_type='boat_registration',
        resource_id='boat-456',
        resource_state={'paid': False}
    )
    
    # Log bypass
    log_permission_grant_with_bypass(
        user_context=user_context,
        action='edit_boat_registration',
        resource_context=resource_context,
        bypass_reason='temporary_access',
        db_client=dynamodb_table,
        table_name='test-table'
    )
    
    # Verify entry was created
    table = dynamodb_table.Table('test-table')
    response = table.query(
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={
            ':pk': 'AUDIT#PERMISSION_BYPASS'
        }
    )
    
    assert response['Count'] == 1
    
    item = response['Items'][0]
    assert item['bypass_reason'] == 'temporary_access'
    # Should NOT have impersonated_user_id for temporary access
    assert 'impersonated_user_id' not in item


def test_log_permission_denial_handles_write_failure_gracefully(dynamodb_table, caplog):
    """Test that write failures are logged but don't raise exceptions."""
    import logging
    
    # Create test contexts
    user_context = UserContext(
        user_id='user-123',
        role='team_manager'
    )
    
    resource_context = ResourceContext(
        resource_type='crew_member',
        resource_id='crew-456'
    )
    
    # Use invalid table name to trigger error
    with caplog.at_level(logging.ERROR):
        log_permission_denial(
            user_context=user_context,
            action='edit_crew_member',
            resource_context=resource_context,
            reason='test_reason',
            db_client=dynamodb_table,
            table_name='nonexistent-table'
        )
    
    # Verify error was logged
    assert any('Failed to log permission denial' in record.message for record in caplog.records)
    # Function should not raise exception


def test_log_permission_bypass_handles_write_failure_gracefully(dynamodb_table, caplog):
    """Test that bypass logging failures are handled gracefully."""
    import logging
    
    # Create test contexts
    user_context = UserContext(
        user_id='admin-123',
        role='admin',
        is_impersonating=True,
        team_manager_id='manager-456'
    )
    
    resource_context = ResourceContext(
        resource_type='crew_member',
        resource_id='crew-789'
    )
    
    # Use invalid table name to trigger error
    with caplog.at_level(logging.ERROR):
        log_permission_grant_with_bypass(
            user_context=user_context,
            action='create_crew_member',
            resource_context=resource_context,
            bypass_reason='impersonation',
            db_client=dynamodb_table,
            table_name='nonexistent-table'
        )
    
    # Verify error was logged
    assert any('Failed to log permission bypass' in record.message for record in caplog.records)
    # Function should not raise exception


def test_log_permission_denial_includes_timestamp(dynamodb_table):
    """Test that denial logs include proper timestamp."""
    user_context = UserContext(
        user_id='user-123',
        role='team_manager'
    )
    
    resource_context = ResourceContext(
        resource_type='crew_member',
        resource_id='crew-456'
    )
    
    # Log denial
    before_time = datetime.utcnow()
    log_permission_denial(
        user_context=user_context,
        action='edit_crew_member',
        resource_context=resource_context,
        reason='test_reason',
        db_client=dynamodb_table,
        table_name='test-table'
    )
    after_time = datetime.utcnow()
    
    # Verify timestamp is within expected range
    table = dynamodb_table.Table('test-table')
    response = table.query(
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={
            ':pk': 'AUDIT#PERMISSION_DENIAL'
        }
    )
    
    item = response['Items'][0]
    timestamp_str = item['timestamp']
    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')).replace(tzinfo=None)
    
    assert before_time <= timestamp <= after_time


def test_log_permission_bypass_includes_timestamp(dynamodb_table):
    """Test that bypass logs include proper timestamp."""
    user_context = UserContext(
        user_id='admin-123',
        role='admin',
        is_impersonating=True,
        team_manager_id='manager-456'
    )
    
    resource_context = ResourceContext(
        resource_type='crew_member',
        resource_id='crew-789'
    )
    
    # Log bypass
    before_time = datetime.utcnow()
    log_permission_grant_with_bypass(
        user_context=user_context,
        action='create_crew_member',
        resource_context=resource_context,
        bypass_reason='impersonation',
        db_client=dynamodb_table,
        table_name='test-table'
    )
    after_time = datetime.utcnow()
    
    # Verify timestamp is within expected range
    table = dynamodb_table.Table('test-table')
    response = table.query(
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={
            ':pk': 'AUDIT#PERMISSION_BYPASS'
        }
    )
    
    item = response['Items'][0]
    timestamp_str = item['timestamp']
    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')).replace(tzinfo=None)
    
    assert before_time <= timestamp <= after_time
