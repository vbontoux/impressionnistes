# Authentication API Documentation

## Overview

This document describes the authentication Lambda functions for team manager registration and profile management.

## Lambda Functions

### 1. Register (`functions/auth/register.py`)

Creates a new team manager account in Cognito and stores profile in DynamoDB.

**Handler**: `auth.register.lambda_handler`

**Request Body**:
```json
{
  "email": "manager@club.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "club_affiliation": "Rowing Club Paris",
  "mobile_number": "+33612345678"
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "user_id": "uuid-here",
    "email": "manager@club.com",
    "first_name": "John",
    "last_name": "Doe",
    "club_affiliation": "Rowing Club Paris",
    "message": "Registration successful. Please check your email to verify your account."
  },
  "timestamp": "2024-03-19T10:30:00Z"
}
```

**Errors**:
- `400 VALIDATION_ERROR`: Invalid input data
- `409 CONFLICT`: Email already exists
- `500 INTERNAL_ERROR`: Server error

**Features**:
- Creates Cognito user with email verification
- Stores profile in DynamoDB
- Automatically adds user to `team_managers` group
- Sends verification email

---

### 2. Get Profile (`functions/auth/get_profile.py`)

Retrieves the authenticated user's profile.

**Handler**: `auth.get_profile.lambda_handler`

**Authentication**: Required (Cognito JWT)

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "user_id": "uuid-here",
    "email": "manager@club.com",
    "first_name": "John",
    "last_name": "Doe",
    "club_affiliation": "Rowing Club Paris",
    "mobile_number": "+33612345678",
    "role": "team_manager",
    "created_at": "2024-03-19T10:30:00Z",
    "updated_at": "2024-03-19T10:30:00Z"
  },
  "timestamp": "2024-03-19T10:35:00Z"
}
```

**Errors**:
- `401 UNAUTHORIZED`: Not authenticated
- `404 NOT_FOUND`: Profile not found
- `500 INTERNAL_ERROR`: Server error

---

### 3. Update Profile (`functions/auth/update_profile.py`)

Updates the authenticated user's profile.

**Handler**: `auth.update_profile.lambda_handler`

**Authentication**: Required (Cognito JWT)

**Request Body** (all fields optional):
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "club_affiliation": "New Rowing Club",
  "mobile_number": "+33698765432"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "user_id": "uuid-here",
    "email": "manager@club.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "club_affiliation": "New Rowing Club",
    "mobile_number": "+33698765432",
    "updated_at": "2024-03-19T11:00:00Z"
  },
  "message": "Profile updated successfully",
  "timestamp": "2024-03-19T11:00:00Z"
}
```

**Errors**:
- `400 VALIDATION_ERROR`: Invalid input data
- `401 UNAUTHORIZED`: Not authenticated
- `404 NOT_FOUND`: Profile not found
- `500 INTERNAL_ERROR`: Server error

**Features**:
- Updates both Cognito user attributes and DynamoDB profile
- Validates all fields before updating
- Maintains audit trail with `updated_at` timestamp

---

### 4. Forgot Password (`functions/auth/forgot_password.py`)

Initiates password reset process by sending verification code via email.

**Handler**: `auth.forgot_password.lambda_handler`

**Request Body**:
```json
{
  "email": "manager@club.com"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "If an account exists with this email, a password reset code has been sent."
  },
  "timestamp": "2024-03-19T12:00:00Z"
}
```

**Errors**:
- `400 VALIDATION_ERROR`: Invalid email format or rate limit exceeded
- `500 INTERNAL_ERROR`: Server error

**Security Features**:
- Always returns success (doesn't reveal if user exists)
- Rate limiting to prevent abuse
- Verification code expires after a set time

---

### 5. Confirm Password Reset (`functions/auth/confirm_password_reset.py`)

Confirms password reset with verification code.

**Handler**: `auth.confirm_password_reset.lambda_handler`

**Request Body**:
```json
{
  "email": "manager@club.com",
  "code": "123456",
  "new_password": "NewSecurePass123"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "Password has been reset successfully. You can now log in with your new password."
  },
  "timestamp": "2024-03-19T12:05:00Z"
}
```

**Errors**:
- `400 VALIDATION_ERROR`: Invalid code, expired code, or weak password
- `404 NOT_FOUND`: User not found
- `500 INTERNAL_ERROR`: Server error

**Password Requirements**:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

---

## Environment Variables

All Lambda functions require these environment variables:

- `TABLE_NAME`: DynamoDB table name
- `USER_POOL_ID`: Cognito User Pool ID
- `USER_POOL_CLIENT_ID`: Cognito User Pool Client ID
- `ENVIRONMENT`: Environment name (dev/prod)

## IAM Permissions

Lambda functions require:

**DynamoDB**:
- `dynamodb:GetItem`
- `dynamodb:PutItem`
- `dynamodb:UpdateItem`
- `dynamodb:Query`

**Cognito**:
- `cognito-idp:AdminCreateUser`
- `cognito-idp:AdminUpdateUserAttributes`
- `cognito-idp:AdminAddUserToGroup`
- `cognito-idp:AdminGetUser`
- `cognito-idp:ListUsers`

## Testing

### Local Testing

You can test Lambda functions locally using the AWS SAM CLI or by invoking them directly with test events.

### Manual Testing with AWS CLI

```bash
# Register a new user
aws lambda invoke \
  --function-name ImpressionnistesApi-dev-RegisterFunction \
  --payload '{"body": "{\"email\":\"test@example.com\",\"password\":\"Test123!\",\"first_name\":\"Test\",\"last_name\":\"User\",\"club_affiliation\":\"Test Club\",\"mobile_number\":\"+33612345678\"}"}' \
  response.json

# Get profile (requires authentication token)
aws lambda invoke \
  --function-name ImpressionnistesApi-dev-GetProfileFunction \
  --payload '{"requestContext":{"authorizer":{"claims":{"sub":"user-id","email":"test@example.com"}}}}' \
  response.json
```

## Deployment

Deploy the API stack with:

```bash
cd infrastructure
make deploy-api ENV=dev
```

Or deploy all stacks:

```bash
make deploy ENV=dev
```

## Monitoring

All Lambda functions log to CloudWatch Logs with structured JSON logging.

View logs:
```bash
aws logs tail /aws/lambda/ImpressionnistesApi-dev-RegisterFunction --follow
```

## Next Steps

- Task 18.1: Create API Gateway REST API with routes
- Task 18.3: Wire up Lambda functions to API Gateway endpoints
- Task 2.3: Build frontend authentication components
