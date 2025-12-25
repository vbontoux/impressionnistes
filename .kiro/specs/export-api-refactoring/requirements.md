# Requirements Document

## Introduction

This specification defines the refactoring of the admin export API endpoints to follow a consistent architecture where the backend provides raw JSON data and the frontend handles format-specific transformations (CSV, Excel, etc.). This improves maintainability, flexibility, and allows easy addition of new export formats without backend changes.

## Glossary

- **Export API**: Backend Lambda functions that retrieve and return data for administrative exports
- **Frontend Formatter**: JavaScript utilities that transform JSON data into specific export formats (CSV, Excel, CrewTimer, Event Program)
- **Raw Data**: Unformatted database records returned as JSON from the API
- **Format-Specific Logic**: Transformations like race name formatting, column ordering, data type conversions specific to an export format
- **Team Manager**: User who manages crew members and boat registrations
- **Crew Member**: Individual rower or coxswain registered by a team manager
- **Boat Registration**: A boat entry with assigned crew members for a specific race
- **Race Number**: Sequential number assigned to each race that has eligible boats
- **Bow Number**: Sequential number assigned to each boat for identification during the race
- **Eligible Boat**: A boat with status complete, paid, or free that is not marked as forfait
- **Short Name**: Abbreviated race name used in exports (e.g., "MW4X+Y" for Master Women 4X+ Yolette)
- **Display Order**: Numeric field on races that determines the order in which races are processed for numbering
- **Event Program**: Multi-sheet Excel export containing crew member list and race schedule for race day printing
- **Stroke Seat**: The highest position rower in a boat (not the coxswain)

## Requirements

### Requirement 1

**User Story:** As an administrator, I want to export crew member data in various formats, so that I can use the data in different systems and tools.

#### Acceptance Criteria

1. WHEN an administrator requests crew member export THEN the Export API SHALL return all crew member records with associated team manager information as JSON
2. WHEN the Export API returns crew member data THEN the data SHALL include crew member ID, name, gender, date of birth, license number, club affiliation, and team manager details
3. WHEN the Export API returns crew member data THEN the data SHALL be sorted by team manager name, then by crew member last name
4. WHEN the Frontend Formatter receives crew member JSON data THEN the Frontend Formatter SHALL convert the data to CSV format with appropriate headers
5. WHEN the Frontend Formatter generates CSV THEN the Frontend Formatter SHALL handle special characters and proper escaping

### Requirement 2

**User Story:** As an administrator, I want to export boat registration data in various formats, so that I can analyze registrations and share data with race organizers.

#### Acceptance Criteria

1. WHEN an administrator requests boat registration export THEN the Export API SHALL return all boat registration records regardless of status with race names and team manager information as JSON
2. WHEN the Export API returns boat registration data THEN the data SHALL include complete boat details including boat ID, event type, boat type, race name, registration status, forfait flag, crew composition, seat assignments, and team manager details
3. WHEN the Export API returns boat registration data THEN the data SHALL be sorted by team manager name, then by event type, then by boat type
4. WHEN the Frontend Formatter receives boat registration JSON data THEN the Frontend Formatter SHALL convert the data to CSV format with appropriate headers
5. WHEN the Frontend Formatter calculates filled seats THEN the Frontend Formatter SHALL format as "X/Y" where X is filled and Y is total

### Requirement 3

**User Story:** As an administrator, I want to export race data for CrewTimer, so that I can import timing data into the CrewTimer system.

#### Acceptance Criteria

1. WHEN an administrator requests race export THEN the Export API SHALL return all races, boats, crew members, team managers, and system configuration as JSON
2. WHEN the Export API returns race data THEN the data SHALL include complete race details with boat type, distance, age category, gender category, short name, and display order
3. WHEN the Export API returns race data THEN the data SHALL include all boats regardless of status (complete, paid, free, incomplete, or forfait)
4. WHEN the Export API returns boat data THEN each boat SHALL include registration status, boat type, event type, race ID, forfait flag, and crew composition details
5. WHEN the Export API returns boat data THEN each boat SHALL include calculated fields such as age category, gender category, average age, and filled seat count
6. WHEN the Export API returns boat data THEN each boat SHALL include complete seat assignments with crew member IDs, positions, and seat types
7. WHEN the Export API returns race data THEN the data SHALL include all crew members with personal details including name, date of birth, gender, and license number
8. WHEN the Export API returns system configuration THEN the configuration SHALL include marathon_start_time, semi_marathon_start_time, semi_marathon_interval_seconds, marathon_bow_start, and semi_marathon_bow_start
9. WHEN the Frontend Formatter receives race JSON data THEN the Frontend Formatter SHALL apply CrewTimer-specific transformations including race name formatting, event numbering, and bow numbering
10. WHEN the Frontend Formatter formats race names THEN the Frontend Formatter SHALL use the race's short_name field if available
11. WHEN the Frontend Formatter formats race names for French locale THEN the Frontend Formatter SHALL translate gender markers in short_name (W→F for femme, X→M for mixte, M→H for homme)
12. WHEN the Frontend Formatter assigns event numbers THEN the Frontend Formatter SHALL increment event number only when starting a new race
13. WHEN the Frontend Formatter assigns bow numbers for marathon races THEN the Frontend Formatter SHALL use sequential numbering starting from marathon_bow_start configuration value
14. WHEN the Frontend Formatter assigns bow numbers for semi-marathon races THEN the Frontend Formatter SHALL use sequential numbering starting from semi_marathon_bow_start configuration value
15. WHEN the Frontend Formatter sorts races THEN the Frontend Formatter SHALL sort by display_order field
16. WHEN the Frontend Formatter filters boats for CrewTimer export THEN the Frontend Formatter SHALL include only boats with status complete, paid, or free and exclude boats marked as forfait
17. WHEN the Frontend Formatter calculates start times for marathon boats THEN all boats in the same marathon race SHALL have the same start time
18. WHEN the Frontend Formatter calculates start times for semi-marathon boats THEN each boat SHALL have a start time incremented by semi_marathon_interval_seconds from the previous boat
19. WHEN the Frontend Formatter formats event times THEN the Frontend Formatter SHALL convert 24-hour time to 12-hour format with AM/PM
20. WHEN the Frontend Formatter has access to all boat details THEN the Frontend Formatter SHALL be able to display or export any field including age category, gender category, club affiliation, and crew composition

### Requirement 4

**User Story:** As a developer, I want consistent API response formats across all export endpoints, so that I can write reusable frontend code and easily add new export formats.

#### Acceptance Criteria

1. WHEN any Export API endpoint is called THEN the Export API SHALL return JSON data with a consistent structure including success status and data payload
2. WHEN the Export API encounters an error THEN the Export API SHALL return a JSON error response with error code and message
3. WHEN the Export API returns data THEN the Export API SHALL include metadata such as total count and timestamp
4. WHEN the Export API processes Decimal types from DynamoDB THEN the Export API SHALL convert Decimal values to float or int for JSON serialization
5. WHEN the Frontend Formatter is implemented THEN the Frontend Formatter SHALL be a reusable utility function that accepts JSON data and returns formatted output

### Requirement 5

**User Story:** As an administrator, I want export operations to handle large datasets efficiently, so that exports complete successfully without timeouts.

#### Acceptance Criteria

1. WHEN the Export API scans DynamoDB tables THEN the Export API SHALL handle pagination using LastEvaluatedKey
2. WHEN the Export API retrieves related data THEN the Export API SHALL cache lookups to minimize database queries
3. WHEN the Export API processes data THEN the Export API SHALL log progress for monitoring and debugging
4. WHEN the Frontend Formatter processes large datasets THEN the Frontend Formatter SHALL use efficient data structures and avoid unnecessary iterations
5. WHEN the Frontend Formatter generates files THEN the Frontend Formatter SHALL use streaming or chunking for large outputs

### Requirement 6

**User Story:** As a developer, I want comprehensive tests for both backend and frontend export logic, so that I can confidently refactor and add new features.

#### Acceptance Criteria

1. WHEN backend export endpoints are implemented THEN integration tests SHALL verify correct JSON data structure and content
2. WHEN backend export endpoints are implemented THEN integration tests SHALL verify pagination handling for large datasets
3. WHEN backend export endpoints are implemented THEN integration tests SHALL verify error handling for missing or invalid data
4. WHEN frontend formatters are implemented THEN unit tests SHALL verify correct transformation of JSON to target format
5. WHEN frontend formatters are implemented THEN unit tests SHALL verify edge cases such as empty data, special characters, and missing fields
6. WHEN frontend formatters are implemented THEN unit tests SHALL verify format-specific rules like CrewTimer race name formatting

### Requirement 7

**User Story:** As an administrator, I want to export an event program with crew member list and race schedule, so that I can print race day materials for participants and organizers.

#### Acceptance Criteria

1. WHEN an administrator requests event program export THEN the Frontend Formatter SHALL generate an Excel file with multiple sheets
2. WHEN the Frontend Formatter generates the crew member list sheet THEN the sheet SHALL include columns for last name, first name, club, race abbreviation, race name, race number, stroke seat, and bow number
3. WHEN the Frontend Formatter generates the crew member list THEN crew members SHALL be sorted alphabetically by last name
4. WHEN the Frontend Formatter generates the crew member list THEN only crew members from eligible boats (complete/paid/free, not forfait) SHALL be included
5. WHEN the Frontend Formatter generates the race schedule sheet THEN the sheet SHALL include columns for race abbreviation, race name, race number, and start time
6. WHEN the Frontend Formatter generates the race schedule THEN races SHALL be sorted by race number
7. WHEN the Frontend Formatter generates the race schedule THEN only races with at least one eligible boat SHALL be included
8. WHEN the Frontend Formatter formats times in the race schedule THEN times SHALL be displayed in 24-hour format (HH:MM)
9. WHEN the Frontend Formatter generates the event program for French locale THEN sheet names SHALL be in French ("Liste des équipiers" and "Programme des courses")
10. WHEN the Frontend Formatter generates the event program for English locale THEN sheet names SHALL be in English ("Crew Member List" and "Race Schedule")
11. WHEN the Frontend Formatter generates the event program THEN race and bow number assignments SHALL use the same shared logic as CrewTimer export to ensure consistency

### Requirement 8

**User Story:** As an administrator, I want backward compatibility during the refactoring, so that existing export functionality continues to work while new endpoints are developed.

#### Acceptance Criteria

1. WHEN new JSON export endpoints are created THEN existing CSV export endpoints SHALL remain functional
2. WHEN the frontend is updated to use new endpoints THEN the frontend SHALL gracefully fall back to old endpoints if new endpoints fail
3. WHEN all exports are migrated to the new architecture THEN old CSV export endpoints MAY be deprecated with appropriate notice
4. WHEN deprecating old endpoints THEN the Export API SHALL return deprecation warnings in response headers
5. WHEN the migration is complete THEN documentation SHALL be updated to reflect the new architecture
