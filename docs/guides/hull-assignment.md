# Hull Assignment Guide

## Overview

Hull assignment allows team managers to optionally request a physical boat (hull) from the event organizers when creating or editing a crew registration. Administrators can then assign specific boats to fulfill these requests.

**Spec Reference:** FR-26 (Boat Hull Assignment Requests)

## How It Works

### For Team Managers

1. **Enable the request:** When creating or editing a crew, toggle the "Request a boat" option
2. **Describe your needs:** Optionally enter a comment (up to 500 characters) describing your boat requirements (e.g., weight range, boat type preference)
3. **Wait for assignment:** An administrator will review your request and assign a specific boat
4. **View assignment:** Once assigned, the boat name and any admin comments appear on your crew registration (read-only)

### For Administrators

1. **View requests:** In the admin boat list, boats with active hull requests are flagged
2. **Assign a boat:** Enter the boat identifier (name or number) in the assignment field
3. **Add a comment:** Optionally add a comment (e.g., dock location, pickup instructions)
4. **Save:** The assignment is immediately visible to the team manager

## Database Fields

| Field | Type | Description |
|-------|------|-------------|
| `boat_request_enabled` | Boolean | Whether the team manager has requested a boat |
| `boat_request_comment` | String (max 500 chars) | Team manager's description of boat requirements |
| `assigned_boat_identifier` | String | Admin-assigned boat name/number |
| `assigned_boat_comment` | String | Admin comment about the assignment |

## Display Format

When a boat has been assigned, it is displayed as:
- **With comment:** `"Skiff 3 - Dock B, arrive 30min early"`
- **Without comment:** `"Skiff 3"`

This format appears in:
- Team manager crew detail view
- Admin boat list
- Event program export (Sheet 1, "Assigned Boat" column)
- CrewTimer export

## Key Rules

- Hull assignment is **optional** — boats can proceed without one
- The request toggle defaults to **off**
- Disabling the toggle clears any existing request comment
- Only administrators can set the assigned boat identifier and comment
- Team managers see the assignment as read-only
- Hull assignment does not affect registration status (a crew can be "complete" without a hull)

## Pricing Impact

Hull assignment itself does not affect pricing. Boat rental fees are calculated separately based on whether the crew uses an RCPM boat (see [Terminology — Pricing](../reference/terminology.md)).

## Related Documentation

- [Terminology — Hull Assignment](../reference/terminology.md#hull-assignment)
- [Terminology — Boat Number](../reference/terminology.md#boat-number)
- [Event Program Export](../reference/event-program-export.md)
