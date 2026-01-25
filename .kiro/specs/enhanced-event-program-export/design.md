# Design Document: Enhanced Event Program Export

## Overview

This design specifies the implementation of an enhanced event program export feature that generates a comprehensive 4-sheet Excel file for race day operations. The implementation is entirely frontend-based, leveraging the existing `/admin/export/races-json` backend endpoint and the xlsx library for Excel file generation.

The enhancement transforms the current 2-sheet export (basic crew list + race schedule) into a 4-sheet export that includes:
1. Enhanced crew member list with detailed personal information
2. Existing race schedule (preserved unchanged)
3. Crews organized by race with full member details
4. Club manager synthesis with participation statistics

This design prioritizes code reusability by extracting shared logic into utility functions, maintains consistency with existing export patterns, and ensures proper localization support for both French and English outputs.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Admin Dashboard UI                       │
│                  (ExportRaceProgram.vue)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ User clicks "Export Program"
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Export Orchestration Layer                      │
│           (exportEventProgram composable)                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ 1. Fetch data
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend API Endpoint                        │
│              GET /admin/export/races-json                    │
│         (Returns races, boats, crew members, etc.)           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ 2. Transform data
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Transformation Layer                       │
│         (Sheet-specific transformer functions)               │
│  • transformCrewMemberList()                                 │
│  • transformRaceSchedule()                                   │
│  • transformCrewsInRaces()                                   │
│  • transformSynthesis()                                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ 3. Generate Excel
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Excel Generation Layer                          │
│              (xlsx library + utilities)                      │
│  • createWorkbook()                                          │
│  • addSheet()                                                │
│  • formatHeaders()                                           │
│  • autoSizeColumns()                                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ 4. Download file
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Browser Download                          │
│            (event-program-YYYY-MM-DD.xlsx)                   │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**ExportRaceProgram.vue (UI Component)**
- Provides export button in admin dashboard
- Handles user interaction and loading states
- Displays success/error messages
- Manages locale context

**exportEventProgram.js (Composable)**
- Orchestrates the entire export process
- Fetches data from backend API
- Coordinates data transformation
- Triggers Excel file generation and download
- Handles error states and user feedback

**eventProgramTransformers.js (Utility Module)**
- Contains sheet-specific data transformation functions
- Filters eligible boats (complete, paid, free status)
- Maps backend data structures to sheet row formats
- Handles missing/optional data gracefully

**excelGenerator.js (Utility Module)**
- Wraps xlsx library functionality
- Creates workbook and sheets
- Applies formatting (headers, column widths)
- Generates downloadable file blob

### Technology Stack

- **Frontend Framework**: Vue 3 Composition API
- **Excel Library**: xlsx (SheetJS)
- **HTTP Client**: Existing API service layer
- **Localization**: Vue I18n
- **State Management**: Composable pattern (no Vuex needed)

## Components and Interfaces

### 1. ExportRaceProgram.vue Component

**Purpose**: UI component that triggers the export process

**Template Structure**:
```vue
<template>
  <div class="export-section">
    <BaseButton
      variant="primary"
      :loading="isExporting"
      :disabled="isExporting"
      @click="handleExport"
    >
      {{ $t('admin.export.eventProgram') }}
    </BaseButton>
    
    <MessageAlert
      v-if="errorMessage"
      type="error"
      :message="errorMessage"
      :dismissible="true"
      @dismiss="errorMessage = ''"
    />
  </div>
</template>
```

**Script Interface**:
```javascript
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { exportEventProgram } from '@/composables/exportEventProgram'
import BaseButton from '@/components/BaseButton.vue'
import MessageAlert from '@/components/MessageAlert.vue'

export default {
  components: { BaseButton, MessageAlert },
  setup() {
    const { t, locale } = useI18n()
    const isExporting = ref(false)
    const errorMessage = ref('')
    
    const handleExport = async () => {
      isExporting.value = true
      errorMessage.value = ''
      
      try {
        await exportEventProgram(locale.value)
      } catch (error) {
        errorMessage.value = t('admin.export.error')
        console.error('Export failed:', error)
      } finally {
        isExporting.value = false
      }
    }
    
    return { isExporting, errorMessage, handleExport }
  }
}
```

### 2. exportEventProgram Composable

**Purpose**: Orchestrates the export process from data fetching to file download

**File**: `frontend/src/composables/exportEventProgram.js`

**Interface**:
```javascript
/**
 * Exports the enhanced event program as a 4-sheet Excel file
 * @param {string} locale - Current locale ('fr' or 'en')
 * @returns {Promise<void>}
 * @throws {Error} If API call fails or data is invalid
 */
export async function exportEventProgram(locale) {
  // 1. Fetch data from backend
  const data = await fetchRaceData()
  
  // 2. Validate data
  validateExportData(data)
  
  // 3. Transform data for each sheet
  const sheet1Data = transformCrewMemberList(data, locale)
  const sheet2Data = transformRaceSchedule(data, locale)
  const sheet3Data = transformCrewsInRaces(data, locale)
  const sheet4Data = transformSynthesis(data, locale)
  
  // 4. Generate Excel file
  const workbook = createWorkbook()
  addSheet(workbook, getSheetName('crewMemberList', locale), sheet1Data)
  addSheet(workbook, getSheetName('raceSchedule', locale), sheet2Data)
  addSheet(workbook, getSheetName('crewsInRaces', locale), sheet3Data)
  addSheet(workbook, getSheetName('synthesis', locale), sheet4Data)
  
  // 5. Download file
  const filename = `event-program-${formatDate(new Date())}.xlsx`
  downloadWorkbook(workbook, filename)
}
```

**Dependencies**:
- API service for `/admin/export/races-json`
- Transformer functions from `eventProgramTransformers.js`
- Excel utilities from `excelGenerator.js`
- I18n for localized sheet names

### 3. eventProgramTransformers.js Module

**Purpose**: Transforms backend JSON data into sheet-specific row arrays

**File**: `frontend/src/utils/eventProgramTransformers.js`

**Key Functions**:

```javascript
/**
 * Filters boats to only include eligible statuses
 * @param {Array} boats - All boats from backend
 * @returns {Array} Filtered boats (complete, paid, free only)
 */
export function filterEligibleBoats(boats) {
  const eligibleStatuses = ['complete', 'paid', 'free']
  return boats.filter(boat => eligibleStatuses.includes(boat.registration_status))
}

/**
 * Transforms data for Sheet 1: Enhanced Crew Member List
 * @param {Object} data - Backend JSON response
 * @param {string} locale - Current locale
 * @returns {Array<Array>} 2D array with headers and data rows
 */
export function transformCrewMemberList(data, locale) {
  const headers = getCrewMemberListHeaders(locale)
  const eligibleBoats = filterEligibleBoats(data.boats)
  
  const rows = []
  for (const boat of eligibleBoats) {
    const race = findRaceForBoat(boat, data.races)
    const raceNumber = getRaceNumber(race)
    const raceName = getRaceName(race, locale)
    
    for (const seat of boat.seats) {
      const member = findCrewMember(seat.crew_member_id, data.crew_members)
      const assignedBoat = formatAssignedBoat(boat)
      
      rows.push([
        raceNumber,
        raceName,
        boat.boat_number,
        member.last_name,
        member.first_name,
        member.club_affiliation,
        member.age,
        member.gender,
        member.license_number,
        seat.seat_type,
        boat.boat_number, // Bow number
        assignedBoat
      ])
    }
  }
  
  return [headers, ...rows]
}

/**
 * Transforms data for Sheet 2: Race Schedule (existing format)
 * @param {Object} data - Backend JSON response
 * @param {string} locale - Current locale
 * @returns {Array<Array>} 2D array with headers and data rows
 */
export function transformRaceSchedule(data, locale) {
  // Reuse existing race schedule transformation logic
  // This sheet remains unchanged from current implementation
  const headers = getRaceScheduleHeaders(locale)
  const rows = data.races.map(race => [
    race.race_number,
    getRaceName(race, locale),
    race.start_time,
    // ... other existing columns
  ])
  
  return [headers, ...rows]
}

/**
 * Transforms data for Sheet 3: Crews in Races
 * @param {Object} data - Backend JSON response
 * @param {string} locale - Current locale
 * @returns {Array<Array>} 2D array with headers and data rows
 */
export function transformCrewsInRaces(data, locale) {
  const headers = getCrewsInRacesHeaders(locale)
  const eligibleBoats = filterEligibleBoats(data.boats)
  
  // Sort boats by race number
  const sortedBoats = sortBoatsByRace(eligibleBoats, data.races)
  
  const rows = []
  for (const boat of sortedBoats) {
    const race = findRaceForBoat(boat, data.races)
    const raceNumber = getRaceNumber(race)
    const raceName = getRaceName(race, locale)
    const assignedBoat = formatAssignedBoat(boat)
    
    // Build row with race info and boat assignment
    const row = [raceNumber, raceName, boat.boat_number, assignedBoat]
    
    // Add up to 9 crew member columns (5 fields each)
    const members = getCrewMembersForBoat(boat, data.crew_members)
    for (let i = 0; i < 9; i++) {
      if (i < members.length) {
        const member = members[i]
        row.push(
          member.last_name,
          member.first_name,
          member.club_affiliation,
          member.age,
          member.gender
        )
      } else {
        // Empty columns for missing members
        row.push('', '', '', '', '')
      }
    }
    
    rows.push(row)
  }
  
  return [headers, ...rows]
}

/**
 * Transforms data for Sheet 4: Synthesis by Club Manager
 * @param {Object} data - Backend JSON response
 * @param {string} locale - Current locale
 * @returns {Array<Array>} 2D array with headers and data rows
 */
export function transformSynthesis(data, locale) {
  const headers = getSynthesisHeaders(locale)
  const eligibleBoats = filterEligibleBoats(data.boats)
  
  // Group boats by team manager
  const managerStats = {}
  
  for (const boat of eligibleBoats) {
    const manager = findTeamManagerForBoat(boat, data.team_managers)
    if (!manager) continue
    
    if (!managerStats[manager.team_manager_id]) {
      managerStats[manager.team_manager_id] = {
        manager,
        assignedBoats: 0,
        marathonCrews: 0,
        semiMarathonCrews: 0
      }
    }
    
    const stats = managerStats[manager.team_manager_id]
    
    // Count assigned boats
    if (boat.assigned_boat_identifier) {
      stats.assignedBoats++
    }
    
    // Count by event type
    if (boat.event_type === 'Marathon') {
      stats.marathonCrews++
    } else if (boat.event_type === 'Semi-Marathon') {
      stats.semiMarathonCrews++
    }
  }
  
  // Convert to rows
  const rows = Object.values(managerStats).map(stats => [
    stats.manager.club_affiliation,
    `${stats.manager.first_name} ${stats.manager.last_name}`,
    stats.manager.email,
    stats.manager.phone || '',
    stats.assignedBoats,
    stats.marathonCrews,
    stats.semiMarathonCrews
  ])
  
  return [headers, ...rows]
}

/**
 * Formats assigned boat information
 * @param {Object} boat - Boat object
 * @returns {string} Formatted string "name - comment" or empty
 */
export function formatAssignedBoat(boat) {
  if (!boat.assigned_boat_name) return ''
  
  if (boat.assigned_boat_comment) {
    return `${boat.assigned_boat_name} - ${boat.assigned_boat_comment}`
  }
  
  return boat.assigned_boat_name
}

/**
 * Gets crew members for a boat in seat order
 * @param {Object} boat - Boat object
 * @param {Array} allMembers - All crew members
 * @returns {Array} Ordered crew members
 */
export function getCrewMembersForBoat(boat, allMembers) {
  return boat.seats
    .map(seat => findCrewMember(seat.crew_member_id, allMembers))
    .filter(member => member !== null)
}
```

**Helper Functions**:
```javascript
function findRaceForBoat(boat, races) {
  return races.find(r => 
    r.event_type === boat.event_type &&
    r.boat_type === boat.boat_type &&
    r.category === boat.category
  )
}

function findCrewMember(memberId, members) {
  return members.find(m => m.crew_member_id === memberId) || null
}

function findTeamManagerForBoat(boat, managers) {
  // Assumes boat has team_manager_id or similar reference
  return managers.find(m => m.team_manager_id === boat.team_manager_id)
}

function sortBoatsByRace(boats, races) {
  return boats.sort((a, b) => {
    const raceA = findRaceForBoat(a, races)
    const raceB = findRaceForBoat(b, races)
    return (raceA?.race_number || 0) - (raceB?.race_number || 0)
  })
}

function getRaceNumber(race) {
  return race?.race_number || 0
}

function getRaceName(race, locale) {
  if (!race) return ''
  // Use existing race naming logic
  return `${race.event_type} - ${race.boat_type} - ${race.category}`
}
```

### 4. excelGenerator.js Module

**Purpose**: Wraps xlsx library for workbook creation and file download

**File**: `frontend/src/utils/excelGenerator.js`

**Interface**:
```javascript
import * as XLSX from 'xlsx'

/**
 * Creates a new Excel workbook
 * @returns {Object} XLSX workbook object
 */
export function createWorkbook() {
  return XLSX.utils.book_new()
}

/**
 * Adds a sheet to the workbook with data and formatting
 * @param {Object} workbook - XLSX workbook
 * @param {string} sheetName - Name of the sheet
 * @param {Array<Array>} data - 2D array of data (headers + rows)
 */
export function addSheet(workbook, sheetName, data) {
  const worksheet = XLSX.utils.aoa_to_sheet(data)
  
  // Apply header formatting (bold)
  formatHeaders(worksheet, data[0].length)
  
  // Auto-size columns
  autoSizeColumns(worksheet, data)
  
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)
}

/**
 * Formats header row with bold text
 * @param {Object} worksheet - XLSX worksheet
 * @param {number} columnCount - Number of columns
 */
export function formatHeaders(worksheet, columnCount) {
  const range = XLSX.utils.decode_range(worksheet['!ref'])
  
  for (let col = range.s.c; col <= range.e.c; col++) {
    const cellAddress = XLSX.utils.encode_cell({ r: 0, c: col })
    if (!worksheet[cellAddress]) continue
    
    worksheet[cellAddress].s = {
      font: { bold: true }
    }
  }
}

/**
 * Auto-sizes columns based on content
 * @param {Object} worksheet - XLSX worksheet
 * @param {Array<Array>} data - 2D array of data
 */
export function autoSizeColumns(worksheet, data) {
  const colWidths = []
  
  // Calculate max width for each column
  data.forEach(row => {
    row.forEach((cell, colIndex) => {
      const cellValue = cell?.toString() || ''
      const cellWidth = cellValue.length
      colWidths[colIndex] = Math.max(colWidths[colIndex] || 10, cellWidth)
    })
  })
  
  // Apply widths (with max limit)
  worksheet['!cols'] = colWidths.map(width => ({
    wch: Math.min(width + 2, 50) // Add padding, max 50 chars
  }))
}

/**
 * Downloads workbook as Excel file
 * @param {Object} workbook - XLSX workbook
 * @param {string} filename - Desired filename
 */
export function downloadWorkbook(workbook, filename) {
  const wbout = XLSX.write(workbook, {
    bookType: 'xlsx',
    type: 'array'
  })
  
  const blob = new Blob([wbout], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  })
  
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  
  // Cleanup
  URL.revokeObjectURL(url)
}

/**
 * Formats date for filename
 * @param {Date} date - Date object
 * @returns {string} Formatted date YYYY-MM-DD
 */
export function formatDate(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
```

### 5. Localization Keys

**File**: `frontend/src/locales/en.json` and `fr.json`

**New Translation Keys**:
```json
{
  "admin": {
    "export": {
      "eventProgram": "Export Event Program",
      "error": "Failed to export event program. Please try again.",
      "noData": "No eligible boats found for export.",
      "sheets": {
        "crewMemberList": "Crew Member List",
        "raceSchedule": "Race Schedule",
        "crewsInRaces": "Crews in Races",
        "synthesis": "Synthesis"
      },
      "columns": {
        "raceNumber": "Race #",
        "raceName": "Race name",
        "crewNumber": "Crew #",
        "lastName": "Last name",
        "firstName": "First name",
        "club": "Club",
        "age": "Age",
        "gender": "Gender",
        "licenseNumber": "License #",
        "placeInBoat": "Place in boat",
        "bowNumber": "Bow number",
        "assignedBoat": "Assigned Boat",
        "boatAssignment": "Boat assignment",
        "email": "Email",
        "phone": "Phone #",
        "assignedBoatsCount": "Number of assigned boats",
        "marathonCrewsCount": "Number of crews in marathon",
        "semiMarathonCrewsCount": "Number of crews in semi-marathon",
        "fullName": "First name + Last name",
        "member": "Member"
      }
    }
  }
}
```

## Data Models

### Backend API Response

The `/admin/export/races-json` endpoint returns:

```typescript
interface ExportData {
  races: Race[]
  boats: Boat[]
  crew_members: CrewMember[]
  team_managers: TeamManager[]
  config: CompetitionConfig
}

interface Race {
  race_id: string
  event_type: 'Marathon' | 'Semi-Marathon'
  boat_type: string
  category: string
  start_time: string // HH:MM format
  race_number: number
}

interface Boat {
  boat_id: string
  boat_number: string
  registration_status: 'incomplete' | 'complete' | 'paid' | 'free' | 'forfait'
  event_type: 'Marathon' | 'Semi-Marathon'
  boat_type: string
  category: string
  assigned_boat_identifier: string | null
  assigned_boat_name: string | null
  assigned_boat_comment: string | null
  team_manager_id: string
  seats: Seat[]
}

interface Seat {
  seat_type: string // e.g., "Rower 1", "Rower 2", "Cox"
  crew_member_id: string
}

interface CrewMember {
  crew_member_id: string
  first_name: string
  last_name: string
  gender: 'M' | 'F'
  age: number
  license_number: string
  club_affiliation: string
}

interface TeamManager {
  team_manager_id: string
  first_name: string
  last_name: string
  email: string
  phone: string | null
  club_affiliation: string
}

interface CompetitionConfig {
  competition_date: string // YYYY-MM-DD
  race_start_time: string // HH:MM
  race_interval_minutes: number
}
```

### Sheet Data Structures

**Sheet 1: Enhanced Crew Member List**
```typescript
type CrewMemberRow = [
  raceNumber: number,
  raceName: string,
  crewNumber: string,
  lastName: string,
  firstName: string,
  club: string,
  age: number,
  gender: string,
  licenseNumber: string,
  placeInBoat: string,
  bowNumber: string,
  assignedBoat: string
]
```

**Sheet 2: Race Schedule**
```typescript
type RaceScheduleRow = [
  raceNumber: number,
  raceName: string,
  startTime: string,
  // ... other existing columns
]
```

**Sheet 3: Crews in Races**
```typescript
type CrewsInRacesRow = [
  raceNumber: number,
  raceName: string,
  crewNumber: string,
  boatAssignment: string,
  // 9 members × 5 fields = 45 additional columns
  member1LastName: string,
  member1FirstName: string,
  member1Club: string,
  member1Age: number,
  member1Gender: string,
  // ... repeat for members 2-9
]
```

**Sheet 4: Synthesis**
```typescript
type SynthesisRow = [
  club: string,
  fullName: string,
  email: string,
  phone: string,
  assignedBoatsCount: number,
  marathonCrewsCount: number,
  semiMarathonCrewsCount: number
]
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified several areas of redundancy:

1. **Eligible boat filtering** (1.1, 3.8, 4.8, 5.2, 5.3) - All refer to the same core filtering logic
2. **Localization** (1.9, 3.9, 4.9, 6.1, 6.2, 6.3, 7.2) - All refer to locale-based header/sheet name translation
3. **Required field presence** (1.2, 1.3, 1.4, 1.5, 2.3, 3.4) - Can be combined into comprehensive field validation properties
4. **Assigned boat formatting** (1.6, 3.6) - Same formatting rule applied in two sheets

These redundancies will be consolidated into comprehensive properties that validate the behavior once rather than multiple times.

### Properties

**Property 1: Eligible Boat Filtering**

*For any* collection of boats with mixed registration statuses, the transformed data for all sheets should only include boats with status 'complete', 'paid', or 'free', and should exclude all boats with status 'forfait'.

**Validates: Requirements 1.1, 3.8, 4.8, 5.2, 5.3**

---

**Property 2: Required Field Completeness in Crew Member List**

*For any* crew member from an eligible boat, the crew member list row should contain all required fields: race number, race name, crew number, last name, first name, club, age, gender, license number, seat position, bow number, and assigned boat (which may be empty).

**Validates: Requirements 1.2, 1.3, 1.4, 1.5**

---

**Property 3: Assigned Boat Formatting**

*For any* boat with assigned boat information, if both name and comment are present, the formatted string should be "name - comment"; if only name is present, it should be just the name; if neither is present, it should be an empty string.

**Validates: Requirements 1.6, 3.6**

---

**Property 4: Localization Consistency**

*For any* locale ('fr' or 'en'), all column headers and sheet names in the generated workbook should be translated to that locale using the i18n translation keys.

**Validates: Requirements 1.9, 3.9, 4.9, 6.1, 6.2, 6.3, 7.2**

---

**Property 5: Variable Crew Size Handling**

*For any* boat with N crew members (where N ≤ 9), the Crews in Races row should contain complete data for the first N member positions and empty strings for all remaining positions up to 9.

**Validates: Requirements 3.3, 3.5**

---

**Property 6: Crew Member Field Completeness in Crews in Races**

*For any* crew member included in the Crews in Races sheet, all five required fields (last name, first name, club, age, gender) should be present in the correct column positions.

**Validates: Requirements 3.4**

---

**Property 7: Race Number Ordering**

*For any* collection of boats, when transformed for the Crews in Races sheet, the resulting rows should be sorted in ascending order by race number.

**Validates: Requirements 3.7**

---

**Property 8: Team Manager Name Formatting**

*For any* team manager, the synthesis row should combine first name and last name into a single field formatted as "FirstName LastName".

**Validates: Requirements 4.3**

---

**Property 9: Assigned Boat Counting**

*For any* team manager, the count of assigned boats should equal the number of eligible boats (complete, paid, free) belonging to that manager that have a non-empty assigned_boat_identifier.

**Validates: Requirements 4.4, 4.8**

---

**Property 10: Event Type Crew Counting**

*For any* team manager, the marathon crew count should equal the number of eligible boats with event_type 'Marathon', and the semi-marathon crew count should equal the number of eligible boats with event_type 'Semi-Marathon'.

**Validates: Requirements 4.5, 4.6, 4.8**

---

**Property 11: Team Manager Aggregation**

*For any* collection of boats with multiple boats per team manager, the synthesis sheet should contain exactly one row per unique team manager, with aggregated counts across all their boats.

**Validates: Requirements 4.10**

---

**Property 12: Filename Format**

*For any* date, the generated filename should match the pattern "event-program-YYYY-MM-DD.xlsx" where YYYY-MM-DD represents the date in ISO format.

**Validates: Requirements 7.6**

---

**Property 13: Malformed Data Handling**

*For any* input data with missing or malformed required fields (e.g., missing crew_member_id, invalid boat status), the transformation functions should handle gracefully without throwing unhandled exceptions.

**Validates: Requirements 8.3**

---

**Property 14: Error Message Localization**

*For any* error condition and locale, the error message displayed to the user should be in the language corresponding to that locale.

**Validates: Requirements 8.5**

## Error Handling

### Error Categories

**1. API Errors**
- Backend endpoint unavailable or returns error status
- Network timeout or connection failure
- Invalid response format

**Handling Strategy**:
```javascript
try {
  const data = await fetchRaceData()
} catch (error) {
  console.error('API Error:', error)
  throw new Error(t('admin.export.error'))
}
```

**2. Data Validation Errors**
- No eligible boats found
- Missing required fields in response
- Malformed data structures

**Handling Strategy**:
```javascript
function validateExportData(data) {
  if (!data.boats || !data.crew_members || !data.races) {
    throw new Error('Missing required data fields')
  }
  
  const eligibleBoats = filterEligibleBoats(data.boats)
  if (eligibleBoats.length === 0) {
    throw new Error(t('admin.export.noData'))
  }
}
```

**3. Transformation Errors**
- Missing crew member references
- Invalid race lookups
- Null/undefined values in critical fields

**Handling Strategy**:
```javascript
function findCrewMember(memberId, members) {
  const member = members.find(m => m.crew_member_id === memberId)
  if (!member) {
    console.warn(`Crew member ${memberId} not found`)
    return {
      first_name: 'Unknown',
      last_name: 'Unknown',
      gender: '',
      age: 0,
      license_number: '',
      club_affiliation: ''
    }
  }
  return member
}
```

**4. Excel Generation Errors**
- xlsx library errors
- Browser download failures
- Memory issues with large datasets

**Handling Strategy**:
```javascript
try {
  const workbook = createWorkbook()
  // ... add sheets
  downloadWorkbook(workbook, filename)
} catch (error) {
  console.error('Excel generation error:', error)
  throw new Error(t('admin.export.error'))
}
```

### Error Recovery

**Graceful Degradation**:
- If optional fields are missing (e.g., phone number), display empty string
- If assigned boat is missing, display empty string
- If crew member not found, use placeholder values and log warning

**User Feedback**:
- Display error messages using MessageAlert component
- Provide actionable error messages (e.g., "Please try again" vs technical details)
- Log detailed errors to console for debugging

**Validation Before Export**:
```javascript
function validateExportData(data) {
  const errors = []
  
  if (!data.boats?.length) {
    errors.push('No boats found')
  }
  
  if (!data.crew_members?.length) {
    errors.push('No crew members found')
  }
  
  if (!data.races?.length) {
    errors.push('No races found')
  }
  
  const eligibleBoats = filterEligibleBoats(data.boats || [])
  if (eligibleBoats.length === 0) {
    errors.push(t('admin.export.noData'))
  }
  
  if (errors.length > 0) {
    throw new Error(errors.join('; '))
  }
}
```

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests**: Focus on specific examples, edge cases, and integration points
- Test specific data transformations with known inputs
- Test error handling with specific error conditions
- Test Excel file structure with sample data
- Test localization with specific locales

**Property Tests**: Verify universal properties across all inputs
- Test filtering logic with randomly generated boat collections
- Test formatting rules with various data combinations
- Test counting logic with random team manager distributions
- Test sorting and ordering with random data sets

Together, these approaches provide comprehensive coverage: unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across the input space.

### Unit Testing

**Test File**: `frontend/src/composables/__tests__/exportEventProgram.spec.js`

**Test Categories**:

1. **Data Transformation Tests**
```javascript
describe('transformCrewMemberList', () => {
  it('should transform crew members with all required fields', () => {
    const mockData = createMockExportData()
    const result = transformCrewMemberList(mockData, 'en')
    
    expect(result[0]).toEqual(expectedHeaders)
    expect(result[1][3]).toBe('Doe') // Last name
    expect(result[1][6]).toBe(25) // Age
  })
  
  it('should handle missing assigned boat', () => {
    const mockData = createMockDataWithoutAssignedBoat()
    const result = transformCrewMemberList(mockData, 'en')
    
    expect(result[1][11]).toBe('') // Assigned boat column
  })
  
  it('should filter out forfait boats', () => {
    const mockData = createMockDataWithForfaitBoats()
    const result = transformCrewMemberList(mockData, 'en')
    
    // Should only have eligible boats
    expect(result.length).toBe(3) // Header + 2 eligible boats
  })
})
```

2. **Synthesis Aggregation Tests**
```javascript
describe('transformSynthesis', () => {
  it('should aggregate boats by team manager', () => {
    const mockData = createMockDataWithMultipleBoatsPerManager()
    const result = transformSynthesis(mockData, 'en')
    
    expect(result.length).toBe(3) // Header + 2 managers
    expect(result[1][4]).toBe(3) // Assigned boats count
  })
  
  it('should count marathon and semi-marathon crews separately', () => {
    const mockData = createMockDataWithMixedEventTypes()
    const result = transformSynthesis(mockData, 'en')
    
    expect(result[1][5]).toBe(2) // Marathon count
    expect(result[1][6]).toBe(1) // Semi-marathon count
  })
})
```

3. **Localization Tests**
```javascript
describe('Localization', () => {
  it('should use French headers when locale is fr', () => {
    const mockData = createMockExportData()
    const result = transformCrewMemberList(mockData, 'fr')
    
    expect(result[0][0]).toBe('Course #')
    expect(result[0][3]).toBe('Nom')
  })
  
  it('should use English headers when locale is en', () => {
    const mockData = createMockExportData()
    const result = transformCrewMemberList(mockData, 'en')
    
    expect(result[0][0]).toBe('Race #')
    expect(result[0][3]).toBe('Last name')
  })
})
```

4. **Error Handling Tests**
```javascript
describe('Error Handling', () => {
  it('should throw error when no eligible boats exist', () => {
    const mockData = createMockDataWithOnlyForfaitBoats()
    
    expect(() => validateExportData(mockData)).toThrow()
  })
  
  it('should handle missing crew member gracefully', () => {
    const mockData = createMockDataWithMissingCrewMember()
    const result = transformCrewMemberList(mockData, 'en')
    
    expect(result[1][3]).toBe('Unknown') // Placeholder last name
  })
})
```

### Property-Based Testing

**Note**: While we prefer explicit test cases over the Hypothesis library for Python, for JavaScript/TypeScript we can use libraries like `fast-check` for property-based testing. However, given the project guidelines, we'll implement property tests using explicit randomized test cases with multiple iterations.

**Test File**: `frontend/src/utils/__tests__/eventProgramTransformers.property.spec.js`

**Property Test Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with feature name and property number
- Use randomized data generation for comprehensive coverage

**Property Test Examples**:

```javascript
describe('Property Tests - Enhanced Event Program Export', () => {
  const ITERATIONS = 100
  
  test('Property 1: Eligible Boat Filtering', () => {
    // Feature: enhanced-event-program-export, Property 1
    for (let i = 0; i < ITERATIONS; i++) {
      const boats = generateRandomBoats(10) // Mix of all statuses
      const mockData = { boats, crew_members: [], races: [], team_managers: [] }
      
      const result = transformCrewMemberList(mockData, 'en')
      
      // Verify no forfait boats in result
      const boatNumbers = result.slice(1).map(row => row[2])
      const forfaitBoatNumbers = boats
        .filter(b => b.registration_status === 'forfait')
        .map(b => b.boat_number)
      
      forfaitBoatNumbers.forEach(num => {
        expect(boatNumbers).not.toContain(num)
      })
      
      // Verify all eligible boats are included
      const eligibleBoatNumbers = boats
        .filter(b => ['complete', 'paid', 'free'].includes(b.registration_status))
        .map(b => b.boat_number)
      
      eligibleBoatNumbers.forEach(num => {
        expect(boatNumbers).toContain(num)
      })
    }
  })
  
  test('Property 3: Assigned Boat Formatting', () => {
    // Feature: enhanced-event-program-export, Property 3
    for (let i = 0; i < ITERATIONS; i++) {
      const boat = generateRandomBoat()
      const formatted = formatAssignedBoat(boat)
      
      if (boat.assigned_boat_name && boat.assigned_boat_comment) {
        expect(formatted).toBe(`${boat.assigned_boat_name} - ${boat.assigned_boat_comment}`)
      } else if (boat.assigned_boat_name) {
        expect(formatted).toBe(boat.assigned_boat_name)
      } else {
        expect(formatted).toBe('')
      }
    }
  })
  
  test('Property 5: Variable Crew Size Handling', () => {
    // Feature: enhanced-event-program-export, Property 5
    for (let i = 0; i < ITERATIONS; i++) {
      const crewSize = Math.floor(Math.random() * 9) + 1 // 1-9 members
      const boat = generateRandomBoatWithCrewSize(crewSize)
      const mockData = {
        boats: [boat],
        crew_members: generateCrewMembersForBoat(boat),
        races: [generateRaceForBoat(boat)],
        team_managers: []
      }
      
      const result = transformCrewsInRaces(mockData, 'en')
      const dataRow = result[1] // First data row after header
      
      // Verify first N members have data
      for (let j = 0; j < crewSize; j++) {
        const baseIndex = 4 + (j * 5) // 4 initial columns + 5 fields per member
        expect(dataRow[baseIndex]).toBeTruthy() // Last name
        expect(dataRow[baseIndex + 1]).toBeTruthy() // First name
      }
      
      // Verify remaining positions are empty
      for (let j = crewSize; j < 9; j++) {
        const baseIndex = 4 + (j * 5)
        expect(dataRow[baseIndex]).toBe('')
        expect(dataRow[baseIndex + 1]).toBe('')
        expect(dataRow[baseIndex + 2]).toBe('')
        expect(dataRow[baseIndex + 3]).toBe('')
        expect(dataRow[baseIndex + 4]).toBe('')
      }
    }
  })
  
  test('Property 7: Race Number Ordering', () => {
    // Feature: enhanced-event-program-export, Property 7
    for (let i = 0; i < ITERATIONS; i++) {
      const boats = generateRandomBoats(20)
      const races = generateRacesForBoats(boats)
      const mockData = {
        boats,
        crew_members: generateCrewMembersForBoats(boats),
        races,
        team_managers: []
      }
      
      const result = transformCrewsInRaces(mockData, 'en')
      const raceNumbers = result.slice(1).map(row => row[0])
      
      // Verify ascending order
      for (let j = 1; j < raceNumbers.length; j++) {
        expect(raceNumbers[j]).toBeGreaterThanOrEqual(raceNumbers[j - 1])
      }
    }
  })
  
  test('Property 9: Assigned Boat Counting', () => {
    // Feature: enhanced-event-program-export, Property 9
    for (let i = 0; i < ITERATIONS; i++) {
      const boats = generateRandomBoatsForManager(10)
      const manager = generateRandomTeamManager()
      const mockData = {
        boats,
        crew_members: [],
        races: [],
        team_managers: [manager]
      }
      
      const result = transformSynthesis(mockData, 'en')
      const dataRow = result[1]
      const assignedBoatsCount = dataRow[4]
      
      // Count boats with assigned_boat_identifier
      const expectedCount = boats.filter(b => 
        ['complete', 'paid', 'free'].includes(b.registration_status) &&
        b.assigned_boat_identifier
      ).length
      
      expect(assignedBoatsCount).toBe(expectedCount)
    }
  })
  
  test('Property 10: Event Type Crew Counting', () => {
    // Feature: enhanced-event-program-export, Property 10
    for (let i = 0; i < ITERATIONS; i++) {
      const boats = generateRandomBoatsWithMixedEventTypes(15)
      const manager = generateRandomTeamManager()
      const mockData = {
        boats,
        crew_members: [],
        races: [],
        team_managers: [manager]
      }
      
      const result = transformSynthesis(mockData, 'en')
      const dataRow = result[1]
      const marathonCount = dataRow[5]
      const semiMarathonCount = dataRow[6]
      
      const eligibleBoats = boats.filter(b => 
        ['complete', 'paid', 'free'].includes(b.registration_status)
      )
      
      const expectedMarathon = eligibleBoats.filter(b => 
        b.event_type === 'Marathon'
      ).length
      
      const expectedSemiMarathon = eligibleBoats.filter(b => 
        b.event_type === 'Semi-Marathon'
      ).length
      
      expect(marathonCount).toBe(expectedMarathon)
      expect(semiMarathonCount).toBe(expectedSemiMarathon)
    }
  })
})
```

**Test Data Generators**:
```javascript
function generateRandomBoat() {
  const statuses = ['incomplete', 'complete', 'paid', 'free', 'forfait']
  const eventTypes = ['Marathon', 'Semi-Marathon']
  
  return {
    boat_id: `boat-${Math.random()}`,
    boat_number: `B${Math.floor(Math.random() * 1000)}`,
    registration_status: statuses[Math.floor(Math.random() * statuses.length)],
    event_type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
    boat_type: 'C4',
    category: 'SM',
    assigned_boat_identifier: Math.random() > 0.5 ? `assigned-${Math.random()}` : null,
    assigned_boat_name: Math.random() > 0.5 ? `Boat ${Math.random()}` : null,
    assigned_boat_comment: Math.random() > 0.5 ? `Comment ${Math.random()}` : null,
    team_manager_id: 'manager-1',
    seats: []
  }
}

function generateRandomBoats(count) {
  return Array.from({ length: count }, () => generateRandomBoat())
}

// Additional generators for other test scenarios...
```

### Integration Testing

**Test Scenarios**:
1. Full export flow with real API endpoint (mocked)
2. Excel file download trigger
3. Error handling with failed API calls
4. Localization switching

**Test File**: `frontend/src/composables/__tests__/exportEventProgram.integration.spec.js`

### Test Coverage Goals

- **Unit Tests**: 90%+ coverage of transformation functions
- **Property Tests**: 100 iterations minimum per property
- **Integration Tests**: Cover all major user flows
- **Error Handling**: Test all error paths

### Running Tests

```bash
# Run all tests
npm run test

# Run specific test file
npm run test exportEventProgram.spec.js

# Run with coverage
npm run test:coverage

# Run property tests only
npm run test eventProgramTransformers.property.spec.js
```
