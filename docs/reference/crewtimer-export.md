# CrewTimer Export

## Overview

The CrewTimer export generates an Excel file compatible with [CrewTimer.com](https://crewtimer.com) timing software. The export includes race information, boat registrations, crew details, and supports full internationalization (English/French).

## Features

- **Internationalization**: Full race name and short name translation (English/French)
- **Smart Sorting**: Uses database `display_order` column for consistent race ordering
- **Boat Filtering**: Exports only complete, paid, or free boats (excludes forfeits and incomplete registrations)
- **Crew Information**: Includes stroke seat names and average crew age
- **Club Affiliation**: Automatically includes team manager club information

## Export Format

### Excel Columns

| Column | Description | Example |
|--------|-------------|---------|
| Event Time | Start time (empty for head races) | |
| Event Num | Sequential event number | 1, 2, 3... |
| Event | Full translated race name | `WOMEN-MASTER-COXED QUAD SCULL YOLETTE` (EN)<br>`FEMMES-MASTER-QUATRE DE COUPLE BARRÉ YOLETTE` (FR) |
| Event Abbrev | Translated short name code | `MW4X+Y` (EN)<br>`MF4X+Y` (FR) |
| Crew | Club name | `ROWING CLUB DE PORT MARLY` |
| Crew Abbrev | Club abbreviation (same as Crew) | `RCPM` |
| Stroke | Last name of stroke seat rower | `Wilson` |
| Bow | Global sequential bow number | 1, 2, 3... |
| Race Info | Race type | `Head` |
| Status | Registration status (empty) | |
| Age | Average age of crew members | 35 |

### Race Sorting

Races are sorted by the `display_order` column (1-55):
- **Marathon races (42km)**: Orders 1-14
- **Semi-marathon races (21km)**: Orders 15-55

If `display_order` is not available, falls back to distance-based sorting (marathon first, then semi-marathon).

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
- `calculateAverageAge(crewMembers, competitionDate)` - Calculates crew average age
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

## Average Age Calculation

Average age is calculated from all crew members' dates of birth:
1. Extract birth year from each crew member's `date_of_birth`
2. Calculate age: `competition_year - birth_year`
3. Average all ages
4. Round to nearest integer

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
