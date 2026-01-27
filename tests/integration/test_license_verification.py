"""
Integration tests for license verification endpoints
Tests Lambda handlers with mock DynamoDB (admin only)
"""
import json
import pytest


@pytest.fixture
def admin_user_id():
    """Return a test admin user ID"""
    return 'test-admin-user-123'


@pytest.fixture
def mock_admin_event(mock_api_gateway_event, admin_user_id):
    """Factory fixture to create admin API Gateway events"""
    def _create_admin_event(**kwargs):
        # Override groups to include admins
        kwargs['groups'] = ['admins']
        kwargs['user_id'] = kwargs.get('user_id', admin_user_id)
        return mock_api_gateway_event(**kwargs)
    return _create_admin_event


def test_update_single_crew_member_license_verification(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id, admin_user_id):
    """Test updating license verification status for a single crew member"""
    # Create crew member
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-1',
        'crew_member_id': 'crew-1',
        'first_name': 'Alice',
        'last_name': 'Smith',
        'date_of_birth': '1990-01-15',
        'gender': 'F',
        'license_number': 'LIC001',
        'club_affiliation': 'RCPM'
    })
    
    from admin.update_crew_member_license_verification import lambda_handler
    
    # Create admin API Gateway event
    event = mock_admin_event(
        http_method='PATCH',
        path=f'/admin/crew/{test_team_manager_id}/crew-1/license-verification',
        path_parameters={
            'team_manager_id': test_team_manager_id,
            'crew_member_id': 'crew-1'
        },
        body=json.dumps({
            'team_manager_id': test_team_manager_id,  # Also required in body
            'status': 'manually_verified_valid',
            'details': 'Verified manually by admin'
        })
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['license_verification_status'] == 'manually_verified_valid'
    assert body['data']['license_verification_details'] == 'Verified manually by admin'
    assert body['data']['license_verified_by'] == admin_user_id
    assert 'license_verification_date' in body['data']


def test_bulk_update_license_verification(dynamodb_table, mock_admin_event, mock_lambda_context, test_team_manager_id, admin_user_id):
    """Test bulk updating license verification status for multiple crew members"""
    # Create crew members
    for i in range(3):
        dynamodb_table.put_item(Item={
            'PK': f'TEAM#{test_team_manager_id}',
            'SK': f'CREW#crew-{i}',
            'crew_member_id': f'crew-{i}',
            'first_name': f'Member{i}',
            'last_name': f'Last{i}',
            'date_of_birth': '1990-01-15',
            'gender': 'M' if i % 2 == 0 else 'F',
            'license_number': f'LIC00{i}',
            'club_affiliation': 'RCPM'
        })
    
    from admin.bulk_update_license_verification import lambda_handler
    
    # Create admin API Gateway event
    event = mock_admin_event(
        http_method='POST',
        path='/admin/crew/bulk-license-verification',
        body=json.dumps({
            'verifications': [
                {
                    'team_manager_id': test_team_manager_id,
                    'crew_member_id': 'crew-0',
                    'status': 'verified_valid',
                    'details': 'Auto-verified'
                },
                {
                    'team_manager_id': test_team_manager_id,
                    'crew_member_id': 'crew-1',
                    'status': 'manually_verified_invalid',
                    'details': 'License expired'
                },
                {
                    'team_manager_id': test_team_manager_id,
                    'crew_member_id': 'crew-2',
                    'status': 'verified_valid',
                    'details': 'Auto-verified'
                }
            ]
        })
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['success_count'] == 3
    assert body['data']['failure_count'] == 0
    assert len(body['data']['results']) == 3
    
    # Verify all updates succeeded
    for result in body['data']['results']:
        assert result['success'] is True
        assert 'crew_member_id' in result


def test_non_admin_cannot_update_license_verification(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test that non-admin users cannot update license verification"""
    # Create crew member
    dynamodb_table.put_item(Item={
        'PK': f'TEAM#{test_team_manager_id}',
        'SK': 'CREW#crew-1',
        'crew_member_id': 'crew-1',
        'first_name': 'Alice',
        'last_name': 'Smith',
        'date_of_birth': '1990-01-15',
        'gender': 'F',
        'license_number': 'LIC001',
        'club_affiliation': 'RCPM'
    })
    
    from admin.update_crew_member_license_verification import lambda_handler
    
    # Create regular team manager event (not admin)
    event = mock_api_gateway_event(
        http_method='PATCH',
        path=f'/admin/crew/{test_team_manager_id}/crew-1/license-verification',
        path_parameters={
            'team_manager_id': test_team_manager_id,
            'crew_member_id': 'crew-1'
        },
        body=json.dumps({
            'team_manager_id': test_team_manager_id,  # Also required in body
            'status': 'manually_verified_valid',
            'details': 'Trying to verify'
        }),
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert forbidden response
    assert response['statusCode'] == 403
    
    body = json.loads(response['body'])
    assert body['success'] is False
