# Design Document

## Overview

This design document specifies the technical architecture for the payment history and balance tracking feature. The system provides comprehensive payment visibility for team managers and administrators, including payment history, outstanding balance calculations, analytics, PDF invoice generation, and integration with the event program Excel export.

The design follows the existing architecture patterns in the Impressionnistes Registration System, using AWS Lambda for backend logic, DynamoDB for data storage, and Vue.js for the frontend interface.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Vue.js)                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ Payment History  │  │ Payment Summary  │  │ Admin Payment │ │
│  │     Page         │  │     Widget       │  │   Analytics   │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS/REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (REST)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Lambda Functions (Python)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │list_payments │  │get_payment_  │  │get_payment_invoice │   │
│  │              │  │   summary    │  │                    │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │list_all_     │  │get_payment_  │                            │
│  │  payments    │  │  analytics   │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DynamoDB (Single Table)                     │
│  PK: TEAM#{id}  SK: PAYMENT#{id}  (Payment Records)            │
│  PK: TEAM#{id}  SK: BOAT#{id}     (Boat Registrations)         │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Payment Creation** (existing):
   - User initiates payment via Stripe
   - Webhook creates payment record in DynamoDB
   - Boats marked as 'paid' with payment_id reference

2. **Payment History Query**:
   - Frontend requests payment list
   - Lambda queries DynamoDB by PK (TEAM#{id}) with SK prefix (PAYMENT#)
   - Returns sorted list of payments

3. **Outstanding Balance Calculation**:
   - Lambda queries boats with status='complete' (unpaid)
   - Calculates estimated amount for each boat
   - Returns total outstanding balance

4. **PDF Invoice Generation**:
   - Lambda retrieves payment record
   - Generates PDF using ReportLab library
   - Returns PDF as base64-encoded response

5. **Event Program Export Enhancement**:
   - Export function queries payment records for each team manager
   - Calculates total paid and outstanding balance
   - Adds columns to Excel crew member list sheet

## Components and Interfaces


### Backend Components

#### 1. List Payments Lambda (`functions/payment/list_payments.py`)

**Purpose:** Retrieve paginated list of payments for a team manager

**Input:**
```python
{
    "pathParameters": {},
    "queryStringParameters": {
        "start_date": "2026-01-01T00:00:00Z",  # Optional
        "end_date": "2026-01-31T23:59:59Z",    # Optional
        "limit": 50,                            # Optional, default 50
        "sort": "desc"                          # Optional, 'asc' or 'desc'
    },
    "requestContext": {
        "authorizer": {
            "claims": {
                "sub": "user-id"
            }
        }
    }
}
```

**Output:**
```python
{
    "statusCode": 200,
    "body": {
        "payments": [
            {
                "payment_id": "uuid",
                "stripe_payment_intent_id": "pi_xxx",
                "amount": 100.00,
                "currency": "EUR",
                "paid_at": "2026-01-15T10:30:00Z",
                "boat_count": 2,
                "boat_registration_ids": ["boat-1", "boat-2"],
                "stripe_receipt_url": "https://...",
                "status": "succeeded"
            }
        ],
        "summary": {
            "total_payments": 5,
            "total_amount": 500.00,
            "currency": "EUR",
            "date_range": {
                "first_payment": "2026-01-01T...",
                "last_payment": "2026-01-15T..."
            }
        }
    }
}
```

**Logic:**
1. Extract team_manager_id from JWT token
2. Query DynamoDB: `PK=TEAM#{team_manager_id}`, `SK begins_with PAYMENT#`
3. Apply date filters if provided
4. Sort by paid_at (descending by default)
5. Calculate summary statistics
6. Return paginated results

**Access Control:** `@require_team_manager_or_admin_override`, `@require_permission('view_payment_history')`


#### 2. Get Payment Summary Lambda (`functions/payment/get_payment_summary.py`)

**Purpose:** Calculate total paid and outstanding balance for a team manager

**Input:**
```python
{
    "requestContext": {
        "authorizer": {
            "claims": {
                "sub": "user-id"
            }
        }
    }
}
```

**Output:**
```python
{
    "statusCode": 200,
    "body": {
        "paid": {
            "total_amount": 500.00,
            "currency": "EUR",
            "payment_count": 5,
            "boat_count": 10
        },
        "outstanding": {
            "total_amount": 100.00,
            "currency": "EUR",
            "boat_count": 2,
            "boats": [
                {
                    "boat_registration_id": "boat-1",
                    "event_type": "Course",
                    "boat_type": "4+",
                    "estimated_amount": 50.00,
                    "registration_status": "complete"
                }
            ]
        },
        "total_registered_boats": 12
    }
}
```

**Logic:**
1. Extract team_manager_id from JWT token
2. Query all payments: `PK=TEAM#{team_manager_id}`, `SK begins_with PAYMENT#`
3. Sum total paid amount
4. Query unpaid boats: `PK=TEAM#{team_manager_id}`, `SK begins_with BOAT#`, filter `registration_status='complete'`
5. Calculate estimated amount for each unpaid boat using pricing configuration
6. Return summary with paid and outstanding totals

**Access Control:** `@require_team_manager_or_admin_override`, `@require_permission('view_payment_history')`


#### 3. Get Payment Invoice Lambda (`functions/payment/get_payment_invoice.py`)

**Purpose:** Generate PDF invoice for a payment

**Input:**
```python
{
    "pathParameters": {
        "payment_id": "uuid"
    },
    "requestContext": {
        "authorizer": {
            "claims": {
                "sub": "user-id"
            }
        }
    }
}
```

**Output:**
```python
{
    "statusCode": 200,
    "headers": {
        "Content-Type": "application/pdf",
        "Content-Disposition": "attachment; filename=invoice-payment-123-2026-01-15.pdf"
    },
    "body": "<base64-encoded-pdf>",
    "isBase64Encoded": true
}
```

**Logic:**
1. Extract team_manager_id and payment_id
2. Retrieve payment record from DynamoDB
3. Retrieve boat details for boats in payment
4. Retrieve team manager profile
5. Generate PDF using ReportLab:
   - Header: Event name, logo
   - Payment details: ID, date, amount
   - Team manager info: Name, club, email
   - Boat list: Event type, boat type, amount
   - Footer: Stripe receipt link
6. Return PDF as base64-encoded response

**Dependencies:** ReportLab library (add to Lambda layer)

**Access Control:** `@require_team_manager_or_admin_override`, `@require_permission('download_payment_invoice')`


#### 4. List All Payments Lambda (`functions/admin/list_all_payments.py`)

**Purpose:** Admin endpoint to list all payments across all team managers

**Input:**
```python
{
    "queryStringParameters": {
        "start_date": "2026-01-01T00:00:00Z",  # Optional
        "end_date": "2026-01-31T23:59:59Z",    # Optional
        "team_manager_id": "user-id",          # Optional filter
        "limit": 100,                           # Optional
        "sort_by": "date",                      # Optional: date, amount, team_manager
        "sort_order": "desc"                    # Optional: asc, desc
    }
}
```

**Output:**
```python
{
    "statusCode": 200,
    "body": {
        "payments": [
            {
                "payment_id": "uuid",
                "team_manager_id": "user-id",
                "team_manager_name": "Club Name",
                "team_manager_email": "email@example.com",
                "club_affiliation": "Club Name",
                "amount": 100.00,
                "currency": "EUR",
                "paid_at": "2026-01-15T10:30:00Z",
                "boat_count": 2,
                "stripe_receipt_url": "https://..."
            }
        ],
        "total_count": 50,
        "total_amount": 5000.00
    }
}
```

**Logic:**
1. Scan all PAYMENT# records across all teams
2. Cache team manager lookups for performance
3. Apply filters (date range, team manager)
4. Sort by specified field
5. Return paginated results with totals

**Access Control:** `@require_admin`, `@require_permission('view_payment_analytics')`


#### 5. Get Payment Analytics Lambda (`functions/admin/get_payment_analytics.py`)

**Purpose:** Admin endpoint for payment analytics and trends

**Input:**
```python
{
    "queryStringParameters": {
        "start_date": "2026-01-01T00:00:00Z",  # Optional
        "end_date": "2026-01-31T23:59:59Z",    # Optional
        "group_by": "day"                       # Optional: day, week, month
    }
}
```

**Output:**
```python
{
    "statusCode": 200,
    "body": {
        "total_revenue": 5000.00,
        "total_payments": 50,
        "total_boats_paid": 100,
        "total_team_managers": 20,
        "outstanding_balance": 500.00,
        "outstanding_boats": 10,
        "payment_timeline": [
            {
                "date": "2026-01-15",
                "amount": 500.00,
                "payment_count": 5,
                "boat_count": 10
            }
        ],
        "top_team_managers": [
            {
                "team_manager_id": "user-id",
                "name": "Club Name",
                "total_paid": 500.00,
                "payment_count": 5,
                "boat_count": 10
            }
        ]
    }
}
```

**Logic:**
1. Scan all PAYMENT# records
2. Calculate total revenue and payment statistics
3. Group payments by time period (day/week/month)
4. Calculate system-wide outstanding balance
5. Rank team managers by total paid
6. Return comprehensive analytics

**Access Control:** `@require_admin`, `@require_permission('view_payment_analytics')`


#### 6. Export Enhancement (`functions/admin/export_races_json.py`)

**Purpose:** Add payment balance to event program export

**Changes:**
1. For each team manager in export, calculate:
   - Total paid amount (sum of all successful payments)
   - Outstanding balance (sum of unpaid boats)
   - Payment status: "Paid in Full", "Partial Payment", or "No Payment"

2. Add to team_managers array in response:
```python
{
    "user_id": "user-id",
    "club_affiliation": "Club Name",
    "email": "email@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "total_paid": 500.00,              # NEW
    "outstanding_balance": 100.00,     # NEW
    "payment_status": "Partial Payment" # NEW
}
```

3. Frontend formatter (`eventProgramFormatter.js`) will add columns to crew member list:
   - "Total Paid (EUR)"
   - "Outstanding Balance (EUR)"
   - "Payment Status"

**Logic:**
1. After loading team managers, query payments for each
2. Calculate totals using same logic as get_payment_summary
3. Add payment fields to team manager objects
4. Frontend reads these fields and adds to Excel export


### Frontend Components

#### 1. Payment History Page (`frontend/src/views/PaymentHistory.vue`)

**Purpose:** Display paginated list of payments for team manager

**Features:**
- Sortable table with columns: Date, Amount, Boats, Receipt
- Date range filter
- Mobile-responsive (card view on mobile)
- Loading states and error handling
- Empty state messaging

**Components Used:**
- `SortableTable` for desktop view
- `DataCard` for mobile view
- `BaseButton` for actions
- `MessageAlert` for errors

**API Calls:**
- `GET /payments` - Fetch payment list
- `GET /payments/summary` - Fetch summary for header


#### 2. Payment Summary Widget (`frontend/src/components/PaymentSummaryWidget.vue`)

**Purpose:** Display payment summary on dashboard

**Features:**
- Total paid amount
- Outstanding balance (highlighted if > 0)
- Last payment date
- Link to full payment history

**Components Used:**
- `DataCard` for container
- `BaseButton` for navigation

**API Calls:**
- `GET /payments/summary` - Fetch summary data

#### 3. Admin Payment Analytics Page (`frontend/src/views/admin/AdminPaymentAnalytics.vue`)

**Purpose:** Display payment analytics for administrators

**Features:**
- Summary cards: Total revenue, payment count, outstanding balance
- Payment timeline chart (Chart.js)
- Top payers table (sortable)
- Date range filters
- CSV export functionality

**Components Used:**
- `DataCard` for summary statistics
- `SortableTable` for top payers
- `BaseButton` for actions
- Chart.js for timeline visualization

**API Calls:**
- `GET /admin/payments/analytics` - Fetch analytics data
- `GET /admin/payments` - Fetch detailed payment list for export


## Data Models

### Payment Record (Existing)

```python
{
    "PK": "TEAM#{team_manager_id}",
    "SK": "PAYMENT#{payment_id}",
    "payment_id": "uuid",
    "stripe_payment_intent_id": "pi_xxx",
    "team_manager_id": "user-id",
    "boat_registration_ids": ["boat-1", "boat-2"],
    "amount": Decimal("100.00"),
    "currency": "EUR",
    "status": "succeeded",
    "paid_at": "2026-01-15T10:30:00Z",
    "stripe_receipt_url": "https://...",
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-01-15T10:30:00Z"
}
```

### Boat Registration (Existing - relevant fields)

```python
{
    "PK": "TEAM#{team_manager_id}",
    "SK": "BOAT#{boat_registration_id}",
    "boat_registration_id": "uuid",
    "registration_status": "complete",  # or "paid"
    "payment_id": "uuid",               # Set when paid
    "paid_at": "2026-01-15T10:30:00Z",  # Set when paid
    "pricing": {                         # Current pricing
        "total": Decimal("50.00"),
        "base_price": Decimal("40.00"),
        "additional_fees": Decimal("10.00")
    },
    "locked_pricing": {                  # Locked when paid
        "total": Decimal("50.00"),
        "base_price": Decimal("40.00"),
        "additional_fees": Decimal("10.00")
    }
}
```

### Payment Summary (Calculated)

```python
{
    "paid": {
        "total_amount": Decimal("500.00"),
        "currency": "EUR",
        "payment_count": 5,
        "boat_count": 10
    },
    "outstanding": {
        "total_amount": Decimal("100.00"),
        "currency": "EUR",
        "boat_count": 2,
        "boats": [...]
    }
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Payment List Sorting

*For any* set of payment records, when querying payment history, the returned list should be sorted by payment date in descending order (newest first).

**Validates: Requirements 1.1**

### Property 2: Date Range Filtering

*For any* set of payment records and any valid date range, when filtering payments by that date range, all returned payments should have paid_at timestamps within the specified range (inclusive).

**Validates: Requirements 1.3, 3.3**

### Property 3: Payment Record Completeness

*For any* payment record returned by the system, it should contain all required fields: payment_id, stripe_payment_intent_id, amount, currency, paid_at, boat_registration_ids, stripe_receipt_url, and status.

**Validates: Requirements 1.2, 3.2, 7.1, 7.2, 7.3**

### Property 4: Total Paid Calculation

*For any* set of successful payment records, the calculated total paid amount should equal the sum of all payment amounts.

**Validates: Requirements 2.1, 4.1, 5.2**

### Property 5: Outstanding Balance Calculation

*For any* set of boat registrations with status='complete', the calculated outstanding balance should equal the sum of estimated amounts for all unpaid boats.

**Validates: Requirements 2.2, 4.3, 5.3**

### Property 6: Unpaid Boat Fields

*For any* unpaid boat in the outstanding balance list, it should contain event_type, boat_type, and estimated_amount fields.

**Validates: Requirements 2.3**

### Property 7: Pricing Fallback

*For any* boat registration without pricing information, the system should calculate the estimated amount using the current pricing configuration, and the result should be greater than zero.

**Validates: Requirements 2.4**


### Property 8: Admin Query Completeness

*For any* set of team managers with payment records, when an administrator queries all payments, the result should include payments from all team managers.

**Validates: Requirements 3.1**

### Property 9: Team Manager Filtering

*For any* set of payment records across multiple team managers, when filtering by a specific team manager ID, all returned payments should belong to that team manager only.

**Validates: Requirements 3.4**

### Property 10: Multi-Field Sorting

*For any* set of payment records, when sorting by a specified field (date, amount, team_manager_name, or club), the returned list should be correctly ordered by that field in the specified direction (ascending or descending).

**Validates: Requirements 3.5**

### Property 11: Analytics Counting

*For any* set of payment records, the analytics should correctly count: total payments, total boats paid (sum of boat_count in each payment), and number of unique team managers who have paid.

**Validates: Requirements 4.2**

### Property 12: Time Period Grouping

*For any* set of payment records and any grouping period (day, week, month), when grouping payments by time period, each payment should appear in exactly one group, and the sum of amounts across all groups should equal the total revenue.

**Validates: Requirements 4.4**

### Property 13: Top Payers Ranking

*For any* set of team managers with payment records, when ranking by total amount paid, the list should be sorted in descending order by total paid amount, and each team manager's total should equal the sum of their individual payments.

**Validates: Requirements 4.5**

### Property 14: Currency Formatting

*For any* decimal amount, when formatting for Excel export, the result should have exactly two decimal places and be a valid currency format.

**Validates: Requirements 5.6**

### Property 15: Access Control Isolation

*For any* team manager, when querying their payment history or summary, the result should contain only their own payment records and should not include payments from other team managers.

**Validates: Requirements 6.1, 6.2**


### Property 16: Admin Access Completeness

*For any* administrator request for payment data, the result should include data from all team managers without filtering by team manager ID (unless explicitly requested).

**Validates: Requirements 6.3**

### Property 17: Impersonation Context

*For any* administrator impersonating a team manager, when querying payment data, the result should match exactly what that team manager would see if they queried directly.

**Validates: Requirements 6.4**

### Property 18: Permission Enforcement

*For any* user without the required permission, when attempting to access payment data, the system should return an authorization error (403 or 401 status code).

**Validates: Requirements 6.5**

### Property 19: Pricing Lock on Payment

*For any* boat registration, when it is marked as paid, the locked_pricing field should be set and should equal the current pricing field at the time of payment.

**Validates: Requirements 7.4**

### Property 20: Pagination Consistency

*For any* paginated query with page size N, the union of all pages should equal the complete result set, and no payment record should appear in multiple pages.

**Validates: Requirements 8.3, 8.4**

### Property 21: PDF Invoice Completeness

*For any* payment record, when generating a PDF invoice, the PDF content should include: payment_id, paid_at, amount, currency, team_manager_name, club_affiliation, email, event name, and the list of boats paid.

**Validates: Requirements 12.2, 12.3, 12.4**

### Property 22: PDF Filename Format

*For any* payment record, when generating a PDF invoice, the filename should match the pattern "invoice-payment-{payment_id}-{date}.pdf" where date is in YYYY-MM-DD format.

**Validates: Requirements 12.5**

### Property 23: PDF Receipt Link Inclusion

*For any* payment record with a non-empty stripe_receipt_url, when generating a PDF invoice, the PDF should contain the Stripe receipt URL.

**Validates: Requirements 12.6**


## Error Handling

### Backend Error Handling

**Database Errors:**
- Catch `ClientError` from boto3
- Return 500 Internal Server Error with message: "Failed to retrieve payment data"
- Log full error details for debugging

**Validation Errors:**
- Invalid date format: Return 400 Bad Request with message: "Invalid date format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)"
- Invalid date range (end before start): Return 400 Bad Request with message: "End date must be after start date"
- Invalid pagination parameters: Return 400 Bad Request with message: "Invalid pagination parameters"
- Invalid sort field: Return 400 Bad Request with message: "Invalid sort field. Supported: date, amount, team_manager_name, club"

**Authorization Errors:**
- Missing authentication: Return 401 Unauthorized
- Insufficient permissions: Return 403 Forbidden with message: "You do not have permission to access this resource"
- Payment not found or not owned: Return 404 Not Found with message: "Payment not found"

**PDF Generation Errors:**
- ReportLab failure: Return 500 Internal Server Error with message: "Failed to generate PDF invoice"
- Missing payment data: Return 404 Not Found with message: "Payment not found"

### Frontend Error Handling

**Network Errors:**
- Display `MessageAlert` with type="error"
- Provide retry button
- Show user-friendly message: "Failed to load payment data. Please try again."

**Empty States:**
- No payments: Display friendly message with icon
- No outstanding balance: Display "All boats paid" message
- No analytics data: Display "No payment data available for selected period"

**Loading States:**
- Show skeleton loaders for tables
- Show spinner for summary cards
- Disable action buttons during loading


## Testing Strategy

### Unit Tests

**Backend Unit Tests:**
- Test payment list query logic with various filters
- Test payment summary calculation with different payment sets
- Test outstanding balance calculation with various boat statuses
- Test date range filtering edge cases
- Test pagination logic
- Test sorting by different fields
- Test access control logic
- Test PDF generation with mock data
- Test currency formatting
- Test error handling for invalid inputs

**Frontend Unit Tests:**
- Test PaymentHistory component rendering
- Test PaymentSummaryWidget data display
- Test AdminPaymentAnalytics component
- Test date filter functionality
- Test sorting interactions
- Test pagination controls
- Test error state rendering
- Test empty state rendering
- Test loading state rendering

### Property-Based Tests

Each correctness property will be implemented as a property-based test using pytest with Hypothesis (Python) or fast-check (JavaScript).

**Test Configuration:**
- Minimum 100 iterations per property test
- Each test tagged with: **Feature: payment-history-balance, Property {number}: {property_text}**

**Property Test Examples:**

```python
# Property 1: Payment List Sorting
@given(st.lists(payment_record()))
def test_payment_list_sorting(payments):
    """
    Feature: payment-history-balance, Property 1: Payment List Sorting
    For any set of payment records, returned list should be sorted by date descending
    """
    result = list_payments(payments)
    assert is_sorted_descending(result, key=lambda p: p['paid_at'])

# Property 4: Total Paid Calculation
@given(st.lists(payment_record()))
def test_total_paid_calculation(payments):
    """
    Feature: payment-history-balance, Property 4: Total Paid Calculation
    For any set of payments, total should equal sum of amounts
    """
    summary = calculate_payment_summary(payments)
    expected_total = sum(p['amount'] for p in payments)
    assert summary['paid']['total_amount'] == expected_total
```

### Integration Tests

**API Integration Tests:**
- Test GET /payments endpoint with authentication
- Test GET /payments/summary endpoint
- Test GET /payments/{id}/invoice endpoint
- Test GET /admin/payments endpoint (admin only)
- Test GET /admin/payments/analytics endpoint (admin only)
- Test access control (team manager can't see others' payments)
- Test admin impersonation
- Test pagination across multiple pages
- Test date range filtering
- Test export enhancement with payment balance

**Database Integration Tests:**
- Test querying payments by partition key
- Test filtering by date range
- Test querying across multiple team managers (admin)
- Test payment record creation (webhook simulation)
- Test boat status update to 'paid'
- Test pricing lock on payment

### End-to-End Tests

- Create payment → View in history → Download invoice
- Multiple payments → View summary → Check outstanding balance
- Admin view all payments → Filter by team manager → Export analytics
- Team manager with no payments → View empty state
- Team manager with outstanding balance → View unpaid boats

