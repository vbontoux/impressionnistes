# Requirements Document

## Introduction

This feature adds a database backup and restore capability for the Impressionnistes Registration System, exposed through a new admin-only page "Gestion de la base" (Database Management) reachable from the Admin menu. This spec covers only the Backup/Restore section of that page; a separate spec ("database-reset") will later add a Database Reset section to the same page, so the page scaffold must accommodate both sections while this spec implements only Backup/Restore.

The system stores all data in a single DynamoDB table (single-table design, PK/SK with GSI1/GSI2/GSI3) following the name pattern `impressionnistes-registration-{env}`. The production table is small (approximately 1250 items, approximately 630 KB), so all backup and restore operations are performed synchronously within a single Lambda invocation; no asynchronous job tracking or polling is required.

Creating a backup produces two artifacts: an application-level JSON export written to a new dedicated per-environment S3 backup bucket, and an AWS native DynamoDB on-demand backup. AWS_Native_Backup artifacts are created with every backup but are not listed in the Database_Management_Page; they remain visible through the existing `make db-list-backups` command. Restore is a strict full replacement of the entire table from a selected JSON backup, with one exception: the Backup_Audit_Records (the audit history of backup, delete and restore actions) are preserved across a restore and never erased. A restore is protected by an automatic pre-restore safety backup, explicit source selection, and a typed confirmation phrase. All backup, restore, and delete actions are audited. The feature is admin-only and must be deployable and testable in the development environment before production.

## Glossary

- **Backup_Service**: The backend Lambda component that creates backups, lists backups, downloads backup content, deletes backups, and performs restores.
- **JSON_Backup**: An application-level export file containing every item of the DynamoDB table serialized as JSON, stored in the Backup_Bucket.
- **AWS_Native_Backup**: A DynamoDB on-demand backup created via the DynamoDB create-backup operation.
- **Backup_Bucket**: A new dedicated per-environment Amazon S3 bucket for storing JSON_Backup files, following the name pattern `rcpm-impressionnistes-backups-{env}` (for example `rcpm-impressionnistes-backups-dev` and `rcpm-impressionnistes-backups-prod`), with encryption enabled, versioning enabled, and all public access blocked.
- **Backup_Category**: A classifier (also referred to as Backup_Type) applied to each JSON_Backup that distinguishes at least two categories: a regular/manual backup with category `manual`, created by an Admin via the Create Backup action; and a safety pre-restore backup with category `safety-pre-restore`, created automatically immediately before a Restore_Operation. Category values are stable identifiers.
- **Backup_Identifier**: The human-readable, self-describing name or key of a JSON_Backup that embeds, from the name alone, an explicit Backup_Category marker and a UTC timestamp, and, for a Safety_Backup, a reference to the source JSON_Backup that the Restore_Operation was about to restore.
- **Safety_Backup**: A JSON_Backup and an AWS_Native_Backup of the current table state taken automatically immediately before a restore executes, whose Backup_Category is `safety-pre-restore`. A Safety_Backup is clearly and distinctly identified as a pre-restore safety backup (not relying on timestamp alone) and records a reference to the source JSON_Backup that the Restore_Operation was about to restore.
- **Restore_Operation**: A strict full-replacement operation that purges every item from the table, except the Backup_Audit_Records, and rewrites the contents of a selected JSON_Backup as specified in Requirement 7.
- **Registration_Table**: The single DynamoDB table named `impressionnistes-registration-{env}`.
- **Database_Management_Page**: The admin-only frontend page "Gestion de la base" containing a Backup/Restore section (this spec) and a placeholder for a future Database Reset section.
- **Admin**: An authenticated user whose role is `admin`.
- **Audit_Record**: An `AUDIT#` item recording an administrative action, who performed it, and when.
- **Backup_Audit_Record**: An Audit_Record written by the Backup_Service for a backup action (create, delete, restore), stored under the dedicated audit partition `AUDIT#DATABASE_BACKUP`.
- **Confirmation_Phrase**: A fixed text string the Admin must type exactly to authorize a Restore_Operation.
- **Backup_Metadata**: The descriptive attributes of a JSON_Backup, consisting of timestamp, item count, size, the identity of the Admin who created it, and the Backup_Category; for a Safety_Backup, the Backup_Metadata also includes the identifier of the source JSON_Backup that the Restore_Operation was about to restore.


> **Note (database-reset spec):** a third Backup_Category `safety-pre-reset` was introduced by the `database-reset` spec. Its Backup_Identifier is `safety-pre-reset_{timestamp}.json` (no source part), the page badge is "Sécurité avant purge", and it is created before a selective purge. It can be the source of a `safety-pre-restore` backup (restoring it is the undo of a purge). The two-category wording above is otherwise unchanged.

## Requirements

### Requirement 1: Database Management Page Access

**User Story:** As an admin, I want a dedicated Database Management page accessible from the Admin menu, so that I can manage backups and restores of the system data in one place.

#### Acceptance Criteria

1. WHEN an Admin opens the Admin menu, THE Database_Management_Page SHALL be presented as a selectable menu entry labeled "Gestion de la base".
2. WHEN an Admin navigates to the Database_Management_Page, THE Database_Management_Page SHALL display a Backup/Restore section.
3. THE Database_Management_Page SHALL reserve a distinct area for a future Database Reset section without implementing Database Reset functionality in this feature.
4. IF a user whose role is not `admin` attempts to navigate to the Database_Management_Page, THEN THE Database_Management_Page SHALL deny access and SHALL NOT display backup or restore controls.
5. THE Database_Management_Page SHALL render its controls using the project design system components, including BaseButton, StatusBadge, FormGroup, MessageAlert, BaseModal, DataCard, and SortableTable where applicable.
6. WHILE any backup, download, delete or restore operation is in progress, THE Database_Management_Page SHALL display a status message naming the operation in progress and SHALL disable every other action.

### Requirement 2: Admin-Only Access

**User Story:** As an admin, I want backup and restore actions restricted to administrators, so that only authorized users can perform these sensitive operations.

#### Acceptance Criteria

1. THE Backup_Service SHALL accept requests to create, list, download, delete and restore backups only from an Admin.
2. IF a request to any backup or restore operation is made by a user who is not an Admin, THEN THE Backup_Service SHALL reject the request with an authorization error and SHALL NOT perform the operation.

### Requirement 3: Create Backup

**User Story:** As an admin, I want to create a backup of the entire database with one action, so that I can preserve a recoverable copy of the current system state.

#### Acceptance Criteria

1. WHEN an Admin requests a backup, THE Backup_Service SHALL scan every item of the Registration_Table and write a JSON_Backup containing all scanned items to the Backup_Bucket.
2. WHEN an Admin requests a backup, THE Backup_Service SHALL create an AWS_Native_Backup of the Registration_Table.
3. WHEN a JSON_Backup is written, THE Backup_Service SHALL record Backup_Metadata consisting of the creation timestamp, the number of items included, the size of the JSON_Backup, the identity of the requesting Admin, and the Backup_Category.
4. WHEN a backup completes successfully, THE Backup_Service SHALL return a result that reports the number of items backed up and the identifier of the created JSON_Backup.
5. IF writing the JSON_Backup to the Backup_Bucket fails, THEN THE Backup_Service SHALL return an error that describes the failure and SHALL report that the backup did not complete.
6. IF creating the AWS_Native_Backup fails, THEN THE Backup_Service SHALL return an error that describes the failure and SHALL report which backup artifact failed.
7. WHEN an Admin triggers a backup from the Database_Management_Page, THE Database_Management_Page SHALL display a loading state during the operation and SHALL display the success result or the error result when the operation returns.
8. WHEN the Backup_Service creates a JSON_Backup, THE Backup_Service SHALL set the Backup_Identifier so that it embeds an explicit Backup_Category marker and a UTC timestamp, so the Backup_Category is identifiable from the Backup_Identifier alone without opening the JSON_Backup.
9. WHEN the Backup_Service creates a backup from the Create Backup action, THE Backup_Service SHALL set the Backup_Category to `manual` and SHALL set the Backup_Identifier to carry the `manual` marker.

### Requirement 4: List Backups

**User Story:** As an admin, I want to see a list of existing backups with their details, so that I can choose which backup to download, delete, or restore.

#### Acceptance Criteria

1. WHEN an Admin opens the Backup/Restore section, THE Backup_Service SHALL return the list of existing JSON_Backup entries available in the Backup_Bucket.
2. THE Database_Management_Page SHALL display, for each JSON_Backup, its creation timestamp, item count, size, and the identity of the Admin who created it.
3. WHILE no JSON_Backup exists, THE Database_Management_Page SHALL display an empty-state message indicating that no backups are available.
4. IF retrieving the backup list fails, THEN THE Backup_Service SHALL return an error that describes the failure, and THE Database_Management_Page SHALL display the error.
5. WHEN the Database_Management_Page displays the list of JSON_Backup entries, THE Database_Management_Page SHALL display each JSON_Backup's Backup_Category as a distinct label so an Admin can visually distinguish safety pre-restore backups from manual backups, and SHALL NOT rely on the creation timestamp alone to differentiate them.

### Requirement 5: Download Backup

**User Story:** As an admin, I want to download a JSON backup file, so that I can retain an off-system copy of the data.

#### Acceptance Criteria

1. WHEN an Admin requests to download a specified JSON_Backup, THE Backup_Service SHALL return the content of that JSON_Backup.
2. IF the specified JSON_Backup does not exist, THEN THE Backup_Service SHALL return an error indicating the backup was not found.
3. WHEN a download is in progress, THE Database_Management_Page SHALL display a loading state until the download content is available or an error is returned.

### Requirement 6: Delete Backup

**User Story:** As an admin, I want to delete a JSON backup, so that I can remove obsolete or unneeded backup copies.

#### Acceptance Criteria

1. WHEN an Admin requests deletion of a specified JSON_Backup, THE Backup_Service SHALL remove that JSON_Backup from the Backup_Bucket.
2. WHEN an Admin requests deletion of a JSON_Backup, THE Database_Management_Page SHALL require the Admin to confirm the deletion before the Backup_Service removes the JSON_Backup.
3. WHEN a JSON_Backup is deleted successfully, THE Backup_Service SHALL return a result confirming the deletion, and THE Database_Management_Page SHALL update the displayed backup list to exclude the deleted JSON_Backup.
4. IF the specified JSON_Backup does not exist, THEN THE Backup_Service SHALL return an error indicating the backup was not found.

### Requirement 7: Restore from Backup

**User Story:** As an admin, I want to restore the database to the exact contents of a selected backup, so that I can recover the system to a known good state.

#### Acceptance Criteria

1. WHEN an Admin confirms a Restore_Operation for a selected JSON_Backup, THE Backup_Service SHALL remove every item from the Registration_Table, except Backup_Audit_Records as specified in criterion 7.10, and then write exactly the items contained in the selected JSON_Backup, except Backup_Audit_Records as specified in criterion 7.11.
2. WHEN a Restore_Operation completes successfully, THE Registration_Table SHALL contain exactly the set of items present in the selected JSON_Backup, except Backup_Audit_Records as specified in criterion 7.11.
3. WHEN a Restore_Operation completes successfully, THE Backup_Service SHALL return a result that reports the number of items purged and the number of items restored.
4. WHEN an Admin initiates a Restore_Operation, THE Backup_Service SHALL create a Safety_Backup of the current Registration_Table state, consisting of a JSON_Backup and an AWS_Native_Backup, before purging the Registration_Table.
5. IF creating the Safety_Backup fails, THEN THE Backup_Service SHALL abort the Restore_Operation, SHALL NOT purge the Registration_Table, and SHALL return an error describing the failure.
6. WHEN the Restore_Operation runs, THE Database_Management_Page SHALL display a loading state during the operation and SHALL display the success result or the error result when the operation returns.
7. WHEN the Backup_Service creates a Safety_Backup before a Restore_Operation, THE Backup_Service SHALL set its Backup_Category to `safety-pre-restore` and SHALL set its Backup_Identifier to carry the `safety-pre-restore` marker, a reference to the source JSON_Backup being restored, and a UTC timestamp.
8. WHEN the Backup_Service creates a Safety_Backup before a Restore_Operation, THE Backup_Service SHALL record in the Safety_Backup's Backup_Metadata the Backup_Category `safety-pre-restore` and the identifier of the source JSON_Backup that was about to be restored.
9. WHEN a Restore_Operation completes successfully, THE Database_Management_Page SHALL present the Safety_Backup of that Restore_Operation as the way to undo it, with an action to restore that Safety_Backup.
10. WHEN a Restore_Operation executes, THE Backup_Service SHALL NOT delete the existing Backup_Audit_Records from the Registration_Table.
11. WHEN a Restore_Operation completes successfully, THE Registration_Table SHALL contain exactly the items of the selected JSON_Backup that are not Backup_Audit_Records, plus the union of the Backup_Audit_Records that existed before the Restore_Operation and the Backup_Audit_Records contained in the selected JSON_Backup, plus the Audit_Record of that Restore_Operation.
12. WHEN a Restore_Operation executes, THE Backup_Service SHALL replace every Audit_Record that is not a Backup_Audit_Record (for example permission audit logs under other `AUDIT#` partitions) with the content of the selected JSON_Backup.
13. WHEN a Restore_Operation completes successfully, THE Backup_Service SHALL report a purged item count that excludes the preserved Backup_Audit_Records.
14. WHEN an Admin restores a Safety_Backup to undo a Restore_Operation, THE Backup_Service SHALL preserve the Backup_Audit_Records so that the history of both Restore_Operations remains available.

### Requirement 8: Restore Confirmation Safeguards

**User Story:** As an admin, I want strong safeguards before a restore executes, so that I cannot accidentally replace the entire database.

#### Acceptance Criteria

1. THE Database_Management_Page SHALL require the Admin to explicitly select a source JSON_Backup from the backup list before a Restore_Operation can be initiated.
2. THE Database_Management_Page SHALL require the Admin to type the Confirmation_Phrase exactly before a Restore_Operation can be initiated.
3. WHILE no source JSON_Backup is selected, THE Database_Management_Page SHALL keep the restore action disabled.
4. WHILE the typed text does not match the Confirmation_Phrase, THE Database_Management_Page SHALL keep the restore action disabled.
5. THE Database_Management_Page SHALL leave every destructive restore control unselected and unchecked by default.
6. IF the specified source JSON_Backup is missing when a Restore_Operation is requested, THEN THE Backup_Service SHALL reject the Restore_Operation with an error indicating the source backup was not found and SHALL NOT purge the Registration_Table.
7. IF the specified source JSON_Backup cannot be parsed as a valid backup, THEN THE Backup_Service SHALL reject the Restore_Operation with an error indicating the source backup is invalid and SHALL NOT purge the Registration_Table.
8. WHEN an Admin selects a source JSON_Backup for a Restore_Operation, THE Database_Management_Page SHALL display the Backup_Category of the selected JSON_Backup at selection time so that the Admin can distinguish a safety pre-restore backup from a manual backup before confirming the Restore_Operation.

### Requirement 9: Restore Failure Reporting

**User Story:** As an admin, I want clear information when a restore does not fully succeed, so that I can recover using the safety backup.

#### Acceptance Criteria

1. IF a Restore_Operation fails after the Registration_Table has been purged, THEN THE Backup_Service SHALL return an error reporting that the Registration_Table is in a partially restored state.
2. WHEN a Restore_Operation fails after purging, THE Backup_Service SHALL include in the error result the identifier of the Safety_Backup taken before the Restore_Operation.
3. WHEN a Restore_Operation fails, THE Database_Management_Page SHALL display the error result including the Safety_Backup identifier.
4. IF the Database_Management_Page receives no response to a Restore_Operation request (for example a network error or gateway timeout), THEN THE Database_Management_Page SHALL display a message stating that the outcome is unknown and instructing the Admin to refresh the backup list and verify the state of the database before taking further action.

### Requirement 10: Backup Content Integrity

**User Story:** As an admin, I want backups to capture the data faithfully, so that a restore reproduces the original state exactly.

#### Acceptance Criteria

1. WHEN the Backup_Service creates a JSON_Backup, THE JSON_Backup SHALL include every item type stored in the Registration_Table, including `USER#`, `CONFIG`, `RACE`, `CLUB`, `TEAM#...#BOAT#...`, `TEAM#...#CREW_MEMBER#...`, `TEAM#...#PAYMENT#...`, `TEMP_ACCESS#`, and `AUDIT#` items.
2. WHEN the Backup_Service creates a JSON_Backup, THE JSON_Backup SHALL preserve the key attributes PK and SK and all stored attributes of each item.
3. FOR ALL items in a JSON_Backup, restoring that JSON_Backup and then creating a new JSON_Backup SHALL produce a JSON_Backup containing the same set of items as the restored JSON_Backup, excluding Backup_Audit_Records from the comparison.

### Requirement 11: Audit Logging

**User Story:** As an admin, I want backup, restore, and delete actions recorded, so that there is an accountable history of these operations.

#### Acceptance Criteria

1. WHEN a backup completes, THE Backup_Service SHALL write an Audit_Record capturing the backup action, the requesting Admin identity, and the timestamp.
2. WHEN a Restore_Operation completes, THE Backup_Service SHALL write an Audit_Record capturing the restore action, the selected source JSON_Backup, the requesting Admin identity, and the timestamp.
3. WHEN a JSON_Backup is deleted, THE Backup_Service SHALL write an Audit_Record capturing the delete action, the deleted JSON_Backup identifier, the requesting Admin identity, and the timestamp.
4. THE Backup_Service SHALL preserve Backup_Audit_Records across Restore_Operations.

### Requirement 12: Environment Deployment and Testing

**User Story:** As an operator, I want the feature deployable and verifiable in development before production, so that I can validate backup and restore safely.

#### Acceptance Criteria

1. THE Backup_Bucket SHALL be provisioned per environment, with the development bucket named `rcpm-impressionnistes-backups-dev` and the production bucket named `rcpm-impressionnistes-backups-prod`.
2. THE Backup_Bucket SHALL have server-side encryption enabled, object versioning enabled, and all public access blocked.
3. THE Backup_Service SHALL operate against the Registration_Table of the environment in which it is deployed.
4. WHERE the feature is deployed to the development environment, THE Backup_Service SHALL support creating a backup and performing a Restore_Operation so that both can be verified before production deployment.
5. WHEN a backup or restore request is received, THE Backup_Service SHALL complete the operation synchronously within a single invocation and return the result without requiring the client to poll for status.
