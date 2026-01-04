# Requirements Document

## Introduction

This specification defines two enhancements to boat registrations in the Impressionnistes registration system:
1. **Simplified Club Display**: Change boat_club_display from a formatted string to a simple comma-separated list of unique clubs
2. **Boat Number Identifier**: Add a unique, human-readable identifier for each boat to facilitate race organization and timing

## Glossary

- **Boat**: A boat registration (crew) entered by a team manager
- **Boat_Club_Display**: The comma-separated list of unique clubs represented in a boat's crew
- **Club_List**: The array of unique clubs stored in the database (unchanged)
- **Boat_Number**: A unique identifier for each boat in format: [M/SM].[display_order].[sequence]
- **Event_Type**: The race distance - either "42km" (Marathon) or "21km" (Semi-Marathon)
- **Display_Order**: The sequential order number assigned to each race (1-55)
- **Sequence_Number**: A unique incrementing number within each race (1-9999)
- **Race**: A specific competition category (e.g., "Master Women 4X+")

## Requirements

### Requirement 1: Simplify Boat Club Display

**User Story:** As a user, I want to see a simple list of clubs for each boat, so that I can quickly understand which clubs are represented without complex formatting.

#### Acceptance Criteria

1. WHEN a boat has crew members from one or more clubs, THE System SHALL set boat_club_display to a comma-separated list of unique club names
2. WHEN a boat has crew from clubs "RCPM", "Club Elite", and "SN Versailles", THE boat_club_display SHALL be "RCPM, Club Elite, SN Versailles"
3. WHEN a boat has all crew from a single club "RCPM", THE boat_club_display SHALL be "RCPM"
4. WHEN a boat has no assigned crew members, THE boat_club_display SHALL be the team manager's club
5. WHEN creating the club list, THE System SHALL sort clubs alphabetically (case-insensitive)
6. WHEN creating the club list, THE System SHALL exclude empty or null club affiliations
7. WHEN creating the club list, THE System SHALL preserve the original case of club names

### Requirement 2: Generate Boat Number Identifier

**User Story:** As a race organizer, I want each boat to have a unique, readable identifier, so that I can easily reference boats during race organization and timing.

#### Acceptance Criteria

1. WHEN a boat is assigned to a race, THE System SHALL generate a boat_number in the format "[M/SM].[display_order].[sequence]"
2. WHEN a boat is registered for a 42km race, THE boat_number SHALL start with "M" (Marathon)
3. WHEN a boat is registered for a 21km race, THE boat_number SHALL start with "SM" (Semi-Marathon)
4. WHEN a boat is assigned to a race, THE System SHALL use the race's display_order as the second component
5. WHEN generating the sequence number, THE System SHALL use a simple incrementing counter starting at 1 for each race
6. WHEN a boat is the first boat in race with display_order 15, THE boat_number SHALL be "SM.15.1"
7. WHEN a boat is the third boat in race with display_order 1, THE boat_number SHALL be "M.1.3"
8. WHEN a boat's race assignment is changed, THE System SHALL regenerate the boat_number for the new race
9. WHEN a boat has no race assigned, THE boat_number SHALL be null or empty

### Requirement 3: Ensure Boat Number Uniqueness

**User Story:** As a system, I want to ensure boat numbers are unique within each race, so that there are no conflicts during race organization.

#### Acceptance Criteria

1. WHEN generating a sequence number for a race, THE System SHALL find the highest existing sequence number for that race and increment by 1
2. WHEN a boat is removed from a race, THE System SHALL NOT reuse its sequence number for new boats
3. WHEN multiple boats are assigned to the same race simultaneously, THE System SHALL ensure each gets a unique sequence number
4. WHEN a race has boats with sequence numbers 1, 2, 5, 7, THE next boat SHALL receive sequence number 8 (not 3)
5. THE System SHALL guarantee that no two boats in the same race have the same boat_number

### Requirement 4: Store Boat Number

**User Story:** As a developer, I want boat_number stored in the database, so that it can be efficiently retrieved and displayed.

#### Acceptance Criteria

1. THE System SHALL store boat_number as a string field on each boat registration
2. WHEN a boat is created without a race, THE boat_number SHALL be null
3. WHEN a boat is assigned to a race, THE System SHALL calculate and store boat_number
4. WHEN a boat's race is changed, THE System SHALL recalculate and update boat_number
5. WHEN a boat's race is removed, THE System SHALL set boat_number to null

### Requirement 5: Display Boat Number in Admin Interface

**User Story:** As an administrator, I want to see the boat number in the boats list, so that I can quickly identify and reference boats.

#### Acceptance Criteria

1. WHEN viewing the admin boats page, THE System SHALL display boat_number in a dedicated column
2. WHEN a boat has no race assigned, THE boat_number column SHALL show "-" or "Not assigned"
3. WHEN sorting by boat_number, THE System SHALL sort alphanumerically (M.1.1, M.1.2, M.2.1, SM.15.1, etc.)
4. WHEN filtering boats, THE System SHALL allow filtering by boat_number
5. WHEN exporting boats, THE System SHALL include boat_number in the export

### Requirement 6: Display Boat Number in Team Manager Interface

**User Story:** As a team manager, I want to see my boat's number, so that I know how to reference it during the event.

#### Acceptance Criteria

1. WHEN viewing my boats, THE System SHALL display boat_number for each boat with a race assigned
2. WHEN my boat has no race assigned, THE System SHALL show "Race not selected" instead of a boat number
3. WHEN viewing boat details, THE System SHALL prominently display the boat_number
4. WHEN printing or exporting my boat information, THE System SHALL include the boat_number

### Requirement 7: Export Boat Number to CSV

**User Story:** As an administrator, I want to export boat numbers to CSV, so that I can use them in external systems.

#### Acceptance Criteria

1. WHEN exporting boats to CSV, THE System SHALL include a "Boat Number" column with boat_number
2. WHEN a boat has no race assigned, THE "Boat Number" column SHALL be empty
3. WHEN exporting, THE System SHALL maintain the boat_number format exactly as stored
4. THE System SHALL include boat_number in all boat export formats

### Requirement 8: Export Boat Number to CrewTimer

**User Story:** As an administrator, I want to export boat numbers to CrewTimer format, so that timing systems can use them for race identification.

#### Acceptance Criteria

1. WHEN exporting to CrewTimer format, THE System SHALL include boat_number in the "Bow" field
2. WHEN a boat has no boat_number, THE "Bow" field SHALL use a fallback value (e.g., sequential number)
3. WHEN exporting to CrewTimer, THE System SHALL ensure boat_number is compatible with CrewTimer import requirements
4. THE System SHALL maintain backward compatibility with existing CrewTimer exports

### Requirement 9: Export Boat Number to Event Program

**User Story:** As an administrator, I want to export boat numbers to event program format, so that printed programs show boat identifiers.

#### Acceptance Criteria

1. WHEN exporting to event program format, THE System SHALL include boat_number for each boat
2. WHEN a boat has no boat_number, THE System SHALL omit it or show "TBD"
3. WHEN exporting in French or English, THE boat_number format SHALL remain unchanged (language-independent)
4. THE System SHALL display boat_number prominently in the program layout

### Requirement 10: Update Club Display in All Locations

**User Story:** As a user, I want to see the simplified club list everywhere boats are displayed, so that club information is consistent across the system.

#### Acceptance Criteria

1. WHEN viewing boats in the admin interface, THE System SHALL display the comma-separated club list
2. WHEN viewing boats in the team manager interface, THE System SHALL display the comma-separated club list
3. WHEN exporting to CSV, THE System SHALL use the comma-separated club list in the "Club" column
4. WHEN exporting to CrewTimer, THE System SHALL use the comma-separated club list in the "Crew" field
5. WHEN exporting to event program, THE System SHALL use the comma-separated club list

### Requirement 11: Remove Multi-Club Indicator

**User Story:** As a developer, I want to remove the multi-club indicator logic, so that the system is simpler and easier to maintain.

#### Acceptance Criteria

1. THE System SHALL remove the "(Multi-Club)" suffix from boat_club_display
2. THE System SHALL remove the "{team_manager_club} ({crew_club})" format from boat_club_display
3. THE System SHALL remove the ClubListPopover component (no longer needed)
4. THE System SHALL remove multi-club detection logic from frontend components
5. THE System SHALL keep the is_multi_club_crew field for backward compatibility but calculate it as: club_list.length > 1

### Requirement 12: Maintain Backward Compatibility

**User Story:** As a developer, I want to maintain backward compatibility, so that existing functionality continues to work during migration.

#### Acceptance Criteria

1. THE System SHALL continue to maintain the club_list array field (unchanged)
2. THE System SHALL continue to maintain the is_multi_club_crew boolean field
3. WHEN club_list has more than one club, THE is_multi_club_crew field SHALL be true
4. WHEN club_list has one or zero clubs, THE is_multi_club_crew field SHALL be false
5. THE System SHALL not break existing API contracts during migration

### Requirement 13: Handle Edge Cases

**User Story:** As a system, I want to handle edge cases gracefully, so that boat numbers and club displays are always accurate.

#### Acceptance Criteria

1. WHEN a race's display_order is updated, THE System SHALL recalculate boat_number for all boats in that race
2. WHEN a boat is assigned to a race that doesn't exist, THE System SHALL return an error
3. WHEN generating boat_number fails, THE System SHALL log the error and set boat_number to null
4. WHEN a crew member's club is updated, THE System SHALL recalculate boat_club_display for all their boats
5. WHEN all crew members have empty clubs, THE System SHALL use the team manager's club in boat_club_display

### Requirement 14: Sequence Number Format

**User Story:** As a race organizer, I want sequence numbers to be short and readable, so that boat numbers are easy to communicate verbally.

#### Acceptance Criteria

1. WHEN generating sequence numbers, THE System SHALL use integers without leading zeros (1, 2, 3, not 001, 002, 003)
2. WHEN a race has more than 99 boats, THE System SHALL support sequence numbers up to 9999
3. WHEN displaying boat_number, THE System SHALL not truncate or abbreviate any component
4. THE boat_number format SHALL be optimized for readability (e.g., "SM.15.42" not "SM-015-0042")
5. THE System SHALL use periods (.) as separators between components for clarity

## Appendix A: Boat Number Examples

| Event Type | Race Display Order | Sequence | Boat Number | Description |
|------------|-------------------|----------|-------------|-------------|
| 42km | 1 | 1 | M.1.1 | First boat in first marathon race |
| 42km | 1 | 2 | M.1.2 | Second boat in first marathon race |
| 42km | 14 | 1 | M.14.1 | First boat in 14th marathon race |
| 21km | 15 | 1 | SM.15.1 | First boat in 15th race (first semi-marathon) |
| 21km | 15 | 12 | SM.15.12 | 12th boat in 15th race |
| 21km | 55 | 3 | SM.55.3 | Third boat in last race |

## Appendix B: Club Display Examples

| Crew Composition | Old boat_club_display | New boat_club_display |
|------------------|----------------------|----------------------|
| All RCPM | "RCPM" | "RCPM" |
| RCPM + Club Elite | "RCPM (Multi-Club)" | "Club Elite, RCPM" |
| RCPM + Club Elite + SN Versailles | "RCPM (Multi-Club)" | "Club Elite, RCPM, SN Versailles" |
| All Club Elite (TM is RCPM) | "RCPM (Club Elite)" | "Club Elite" |
| No crew (TM is RCPM) | "RCPM" | "RCPM" |

## Appendix C: Race Display Orders

Based on current race data:

**Marathon (42km):** Display orders 1-14
- M01-M14: Master and Senior skiff races

**Semi-Marathon (21km):** Display orders 15-55
- SM01-SM41: Various boat types (4+, 4-, 8+, 4x+, 4x-, 8x+)
- All age categories (J16, J18, Senior, Master)
- All gender categories (Men, Women, Mixed)
