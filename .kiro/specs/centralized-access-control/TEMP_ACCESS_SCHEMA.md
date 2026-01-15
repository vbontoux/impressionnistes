# Temporary Access Grant Schema

## Overview

Temporary access grants allow administrators to give team managers temporary permission to edit data outside the normal registration period. This is useful for handling late changes or corrections.

## DynamoDB Schema

### Item Structure

```python
{
    'PK': 'TEMP_ACCESS',
    'SK': 'USER#{user_id}',
    'grant_id': str,  # Unique identifier for the grant
    'user_id': str,  # Team manager user ID
    'granted_by_admin_id': str,  # Admin who created the grant
    'grant_timestamp': str,  # ISO 8601 timestamp when grant was created
    'expiration_timestamp': str,  # ISO 8601 timestamp when grant expires
    'hours': int,  # Duration in hours (for display)
    'status': str,  # 'active', 'expired', or 'revoked'
    'notes': str,  # Optional notes from admin
    'revoked_at': str,  # ISO 8601 timestamp when revoked (if applicable)
    'revoked_by_admin_id': str,  # Admin who revoked (if applicable)
    'created_at': str,  # ISO 8601 timestamp
    'updated_at': str,  # ISO 8601 timestamp
}
```

### Access Patterns

1. **Check if user has active grant**
   - Query: `PK = 'TEMP_ACCESS' AND SK = 'USER#{user_id}'`
   - Filter: `status = 'active' AND expiration_timestamp > current_time`

2. **List all active grants**
   - Query: `PK = 'TEMP_ACCESS'`
   - Filter: `status = 'active'`

3. **Get specific grant**
   - Query: `PK = 'TEMP_ACCESS' AND SK = 'USER#{user_id}'`

### Status Values

- **active**: Grant is currently valid and not expired
- **expired**: Grant has passed its expiration timestamp
- **revoked**: Grant was manually revoked by an admin

### Example Item

```python
{
    'PK': 'TEMP_ACCESS',
    'SK': 'USER#abc123',
    'grant_id': 'grant_20260114_abc123',
    'user_id': 'abc123',
    'granted_by_admin_id': 'admin_xyz',
    'grant_timestamp': '2026-01-14T10:00:00Z',
    'expiration_timestamp': '2026-01-16T10:00:00Z',
    'hours': 48,
    'status': 'active',
    'notes': 'Late crew member change needed',
    'created_at': '2026-01-14T10:00:00Z',
    'updated_at': '2026-01-14T10:00:00Z',
}
```

## Implementation Notes

1. **One grant per user**: Each user can only have one active grant at a time (enforced by PK/SK)
2. **Automatic expiration**: Grants are checked at permission check time, not via scheduled job
3. **Manual revocation**: Admins can revoke grants before expiration
4. **Audit trail**: All grant operations are logged to audit table
5. **No GSI needed**: Simple query patterns work with base table

## Permission Bypass Rules

When a user has an active temporary access grant:
- ✅ **Bypasses event phase restrictions** (can edit during/after registration closes)
- ❌ **Does NOT bypass data state restrictions** (still cannot edit assigned crew or paid boats)
- ✅ **Logged in audit trail** with bypass_reason='temporary_access'

## Migration

No migration needed - items are created on-demand when admins grant temporary access.
