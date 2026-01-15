"""
Integration tests for boat registration permission checks
Tests that permission system correctly enforces access control rules
"""
import json
import pytest
from datetime import datetime, timedelta


def test_create_boat_registration_during_registration_success(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id
):
    """Test creating boat registration during registration period succeeds"""
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
    from boat.create_boat_registration import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='POST',
        path='/boats',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4+'
        }),
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert success
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert body['success'] is True
    assert 'boat_registration_id' in body['data']


def test_create_boat_registration_after_registration_denied(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id
):
    """Test creating boat registration after registration closes is denied"""
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
    from boat.create_boat_registration import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='POST',
        path='/boats',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4+'
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


def test_edit_paid_boat_denied(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id
):
    """Test editing paid boat is denied due to data state restriction"""
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
    
    # Create a paid boat registration
    boat_registration_id = 'boat-paid-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_registration_id}',
        'boat_registration_id': boat_registration_id,
        'team_manager_id': test_team_manager_id,
        'event_type': '21km',
        'boat_type': '4+',
        'seats': [],
        'registration_status': 'paid',  # Paid boat
        'is_boat_rental': False,
        'boat_request_enabled': False,
        'is_multi_club_crew': False,
        'boat_club_display': 'Test Club',
        'club_list': ['Test Club']
    })
    
    # Import Lambda handler
    from boat.update_boat_registration import lambda_handler
    
    # Try to update the paid boat
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boats/{boat_registration_id}',
        body=json.dumps({
            'event_type': '42km'
        }),
        path_parameters={'boat_registration_id': boat_registration_id},
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert denied due to data state restriction
    assert response['statusCode'] == 403
    body = json.loads(response['body'])
    assert body['success'] is False
    assert 'error' in body


def test_delete_paid_boat_denied(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id
):
    """Test deleting paid boat is denied due to data state restriction"""
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
    
    # Create a paid boat registration
    boat_registration_id = 'boat-paid-delete-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_registration_id}',
        'boat_registration_id': boat_registration_id,
        'team_manager_id': test_team_manager_id,
        'event_type': '21km',
        'boat_type': '4+',
        'seats': [],
        'registration_status': 'paid',  # Paid boat
        'is_boat_rental': False,
        'boat_request_enabled': False,
        'is_multi_club_crew': False,
        'boat_club_display': 'Test Club',
        'club_list': ['Test Club']
    })
    
    # Import Lambda handler
    from boat.delete_boat_registration import lambda_handler
    
    # Try to delete the paid boat
    event = mock_api_gateway_event(
        http_method='DELETE',
        path=f'/boats/{boat_registration_id}',
        path_parameters={'boat_registration_id': boat_registration_id},
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert denied - permission decorator checks data state restrictions
    assert response['statusCode'] == 403
    body = json.loads(response['body'])
    assert body['success'] is False
    # The error message comes from the permission system
    assert 'error' in body


def test_admin_impersonation_bypasses_phase_restrictions_for_boats(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_admin_id
):
    """Test admin impersonation bypasses event phase restrictions for boat operations"""
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
    from boat.create_boat_registration import lambda_handler
    
    # Create API Gateway event with admin impersonation
    event = mock_api_gateway_event(
        http_method='POST',
        path='/boats',
        body=json.dumps({
            'event_type': '21km',
            'boat_type': '4+'
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
    assert 'boat_registration_id' in body['data']
    
    # Verify audit log was created for impersonation
    audit_items = dynamodb_table.query(
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={':pk': 'AUDIT#PERMISSION_BYPASS'}
    )
    
    # Should have at least one audit log entry
    assert audit_items['Count'] > 0


def test_admin_impersonation_bypasses_data_state_for_boats(
    dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id, test_admin_id
):
    """Test admin impersonation bypasses data state restrictions for boats"""
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
    
    # Create a paid boat registration
    boat_registration_id = 'boat-admin-paid-test'
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': f'BOAT#{boat_registration_id}',
        'boat_registration_id': boat_registration_id,
        'team_manager_id': test_team_manager_id,
        'event_type': '21km',
        'boat_type': '4+',
        'seats': [],
        'registration_status': 'paid',  # Paid boat
        'is_boat_rental': False,
        'boat_request_enabled': False,
        'is_multi_club_crew': False,
        'boat_club_display': 'Test Club',
        'club_list': ['Test Club']
    })
    
    # Import Lambda handler
    from boat.update_boat_registration import lambda_handler
    
    # Try to update the paid boat as admin
    event = mock_api_gateway_event(
        http_method='PUT',
        path=f'/boats/{boat_registration_id}',
        body=json.dumps({
            'boat_type': '8+'  # Try to change boat type
        }),
        path_parameters={'boat_registration_id': boat_registration_id},
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
    updated_boat = dynamodb_table.get_item(
        Key={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'BOAT#{boat_registration_id}'
        }
    )['Item']
    assert updated_boat['boat_type'] == '8+'
