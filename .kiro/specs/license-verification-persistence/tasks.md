# License Verification Persistence - Tasks

## 1. Backend - Database Schema & Permissions

### 1.1 Add Permission to Permission Matrix
- [x] Add `verify_crew_member_license` permission to `functions/init/init_config.py`
- [x] Set admin role: `allowed: True, phases: ['all']`
- [x] Set team_manager role: `allowed: False, phases: []`
- [x] Test permission configuration loads correctly

### 1.2 Update init_config.py
- [x] Verify permission matrix includes new permission
- [x] Document that no migration is needed (schema-less DynamoDB)

### 1.3 Create Migration Script
- [x] Create `functions/migrations/add_license_verification_permission.py`
- [x] Add permission to existing databases
- [x] Run migration on dev environment
- [ ] Run migration on prod environment (after testing)
- [ ] Delete migration file after running on all environments

## 2. Backend - Lambda Functions

### 2.1 Create Single License Verification Endpoint
- [x] Create `functions/admin/update_crew_member_license_verification.py`
- [x] Implement `lambda_handler` with decorators:
  - `@handle_exceptions`
  - `@require_admin`
  - `@require_permission('verify_crew_member_license')`
- [x] Validate request body (status, team_manager_id, details)
- [x] Verify crew member exists
- [x] Update crew member with verification fields:
  - `license_verification_status`
  - `license_verification_date` (current timestamp)
  - `license_verification_details`
  - `license_verified_by` (admin user ID)
- [x] Return updated crew member data
- [x] Handle errors (not found, validation, permission)

### 2.2 Create Bulk License Verification Endpoint
- [x] Create `functions/admin/bulk_update_license_verification.py`
- [x] Implement `lambda_handler` with same decorators as 2.1
- [x] Validate request body (array of verifications)
- [x] Loop through verifications:
  - Verify each crew member exists
  - Update with verification fields
  - Track success/failure for each
- [x] Return summary: `success_count`, `failure_count`, `results` array
- [x] Handle partial failures gracefully
- [x] Set timeout to 60 seconds for bulk operations

### 2.3 Update List All Crew Members (Admin)
- [x] Modify `functions/admin/admin_list_all_crew_members.py`
- [x] Include verification fields in response:
  - `license_verification_status`
  - `license_verification_date`
  - `license_verification_details`
  - `license_verified_by`
- [x] Test that fields return `null` for unverified members

### 2.4 Update List Crew Members (Team Manager)
- [x] Modify `functions/crew/list_crew_members.py`
- [x] Include same verification fields as admin endpoint
- [x] Test that team managers can see verification status

## 3. Backend - API Routes

### 3.1 Add Single Verification Route
- [x] Update `infrastructure/stacks/api_stack.py`
- [x] Create Lambda function resource for `update_crew_member_license_verification`
- [x] Add route: `PATCH /admin/crew/{team_manager_id}/{crew_member_id}/license-verification`
- [x] Configure authorizer
- [x] Set timeout to 30 seconds

### 3.2 Add Bulk Verification Route
- [x] Update `infrastructure/stacks/api_stack.py`
- [x] Create Lambda function resource for `bulk_update_license_verification`
- [x] Add route: `POST /admin/crew/bulk-license-verification`
- [x] Configure authorizer
- [x] Set timeout to 60 seconds

## 4. Backend - Testing

### 4.1 Write Integration Tests
- [x] Create `tests/integration/test_license_verification.py`
- [x] Test: Update single crew member verification (success)
- [x] Test: Update single crew member verification (not found)
- [x] Test: Update single crew member verification (permission denied)
- [x] Test: Bulk update verification (all success)
- [x] Test: Bulk update verification (partial failure)
- [x] Test: Verification status persists after update
- [x] Test: Verification date is set correctly
- [x] Test: Verified by admin ID is recorded
- [x] Test: Team manager can view but not modify

### 4.2 Run Backend Tests
- [x] Run all integration tests: `cd infrastructure && make test`
- [x] Fix any failing tests
- [x] Verify all tests pass

## 5. Frontend - Admin Service

### 5.1 Add API Methods
- [x] Update `frontend/src/services/adminService.js`
- [x] Add `updateCrewMemberLicenseVerification(crewMemberId, teamManagerId, data)`
- [x] Add `bulkUpdateLicenseVerification(data)`
- [x] Test API methods connect to correct endpoints

## 6. Frontend - AdminLicenseChecker Component

### 6.1 Add State Variables
- [x] Add `saving` ref (boolean)
- [x] Add `saveError` ref (string)

### 6.2 Add Computed Properties
- [x] Add `hasUnsavedResults` computed property
- [x] Check if selected members have temporary verification results

### 6.3 Implement Mark as Valid
- [x] Create `markSelectedAsValid` method
- [x] Show confirmation dialog
- [x] Call `bulkUpdateVerification` with `'manually_verified_valid'`
- [x] Update local state on success
- [x] Show success/error message
- [x] Keep selection after operation

### 6.4 Implement Mark as Invalid
- [x] Create `markSelectedAsInvalid` method
- [x] Show confirmation dialog
- [x] Call `bulkUpdateVerification` with `'manually_verified_invalid'`
- [x] Update local state on success
- [x] Show success/error message
- [x] Keep selection after operation

### 6.5 Implement Save Verification Results
- [x] Create `saveVerificationResults` method
- [x] Filter selected members with temporary results (`_licenseStatus`)
- [x] Map to verification payload (status, details)
- [x] Call `bulkUpdateVerification` with payload
- [x] Update local state on success
- [x] Show success/error message with counts
- [x] Keep selection after operation

### 6.6 Implement Bulk Update Helper
- [x] Create `bulkUpdateVerification(manualStatus, verifications)` method
- [x] Handle manual verification (manualStatus provided)
- [x] Handle automatic verification save (verifications provided)
- [x] Call `adminService.bulkUpdateLicenseVerification`
- [x] Update local crew member state with DB response
- [x] Handle errors (403, 404, 400, network)
- [x] Show appropriate error messages

### 6.7 Update Load Crew Members
- [x] Modify `loadCrewMembers` method
- [x] Keep DB verification fields when loading
- [x] Initialize temporary UI state (`_licenseStatus`, `_licenseDetails`, `_checking`)
- [x] Test that DB status displays correctly on load

### 6.8 Add UI Buttons
- [x] Add "Mark as Valid" button to bulk actions section
- [x] Add "Mark as Invalid" button to bulk actions section
- [x] Add "Save Verification Results" button to bulk actions section
- [x] Disable buttons when no selection
- [x] Disable buttons during save operation
- [x] Show loading state on buttons

### 6.9 Update Status Column
- [x] Show DB status if exists (priority)
- [x] Show temporary check status if no DB status
- [x] Show "Not verified" if neither exists
- [x] Add verification method badge (Auto/Manual)
- [x] Add "Unsaved" indicator for temporary results
- [x] Style status badges appropriately

### 6.10 Update Details Column
- [x] Show DB details if exists
- [x] Show verification date
- [x] Show temporary check details if no DB details
- [x] Format date appropriately

### 6.11 Add Helper Methods
- [x] Create `getVerificationStatusClass(status)` method
- [x] Create `getVerificationStatusLabel(status)` method
- [x] Create `formatDate(dateString)` method

## 7. Frontend - CrewMemberList Component (Team Manager)

### 7.1 Add Verification Column
- [x] Add `license_verification` column to `tableColumns`
- [x] Set label, sortable, width, responsive properties
- [x] Position column appropriately in table

### 7.2 Add Template Slot
- [x] Create `#cell-license_verification` template slot
- [x] Show verification badge (Verified/Invalid/Not Verified)
- [x] Style badges with appropriate colors
- [x] Make read-only (no actions)

### 7.3 Add Helper Methods
- [x] Create `getVerificationBadgeClass(status)` method
- [x] Create `getVerificationLabel(status)` method
- [x] Map status to user-friendly labels

### 7.4 Update Card View (Optional)
- [x] Add verification status to CrewMemberCard component
- [x] Show badge in card view
- [x] Ensure consistent styling with table view

## 8. Frontend - Internationalization

### 8.1 Add English Translations
- [x] Update `frontend/src/locales/en.json`
- [x] Add admin.licenseChecker translations:
  - markAsValid, markAsInvalid, saveResults
  - markValidTitle, markValidMessage
  - markInvalidTitle, markInvalidMessage
  - saveSuccess, saveError, noResultsToSave
  - verificationStatus, verifiedValid, verifiedInvalid
  - manuallyVerified, autoVerified
- [x] Add crew.list translations:
  - licenseVerification, notVerified, verified, invalid

### 8.2 Add French Translations
- [x] Update `frontend/src/locales/fr.json`
- [x] Add same translations as English (in French)
- [x] Verify translations are accurate and natural

## 9. Frontend - Styling

### 9.1 Add Status Badge Styles
- [x] Add `.status-verified` class (green)
- [x] Add `.status-invalid` class (red)
- [x] Add `.status-unchecked` class (grey)
- [x] Add `.status-unsaved` class (yellow/warning)
- [x] Add `.verification-method` class (small, muted)
- [x] Add `.verification-meta` class (date display)

### 9.2 Update Button Styles
- [x] Ensure buttons use design tokens
- [x] Verify button sizing is consistent
- [x] Test responsive behavior on mobile

## 10. Testing & Validation

### 10.1 Manual Testing - Admin
- [ ] Load AdminLicenseChecker page
- [ ] Verify DB verification status displays correctly
- [ ] Select crew members
- [ ] Click "Check Selected" with FFAviron cookie
- [ ] Verify temporary results show
- [ ] Click "Save Verification Results"
- [ ] Verify status persists after page refresh
- [ ] Select crew members
- [ ] Click "Mark as Valid"
- [ ] Verify status saved immediately
- [ ] Select crew members
- [ ] Click "Mark as Invalid"
- [ ] Verify status saved immediately
- [ ] Test selection persists through operations
- [ ] Test error handling (network error, permission error)
- [ ] Test filter by verification status
- [ ] Test sort by verification status

### 10.2 Manual Testing - Team Manager
- [ ] Load CrewMemberList page as team manager
- [ ] Verify verification status displays in table view
- [ ] Verify verification status displays in card view
- [ ] Verify status is read-only (no actions available)
- [ ] Verify status persists after page refresh

### 10.3 Edge Cases
- [ ] Test with no crew members
- [ ] Test with all crew members verified
- [ ] Test with mixed verification statuses
- [ ] Test bulk operation with 50+ crew members
- [ ] Test partial failure in bulk operation
- [ ] Test with expired FFAviron cookie
- [ ] Test with invalid crew member ID
- [ ] Test with missing team_manager_id

## 11. Deployment

### 11.1 Deploy Backend
- [ ] Run backend tests: `cd infrastructure && make test`
- [ ] Deploy to dev: `cd infrastructure && make deploy-dev`
- [ ] Test API endpoints in dev environment
- [ ] Verify permission configuration
- [ ] Deploy to prod: `cd infrastructure && make deploy-prod`

### 11.2 Deploy Frontend
- [ ] Build frontend: `cd frontend && npm run build`
- [ ] Deploy to dev: `cd infrastructure && make deploy-frontend-dev`
- [ ] Test UI in dev environment
- [ ] Deploy to prod: `cd infrastructure && make deploy-frontend-prod`

### 11.3 Smoke Testing
- [ ] Test automatic verification + save in prod
- [ ] Test manual verification in prod
- [ ] Test team manager view in prod
- [ ] Verify data persistence in prod
- [ ] Monitor CloudWatch logs for errors

## 12. Documentation

### 12.1 Update User Documentation
- [ ] Document how to use license verification feature
- [ ] Document manual verification fallback
- [ ] Document verification status meanings
- [ ] Add screenshots of UI

### 12.2 Update Technical Documentation
- [ ] Document new API endpoints
- [ ] Document database schema changes
- [ ] Document permission requirements
- [ ] Update API reference documentation

## Notes

- No database migration needed (DynamoDB is schema-less)
- Selection persistence is critical for good UX
- Error handling must be robust (FFAviron can be unreliable)
- Team managers see status but cannot modify (transparency)
- Manual verification provides fallback when automatic fails
