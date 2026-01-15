"""
Unit tests for temporary access grant validation in access control system

Tests the check_temporary_access_grant() function with various grant states
and validates automatic expiration marking.

Feature: centralized-access-control
Validates: Requirements 1.2, 1.4
"""
import pytest
from datetime import datetime, timedelta
from moto import mock_dynamodb
import boto3
import os

# Import the access control module
from access_control import PermissionChecker


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


def create_grant(table, user_id, status='active', hours_from_now=48):
    """Helper to create a temporary access grant"""
    now = datetime.utcnow()
    expiration = now + timedelta(hours=hours_from_now)
    
    table.put_item(Item={
        'PK': 'TEMP_ACCESS',
        'SK': f'USER#{user_id}',
        'grant_id': f'grant_{user_id}',
        'user_id': user_id,
        'granted_by_admin_id': 'admin_test',
        'grant_timestamp': now.isoformat() + 'Z',
        'expiration_timestamp': expiration.isoformat() + 'Z',
        'hours': abs(hours_from_now),
        'status': status,
        'notes': 'Test grant',
        'created_at': now.isoformat() + 'Z',
        'updated_at': now.isoformat() + 'Z',
    })


class TestTemporaryAccessGrants:
    """Test temporary access grant validation logic"""
    
    def test_active_grant_returns_true(self, mock_dynamodb_table):
        """Test that an active, non-expired grant returns True"""
        user_id = 'user123'
        
        # Create active grant that expires in 48 hours
        create_grant(mock_dynamodb_table, user_id, status='active', hours_from_now=48)
        
        # Check grant
        checker = PermissionChecker(table_name='test-access-control-table')
        has_grant = checker.check_temporary_access_grant(user_id)
        
        assert has_grant is True
    
    def test_expired_grant_returns_false(self, mock_dynamodb_table):
        """Test that an expired grant returns False"""
        user_id = 'user456'
        
        # Create grant that expired 2 hours ago
        create_grant(mock_dynamodb_table, user_id, status='active', hours_from_now=-2)
        
        # Check grant
        checker = PermissionChecker(table_name='test-access-control-table')
        has_grant = checker.check_temporary_access_grant(user_id)
        
        assert has_grant is False
    
    def test_expired_grant_marked_as_expired(self, mock_dynamodb_table):
        """Test that expired grant is automatically marked as expired in database"""
        user_id = 'user789'
        
        # Create grant that expired 2 hours ago
        create_grant(mock_dynamodb_table, user_id, status='active', hours_from_now=-2)
        
        # Check grant (should mark as expired)
        checker = PermissionChecker(table_name='test-access-control-table')
        has_grant = checker.check_temporary_access_grant(user_id)
        
        assert has_grant is False
        
        # Verify grant was marked as expired in database
        response = mock_dynamodb_table.get_item(
            Key={
                'PK': 'TEMP_ACCESS',
                'SK': f'USER#{user_id}'
            }
        )
        
        assert 'Item' in response
        assert response['Item']['status'] == 'expired'
        assert 'updated_at' in response['Item']
    
    def test_no_grant_returns_false(self, mock_dynamodb_table):
        """Test that user with no grant returns False"""
        user_id = 'user_no_grant'
        
        # Don't create any grant
        
        # Check grant
        checker = PermissionChecker(table_name='test-access-control-table')
        has_grant = checker.check_temporary_access_grant(user_id)
        
        assert has_grant is False
    
    def test_revoked_grant_returns_false(self, mock_dynamodb_table):
        """Test that a revoked grant returns False"""
        user_id = 'user_revoked'
        
        # Create revoked grant
        create_grant(mock_dynamodb_table, user_id, status='revoked', hours_from_now=48)
        
        # Check grant
        checker = PermissionChecker(table_name='test-access-control-table')
        has_grant = checker.check_temporary_access_grant(user_id)
        
        assert has_grant is False
    
    def test_already_expired_status_returns_false(self, mock_dynamodb_table):
        """Test that grant with status='expired' returns False"""
        user_id = 'user_already_expired'
        
        # Create grant with expired status
        create_grant(mock_dynamodb_table, user_id, status='expired', hours_from_now=48)
        
        # Check grant
        checker = PermissionChecker(table_name='test-access-control-table')
        has_grant = checker.check_temporary_access_grant(user_id)
        
        assert has_grant is False
    
    def test_grant_without_expiration_timestamp_returns_false(self, mock_dynamodb_table):
        """Test that grant missing expiration_timestamp returns False"""
        user_id = 'user_no_expiration'
        
        # Create grant without expiration timestamp
        now = datetime.utcnow()
        mock_dynamodb_table.put_item(Item={
            'PK': 'TEMP_ACCESS',
            'SK': f'USER#{user_id}',
            'grant_id': f'grant_{user_id}',
            'user_id': user_id,
            'granted_by_admin_id': 'admin_test',
            'grant_timestamp': now.isoformat() + 'Z',
            # Missing expiration_timestamp
            'hours': 48,
            'status': 'active',
            'notes': 'Test grant',
            'created_at': now.isoformat() + 'Z',
            'updated_at': now.isoformat() + 'Z',
        })
        
        # Check grant
        checker = PermissionChecker(table_name='test-access-control-table')
        has_grant = checker.check_temporary_access_grant(user_id)
        
        assert has_grant is False
    
    def test_grant_with_invalid_expiration_format_returns_false(self, mock_dynamodb_table):
        """Test that grant with invalid expiration timestamp format returns False"""
        user_id = 'user_invalid_expiration'
        
        # Create grant with invalid expiration format
        now = datetime.utcnow()
        mock_dynamodb_table.put_item(Item={
            'PK': 'TEMP_ACCESS',
            'SK': f'USER#{user_id}',
            'grant_id': f'grant_{user_id}',
            'user_id': user_id,
            'granted_by_admin_id': 'admin_test',
            'grant_timestamp': now.isoformat() + 'Z',
            'expiration_timestamp': 'invalid-date-format',
            'hours': 48,
            'status': 'active',
            'notes': 'Test grant',
            'created_at': now.isoformat() + 'Z',
            'updated_at': now.isoformat() + 'Z',
        })
        
        # Check grant
        checker = PermissionChecker(table_name='test-access-control-table')
        has_grant = checker.check_temporary_access_grant(user_id)
        
        assert has_grant is False
    
    def test_grant_expiring_soon_returns_true(self, mock_dynamodb_table):
        """Test that grant expiring in 1 hour still returns True"""
        user_id = 'user_expiring_soon'
        
        # Create grant expiring in 1 hour
        create_grant(mock_dynamodb_table, user_id, status='active', hours_from_now=1)
        
        # Check grant
        checker = PermissionChecker(table_name='test-access-control-table')
        has_grant = checker.check_temporary_access_grant(user_id)
        
        assert has_grant is True
    
    def test_grant_just_expired_returns_false(self, mock_dynamodb_table):
        """Test that grant expired 1 minute ago returns False"""
        user_id = 'user_just_expired'
        
        # Create grant that expired 1 minute ago (negative hours)
        now = datetime.utcnow()
        expiration = now - timedelta(minutes=1)
        
        mock_dynamodb_table.put_item(Item={
            'PK': 'TEMP_ACCESS',
            'SK': f'USER#{user_id}',
            'grant_id': f'grant_{user_id}',
            'user_id': user_id,
            'granted_by_admin_id': 'admin_test',
            'grant_timestamp': (now - timedelta(hours=48)).isoformat() + 'Z',
            'expiration_timestamp': expiration.isoformat() + 'Z',
            'hours': 48,
            'status': 'active',
            'notes': 'Test grant',
            'created_at': now.isoformat() + 'Z',
            'updated_at': now.isoformat() + 'Z',
        })
        
        # Check grant
        checker = PermissionChecker(table_name='test-access-control-table')
        has_grant = checker.check_temporary_access_grant(user_id)
        
        assert has_grant is False
    
    def test_date_only_format_support(self, mock_dynamodb_table):
        """Test that date-only format (YYYY-MM-DD) is supported for expiration"""
        user_id = 'user_date_only'
        
        # Create grant with date-only expiration (tomorrow)
        now = datetime.utcnow()
        tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')
        
        mock_dynamodb_table.put_item(Item={
            'PK': 'TEMP_ACCESS',
            'SK': f'USER#{user_id}',
            'grant_id': f'grant_{user_id}',
            'user_id': user_id,
            'granted_by_admin_id': 'admin_test',
            'grant_timestamp': now.isoformat() + 'Z',
            'expiration_timestamp': tomorrow,  # Date-only format
            'hours': 24,
            'status': 'active',
            'notes': 'Test grant',
            'created_at': now.isoformat() + 'Z',
            'updated_at': now.isoformat() + 'Z',
        })
        
        # Check grant
        checker = PermissionChecker(table_name='test-access-control-table')
        has_grant = checker.check_temporary_access_grant(user_id)
        
        assert has_grant is True
