# Implementation Plan: Boat Rental Refactoring

## Overview

This implementation plan refactors the boat rental system from an inventory-based model to a request-based model. Team managers will create rental requests specifying their needs, and admins will assign boats and accept requests. The implementation follows a phased approach to ensure backward compatibility during migration.

## Tasks

- [x] 1. Update shared utilities and data models
  - Create rental request validation utilities
  - Add status transition validation functions
  - Update pricing calculation to work with rental requests
  - _Requirements: 1.5, 1.6, 1.7, 4.5, 5.4, 8.1-8.8_

- [x] 1.1 Write property test for rental request validation
  - **Property 1: Request Creation Validation**
  - **Validates: Requirements 1.1, 1.5, 1.6, 1.7**

- [x] 1.2 Write property test for pricing calculation
  - **Property 18: Rental Price Calculation**
  - **Validates: Requirements 5.4, 8.1-8.8**

- [x] 2. Implement team manager rental request creation
  - [x] 2.1 Create `functions/rental/create_rental_request.py`
    - Implement request validation
    - Generate rental_request_id
    - Set initial status to "pending"
    - Record requester information and timestamps
    - Save to DynamoDB
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

- [x] 2.2 Write property tests for request creation
  - **Property 2: Initial Status is Pending**
  - **Property 3: Requester Information Recorded**
  - **Property 4: Creation Timestamp Recorded**
  - **Validates: Requirements 1.2, 1.3, 1.4**

- [x] 3. Implement team manager request viewing
  - [x] 3.1 Create `functions/rental/get_my_rental_requests.py`
    - Query DynamoDB for requests by requester_id
    - Sort by created_at descending
    - Return only requester's own requests
    - Include all required fields in response
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [x] 3.2 Write property tests for request listing
  - **Property 5: Team Manager Request Isolation**
  - **Property 6: Request List Sorting**
  - **Property 7: Required Fields Present in Response**
  - **Property 8: Conditional Fields Present Based on Status**
  - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

- [x] 4. Implement admin request viewing and filtering
  - [x] 4.1 Create `functions/admin/list_rental_requests.py`
    - Scan DynamoDB for all rental requests
    - Implement status filtering
    - Implement boat_type filtering
    - Sort by created_at descending
    - Include requester information in response
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 4.2 Write property tests for admin listing and filtering
  - **Property 9: Admin Sees All Requests**
  - **Property 10: Status Filtering Works Correctly**
  - **Property 11: Boat Type Filtering Works Correctly**
  - **Validates: Requirements 3.1, 3.3, 3.4**

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement admin request acceptance
  - [x] 6.1 Create `functions/admin/accept_rental_request.py`
    - Validate assignment_details (required, not empty, ≤1000 chars)
    - Validate current status is "pending"
    - Update status to "accepted"
    - Record accepted_at timestamp
    - Record accepted_by (admin user_id)
    - Save to DynamoDB
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [x] 6.2 Write property tests for request acceptance
  - **Property 12: Accept Requires Assignment Details**
  - **Property 13: Accept Transitions Status Correctly**
  - **Property 14: Accept Only Works on Pending Requests**
  - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6**

- [x] 7. Implement admin assignment details update
  - [x] 7.1 Create `functions/admin/update_assignment_details.py`
    - Validate assignment_details
    - Validate current status is "accepted"
    - Update assignment_details without changing status
    - Record updated_at timestamp
    - Save to DynamoDB
    - _Requirements: 4.7_

- [x] 7.2 Write property test for assignment update
  - **Property 15: Assignment Details Update Preserves Status**
  - **Validates: Requirements 4.7**

- [x] 8. Implement team manager request cancellation
  - [x] 8.1 Create `functions/rental/cancel_rental_request.py`
    - Validate requester_id matches authenticated user
    - Validate status is "pending" or "accepted"
    - Update status to "cancelled"
    - Record cancelled_at timestamp
    - Record cancelled_by (team manager user_id)
    - Preserve all original request data
    - Save to DynamoDB
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 8.2 Write property tests for request cancellation
  - **Property 20: Cancellation Only for Pending or Accepted**
  - **Property 21: Cancellation Transitions Status Correctly**
  - **Property 22: Cancellation Preserves Request Data**
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**

- [x] 9. Implement admin request rejection
  - [x] 9.1 Create `functions/admin/reject_rental_request.py`
    - Validate status is "pending"
    - Update status to "cancelled"
    - Record cancelled_at timestamp
    - Record cancelled_by (admin user_id)
    - Set rejection_reason if provided (optional)
    - Save to DynamoDB
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 9.2 Write property tests for request rejection
  - **Property 23: Admin Rejection Only for Pending**
  - **Property 24: Rejection Reason is Optional**
  - **Validates: Requirements 7.1, 7.3, 7.4, 7.5**

- [x] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Update payment integration
  - [x] 11.1 Update `functions/rental/get_rentals_for_payment.py`
    - Query for RENTAL_REQUEST records instead of RENTAL_BOAT
    - Filter by status "accepted" and requester_id
    - Calculate pricing based on boat_type
    - Return requests with pricing information
    - _Requirements: 5.1, 5.4, 5.6_

- [x] 11.2 Update `functions/payment/confirm_payment_webhook.py`
    - Handle RENTAL_REQUEST records instead of RENTAL_BOAT
    - Update status from "accepted" to "paid"
    - Record paid_at timestamp
    - Validate status is "accepted" before payment
    - Prevent modifications after payment
    - _Requirements: 5.2, 5.3, 5.5_

- [x] 11.3 Write property tests for payment
  - **Property 16: Payment Only for Accepted Requests**
  - **Property 17: Payment Transitions Status Correctly**
  - **Property 19: Paid Requests are Immutable**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.5, 5.6**

- [x] 12. Implement comprehensive state transition validation
  - [x] 12.1 Add state transition validation to all endpoints
    - Validate all status transitions follow allowed paths
    - Reject invalid transitions with descriptive errors
    - _Requirements: Appendix A_

- [x] 12.2 Write property test for state transitions
  - **Property 25: Valid Status Transitions**
  - **Validates: Appendix A (Status Transitions)**

- [x] 13. Update API Gateway routes
  - [x] 13.1 Add new rental request endpoints
    - POST /rental/request (create_rental_request)
    - GET /rental/my-requests (get_my_rental_requests)
    - GET /rental/requests-for-payment (get_rentals_for_payment)
    - DELETE /rental/request/{id} (cancel_rental_request)
    - _Requirements: 10.1, 10.2, 10.6, 10.8_

- [x] 13.2 Add new admin rental request endpoints
    - GET /admin/rental-requests (list_rental_requests)
    - PUT /admin/rental-requests/{id}/accept (accept_rental_request)
    - PUT /admin/rental-requests/{id}/assignment (update_assignment_details)
    - DELETE /admin/rental-requests/{id} (reject_rental_request)
    - _Requirements: 10.3, 10.4, 10.5, 10.7_

- [x] 14. Checkpoint - Ensure all backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 15. Refactor frontend team manager interface
  - [x] 15.1 Update `frontend/src/views/BoatRentalPage.vue`
    - Remove "Available Boats" section
    - Add "Create Rental Request" form with:
      - Boat type selector
      - Desired weight range input
      - Request comment textarea
      - Submit button
    - Update "My Requests" section to show:
      - Request details (boat_type, desired_weight_range, request_comment)
      - Status badge with color coding
      - Assignment details (when accepted)
      - Cancel button (for pending/accepted)
      - Pay button (for accepted)
    - Update API calls to use new endpoints
    - _Requirements: 1.1-1.7, 2.1-2.6, 6.1-6.5_

- [x] 15.2 Update `frontend/src/services/apiClient.js`
    - Add methods for new rental request endpoints
    - Update payment flow to use rental requests
    - _Requirements: 10.1, 10.2, 10.6, 10.8_

- [x] 16. Refactor frontend admin interface
  - [x] 16.1 Refactor `frontend/src/views/admin/AdminBoatInventory.vue`
    - Replace old inventory-based interface with new request-based interface
    - List all rental requests with table/card view toggle
    - Add filters for status and boat_type
    - Show requester information (email, user_id)
    - For pending requests:
      - "Accept" button that opens modal for assignment details
      - "Reject" button with optional rejection reason
    - For accepted requests:
      - "Edit Assignment" button to update assignment details
    - Display all request details and timestamps
    - _Requirements: 3.1-3.6, 4.1-4.7, 7.1-7.5_
    - _Note: Reused existing file and route (/admin/boats) instead of creating new AdminRentalRequests.vue_

- [x] 16.2 Update `frontend/src/services/apiClient.js`
    - Add admin rental request API methods (listRentalRequests, acceptRentalRequest, updateAssignmentDetails, rejectRentalRequest)
    - _Requirements: 10.3, 10.4, 10.5, 10.7_
    - _Note: Route and navigation already exist, no changes needed_

- [x] 17. Update translations
  - [x] 17.1 Update `frontend/src/locales/en.json`
    - Add translations for rental request creation
    - Add translations for request statuses
    - Add translations for assignment details
    - Add translations for admin actions

- [x] 17.2 Update `frontend/src/locales/fr.json`
    - Add French translations for all new strings

- [x] 18. Create cleanup script for old rental records
  - [x] 18.1 Create `infrastructure/delete_old_rental_boats.py`
    - Query all RENTAL_BOAT records from DynamoDB
    - Display count and list of records to be deleted
    - Prompt for confirmation before deletion
    - Delete all RENTAL_BOAT records
    - Log deletion results
    - _Note: Replaces migration since no prod data exists yet_

- [x] 19. Final checkpoint - End-to-end testing
  - [x] 19.1 Test team manager workflow
    - Create rental request
    - View own requests
    - Cancel request
    - Pay for accepted request

- [x] 19.2 Test admin workflow
    - View all requests
    - Filter by status and boat_type
    - Accept request with assignment details
    - Update assignment details
    - Reject request

- [ ] 20. Documentation and cleanup
  - [ ] 20.1 Update API documentation
    - Document new endpoints
    - Mark old endpoints as deprecated
    - Update request/response examples

- [ ] 20.2 Update user guides
    - Create team manager guide for rental requests
    - Create admin guide for managing rental requests
    - Document migration process

- [ ] 20.3 Add monitoring and alerts
    - Add CloudWatch metrics for request creation, acceptance, payment
    - Add alarms for high error rates
    - Add logging for state transitions

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests use simple parameterized tests (pytest.mark.parametrize)
- Unit tests validate specific examples and edge cases
- Migration script is critical for preserving existing rental data
- Frontend changes should maintain mobile responsiveness
- All API changes maintain backward compatibility during migration phase


## Additional Fixes Required

- [ ] 21. Fix rejected request handling
  - [x] 21.1 Change reject behavior to mark as "rejected" instead of deleting
    - Update `functions/admin/reject_rental_request.py` to set status to "rejected" instead of deleting
    - Keep rejection_reason field
    - Record rejected_at timestamp
    - Record rejected_by (admin user_id)
    - _Rationale: Team managers need to see rejected requests, unlike cancelled ones_

  - [x] 21.2 Update team manager request listing to show rejected requests
    - Update `functions/rental/get_my_rental_requests.py` to include rejected requests
    - Ensure rejected requests are visible in team manager view
    - _Requirements: Team managers should see all their requests including rejected ones_

  - [x] 21.3 Update frontend to display rejected status
    - Update `frontend/src/views/BoatRentalPage.vue` to show rejected requests
    - Add visual distinction for rejected status (red badge)
    - Show rejection_reason if provided
    - Remove action buttons for rejected requests

- [x] 22. Add admin ability to reject/reset accepted requests
  - [x] 22.1 Update reject endpoint to allow rejecting accepted requests
    - Modify `functions/admin/reject_rental_request.py` to accept both "pending" and "accepted" status
    - Validate request is not yet paid (status != "paid")
    - _Requirements: Admin should be able to reject accepted requests if not yet paid_

  - [x] 22.2 Add "Reset to Pending" functionality for accepted requests
    - Create new endpoint `functions/admin/reset_rental_request.py`
    - Allow admin to reset "accepted" request back to "pending"
    - Clear assignment_details, accepted_at, accepted_by
    - Validate request is not yet paid
    - _Alternative: Could be part of reject functionality_

  - [x] 22.3 Update frontend admin interface
    - Add "Reject" button for accepted requests (if not paid)
    - Add "Reset to Pending" button for accepted requests (if not paid)
    - Update UI to show these options only when status is "accepted" and not "paid"

- [x] 23. Remove "Pay Now" button from rental request list
  - [x] 23.1 Update `frontend/src/views/BoatRentalPage.vue`
    - Remove "Pay Now" button from individual rental requests
    - Keep only "Cancel" button for pending/accepted requests
    - _Rationale: Payment should only happen through the dedicated payment page_

  - [x] 23.2 Update translations
    - Remove or update any payment-related strings in rental request list
    - Ensure payment flow is clear (accepted requests → payment page)

- [x] 24. Fix payment page to show accepted rental requests
  - [x] 24.1 Verify `functions/rental/get_rentals_for_payment.py` is working
    - Ensure it queries for status "accepted"
    - Ensure it filters by requester_id
    - Ensure it includes pricing information
    - _Note: Backend should already be correct, verify it's working_

  - [x] 24.2 Update frontend payment page
    - Verify `frontend/src/views/Payment.vue` calls correct endpoint
    - Ensure accepted rental requests are displayed
    - Show boat type, assignment details, and pricing
    - _Requirements: Accepted rental requests should appear on payment page_

## Summary of Changes

**Key Differences from Original Behavior:**
1. **Cancelled vs Rejected:**
   - Cancelled (by team manager): Deleted from database, not visible
   - Rejected (by admin): Kept in database with "rejected" status, visible to team manager

2. **Admin Powers:**
   - Can reject both pending AND accepted requests (if not paid)
   - Can reset accepted requests back to pending (if not paid)

3. **Payment Flow:**
   - No "Pay Now" button in rental request list
   - Accepted requests automatically appear on payment page
   - Single payment flow for all accepted requests

