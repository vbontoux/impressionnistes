# API Gateway Implementation - Tasks 18.1 & 18.3

## Summary

Implemented API Gateway REST API with Cognito authorization and connected all authentication Lambda functions to HTTP endpoints.

## What Was Implemented

### Task 18.1: API Gateway REST API ✅

1. **REST API Created**
   - Name: `impressionnistes-api-{env}`
   - Description: Course des Impressionnistes Registration System API
   - Stage: dev/prod (environment-based)

2. **CORS Configuration**
   - Allow all origins (TODO: restrict in production)
   - Allow all methods (GET, POST, PUT, DELETE, OPTIONS)
   - Allow credentials
   - Headers: Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token

3. **Cognito Authorizer**
   - Integrated with Cognito User Pool
   - Identity source: Authorization header
   - Protects authenticated endpoints

4. **Logging & Monitoring**
   - CloudWatch logging enabled
   - Log level: INFO
   - Data trace enabled
   - Metrics enabled

5. **Rate Limiting**
   - Rate limit: 1000 requests/second
   - Burst limit: 2000 requests

### Task 18.3: API Gateway Routes (Auth Endpoints) ✅

| Method | Endpoint | Auth Required | Lambda Function |
|--------|----------|---------------|-----------------|
| POST | `/auth/register` | No | RegisterFunction |
| GET | `/auth/profile` | Yes | GetProfileFunction |
| PUT | `/auth/profile` | Yes | UpdateProfileFunction |
| POST | `/auth/forgot-password` | No | ForgotPasswordFunction |
| POST | `/auth/reset-password` | No | ConfirmPasswordResetFunction |

## Files Modified

1. **`infrastructure/stacks/api_stack.py`**
   - Added `_create_api_gateway()` method
   - Created REST API with CORS
   - Added Cognito authorizer
   - Wired up all 5 auth endpoints
   - Added CloudFormation output for API URL

## Files Created

1. **`infrastructure/API_ENDPOINTS.md`**
   - Complete API documentation
   - Request/response examples
   - cURL examples
   - Error responses
   - Authentication flow

## Deployment

Deploy the updated API stack:

```bash
cd infrastructure
make deploy-api ENV=dev
```

## Get API URL

After deployment:

```bash
aws cloudformation describe-stacks \
  --stack-name ImpressionnistesApi-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

Or check the CDK output during deployment.

## Testing the API

### 1. Register a User

```bash
API_URL="https://your-api-id.execute-api.eu-west-3.amazonaws.com/dev"

curl -X POST $API_URL/auth/register \
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

### 2. Verify Email

Use Cognito Console or AWS CLI to confirm the user.

### 3. Get JWT Token

Use Cognito Hosted UI or AWS Amplify to authenticate and get a JWT token.

### 4. Get Profile

```bash
curl -X GET $API_URL/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 5. Update Profile

```bash
curl -X PUT $API_URL/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Pierre"}'
```

## Architecture

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────────┐
│   API Gateway       │
│  - CORS enabled     │
│  - Rate limiting    │
│  - Logging          │
└──────┬──────────────┘
       │
       ├─ No Auth ──────► POST /auth/register ──────► RegisterFunction
       │                  POST /auth/forgot-password ► ForgotPasswordFunction
       │                  POST /auth/reset-password ─► ConfirmPasswordResetFunction
       │
       └─ Cognito Auth ─► GET  /auth/profile ────────► GetProfileFunction
                          PUT  /auth/profile ────────► UpdateProfileFunction
                                    │
                                    ▼
                          ┌──────────────────┐
                          │  Cognito         │
                          │  User Pool       │
                          │  - JWT tokens    │
                          │  - User groups   │
                          └──────────────────┘
```

## Security Features

1. **Cognito Authorization**
   - JWT token validation
   - User pool integration
   - Automatic token expiration (30 minutes)

2. **CORS**
   - Configured for cross-origin requests
   - Credentials allowed
   - TODO: Restrict origins in production

3. **Rate Limiting**
   - Prevents API abuse
   - 1000 req/s with 2000 burst

4. **HTTPS Only**
   - All traffic encrypted
   - TLS 1.2+

## Next Steps

### For Frontend (Task 2.3)

Now that API Gateway is ready, you can:
1. Build Vue.js authentication components
2. Call real API endpoints (no mocking needed)
3. Handle JWT tokens from Cognito
4. Implement auth guards in Vue Router

### Future API Endpoints

Add more endpoints as you implement features:
- `/crew/*` - Crew member management
- `/boat/*` - Boat registration
- `/payment/*` - Payment processing
- `/admin/*` - Admin operations
- `/contact` - Contact form

## Troubleshooting

### CORS Errors

If you get CORS errors:
1. Check that CORS is enabled in API Gateway
2. Verify the request includes proper headers
3. Check browser console for specific CORS error

### 401 Unauthorized

If authenticated endpoints return 401:
1. Verify JWT token is valid
2. Check Authorization header format: `Bearer <token>`
3. Ensure token hasn't expired (30 min lifetime)
4. Verify user is in correct Cognito group

### 403 Forbidden

If you get 403:
1. Check user has required permissions
2. Verify Cognito authorizer is configured correctly
3. Check CloudWatch logs for details

## Monitoring

View API Gateway logs:

```bash
aws logs tail /aws/apigateway/impressionnistes-api-dev --follow
```

View Lambda function logs:

```bash
aws logs tail /aws/lambda/ImpressionnistesApi-dev-RegisterFunction --follow
```

## Status

✅ **Task 18.1 Complete** - API Gateway REST API set up
✅ **Task 18.3 Partial** - Auth endpoints implemented
⏳ **Task 2.3 Ready** - Can now build frontend components

## Documentation

- **API Endpoints**: `infrastructure/API_ENDPOINTS.md`
- **Lambda Testing**: `functions/auth/TEST_EVENTS.md`
- **Auth Stack**: `infrastructure/AUTH.md`
