```

# Python Testing Guidelines

## Purpose
Ensure consistent and efficient testing practices for backend Python code.

## Rules

### 1. No Hypothesis Library

**DO NOT use the Hypothesis property-based testing library** for Python tests.

❌ **Don't do this:**
```python
from hypothesis import given, strategies as st

@given(st.integers())
def test_something(value):
    assert function(value) > 0
```

✅ **Do this instead:**
```python
import pytest

def test_something():
    assert function(42) > 0
    assert function(-10) > 0
    assert function(0) > 0
```

**Why:** We prefer explicit test cases over property-based testing for clarity and maintainability.

### 2. Reuse Existing Tests

**ALWAYS check for existing tests before writing new ones.** Reuse and extend existing test patterns.

**Test locations:**
- `tests/integration/` - Integration tests for Lambda APIs
- `tests/unit/` - Unit tests for shared utilities
- `functions/shared/test_*.py` - Inline tests for shared modules

**Before writing a new test:**

1. **Search for similar tests:**
   ```bash
   # Find tests for a specific function
   grep -r "test_function_name" tests/
   
   # Find tests for a module
   grep -r "from functions.shared.module import" tests/
   ```

2. **Reuse test patterns:**
   - Copy the structure of existing tests
   - Use the same fixtures and setup patterns
   - Follow the same assertion style
   - Reuse helper functions and mock data

3. **Extend existing test files:**
   - Add new test cases to existing test files when testing the same module
   - Don't create duplicate test files for the same functionality

**Example - Reusing existing test structure:**

```python
# Existing test in tests/integration/test_crew_member_api.py
def test_create_crew_member(api_client, auth_headers):
    response = api_client.post('/crew-members', 
        json={'name': 'John Doe', 'email': 'john@example.com'},
        headers=auth_headers)
    assert response.status_code == 201

# New test - reuse the same pattern
def test_create_crew_member_with_phone(api_client, auth_headers):
    response = api_client.post('/crew-members',
        json={'name': 'Jane Doe', 'email': 'jane@example.com', 'phone': '1234567890'},
        headers=auth_headers)
    assert response.status_code == 201
    assert response.json()['phone'] == '1234567890'
```

### 3. Test Organization

**Integration tests** (`tests/integration/`):
- Test Lambda API endpoints end-to-end
- Use moto for AWS service mocking
- Test request/response contracts
- Test error handling and validation

**Unit tests** (`tests/unit/` or inline):
- Test individual functions in isolation
- Test business logic calculations
- Test data transformations
- Test validation rules

### 4. Running Tests

```bash
# Run all tests
cd infrastructure && make test

# Run specific test file
cd infrastructure && make test ARGS="tests/integration/test_crew_member_api.py"

# Run single test
source tests/venv/bin/activate
pytest tests/integration/test_crew_member_api.py::test_create_crew_member -v
```

### 5. Test Quality Checklist

When writing or reviewing tests:
- [ ] No Hypothesis library used
- [ ] Checked for existing similar tests
- [ ] Reused existing test patterns and fixtures
- [ ] Clear test names describing what is being tested
- [ ] Tests are independent (no shared state)
- [ ] Both success and error cases covered
- [ ] Assertions are specific and meaningful

## Current Test Status

- **24 tests passing** across 6 API categories
- Tests use pytest with moto for AWS mocking
- Average test run time: ~2-3 seconds
- No external AWS calls (all mocked locally)

```
