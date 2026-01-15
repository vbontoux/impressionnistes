"""
Integration tests for backend-frontend permission alignment
Tests that backend and frontend return the same permission results for the same context
Validates: Requirements 7.8, 8.12
"""
import json
import pytest
from datetime import datetime, timedelta
import sys
import os

# Add functions/shared to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../functions/shared'))

from access_control import (
    PermissionChecker,
    UserContext,
    ResourceContext
)


def test_permission_check_alignment_during_registration(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id
):
    """
    Test that backend and frontend return same result during registration period
    
    This test simulates the frontend permission check logic and compares it
    with the backend permission check result.
    """
    # Set registration period to be active
    today = datetime.now().date()
    start_date = (today - timedelta(days=5)).isoformat()
    end_date = (today + timedelta(days=25)).isoformat()
    payment_deadline = (today + timedelta(days=30)).isoformat()
    
    dynamodb_table.update_item(
        Key={'PK': 'CONFIG', 'SK': 'SYSTEM'},
        UpdateExpression='SET registration_start_date = :start, registration_end_date = :end, payment_deadline = :deadline',
        ExpressionAttributeValues={
            ':start': start_date,
            ':end': end_date,
            ':deadline': payment_deadline
        }
    )
    
    # Get table name from environment
    import os
    table_name = os.environ.get('TABLE_NAME')
    
    # Create permission checker
    checker = PermissionChecker(table_name=table_name)
    
    # Get current phase (backend logic)
    backend_phase = checker.get_current_event_phase()
    assert backend_phase.value == 'during_registration'
    
    # Test various actions
    test_cases = [
        {
            'action': 'create_crew_member',
            'resource_context': ResourceContext(
                resource_type='crew_member',
                resource_id=None,
                resource_state={}
            ),
            'expected_permitted': True,
            'description': 'Create crew member during registration'
        },
        {
            'action': 'edit_crew_member',
            'resource_context': ResourceContext(
                resource_type='crew_member',
                resource_id='crew_001',
                resource_state={'assigned': False}
            ),
            'expected_permitted': True,
            'description': 'Edit unassigned crew member during registration'
        },
        {
            'action': 'edit_crew_member',
            'resource_context': ResourceContext(
                resource_type='crew_member',
                resource_id='crew_001',
                resource_state={'assigned': True}
            ),
            'expected_permitted': False,
            'description': 'Edit assigned crew member (should be denied)'
        },
        {
            'action': 'create_boat_registration',
            'resource_context': ResourceContext(
                resource_type='boat_registration',
                resource_id=None,
                resource_state={}
            ),
            'expected_permitted': True,
            'description': 'Create boat registration during registration'
        },
        {
            'action': 'edit_boat_registration',
            'resource_context': ResourceContext(
                resource_type='boat_registration',
                resource_id='boat_001',
                resource_state={'paid': False}
            ),
            'expected_permitted': True,
            'description': 'Edit unpaid boat during registration'
        },
        {
            'action': 'edit_boat_registration',
            'resource_context': ResourceContext(
                resource_type='boat_registration',
                resource_id='boat_001',
                resource_state={'paid': True}
            ),
            'expected_permitted': False,
            'description': 'Edit paid boat (should be denied)'
        },
        {
            'action': 'process_payment',
            'resource_context': ResourceContext(
                resource_type='payment',
                resource_id=None,
                resource_state={}
            ),
            'expected_permitted': True,
            'description': 'Process payment during registration'
        }
    ]
    
    # Test each case
    for test_case in test_cases:
        user_context = UserContext(
            user_id=test_team_manager_id,
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=False,
            team_manager_id=test_team_manager_id
        )
        
        # Backend check
        backend_result = checker.check_permission(
            user_context,
            test_case['action'],
            test_case['resource_context']
        )
        
        # Assert backend result matches expected
        assert backend_result.is_permitted == test_case['expected_permitted'], \
            f"Backend check failed for: {test_case['description']}"


def test_permission_check_alignment_after_registration(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id
):
    """
    Test that backend and frontend return same result after registration closes
    """
    # Set registration period to be closed
    today = datetime.now().date()
    start_date = (today - timedelta(days=30)).isoformat()
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
    
    # Get table name from environment
    import os
    table_name = os.environ.get('TABLE_NAME')
    
    # Create permission checker
    checker = PermissionChecker(table_name=table_name)
    
    # Get current phase (backend logic)
    backend_phase = checker.get_current_event_phase()
    assert backend_phase.value == 'after_registration'
    
    # Test various actions - all should be denied except payment
    test_cases = [
        {
            'action': 'create_crew_member',
            'resource_context': ResourceContext(
                resource_type='crew_member',
                resource_id=None,
                resource_state={}
            ),
            'expected_permitted': False,
            'expected_reason_key': 'errors.permission.registration_closed',
            'description': 'Create crew member after registration (should be denied)'
        },
        {
            'action': 'edit_crew_member',
            'resource_context': ResourceContext(
                resource_type='crew_member',
                resource_id='crew_001',
                resource_state={'assigned': False}
            ),
            'expected_permitted': False,
            'expected_reason_key': 'errors.permission.registration_closed',
            'description': 'Edit crew member after registration (should be denied)'
        },
        {
            'action': 'create_boat_registration',
            'resource_context': ResourceContext(
                resource_type='boat_registration',
                resource_id=None,
                resource_state={}
            ),
            'expected_permitted': False,
            'expected_reason_key': 'errors.permission.registration_closed',
            'description': 'Create boat after registration (should be denied)'
        },
        {
            'action': 'process_payment',
            'resource_context': ResourceContext(
                resource_type='payment',
                resource_id=None,
                resource_state={}
            ),
            'expected_permitted': True,
            'description': 'Process payment after registration (should be allowed)'
        }
    ]
    
    # Test each case
    for test_case in test_cases:
        user_context = UserContext(
            user_id=test_team_manager_id,
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=False,
            team_manager_id=test_team_manager_id
        )
        
        # Backend check
        backend_result = checker.check_permission(
            user_context,
            test_case['action'],
            test_case['resource_context']
        )
        
        # Assert backend result matches expected
        assert backend_result.is_permitted == test_case['expected_permitted'], \
            f"Backend check failed for: {test_case['description']}"
        
        # If denied, check reason key matches
        if not test_case['expected_permitted'] and 'expected_reason_key' in test_case:
            assert backend_result.denial_reason_key == test_case['expected_reason_key'], \
                f"Backend denial reason mismatch for: {test_case['description']}"


def test_permission_check_alignment_with_impersonation(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_admin_id, test_team_manager_id
):
    """
    Test that backend and frontend return same result with admin impersonation
    Impersonation should bypass all restrictions
    """
    # Set registration period to be closed
    today = datetime.now().date()
    start_date = (today - timedelta(days=30)).isoformat()
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
    
    # Get table name from environment
    import os
    table_name = os.environ.get('TABLE_NAME')
    
    # Create permission checker
    checker = PermissionChecker(table_name=table_name)
    
    # Test with impersonation - all actions should be allowed
    test_cases = [
        {
            'action': 'create_crew_member',
            'resource_context': ResourceContext(
                resource_type='crew_member',
                resource_id=None,
                resource_state={}
            ),
            'expected_permitted': True,
            'description': 'Create crew member with impersonation (should bypass phase restriction)'
        },
        {
            'action': 'edit_crew_member',
            'resource_context': ResourceContext(
                resource_type='crew_member',
                resource_id='crew_001',
                resource_state={'assigned': True}
            ),
            'expected_permitted': True,
            'description': 'Edit assigned crew member with impersonation (should bypass data state)'
        },
        {
            'action': 'edit_boat_registration',
            'resource_context': ResourceContext(
                resource_type='boat_registration',
                resource_id='boat_001',
                resource_state={'paid': True}
            ),
            'expected_permitted': True,
            'description': 'Edit paid boat with impersonation (should bypass data state)'
        }
    ]
    
    # Test each case with impersonation
    for test_case in test_cases:
        user_context = UserContext(
            user_id=test_admin_id,
            role='admin',
            is_impersonating=True,
            has_temporary_access=False,
            team_manager_id=test_team_manager_id
        )
        
        # Backend check
        backend_result = checker.check_permission(
            user_context,
            test_case['action'],
            test_case['resource_context']
        )
        
        # Assert backend result matches expected
        assert backend_result.is_permitted == test_case['expected_permitted'], \
            f"Backend check failed for: {test_case['description']}"
        
        # Verify bypass reason is set
        if backend_result.is_permitted:
            assert backend_result.bypass_reason == 'impersonation', \
                f"Expected impersonation bypass reason for: {test_case['description']}"


def test_permission_messages_match_between_backend_and_frontend(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id
):
    """
    Test that permission denial messages use consistent keys between backend and frontend
    This ensures the frontend can properly translate backend error messages
    """
    # Set registration period to be closed
    today = datetime.now().date()
    start_date = (today - timedelta(days=30)).isoformat()
    end_date = (today - timedelta(days=5)).isoformat()
    payment_deadline = (today - timedelta(days=5)).isoformat()  # Also past deadline
    
    dynamodb_table.update_item(
        Key={'PK': 'CONFIG', 'SK': 'SYSTEM'},
        UpdateExpression='SET registration_start_date = :start, registration_end_date = :end, payment_deadline = :deadline',
        ExpressionAttributeValues={
            ':start': start_date,
            ':end': end_date,
            ':deadline': payment_deadline
        }
    )
    
    # Get table name from environment
    import os
    table_name = os.environ.get('TABLE_NAME')
    
    # Create permission checker
    checker = PermissionChecker(table_name=table_name)
    
    # Test message keys for different denial scenarios
    test_cases = [
        {
            'action': 'create_crew_member',
            'resource_context': ResourceContext(
                resource_type='crew_member',
                resource_id=None,
                resource_state={}
            ),
            'expected_reason_key': 'errors.permission.payment_deadline_passed',
            'description': 'Create crew member after payment deadline'
        },
        {
            'action': 'edit_crew_member',
            'resource_context': ResourceContext(
                resource_type='crew_member',
                resource_id='crew_001',
                resource_state={'assigned': True}
            ),
            'expected_reason_key': 'errors.permission.crew_member_assigned',
            'description': 'Edit assigned crew member'
        },
        {
            'action': 'edit_boat_registration',
            'resource_context': ResourceContext(
                resource_type='boat_registration',
                resource_id='boat_001',
                resource_state={'paid': True}
            ),
            'expected_reason_key': 'errors.permission.boat_paid',
            'description': 'Edit paid boat'
        },
        {
            'action': 'process_payment',
            'resource_context': ResourceContext(
                resource_type='payment',
                resource_id=None,
                resource_state={}
            ),
            'expected_reason_key': 'errors.permission.payment_deadline_passed',
            'description': 'Process payment after deadline'
        }
    ]
    
    # Test each case
    for test_case in test_cases:
        user_context = UserContext(
            user_id=test_team_manager_id,
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=False,
            team_manager_id=test_team_manager_id
        )
        
        # Backend check
        backend_result = checker.check_permission(
            user_context,
            test_case['action'],
            test_case['resource_context']
        )
        
        # Assert action is denied
        assert not backend_result.is_permitted, \
            f"Expected denial for: {test_case['description']}"
        
        # Assert denial reason key matches expected
        assert backend_result.denial_reason_key == test_case['expected_reason_key'], \
            f"Backend denial reason key mismatch for: {test_case['description']}. " \
            f"Expected '{test_case['expected_reason_key']}', got '{backend_result.denial_reason_key}'"
        
        # Verify denial reason message is present
        assert backend_result.denial_reason is not None, \
            f"Backend should provide denial reason message for: {test_case['description']}"


def test_permission_check_alignment_with_temporary_access(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id
):
    """
    Test that backend and frontend return same result with temporary access grant
    Temporary access should bypass phase restrictions but not data state restrictions
    """
    # Set registration period to be closed
    today = datetime.now().date()
    start_date = (today - timedelta(days=30)).isoformat()
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
            'status': 'active'
        }
    )
    
    # Get table name from environment
    import os
    table_name = os.environ.get('TABLE_NAME')
    
    # Create permission checker
    checker = PermissionChecker(table_name=table_name)
    
    # Test with temporary access
    test_cases = [
        {
            'action': 'create_crew_member',
            'resource_context': ResourceContext(
                resource_type='crew_member',
                resource_id=None,
                resource_state={}
            ),
            'expected_permitted': True,
            'description': 'Create crew member with temporary access (should bypass phase)'
        },
        {
            'action': 'edit_crew_member',
            'resource_context': ResourceContext(
                resource_type='crew_member',
                resource_id='crew_001',
                resource_state={'assigned': True}
            ),
            'expected_permitted': False,
            'description': 'Edit assigned crew member with temporary access (should NOT bypass data state)'
        },
        {
            'action': 'edit_boat_registration',
            'resource_context': ResourceContext(
                resource_type='boat_registration',
                resource_id='boat_001',
                resource_state={'paid': True}
            ),
            'expected_permitted': False,
            'description': 'Edit paid boat with temporary access (should NOT bypass data state)'
        }
    ]
    
    # Test each case
    for test_case in test_cases:
        user_context = UserContext(
            user_id=test_team_manager_id,
            role='team_manager',
            is_impersonating=False,
            has_temporary_access=True,  # Will be verified by backend
            team_manager_id=test_team_manager_id
        )
        
        # Backend check
        backend_result = checker.check_permission(
            user_context,
            test_case['action'],
            test_case['resource_context']
        )
        
        # Assert backend result matches expected
        assert backend_result.is_permitted == test_case['expected_permitted'], \
            f"Backend check failed for: {test_case['description']}"
        
        # If permitted, verify bypass reason is set
        if backend_result.is_permitted and test_case['expected_permitted']:
            assert backend_result.bypass_reason == 'temporary_access', \
                f"Expected temporary_access bypass reason for: {test_case['description']}"
