# License Verification Persistence - Requirements

## Overview

Enable admins to verify crew member rowing licenses and persist verification results to the database. This provides both automatic verification via FFAviron intranet scraping and manual verification as a fallback when the automatic system is unavailable.

## Background

Currently, the license verification feature works locally in the frontend only:
- Admins can check licenses via FFAviron intranet (using a workaround with cookies)
- Results are displayed in the UI temporarily
- Results are **not saved** to the database
- If the page is refreshed, all verification results are lost

This feature adds persistence so that:
- Verification results are saved to crew member records
- Both team managers and admins can see verification status
- Manual verification is available as a fallback
- Verification history is maintained (who verified, when)

## User Stories

### US-1: Save Automatic Verification Results
**As an** admin  
**I want to** save the results of automatic license checks to the database  
**So that** verification results persist and don't need to be re-checked every time

**Acceptance Criteria:**
1. After running automatic license checks, admin can select crew members and click "Save Verification Results"
2. Only selected crew members' verification results are saved
3. Saved data includes: status (valid/invalid), verification date, details from FFAviron, and admin user ID
4. If save fails, error message is shown and verification status remains unchanged
5. Successfully saved verifications show a success message
6. Verification status persists after page refresh

### US-2: Manual License Verification (Valid)
**As an** admin  
**I want to** manually mark selected crew members' licenses as valid  
**So that** I can verify licenses when the automatic system is unavailable or I've verified through other means

**Acceptance Criteria:**
1. Admin can select one or more crew members
2. "Mark as Valid" button is available when crew members are selected
3. Clicking the button immediately saves verification status to database
4. Status is set to "manually_verified_valid"
5. Verification date and admin ID are recorded
6. Success message confirms how many licenses were marked as valid
7. UI updates to show verified status immediately

### US-3: Manual License Verification (Invalid)
**As an** admin  
**I want to** manually mark selected crew members' licenses as invalid  
**So that** I can flag problematic licenses when the automatic system is unavailable

**Acceptance Criteria:**
1. Admin can select one or more crew members
2. "Mark as Invalid" button is available when crew members are selected
3. Clicking the button immediately saves verification status to database
4. Status is set to "manually_verified_invalid"
5. Verification date and admin ID are recorded
6. Success message confirms how many licenses were marked as invalid
7. UI updates to show invalid status immediately

### US-4: View Verification Status (Admin)
**As an** admin  
**I want to** see the verification status of all crew members  
**So that** I can track which licenses have been verified and which still need verification

**Acceptance Criteria:**
1. License checker page loads verification status from database
2. Status column shows: Not verified (grey), Verified Valid (green), Verified Invalid (red)
3. Badge indicates if verification was automatic or manual
4. Details column shows verification date and who verified
5. Can filter by verification status (all, unchecked, valid, invalid)
6. Can sort by verification status
7. Verification status persists across page refreshes

### US-5: View Verification Status (Team Manager)
**As a** team manager  
**I want to** see the verification status of my crew members  
**So that** I know which licenses have been verified by admins

**Acceptance Criteria:**
1. Crew member list shows verification status badge for each member
2. Status displayed: Not verified, Verified, Invalid
3. Team managers can see status but cannot modify it
4. Verification date is visible
5. Status is visible in both card and table views

### US-6: Error Handling for Verification Failures
**As an** admin  
**I want to** see clear error messages when verification fails  
**So that** I understand what went wrong and can take appropriate action

**Acceptance Criteria:**
1. If automatic check fails (network error, FFAviron unavailable), error is shown but status remains "not verified"
2. If save to database fails, error message explains the issue
3. Crew members with errors are clearly indicated in the UI
4. Partial success is handled (some save successfully, others fail)
5. Error messages are dismissible
6. Failed verifications can be retried

### US-7: Bulk Operations with Selection Persistence
**As an** admin  
**I want to** select crew members and have that selection persist through verification actions  
**So that** I can check licenses and then save the results without re-selecting

**Acceptance Criteria:**
1. Selecting crew members persists through "Check Selected" action
2. Selecting crew members persists through "Mark as Valid" action
3. Selecting crew members persists through "Mark as Invalid" action
4. "Save Verification Results" button saves only selected crew members
5. Selection can be cleared manually
6. Selection state is visible (count of selected members)

## Functional Requirements

### FR-1: Database Schema
Crew member records must include the following fields:
- `license_verification_status`: String | null
  - Values: `null`, `'verified_valid'`, `'verified_invalid'`, `'manually_verified_valid'`, `'manually_verified_invalid'`
- `license_verification_date`: ISO 8601 timestamp string | null
- `license_verification_details`: String | null (details from FFAviron or manual note)
- `license_verified_by`: String | null (user ID of admin who verified)

### FR-2: Backend API Endpoints

#### PATCH /admin/crew-members/{crew_member_id}/license-verification
Update license verification status for a single crew member.

**Request Body:**
```json
{
  "status": "verified_valid" | "verified_invalid" | "manually_verified_valid" | "manually_verified_invalid",
  "details": "string (optional)",
  "team_manager_id": "string (required for admin impersonation)"
}
```

**Response:**
```json
{
  "crew_member_id": "string",
  "license_verification_status": "string",
  "license_verification_date": "ISO timestamp",
  "license_verified_by": "string"
}
```

#### POST /admin/crew-members/bulk-license-verification
Update license verification status for multiple crew members.

**Request Body:**
```json
{
  "verifications": [
    {
      "crew_member_id": "string",
      "team_manager_id": "string",
      "status": "verified_valid" | "verified_invalid" | "manually_verified_valid" | "manually_verified_invalid",
      "details": "string (optional)"
    }
  ]
}
```

**Response:**
```json
{
  "success_count": 0,
  "failure_count": 0,
  "results": [
    {
      "crew_member_id": "string",
      "success": true,
      "error": "string (if failed)"
    }
  ]
}
```

### FR-3: Permissions
- New permission: `verify_crew_member_license`
- Only admins can verify licenses (both automatic and manual)
- Team managers can view verification status but cannot modify it

### FR-4: Frontend UI Components

#### Admin License Checker Page
**New Buttons:**
1. "Mark as Valid" - Manually mark selected crew members as valid
2. "Mark as Invalid" - Manually mark selected crew members as invalid
3. "Save Verification Results" - Save automatic check results for selected crew members

**Button States:**
- Disabled when no crew members selected
- Disabled during verification operations
- Show loading state during save operations

**Status Display:**
- Load verification status from database on page load
- Show status badge: Not verified (grey), Verified Valid (green), Verified Invalid (red)
- Show verification method badge: "Auto" or "Manual"
- Show verification date and admin name in details column
- Filter by verification status

#### Team Manager Crew Member List
**Status Display:**
- Show verification status badge in both card and table views
- Badge colors: Not verified (grey), Verified (green), Invalid (red)
- Show verification date (no admin name for privacy)
- Read-only (no verification actions available)

### FR-5: Error Handling
1. Network errors during automatic check: Show error, keep status as "not verified"
2. Database save errors: Show error message, don't update UI status
3. Partial bulk save failures: Show summary (X succeeded, Y failed)
4. Invalid data errors: Show validation error messages
5. Permission errors: Show "not authorized" message

### FR-6: Data Validation
1. Status must be one of the allowed values
2. Crew member ID must exist
3. Team manager ID must exist (for admin impersonation)
4. Admin must have `verify_crew_member_license` permission
5. Details field is optional, max 500 characters

## Non-Functional Requirements

### NFR-1: Performance
- Bulk verification save should complete within 5 seconds for up to 100 crew members
- Page load should retrieve verification status efficiently (single query)
- UI should remain responsive during bulk operations

### NFR-2: Usability
- Clear visual distinction between verified and unverified licenses
- Clear indication of verification method (automatic vs manual)
- Error messages are clear and actionable
- Success messages confirm the action taken

### NFR-3: Data Integrity
- Verification status changes are atomic (all or nothing for single updates)
- Bulk operations handle partial failures gracefully
- Verification date is always set when status is set
- Verified by admin ID is always recorded

### NFR-4: Security
- Only admins can modify verification status
- Admin impersonation is properly logged
- Verification actions are auditable (who, when, what)

## Out of Scope

The following are explicitly out of scope for this feature:
1. Verification history tracking (keeping old verification records)
2. Verification required phase (blocking payments until verified)
3. Automatic re-verification after a time period
4. Email notifications for verification status changes
5. Verification notes/comments field (beyond the details field)
6. Verification approval workflow (multi-step verification)

## Success Metrics

1. **Verification Persistence Rate**: 100% of saved verifications persist after page refresh
2. **Error Rate**: < 5% of verification save operations fail
3. **Manual Verification Usage**: Track % of verifications that are manual vs automatic
4. **Time Savings**: Reduce time spent re-verifying licenses by eliminating need to re-check

## Dependencies

1. Existing AdminLicenseChecker.vue component
2. Existing license checking utility (licenseChecker.js)
3. Existing admin API infrastructure
4. Existing permission system
5. DynamoDB crew member table (no migration needed - schema-less)

## Assumptions

1. DynamoDB schema can be extended without migration (schema-less)
2. Existing FFAviron scraping mechanism continues to work
3. Admin users have proper permissions configured
4. Team managers should see verification status for transparency
5. No verification history is needed (only current status)

## Risks

1. **FFAviron Availability**: Automatic verification depends on FFAviron intranet being accessible
   - **Mitigation**: Manual verification provides fallback
   
2. **Cookie Expiration**: FFAviron cookies expire, requiring admins to refresh them
   - **Mitigation**: Clear error messages guide admins to refresh cookies
   
3. **Bulk Operation Performance**: Large bulk saves might be slow
   - **Mitigation**: Implement with reasonable batch sizes, show progress

4. **Data Consistency**: Verification status might become stale over time
   - **Mitigation**: Out of scope for now, can add re-verification later

## Open Questions

None - all questions have been answered.
