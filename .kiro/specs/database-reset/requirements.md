# Requirements Document

## Introduction

This feature adds a database reset capability for the Impressionnistes Registration System, exposed through the Database Reset section of the existing admin-only page "Gestion de la base" (Database Management). The Database Management page and its Backup/Restore section are defined by the companion spec "database-backup-restore", which reserves a distinct area on that page for this Database Reset section; this spec implements only the Database Reset section.

A reset purges the operational business data of a competition cycle so that a fresh registration period can begin, while preserving the system configuration, race definitions, and club definitions. By default a reset also preserves team manager accounts, and the Admin must explicitly opt in to delete them. A reset is the web/admin equivalent of the existing command-line script `delete_all_data_keep_team_managers.py`.

This feature depends on the backup capability delivered by the "database-backup-restore" spec. By default, every reset first creates a full backup using that same backup mechanism (an application-level JSON export written to the per-environment S3 backup bucket together with an AWS native DynamoDB on-demand backup) before any deletion occurs. If that pre-reset backup fails, the reset aborts without deleting anything.

The system stores all data in a single DynamoDB table (single-table design, PK/SK with GSI1/GSI2/GSI3) following the name pattern `impressionnistes-registration-{env}`. The production table is small (approximately 1250 items), so the reset is performed synchronously within a single Lambda invocation; no asynchronous job tracking or polling is required. The reset action is admin-only, is audited, and must be deployable and verifiable in the development environment before production.

## Glossary

- **Reset_Service**: The backend Lambda component that performs a database reset, orchestrating the optional pre-reset backup, the deletion of operational data, and the counter reset.
- **Reset_Operation**: The operation that purges operational business data from the Registration_Table according to the chosen options and resets the boat number counter.
- **Registration_Table**: The single DynamoDB table named `impressionnistes-registration-{env}`.
- **Operational_Data**: The set of items purged by a Reset_Operation, consisting of boat registration items (`TEAM#...#BOAT#...`), crew member items (`TEAM#...#CREW_MEMBER#...`), payment items (`TEAM#...#PAYMENT#...`), temporary access grant items (`TEMP_ACCESS#`), and audit log items (`AUDIT#`).
- **Preserved_Data**: The set of items never purged by a Reset_Operation, consisting of system configuration items (`CONFIG`), race definition items (`RACE`), and club definition items (`CLUB`).
- **Team_Manager**: A user account stored as a `USER#` item whose role is team manager.
- **System_Config_Item**: The configuration item stored under `CONFIG#SYSTEM` that contains the `boat_number_counter` attribute.
- **Boat_Number_Counter**: The `boat_number_counter` attribute of the System_Config_Item.
- **Pre_Reset_Backup**: A full backup of the current Registration_Table state, consisting of a JSON_Backup and an AWS_Native_Backup, created by the Backup_Service before any deletion in a Reset_Operation. The Pre_Reset_Backup has its own Backup_Category, `safety-pre-reset`, distinct from `manual` and `safety-pre-restore` defined by the "database-backup-restore" spec.
- **Backup_Category**: The classifier of a JSON_Backup, as defined by the "database-backup-restore" spec. Category values are stable identifiers. This spec adds the category `safety-pre-reset` to the categories `manual` and `safety-pre-restore`; this category is added to the backup naming when this spec is implemented.
- **Backup_Identifier**: The human-readable, self-describing name or key of a JSON_Backup that embeds an explicit Backup_Category marker and a UTC timestamp, as defined by the "database-backup-restore" spec.
- **Backup_Service**: The backend backup component defined by the "database-backup-restore" spec, reused by the Reset_Service to create the Pre_Reset_Backup.
- **JSON_Backup**: An application-level export file containing every item of the Registration_Table serialized as JSON, as defined by the "database-backup-restore" spec.
- **AWS_Native_Backup**: A DynamoDB on-demand backup, as defined by the "database-backup-restore" spec.
- **Database_Management_Page**: The admin-only frontend page "Gestion de la base" defined by the "database-backup-restore" spec, containing a Backup/Restore section and the Database Reset section implemented by this spec.
- **Database_Reset_Section**: The area of the Database_Management_Page that presents the reset controls and results.
- **Admin**: An authenticated user whose role is `admin`.
- **Audit_Record**: An `AUDIT#` item recording an administrative action, who performed it, and when.
- **Confirmation_Phrase**: A fixed text string the Admin must type exactly to authorize a Reset_Operation.
- **Reset_Result**: The result returned by the Reset_Service after a Reset_Operation, reporting the counts of deleted items by type, whether a Pre_Reset_Backup was taken, and the Pre_Reset_Backup identifier when taken.

## Requirements

### Requirement 1: Database Reset Section Access

**User Story:** As an admin, I want a Database Reset section on the Database Management page, so that I can reset the system data from one place.

#### Acceptance Criteria

1. WHEN an Admin navigates to the Database_Management_Page, THE Database_Reset_Section SHALL be displayed within the area reserved for database reset.
2. IF a user whose role is not `admin` attempts to access the Database_Reset_Section, THEN THE Database_Reset_Section SHALL deny access and SHALL NOT display reset controls.
3. THE Database_Reset_Section SHALL render its controls using the project design system components, including BaseButton, StatusBadge, FormGroup, MessageAlert, BaseModal, DataCard, and SortableTable where applicable.

### Requirement 2: Admin-Only Access

**User Story:** As an admin, I want the reset action restricted to administrators, so that only authorized users can perform this destructive operation.

#### Acceptance Criteria

1. THE Reset_Service SHALL accept Reset_Operation requests only from an Admin.
2. IF a Reset_Operation request is made by a user who is not an Admin, THEN THE Reset_Service SHALL reject the request with an authorization error and SHALL NOT perform the Reset_Operation.

### Requirement 3: Purge Operational Data

**User Story:** As an admin, I want a reset to remove all boat registrations, crew members, payments, temporary access grants, and audit logs, so that the database is cleared of the previous cycle's operational data.

#### Acceptance Criteria

1. WHEN a Reset_Operation executes, THE Reset_Service SHALL delete every boat registration item identified by the `TEAM#...#BOAT#...` key pattern.
2. WHEN a Reset_Operation executes, THE Reset_Service SHALL delete every crew member item identified by the `TEAM#...#CREW_MEMBER#...` key pattern.
3. WHEN a Reset_Operation executes, THE Reset_Service SHALL delete every payment item identified by the `TEAM#...#PAYMENT#...` key pattern.
4. WHEN a Reset_Operation executes, THE Reset_Service SHALL delete every temporary access grant item identified by the `TEMP_ACCESS#` key pattern.
5. WHEN a Reset_Operation executes, THE Reset_Service SHALL delete every audit log item identified by the `AUDIT#` key pattern.

### Requirement 4: Preserve Configuration, Races, and Clubs

**User Story:** As an admin, I want a reset to keep the system configuration, race definitions, and club definitions, so that the system remains configured and ready for a new cycle.

#### Acceptance Criteria

1. WHEN a Reset_Operation executes, THE Reset_Service SHALL preserve every system configuration item identified by the `CONFIG` key pattern.
2. WHEN a Reset_Operation executes, THE Reset_Service SHALL preserve every race definition item identified by the `RACE` key pattern.
3. WHEN a Reset_Operation executes, THE Reset_Service SHALL preserve every club definition item identified by the `CLUB` key pattern.

### Requirement 5: Preserve Team Managers by Default

**User Story:** As an admin, I want team managers kept by default, so that I do not accidentally remove their accounts when resetting operational data.

#### Acceptance Criteria

1. THE Database_Reset_Section SHALL present a "delete team managers" option that is deselected by default.
2. WHILE the "delete team managers" option is deselected, THE Reset_Service SHALL preserve every Team_Manager item identified by the `USER#` key pattern during a Reset_Operation.
3. WHERE the "delete team managers" option is deselected and a Reset_Operation completes, THE preserved Team_Manager accounts SHALL remain able to log in.

### Requirement 6: Optionally Delete Team Managers

**User Story:** As an admin, I want the ability to also delete team managers, so that I can fully clear accounts when a cycle requires it.

#### Acceptance Criteria

1. WHERE the "delete team managers" option is selected, THE Reset_Service SHALL delete every Team_Manager item identified by the `USER#` key pattern during a Reset_Operation.
2. WHERE the "delete team managers" option is selected, THE Reset_Service SHALL preserve every non-user Preserved_Data item during the Reset_Operation.
3. WHERE the "delete team managers" option is selected, THE Database_Reset_Section SHALL present the effect of also deleting team manager accounts to the Admin before the Reset_Operation is initiated.
4. WHERE the "delete team managers" option is selected and Team_Manager items are deleted from the Registration_Table, THE Reset_Service SHALL report whether the corresponding Cognito authentication accounts are affected by the Reset_Operation.

### Requirement 7: Reset Boat Number Counter

**User Story:** As an admin, I want the boat number counter reset to zero after a reset, so that new registrations start numbering from the beginning.

#### Acceptance Criteria

1. WHEN a Reset_Operation completes the deletion of Operational_Data, THE Reset_Service SHALL set the Boat_Number_Counter of the System_Config_Item to 0.
2. THE Reset_Service SHALL preserve the System_Config_Item while setting the Boat_Number_Counter to 0.

### Requirement 8: Mandatory-by-Default Pre-Reset Backup

**User Story:** As an admin, I want a backup created before any deletion by default, so that I can recover if the reset was a mistake.

#### Acceptance Criteria

1. WHEN the Database_Reset_Section is displayed, THE Database_Reset_Section SHALL present a "create a backup before reset" option in a selected (enabled) state.
2. WHERE the "create a backup before reset" option is selected, THE Reset_Service SHALL create a complete Pre_Reset_Backup using the Backup_Service and SHALL confirm the Pre_Reset_Backup has completed successfully before deleting any item from the Registration_Table.
3. WHERE the "create a backup before reset" option is selected, THE Pre_Reset_Backup SHALL consist of both a JSON_Backup written to the per-environment backup bucket and an AWS_Native_Backup of the Registration_Table, and SHALL be considered successful only when both components have completed successfully.
4. IF the "create a backup before reset" option is selected and either component of the Pre_Reset_Backup fails to complete successfully, THEN THE Reset_Service SHALL abort the Reset_Operation, SHALL NOT delete any item from the Registration_Table, SHALL leave the Registration_Table unchanged, and SHALL return an error response indicating which backup component failed.
5. WHERE the "create a backup before reset" option is deselected, THE Reset_Service SHALL perform the Reset_Operation without creating a Pre_Reset_Backup.
6. WHEN the Reset_Service creates a Pre_Reset_Backup, THE Reset_Service SHALL set the Backup_Category of the Pre_Reset_Backup to `safety-pre-reset`, so that the Pre_Reset_Backup is distinguishable from a `manual` backup and from a `safety-pre-restore` backup when an Admin chooses a restore source.
7. WHEN the Reset_Service creates a Pre_Reset_Backup, THE Reset_Service SHALL set the Backup_Identifier of the Pre_Reset_Backup to carry the `safety-pre-reset` marker and a UTC timestamp, so that the Backup_Category is identifiable from the Backup_Identifier alone and does not rely on the timestamp alone.
8. WHEN a reset completes successfully and a Pre_Reset_Backup was taken, THE Database_Reset_Section SHALL present that Pre_Reset_Backup as the way to undo the reset and SHALL point the Admin to the restore action of the Backup/Restore section.

### Requirement 9: Confirmation Safeguards

**User Story:** As an admin, I want strong safeguards before a reset executes, so that I cannot accidentally purge the database.

#### Acceptance Criteria

1. WHEN an Admin initiates a Reset_Operation, THE Database_Reset_Section SHALL require the Admin to confirm the reset.
2. THE Database_Reset_Section SHALL require the Admin to type the Confirmation_Phrase exactly before a Reset_Operation can be executed.
3. WHILE the typed text does not match the Confirmation_Phrase, THE Database_Reset_Section SHALL keep the reset action disabled.
4. THE Database_Reset_Section SHALL leave the "delete team managers" option deselected by default and the "create a backup before reset" option selected by default.
5. IF a Reset_Operation request is received without a typed Confirmation_Phrase that matches exactly, THEN THE Reset_Service SHALL reject the request and SHALL NOT delete any item.

### Requirement 10: Synchronous Execution and Result Reporting

**User Story:** As an admin, I want the reset to run in one step and report what happened, so that I know exactly what was deleted and backed up.

#### Acceptance Criteria

1. WHEN a Reset_Operation request is received, THE Reset_Service SHALL complete the operation synchronously within a single invocation and return a Reset_Result without requiring the client to poll for status.
2. WHEN a Reset_Operation completes successfully, THE Reset_Result SHALL report the count of deleted items for each purged key pattern.
3. WHEN a Reset_Operation completes successfully, THE Reset_Result SHALL report whether a Pre_Reset_Backup was taken and, where a Pre_Reset_Backup was taken, the identifier of the Pre_Reset_Backup.
4. WHILE a Reset_Operation is in progress, THE Database_Management_Page SHALL display a loading state and a status message naming the operation in progress, and SHALL disable every other action.
5. WHEN a Reset_Operation returns, THE Database_Reset_Section SHALL display the success Reset_Result or the error result.

### Requirement 11: Audit Logging

**User Story:** As an admin, I want each reset recorded, so that there is an accountable history of resets.

#### Acceptance Criteria

1. WHEN a Reset_Operation completes, THE Reset_Service SHALL write an Audit_Record capturing the reset action, the requesting Admin identity, and the timestamp.
2. WHEN a Reset_Operation completes, THE Audit_Record SHALL record whether the "delete team managers" option was selected.
3. WHEN a Reset_Operation completes, THE Audit_Record SHALL record whether a Pre_Reset_Backup was taken and, where a Pre_Reset_Backup was taken, the identifier of the Pre_Reset_Backup.
4. WHEN a Reset_Operation completes, THE Audit_Record SHALL record the count of deleted items for each purged key pattern.

### Requirement 12: Error Handling

**User Story:** As an admin, I want clear messages when a reset cannot complete, so that I understand the outcome and the state of the data.

#### Acceptance Criteria

1. IF the Reset_Service cannot delete one or more Operational_Data items after deletion has begun, THEN THE Reset_Service SHALL return an error that describes the failure and SHALL report that the Reset_Operation did not fully complete.
2. WHEN a Reset_Operation fails after a Pre_Reset_Backup was taken, THE Reset_Service SHALL include the identifier of the Pre_Reset_Backup in the error result.
3. WHEN a Reset_Operation returns an error, THE Database_Reset_Section SHALL display the error using the project design system messaging components.
4. IF the Database_Reset_Section receives no response to a Reset_Operation request (for example a network error or gateway timeout), THEN THE Database_Reset_Section SHALL display a message stating that the outcome is unknown and instructing the Admin to refresh and verify the state of the database before taking further action.

### Requirement 13: Environment Deployment and Testing

**User Story:** As an operator, I want the reset feature deployable and verifiable in development before production, so that I can validate reset behavior safely.

#### Acceptance Criteria

1. THE Reset_Service SHALL operate against the Registration_Table of the environment in which it is deployed.
2. WHERE the feature is deployed to the development environment, THE Reset_Service SHALL support performing a Reset_Operation so that it can be verified before production deployment.
3. THE Reset_Service SHALL create the Pre_Reset_Backup in the backup bucket of the environment in which it is deployed.
