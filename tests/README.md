# Integration Tests

This directory contains integration tests for the Lambda functions using mocked AWS services.

## Overview

These tests verify that:
- Lambda handlers receive correct API Gateway event formats
- Lambda handlers return correct response formats
- Data is correctly written to and read from DynamoDB
- Business logic works end-to-end

## Setup

1. Install test dependencies:
```bash
pip install -r tests/requirements.txt
```

Or if using a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r tests/requirements.txt
```

2. Install your Lambda dependencies (if not already done):
```bash
cd functions
pip install -r layer/requirements.txt
```

## Running Tests

### Run all tests:
```bash
pytest tests/
```

### Run with verbose output:
```bash
pytest tests/ -v
```

### Run specific test file:
```bash
pytest tests/integration/test_crew_member_api.py -v
```

### Run specific test:
```bash
pytest tests/integration/test_crew_member_api.py::test_create_crew_member -v
```

### Run with coverage:
```bash
pytest tests/ --cov=functions --cov-report=html
```

Then open `htmlcov/index.html` in your browser to see coverage report.

## Test Structure

```
tests/
├── conftest.py                          # Pytest fixtures (DynamoDB mock, event builders)
├── requirements.txt                     # Test dependencies
├── integration/
│   ├── test_crew_member_api.py         # Crew member CRUD tests
│   ├── test_boat_registration_api.py   # Boat registration tests
│   └── test_admin_api.py               # Admin endpoint tests (TODO)
└── README.md                            # This file
```

## Key Features

### 1. Mock DynamoDB (moto)
- Tests run completely locally
- No AWS credentials needed
- Fast in-memory database
- Clean slate for each test

### 2. No Authentication Required
- Tests bypass Cognito authentication
- User ID is injected directly into events
- Focus on business logic, not auth

### 3. Real Lambda Code
- Tests import and execute actual Lambda handlers
- Catches contract issues between frontend and backend
- Validates request/response formats

## Writing New Tests

### Example: Test a new endpoint

```python
def test_my_new_endpoint(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test description"""
    # Import your Lambda handler
    from my_module.my_handler import lambda_handler
    
    # Create API Gateway event
    event = mock_api_gateway_event(
        http_method='POST',
        path='/my-endpoint',
        body=json.dumps({'key': 'value'}),
        user_id=test_team_manager_id
    )
    
    # Call Lambda handler
    response = lambda_handler(event, mock_lambda_context)
    
    # Assert response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    
    # Optionally verify DynamoDB state
    item = dynamodb_table.get_item(Key={'PK': '...', 'SK': '...'})
    assert 'Item' in item
```

## Fixtures Available

### `dynamodb_table`
- Mock DynamoDB table with production schema
- Pre-seeded with configuration data
- Clean slate for each test

### `mock_api_gateway_event()`
- Factory to create API Gateway events
- Parameters: `http_method`, `path`, `body`, `path_parameters`, `query_parameters`, `user_id`

### `mock_lambda_context`
- Mock Lambda context object
- Contains function name, request ID, etc.

### `test_team_manager_id`
- Test user ID: `'test-team-manager-123'`

## Best Practices

1. **Test one thing at a time**: Each test should verify one specific behavior
2. **Use descriptive names**: `test_create_crew_member_validation_error` is better than `test_error`
3. **Arrange-Act-Assert**: Set up data, call handler, verify results
4. **Clean tests**: Each test should be independent and not rely on others
5. **Test error cases**: Don't just test happy paths

## Common Issues

### Import errors
If you get import errors, make sure:
- You're running pytest from the project root
- The `functions` directory is in your Python path (conftest.py handles this)

### DynamoDB errors
If you get DynamoDB errors:
- Make sure `moto[dynamodb]` is installed
- Check that `aws_credentials` fixture is being used

### Test isolation
If tests interfere with each other:
- Make sure you're using the `dynamodb_table` fixture (it creates a fresh table per test)
- Don't use global state in your Lambda code

## CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
- name: Run integration tests
  run: |
    pip install -r tests/requirements.txt
    pytest tests/ -v --cov=functions
```

## Next Steps

1. Add more test coverage for:
   - Admin endpoints
   - Payment endpoints
   - Race eligibility logic
   - Edge cases and error handling

2. Set up CI/CD to run tests automatically

3. Add test coverage reporting

4. Consider adding contract tests for frontend API calls
