# Testing Strategy - Course des Impressionnistes

## Overview

This project uses **integration tests** to verify that the frontend, API Gateway, and Lambda functions work together correctly. Tests run locally using mocked AWS services (no real AWS calls).

## Why Integration Tests?

✅ **Catch contract breakage** between frontend and backend  
✅ **Test real Lambda code** with realistic events  
✅ **Fast feedback** - run locally in seconds  
✅ **No AWS costs** - everything runs in-memory  
✅ **No authentication complexity** - bypass Cognito for testing  

## Quick Start

```bash
# Install dependencies
pip install -r tests/requirements.txt

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/integration/test_crew_member_api.py -v
```

See `tests/QUICKSTART.md` for detailed getting started guide.

## Test Structure

```
tests/
├── conftest.py                          # Pytest fixtures (shared test setup)
├── requirements.txt                     # Test dependencies
├── integration/
│   ├── test_crew_member_api.py         # ✅ Crew member CRUD operations
│   ├── test_boat_registration_api.py   # ✅ Boat registration operations
│   ├── test_public_api.py              # ✅ Public endpoints (no auth)
│   └── test_admin_api.py               # 🚧 TODO: Admin endpoints
├── README.md                            # Detailed documentation
├── QUICKSTART.md                        # 5-minute getting started
└── run_tests.sh                         # Convenience script
```

## What's Tested

### ✅ Crew Member API
- Create crew member
- List crew members
- Update crew member
- Delete crew member
- Validation errors

### ✅ Boat Registration API
- Create boat registration
- List boat registrations
- Update boat registration
- Delete boat registration
- Cannot delete paid boats

### ✅ Public API
- Get event information (dates)
- List clubs

### 🚧 TODO
- Admin endpoints (crew, boats, config)
- Payment endpoints
- Race eligibility logic
- Rental boat management

## How It Works

### 1. Mock DynamoDB (moto)
Tests use `moto` library to create an in-memory DynamoDB:
- Same schema as production
- Pre-seeded with configuration
- Clean slate for each test
- No AWS credentials needed

### 2. Mock API Gateway Events
Tests create realistic API Gateway events:
```python
event = mock_api_gateway_event(
    http_method='POST',
    path='/crew',
    body=json.dumps({'first_name': 'John', ...}),
    user_id='test-user-123'
)
```

### 3. Call Real Lambda Code
Tests import and execute actual Lambda handlers:
```python
from crew.create_crew_member import lambda_handler
response = lambda_handler(event, context)
```

### 4. Verify Response Format
Tests check that responses match expected format:
```python
assert response['statusCode'] == 200
body = json.loads(response['body'])
assert body['success'] is True
assert 'crew_member_id' in body['data']
```

## Benefits

1. **Catch Breaking Changes Early**
   - Frontend changes field name → test fails
   - Lambda changes response format → test fails
   - Database schema changes → test fails

2. **Fast Development Cycle**
   - No deployment needed
   - Run tests in seconds
   - Immediate feedback

3. **Documentation**
   - Tests show correct API usage
   - Examples for new developers
   - Living documentation

4. **Confidence**
   - Deploy with confidence
   - Refactor safely
   - Add features without fear

## Running Tests

### Locally
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=functions --cov-report=html

# Specific file
pytest tests/integration/test_crew_member_api.py -v

# Specific test
pytest tests/integration/test_crew_member_api.py::test_create_crew_member -v

# Watch mode (re-run on file changes)
pytest-watch tests/
```

### In CI/CD
Add to `.github/workflows/test.yml`:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r tests/requirements.txt
      - run: pytest tests/ -v --cov=functions
```

## Writing New Tests

See `tests/README.md` for detailed guide on writing tests.

Quick template:
```python
def test_my_feature(dynamodb_table, mock_api_gateway_event, mock_lambda_context, test_team_manager_id):
    """Test description"""
    from my_module.handler import lambda_handler
    
    event = mock_api_gateway_event(
        http_method='POST',
        path='/my-endpoint',
        body=json.dumps({'key': 'value'}),
        user_id=test_team_manager_id
    )
    
    response = lambda_handler(event, mock_lambda_context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
```

## Next Steps

1. **Add More Tests**
   - Admin endpoints
   - Payment flow
   - Race eligibility
   - Error cases

2. **Set Up CI/CD**
   - Run tests on every commit
   - Block merges if tests fail
   - Generate coverage reports

3. **Add Frontend Tests**
   - Test API client calls
   - Test response handling
   - Use MSW to mock API

4. **Monitor Coverage**
   - Aim for 80%+ coverage on critical paths
   - Focus on business logic
   - Don't obsess over 100%

## Resources

- `tests/README.md` - Detailed documentation
- `tests/QUICKSTART.md` - 5-minute getting started
- `tests/integration/` - Example tests to learn from
- [pytest documentation](https://docs.pytest.org/)
- [moto documentation](https://docs.getmoto.org/)

## Questions?

Check the test files for examples, or ask for help!
