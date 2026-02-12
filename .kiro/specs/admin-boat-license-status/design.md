# Admin Boat License Status - Design

## Overview

This document describes the technical design for adding a combined license verification status column to the admin boat list. The status aggregates the license verification status of all crew members in each boat.

## Architecture

### System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Vue.js)                        │
├─────────────────────────────────────────────────────────────┤
│  AdminBoats.vue                                              │
│  - Display crew_license_status in table                     │
│  - Display crew_license_status in card view                 │
│  - Render verification badges                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ GET /admin/boats
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (AWS Lambda)                        │
├─────────────────────────────────────────────────────────────┤
│  admin_list_all_boats.py                                    │
│  - Fetch all boats with seat data                          │
│  - Calculate crew_license_status for each boat             │
│  - Return boats with crew_license_status field             │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Query
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Database (DynamoDB)                         │
├─────────────────────────────────────────────────────────────┤
│  Boat Items:                                                │
│  - seats[] with crew_member_id                              │
│  - seats[].crew_member_license_verification_status          │
└─────────────────────────────────────────────────────────────┘
```

## Backend Implementation

### Modified Lambda Function

**File:** `functions/admin/admin_list_all_boats.py`

#### Add Helper Function

```python
def calculate_crew_license_status(boat):
    """
    Calculate combined license verification status for boat crew.
    
    Args:
        boat (dict): Boat registration item with seats data
        
    Returns:
        str | None: 'verified', 'invalid', or None
    """
    seats = boat.get('seats', [])
    
    # No seats defined
    if not seats:
        return None
    
    # Get all crew members assigned to seats
    assigned_crew_statuses = []
    for seat in seats:
        if seat.get('crew_member_id'):
            status = seat.get('crew_member_license_verification_status')
            assigned_crew_statuses.append(status)
    
    # No crew assigned
    if not assigned_crew_statuses:
        return None
    
    # Check if ALL crew members are verified valid
    valid_statuses = ['verified_valid', 'manually_verified_valid']
    all_verified = all(
        status in valid_statuses
        for status in assigned_crew_statuses
    )
    
    if all_verified:
        return 'verified'
    
    # Any crew member is invalid or not verified
    return 'invalid'
```

#### Modify Lambda Handler

```python
def lambda_handler(event, context):
    """
    List all boat registrations with combined license status.
    """
    # ... existing code to fetch boats ...
    
    # Add crew_license_status to each boat
    for boat in boats:
        boat['crew_license_status'] = calculate_crew_license_status(boat)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'boats': boats
        })
    }
```

### Response Schema

**Modified Response:**
```json
{
  "boats": [
    {
      "boat_registration_id": "uuid",
      "team_manager_id": "uuid",
      "event_type": "42km",
      "boat_type": "8+",
      "seats": [
        {
          "position": 1,
          "type": "rower",
          "crew_member_id": "uuid",
          "crew_member_first_name": "John",
          "crew_member_last_name": "Doe",
          "crew_member_license_verification_status": "verified_valid"
        },
        {
          "position": 2,
          "type": "rower",
          "crew_member_id": "uuid",
          "crew_member_first_name": "Jane",
          "crew_member_last_name": "Smith",
          "crew_member_license_verification_status": null
        }
      ],
      "crew_license_status": "invalid",
      "registration_status": "complete",
      "boat_number": "42-001",
      "race_id": "uuid",
      "team_manager_name": "Manager Name",
      "boat_club_display": "Club Name"
    }
  ]
}
```

### Calculation Examples

**Example 1: All Verified**
```python
seats = [
    {"crew_member_id": "1", "crew_member_license_verification_status": "verified_valid"},
    {"crew_member_id": "2", "crew_member_license_verification_status": "manually_verified_valid"},
    {"crew_member_id": "3", "crew_member_license_verification_status": "verified_valid"}
]
# Result: 'verified'
```

**Example 2: One Unverified**
```python
seats = [
    {"crew_member_id": "1", "crew_member_license_verification_status": "verified_valid"},
    {"crew_member_id": "2", "crew_member_license_verification_status": null},
    {"crew_member_id": "3", "crew_member_license_verification_status": "verified_valid"}
]
# Result: 'invalid'
```

**Example 3: No Crew**
```python
seats = [
    {"position": 1, "type": "rower"},
    {"position": 2, "type": "rower"}
]
# Result: None
```

**Example 4: One Invalid**
```python
seats = [
    {"crew_member_id": "1", "crew_member_license_verification_status": "verified_valid"},
    {"crew_member_id": "2", "crew_member_license_verification_status": "verified_invalid"}
]
# Result: 'invalid'
```

## Frontend Implementation

### AdminBoats.vue Changes

#### 1. Add License Column to Table

**Location:** `tableColumns` computed property

```javascript
const tableColumns = computed(() => [
  // ... existing columns ...
  {
    key: 'boat_club_display',
    label: t('admin.boats.club'),
    sortable: true,
    minWidth: '100px',
    responsive: 'always'
  },
  // NEW: License column
  {
    key: 'crew_license_status',
    label: t('admin.boats.licenseStatus'),
    sortable: false,
    width: '120px',
    align: 'center',
    responsive: 'always'
  },
  {
    key: 'status',
    label: t('boat.status.label'),
    sortable: false,
    width: '100px',
    align: 'center',
    responsive: 'always'
  },
  // ... remaining columns ...
])
```

#### 2. Add Template Slot for License Column

**Location:** SortableTable template slots

```vue
<!-- Custom cell: License Status -->
<template #cell-crew_license_status="{ row }">
  <span v-if="row._original.crew_license_status === 'verified'" 
        class="verification-badge verification-valid">
    {{ $t('admin.boats.verified') }}
  </span>
  <span v-else-if="row._original.crew_license_status === 'invalid'" 
        class="verification-badge verification-invalid">
    {{ $t('admin.boats.invalid') }}
  </span>
  <span v-else class="no-race-text">-</span>
</template>
```

#### 3. Add License Status to Card View

**Location:** Card view boat details section

```vue
<div class="boat-details">
  <!-- ... existing detail rows ... -->
  
  <div class="detail-row">
    <span class="label">{{ $t('admin.boats.club') }}&nbsp;:</span>
    <span class="club-box">{{ boat.boat_club_display }}</span>
  </div>
  
  <!-- NEW: License status row -->
  <div class="detail-row">
    <span class="label">{{ $t('admin.boats.licenseStatus') }}&nbsp;:</span>
    <span v-if="boat.crew_license_status === 'verified'" 
          class="verification-badge verification-valid">
      {{ $t('admin.boats.verified') }}
    </span>
    <span v-else-if="boat.crew_license_status === 'invalid'" 
          class="verification-badge verification-invalid">
      {{ $t('admin.boats.invalid') }}
    </span>
    <span v-else class="no-race-text">-</span>
  </div>
  
  <!-- ... remaining detail rows ... -->
</div>
```

#### 4. Add Badge Styles

**Location:** `<style scoped>` section

```css
/* License Verification Badge Styles */
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

### Internationalization

#### English Translations

**File:** `frontend/src/locales/en.json`

```json
{
  "admin": {
    "boats": {
      "licenseStatus": "License",
      "verified": "Verified",
      "invalid": "Invalid"
    }
  }
}
```

#### French Translations

**File:** `frontend/src/locales/fr.json`

```json
{
  "admin": {
    "boats": {
      "licenseStatus": "Licence",
      "verified": "Vérifié",
      "invalid": "Invalide"
    }
  }
}
```

## Testing Strategy

### Backend Tests

**File:** `tests/integration/test_admin_boat_license_status.py`

```python
import pytest
from functions.admin.admin_list_all_boats import calculate_crew_license_status

def test_all_verified_crew():
    """Test boat with all verified crew returns 'verified'."""
    boat = {
        'seats': [
            {'crew_member_id': '1', 'crew_member_license_verification_status': 'verified_valid'},
            {'crew_member_id': '2', 'crew_member_license_verification_status': 'manually_verified_valid'}
        ]
    }
    assert calculate_crew_license_status(boat) == 'verified'

def test_one_unverified_crew():
    """Test boat with one unverified crew returns 'invalid'."""
    boat = {
        'seats': [
            {'crew_member_id': '1', 'crew_member_license_verification_status': 'verified_valid'},
            {'crew_member_id': '2', 'crew_member_license_verification_status': None}
        ]
    }
    assert calculate_crew_license_status(boat) == 'invalid'

def test_one_invalid_crew():
    """Test boat with one invalid crew returns 'invalid'."""
    boat = {
        'seats': [
            {'crew_member_id': '1', 'crew_member_license_verification_status': 'verified_valid'},
            {'crew_member_id': '2', 'crew_member_license_verification_status': 'verified_invalid'}
        ]
    }
    assert calculate_crew_license_status(boat) == 'invalid'

def test_no_crew_assigned():
    """Test boat with no crew assigned returns None."""
    boat = {
        'seats': [
            {'position': 1, 'type': 'rower'},
            {'position': 2, 'type': 'rower'}
        ]
    }
    assert calculate_crew_license_status(boat) is None

def test_empty_seats():
    """Test boat with empty seats array returns None."""
    boat = {'seats': []}
    assert calculate_crew_license_status(boat) is None

def test_no_seats_key():
    """Test boat with no seats key returns None."""
    boat = {}
    assert calculate_crew_license_status(boat) is None

def test_mixed_manual_auto_verified():
    """Test boat with mixed manual and auto verified crew returns 'verified'."""
    boat = {
        'seats': [
            {'crew_member_id': '1', 'crew_member_license_verification_status': 'verified_valid'},
            {'crew_member_id': '2', 'crew_member_license_verification_status': 'manually_verified_valid'},
            {'crew_member_id': '3', 'crew_member_license_verification_status': 'verified_valid'}
        ]
    }
    assert calculate_crew_license_status(boat) == 'verified'
```

### Frontend Manual Testing

**Test Checklist:**

1. **Table View - Verified Status**
   - [ ] Load admin boats page
   - [ ] Find boat with all verified crew
   - [ ] Verify "License" column shows green "Verified" badge
   - [ ] Verify badge styling matches crew member list

2. **Table View - Invalid Status**
   - [ ] Find boat with unverified crew
   - [ ] Verify "License" column shows red "Invalid" badge
   - [ ] Verify badge styling is consistent

3. **Table View - No Crew**
   - [ ] Find boat with no crew assigned
   - [ ] Verify "License" column shows "-"
   - [ ] Verify grey text styling

4. **Card View - All Statuses**
   - [ ] Switch to card view
   - [ ] Verify license status appears in card details
   - [ ] Verify same badge logic as table view
   - [ ] Verify positioning after club field

5. **Responsive Behavior**
   - [ ] Test on mobile device
   - [ ] Verify column is visible on small screens
   - [ ] Verify card view works on mobile

6. **Data Updates**
   - [ ] Verify crew member license
   - [ ] Refresh boat list
   - [ ] Verify boat license status updates

7. **Edge Cases**
   - [ ] Test with 8+ crew boat
   - [ ] Test with boat containing coxswain
   - [ ] Test with partially filled boat

## Error Handling

### Backend Errors

No new error cases - calculation is defensive:
- Missing `seats` key → returns `None`
- Empty `seats` array → returns `None`
- Missing `crew_member_license_verification_status` → treated as unverified

### Frontend Errors

No new error handling needed:
- Missing `crew_license_status` field → displays "-" (null check)
- Invalid status value → displays "-" (else clause)

## Performance Considerations

### Backend Performance

**Calculation Complexity:** O(n) where n = number of seats per boat
- Single pass over seats array
- No additional database queries
- Minimal memory overhead

**Expected Impact:**
- Boats with 8 seats: ~8 comparisons per boat
- 100 boats: ~800 comparisons total
- Negligible performance impact (<1ms per boat)

### Frontend Performance

**Rendering:**
- One additional column in table
- One additional row in card view
- Minimal DOM elements added
- No JavaScript computation (status pre-calculated)

## Deployment Plan

### Phase 1: Backend
1. Modify `admin_list_all_boats.py`
2. Add `calculate_crew_license_status()` function
3. Update lambda handler to include status
4. Write and run backend tests
5. Deploy to dev environment
6. Test API response includes `crew_license_status`
7. Deploy to prod environment

### Phase 2: Frontend
1. Update `AdminBoats.vue` table columns
2. Add template slot for license column
3. Add license status to card view
4. Add badge styles
5. Add i18n translations (EN + FR)
6. Test in local development
7. Deploy to dev environment
8. Manual testing in dev
9. Deploy to prod environment

### Phase 3: Validation
1. Smoke test in production
2. Verify status accuracy
3. Verify badge styling
4. Verify responsive behavior
5. Monitor for errors

## Security Considerations

No new security concerns:
- Uses existing admin authentication
- No new permissions required
- No sensitive data exposed
- Read-only display (no actions)

## Monitoring and Logging

**CloudWatch Logs:**
- Log any errors in status calculation
- Monitor API response times

**Metrics:**
- Track percentage of boats with verified crew
- Track percentage of boats with invalid crew
- Track percentage of boats with no crew

## Future Enhancements (Out of Scope)

1. **Clickable badges** - Navigate to license checker filtered by boat
2. **Filter by license status** - Add filter dropdown
3. **Sort by license status** - Make column sortable
4. **Drill-down modal** - Show which crew members are unverified
5. **License expiration warnings** - Show upcoming expirations
6. **Bulk verification** - Verify all crew in a boat at once

## Correctness Properties

### Property 1: Status Accuracy
**Validates: Requirements US-1, FR-1**

For any boat with crew assigned:
- If ALL crew have `verified_valid` or `manually_verified_valid`, status MUST be `'verified'`
- If ANY crew has other status or null, status MUST be `'invalid'`
- If no crew assigned, status MUST be `null`

### Property 2: Display Consistency
**Validates: Requirements US-1, FR-3, FR-4**

For any boat displayed:
- Table view and card view MUST show same status
- Badge styling MUST match CrewMemberList.vue badges
- Status MUST update when crew verification changes

### Property 3: Performance
**Validates: Requirements NFR-1**

For any boat list request:
- Status calculation MUST complete in O(n) time
- No additional database queries MUST be made
- Response time MUST not increase by more than 100ms
