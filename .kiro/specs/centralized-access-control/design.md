# Design Document - Centralized Access Control System

## Overview

The Centralized Access Control System provides a unified permission management layer for the Course des Impressionnistes registration system. It determines which actions are permitted based on user role, impersonation status, event phases (dates), and data state, enforcing these rules consistently across both backend (API) and frontend (UI).

### Design Philosophy

1. **Single Source of Truth**: All permission rules defined in one centralized location
2. **Fail-Safe Defaults**: Deny by default, explicitly allow specific actions
3. **Layered Enforcement**: Backend enforces security, frontend provides UX
4. **Audit Everything**: Log all permission decisions for transparency
5. **Flexible Configuration**: Admins can adjust rules without code changes

### Key Design Decisions

**Decision 1: Permission Matrix in Database**
- **Rationale**: Allows runtime configuration changes without deployment
- **Trade-off**: Slightly more complex than hardcoded rules, but much more flexible
- **Implementation**: Store in DynamoDB CONFIG table, cache in memory

**Decision 2: Dual Backend/Frontend Enforcement**
- **Rationale**: Backend for security, frontend for user experience
- **Trade-off**: Must keep both in sync, but provides better UX
- **Implementation**: Shared permission logic, frontend calls backend for permission state

**Decision 3: Event Phase as Primary Dimension**
- **Rationale**: Most restrictions are time-based (registration period, payment deadline)
- **Trade-off**: Requires accurate system time and configuration
- **Implementation**: Calculate phase from current time + config dates


## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Vue)                        │
├─────────────────────────────────────────────────────────────┤
│  usePermissions() Composable                                 │
│  - canPerformAction(action, context)                         │
│  - getPermissionMessage(action, context)                     │
│  - getCurrentEventPhase()                                    │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP Requests
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway + Lambda                      │
├─────────────────────────────────────────────────────────────┤
│  Auth Decorator (@require_team_manager_or_admin_override)    │
│  - Extracts user context (role, impersonation)               │
│  - Passes to permission checker                              │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              Access Control Module (Python)                  │
├─────────────────────────────────────────────────────────────┤
│  PermissionChecker                                           │
│  - check_permission(user_ctx, action, resource_ctx)          │
│  - get_current_event_phase()                                 │
│  - evaluate_permission_matrix()                              │
│  - check_temporary_access_grant()                            │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                      DynamoDB Tables                         │
├─────────────────────────────────────────────────────────────┤
│  CONFIG#SYSTEM - Event dates                                 │
│  CONFIG#PERMISSIONS - Permission matrix                      │
│  TEMP_ACCESS#USER#{id} - Temporary access grants             │
│  AUDIT#PERMISSION_DENIAL - Audit logs                        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

**Permission Check Flow:**
1. User initiates action (click button, submit form)
2. Frontend checks permission via `usePermissions()` composable
3. If denied, button is disabled with tooltip
4. If allowed, request sent to backend
5. Backend decorator extracts user context
6. Backend calls `check_permission()` with full context
7. Permission checker evaluates rules and returns result
8. If denied, return HTTP 403 with reason
9. If allowed, execute operation and log action


## Components and Interfaces

### Backend Components

#### 1. PermissionChecker Class

**Location:** `functions/shared/access_control.py`

**Purpose:** Central permission evaluation engine

**Interface:**
```python
class PermissionChecker:
    def __init__(self, db_client):
        self.db = db_client
        self._permission_cache = {}
        self._config_cache = {}
        self._cache_ttl = 60  # seconds
    
    def check_permission(
        self,
        user_context: UserContext,
        action: str,
        resource_context: ResourceContext
    ) -> PermissionResult:
        """
        Check if an action is permitted.
        
        Args:
            user_context: User information (id, role, impersonation status)
            action: Action to perform (e.g., 'create_crew_member')
            resource_context: Resource information (type, state, data)
        
        Returns:
            PermissionResult with is_permitted and optional denial_reason
        """
        pass
    
    def get_current_event_phase(self) -> EventPhase:
        """
        Determine current event phase based on system time and config dates.
        
        Returns:
            EventPhase enum value
        """
        pass
    
    def get_permission_matrix(self) -> dict:
        """
        Retrieve permission matrix from database (with caching).
        
        Returns:
            Dictionary mapping actions to phase-based rules
        """
        pass
    
    def check_temporary_access_grant(self, user_id: str) -> bool:
        """
        Check if user has an active temporary access grant.
        
        Args:
            user_id: User ID to check
        
        Returns:
            True if active grant exists, False otherwise
        """
        pass
```


#### 2. Data Models

**UserContext:**
```python
@dataclass
class UserContext:
    user_id: str
    role: str  # 'admin' or 'team_manager'
    is_impersonating: bool
    has_temporary_access: bool
    team_manager_id: Optional[str]  # For impersonation
```

**ResourceContext:**
```python
@dataclass
class ResourceContext:
    resource_type: str  # 'crew_member', 'boat_registration', 'payment'
    resource_id: Optional[str]
    resource_state: dict  # e.g., {'assigned': True, 'paid': False}
```

**PermissionResult:**
```python
@dataclass
class PermissionResult:
    is_permitted: bool
    denial_reason: Optional[str]
    denial_reason_key: Optional[str]  # For i18n
    bypass_reason: Optional[str]  # 'impersonation' or 'temporary_access'
```

**EventPhase:**
```python
class EventPhase(Enum):
    BEFORE_REGISTRATION = "before_registration"
    DURING_REGISTRATION = "during_registration"
    AFTER_REGISTRATION = "after_registration"
    AFTER_PAYMENT_DEADLINE = "after_payment_deadline"
```

#### 3. Helper Functions

**Location:** `functions/shared/access_control.py`

```python
def require_permission(action: str):
    """
    Decorator for Lambda handlers to enforce permissions.
    
    Usage:
        @require_permission('create_crew_member')
        def lambda_handler(event, context):
            # Handler code
    """
    pass

def get_user_context_from_event(event: dict) -> UserContext:
    """Extract user context from Lambda event."""
    pass

def get_resource_context_from_body(body: dict, resource_type: str) -> ResourceContext:
    """Extract resource context from request body."""
    pass

def log_permission_denial(
    user_context: UserContext,
    action: str,
    resource_context: ResourceContext,
    reason: str
):
    """Log permission denial to DynamoDB audit table."""
    pass

def log_permission_grant_with_bypass(
    user_context: UserContext,
    action: str,
    resource_context: ResourceContext,
    bypass_reason: str
):
    """Log permission grant that used impersonation or temporary access."""
    pass
```


### Frontend Components

#### 1. usePermissions Composable

**Location:** `frontend/src/composables/usePermissions.js`

**Purpose:** Provide permission checking for Vue components

**Interface:**
```javascript
export function usePermissions() {
  // Reactive state
  const currentPhase = ref(null)
  const permissionMatrix = ref(null)
  const userContext = ref(null)
  const loading = ref(true)
  
  // Initialize permission state
  async function initialize() {
    await fetchCurrentPhase()
    await fetchPermissionMatrix()
    await fetchUserContext()
    loading.value = false
  }
  
  // Check if action is permitted
  function canPerformAction(action, resourceContext = {}) {
    if (loading.value) return false
    
    // Check event phase restrictions
    const phaseAllowed = checkPhasePermission(action, currentPhase.value)
    if (!phaseAllowed && !hasBypass()) return false
    
    // Check data state restrictions
    const stateAllowed = checkStatePermission(action, resourceContext)
    if (!stateAllowed) return false
    
    return true
  }
  
  // Get user-friendly message explaining why action is denied
  function getPermissionMessage(action, resourceContext = {}) {
    if (canPerformAction(action, resourceContext)) return null
    
    // Determine denial reason
    if (!checkPhasePermission(action, currentPhase.value)) {
      return getPhaseMessage(currentPhase.value)
    }
    
    if (!checkStatePermission(action, resourceContext)) {
      return getStateMessage(action, resourceContext)
    }
    
    return 'Action not permitted'
  }
  
  // Check if user has bypass (impersonation or temporary access)
  function hasBypass() {
    return userContext.value?.is_impersonating || 
           userContext.value?.has_temporary_access
  }
  
  // Get current event phase
  function getCurrentPhase() {
    return currentPhase.value
  }
  
  return {
    initialize,
    canPerformAction,
    getPermissionMessage,
    getCurrentPhase,
    hasBypass,
    loading
  }
}
```


#### 2. Component Integration Pattern

**Example: Crew Member Card with Permission Checks**

```vue
<template>
  <div class="crew-card">
    <h3>{{ crewMember.name }}</h3>
    
    <div class="actions">
      <BaseButton
        size="small"
        variant="secondary"
        :disabled="!canEdit"
        :title="editTooltip"
        @click="editCrewMember"
      >
        Edit
      </BaseButton>
      
      <BaseButton
        size="small"
        variant="danger"
        :disabled="!canDelete"
        :title="deleteTooltip"
        @click="deleteCrewMember"
      >
        Delete
      </BaseButton>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { usePermissions } from '@/composables/usePermissions'

const props = defineProps(['crewMember'])
const { canPerformAction, getPermissionMessage } = usePermissions()

const resourceContext = computed(() => ({
  resource_type: 'crew_member',
  resource_id: props.crewMember.crew_member_id,
  resource_state: {
    assigned: !!props.crewMember.assigned_boat_id
  }
}))

const canEdit = computed(() => 
  canPerformAction('edit_crew_member', resourceContext.value)
)

const canDelete = computed(() => 
  canPerformAction('delete_crew_member', resourceContext.value)
)

const editTooltip = computed(() => 
  canEdit.value ? '' : getPermissionMessage('edit_crew_member', resourceContext.value)
)

const deleteTooltip = computed(() => 
  canDelete.value ? '' : getPermissionMessage('delete_crew_member', resourceContext.value)
)
</script>
```


## Data Models

### Database Schema

#### 1. Permission Configuration

**Table:** Main DynamoDB table  
**PK:** `CONFIG`  
**SK:** `PERMISSIONS`

```json
{
  "PK": "CONFIG",
  "SK": "PERMISSIONS",
  "permissions": {
    "create_crew_member": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": false,
      "after_payment_deadline": false
    },
    "edit_crew_member": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": false,
      "after_payment_deadline": false,
      "requires_not_assigned": true
    },
    "delete_crew_member": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": false,
      "after_payment_deadline": false,
      "requires_not_assigned": true
    },
    "create_boat_registration": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": false,
      "after_payment_deadline": false
    },
    "edit_boat_registration": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": false,
      "after_payment_deadline": false,
      "requires_not_paid": true
    },
    "delete_boat_registration": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": false,
      "after_payment_deadline": false,
      "requires_not_paid": true
    },
    "process_payment": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": true,
      "after_payment_deadline": false
    },
    "view_data": {
      "before_registration": true,
      "during_registration": true,
      "after_registration": true,
      "after_payment_deadline": true
    },
    "export_data": {
      "before_registration": true,
      "during_registration": true,
      "after_registration": true,
      "after_payment_deadline": true
    }
  },
  "updated_at": "2026-01-14T10:00:00Z",
  "updated_by": "admin@example.com"
}
```


#### 2. Temporary Access Grant

**Table:** Main DynamoDB table  
**PK:** `TEMP_ACCESS`  
**SK:** `USER#{user_id}`

```json
{
  "PK": "TEMP_ACCESS",
  "SK": "USER#user-123",
  "user_id": "user-123",
  "grant_timestamp": "2026-01-14T10:00:00Z",
  "expiration_timestamp": "2026-01-16T10:00:00Z",
  "granted_by_admin_id": "admin-456",
  "status": "active",
  "revoked_at": null,
  "revoked_by_admin_id": null,
  "notes": "Requested by user to fix registration error"
}
```

**Status Values:**
- `active`: Grant is currently active
- `expired`: Grant has passed expiration_timestamp
- `revoked`: Grant was manually revoked by admin

**Indexes:**
- GSI on `status` for querying active grants
- TTL on `expiration_timestamp` for automatic cleanup

#### 3. Permission Denial Audit Log

**Table:** Main DynamoDB table  
**PK:** `AUDIT#PERMISSION_DENIAL`  
**SK:** `{timestamp}#{user_id}`

```json
{
  "PK": "AUDIT#PERMISSION_DENIAL",
  "SK": "2026-01-14T10:00:00.123Z#user-123",
  "user_id": "user-123",
  "action": "edit_crew_member",
  "resource_type": "crew_member",
  "resource_id": "crew-789",
  "denial_reason": "after_registration_closed",
  "denial_reason_key": "errors.registration_closed",
  "event_phase": "after_registration",
  "timestamp": "2026-01-14T10:00:00.123Z",
  "user_agent": "Mozilla/5.0...",
  "ip_address": "192.168.1.1"
}
```

#### 4. Permission Grant with Bypass Audit Log

**Table:** Main DynamoDB table  
**PK:** `AUDIT#PERMISSION_BYPASS`  
**SK:** `{timestamp}#{user_id}`

```json
{
  "PK": "AUDIT#PERMISSION_BYPASS",
  "SK": "2026-01-14T10:00:00.123Z#admin-456",
  "user_id": "admin-456",
  "action": "edit_crew_member",
  "resource_type": "crew_member",
  "resource_id": "crew-789",
  "bypass_reason": "impersonation",
  "impersonated_user_id": "user-123",
  "event_phase": "after_registration",
  "timestamp": "2026-01-14T10:00:00.123Z"
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Event Phase Determination is Consistent

*For any* system time and configuration dates, calling `get_current_event_phase()` multiple times within a short period (< cache TTL) should return the same event phase.

**Validates: Requirements 1.1, 1.3**

**Rationale:** Event phase should be deterministic based on time and configuration. Caching ensures consistency within a request lifecycle.

### Property 2: Permission Denial is Logged

*For any* permission check that returns `is_permitted=False`, an audit log entry should be created in the database with the denial reason.

**Validates: Requirements 12.1**

**Rationale:** All denials must be auditable for security and debugging purposes.

### Property 3: Impersonation Bypasses All Restrictions

*For any* action attempted by an admin in impersonation mode, the action should be allowed regardless of event phase or data state restrictions.

**Validates: Requirements 4.1, 4.2**

**Rationale:** Admins using impersonation are trusted to make any necessary changes to help users, including modifying assigned crew members and paid boats.

### Property 4: Temporary Access Grant Bypasses Phase Restrictions Only

*For any* action attempted by a user with an active temporary access grant, if the action is denied due to event phase, it should be allowed; if denied due to data state, it should still be denied.

**Validates: Requirements 5.3, 5.4**

**Rationale:** Temporary access grants are for exceptional cases but should not compromise data integrity.

### Property 5: Expired Grants Do Not Provide Access

*For any* temporary access grant where current time > expiration_timestamp, the grant should not bypass any restrictions.

**Validates: Requirements 5.5**

**Rationale:** Grants must have time limits to prevent indefinite access.

### Property 6: Permission Matrix Consistency

*For any* action in the permission matrix, if it is allowed in phase X, and a user attempts it in phase X with no data state restrictions, the permission check should return `is_permitted=True`.

**Validates: Requirements 6.4, 6.5**

**Rationale:** The permission matrix should be the authoritative source for phase-based permissions.


### Property 7: Data State Restrictions Apply to Non-Impersonating Users

*For any* user who is NOT an admin using impersonation, if a crew member is assigned to a boat, attempts to edit or delete that crew member should be denied.

**Validates: Requirements 3.1, 3.2, 5.4**

**Rationale:** Data integrity rules apply to team managers and users with temporary access, but admins with impersonation get full override.

### Property 8: Paid Boat Restrictions Apply to Non-Impersonating Users

*For any* user who is NOT an admin using impersonation, if a boat registration has status "paid", attempts to edit or delete that boat should be denied.

**Validates: Requirements 3.3, 3.4, 5.4**

**Rationale:** Paid boats are immutable for team managers to protect financial records, but admins with impersonation can modify them if needed.

### Property 9: Backend and Frontend Permission Alignment

*For any* action and context, if the backend `check_permission()` returns `is_permitted=False`, the frontend `canPerformAction()` should also return `false` for the same action and context.

**Validates: Requirements 7.8, 8.12**

**Rationale:** Frontend and backend must enforce the same rules to provide consistent UX and security.

### Property 10: Permission Cache Invalidation

*For any* permission configuration update, subsequent permission checks should reflect the new configuration within the cache TTL period.

**Validates: Requirements 1.3, 9.9, 11.9**

**Rationale:** Configuration changes must take effect promptly without requiring system restart.

### Property 11: Audit Log Completeness

*For any* action performed with impersonation or temporary access bypass, an audit log entry should be created with the bypass reason.

**Validates: Requirements 4.3, 5.9, 12.2, 12.3**

**Rationale:** All privileged actions must be auditable for security and compliance.


## Error Handling

### Backend Error Responses

**Permission Denied (HTTP 403):**
```json
{
  "error": "Permission denied",
  "reason": "after_registration_closed",
  "reason_key": "errors.registration_closed",
  "message": "La période d'inscription est terminée. Contactez l'organisation pour toute modification.",
  "message_en": "Registration period has ended. Contact the organization for any changes.",
  "event_phase": "after_registration",
  "action": "edit_crew_member"
}
```

**Configuration Error (HTTP 500):**
```json
{
  "error": "Configuration error",
  "message": "Unable to determine event phase. System configuration may be incomplete.",
  "details": "Missing registration_start_date in configuration"
}
```

**Temporary Access Grant Expired (HTTP 403):**
```json
{
  "error": "Permission denied",
  "reason": "temporary_access_expired",
  "reason_key": "errors.temporary_access_expired",
  "message": "Votre accès temporaire a expiré. Contactez un administrateur.",
  "message_en": "Your temporary access has expired. Contact an administrator.",
  "expired_at": "2026-01-16T10:00:00Z"
}
```

### Frontend Error Handling

**Permission Check Failures:**
- Display disabled buttons with tooltips explaining why
- Show MessageAlert with clear explanation when API returns 403
- Provide contact information for users to request help

**Network Errors:**
- Gracefully degrade to "deny all" if permission check fails
- Show error message indicating system issue
- Allow retry of permission check

**Configuration Errors:**
- Log to console for debugging
- Display generic error message to user
- Notify admins via monitoring system


### Error Recovery Strategies

**Scenario 1: Permission Matrix Missing**
- **Detection:** `get_permission_matrix()` returns None
- **Recovery:** Initialize default permissions from code
- **Action:** Log warning, notify admins
- **User Impact:** System continues with safe defaults

**Scenario 2: Event Phase Cannot Be Determined**
- **Detection:** Configuration dates are missing or invalid
- **Recovery:** Default to most restrictive phase (after_payment_deadline)
- **Action:** Log error, notify admins immediately
- **User Impact:** All modifications blocked until fixed

**Scenario 3: Temporary Access Grant Query Fails**
- **Detection:** DynamoDB query throws exception
- **Recovery:** Assume no temporary access (fail-safe)
- **Action:** Log error, retry once
- **User Impact:** User may be denied access they should have

**Scenario 4: Audit Log Write Fails**
- **Detection:** DynamoDB put_item throws exception
- **Recovery:** Log to CloudWatch, continue operation
- **Action:** Retry audit log write asynchronously
- **User Impact:** None (operation proceeds)


## Testing Strategy

### Unit Tests

**Backend Unit Tests** (`functions/shared/test_access_control.py`):
- Test event phase calculation with various date configurations
- Test permission matrix evaluation for each action and phase
- Test temporary access grant validation (active, expired, revoked)
- Test data state restriction checks (assigned crew, paid boat)
- Test impersonation bypass logic
- Test error handling for missing configuration
- Test cache behavior and invalidation

**Frontend Unit Tests** (`frontend/src/composables/usePermissions.test.js`):
- Test `canPerformAction()` with various contexts
- Test `getPermissionMessage()` returns correct messages
- Test phase detection and caching
- Test bypass detection (impersonation, temporary access)
- Test error handling for API failures

### Property-Based Tests

**Property Test 1: Event Phase Consistency**
- **Property:** Event phase determination is consistent
- **Generator:** Random system times and configuration dates
- **Test:** Call `get_current_event_phase()` multiple times, verify same result
- **Validates:** Property 1

**Property Test 2: Permission Denial Logging**
- **Property:** All denials are logged
- **Generator:** Random actions, users, and contexts that should be denied
- **Test:** Check permission, verify audit log entry exists
- **Validates:** Property 2

**Property Test 3: Impersonation Bypass Rules**
- **Property:** Impersonation bypasses phase but not data state
- **Generator:** Random actions with phase and data state restrictions
- **Test:** Verify phase restrictions bypassed, data state restrictions enforced
- **Validates:** Property 3

**Property Test 4: Temporary Access Bypass Rules**
- **Property:** Temporary access bypasses phase but not data state
- **Generator:** Random actions with active grants
- **Test:** Verify phase restrictions bypassed, data state restrictions enforced
- **Validates:** Property 4

**Property Test 5: Expired Grant Denial**
- **Property:** Expired grants provide no access
- **Generator:** Random grants with expiration in the past
- **Test:** Verify no bypass occurs
- **Validates:** Property 5

**Property Test 6: Permission Matrix Consistency**
- **Property:** Matrix rules are followed
- **Generator:** Random actions and phases from matrix
- **Test:** Verify permission check matches matrix definition
- **Validates:** Property 6


**Property Test 7: Data State Restrictions Universal**
- **Property:** Data state restrictions apply to all users
- **Generator:** Random users (admin, manager, impersonating) with assigned crew/paid boats
- **Test:** Verify all attempts to modify are denied
- **Validates:** Property 7, 8

**Property Test 8: Backend-Frontend Alignment**
- **Property:** Backend and frontend return same permission results
- **Generator:** Random actions and contexts
- **Test:** Call both backend and frontend permission checks, verify alignment
- **Validates:** Property 9

**Property Test 9: Configuration Cache Invalidation**
- **Property:** Config changes take effect within TTL
- **Generator:** Random permission matrix updates
- **Test:** Update config, verify new rules applied after cache expires
- **Validates:** Property 10

**Property Test 10: Audit Log Completeness**
- **Property:** All bypass actions are logged
- **Generator:** Random actions with impersonation or temporary access
- **Test:** Verify audit log entry with bypass reason exists
- **Validates:** Property 11

### Integration Tests

**Integration Test 1: End-to-End Permission Flow**
- Create crew member during registration period → Success
- Attempt to create crew member after registration closes → Denied
- Admin impersonates and creates crew member → Success with audit log
- Verify frontend buttons disabled after registration closes

**Integration Test 2: Temporary Access Grant Lifecycle**
- Admin grants temporary access to user
- User creates crew member outside registration period → Success
- Grant expires
- User attempts to create crew member → Denied
- Verify audit logs for all actions

**Integration Test 3: Data State Restrictions**
- Create crew member and boat registration
- Assign crew member to boat
- Attempt to edit assigned crew member → Denied
- Unassign crew member
- Edit crew member → Success
- Pay for boat
- Attempt to edit boat → Denied

**Integration Test 4: Permission Configuration Changes**
- Admin updates permission matrix
- Verify new rules take effect immediately
- Verify frontend reflects new permissions
- Verify audit log of configuration change


### Test Configuration

**Property-Based Test Library:** Python's `hypothesis` library for backend tests

**Test Iterations:** Minimum 100 iterations per property test

**Test Tagging:** Each property test must reference its design property:
```python
# Feature: centralized-access-control, Property 1: Event phase determination is consistent
@given(st.datetimes(), st.datetimes(), st.datetimes())
def test_event_phase_consistency(current_time, start_date, end_date):
    # Test implementation
    pass
```

**Coverage Goals:**
- Backend: 90% code coverage for access_control.py
- Frontend: 85% code coverage for usePermissions.js
- Integration: All critical user flows covered


## Implementation Details

### Backend Implementation

#### Phase 1: Core Permission Module

**File:** `functions/shared/access_control.py`

**Key Classes and Functions:**
1. `PermissionChecker` class with caching
2. `get_current_event_phase()` function
3. `check_permission()` function
4. `require_permission()` decorator
5. Helper functions for context extraction

**Integration Points:**
- Modify existing Lambda handlers to use `@require_permission` decorator
- Replace all TODO comments with permission checks
- Update `auth_utils.py` to pass impersonation context

#### Phase 2: Database Schema

**Configuration Initialization:**
- Update `functions/init/init_config.py` to create default permission matrix
- Add migration script to populate permissions for existing deployments

**Temporary Access Grant Schema:**
- Add GSI on status field for querying active grants
- Add TTL attribute for automatic cleanup of expired grants

**Audit Log Schema:**
- Add indexes for querying by user, action, and date range
- Configure retention policy (1 year default)

#### Phase 3: Admin APIs

**New Lambda Functions:**
1. `functions/admin/grant_temporary_access.py`
2. `functions/admin/revoke_temporary_access.py`
3. `functions/admin/list_temporary_access_grants.py`
4. `functions/admin/update_permission_config.py`
5. `functions/admin/get_permission_audit_logs.py`

**API Endpoints:**
- `POST /admin/temporary-access/grant`
- `POST /admin/temporary-access/revoke`
- `GET /admin/temporary-access/list`
- `PUT /admin/permissions/config`
- `GET /admin/permissions/audit-logs`


### Frontend Implementation

#### Phase 1: Permission Composable

**File:** `frontend/src/composables/usePermissions.js`

**Features:**
- Reactive permission state
- Caching of permission checks
- Automatic refresh on configuration changes
- Integration with auth store for user context

**API Integration:**
- Call backend `/api/permissions/check` endpoint
- Call backend `/api/permissions/current-phase` endpoint
- Cache results for 60 seconds

#### Phase 2: Component Updates

**Files to Update:**
- `frontend/src/components/CrewMemberCard.vue`
- `frontend/src/components/CrewMemberList.vue`
- `frontend/src/components/BoatRegistrationCard.vue`
- `frontend/src/components/BoatRegistrationList.vue`
- `frontend/src/views/CrewMembers.vue`
- `frontend/src/views/BoatRegistrations.vue`
- `frontend/src/views/Payment.vue`

**Changes:**
- Add `usePermissions()` composable
- Compute `canEdit`, `canDelete`, `canCreate` based on permissions
- Add `:disabled` bindings to buttons
- Add `:title` tooltips with permission messages
- Show phase-specific messages to users

#### Phase 3: Admin UI

**New Components:**
1. `frontend/src/views/admin/PermissionConfig.vue` - Permission matrix editor
2. `frontend/src/views/admin/TemporaryAccessGrants.vue` - Grant management
3. `frontend/src/views/admin/PermissionAuditLogs.vue` - Audit log viewer
4. `frontend/src/components/admin/PermissionMatrixTable.vue` - Editable matrix
5. `frontend/src/components/admin/TemporaryAccessGrantForm.vue` - Grant creation form

**Features:**
- Visual permission matrix editor with checkboxes
- Temporary access grant creation with expiration picker
- Active grants list with revoke buttons
- Audit log viewer with filters (user, action, date range)
- Real-time updates when permissions change


### Caching Strategy

**Backend Caching:**
- Permission matrix: 60 seconds in-memory cache
- Event phase: 60 seconds in-memory cache
- Temporary access grants: No caching (always fresh from DB)
- Cache invalidation on configuration updates

**Frontend Caching:**
- Permission state: 60 seconds in composable
- Event phase: 60 seconds in composable
- User context: Session duration (until logout)
- Automatic refresh on visibility change

**Cache Invalidation:**
- Backend: Explicit cache clear on config update
- Frontend: Polling every 60 seconds for phase changes
- Frontend: WebSocket notification for config changes (future enhancement)

### Performance Considerations

**Backend:**
- Permission checks add ~5-10ms per request (cached)
- First check after cache expiry: ~50-100ms (DB query)
- Audit logging is asynchronous (no user-facing delay)

**Frontend:**
- Initial permission load: ~100-200ms
- Subsequent checks: <1ms (in-memory)
- Button state updates: Reactive, no manual refresh needed

**Optimization:**
- Batch permission checks for list views
- Pre-fetch permissions on page load
- Use DynamoDB batch operations for audit logs


## Security Considerations

### Threat Model

**Threat 1: Unauthorized Access via Frontend Bypass**
- **Attack:** User modifies frontend code to enable disabled buttons
- **Mitigation:** Backend always validates permissions, frontend is UX only
- **Impact:** Attack fails at backend, logged in audit trail

**Threat 2: Permission Configuration Tampering**
- **Attack:** Attacker modifies permission matrix in database
- **Mitigation:** Only admins can update config, all changes logged
- **Impact:** Audit trail shows who made changes, can be reverted

**Threat 3: Temporary Access Grant Abuse**
- **Attack:** Admin grants indefinite access or grants to wrong user
- **Mitigation:** Grants have expiration, all grants logged with admin ID
- **Impact:** Grants expire automatically, abuse is auditable

**Threat 4: Impersonation Abuse**
- **Attack:** Admin uses impersonation to bypass all restrictions and corrupt data
- **Mitigation:** All impersonation actions logged with admin ID, can be audited and reverted
- **Impact:** Admin accountability through audit trail, changes can be rolled back

**Threat 5: Time-Based Attack (Clock Manipulation)**
- **Attack:** User manipulates system clock to bypass date restrictions
- **Mitigation:** Backend uses server time, not client time
- **Impact:** Attack fails, client time is irrelevant

### Security Best Practices

1. **Defense in Depth:** Backend enforces security, frontend provides UX
2. **Fail-Safe Defaults:** Deny by default, explicitly allow actions
3. **Audit Everything:** Log all permission decisions and privileged actions
4. **Least Privilege:** Users only get permissions they need
5. **Time-Limited Access:** Temporary grants expire automatically
6. **Admin Accountability:** All admin actions logged with user ID, full audit trail
7. **Trusted Admins:** Admins with impersonation have full access, trusted to make correct decisions


## Migration Strategy

### Phase 1: Backend Foundation (Week 1)

**Goals:**
- Create access_control.py module
- Implement event phase detection
- Add permission matrix to configuration
- Write unit tests

**Deliverables:**
- `functions/shared/access_control.py` with core logic
- Updated `functions/init/init_config.py` with default permissions
- Unit tests with 90% coverage

**Risk:** None (new code, no existing functionality affected)

### Phase 2: Backend Integration (Week 2)

**Goals:**
- Add `@require_permission` decorator to Lambda handlers
- Replace all TODO comments with permission checks
- Add temporary access grant APIs
- Write integration tests

**Deliverables:**
- All Lambda handlers use permission checks
- Temporary access grant CRUD APIs
- Integration tests for permission flows

**Risk:** Medium (modifying existing handlers, requires thorough testing)

**Mitigation:** Deploy to dev environment first, test all user flows

### Phase 3: Frontend Integration (Week 3)

**Goals:**
- Create usePermissions composable
- Update all components with disabled buttons
- Add tooltips and messages
- Write frontend tests

**Deliverables:**
- `frontend/src/composables/usePermissions.js`
- All components use permission checks
- Frontend unit tests

**Risk:** Low (frontend changes are UX improvements, backend still enforces)

### Phase 4: Admin UI (Week 4)

**Goals:**
- Create permission configuration UI
- Create temporary access grant UI
- Create audit log viewer
- End-to-end testing

**Deliverables:**
- Admin permission management pages
- Complete documentation
- User training materials

**Risk:** Low (admin-only features, can be rolled back easily)


### Rollback Plan

**If Issues Arise:**

1. **Backend Issues:**
   - Revert Lambda function deployments
   - Restore previous version from Git
   - Permission checks fail-open (allow all) in emergency mode

2. **Frontend Issues:**
   - Revert frontend deployment
   - Buttons remain enabled (backend still enforces)
   - Users see backend error messages

3. **Configuration Issues:**
   - Restore previous permission matrix from backup
   - Reset to default permissions
   - Disable permission checking temporarily

**Emergency Mode:**
- Environment variable: `DISABLE_PERMISSION_CHECKS=true`
- Logs warning on every request
- Allows all actions (backend only validates data state)
- Only for critical production issues

### Monitoring and Alerts

**Metrics to Track:**
- Permission denial rate (should be low after registration closes)
- Permission check latency (should be <10ms)
- Cache hit rate (should be >95%)
- Audit log write failures (should be 0)
- Configuration load failures (should be 0)

**Alerts:**
- Permission check latency >100ms
- Cache hit rate <80%
- Audit log write failure rate >1%
- Configuration missing or invalid
- Unusual spike in permission denials

**Dashboards:**
- Permission denials by action and phase
- Temporary access grants (active, expired, revoked)
- Impersonation usage by admin
- Permission check performance


## Future Enhancements

### Phase 5: Advanced Features (Future)

**1. Role-Based Access Control (RBAC)**
- Add more granular roles (e.g., "race_organizer", "treasurer")
- Define permissions per role
- Allow multiple roles per user

**2. Resource-Level Permissions**
- Club-specific permissions (manager can only edit their club's data)
- Boat-specific permissions (only boat owner can edit)
- Race-specific permissions (different rules per race type)

**3. Real-Time Permission Updates**
- WebSocket notifications for permission changes
- Instant UI updates without polling
- Push notifications for temporary access grants

**4. Permission Delegation**
- Team managers can delegate permissions to assistants
- Time-limited delegation
- Audit trail of delegations

**5. Advanced Audit Features**
- Export audit logs to CSV
- Audit log analytics dashboard
- Anomaly detection for suspicious patterns

**6. Self-Service Temporary Access**
- Users can request temporary access
- Admins approve/deny requests via email
- Automatic expiration after use

**7. Permission Testing Mode**
- Admins can test permission changes before applying
- Preview mode shows what would be allowed/denied
- Rollback to previous configuration

**8. Multi-Language Support**
- Permission messages in French and English
- Admin UI in multiple languages
- Configurable default language


## Appendix A: Permission Matrix Reference

### Default Permission Rules

| Action | Before Registration | During Registration | After Registration | After Payment Deadline |
|--------|-------------------|-------------------|------------------|---------------------|
| **Crew Member Operations** |
| create_crew_member | ❌ | ✅ | ❌ | ❌ |
| edit_crew_member | ❌ | ✅ (not assigned) | ❌ | ❌ |
| delete_crew_member | ❌ | ✅ (not assigned) | ❌ | ❌ |
| **Boat Registration Operations** |
| create_boat_registration | ❌ | ✅ | ❌ | ❌ |
| edit_boat_registration | ❌ | ✅ (not paid) | ❌ | ❌ |
| delete_boat_registration | ❌ | ✅ (not paid) | ❌ | ❌ |
| **Payment Operations** |
| process_payment | ❌ | ✅ | ✅ | ❌ |
| **Read Operations** |
| view_data | ✅ | ✅ | ✅ | ✅ |
| export_data | ✅ | ✅ | ✅ | ✅ |

### Bypass Rules

**Admin Impersonation:**
- Bypasses: All event phase restrictions AND all data state restrictions
- Still enforces: Nothing (full override)
- Logged: Yes, with impersonation flag

**Temporary Access Grant:**
- Bypasses: All event phase restrictions
- Still enforces: Data state restrictions (assigned crew, paid boats)
- Logged: Yes, with grant ID

**Data State Restrictions (Apply to non-impersonating users only):**
- Cannot edit/delete assigned crew members
- Cannot edit/delete paid boat registrations
- Applies to: Team managers and users with temporary access grants
- Does NOT apply to: Admins using impersonation


## Appendix B: Error Message Reference

### French Messages

| Scenario | Message |
|----------|---------|
| Before registration | "Les inscriptions ne sont pas encore ouvertes. Ouverture le {date}." |
| After registration closed | "La période d'inscription est terminée. Contactez l'organisation pour toute modification." |
| After payment deadline | "La date limite de paiement est dépassée. Contactez l'organisation." |
| Crew member assigned | "Impossible de modifier un équipier assigné. Désassignez-le d'abord de l'équipage." |
| Boat paid | "Impossible de modifier un équipage payé. Contactez l'organisation." |
| Temporary access expired | "Votre accès temporaire a expiré. Contactez un administrateur." |

### English Messages

| Scenario | Message |
|----------|---------|
| Before registration | "Registration is not yet open. Opens on {date}." |
| After registration closed | "Registration period has ended. Contact the organization for any changes." |
| After payment deadline | "Payment deadline has passed. Contact the organization." |
| Crew member assigned | "Cannot edit an assigned crew member. Unassign from boat first." |
| Boat paid | "Cannot edit a paid boat registration. Contact the organization." |
| Temporary access expired | "Your temporary access has expired. Contact an administrator." |

### Message Keys (i18n)

```javascript
// frontend/src/locales/en.json
{
  "errors": {
    "registration_not_open": "Registration is not yet open. Opens on {date}.",
    "registration_closed": "Registration period has ended. Contact the organization for any changes.",
    "payment_deadline_passed": "Payment deadline has passed. Contact the organization.",
    "crew_member_assigned": "Cannot edit an assigned crew member. Unassign from boat first.",
    "boat_paid": "Cannot edit a paid boat registration. Contact the organization.",
    "temporary_access_expired": "Your temporary access has expired. Contact an administrator."
  }
}
```


## Appendix C: API Endpoints

### Permission Check Endpoints

**GET /api/permissions/current-phase**
- Returns current event phase
- No authentication required (public info)
- Response: `{ "phase": "during_registration", "dates": {...} }`

**POST /api/permissions/check**
- Check if action is permitted
- Requires authentication
- Request: `{ "action": "edit_crew_member", "resource_context": {...} }`
- Response: `{ "is_permitted": true, "denial_reason": null }`

### Temporary Access Grant Endpoints

**POST /admin/temporary-access/grant**
- Grant temporary access to user
- Requires admin role
- Request: `{ "user_id": "user-123", "hours": 48, "notes": "..." }`
- Response: `{ "grant_id": "...", "expiration": "..." }`

**POST /admin/temporary-access/revoke**
- Revoke temporary access grant
- Requires admin role
- Request: `{ "grant_id": "..." }`
- Response: `{ "success": true }`

**GET /admin/temporary-access/list**
- List all active grants
- Requires admin role
- Response: `{ "grants": [...] }`

### Permission Configuration Endpoints

**GET /admin/permissions/config**
- Get current permission matrix
- Requires admin role
- Response: `{ "permissions": {...} }`

**PUT /admin/permissions/config**
- Update permission matrix
- Requires admin role
- Request: `{ "permissions": {...} }`
- Response: `{ "success": true, "updated_at": "..." }`

**GET /admin/permissions/audit-logs**
- Get permission audit logs
- Requires admin role
- Query params: `?user_id=...&action=...&start_date=...&end_date=...`
- Response: `{ "logs": [...], "next_token": "..." }`


## Appendix D: Configuration Example

### System Configuration with Permissions

```json
{
  "PK": "CONFIG",
  "SK": "SYSTEM",
  "registration_start_date": "2026-03-01T00:00:00Z",
  "registration_end_date": "2026-04-15T23:59:59Z",
  "payment_deadline": "2026-04-30T23:59:59Z",
  "temporary_editing_access_hours": 48,
  "permission_cache_ttl_seconds": 60,
  "event_name": "Course des Impressionnistes 2026",
  "event_date": "2026-05-10"
}
```

### Permission Matrix Configuration

```json
{
  "PK": "CONFIG",
  "SK": "PERMISSIONS",
  "version": "1.0",
  "updated_at": "2026-01-14T10:00:00Z",
  "updated_by": "admin@example.com",
  "permissions": {
    "create_crew_member": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": false,
      "after_payment_deadline": false,
      "description": "Create new crew member"
    },
    "edit_crew_member": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": false,
      "after_payment_deadline": false,
      "requires_not_assigned": true,
      "description": "Edit existing crew member"
    },
    "delete_crew_member": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": false,
      "after_payment_deadline": false,
      "requires_not_assigned": true,
      "description": "Delete crew member"
    },
    "create_boat_registration": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": false,
      "after_payment_deadline": false,
      "description": "Create new boat registration"
    },
    "edit_boat_registration": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": false,
      "after_payment_deadline": false,
      "requires_not_paid": true,
      "description": "Edit boat registration"
    },
    "delete_boat_registration": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": false,
      "after_payment_deadline": false,
      "requires_not_paid": true,
      "description": "Delete boat registration"
    },
    "process_payment": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": true,
      "after_payment_deadline": false,
      "description": "Process payment for boat registration"
    },
    "view_data": {
      "before_registration": true,
      "during_registration": true,
      "after_registration": true,
      "after_payment_deadline": true,
      "description": "View data (always allowed)"
    },
    "export_data": {
      "before_registration": true,
      "during_registration": true,
      "after_registration": true,
      "after_payment_deadline": true,
      "description": "Export data (always allowed)"
    }
  }
}
```

---

**End of Design Document**

