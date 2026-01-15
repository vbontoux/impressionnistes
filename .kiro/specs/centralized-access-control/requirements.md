# Requirements Document - Centralized Access Control System

## Introduction

The Centralized Access Control System manages permissions for all operations in the Course des Impressionnistes registration system. It determines which actions are permitted based on user role (admin, club manager), impersonation status, event phases (dates), and data state (paid boat, assigned crew member). The system applies these rules consistently across the backend (API) and frontend (UI).

### Current State

The system currently has:
- ✅ **Partial implementation**: Some data state restrictions exist (cannot delete assigned crew, cannot delete paid boats)
- ✅ **Infrastructure in place**: Admin impersonation, configuration system, date storage
- ⚠️ **Incomplete enforcement**: Many TODOs exist for date-based restrictions but are not implemented
- ❌ **No centralization**: Permission logic is scattered across multiple Lambda functions
- ❌ **No frontend enforcement**: All buttons are always enabled regardless of restrictions

### What This Spec Will Do

This specification will:
1. **Complete** the existing TODOs by implementing date-based restrictions
2. **Centralize** all permission logic into a single, maintainable module
3. **Synchronize** backend and frontend to enforce the same rules
4. **Add** missing features (temporary access grants, admin configuration UI)
5. **Improve** user experience with disabled buttons and clear feedback messages

See `EXISTING_PERMISSIONS_ANALYSIS.md` for detailed analysis of current implementation.

## Glossary

- **Access_Control_System**: Le système centralisé qui détermine si une action est autorisée ou non
- **Permission**: Une règle qui autorise ou interdit une action spécifique dans un contexte donné
- **Action**: Une opération que l'utilisateur peut tenter d'effectuer (créer, modifier, supprimer, payer)
- **Event_Phase**: La phase actuelle de l'événement basée sur les dates de configuration (avant ouverture, période d'inscription, après clôture, après deadline de paiement)
- **Admin_User**: Utilisateur avec privilèges administratifs complets
- **Club_Manager**: Utilisateur gérant les inscriptions pour un club
- **Impersonation_Mode**: Mode où un admin accède au système en tant qu'un manager de club spécifique
- **Temporary_Access_Grant**: Permission temporaire accordée par un admin à un manager pour contourner les restrictions de dates
- **Crew_Member**: Équipier (rameur ou barreur)
- **Boat_Registration**: Équipage (inscription d'un bateau avec ses équipiers)
- **Assigned_Crew_Member**: Équipier assigné à une position dans un équipage
- **Paid_Boat**: Équipage dont le paiement a été effectué
- **Permission_Matrix**: Matrice définissant toutes les permissions pour chaque action et phase
- **Registration_System**: Le système complet d'inscription de la Course des Impressionnistes

## Requirements

### Requirement 1: Event Phase Detection

**User Story:** En tant que système, je veux détecter automatiquement la phase actuelle de l'événement, afin d'appliquer les règles d'accès appropriées.

#### Acceptance Criteria

1. THE Access_Control_System SHALL determine the current Event_Phase by comparing the current date/time with the configured dates (registration_start_date, registration_end_date, payment_deadline)
2. THE Access_Control_System SHALL identify four distinct Event_Phases:
   - "before_registration": Current date is before registration_start_date
   - "during_registration": Current date is between registration_start_date and registration_end_date (inclusive)
   - "after_registration": Current date is after registration_end_date but before or equal to payment_deadline
   - "after_payment_deadline": Current date is after payment_deadline
3. WHEN the system configuration dates are updated, THE Access_Control_System SHALL immediately reflect the new Event_Phase without requiring system restart
4. THE Access_Control_System SHALL provide a function to query the current Event_Phase that can be called from both backend and frontend
5. THE Access_Control_System SHALL cache the Event_Phase calculation for a configurable duration (default: 60 seconds) to optimize performance

### Requirement 2: Permission Rules for Event Phases

**User Story:** As a club manager, I want my actions to be automatically restricted based on the event phase, so that I comply with the organization's rules.

#### Acceptance Criteria

1. WHILE Event_Phase is "before_registration", THE Access_Control_System SHALL prevent Club_Managers from creating crew members, boat registrations, or processing payments
2. WHILE Event_Phase is "before_registration", THE Access_Control_System SHALL allow Club_Managers to register accounts, view home page content, and read preliminary program and terms
3. WHILE Event_Phase is "during_registration", THE Access_Control_System SHALL allow Club_Managers to create, edit, and delete crew members and boat registrations
4. WHILE Event_Phase is "during_registration", THE Access_Control_System SHALL allow Club_Managers to process payments for boat registrations
5. WHILE Event_Phase is "after_registration", THE Access_Control_System SHALL prevent Club_Managers from creating new crew members or boat registrations
6. WHILE Event_Phase is "after_registration", THE Access_Control_System SHALL prevent Club_Managers from editing or deleting crew members
7. WHILE Event_Phase is "after_registration", THE Access_Control_System SHALL prevent Club_Managers from editing or deleting boat registrations
8. WHILE Event_Phase is "after_registration", THE Access_Control_System SHALL allow Club_Managers to process payments only
9. WHILE Event_Phase is "after_payment_deadline", THE Access_Control_System SHALL prevent Club_Managers from making any modifications
10. WHILE Event_Phase is "after_payment_deadline", THE Access_Control_System SHALL prevent Club_Managers from processing new payments
11. WHILE Event_Phase is "after_payment_deadline", THE Access_Control_System SHALL display a message instructing Club_Managers to contact the organization for any changes

### Requirement 3: Data State Restrictions

**User Story:** As a club manager, I want certain modifications to be automatically blocked based on data state, so that the integrity of registrations is protected.

#### Acceptance Criteria

1. WHEN a Crew_Member is assigned to a seat in a Boat_Registration, THE Access_Control_System SHALL prevent editing or deleting that Crew_Member
2. IF a Club_Manager wants to edit an Assigned_Crew_Member, THEN THE Access_Control_System SHALL require first unassigning the Crew_Member from the boat
3. WHEN a Boat_Registration has status "paid", THE Access_Control_System SHALL prevent any modifications to that boat registration
4. WHEN a Boat_Registration has status "paid", THE Access_Control_System SHALL prevent deletion of that boat registration
5. THE Access_Control_System SHALL allow viewing and exporting data for Paid_Boats without restrictions
6. THE Access_Control_System SHALL apply data state restrictions independently of Event_Phase restrictions (both must be satisfied)

### Requirement 4: Admin Impersonation Bypass

**User Story:** As an admin using impersonation, I want full access to all functions without any restrictions, so that I can efficiently help club managers fix any issues.

#### Acceptance Criteria

1. WHEN an Admin_User is in Impersonation_Mode, THE Access_Control_System SHALL bypass all Event_Phase restrictions
2. WHEN an Admin_User is in Impersonation_Mode, THE Access_Control_System SHALL bypass all data state restrictions (can modify paid boats, can edit assigned crew members)
3. WHEN an Admin_User is in Impersonation_Mode, THE Access_Control_System SHALL log all actions with a flag indicating impersonation was active
4. THE Access_Control_System SHALL detect Impersonation_Mode by checking for the presence of an impersonation token or header in the request
5. THE Access_Control_System SHALL apply full impersonation bypass rules consistently in both backend and frontend

### Requirement 5: Temporary Access Grants

**User Story:** As an admin, I want to temporarily grant a club manager the ability to modify their data outside the registration period, so that I can handle exceptional cases.

#### Acceptance Criteria

1. WHEN an Admin_User grants a Temporary_Access_Grant to a Club_Manager, THE Access_Control_System SHALL record the grant with the manager's user ID, grant timestamp, expiration timestamp, and granting admin ID
2. WHEN creating a Temporary_Access_Grant, THE Access_Control_System SHALL set the expiration time to a configurable number of hours from the grant time (default from system configuration: temporary_editing_access_hours)
3. WHILE a Club_Manager has an active Temporary_Access_Grant, THE Access_Control_System SHALL bypass Event_Phase restrictions for that manager
4. WHILE a Club_Manager has an active Temporary_Access_Grant, THE Access_Control_System SHALL still enforce data state restrictions (cannot modify paid boats, cannot edit assigned crew members without unassigning)
5. WHEN a Temporary_Access_Grant expires, THE Access_Control_System SHALL automatically revoke the grant and restore normal Event_Phase restrictions
6. WHEN an Admin_User manually revokes a Temporary_Access_Grant, THE Access_Control_System SHALL immediately restore normal Event_Phase restrictions for that manager
7. THE Access_Control_System SHALL provide an admin interface to view all active Temporary_Access_Grants with remaining time
8. THE Access_Control_System SHALL provide an admin interface to manually revoke any active Temporary_Access_Grant
9. THE Access_Control_System SHALL log all Temporary_Access_Grant creations, expirations, and revocations with timestamps and admin identification

### Requirement 6: Centralized Permission Matrix

**User Story:** As a developer, I want a centralized permission matrix, so that I can easily manage all access rules in one place.

#### Acceptance Criteria

1. THE Access_Control_System SHALL define a Permission_Matrix that maps each action to its permission rules
2. THE Permission_Matrix SHALL include the following actions:
   - create_crew_member
   - edit_crew_member
   - delete_crew_member
   - create_boat_registration
   - edit_boat_registration
   - delete_boat_registration
   - process_payment
   - view_data
   - export_data
3. FOR EACH action in the Permission_Matrix, THE Access_Control_System SHALL define rules based on:
   - Event_Phase (before_registration, during_registration, after_registration, after_payment_deadline)
   - User role (admin, club_manager)
   - Impersonation status (true/false)
   - Temporary access grant status (active/inactive)
   - Data state (crew_member_assigned, boat_paid)
4. THE Access_Control_System SHALL provide a function to check if an action is permitted given the current context (user, phase, data state)
5. THE Access_Control_System SHALL return a boolean result (permitted/denied) and an optional reason message when an action is denied
6. THE Permission_Matrix SHALL be defined in a single location in the codebase for easy maintenance
7. THE Permission_Matrix SHALL be accessible from both backend (Python) and frontend (JavaScript/Vue)

### Requirement 7: Backend Permission Enforcement

**User Story:** As a backend system, I want to validate all API requests against permissions, so that unauthorized actions are prevented.

#### Acceptance Criteria

1. WHEN a Club_Manager attempts any API operation, THE Access_Control_System SHALL check permissions before executing the operation
2. IF an action is not permitted, THEN THE Access_Control_System SHALL return an HTTP 403 Forbidden response with a clear error message explaining why the action was denied
3. THE Access_Control_System SHALL validate permissions for all crew member operations (create, update, delete)
4. THE Access_Control_System SHALL validate permissions for all boat registration operations (create, update, delete)
5. THE Access_Control_System SHALL validate permissions for payment operations
6. WHEN validating permissions, THE Access_Control_System SHALL consider the current Event_Phase, user role, impersonation status, temporary access grants, and data state
7. THE Access_Control_System SHALL log all permission denials with the attempted action, user ID, reason for denial, and timestamp
8. THE Access_Control_System SHALL provide consistent error messages between backend and frontend for the same permission denial

### Requirement 8: Frontend Permission Enforcement

**User Story:** As a frontend user, I want unauthorized buttons and functions to be disabled, so that I clearly understand what I can do.

#### Acceptance Criteria

1. WHEN the frontend loads, THE Access_Control_System SHALL evaluate all permissions for the current user and context
2. WHEN an action is not permitted, THE Access_Control_System SHALL disable the corresponding UI buttons and form fields
3. WHEN a button is disabled due to permissions, THE Access_Control_System SHALL display a tooltip or message explaining why the action is not available
4. THE Access_Control_System SHALL hide or disable "Create Crew Member" and "Create Boat Registration" buttons when Event_Phase is "before_registration", "after_registration", or "after_payment_deadline"
5. THE Access_Control_System SHALL disable "Edit" and "Delete" buttons for crew members when Event_Phase is "after_registration" or "after_payment_deadline"
6. THE Access_Control_System SHALL disable "Edit" and "Delete" buttons for boat registrations when Event_Phase is "after_registration" or "after_payment_deadline"
7. THE Access_Control_System SHALL disable "Edit" button for assigned crew members at all times (must unassign first)
8. THE Access_Control_System SHALL disable all modification buttons for paid boat registrations at all times
9. THE Access_Control_System SHALL disable "Pay" button when Event_Phase is "before_registration" or "after_payment_deadline"
10. WHEN an Admin_User is in Impersonation_Mode, THE Access_Control_System SHALL enable all buttons except those restricted by data state
11. WHEN a Club_Manager has an active Temporary_Access_Grant, THE Access_Control_System SHALL enable buttons that would normally be restricted by Event_Phase
12. THE Access_Control_System SHALL re-evaluate permissions when the Event_Phase changes or when temporary access grants are modified

### Requirement 9: Admin Permission Configuration Interface

**User Story:** As an admin, I want to configure permissions through an interface, so that I can adjust rules without modifying code.

#### Acceptance Criteria

1. WHEN an Admin_User accesses the permission configuration interface, THE Access_Control_System SHALL display the Permission_Matrix in an editable table format
2. THE permission configuration interface SHALL show all actions (rows) and all Event_Phases (columns)
3. FOR EACH action and Event_Phase combination, THE interface SHALL display a checkbox indicating if the action is permitted
4. WHEN an Admin_User modifies a permission checkbox, THE Access_Control_System SHALL update the Permission_Matrix in the system configuration
5. WHEN permission configuration is saved, THE Access_Control_System SHALL validate that the changes are consistent and do not create security vulnerabilities
6. THE Access_Control_System SHALL provide default permissions matching the rules defined in Requirement 2
7. WHEN an Admin_User resets permissions to defaults, THE Access_Control_System SHALL restore the original permission rules
8. THE Access_Control_System SHALL log all permission configuration changes with timestamps, previous values, new values, and admin identification
9. THE Access_Control_System SHALL apply permission configuration changes immediately without requiring system restart

### Requirement 10: Configuration Storage and Initialization

**User Story:** As a system, I want to store permission configuration in the database, so that dynamic modifications are possible.

#### Acceptance Criteria

1. THE Access_Control_System SHALL store the Permission_Matrix in DynamoDB with PK='CONFIG' and SK='PERMISSIONS'
2. WHEN the system is initialized, THE Access_Control_System SHALL create default permission configuration if none exists
3. THE init_config.py script SHALL include a function to initialize default permissions matching the rules in Requirement 2
4. THE Access_Control_System SHALL store Temporary_Access_Grants in DynamoDB with PK='TEMP_ACCESS' and SK='USER#{user_id}'
5. THE Access_Control_System SHALL include grant_timestamp, expiration_timestamp, granted_by_admin_id, and status fields for each Temporary_Access_Grant
6. THE Access_Control_System SHALL provide functions to query active Temporary_Access_Grants for a given user
7. THE Access_Control_System SHALL automatically clean up expired Temporary_Access_Grants (mark as expired) when they are queried

### Requirement 11: Permission Check API

**User Story:** As a developer, I want a simple API to check permissions, so that I can easily integrate access controls into the code.

#### Acceptance Criteria

1. THE Access_Control_System SHALL provide a backend function `check_permission(user_context, action, resource_context)` that returns a permission result
2. THE user_context parameter SHALL include user_id, role, is_impersonating, and temporary_access_grant_status
3. THE resource_context parameter SHALL include resource_type (crew_member, boat_registration), resource_state (assigned, paid), and any other relevant data
4. THE permission result SHALL include a boolean `is_permitted` field and an optional `denial_reason` message
5. THE Access_Control_System SHALL provide a frontend composable `usePermissions()` that exposes permission checking functions
6. THE frontend composable SHALL provide a `canPerformAction(action, resourceContext)` function that returns boolean
7. THE frontend composable SHALL provide a `getPermissionMessage(action, resourceContext)` function that returns a user-friendly message explaining why an action is denied
8. THE Access_Control_System SHALL cache permission checks for the duration of a request to optimize performance
9. THE Access_Control_System SHALL provide a function to invalidate permission cache when configuration changes

### Requirement 12: Audit Logging for Access Control

**User Story:** As an admin, I want to see a log of all access decisions, so that I can understand who did what and why certain actions were blocked.

#### Acceptance Criteria

1. WHEN a permission check denies an action, THE Access_Control_System SHALL log the denial with user_id, action, resource, reason, and timestamp
2. WHEN a permission check allows an action due to impersonation, THE Access_Control_System SHALL log the action with an impersonation flag
3. WHEN a permission check allows an action due to temporary access grant, THE Access_Control_System SHALL log the action with the grant ID
4. THE Access_Control_System SHALL provide an admin interface to view permission denial logs filtered by user, action, date range, and reason
5. THE Access_Control_System SHALL provide an admin interface to view all actions performed under impersonation
6. THE Access_Control_System SHALL provide an admin interface to view all actions performed under temporary access grants
7. THE Access_Control_System SHALL retain audit logs for a configurable period (default: 1 year)

---

## Appendix A: Permission Matrix Default Configuration

This appendix defines the default permission rules for each action and event phase.

### Matrix Structure

| Action | Before Registration | During Registration | After Registration | After Payment Deadline | Notes |
|--------|-------------------|-------------------|------------------|---------------------|-------|
| **Crew Member Operations** |
| create_crew_member | ❌ Denied | ✅ Allowed | ❌ Denied | ❌ Denied | Contact organization after registration |
| edit_crew_member | ❌ Denied | ✅ Allowed (if not assigned) | ❌ Denied | ❌ Denied | Must unassign first if assigned |
| delete_crew_member | ❌ Denied | ✅ Allowed (if not assigned) | ❌ Denied | ❌ Denied | Must unassign first if assigned |
| **Boat Registration Operations** |
| create_boat_registration | ❌ Denied | ✅ Allowed | ❌ Denied | ❌ Denied | Contact organization after registration |
| edit_boat_registration | ❌ Denied | ✅ Allowed (if not paid) | ❌ Denied | ❌ Denied | Cannot edit paid boats |
| delete_boat_registration | ❌ Denied | ✅ Allowed (if not paid) | ❌ Denied | ❌ Denied | Cannot delete paid boats |
| **Payment Operations** |
| process_payment | ❌ Denied | ✅ Allowed | ✅ Allowed | ❌ Denied | Payment only after registration closes |
| **Read Operations** |
| view_data | ✅ Allowed | ✅ Allowed | ✅ Allowed | ✅ Allowed | Always allowed |
| export_data | ✅ Allowed | ✅ Allowed | ✅ Allowed | ✅ Allowed | Always allowed |

### Special Rules

1. **Admin Impersonation**: When admin is impersonating, ALL restrictions are bypassed (both Event_Phase and data state restrictions)
2. **Temporary Access Grant**: When active, Event_Phase restrictions are bypassed for that specific user, but data state restrictions still apply
3. **Data State Restrictions** (apply only to non-impersonating users):
   - Cannot edit/delete assigned crew members (must unassign first)
   - Cannot edit/delete paid boat registrations

### Denial Messages

| Scenario | Message (French) | Message (English) |
|----------|-----------------|-------------------|
| Before registration | "Les inscriptions ne sont pas encore ouvertes. Ouverture le {date}." | "Registration is not yet open. Opens on {date}." |
| After registration closed | "La période d'inscription est terminée. Contactez l'organisation pour toute modification." | "Registration period has ended. Contact the organization for any changes." |
| After payment deadline | "La date limite de paiement est dépassée. Contactez l'organisation." | "Payment deadline has passed. Contact the organization." |
| Crew member assigned | "Impossible de modifier un équipier assigné. Désassignez-le d'abord de l'équipage." | "Cannot edit an assigned crew member. Unassign from boat first." |
| Boat paid | "Impossible de modifier un équipage payé. Contactez l'organisation." | "Cannot edit a paid boat registration. Contact the organization." |

---

## Appendix B: Database Schema for Access Control

### Permission Configuration

```
PK: CONFIG
SK: PERMISSIONS
{
  "permissions": {
    "create_crew_member": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": false,
      "after_payment_deadline": false
    },
    "edit_crew_member": {
      "before_registration": false,
      "during_registration": true,
      "after_registration": false,
      "after_payment_deadline": false,
      "requires_not_assigned": true
    },
    // ... other actions
  },
  "updated_at": "2026-01-14T10:00:00Z",
  "updated_by": "admin@example.com"
}
```

### Temporary Access Grant

```
PK: TEMP_ACCESS
SK: USER#{user_id}
{
  "user_id": "user-123",
  "grant_timestamp": "2026-01-14T10:00:00Z",
  "expiration_timestamp": "2026-01-16T10:00:00Z",
  "granted_by_admin_id": "admin-456",
  "status": "active",  // active, expired, revoked
  "revoked_at": null,
  "revoked_by_admin_id": null
}
```

### Permission Denial Log

```
PK: AUDIT#PERMISSION_DENIAL
SK: {timestamp}#{user_id}
{
  "user_id": "user-123",
  "action": "edit_crew_member",
  "resource_type": "crew_member",
  "resource_id": "crew-789",
  "denial_reason": "after_registration_closed",
  "event_phase": "after_registration",
  "timestamp": "2026-01-14T10:00:00Z"
}
```

---

## Appendix C: Implementation Notes

### Backend Implementation

1. Create `functions/shared/access_control.py` with:
   - `get_current_event_phase()` function
   - `check_permission(user_context, action, resource_context)` function
   - `Permission` class with permission checking logic
   - Integration with DynamoDB for permission configuration

2. Update all Lambda handlers to call `check_permission()` before executing operations

3. Return HTTP 403 with structured error message when permission denied

### Frontend Implementation

1. Create `frontend/src/composables/usePermissions.js` with:
   - `canPerformAction(action, resourceContext)` function
   - `getPermissionMessage(action, resourceContext)` function
   - `getCurrentEventPhase()` function
   - Reactive state for permissions

2. Update all components to use `usePermissions()` composable

3. Disable buttons and show tooltips based on permission checks

4. Display phase-specific messages to users

### Configuration Updates

1. Update `functions/init/init_config.py` to initialize default permissions

2. Add permission configuration UI in admin panel

3. Add temporary access grant management UI in admin panel
