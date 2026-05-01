# License Verification Guide

## Overview

The license verification system allows administrators to verify crew member rowing licenses and persist the results. It supports both automatic verification via FFAviron intranet and manual verification as a fallback.

**Spec Reference:** FR-24 (License Verification Persistence), FR-27 (Admin Boat License Status)

## Verification Methods

### Automatic Verification

1. Navigate to the license checker page (Admin → License Checker)
2. Select crew members to verify
3. Click "Check Licenses" — the system queries FFAviron intranet
4. Review results (valid/invalid for each crew member)
5. Click "Save Verification Results" to persist selected results

### Manual Verification (Valid)

When automatic verification is unavailable:
1. Select one or more crew members
2. Click "Mark as Valid"
3. Status is immediately saved as `manually_verified_valid`
4. Verification date and admin ID are recorded

### Manual Verification (Invalid)

1. Select one or more crew members
2. Click "Mark as Invalid"
3. Status is immediately saved as `manually_verified_invalid`
4. Verification date and admin ID are recorded

## Verification Statuses

| Status | Badge Color | Meaning |
|--------|-------------|---------|
| `pending` | Grey | Not yet verified (default) |
| `verified_valid` | Green | Automatically verified as valid |
| `verified_invalid` | Red | Automatically verified as invalid |
| `manually_verified_valid` | Green | Manually marked as valid by admin |
| `manually_verified_invalid` | Red | Manually marked as invalid by admin |

## Database Fields (Crew Member)

| Field | Type | Description |
|-------|------|-------------|
| `license_verification_status` | String | One of the statuses above |
| `license_verification_date` | Timestamp | When verification was performed |
| `license_verified_by` | String | Admin user ID who performed verification |

## Admin Boat License Status (FR-27)

The admin boat list displays an aggregated license status per boat:

| Display | Badge | Condition |
|---------|-------|-----------|
| **Verified** | Green | ALL crew members have valid licenses (`verified_valid` or `manually_verified_valid`) |
| **Invalid** | Red | ANY crew member has invalid or unverified license |
| **-** | None | No crew members assigned to the boat |

This column appears in both table view and card view. It is informational only (not clickable).

The status updates automatically when individual crew member verification statuses change.

## Re-verification

To re-verify a crew member with an invalid license:
1. Navigate to the license checker
2. Select the crew member
3. Run automatic verification again, or manually mark as valid
4. The new status overwrites the previous one

## Exports

License verification status is included in:
- Crew member CSV export
- Event program export (Sheet 1)
- Admin crew member list

## Permissions

- Only administrators can verify licenses
- Team managers can view verification status but cannot modify it
- Verification actions are logged with admin ID and timestamp

## Related Documentation

- [License Checker Guide](./license-checker-guide.md) — Detailed FFAviron integration guide
- [Admin Crew Members](./admin-crew-members.md) — Crew member management
- [Terminology](../../reference/terminology.md) — Standard terminology
