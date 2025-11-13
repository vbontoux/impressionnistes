# API Endpoints Documentation

## Base URL

After deployment, get the API URL from CloudFormation outputs:

```bash
aws cloudformation describe-stacks \
  --stack-name ImpressionnistesApi-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

Or from CDK output after deployment.

## Authentication Endpoints

### POST /auth/register

Register a new team manager account.

**Authentication**: None required

**Request Body**:
```json
{
  "email": "manager@club.com",
  "password": "SecurePass123!",
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

**cURL Example**:
```bash
curl -X POST https://your-api-url/dev/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "first_name": "Jean",
    "last_name": "Dupont",
    "club_affiliation": "Test Club",
    "mobile_number": "+33612345678"
  }'
```

---

### GET /auth/profile

Get the authenticated user's profile.

**Authentication**: Required (Cognito JWT token)

**Headers**:
```
Authorization: Bearer <cognito-jwt-token>
```

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

**cURL Example**:
```bash
curl -X GET https://your-api-url/dev/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### PUT /auth/profile

Update the authenticated user's profile.

**Authentication**: Required (Cognito JWT token)

**Headers**:
```
Authorization: Bearer <cognito-jwt-token>
```

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

**cURL Example**:
```bash
curl -X PUT https://your-api-url/dev/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Pierre"}'
```

---

### POST /auth/forgot-password

Initiate password reset process.

**Authentication**: None required

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

**cURL Example**:
```bash
curl -X POST https://your-api-url/dev/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

---

### POST /auth/reset-password

Confirm password reset with verification code.

**Authentication**: None required

**Request Body**:
```json
{
  "email": "manager@club.com",
  "code": "123456",
  "new_password": "NewSecurePass123!"
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

**cURL Example**:
```bash
curl -X POST https://your-api-url/dev/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456",
    "new_password": "NewPass123!"
  }'
```

---

## Authentication Flow

### 1. Register

```bash
POST /auth/register
→ Returns user_id
→ Email sent with verification code
```

### 2. Verify Email (via Cognito Hosted UI or AWS CLI)

```bash
aws cognito-idp confirm-sign-up \
  --client-id YOUR_CLIENT_ID \
  --username user@example.com \
  --confirmation-code 123456
```

### 3. Login (via Cognito Hosted UI or AWS SDK)

Use Cognito Hosted UI or AWS Amplify to get JWT token.

### 4. Use JWT Token

Include in Authorization header for protected endpoints:
```
Authorization: Bearer eyJraWQiOiJ...
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": "Invalid email format"
    }
  },
  "timestamp": "2024-03-19T10:30:00Z"
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  },
  "timestamp": "2024-03-19T10:30:00Z"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Profile not found"
  },
  "timestamp": "2024-03-19T10:30:00Z"
}
```

### 409 Conflict
```json
{
  "success": false,
  "error": {
    "code": "CONFLICT",
    "message": "An account with this email already exists"
  },
  "timestamp": "2024-03-19T10:30:00Z"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred"
  },
  "timestamp": "2024-03-19T10:30:00Z"
}
```

---

## CORS Configuration

The API is configured with CORS to allow:
- **Origins**: All origins (restrict in production)
- **Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Headers**: Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token
- **Credentials**: Allowed

---

## Rate Limiting

- **Rate Limit**: 1000 requests/second
- **Burst Limit**: 2000 requests

---

## Deployment

Deploy the API:

```bash
cd infrastructure
make deploy-api ENV=dev
```

Get the API URL:

```bash
aws cloudformation describe-stacks \
  --stack-name ImpressionnistesApi-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

---

## Testing

### Using cURL

```bash
# Set API URL
API_URL="https://your-api-id.execute-api.eu-west-3.amazonaws.com/dev"

# Register
curl -X POST $API_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!","first_name":"Jean","last_name":"Dupont","club_affiliation":"Test Club","mobile_number":"+33612345678"}'

# Get profile (requires JWT token)
curl -X GET $API_URL/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Using Postman

1. Import the API endpoints
2. Set up environment variable for API_URL
3. For authenticated endpoints, add Authorization header with Bearer token

---

## Next Steps

- Add crew member endpoints (/crew/*)
- Add boat registration endpoints (/boat/*)
- Add payment endpoints (/payment/*)
- Add admin endpoints (/admin/*)
- Add contact form endpoint (/contact)
