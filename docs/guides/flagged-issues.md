# Flagged Issues Guide

## Overview

The flagged issues system allows administrators to flag problems with crew member registrations and notify the corresponding club managers. Club managers can then resolve the issues autonomously during the registration period.

**Spec Reference:** FR-6 (Registration Validation and Management)

## How It Works

### Admin Flags an Issue

1. Navigate to **Admin → Crew Members** or **Admin → Boats**
2. Identify a crew member with a problem (e.g., invalid license, incorrect date of birth, missing information)
3. Click "Flag Issue" on the crew member
4. Enter a description of the problem
5. Save — the club manager is notified immediately

### Club Manager Resolves the Issue

1. The club manager receives a notification (email, in-app, and/or Slack depending on configuration)
2. The flagged issue appears on the crew member's detail view and on the boat registration
3. The club manager corrects the information
4. The club manager clicks "Mark as Resolved"
5. The admin can see the issue is marked as resolved by the club manager

### Admin Reviews Resolution

1. Navigate to the crew member or boat registration
2. See that the flagged issue is marked as "Resolved by club manager"
3. Verify the correction is satisfactory
4. Optionally clear the flag or flag a new issue

## Notification Flow

When an issue is flagged:
1. **Immediate notification** sent to the club manager via configured channels (email, in-app, Slack)
2. **Repeated reminders** sent at the configured notification frequency (default: weekly) if the issue remains unresolved
3. **Deadline reminders** sent as registration deadlines approach, highlighting any unresolved issues

## Issue Visibility

Flagged issues are visible in:
- **Club manager dashboard:** Highlighted with warning indicators
- **Crew member detail view:** Issue description and status
- **Boat registration view:** Crew members with flagged issues are marked
- **Seat assignment display:** Visual indicator next to flagged crew members
- **Admin views:** All flagged issues across all club managers

## Payment with Flagged Issues

Flagged issues do **not** block payment. Club managers can still process payments even if some crew members have unresolved flagged issues (FR-4, criterion 10).

## Date Restrictions

- **During registration:** Club managers can correct flagged issues autonomously
- **After registration:** Club managers cannot edit crew members unless granted temporary access by an admin
- **Admin:** Can edit at any time regardless of phase

## Common Flagged Issues

| Issue Type | Example | Resolution |
|------------|---------|------------|
| Invalid license | License number doesn't match FFA records | Club manager updates license number |
| Incorrect date of birth | Age doesn't match license records | Club manager corrects date of birth |
| Missing information | Club affiliation not provided | Club manager fills in missing field |
| Duplicate entry | Same person registered under different names | Club manager removes duplicate |
| Ineligible crew | Crew composition doesn't match race rules | Club manager adjusts crew or race selection |

## Audit Trail

All flagged issue actions are logged:
- Admin flags issue (timestamp, admin ID, description)
- Club manager marks as resolved (timestamp, user ID)
- Admin clears flag (timestamp, admin ID)
- Notification sent (timestamp, channel, recipient)

## Related Documentation

- [Admin Crew Members](./admin/admin-crew-members.md) — Where admins flag issues
- [Admin Boat Registrations](./admin/admin-boat-registrations.md) — Boat-level issue visibility
- [Notifications](./notifications.md) — Notification system
- [Event Phases](./admin/event-phases.md) — Date restrictions on issue resolution
