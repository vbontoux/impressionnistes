# Requirements Document

## Introduction

This specification defines the refactoring of the admin export API endpoints to follow a consistent architecture where the backend provides raw JSON data and the frontend handles format-specific transformations (CSV, Excel, etc.). This improves maintainability, flexibility, and allows easy addition of new export formats without backend changes.

## Glossary

- **Export API**: Backend Lambda functions that retrieve and return data for administrative exports
- **Frontend Formatter**: JavaScript utilities that transform JSON data into specific export formats (CSV, Excel, CrewTimer)
- **Raw Data**: Unformatted database records returned as JSON from the API
- **Format-Specific Logic**: Transformations like race name formatting, column ordering, data type conversions specific to an export format
- **Team Manager**: User who manages crew members and boat registrations
- **Crew Member**: Individual rower or coxswain registered by a team manager
- **Boat Registration**: A boat entry with assigned crew members for a specific race

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

1. WHEN an administrator requests race export THEN the Export API SHALL return all races, boats, crew members, and system configuration as JSON
2. WHEN the Export API returns race data THEN the data SHALL include complete race details with boat type, distance, age category, and gender category
3. WHEN the Export API returns race data THEN the data SHALL include all boats regardless of status (complete, paid, free, incomplete, or forfait)
4. WHEN the Export API returns boat data THEN each boat SHALL include registration status, boat type, event type, race ID, forfait flag, and crew composition details
5. WHEN the Export API returns boat data THEN each boat SHALL include calculated fields such as age category, gender category, average age, and filled seat count
6. WHEN the Export API returns boat data THEN each boat SHALL include complete seat assignments with crew member IDs, positions, and seat types
7. WHEN the Export API returns race data THEN the data SHALL include all crew members with personal details including name, date of birth, gender, and license number
8. WHEN the Frontend Formatter receives race JSON data THEN the Frontend Formatter SHALL apply CrewTimer-specific transformations including race name formatting, event numbering, and bow numbering
9. WHEN the Frontend Formatter formats semi-marathon race names THEN the Frontend Formatter SHALL use the pattern: boat_type [Y if yolette] age_category gender_category
10. WHEN the Frontend Formatter formats marathon race names THEN the Frontend Formatter SHALL use the original race name from the database
11. WHEN the Frontend Formatter assigns event numbers THEN the Frontend Formatter SHALL increment event number only when starting a new race
12. WHEN the Frontend Formatter assigns bow numbers THEN the Frontend Formatter SHALL increment bow number globally across all boats in all races
13. WHEN the Frontend Formatter sorts races THEN the Frontend Formatter SHALL place marathon races before semi-marathon races
14. WHEN the Frontend Formatter filters boats for CrewTimer export THEN the Frontend Formatter SHALL include only boats with status complete, paid, or free and exclude boats marked as forfait
15. WHEN the Frontend Formatter has access to all boat details THEN the Frontend Formatter SHALL be able to display or export any field including age category, gender category, club affiliation, and crew composition

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

**User Story:** As an administrator, I want backward compatibility during the refactoring, so that existing export functionality continues to work while new endpoints are developed.

#### Acceptance Criteria

1. WHEN new JSON export endpoints are created THEN existing CSV export endpoints SHALL remain functional
2. WHEN the frontend is updated to use new endpoints THEN the frontend SHALL gracefully fall back to old endpoints if new endpoints fail
3. WHEN all exports are migrated to the new architecture THEN old CSV export endpoints MAY be deprecated with appropriate notice
4. WHEN deprecating old endpoints THEN the Export API SHALL return deprecation warnings in response headers
5. WHEN the migration is complete THEN documentation SHALL be updated to reflect the new architecture
