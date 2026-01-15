# Implementation Plan: Centralized Access Control System

## Overview

This implementation plan breaks down the Centralized Access Control System into discrete, incremental tasks. Each task builds on previous work and includes testing to validate functionality. The plan follows a 4-phase approach: Backend Foundation → Backend Integration → Frontend Integration → Admin UI.

## Tasks

- [x] 1. Set up access control module foundation
  - Create `functions/shared/access_control.py` with core classes and data models
  - Implement `EventPhase` enum and `UserContext`, `ResourceContext`, `PermissionResult` dataclasses
  - Add basic module structure with imports and constants
  - _Requirements: 1.1, 1.2, 6.1_

- [x] 2. Implement event phase detection
  - [x] 2.1 Implement `get_current_event_phase()` function
    - Query system configuration for registration dates
    - Compare current time with dates to determine phase
    - Return appropriate `EventPhase` enum value
    - _Requirements: 1.1, 1.2_

  - [x] 2.2 Write unit test for event phase detection
    - Create `tests/unit/test_access_control_phase.py`
    - Test phase calculation with various date configurations
    - Test caching behavior (same result within TTL)
    - Run via `cd infrastructure && make test`
    - **Validates: Requirements 1.1, 1.3**

  - [x] 2.3 Add caching for event phase calculation
    - Implement 60-second in-memory cache
    - Add cache invalidation on configuration updates
    - _Requirements: 1.5, 11.9_

- [x] 3. Implement permission matrix storage and retrieval
  - [x] 3.1 Update init_config.py to create default permission matrix
    - Add default permissions matching requirements appendix A
    - Store in DynamoDB with PK='CONFIG', SK='PERMISSIONS'
    - _Requirements: 10.1, 10.2, 10.3_

  - [x] 3.2 Implement `get_permission_matrix()` function
    - Query DynamoDB for permission configuration
    - Implement 60-second caching
    - Handle missing configuration with safe defaults
    - _Requirements: 6.6, 11.8_

  - [x] 3.3 Write unit test for permission matrix retrieval
    - Create `tests/unit/test_access_control_matrix.py`
    - Test loading matrix from database
    - Test caching behavior
    - Test fallback to defaults when missing
    - Run via `cd infrastructure && make test`
    - **Validates: Requirements 6.4, 6.5**


- [x] 4. Implement temporary access grant system
  - [x] 4.1 Create database schema for temporary access grants
    - Add DynamoDB items with PK='TEMP_ACCESS', SK='USER#{user_id}'
    - Include grant_timestamp, expiration_timestamp, status fields
    - Add GSI on status for querying active grants
    - _Requirements: 10.4, 10.5_

  - [x] 4.2 Implement `check_temporary_access_grant()` function
    - Query DynamoDB for active grants by user_id
    - Check expiration timestamp against current time
    - Mark expired grants as expired
    - Return boolean indicating active grant exists
    - _Requirements: 5.1, 5.2, 5.5, 10.6, 10.7_

  - [x] 4.3 Write unit tests for temporary access grant validation
    - Create `tests/unit/test_access_control_grants.py`
    - Test active grant detection
    - Test expired grant rejection
    - Test grant expiration marking
    - Run via `cd infrastructure && make test`
    - **Validates: Requirements 5.3, 5.4, 5.5**

- [x] 5. Implement core permission checking logic
  - [x] 5.1 Implement `check_permission()` function
    - Extract event phase from cache or calculate
    - Load permission matrix from cache or database
    - Check temporary access grant for user
    - Evaluate phase-based permissions
    - Evaluate data state restrictions
    - Apply impersonation bypass rules
    - Return PermissionResult with is_permitted and denial_reason
    - _Requirements: 6.4, 6.5, 11.1, 11.2, 11.3, 11.4_

  - [x] 5.2 Implement data state restriction checks
    - Check if crew member is assigned (requires_not_assigned)
    - Check if boat is paid (requires_not_paid)
    - Apply restrictions universally to all users
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6_

  - [x] 5.3 Implement impersonation bypass logic
    - Detect impersonation from user context
    - Bypass event phase restrictions when impersonating
    - Still enforce data state restrictions
    - _Requirements: 4.1, 4.2, 4.5_

  - [x] 5.4 Write unit tests for permission checking
    - Create `tests/unit/test_access_control_permissions.py`
    - Test phase-based permission evaluation
    - Test impersonation bypass (phase only, not data state)
    - Test data state restrictions (assigned crew, paid boat)
    - Test temporary access bypass (phase only, not data state)
    - Run via `cd infrastructure && make test`
    - **Validates: Requirements 3.1-3.6, 4.1, 4.2**


- [x] 6. Implement audit logging
  - [x] 6.1 Implement `log_permission_denial()` function
    - Write denial to DynamoDB with PK='AUDIT#PERMISSION_DENIAL'
    - Include user_id, action, resource, reason, timestamp
    - Handle write failures gracefully (log to CloudWatch)
    - _Requirements: 12.1, 12.7_

  - [x] 6.2 Implement `log_permission_grant_with_bypass()` function
    - Write grant to DynamoDB with PK='AUDIT#PERMISSION_BYPASS'
    - Include bypass_reason (impersonation or temporary_access)
    - Include impersonated_user_id if applicable
    - _Requirements: 4.3, 5.9, 12.2, 12.3_

  - [x] 6.3 Write unit tests for audit logging
    - Create `tests/unit/test_access_control_audit.py`
    - Test denial logging creates correct entry
    - Test bypass logging includes bypass reason
    - Test graceful handling of write failures
    - Run via `cd infrastructure && make test`
    - **Validates: Requirements 12.1, 12.2, 12.3**

- [x] 7. Create permission decorator for Lambda handlers
  - [x] 7.1 Implement `@require_permission` decorator
    - Extract user context from Lambda event
    - Extract resource context from request body
    - Call check_permission() with contexts
    - Return HTTP 403 with error message if denied
    - Log permission decision
    - _Requirements: 7.1, 7.2, 7.7_

  - [x] 7.2 Implement helper functions for context extraction
    - `get_user_context_from_event()` - Extract user info from event
    - `get_resource_context_from_body()` - Extract resource info from body
    - Handle missing or invalid context gracefully
    - _Requirements: 11.2, 11.3_

  - [x] 7.3 Write unit tests for decorator
    - Create `tests/unit/test_access_control_decorator.py`
    - Test successful permission grant
    - Test permission denial with 403 response
    - Test context extraction from various event formats
    - Run via `cd infrastructure && make test`
    - **Validates: Requirements 7.1, 7.2**

- [x] 8. Checkpoint - Backend foundation complete
  - Ensure all tests pass ✅ (266 tests passing)
  - Verify permission checking works in isolation ✅ (Decorator tests confirm this)
  - Ask the user if questions arise


- [x] 9. Integrate permission checks into crew member Lambda handlers
  - [x] 9.1 Update create_crew_member.py
    - Add `@require_permission('create_crew_member')` decorator
    - Remove TODO comments
    - Test with various event phases
    - _Requirements: 2.1, 2.2, 7.3_

  - [x] 9.2 Update update_crew_member.py
    - Add `@require_permission('edit_crew_member')` decorator
    - Keep existing assigned crew check (now handled by permission system)
    - Remove TODO comments
    - _Requirements: 2.3, 2.6, 3.1, 7.4_

  - [x] 9.3 Update delete_crew_member.py
    - Add `@require_permission('delete_crew_member')` decorator
    - Keep existing assigned crew check (now handled by permission system)
    - Remove TODO comments
    - _Requirements: 2.3, 2.6, 3.1, 7.4_

  - [x] 9.4 Write integration tests for crew member permissions
    - Create `tests/integration/test_crew_member_permissions.py`
    - Test create during registration period → Success
    - Test create after registration closes → Denied
    - Test edit assigned crew member → Denied
    - Test admin impersonation → Success with audit log
    - Run via `cd infrastructure && make test`
    - **Validates: Requirements 2.1-2.11, 3.1, 3.2, 4.1-4.5**

- [x] 10. Integrate permission checks into boat registration Lambda handlers
  - [x] 10.1 Update create_boat_registration.py
    - Add `@require_permission('create_boat_registration')` decorator
    - Remove TODO comments
    - _Requirements: 2.1, 2.2, 7.3_

  - [x] 10.2 Update update_boat_registration.py
    - Add `@require_permission('edit_boat_registration')` decorator
    - Keep existing paid boat check (now handled by permission system)
    - Remove TODO comments
    - _Requirements: 2.3, 2.7, 3.3, 7.4_

  - [x] 10.3 Update delete_boat_registration.py
    - Add `@require_permission('delete_boat_registration')` decorator
    - Keep existing paid boat check (now handled by permission system)
    - Remove TODO comments
    - _Requirements: 2.3, 2.7, 3.4, 7.4_

  - [x] 10.4 Write integration tests for boat registration permissions
    - Create `tests/integration/test_boat_registration_permissions.py`
    - Test create during registration period → Success
    - Test create after registration closes → Denied
    - Test edit paid boat → Denied
    - Test delete paid boat → Denied
    - Run via `cd infrastructure && make test`
    - **Validates: Requirements 2.1-2.11, 3.3, 3.4**


- [x] 11. Integrate permission checks into payment Lambda handler
  - [x] 11.1 Update create_payment_intent.py
    - Add `@require_permission('process_payment')` decorator
    - Allow payments during and after registration period
    - Deny payments after payment deadline
    - Fixed decorator order consistency (auth decorator before permission decorator)
    - _Requirements: 2.4, 2.8, 2.10, 7.5_

  - [x] 11.2 Write integration tests for payment permissions
    - Create `tests/integration/test_payment_permissions.py`
    - Test payment during registration → Success ✅
    - Test payment after registration closes → Success ✅
    - Test payment after payment deadline → Denied ✅
    - Test payment before registration → Denied ✅
    - Test admin impersonation bypasses payment deadline ✅
    - Run via `cd infrastructure && make test` ✅ (All 282 tests passing)
    - **Validates: Requirements 2.4, 2.8, 2.10**

- [x] 12. Create admin APIs for temporary access grants
  - [x] 12.1 Create grant_temporary_access.py Lambda
    - Accept user_id and hours parameters ✅
    - Calculate expiration timestamp from config ✅
    - Create grant in DynamoDB ✅
    - Log grant creation with admin ID ✅
    - _Requirements: 5.1, 5.2, 5.9_

  - [x] 12.2 Create revoke_temporary_access.py Lambda
    - Accept grant_id parameter ✅
    - Update grant status to 'revoked' ✅
    - Set revoked_at timestamp and revoked_by_admin_id ✅
    - Log revocation ✅
    - _Requirements: 5.6, 5.9_

  - [x] 12.3 Create list_temporary_access_grants.py Lambda
    - Query all grants with status='active' ✅
    - Calculate remaining time for each grant ✅
    - Return list with grant details ✅
    - _Requirements: 5.7_

  - [x] 12.4 Write integration tests for temporary access grant APIs
    - Create `tests/integration/test_temporary_access_grants.py` ✅
    - Test grant creation → Success ✅
    - Test user with active grant can bypass phase restrictions ✅
    - Test grant expiration → No longer provides access ✅
    - Test manual revocation → Immediate effect ✅
    - Run via `cd infrastructure && make test` ✅ (All 292 tests passing)
    - **Validates: Requirements 5.1-5.9**

- [x] 13. Checkpoint - Backend integration complete
  - Ensure all Lambda handlers use permission checks
  - Verify all TODOs are replaced
  - Run full integration test suite
  - Ask the user if questions arise


- [x] 14. Create frontend permission composable
  - [x] 14.1 Create usePermissions.js composable
    - Implement reactive state for currentPhase, permissionMatrix, userContext
    - Implement `initialize()` function to fetch permission state
    - Implement `canPerformAction()` function for permission checks
    - Implement `getPermissionMessage()` function for denial messages
    - Implement `hasBypass()` function to check impersonation/temporary access
    - Implement `getCurrentPhase()` function
    - Add 60-second caching for permission state
    - _Requirements: 8.1, 8.12, 11.5, 11.6, 11.7_

  - [x] 14.2 Create API service functions for permission checks
    - `fetchCurrentPhase()` - Call GET /api/permissions/current-phase
    - `fetchPermissionMatrix()` - Call GET /admin/permissions/config
    - `fetchUserContext()` - Extract from auth store
    - Handle API errors gracefully
    - _Requirements: 8.1, 11.5_

  - [x] 14.3 Write unit tests for usePermissions composable
    - Test canPerformAction() with various contexts
    - Test getPermissionMessage() returns correct messages
    - Test bypass detection (impersonation, temporary access)
    - Test caching behavior
    - **Validates: Requirements 8.1, 8.11, 8.12**

- [x] 15. Update crew member components with permission checks
  - [x] 15.1 Update CrewMemberCard.vue
    - Import and use usePermissions composable
    - Compute canEdit and canDelete based on permissions
    - Add :disabled bindings to Edit and Delete buttons
    - Add :title tooltips with permission messages
    - _Requirements: 8.2, 8.3, 8.5, 8.7_

  - [x] 15.2 Update CrewMemberList.vue
    - Use usePermissions composable
    - Disable Edit and Delete buttons based on permissions
    - Add tooltips explaining why buttons are disabled
    - _Requirements: 8.2, 8.3, 8.5, 8.7_

  - [x] 15.3 Update CrewMembers.vue (list page)
    - Use usePermissions composable
    - Disable "Create Crew Member" button based on event phase
    - Show message explaining when creation is allowed
    - _Requirements: 8.4_

  - [x] 15.4 Write integration tests for crew member UI permissions
    - Test buttons enabled during registration period
    - Test buttons disabled after registration closes
    - Test tooltips display correct messages
    - Test admin impersonation enables buttons
    - **Validates: Requirements 8.2-8.7, 8.10**


  - [x] 16. Update boat registration components with permission checks
  - [x] 16.1 Update BoatRegistrationCard.vue
    - Import and use usePermissions composable
    - Compute canEdit, canDelete, canPay based on permissions
    - Add :disabled bindings to buttons
    - Add :title tooltips with permission messages
    - Disable all buttons for paid boats
    - _Requirements: 8.2, 8.3, 8.6, 8.8, 8.9_

  - [x] 16.2 Update BoatRegistrationList.vue
    - Use usePermissions composable
    - Disable Edit and Delete buttons based on permissions
    - Disable buttons for paid boats
    - Add tooltips explaining restrictions
    - _Requirements: 8.2, 8.3, 8.6, 8.8_

  - [x] 16.3 Update BoatRegistrations.vue (list page)
    - Use usePermissions composable
    - Disable "Create Boat Registration" button based on event phase
    - Show message explaining when creation is allowed
    - _Requirements: 8.4_

  - [x] 16.4 Write integration tests for boat registration UI permissions
    - Test buttons enabled during registration period
    - Test buttons disabled after registration closes
    - Test paid boat buttons always disabled
    - Test payment button disabled after payment deadline
    - **Validates: Requirements 8.2-8.9**

- [x] 17. Update payment components with permission checks
  - [x] 17.1 Update Payment.vue
    - Use usePermissions composable
    - Disable "Pay" button based on event phase
    - Show message when payment is not allowed
    - Allow payment during and after registration period
    - Deny payment after payment deadline
    - _Requirements: 8.9_

  - [x] 17.2 Write integration tests for payment UI permissions
    - Test payment button enabled during registration
    - Test payment button enabled after registration closes
    - Test payment button disabled after payment deadline
    - **Validates: Requirements 8.9**

- [x] 18. Checkpoint - Frontend integration complete
  - Ensure all components use permission checks ✅
  - Verify buttons are disabled appropriately ✅
  - Verify tooltips display correct messages ✅
  - Test with various event phases ✅
  - Ask the user if questions arise


- [x] 19. Create admin permission configuration UI
  - [x] 19.1 Create PermissionMatrixTable.vue component
    - Display permission matrix as editable table
    - Rows: actions, Columns: event phases
    - Checkboxes for each action/phase combination
    - Show data state requirements (requires_not_assigned, requires_not_paid)
    - _Requirements: 9.2, 9.3_

  - [x] 19.2 Create PermissionConfig.vue admin page
    - Use PermissionMatrixTable component
    - Load current permission configuration
    - Allow editing of permission matrix
    - Save button to update configuration
    - Reset to defaults button
    - Show confirmation before saving
    - _Requirements: 9.1, 9.4, 9.5, 9.6, 9.7_

  - [x] 19.3 Create update_permission_config.py Lambda
    - Accept updated permission matrix
    - Validate matrix for consistency
    - Update CONFIG#PERMISSIONS in DynamoDB
    - Log configuration change with admin ID
    - Invalidate permission cache
    - _Requirements: 9.4, 9.5, 9.8, 9.9_

  - [x] 19.4 Write integration tests for permission configuration
    - Create `tests/integration/test_permission_config.py`
    - Test loading current configuration
    - Test updating configuration → Success
    - Test invalid configuration → Validation error
    - Test reset to defaults → Restores original rules
    - Test configuration change takes effect immediately
    - Run via `cd infrastructure && make test`
    - **Validates: Requirements 9.1-9.9**
    - ✅ All 8 tests passing

- [x] 20. Create admin temporary access grant UI
  - [x] 20.1 Create TemporaryAccessGrantForm.vue component
    - User selection dropdown
    - Hours input (default from config)
    - Notes textarea
    - Submit button to create grant
    - _Requirements: 5.1, 5.2_

  - [x] 20.2 Create TemporaryAccessGrants.vue admin page
    - Show list of active grants with remaining time
    - Show TemporaryAccessGrantForm for creating new grants
    - Revoke button for each active grant
    - Show grant history (expired and revoked)
    - Auto-refresh every 60 seconds
    - _Requirements: 5.7, 5.8_

  - [x] 20.3 Write integration tests for temporary access grant UI
    - Test creating grant → Success
    - Test grant appears in active list
    - Test revoking grant → Removed from active list
    - Test expired grants move to history
    - **Validates: Requirements 5.1-5.9**


- [x] 21. Create admin audit log viewer UI
  - [x] 21.1 Create get_permission_audit_logs.py Lambda
    - Query audit logs from DynamoDB
    - Support filtering by user_id, action, date range
    - Support pagination with next_token
    - Return both denial logs and bypass logs
    - _Requirements: 12.4, 12.5, 12.6_
    - ✅ Lambda function created with proper environment variable handling

  - [x] 21.2 Create PermissionAuditLogs.vue admin page
    - Display audit logs in sortable table
    - Filter by user, action, date range, reason
    - Show denial logs with reasons
    - Show bypass logs with impersonation/temporary access flags
    - Pagination controls
    - Export to CSV button
    - _Requirements: 12.4, 12.5, 12.6_
    - ✅ Admin page created with full filtering and export functionality

  - [x] 21.3 Write integration tests for audit log viewer
    - Create `tests/integration/test_permission_audit_logs.py`
    - Test loading audit logs → Success
    - Test filtering by user → Correct results
    - Test filtering by action → Correct results
    - Test filtering by date range → Correct results
    - Test filtering by log type → Correct results
    - Test pagination → Correct page navigation
    - Test empty results → Empty list
    - Test timestamp sorting → Descending order
    - Run via `cd infrastructure && make test`
    - **Validates: Requirements 12.4, 12.5, 12.6**
    - ✅ All 8 tests passing

- [x] 22. Add i18n messages for permission errors
  - [x] 22.1 Add French error messages
    - Add messages to frontend/src/locales/fr.json
    - Include all denial reasons from appendix B
    - _Requirements: 7.8, 8.3_

  - [x] 22.2 Add English error messages
    - Add messages to frontend/src/locales/en.json
    - Include all denial reasons from appendix B
    - _Requirements: 7.8, 8.3_

  - [x] 22.3 Update components to use i18n messages
    - Use $t() for all permission messages
    - Pass denial_reason_key from backend
    - Fallback to English if translation missing
    - _Requirements: 7.8, 8.3_

- [x] 23. End-to-end testing and validation
  - [x] 23.1 Run full integration test suite
    - Run `cd infrastructure && make test` to verify all backend tests pass ✅
    - All backend permission checks working ✅
    - All frontend buttons disabled appropriately ✅
    - All audit logs created correctly ✅
    - All admin UIs functional ✅
    - **Validates: All requirements**

  - [x] 23.2 Test complete user flows
    - Team manager registration flow with date restrictions ✅
    - Admin impersonation flow with bypass ✅
    - Temporary access grant flow ✅
    - Permission configuration update flow ✅
    - **Validates: All requirements**

  - [x] 23.3 Write integration test for backend-frontend alignment
    - Create `tests/integration/test_backend_frontend_alignment.py` ✅
    - Test same action/context returns same result in backend and frontend ✅
    - Test permission messages match between backend and frontend ✅
    - Run via `cd infrastructure && make test` ✅ (All 313 tests passing)
    - **Validates: Requirements 7.8, 8.12**

- [x] 24. Fix permission state reactivity across components
  - [x] 24.1 Convert usePermissions to use shared reactive state
    - Replace local refs with shared reactive object
    - Ensure all components see same permission state
    - When admin saves permissions, all components update automatically
    - _Requirements: 8.12, 9.9_
  
  - [x] 24.2 Test permission refresh across components
    - Admin changes permission in config page
    - Verify crew member list buttons update without page refresh
    - Verify boat registration buttons update without page refresh
    - **Validates: Requirements 8.12, 9.9**

- [x] 25. Final checkpoint - System complete
  - All tests passing
  - All requirements validated
  - Documentation updated
  - Ready for deployment

## Notes

- All tests are required and must be minimal (no Hypothesis library)
- Tests should run fast using pytest with moto for AWS mocking
- **All backend tests must be runnable via `cd infrastructure && make test`**
- Backend tests should be placed in `tests/integration/` or `tests/unit/` directories
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end flows
- Focus on essential test cases that validate core functionality

## Running Tests

**Backend tests:**
```bash
cd infrastructure
make test                    # Run all tests
make test ARGS="tests/integration/test_access_control.py"  # Run specific test file
```

**Frontend tests:**
```bash
cd frontend
npm run test                 # Run all frontend tests
npm run test -- usePermissions.test.js  # Run specific test file
```

