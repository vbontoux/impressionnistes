# Existing Permissions and Restrictions Analysis

## Current State

This document analyzes the existing permission and restriction logic in the Impressionnistes Registration System to inform the design of the centralized access control system.

## Backend Restrictions (Currently Implemented)

### 1. Crew Member Operations

**Location:** `functions/crew/delete_crew_member.py`, `functions/crew/update_crew_member.py`

**Current Restrictions:**
- ✅ **Cannot delete assigned crew member**: Checks `assigned_boat_id` field
  ```python
  if existing_crew.get('assigned_boat_id'):
      return conflict_error('Cannot delete crew member who is assigned to a boat...')
  ```
- ⚠️ **No date-based restrictions**: TODOs exist but not implemented
  ```python
  # TODO: Add registration period check when configuration is fully implemented
  # For now, allow updates
  ```

**What's Missing:**
- No check for registration period dates
- No check for payment deadline
- No temporary access grant support
- No impersonation bypass logic (exists in decorator but not date checks)

### 2. Boat Registration Operations

**Location:** `functions/boat/delete_boat_registration.py`, `functions/boat/update_boat_registration.py`

**Current Restrictions:**
- ✅ **Cannot delete paid boats**: Checks `registration_status == 'paid'`
  ```python
  if existing_boat.get('registration_status') == 'paid':
      return forbidden_error('Cannot delete a paid boat registration...')
  ```
- ✅ **Cannot update assigned boat fields (team managers)**: Explicit check
  ```python
  if 'assigned_boat_identifier' in body or 'assigned_boat_comment' in body:
      return forbidden_error('Only administrators can assign boats')
  ```
- ⚠️ **No date-based restrictions**: TODOs exist but not implemented
  ```python
  # TODO: Add registration period check when configuration is fully implemented
  # For now, allow updates
  ```

**What's Missing:**
- No check for registration period dates
- No check for payment deadline
- No temporary access grant support
- No impersonation bypass logic for dates

### 3. Admin Impersonation

**Location:** `functions/shared/auth_utils.py` (decorator: `@require_team_manager_or_admin_override`)

**Current Implementation:**
- ✅ Admin can impersonate team managers
- ✅ Sets `_is_admin_override` flag in event
- ✅ Audit logging for admin actions
- ⚠️ **But**: No special permission bypass logic - admins still hit the same TODOs

**What Works:**
- Impersonation detection and logging
- Admin can access team manager data

**What's Missing:**
- No automatic bypass of date restrictions during impersonation
- No special permission matrix for admins

### 4. Configuration System

**Location:** `functions/shared/configuration.py`, `functions/init/init_config.py`

**Current Implementation:**
- ✅ System configuration stored in DynamoDB (PK='CONFIG', SK='SYSTEM')
- ✅ Dates defined: `registration_start_date`, `registration_end_date`, `payment_deadline`
- ✅ Helper functions exist:
  - `get_registration_period()` - Returns start, end, payment_deadline
  - `is_payment_period_active()` - Checks if today is within payment period
- ⚠️ **But**: These functions are not used in Lambda handlers

**What Works:**
- Configuration storage and retrieval
- Date validation helpers

**What's Missing:**
- No enforcement of date restrictions in API handlers
- No event phase detection
- No permission matrix storage

## Frontend Restrictions (Currently Implemented)

### 1. Crew Member UI

**Location:** `frontend/src/components/CrewMemberCard.vue`, `CrewMemberList.vue`

**Current Implementation:**
- ✅ Visual indication of assigned crew members
  ```javascript
  const isAssigned = computed(() => !!props.crewMember.assigned_boat_id);
  ```
- ✅ Filtering by assignment status
- ⚠️ **But**: No disabled buttons based on assignment or dates

**What Works:**
- Display of assignment status
- Filtering capabilities

**What's Missing:**
- No disabled edit/delete buttons for assigned crew
- No date-based button disabling
- No tooltips explaining why actions are disabled

### 2. Boat Registration UI

**Location:** `frontend/src/components/BoatRegistrationForm.vue`, `SeatAssignment.vue`

**Current Implementation:**
- ✅ Read-only fields for admin-assigned boats
  ```vue
  <input :value="formData.assigned_boat_identifier" disabled class="form-input read-only" />
  ```
- ✅ Prevents assigning already-assigned crew members
  ```javascript
  if (member.assigned_boat_id && member.assigned_boat_id !== props.boatRegistrationId) {
    return false // Filter out
  }
  ```
- ⚠️ **But**: No date-based restrictions

**What Works:**
- Admin-only fields are read-only
- Seat assignment validation

**What's Missing:**
- No disabled buttons based on registration period
- No disabled buttons based on payment deadline
- No disabled buttons for paid boats
- No tooltips explaining restrictions

### 3. Payment UI

**Location:** Not yet analyzed (would need to check payment views)

**What's Missing:**
- No date-based payment button disabling
- No check for payment deadline

## Summary of Gaps

### Backend Gaps

1. **No date-based enforcement**: All TODOs for registration period checks
2. **No event phase detection**: No centralized function to determine current phase
3. **No permission matrix**: Rules are hardcoded in each Lambda
4. **No temporary access grants**: No database schema or logic
5. **Impersonation doesn't bypass dates**: Admin impersonation exists but doesn't help with date restrictions

### Frontend Gaps

1. **No disabled buttons**: All buttons are always enabled
2. **No date-based UI changes**: No awareness of registration phases
3. **No permission checking**: No composable or utility for checking permissions
4. **No user feedback**: No tooltips or messages explaining why actions might fail
5. **No synchronization with backend**: Frontend doesn't know about backend restrictions

## Recommendations for Centralized Access Control

### 1. Keep What Works

- ✅ Keep `assigned_boat_id` check for crew member deletion
- ✅ Keep `registration_status == 'paid'` check for boat deletion
- ✅ Keep admin impersonation infrastructure
- ✅ Keep configuration system and date storage

### 2. Centralize What's Scattered

- 🔄 Move all permission checks to a central `access_control.py` module
- 🔄 Create a permission matrix in configuration
- 🔄 Implement event phase detection
- 🔄 Add temporary access grant system

### 3. Add What's Missing

- ➕ Date-based restrictions (replace all TODOs)
- ➕ Frontend permission checking composable
- ➕ Button disabling based on permissions
- ➕ User-friendly error messages and tooltips
- ➕ Admin configuration UI for permissions

### 4. Integration Strategy

**Phase 1: Backend Foundation**
1. Create `access_control.py` with permission checking
2. Implement event phase detection
3. Add permission matrix to configuration
4. Replace all TODOs with permission checks

**Phase 2: Frontend Integration**
1. Create `usePermissions()` composable
2. Add button disabling logic
3. Add tooltips and messages
4. Sync with backend permission rules

**Phase 3: Admin Features**
1. Add temporary access grant UI
2. Add permission configuration UI
3. Add audit log viewing

## Existing Code to Modify

### Backend Files to Update

1. `functions/shared/access_control.py` - **CREATE NEW**
2. `functions/crew/delete_crew_member.py` - Replace TODO with permission check
3. `functions/crew/update_crew_member.py` - Replace TODO with permission check
4. `functions/crew/create_crew_member.py` - Add permission check
5. `functions/boat/delete_boat_registration.py` - Replace TODO with permission check
6. `functions/boat/update_boat_registration.py` - Replace TODO with permission check
7. `functions/boat/create_boat_registration.py` - Add permission check
8. `functions/payment/create_payment_intent.py` - Add permission check
9. `functions/init/init_config.py` - Add permission matrix initialization

### Frontend Files to Update

1. `frontend/src/composables/usePermissions.js` - **CREATE NEW**
2. `frontend/src/components/CrewMemberCard.vue` - Add disabled buttons
3. `frontend/src/components/CrewMemberList.vue` - Add disabled buttons
4. `frontend/src/components/BoatRegistrationCard.vue` - Add disabled buttons
5. `frontend/src/views/CrewMembers.vue` - Add disabled create button
6. `frontend/src/views/BoatRegistrations.vue` - Add disabled create button
7. `frontend/src/views/Payment.vue` - Add disabled payment button

### New Files to Create

1. `functions/shared/access_control.py` - Permission checking logic
2. `functions/admin/grant_temporary_access.py` - Grant temporary access
3. `functions/admin/revoke_temporary_access.py` - Revoke temporary access
4. `functions/admin/list_temporary_access_grants.py` - List active grants
5. `functions/admin/update_permission_config.py` - Update permission matrix
6. `frontend/src/composables/usePermissions.js` - Permission checking composable
7. `frontend/src/views/admin/PermissionConfig.vue` - Permission configuration UI
8. `frontend/src/views/admin/TemporaryAccessGrants.vue` - Temporary access management UI

## Conclusion

The existing system has:
- ✅ Good foundation (impersonation, configuration, data state checks)
- ⚠️ Incomplete implementation (TODOs everywhere)
- ❌ No centralization (rules scattered across files)
- ❌ No frontend enforcement (all buttons always enabled)

The centralized access control system will:
1. **Complete** the existing TODOs with proper date checks
2. **Centralize** all permission logic in one place
3. **Synchronize** backend and frontend restrictions
4. **Add** missing features (temporary access, admin config)
5. **Improve** user experience with clear feedback
