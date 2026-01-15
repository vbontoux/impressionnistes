"""
Unit tests for core permission checking logic in access control system

Tests the check_permission() function with various scenarios:
- Phase-based permission evaluation
- Impersonation bypass (phase AND data state - full override)
- Data state restrictions (assigned crew, paid boat)
- Temporary access bypass (phase only, not data state)

Feature: centralized-access-control
Validates: Requirements 3.1-3.6, 4.1, 4.2
"""
import pytest
from datetime import datetime, timedelta
from moto import mock_dynamodb
import boto3
import os
import sys

# Add functions/shared to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/shared'))

from access_control import (
    PermissionChecker,
    UserContext,
    ResourceContext,
    EventPhase
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


def seed_config(table, registration_start, registration_end, payment_deadline):
    """Helper to seed configuration with specific dates"""
    table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'registration_start_date': registration_start,
        'registration_end_date': registration_end,
        'payment_deadline': payment_deadline,
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
            },
            'delete_crew_member': {
                'before_registration': False,
                'during_registration': True,
                'after_registration': False,
                'after_payment_deadline': False,
                'requires_not_assigned': True,
            },
            'edit_boat_registration': {
                'before_registration': False,
                'during_registration': True,
                'after_registration': False,
                'after_payment_deadline': False,
                'requires_not_paid': True,
            },
            'delete_boat_registration': {
                'before_registration': False,
                'during_registration': True,
                'after_registration': False,
                'after_payment_deadline': False,
                'requires_not_paid': True,
            },
            'process_payment': {
                'before_registration': False,
                'during_registration': True,
                'after_registration': True,
                'after_payment_deadline': False,
            },
        }
    })


def create_temp_grant(table, user_id, hours_from_now=48):
    """Helper to create a temporary access grant"""
    now = datetime.utcnow()
    expiration = now + timedelta(hours=hours_from_now)
    
    table.put_item(Item={
        'PK': 'TEMP_ACCESS',
        'SK': f'USER#{user_id}',
        'user_id': user_id,
        'grant_timestamp': now.isoformat() + 'Z',
        'expiration_timestamp': expiration.isoformat() + 'Z',
        'granted_by_admin_id': 'admin_test',
        'status': 'active',
    })


class TestPhaseBasedPermissions:
    """Test phase-based permission evaluation"""
    
    def test_action_allowed_during_registration(self, mock_dynamodb_table):
        """Test that action is allowed during registration period"""
        # Set dates for during registration
        now = datetime.utcnow()
        start = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        end = (now + timedelta(days=20)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=30)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        seed_permissions(mock_dynamodb_table)
        
        # Create user and resource contexts
        user_ctx = UserContext(
            user_id='user123',
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=False
        )
        resource_ctx = ResourceContext(
            resource_type='crew_member',
            resource_state={'assigned': False}
        )
        
        # Check permission
        checker = PermissionChecker(table_name='test-access-control-table')
        result = checker.check_permission(user_ctx, 'create_crew_member', resource_ctx)
        
        assert result.is_permitted is True
        assert result.bypass_reason is None
    
    def test_action_denied_before_registration(self, mock_dynamodb_table):
        """Test that action is denied before registration opens"""
        # Set dates for before registration
        now = datetime.utcnow()
        start = (now + timedelta(days=10)).strftime('%Y-%m-%d')
        end = (now + timedelta(days=40)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=50)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        seed_permissions(mock_dynamodb_table)
        
        # Create user and resource contexts
        user_ctx = UserContext(
            user_id='user123',
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=False
        )
        resource_ctx = ResourceContext(
            resource_type='crew_member',
            resource_state={'assigned': False}
        )
        
        # Check permission
        checker = PermissionChecker(table_name='test-access-control-table')
        result = checker.check_permission(user_ctx, 'create_crew_member', resource_ctx)
        
        assert result.is_permitted is False
        assert result.denial_reason is not None
        assert result.denial_reason_key is not None
    
    def test_action_denied_after_registration(self, mock_dynamodb_table):
        """Test that action is denied after registration closes"""
        # Set dates for after registration
        now = datetime.utcnow()
        start = (now - timedelta(days=40)).strftime('%Y-%m-%d')
        end = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=10)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        seed_permissions(mock_dynamodb_table)
        
        # Create user and resource contexts
        user_ctx = UserContext(
            user_id='user123',
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=False
        )
        resource_ctx = ResourceContext(
            resource_type='crew_member',
            resource_state={'assigned': False}
        )
        
        # Check permission
        checker = PermissionChecker(table_name='test-access-control-table')
        result = checker.check_permission(user_ctx, 'create_crew_member', resource_ctx)
        
        assert result.is_permitted is False
        assert result.denial_reason is not None
    
    def test_payment_allowed_after_registration(self, mock_dynamodb_table):
        """Test that payment is allowed after registration closes"""
        # Set dates for after registration
        now = datetime.utcnow()
        start = (now - timedelta(days=40)).strftime('%Y-%m-%d')
        end = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=10)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        seed_permissions(mock_dynamodb_table)
        
        # Create user and resource contexts
        user_ctx = UserContext(
            user_id='user123',
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=False
        )
        resource_ctx = ResourceContext(
            resource_type='payment',
            resource_state={}
        )
        
        # Check permission
        checker = PermissionChecker(table_name='test-access-control-table')
        result = checker.check_permission(user_ctx, 'process_payment', resource_ctx)
        
        assert result.is_permitted is True


class TestDataStateRestrictions:
    """Test data state restrictions (assigned crew, paid boat)"""
    
    def test_cannot_edit_assigned_crew_member(self, mock_dynamodb_table):
        """Test that assigned crew member cannot be edited"""
        # Set dates for during registration
        now = datetime.utcnow()
        start = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        end = (now + timedelta(days=20)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=30)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        seed_permissions(mock_dynamodb_table)
        
        # Create user and resource contexts with assigned crew member
        user_ctx = UserContext(
            user_id='user123',
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=False
        )
        resource_ctx = ResourceContext(
            resource_type='crew_member',
            resource_state={'assigned': True}  # Crew member is assigned
        )
        
        # Check permission
        checker = PermissionChecker(table_name='test-access-control-table')
        result = checker.check_permission(user_ctx, 'edit_crew_member', resource_ctx)
        
        assert result.is_permitted is False
        assert 'assigned' in result.denial_reason.lower()
    
    def test_can_edit_unassigned_crew_member(self, mock_dynamodb_table):
        """Test that unassigned crew member can be edited"""
        # Set dates for during registration
        now = datetime.utcnow()
        start = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        end = (now + timedelta(days=20)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=30)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        seed_permissions(mock_dynamodb_table)
        
        # Create user and resource contexts with unassigned crew member
        user_ctx = UserContext(
            user_id='user123',
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=False
        )
        resource_ctx = ResourceContext(
            resource_type='crew_member',
            resource_state={'assigned': False}  # Crew member is not assigned
        )
        
        # Check permission
        checker = PermissionChecker(table_name='test-access-control-table')
        result = checker.check_permission(user_ctx, 'edit_crew_member', resource_ctx)
        
        assert result.is_permitted is True
    
    def test_cannot_edit_paid_boat(self, mock_dynamodb_table):
        """Test that paid boat cannot be edited"""
        # Set dates for during registration
        now = datetime.utcnow()
        start = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        end = (now + timedelta(days=20)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=30)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        seed_permissions(mock_dynamodb_table)
        
        # Create user and resource contexts with paid boat
        user_ctx = UserContext(
            user_id='user123',
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=False
        )
        resource_ctx = ResourceContext(
            resource_type='boat_registration',
            resource_state={'paid': True}  # Boat is paid
        )
        
        # Check permission
        checker = PermissionChecker(table_name='test-access-control-table')
        result = checker.check_permission(user_ctx, 'edit_boat_registration', resource_ctx)
        
        assert result.is_permitted is False
        assert 'paid' in result.denial_reason.lower()
    
    def test_cannot_delete_paid_boat(self, mock_dynamodb_table):
        """Test that paid boat cannot be deleted"""
        # Set dates for during registration
        now = datetime.utcnow()
        start = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        end = (now + timedelta(days=20)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=30)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        seed_permissions(mock_dynamodb_table)
        
        # Create user and resource contexts with paid boat
        user_ctx = UserContext(
            user_id='user123',
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=False
        )
        resource_ctx = ResourceContext(
            resource_type='boat_registration',
            resource_state={'paid': True}  # Boat is paid
        )
        
        # Check permission
        checker = PermissionChecker(table_name='test-access-control-table')
        result = checker.check_permission(user_ctx, 'delete_boat_registration', resource_ctx)
        
        assert result.is_permitted is False
        assert 'paid' in result.denial_reason.lower()


class TestImpersonationBypass:
    """Test impersonation bypass (phase AND data state - full override)"""
    
    def test_impersonation_bypasses_phase_restriction(self, mock_dynamodb_table):
        """Test that impersonation bypasses phase restrictions"""
        # Set dates for after registration (normally denied)
        now = datetime.utcnow()
        start = (now - timedelta(days=40)).strftime('%Y-%m-%d')
        end = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=10)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        seed_permissions(mock_dynamodb_table)
        
        # Create user context with impersonation
        user_ctx = UserContext(
            user_id='admin123',
            role='admin',
            is_impersonating=True,  # Admin is impersonating
            has_temporary_access=False,
            team_manager_id='user123'
        )
        resource_ctx = ResourceContext(
            resource_type='crew_member',
            resource_state={'assigned': False}
        )
        
        # Check permission
        checker = PermissionChecker(table_name='test-access-control-table')
        result = checker.check_permission(user_ctx, 'create_crew_member', resource_ctx)
        
        assert result.is_permitted is True
        assert result.bypass_reason == 'impersonation'
    
    def test_impersonation_bypasses_data_state(self, mock_dynamodb_table):
        """Test that impersonation bypasses data state restrictions"""
        # Set dates for during registration
        now = datetime.utcnow()
        start = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        end = (now + timedelta(days=20)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=30)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        seed_permissions(mock_dynamodb_table)
        
        # Create user context with impersonation
        user_ctx = UserContext(
            user_id='admin123',
            role='admin',
            is_impersonating=True,  # Admin is impersonating
            has_temporary_access=False,
            team_manager_id='user123'
        )
        resource_ctx = ResourceContext(
            resource_type='crew_member',
            resource_state={'assigned': True}  # Crew member is assigned
        )
        
        # Check permission
        checker = PermissionChecker(table_name='test-access-control-table')
        result = checker.check_permission(user_ctx, 'edit_crew_member', resource_ctx)
        
        # Should be allowed - impersonation bypasses ALL restrictions
        assert result.is_permitted is True
        assert result.bypass_reason == 'impersonation'
    
    def test_impersonation_bypasses_paid_boat_state(self, mock_dynamodb_table):
        """Test that impersonation bypasses paid boat state restrictions"""
        # Set dates for after registration (normally denied)
        now = datetime.utcnow()
        start = (now - timedelta(days=40)).strftime('%Y-%m-%d')
        end = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=10)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        seed_permissions(mock_dynamodb_table)
        
        # Create user context with impersonation
        user_ctx = UserContext(
            user_id='admin123',
            role='admin',
            is_impersonating=True,  # Admin is impersonating
            has_temporary_access=False,
            team_manager_id='user123'
        )
        resource_ctx = ResourceContext(
            resource_type='boat_registration',
            resource_state={'paid': True}  # Boat is paid
        )
        
        # Check permission
        checker = PermissionChecker(table_name='test-access-control-table')
        result = checker.check_permission(user_ctx, 'edit_boat_registration', resource_ctx)
        
        # Should be allowed - impersonation bypasses ALL restrictions
        assert result.is_permitted is True
        assert result.bypass_reason == 'impersonation'


class TestTemporaryAccessBypass:
    """Test temporary access bypass (phase only, not data state)"""
    
    def test_temporary_access_bypasses_phase_restriction(self, mock_dynamodb_table):
        """Test that temporary access bypasses phase restrictions"""
        # Set dates for after registration (normally denied)
        now = datetime.utcnow()
        start = (now - timedelta(days=40)).strftime('%Y-%m-%d')
        end = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=10)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        seed_permissions(mock_dynamodb_table)
        
        # Create temporary access grant
        user_id = 'user123'
        create_temp_grant(mock_dynamodb_table, user_id, hours_from_now=48)
        
        # Create user context with temporary access
        user_ctx = UserContext(
            user_id=user_id,
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=True  # User has temporary access
        )
        resource_ctx = ResourceContext(
            resource_type='crew_member',
            resource_state={'assigned': False}
        )
        
        # Check permission
        checker = PermissionChecker(table_name='test-access-control-table')
        result = checker.check_permission(user_ctx, 'create_crew_member', resource_ctx)
        
        assert result.is_permitted is True
        assert result.bypass_reason == 'temporary_access'
    
    def test_temporary_access_does_not_bypass_data_state(self, mock_dynamodb_table):
        """Test that temporary access does NOT bypass data state restrictions"""
        # Set dates for during registration
        now = datetime.utcnow()
        start = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        end = (now + timedelta(days=20)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=30)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        seed_permissions(mock_dynamodb_table)
        
        # Create temporary access grant
        user_id = 'user123'
        create_temp_grant(mock_dynamodb_table, user_id, hours_from_now=48)
        
        # Create user context with temporary access
        user_ctx = UserContext(
            user_id=user_id,
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=True  # User has temporary access
        )
        resource_ctx = ResourceContext(
            resource_type='crew_member',
            resource_state={'assigned': True}  # Crew member is assigned
        )
        
        # Check permission
        checker = PermissionChecker(table_name='test-access-control-table')
        result = checker.check_permission(user_ctx, 'edit_crew_member', resource_ctx)
        
        # Should be denied due to data state restriction
        assert result.is_permitted is False
        assert 'assigned' in result.denial_reason.lower()
    
    def test_expired_temporary_access_does_not_bypass(self, mock_dynamodb_table):
        """Test that expired temporary access does not bypass restrictions"""
        # Set dates for after registration (normally denied)
        now = datetime.utcnow()
        start = (now - timedelta(days=40)).strftime('%Y-%m-%d')
        end = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=10)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        seed_permissions(mock_dynamodb_table)
        
        # Create expired temporary access grant
        user_id = 'user123'
        create_temp_grant(mock_dynamodb_table, user_id, hours_from_now=-2)  # Expired 2 hours ago
        
        # Create user context with temporary access flag
        user_ctx = UserContext(
            user_id=user_id,
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=True  # Flag is set but grant is expired
        )
        resource_ctx = ResourceContext(
            resource_type='crew_member',
            resource_state={'assigned': False}
        )
        
        # Check permission
        checker = PermissionChecker(table_name='test-access-control-table')
        result = checker.check_permission(user_ctx, 'create_crew_member', resource_ctx)
        
        # Should be denied because grant is expired
        assert result.is_permitted is False


class TestUnknownAction:
    """Test handling of unknown actions"""
    
    def test_unknown_action_denied(self, mock_dynamodb_table):
        """Test that unknown action is denied"""
        # Set dates for during registration
        now = datetime.utcnow()
        start = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        end = (now + timedelta(days=20)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=30)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        seed_permissions(mock_dynamodb_table)
        
        # Create user and resource contexts
        user_ctx = UserContext(
            user_id='user123',
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=False
        )
        resource_ctx = ResourceContext(
            resource_type='unknown',
            resource_state={}
        )
        
        # Check permission for unknown action
        checker = PermissionChecker(table_name='test-access-control-table')
        result = checker.check_permission(user_ctx, 'unknown_action', resource_ctx)
        
        assert result.is_permitted is False
        assert 'unknown' in result.denial_reason.lower()
