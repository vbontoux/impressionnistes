# Requirements Document

## Introduction

This specification defines enhancements to the existing event program export functionality in the Impressionnistes Registration System. The current export generates a 2-sheet Excel file with basic crew member and race schedule information. This enhancement expands the export to 4 sheets with comprehensive crew details, race-by-crew listings, and club manager synthesis data.

The enhanced export will provide event administrators with complete race day operational information including detailed crew member data (age, gender, license numbers, boat positions), boat assignments, and club-level summaries for coordination purposes.

## Glossary

- **Event_Program_Export**: Excel file containing comprehensive race day information across multiple sheets
- **Crew_Member_List**: Sheet 1 - Enhanced listing of all crew members with detailed personal and race information
- **Race_Schedule**: Sheet 2 - Existing schedule of races with start times (unchanged)
- **Crews_In_Races**: Sheet 3 - New sheet listing all crews organized by race with full member details
- **Synthesis**: Sheet 4 - New sheet providing club manager summary with boat and crew counts
- **Eligible_Boat**: A boat with registration status of complete, paid, or free (excludes forfait status)
- **Boat_Assignment**: The confirmed boat identifier assigned to a crew, formatted as "boat_name - comment"
- **Race_Number**: Sequential number assigned to races based on event type, boat type, and category
- **Team_Manager**: Club representative responsible for crew registrations and payments
- **Seat_Position**: Crew member's position in the boat (e.g., "Rower 1", "Rower 2", "Cox")

## Requirements

### Requirement 1: Enhanced Crew Member List Sheet

**User Story:** As an event administrator, I want an enhanced crew member list with detailed personal information and boat assignments, so that I have complete crew member data for race day operations.

#### Acceptance Criteria

1. WHEN generating the export, THE System SHALL include all crew members from eligible boats in Sheet 1
2. THE System SHALL display crew member gender in the enhanced list
3. THE System SHALL display crew member age in the enhanced list
4. THE System SHALL display crew member license number in the enhanced list
5. THE System SHALL display crew member seat position (e.g., "Rower 1", "Cox") in the enhanced list
6. THE System SHALL display assigned boat information formatted as "boat_name - comment" when available
7. THE System SHALL order columns as: Race #, Race name, Crew #, Last name, First name, Club, Age, Gender, License #, Place in boat, Bow number, Assigned Boat
8. WHEN a crew member has no assigned boat, THE System SHALL display an empty value in the Assigned Boat column
9. THE System SHALL support both French and English column headers based on locale

### Requirement 2: Race Schedule Sheet Preservation

**User Story:** As an event administrator, I want the existing race schedule sheet to remain unchanged, so that I maintain consistency with current workflows.

#### Acceptance Criteria

1. THE System SHALL preserve Sheet 2 (Race Schedule) with existing structure and data
2. THE System SHALL maintain current race schedule column headers and formatting
3. THE System SHALL include race start times in the schedule sheet

### Requirement 3: Crews in Races Sheet

**User Story:** As an event administrator, I want a detailed listing of all crews organized by race with complete member information, so that I can quickly reference crew composition for each race.

#### Acceptance Criteria

1. WHEN generating the export, THE System SHALL create Sheet 3 (Crews in Races) with race-organized crew listings
2. THE System SHALL include columns for Race #, Race name, Crew #, and Boat assignment
3. THE System SHALL include columns for up to 9 crew member positions (supporting 8+cox boats)
4. FOR EACH crew member position, THE System SHALL include columns for: Last name, First name, Club, Age, Gender
5. WHEN a crew has fewer than 9 members, THE System SHALL leave remaining member columns empty
6. THE System SHALL format boat assignments as "boat_name - comment" when available
7. THE System SHALL group crews by race number in ascending order
8. THE System SHALL only include eligible boats (complete, paid, or free status)
9. THE System SHALL support both French and English column headers based on locale

### Requirement 4: Synthesis Sheet by Club Manager

**User Story:** As an event administrator, I want a summary table showing club manager information with boat and crew counts, so that I can coordinate with clubs and track participation by organization.

#### Acceptance Criteria

1. WHEN generating the export, THE System SHALL create Sheet 4 (Synthesis) with club manager summaries
2. THE System SHALL include columns for: Club, First name + Last name, Email, Phone #, Number of assigned boats, Number of crews in marathon, Number of crews in semi-marathon
3. THE System SHALL combine team manager first name and last name in a single column
4. THE System SHALL count assigned boats as boats with a non-empty assigned_boat_identifier
5. THE System SHALL count marathon crews as boats where event_type equals 'Marathon'
6. THE System SHALL count semi-marathon crews as boats where event_type equals 'Semi-Marathon'
7. WHEN a team manager has no phone number, THE System SHALL display an empty value in the Phone # column
8. THE System SHALL only count eligible boats (complete, paid, or free status) in all counts
9. THE System SHALL support both French and English column headers based on locale
10. THE System SHALL group data by team manager, showing one row per team manager

### Requirement 5: Data Source and Filtering

**User Story:** As a system developer, I want to reuse existing backend data endpoints and filtering logic, so that the export maintains consistency with other system features.

#### Acceptance Criteria

1. THE System SHALL retrieve all export data from the existing `/admin/export/races-json` endpoint
2. THE System SHALL filter boats to only include those with status: complete, paid, or free
3. THE System SHALL exclude boats with status: forfait from all sheets
4. THE System SHALL use existing race numbering logic from raceNumbering.js
5. THE System SHALL reuse existing data transformation functions where applicable

### Requirement 6: Localization Support

**User Story:** As an event administrator, I want the export to support both French and English languages, so that I can provide documentation in the appropriate language for my audience.

#### Acceptance Criteria

1. WHEN the user's locale is French, THE System SHALL display all column headers in French
2. WHEN the user's locale is English, THE System SHALL display all column headers in English
3. THE System SHALL translate sheet names based on locale
4. THE System SHALL format dates and numbers according to locale conventions
5. THE System SHALL use existing i18n translation keys for consistency

### Requirement 7: Excel File Generation

**User Story:** As an event administrator, I want the export to generate a properly formatted Excel file, so that I can open and work with the data in spreadsheet applications.

#### Acceptance Criteria

1. THE System SHALL generate an Excel file (.xlsx format) with 4 sheets
2. THE System SHALL name sheets appropriately based on locale
3. THE System SHALL apply appropriate column widths for readability
4. THE System SHALL include header rows with bold formatting
5. THE System SHALL trigger automatic file download in the browser
6. THE System SHALL name the file with format: "event-program-YYYY-MM-DD.xlsx"

### Requirement 8: Error Handling

**User Story:** As an event administrator, I want clear error messages if the export fails, so that I understand what went wrong and can take corrective action.

#### Acceptance Criteria

1. WHEN the backend endpoint fails, THE System SHALL display an error message to the user
2. WHEN no eligible boats exist, THE System SHALL display a warning message
3. WHEN data is incomplete or malformed, THE System SHALL handle gracefully and log errors
4. THE System SHALL not generate a partial export file if critical data is missing
5. THE System SHALL provide user-friendly error messages in the current locale

## Appendix A: Data Structures

### Backend JSON Response Structure

The `/admin/export/races-json` endpoint provides:

```json
{
  "races": [
    {
      "race_id": "string",
      "event_type": "Marathon|Semi-Marathon",
      "boat_type": "string",
      "category": "string",
      "start_time": "HH:MM",
      "race_number": "number"
    }
  ],
  "boats": [
    {
      "boat_id": "string",
      "boat_number": "string",
      "registration_status": "complete|paid|free|forfait",
      "event_type": "Marathon|Semi-Marathon",
      "boat_type": "string",
      "category": "string",
      "assigned_boat_identifier": "string|null",
      "assigned_boat_name": "string|null",
      "assigned_boat_comment": "string|null",
      "seats": [
        {
          "seat_type": "string",
          "crew_member_id": "string"
        }
      ]
    }
  ],
  "crew_members": [
    {
      "crew_member_id": "string",
      "first_name": "string",
      "last_name": "string",
      "gender": "M|F",
      "age": "number",
      "license_number": "string",
      "club_affiliation": "string"
    }
  ],
  "team_managers": [
    {
      "team_manager_id": "string",
      "first_name": "string",
      "last_name": "string",
      "email": "string",
      "phone": "string|null",
      "club_affiliation": "string"
    }
  ],
  "config": {
    "competition_date": "YYYY-MM-DD",
    "race_start_time": "HH:MM",
    "race_interval_minutes": "number"
  }
}
```

## Appendix B: Column Specifications

### Sheet 1: Enhanced Crew Member List Columns

1. Race # (number)
2. Race name (string)
3. Crew # (string - boat number)
4. Last name (string)
5. First name (string)
6. Club (string)
7. Age (number)
8. Gender (M/F)
9. License # (string)
10. Place in boat (string - seat position)
11. Bow number (string)
12. Assigned Boat (string - "name - comment" format)

### Sheet 3: Crews in Races Columns

1. Race # (number)
2. Race name (string)
3. Crew # (string - boat number)
4. Boat assignment (string - "name - comment" format)
5-49. Crew member columns (9 members × 5 fields each):
   - Member N Last name
   - Member N First name
   - Member N Club
   - Member N Age
   - Member N Gender

### Sheet 4: Synthesis Columns

1. Club (string)
2. First name + Last name (string - combined)
3. Email (string)
4. Phone # (string)
5. Number of assigned boats (number)
6. Number of crews in marathon (number)
7. Number of crews in semi-marathon (number)
