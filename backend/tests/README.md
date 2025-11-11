# Backend Tests

This directory contains tests for the Course des Impressionnistes Registration System backend.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── test_placeholder.py      # Placeholder tests (remove when real tests added)
├── functions/               # Tests for Lambda functions (to be created)
│   ├── test_auth.py
│   ├── test_crew.py
│   ├── test_boat.py
│   └── test_payment.py
└── shared/                  # Tests for shared utilities (to be created)
    ├── test_database.py
    ├── test_validation.py
    └── test_configuration.py
```

## Running Tests

### Run all tests
```bash
make test
```

### Run tests with coverage
```bash
make test-cov
```

### Run specific test file
```bash
venv/bin/pytest tests/test_placeholder.py
```

### Run specific test function
```bash
venv/bin/pytest tests/test_placeholder.py::test_placeholder
```

### Run tests with markers
```bash
# Run only unit tests
venv/bin/pytest -m unit

# Run only integration tests
venv/bin/pytest -m integration

# Skip slow tests
venv/bin/pytest -m "not slow"
```

## Test Markers

Tests can be marked with the following markers (defined in pytest.ini):

- `@pytest.mark.unit` - Unit tests (fast, no external dependencies)
- `@pytest.mark.integration` - Integration tests (may require AWS/external services)
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.aws` - Tests requiring AWS credentials

Example:
```python
@pytest.mark.unit
def test_validation():
    assert validate_email("test@example.com") == True

@pytest.mark.integration
@pytest.mark.aws
def test_dynamodb_connection():
    # Test that requires actual AWS DynamoDB
    pass
```

## Fixtures

Common fixtures are defined in `conftest.py`:

- `mock_env_vars` - Mock environment variables
- `sample_crew_member` - Sample crew member data
- `sample_boat_registration` - Sample boat registration data

Usage:
```python
def test_crew_member(sample_crew_member):
    assert sample_crew_member['first_name'] == 'Jean'
```

## Mocking AWS Services

For testing Lambda functions that interact with AWS services, use `moto`:

```python
import boto3
from moto import mock_dynamodb

@mock_dynamodb
def test_dynamodb_operation():
    # Create mock DynamoDB table
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')
    table = dynamodb.create_table(
        TableName='test-table',
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
    
    # Test your function
    # ...
```

## Coverage Reports

After running `make test-cov`, coverage reports are generated:

- **Terminal output**: Shows coverage summary
- **HTML report**: Open `htmlcov/index.html` in browser for detailed report

## Best Practices

1. **Test naming**: Use descriptive names starting with `test_`
2. **One assertion per test**: Keep tests focused
3. **Use fixtures**: Reuse common test data
4. **Mock external services**: Don't make real AWS calls in unit tests
5. **Test edge cases**: Include tests for error conditions
6. **Keep tests fast**: Unit tests should run in milliseconds
7. **Document complex tests**: Add docstrings explaining what's being tested

## Writing New Tests

When implementing new features, create corresponding test files:

1. Create test file: `tests/functions/test_<feature>.py`
2. Import the function to test
3. Write test cases covering:
   - Happy path (normal operation)
   - Edge cases
   - Error conditions
   - Input validation

Example:
```python
import pytest
from functions.crew.create_crew_member import lambda_handler

def test_create_crew_member_success(mock_env_vars, sample_crew_member):
    """Test successful crew member creation"""
    event = {
        'body': json.dumps(sample_crew_member)
    }
    
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    assert 'crew_id' in json.loads(response['body'])

def test_create_crew_member_invalid_data(mock_env_vars):
    """Test crew member creation with invalid data"""
    event = {
        'body': json.dumps({'first_name': 'John'})  # Missing required fields
    }
    
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 400
```

## Continuous Integration

Tests should be run automatically in CI/CD pipeline before deployment.

## Troubleshooting

### Import errors
Make sure you're running tests from the backend directory:
```bash
cd backend
make test
```

### AWS credential errors
For tests marked with `@pytest.mark.aws`, ensure AWS credentials are configured:
```bash
aws configure
```

Or use moto to mock AWS services instead.

### Module not found
Ensure virtual environment is activated and dependencies installed:
```bash
make setup
```
