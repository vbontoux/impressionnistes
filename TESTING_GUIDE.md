# Testing Guide

This project includes comprehensive tests for both backend and frontend code.

## Quick Start

Run all tests:
```bash
cd infrastructure
make test
```

## Test Categories

### 1. Backend Integration Tests (24 tests)
Located in `tests/integration/`, these tests verify Lambda function behavior using mocked AWS services.

**Run backend tests only:**
```bash
cd infrastructure
make test-backend
```

**Test coverage:**
- Auth API (6 tests - currently skipped, require Cognito mocking)
- Admin API (boat/crew management)
- Boat Registration API
- Crew Member API
- Public API (health checks, event info)
- Race API
- Rental API

### 2. Frontend Formatter Tests (101 tests)
Located in `frontend/src/utils/exportFormatters/`, these tests verify CSV and Excel export formatting.

**Run frontend tests only:**
```bash
cd infrastructure
make test-frontend
```

**Test coverage:**
- Crew Members Formatter (22 tests)
  - CSV structure and headers
  - Special character escaping
  - Empty dataset handling
  - Missing field handling
  
- Boat Registrations Formatter (33 tests)
  - CSV structure and headers
  - Filled seats calculation
  - Boolean formatting (Yes/No)
  - Nested data handling
  
- CrewTimer Formatter (46 tests)
  - Boat filtering (complete/paid/free, exclude forfait)
  - Race sorting (marathon before semi-marathon)
  - Event and bow numbering
  - Race name formatting
  - Gender mapping
  - Yolette detection
  - Stroke seat extraction
  - Average age calculation

## Test Commands

### Setup
```bash
cd infrastructure
make test-setup          # Create test environment (one-time setup)
```

### Running Tests
```bash
make test                # Run all tests (backend + frontend)
make test-backend        # Run backend integration tests only
make test-frontend       # Run frontend formatter tests only
make test-coverage       # Run backend tests with HTML coverage report
```

### Cleanup
```bash
make test-clean          # Remove test environment and cache files
```

## Test Output

### Backend Tests
Backend tests use pytest and provide detailed output:
```
tests/integration/test_admin_api.py::test_list_all_boats PASSED
tests/integration/test_crew_member_api.py::test_create_crew_member PASSED
...
======================== 24 passed, 6 skipped in 2.34s ========================
```

### Frontend Tests
Frontend tests use simple console-based assertions:
```
=== Testing Crew Members Formatter ===

Test 1: CSV structure and headers
✓ PASS: Headers include Crew Member ID
✓ PASS: Headers include First Name
...

=== Test Summary ===
Total: 22 tests
Passed: 22
Failed: 0

✓ All tests passed!
```

## Writing New Tests

### Backend Tests
Add new test files to `tests/integration/`:

```python
# tests/integration/test_my_feature.py
import pytest
from moto import mock_dynamodb

@mock_dynamodb
def test_my_feature():
    # Test implementation
    assert result == expected
```

### Frontend Tests
Add new test files to `frontend/src/utils/exportFormatters/`:

```javascript
// myFormatter.test.js
import { myFunction } from './myFormatter.js';

console.log('=== Testing My Formatter ===\n');

let passCount = 0;
let failCount = 0;

function assert(condition, testName) {
  if (condition) {
    console.log(`✓ PASS: ${testName}`);
    passCount++;
  } else {
    console.log(`✗ FAIL: ${testName}`);
    failCount++;
  }
}

// Test 1: Basic functionality
console.log('Test 1: Basic functionality');
const result = myFunction(input);
assert(result === expected, 'Function returns expected value');

// Summary
console.log('\n=== Test Summary ===');
console.log(`Total: ${passCount + failCount} tests`);
console.log(`Passed: ${passCount}`);
console.log(`Failed: ${failCount}`);

if (failCount === 0) {
  console.log('\n✓ All tests passed!');
} else {
  console.log(`\n✗ ${failCount} test(s) failed`);
  process.exit(1);
}
```

Then add the test to `runTests.sh`:
```bash
echo "4. My Formatter Tests"
echo "---------------------"
node myFormatter.test.js
if [ $? -ne 0 ]; then
  echo "❌ My Formatter tests failed"
  exit 1
fi
```

## Continuous Integration

Tests should be run:
- Before committing code changes
- Before deploying to dev environment
- Before deploying to production

**Recommended workflow:**
```bash
# 1. Make changes
# 2. Run tests
cd infrastructure && make test

# 3. If tests pass, deploy
make deploy-dev

# 4. Test in dev environment
# 5. Deploy to production
make deploy-prod
```

## Test Dependencies

### Backend
- pytest - Test framework
- moto - AWS service mocking
- boto3 - AWS SDK

### Frontend
- Node.js - JavaScript runtime
- No external test framework (uses console-based assertions)

## Troubleshooting

### Backend Tests Fail
1. Ensure test environment is set up: `make test-setup`
2. Check Python version: `python3 --version` (should be 3.9+)
3. Verify dependencies: `cd .. && tests/venv/bin/pip list`

### Frontend Tests Fail
1. Ensure Node.js is installed: `node --version`
2. Check test file permissions: `chmod +x frontend/src/utils/exportFormatters/runTests.sh`
3. Run tests individually to isolate issues:
   ```bash
   cd frontend/src/utils/exportFormatters
   node crewMembersFormatter.test.js
   ```

### Tests Pass Locally But Fail in CI
- Check environment variables
- Verify AWS credentials are not required (tests use mocks)
- Ensure all dependencies are installed

## Test Coverage

Current test coverage:
- **Backend**: 24 integration tests (6 skipped pending Cognito mocking)
- **Frontend**: 101 formatter tests
- **Total**: 125 tests

Coverage areas:
- ✅ Admin API endpoints
- ✅ Boat registration CRUD
- ✅ Crew member CRUD
- ✅ Export formatters (CSV, Excel)
- ✅ Race eligibility logic
- ⏳ Auth endpoints (pending Cognito mocking)

## Future Improvements

- [ ] Add Cognito mocking for auth tests
- [ ] Add frontend component tests (Vue components)
- [ ] Add end-to-end tests
- [ ] Add performance tests
- [ ] Increase backend test coverage to 90%+
- [ ] Add property-based tests for complex logic
