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

Register a new club manager account.

**Authentication**: None required

**Request Body**:
```json
{
  "email": "manager@club.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "club_affiliation": "Rowing Club Paris",
  "mobile_number": "+33612345678",
  "privacy_consent": true,
  "terms_consent": true,
  "consent_version": "1.0"
}
```

**Required Fields**:
- `email`: Valid email address
- `password`: Minimum 8 characters
- `first_name`: User's first name
- `last_name`: User's last name
- `club_affiliation`: Rowing club name
- `mobile_number`: Phone number with country code
- `privacy_consent`: Must be `true` (GDPR requirement)
- `terms_consent`: Must be `true` (GDPR requirement)
- `consent_version`: Current version (default: "1.0")

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
    "mobile_number": "+33612345678",
    "privacy_consent": true,
    "terms_consent": true,
    "consent_version": "1.0"
  }'
```

**Consent Records**:
Upon successful registration, two consent records are automatically created in DynamoDB:
- Privacy Policy consent record
- Terms & Conditions consent record

Both records include timestamp and optional IP address for audit trail. See [GDPR Compliance Guide](../guides/GDPR_COMPLIANCE.md#consent-storage-schema) for details.

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

### 400 Bad Request - Missing Consent
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "You must accept the Privacy Policy and Terms & Conditions to register",
    "details": {
      "consent": "Consent is required"
    }
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

## Boat Registration Endpoints

> **Terminology Note:** In the API and database, "boat" refers to a crew registration (the team of rowers). In the user interface, this is displayed as "Crew" (English) or "Équipage" (French). The term "boat" is only used in the UI when referring to physical equipment (boat types, boat rentals). See the [Requirements Document](../../.kiro/specs/impressionnistes-registration-system/requirements.md#terminology-mapping-databaseapi-vs-ui) for the complete terminology mapping.

### POST /boat

Create a new boat registration (crew).

**Authentication**: Required (Cognito JWT token)

**Headers**:
```
Authorization: Bearer <cognito-jwt-token>
```

**Request Body**:
```json
{
  "event_type": "21km",
  "boat_type": "4+",
  "race_id": null,
  "seats": [],
  "is_boat_rental": false
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "boat_registration_id": "uuid-here",
    "team_manager_id": "uuid-here",
    "event_type": "21km",
    "boat_type": "4+",
    "race_id": null,
    "seats": [
      {"position": 1, "type": "rower", "crew_member_id": null},
      {"position": 2, "type": "rower", "crew_member_id": null},
      {"position": 3, "type": "rower", "crew_member_id": null},
      {"position": 4, "type": "rower", "crew_member_id": null},
      {"position": 5, "type": "cox", "crew_member_id": null}
    ],
    "is_boat_rental": false,
    "is_multi_club_crew": false,
    "registration_status": "incomplete",
    "flagged_issues": [],
    "created_at": "2024-03-19T14:00:00Z",
    "updated_at": "2024-03-19T14:00:00Z"
  },
  "timestamp": "2024-03-19T14:00:00Z"
}
```

**cURL Example**:
```bash
curl -X POST https://your-api-url/dev/boat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "21km",
    "boat_type": "4+",
    "is_boat_rental": false
  }'
```

---

### GET /boat

List all boat registrations (crews) for the authenticated club manager.

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
    "boat_registrations": [
      {
        "boat_registration_id": "uuid-1",
        "event_type": "21km",
        "boat_type": "4+",
        "registration_status": "incomplete",
        "created_at": "2024-03-19T14:00:00Z"
      },
      {
        "boat_registration_id": "uuid-2",
        "event_type": "42km",
        "boat_type": "skiff",
        "registration_status": "complete",
        "created_at": "2024-03-19T15:00:00Z"
      }
    ]
  },
  "timestamp": "2024-03-19T16:00:00Z"
}
```

**cURL Example**:
```bash
curl -X GET https://your-api-url/dev/boat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### GET /boat/{boat_registration_id}

Get a specific boat registration (crew).

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
    "boat_registration_id": "uuid-here",
    "team_manager_id": "uuid-here",
    "event_type": "21km",
    "boat_type": "4+",
    "race_id": "race-uuid",
    "seats": [
      {"position": 1, "type": "rower", "crew_member_id": "crew-1"},
      {"position": 2, "type": "rower", "crew_member_id": "crew-2"},
      {"position": 3, "type": "rower", "crew_member_id": "crew-3"},
      {"position": 4, "type": "rower", "crew_member_id": "crew-4"},
      {"position": 5, "type": "cox", "crew_member_id": "crew-5"}
    ],
    "is_boat_rental": false,
    "is_multi_club_crew": false,
    "registration_status": "complete",
    "flagged_issues": [],
    "created_at": "2024-03-19T14:00:00Z",
    "updated_at": "2024-03-19T15:30:00Z"
  },
  "timestamp": "2024-03-19T16:00:00Z"
}
```

**cURL Example**:
```bash
curl -X GET https://your-api-url/dev/boat/BOAT_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### PUT /boat/{boat_registration_id}

Update a boat registration (crew).

**Authentication**: Required (Cognito JWT token)

**Headers**:
```
Authorization: Bearer <cognito-jwt-token>
```

**Request Body** (all fields optional):
```json
{
  "race_id": "race-uuid",
  "seats": [
    {"position": 1, "type": "rower", "crew_member_id": "crew-1"},
    {"position": 2, "type": "rower", "crew_member_id": "crew-2"},
    {"position": 3, "type": "rower", "crew_member_id": "crew-3"},
    {"position": 4, "type": "rower", "crew_member_id": "crew-4"},
    {"position": 5, "type": "cox", "crew_member_id": "crew-5"}
  ]
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "boat_registration_id": "uuid-here",
    "registration_status": "complete",
    "updated_at": "2024-03-19T16:30:00Z"
  },
  "message": "Boat registration updated successfully",
  "timestamp": "2024-03-19T16:30:00Z"
}
```

**cURL Example**:
```bash
curl -X PUT https://your-api-url/dev/boat/BOAT_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "race_id": "race-uuid"
  }'
```

---

### DELETE /boat/{boat_registration_id}

Delete a boat registration (crew).

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
    "message": "Boat registration deleted successfully"
  },
  "timestamp": "2024-03-19T17:00:00Z"
}
```

**cURL Example**:
```bash
curl -X DELETE https://your-api-url/dev/boat/BOAT_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Payment Endpoints

### GET /payments

List all payment transactions for the authenticated team manager.

**Authentication**: Required (Cognito JWT token)

**Headers**:
```
Authorization: Bearer <cognito-jwt-token>
```

**Query Parameters** (all optional):
- `start_date`: ISO 8601 date (e.g., "2026-01-01") - Filter payments from this date
- `end_date`: ISO 8601 date (e.g., "2026-12-31") - Filter payments until this date
- `limit`: Number (default: 50) - Maximum number of results per page
- `last_evaluated_key`: String - Pagination token from previous response

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "payments": [
      {
        "payment_id": "uuid-here",
        "stripe_payment_intent_id": "pi_xxx",
        "amount": 150.00,
        "currency": "EUR",
        "status": "succeeded",
        "paid_at": "2026-01-15T10:30:00Z",
        "stripe_receipt_url": "https://pay.stripe.com/receipts/...",
        "boat_registration_ids": ["boat-1", "boat-2"],
        "boat_count": 2
      }
    ],
    "summary": {
      "total_payments": 5,
      "total_amount": 750.00,
      "currency": "EUR"
    },
    "last_evaluated_key": null
  },
  "timestamp": "2026-01-16T12:00:00Z"
}
```

**cURL Example**:
```bash
curl -X GET "https://your-api-url/dev/payments?start_date=2026-01-01&end_date=2026-12-31" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### GET /payments/summary

Get payment summary including total paid and outstanding balance for the authenticated team manager.

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
    "total_paid": 750.00,
    "outstanding_balance": 300.00,
    "currency": "EUR",
    "unpaid_boats": [
      {
        "boat_registration_id": "boat-3",
        "event_type": "21km",
        "boat_type": "4+",
        "estimated_amount": 150.00,
        "registration_status": "complete"
      },
      {
        "boat_registration_id": "boat-4",
        "event_type": "42km",
        "boat_type": "skiff",
        "estimated_amount": 150.00,
        "registration_status": "complete"
      }
    ]
  },
  "timestamp": "2026-01-16T12:00:00Z"
}
```

**cURL Example**:
```bash
curl -X GET https://your-api-url/dev/payments/summary \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### GET /payments/{payment_id}/invoice

Download a payment invoice as PDF.

**Authentication**: Required (Cognito JWT token)

**Headers**:
```
Authorization: Bearer <cognito-jwt-token>
```

**Response (200 OK)**:
- **Content-Type**: `application/pdf`
- **Content-Disposition**: `attachment; filename="invoice-payment-{payment_id}-{date}.pdf"`
- **Body**: PDF binary data (base64 encoded)

**PDF Contents**:
- Event branding (Course des Impressionnistes)
- Payment date, amount, currency, payment ID
- Team manager name, club affiliation, email
- List of boats paid (event type, boat type)
- Link to Stripe receipt (if available)

**cURL Example**:
```bash
curl -X GET https://your-api-url/dev/payments/PAYMENT_ID/invoice \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o invoice.pdf
```

---

## Admin Payment Endpoints

### GET /admin/payments

List all payment transactions across all team managers (admin only).

**Authentication**: Required (Cognito JWT token with admin role)

**Headers**:
```
Authorization: Bearer <cognito-jwt-token>
```

**Query Parameters** (all optional):
- `team_manager_id`: String - Filter by specific team manager
- `start_date`: ISO 8601 date - Filter payments from this date
- `end_date`: ISO 8601 date - Filter payments until this date
- `sort_by`: String (default: "paid_at") - Sort field (paid_at, amount, team_manager_name)
- `sort_order`: String (default: "desc") - Sort order (asc, desc)
- `limit`: Number (default: 50) - Maximum results per page
- `last_evaluated_key`: String - Pagination token

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "payments": [
      {
        "payment_id": "uuid-1",
        "team_manager_id": "tm-1",
        "team_manager_name": "Jean Dupont",
        "team_manager_email": "jean@club.com",
        "club_affiliation": "Rowing Club Paris",
        "amount": 150.00,
        "currency": "EUR",
        "status": "succeeded",
        "paid_at": "2026-01-15T10:30:00Z",
        "boat_count": 2
      }
    ],
    "summary": {
      "total_payments": 25,
      "total_amount": 3750.00,
      "currency": "EUR"
    },
    "last_evaluated_key": null
  },
  "timestamp": "2026-01-16T12:00:00Z"
}
```

**cURL Example**:
```bash
curl -X GET "https://your-api-url/dev/admin/payments?sort_by=amount&sort_order=desc" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN"
```

---

### GET /admin/payments/analytics

Get payment analytics and trends (admin only).

**Authentication**: Required (Cognito JWT token with admin role)

**Headers**:
```
Authorization: Bearer <cognito-jwt-token>
```

**Query Parameters** (all optional):
- `start_date`: ISO 8601 date - Filter analytics from this date
- `end_date`: ISO 8601 date - Filter analytics until this date
- `group_by`: String (default: "day") - Time grouping (day, week, month)

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_revenue": 3750.00,
      "total_payments": 25,
      "total_boats_paid": 50,
      "unique_payers": 10,
      "outstanding_balance": 1200.00,
      "currency": "EUR"
    },
    "timeline": [
      {
        "period": "2026-01-15",
        "payment_count": 5,
        "total_amount": 750.00
      },
      {
        "period": "2026-01-16",
        "payment_count": 3,
        "total_amount": 450.00
      }
    ],
    "top_payers": [
      {
        "team_manager_id": "tm-1",
        "team_manager_name": "Jean Dupont",
        "club_affiliation": "Rowing Club Paris",
        "total_paid": 450.00,
        "payment_count": 3,
        "boat_count": 6
      }
    ]
  },
  "timestamp": "2026-01-16T12:00:00Z"
}
```

**cURL Example**:
```bash
curl -X GET "https://your-api-url/dev/admin/payments/analytics?group_by=week" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN"
```

---

## Access Control

### Payment Permissions

| Permission | Team Manager | Admin |
|------------|--------------|-------|
| View own payment history | ✓ | ✓ |
| View own payment summary | ✓ | ✓ |
| Download payment invoice | ✓ | ✓ |
| View all payments | ✗ | ✓ |
| View payment analytics | ✗ | ✓ |
| Export payment data | ✗ | ✓ |

### Access Control Rules

1. **Team managers** can only access their own payment data
2. **Admins** can access all payment data across all team managers
3. Attempting to access another team manager's payment returns 404 Not Found
4. Attempting to access admin endpoints without admin role returns 403 Forbidden

---

## Next Steps

- Add admin endpoints (/admin/*)
- Add contact form endpoint (/contact)
