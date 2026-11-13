# Implementation Plan: Database Backup & Restore

## Overview

Build the feature bottom-up so each step is verifiable: backend service module with its tests, a single routing Lambda, CDK (bucket + Lambda + routes), then the frontend (util, composable, components, view, router, i18n), then manual dev and prod rollout, then documentation.

Conventions for every task:
- Shared Python code goes in `functions/shared/` only. Never edit `functions/layer/python/`. The layer is rebuilt by the `build-layer` step that `make deploy-dev` / `make deploy-prod` already run, so no separate step is needed.
- Backend tests: pytest + moto, explicit parametrized cases, no Hypothesis. Reuse the fixtures in `tests/conftest.py` and mirror `tests/integration/test_admin_api.py`. Only one new fixture (`backup_bucket`, moto S3) is added. The `dynamodb_table` fixture seeds configuration items, so tests asserting exact counts or an empty table must clear the seeded items first or compare against the seeded set; compare item sets keyed by `(PK, SK)`.
- Frontend: design-system components, design tokens, fr/en i18n, same fields and actions in card and table views, `size="small"` in rows/cards, `size="medium"` in modals.
- All build, test and deploy commands run through `infrastructure/Makefile` (`make test`, `make test-backend`, `make test-frontend`, `make lint-frontend`, `make synth`, `make deploy-dev`, `make deploy-frontend-dev`, `make deploy-prod`, `make deploy-frontend-prod`). No new Makefile target is needed.
- No commits or pushes are part of this plan.
- Not in scope (removed by the design): permission matrix entries, `init_config.py` change, migration, per-endpoint Lambdas, bucket lifecycle rule.

## Tasks

- [x] 1. Backend service module `functions/shared/backup_service.py`
  - [x] 1.1 Implement constants, naming, envelope and typed-JSON helpers
    - Constants: `CATEGORY_MANUAL`, `CATEGORY_SAFETY`, `CONFIRMATION_PHRASE`, `SOURCE_MARKER`, `FORMAT_VERSION`, `AUDIT_PK`
    - `make_backup_id`, `parse_backup_id`, regex validation raising `InvalidBackupId`
    - `scan_table` (low-level client, `ConsistentRead=True`, paginated), `encode_items` / `decode_items` (recursive `B`/`BS` base64 helper over `M`/`L`)
    - `build_envelope`, `validate_envelope` (format_version, list of items, string PK/SK, no duplicate keys, `item_count` match, base64 decodes)
    - _Requirements: 3.3, 3.8, 3.9, 7.7, 8.7, 10.1, 10.2_

  - [x] 1.2 Write tests for naming, envelope and special types
    - Create `tests/integration/test_database_backup_restore.py` with the `backup_bucket` fixture (depends on `dynamodb_table`, starts moto `mock_s3`, creates the bucket, sets `BACKUP_BUCKET`; `from moto import mock_s3` is importable in the test venv, moto 4.2.9, so `tests/requirements.txt` is unchanged)
    - Needs 1.3 and 1.5 implemented (the restore/undo test goes through restore)
    - `test_backup_id_roundtrip`, `test_backup_id_rejects_invalid` (traversal, `/`, wrong category, safety without source, manual with source, nested chain id such as a safety id whose source part is itself a safety id with a source)
    - `test_restore_undo_repeatedly_keeps_valid_ids` (restore then undo repeated to depth 6: every generated id is valid and parses back with the right category, timestamp and `source_ref`; ids stay under 150 chars; native backup names stay under 100 chars and match `^[a-zA-Z0-9_.-]{3,255}$`)
    - Naming tests: the safety id uses the bounded source reference `{source_category}_{source_timestamp}` for both a manual source and a safety source; a nested chain id is rejected; `parse_backup_id` returns `source_ref` (and the `source_stem` alias) and NOT a derived `source_backup_id`
    - `test_special_dynamodb_types_roundtrip` (N decimals/exponent, SS, NS, BS, B, nested M/L, BOOL, NULL, unicode)
    - **Property 2: Backup identifier encodes category and time**
    - **Property 1 and 3 (types part): faithful capture and round trip**
    - **Validates: Requirements 3.2, 3.8, 3.9, 7.7, 10.2, 10.3**

  - [x] 1.3 Implement S3 I/O, native backup, create, list, read, delete, audit
    - Build boto3 clients through lazy getters `_get_dynamodb_client()` / `_get_s3_client()` (precedent: `functions/shared/secrets_manager.py` `_get_s3_client` with module-level `_s3_client`) so tests can inject fakes; table name from env `TABLE_NAME`, bucket from env `BACKUP_BUCKET`
    - `create_backup(category, user, source_id=None)`: JSON to S3 with ASCII object metadata (`category`, `created-at`, `created-by`, `item-count`, `source-backup-id`), then native DynamoDB backup named `{table_name}-{category}_{timestamp}` (no source part; BackupName is limited to 255 chars `[a-zA-Z0-9_.-]`)
    - `source_backup_id` (the FULL real source id) is stored in the S3 object metadata, the envelope metadata, the return value of `create_backup` and the audit details; the S3 key only carries the bounded `source_ref`
    - `list_backups` (S3 list + `head_object`, category/time/`source_ref` parsed from key, newest first); each row exposes both `source_backup_id` (from the object metadata) and `source_ref` (from the key); `read_backup`, `delete_backup` (404 check first)
    - `write_audit(table, action, user, details)` writing `AUDIT#DATABASE_BACKUP` / `{timestamp}#{user_id}`
    - Error codes: `JSON_BACKUP_FAILED`, `NATIVE_BACKUP_FAILED` (with `failed_artifact`), `BACKUP_NOT_FOUND`, `LIST_FAILED`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 5.1, 5.2, 6.1, 6.4, 11.1, 11.3_

  - [x] 1.4 Write tests for create, list, download, delete and audit
    - Clear the items seeded by `dynamodb_table` before exact-count or empty-table assertions (or compare against the seeded set); compare sets keyed by `(PK, SK)`
    - Inject failures with `unittest.mock.patch` on `backup_service` functions or a thin fake client wrapper (moto never fails `CreateBackup` or S3 puts): native backup raises `ClientError`, `put_object` raises
    - `test_create_backup_captures_items` (empty, 1, 1250 items, each item-type prefix: USER#, CONFIG, RACE, CLUB, TEAM#, TEMP_ACCESS#, AUDIT#)
    - `test_create_backup_s3_failure`, `test_create_backup_native_failure`
    - `test_list_download_delete` including not-found cases
    - `test_audit_records` for create and delete
    - **Property 1: Backup captures every item faithfully**
    - **Property 11: List, download and delete reflect the bucket**
    - **Property 12: Every state-changing action is audited (create, delete)**
    - **Validates: Requirements 3.5, 3.6, 4.1, 5.1, 6.1, 10.1, 11.1, 11.3**

  - [x] 1.5 Implement batch write, purge, verify, restore and `handle_*` adapters
    - `batch_write_with_retry` (chunks of 25, up to 8 attempts, backoff 50 ms doubling, cap 1 s, then `BatchWriteError`)
    - `purge_table` (full consistent scan, deletes by PK/SK), `write_items`, count verification (`Select="COUNT"`)
    - `restore_backup(backup_id, phrase, user)` in the design's order: validate id, validate phrase, load and validate source, safety backup (abort before purge on failure), purge, write, verify, audit after rewrite
    - The safety backup step passes the real source backup id: `create_backup(CATEGORY_SAFETY, user, source_id=backup_id)`; the restore audit details include `source_backup_id` and `safety_backup_id`
    - One top-level `try/except` around purge, write and verify that returns `RESTORE_PARTIAL` with `safety_backup_id`, `safety_native_backup`, `source_backup_id`, `stage`, `purged_count`, `written_count`, `steps`
    - `RestoreResult` with counts, steps, `audit_written`, `duration_ms`
    - `handle_create`, `handle_list`, `handle_download`, `handle_delete`, `handle_restore` returning `success_response` / `error_response`
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.7, 7.8, 8.2, 8.6, 8.7, 9.1, 9.2, 11.2, 12.5_

  - [x] 1.6 Write tests for restore
    - Clear the items seeded by `dynamodb_table` where exact counts matter; compare item sets keyed by `(PK, SK)`
    - Inject failures with `unittest.mock.patch` on `backup_service` functions or a thin fake client wrapper: first N `batch_write_item` calls return `UnprocessedItems` (moto never does), safety JSON/native backup raises, purge/write/verify raise at a chosen stage
    - `test_restore_replaces_table` (source smaller / equal / larger / disjoint keys) with count assertions
    - `test_restore_creates_safety_backup_first` (safety object exists before the first delete; its S3 key includes the bounded `source_ref`, while the object metadata, envelope metadata and audit record carry the full `source_backup_id`; the restore audit details include `source_backup_id` and `safety_backup_id`)
    - `test_restore_aborts_when_safety_fails` (JSON fails, native fails; table unchanged)
    - `test_restore_rejects_invalid_source` (missing, bad JSON, wrong version, no PK, duplicates, count mismatch; no safety backup created)
    - `test_restore_rejects_wrong_phrase` (empty, lowercase, trailing space, missing)
    - `test_restore_partial_failure` (purge, write, verify) then restoring the safety backup returns the original item set
    - `test_batch_write_retries_unprocessed_items`
    - `test_audit_records` extended: restore record present in the table after restore
    - **Property 3: Restore round trip**
    - **Property 4: Restore reports accurate counts**
    - **Property 5: Safety backup precedes purge**
    - **Property 6: Failed safety backup aborts without purge**
    - **Property 7: Invalid source leaves the table untouched**
    - **Property 8: Wrong confirmation phrase is rejected server-side**
    - **Property 9: Partial failure reports the safety backup**
    - **Property 12: Every state-changing action is audited (restore)**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.7, 7.8, 8.2, 8.6, 8.7, 9.1, 9.2, 11.2**

- [x] 2. Single Lambda handler
  - [x] 2.1 Create `functions/admin/manage_backups.py`
    - `ROUTES` dict keyed by `(httpMethod, resource)` for the five routes, 404 `NOT_FOUND` for unknown routes
    - Parse the restore body (`confirmation_phrase`) with the existing JSON body helper in `functions/shared/responses.py`; a missing or invalid body returns `INVALID_CONFIRMATION` / 400, never a 500
    - `@handle_exceptions` then `@require_admin`, admin identity from claims via `get_user_from_event`, same conventions as the other handlers in `functions/admin/`
    - _Requirements: 2.1, 2.2, 12.3, 12.5_

  - [x] 2.2 Write handler tests
    - `mock_api_gateway_event` does not set `resource`: set `event['resource']` explicitly (e.g. `/admin/backups/{backup_id}/restore`) plus `path_parameters={'backup_id': ...}`; admin events use `groups=['admins']` and a `user_id`
    - `test_non_admin_rejected` parametrized over all five routes: 403 and no S3 object, native backup or table item changed
    - Restore with a missing or invalid body returns 400 `INVALID_CONFIRMATION`
    - Routing test for an unknown route (404)
    - End-to-end create then list through the handler using the admin event pattern from `test_admin_api.py`
    - **Property 10: Non-admin requests are rejected without effect**
    - **Validates: Requirements 2.1, 2.2**

- [x] 3. CDK infrastructure
  - [x] 3.1 Add `backup_bucket` to `infrastructure/stacks/database_stack.py`
    - `rcpm-impressionnistes-backups-{env}`, `S3_MANAGED` encryption, `versioned=True`, `BLOCK_ALL`, `enforce_ssl=True`
    - Removal policy follows the table's policy; no `auto_delete_objects`, no lifecycle rule
    - Expose `self.backup_bucket` beside `secrets_bucket`
    - _Requirements: 12.1, 12.2_

  - [x] 3.2 Add the Lambda, routes and IAM in `infrastructure/stacks/api_stack.py` (after 2.1: the handler file must exist before synth)
    - The bucket is reached as `database_stack.backup_bucket` (ApiStack already receives `database_stack`, like `secrets_bucket`); no change in `infrastructure/app.py`
    - Add `BACKUP_BUCKET` to `common_env`
    - Add a `memory_size=256` parameter (defaulting to 256) to `_create_lambda_function` (currently hardcoded 256)
    - Create `lambda_functions['manage_backups']` with handler path `admin/manage_backups`, timeout 120, memory 512
    - IAM: `backup_bucket.grant_read_write(fn)` and `dynamodb:CreateBackup` on the table ONLY (no other backup actions)
    - `admin_resource.add_resource('backups')`, then `add_method(..., apigateway.LambdaIntegration(fn, proxy=True), authorizer=self.authorizer, authorization_type=apigateway.AuthorizationType.COGNITO)` for POST and GET on `/admin/backups`, GET on `{backup_id}/download`, DELETE on `{backup_id}`, POST on `{backup_id}/restore`; CORS preflight is already covered by the API-level `default_cors_preflight_options`
    - _Requirements: 2.1, 12.1, 12.3, 12.5_

- [x] 4. Checkpoint - Backend and infrastructure
  - Ask the user to run `cd infrastructure && make test-backend` (or `make test`); it must be green
  - The project has NO CDK/infra tests, and no CDK test harness is added. The infrastructure check is the mandatory review of the `make synth ENV=dev` output: bucket name, encryption, versioning, public access block, `RETAIN`, enforce SSL, one Lambda (120 s / 512 MB) with five methods under `/admin/backups`, and IAM limited to `dynamodb:CreateBackup` plus table and bucket read/write
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Frontend
  - [x] 5.1 Create `frontend/src/utils/backupNaming.js`
    - Export `CONFIRMATION_PHRASE`, `CATEGORY_MANUAL`, `CATEGORY_SAFETY`, `SOURCE_MARKER` (values identical to the backend), `parseBackupId`, `categoryBadge` (manual maps to `paid`, safety maps to `incomplete`, with label keys), `isPhraseValid` (exact, case-sensitive)
    - _Requirements: 3.8, 4.5, 7.7, 8.2, 8.4, 8.8_

  - [x] 5.2 Write `frontend/src/utils/backupNaming.test.js`
    - Table-driven cases for `parseBackupId` (manual, safety, invalid), `categoryBadge`, `isPhraseValid` (exact match only; case, whitespace, empty), constants
    - **Validates: Requirements 4.5, 8.2, 8.4, 8.8**

  - [x] 5.3 Create `frontend/src/composables/useBackupRestore.js`
    - Reuse `services/apiClient`; expose `state`, `busyLabel`, `backups`, `selected`, `phrase`, `result`, `error`, `load`, `create`, `download`, `remove`, `select`, `setPhrase`, `confirmRestore`, `dismiss`
    - States `idle | busy | ready_to_restore | success | error | partial`; transitions only inside the composable, per the state diagram
    - Enabled-actions table from the design (e.g. delete disabled on the selected row and in `partial`; create disabled in `partial` and `success`; only the safety backup selectable in `success`)
    - `canRestore` rule; destructive controls start unselected and empty
    - Exported `nextStateFromRestoreError(err)`: `err.response.data.error.code === 'RESTORE_PARTIAL'` gives `partial`; any other envelope code gives `error`; no `err.response` (network error, CORS-masked 401, `err.code === 'ECONNABORTED'`), HTTP 504 or a non-envelope body gives `error` with the outcome-unknown message
    - A 401 is redirected to login by the `apiClient` interceptor; the outcome is treated as unknown after re-login
    - Download builds a `Blob` from `content` and triggers the browser download
    - Safety rows are labelled from the list field `source_ref` (and `parseBackupId().sourceRef` when needed); the real source id is never derived from the key
    - After a successful restore, expose the safety backup for the undo action ("Annuler cette restauration" selects it, phrase still required)
    - _Requirements: 1.6, 3.7, 5.3, 6.2, 6.3, 7.6, 7.9, 8.1, 8.3, 8.4, 8.5, 9.3, 9.4_

  - [x] 5.4 Write `frontend/src/composables/useBackupRestore.test.js`
    - Mock `apiClient`; cover every transition of the 6-state diagram
    - Table-driven enabled-actions check per state, and Restore disabled without selection or with a wrong phrase; `busy` disables everything
    - Table-driven `nextStateFromRestoreError` cases: `RESTORE_PARTIAL`, another envelope code, 504, no response, `ECONNABORTED`, 401
    - **Property 13: UI action availability follows the state model**
    - **Property 14: Restore error classification**
    - **Validates: Requirements 1.6, 8.1, 8.3, 8.4, 8.5, 9.3, 9.4**

  - [x] 5.5 Add i18n keys to `frontend/src/locales/fr.json` and `en.json`
    - `admin.database.*`: `title`, `states.*`, `actions.*`, `category.*`, `list.*`, `restore.*`, `errors.<CODE>` for every code in the design's error table, `reset.placeholder*`; `nav.databaseManagement` ("Gestion de la base" / "Database management")
    - Include the "Rien n'a été modifié dans la base" message, the outcome-unknown message, the partial-state recovery instructions (including `make db-restore-backup BACKUP_ARN=<arn>` and PITR) and the undo texts
    - The Confirmation_Phrase is interpolated, not translated
    - _Requirements: 1.1, 3.7, 4.3, 4.4, 7.9, 9.3, 9.4_

  - [x] 5.6 Create the components in `frontend/src/components/admin/`
    - `BackupRestoreSection.vue`: state banner (state, what is possible, `busyLabel`), toolbar (Create, Refresh), list as `SortableTable` (desktop) and `DataCard` (mobile) with identical fields and actions (id, category `StatusBadge` rendering its default slot (it accepts `incomplete|complete|paid|forfait|free`), created_at, item_count, size, created_by, source (for a safety row: "avant restauration de : {source_ref}" from the list field `source_ref`, never derived from the key), Télécharger / Supprimer / Restaurer…), empty state, list loading with `components/base/LoadingSpinner.vue`, delete confirmation via the existing promise-based `useConfirm` composable (as in `views/admin/AdminPermissionAuditLogs.vue`), card header with bottom border
    - `RestorePanel.vue`: selected id with category badge and safety source, impact summary, phrase `FormGroup` with phrase as help text, Restore button (`danger`, `medium`), confirmation `BaseModal` (the restore confirmation stays a modal) with the texts from the design (Annuler `secondary` / Confirmer `danger`, both `medium`)
    - `RestoreResultPanel.vue`: `success` (counts, step list, highlighted undo `DataCard` with "Annuler cette restauration"), `error` (message, unchanged-database text, outcome-unknown instructions), `partial` (prominent `MessageAlert`, failed step, safety backup id and native name, recovery steps with "Restaurer la sauvegarde de sécurité")
    - `DatabaseResetPlaceholder.vue`: disabled `DataCard` "Bientôt disponible"
    - `BaseButton` for every button (`small` in rows/cards, `medium` in modals and panel actions), `MessageAlert` for messages, design tokens only, no custom badge or button CSS
    - _Requirements: 1.3, 1.5, 1.6, 3.7, 4.2, 4.3, 4.5, 5.3, 6.2, 7.6, 7.9, 8.1, 8.2, 8.3, 8.4, 8.5, 8.8, 9.3, 9.4_

  - [x] 5.7 Create the view, route, and navigation entries
    - `frontend/src/views/admin/AdminDatabaseManagement.vue`: page title, `BackupRestoreSection`, `DatabaseResetPlaceholder`
    - `frontend/src/router/index.js`: `/admin/database` with `meta: { requiresAuth: true, requiresAdmin: true }`
    - `App.vue` nav item (`v-if="authStore.isAdmin"`) and one card in `AdminDashboard.vue`, using the `nav.databaseManagement` key
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 5.8 Add `test_frontend_backend_constants_aligned` to `tests/integration/test_database_backup_restore.py`
    - Read `frontend/src/utils/backupNaming.js` as text and assert the same phrase, category identifiers and source marker as `backup_service.py`
    - **Validates: Requirements 3.8, 7.7, 8.2**

- [x] 6. Checkpoint - Frontend
  - Ask the user to run `cd infrastructure && make test-frontend` and `make lint-frontend`, then `make test` once more for the full suite
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. DEV deployment and verification (manual, performed by the user, not for automated execution)
  - [x] 7.1 Deploy to DEV
    - `cd infrastructure && make deploy-dev`, then `make deploy-frontend-dev`
    - Confirm the bucket `rcpm-impressionnistes-backups-dev` exists (`make describe-infra-dev` for URLs)
    - _Requirements: 12.1, 12.2, 12.3, 12.4_

  - [x] 7.2 Run the manual verification checklist in DEV
    - Open "Gestion de la base": empty state shown, non-admin cannot reach the page
    - Create a backup: name starts with `manual_`, badge "Manuelle", object metadata in S3 (category, created-at, created-by, item-count), item count matches `make db-view ENV=dev`; download it and check `metadata.item_count`
    - Change data in the app (add a crew member, delete a boat)
    - Restore the backup: wrong phrase keeps the button disabled; correct phrase and modal confirmation; the change is gone; the result shows counts and the safety backup (`safety-pre-restore_<ts>_before-restore-of_<source_category>_<source_ts>.json` (e.g. `safety-pre-restore_<ts>_before-restore-of_manual_<ts>.json`), badge "Sécurité avant restauration")
    - Undo: "Annuler cette restauration", type the phrase, confirm; the changes are back
    - Delete a backup via the confirmation modal; it disappears
    - `make db-list-backups ENV=dev` shows the native backups; `make db-view ENV=dev` shows `AUDIT#DATABASE_BACKUP` items
    - _Requirements: 1.1, 1.2, 1.4, 3.7, 4.2, 4.5, 5.1, 6.2, 6.3, 7.3, 7.4, 7.7, 7.9, 8.4, 8.8, 11.1, 11.2, 11.3, 12.4_

  - [x] 7.3 Run failure drills in DEV (required)
    - Upload a file with a corrupted `item_count` to the dev bucket and try to restore it: expect an error and an unchanged table
    - Confirm the banner and disabled actions while an operation is running
    - Confirm the outcome-unknown message: start a restore in DEV, cut the network (browser offline) while it runs, check that the page shows the 'outcome unknown' message, then restore connectivity, refresh the list and check that a new `safety-pre-restore_…` backup exists and that the data is in the expected state
    - _Requirements: 1.6, 8.7, 9.3, 9.4_

- [x] 10. Preserve backup audit records across restore
  - [x] 10.1 Preserve the `AUDIT#DATABASE_BACKUP` partition in `restore_backup`
    - Edit `functions/shared/backup_service.py` only, never `functions/layer/python/`
    - Purge deletes every item whose `PK != AUDIT_PK` and records the preserved audit keys
    - Write puts all source items, including the source's own `AUDIT_PK` records
    - Verify expects `|source keys ∪ preserved audit keys|`, computed before the write
    - `purged_count` excludes the preserved records; add `preserved_audit_count` to `RestoreResult` and to the `RESTORE_PARTIAL` details
    - The restore audit record is still written after verify
    - _Requirements: 7.1, 7.2, 7.10, 7.11, 7.12, 7.13, 7.14, 11.4_

  - [x] 10.2 Write tests for audit preservation
    - Extend `tests/integration/test_database_backup_restore.py` (pytest + moto, explicit parametrized cases, no Hypothesis)
    - Add `test_restore_preserves_backup_audit_records`: backup audit records written after the source backup survive the restore and an undo; source audit records are merged; the restore's own record is present; other `AUDIT#` partitions such as `AUDIT#PERMISSION_DENIAL` are replaced by the backup content; `purged_count` excludes preserved records; the verify count equals the union
    - Update existing tests whose expectations assumed audit records were erased (for example the handler end-to-end test audit list assertions, the partial-failure recovery assertions and the counts)
    - Run `cd infrastructure && make test-backend` and make it green
    - **Property 3: Restore round trip**
    - **Property 4: Restore reports accurate counts**
    - **Property 12: Every state-changing action is audited (restore)**
    - **Validates: Requirements 7.10, 7.11, 7.12, 7.13, 7.14, 10.3, 11.4**
    - _Requirements: 7.10, 7.11, 7.12, 7.13, 7.14, 10.3, 11.4_

  - [x] 10.3 Redeploy and re-check in DEV (manual, performed by the user)
    - `cd infrastructure && make deploy-dev`
    - Run a restore and an undo, then check that the `AUDIT#DATABASE_BACKUP` history keeps every create, delete and restore record (`make db-view ENV=dev`)
    - _Requirements: 7.14, 11.4, 12.4_

- [x] 8. PROD rollout (manual, user-driven, only after DEV is validated; not for automated execution)
  - [x] 8.1 Deploy to PROD
    - `cd infrastructure && make deploy-prod` and `make deploy-frontend-prod` (type the Makefile confirmation prompts)
    - Confirm the bucket `rcpm-impressionnistes-backups-prod` exists with the expected settings
    - _Requirements: 12.1, 12.2, 12.3_

  - [x] 8.2 Verify in PROD
    - Create a manual backup, check name, item count against `make db-view ENV=prod`, and download it
    - Do NOT restore in prod unless needed: if a restore is required, take a fresh manual backup first, run it outside active registration hours, and only with explicit user go-ahead
    - _Requirements: 3.1, 3.4, 5.1, 12.3_

- [x] 9. Documentation updates (ask the user to confirm before editing, per the `documentation-updates` and `requirements-sync` rules)
  - [x] 9.1 Update `docs/reference/api-endpoints.md` with the five `/admin/backups` endpoints, request/response examples and error codes
    - _Requirements: 2.1, 3.4, 4.1, 5.1, 6.1, 7.3_

  - [x] 9.2 Update `docs/reference/project-structure.md` with `backup_service.py`, `functions/admin/manage_backups.py`, `components/admin/` additions and the Backup_Bucket
    - _Requirements: 12.1_

  - [x] 9.3 Add a short runbook in `docs/guides/operations/` covering create, restore, undo, partial-failure recovery (safety backup, `make db-restore-backup`, PITR) and the outcome-unknown case
    - _Requirements: 7.9, 9.1, 9.2, 9.4_

  - [x] 9.4 Update `docs/reference/commands.md` with the relation of `db-backup`, `db-list-backups` and `db-restore-backup` to the feature
    - _Requirements: 3.2_

## Notes

- Task 7.2/7.3 were signed off by the user without running the undo step and the failure drills in DEV; task 10.3 includes an undo.
- All test tasks (1.2, 1.4, 1.6, 2.2, 5.2, 5.4, 5.8, 10.2) are required; none is optional and nothing is skipped. A checkpoint passes only when `make test-backend`, `make test-frontend` and `make lint-frontend` are green.
- The correctness properties are covered by explicit parametrized pytest and table-driven vitest cases (no Hypothesis).
- Tasks 7 and 8 are manual and user-driven. They are not for automated execution.
- Backend files were changed, so remind the user to run `cd infrastructure && make test` at each checkpoint.
- Backend/frontend alignment: `CONFIRMATION_PHRASE`, category identifiers and `SOURCE_MARKER` live in `backup_service.py` and `backupNaming.js`; task 5.8 checks them.
- Requirements file sync: this feature adds new behavior; ask the user before touching `.kiro/specs/impressionnistes-registration-system/requirements.md`.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "3.1", "5.1", "5.5"] },
    { "id": 1, "tasks": ["1.3", "5.2", "5.3"] },
    { "id": 2, "tasks": ["1.5", "5.4", "5.6"] },
    { "id": 3, "tasks": ["1.2", "2.1", "5.7"] },
    { "id": 4, "tasks": ["1.4", "3.2"] },
    { "id": 5, "tasks": ["1.6"] },
    { "id": 6, "tasks": ["2.2"] },
    { "id": 7, "tasks": ["5.8"] },
    { "id": 8, "tasks": ["7.1"] },
    { "id": 9, "tasks": ["7.2"] },
    { "id": 10, "tasks": ["7.3"] },
    { "id": 11, "tasks": ["10.1"] },
    { "id": 12, "tasks": ["10.2"] },
    { "id": 13, "tasks": ["10.3"] },
    { "id": 14, "tasks": ["8.1"] },
    { "id": 15, "tasks": ["8.2"] },
    { "id": 16, "tasks": ["9.1", "9.2", "9.3", "9.4"] }
  ]
}
```
