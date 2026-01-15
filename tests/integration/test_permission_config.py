"""
Integration tests for permission configuration management.
Tests the admin APIs for getting, updating, and resetting permission configuration.
"""
import json
import pytest
from moto import mock_dynamodb
import boto3
import os

# Import Lambda handlers
from functions.admin.get_permission_config import lambda_handler as get_config_handler
from functions.admin.update_permission_config import lambda_handler as update_config_handler
from functions.admin.reset_permission_config import lambda_handler as reset_config_handler
from functions.shared.access_control import get_default_permissions


@pytest.fixture
def aws_credentials():
    """Mock AWS credentials for moto"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture
def dynamodb_table(aws_credentials):
    """Create a mock DynamoDB table for testing."""
    with mock_dynamodb():
        # Set table name BEFORE creating the table
        table_name = 'test-table'
        os.environ['DYNAMODB_TABLE'] = table_name
        
        # Create DynamoDB resource
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
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


def test_get_permission_config_default(dynamodb_table):
    """Test getting permission configuration when none exists (returns defaults)."""
    event = {
        'httpMethod': 'GET',
        'requestContext': {
            'authorizer': {
                'claims': {
                    'email': 'admin@example.com'
                }
            }
        }
    }
    
    response = get_config_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'permissions' in body
    
    # Verify default permissions are returned
    default_permissions = get_default_permissions()
    assert body['permissions'] == default_permissions


def test_update_permission_config_success(dynamodb_table):
    """Test updating permission configuration successfully."""
    # Create custom permissions
    custom_permissions = get_default_permissions()
    custom_permissions['create_crew_member']['before_registration'] = True  # Change from default
    
    event = {
        'httpMethod': 'PUT',
        'body': json.dumps({
            'permissions': custom_permissions
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'email': 'admin@example.com'
                }
            }
        }
    }
    
    response = update_config_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Permission configuration updated successfully'
    assert body['permissions'] == custom_permissions
    assert 'updated_at' in body
    assert body['updated_by'] == 'admin@example.com'
    
    # Verify configuration was saved to DynamoDB
    item = dynamodb_table.get_item(
        Key={'PK': 'CONFIG', 'SK': 'PERMISSIONS'}
    )
    assert 'Item' in item
    assert item['Item']['permissions'] == custom_permissions


def test_update_permission_config_invalid_matrix(dynamodb_table):
    """Test updating with invalid permission matrix returns validation error."""
    # Missing required action
    invalid_permissions = {
        'create_crew_member': {
            'before_registration': False,
            'during_registration': True,
            'after_registration': False,
            'after_payment_deadline': False
        }
        # Missing other required actions
    }
    
    event = {
        'httpMethod': 'PUT',
        'body': json.dumps({
            'permissions': invalid_permissions
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'email': 'admin@example.com'
                }
            }
        }
    }
    
    response = update_config_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'Invalid permission matrix' in body['error']['message']


def test_update_permission_config_missing_phase(dynamodb_table):
    """Test updating with missing phase returns validation error."""
    invalid_permissions = get_default_permissions()
    # Remove a required phase
    del invalid_permissions['create_crew_member']['during_registration']
    
    event = {
        'httpMethod': 'PUT',
        'body': json.dumps({
            'permissions': invalid_permissions
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'email': 'admin@example.com'
                }
            }
        }
    }
    
    response = update_config_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'Missing phase' in body['error']['message']


def test_reset_permission_config(dynamodb_table):
    """Test resetting permission configuration to defaults."""
    # First, set custom permissions
    custom_permissions = get_default_permissions()
    custom_permissions['create_crew_member']['before_registration'] = True
    
    dynamodb_table.put_item(
        Item={
            'PK': 'CONFIG',
            'SK': 'PERMISSIONS',
            'permissions': custom_permissions
        }
    )
    
    # Now reset to defaults
    event = {
        'httpMethod': 'POST',
        'requestContext': {
            'authorizer': {
                'claims': {
                    'email': 'admin@example.com'
                }
            }
        }
    }
    
    response = reset_config_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Permission configuration reset to defaults'
    
    # Verify defaults are returned
    default_permissions = get_default_permissions()
    assert body['permissions'] == default_permissions
    
    # Verify configuration was saved to DynamoDB
    item = dynamodb_table.get_item(
        Key={'PK': 'CONFIG', 'SK': 'PERMISSIONS'}
    )
    assert 'Item' in item
    assert item['Item']['permissions'] == default_permissions


def test_configuration_change_takes_effect_immediately(dynamodb_table):
    """Test that configuration changes take effect immediately."""
    # Update configuration
    custom_permissions = get_default_permissions()
    custom_permissions['create_crew_member']['before_registration'] = True
    
    update_event = {
        'httpMethod': 'PUT',
        'body': json.dumps({
            'permissions': custom_permissions
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'email': 'admin@example.com'
                }
            }
        }
    }
    
    update_response = update_config_handler(update_event, None)
    assert update_response['statusCode'] == 200
    
    # Immediately get configuration
    get_event = {
        'httpMethod': 'GET',
        'requestContext': {
            'authorizer': {
                'claims': {
                    'email': 'admin@example.com'
                }
            }
        }
    }
    
    get_response = get_config_handler(get_event, None)
    assert get_response['statusCode'] == 200
    
    body = json.loads(get_response['body'])
    assert body['permissions'] == custom_permissions


def test_audit_log_created_on_update(dynamodb_table):
    """Test that audit log is created when configuration is updated."""
    custom_permissions = get_default_permissions()
    
    event = {
        'httpMethod': 'PUT',
        'body': json.dumps({
            'permissions': custom_permissions
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'email': 'admin@example.com'
                }
            }
        }
    }
    
    response = update_config_handler(event, None)
    assert response['statusCode'] == 200
    
    # Query audit logs
    from boto3.dynamodb.conditions import Key
    audit_logs = dynamodb_table.query(
        KeyConditionExpression=Key('PK').eq('AUDIT#PERMISSION_CONFIG')
    )
    
    assert audit_logs['Count'] > 0
    audit_entry = audit_logs['Items'][0]
    assert audit_entry['action'] == 'update_permission_config'
    assert audit_entry['admin_email'] == 'admin@example.com'
    assert 'timestamp' in audit_entry


def test_audit_log_created_on_reset(dynamodb_table):
    """Test that audit log is created when configuration is reset."""
    event = {
        'httpMethod': 'POST',
        'requestContext': {
            'authorizer': {
                'claims': {
                    'email': 'admin@example.com'
                }
            }
        }
    }
    
    response = reset_config_handler(event, None)
    assert response['statusCode'] == 200
    
    # Query audit logs
    from boto3.dynamodb.conditions import Key
    audit_logs = dynamodb_table.query(
        KeyConditionExpression=Key('PK').eq('AUDIT#PERMISSION_CONFIG')
    )
    
    assert audit_logs['Count'] > 0
    audit_entry = audit_logs['Items'][0]
    assert audit_entry['action'] == 'reset_permission_config'
    assert audit_entry['admin_email'] == 'admin@example.com'
    assert 'timestamp' in audit_entry
