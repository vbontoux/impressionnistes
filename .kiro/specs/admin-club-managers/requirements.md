# Requirements Document

## Introduction

This specification defines the Club Managers admin page, which allows administrators to view all club managers (team managers) and contact them via email. The feature leverages the existing `list_team_managers` API endpoint and provides a simple interface for bulk email communication.

## Glossary

- **Club_Manager**: A user who has created at least one boat registration or crew member
- **Admin**: A user with administrative privileges who can access admin-only pages
- **Team_Manager**: Synonym for Club_Manager (used interchangeably in the system)
- **Bulk_Email**: The ability to compose an email to multiple selected club managers at once

## Requirements

### Requirement 1: Display Club Managers List

**User Story:** As an admin, I want to view a list of all club managers, so that I can see who is managing teams in the system.

#### Acceptance Criteria

1. WHEN an admin navigates to the club managers page, THE System SHALL display a table with all club managers
2. WHEN displaying club managers, THE System SHALL show first name, last name, email, and club affiliation for each manager
3. WHEN the club managers list is loading, THE System SHALL display a loading indicator
4. WHEN no club managers exist, THE System SHALL display an appropriate empty state message
5. WHEN the API request fails, THE System SHALL display an error message with retry option

### Requirement 2: Individual Email Contact

**User Story:** As an admin, I want to click on a club manager's email address, so that I can quickly send them an individual email.

#### Acceptance Criteria

1. WHEN an email address is displayed, THE System SHALL render it as a clickable mailto link
2. WHEN an admin clicks an email address, THE System SHALL open the default email client with the recipient pre-filled

### Requirement 3: Bulk Email Selection

**User Story:** As an admin, I want to select multiple club managers and compose an email to all of them, so that I can efficiently communicate with multiple managers at once.

#### Acceptance Criteria

1. WHEN viewing the club managers list, THE System SHALL provide a checkbox for each manager
2. WHEN an admin clicks a checkbox, THE System SHALL toggle the selection state for that manager
3. WHEN an admin clicks "Select All", THE System SHALL select all visible club managers
4. WHEN an admin clicks "Deselect All", THE System SHALL deselect all selected club managers
5. WHEN managers are selected, THE System SHALL display the count of selected managers
6. WHEN an admin clicks "Email Selected" with managers selected, THE System SHALL open the default email client with all selected email addresses in the BCC field
7. WHEN no managers are selected, THE System SHALL disable the "Email Selected" button

### Requirement 4: Search and Filter

**User Story:** As an admin, I want to search and filter the club managers list, so that I can quickly find specific managers.

#### Acceptance Criteria

1. WHEN an admin types in the search field, THE System SHALL filter the list to show only managers matching the search term
2. WHEN filtering, THE System SHALL search across first name, last name, email, and club affiliation fields
3. WHEN the search field is cleared, THE System SHALL display all club managers again

### Requirement 5: Admin Dashboard Integration

**User Story:** As an admin, I want to access the club managers page from the admin dashboard, so that I can easily navigate to this feature.

#### Acceptance Criteria

1. WHEN an admin views the admin dashboard, THE System SHALL display a "Club Managers" card in the configuration sections
2. WHEN an admin clicks the "Club Managers" card, THE System SHALL navigate to the club managers page
3. WHEN a non-admin user attempts to access the club managers page, THE System SHALL redirect them to the dashboard

### Requirement 6: Responsive Design

**User Story:** As an admin, I want the club managers page to work on mobile devices, so that I can manage communications on the go.

#### Acceptance Criteria

1. WHEN viewing on mobile devices, THE System SHALL display the table in a responsive format
2. WHEN viewing on small screens, THE System SHALL maintain readability and usability of all features
