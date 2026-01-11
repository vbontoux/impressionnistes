# Requirements Document

## Introduction

This specification defines a new feature that allows team managers to optionally request a boat (hull) assignment from the event organizers when creating or editing a crew registration. This feature enables team managers to indicate they need a physical boat and provide details about their requirements, while allowing administrators to later assign specific boats to fulfill these requests.

## Glossary

- **Crew**: A boat registration (formerly called "boat") entered by a team manager, consisting of crew members assigned to seats
- **Boat (Hull)**: The physical rowing boat/shell that a crew will use during the race
- **Boat Request**: An optional request by a team manager to have a boat (hull) assigned by administrators
- **Boat Assignment**: The act of an administrator assigning a specific physical boat to a crew's request
- **Request Comment**: Free-text field where team managers can specify their boat preferences or requirements
- **Assigned Boat Identifier**: The identifier (name or number) of the physical boat assigned by administrators
- **Team_Manager**: The user who creates and manages crew registrations
- **Administrator**: User with admin privileges who can assign boats to requests
- **Registration_Status**: The status of a crew registration (incomplete, complete, free, paid)

## Requirements

### Requirement 1: Enable Boat Request Toggle

**User Story:** As a team manager, I want to optionally request a boat assignment, so that I can indicate when I need the organization to provide a physical boat.

#### Acceptance Criteria

1. WHEN creating or editing a crew, THE System SHALL display a toggle/checkbox to enable boat request
2. WHEN the boat request toggle is disabled (default), THE System SHALL not show boat request fields
3. WHEN the boat request toggle is enabled, THE System SHALL display boat request fields (comment and assigned boat)
4. WHEN saving a crew with boat request disabled, THE System SHALL set boat_request_enabled to false
5. WHEN saving a crew with boat request enabled, THE System SHALL set boat_request_enabled to true
6. THE System SHALL persist the boat_request_enabled state in the database

### Requirement 2: Capture Boat Request Comment

**User Story:** As a team manager, I want to provide details about the boat I need, so that administrators understand my requirements.

#### Acceptance Criteria

1. WHEN boat request is enabled, THE System SHALL display a text area for boat request comments
2. WHEN entering a boat request comment, THE System SHALL allow up to 500 characters
3. WHEN saving a crew, THE System SHALL store the boat_request_comment in the database
4. WHEN boat request is disabled, THE System SHALL clear any existing boat_request_comment
5. THE boat_request_comment field SHALL be optional (can be empty)
6. THE System SHALL preserve line breaks and formatting in boat_request_comment
7. WHEN displaying boat_request_comment, THE System SHALL show the full text without truncation

### Requirement 3: Display Assigned Boat (Read-Only)

**User Story:** As a team manager, I want to see which boat has been assigned to my crew and any related details, so that I know which physical boat to use and where to find it.

#### Acceptance Criteria

1. WHEN boat request is enabled, THE System SHALL display a read-only field for assigned boat
2. WHEN no boat has been assigned, THE assigned boat field SHALL display "Not yet assigned" or similar placeholder
3. WHEN a boat has been assigned by an administrator, THE assigned boat field SHALL display the boat name/number
4. WHEN a boat has been assigned with a comment, THE System SHALL display the assignment comment
5. WHEN viewing the crew list in card mode, THE System SHALL display the assigned boat name and comment directly
6. WHEN viewing the crew list in table mode, THE System SHALL display the assigned boat name and show the comment on hover
7. THE assigned boat field SHALL NOT be editable by team managers
8. THE assigned boat comment field SHALL NOT be editable by team managers
9. WHEN boat request is disabled, THE System SHALL not display the assigned boat fields
10. THE System SHALL clearly indicate that the assigned boat fields are read-only

### Requirement 4: Incomplete Status for Unassigned Requests

**User Story:** As a system, I want crews with pending boat requests to remain incomplete, so that team managers know they cannot proceed until a boat is assigned.

#### Acceptance Criteria

1. WHEN boat request is enabled AND assigned_boat_identifier is null or empty, THE crew SHALL be considered incomplete
2. WHEN boat request is enabled AND assigned_boat_identifier has a value, THE crew MAY be complete (if other conditions are met)
3. WHEN boat request is disabled, THE assigned_boat_identifier SHALL NOT affect completion status
4. WHEN calculating registration_status, THE System SHALL check boat request assignment status
5. WHEN displaying incomplete status, THE System SHALL indicate if waiting for boat assignment
6. THE System SHALL prevent payment for crews with pending boat requests

### Requirement 5: Store Boat Request Data

**User Story:** As a developer, I want boat request data stored in the database, so that it can be retrieved and managed efficiently.

#### Acceptance Criteria

1. THE System SHALL add a boat_request_enabled boolean field to crew registrations (default: false)
2. THE System SHALL add a boat_request_comment string field to crew registrations (nullable, max 500 chars)
3. THE System SHALL add an assigned_boat_identifier string field to crew registrations (nullable, max 100 chars)
4. THE System SHALL add an assigned_boat_comment string field to crew registrations (nullable, max 500 chars)
5. WHEN boat_request_enabled is false, THE boat_request_comment, assigned_boat_identifier, and assigned_boat_comment SHALL be null
6. WHEN boat_request_enabled is true, THE boat_request_comment MAY be null or have a value
7. WHEN boat_request_enabled is true, THE assigned_boat_identifier MAY be null (pending) or have a value (assigned)
8. WHEN boat_request_enabled is true, THE assigned_boat_comment MAY be null or have a value
9. THE System SHALL validate field lengths before saving

### Requirement 6: Display Boat Request in Team Manager Interface

**User Story:** As a team manager, I want to see boat request status in my crews list, so that I can quickly identify which crews are waiting for boat assignments.

#### Acceptance Criteria

1. WHEN viewing the crews list, THE System SHALL indicate which crews have boat requests enabled
2. WHEN a crew has a pending boat request, THE System SHALL show "Waiting for boat assignment" or similar indicator
3. WHEN a crew has an assigned boat, THE System SHALL display the assigned boat name/number
4. WHEN viewing crew details, THE System SHALL prominently display boat request information
5. WHEN a crew has no boat request, THE System SHALL not display boat request information

### Requirement 7: Display Boat Request in Admin Interface

**User Story:** As an administrator, I want to see which crews have requested boats, so that I can manage boat assignments efficiently.

#### Acceptance Criteria

1. WHEN viewing the admin crews list, THE System SHALL display a column for boat request status
2. WHEN a crew has boat request enabled, THE System SHALL show "Requested" or similar indicator
3. WHEN a crew has an assigned boat, THE System SHALL show the assigned boat name
4. WHEN a crew has no boat request, THE System SHALL show "-" or "No request"
5. WHEN filtering crews, THE System SHALL allow filtering by boat request status (requested, assigned, no request)
6. WHEN viewing crew details in admin, THE System SHALL display the full boat_request_comment
7. WHEN exporting crews, THE System SHALL include boat request fields in the export

### Requirement 8: Admin Boat Assignment

**User Story:** As an administrator, I want to assign boats to crew requests with additional details, so that team managers know which physical boats to use and where to find them.

#### Acceptance Criteria

1. WHEN viewing a crew with boat request enabled in admin interface, THE System SHALL provide a text input field to assign a boat
2. WHEN assigning a boat, THE System SHALL allow entering a boat name or number as free text
3. WHEN assigning a boat, THE System SHALL provide an optional text area for assignment details/comments
4. WHEN saving a boat assignment, THE System SHALL update the assigned_boat_identifier field
5. WHEN saving a boat assignment, THE System SHALL update the assigned_boat_comment field (if provided)
6. WHEN a boat is assigned, THE System SHALL recalculate the crew's completion status
7. THE System SHALL allow administrators to change or remove boat assignments by editing the text fields
8. WHEN clearing the assigned_boat_identifier field, THE crew SHALL return to incomplete status (if boat request is enabled)
9. THE assigned_boat_identifier field SHALL accept alphanumeric characters, spaces, and common punctuation
10. THE assigned_boat_comment field SHALL accept up to 500 characters
11. THE assigned_boat_comment field SHALL be optional (can be empty)

**Note:** In a future enhancement, this will be replaced with a dropdown selection from a boat inventory list. For now, administrators manually enter boat identifiers as text.

### Requirement 9: Validation Rules

**User Story:** As a system, I want to validate boat request data, so that data integrity is maintained.

#### Acceptance Criteria

1. WHEN boat_request_enabled is true, THE boat_request_comment SHALL be validated for maximum length (500 chars)
2. WHEN boat_request_enabled is true, THE assigned_boat_identifier SHALL be validated for maximum length (100 chars)
3. WHEN boat_request_enabled is true, THE assigned_boat_comment SHALL be validated for maximum length (500 chars)
4. WHEN boat_request_enabled is false, THE System SHALL ignore boat_request_comment, assigned_boat_identifier, and assigned_boat_comment values
5. WHEN saving invalid data, THE System SHALL return clear validation error messages
6. THE System SHALL sanitize boat_request_comment to prevent XSS attacks
7. THE System SHALL sanitize assigned_boat_comment to prevent XSS attacks
8. THE System SHALL trim whitespace from assigned_boat_identifier

### Requirement 10: Pricing Calculation with Boat Request

**User Story:** As a system, I want to calculate pricing correctly based on boat request status, so that teams are only charged when a boat is actually assigned and the crew is complete.

#### Acceptance Criteria

1. WHEN calculating payment for a crew with boat_request_enabled=false, THE System SHALL include Participation Fee (`base_seat_price`) for non-RCPM members only (existing behavior for crews using their own boats)
2. WHEN calculating payment for a crew with boat_request_enabled=true AND assigned_boat_identifier is null, THE System SHALL NOT calculate any prices (crew is incomplete, payment blocked)
3. WHEN calculating payment for a crew with boat_request_enabled=true AND assigned_boat_identifier has a value, THE System SHALL include Participation Fee (`base_seat_price`) AND Boat Rental (`rental_price`) for non-RCPM members (crew is using an RCPM boat)
4. WHEN calculating payment for any crew, THE System SHALL charge €0 for RCPM members (no Participation Fee, no Boat Rental)
5. WHEN displaying payment preview, THE System SHALL show Participation Fee and Boat Rental line items only if crew is complete
6. WHEN a crew becomes complete (boat assigned), THE System SHALL recalculate the total price including Participation Fee and Boat Rental for non-RCPM members
7. THE System SHALL prevent payment initiation for crews with pending boat requests (assigned_boat_identifier is null)
8. WHEN boat_request_enabled changes from true to false, THE System SHALL recalculate pricing to remove Boat Rental charges (crew now using own boat)

### Requirement 11: UI/UX Guidelines

**User Story:** As a user, I want the boat request interface to be intuitive, so that I can easily understand and use the feature.

#### Acceptance Criteria

1. THE boat request toggle SHALL have a clear label: "Request boat assignment from organizers"
2. THE boat request comment field SHALL have a helpful placeholder: "e.g., Beginner level, boat #42, etc."
3. THE assigned boat field SHALL be visually distinct as read-only (grayed out or disabled appearance)
4. WHEN boat request is enabled but not assigned, THE System SHALL show a clear status message
5. THE System SHALL use consistent terminology: "boat" for physical hull, "crew" for registration
6. THE System SHALL provide tooltips or help text explaining the boat request feature
7. THE UI SHALL be responsive and work on mobile devices

### Requirement 11: Backward Compatibility

**User Story:** As a developer, I want existing crews to work without modification, so that the feature is non-breaking.

#### Acceptance Criteria

1. WHEN loading existing crews without boat request fields, THE System SHALL default boat_request_enabled to false
2. WHEN displaying existing crews, THE System SHALL not show boat request information if not enabled
3. THE System SHALL not require database migration for existing crews (new fields are nullable)
4. WHEN exporting crews, THE System SHALL handle missing boat request fields gracefully
5. THE API SHALL remain backward compatible with existing clients

### Requirement 12: Edge Cases

**User Story:** As a system, I want to handle edge cases gracefully, so that the feature is robust.

#### Acceptance Criteria

1. WHEN a crew is paid, THE System SHALL not allow disabling boat request if a boat is assigned
2. WHEN a crew is deleted, THE System SHALL delete associated boat request data
3. WHEN boat_request_comment contains special characters, THE System SHALL display them correctly
3. WHEN assigned_boat_identifier is very long, THE System SHALL truncate it in list views with ellipsis
5. WHEN multiple administrators assign boats simultaneously, THE System SHALL prevent conflicts
6. WHEN a team manager disables boat request after assignment, THE System SHALL warn about losing assignment

## Appendix A: Boat Request States

| boat_request_enabled | assigned_boat_identifier | Status Display | Crew Complete? |
|---------------------|-------------------------|----------------|----------------|
| false | null | No request | Depends on other factors |
| false | "Boat 42" | No request (ignored) | Depends on other factors |
| true | null | Waiting for assignment | No (incomplete) |
| true | "Boat 42" | Assigned: Boat 42 | Depends on other factors |

## Appendix B: UI Mockup (Text Description)

### Team Manager - Create/Edit Crew Form

```
[Crew Details Section]
Event Type: 42km
Boat Type: 4+
Race: [Select Race]

[Boat Request Section]
☐ Request boat assignment from organizers
    (When checked, shows:)
    
    Boat Request Details:
    [Text area: "Describe your boat requirements..."]
    (e.g., Beginner level, boat #42, specific boat type, etc.)
    
    Assigned Boat:
    [Read-only field: "Not yet assigned" or "Boat 42"]
    (This will be filled by administrators)

[Continue with rest of form...]
```

### Admin - Crew List View

```
| Crew ID | Event | Boat Type | Status | Boat Request | Assigned Boat | Actions |
|---------|-------|-----------|--------|--------------|---------------|---------|
| 001 | 42km | 4+ | Complete | No request | - | View |
| 002 | 21km | 8+ | Incomplete | Requested | Not assigned | View / Assign |
| 003 | 42km | 4x+ | Complete | Requested | Boat 42 | View / Edit |
```

## Appendix C: Example Boat Request Comments

- "Beginner level crew, need stable boat"
- "Prefer boat #42 if available"
- "Elite level, racing shell"
- "Need boat suitable for mixed crew"
- "Lightweight boat for junior crew"
- "Boat with adjustable footboards"
