"""
Unit tests for permission decorator in access control system

Tests the @require_permission decorator with various scenarios:
- Successful permission grant
- Permission denial with 403 response
- Context extraction from various event formats
- Impersonation handling
- Error handling

Feature: centralized-access-control
Validates: Requirements 7.1, 7.2
"""
import pytest
import json
from datetime import datetime, timedelta
from moto import mock_dynamodb
import boto3
import os
import sys

# Add functions/shared to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/shared'))

from access_control import (
    require_permission,
    get_user_context_from_event,
    get_resource_context_from_body,
    UserContext,
    ResourceContext
)


@pytest.fixture
def mock_dynamodb_table():
    """Create a mock DynamoDB table for testing"""
    with mock_dynamodb():
        # Set up AWS credentials
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_DEFAULT_REGION'] = 'eu-west-3'
        
        # Set table name
        table_name = 'test-access-control-table'
        os.environ['TABLE_NAME'] = table_name
        
        # Create DynamoDB resource
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')
        
        # Create table
        table = dynamodb.create_table(
            TableName=table_name,
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
        
        # Wait for table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        
        yield table


def seed_config_during_registration(table):
    """Helper to seed configuration for during registration phase"""
    now = datetime.utcnow()
    table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'registration_start_date': (now - timedelta(days=1)).isoformat() + 'Z',
        'registration_end_date': (now + timedelta(days=30)).isoformat() + 'Z',
        'payment_deadline': (now + timedelta(days=45)).isoformat() + 'Z',
        'temporary_editing_access_hours': 48
    })


def seed_config_after_registration(table):
    """Helper to seed configuration for after registration phase"""
    now = datetime.utcnow()
    table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'registration_start_date': (now - timedelta(days=60)).isoformat() + 'Z',
        'registration_end_date': (now - timedelta(days=1)).isoformat() + 'Z',
        'payment_deadline': (now + timedelta(days=15)).isoformat() + 'Z',
        'temporary_editing_access_hours': 48
    })


def seed_permissions(table):
    """Helper to seed default permission matrix"""
    table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'PERMISSIONS',
        'permissions': {
            'create_crew_member': {
                'before_registration': False,
                'during_registration': True,
                'after_registration': False,
                'after_payment_deadline': False,
            },
            'edit_crew_member': {
                'before_registration': False,
                'during_registration': True,
                'after_registration': False,
                'after_payment_deadline': False,
                'requires_not_assigned': True,
            }
        }
    })


def create_mock_event(user_id='user-123', is_admin=False, is_impersonating=False, body=None):
    """Create a mock Lambda event for testing"""
    event = {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': user_id,
                    'email': 'test@example.com',
                    'cognito:groups': 'admins' if is_admin else 'team_managers'
                }
            }
        },
        'body': json.dumps(body) if body else '{}',
        'pathParameters': {},
        'queryStringParameters': {}
    }
    
    if is_impersonating:
        event['_is_admin_override'] = True
        event['_effective_user_id'] = 'manager-456'
        event['_admin_user_id'] = user_id
    
    return event


# ============================================================================
# Tests for get_user_context_from_event
# ============================================================================

def test_get_user_context_from_event_team_manager():
    """Test extracting user context for a team manager"""
    event = create_mock_event(user_id='user-123', is_admin=False)
    
    context = get_user_context_from_event(event)
    
    assert context.user_id == 'user-123'
    assert context.role == 'team_manager'
    assert context.is_impersonating is False
    assert context.has_temporary_access is False
    assert context.team_manager_id is None


def test_get_user_context_from_event_admin():
    """Test extracting user context for an admin"""
    event = create_mock_event(user_id='admin-123', is_admin=True)
    
    context = get_user_context_from_event(event)
    
    assert context.user_id == 'admin-123'
    assert context.role == 'admin'
    assert context.is_impersonating is False


def test_get_user_context_from_event_impersonating():
    """Test extracting user context for admin impersonating"""
    event = create_mock_event(user_id='admin-123', is_admin=True, is_impersonating=True)
    
    context = get_user_context_from_event(event)
    
    # When impersonating, user_id should be the impersonated user's ID for permission checks
    assert context.user_id == 'manager-456'
    assert context.role == 'admin'
    assert context.is_impersonating is True
    assert context.team_manager_id == 'manager-456'


def test_get_user_context_from_event_no_auth():
    """Test extracting user context when no authentication present"""
    event = {
        'requestContext': {},
        'body': '{}',
        'pathParameters': {}
    }
    
    context = get_user_context_from_event(event)
    
    assert context.user_id == 'anonymous'
    assert context.role == 'anonymous'


# ============================================================================
# Tests for get_resource_context_from_body
# ============================================================================

def test_get_resource_context_from_body_crew_member():
    """Test extracting resource context for crew member"""
    body = {'crew_member_id': 'crew-123', 'name': 'John Doe'}
    event = {'pathParameters': {'crew_member_id': 'crew-123'}}
    
    context = get_resource_context_from_body(body, 'crew_member', event)
    
    assert context.resource_type == 'crew_member'
    assert context.resource_id == 'crew-123'
    assert isinstance(context.resource_state, dict)


def test_get_resource_context_from_body_boat_registration():
    """Test extracting resource context for boat registration"""
    body = {'boat_registration_id': 'boat-456'}
    event = {'pathParameters': {'boat_registration_id': 'boat-456'}}
    
    context = get_resource_context_from_body(body, 'boat_registration', event)
    
    assert context.resource_type == 'boat_registration'
    assert context.resource_id == 'boat-456'


def test_get_resource_context_from_body_no_id():
    """Test extracting resource context when no ID present (create operation)"""
    body = {'name': 'New Crew Member'}
    event = {'pathParameters': {}}
    
    context = get_resource_context_from_body(body, 'crew_member', event)
    
    assert context.resource_type == 'crew_member'
    assert context.resource_id is None
    assert context.resource_state.get('assigned') is False


# ============================================================================
# Tests for @require_permission decorator
# ============================================================================

def test_decorator_allows_action_during_registration(mock_dynamodb_table):
    """Test decorator allows action during registration period"""
    # Seed configuration and permissions
    seed_config_during_registration(mock_dynamodb_table)
    seed_permissions(mock_dynamodb_table)
    
    # Create test handler with decorator
    @require_permission('create_crew_member')
    def test_handler(event, context):
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Success'})
        }
    
    # Create event
    event = create_mock_event(user_id='user-123', is_admin=False)
    
    # Call handler
    result = test_handler(event, None)
    
    # Should succeed
    assert result['statusCode'] == 200


def test_decorator_denies_action_after_registration(mock_dynamodb_table):
    """Test decorator denies action after registration closes"""
    # Seed configuration and permissions
    seed_config_after_registration(mock_dynamodb_table)
    seed_permissions(mock_dynamodb_table)
    
    # Create test handler with decorator
    @require_permission('create_crew_member')
    def test_handler(event, context):
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Success'})
        }
    
    # Create event
    event = create_mock_event(user_id='user-123', is_admin=False)
    
    # Call handler
    result = test_handler(event, None)
    
    # Should be denied with 403
    assert result['statusCode'] == 403
    body = json.loads(result['body'])
    assert body['error'] == 'Permission denied'
    assert 'reason' in body


def test_decorator_allows_impersonation_bypass(mock_dynamodb_table):
    """Test decorator allows admin impersonation to bypass phase restrictions"""
    # Seed configuration and permissions
    seed_config_after_registration(mock_dynamodb_table)
    seed_permissions(mock_dynamodb_table)
    
    # Create test handler with decorator
    @require_permission('create_crew_member')
    def test_handler(event, context):
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Success'})
        }
    
    # Create event with impersonation
    event = create_mock_event(user_id='admin-123', is_admin=True, is_impersonating=True)
    
    # Call handler
    result = test_handler(event, None)
    
    # Should succeed due to impersonation bypass
    assert result['statusCode'] == 200


def test_decorator_allows_impersonation_to_bypass_data_state(mock_dynamodb_table):
    """Test decorator allows admin impersonation to bypass data state restrictions"""
    # Seed configuration and permissions
    seed_config_during_registration(mock_dynamodb_table)
    seed_permissions(mock_dynamodb_table)
    
    # Seed a crew member that is assigned
    # Use the correct PK/SK structure: PK=TEAM#{team_manager_id}, SK=CREW#{crew_member_id}
    mock_dynamodb_table.put_item(Item={
        'PK': 'TEAM#manager-456',  # team_manager_id from create_mock_event
        'SK': 'CREW#crew-123',
        'crew_member_id': 'crew-123',
        'assigned_boat_id': 'boat-456'
    })
    
    # Create test handler with decorator
    @require_permission('edit_crew_member')
    def test_handler(event, context):
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Success'})
        }
    
    # Create event with impersonation and assigned crew member
    event = create_mock_event(
        user_id='admin-123',
        is_admin=True,
        is_impersonating=True,
        body={'crew_member_id': 'crew-123'}
    )
    event['pathParameters'] = {'crew_member_id': 'crew-123'}
    
    # Call handler
    result = test_handler(event, None)
    
    # Should succeed - admin impersonation bypasses ALL restrictions
    assert result['statusCode'] == 200
    body = json.loads(result['body'])
    assert body['message'] == 'Success'


def test_decorator_handles_json_body():
    """Test decorator correctly parses JSON body"""
    event = create_mock_event(
        user_id='user-123',
        is_admin=False,
        body={'name': 'Test', 'email': 'test@example.com'}
    )
    
    # Verify body is JSON string
    assert isinstance(event['body'], str)
    
    # Context extraction should handle it
    context = get_user_context_from_event(event)
    assert context.user_id == 'user-123'


def test_decorator_handles_empty_body():
    """Test decorator handles empty or missing body"""
    event = create_mock_event(user_id='user-123', is_admin=False)
    event['body'] = ''
    
    context = get_user_context_from_event(event)
    assert context.user_id == 'user-123'


def test_decorator_returns_403_with_correct_structure(mock_dynamodb_table):
    """Test decorator returns properly structured 403 response"""
    # Seed configuration and permissions
    seed_config_after_registration(mock_dynamodb_table)
    seed_permissions(mock_dynamodb_table)
    
    # Create test handler with decorator
    @require_permission('create_crew_member')
    def test_handler(event, context):
        return {'statusCode': 200}
    
    # Create event
    event = create_mock_event(user_id='user-123', is_admin=False)
    
    # Call handler
    result = test_handler(event, None)
    
    # Verify 403 structure
    assert result['statusCode'] == 403
    assert 'headers' in result
    assert result['headers']['Content-Type'] == 'application/json'
    assert 'Access-Control-Allow-Origin' in result['headers']
    
    body = json.loads(result['body'])
    assert 'error' in body
    assert 'reason' in body
    assert 'action' in body
    assert body['action'] == 'create_crew_member'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
