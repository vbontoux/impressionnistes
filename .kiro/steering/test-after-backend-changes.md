---
inclusion: always
---

# Run Tests After Backend Changes

## Purpose
Ensure code quality by running integration tests after modifying Lambda functions or shared backend code.

## Rule

WHEN you modify Python files in the backend, you MUST remind the user to run tests:

### Files that require test runs:
- Any file in `functions/*/` directories (Lambda handlers)
- Any file in `functions/shared/` (shared utilities)
- Any file in `functions/layer/python/` (Lambda layer code)
- Any file in `tests/` (test files themselves)

### What to do:

1. **After completing backend changes**, explicitly remind the user:
   ```
   ⚠️ Backend code was modified. Please run tests to ensure nothing broke:
   cd infrastructure && make test
   ```

2. **When completing a task** that involved backend changes:
   ```
   ✅ Task complete! Before moving on, please run tests:
   cd infrastructure && make test
   ```

3. **If tests might fail** due to your changes:
   ```
   ⚠️ I've modified [file]. This may affect tests. Please run:
   cd infrastructure && make test
   
   If tests fail, we can fix them together.
   ```

## Why This Matters

- **Catch regressions early:** Tests catch bugs before they reach production
- **Maintain quality:** Ensures all APIs continue working as expected
- **Fast feedback:** Local tests run in seconds with no AWS costs
- **Confidence:** Know that changes don't break existing functionality

## Examples

✅ **DO remind about tests:**
```
I've updated the crew member validation logic in functions/shared/validation.py.

⚠️ Please run tests to ensure this doesn't break anything:
cd infrastructure && make test
```

✅ **DO remind at task completion:**
```
Task complete! I've implemented the new rental boat feature.

✅ Before moving on, please verify all tests pass:
cd infrastructure && make test
```

❌ **DON'T forget to remind:**
```
I've updated 3 Lambda functions. [No mention of tests]
```

## Test Commands Reference

```bash
# Run all tests
cd infrastructure && make test

# Run specific test file
cd infrastructure && make test ARGS="tests/integration/test_crew_member_api.py"

# Run with coverage report
cd infrastructure && make test-coverage

# Run single test
source tests/venv/bin/activate
pytest tests/integration/test_crew_member_api.py::test_create_crew_member -v
```

## Current Test Status

- **24 tests passing** across 6 API categories
- **6 auth tests skipped** (require Cognito mocking)
- Tests run locally with moto (no AWS costs)
- Average test run time: ~2-3 seconds

## Exception

If you're only modifying:
- Frontend code (Vue, JavaScript)
- Documentation (Markdown files)
- Configuration files (JSON, YAML)
- Infrastructure code (CDK stacks)

Then tests are optional, but still recommended if the changes might affect API contracts.
