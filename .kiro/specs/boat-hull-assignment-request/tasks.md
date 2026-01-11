# Implementation Plan: Boat Hull Assignment Request

## Overview

This implementation adds an optional boat (hull) assignment request feature to crew registrations. Team managers can request a physical boat from organizers, provide requirements, and see which boat has been assigned. The feature includes four new database fields and updates to pricing logic to replace the deprecated `is_boat_rental` field.

## Tasks

- [x] 0. Database Migration: Reset Paid Crews
- Create migration script to reset all paid crews to appropriate status
- Script should recalculate status based on current crew state (seats filled, race selected)
- Crews should become 'complete', 'free' (all RCPM), or 'incomplete' based on current data
- _Requirements: Preparation for pricing logic changes_

- [x] 1. Backend: Add Database Schema Fields
- [x] 1.1 Update validation schema in `functions/shared/validation.py`
  - Add `boat_request_enabled` (boolean, default: false)
  - Add `boat_request_comment` (string, nullable, max 500 chars)
  - Add `assigned_boat_identifier` (string, nullable, max 100 chars)
  - Add `assigned_boat_comment` (string, nullable, max 500 chars)
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 1.2 Add validation tests to existing test file
  - Add tests to `tests/integration/test_boat_registration_api.py`
  - Test boat_request_comment length validation (500 char limit)
  - Test assigned_boat_identifier length validation (100 char limit)
  - Test boundary cases (exactly at limit, one over limit)
  - Test empty/null values are accepted
  - Test special characters are accepted
  - _Requirements: 2.2, 5.3_

- [x] 2. Backend: Update Completion Status Logic
- [x] 2.1 Update `is_registration_complete` in `functions/shared/boat_registration_utils.py`
  - Add check for boat_request_enabled
  - If boat_request_enabled=true AND assigned_boat_identifier is null/empty, return False
  - If boat_request_enabled=false, ignore assigned_boat_identifier
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 2.2 Add completion status tests to existing test file
  - Add tests to `tests/integration/test_boat_registration_api.py`
  - Test crew with boat_request_enabled=true and no assignment is incomplete
  - Test crew with boat_request_enabled=true and assignment can be complete
  - Test crew with boat_request_enabled=false ignores assignment status
  - _Requirements: 4.1, 4.2, 4.3_
  - **Note:** Tests will fail until backend implementation is complete (tasks 4.1, 4.2, 5.1)

- [x] 3. Backend: Update Pricing Calculation
- [x] 3.1 Update `calculate_boat_pricing` in `functions/shared/pricing.py`
  - Replace `is_boat_rental` check with `boat_request_enabled AND assigned_boat_identifier` check
  - Calculate rental fees only when boat is actually assigned
  - Ensure RCPM members pay €0 for both Participation Fee and Boat Rental
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.8_

- [x] 3.2 Add pricing tests to existing test file
  - Add tests to `tests/integration/test_boat_registration_api.py` or create `functions/shared/test_pricing.py`
  - Test crew with boat_request_enabled=false (own boat) - participation fee only
  - Test crew with boat_request_enabled=true, assigned_boat_identifier=null (incomplete) - no pricing
  - Test crew with boat_request_enabled=true, assigned_boat_identifier set (RCPM boat) - participation + rental
  - Test RCPM members pay €0 for both fees
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 4. Backend: Create Boat Registration Updates
- [x] 4.1 Update `create_boat_registration.py`
  - Initialize boat_request_enabled, boat_request_comment, assigned_boat_identifier, assigned_boat_comment
  - Clear boat request fields if boat_request_enabled=false
  - _Requirements: 1.4, 1.5, 5.5_

- [x] 4.2 Update `update_boat_registration.py`
  - Allow team managers to update boat_request_enabled and boat_request_comment
  - Clear related fields when disabling boat request
  - Prevent team managers from updating assigned_boat_identifier or assigned_boat_comment
  - _Requirements: 1.4, 2.3, 2.4, 3.7, 3.8_

- [x] 4.3 Add boat request field tests to existing test file
  - Add tests to `tests/integration/test_boat_registration_api.py`
  - Test disabling boat_request clears related fields
  - Test round-trip persistence of boat_request_enabled
  - Test round-trip persistence of boat_request_comment
  - Test team managers cannot modify assigned_boat_identifier
  - _Requirements: 1.4, 1.5, 1.6, 2.3, 2.4, 2.6, 3.4, 5.4_

- [x] 5. Backend: Admin Boat Assignment
- [x] 5.1 Update `admin_update_boat.py`
  - Allow admins to set assigned_boat_identifier (max 100 chars)
  - Allow admins to set assigned_boat_comment (max 500 chars)
  - Recalculate registration_status after assignment
  - Sanitize and validate inputs
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.9, 8.10, 8.11_

- [x] 5.2 Add admin assignment tests to existing test file
  - Add tests to `tests/integration/test_admin_api.py`
  - Test admin can assign boat identifier
  - Test admin can add assignment comment
  - Test completion status recalculates after assignment
  - Test team managers cannot modify assigned boat fields
  - _Requirements: 3.4, 8.3, 8.4, 8.5, 8.6_

- [x] 6. Backend: Payment Prevention
- [x] 6.1 Update payment logic to block pending boat requests
  - Check boat_request_enabled and assigned_boat_identifier before allowing payment
  - Return clear error message if boat not assigned
  - _Requirements: 4.6, 10.2, 10.7_

- [x] 6.2 Add payment prevention tests to existing test file
  - Add tests to `tests/integration/test_boat_registration_api.py`
  - Test payment blocked when boat_request_enabled=true and no assignment
  - Test payment allowed when boat_request_enabled=true and boat assigned
  - Test payment allowed when boat_request_enabled=false
  - _Requirements: 4.6_

- [x] 7. Backend: Input Sanitization
- [x] 7.1 Add XSS sanitization for boat_request_comment and assigned_boat_comment
  - Sanitize HTML/script tags
  - Preserve other special characters
  - _Requirements: 9.6, 9.7_

- [x] 7.2 Add whitespace trimming for assigned_boat_identifier
  - Trim leading/trailing whitespace
  - Convert empty strings to null
  - _Requirements: 9.8_

- [x] 7.3 Add sanitization tests to existing test file
  - Add tests to `tests/integration/test_boat_registration_api.py`
  - Test whitespace trimming on assigned_boat_identifier
  - Test XSS sanitization on comments
  - Test special characters are preserved (non-XSS)
  - _Requirements: 9.6, 9.7, 9.8_

- [x] 8. Checkpoint - Backend Complete
- Run all backend tests
- Verify API endpoints work correctly
- Ensure all tests pass, ask the user if questions arise

- [x] 9. Frontend: Boat Registration Form
- [x] 9.1 Update `BoatRegistrationForm.vue`
  - Add boat request toggle/checkbox
  - Add boat request comment textarea (500 char limit with counter)
  - Add read-only assigned boat name field
  - Add read-only assigned boat comment display
  - Show/hide fields based on boat_request_enabled
  - Clear fields when disabling boat request
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 3.1, 3.2, 3.3, 3.4, 3.7, 3.8, 3.9, 3.10, 11.1, 11.2, 11.3_

- [x] 9.2 Write unit tests for form behavior
  - Test toggle shows/hides fields
  - Test character counter
  - Test field clearing on disable
  - Test read-only fields cannot be edited
  - _Requirements: 1.2, 1.3, 2.2, 3.7, 3.8_

- [x] 10. Frontend: Boats List View
- [x] 10.1 Update `Boats.vue` (Card View)
  - Display boat request status when enabled
  - Show "Waiting for assignment" if pending
  - Show assigned boat name if assigned
  - Display assigned boat comment directly in card view
  - Hide boat request info if not enabled
  - _Requirements: 3.5, 3.6, 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 10.2 Update `Boats.vue` (Table View)
  - Add boat request status column
  - Show assigned boat name with hover tooltip for comment
  - Display info icon when comment exists
  - _Requirements: 3.5, 3.6, 6.1, 6.2, 6.3_

- [x] 11. Frontend: Admin Boats View
- [x] 11.1 Update `AdminBoats.vue` table
  - Add "Boat Request" column
  - Show "-" for no request
  - Show "Requested" for pending requests
  - Show assigned boat name with hover tooltip for comment
  - Display info icon when comment exists
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 11.2 Update `AdminBoats.vue` edit modal
  - Display team manager's boat_request_comment if present
  - Add text input for assigned_boat_identifier (100 char limit)
  - Add textarea for assigned_boat_comment (500 char limit with counter)
  - Add help text explaining fields
  - Allow clearing assignment by emptying fields
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.7, 8.10, 8.11_

- [x] 11.3 Write unit tests for admin interface
  - Test boat request column displays correctly
  - Test edit modal shows/hides assignment fields
  - Test character counters
  - _Requirements: 7.1, 7.2, 7.3, 8.1, 8.2_

- [x] 12. Frontend: Add Translations
- [x] 12.1 Add English translations to `en.json`
  - boat.boatRequest.title
  - boat.boatRequest.enableLabel
  - boat.boatRequest.helpText
  - boat.boatRequest.commentLabel
  - boat.boatRequest.commentPlaceholder
  - boat.boatRequest.assignedBoatLabel
  - boat.boatRequest.assignedBoatCommentLabel
  - boat.boatRequest.assignedBoatHelp
  - boat.boatRequest.notAssigned
  - boat.boatRequest.status
  - boat.boatRequest.waitingAssignment
  - boat.boatRequest.assignmentDetails
  - _Requirements: 11.5_

- [x] 12.2 Add French translations to `fr.json`
  - Same keys as English with French translations
  - _Requirements: 11.5_

- [x] 13. Checkpoint - Frontend Complete
- Test all UI components manually
- Verify responsive design on mobile
- Ensure all translations display correctly
- Ensure all tests pass, ask the user if questions arise

- [ ] 14. Integration Testing
- [ ] 14.1 Add integration tests to existing test file
  - Add tests to `tests/integration/test_boat_registration_api.py`
  - Test create crew with boat request enabled
  - Test update crew to enable/disable boat request
  - Test admin assigns boat (in `test_admin_api.py`)
  - Test admin changes assignment
  - Test admin removes assignment
  - Test payment blocked with pending request
  - Test payment allowed after assignment
  - Test paid crew cannot disable boat request if boat assigned
  - _Requirements: 1.1-1.6, 2.1-2.7, 3.1-3.10, 4.1-4.6, 8.1-8.11, 12.1_

- [ ] 15. Export Updates
- [ ] 15.1 Update export endpoints to include boat request fields
  - Update `export_boat_registrations_json.py`
  - Include boat_request_enabled, boat_request_comment, assigned_boat_identifier, assigned_boat_comment
  - Handle missing fields gracefully for backward compatibility
  - _Requirements: 7.7, 11.4_

- [ ] 16. Final Testing and Deployment
- [ ] 16.1 Run full test suite
  - All unit tests pass
  - All integration tests pass
  - _Requirements: All_

- [ ] 16.2 Test backward compatibility
  - Verify existing crews without boat request fields work correctly
  - Verify API remains backward compatible
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 16.3 Deploy to dev environment
  - Deploy backend changes
  - Deploy frontend changes
  - Verify feature works end-to-end in dev
  - _Requirements: All_

- [ ] 16.4 Manual testing checklist
  - Create crew with boat request enabled
  - Enter boat request comment with special characters
  - Verify assigned boat field is read-only
  - Admin assigns boat with comment
  - Verify crew becomes complete after assignment
  - Admin changes boat assignment
  - Admin removes boat assignment
  - Verify crew becomes incomplete after removal
  - Disable boat request on crew
  - Verify fields are cleared
  - Try to disable boat request on paid crew with assignment
  - Verify error message
  - View boat request status in boats list (card and table views)
  - View boat request in admin interface
  - Export crews with boat request data
  - _Requirements: All_

## Notes

- All tasks including tests are required to ensure comprehensive coverage
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Tests are added to existing test files where possible to complement boat registration tests
- Unit tests validate specific examples, edge cases, and integration scenarios
- The migration script (Task 0) must be run before deploying to reset paid crews
- Tests complement existing test suites and validate new boat request functionality
