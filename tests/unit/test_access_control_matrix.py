"""
Unit tests for permission matrix retrieval in access control system.

Tests:
- Loading matrix from database
- Caching behavior
- Fallback to defaults when missing
"""
import pytest
import time
from unittest.mock import MagicMock, patch
from datetime import datetime
import sys
import os

# Add functions/shared to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/shared'))

from access_control import PermissionChecker, DEFAULT_PERMISSIONS


@pytest.fixture
def mock_dynamodb():
    """Create a mock DynamoDB resource"""
    mock_db = MagicMock()
    mock_table = MagicMock()
    mock_db.Table.return_value = mock_table
    return mock_db, mock_table


def test_get_permission_matrix_from_database(mock_dynamodb):
    """Test loading permission matrix from database"""
    mock_db, mock_table = mock_dynamodb
    
    # Mock database response with permission matrix
    mock_table.get_item.return_value = {
        'Item': {
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
            }
        }
    }
    
    # Create checker with mock database
    with patch('configuration.ConfigurationManager') as mock_config_manager:
        mock_config_manager.return_value.table_name = 'test-table'
        checker = PermissionChecker(db_client=mock_db, table_name='test-table')
        
        # Get permission matrix
        matrix = checker.get_permission_matrix()
        
        # Verify database was queried
        mock_table.get_item.assert_called_once_with(
            Key={'PK': 'CONFIG', 'SK': 'PERMISSIONS'}
        )
        
        # Verify matrix was returned
        assert 'create_crew_member' in matrix
        assert matrix['create_crew_member']['during_registration'] is True
        assert 'edit_crew_member' in matrix
        assert matrix['edit_crew_member']['requires_not_assigned'] is True


def test_get_permission_matrix_caching(mock_dynamodb):
    """Test that permission matrix is cached for 60 seconds"""
    mock_db, mock_table = mock_dynamodb
    
    # Mock database response
    mock_table.get_item.return_value = {
        'Item': {
            'PK': 'CONFIG',
            'SK': 'PERMISSIONS',
            'permissions': {
                'create_crew_member': {
                    'during_registration': True,
                }
            }
        }
    }
    
    # Create checker with mock database
    with patch('configuration.ConfigurationManager') as mock_config_manager:
        mock_config_manager.return_value.table_name = 'test-table'
        checker = PermissionChecker(db_client=mock_db, table_name='test-table')
        
        # First call - should query database
        matrix1 = checker.get_permission_matrix()
        assert mock_table.get_item.call_count == 1
        
        # Second call within TTL - should use cache
        matrix2 = checker.get_permission_matrix()
        assert mock_table.get_item.call_count == 1  # No additional call
        
        # Verify same result
        assert matrix1 == matrix2


def test_get_permission_matrix_cache_expiration(mock_dynamodb):
    """Test that cache expires after TTL"""
    mock_db, mock_table = mock_dynamodb
    
    # Mock database response
    mock_table.get_item.return_value = {
        'Item': {
            'PK': 'CONFIG',
            'SK': 'PERMISSIONS',
            'permissions': {
                'create_crew_member': {
                    'during_registration': True,
                }
            }
        }
    }
    
    # Create checker with short TTL for testing
    with patch('configuration.ConfigurationManager') as mock_config_manager:
        mock_config_manager.return_value.table_name = 'test-table'
        checker = PermissionChecker(db_client=mock_db, table_name='test-table', cache_ttl=1)
        
        # First call
        matrix1 = checker.get_permission_matrix()
        assert mock_table.get_item.call_count == 1
        
        # Wait for cache to expire
        time.sleep(1.1)
        
        # Second call after TTL - should query database again
        matrix2 = checker.get_permission_matrix()
        assert mock_table.get_item.call_count == 2


def test_get_permission_matrix_missing_config(mock_dynamodb):
    """Test fallback to defaults when configuration is missing"""
    mock_db, mock_table = mock_dynamodb
    
    # Mock database response with no Item
    mock_table.get_item.return_value = {}
    
    # Create checker with mock database
    with patch('configuration.ConfigurationManager') as mock_config_manager:
        mock_config_manager.return_value.table_name = 'test-table'
        checker = PermissionChecker(db_client=mock_db, table_name='test-table')
        
        # Get permission matrix
        matrix = checker.get_permission_matrix()
        
        # Verify defaults were returned
        assert matrix == DEFAULT_PERMISSIONS


def test_get_permission_matrix_database_error(mock_dynamodb):
    """Test fallback to defaults when database query fails"""
    mock_db, mock_table = mock_dynamodb
    
    # Mock database error
    mock_table.get_item.side_effect = Exception("Database error")
    
    # Create checker with mock database
    with patch('configuration.ConfigurationManager') as mock_config_manager:
        mock_config_manager.return_value.table_name = 'test-table'
        checker = PermissionChecker(db_client=mock_db, table_name='test-table')
        
        # Get permission matrix - should not raise exception
        matrix = checker.get_permission_matrix()
        
        # Verify defaults were returned
        assert matrix == DEFAULT_PERMISSIONS


def test_get_permission_matrix_cache_invalidation(mock_dynamodb):
    """Test that cache can be invalidated"""
    mock_db, mock_table = mock_dynamodb
    
    # Mock database response
    mock_table.get_item.return_value = {
        'Item': {
            'PK': 'CONFIG',
            'SK': 'PERMISSIONS',
            'permissions': {
                'create_crew_member': {
                    'during_registration': True,
                }
            }
        }
    }
    
    # Create checker with mock database
    with patch('configuration.ConfigurationManager') as mock_config_manager:
        mock_config_manager.return_value.table_name = 'test-table'
        checker = PermissionChecker(db_client=mock_db, table_name='test-table')
        
        # First call
        matrix1 = checker.get_permission_matrix()
        assert mock_table.get_item.call_count == 1
        
        # Invalidate cache
        checker.invalidate_cache()
        
        # Second call after invalidation - should query database again
        matrix2 = checker.get_permission_matrix()
        assert mock_table.get_item.call_count == 2


def test_get_permission_matrix_all_actions():
    """Test that default matrix includes all required actions"""
    checker = PermissionChecker()
    matrix = checker.get_permission_matrix()
    
    # Verify all required actions are present
    required_actions = [
        'create_crew_member',
        'edit_crew_member',
        'delete_crew_member',
        'create_boat_registration',
        'edit_boat_registration',
        'delete_boat_registration',
        'process_payment',
        'view_data',
        'export_data',
    ]
    
    for action in required_actions:
        assert action in matrix, f"Action {action} missing from matrix"


def test_get_permission_matrix_phase_keys():
    """Test that each action has all phase keys"""
    checker = PermissionChecker()
    matrix = checker.get_permission_matrix()
    
    required_phases = [
        'before_registration',
        'during_registration',
        'after_registration',
        'after_payment_deadline',
    ]
    
    for action, rules in matrix.items():
        for phase in required_phases:
            assert phase in rules, f"Phase {phase} missing from action {action}"
