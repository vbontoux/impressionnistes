# Export Formatters

This directory contains utilities for transforming JSON data from the backend API into various export formats (CSV, Excel, etc.).

## Architecture

The export system follows a clean separation of concerns:
- **Backend**: Provides raw JSON data via API endpoints
- **Frontend Formatters**: Transform JSON into specific export formats

This architecture makes it easy to add new export formats without backend changes.

## Files

### Formatters
- `crewMembersFormatter.js` - Converts crew member data to CSV
- `boatRegistrationsFormatter.js` - Converts boat registration data to CSV
- `crewTimerFormatter.js` - Converts race data to CrewTimer Excel format
- `shared.js` - Shared utility functions (CSV escaping, date formatting, etc.)
- `index.js` - Main export file

### Tests
- `crewMembersFormatter.test.js` - Tests for crew members formatter (22 tests)
- `boatRegistrationsFormatter.test.js` - Tests for boat registrations formatter (33 tests)
- `crewTimerFormatter.test.js` - Tests for CrewTimer formatter (46 tests)
- `runTests.sh` - Script to run all tests

## Running Tests

Run all formatter tests:
```bash
cd frontend/src/utils/exportFormatters
./runTests.sh
```

Run individual test files:
```bash
node crewMembersFormatter.test.js
node boatRegistrationsFormatter.test.js
node crewTimerFormatter.test.js
```

## Test Coverage

### Crew Members Formatter (22 tests)
- ✓ CSV structure and headers
- ✓ Special character escaping (commas, quotes, newlines)
- ✓ Empty dataset handling
- ✓ Missing field handling
- ✓ Invalid data format error handling
- ✓ Multiple crew members

### Boat Registrations Formatter (33 tests)
- ✓ CSV structure and headers
- ✓ Filled seats calculation (from crew_composition or seats array)
- ✓ Boolean formatting (Yes/No)
- ✓ Nested data handling (crew_composition fields)
- ✓ Empty dataset handling
- ✓ Missing field handling
- ✓ Invalid data format error handling
- ✓ Multiple boats

### CrewTimer Formatter (46 tests)
- ✓ Boat filtering (complete/paid/free, exclude forfait)
- ✓ Race sorting (marathon before semi-marathon)
- ✓ Event numbering (same race = same event num)
- ✓ Bow numbering (global sequential)
- ✓ Semi-marathon race name formatting
- ✓ Marathon race name unchanged
- ✓ Gender mapping (MAN/WOMAN/MIXED)
- ✓ Yolette detection (Y marker)
- ✓ Stroke seat extraction (highest position rower)
- ✓ Average age calculation
- ✓ Empty dataset handling
- ✓ Invalid data format error handling
- ✓ Complete integration test

## Usage Examples

### Crew Members Export
```javascript
import { downloadCrewMembersCSV } from './exportFormatters';

// Fetch data from API
const response = await fetch('/api/admin/export/crew-members');
const jsonData = await response.json();

// Download as CSV
downloadCrewMembersCSV(jsonData);
```

### Boat Registrations Export
```javascript
import { downloadBoatRegistrationsCSV } from './exportFormatters';

const response = await fetch('/api/admin/export/boat-registrations');
const jsonData = await response.json();

downloadBoatRegistrationsCSV(jsonData);
```

### CrewTimer Export
```javascript
import { downloadCrewTimerExcel } from './exportFormatters';

const response = await fetch('/api/admin/export/races');
const jsonData = await response.json();

downloadCrewTimerExcel(jsonData);
```

## CrewTimer Format Specification

The CrewTimer formatter produces Excel files with the following columns:
- **Event Time**: Empty (filled in by CrewTimer)
- **Event Num**: Sequential number per race (same race = same event num)
- **Event**: Race name (formatted for semi-marathon, original for marathon)
- **Event Abbrev**: Same as Event
- **Crew**: Club name
- **Crew Abbrev**: Same as Crew
- **Stroke**: Last name of stroke seat rower (highest position)
- **Bow**: Global sequential bow number (1, 2, 3, ...)
- **Race Info**: "Head" (race type)
- **Status**: Empty (filled in by CrewTimer)
- **Age**: Average age of crew members

### Race Name Formatting Rules

**Semi-Marathon (21km):**
- Pattern: `boat_type [Y if yolette] age_category gender_category`
- Example: `4+ Y J16 WOMAN` (yolette race)
- Example: `1X SENIOR MAN` (non-yolette)

**Marathon (42km):**
- Original race name from database unchanged
- Example: `1X SENIOR MAN`

### Boat Filtering Rules
- Include: `complete`, `paid`, `free` status
- Exclude: `incomplete` status
- Exclude: boats marked as `forfait: true`

### Race Sorting Rules
- Marathon races (42km) appear first
- Semi-marathon races (21km) appear after
- Within each distance, races maintain database order

## Adding New Export Formats

To add a new export format:

1. Create a new formatter file (e.g., `myFormatFormatter.js`)
2. Implement format conversion function
3. Implement download function
4. Export functions in `index.js`
5. Create test file (e.g., `myFormatFormatter.test.js`)
6. Add test to `runTests.sh`

Example:
```javascript
// myFormatFormatter.js
export function formatToMyFormat(jsonData) {
  // Transform JSON to your format
  return formattedData;
}

export function downloadMyFormat(jsonData, filename = null) {
  const content = formatToMyFormat(jsonData);
  // Create blob and download
}
```

## Dependencies

- `xlsx` - Excel file generation (for CrewTimer export)
- No other external dependencies (CSV generation is custom)

## Notes

- CSV escaping handles commas, quotes, and newlines correctly
- All formatters validate input data and throw descriptive errors
- Empty datasets are handled gracefully (headers only for CSV, empty array for CrewTimer)
- Missing fields result in empty values (not errors)
- All tests use simple console-based assertions (no test framework required)
