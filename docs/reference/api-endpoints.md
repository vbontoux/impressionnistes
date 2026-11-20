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
- `password`: Minimum 12 characters, must include uppercase, lowercase, number, and special character
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

### 2. Verify Email (via verification code on self-hosted page)

```bash
aws cognito-idp confirm-sign-up \
  --client-id YOUR_CLIENT_ID \
  --username user@example.com \
  --confirmation-code 123456
```

### 3. Login (via self-hosted login page or AWS SDK)

Use the self-hosted login page or AWS SDK to authenticate and get JWT token.

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

## Admin Database Backup Endpoints

All five endpoints require a Cognito JWT token for a user in the `admins` group. They are served by the `manage_backups` Lambda (`functions/admin/manage_backups.py`, logic in `functions/shared/backup_service.py`).

**Authentication**: Required (Cognito JWT token with admin role) for all endpoints below.

**Headers**:
```
Authorization: Bearer <cognito-jwt-token>
```

**Backup ids**: the `backup_id` is also the S3 object key and the download file name.
- Manual backup: `manual_<timestamp>.json`, e.g. `manual_2026-11-01T14-30-00Z.json`
- Safety backup (created automatically before a restore): `safety-pre-restore_<timestamp>_before-restore-of_<category>_<timestamp>.json`, e.g. `safety-pre-restore_2026-11-02T09-00-00Z_before-restore-of_manual_2026-11-01T14-30-00Z.json`. The part after `_before-restore-of_` is the category and timestamp of the source backup (the full source id is returned in `source_backup_id`).
- Pre-reset backup (created automatically before a database purge): `safety-pre-reset_<timestamp>.json`, e.g. `safety-pre-reset_2026-11-02T09-00-00Z.json`. It has no source part. Restoring it creates a `safety-pre-restore` backup whose source is the `safety-pre-reset` id.
- `<timestamp>` is UTC, formatted `YYYY-MM-DDTHH-MM-SSZ`.

**Notes**:
- Each backup creates two artifacts: a JSON file in the backup S3 bucket and an AWS native DynamoDB backup (`native_backup`). The native backup is not removed when the JSON backup is deleted.
- Backups contain every item of the registration table (all partitions), in DynamoDB typed JSON.
- Create, delete and restore are recorded as `AUDIT#DATABASE_BACKUP` items (action, admin identity, timestamp).

---

### POST /admin/backups

Create a manual backup (JSON file + AWS native backup).

**Path Parameters**: none

**Request Body**: none

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "backup_id": "manual_2026-11-01T14-30-00Z.json",
    "category": "manual",
    "item_count": 1250,
    "size_bytes": 834512,
    "created_at": "2026-11-01T14:30:00Z",
    "source_backup_id": null,
    "native_backup": {
      "name": "impressionnistes-registration-prod-manual_2026-11-01T14-30-00Z",
      "arn": "arn:aws:dynamodb:eu-west-3:123456789012:table/impressionnistes-registration-prod/backup/01234567890123-abcdef01",
      "status": "CREATING"
    }
  },
  "timestamp": "2026-11-01T14:30:05Z"
}
```

**Errors**:

| HTTP | Code | When |
|------|------|------|
| 401 | `UNAUTHORIZED` | No valid token |
| 403 | `FORBIDDEN` | User is not in the `admins` group |
| 500 | `JSON_BACKUP_FAILED` | Table scan or S3 write failed; nothing was stored (`details.failed_artifact = "json"`) |
| 502 | `NATIVE_BACKUP_FAILED` | JSON backup was stored but the native backup failed (`details.failed_artifact = "aws_native"`, `details.backup_id` = the stored JSON backup) |

---

### GET /admin/backups

List JSON backups, newest first. Files in the bucket that are not valid backup ids are ignored.

**Path Parameters**: none

**Request Body**: none

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "backups": [
      {
        "backup_id": "safety-pre-restore_2026-11-02T09-00-00Z_before-restore-of_manual_2026-11-01T14-30-00Z.json",
        "category": "safety-pre-restore",
        "created_at": "2026-11-02T09:00:00Z",
        "item_count": 1250,
        "size_bytes": 834512,
        "created_by": "admin@example.com",
        "source_backup_id": "manual_2026-11-01T14-30-00Z.json",
        "source_ref": "manual_2026-11-01T14-30-00Z"
      },
      {
        "backup_id": "manual_2026-11-01T14-30-00Z.json",
        "category": "manual",
        "created_at": "2026-11-01T14:30:00Z",
        "item_count": 1250,
        "size_bytes": 834512,
        "created_by": "admin@example.com",
        "source_backup_id": null,
        "source_ref": null
      }
    ]
  },
  "timestamp": "2026-11-02T10:00:00Z"
}
```

`category` is `manual`, `safety-pre-restore` or `safety-pre-reset` (see [Admin Database Reset Endpoints](#admin-database-reset-endpoints)). `source_ref` is parsed from the id (`safety-pre-restore` backups only); `source_backup_id` is the full source id from the S3 metadata (can be `null` if the metadata is missing). `item_count` and `created_by` can be `null` if the metadata is missing.

**Errors**:

| HTTP | Code | When |
|------|------|------|
| 401 | `UNAUTHORIZED` | No valid token |
| 403 | `FORBIDDEN` | User is not in the `admins` group |
| 500 | `LIST_FAILED` | S3 listing failed |

---

### GET /admin/backups/{backup_id}/download

Return the full content of a backup so the client can save it as a file.

**Path Parameters**:
- `backup_id`: String - Backup id (e.g. `manual_2026-11-01T14-30-00Z.json`)

**Request Body**: none

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "backup_id": "manual_2026-11-01T14-30-00Z.json",
    "filename": "manual_2026-11-01T14-30-00Z.json",
    "content": {
      "format_version": 1,
      "metadata": {
        "backup_id": "manual_2026-11-01T14-30-00Z.json",
        "category": "manual",
        "created_at": "2026-11-01T14:30:00Z",
        "created_by": "admin@example.com",
        "item_count": 1,
        "table_name": "impressionnistes-registration-prod",
        "environment": "prod"
      },
      "items": [
        {
          "PK": {"S": "CONFIG"},
          "SK": {"S": "SYSTEM"},
          "registration_open": {"BOOL": true}
        }
      ]
    }
  },
  "timestamp": "2026-11-02T10:00:00Z"
}
```

The backup file is validated before being returned (`format_version`, unique `PK`/`SK`, `item_count`). Binary values (`B`, `BS`) are base64 encoded. Backups contain all application data, including personal data: store downloaded files securely.

**Errors**:

| HTTP | Code | When |
|------|------|------|
| 400 | `INVALID_BACKUP_ID` | `backup_id` does not match the backup naming format |
| 401 | `UNAUTHORIZED` | No valid token |
| 403 | `FORBIDDEN` | User is not in the `admins` group |
| 404 | `BACKUP_NOT_FOUND` | No backup with this id |
| 422 | `BACKUP_INVALID` | The stored file is not valid JSON or fails validation |

---

### DELETE /admin/backups/{backup_id}

Delete a JSON backup. The AWS native backup is kept.

**Path Parameters**:
- `backup_id`: String - Backup id

**Request Body**: none

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "backup_id": "manual_2026-11-01T14-30-00Z.json",
    "deleted": true
  },
  "timestamp": "2026-11-02T10:00:00Z"
}
```

**Errors**:

| HTTP | Code | When |
|------|------|------|
| 400 | `INVALID_BACKUP_ID` | `backup_id` does not match the backup naming format |
| 401 | `UNAUTHORIZED` | No valid token |
| 403 | `FORBIDDEN` | User is not in the `admins` group |
| 404 | `BACKUP_NOT_FOUND` | No backup with this id |

---

### POST /admin/backups/{backup_id}/restore

Restore the database from a backup. **This is a full replacement**: every item of the table is deleted and replaced by the content of the backup.

**Path Parameters**:
- `backup_id`: String - Backup to restore (manual or safety backup)

**Request Body**:
```json
{
  "confirmation_phrase": "RESTAURER LA BASE"
}
```

The phrase must match exactly (case and spaces). A missing or different phrase is rejected before anything is read or changed.

**Behavior** (in order):
1. Validate the id and the confirmation phrase.
2. Load and validate the source backup.
3. Create a safety backup (JSON + AWS native) of the current table. If this fails, the restore is aborted and the table is not modified.
4. Purge the table, except `AUDIT#DATABASE_BACKUP` records (backup audit history), which are always preserved. If the source contains audit records with the same key, the source version wins.
5. Write the source items.
6. Verify the item count: source items plus preserved audit records not present in the source.
7. Write a `restore_backup` audit record.

To undo a restore, restore the safety backup it returned.

**Synchronous execution**: the restore runs inside the request. The Lambda timeout is 120 s but API Gateway cuts the response at 29 s. A **504** (or a network error) means the **outcome is unknown**: the restore may still be running or have completed. Do not retry blindly; check the backup list and the data first. Re-running the same restore is safe (full replacement is idempotent).

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "source_backup_id": "manual_2026-11-01T14-30-00Z.json",
    "purged_count": 1240,
    "preserved_audit_count": 10,
    "restored_count": 1250,
    "safety_backup": {
      "backup_id": "safety-pre-restore_2026-11-02T09-00-00Z_before-restore-of_manual_2026-11-01T14-30-00Z.json",
      "native_backup": {
        "name": "impressionnistes-registration-prod-safety-pre-restore_2026-11-02T09-00-00Z",
        "arn": "arn:aws:dynamodb:eu-west-3:123456789012:table/impressionnistes-registration-prod/backup/01234567890123-abcdef02"
      }
    },
    "steps": [
      {"name": "safety_backup", "status": "ok", "count": 1250},
      {"name": "purge", "status": "ok", "count": 1240},
      {"name": "write", "status": "ok", "count": 1250},
      {"name": "verify", "status": "ok", "count": 1255}
    ],
    "audit_written": true,
    "duration_ms": 8400
  },
  "timestamp": "2026-11-02T09:00:09Z"
}
```

`purged_count` excludes the preserved audit records (`preserved_audit_count`). `audit_written: false` means the final audit record could not be written; the restore itself succeeded. Step `status` is `ok`, `failed` or `skipped`.

**Errors**:

| HTTP | Code | When | Table modified? |
|------|------|------|-----------------|
| 400 | `INVALID_BACKUP_ID` | `backup_id` does not match the backup naming format | No |
| 400 | `INVALID_CONFIRMATION` | Phrase missing or different from `RESTAURER LA BASE` | No |
| 401 | `UNAUTHORIZED` | No valid token | No |
| 403 | `FORBIDDEN` | User is not in the `admins` group | No |
| 404 | `BACKUP_NOT_FOUND` | No backup with this id | No |
| 422 | `BACKUP_INVALID` | Source backup fails validation | No |
| 500 | `SAFETY_BACKUP_FAILED` | Safety backup could not be created (`details.failed_artifact`, `details.source_backup_id`) | No |
| 500 | `RESTORE_PARTIAL` | Failure during purge, write or verify | **Yes (partial)** |
| 504 | (API Gateway timeout) | Response not returned within 29 s | Unknown |

**RESTORE_PARTIAL (500)**: the restore failed after the purge started, so the table may be incomplete. Restore the safety backup (or re-run the same restore) to recover.
```json
{
  "success": false,
  "error": {
    "code": "RESTORE_PARTIAL",
    "message": "The restore failed after the purge started; restore the safety backup",
    "details": {
      "safety_backup_id": "safety-pre-restore_2026-11-02T09-00-00Z_before-restore-of_manual_2026-11-01T14-30-00Z.json",
      "safety_native_backup": {
        "name": "impressionnistes-registration-prod-safety-pre-restore_2026-11-02T09-00-00Z",
        "arn": "arn:aws:dynamodb:eu-west-3:123456789012:table/impressionnistes-registration-prod/backup/01234567890123-abcdef02"
      },
      "source_backup_id": "manual_2026-11-01T14-30-00Z.json",
      "stage": "write",
      "purged_count": 1240,
      "preserved_audit_count": 10,
      "written_count": 600,
      "steps": [
        {"name": "safety_backup", "status": "ok", "count": 1250},
        {"name": "purge", "status": "ok", "count": 1240},
        {"name": "write", "status": "failed", "count": null},
        {"name": "verify", "status": "skipped", "count": null}
      ]
    }
  },
  "timestamp": "2026-11-02T09:00:09Z"
}
```

`stage` is `purge`, `write` or `verify`. Steps not reached are `skipped`.

---

## Admin Database Reset Endpoints

Selective purge of operational data. Both endpoints require a Cognito JWT token for a user in the `admins` group. They are served by the same `manage_backups` Lambda as the backup endpoints (`functions/admin/manage_backups.py`, logic in `functions/shared/reset_service.py`).

**Authentication**: Required (Cognito JWT token with admin role) for all endpoints below.

**Headers**:
```
Authorization: Bearer <cognito-jwt-token>
```

**Purge sets** (ids used in `counts`, `sets` and `deleted`):

| Id | Content |
|----|---------|
| `boats` | Crew registrations (`TEAM#*` / `BOAT#*`) |
| `payments` | Payments (`TEAM#*` / `PAYMENT#*`) |
| `crew` | Crew members (`TEAM#*` / `CREW#*`) |
| `managers` | Team manager profiles and consents (`USER#*` / `PROFILE`, `CONSENT#*`) |
| `temp_access` | Temporary access grants (`TEMP_ACCESS` / `USER#*`) |
| `audit_logs` | Permission and temporary-access audit logs (five `AUDIT#` partitions) |

**Dependency rules**: a selection must be closed under these rules. The API never adds sets for you; a selection that is not closed is rejected.
- `boats` requires `payments`
- `crew` requires `boats` and `payments`
- `managers` requires `boats`, `payments`, `crew` and `temp_access`

**Protected data** is never purged: `CONFIG`, `RACE`, `CLUB` and the `AUDIT#DATABASE_BACKUP` records (backup audit history), as well as any key that matches no purge set.

---

### GET /admin/reset

Return the number of items in each purge set and the environment flags used by the reset page.

**Path Parameters**: none

**Request Body**: none

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "environment": "prod",
    "backup_required": true,
    "counts": {
      "boats": 120,
      "payments": 95,
      "crew": 640,
      "managers": 70,
      "temp_access": 3,
      "audit_logs": 410
    },
    "cognito_accounts_max": 35
  },
  "timestamp": "2026-11-02T10:00:00Z"
}
```

`environment` comes from the Lambda configuration. `backup_required` is `true` only in `prod`. `cognito_accounts_max` is the number of `USER#<sub>` / `PROFILE` items, which is the maximum number of Cognito accounts a purge of `managers` can delete.

**Errors**:

| HTTP | Code | When |
|------|------|------|
| 401 | `UNAUTHORIZED` | No valid token |
| 403 | `FORBIDDEN` | User is not in the `admins` group |
| 500 | `INTERNAL_ERROR` | Table scan failed |

---

### POST /admin/reset

Delete the selected purge sets. **This is irreversible except through the pre-reset backup.**

**Path Parameters**: none

**Request Body**:
```json
{
  "sets": ["boats", "payments"],
  "delete_cognito": false,
  "backup_before": true,
  "confirmation_phrase": "PURGER LA BASE"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sets` | Array of String | Yes | Non-empty list of purge set ids, closed under the dependency rules |
| `delete_cognito` | Boolean | No (default `false`) | Also delete the Cognito accounts of the purged team managers. Only allowed when `managers` is in `sets` |
| `backup_before` | Boolean | No (default `true`) | Take a `safety-pre-reset` backup (JSON + AWS native) before deleting. Must not be `false` in `prod` |
| `confirmation_phrase` | String | Yes | Must be exactly `PURGER LA BASE` (case and spaces) |

The environment is read from the Lambda configuration; a value sent in the request is ignored.

**Behavior** (in order):
1. Validate the request: confirmation phrase, selection, Cognito flag, backup rule. Nothing is read or changed if it is rejected.
2. Create the pre-reset backup (always in `prod`, otherwise when `backup_before` is `true`). If this fails, the purge is aborted and nothing is deleted.
3. Delete the selected sets, dependents first: `payments`, `boats`, `crew`, `temp_access`, `managers`, `audit_logs`. If a deletion fails, the purge stops and the Cognito step is not run.
4. If `delete_cognito` is `true`, delete the Cognito accounts of the purged managers. Accounts in the `admins` group are always skipped. If the group check fails for an account, that account is skipped and reported in `failed`.
5. Write a `reset_database` audit record (`AUDIT#DATABASE_BACKUP` partition) with the outcome, sets, counts, Cognito counts, backup id and admin identity.

To undo a purge, restore the pre-reset backup with `POST /admin/backups/{backup_id}/restore`.

**Synchronous execution**: the purge runs inside the request. A **504** (or a network error) means the **outcome is unknown**: check the counts (`GET /admin/reset`) and the backup list before retrying. Re-running the same purge is safe.

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "sets": ["payments", "boats"],
    "deleted": {
      "payments": 95,
      "boats": 120
    },
    "total_deleted": 215,
    "cognito": {
      "requested": false,
      "deleted": 0,
      "skipped_admins": 0,
      "not_found": 0,
      "failed": []
    },
    "pre_reset_backup": {
      "backup_id": "safety-pre-reset_2026-11-02T09-00-00Z.json",
      "native_backup": {
        "name": "impressionnistes-registration-prod-safety-pre-reset_2026-11-02T09-00-00Z",
        "arn": "arn:aws:dynamodb:eu-west-3:123456789012:table/impressionnistes-registration-prod/backup/01234567890123-abcdef03"
      }
    },
    "audit_written": true,
    "duration_ms": 3200
  },
  "timestamp": "2026-11-02T09:00:04Z"
}
```

`sets` lists the purged sets in deletion order. `deleted` holds the number of items deleted per set. `pre_reset_backup` is `null` when no backup was taken (non-prod with `backup_before: false`). When `delete_cognito` is `true`, `cognito` reports:
- `deleted`: accounts deleted
- `skipped_admins`: accounts kept because they belong to the `admins` group
- `not_found`: profiles without a Cognito account
- `failed`: list of `{"sub": "...", "code": "..."}` for accounts that could not be processed (the other accounts are still processed)

`audit_written: false` means the audit record could not be written; the purge itself succeeded.

**Errors**:

| HTTP | Code | When | Database modified? |
|------|------|------|--------------------|
| 400 | `INVALID_CONFIRMATION` | Body missing or not valid JSON, or phrase missing or different from `PURGER LA BASE` | No |
| 400 | `INVALID_SELECTION` | `sets` empty or not a list, unknown id (`details.unknown`), selection not closed under the dependency rules (`details.missing`), `delete_cognito` without `managers` (`details.missing = ["managers"]`), or a non-boolean flag | No |
| 400 | `BACKUP_REQUIRED` | `backup_before` is `false` in `prod` | No |
| 401 | `UNAUTHORIZED` | No valid token | No |
| 403 | `FORBIDDEN` | User is not in the `admins` group | No |
| 500 | `PRE_RESET_BACKUP_FAILED` | The pre-reset backup could not be created (`details.failed_artifact` = `json` or `aws_native`, `details.database_modified` = `false`) | No |
| 500 | `RESET_PARTIAL` | A deletion failed after the purge started | **Yes (partial)** |
| 500 | `INTERNAL_ERROR` | Unexpected failure before any deletion (`details.database_modified` = `false`) | No |
| 504 | (API Gateway timeout) | Response not returned within 29 s | Unknown |

**INVALID_SELECTION (400)** example, `boats` selected without `payments`:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_SELECTION",
    "message": "The selection is not closed under the dependency rules",
    "details": {
      "missing": ["payments"]
    }
  },
  "timestamp": "2026-11-02T09:00:01Z"
}
```

**PRE_RESET_BACKUP_FAILED (500)** example:
```json
{
  "success": false,
  "error": {
    "code": "PRE_RESET_BACKUP_FAILED",
    "message": "The pre-reset backup failed: nothing was deleted",
    "details": {
      "failed_artifact": "aws_native",
      "database_modified": false
    }
  },
  "timestamp": "2026-11-02T09:00:03Z"
}
```

**RESET_PARTIAL (500)**: the purge failed after it started, so some sets may be partly or fully deleted. `stage` is the set being deleted when the failure occurred, `deleted` the items deleted so far per set, and `cognito` is always `"not_attempted"`. A `reset_database` audit record with outcome `partial` is written. Re-run the same purge to finish it, or restore `pre_reset_backup_id` (`null` if no backup was taken) to recover.
```json
{
  "success": false,
  "error": {
    "code": "RESET_PARTIAL",
    "message": "The purge failed before completion",
    "details": {
      "stage": "boats",
      "deleted": {
        "payments": 95,
        "boats": 40
      },
      "pre_reset_backup_id": "safety-pre-reset_2026-11-02T09-00-00Z.json",
      "cognito": "not_attempted"
    }
  },
  "timestamp": "2026-11-02T09:00:04Z"
}
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
