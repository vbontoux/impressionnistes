# Requirements Document

## Introduction

This feature adds a selective database purge capability ("reset") for the Impressionnistes Registration System. It is exposed through the Database Reset section of the existing admin-only page "Gestion de la base" (Database_Management_Page). That page, its Backup/Restore section, the Backup_Service and the reserved reset area are delivered by the companion spec "database-backup-restore" (final, implemented and in production). This spec implements only the reset section and the small extensions it needs in the Backup_Service.

A purge lets an Admin prepare a new competition cycle by deleting, at several levels, the operational data of the previous one: everything, or any combination of purge sets (Équipages, Paiements, Équipiers, Team managers, Accès temporaires, Journaux d'audit). By default only "Équipages" is checked, and "Paiements" is checked and locked with it because of a dependency rule. A purge never touches the system configuration (`CONFIG`), the race definitions (`RACE`), the club definitions (`CLUB`) or the backup history (`AUDIT#DATABASE_BACKUP`).

Data inventory (production, by key):

| Purge set | Items deleted | Key | Production count |
|---|---|---|---|
| Équipages | Boat registrations (seats, paid status, boat number, boat rental request fields) | PK `TEAM#<sub>`, SK `BOAT#...` | 86 |
| Paiements | Stripe payment history | PK `TEAM#<sub>`, SK `PAYMENT#...` | 25 |
| Équipiers | Crew members | PK `TEAM#<sub>`, SK `CREW#...` | 372 |
| Team managers | Profiles and GDPR consents; `<sub>` is the Cognito sub | PK `USER#<sub>`, SK `PROFILE` and SK `CONSENT#...` | 34 and 66 |
| Accès temporaires | Temporary access grants | PK `TEMP_ACCESS`, SK `USER#<sub>` | 2 |
| Journaux d'audit | Permission audit logs and temporary-access audit logs | PK `AUDIT#PERMISSION_BYPASS`, `AUDIT#PERMISSION_DENIAL`, `AUDIT#PERMISSION_CONFIG`, `AUDIT#TEMP_ACCESS_GRANT`, `AUDIT#TEMP_ACCESS_REVOKE` | about 200 |

Never purged: `CONFIG` (SYSTEM, PRICING, PERMISSIONS, NOTIFICATION, RACE_TIMING), `RACE` (55), `CLUB` (414) and `AUDIT#DATABASE_BACKUP` (backup history).

The crew member key prefix is `CREW#`. The former reset script `delete_all_data_keep_team_managers.py` wrongly uses `CREW_MEMBER#`. No boat number counter exists: boat numbers (for example M.3.2) are computed from the existing boats of a race, so purging the boats restarts numbering with no further action.

The table is small (about 1250 items), so, as for backup and restore, a purge runs synchronously within a single Lambda invocation. A full backup (JSON_Backup and AWS_Native_Backup) is taken through the Backup_Service before any deletion, with its own Backup_Category `safety-pre-reset`. It is mandatory in production. The feature is admin-only, audited, and deployed to the development environment before production.

## Glossary

- **Reset_Service**: The backend component that validates a purge request, takes the Pre_Reset_Backup, deletes the selected Purge_Sets, deletes Cognito accounts when requested, and writes the Backup_Audit_Record. It is a route of the existing Backup_Service Lambda or a sibling Lambda, and it reuses `functions/shared/backup_service.py`.
- **Backup_Service**: The backend component defined by the "database-backup-restore" spec that creates, lists, downloads, deletes and restores backups. The Reset_Service reuses it to create the Pre_Reset_Backup.
- **Registration_Table**: The single DynamoDB table named `impressionnistes-registration-{env}`.
- **Purge_Set**: A selectable group of items deleted by a Purge_Operation. The six Purge_Sets are: "Équipages", "Paiements", "Équipiers", "Team managers", "Accès temporaires" and "Journaux d'audit".
- **Purge_Selection**: The set of Purge_Sets chosen for one Purge_Operation, including those added by the Dependency_Rules.
- **Purge_Operation**: The operation that deletes the items of every Purge_Set of a Purge_Selection from the Registration_Table, after the Pre_Reset_Backup when one is taken.
- **Équipages_Set**: The Purge_Set of boat registration items (PK `TEAM#<sub>`, SK `BOAT#...`).
- **Paiements_Set**: The Purge_Set of payment items (PK `TEAM#<sub>`, SK `PAYMENT#...`).
- **Équipiers_Set**: The Purge_Set of crew member items (PK `TEAM#<sub>`, SK `CREW#...`).
- **Team_Managers_Set**: The Purge_Set of team manager profile items (PK `USER#<sub>`, SK `PROFILE`) and GDPR consent items (PK `USER#<sub>`, SK `CONSENT#...`), where `<sub>` is the Cognito sub.
- **Temp_Access_Set**: The Purge_Set of temporary access grant items (PK `TEMP_ACCESS`, SK `USER#<sub>`), labeled "Accès temporaires".
- **Audit_Logs_Set**: The Purge_Set of items under PK `AUDIT#PERMISSION_BYPASS`, `AUDIT#PERMISSION_DENIAL`, `AUDIT#PERMISSION_CONFIG`, `AUDIT#TEMP_ACCESS_GRANT` and `AUDIT#TEMP_ACCESS_REVOKE`, labeled "Journaux d'audit".
- **Tout_Purger_Control**: The control labeled "Tout purger" that selects every Purge_Set.
- **Dependency_Rules**: The rules that add Purge_Sets to a Purge_Selection: Équipages_Set implies Paiements_Set; Équipiers_Set implies Équipages_Set and Paiements_Set; Team_Managers_Set implies Équipages_Set, Paiements_Set, Équipiers_Set and Temp_Access_Set.
- **Implied_Set**: A Purge_Set added to the Purge_Selection by a Dependency_Rule and not chosen directly by the Admin.
- **Cognito_Option**: The option labeled "Supprimer aussi les comptes de connexion (Cognito)", offered when the Team_Managers_Set is selected.
- **Cognito_Admins_Group**: The Cognito user pool group `admins`, whose members are the Admin users.
- **Protected_Data**: The items never deleted by a Purge_Operation: PK `CONFIG`, PK `RACE`, PK `CLUB` and PK `AUDIT#DATABASE_BACKUP`.
- **Pre_Reset_Backup**: A JSON_Backup and an AWS_Native_Backup of the full Registration_Table taken by the Backup_Service before any deletion, with Backup_Category `safety-pre-reset`.
- **Backup_Category**: The classifier of a JSON_Backup, as defined by the "database-backup-restore" spec (`manual`, `safety-pre-restore`). This spec adds the stable identifier `safety-pre-reset`.
- **Backup_Identifier**: The self-describing name of a JSON_Backup that embeds a Backup_Category marker and a UTC timestamp, as defined by the "database-backup-restore" spec.
- **JSON_Backup**: The application-level JSON export of every item of the Registration_Table, stored in the Backup_Bucket, as defined by the "database-backup-restore" spec.
- **AWS_Native_Backup**: A DynamoDB on-demand backup, as defined by the "database-backup-restore" spec.
- **Backup_Bucket**: The per-environment S3 bucket `rcpm-impressionnistes-backups-{env}` that stores JSON_Backups.
- **Backup_Audit_Record**: An audit item stored under PK `AUDIT#DATABASE_BACKUP`, as defined by the "database-backup-restore" spec. This spec adds the action `reset_database`.
- **Database_Management_Page**: The admin-only frontend page "Gestion de la base" defined by the "database-backup-restore" spec.
- **Database_Reset_Section**: The area of the Database_Management_Page that the "database-backup-restore" spec reserves for the reset, implemented by this spec.
- **State_Banner**: The banner of the Database_Reset_Section that shows the current state, the possible actions and the running action, following the UI state model of the "database-backup-restore" spec.
- **Reset_UI_State**: One of the six states of the Database_Reset_Section: `idle` (selection displayed), `busy` (purge running), `ready_to_purge` (Purge_Selection chosen, confirmation phrase entry), `success`, `error` (database not modified, or outcome unknown) and `partial` (deletion started, then failed).
- **Confirmation_Phrase**: The fixed text `PURGER LA BASE` that the Admin types exactly to authorize a Purge_Operation. It is distinct from the restore phrase.
- **Confirmation_Modal**: The BaseModal that summarizes what a Purge_Operation will delete and keep before execution.
- **Item_Count**: The number of items currently in the Registration_Table for a Purge_Set, computed by the Reset_Service.
- **Purge_Result**: The result of a Purge_Operation: deleted counts per Purge_Set, Cognito accounts deleted, and the Pre_Reset_Backup identifier.
- **Production_Environment**: The deployment whose `{env}` value is `prod`.
- **Admin**: An authenticated user who belongs to the Cognito_Admins_Group.
- **Fallback_Purge**: The command-line purge, run through an `infrastructure/Makefile` target, that applies the same Purge_Sets, Dependency_Rules, Protected_Data, Cognito_Option, Pre_Reset_Backup, Confirmation_Phrase and Backup_Audit_Record as the Database_Reset_Section. It is used when the Database_Management_Page is unavailable.
- **Dry_Run_Mode**: The mode of the Fallback_Purge that only reports the Item_Count of each Purge_Set and modifies nothing.
- **Admin_Deletion_Tool**: The command-line tool, run through the `infrastructure/Makefile` target `cognito-delete-admin`, that deletes the Cognito account of one Admin identified by an email address. It has no equivalent in the Database_Management_Page.
- **Admin_Profile_Items**: The items under PK `USER#<sub>` (SK `PROFILE` and SK `CONSENT#...`) of an Admin, where `<sub>` is the Cognito sub of that Admin.

## Requirements

### Requirement 1: Admin-Only Access

**User Story:** As an admin, I want the purge restricted to administrators, so that only authorized users can perform this destructive operation.

#### Acceptance Criteria

1. THE Reset_Service SHALL accept Item_Count requests and Purge_Operation requests only from an Admin.
2. IF a user who does not belong to the Cognito_Admins_Group sends an Item_Count request or a Purge_Operation request, THEN THE Reset_Service SHALL reject the request with an authorization error and SHALL NOT delete any item.
3. IF a user whose role is not `admin` navigates to the Database_Management_Page, THEN THE Database_Reset_Section SHALL NOT display purge controls.
4. WHEN an Admin navigates to the Database_Management_Page, THE Database_Reset_Section SHALL be displayed in the area reserved by the "database-backup-restore" spec.
5. THE Database_Reset_Section SHALL render its controls with the project design system components BaseButton, StatusBadge, FormGroup, MessageAlert, BaseModal and DataCard.

### Requirement 2: Purge Sets and Item Counts

**User Story:** As an admin, I want to choose which groups of data to purge and see how many items each contains, so that I know exactly what a purge removes.

#### Acceptance Criteria

1. THE Database_Reset_Section SHALL present one checkbox for each of the six Purge_Sets, labeled "Équipages", "Paiements", "Équipiers", "Team managers", "Accès temporaires" and "Journaux d'audit".
2. THE Database_Reset_Section SHALL list, for each Purge_Set, a description of the items that Purge_Set deletes.
3. WHEN the Database_Reset_Section is displayed, THE Reset_Service SHALL return the current Item_Count of each Purge_Set, and THE Database_Reset_Section SHALL display each Item_Count next to its Purge_Set before any Purge_Operation is executed.
4. THE Reset_Service SHALL compute the Item_Count of the Équipiers_Set from items whose SK starts with `CREW#`.
5. THE Reset_Service SHALL compute the Item_Count of the Audit_Logs_Set without counting items under PK `AUDIT#DATABASE_BACKUP`.
6. THE Database_Reset_Section SHALL present the Tout_Purger_Control.
7. WHEN an Admin activates the Tout_Purger_Control, THE Database_Reset_Section SHALL select every Purge_Set.
8. WHEN an Admin activates the Tout_Purger_Control, THE Database_Reset_Section SHALL leave the Cognito_Option unchecked.
9. IF retrieving the Item_Counts fails, THEN THE Database_Reset_Section SHALL display the error and SHALL keep the purge action disabled.

### Requirement 3: Default Selection

**User Story:** As an admin, I want the safest useful selection by default, so that a typical end-of-cycle purge needs no extra clicks and cannot remove more than intended.

#### Acceptance Criteria

1. WHEN the Database_Reset_Section is displayed, THE Database_Reset_Section SHALL show only the "Équipages" Purge_Set as chosen by the Admin.
2. WHEN the Database_Reset_Section is displayed, THE Database_Reset_Section SHALL show "Paiements" as checked and locked, because the Dependency_Rules add the Paiements_Set to "Équipages".
3. WHEN the Database_Reset_Section is displayed, THE Database_Reset_Section SHALL display a message stating that "Paiements" is checked automatically because deleting the boats without their payments would leave orphaned payments.
4. WHEN the Database_Reset_Section is displayed, THE Database_Reset_Section SHALL show the "Équipiers", "Team managers", "Accès temporaires" and "Journaux d'audit" Purge_Sets unchecked.
5. WHEN the Database_Reset_Section is displayed, THE Database_Reset_Section SHALL show the Cognito_Option as unavailable until the Team_Managers_Set is selected.

### Requirement 4: Dependency Rules

**User Story:** As an admin, I want dependent data purged together, so that the database never contains orphaned records.

#### Acceptance Criteria

1. WHEN an Admin selects the Équipages_Set, THE Database_Reset_Section SHALL add the Paiements_Set to the Purge_Selection.
2. WHEN an Admin selects the Équipiers_Set, THE Database_Reset_Section SHALL add the Équipages_Set and the Paiements_Set to the Purge_Selection.
3. WHEN an Admin selects the Team_Managers_Set, THE Database_Reset_Section SHALL add the Équipages_Set, the Paiements_Set, the Équipiers_Set and the Temp_Access_Set to the Purge_Selection.
4. WHILE a Purge_Set is an Implied_Set of a selected Purge_Set, THE Database_Reset_Section SHALL display that Purge_Set as checked and locked, so that the Admin cannot uncheck it.
5. WHEN an Admin unchecks a selected Purge_Set, THE Database_Reset_Section SHALL unlock every Purge_Set that is no longer an Implied_Set of another selected Purge_Set.
6. THE Database_Reset_Section SHALL display, next to each locked Purge_Set, the Purge_Set that requires it.
7. WHEN the Reset_Service receives a Purge_Operation request, THE Reset_Service SHALL verify that the Purge_Selection contains every Implied_Set required by the Dependency_Rules.
8. IF the Purge_Selection violates a Dependency_Rule, THEN THE Reset_Service SHALL reject the request with the error code `INVALID_SELECTION`, SHALL name the missing Purge_Sets, and SHALL NOT take a Pre_Reset_Backup or delete any item.
9. IF the Purge_Selection is empty or contains an unknown Purge_Set identifier, THEN THE Reset_Service SHALL reject the request with the error code `INVALID_SELECTION` and SHALL NOT take a Pre_Reset_Backup or delete any item.

### Requirement 5: Purge Scope and Protected Data

**User Story:** As an admin, I want a purge to delete exactly the selected sets and nothing else, so that configuration, races, clubs and the backup history are always kept.

#### Acceptance Criteria

1. WHEN a Purge_Operation executes, THE Reset_Service SHALL delete every item of each Purge_Set of the Purge_Selection, identified by the keys listed in the Introduction.
2. WHEN a Purge_Operation executes, THE Reset_Service SHALL NOT delete any item of a Purge_Set that is absent from the Purge_Selection.
3. WHEN a Purge_Operation executes, THE Reset_Service SHALL preserve every Protected_Data item.
4. WHEN a Purge_Operation completes, THE Registration_Table SHALL contain every Protected_Data item that existed before the Purge_Operation, unchanged.
5. THE Reset_Service SHALL NOT keep, create or update any boat number counter, because boat numbers are computed from the existing boats of a race.
6. WHEN the Équipages_Set is purged, THE Database_Reset_Section SHALL state in the Purge_Result that boat numbering restarts from the first number of each race.
7. THE Confirmation_Modal SHALL list the Protected_Data kept by the Purge_Operation: "Configuration", "Courses", "Clubs" and "Historique des sauvegardes".

### Requirement 6: Cognito Accounts

**User Story:** As an admin, I want to decide whether purged team managers lose their login accounts, so that I can either keep or fully remove them.

#### Acceptance Criteria

1. WHILE the Team_Managers_Set is selected, THE Database_Reset_Section SHALL display the Cognito_Option.
2. WHEN the Team_Managers_Set is selected, THE Database_Reset_Section SHALL leave the Cognito_Option unchecked.
3. WHILE the Team_Managers_Set is not selected, THE Database_Reset_Section SHALL hide the Cognito_Option and SHALL send the Cognito_Option as unchecked.
4. WHERE the Cognito_Option is displayed, THE Database_Reset_Section SHALL state that deleting Cognito accounts is irreversible, and that a backup restore does not restore Cognito accounts.
5. WHERE the Cognito_Option is displayed and unchecked, THE Database_Reset_Section SHALL warn that the accounts of the purged team managers can still log in but will have no profile.
6. WHERE the Cognito_Option is checked, THE Reset_Service SHALL delete the Cognito account of each team manager whose profile is purged, identified by the Cognito sub of the `USER#<sub>` key.
7. THE Reset_Service SHALL exclude every member of the Cognito_Admins_Group from Cognito account deletion.
8. THE Database_Reset_Section SHALL state that admin accounts are always excluded from Cognito account deletion.
9. WHERE the Cognito_Option is checked, THE Reset_Service SHALL delete the Cognito accounts after every DynamoDB deletion of the Purge_Selection has succeeded.
10. WHERE the Cognito_Option is checked and the deletion of a Cognito account fails, THE Reset_Service SHALL continue with the remaining accounts and SHALL report the number of Cognito accounts deleted and the identifiers of the accounts that failed.
11. WHERE the Cognito_Option is unchecked, THE Reset_Service SHALL NOT delete any Cognito account.
12. WHERE the Cognito_Option is checked, THE Confirmation_Modal SHALL display the number of Cognito accounts that will be deleted and SHALL state that this deletion is irreversible.
13. IF a request has the Cognito_Option checked and the Team_Managers_Set is absent from the Purge_Selection, THEN THE Reset_Service SHALL reject the request with the error code `INVALID_SELECTION` and SHALL NOT delete any item.

### Requirement 7: Audit

**User Story:** As an admin, I want every purge recorded and the backup history preserved, so that there is an accountable history of purges.

#### Acceptance Criteria

1. THE Reset_Service SHALL preserve every Backup_Audit_Record during a Purge_Operation, whatever the Purge_Selection.
2. WHEN a Purge_Operation completes, THE Reset_Service SHALL write a Backup_Audit_Record under PK `AUDIT#DATABASE_BACKUP` with the action `reset_database`.
3. THE Backup_Audit_Record of a Purge_Operation SHALL list the Purge_Sets of the Purge_Selection, including the Implied_Sets.
4. THE Backup_Audit_Record of a Purge_Operation SHALL record the number of items deleted for each Purge_Set.
5. THE Backup_Audit_Record of a Purge_Operation SHALL record the value of the Cognito_Option and the number of Cognito accounts deleted.
6. THE Backup_Audit_Record of a Purge_Operation SHALL record the Backup_Identifier of the Pre_Reset_Backup, or the fact that no Pre_Reset_Backup was taken.
7. THE Backup_Audit_Record of a Purge_Operation SHALL record the identity of the requesting Admin and the UTC timestamp.
8. IF a Purge_Operation fails after deletion has started, THEN THE Reset_Service SHALL write a Backup_Audit_Record with the action `reset_database` and the outcome `partial`, listing the deleted counts reached.
9. WHEN the Audit_Logs_Set is purged, THE Reset_Service SHALL write the Backup_Audit_Record of the Purge_Operation after the purge, so that the record is preserved.

### Requirement 8: Pre-Purge Backup

**User Story:** As an admin, I want a full backup taken before any deletion, so that I can undo a purge made by mistake.

#### Acceptance Criteria

1. WHEN a Purge_Operation is requested with the Pre_Reset_Backup enabled, THE Reset_Service SHALL create a Pre_Reset_Backup through the Backup_Service before deleting any item.
2. THE Pre_Reset_Backup SHALL consist of a JSON_Backup in the Backup_Bucket and an AWS_Native_Backup, and SHALL be successful only when both have completed.
3. WHEN the Reset_Service creates the Pre_Reset_Backup, THE Reset_Service SHALL set its Backup_Category to `safety-pre-reset`.
4. WHEN the Reset_Service creates the Pre_Reset_Backup, THE Reset_Service SHALL set its Backup_Identifier to carry the marker `safety-pre-reset` and a UTC timestamp, so that the Backup_Category is identifiable from the Backup_Identifier alone and is distinct from `manual` and `safety-pre-restore`.
5. THE Backup_Service SHALL list a `safety-pre-reset` JSON_Backup in the Backup/Restore section with a Backup_Category label distinct from the labels of `manual` and `safety-pre-restore`.
6. WHILE the environment is the Production_Environment, THE Database_Reset_Section SHALL display the pre-purge backup option checked and locked.
7. WHILE the environment is not the Production_Environment, THE Database_Reset_Section SHALL display the pre-purge backup option checked by default and SHALL allow the Admin to uncheck it.
8. IF a Purge_Operation request for the Production_Environment disables the Pre_Reset_Backup, THEN THE Reset_Service SHALL reject the request with the error code `BACKUP_REQUIRED` and SHALL NOT delete any item.
9. IF the Pre_Reset_Backup fails, THEN THE Reset_Service SHALL NOT delete any item, SHALL return an error naming the failed backup artifact, and SHALL report that the database was not modified.
10. WHEN a Purge_Operation completes successfully with a Pre_Reset_Backup, THE Database_Reset_Section SHALL present the Pre_Reset_Backup as the way to undo the purge, with an action that selects it in the Backup/Restore section for restoration.
11. WHEN a Purge_Operation completes successfully with Cognito accounts deleted, THE Database_Reset_Section SHALL state that the restore of the Pre_Reset_Backup does not restore the deleted Cognito accounts.
12. WHERE the pre-purge backup option is unchecked, THE Reset_Service SHALL perform the Purge_Operation without a Pre_Reset_Backup, and THE Database_Reset_Section SHALL state that the purge cannot be undone.

### Requirement 9: Confirmation Safeguards

**User Story:** As an admin, I want strong safeguards before a purge executes, so that I cannot purge data by accident.

#### Acceptance Criteria

1. THE Database_Reset_Section SHALL require the Admin to type the Confirmation_Phrase `PURGER LA BASE` exactly before a Purge_Operation can be initiated.
2. WHILE the typed text differs from the Confirmation_Phrase, THE Database_Reset_Section SHALL keep the purge action disabled.
3. WHILE the Purge_Selection is empty, THE Database_Reset_Section SHALL keep the purge action disabled.
4. WHEN an Admin initiates a Purge_Operation, THE Database_Reset_Section SHALL display the Confirmation_Modal before the request is sent.
5. THE Confirmation_Modal SHALL list each Purge_Set of the Purge_Selection with its Item_Count, marking each Implied_Set.
6. THE Confirmation_Modal SHALL display the value of the Cognito_Option and the pre-purge backup option.
7. THE Confirmation_Modal SHALL list what is kept by the Purge_Operation, including each Purge_Set absent from the Purge_Selection and the Protected_Data.
8. WHEN the Reset_Service receives a Purge_Operation request, THE Reset_Service SHALL compare the typed phrase with the Confirmation_Phrase, character for character.
9. IF the typed phrase differs from the Confirmation_Phrase, THEN THE Reset_Service SHALL reject the request with the error code `INVALID_CONFIRMATION` and SHALL NOT take a Pre_Reset_Backup or delete any item.
10. THE Reset_Service SHALL reject the restore phrase as a Confirmation_Phrase.

### Requirement 10: Execution and UI States

**User Story:** As an admin, I want a clear indication of what the page is doing, so that I do not start conflicting actions.

#### Acceptance Criteria

1. WHEN the Reset_Service receives a valid Purge_Operation request, THE Reset_Service SHALL complete the operation within a single invocation and return the Purge_Result without requiring the client to poll.
2. THE State_Banner SHALL display the current Reset_UI_State, the possible actions and the running action.
3. WHILE a Purge_Operation is in progress, THE Database_Management_Page SHALL display the Reset_UI_State `busy` with a status message naming the operation in progress and SHALL disable every other action of the page, including the Backup/Restore section.
4. WHILE a backup, download, delete or restore of the Backup/Restore section is in progress, THE Database_Reset_Section SHALL disable the purge action.
5. WHEN the Admin has chosen a Purge_Selection, THE Database_Reset_Section SHALL enter the Reset_UI_State `ready_to_purge` and SHALL enable the purge action only while the typed text equals the Confirmation_Phrase.
6. WHEN a Purge_Operation fails before any deletion, THE Database_Reset_Section SHALL enter the Reset_UI_State `error` and SHALL state "Rien n'a été modifié dans la base".
7. IF the Database_Reset_Section receives no response to a Purge_Operation request, such as a network error or a gateway timeout, THEN THE Database_Reset_Section SHALL enter the Reset_UI_State `error` with a message stating that the outcome is unknown and instructing the Admin to refresh the backup list, check whether a new `safety-pre-reset` backup exists, and verify the state of the database before taking further action.
8. WHEN the Admin loads or refreshes the Database_Reset_Section, THE Database_Reset_Section SHALL display the default selection defined in Requirement 3 with an empty confirmation phrase.

### Requirement 11: Result Reporting

**User Story:** As an admin, I want a precise report after a purge, so that I know what was deleted and what to do next.

#### Acceptance Criteria

1. WHEN a Purge_Operation completes successfully, THE Database_Reset_Section SHALL enter the Reset_UI_State `success` and SHALL display the Purge_Result.
2. THE Purge_Result SHALL report the number of items deleted for each Purge_Set of the Purge_Selection.
3. THE Purge_Result SHALL report the number of Cognito accounts deleted, and the number of Cognito accounts that failed, when the Cognito_Option is checked.
4. THE Purge_Result SHALL report the Backup_Identifier of the Pre_Reset_Backup, when one was taken.
5. WHEN a Purge_Operation completes successfully, THE Database_Reset_Section SHALL display a reminder to update, in the event configuration, the registration dates, the payment deadline and the competition date for the next edition.
6. THE Database_Reset_Section SHALL NOT change any event configuration value automatically.
7. WHEN a Purge_Operation completes successfully, THE Database_Reset_Section SHALL refresh the Item_Counts of the Purge_Sets.

### Requirement 12: Error Handling and Partial Failure

**User Story:** As an admin, I want clear errors and a recovery path when a purge fails midway, so that I can restore the database.

#### Acceptance Criteria

1. IF the deletion of an item fails after deletion has started, THEN THE Reset_Service SHALL stop the Purge_Operation and SHALL return the error code `RESET_PARTIAL`.
2. THE `RESET_PARTIAL` result SHALL report the number of items deleted for each Purge_Set at the time of the failure, the Purge_Set being deleted, and the Backup_Identifier of the Pre_Reset_Backup when one was taken.
3. WHEN the Database_Reset_Section receives `RESET_PARTIAL`, THE Database_Reset_Section SHALL enter the Reset_UI_State `partial`, display the banner "ÉTAT PARTIEL : la purge n'est pas terminée", and display the per-Purge_Set counts and the Backup_Identifier of the Pre_Reset_Backup.
4. WHEN the Database_Reset_Section enters the Reset_UI_State `partial` and a Pre_Reset_Backup exists, THE Database_Reset_Section SHALL offer an action that selects the Pre_Reset_Backup for restoration, and an action to retry the purge.
5. IF `RESET_PARTIAL` occurs and no Pre_Reset_Backup was taken, THEN THE Database_Reset_Section SHALL state that the database cannot be restored from a pre-purge backup.
6. WHEN the Reset_Service rejects a request with `INVALID_SELECTION`, `INVALID_CONFIRMATION` or `BACKUP_REQUIRED`, THE Database_Reset_Section SHALL enter the Reset_UI_State `error` and display the translated message of the error code.
7. IF an unexpected error occurs before deletion has started, THEN THE Reset_Service SHALL return an error that does not include a stack trace and SHALL report that the database was not modified.
8. WHEN a Purge_Operation returns an error, THE Database_Reset_Section SHALL display the error with the MessageAlert component.

### Requirement 13: Environments and Rollout

**User Story:** As an operator, I want the purge deployed and verified in development before production, so that I can validate it safely.

#### Acceptance Criteria

1. THE Reset_Service SHALL operate on the Registration_Table, the Backup_Bucket and the Cognito user pool of the environment in which it is deployed.
2. WHERE the feature is deployed to the development environment, THE Reset_Service SHALL support every Purge_Set, the Cognito_Option and the Pre_Reset_Backup so that each can be verified before the production deployment.
3. WHEN the Reset_Service reads the environment name to apply the production rules, THE Reset_Service SHALL take the value from its deployment configuration and SHALL NOT take it from the request.
4. THE Reset_Service SHALL use the Admin check of the Backup_Service (Cognito_Admins_Group), with no permission matrix entry.

### Requirement 14: Fallback Command-Line Purge

**User Story:** As an operator, I want command-line fallback purge tools that apply the same rules as the Database_Reset_Section, so that I can purge the database when the admin page is unavailable without risking data that the page protects.

#### Acceptance Criteria

1. THE project SHALL keep a Fallback_Purge, run only through a target of `infrastructure/Makefile`, and SHALL NOT retire the script `delete_all_data_keep_team_managers.py` without a Fallback_Purge of the same purpose.
2. THE Fallback_Purge SHALL offer the same six Purge_Sets, the same default selection (Équipages_Set with the Paiements_Set implied), the same Dependency_Rules and the same Protected_Data (`CONFIG`, `RACE`, `CLUB`, `AUDIT#DATABASE_BACKUP`) as the Database_Reset_Section.
3. THE Fallback_Purge SHALL offer the Cognito_Option, unchecked by default, with the same exclusion of every member of the Cognito_Admins_Group as the Reset_Service.
4. THE Fallback_Purge SHALL take the definition of the Purge_Sets, the Dependency_Rules and the Protected_Data from the same source as the Reset_Service, without duplicating key patterns.
5. WHEN the Fallback_Purge starts a Purge_Operation, THE Fallback_Purge SHALL create a Pre_Reset_Backup with Backup_Category `safety-pre-reset` through the Backup_Service before deleting any item.
6. WHILE the environment is the Production_Environment, THE Fallback_Purge SHALL refuse to run without the Pre_Reset_Backup.
7. IF the Pre_Reset_Backup fails, THEN THE Fallback_Purge SHALL NOT delete any item and SHALL report that the database was not modified.
8. THE Fallback_Purge SHALL display the Item_Count of each Purge_Set of the Purge_Selection before deleting.
9. THE Fallback_Purge SHALL require the Confirmation_Phrase `PURGER LA BASE`, typed exactly, before deleting any item.
10. IF the typed text differs from the Confirmation_Phrase, THEN THE Fallback_Purge SHALL NOT take a Pre_Reset_Backup or delete any item.
11. WHERE the Dry_Run_Mode is requested, THE Fallback_Purge SHALL report the Item_Count of each Purge_Set and SHALL NOT take a Pre_Reset_Backup, delete any item, delete any Cognito account or write a Backup_Audit_Record.
12. WHEN a Purge_Operation of the Fallback_Purge completes, THE Fallback_Purge SHALL write the same `reset_database` Backup_Audit_Record as the Reset_Service, including the outcome `partial` after a failure that occurs once deletion has started.
13. THE script `delete_all_data_keep_team_managers.py` SHALL be corrected, or replaced by the Fallback_Purge with the same purpose, so that the purge uses the `CREW#` crew member prefix.
14. THE corrected script SHALL preserve every item under PK `AUDIT#DATABASE_BACKUP`.
15. THE corrected script SHALL NOT write a `boat_number_counter` field into `CONFIG#SYSTEM`.
16. THE corrected script SHALL be reachable through an `infrastructure/Makefile` target whose name matches the usage documented in the script and in `scripts/database/README.md`.
17. THE `db-reset` Makefile target SHALL keep its purpose of reinitializing the database to defaults, distinct from the edition purge of the Database_Reset_Section.
18. WHEN the `db-reset` Makefile target is run, THE `db-reset` target SHALL create a Pre_Reset_Backup before deleting any item.
19. WHEN the `db-reset` Makefile target is run, THE `db-reset` target SHALL require the Confirmation_Phrase `PURGER LA BASE`, typed exactly, before deleting any item.
20. WHEN the `db-reset` Makefile target completes, THE `db-reset` target SHALL report the number of races actually present in the Registration_Table.
21. THE script `delete_team_manager.py` SHALL NOT delete a Cognito account that belongs to the Cognito_Admins_Group.

### Requirement 15: Admin Account Deletion Script

**User Story:** As an operator, I want a command-line tool to delete an admin account, so that admin accounts can be removed safely without the AWS console.

#### Acceptance Criteria

1. THE project SHALL provide the Admin_Deletion_Tool through the `infrastructure/Makefile` target `cognito-delete-admin`, which takes the parameters `EMAIL` and `ENV`.
2. THE Database_Management_Page SHALL NOT offer any action that deletes an Admin account.
3. IF the Cognito account identified by `EMAIL` does not exist, THEN THE Admin_Deletion_Tool SHALL report that the account does not exist and SHALL NOT modify the Cognito user pool, the Registration_Table or the Backup_Audit_Record history.
4. IF the Cognito account identified by `EMAIL` is not a member of the Cognito_Admins_Group, THEN THE Admin_Deletion_Tool SHALL refuse the deletion, SHALL state that team managers are deleted with the `delete-team-manager` Makefile target, and SHALL NOT modify the Cognito user pool or the Registration_Table.
5. IF the Cognito account identified by `EMAIL` is the last remaining member of the Cognito_Admins_Group, THEN THE Admin_Deletion_Tool SHALL refuse the deletion, SHALL state that the deletion would leave no Admin able to log in, and SHALL NOT modify the Cognito user pool or the Registration_Table.
6. WHEN the Admin_Deletion_Tool accepts the account for deletion, THE Admin_Deletion_Tool SHALL display the email address of the account, the groups of the account and the target environment before deleting.
7. THE Admin_Deletion_Tool SHALL require the operator to type the email address of the account exactly before deleting.
8. IF the typed text differs from the email address of the account, THEN THE Admin_Deletion_Tool SHALL NOT take a backup or delete anything.
9. WHERE the environment is the Production_Environment, THE `cognito-delete-admin` Makefile target SHALL require the production confirmation used by the other production targets of `infrastructure/Makefile`, in addition to the typed email address.
10. WHEN the operator confirms the deletion and the option `WITH_PROFILE=1` is not given, THE Admin_Deletion_Tool SHALL delete only the Cognito account and SHALL leave the Admin_Profile_Items of that Admin unchanged.
11. WHERE the option `WITH_PROFILE=1` is given, THE Admin_Deletion_Tool SHALL create a Pre_Reset_Backup (JSON_Backup and AWS_Native_Backup) through the Backup_Service before deleting the Admin_Profile_Items.
12. WHERE the option `WITH_PROFILE=1` is given, IF the Pre_Reset_Backup fails, THEN THE Admin_Deletion_Tool SHALL abort without deleting the Cognito account or any item, and SHALL report that nothing was modified.
13. WHERE the option `WITH_PROFILE=1` is given and the Pre_Reset_Backup succeeds, THE Admin_Deletion_Tool SHALL delete the Admin_Profile_Items of the account and SHALL then delete the Cognito account.
14. WHEN the Admin_Deletion_Tool deletes a Cognito account, THE Admin_Deletion_Tool SHALL write a Backup_Audit_Record with the action `delete_admin`.
15. THE Backup_Audit_Record of the Admin_Deletion_Tool SHALL record the Cognito sub and the email address of the deleted account, the environment given by the operator, whether the Admin_Profile_Items were deleted, and the Backup_Identifier of the Pre_Reset_Backup when one was taken.
16. WHEN the Admin_Deletion_Tool completes, THE Admin_Deletion_Tool SHALL report the Cognito account deleted, the number of Admin_Profile_Items deleted, and the Backup_Identifier of the Pre_Reset_Backup when one was taken.
