# Admin Boat Registration Management

## Overview

The admin boat registration management interface allows administrators to view and manage all boat registrations (crews) across all club managers, handle forfaits, and oversee the competition.

**Spec Reference:** FR-14 (Admin Boat Registration Management)

## Accessing the Interface

Navigate to **Admin → Boats** from the admin navigation menu.

## Features

### View All Boat Registrations

The interface displays all boat registrations with:
- Boat number (format: `[M/SM].[display_order].[sequence]`)
- Event type (21km / 42km)
- Boat type (skiff, 4-, 4+, 8+)
- Race assignment
- Crew composition (filled seats / total seats, average age)
- Registration status badge (incomplete, complete, paid, forfait)
- License verification status badge (Verified / Invalid / -)
- Club manager name
- Club display (comma-separated list of clubs)
- Hull assignment (if any)

### Search and Filter

- **Search:** Filter by event type, boat type, or boat number
- **Filter by club manager:** Select a specific club manager
- **Filter by club affiliation:** Filter by rowing club
- **Filter by registration status:** Show only specific statuses
- **Sort:** Click column headers to sort by any column

### Forfait Management

To mark a boat as forfait (withdrawal from competition):
1. Find the boat in the list
2. Click the "Forfait" button
3. Confirm the action
4. The boat status changes to forfait with distinct visual styling

To remove forfait status:
1. Find the forfait boat
2. Click "Remove Forfait"
3. The boat returns to its previous registration status

Forfait boats are visually distinguished with:
- Red/muted styling
- Strikethrough or dimmed appearance
- Clear "Forfait" status badge

### Delete Boat Registration

Administrators can delete boat registrations with restrictions:
- **Can delete:** Incomplete, complete, and forfait boats (regardless of date)
- **Cannot delete:** Paid boats (to maintain payment integrity)

### Visual Indicators

| Status | Badge Color | Description |
|--------|-------------|-------------|
| Incomplete | Yellow | Missing crew members or race assignment |
| Complete | Green | All seats filled, race selected |
| Paid | Blue | Payment received |
| Forfait | Red | Withdrawn from competition |
| Free | Green | RCPM members, no payment required |

## Date Restriction Bypass

Administrators bypass all date-based restrictions:

| Action | Club Manager | Admin |
|--------|-------------|-------|
| View boats | Any time | Any time |
| Mark forfait | N/A | Any time |
| Remove forfait | N/A | Any time |
| Delete boat | During registration (if not paid) | Any time (if not paid) |

## Audit Logging

All admin actions on boat registrations are logged with:
- Timestamp
- Admin user ID
- Action performed (forfait, remove forfait, delete)
- Affected boat ID
- Previous and new status

## Related Documentation

- [Admin Crew Members](./admin-crew-members.md) — Crew member management
- [License Verification](./license-verification.md) — License status in boat list
- [Admin Club Managers](./admin-club-managers.md) — Club manager management
- [Centralized Access Control](./centralized-access-control.md) — Permission system
- [Hull Assignment Guide](../hull-assignment.md) — Hull assignment workflow
