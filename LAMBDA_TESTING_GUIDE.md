# Lambda Testing Guide

Quick guide for testing Lambda functions in the AWS Console.

## Test Files

- **`functions/auth/TEST_EVENTS.md`** - Detailed guide with all test events and explanations
- **`functions/auth/test-events.json`** - JSON file with all test payloads

## Quick Start

### 1. Find Your Lambda Functions

Go to AWS Lambda Console and look for:
- `ImpressionnistesApi-dev-RegisterFunction`
- `ImpressionnistesApi-dev-GetProfileFunction`
- `ImpressionnistesApi-dev-UpdateProfileFunction`
- `ImpressionnistesApi-dev-ForgotPasswordFunction`
- `ImpressionnistesApi-dev-ConfirmPasswordResetFunction`

### 2. Test Registration

1. Open `RegisterFunction`
2. Click "Test" tab
3. Create new test event named "register-test"
4. Paste this JSON:

```json
{
  "body": "{\"email\":\"your-email@example.com\",\"password\":\"TestPass123!\",\"first_name\":\"Jean\",\"last_name\":\"Dupont\",\"club_affiliation\":\"Test Club\",\"mobile_number\":\"+33612345678\"}"
}
```

5. Click "Test"
6. Check the response - should be 201 Created

### 3. Verify User in Cognito

1. Go to Amazon Cognito Console
2. Select your User Pool (`impressionnistes-users-dev`)
3. Find the user you just created
4. Click "Confirm user" (or use the verification code from email)
5. Copy the user's `sub` (user ID) - you'll need this for other tests

### 4. Test Get Profile

1. Open `GetProfileFunction`
2. Create test event with your user's `sub`:

```json
{
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com",
        "given_name": "Jean",
        "family_name": "Dupont",
        "custom:club_affiliation": "Test Club",
        "custom:role": "team_manager",
        "cognito:groups": "team_managers"
      }
    }
  }
}
```

3. Click "Test"
4. Should return your profile data

### 5. Test Update Profile

1. Open `UpdateProfileFunction`
2. Create test event:

```json
{
  "body": "{\"first_name\":\"Pierre\",\"club_affiliation\":\"New Club\"}",
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com"
      }
    }
  }
}
```

3. Click "Test"
4. Should return updated profile

### 6. Test Password Reset

1. Open `ForgotPasswordFunction`
2. Create test event:

```json
{
  "body": "{\"email\":\"your-email@example.com\"}"
}
```

3. Click "Test"
4. Check your email for verification code
5. Open `ConfirmPasswordResetFunction`
6. Create test event with the code:

```json
{
  "body": "{\"email\":\"your-email@example.com\",\"code\":\"123456\",\"new_password\":\"NewPass123!\"}"
}
```

7. Click "Test"
8. Password should be reset

## Getting User IDs

### Option 1: From Cognito Console
1. Go to Cognito User Pool
2. Click on Users
3. Click on a user
4. Copy the `sub` attribute

### Option 2: Using AWS CLI

```bash
aws cognito-idp list-users \
  --user-pool-id $(aws cloudformation describe-stacks \
    --stack-name ImpressionnistesAuth-dev \
    --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
    --output text) \
  --query 'Users[].{Email:Attributes[?Name==`email`].Value|[0],Sub:Attributes[?Name==`sub`].Value|[0]}'
```

### Option 3: Using Makefile

```bash
cd infrastructure
make cognito-list-users ENV=dev
```

## Checking Logs

View function logs in CloudWatch:

```bash
# View logs for a specific function
aws logs tail /aws/lambda/ImpressionnistesApi-dev-RegisterFunction --follow

# Or in the Lambda Console
# Click on "Monitor" tab → "View CloudWatch logs"
```

## Common Issues

### "User already exists"
- Email is already registered
- Use a different email or delete the user from Cognito

### "Profile not found"
- User wasn't created via Register function
- Check DynamoDB table: `impressionnistes-registration-dev`
- Look for item with PK=`USER#{user-id}` and SK=`PROFILE`

### "Invalid verification code"
- Code expired (24 hours)
- Request new password reset

### "Authentication required"
- Missing `requestContext.authorizer.claims`
- Make sure to include full auth context in test event

## Verify in DynamoDB

Check if profile was created:

```bash
aws dynamodb get-item \
  --table-name impressionnistes-registration-dev \
  --key '{"PK":{"S":"USER#your-user-id"},"SK":{"S":"PROFILE"}}'
```

Or use the Makefile:

```bash
cd infrastructure
make db-view ENV=dev
```

## Success Indicators

✅ **Register**: Returns 201 with user_id and success message
✅ **Get Profile**: Returns 200 with complete profile data
✅ **Update Profile**: Returns 200 with updated fields
✅ **Forgot Password**: Returns 200 (always, for security)
✅ **Confirm Reset**: Returns 200 with success message

## Next Steps

After testing individual functions:
1. Test the complete registration flow
2. Test error cases (invalid data, missing fields)
3. Test with multiple users
4. Verify data in DynamoDB
5. Check CloudWatch logs for any warnings

## Full Test Event Reference

See `functions/auth/TEST_EVENTS.md` for:
- All test event variations
- Error case testing
- Expected responses
- Troubleshooting guide
- CLI testing commands
