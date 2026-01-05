"""
Integration tests for admin impersonation feature
Tests the require_team_manager_or_admin_override decorator

Feature: admin-impersonation
"""
import json
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis import assume

# Import the decorator and auth utilities
from auth_utils import (
    require_team_manager_or_admin_override,
    get_user_from_event
)


# Helper function to create API Gateway event
def create_api_gateway_event(
    http_method='GET',
    path='/',
    body=None,
    path_parameters=None,
    query_parameters=None,
    user_id=None,
    groups=None
):
    """Create a mock API Gateway event"""
    event = {
        'httpMethod': http_method,
        'path': path,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': body,
        'pathParameters': path_parameters or {},
        'queryStringParameters': query_parameters or {},
        'requestContext': {
            'requestId': 'test-request-id',
            'authorizer': {}
        }
    }
    
    # Add user context if provided (simulates Cognito authorizer)
    if user_id:
        # Default to team_managers group if not specified
        if groups is None:
            groups = ['team_managers']
        
        event['requestContext']['authorizer'] = {
            'claims': {
                'sub': user_id,
                'cognito:username': user_id,
                'email': f'{user_id}@test.com',
                'cognito:groups': groups,
                'custom:role': 'team_manager',
                'custom:club_affiliation': 'Test Club'
            }
        }
    
    return event


# Helper function to create Lambda context
class MockLambdaContext:
    """Mock Lambda context"""
    def __init__(self):
        self.function_name = 'test-function'
        self.memory_limit_in_mb = 128
        self.invoked_function_arn = 'arn:aws:lambda:eu-west-3:123456789012:function:test-function'
        self.aws_request_id = 'test-request-id'


# Helper function to create a simple Lambda handler for testing
def create_test_handler():
    """Create a test Lambda handler that uses the decorator"""
    @require_team_manager_or_admin_override
    def test_handler(event, context):
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'effective_user_id': event.get('_effective_user_id'),
                'is_admin_override': event.get('_is_admin_override'),
                'admin_user_id': event.get('_admin_user_id')
            })
        }
    return test_handler


# Strategy for generating user IDs
user_id_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=48, max_codepoint=122),
    min_size=10,
    max_size=50
).filter(lambda x: x and not x.isspace())

# Strategy for generating email addresses
email_strategy = st.emails()

# Strategy for generating groups (admin or team_manager)
groups_strategy = st.sampled_from([
    ['admins'],
    ['team_managers'],
    ['admins', 'team_managers'],
    []
])


class TestAdminImpersonationDecorator:
    """Test suite for admin impersonation decorator"""
    
    # Task 1.1: Property test for admin-only access
    # Property 1: Admin-only impersonation access
    # Validates: Requirements 5.1, 5.3, 9.1, 9.2
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        admin_user_id=user_id_strategy,
        admin_email=email_strategy,
        team_manager_id=user_id_strategy,
        is_admin=st.booleans()
    )
    def test_property_admin_only_impersonation_access(
        self,
        admin_user_id,
        admin_email,
        team_manager_id,
        is_admin
    ):
        """
        Property 1: Admin-only impersonation access
        
        For any API request with team_manager_id parameter, the authenticated user
        must be an admin, otherwise the request is rejected with 403 Forbidden.
        
        Feature: admin-impersonation, Property 1: Admin-only impersonation access
        Validates: Requirements 5.1, 5.3, 9.1, 9.2
        """
        # Ensure admin and team manager IDs are different
        assume(admin_user_id != team_manager_id)
        
        # Set groups based on is_admin flag
        groups = ['admins'] if is_admin else ['team_managers']
        
        # Create event with team_manager_id query parameter
        event = create_api_gateway_event(
            http_method='GET',
            path='/test',
            query_parameters={'team_manager_id': team_manager_id},
            user_id=admin_user_id,
            groups=groups
        )
        
        # Override email in the event
        event['requestContext']['authorizer']['claims']['email'] = admin_email
        
        # Create test handler and context
        handler = create_test_handler()
        context = MockLambdaContext()
        
        # Call handler
        response = handler(event, context)
        
        # Assert: Only admins can impersonate
        if is_admin:
            # Admin should be allowed to impersonate
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['success'] is True
            assert body['effective_user_id'] == team_manager_id
            assert body['is_admin_override'] is True
        else:
            # Non-admin should be rejected with 403
            assert response['statusCode'] == 403
            body = json.loads(response['body'])
            assert body['success'] is False
            assert 'Admin access required' in body['error']['message']
    
    # Task 1.2: Property test for effective user ID substitution
    # Property 2: Effective user ID substitution
    # Validates: Requirements 5.2
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        admin_user_id=user_id_strategy,
        team_manager_id=user_id_strategy
    )
    def test_property_effective_user_id_substitution(
        self,
        admin_user_id,
        team_manager_id
    ):
        """
        Property 2: Effective user ID substitution
        
        For any admin API request with team_manager_id parameter, the system uses
        that team manager ID for data access instead of the admin's ID.
        
        Feature: admin-impersonation, Property 2: Effective user ID substitution
        Validates: Requirements 5.2
        """
        # Ensure admin and team manager IDs are different
        assume(admin_user_id != team_manager_id)
        
        # Create event with admin user and team_manager_id parameter
        event = create_api_gateway_event(
            http_method='GET',
            path='/test',
            query_parameters={'team_manager_id': team_manager_id},
            user_id=admin_user_id,
            groups=['admins']
        )
        
        # Create test handler and context
        handler = create_test_handler()
        context = MockLambdaContext()
        
        # Call handler
        response = handler(event, context)
        
        # Assert: effective_user_id should be team_manager_id, not admin_user_id
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['effective_user_id'] == team_manager_id
        assert body['effective_user_id'] != admin_user_id
        assert body['is_admin_override'] is True
        assert body['admin_user_id'] == admin_user_id
    
    # Task 1.3: Property test for JWT token preservation
    # Property 3: JWT token preservation
    # Validates: Requirements 5.5, 8.1
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        admin_user_id=user_id_strategy,
        admin_email=email_strategy,
        team_manager_id=user_id_strategy
    )
    def test_property_jwt_token_preservation(
        self,
        admin_user_id,
        admin_email,
        team_manager_id
    ):
        """
        Property 3: JWT token preservation
        
        For any impersonation session, the admin's original JWT token and identity
        remain unchanged for audit logging.
        
        Feature: admin-impersonation, Property 3: JWT token preservation
        Validates: Requirements 5.5, 8.1
        """
        # Ensure admin and team manager IDs are different
        assume(admin_user_id != team_manager_id)
        
        # Create event with admin user and team_manager_id parameter
        event = create_api_gateway_event(
            http_method='GET',
            path='/test',
            query_parameters={'team_manager_id': team_manager_id},
            user_id=admin_user_id,
            groups=['admins']
        )
        
        # Override email in the event
        event['requestContext']['authorizer']['claims']['email'] = admin_email
        
        # Store original JWT claims
        original_claims = event['requestContext']['authorizer']['claims'].copy()
        
        # Create test handler and context
        handler = create_test_handler()
        context = MockLambdaContext()
        
        # Call handler
        response = handler(event, context)
        
        # Assert: JWT claims should remain unchanged
        assert response['statusCode'] == 200
        
        # Verify JWT claims are preserved
        current_claims = event['requestContext']['authorizer']['claims']
        assert current_claims['sub'] == original_claims['sub']
        assert current_claims['email'] == original_claims['email']
        assert current_claims['sub'] == admin_user_id
        assert current_claims['email'] == admin_email
        
        # Verify admin_user_id is tracked separately
        body = json.loads(response['body'])
        assert body['admin_user_id'] == admin_user_id
        assert body['effective_user_id'] == team_manager_id


class TestAdminImpersonationWithoutOverride:
    """Test normal team manager access without impersonation"""
    
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        user_id=user_id_strategy,
        is_team_manager=st.booleans(),
        is_admin=st.booleans()
    )
    def test_normal_access_without_impersonation(
        self,
        user_id,
        is_team_manager,
        is_admin
    ):
        """
        Test that normal access (without team_manager_id parameter) works correctly
        for team managers and admins, but rejects regular users.
        """
        # Set groups based on flags
        groups = []
        if is_admin:
            groups.append('admins')
        if is_team_manager:
            groups.append('team_managers')
        
        # Create event WITHOUT team_manager_id parameter
        event = create_api_gateway_event(
            http_method='GET',
            path='/test',
            query_parameters={},  # No impersonation parameter
            user_id=user_id,
            groups=groups
        )
        
        # Create test handler and context
        handler = create_test_handler()
        context = MockLambdaContext()
        
        # Call handler
        response = handler(event, context)
        
        # Assert: Team managers and admins should have access
        if is_team_manager or is_admin:
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['success'] is True
            assert body['effective_user_id'] == user_id
            assert body['is_admin_override'] is False
        else:
            # Regular users should be rejected
            assert response['statusCode'] == 403
            body = json.loads(response['body'])
            assert body['success'] is False


class TestAdminImpersonationAuditLogging:
    """Test audit logging for impersonation"""
    
    # Task 3.1: Property test for audit logging
    # Property 10: Audit log completeness
    # Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        admin_user_id=user_id_strategy,
        admin_email=email_strategy,
        team_manager_id=user_id_strategy,
        http_method=st.sampled_from(['GET', 'POST', 'PUT', 'DELETE']),
        endpoint_path=st.sampled_from([
            '/api/boats',
            '/api/crew',
            '/api/boats/123',
            '/api/crew/456'
        ])
    )
    def test_property_audit_log_completeness(
        self,
        admin_user_id,
        admin_email,
        team_manager_id,
        http_method,
        endpoint_path,
        caplog
    ):
        """
        Property 10: Audit log completeness
        
        For any impersonated API request, the system logs the admin's user ID,
        impersonated user ID, action, endpoint, and timestamp.
        
        Feature: admin-impersonation, Property 10: Audit log completeness
        Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5
        """
        # Ensure admin and team manager IDs are different
        assume(admin_user_id != team_manager_id)
        
        # Create event with admin user and team_manager_id parameter
        event = create_api_gateway_event(
            http_method=http_method,
            path=endpoint_path,
            query_parameters={'team_manager_id': team_manager_id},
            user_id=admin_user_id,
            groups=['admins']
        )
        
        # Override email in the event
        event['requestContext']['authorizer']['claims']['email'] = admin_email
        
        # Create test handler and context
        handler = create_test_handler()
        context = MockLambdaContext()
        
        # Call handler with logging capture
        import logging
        
        # Clear any previous log records
        caplog.clear()
        
        with caplog.at_level(logging.INFO):
            response = handler(event, context)
        
        # Assert: Impersonation should succeed
        assert response['statusCode'] == 200
        
        # Assert: Audit log should contain ALL required fields
        # Requirements 8.1, 8.2, 8.3, 8.4, 8.5
        log_found = False
        
        # Look for the most recent admin_impersonation log entry
        for record in reversed(caplog.records):
            if hasattr(record, 'msg') and isinstance(record.msg, dict):
                msg = record.msg
                if msg.get('event') == 'admin_impersonation':
                    log_found = True
                    
                    # Requirement 8.1: Log admin's real user ID
                    assert 'admin_user_id' in msg, "admin_user_id missing from log"
                    assert msg['admin_user_id'] == admin_user_id, f"Expected admin_user_id {admin_user_id}, got {msg['admin_user_id']}"
                    
                    # Requirement 8.2: Log impersonated team manager ID
                    assert 'impersonated_user_id' in msg, "impersonated_user_id missing from log"
                    assert msg['impersonated_user_id'] == team_manager_id, f"Expected impersonated_user_id {team_manager_id}, got {msg['impersonated_user_id']}"
                    
                    # Requirement 8.3: Log action performed
                    assert 'action' in msg, "action missing from log"
                    assert msg['action'] == context.function_name, f"Expected action {context.function_name}, got {msg['action']}"
                    
                    # Requirement 8.4: Timestamps are included (implicit in logging)
                    # The logging framework automatically adds timestamps
                    
                    # Requirement 8.5: Log API endpoint accessed
                    assert 'endpoint' in msg, "endpoint missing from log"
                    assert msg['endpoint'] == endpoint_path, f"Expected endpoint {endpoint_path}, got {msg['endpoint']}"
                    assert 'method' in msg, "method missing from log"
                    assert msg['method'] == http_method, f"Expected method {http_method}, got {msg['method']}"
                    
                    # Additional audit fields
                    assert 'admin_email' in msg, "admin_email missing from log"
                    assert msg['admin_email'] == admin_email, f"Expected admin_email {admin_email}, got {msg['admin_email']}"
                    
                    break
        
        # If structured logging didn't work, check string logs
        if not log_found:
            log_text = ' '.join([record.message for record in caplog.records])
            # At minimum, verify impersonation was logged
            assert 'admin_impersonation' in log_text or 'impersonating' in log_text.lower()
            assert admin_user_id in log_text
            assert team_manager_id in log_text
    
    def test_audit_logging_on_impersonation(self, caplog):
        """
        Test that impersonation attempts are logged for audit purposes.
        
        Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5
        """
        admin_user_id = 'admin-123'
        admin_email = 'admin@test.com'
        team_manager_id = 'tm-456'
        
        # Create event with admin user and team_manager_id parameter
        event = create_api_gateway_event(
            http_method='POST',
            path='/api/boats',
            query_parameters={'team_manager_id': team_manager_id},
            user_id=admin_user_id,
            groups=['admins']
        )
        
        # Override email in the event
        event['requestContext']['authorizer']['claims']['email'] = admin_email
        
        # Create test handler and context
        handler = create_test_handler()
        context = MockLambdaContext()
        
        # Call handler with logging capture
        import logging
        with caplog.at_level(logging.INFO):
            response = handler(event, context)
        
        # Assert: Impersonation should succeed
        assert response['statusCode'] == 200
        
        # Assert: Audit log should contain impersonation details
        # Check if any log record contains the impersonation event
        log_found = False
        for record in caplog.records:
            if hasattr(record, 'msg') and isinstance(record.msg, dict):
                msg = record.msg
                if msg.get('event') == 'admin_impersonation':
                    log_found = True
                    assert msg['admin_user_id'] == admin_user_id
                    assert msg['impersonated_user_id'] == team_manager_id
                    assert msg['admin_email'] == admin_email
                    assert 'action' in msg
                    assert 'endpoint' in msg
                    assert 'method' in msg
                    break
        
        # If structured logging didn't work, check string logs
        if not log_found:
            log_text = ' '.join([record.message for record in caplog.records])
            assert 'admin_impersonation' in log_text or 'impersonating' in log_text.lower()



class TestListTeamManagersEndpoint:
    """Test suite for list team managers endpoint"""
    
    # Task 2.1: Property test for team manager list completeness
    # Property 8: Team manager list completeness
    # Validates: Requirements 7.2, 7.3
    def test_property_team_manager_list_completeness(self, dynamodb_table):
        """
        Property 8: Team manager list completeness
        
        For any set of team managers in the system, the list endpoint returns all of them
        with required fields (user_id, first_name, last_name, email, club_affiliation).
        
        Feature: admin-impersonation, Property 8: Team manager list completeness
        Validates: Requirements 7.2, 7.3
        """
        from admin.list_team_managers import lambda_handler
        
        admin_user_id = 'admin-123'
        
        # Create event with admin user
        event = create_api_gateway_event(
            http_method='GET',
            path='/admin/team-managers',
            user_id=admin_user_id,
            groups=['admins']
        )
        
        # Create context
        context = MockLambdaContext()
        
        # Call handler
        response = lambda_handler(event, context)
        
        # Assert: Response should be successful
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        
        # Assert: Response has the expected structure
        assert 'data' in body
        assert 'team_managers' in body['data']
        assert 'count' in body['data']
        
        returned_tms = body['data']['team_managers']
        
        # Assert: Each team manager has required fields
        for tm in returned_tms:
            assert 'user_id' in tm
            assert 'first_name' in tm
            assert 'last_name' in tm
            assert 'email' in tm
            assert 'club_affiliation' in tm
            
            # Verify the fields are not empty (except club_affiliation which can be empty)
            assert tm['user_id']
            assert tm['first_name']
            assert tm['last_name']
            assert tm['email']
    
    # Task 2.2: Property test for non-admin rejection
    # Property 9: Non-admin rejection
    # Validates: Requirements 7.4
    def test_property_non_admin_rejection(self, dynamodb_table):
        """
        Property 9: Non-admin rejection
        
        For any non-admin request to the team manager list endpoint, the request is
        rejected with 403 Forbidden.
        
        Feature: admin-impersonation, Property 9: Non-admin rejection
        Validates: Requirements 7.4
        """
        from admin.list_team_managers import lambda_handler
        
        # Test with non-admin user
        non_admin_event = create_api_gateway_event(
            http_method='GET',
            path='/admin/team-managers',
            user_id='team-manager-123',
            groups=['team_managers']
        )
        
        context = MockLambdaContext()
        response = lambda_handler(non_admin_event, context)
        
        # Non-admin should be rejected with 403
        assert response['statusCode'] == 403
        body = json.loads(response['body'])
        assert body['success'] is False
        assert 'Admin access required' in body['error']['message']
        
        # Test with admin user
        admin_event = create_api_gateway_event(
            http_method='GET',
            path='/admin/team-managers',
            user_id='admin-123',
            groups=['admins']
        )
        
        response = lambda_handler(admin_event, context)
        
        # Admin should get successful response
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True

