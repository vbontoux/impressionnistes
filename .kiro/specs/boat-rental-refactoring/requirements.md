# Requirements Document

## Introduction

This specification defines the refactoring of the boat rental system to improve the workflow by making team managers the initiators of rental requests. The current system requires admins to create rental boat inventory first, which team managers then request. The new system will allow team managers to create rental requests directly, specifying their needs, and admins will then assign specific boats and accept the requests.

## Glossary

- **Team_Manager**: A user with team manager role who can create rental requests and make payments
- **Admin**: A user with administrative privileges who can view, assign, and accept rental requests
- **Rental_Request**: A request created by a team manager for a boat rental, specifying boat type, desired weight, and comments
- **Rental_Assignment**: Admin-provided details including boat number, oars, location, and other assignment information
- **Boat_Type**: The type of boat (skiff, 4-, 4+, 4x-, 4x+, 8+, 8x+)
- **Request_Status**: The current state of a rental request (pending, accepted, paid, cancelled)
- **Weight_Range**: The desired weight capacity for the rental boat (e.g., "70-90kg")

## Requirements

### Requirement 1: Team Manager Creates Rental Request

**User Story:** As a team manager, I want to create a rental request by specifying my needs, so that I can request a boat without waiting for admin to create inventory first.

#### Acceptance Criteria

1. WHEN a team manager creates a rental request, THE System SHALL require boat_type, desired_weight_range, and request_comment
2. WHEN a team manager creates a rental request, THE System SHALL set the initial status to "pending"
3. WHEN a rental request is created, THE System SHALL record the requester's user_id and email
4. WHEN a rental request is created, THE System SHALL record the creation timestamp
5. THE System SHALL validate that boat_type is one of: skiff, 4-, 4+, 4x-, 4x+, 8+, 8x+
6. THE System SHALL validate that request_comment is not empty and does not exceed 500 characters
7. THE System SHALL validate that desired_weight_range does not exceed 50 characters

### Requirement 2: Team Manager Views Own Rental Requests

**User Story:** As a team manager, I want to view all my rental requests and their current status, so that I can track the progress of my requests.

#### Acceptance Criteria

1. WHEN a team manager requests their rental list, THE System SHALL return only requests created by that team manager
2. WHEN displaying rental requests, THE System SHALL show boat_type, desired_weight_range, request_comment, status, and timestamps
3. WHEN a request is accepted, THE System SHALL display assignment_details provided by the admin
4. THE System SHALL sort rental requests by creation date (most recent first)
5. WHEN a request has status "accepted", THE System SHALL display the accepted_at timestamp
6. WHEN a request has status "paid", THE System SHALL display the paid_at timestamp

### Requirement 3: Admin Views All Rental Requests

**User Story:** As an admin, I want to view all rental requests from all team managers, so that I can manage and assign boats to requests.

#### Acceptance Criteria

1. WHEN an admin requests the rental list, THE System SHALL return all rental requests from all team managers
2. WHEN displaying rental requests, THE System SHALL show requester information (email, user_id)
3. THE System SHALL allow filtering by status (pending, accepted, paid, cancelled)
4. THE System SHALL allow filtering by boat_type
5. THE System SHALL sort rental requests by creation date (most recent first)
6. WHEN displaying requests, THE System SHALL show request_comment and desired_weight_range

### Requirement 4: Admin Assigns and Accepts Rental Request

**User Story:** As an admin, I want to add assignment details and accept a rental request, so that the team manager knows which specific boat they will receive and where to find it.

#### Acceptance Criteria

1. WHEN an admin accepts a rental request, THE System SHALL require assignment_details
2. WHEN an admin accepts a rental request, THE System SHALL change the status from "pending" to "accepted"
3. WHEN a request is accepted, THE System SHALL record the accepted_at timestamp
4. WHEN a request is accepted, THE System SHALL record the admin user_id who accepted it
5. THE System SHALL validate that assignment_details is not empty and does not exceed 1000 characters
6. THE System SHALL prevent accepting a request that is not in "pending" status
7. WHEN assignment_details are updated, THE System SHALL allow updating them without changing the status

### Requirement 5: Team Manager Pays for Accepted Rental

**User Story:** As a team manager, I want to pay for my accepted rental requests, so that I can complete the rental process.

#### Acceptance Criteria

1. WHEN a team manager initiates payment, THE System SHALL only allow payment for requests with status "accepted"
2. WHEN payment is completed, THE System SHALL change the status from "accepted" to "paid"
3. WHEN a request is paid, THE System SHALL record the paid_at timestamp
4. THE System SHALL calculate rental price based on boat_type and base_seat_price configuration
5. WHEN a request has status "paid", THE System SHALL prevent any further modifications
6. THE System SHALL prevent payment for requests that are not in "accepted" status

### Requirement 6: Team Manager Cancels Rental Request

**User Story:** As a team manager, I want to cancel my rental request before payment, so that I can withdraw requests I no longer need.

#### Acceptance Criteria

1. WHEN a team manager cancels a request, THE System SHALL only allow cancellation for requests with status "pending" or "accepted"
2. WHEN a request is cancelled, THE System SHALL change the status to "cancelled"
3. WHEN a request is cancelled, THE System SHALL record the cancelled_at timestamp
4. THE System SHALL prevent cancellation of requests with status "paid"
5. WHEN a request is cancelled, THE System SHALL preserve all request data for audit purposes

### Requirement 7: Admin Rejects Rental Request

**User Story:** As an admin, I want to reject a rental request, so that I can decline requests that cannot be fulfilled.

#### Acceptance Criteria

1. WHEN an admin rejects a request, THE System SHALL change the status from "pending" to "cancelled"
2. WHEN a request is rejected, THE System SHALL record the cancelled_at timestamp
3. WHEN a request is rejected, THE System SHALL record the admin user_id who rejected it
4. THE System SHALL allow admin to provide a rejection_reason
5. THE System SHALL prevent rejection of requests with status "paid"

### Requirement 8: Rental Pricing Calculation

**User Story:** As a system, I want to calculate rental prices consistently, so that team managers know the cost before payment.

#### Acceptance Criteria

1. WHEN calculating rental price for skiff, THE System SHALL use base_seat_price × 2.5
2. WHEN calculating rental price for 4-, THE System SHALL use base_seat_price × 4
3. WHEN calculating rental price for 4+, THE System SHALL use base_seat_price × 5
4. WHEN calculating rental price for 4x-, THE System SHALL use base_seat_price × 4
5. WHEN calculating rental price for 4x+, THE System SHALL use base_seat_price × 5
6. WHEN calculating rental price for 8+, THE System SHALL use base_seat_price × 9
7. WHEN calculating rental price for 8x+, THE System SHALL use base_seat_price × 9
8. THE System SHALL retrieve base_seat_price from the pricing configuration

### Requirement 9: Data Migration from Old System

**User Story:** As a system administrator, I want to migrate existing rental boat data to the new request-based system, so that existing rentals are preserved.

#### Acceptance Criteria

1. WHEN migrating existing rental boats with status "requested", THE System SHALL convert them to rental requests with status "pending"
2. WHEN migrating existing rental boats with status "confirmed", THE System SHALL convert them to rental requests with status "accepted"
3. WHEN migrating existing rental boats with status "paid", THE System SHALL convert them to rental requests with status "paid"
4. WHEN migrating, THE System SHALL preserve requester, timestamps, and boat information
5. WHEN migrating, THE System SHALL create assignment_details from existing boat_name and rower_weight_range
6. THE System SHALL delete old rental boat inventory records after successful migration

### Requirement 10: API Endpoint Changes

**User Story:** As a developer, I want clear API endpoints for the new rental request system, so that frontend can interact with the backend correctly.

#### Acceptance Criteria

1. THE System SHALL provide POST /rental/request endpoint for creating rental requests
2. THE System SHALL provide GET /rental/my-requests endpoint for team managers to view their requests
3. THE System SHALL provide GET /admin/rental-requests endpoint for admins to view all requests
4. THE System SHALL provide PUT /admin/rental-requests/{id}/accept endpoint for accepting requests
5. THE System SHALL provide PUT /admin/rental-requests/{id}/assignment endpoint for updating assignment details
6. THE System SHALL provide DELETE /rental/request/{id} endpoint for team managers to cancel requests
7. THE System SHALL provide DELETE /admin/rental-requests/{id} endpoint for admins to reject requests
8. THE System SHALL provide GET /rental/requests-for-payment endpoint for team managers to view accepted requests ready for payment
9. THE System SHALL deprecate old rental boat inventory endpoints

## Appendix A: Status Transitions

Valid status transitions:

- **pending** → accepted (admin accepts)
- **pending** → cancelled (team manager cancels OR admin rejects)
- **accepted** → paid (team manager completes payment)
- **accepted** → cancelled (team manager cancels)
- **paid** → (no transitions allowed - final state)
- **cancelled** → (no transitions allowed - final state)

## Appendix B: Data Model Changes

### Old Model (Rental Boat Inventory)
```
RENTAL_BOAT#{uuid}
- boat_type
- boat_name
- rower_weight_range
- status (new, available, requested, confirmed, paid)
- requester (email)
- requested_at
- confirmed_at
- paid_at
```

### New Model (Rental Request)
```
RENTAL_REQUEST#{uuid}
- boat_type
- desired_weight_range
- request_comment
- status (pending, accepted, paid, cancelled)
- requester_id (user_id)
- requester_email
- assignment_details (added by admin when accepting)
- created_at
- accepted_at
- accepted_by (admin user_id)
- paid_at
- cancelled_at
- cancelled_by (user_id - could be team manager or admin)
- rejection_reason (optional, set by admin)
```

## Appendix C: Pricing Reference

| Boat Type | Seats | Price Formula |
|-----------|-------|---------------|
| skiff | 1 | base_seat_price × 2.5 |
| 4- | 4 | base_seat_price × 4 |
| 4+ | 5 | base_seat_price × 5 |
| 4x- | 4 | base_seat_price × 4 |
| 4x+ | 5 | base_seat_price × 5 |
| 8+ | 9 | base_seat_price × 9 |
| 8x+ | 9 | base_seat_price × 9 |
