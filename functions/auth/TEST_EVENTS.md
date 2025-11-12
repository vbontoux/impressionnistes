# Lambda Test Events for Authentication Functions

This document contains test JSON payloads for testing Lambda functions in the AWS Lambda console.

## How to Use

1. Go to AWS Lambda Console
2. Select the function you want to test
3. Click "Test" tab
4. Create a new test event
5. Copy and paste the JSON from below
6. Click "Test" to invoke the function

---

## 1. Register Function

**Function Name**: `ImpressionnistesApi-dev-RegisterFunction`

### Test Event: Valid Registration

```json
{
  "body": "{\"email\":\"test@example.com\",\"password\":\"TestPass123!\",\"first_name\":\"Jean\",\"last_name\":\"Dupont\",\"club_affiliation\":\"Rowing Club Paris\",\"mobile_number\":\"+33612345678\"}"
}
```

### Test Event: Invalid Email

```json
{
  "body": "{\"email\":\"invalid-email\",\"password\":\"TestPass123!\",\"first_name\":\"Jean\",\"last_name\":\"Dupont\",\"club_affiliation\":\"Rowing Club Paris\",\"mobile_number\":\"+33612345678\"}"
}
```

### Test Event: Missing Fields

```json
{
  "body": "{\"email\":\"test@example.com\",\"password\":\"TestPass123!\"}"
}
```

### Test Event: Weak Password

```json
{
  "body": "{\"email\":\"test@example.com\",\"password\":\"weak\",\"first_name\":\"Jean\",\"last_name\":\"Dupont\",\"club_affiliation\":\"Rowing Club Paris\",\"mobile_number\":\"+33612345678\"}"
}
```

---

## 2. Get Profile Function

**Function Name**: `ImpressionnistesApi-dev-GetProfileFunction`

### Test Event: Authenticated User

```json
{
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "test-user-id-123",
        "email": "test@example.com",
        "given_name": "Jean",
        "family_name": "Dupont",
        "custom:club_affiliation": "Rowing Club Paris",
        "custom:role": "team_manager",
        "cognito:groups": "team_managers"
      }
    }
  }
}
```

### Test Event: Missing Authentication

```json
{
  "requestContext": {}
}
```

---

## 3. Update Profile Function

**Function Name**: `ImpressionnistesApi-dev-UpdateProfileFunction`

### Test Event: Update First Name

```json
{
  "body": "{\"first_name\":\"Pierre\"}",
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "test-user-id-123",
        "email": "test@example.com",
        "given_name": "Jean",
        "family_name": "Dupont",
        "custom:club_affiliation": "Rowing Club Paris",
        "custom:role": "team_manager",
        "cognito:groups": "team_managers"
      }
    }
  }
}
```

### Test Event: Update Multiple Fields

```json
{
  "body": "{\"first_name\":\"Pierre\",\"last_name\":\"Martin\",\"club_affiliation\":\"New Rowing Club\",\"mobile_number\":\"+33698765432\"}",
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "test-user-id-123",
        "email": "test@example.com",
        "given_name": "Jean",
        "family_name": "Dupont",
        "custom:club_affiliation": "Rowing Club Paris",
        "custom:role": "team_manager",
        "cognito:groups": "team_managers"
      }
    }
  }
}
```

### Test Event: Invalid Phone Number

```json
{
  "body": "{\"mobile_number\":\"invalid\"}",
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "test-user-id-123",
        "email": "test@example.com",
        "given_name": "Jean",
        "family_name": "Dupont",
        "custom:club_affiliation": "Rowing Club Paris",
        "custom:role": "team_manager",
        "cognito:groups": "team_managers"
      }
    }
  }
}
```

---

## 4. Forgot Password Function

**Function Name**: `ImpressionnistesApi-dev-ForgotPasswordFunction`

### Test Event: Valid Email

```json
{
  "body": "{\"email\":\"test@example.com\"}"
}
```

### Test Event: Invalid Email Format

```json
{
  "body": "{\"email\":\"not-an-email\"}"
}
```

### Test Event: Missing Email

```json
{
  "body": "{}"
}
```

---

## 5. Confirm Password Reset Function

**Function Name**: `ImpressionnistesApi-dev-ConfirmPasswordResetFunction`

### Test Event: Valid Reset

```json
{
  "body": "{\"email\":\"test@example.com\",\"code\":\"123456\",\"new_password\":\"NewSecurePass123!\"}"
}
```

### Test Event: Invalid Code

```json
{
  "body": "{\"email\":\"test@example.com\",\"code\":\"wrong\",\"new_password\":\"NewSecurePass123!\"}"
}
```

### Test Event: Weak Password

```json
{
  "body": "{\"email\":\"test@example.com\",\"code\":\"123456\",\"new_password\":\"weak\"}"
}
```

### Test Event: Missing Fields

```json
{
  "body": "{\"email\":\"test@example.com\"}"
}
```

---

## Testing Workflow

### 1. Test Registration Flow

1. **Register a new user** using the Register function
   - Use a real email you have access to
   - Note the verification code sent to your email
   
2. **Verify the user** in Cognito Console
   - Go to Cognito User Pool
   - Find the user
   - Confirm the user manually (or use the verification code)

3. **Get the user's profile** using Get Profile function
   - Replace `sub` with the actual user ID from Cognito
   - Should return the profile data

4. **Update the profile** using Update Profile function
   - Use the same user ID
   - Should update successfully

### 2. Test Password Reset Flow

1. **Initiate password reset** using Forgot Password function
   - Use an existing user's email
   - Check email for verification code

2. **Confirm password reset** using Confirm Password Reset function
   - Use the verification code from email
   - Should reset password successfully

3. **Try logging in** with new password
   - Use Cognito Hosted UI or AWS CLI

---

## Getting Real User IDs

To test with real users, you need actual Cognito user IDs. Get them using:

```bash
# List all users
aws cognito-idp list-users \
  --user-pool-id <YOUR_USER_POOL_ID> \
  --query 'Users[].{Username:Username,Sub:Attributes[?Name==`sub`].Value|[0],Email:Attributes[?Name==`email`].Value|[0]}'

# Or use the Makefile
cd infrastructure
make cognito-list-users ENV=dev
```

Then replace `test-user-id-123` in the test events with the actual `sub` value.

---

## Expected Responses

### Success Response (200)

```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
  },
  "body": "{\"success\":true,\"data\":{...},\"timestamp\":\"2024-03-19T10:30:00Z\"}"
}
```

### Error Response (400)

```json
{
  "statusCode": 400,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
  },
  "body": "{\"success\":false,\"error\":{\"code\":\"VALIDATION_ERROR\",\"message\":\"Invalid input data\",\"details\":{...}},\"timestamp\":\"2024-03-19T10:30:00Z\"}"
}
```

---

## Troubleshooting

### "User already exists" error
- The email is already registered
- Use a different email or delete the existing user from Cognito

### "Profile not found" error
- The user ID doesn't exist in DynamoDB
- Make sure the user was created via the Register function
- Check DynamoDB table for the user's profile

### "Authentication required" error
- The `requestContext.authorizer.claims` is missing or invalid
- Make sure you include the full authentication context in test events

### "Invalid verification code" error
- The code has expired (usually 24 hours)
- Request a new password reset
- Use the new code

---

## Quick Test Script

You can also test using AWS CLI:

```bash
# Register a user
aws lambda invoke \
  --function-name ImpressionnistesApi-dev-RegisterFunction \
  --payload '{"body":"{\"email\":\"test@example.com\",\"password\":\"TestPass123!\",\"first_name\":\"Jean\",\"last_name\":\"Dupont\",\"club_affiliation\":\"Test Club\",\"mobile_number\":\"+33612345678\"}"}' \
  response.json && cat response.json | jq

# Get profile (replace user-id)
aws lambda invoke \
  --function-name ImpressionnistesApi-dev-GetProfileFunction \
  --payload '{"requestContext":{"authorizer":{"claims":{"sub":"user-id-here","email":"test@example.com"}}}}' \
  response.json && cat response.json | jq
```

---

## Notes

- All test events simulate API Gateway request format
- The `body` field contains JSON as a string (escaped)
- Authentication context is in `requestContext.authorizer.claims`
- Replace placeholder values (user IDs, emails) with real data
- Check CloudWatch Logs for detailed error messages
