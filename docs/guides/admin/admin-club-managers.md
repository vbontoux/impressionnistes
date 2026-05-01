# Admin Club Manager Management

## Overview

The admin club managers page allows administrators to view all club managers (team managers) and contact them individually or in bulk via email.

**Spec Reference:** FR-15 (Admin Club Manager Management)

## Accessing the Interface

Navigate to **Admin → Club Managers** from the admin navigation menu.

## Features

### View All Club Managers

The interface displays a table with all club managers showing:
- First name
- Last name
- Email (clickable mailto link)
- Club affiliation

### Search and Filter

- **Search:** Type in the search box to filter across name, email, and club affiliation
- **Sort:** Click column headers to sort by any field

### Individual Email

Click any email address in the table to open your default email client with that address pre-filled.

### Bulk Email

1. **Select managers:** Check the checkbox next to each manager you want to email, or click "Select All" to select everyone
2. **View count:** The selected count is displayed (e.g., "5 selected")
3. **Send email:** Click "Email Selected" to open your default email client with all selected addresses in the BCC field
4. **Deselect:** Click "Deselect All" to clear the selection

The "Email Selected" button is disabled when no managers are selected.

## Use Cases

- **Announce registration opening:** Select all managers, send announcement
- **Payment reminders:** Filter by club, select managers with outstanding balances
- **Race day logistics:** Contact specific club managers about boat assignments
- **Issue follow-up:** Email individual managers about flagged crew member issues

## API

**Endpoint:** `GET /admin/team-managers`

Returns all team managers with their profile information. This endpoint is admin-only.

## Related Documentation

- [Admin Impersonation](./admin-impersonation.md) — View system as a specific team manager
- [Admin Crew Members](./admin-crew-members.md) — Manage crew members across all managers
- [Admin Boat Registrations](./admin-boat-registrations.md) — Manage boat registrations
