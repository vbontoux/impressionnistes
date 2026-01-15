"""
Unit tests for event phase detection in access control system

Tests the get_current_event_phase() function with various date configurations
and validates caching behavior.

Feature: centralized-access-control
Validates: Requirements 1.1, 1.3
"""
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from moto import mock_dynamodb
import boto3
import os

# Import the access control module
from access_control import PermissionChecker, EventPhase


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


class TestEventPhaseDetection:
    """Test event phase detection logic"""
    
    def test_before_registration_phase(self, mock_dynamodb_table):
        """Test phase detection when current time is before registration starts"""
        # Set dates in the future
        now = datetime.utcnow()
        start = (now + timedelta(days=10)).strftime('%Y-%m-%d')
        end = (now + timedelta(days=40)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=50)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        
        # Create checker and get phase
        checker = PermissionChecker(table_name='test-access-control-table')
        phase = checker.get_current_event_phase()
        
        assert phase == EventPhase.BEFORE_REGISTRATION
    
    def test_during_registration_phase(self, mock_dynamodb_table):
        """Test phase detection when current time is during registration period"""
        # Set dates so we're in the middle of registration
        now = datetime.utcnow()
        start = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        end = (now + timedelta(days=20)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=30)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        
        # Create checker and get phase
        checker = PermissionChecker(table_name='test-access-control-table')
        phase = checker.get_current_event_phase()
        
        assert phase == EventPhase.DURING_REGISTRATION
    
    def test_after_registration_phase(self, mock_dynamodb_table):
        """Test phase detection when registration has closed but payment deadline not passed"""
        # Set dates so registration is closed but payment deadline is in future
        now = datetime.utcnow()
        start = (now - timedelta(days=40)).strftime('%Y-%m-%d')
        end = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=10)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        
        # Create checker and get phase
        checker = PermissionChecker(table_name='test-access-control-table')
        phase = checker.get_current_event_phase()
        
        assert phase == EventPhase.AFTER_REGISTRATION
    
    def test_after_payment_deadline_phase(self, mock_dynamodb_table):
        """Test phase detection when payment deadline has passed"""
        # Set all dates in the past
        now = datetime.utcnow()
        start = (now - timedelta(days=50)).strftime('%Y-%m-%d')
        end = (now - timedelta(days=20)).strftime('%Y-%m-%d')
        deadline = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        
        # Create checker and get phase
        checker = PermissionChecker(table_name='test-access-control-table')
        phase = checker.get_current_event_phase()
        
        assert phase == EventPhase.AFTER_PAYMENT_DEADLINE
    
    def test_phase_caching_within_ttl(self, mock_dynamodb_table):
        """Test that phase is cached and same result returned within TTL"""
        # Set dates for during registration
        now = datetime.utcnow()
        start = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        end = (now + timedelta(days=20)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=30)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        
        # Create checker with short TTL for testing
        checker = PermissionChecker(cache_ttl=5, table_name='test-access-control-table')
        
        # First call - should query database
        phase1 = checker.get_current_event_phase()
        
        # Second call immediately - should use cache
        phase2 = checker.get_current_event_phase()
        
        # Both should return same phase
        assert phase1 == phase2
        assert phase1 == EventPhase.DURING_REGISTRATION
        
        # Verify cache was used (cache time should be set)
        assert checker._phase_cache is not None
        assert checker._phase_cache_time > 0
    
    def test_phase_cache_expiration(self, mock_dynamodb_table):
        """Test that cache expires after TTL and phase is recalculated"""
        # Set dates for during registration
        now = datetime.utcnow()
        start = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        end = (now + timedelta(days=20)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=30)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        
        # Create checker with very short TTL
        checker = PermissionChecker(cache_ttl=1, table_name='test-access-control-table')
        
        # First call
        phase1 = checker.get_current_event_phase()
        cache_time1 = checker._phase_cache_time
        
        # Wait for cache to expire
        time.sleep(1.5)
        
        # Second call - should recalculate
        phase2 = checker.get_current_event_phase()
        cache_time2 = checker._phase_cache_time
        
        # Phase should be same but cache time should be updated
        assert phase1 == phase2
        assert cache_time2 > cache_time1
    
    def test_missing_configuration_defaults_to_restrictive(self, mock_dynamodb_table):
        """Test that missing configuration defaults to most restrictive phase"""
        # Don't seed any configuration
        
        # Create checker and get phase
        checker = PermissionChecker(table_name='test-access-control-table')
        phase = checker.get_current_event_phase()
        
        # Should default to most restrictive phase
        assert phase == EventPhase.AFTER_PAYMENT_DEADLINE
    
    def test_invalid_date_format_defaults_to_restrictive(self, mock_dynamodb_table):
        """Test that invalid date format defaults to most restrictive phase"""
        # Seed with invalid date formats
        mock_dynamodb_table.put_item(Item={
            'PK': 'CONFIG',
            'SK': 'SYSTEM',
            'registration_start_date': 'invalid-date',
            'registration_end_date': 'also-invalid',
            'payment_deadline': 'not-a-date',
            'temporary_editing_access_hours': 48
        })
        
        # Create checker and get phase
        checker = PermissionChecker(table_name='test-access-control-table')
        phase = checker.get_current_event_phase()
        
        # Should default to most restrictive phase
        assert phase == EventPhase.AFTER_PAYMENT_DEADLINE
    
    def test_iso_datetime_format_support(self, mock_dynamodb_table):
        """Test that ISO datetime format (with time) is supported"""
        # Set dates with ISO datetime format
        now = datetime.utcnow()
        start = (now - timedelta(days=10)).isoformat() + 'Z'
        end = (now + timedelta(days=20)).isoformat() + 'Z'
        deadline = (now + timedelta(days=30)).isoformat() + 'Z'
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        
        # Create checker and get phase
        checker = PermissionChecker(table_name='test-access-control-table')
        phase = checker.get_current_event_phase()
        
        assert phase == EventPhase.DURING_REGISTRATION
    
    def test_boundary_condition_registration_start(self, mock_dynamodb_table):
        """Test phase at exact registration start time"""
        # Set start date to now
        now = datetime.utcnow()
        start = now.strftime('%Y-%m-%d')
        end = (now + timedelta(days=30)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=40)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        
        # Create checker and get phase
        checker = PermissionChecker(table_name='test-access-control-table')
        phase = checker.get_current_event_phase()
        
        # Should be during registration (inclusive)
        assert phase == EventPhase.DURING_REGISTRATION
    
    def test_boundary_condition_registration_end(self, mock_dynamodb_table):
        """Test phase at exact registration end time"""
        # Set end date to now
        now = datetime.utcnow()
        start = (now - timedelta(days=30)).strftime('%Y-%m-%d')
        end = now.strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=10)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        
        # Create checker and get phase
        checker = PermissionChecker(table_name='test-access-control-table')
        phase = checker.get_current_event_phase()
        
        # Should be during registration (inclusive)
        assert phase == EventPhase.DURING_REGISTRATION
    
    def test_cache_invalidation(self, mock_dynamodb_table):
        """Test that cache can be manually invalidated"""
        # Set dates for during registration
        now = datetime.utcnow()
        start = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        end = (now + timedelta(days=20)).strftime('%Y-%m-%d')
        deadline = (now + timedelta(days=30)).strftime('%Y-%m-%d')
        
        seed_config(mock_dynamodb_table, start, end, deadline)
        
        # Create checker and get phase
        checker = PermissionChecker(table_name='test-access-control-table')
        phase1 = checker.get_current_event_phase()
        
        # Verify cache is populated
        assert checker._phase_cache is not None
        
        # Invalidate cache
        checker.invalidate_cache()
        
        # Verify cache is cleared
        assert checker._phase_cache is None
        assert checker._phase_cache_time == 0
        
        # Get phase again - should recalculate
        phase2 = checker.get_current_event_phase()
        
        # Should still return same phase
        assert phase1 == phase2
