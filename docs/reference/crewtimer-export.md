# CrewTimer Export

## Overview

The CrewTimer export generates an Excel file compatible with [CrewTimer.com](https://crewtimer.com) timing software. The export includes race information, crew registrations (boat registrations in the database), crew details, and supports full internationalization (English/French).

> **Terminology Note:** In the database and API, crew registrations are called "boat registrations" or "boats". In the user interface, these are displayed as "Crews" or "Équipages". This documentation uses both terms interchangeably to match the codebase.

## Features

- **Internationalization**: Full race name and short name translation (English/French)
- **Smart Sorting**: Uses database `display_order` column for consistent race ordering
- **Crew Filtering**: Exports only complete, paid, or free crews (excludes forfeits and incomplete registrations)
- **Crew Information**: Includes stroke seat names and average crew age
- **Club Affiliation**: Automatically includes club manager club information

## Export Format

### Excel Columns

| Column | Description | Example |
|--------|-------------|---------|
| Event Time | Start time in 12-hour format (H:MM:SS AM/PM) | 7:45:00 AM, 9:00:30 AM |
| Event Num | Sequential event number | 1, 2, 3... |
| Event | Full translated race name | `WOMEN-MASTER-COXED QUAD SCULL YOLETTE` (EN)<br>`FEMMES-MASTER-QUATRE DE COUPLE BARRÉ YOLETTE` (FR) |
| Event Abbrev | Translated short name code | `MW4X+Y` (EN)<br>`MF4X+Y` (FR) |
| Crew | Comma-separated list of clubs from crew members | `RCPM`, `Club Elite, RCPM, SN Versailles` |
| Crew Abbrev | Full boat club display (may include Multi-Club or external crew indicators) | `RCPM`, `RCPM (Multi-Club)`, `RCPM (SN Versailles)` |
| Stroke | Last name of stroke seat rower | `Wilson` |
| Bow | Global sequential bow number | 1, 2, 3... |
| Race Info | Race type | `Head` |
| Status | Registration status (empty) | |
| Age | Average age of crew members | 35 |
| Handicap | Handicap value (reserved for future use) | (empty) |
| Note | Comma-separated list of crew member names | `Alice Martin, Bob Dupont, Charlie Bernard` |

### Race Timing

**Marathon Races (42km):**
- All boats start at the same time
- Start time configured in event settings (default: 7:45 AM)
- All marathon skiffs are positioned according to race order but start simultaneously

**Semi-Marathon Races (21km):**
- Boats start with intervals
- First boat starts at configured time (default: 9:00 AM)
- Each subsequent boat starts after a configured interval (default: 30 seconds)
- Example with 30-second intervals:
  - Boat 1: 9:00:00 AM
  - Boat 2: 9:00:30 AM
  - Boat 3: 9:01:00 AM

**Configuration:**
Race timing is configured in Admin → Event Configuration:
- Marathon Start Time (HH:MM format)
- Semi-Marathon Start Time (HH:MM format)
- Semi-Marathon Interval (10-300 seconds)

### Race Sorting

Races are sorted by the `display_order` column (1-55):
- **Marathon races (42km)**: Orders 1-14
- **Semi-marathon races (21km)**: Orders 15-55

If `display_order` is not available, falls back to distance-based sorting (marathon first, then semi-marathon).

### Boat Sorting Within Races

Within each race, boats (crews) are sorted by:
1. **Average age (descending)**: Oldest crews start first
2. **Registration order**: If ages are equal, boats maintain their registration order (by boat_registration_id)

This ordering ensures that older crews have priority positioning within their race category, which is a common practice in master rowing competitions.

## Internationalization

### Short Name Translation

Short name format: `[AgeCategory][Gender][BoatType]`

**Translation Rules:**
- **Age category** (first position): M, S, J16, J18 → **NOT translated**
- **Gender marker** (second position): **Translated**
  - M (Men) → H (Homme)
  - W (Women) → F (Femme)
  - X (Mixed) → M (Mixte)
- **Boat type** (remaining): 1X, 4X+, 8+, etc. → **NOT translated**

**Examples:**
- `MW4X+Y` → `MF4X+Y` (Master Women → Master Femme)
- `SM8+` → `SH8+` (Senior Men → Senior Homme)
- `J16X4+` → `J16M4+` (Junior 16 Mixed → Junior 16 Mixte)

### Full Race Name Translation

Full race names are translated using the i18n system (`frontend/src/locales/fr.json`):

**English:**
```
WOMEN-MASTER-COXED QUAD SCULL YOLETTE
```

**French:**
```
FEMMES-MASTER-QUATRE DE COUPLE BARRÉ YOLETTE
```

## Implementation

### Backend API

**Endpoint:** `GET /admin/export/races-json`

**Response Structure:**
```json
{
  "success": true,
  "data": {
    "config": {
      "competition_date": "2025-05-01"
    },
    "races": [
      {
        "race_id": "SM01",
        "name": "WOMEN-MASTER-COXED QUAD SCULL YOLETTE",
        "distance": 21,
        "event_type": "21km",
        "boat_type": "4X+",
        "age_category": "master",
        "gender_category": "women",
        "display_order": 15,
        "short_name": "MW4X+Y"
      }
    ],
    "boats": [...],
    "crew_members": [...],
    "team_managers": [...]
  }
}
```

**File:** `functions/admin/export_races_json.py`

### Frontend Formatter

**File:** `frontend/src/utils/exportFormatters/crewTimerFormatter.js`

**Key Functions:**
- `formatRacesToCrewTimer(jsonData, locale, t)` - Converts JSON to CrewTimer format
- `downloadCrewTimerExcel(jsonData, filename, locale, t)` - Generates and downloads Excel file
- `translateShortNameToFrench(shortName)` - Translates gender markers in short names
- `calculateAverageAge(crewMembers)` - Helper function for age calculation (kept for backward compatibility, but main export uses pre-calculated `crew_composition.avg_age`)
- `getStrokeSeatName(seats, crewMembersDict)` - Extracts stroke seat rower name

**Usage:**
```javascript
import { downloadCrewTimerExcel } from '@/utils/exportFormatters'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

// Export with current locale
downloadCrewTimerExcel(response.data, null, locale.value, t)
```

## Testing

### Manual Testing

1. **English Export:**
   - Set browser language to English
   - Log in as admin
   - Navigate to Data Export page
   - Click "Export to CrewTimer"
   - Verify:
     - Event column shows English race names
     - Event Abbrev shows English short codes (e.g., `MW4X+Y`)
     - Races are in correct order (1-55)

2. **French Export:**
   - Set browser language to French
   - Repeat export process
   - Verify:
     - Event column shows French race names
     - Event Abbrev shows French short codes (e.g., `MF4X+Y`)
     - Gender markers are translated (W→F, M→H, X→M)

### Automated Tests

**File:** `frontend/src/utils/exportFormatters/crewTimerFormatter.test.js`

Run tests:
```bash
node frontend/src/utils/exportFormatters/crewTimerFormatter.test.js
```

**Test Coverage:**
- Boat filtering (complete/paid/free, exclude forfait)
- Race sorting (marathon before semi-marathon, display_order)
- Event numbering (same race = same event number)
- Bow numbering (global sequential)
- Stroke seat extraction
- Average age calculation
- Empty dataset handling
- Invalid data format error handling
- Complete integration test

## Boat Filtering Rules

Only boats with the following statuses are included:
- `complete` - Registration complete, awaiting payment
- `paid` - Payment received
- `free` - Free registration (RCPM members)

**Excluded:**
- `incomplete` - Registration not finished
- `forfait: true` - Boat has forfeited

## Stroke Seat Determination

The stroke seat is the **highest position rower** (not coxswain):
- For a coxed four (4+): Position 4 is stroke
- For a skiff (1X): Position 1 is stroke
- For an eight (8+): Position 8 is stroke

## Club Name Handling

The CrewTimer export uses a specific approach for club names to provide comprehensive information:

**Crew Column:**
- Contains comma-separated list of all unique clubs from crew members
- Taken directly from the `club_list` field calculated by the backend
- Examples:
  - Single club: `RCPM`
  - Multi-club: `Club Elite, RCPM, SN Versailles`
  - Empty if no crew members: (empty)

**Crew Abbrev Column:**
- Contains the full `boat_club_display` value
- May include indicators for multi-club or external crews
- Examples:
  - Single club: `RCPM`
  - Multi-club crew: `RCPM (Multi-Club)`
  - External crew: `RCPM (SN Versailles)`

**Note Column:**
- Contains comma-separated list of all crew member names
- Format: `FirstName LastName, FirstName LastName, ...`
- Includes all crew members from the seats (rowers and coxswains)
- Examples:
  - Single rower: `Alice Martin`
  - Multiple crew: `Alice Martin, Bob Dupont, Charlie Bernard, Diana Petit`
  - Empty if no crew members: (empty)

This approach ensures that:
1. The Crew column provides a clean list of participating clubs
2. The Crew Abbrev column shows the formatted club display with context
3. The Note column provides complete crew member information for reference

## Average Age Calculation

Average age is calculated by the backend in the `crew_composition` object:
1. Backend calculates age for each crew member: `competition_year - birth_year`
2. Backend calculates average age of **rowers only** (excluding coxswains)
3. Frontend uses the pre-calculated `boat.crew_composition.avg_age` value
4. Result is rounded to nearest integer for display

**Note:** The backend handles age calculation to ensure consistency across the application. The frontend simply uses the pre-calculated value from `crew_composition.avg_age`, which is more efficient and avoids redundant calculations.

## Future Enhancements

- Support additional languages (Spanish, German, etc.)
- Add locale selector in export UI
- Translate boat type abbreviations in short names
- Export multiple formats simultaneously (CSV + Excel)

## Related Documentation

- [API Endpoints](./api-endpoints.md)
- [Admin API](./auth-api.md)
- [Project Structure](./project-structure.md)

## Change History

### 2026-01-02: Crew Member Names in Note Column
- Changed Note column to contain comma-separated list of crew member names (FirstName LastName)
- Changed Crew column to contain comma-separated list of clubs from club_list
- Crew Abbrev remains as boat_club_display for full context
- Provides complete crew roster information in the export

### 2026-01-02: Club Name Handling for CrewTimer Compatibility
- Changed Crew column to contain only team manager's club name (for CrewTimer software compatibility)
- Changed Crew Abbrev column to contain full boat_club_display (including Multi-Club or external crew indicators)
- This ensures CrewTimer software can properly parse the club name while preserving full club information in Crew Abbrev

### 2026-01-02: Additional Export Columns
- Added Handicap column (empty, reserved for future use)
- Added Note column containing comma-separated list of all clubs in the crew
- Note column uses the `club_list` field from boat data, which includes all unique clubs from crew members

### 2024-12-27: Boat Ordering Within Races
- Added sorting of boats within each race by average age (oldest first)
- Maintains registration order as secondary sort criterion when ages are equal
- Ensures consistent and fair positioning for master categories

### 2024-12-24: Use Pre-calculated Average Age
- Optimized to use `boat.crew_composition.avg_age` from backend instead of recalculating
- More efficient: avoids iterating through crew members and recalculating ages
- More consistent: uses the same age calculation logic as the rest of the application
- Backend calculates average age of rowers only (excluding coxswains) per competition rules

### 2024-12-24: Age Calculation Fix
- Fixed age ordering bug in CrewTimer export
- Changed to use backend-provided `age` field instead of recalculating from `date_of_birth`
- Ensures consistent age calculation across the application
- Removed `competitionDate` parameter from `calculateAverageAge()` function

### 2024-12-24: Internationalization
- Added full i18n support for race names and short codes
- Implemented gender marker translation (W→F, M→H, X→M)
- Separated Event and Event Abbrev columns
- Added translation function parameter to formatters

### 2024-12-24: Display Order
- Added `display_order` column support for race sorting
- Added `short_name` column to race export
- Implemented fallback to distance-based sorting
- Updated frontend formatter to use display_order

### Previous
- Initial CrewTimer export implementation
- Basic race sorting by distance
- Boat filtering by status
- Stroke seat and average age calculations
