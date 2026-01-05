# Requirements Document: Admin Impersonation

## Introduction

This feature enables administrators to view and interact with the application as if they were a specific team manager, without needing separate credentials. This allows admins to troubleshoot issues, assist team managers, and perform administrative tasks using the same interface that team managers see, eliminating the need to build duplicate admin interfaces for every team manager feature.

## Glossary

- **Admin**: A user with administrative privileges who belongs to the 'admins' Cognito group
- **Team_Manager**: A user who manages crew members and boat registrations
- **Impersonation**: The act of an admin viewing the application as a specific team manager
- **Effective_User_ID**: The user ID used for data access - either the impersonated team manager's ID or the admin's own ID
- **Impersonation_Bar**: A visual component displayed at the top of the application showing impersonation status
- **Query_Parameter**: The URL parameter `team_manager_id` that persists impersonation state across navigation

## Requirements

### Requirement 1: Admin Impersonation Selection

**User Story:** As an admin, I want to select a team manager to impersonate, so that I can view and manage their data using the team manager interface.

#### Acceptance Criteria

1. WHEN an admin is logged in, THE System SHALL display an impersonation selector component
2. WHEN the impersonation selector is displayed, THE System SHALL show a dropdown list of all team managers with their names and emails
3. WHEN an admin selects a team manager from the dropdown, THE System SHALL set the impersonation state and reload the current page with the team manager's data
4. WHEN an admin is not logged in, THE System SHALL NOT display the impersonation selector
5. WHEN a non-admin user is logged in, THE System SHALL NOT display the impersonation selector

### Requirement 2: Impersonation State Persistence

**User Story:** As an admin, I want my impersonation selection to persist across page navigation and browser refreshes, so that I don't have to re-select the team manager every time I navigate.

#### Acceptance Criteria

1. WHEN an admin selects a team manager to impersonate, THE System SHALL add `team_manager_id` to the URL query parameters
2. WHEN an admin navigates to a different page, THE System SHALL preserve the `team_manager_id` query parameter in the URL
3. WHEN an admin refreshes the browser, THE System SHALL restore the impersonation state from the URL query parameter
4. WHEN an admin shares a URL with `team_manager_id` parameter, THE System SHALL allow another admin to open that URL and view the same team manager's data
5. WHEN the impersonation state changes, THE System SHALL update the URL query parameter without triggering a full page reload

### Requirement 3: Visual Impersonation Indicator

**User Story:** As an admin, I want a clear visual indicator when I'm impersonating a team manager, so that I always know whose data I'm viewing and don't confuse it with my own.

#### Acceptance Criteria

1. WHEN an admin is impersonating a team manager, THE System SHALL display a prominent impersonation bar at the top of the page
2. WHEN the impersonation bar is displayed, THE System SHALL show the team manager's full name and email address
3. WHEN the impersonation bar is displayed, THE System SHALL use a distinctive background color (warning/alert style) to make it visually prominent
4. WHEN the impersonation bar is displayed, THE System SHALL remain visible while scrolling (sticky/fixed position)
5. WHEN an admin is not impersonating, THE System SHALL NOT display the impersonation bar

### Requirement 4: Exit Impersonation

**User Story:** As an admin, I want to easily exit impersonation mode, so that I can return to viewing my own admin interface.

#### Acceptance Criteria

1. WHEN an admin is impersonating a team manager, THE Impersonation_Bar SHALL display an "Exit Impersonation" button
2. WHEN an admin clicks the "Exit Impersonation" button, THE System SHALL clear the impersonation state
3. WHEN impersonation is cleared, THE System SHALL remove the `team_manager_id` query parameter from the URL
4. WHEN impersonation is cleared, THE System SHALL reload the current page with the admin's own data
5. WHEN impersonation is cleared, THE System SHALL hide the impersonation bar

### Requirement 5: Backend API Support

**User Story:** As a system, I need to support admin impersonation in the backend API, so that admins can access team manager data through existing endpoints.

#### Acceptance Criteria

1. WHEN an API request includes a `team_manager_id` query parameter, THE System SHALL validate that the authenticated user is an admin
2. WHEN an admin makes an API request with `team_manager_id` parameter, THE System SHALL use that team manager ID for data access instead of the admin's user ID
3. WHEN a non-admin user makes an API request with `team_manager_id` parameter, THE System SHALL reject the request with a 403 Forbidden error
4. WHEN an admin makes an API request without `team_manager_id` parameter, THE System SHALL use the admin's own user ID for data access
5. WHEN an admin impersonates a team manager, THE System SHALL maintain the admin's JWT token and identity for audit logging

### Requirement 6: API Client Integration

**User Story:** As a developer, I want the API client to automatically include the impersonation parameter, so that individual components don't need to manually add it to every request.

#### Acceptance Criteria

1. WHEN the impersonation state is set, THE API_Client SHALL automatically add `team_manager_id` as a query parameter to all API requests
2. WHEN the impersonation state is cleared, THE API_Client SHALL stop adding the `team_manager_id` query parameter
3. WHEN an API request already has query parameters, THE API_Client SHALL append `team_manager_id` without overwriting existing parameters
4. WHEN making API requests, THE System SHALL preserve the original request method, headers, and body
5. WHEN the API client adds the query parameter, THE System SHALL do so transparently without requiring changes to existing API call code

### Requirement 7: Team Manager List API

**User Story:** As an admin, I need to see a list of all team managers, so that I can select which one to impersonate.

#### Acceptance Criteria

1. THE System SHALL provide an API endpoint to list all team managers
2. WHEN an admin requests the team manager list, THE System SHALL return all users in the 'team_managers' Cognito group
3. WHEN returning team manager data, THE System SHALL include user ID, first name, last name, email, and club affiliation
4. WHEN a non-admin requests the team manager list, THE System SHALL reject the request with a 403 Forbidden error
5. WHEN the team manager list is empty, THE System SHALL return an empty array

### Requirement 8: Audit Logging

**User Story:** As a system administrator, I want to track when admins impersonate team managers, so that I can maintain accountability and security.

#### Acceptance Criteria

1. WHEN an admin makes an API request while impersonating, THE System SHALL log the admin's real user ID
2. WHEN an admin makes an API request while impersonating, THE System SHALL log the impersonated team manager ID
3. WHEN an admin makes an API request while impersonating, THE System SHALL log the action performed
4. WHEN logging impersonation actions, THE System SHALL include timestamps
5. WHEN logging impersonation actions, THE System SHALL include the API endpoint accessed

### Requirement 9: Security Constraints

**User Story:** As a security officer, I want to ensure that impersonation cannot be abused, so that the system remains secure.

#### Acceptance Criteria

1. THE System SHALL only allow users in the 'admins' Cognito group to impersonate team managers
2. WHEN a user attempts to impersonate without admin privileges, THE System SHALL reject the request with a 403 Forbidden error
3. WHEN validating impersonation requests, THE System SHALL verify the JWT token is valid and not expired
4. THE System SHALL NOT allow impersonation of other admin users
5. WHEN an admin impersonates a team manager, THE System SHALL allow the admin to bypass date restrictions and business rule limitations that would normally apply to team managers

### Requirement 10: Frontend State Management

**User Story:** As a developer, I want impersonation state managed centrally, so that all components can easily access the current impersonation status.

#### Acceptance Criteria

1. THE System SHALL store impersonation state in the existing auth store (Pinia)
2. WHEN impersonation state changes, THE System SHALL provide reactive getters for components to access
3. THE System SHALL provide an `effectiveUserId` getter that returns the impersonated ID or the admin's ID
4. THE System SHALL provide an `isImpersonating` getter that returns true when impersonating
5. THE System SHALL synchronize the store state with URL query parameters bidirectionally

### Requirement 11: Admin Override for Business Rules

**User Story:** As an admin, I want to bypass date restrictions and business rule limitations when impersonating a team manager, so that I can help team managers who missed deadlines and fix data issues at any time.

#### Acceptance Criteria

1. WHEN an admin impersonates a team manager, THE System SHALL set an `_is_admin_override` flag in the Lambda event context
2. WHEN validation functions check business rules, THE System SHALL skip date restrictions if `_is_admin_override` is true
3. WHEN validation functions check business rules, THE System SHALL skip registration deadline checks if `_is_admin_override` is true
4. WHEN validation functions check business rules, THE System SHALL skip payment requirement checks if `_is_admin_override` is true
5. WHEN an admin override occurs, THE System SHALL log which restrictions were bypassed for audit purposes

## Non-Functional Requirements

### Performance
- Impersonation state changes should complete within 500ms
- Team manager list should load within 2 seconds
- URL parameter synchronization should not cause visible page flicker

### Usability
- The impersonation bar should be immediately visible and distinguishable
- Team manager selection should support search/filter for large lists
- The interface should work on mobile devices (responsive design)

### Security
- All impersonation actions must be logged for audit purposes
- JWT tokens must remain valid and secure during impersonation
- Impersonation must not expose sensitive admin-only data to team managers

### Compatibility
- Must work with existing authentication system (AWS Cognito)
- Must not break existing team manager or admin functionality
- Must work across all supported browsers (Chrome, Firefox, Safari, Edge)
