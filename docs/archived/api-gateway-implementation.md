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

## Crew Member Management Endpoints

### POST /crew - Create Crew Member

Create a new crew member for the authenticated club manager.

**Authentication**: Required (Club Manager)

**Request Body**:
```json
{
  "first_name": "Marie",
  "last_name": "Dubois",
  "date_of_birth": "1995-06-15",
  "gender": "F",
  "license_number": "ABC123456",
  "club_affiliation": "RCPM"
}
```

**Response** (201 Created):
```json
{
  "crew_member_id": "550e8400-e29b-41d4-a716-446655440000",
  "team_manager_id": "user-sub-id",
  "first_name": "Marie",
  "last_name": "Dubois",
  "date_of_birth": "1995-06-15",
  "gender": "F",
  "license_number": "ABC123456",
  "club_affiliation": "RCPM",
  "is_rcpm_member": true,
  "assigned_boat_id": null,
  "flagged_issues": [],
  "created_at": "2024-11-14T20:30:00Z",
  "updated_at": "2024-11-14T20:30:00Z"
}
```

**cURL Example**:
```bash
curl -X POST $API_URL/crew \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Marie",
    "last_name": "Dubois",
    "date_of_birth": "1995-06-15",
    "gender": "F",
    "license_number": "ABC123456",
    "club_affiliation": "RCPM"
  }'
```

**Validation Rules**:
- `first_name`: Required, 1-50 characters
- `last_name`: Required, 1-50 characters
- `date_of_birth`: Required, YYYY-MM-DD format
- `gender`: Required, "M" or "F"
- `license_number`: Required, alphanumeric 6-12 characters
- `club_affiliation`: Optional, defaults to club manager's club, max 100 characters

**Notes**:
- `is_rcpm_member` is automatically calculated based on club_affiliation
- If club_affiliation is not provided, it defaults to the club manager's club
- License number is automatically converted to uppercase

---

### GET /crew - List Crew Members

Get all crew members for the authenticated club manager.

**Authentication**: Required (Club Manager)

**Response** (200 OK):
```json
{
  "crew_members": [
    {
      "crew_member_id": "550e8400-e29b-41d4-a716-446655440000",
      "team_manager_id": "user-sub-id",
      "first_name": "Marie",
      "last_name": "Dubois",
      "date_of_birth": "1995-06-15",
      "gender": "F",
      "license_number": "ABC123456",
      "club_affiliation": "RCPM",
      "is_rcpm_member": true,
      "assigned_boat_id": null,
      "flagged_issues": [],
      "created_at": "2024-11-14T20:30:00Z",
      "updated_at": "2024-11-14T20:30:00Z"
    },
    {
      "crew_member_id": "660e8400-e29b-41d4-a716-446655440001",
      "team_manager_id": "user-sub-id",
      "first_name": "Pierre",
      "last_name": "Martin",
      "date_of_birth": "1992-03-22",
      "gender": "M",
      "license_number": "XYZ789012",
      "club_affiliation": "External Club",
      "is_rcpm_member": false,
      "assigned_boat_id": "boat-123",
      "flagged_issues": [],
      "created_at": "2024-11-14T20:35:00Z",
      "updated_at": "2024-11-14T20:35:00Z"
    }
  ]
}
```

**cURL Example**:
```bash
curl -X GET $API_URL/crew \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### GET /crew/{crew_member_id} - Get Crew Member

Get details of a specific crew member.

**Authentication**: Required (Club Manager)

**Path Parameters**:
- `crew_member_id`: UUID of the crew member

**Response** (200 OK):
```json
{
  "crew_member_id": "550e8400-e29b-41d4-a716-446655440000",
  "team_manager_id": "user-sub-id",
  "first_name": "Marie",
  "last_name": "Dubois",
  "date_of_birth": "1995-06-15",
  "gender": "F",
  "license_number": "ABC123456",
  "club_affiliation": "RCPM",
  "is_rcpm_member": true,
  "assigned_boat_id": null,
  "flagged_issues": [],
  "created_at": "2024-11-14T20:30:00Z",
  "updated_at": "2024-11-14T20:30:00Z"
}
```

**cURL Example**:
```bash
curl -X GET $API_URL/crew/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Error Responses**:
- `404 Not Found`: Crew member doesn't exist or doesn't belong to the club manager

---

### PUT /crew/{crew_member_id} - Update Crew Member

Update an existing crew member's information.

**Authentication**: Required (Club Manager)

**Path Parameters**:
- `crew_member_id`: UUID of the crew member

**Request Body** (all fields optional):
```json
{
  "first_name": "Marie-Claire",
  "last_name": "Dubois-Martin",
  "date_of_birth": "1995-06-15",
  "gender": "F",
  "license_number": "ABC123789",
  "club_affiliation": "RCPM Paris"
}
```

**Response** (200 OK):
```json
{
  "crew_member_id": "550e8400-e29b-41d4-a716-446655440000",
  "team_manager_id": "user-sub-id",
  "first_name": "Marie-Claire",
  "last_name": "Dubois-Martin",
  "date_of_birth": "1995-06-15",
  "gender": "F",
  "license_number": "ABC123789",
  "club_affiliation": "RCPM Paris",
  "is_rcpm_member": true,
  "assigned_boat_id": null,
  "flagged_issues": [],
  "created_at": "2024-11-14T20:30:00Z",
  "updated_at": "2024-11-14T21:15:00Z"
}
```

**cURL Example**:
```bash
curl -X PUT $API_URL/crew/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Marie-Claire",
    "license_number": "ABC123789"
  }'
```

**Notes**:
- Only provided fields will be updated
- `is_rcpm_member` is recalculated if `club_affiliation` changes
- Updates are allowed during the registration period
- After registration period ends, admin must grant temporary editing access

**Error Responses**:
- `404 Not Found`: Crew member doesn't exist
- `403 Forbidden`: Registration period ended and no editing access granted

---

### DELETE /crew/{crew_member_id} - Delete Crew Member

Delete a crew member (only if not assigned to a boat).

**Authentication**: Required (Club Manager)

**Path Parameters**:
- `crew_member_id`: UUID of the crew member

**Response** (200 OK):
```json
{
  "message": "Crew member deleted successfully"
}
```

**cURL Example**:
```bash
curl -X DELETE $API_URL/crew/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Error Responses**:
- `404 Not Found`: Crew member doesn't exist
- `409 Conflict`: Crew member is assigned to a boat (must be removed from boat first)

---

## Testing Crew Member Endpoints

### Complete Workflow Example

```bash
# Set your API URL and token
API_URL="https://your-api-id.execute-api.eu-west-3.amazonaws.com/dev"
TOKEN="your-jwt-token"

# 1. Create a crew member
CREW_RESPONSE=$(curl -s -X POST $API_URL/crew \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Sophie",
    "last_name": "Laurent",
    "date_of_birth": "1998-09-10",
    "gender": "F",
    "license_number": "SL987654",
    "club_affiliation": "RCPM"
  }')

echo "Created crew member:"
echo $CREW_RESPONSE | jq .

# Extract crew member ID
CREW_ID=$(echo $CREW_RESPONSE | jq -r '.crew_member_id')

# 2. Get the crew member
curl -s -X GET $API_URL/crew/$CREW_ID \
  -H "Authorization: Bearer $TOKEN" | jq .

# 3. List all crew members
curl -s -X GET $API_URL/crew \
  -H "Authorization: Bearer $TOKEN" | jq .

# 4. Update the crew member
curl -s -X PUT $API_URL/crew/$CREW_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Sophie-Marie"
  }' | jq .

# 5. Delete the crew member (only if not assigned)
curl -s -X DELETE $API_URL/crew/$CREW_ID \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Test Data Examples

**RCPM Member**:
```json
{
  "first_name": "Jean",
  "last_name": "Dupont",
  "date_of_birth": "1990-05-15",
  "gender": "M",
  "license_number": "JD123456",
  "club_affiliation": "RCPM"
}
```

**External Club Member**:
```json
{
  "first_name": "Alice",
  "last_name": "Bernard",
  "date_of_birth": "1993-08-22",
  "gender": "F",
  "license_number": "AB789012",
  "club_affiliation": "Aviron Club Paris"
}
```

**Member with Default Club** (uses team manager's club):
```json
{
  "first_name": "Thomas",
  "last_name": "Petit",
  "date_of_birth": "1995-12-03",
  "gender": "M",
  "license_number": "TP456789"
}
```

---

### Future API Endpoints

Add more endpoints as you implement features:
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
