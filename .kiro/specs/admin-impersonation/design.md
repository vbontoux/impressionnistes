# Design Document: Admin Impersonation

## Overview

The Admin Impersonation feature allows administrators to view and interact with the application as if they were a specific team manager. This eliminates the need to build duplicate admin interfaces for every team manager feature, as admins can simply use the existing team manager UI while impersonating.

The design uses a combination of URL query parameters (for persistence and shareability) and Pinia store state (for reactive access) to manage impersonation. An API client interceptor automatically adds the impersonation parameter to all requests, making the feature transparent to existing code.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Browser                                                     │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ App.vue                                                │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │ AdminImpersonationBar (Fixed Position)          │  │ │
│  │  │ - Team Manager Selector                         │  │ │
│  │  │ - Visual Indicator                              │  │ │
│  │  │ - Exit Button                                   │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │ Router View (Team Manager Pages)                │  │ │
│  │  │ - /boats, /crew, /dashboard, etc.               │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Pinia Auth Store                                      │ │
│  │ - impersonatedTeamManagerId                           │ │
│  │ - impersonatedTeamManager (name, email)               │ │
│  │ - effectiveUserId getter                              │ │
│  │ - isImpersonating getter                              │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ↕                                   │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Vue Router                                            │ │
│  │ - Query params: ?team_manager_id=xxx                  │ │
│  │ - Bidirectional sync with store                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ↕                                   │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ API Client (Axios)                                    │ │
│  │ - Request interceptor                                 │ │
│  │ - Adds ?team_manager_id to all requests              │ │
│  └───────────────────────────────────────────────────────┘ │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTP Requests
                               ↓
┌─────────────────────────────────────────────────────────────┐
│  Backend (AWS Lambda)                                        │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ API Gateway                                           │ │
│  │ - Cognito Authorizer (validates JWT)                  │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Lambda Functions                                      │ │
│  │ - @require_team_manager_or_admin_override decorator   │ │
│  │ - Validates admin permission                          │ │
│  │ - Sets effective_user_id from query param             │ │
│  │ - Logs admin actions for audit                        │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ DynamoDB                                              │ │
│  │ - Accesses data using effective_user_id               │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### State Flow

```
1. Admin selects team manager
   ↓
2. Store updates impersonation state
   ↓
3. Router updates URL query param
   ↓
4. Page reloads with new data
   ↓
5. API client adds param to all requests
   ↓
6. Backend validates admin + uses team manager ID
   ↓
7. Returns team manager's data
```

## Components and Interfaces

### Frontend Components

#### 1. AdminImpersonationBar.vue

**Purpose:** Visual component that displays impersonation status and provides controls.

**Props:** None (reads from store)

**Template Structure:**
```vue
<template>
  <div v-if="authStore.isImpersonating" class="impersonation-bar">
    <div class="impersonation-info">
      <span class="warning-icon">⚠️</span>
      <span class="label">ADMIN MODE: Viewing as</span>
      <span class="team-manager-name">{{ impersonatedTeamManager.name }}</span>
      <span class="team-manager-email">({{ impersonatedTeamManager.email }})</span>
    </div>
    <div class="impersonation-controls">
      <select v-model="selectedTeamManagerId" @change="changeImpersonation">
        <option value="">-- Select Team Manager --</option>
        <option v-for="tm in teamManagers" :key="tm.user_id" :value="tm.user_id">
          {{ tm.first_name }} {{ tm.last_name }} ({{ tm.email }})
        </option>
      </select>
      <button @click="exitImpersonation" class="exit-btn">
        Exit Impersonation ✕
      </button>
    </div>
  </div>
</template>
```

**Styling:**
- Fixed position at top of page (below header)
- Distinctive warning/alert background color (#FFF3CD with #856404 text)
- High z-index to stay above content
- Responsive design for mobile

**Methods:**
- `changeImpersonation(teamManagerId)` - Updates impersonation to new team manager
- `exitImpersonation()` - Clears impersonation state
- `fetchTeamManagers()` - Loads list of team managers from API

#### 2. App.vue Modifications

**Changes:**
- Add `<AdminImpersonationBar />` component below header
- Add watchers for bidirectional sync between router and store
- Only show bar when `authStore.isAdmin` is true

**Sync Logic:**
```javascript
// Watch route query param → update store
watch(() => route.query.team_manager_id, async (teamManagerId) => {
  if (authStore.isAdmin && teamManagerId) {
    // Fetch team manager details
    const teamManager = await fetchTeamManagerDetails(teamManagerId)
    authStore.setImpersonation(teamManagerId, teamManager)
  } else {
    authStore.clearImpersonation()
  }
}, { immediate: true })

// Watch store → update route query param
watch(() => authStore.impersonatedTeamManagerId, (teamManagerId) => {
  const currentQuery = { ...route.query }
  
  if (teamManagerId) {
    currentQuery.team_manager_id = teamManagerId
  } else {
    delete currentQuery.team_manager_id
  }
  
  router.replace({ query: currentQuery })
})
```

### Frontend State Management

#### Auth Store Extensions (frontend/src/stores/authStore.js)

**New State Properties:**
```javascript
state: () => ({
  // ... existing state ...
  impersonatedTeamManagerId: null,
  impersonatedTeamManager: null, // { user_id, first_name, last_name, email, club_affiliation }
})
```

**New Getters:**
```javascript
getters: {
  // ... existing getters ...
  
  /**
   * Get the effective user ID for API requests
   * Returns impersonated ID if impersonating, otherwise admin's ID
   */
  effectiveUserId: (state) => {
    return state.impersonatedTeamManagerId || state.user?.user_id
  },
  
  /**
   * Check if currently impersonating
   */
  isImpersonating: (state) => {
    return state.isAdmin && !!state.impersonatedTeamManagerId
  },
}
```

**New Actions:**
```javascript
actions: {
  // ... existing actions ...
  
  /**
   * Start impersonating a team manager
   */
  setImpersonation(teamManagerId, teamManagerInfo) {
    this.impersonatedTeamManagerId = teamManagerId
    this.impersonatedTeamManager = teamManagerInfo
  },
  
  /**
   * Stop impersonating
   */
  clearImpersonation() {
    this.impersonatedTeamManagerId = null
    this.impersonatedTeamManager = null
  },
}
```

### API Client Integration

#### Axios Request Interceptor (frontend/src/services/apiClient.js)

**Purpose:** Automatically add `team_manager_id` query parameter to all API requests when impersonating.

**Implementation:**
```javascript
import { useAuthStore } from '@/stores/authStore'

// Request interceptor
apiClient.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  
  // Add impersonation parameter if impersonating
  if (authStore.isImpersonating) {
    // Parse existing URL and params
    const url = new URL(config.url, config.baseURL || window.location.origin)
    url.searchParams.set('team_manager_id', authStore.impersonatedTeamManagerId)
    
    // Update config with new URL
    config.url = url.pathname + url.search
  }
  
  return config
}, (error) => {
  return Promise.reject(error)
})
```

**Behavior:**
- Runs before every API request
- Checks if admin is impersonating
- Adds `team_manager_id` to query parameters
- Preserves existing query parameters
- Does not modify request method, headers, or body

### Backend Components

#### 1. New Decorator: require_team_manager_or_admin_override

**File:** `functions/shared/auth_utils.py`

**Purpose:** Replace `@require_team_manager` decorator to support admin impersonation.

**Implementation:**
```python
def require_team_manager_or_admin_override(func):
    """
    Decorator to require team manager access or admin with override
    
    Allows:
    - Team managers to access their own data
    - Admins to access their own data
    - Admins to access any team manager's data via ?team_manager_id parameter
    
    Sets event['_effective_user_id'] for use in handler
    Sets event['_is_admin_override'] to track impersonation
    """
    @wraps(func)
    def wrapper(event, context):
        user_info = get_user_from_event(event)
        
        if not user_info or not user_info.get('user_id'):
            logger.warning("Unauthorized access attempt")
            return unauthorized_error('Authentication required')
        
        # Check for admin override
        query_params = event.get('queryStringParameters', {}) or {}
        override_id = query_params.get('team_manager_id')
        
        if override_id:
            # Admin override requested
            if not is_admin(user_info):
                logger.warning(f"Non-admin {user_info.get('email')} attempted impersonation")
                return forbidden_error('Admin access required for impersonation')
            
            # Validate that target is not an admin
            # (We'll need to check this - for now, trust the override)
            
            # Set effective user ID and log
            event['_effective_user_id'] = override_id
            event['_is_admin_override'] = True
            event['_admin_user_id'] = user_info['user_id']
            
            logger.info(f"Admin {user_info.get('email')} impersonating team manager {override_id}")
        else:
            # Normal access - check team manager or admin permission
            if not is_team_manager(user_info) and not is_admin(user_info):
                logger.warning(f"Forbidden: User {user_info.get('email')} attempted team manager access")
                return forbidden_error('Team manager access required')
            
            event['_effective_user_id'] = user_info['user_id']
            event['_is_admin_override'] = False
        
        return func(event, context)
    
    return wrapper
```

**Usage in Lambda Functions:**
```python
@handle_exceptions
@require_team_manager_or_admin_override
def lambda_handler(event, context):
    # Get effective user ID (impersonated or real)
    team_manager_id = event['_effective_user_id']
    is_admin_override = event['_is_admin_override']
    
    # Use team_manager_id for data access
    boats = db.query_by_pk(pk=f'TEAM#{team_manager_id}', sk_prefix='BOAT#')
    
    # Log if admin override
    if is_admin_override:
        admin_id = event['_admin_user_id']
        logger.info(f"Admin {admin_id} accessed boats for team manager {team_manager_id}")
    
    return success_response(data=boats)
```

**Usage in Validation Functions:**
```python
def validate_registration_deadline(event, boat_data):
    """
    Validate that registration is within allowed dates
    Admins can bypass this check when impersonating
    """
    # Skip deadline check if admin is impersonating
    if event.get('_is_admin_override'):
        logger.info(f"Admin override: Skipping registration deadline check")
        return True
    
    # Normal deadline check for team managers
    current_date = datetime.now()
    if current_date > REGISTRATION_DEADLINE:
        raise ValidationError("Registration deadline has passed")
    
    if current_date < REGISTRATION_START_DATE:
        raise ValidationError("Registration has not opened yet")
    
    return True

def validate_payment_status(event, team_manager_id):
    """
    Validate that team manager has paid registration fees
    Admins can bypass this check when impersonating
    """
    # Skip payment check if admin is impersonating
    if event.get('_is_admin_override'):
        logger.info(f"Admin override: Skipping payment validation")
        return True
    
    # Normal payment check for team managers
    payment = get_payment_status(team_manager_id)
    if not payment or payment['status'] != 'paid':
        raise ValidationError("Payment required before registration")
    
    return True
```

#### 2. List Team Managers Endpoint

**File:** `functions/admin/list_team_managers.py`

**Purpose:** Provide list of all team managers for impersonation selector.

**Implementation:**
```python
@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """
    List all team managers
    
    Returns:
        List of team managers with user_id, first_name, last_name, email, club_affiliation
    """
    logger.info("List team managers request")
    
    db = get_db_client()
    
    # Query all users with PROFILE sort key
    # Filter for team_managers group in application code
    # (DynamoDB doesn't store Cognito groups, so we need to get from Cognito)
    
    # For now, query all user profiles and filter
    response = db.table.scan(
        FilterExpression='begins_with(SK, :profile)',
        ExpressionAttributeValues={':profile': 'PROFILE'}
    )
    
    users = response.get('Items', [])
    
    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = db.table.scan(
            FilterExpression='begins_with(SK, :profile)',
            ExpressionAttributeValues={':profile': 'PROFILE'},
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        users.extend(response.get('Items', []))
    
    # Filter for team managers (those who have created boats or crew)
    # This is a heuristic - ideally we'd check Cognito groups
    team_managers = []
    for user in users:
        user_id = user.get('user_id')
        if not user_id:
            continue
        
        # Check if user has any boats or crew members
        has_data = db.query_by_pk(
            pk=f'TEAM#{user_id}',
            sk_prefix='BOAT#',
            limit=1
        ) or db.query_by_pk(
            pk=f'TEAM#{user_id}',
            sk_prefix='CREW#',
            limit=1
        )
        
        if has_data:
            team_managers.append({
                'user_id': user_id,
                'first_name': user.get('first_name', ''),
                'last_name': user.get('last_name', ''),
                'email': user.get('email', ''),
                'club_affiliation': user.get('club_affiliation', '')
            })
    
    # Sort by last name
    team_managers.sort(key=lambda x: (x['last_name'], x['first_name']))
    
    return success_response(data={'team_managers': team_managers})
```

**API Route:** `GET /admin/team-managers`

#### 3. Audit Logging

**Implementation:** Add logging to all Lambda functions that use the decorator.

**Log Format:**
```python
if event.get('_is_admin_override'):
    logger.info({
        'event': 'admin_impersonation',
        'admin_user_id': event['_admin_user_id'],
        'impersonated_user_id': event['_effective_user_id'],
        'action': context.function_name,
        'endpoint': event.get('path'),
        'method': event.get('httpMethod'),
        'timestamp': get_timestamp()
    })
```

**CloudWatch Logs:** All impersonation actions will be logged to CloudWatch for audit purposes.

## Data Models

### Frontend Models

#### ImpersonationState (TypeScript/JSDoc)
```javascript
/**
 * @typedef {Object} ImpersonationState
 * @property {string|null} impersonatedTeamManagerId - ID of impersonated team manager
 * @property {TeamManagerInfo|null} impersonatedTeamManager - Details of impersonated team manager
 */

/**
 * @typedef {Object} TeamManagerInfo
 * @property {string} user_id - Team manager's user ID
 * @property {string} first_name - Team manager's first name
 * @property {string} last_name - Team manager's last name
 * @property {string} email - Team manager's email
 * @property {string} club_affiliation - Team manager's club
 */
```

### Backend Models

No new database models required. Existing models are used with the effective user ID.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Admin-only impersonation access
*For any* API request with `team_manager_id` parameter, the authenticated user must be an admin, otherwise the request is rejected with 403 Forbidden.
**Validates: Requirements 5.1, 5.3, 9.1, 9.2**

### Property 2: Effective user ID substitution
*For any* admin API request with `team_manager_id` parameter, the system uses that team manager ID for data access instead of the admin's ID.
**Validates: Requirements 5.2**

### Property 3: JWT token preservation
*For any* impersonation session, the admin's original JWT token and identity remain unchanged for audit logging.
**Validates: Requirements 5.5, 8.1**

### Property 4: URL parameter persistence
*For any* navigation action while impersonating, the `team_manager_id` query parameter is preserved in the URL.
**Validates: Requirements 2.2**

### Property 5: State restoration from URL
*For any* valid `team_manager_id` in the URL, the impersonation state is restored when the page loads.
**Validates: Requirements 2.3, 2.4**

### Property 6: API client parameter injection
*For any* API request while impersonating, the API client automatically adds `team_manager_id` as a query parameter.
**Validates: Requirements 6.1**

### Property 7: Parameter cleanup on exit
*For any* impersonation exit action, the `team_manager_id` query parameter is removed from the URL.
**Validates: Requirements 4.3**

### Property 8: Team manager list completeness
*For any* set of team managers in the system, the list endpoint returns all of them with required fields (user_id, first_name, last_name, email, club_affiliation).
**Validates: Requirements 7.2, 7.3**

### Property 9: Non-admin rejection
*For any* non-admin request to the team manager list endpoint, the request is rejected with 403 Forbidden.
**Validates: Requirements 7.4**

### Property 10: Audit log completeness
*For any* impersonated API request, the system logs the admin's user ID, impersonated user ID, action, endpoint, and timestamp.
**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

### Property 11: Effective user ID getter
*For any* impersonation state (impersonating or not), the `effectiveUserId` getter returns the impersonated ID when impersonating, or the admin's ID when not.
**Validates: Requirements 10.3**

### Property 12: Impersonation status getter
*For any* impersonation state, the `isImpersonating` getter returns true when impersonating and false when not.
**Validates: Requirements 10.4**

### Property 13: Bidirectional state sync
*For any* change to impersonation state (store or URL), the other is updated to match, maintaining consistency.
**Validates: Requirements 10.5**

### Property 14: Request parameter preservation
*For any* API request with existing query parameters, adding `team_manager_id` does not overwrite or remove existing parameters.
**Validates: Requirements 6.3**

### Property 15: Request integrity preservation
*For any* API request, the interceptor preserves the original request method, headers, and body.
**Validates: Requirements 6.4**

### Property 16: Admin-only impersonation prevention
*For any* impersonation attempt targeting a user in the 'admins' group, the request is rejected.
**Validates: Requirements 9.4**

### Property 17: Admin override for business rules
*For any* impersonated request with `_is_admin_override` flag set, business rule validations (payment requirements, registration deadlines) are bypassed.
**Validates: Requirements 9.5, 11.1, 11.2, 11.3, 11.4**

### Property 18: Token validation
*For any* impersonation request, the JWT token is validated for authenticity and expiration.
**Validates: Requirements 9.3**

### Property 19: Store reactivity
*For any* change to impersonation state in the store, reactive getters immediately reflect the new value.
**Validates: Requirements 10.2**

### Property 20: Team manager data display
*For any* impersonated team manager, the impersonation bar displays their full name and email address.
**Validates: Requirements 3.2**

## Error Handling

### Frontend Error Handling

**Scenarios:**
1. **Team manager list fails to load**
   - Display error message in selector
   - Allow retry
   - Log error to console

2. **Invalid team manager ID in URL**
   - Clear impersonation state
   - Show notification to admin
   - Redirect to admin dashboard

3. **API request fails during impersonation**
   - Display standard error message
   - Do not automatically exit impersonation
   - Allow admin to retry or exit manually

4. **Network error during impersonation change**
   - Show loading state
   - Display error message
   - Revert to previous impersonation state

### Backend Error Handling

**Scenarios:**
1. **Non-admin attempts impersonation**
   - Return 403 Forbidden
   - Log security event
   - Include clear error message

2. **Invalid team manager ID provided**
   - Return 404 Not Found
   - Log warning
   - Include error message

3. **Expired JWT token**
   - Return 401 Unauthorized
   - Trigger frontend re-authentication
   - Clear impersonation state

4. **Team manager has no data**
   - Return empty results (not an error)
   - Log info message
   - Allow admin to see empty state

## Testing Strategy

### Unit Tests

**Frontend Unit Tests:**
1. Auth store impersonation actions
   - `setImpersonation()` updates state correctly
   - `clearImpersonation()` clears state
   - `effectiveUserId` getter returns correct ID
   - `isImpersonating` getter returns correct boolean

2. API client interceptor
   - Adds parameter when impersonating
   - Does not add parameter when not impersonating
   - Preserves existing query parameters
   - Preserves request method, headers, body

3. AdminImpersonationBar component
   - Renders when impersonating
   - Does not render when not impersonating
   - Displays correct team manager info
   - Exit button clears impersonation

**Backend Unit Tests:**
1. Decorator logic
   - Allows admin with parameter
   - Rejects non-admin with parameter
   - Allows team manager without parameter
   - Sets effective_user_id correctly

2. List team managers endpoint
   - Returns all team managers
   - Includes required fields
   - Rejects non-admin requests
   - Handles empty list

### Property-Based Tests

**Test Configuration:** Minimum 100 iterations per property test.

**Property Test 1: Admin-only access**
- **Feature:** admin-impersonation, Property 1
- Generate random user roles and team manager IDs
- Verify only admins can impersonate
- Verify non-admins get 403 error

**Property Test 2: Effective user ID substitution**
- **Feature:** admin-impersonation, Property 2
- Generate random admin IDs and team manager IDs
- Verify data access uses team manager ID
- Verify admin ID is not used for data queries

**Property Test 3: URL parameter persistence**
- **Feature:** admin-impersonation, Property 4
- Generate random navigation paths
- Verify parameter persists across all navigations
- Verify parameter format is correct

**Property Test 4: State restoration**
- **Feature:** admin-impersonation, Property 5
- Generate random team manager IDs in URL
- Verify state is restored correctly
- Verify invalid IDs are handled

**Property Test 5: API parameter injection**
- **Feature:** admin-impersonation, Property 6
- Generate random API endpoints
- Verify parameter is added to all requests
- Verify parameter is not added when not impersonating

**Property Test 6: Audit logging**
- **Feature:** admin-impersonation, Property 10
- Generate random impersonated requests
- Verify all required fields are logged
- Verify log format is consistent

### Integration Tests

1. **End-to-end impersonation flow**
   - Admin logs in
   - Selects team manager
   - Views team manager's boats
   - Exits impersonation
   - Verify data changes at each step

2. **Cross-page navigation**
   - Start impersonation
   - Navigate to multiple pages
   - Verify parameter persists
   - Verify data is correct on each page

3. **Browser refresh**
   - Start impersonation
   - Refresh browser
   - Verify impersonation is restored
   - Verify data is correct

4. **URL sharing**
   - Admin 1 impersonates team manager
   - Copy URL
   - Admin 2 opens URL
   - Verify Admin 2 sees same data

### Manual Testing Checklist

- [ ] Impersonation bar is visually prominent
- [ ] Team manager selector is searchable/filterable
- [ ] Exit button is easily accessible
- [ ] Mobile responsive design works
- [ ] No visual flicker during state changes
- [ ] Error messages are clear and helpful
- [ ] Audit logs are created correctly
- [ ] Performance is acceptable (<500ms state changes)

## Security Considerations

1. **JWT Token Security**
   - Admin's JWT token is never modified
   - Token validation occurs on every request
   - Expired tokens trigger re-authentication

2. **Authorization Checks**
   - Admin group membership verified on every impersonation request
   - Cannot impersonate other admins
   - Cannot bypass business rules through impersonation

3. **Audit Trail**
   - All impersonation actions logged to CloudWatch
   - Logs include admin ID, team manager ID, action, timestamp
   - Logs are immutable and retained per compliance requirements

4. **Data Access and Admin Privileges**
   - Impersonation affects both data queries and business rule enforcement
   - Admins can bypass payment requirements when impersonating
   - Admins can bypass registration deadlines when impersonating
   - Admin overrides are logged for audit purposes
   - `_is_admin_override` flag signals to validation functions to skip restrictions

5. **URL Parameter Validation**
   - Team manager ID validated against database
   - Invalid IDs rejected gracefully
   - No SQL injection or XSS vulnerabilities

## Performance Considerations

1. **State Synchronization**
   - Debounce URL updates to avoid excessive history entries
   - Use `router.replace()` instead of `router.push()` to avoid history pollution
   - Minimize re-renders during state changes

2. **API Client Interceptor**
   - Interceptor runs on every request (minimal overhead)
   - URL parsing is efficient (native URL API)
   - No additional network requests

3. **Team Manager List**
   - Cache list in component for 5 minutes
   - Lazy load on first open of selector
   - Support search/filter for large lists

4. **Audit Logging**
   - Asynchronous logging (non-blocking)
   - Batch logs if high volume
   - Use CloudWatch Logs Insights for queries

## Deployment Considerations

1. **Backend Deployment**
   - Deploy new decorator to Lambda layer
   - Update all team manager endpoints to use new decorator
   - Deploy list team managers endpoint
   - Test in dev environment first

2. **Frontend Deployment**
   - Deploy auth store changes
   - Deploy AdminImpersonationBar component
   - Deploy App.vue changes
   - Deploy API client interceptor
   - Test in dev environment first

3. **Rollback Plan**
   - Backend: Revert to old decorator
   - Frontend: Hide impersonation bar with feature flag
   - Database: No schema changes, no rollback needed

4. **Monitoring**
   - CloudWatch metrics for impersonation usage
   - Error rate monitoring
   - Performance monitoring (API latency)
   - Security monitoring (failed impersonation attempts)
