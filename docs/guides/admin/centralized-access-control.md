# Centralized Access Control System

## Overview

The Centralized Access Control System provides fine-grained permission management for the Impressionnistes Registration System. It allows administrators to control what actions users can perform based on:

- **Event Phase**: Before registration, during registration, after registration, after payment deadline
- **User Role**: Admin vs Team Manager
- **Data State**: Whether crew members are assigned, whether boats are paid
- **Special Access**: Admin impersonation and temporary access grants

## Key Features

### 1. Permission Matrix Configuration
Administrators can configure permissions for each action across different event phases through the admin panel at `/admin/permissions`.

**Available Actions:**
- Create/Edit/Delete Crew Members
- Create/Edit/Delete Boat Registrations
- Process Payments
- View/Export Data (always allowed)

**Event Phases:**
- Before Registration Opens
- During Registration Period
- After Registration Closes
- After Payment Deadline

### 2. Admin Impersonation
Admins can view and manage data as if they were another team manager. This bypasses phase restrictions but respects data state restrictions for transparency.

**Access:** Admin Dashboard → "Impersonate Club Manager" card

### 3. Temporary Access Grants
Admins can grant temporary access to team managers to perform actions outside the normal registration period.

**Features:**
- Configurable duration (default 24 hours, max 7 days)
- Optional notes for audit trail
- Can be revoked at any time
- Automatically expires

**Access:** Admin Dashboard → "Permissions & Access" → "Temporary Access"

### 4. Audit Logs
All permission decisions and privileged actions are logged for compliance and debugging.

**Log Types:**
- **Denial Logs**: When an action is blocked due to permissions
- **Bypass Logs**: When an action succeeds via impersonation or temporary access
- **Config Logs**: When permission configuration is changed

**Access:** Admin Dashboard → "Permissions & Access" → "Audit Logs"

**Features:**
- Filter by user, action, log type, date range
- Export to CSV
- Clear all logs (with automatic backup)

## Architecture

### Backend Components

**Core Module:** `functions/shared/access_control.py`
- `check_permission()`: Main permission checking function
- `require_permission()`: Decorator for Lambda functions
- `log_permission_denial()`: Audit logging for denials
- `log_permission_bypass()`: Audit logging for bypasses

**Lambda Functions:**
- `get_permission_config`: Fetch current permission matrix
- `update_permission_config`: Update permission matrix
- `reset_permission_config`: Reset to default permissions
- `grant_temporary_access`: Create temporary access grant
- `revoke_temporary_access`: Revoke temporary access grant
- `list_temporary_access_grants`: List all grants
- `get_permission_audit_logs`: Fetch audit logs
- `clear_audit_logs`: Clear all audit logs (with backup)

**API Endpoints:**
```
GET    /admin/permissions/config
PUT    /admin/permissions/config
POST   /admin/permissions/config/reset
POST   /admin/permissions/temporary-access
DELETE /admin/permissions/temporary-access/{grant_id}
GET    /admin/permissions/temporary-access
GET    /admin/permissions/audit-logs
DELETE /admin/permissions/audit-logs
```

### Frontend Components

**Composable:** `frontend/src/composables/usePermissions.js`
- Fetches and caches permission matrix
- Determines current event phase
- Checks if actions are permitted
- Provides user-friendly denial messages

**Admin Pages:**
- `AdminPermissionConfig.vue`: Configure permission matrix
- `AdminTemporaryAccessGrants.vue`: Manage temporary access
- `AdminPermissionAuditLogs.vue`: View audit logs

**Integration:**
All action buttons (Create, Edit, Delete) use `usePermissions` to:
- Disable buttons when action not permitted
- Show tooltip explaining why action is blocked
- Handle permission errors gracefully

## Usage Examples

### For Developers

**Protecting a Lambda Function:**
```python
from functions.shared.access_control import require_permission

@require_permission('create_crew_member')
def lambda_handler(event, context):
    # Your code here
    pass
```

**Manual Permission Check:**
```python
from functions.shared.access_control import check_permission

result = check_permission(
    user_id='user-123',
    action='edit_crew_member',
    resource_context={
        'resource_type': 'crew_member',
        'resource_id': 'member-456',
        'resource_state': {
            'assigned': True  # Crew member is assigned to a boat
        }
    }
)

if not result['is_permitted']:
    return {
        'statusCode': 403,
        'body': json.dumps({
            'error': result['denial_reason']
        })
    }
```

**Frontend Permission Check:**
```vue
<script setup>
import { usePermissions } from '@/composables/usePermissions'

const { canPerformAction, getPermissionMessage } = usePermissions()

const canCreate = computed(() => {
  return canPerformAction('create_crew_member', {
    resource_type: 'crew_member'
  })
})

const createTooltip = computed(() => {
  return getPermissionMessage('create_crew_member', {
    resource_type: 'crew_member'
  })
})
</script>

<template>
  <BaseButton 
    :disabled="!canCreate"
    :title="createTooltip"
    @click="handleCreate"
  >
    Add Member
  </BaseButton>
</template>
```

### For Administrators

**Scenario 1: Extend Registration Period**
1. Go to Admin Dashboard → Event Configuration
2. Update registration end date
3. Permissions automatically adjust based on new dates

**Scenario 2: Allow Late Registration**
1. Go to Admin Dashboard → Permissions & Access → Temporary Access
2. Select the team manager
3. Set duration (e.g., 24 hours)
4. Add note: "Late registration for Team X"
5. Click "Grant Access"
6. Team manager can now create/edit registrations

**Scenario 3: Fix Data After Deadline**
1. Go to Admin Dashboard → Impersonate Club Manager
2. Select the team manager
3. Make necessary changes
4. Exit impersonation
5. Changes are logged in audit logs

**Scenario 4: Review Permission Denials**
1. Go to Admin Dashboard → Permissions & Access → Audit Logs
2. Filter by "Denial" log type
3. Review why actions were blocked
4. Take appropriate action (grant temporary access, adjust permissions, etc.)

## Default Permission Matrix

```javascript
{
  create_crew_member: {
    before_registration: false,
    during_registration: true,
    after_registration: false,
    after_payment_deadline: false
  },
  edit_crew_member: {
    before_registration: false,
    during_registration: true,
    after_registration: false,
    after_payment_deadline: false,
    requires_not_assigned: true  // Can't edit if assigned to boat
  },
  delete_crew_member: {
    before_registration: false,
    during_registration: true,
    after_registration: false,
    after_payment_deadline: false,
    requires_not_assigned: true  // Can't delete if assigned to boat
  },
  create_boat_registration: {
    before_registration: false,
    during_registration: true,
    after_registration: false,
    after_payment_deadline: false
  },
  edit_boat_registration: {
    before_registration: false,
    during_registration: true,
    after_registration: false,
    after_payment_deadline: false,
    requires_not_paid: true  // Can't edit if payment processed
  },
  delete_boat_registration: {
    before_registration: false,
    during_registration: true,
    after_registration: false,
    after_payment_deadline: false,
    requires_not_paid: true  // Can't delete if payment processed
  },
  process_payment: {
    before_registration: false,
    during_registration: true,
    after_registration: true,  // Allow payments after registration
    after_payment_deadline: false
  }
}
```

## Testing

**Backend Tests:**
- `tests/unit/test_access_control_*.py`: Unit tests for core logic
- `tests/integration/test_*_permissions.py`: Integration tests for each API

**Frontend Tests:**
- `frontend/src/composables/usePermissions.test.js`: Composable tests

**Run Tests:**
```bash
cd infrastructure
make test
```

## Troubleshooting

### Button Not Disabled After Permission Change

**Symptom:** After changing permissions in admin panel, buttons remain enabled.

**Cause:** Permission cache not refreshed.

**Solution:** 
1. Check browser console for permission logs
2. Hard refresh the page (Cmd+Shift+R / Ctrl+Shift+R)
3. Clear browser cache if issue persists

### Permission Denied Despite Being Admin

**Symptom:** Admin gets permission denied errors.

**Cause:** Admin impersonation or temporary access not active.

**Solution:**
- Admins must use impersonation to bypass phase restrictions
- Or grant themselves temporary access
- Direct admin actions respect the same permission matrix

### Audit Logs Not Showing

**Symptom:** No logs appear in audit logs page.

**Cause:** No permission denials or bypasses have occurred yet.

**Solution:** This is normal if all actions are permitted. Logs only appear when:
- An action is denied due to permissions
- An action succeeds via impersonation or temporary access
- Permission configuration is changed

## Security Considerations

1. **Admin-Only Access**: All permission management endpoints require admin role
2. **Audit Trail**: All privileged actions are logged with user, timestamp, and reason
3. **Temporary Access Expiry**: Temporary grants automatically expire
4. **Impersonation Transparency**: Impersonation is clearly indicated in UI and logs
5. **Data State Protection**: Even with bypass, certain data states are protected (e.g., can't delete paid boats)

## Future Enhancements

- Role-based permissions (beyond admin/team_manager)
- Custom permission rules per team manager
- Email notifications for temporary access grants
- Permission change history
- Bulk temporary access grants
- Permission templates for common scenarios

## Related Documentation

- [Admin Impersonation Guide](./admin-impersonation.md)
- [Event Configuration](../operations/event-configuration.md)
- [API Reference](../../reference/api-endpoints.md)
