# Admin Boat License Status - Requirements

## Overview

Add a combined license verification status column to the admin boat list (AdminBoats.vue) that shows whether all crew members in a boat have verified licenses. This allows admins to quickly identify boats with unverified crew members.

## Background

Currently, the admin boat list shows:
- Boat number, event type, boat type
- Race assignment
- Team manager, club
- Registration status (incomplete, complete, paid, forfait)
- Crew composition (filled seats, average age)

However, there is no visibility into whether the crew members have verified licenses. Admins must navigate to the license checker page to verify crew licenses, then manually cross-reference with boats.

This feature adds a "License" column that aggregates the license verification status of all crew members in each boat, providing at-a-glance visibility.

## User Story

### US-1: View Combined License Status in Admin Boat List

**As an** admin  
**I want to** see a combined license verification status for each boat registration  
**So that** I can quickly identify boats with unverified crew members

**Acceptance Criteria:**

1. Admin boat list (AdminBoats.vue) shows a "License" column in table view
2. License column displays a badge with combined status:
   - **"Verified" (green)** - ALL crew members have valid licenses (`verified_valid` or `manually_verified_valid`)
   - **"Invalid" (red)** - ANY crew member has invalid or unverified license
3. If boat has no crew assigned yet, show **"-"**
4. Badge uses same styling as existing verification badges (consistent with team manager crew list)
5. Status is visible in both table view and card view
6. Badge is informational only (not clickable)
7. Combined status is calculated from crew member `license_verification_status` fields
8. Status updates automatically when crew verification changes
9. Status persists across page refreshes

## Functional Requirements

### FR-1: Combined Status Calculation Logic

The combined license status must be calculated as follows:

```
IF boat has no crew assigned (no seats with crew_member_id):
  RETURN null (display "-")

IF ALL crew members have status in ['verified_valid', 'manually_verified_valid']:
  RETURN 'verified' (display "Verified" green badge)

IF ANY crew member has status NOT in ['verified_valid', 'manually_verified_valid']:
  RETURN 'invalid' (display "Invalid" red badge)
```

**Edge Cases:**
- Boat with empty seats array → null
- Boat with seats but no crew assigned → null
- Boat with mix of verified and unverified crew → 'invalid'
- Boat with all manually verified crew → 'verified'
- Boat with all automatically verified crew → 'verified'
- Boat with mix of manual and automatic verified crew → 'verified'

### FR-2: Backend API Response

The admin boats endpoint must include the combined license status:

**Endpoint:** `GET /admin/boats`

**Response** (modified):
```json
{
  "boats": [
    {
      "boat_registration_id": "uuid",
      "event_type": "42km",
      "boat_type": "8+",
      "seats": [
        {
          "position": 1,
          "crew_member_id": "uuid",
          "crew_member_license_verification_status": "verified_valid"
        }
      ],
      "crew_license_status": "verified" | "invalid" | null,
      // ... other existing fields ...
    }
  ]
}
```

**Calculation:** Backend calculates `crew_license_status` for each boat based on FR-1 logic.

### FR-3: Frontend Display - Table View

**Column Configuration:**
- **Key:** `crew_license_status`
- **Label:** "License" (i18n: `admin.boats.licenseStatus`)
- **Sortable:** false
- **Width:** 120px
- **Align:** center
- **Responsive:** always visible

**Display Logic:**
- `crew_license_status === 'verified'` → Green badge "Verified"
- `crew_license_status === 'invalid'` → Red badge "Invalid"
- `crew_license_status === null` → "-" (grey text)

### FR-4: Frontend Display - Card View

**Location:** In boat details section, after club information

**Display:**
```
License: [Verified Badge] or [Invalid Badge] or "-"
```

Same badge styling and logic as table view.

### FR-5: Badge Styling

Reuse existing verification badge styles from `CrewMemberList.vue`:

```css
.verification-badge {
  display: inline-block;
  padding: var(--badge-padding, 0.25rem 0.75rem);
  border-radius: var(--badge-border-radius, 12px);
  font-size: var(--badge-font-size, 0.75rem);
  font-weight: var(--font-weight-medium, 500);
  width: fit-content;
}

.verification-valid {
  background-color: #d4edda;
  color: #155724;
}

.verification-invalid {
  background-color: #f8d7da;
  color: #721c24;
}
```

### FR-6: Internationalization

**English:**
- `admin.boats.licenseStatus`: "License"
- `admin.boats.verified`: "Verified"
- `admin.boats.invalid`: "Invalid"

**French:**
- `admin.boats.licenseStatus`: "Licence"
- `admin.boats.verified`: "Vérifié"
- `admin.boats.invalid`: "Invalide"

## Non-Functional Requirements

### NFR-1: Performance

- Combined status calculation must not significantly impact boat list load time
- Calculation should be done in a single pass over crew members
- No additional database queries required (use existing seat data)

### NFR-2: Consistency

- Badge styling must match existing verification badges in CrewMemberList.vue
- Status calculation logic must be consistent across all boats
- Display behavior must be identical in table and card views

### NFR-3: Maintainability

- Calculation logic should be centralized in backend
- Frontend should only display the calculated status
- Badge styles should be reusable across components

## Out of Scope

The following are explicitly out of scope for this feature:

1. **Clickable badges** - Badge is informational only, not interactive
2. **Drill-down to crew details** - No modal or navigation on badge click
3. **Filtering by license status** - No filter dropdown for license status
4. **Sorting by license status** - Column is not sortable
5. **License verification actions** - No ability to verify licenses from boat list
6. **Historical license status** - Only current status is shown
7. **License expiration warnings** - No date-based warnings

## Success Metrics

1. **Visibility:** 100% of boats show license status (verified/invalid/-)
2. **Accuracy:** Combined status correctly reflects all crew member statuses
3. **Consistency:** Badge styling matches existing verification badges
4. **Performance:** No measurable impact on boat list load time (<100ms)

## Dependencies

1. Existing license verification fields on crew members:
   - `license_verification_status`
   - Values: `verified_valid`, `verified_invalid`, `manually_verified_valid`, `manually_verified_invalid`, `null`
2. Existing admin boats endpoint: `GET /admin/boats`
3. Existing boat seat data structure with crew member assignments
4. Existing verification badge styles in CrewMemberList.vue

## Assumptions

1. Crew member license verification status is already implemented and working
2. Admin boats endpoint already includes seat data with crew member IDs
3. Seat data includes crew member license verification status
4. Badge styling from CrewMemberList.vue can be reused
5. No migration needed - status is calculated on-the-fly

## Risks

1. **Performance:** Calculating status for many boats with many crew members could be slow
   - **Mitigation:** Calculate in single pass, no additional queries
   
2. **Data Consistency:** Crew member status might be stale if not refreshed
   - **Mitigation:** Status is calculated from current database data on each request
   
3. **UI Clutter:** Adding another column might make table too wide
   - **Mitigation:** Column is always visible (responsive: always), width is minimal (120px)

## Open Questions

None - all requirements are clear and agreed upon.
