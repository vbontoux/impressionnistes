# Export API Refactoring - Design Document

## Overview

This design refactors the admin export system to follow a clean separation of concerns: the backend provides raw JSON data while the frontend handles format-specific transformations. This architecture improves maintainability, enables easy addition of new export formats, and provides better testability.

### Current Architecture Problems
- Backend generates CSV/Excel files directly
- Format-specific logic (CrewTimer race name formatting) in backend
- Hard to add new export formats
- Tight coupling between data retrieval and presentation

### New Architecture Benefits
- Backend focuses on data retrieval and aggregation
- Frontend handles all format-specific transformations
- Easy to add new export formats (just add new frontend formatter)
- Better testability (unit test formatters, integration test APIs)
- Consistent JSON API responses

## Architecture

### High-Level Flow

```
┌─────────────┐         ┌──────────────┐         ┌─────────────────┐
│   Admin     │  HTTP   │   Backend    │  JSON   │    Frontend     │
│   User      │────────>│   Lambda     │────────>│   Formatter     │
│             │         │   (Raw Data) │         │   (CSV/Excel)   │
└─────────────┘         └──────────────┘         └─────────────────┘
                              │                           │
                              │                           │
                              v                           v
                        ┌──────────┐              ┌──────────────┐
                        │ DynamoDB │              │  Download    │
                        │          │              │  File        │
                        └──────────┘              └──────────────┘
```

### Component Responsibilities

**Backend (Lambda Functions):**
- Query DynamoDB for raw data
- Aggregate related data (join races with boats, boats with crew)
- Cache lookups to minimize queries
- Return structured JSON with all fields
- Handle pagination for large datasets
- Convert DynamoDB types (Decimal) to JSON-compatible types

**Frontend (JavaScript Utilities):**
- Receive JSON data from backend
- Apply format-specific transformations
- Generate downloadable files (CSV, Excel, etc.)
- Handle client-side filtering and sorting
- Provide user feedback during export

## Components and Interfaces

### Backend Components

#### 1. Export Crew Members API
**Endpoint:** `GET /admin/export/crew-members`

**Response Structure:**
```json
{
  "success": true,
  "data": {
    "crew_members": [
      {
        "crew_member_id": "crew-123",
        "first_name": "Alice",
        "last_name": "Smith",
        "gender": "F",
        "date_of_birth": "1990-01-15",
        "age": 35,
        "license_number": "LIC001",
        "club_affiliation": "RCPM",
        "team_manager_id": "user-456",
        "team_manager_name": "John Doe",
        "team_manager_email": "john@example.com",
        "team_manager_club": "RCPM",
        "created_at": "2025-01-01T10:00:00Z",
        "updated_at": "2025-01-02T15:30:00Z"
      }
    ],
    "total_count": 150,
    "exported_at": "2025-12-19T10:30:00Z"
  }
}
```

#### 2. Export Boat Registrations API
**Endpoint:** `GET /admin/export/boat-registrations`

**Response Structure:**
```json
{
  "success": true,
  "data": {
    "boats": [
      {
        "boat_registration_id": "boat-789",
        "event_type": "21km",
        "boat_type": "4+",
        "race_id": "SM01A",
        "race_name": "WOMEN-JUNIOR J16-COXED SWEEP FOUR",
        "registration_status": "complete",
        "forfait": false,
        "seats": [
          {
            "position": 1,
            "type": "rower",
            "crew_member_id": "crew-123"
          }
        ],
        "crew_composition": {
          "gender_category": "women",
          "age_category": "j16",
          "avg_age": 16.5,
          "filled_seats": 4,
          "total_seats": 5
        },
        "is_multi_club_crew": false,
        "team_manager_id": "user-456",
        "team_manager_name": "John Doe",
        "team_manager_email": "john@example.com",
        "team_manager_club": "RCPM",
        "created_at": "2025-01-01T10:00:00Z",
        "updated_at": "2025-01-02T15:30:00Z",
        "paid_at": "2025-01-03T09:00:00Z"
      }
    ],
    "total_count": 85,
    "exported_at": "2025-12-19T10:30:00Z"
  }
}
```

#### 3. Export Races API
**Endpoint:** `GET /admin/export/races`

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
        "race_id": "M01",
        "name": "1X SENIOR MAN",
        "distance": 42,
        "event_type": "42km",
        "boat_type": "skiff",
        "age_category": "senior",
        "gender_category": "men"
      }
    ],
    "boats": [
      {
        "boat_registration_id": "boat-789",
        "race_id": "M01",
        "event_type": "42km",
        "boat_type": "skiff",
        "registration_status": "complete",
        "forfait": false,
        "team_manager_id": "user-456",
        "club_affiliation": "RCPM",
        "seats": [
          {
            "position": 1,
            "type": "rower",
            "crew_member_id": "crew-123"
          }
        ]
      }
    ],
    "crew_members": [
      {
        "crew_member_id": "crew-123",
        "first_name": "Alice",
        "last_name": "Smith",
        "date_of_birth": "1990-01-15",
        "gender": "F",
        "license_number": "LIC001"
      }
    ],
    "team_managers": [
      {
        "user_id": "user-456",
        "club_affiliation": "RCPM",
        "email": "john@example.com"
      }
    ],
    "total_races": 25,
    "total_boats": 85,
    "total_crew_members": 150,
    "exported_at": "2025-12-19T10:30:00Z"
  }
}
```

### Frontend Components

#### 1. Crew Members Formatter
**File:** `frontend/src/utils/exportFormatters/crewMembersFormatter.js`

**Functions:**
- `formatCrewMembersToCSV(jsonData)` - Converts JSON to CSV string
- `downloadCrewMembersCSV(jsonData, filename)` - Triggers browser download

**Responsibilities:**
- Define CSV column headers
- Map JSON fields to CSV columns
- Handle special characters and escaping
- Sort data appropriately
- Generate timestamp for filename

#### 2. Boat Registrations Formatter
**File:** `frontend/src/utils/exportFormatters/boatRegistrationsFormatter.js`

**Functions:**
- `formatBoatRegistrationsToCSV(jsonData)` - Converts JSON to CSV string
- `calculateFilledSeats(boat)` - Formats as "X/Y"
- `downloadBoatRegistrationsCSV(jsonData, filename)` - Triggers download

**Responsibilities:**
- Define CSV column headers
- Calculate derived fields (filled seats)
- Format boolean values (Yes/No)
- Handle nested data structures
- Sort data appropriately

#### 3. CrewTimer Formatter
**File:** `frontend/src/utils/exportFormatters/crewTimerFormatter.js`

**Functions:**
- `formatRacesToCrewTimer(jsonData)` - Converts JSON to CrewTimer format
- `formatSemiMarathonRaceName(race)` - Formats race name for semi-marathons
- `getBoatTypeDisplay(boatType)` - Converts boat type to display format
- `calculateAverageAge(crewMembers, competitionDate)` - Calculates average age
- `getStrokeSeatName(seats, crewMembersDict)` - Extracts stroke seat name
- `downloadCrewTimerExcel(jsonData, filename)` - Generates Excel file

**Responsibilities:**
- Filter boats (complete/paid/free, exclude forfait)
- Sort races (marathon first, then semi-marathon)
- Format race names based on distance
- Assign event numbers (per race)
- Assign bow numbers (global)
- Calculate average age
- Extract stroke seat name
- Generate Excel file with CrewTimer format

## Data Models

### Crew Member
```typescript
interface CrewMember {
  crew_member_id: string;
  first_name: string;
  last_name: string;
  gender: 'M' | 'F';
  date_of_birth: string; // ISO date
  age?: number;
  license_number?: string;
  club_affiliation?: string;
  team_manager_id: string;
  team_manager_name?: string;
  team_manager_email?: string;
  team_manager_club?: string;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}
```

### Boat Registration
```typescript
interface BoatRegistration {
  boat_registration_id: string;
  event_type: '21km' | '42km';
  boat_type: string;
  race_id: string;
  race_name?: string;
  registration_status: 'incomplete' | 'complete' | 'paid' | 'free';
  forfait: boolean;
  seats: Seat[];
  crew_composition?: {
    gender_category: string;
    age_category: string;
    avg_age: number;
    filled_seats: number;
    total_seats: number;
  };
  is_multi_club_crew?: boolean;
  team_manager_id: string;
  team_manager_name?: string;
  team_manager_email?: string;
  team_manager_club?: string;
  created_at: string;
  updated_at: string;
  paid_at?: string;
}

interface Seat {
  position: number;
  type: 'rower' | 'cox';
  crew_member_id?: string;
}
```

### Race
```typescript
interface Race {
  race_id: string;
  name: string;
  distance: 21 | 42;
  event_type: '21km' | '42km';
  boat_type: string;
  age_category?: string;
  gender_category?: string;
}
```

### Team Manager
```typescript
interface TeamManager {
  user_id: string;
  club_affiliation: string;
  email: string;
  first_name?: string;
  last_name?: string;
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Complete data retrieval
*For any* export request, the backend API should return all relevant records from the database without omitting any data due to pagination or query limits.
**Validates: Requirements 1.1, 2.1, 3.1, 5.1**

### Property 2: Data consistency
*For any* boat registration, if the boat references a race_id, the race data should be included in the races export, and if the boat has crew_member_ids in seats, those crew members should be included in the crew members export.
**Validates: Requirements 2.2, 3.3, 3.4**

### Property 3: JSON serialization
*For any* DynamoDB Decimal value in the exported data, it should be converted to a JSON-compatible number type (float or int) without loss of precision for reasonable values.
**Validates: Requirements 4.4**

### Property 4: Filtering correctness
*For any* CrewTimer export, the frontend formatter should include only boats where registration_status is 'complete', 'paid', or 'free' AND forfait is false.
**Validates: Requirements 3.14**

### Property 5: Race sorting
*For any* CrewTimer export, marathon races (distance=42) should appear before semi-marathon races (distance=21) in the output.
**Validates: Requirements 3.13**

### Property 6: Event numbering
*For any* CrewTimer export with multiple boats in the same race, all boats in that race should have the same Event Num value.
**Validates: Requirements 3.11**

### Property 7: Bow numbering
*For any* CrewTimer export, bow numbers should increment sequentially starting from 1 and continuing across all races without gaps or duplicates.
**Validates: Requirements 3.12**

### Property 8: Race name formatting
*For any* semi-marathon race in CrewTimer export, the formatted race name should follow the pattern: boat_type [Y if yolette] age_category gender_category, where gender is mapped to MAN/WOMAN/MIXED.
**Validates: Requirements 3.9**

### Property 9: CSV escaping
*For any* field value containing special characters (comma, quote, newline), the CSV formatter should properly escape the value to maintain data integrity.
**Validates: Requirements 1.5**

### Property 10: Filled seats calculation
*For any* boat registration, the filled seats count should equal the number of seats where crew_member_id is not null or empty.
**Validates: Requirements 2.5**

## Error Handling

### Backend Error Scenarios

1. **DynamoDB Query Failure**
   - Return 500 status with error message
   - Log full error details for debugging
   - Include error code for client handling

2. **Pagination Timeout**
   - Implement timeout for scan operations
   - Return partial data with warning if timeout occurs
   - Log warning for monitoring

3. **Missing Related Data**
   - Continue processing if team manager not found
   - Use default values (e.g., "Unknown" for club)
   - Log warnings for data integrity issues

4. **Invalid Data Types**
   - Handle Decimal conversion errors gracefully
   - Default to 0 or null for numeric fields
   - Log conversion errors

### Frontend Error Scenarios

1. **API Request Failure**
   - Display user-friendly error message
   - Provide retry option
   - Log error for debugging

2. **Empty Dataset**
   - Show "No data to export" message
   - Don't generate empty file
   - Provide guidance to user

3. **Format Conversion Error**
   - Catch and display specific error
   - Allow user to download raw JSON as fallback
   - Log error details

4. **Browser Download Failure**
   - Retry download
   - Offer alternative download method
   - Show error message with troubleshooting steps

## Testing Strategy

### Backend Integration Tests

**Test File:** `tests/integration/test_admin_export_api.py`

**Test Cases:**
1. `test_export_crew_members_returns_json` - Verify JSON structure and content
2. `test_export_crew_members_includes_team_manager_info` - Verify data aggregation
3. `test_export_crew_members_handles_pagination` - Verify large dataset handling
4. `test_export_crew_members_sorts_correctly` - Verify sorting logic
5. `test_export_boat_registrations_returns_json` - Verify JSON structure
6. `test_export_boat_registrations_includes_all_boats` - Verify no filtering
7. `test_export_boat_registrations_includes_race_names` - Verify race lookup
8. `test_export_races_returns_complete_data` - Verify all entities included
9. `test_export_races_includes_all_boats_regardless_of_status` - Verify no filtering
10. `test_export_races_converts_decimals_to_numbers` - Verify type conversion
11. `test_export_api_handles_missing_team_manager` - Verify error handling
12. `test_export_api_handles_empty_database` - Verify empty dataset handling

### Frontend Unit Tests

**Test File:** `frontend/tests/unit/exportFormatters.spec.js`

**Test Cases:**
1. `test_crew_members_csv_format` - Verify CSV structure and headers
2. `test_crew_members_csv_escaping` - Verify special character handling
3. `test_boat_registrations_csv_format` - Verify CSV structure
4. `test_boat_registrations_filled_seats_calculation` - Verify calculation
5. `test_crewtimer_filters_boats_correctly` - Verify filtering logic
6. `test_crewtimer_sorts_races_correctly` - Verify marathon before semi-marathon
7. `test_crewtimer_event_numbering` - Verify same race = same event num
8. `test_crewtimer_bow_numbering` - Verify global sequential numbering
9. `test_crewtimer_semi_marathon_race_name_formatting` - Verify formatting
10. `test_crewtimer_marathon_race_name_unchanged` - Verify original name used
11. `test_crewtimer_gender_mapping` - Verify MAN/WOMAN/MIXED mapping
12. `test_crewtimer_yolette_detection` - Verify Y marker for yolette races
13. `test_crewtimer_stroke_seat_extraction` - Verify highest position rower
14. `test_crewtimer_average_age_calculation` - Verify age calculation
15. `test_formatter_handles_empty_data` - Verify empty dataset handling
16. `test_formatter_handles_missing_fields` - Verify null/undefined handling

## Implementation Notes

### Backend Migration Strategy

1. **Phase 1: Create new JSON endpoints**
   - Implement new Lambda functions
   - Add API Gateway routes
   - Deploy alongside existing CSV endpoints

2. **Phase 2: Update frontend to use new endpoints**
   - Implement frontend formatters
   - Update UI to call new endpoints
   - Keep fallback to old endpoints

3. **Phase 3: Deprecate old endpoints**
   - Add deprecation warnings to old endpoints
   - Monitor usage metrics
   - Remove old endpoints after migration period

### Frontend Implementation Details

**CSV Generation:**
- Use `papaparse` library for robust CSV generation
- Handle large datasets with streaming if needed
- Provide progress indicator for large exports

**Excel Generation:**
- Use `xlsx` library for Excel file generation
- Support multiple sheets if needed
- Apply basic formatting (headers bold, etc.)

**Download Mechanism:**
- Use Blob API for file generation
- Create temporary download link
- Clean up after download

### Performance Considerations

**Backend:**
- Implement caching for team manager lookups
- Use batch operations where possible
- Set reasonable timeout limits (30 seconds)
- Monitor Lambda execution time

**Frontend:**
- Process data in chunks for large datasets
- Use Web Workers for heavy processing
- Show progress indicator
- Implement cancellation if needed

## Migration Path

### Step 1: Backend Implementation
1. Create `export_crew_members_json.py`
2. Create `export_boat_registrations_json.py`
3. Create `export_races_json.py`
4. Add API Gateway routes
5. Write integration tests
6. Deploy to dev environment

### Step 2: Frontend Implementation
1. Create formatter utilities
2. Write unit tests
3. Update AdminDataExport.vue component
4. Test in dev environment
5. Deploy to production

### Step 3: Cleanup
1. Monitor usage of old endpoints
2. Add deprecation warnings
3. Update documentation
4. Remove old endpoints after 30 days
5. Remove old Lambda functions

## Dependencies

**Backend:**
- `boto3` - DynamoDB client
- `responses` - Response utilities
- `auth_utils` - Admin authentication
- `database` - Database client

**Frontend:**
- `papaparse` - CSV generation
- `xlsx` - Excel generation
- `file-saver` - File download utility

## Security Considerations

1. **Authentication:** All endpoints require admin group membership
2. **Authorization:** Verify admin role before returning data
3. **Data Sanitization:** Escape special characters in exports
4. **Rate Limiting:** Consider rate limits for export endpoints
5. **Audit Logging:** Log all export operations with user ID and timestamp
