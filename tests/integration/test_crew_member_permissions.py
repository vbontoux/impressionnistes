"""
Integration tests for crew member permission checks
Tests that permission system correctly enforces access control rules
"""
import json
import pytest
from datetime import datetime, timedelta


def test_create_crew_member_during_registration_success(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id
):
    """Test creating crew member during registration period succeeds"""
    # Set registration period to be active (current date is within period)
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
    
    
    # Import Lambda handler
    from crew.create_crew_member import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='POST',
        path='/crew',
        body=json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'license_number': 'ABC123',
            'club_affiliation': 'Test Club'
        }),
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert success
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'crew_member_id' in body['data']


def test_create_crew_member_after_registration_denied(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id
):
    """Test creating crew member after registration closes is denied"""
    # Set registration period to be closed (current date is after end date)
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
    
    
    # Import Lambda handler
    from crew.create_crew_member import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='POST',
        path='/crew',
        body=json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'license_number': 'ABC456',
            'club_affiliation': 'Test Club'
        }),
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert denied
    assert response['statusCode'] == 403
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'error' in body


def test_edit_assigned_crew_member_denied(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id
):
    """Test editing assigned crew member is denied due to data state restriction"""
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
    
    
    # Create a crew member assigned to a boat
    crew_member_id = 'crew-assigned-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'CREW#{crew_member_id}',
        'crew_member_id': crew_member_id,
        'first_name': 'Assigned',
        'last_name': 'Rower',
        'date_of_birth': '1990-01-01',
        'gender': 'M',
        'license_number': 'LIC789',
        'club_affiliation': 'Test Club',
        'assigned_boat_id': 'boat-123'  # Assigned to a boat
    })
    
    # Import Lambda handler
    from crew.update_crew_member import lambda_handler
    
    # Try to update the assigned crew member
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/crew/{crew_member_id}',
        body=json.dumps({
            'first_name': 'Updated',
            'last_name': 'Rower',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'license_number': 'LIC789',
            'club_affiliation': 'Test Club'
        }),
        path_parameters={'crew_member_id': crew_member_id},
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert denied due to data state restriction
    assert response['statusCode'] == 403
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'error' in body


def test_admin_impersonation_bypasses_phase_restrictions(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_admin_id
):
    """Test admin impersonation bypasses event phase restrictions"""
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
    
    
    # Import Lambda handler
    from crew.create_crew_member import lambda_handler
    
    # Create API Gateway event with admin impersonation
    event = mock_api_gateway_event(
        http_method='POST',
        path='/crew',
        body=json.dumps({
            'first_name': 'Admin',
            'last_name': 'Created',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'license_number': 'ADMIN123',
            'club_affiliation': 'Test Club'
        }),
        user_id=test_admin_id,
        groups=['admins']
    )
    
    # Add impersonation context
    event['requestContext']['authorizer']['claims']['custom:impersonated_user_id'] = test_team_manager_id
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert success - admin can bypass phase restrictions
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'crew_member_id' in body['data']
    
    # Verify audit log was created for impersonation
    # Query for audit logs
    audit_items = dynamodb_table.query(
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={':pk': 'AUDIT#PERMISSION_BYPASS'}
    )
    
    # Should have at least one audit log entry
    assert audit_items['Count'] > 0


def test_admin_impersonation_bypasses_data_state_restrictions(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_admin_id
):
    """Test admin impersonation bypasses data state restrictions"""
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
    
    
    # Create a crew member assigned to a boat
    crew_member_id = 'crew-admin-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'CREW#{crew_member_id}',
        'crew_member_id': crew_member_id,
        'first_name': 'Assigned',
        'last_name': 'Rower',
        'date_of_birth': '1990-01-01',
        'gender': 'M',
        'license_number': 'LICADMIN',
        'club_affiliation': 'Test Club',
        'assigned_boat_id': 'boat-456'  # Assigned to a boat
    })
    
    # Import Lambda handler
    from crew.update_crew_member import lambda_handler
    
    # Try to update the assigned crew member as admin (should succeed with impersonation)
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/crew/{crew_member_id}',
        body=json.dumps({
            'first_name': 'Updated',
            'last_name': 'Rower',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'license_number': 'LICADMIN-UPDATED',
            'club_affiliation': 'Test Club'
        }),
        path_parameters={'crew_member_id': crew_member_id},
        user_id=test_admin_id,
        groups=['admins']
    )
    
    # Add impersonation context
    event['requestContext']['authorizer']['claims']['custom:impersonated_user_id'] = test_team_manager_id
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert success - admin can bypass ALL restrictions including data state
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    # Verify the update was applied
    updated_crew = dynamodb_table.get_item(
        Key={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'CREW#{crew_member_id}'
        }
    )['Item']
    assert updated_crew['license_number'] == 'LICADMIN-UPDATED'
