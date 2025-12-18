"""
Pytest configuration and fixtures for integration tests
"""
import os
import sys
import pytest
import boto3
from moto import mock_dynamodb
from decimal import Decimal

# Add functions directory to path so we can import Lambda code
# We need to handle the conflict between moto's 'responses' package
# and our functions/shared/responses.py module
functions_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'functions'))
shared_dir = os.path.join(functions_dir, 'shared')
layer_dir = os.path.join(functions_dir, 'layer', 'python')

# Remove any existing entries to avoid duplicates
for path in [functions_dir, shared_dir, layer_dir]:
    if path in sys.path:
        sys.path.remove(path)

# Insert at the beginning to prioritize our modules over installed packages
# This ensures 'from responses import' finds our module, not moto's
sys.path.insert(0, layer_dir)
sys.path.insert(0, shared_dir)
sys.path.insert(0, functions_dir)

# Verify the paths are correct
print(f"Test environment paths:")
print(f"  Functions: {functions_dir}")
print(f"  Shared: {shared_dir}")
print(f"  Layer: {layer_dir}")

# CRITICAL: Import our responses module BEFORE moto can import the other one
# This caches our module in sys.modules
import importlib.util
responses_path = os.path.join(shared_dir, 'responses.py')
spec = importlib.util.spec_from_file_location("responses", responses_path)
responses_module = importlib.util.module_from_spec(spec)
sys.modules['responses'] = responses_module
spec.loader.exec_module(responses_module)
print(f"  Loaded our responses module from: {responses_path}")


@pytest.fixture(scope='function')
def aws_credentials():
    """Mock AWS credentials for moto"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-3'


@pytest.fixture(scope='function')
def dynamodb_table(aws_credentials):
    """Create a mock DynamoDB table for testing"""
    with mock_dynamodb():
        # Set table name
        table_name = 'test-impressionnistes-table'
        os.environ['TABLE_NAME'] = table_name
        
        # Create DynamoDB client
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')
        
        # Create table with same schema as production
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'},
                {'AttributeName': 'license_number', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'GSI3',
                    'KeySchema': [
                        {'AttributeName': 'license_number', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Wait for table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        
        # Seed with configuration data
        _seed_configuration(table)
        
        yield table


def _seed_configuration(table):
    """Seed the table with default configuration"""
    # System configuration
    table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'SYSTEM',
        'registration_start_date': '2025-03-19',
        'registration_end_date': '2025-04-19',
        'payment_deadline': '2025-04-25',
        'rental_priority_days': 15,
        'event_date': '2025-05-01',
        'temporary_editing_access_hours': 48
    })
    
    # Pricing configuration
    table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'PRICING',
        'base_seat_price': Decimal('20.00'),
        'boat_rental_multiplier_skiff': Decimal('2.5'),
        'boat_rental_price_crew': Decimal('20.00'),
        'currency': 'EUR'
    })
    
    # Notification configuration
    table.put_item(Item={
        'PK': 'CONFIG',
        'SK': 'NOTIFICATION',
        'notification_frequency_days': 7,
        'session_timeout_minutes': 30,
        'notification_channels': ['email', 'in_app'],
        'email_from': 'test@example.com'
    })


@pytest.fixture
def test_team_manager_id():
    """Return a test team manager ID"""
    return 'test-team-manager-123'


@pytest.fixture
def mock_api_gateway_event():
    """Factory fixture to create API Gateway events"""
    def _create_event(
        http_method='GET',
        path='/',
        body=None,
        path_parameters=None,
        query_parameters=None,
        user_id=None,
        groups=None
    ):
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
                    'cognito:groups': groups,  # Add groups for authorization
                    'custom:role': 'team_manager',
                    'custom:club_affiliation': 'Test Club'  # Add club affiliation
                }
            }
        
        return event
    
    return _create_event


@pytest.fixture
def mock_lambda_context():
    """Create a mock Lambda context"""
    class MockContext:
        def __init__(self):
            self.function_name = 'test-function'
            self.memory_limit_in_mb = 128
            self.invoked_function_arn = 'arn:aws:lambda:eu-west-3:123456789012:function:test-function'
            self.aws_request_id = 'test-request-id'
    
    return MockContext()
