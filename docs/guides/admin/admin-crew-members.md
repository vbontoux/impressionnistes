# Admin Crew Member Management

## Overview

The admin crew member management interface allows administrators to view and manage all crew members across all club managers, regardless of date restrictions.

**Spec Reference:** FR-13 (Admin Crew Member Management)

## Accessing the Interface

Navigate to **Admin → Crew Members** from the admin navigation menu.

## Features

### View All Crew Members

The interface displays all crew members from all club managers in a single view with:
- First name, last name
- Age (calculated from date of birth and competition date)
- Gender
- License number
- License verification status badge
- Club affiliation
- Associated club manager name
- Boat assignment status (assigned/unassigned)

### Search and Filter

- **Search:** Type in the search box to filter by name or license number
- **Filter by club manager:** Select a specific club manager from the dropdown
- **Filter by club affiliation:** Filter by rowing club
- **Sort:** Click column headers to sort by name, club, club manager, age, etc.

### Create Crew Member

Administrators can create crew members for any club manager:
1. Click "Add Crew Member"
2. Select the target club manager from the dropdown
3. Fill in crew member details (first name, last name, date of birth, gender, license number, club affiliation)
4. Save

Admin creation bypasses registration period date restrictions.

### Edit Crew Member

Administrators can edit any crew member regardless of date restrictions:
1. Click the edit button on a crew member row
2. Modify the desired fields
3. Save

Changes are allowed even after registration period or payment deadline.

### Delete Crew Member

Administrators can delete crew members regardless of date restrictions, with one exception:
- **Cannot delete** a crew member who is currently assigned to a boat
- The crew member must first be unassigned from any boat before deletion

## Date Restriction Bypass

Unlike club managers, administrators are not restricted by event phases:

| Action | Club Manager | Admin |
|--------|-------------|-------|
| Create crew member | Only during registration | Any time |
| Edit crew member | Only during registration | Any time |
| Delete crew member | Only during registration (if unassigned) | Any time (if unassigned) |

## Audit Logging

All admin actions on crew members are logged with:
- Timestamp
- Admin user ID
- Action performed (create, update, delete)
- Affected crew member ID
- Changes made

## Related Documentation

- [License Verification](./license-verification.md) — License verification workflow
- [Admin Boat Registrations](./admin-boat-registrations.md) — Boat registration management
- [Centralized Access Control](./centralized-access-control.md) — Permission system
- [Event Phases](./event-phases.md) — Event phase restrictions
