# Requirements Document

## Introduction

This specification defines how boat club information should be calculated, stored, displayed, and exported throughout the Impressionnistes registration system. The goal is to provide clear, accurate club information that handles both single-club and multi-club crews in a simple and practical way.

## Glossary

- **Boat**: A boat registration (crew) entered by a team manager
- **Crew_Member**: An individual rower or coxswain assigned to a boat
- **Club_Affiliation**: The rowing club a crew member belongs to
- **Single_Club_Crew**: A boat where all assigned crew members belong to the same club
- **Multi_Club_Crew**: A boat where assigned crew members belong to two or more different clubs
- **Boat_Club_Display**: The calculated club name to display for a boat (either a single club name or "Multi-Club")
- **Club_List**: The list of unique clubs represented in a boat's crew

## Requirements

### Requirement 1: Calculate Boat Club Display

**User Story:** As a system, I want to calculate the appropriate club display for each boat, so that users see accurate club information with the registering club always visible.

#### Acceptance Criteria

1. WHEN all assigned crew members belong to the team manager's club, THE System SHALL set the boat_club_display to the team manager's club name
2. WHEN assigned crew members belong to multiple different clubs, THE System SHALL set the boat_club_display to "{team_manager_club} (Multi-Club)"
3. WHEN all assigned crew members belong to a single club different from the team manager's club, THE System SHALL set the boat_club_display to "{team_manager_club} ({crew_club})"
4. WHEN a boat has no assigned crew members, THE System SHALL set the boat_club_display to the team manager's club
5. WHEN comparing club affiliations, THE System SHALL use case-insensitive comparison
6. WHEN a crew member has an empty or null club_affiliation, THE System SHALL exclude them from the club calculation

### Requirement 2: Calculate Club List

**User Story:** As a system, I want to maintain a list of unique clubs in each boat, so that detailed club information is available.

#### Acceptance Criteria

1. WHEN crew members are assigned to a boat, THE System SHALL create a list of unique club names from all assigned crew members
2. WHEN creating the club list, THE System SHALL exclude empty or null club affiliations
3. WHEN creating the club list, THE System SHALL preserve the original case of club names
4. WHEN creating the club list, THE System SHALL sort clubs alphabetically
5. WHEN a boat has no assigned crew members with clubs, THE System SHALL include only the team manager's club in the list

### Requirement 3: Store Boat Club Information

**User Story:** As a developer, I want boat club information stored in the database, so that it can be efficiently retrieved and displayed.

#### Acceptance Criteria

1. THE System SHALL store boat_club_display as a string field on each boat registration
2. THE System SHALL store club_list as an array of strings on each boat registration
3. WHEN a crew member is assigned to or removed from a boat, THE System SHALL recalculate and update boat_club_display and club_list
4. WHEN a boat registration is updated, THE System SHALL recalculate and update boat_club_display and club_list
5. WHEN a boat is created, THE System SHALL initialize boat_club_display to the team manager's club and club_list to contain only the team manager's club

### Requirement 4: Display Club in Admin Boats Page

**User Story:** As an administrator, I want to see the boat's club in the boats list, so that I can quickly identify which club registered each boat and the crew composition.

#### Acceptance Criteria

1. WHEN viewing the admin boats page, THE System SHALL display boat_club_display in the club column
2. WHEN a boat displays "{club} (Multi-Club)", THE System SHALL provide a way to view the full club_list
3. WHEN hovering over or clicking a multi-club or external crew entry, THE System SHALL show a tooltip or popover with all clubs in club_list
4. WHEN filtering by club, THE System SHALL match boats where the team manager's club or any club in club_list contains the filter text
5. WHEN sorting by club, THE System SHALL sort by boat_club_display

### Requirement 5: Display Club in Team Manager Interface

**User Story:** As a team manager, I want to see my boat's club information, so that I understand how my crew is classified.

#### Acceptance Criteria

1. WHEN viewing my boats, THE System SHALL display boat_club_display for each boat showing my club as the registering club
2. WHEN my boat has crew from multiple clubs, THE System SHALL clearly indicate this with "{my_club} (Multi-Club)"
3. WHEN viewing boat details, THE System SHALL show the complete club_list
4. WHEN all my crew members are from my club, THE System SHALL display only my club name

### Requirement 6: Export Club Information to CSV

**User Story:** As an administrator, I want to export boat club information to CSV, so that I can analyze and share crew data.

#### Acceptance Criteria

1. WHEN exporting boats to CSV, THE System SHALL include a "Club" column with boat_club_display
2. WHEN exporting boats to CSV, THE System SHALL include a "Club List" column with all clubs from club_list separated by semicolons
3. WHEN a boat has all crew from the team manager's club, THE "Club" column SHALL show only the club name
4. WHEN a boat is multi-club, THE "Club" column SHALL show "{team_manager_club} (Multi-Club)" and "Club List" SHALL show all clubs
5. WHEN exporting, THE System SHALL preserve the original case of club names

### Requirement 7: Export Club Information to CrewTimer

**User Story:** As an administrator, I want to export boat club information to CrewTimer format, so that race timing systems have accurate club data.

#### Acceptance Criteria

1. WHEN exporting to CrewTimer format, THE System SHALL use boat_club_display for the "Crew" field
2. WHEN a boat has all crew from the team manager's club, THE "Crew" field SHALL contain the club name
3. WHEN a boat is multi-club, THE "Crew" field SHALL contain "{team_manager_club} (Multi-Club)"
4. WHEN exporting to CrewTimer, THE System SHALL maintain compatibility with existing CrewTimer import requirements
5. THE System SHALL NOT include the detailed club_list in CrewTimer export (as CrewTimer format has no field for this)

### Requirement 8: Export Club Information to Event Program

**User Story:** As an administrator, I want to export boat club information to event program format, so that printed programs show accurate club information.

#### Acceptance Criteria

1. WHEN exporting to event program format, THE System SHALL use boat_club_display for the club field
2. WHEN a boat is multi-club, THE System SHALL display "{team_manager_club} (Multi-Club)" in the program
3. WHEN exporting in French, THE System SHALL keep the format "{club} (Multi-Club)" (works in both languages)
4. WHEN exporting in English, THE System SHALL use "{club} (Multi-Club)"
5. THE System SHALL maintain consistent club display across all export formats

### Requirement 9: Handle Edge Cases

**User Story:** As a system, I want to handle edge cases gracefully, so that club information is always accurate and meaningful.

#### Acceptance Criteria

1. WHEN a crew member's club_affiliation is updated, THE System SHALL recalculate boat_club_display and club_list for all boats they are assigned to
2. WHEN the team manager's club is updated, THE System SHALL recalculate boat_club_display and club_list for all their boats with no assigned crew
3. WHEN all crew members have empty club affiliations, THE System SHALL use the team manager's club
4. WHEN comparing clubs, THE System SHALL treat "RCPM", "rcpm", and "Rcpm" as the same club
5. WHEN a boat has only a coxswain assigned, THE System SHALL calculate club based on that single crew member

### Requirement 10: Backward Compatibility

**User Story:** As a developer, I want to maintain backward compatibility, so that existing functionality continues to work.

#### Acceptance Criteria

1. THE System SHALL continue to maintain the is_multi_club_crew boolean field for backward compatibility
2. WHEN boat_club_display contains "(Multi-Club)", THE is_multi_club_crew field SHALL be true
3. WHEN boat_club_display does not contain "(Multi-Club)", THE is_multi_club_crew field SHALL be false
4. THE System SHALL continue to export team_manager_club in addition to boat_club_display
5. THE System SHALL not break existing API contracts or frontend components during migration
