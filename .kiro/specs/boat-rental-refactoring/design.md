# Design Document: Boat Rental Refactoring

## Overview

This design document describes the refactoring of the boat rental system from an inventory-based model to a request-based model. The key change is that team managers will initiate rental requests by specifying their needs (boat type, desired weight, comments), and admins will then assign specific boats and accept the requests.

### Key Design Decisions

1. **Request-First Model**: Team managers create requests first, admins fulfill them later
2. **Status-Driven Workflow**: Clear status transitions (pending → accepted → paid)
3. **Flexible Assignment**: Admins can provide detailed assignment information (boat number, oars, location)
4. **Backward Compatibility**: Migration path from old inventory-based system
5. **Immutable Paid State**: Once paid, rental requests cannot be modified

## Architecture

### System Components

```
┌─────────────────┐
│  Team Manager   │
│   Frontend      │
└────────┬────────┘
         │
         │ Create Request
         │ View My Requests
         │ Cancel Request
         │ Pay for Rental
         │
         v
┌─────────────────────────────────────┐
│         API Gateway                 │
│  /rental/request                    │
│  /rental/my-requests                │
│  /rental/requests-for-payment       │
│  /rental/request/{id}               │
└────────┬────────────────────────────┘
         │
         v
┌─────────────────────────────────────┐
│      Lambda Functions               │
│  - create_rental_request            │
│  - get_my_rental_requests           │
│  - get_rentals_for_payment          │
│  - cancel_rental_request            │
└────────┬────────────────────────────┘
         │
         v
┌─────────────────────────────────────┐
│         DynamoDB                    │
│  RENTAL_REQUEST#{uuid}              │
│    SK: METADATA                     │
└─────────────────────────────────────┘
         ^
         │
┌────────┴────────────────────────────┐
│      Lambda Functions               │
│  - list_rental_requests (admin)     │
│  - accept_rental_request (admin)    │
│  - update_assignment_details (admin)│
│  - reject_rental_request (admin)    │
└────────┬────────────────────────────┘
         │
         │ View All Requests
         │ Accept Request
         │ Update Assignment
         │ Reject Request
         │
         v
┌─────────────────┐
│     Admin       │
│   Frontend      │
└─────────────────┘
```

### Data Flow

1. **Request Creation Flow**:
   - Team manager submits request (boat_type, desired_weight_range, request_comment)
   - System validates input
   - System creates RENTAL_REQUEST record with status "pending"
   - System returns confirmation to team manager

2. **Admin Assignment Flow**:
   - Admin views all pending requests
   - Admin selects a request to fulfill
   - Admin provides assignment_details (boat number, oars, location, etc.)
   - Admin accepts the request
   - System updates status to "accepted" and records accepted_at timestamp
   - Team manager can now see assignment details

3. **Payment Flow**:
   - Team manager views accepted requests
   - System calculates rental price based on boat_type
   - Team manager initiates payment via Stripe
   - On successful payment, system updates status to "paid"
   - System records paid_at timestamp

4. **Cancellation Flow**:
   - Team manager or admin can cancel request
   - System validates status (must be "pending" or "accepted")
   - System updates status to "cancelled"
   - System records cancelled_at timestamp and cancelled_by user_id

## Components and Interfaces

### Backend Lambda Functions

#### 1. create_rental_request.py
**Purpose**: Team manager creates a new rental request

**Input**:
```python
{
    "boat_type": str,  # Required: skiff, 4-, 4+, 4x-, 4x+, 8+, 8x+
    "desired_weight_range": str,  # Required: e.g., "70-90kg"
    "request_comment": str  # Required: max 500 chars
}
```

**Output**:
```python
{
    "rental_request_id": str,
    "boat_type": str,
    "desired_weight_range": str,
    "request_comment": str,
    "status": "pending",
    "requester_id": str,
    "requester_email": str,
    "created_at": str
}
```

**Logic**:
1. Validate authentication (require_team_manager)
2. Validate input fields
3. Generate rental_request_id: RENTAL_REQUEST#{uuid}
4. Create record with status "pending"
5. Record requester_id, requester_email, created_at
6. Save to DynamoDB
7. Return confirmation

#### 2. get_my_rental_requests.py
**Purpose**: Team manager retrieves their own rental requests

**Input**: None (uses authenticated user from token)

**Output**:
```python
{
    "rental_requests": [
        {
            "rental_request_id": str,
            "boat_type": str,
            "desired_weight_range": str,
            "request_comment": str,
            "status": str,
            "assignment_details": str | None,
            "created_at": str,
            "accepted_at": str | None,
            "paid_at": str | None,
            "cancelled_at": str | None
        }
    ],
    "count": int
}
```

**Logic**:
1. Validate authentication (require_team_manager)
2. Query DynamoDB for RENTAL_REQUEST records where requester_id matches
3. Sort by created_at (most recent first)
4. Return list of requests

#### 3. list_rental_requests.py (Admin)
**Purpose**: Admin retrieves all rental requests with optional filtering

**Input** (query parameters):
```python
{
    "status": str | None,  # Optional: pending, accepted, paid, cancelled
    "boat_type": str | None  # Optional: filter by boat type
}
```

**Output**:
```python
{
    "rental_requests": [
        {
            "rental_request_id": str,
            "boat_type": str,
            "desired_weight_range": str,
            "request_comment": str,
            "status": str,
            "requester_id": str,
            "requester_email": str,
            "assignment_details": str | None,
            "created_at": str,
            "accepted_at": str | None,
            "accepted_by": str | None,
            "paid_at": str | None,
            "cancelled_at": str | None,
            "cancelled_by": str | None,
            "rejection_reason": str | None
        }
    ],
    "count": int
}
```

**Logic**:
1. Validate authentication (require_admin)
2. Scan DynamoDB for all RENTAL_REQUEST records
3. Apply filters if provided (status, boat_type)
4. Sort by created_at (most recent first)
5. Return list of requests

#### 4. accept_rental_request.py (Admin)
**Purpose**: Admin accepts a rental request and provides assignment details

**Input**:
```python
{
    "rental_request_id": str,  # Path parameter
    "assignment_details": str  # Required: max 1000 chars
}
```

**Output**:
```python
{
    "rental_request_id": str,
    "status": "accepted",
    "assignment_details": str,
    "accepted_at": str,
    "accepted_by": str
}
```

**Logic**:
1. Validate authentication (require_admin)
2. Validate assignment_details (not empty, max 1000 chars)
3. Get rental request from DynamoDB
4. Validate current status is "pending"
5. Update status to "accepted"
6. Set assignment_details
7. Record accepted_at timestamp
8. Record accepted_by (admin user_id)
9. Save to DynamoDB
10. Return updated request

#### 5. update_assignment_details.py (Admin)
**Purpose**: Admin updates assignment details without changing status

**Input**:
```python
{
    "rental_request_id": str,  # Path parameter
    "assignment_details": str  # Required: max 1000 chars
}
```

**Output**:
```python
{
    "rental_request_id": str,
    "assignment_details": str,
    "updated_at": str
}
```

**Logic**:
1. Validate authentication (require_admin)
2. Validate assignment_details
3. Get rental request from DynamoDB
4. Validate status is "accepted" (cannot update if pending or paid)
5. Update assignment_details
6. Record updated_at timestamp
7. Save to DynamoDB
8. Return updated request

#### 6. cancel_rental_request.py
**Purpose**: Team manager cancels their own rental request

**Input**:
```python
{
    "rental_request_id": str  # Path parameter
}
```

**Output**:
```python
{
    "rental_request_id": str,
    "status": "cancelled",
    "cancelled_at": str,
    "cancelled_by": str
}
```

**Logic**:
1. Validate authentication (require_team_manager)
2. Get rental request from DynamoDB
3. Validate requester_id matches authenticated user
4. Validate status is "pending" or "accepted" (cannot cancel if paid)
5. Update status to "cancelled"
6. Record cancelled_at timestamp
7. Record cancelled_by (team manager user_id)
8. Save to DynamoDB
9. Return updated request

#### 7. reject_rental_request.py (Admin)
**Purpose**: Admin rejects a rental request

**Input**:
```python
{
    "rental_request_id": str,  # Path parameter
    "rejection_reason": str | None  # Optional: reason for rejection
}
```

**Output**:
```python
{
    "rental_request_id": str,
    "status": "cancelled",
    "cancelled_at": str,
    "cancelled_by": str,
    "rejection_reason": str | None
}
```

**Logic**:
1. Validate authentication (require_admin)
2. Get rental request from DynamoDB
3. Validate status is "pending" (cannot reject if accepted or paid)
4. Update status to "cancelled"
5. Record cancelled_at timestamp
6. Record cancelled_by (admin user_id)
7. Set rejection_reason if provided
8. Save to DynamoDB
9. Return updated request

#### 8. get_rentals_for_payment.py
**Purpose**: Team manager retrieves accepted requests ready for payment

**Input**: None (uses authenticated user from token)

**Output**:
```python
{
    "rental_requests": [
        {
            "rental_request_id": str,
            "boat_type": str,
            "desired_weight_range": str,
            "request_comment": str,
            "assignment_details": str,
            "status": "accepted",
            "pricing": {
                "rental_fee": float,
                "total": float,
                "currency": "EUR"
            },
            "accepted_at": str
        }
    ],
    "count": int
}
```

**Logic**:
1. Validate authentication (require_team_manager)
2. Query DynamoDB for RENTAL_REQUEST records where:
   - requester_id matches authenticated user
   - status is "accepted"
3. For each request, calculate rental price based on boat_type
4. Add pricing information to each request
5. Return list of requests ready for payment

### Frontend Components

#### 1. BoatRentalPage.vue (Refactored)
**Purpose**: Team manager interface for creating and managing rental requests

**Key Changes**:
- Remove "Available Boats" section (no longer browsing inventory)
- Add "Create Rental Request" form with:
  - Boat type selector
  - Desired weight range input
  - Request comment textarea
- Update "My Requests" section to show:
  - Request details (boat_type, desired_weight_range, request_comment)
  - Status badge (pending, accepted, paid, cancelled)
  - Assignment details (when accepted)
  - Cancel button (for pending/accepted requests)
  - Pay button (for accepted requests)

#### 2. AdminBoatInventory.vue (Refactored)
**Purpose**: Admin interface for viewing and managing all rental requests

**Note**: This file was refactored from the old inventory-based system to the new request-based system. The route `/admin/boats` and navigation structure were preserved to minimize changes.

**Features**:
- List all rental requests with filters (status, boat_type)
- Show requester information
- For pending requests:
  - "Accept" button that opens modal for assignment details
  - "Reject" button with optional rejection reason
- For accepted requests:
  - "Edit Assignment" button to update assignment details
- Display all request details and timestamps

### Payment Integration

The payment flow remains largely the same, but now operates on rental requests instead of rental boats:

1. Team manager views accepted requests via `/rental/requests-for-payment`
2. System calculates price based on boat_type
3. Team manager proceeds to Stripe checkout
4. On successful payment webhook, system updates rental request status to "paid"

**Changes to confirm_payment_webhook.py**:
- Update to handle RENTAL_REQUEST records instead of RENTAL_BOAT
- Update status from "accepted" to "paid"
- Record paid_at timestamp

## Data Models

### Rental Request (DynamoDB)

```python
{
    "PK": "RENTAL_REQUEST#{uuid}",
    "SK": "METADATA",
    "rental_request_id": "RENTAL_REQUEST#{uuid}",
    
    # Request details (provided by team manager)
    "boat_type": str,  # skiff, 4-, 4+, 4x-, 4x+, 8+, 8x+
    "desired_weight_range": str,  # e.g., "70-90kg"
    "request_comment": str,  # Team manager's notes/requirements
    
    # Status and workflow
    "status": str,  # pending, accepted, paid, cancelled
    
    # Requester information
    "requester_id": str,  # Team manager user_id
    "requester_email": str,  # Team manager email
    
    # Assignment details (provided by admin when accepting)
    "assignment_details": str | None,  # Boat number, oars, location, etc.
    
    # Timestamps
    "created_at": str,  # ISO 8601 timestamp
    "accepted_at": str | None,  # When admin accepted
    "paid_at": str | None,  # When payment completed
    "cancelled_at": str | None,  # When cancelled
    
    # Admin tracking
    "accepted_by": str | None,  # Admin user_id who accepted
    "cancelled_by": str | None,  # User_id who cancelled (team manager or admin)
    "rejection_reason": str | None,  # Optional reason if admin rejected
    
    # Audit fields
    "updated_at": str,  # Last update timestamp
    "updated_by": str | None  # Last user who updated
}
```

### Status Transitions

```
pending ──accept──> accepted ──pay──> paid (final)
   │                    │
   │                    │
   └──cancel/reject──>  │
                        │
                        └──cancel──> cancelled (final)
```

**Valid Transitions**:
- `pending` → `accepted` (admin accepts with assignment details)
- `pending` → `cancelled` (team manager cancels OR admin rejects)
- `accepted` → `paid` (team manager completes payment)
- `accepted` → `cancelled` (team manager cancels)
- `paid` → (no transitions - final state)
- `cancelled` → (no transitions - final state)

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Request Creation Validation
*For any* rental request creation attempt, the system should accept it if and only if all required fields (boat_type, desired_weight_range, request_comment) are present, boat_type is valid, request_comment is non-empty and ≤500 chars, and desired_weight_range is ≤50 chars.

**Validates: Requirements 1.1, 1.5, 1.6, 1.7**

### Property 2: Initial Status is Pending
*For any* newly created rental request, the status should always be "pending".

**Validates: Requirements 1.2**

### Property 3: Requester Information Recorded
*For any* newly created rental request, the requester_id and requester_email fields should be populated with the authenticated user's information.

**Validates: Requirements 1.3**

### Property 4: Creation Timestamp Recorded
*For any* newly created rental request, the created_at field should be present and contain a valid ISO 8601 timestamp.

**Validates: Requirements 1.4**

### Property 5: Team Manager Request Isolation
*For any* team manager querying their rental requests, the returned list should contain only requests where requester_id matches that team manager's user_id.

**Validates: Requirements 2.1**

### Property 6: Request List Sorting
*For any* list of rental requests (team manager or admin view), the requests should be sorted by created_at in descending order (most recent first).

**Validates: Requirements 2.4, 3.5**

### Property 7: Required Fields Present in Response
*For any* rental request in a response, the following fields should always be present: rental_request_id, boat_type, desired_weight_range, request_comment, status, requester_id, requester_email, created_at.

**Validates: Requirements 2.2, 3.2, 3.6**

### Property 8: Conditional Fields Present Based on Status
*For any* rental request with status "accepted", the assignment_details and accepted_at fields should be present; for status "paid", the paid_at field should be present; for status "cancelled", the cancelled_at field should be present.

**Validates: Requirements 2.3, 2.5, 2.6**

### Property 9: Admin Sees All Requests
*For any* admin querying rental requests without filters, the returned list should contain requests from all team managers.

**Validates: Requirements 3.1**

### Property 10: Status Filtering Works Correctly
*For any* admin query with a status filter, all returned requests should have that exact status, and no requests with that status should be excluded.

**Validates: Requirements 3.3**

### Property 11: Boat Type Filtering Works Correctly
*For any* admin query with a boat_type filter, all returned requests should have that exact boat_type, and no requests with that boat_type should be excluded.

**Validates: Requirements 3.4**

### Property 12: Accept Requires Assignment Details
*For any* attempt to accept a rental request, the operation should succeed if and only if assignment_details is provided, is non-empty, and is ≤1000 characters.

**Validates: Requirements 4.1, 4.5**

### Property 13: Accept Transitions Status Correctly
*For any* rental request with status "pending", accepting it should change the status to "accepted", record accepted_at timestamp, and record accepted_by with the admin's user_id.

**Validates: Requirements 4.2, 4.3, 4.4**

### Property 14: Accept Only Works on Pending Requests
*For any* rental request with status other than "pending", attempting to accept it should be rejected.

**Validates: Requirements 4.6**

### Property 15: Assignment Details Update Preserves Status
*For any* rental request with status "accepted", updating assignment_details should preserve the status as "accepted".

**Validates: Requirements 4.7**

### Property 16: Payment Only for Accepted Requests
*For any* payment attempt, the operation should succeed if and only if the rental request has status "accepted".

**Validates: Requirements 5.1, 5.6**

### Property 17: Payment Transitions Status Correctly
*For any* rental request with status "accepted", completing payment should change the status to "paid" and record paid_at timestamp.

**Validates: Requirements 5.2, 5.3**

### Property 18: Rental Price Calculation
*For any* rental request, the calculated price should equal base_seat_price multiplied by the seat multiplier for that boat_type (skiff: 2.5, 4-: 4, 4+: 5, 4x-: 4, 4x+: 5, 8+: 9, 8x+: 9).

**Validates: Requirements 5.4, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8**

### Property 19: Paid Requests are Immutable
*For any* rental request with status "paid", all modification attempts (update, cancel, accept) should be rejected.

**Validates: Requirements 5.5**

### Property 20: Cancellation Only for Pending or Accepted
*For any* team manager cancellation attempt, the operation should succeed if and only if the request has status "pending" or "accepted".

**Validates: Requirements 6.1, 6.4**

### Property 21: Cancellation Transitions Status Correctly
*For any* rental request being cancelled, the status should change to "cancelled", cancelled_at timestamp should be recorded, and cancelled_by should be set to the user_id of the cancelling user.

**Validates: Requirements 6.2, 6.3, 7.2, 7.3**

### Property 22: Cancellation Preserves Request Data
*For any* rental request being cancelled, all original fields (boat_type, desired_weight_range, request_comment, requester_id, requester_email, created_at) should remain unchanged.

**Validates: Requirements 6.5**

### Property 23: Admin Rejection Only for Pending
*For any* admin rejection attempt, the operation should succeed if and only if the request has status "pending".

**Validates: Requirements 7.1, 7.5**

### Property 24: Rejection Reason is Optional
*For any* admin rejection, the operation should succeed both with and without a rejection_reason provided.

**Validates: Requirements 7.4**

### Property 25: Valid Status Transitions
*For any* rental request, status transitions should only occur in these valid paths:
- pending → accepted (via admin accept)
- pending → cancelled (via team manager cancel or admin reject)
- accepted → paid (via payment completion)
- accepted → cancelled (via team manager cancel)
All other transitions should be rejected.

**Validates: Appendix A (Status Transitions)**

## Error Handling

### Validation Errors

All validation errors should return HTTP 400 with descriptive error messages:

```python
{
    "error": "Validation error",
    "message": "request_comment cannot be empty"
}
```

**Validation Rules**:
- Required fields missing → "field_name is required"
- Invalid boat_type → "boat_type must be one of: skiff, 4-, 4+, 4x-, 4x+, 8+, 8x+"
- Empty request_comment → "request_comment cannot be empty"
- request_comment too long → "request_comment must be 500 characters or less"
- desired_weight_range too long → "desired_weight_range must be 50 characters or less"
- Empty assignment_details → "assignment_details cannot be empty"
- assignment_details too long → "assignment_details must be 1000 characters or less"

### Authorization Errors

Authorization errors should return HTTP 403:

```python
{
    "error": "Forbidden",
    "message": "You do not have permission to perform this action"
}
```

**Authorization Rules**:
- Team manager accessing another team manager's requests → 403
- Team manager accessing admin endpoints → 403
- Non-authenticated user accessing any endpoint → 401

### State Transition Errors

Invalid state transitions should return HTTP 400:

```python
{
    "error": "Invalid state transition",
    "message": "Cannot accept request with status 'paid'"
}
```

**State Transition Rules**:
- Accept non-pending request → "Cannot accept request with status '{current_status}'"
- Pay non-accepted request → "Cannot pay for request with status '{current_status}'"
- Cancel paid request → "Cannot cancel request with status 'paid'"
- Reject non-pending request → "Cannot reject request with status '{current_status}'"
- Modify paid request → "Cannot modify request with status 'paid'"

### Not Found Errors

Missing resources should return HTTP 404:

```python
{
    "error": "Not found",
    "message": "Rental request not found: RENTAL_REQUEST#uuid"
}
```

## Testing Strategy

### Dual Testing Approach

This feature will use both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests**:
- Specific examples of request creation, acceptance, payment, cancellation
- Edge cases: empty fields, maximum length fields, boundary values
- Error conditions: invalid boat types, invalid status transitions
- Integration points: payment webhook, admin actions
- Use pytest.mark.parametrize for testing multiple similar cases
- Keep tests simple and focused on one behavior at a time

**Property-Based Tests**:
- Universal properties across all inputs (see Correctness Properties section)
- Use parameterized tests to cover multiple input variations
- State transition validation across all possible states
- Authorization and filtering logic
- Keep tests simple - use pytest.mark.parametrize instead of complex generators

### Property-Based Testing Configuration

**Framework**: Standard pytest with parameterized tests

**Configuration**:
- Each test tagged with: `# Feature: boat-rental-refactoring, Property {N}: {property_text}`
- Use pytest.mark.parametrize for testing multiple inputs
- Test data includes:
  - Valid/invalid boat types
  - Valid/invalid request comments (length variations)
  - Valid/invalid weight ranges
  - Valid/invalid assignment details
  - Request states (pending, accepted, paid, cancelled)
  - User roles (team manager, admin)

**Test Organization**:
```
tests/integration/
  test_rental_request_creation.py
    - test_property_1_request_creation_validation()
    - test_property_2_initial_status_pending()
    - test_property_3_requester_information()
    - test_property_4_creation_timestamp()
  
  test_rental_request_listing.py
    - test_property_5_team_manager_isolation()
    - test_property_6_request_list_sorting()
    - test_property_7_required_fields_present()
    - test_property_8_conditional_fields_present()
    - test_property_9_admin_sees_all()
    - test_property_10_status_filtering()
    - test_property_11_boat_type_filtering()
  
  test_rental_request_acceptance.py
    - test_property_12_accept_requires_assignment()
    - test_property_13_accept_transitions_status()
    - test_property_14_accept_only_pending()
    - test_property_15_assignment_update_preserves_status()
  
  test_rental_request_payment.py
    - test_property_16_payment_only_accepted()
    - test_property_17_payment_transitions_status()
    - test_property_18_rental_price_calculation()
    - test_property_19_paid_immutable()
  
  test_rental_request_cancellation.py
    - test_property_20_cancellation_only_pending_accepted()
    - test_property_21_cancellation_transitions_status()
    - test_property_22_cancellation_preserves_data()
    - test_property_23_rejection_only_pending()
    - test_property_24_rejection_reason_optional()
  
  test_rental_request_state_transitions.py
    - test_property_25_valid_status_transitions()
```

### Migration Testing

Migration from old rental boat system to new rental request system:

**Unit Tests**:
- Test migration of each status: requested → pending, confirmed → accepted, paid → paid
- Test preservation of requester, timestamps, boat information
- Test creation of assignment_details from boat_name and rower_weight_range
- Test deletion of old records after migration

**Migration Script**:
```python
# functions/migrations/migrate_rental_boats_to_requests.py
# One-time migration script to convert RENTAL_BOAT records to RENTAL_REQUEST records
```

## Migration Strategy

### Phase 1: Preparation
1. Deploy new Lambda functions alongside old ones
2. Update API Gateway to route to new endpoints
3. Keep old endpoints active for backward compatibility

### Phase 2: Data Migration
1. Run migration script to convert existing RENTAL_BOAT records to RENTAL_REQUEST records
2. Verify all data migrated correctly
3. Keep old records for rollback capability

### Phase 3: Frontend Update
1. Deploy new frontend components (BoatRentalPage.vue, AdminRentalRequests.vue)
2. Update routing to use new components
3. Test end-to-end workflows

### Phase 4: Cleanup
1. Monitor for issues for 1 week
2. Delete old RENTAL_BOAT records
3. Remove old Lambda functions and API endpoints
4. Update documentation

### Rollback Plan

If issues are discovered:
1. Revert frontend to old components
2. Revert API Gateway routes to old endpoints
3. Old RENTAL_BOAT records still exist for rollback
4. Investigate and fix issues
5. Retry migration

## API Endpoint Summary

### Team Manager Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /rental/request | Create new rental request |
| GET | /rental/my-requests | View own rental requests |
| GET | /rental/requests-for-payment | View accepted requests ready for payment |
| DELETE | /rental/request/{id} | Cancel own rental request |

### Admin Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /admin/rental-requests | View all rental requests (with filters) |
| PUT | /admin/rental-requests/{id}/accept | Accept request and provide assignment details |
| PUT | /admin/rental-requests/{id}/assignment | Update assignment details |
| DELETE | /admin/rental-requests/{id} | Reject rental request |

### Deprecated Endpoints (to be removed after migration)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /admin/rental-boats | Create rental boat inventory |
| GET | /admin/rental-boats | List rental boat inventory |
| PUT | /admin/rental-boats/{id} | Update rental boat |
| DELETE | /admin/rental-boats/{id} | Delete rental boat |
| GET | /rental/boats | List available rental boats |
| POST | /rental/request | Request a rental boat (old version) |

## Performance Considerations

### Database Queries

**Team Manager Queries**:
- Get my requests: Scan with filter on requester_id (consider GSI if performance issues)
- Get requests for payment: Scan with filter on requester_id and status="accepted"

**Admin Queries**:
- Get all requests: Scan all RENTAL_REQUEST records
- Filter by status: Scan with filter expression
- Filter by boat_type: Scan with filter expression

**Optimization Opportunities**:
- Add GSI on requester_id for faster team manager queries
- Add GSI on status for faster admin filtering
- Consider composite GSI on (status, created_at) for sorted filtered queries

### Caching

No caching required for MVP. Rental requests are not high-frequency operations.

### Pagination

For MVP, return all results. If request volume grows:
- Implement pagination with LastEvaluatedKey
- Add limit parameter (default 50, max 100)
- Return pagination metadata in response

## Security Considerations

### Authentication
- All endpoints require valid JWT token
- Token must contain user_id and email
- Token must contain groups (team_managers or admins)

### Authorization
- Team managers can only view/modify their own requests
- Admins can view/modify all requests
- Payment webhook validates Stripe signature

### Data Validation
- All input fields validated for type, length, format
- SQL injection not applicable (DynamoDB)
- XSS prevention in frontend (Vue escapes by default)

### Audit Trail
- All state transitions record user_id and timestamp
- Cancelled requests preserve original data
- Paid requests are immutable

## Monitoring and Logging

### CloudWatch Metrics
- Request creation rate
- Acceptance rate
- Payment completion rate
- Cancellation rate
- Error rates by endpoint

### CloudWatch Logs
- All Lambda invocations logged
- State transitions logged with user_id
- Validation errors logged with details
- Payment webhook events logged

### Alarms
- High error rate (>5% of requests)
- Payment webhook failures
- Database write failures

## Future Enhancements

### Phase 2 Features (not in MVP)
1. Email notifications:
   - Team manager notified when request accepted
   - Admin notified when new request created
2. Request expiration:
   - Pending requests expire after 7 days
   - Accepted requests expire after 3 days if not paid
3. Request history:
   - View all past requests (including cancelled)
   - Export request history to CSV
4. Bulk operations:
   - Admin can accept multiple requests at once
   - Admin can reject multiple requests at once
5. Request comments:
   - Admin can add notes to requests
   - Team manager can add follow-up comments

### Technical Debt
1. Add GSI for better query performance
2. Implement pagination for large result sets
3. Add request caching for frequently accessed data
4. Implement rate limiting per user
