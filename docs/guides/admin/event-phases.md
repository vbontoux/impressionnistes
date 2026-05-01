# Event Phases Guide

## Overview

The event phase system automatically determines which actions are permitted based on the current date relative to configured registration and payment dates. It enforces consistent rules across both backend (API) and frontend (UI).

**Spec Reference:** FR-17 (Event Phase-Based Access Control), FR-18 (Temporary Access Grants)

## The Four Phases

| Phase | Condition | Description |
|-------|-----------|-------------|
| **before_registration** | Current date < `registration_start_date` | Before registration period opens |
| **during_registration** | `registration_start_date` ≤ Current date ≤ `registration_end_date` | Active registration period |
| **after_registration** | `registration_end_date` < Current date ≤ `payment_deadline` | Registration closed, payments still accepted |
| **after_payment_deadline** | Current date > `payment_deadline` | All modifications locked |

## Phase Detection

The system determines the current phase by comparing the current date/time with three configured dates:
- `registration_start_date` (default: March 19)
- `registration_end_date` (default: April 19)
- `payment_deadline` (default: April 25)

These dates are configured in **Admin → Configuration → System**.

Phase detection is cached for 60 seconds to optimize performance.

## Permission Matrix

### Club Manager Permissions

| Action | before_registration | during_registration | after_registration | after_payment_deadline |
|--------|:---:|:---:|:---:|:---:|
| View registrations | ✅ | ✅ | ✅ | ✅ |
| Create crew member | ❌ | ✅ | ❌ | ❌ |
| Edit crew member | ❌ | ✅ | ❌ | ❌ |
| Delete crew member | ❌ | ✅ (if unassigned) | ❌ | ❌ |
| Create boat registration | ❌ | ✅ | ❌ | ❌ |
| Edit boat registration | ❌ | ✅ | ❌ | ❌ |
| Delete boat registration | ❌ | ✅ (if not paid) | ❌ | ❌ |
| Process payment | ❌ | ✅ | ✅ | ❌ |
| Request boat rental | ❌ | ✅ | ❌ | ❌ |
| Request hull assignment | ❌ | ✅ | ❌ | ❌ |

### Admin Permissions

Administrators bypass all date-based restrictions. They can perform any action in any phase.

When impersonating a team manager, the admin retains full permissions (the impersonated manager's phase restrictions do not apply).

## Frontend Enforcement

The frontend uses the `usePermissions` composable to:
- Disable buttons when actions are not permitted
- Display tooltip messages explaining why an action is restricted
- Hide create/edit forms when the phase doesn't allow them

Example restriction message: *"Registration period has ended. Contact the administrator for assistance."*

## Backend Enforcement

The backend `access_control.py` module checks permissions on every API request:
1. Determines the current event phase
2. Checks the user's role (admin or club manager)
3. Checks for active temporary access grants
4. Returns allowed/denied with a reason message

If an action is denied, the API returns a `403 Forbidden` response with a clear error message.

## Temporary Access Grants (FR-18)

Administrators can grant temporary access to specific club managers, allowing them to bypass phase restrictions for a limited time.

### Creating a Grant

1. Navigate to **Admin → Access Control** (or use the team manager's profile)
2. Select the club manager
3. Specify duration in hours (default: 48 hours)
4. Click "Grant Access"

### Grant Behavior

- The club manager can perform all actions regardless of the current phase
- A notification banner is displayed to the club manager indicating temporary access is active
- The grant automatically expires after the specified duration
- All actions performed under a temporary grant are logged

### Revoking a Grant

Administrators can revoke a grant at any time:
1. Find the active grant in the access control interface
2. Click "Revoke"
3. Access is immediately terminated

### Grant Statuses

| Status | Meaning |
|--------|---------|
| `active` | Grant is currently in effect |
| `expired` | Grant has passed its expiration time |
| `revoked` | Grant was manually revoked by an admin |

## Configuration

Event phase dates are managed in **Admin → Configuration → System**:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `registration_start_date` | March 19 | When registration opens |
| `registration_end_date` | April 19 | When registration closes |
| `payment_deadline` | April 25 | Final payment deadline |
| `temporary_access_duration_hours` | 48 | Default grant duration |
| `permission_cache_ttl_seconds` | 60 | Permission check cache |
| `event_phase_cache_ttl_seconds` | 60 | Phase detection cache |

## Audit Logging

All permission-related events are logged:
- Permission denials (action, user, phase, reason)
- Admin bypasses
- Temporary access grants (created, expired, revoked)
- Actions performed under temporary access

## Related Documentation

- [Centralized Access Control](./centralized-access-control.md) — Full permission system details
- [Admin Impersonation](./admin-impersonation.md) — Admin impersonation and permissions
- [Admin Crew Members](./admin-crew-members.md) — Date restriction bypass for admins
- [Admin Boat Registrations](./admin-boat-registrations.md) — Date restriction bypass for admins
