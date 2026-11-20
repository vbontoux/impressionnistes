# Implementation Plan: Database Reset (selective purge)

## Overview

Build the feature bottom-up so each step is verifiable: the new backup category in `backup_service` and the frontend naming, then the shared module `reset_service.py` with its tests, then the two routes on the existing ManageBackups Lambda, CDK (routes and IAM only), a backend checkpoint with a Api stack resource recount, the command-line tools and Makefile targets, the frontend (rules, composable, components, wiring, i18n), a frontend checkpoint, then manual dev and prod rollout and documentation.

Conventions for every task:
- No new Lambda. The two routes `GET` and `POST /admin/reset` go on the existing ManageBackups Lambda. All reset logic lives in ONE new module `functions/shared/reset_service.py`, which imports and reuses `backup_service.py` (scan, batch write, backup, audit). Never edit `functions/layer/python/`: the layer is rebuilt by the `build-layer` step that `make deploy-dev` / `make deploy-prod` already run.
- Backend tests: pytest + moto 4.2.9 (`mock_dynamodb`, `mock_s3`, `mock_cognitoidp`), explicit parametrized cases, NO Hypothesis. Reuse the existing fixtures and the fault-injection patterns of `tests/integration/test_database_backup_restore.py` and `tests/integration/test_admin_api.py`. The `dynamodb_table` fixture seeds configuration items: tests asserting exact counts clear the table first (or compare against the seeded set) and compare item sets keyed by `(PK, SK)`. Cognito test users are created with `Username=<sub>`, as in production.
- Frontend tests: vitest, table-driven. Design-system components (`BaseButton`, `StatusBadge`, `FormGroup`, `MessageAlert`, `BaseModal`, `DataCard`), design tokens only, fr/en i18n, `size="small"` in rows and cards, `size="medium"` in panels and modals, bottom-border separator on card headers.
- ALL test tasks are REQUIRED. There is no optional `*` marker in this plan.
- The agent runs tests itself, ONLY through `infrastructure/Makefile` targets: `make test-backend`, `make test-backend-one TEST=<path>`, `make test-frontend`, `make lint-frontend`, `make test`, `make synth ENV=dev`. Never `npm`, `npx`, `pytest`, `python` on scripts, or `cdk` directly. The agent never deploys and never commits or pushes. Deployments are run by the user (tasks 9 and 10).
- Scripts under `scripts/database/` follow the script-organization rule (flat structure, shebang, executable bit, README entry, Makefile target). Scripts are tested by importing their functions with moto; no test calls real AWS.
- Not in scope (removed by the design): Lambda, API resource beyond `/admin/reset`, permission matrix entry, `init_config.py` change, migration, bucket, table, async job, any automatic change of event configuration values.

## Tasks

- [x] 1. Backup category `safety-pre-reset` (backend and frontend naming)
  - [x] 1.1 Add the category to `functions/shared/backup_service.py`
    - Constant `CATEGORY_RESET = "safety-pre-reset"`; `CATEGORIES = (manual, safety-pre-restore, safety-pre-reset)`
    - Regex: one `_CAT = manual|safety-pre-restore|safety-pre-reset` alternation used for the id category AND inside `_STEM` (the source of a `safety-pre-restore` can now be a `safety-pre-reset`: the undo path)
    - `make_backup_id` / `parse_backup_id`: a source part is required for `safety-pre-restore` only and forbidden for `manual` and `safety-pre-reset`; id `safety-pre-reset_{timestamp}.json`; native name `{table}-safety-pre-reset_{timestamp}` (unchanged formula)
    - `create_backup`, `list_backups`, `restore_backup`, `build_envelope` stay unchanged (the category comes from the id)
    - _Requirements: 8.3, 8.4, 8.5_

  - [x] 1.2 Write tests for the new category in `tests/integration/test_database_backup_restore.py`
    - Extend the existing parametrized naming cases: `safety-pre-reset` valid without source, invalid with a source; update `test_backup_id_rejects_invalid`
    - `test_reset_backup_id_naming`: id matches `^safety-pre-reset_{timestamp}\.json$`, parses back to the same category and timestamp, native name matches `^[a-zA-Z0-9_.-]{3,255}$`
    - `test_list_shows_reset_category`: `list_backups` returns the category `safety-pre-reset` and no source part
    - `test_restore_of_reset_backup_returns_pre_purge_state`: restoring a `safety-pre-reset` backup yields a `safety-pre-restore` id whose `source_ref` is `safety-pre-reset_{timestamp}`, stays bounded, and returns the pre-purge item set
    - Keep every existing test green
    - **Property 8: Backup identifier and category**
    - **Validates: Requirements 8.3, 8.4, 8.5**

  - [x] 1.3 Add the category to `frontend/src/utils/backupNaming.js`
    - `CATEGORY_RESET`, regex alternation with the three categories, same parse rule as the backend (source part for `safety-pre-restore` only)
    - `categoryBadge`: `safety-pre-reset` maps to `forfait` (red) with a label key; `manual` stays `paid`, `safety-pre-restore` stays `incomplete`
    - _Requirements: 8.3, 8.4, 8.5_

  - [x] 1.4 Write the category cases in `frontend/src/utils/backupNaming.test.js`
    - Table-driven: the new category in `parseBackupId` (valid, invalid with source), `categoryBadge` (`forfait`), shared sample ids accepted and rejected like the Python regex
    - **Property 8: Backup identifier and category**
    - **Validates: Requirements 8.3, 8.4, 8.5**

  - [x] 1.5 Update the backup alignment tests in `tests/integration/test_database_backup_restore.py`
    - `test_frontend_backend_constants_aligned`: the category list now has three entries and `CATEGORY_RESET` equals the backend value
    - Update the assertion `alternation == 'manual|safety-pre-restore'` and the JS regex structure test (three categories); both sides accept and reject the same shared sample ids
    - **Property 8: Backup identifier and category**
    - **Validates: Requirements 8.3, 8.4, 8.5**

  - [x] 1.6 Add the category label to `frontend/src/locales/fr.json` and `en.json`
    - `admin.database.category.safety-pre-reset`: "Sécurité avant purge" / "Safety before purge"
    - _Requirements: 8.5_

  - [x] 1.7 Show and restore the new category in `frontend/src/components/admin/BackupRestoreSection.vue`
    - Rows and cards render the `forfait` badge and label for `safety-pre-reset` (same fields and actions in table and card views); no source line for this category
    - "Restaurer…" works on a `safety-pre-reset` backup through the existing restore panel (phrase `RESTAURER LA BASE` unchanged)
    - _Requirements: 8.5, 8.10_

- [x] 2. Reset service `functions/shared/reset_service.py`
  - [x] 2.1 Move shared test fixtures and helpers out of `test_database_backup_restore.py`
    - Create `tests/integration/conftest.py` with the fixtures `reset_backup_clients` (autouse) and `backup_bucket` moved from `test_database_backup_restore.py`, plus the new fixture `cognito_pool` (moto pool, `admins` group, helper to add users with `Username=<sub>`, sets `USER_POOL_ID`)
    - Create `tests/integration/backup_helpers.py` with the plain helpers `clear_table`, `put_typed_items`, `items_by_key`, `table_state`, `utc`, `ADMIN_USER` (follow the import style of the other integration tests; verify the import path works)
    - `test_database_backup_restore.py` imports them instead of defining them; behaviour unchanged and the whole file stays green (`make test-backend-one TEST=tests/integration/test_database_backup_restore.py`)
    - _Requirements: 13.1 (shared test infrastructure for the reuse of the Backup_Service)_

  - [x] 2.2 Implement purge sets, rules, classification, closure and counts
    - `CONFIRMATION_PHRASE = "PURGER LA BASE"`, `ADMINS_GROUP = "admins"`, `PURGE_SETS` (six ids with label and key rules; `crew` uses `CREW#*`; `audit_logs` lists the five `AUDIT#` partitions), `PURGE_ORDER = (payments, boats, crew, temp_access, managers, audit_logs)`, `DEPENDENCIES`
    - `classify(pk, sk)`: first matching set, `None` for Protected_Data (`CONFIG`, `RACE`, `CLUB`, `AUDIT#DATABASE_BACKUP`) and for keys matching no rule; `CREW_MEMBER#` is not `crew`
    - `resolve_closure(ids)`; `compute_item_counts()` (one `backup_service.scan_table()`, returns `(counts, cognito_accounts_max)` with `cognito_accounts_max` = number of `USER#<sub>` / `PROFILE` items)
    - New error classes as subclasses of `backup_service.BackupError`: `InvalidSelection` (400), `BackupRequired` (400), `PreResetBackupFailed` (500), `ResetPartial` (500); reuse `InvalidConfirmation`
    - _Requirements: 2.3, 2.4, 2.5, 4.1, 4.2, 4.3, 5.1, 5.3, 13.4_

  - [x] 2.3 Write tests for classification, closure and counts in `tests/integration/test_database_reset.py`
    - Create the file using the shared fixtures; add a `reset_table` helper seeding one item of every key kind (several `TEAM#` owners, `CREW_MEMBER#` decoy, backup audit records, items matching no rule) after `clear_table`
    - `test_classify_keys` (every key kind, decoys, Protected_Data returns `None`) and `test_rules_are_disjoint`
    - `test_closure_all_subsets` (64 subsets: contains the subset, idempotent, exactly the Dependency_Rules)
    - `test_counts_match_seed` (counts equal an independently tallied seed, no `AUDIT#DATABASE_BACKUP` in `audit_logs`, `cognito_accounts_max`)
    - **Property 1: Classification is disjoint and never touches protected data**
    - **Property 2: Dependency closure (backend part)**
    - **Property 3 (counts part): Purge deletes exactly the selected sets and reports exact counts**
    - **Validates: Requirements 2.3, 2.4, 2.5, 4.1, 4.2, 4.3, 5.3, 7.1**

  - [x] 2.4 Implement request validation in `reset_service.py`
    - `validate_request(body) -> (sets, delete_cognito, backup_before)` in the fixed order: phrase (exact, restore phrase rejected, non-JSON or missing body gives `INVALID_CONFIRMATION`), selection (list, non-empty, known ids, closed under `DEPENDENCIES`; `details.missing` / `details.unknown`), Cognito flag (only with `managers`), backup rule (`os.environ['ENVIRONMENT'] == "prod"` and `backup_before is False` gives `BACKUP_REQUIRED`; a missing field is `true`; the request never supplies the environment)
    - No backup is taken and nothing is deleted for any rejected request
    - _Requirements: 4.7, 4.8, 4.9, 6.13, 8.8, 9.8, 9.9, 9.10, 13.3_

  - [x] 2.5 Write tests for validation in `tests/integration/test_database_reset.py`
    - `test_invalid_selection_rejected` (empty, unknown id, each non-closed subset with `details.missing`, non-list, Cognito without `managers`) and `test_selection_accepted_iff_closed` (all 64 subsets)
    - `test_wrong_phrase_rejected` (empty, lowercase, trailing space, missing, non-JSON body, restore phrase `RESTAURER LA BASE`)
    - `test_prod_backup_rule` (environment in {prod, dev} x `backup_before` in {true, false, missing} x a misleading `environment` field in the body): `prod` with `false` is `BACKUP_REQUIRED`
    - In every rejected case: no S3 object, no native backup, table unchanged
    - **Property 4: Invalid selections are rejected without effect**
    - **Property 5: Only the exact confirmation phrase authorizes a purge**
    - **Property 7: Production requires the backup, decided server-side**
    - **Validates: Requirements 4.7, 4.8, 4.9, 6.13, 8.8, 9.8, 9.9, 9.10, 13.3**

  - [x] 2.6 Implement `execute_reset(body, user)` (without the Cognito step)
    - Ordered algorithm: validate, Pre_Reset_Backup through `backup_service.create_backup(CATEGORY_RESET, user)` when enabled (or forced in prod), one scan and classification into `keys_by_set` (collect the `managers` subs), deletion per set in `PURGE_ORDER` in chunks of 25 with `backup_service.batch_write_with_retry` (counts added per successful chunk), audit, `PurgeResult` (`sets`, `deleted`, `total_deleted`, `cognito`, `pre_reset_backup` or `null`, `audit_written`, `duration_ms`)
    - Backup failure: `PRE_RESET_BACKUP_FAILED` with `details.failed_artifact` (`json` or `aws_native`) and `database_modified: false`, no item deleted
    - Failure during deletion: one top-level catch, an audit record with `outcome: "partial"` first, then `RESET_PARTIAL` with `details = {stage, deleted, pre_reset_backup_id, cognito: "not_attempted"}`; the Cognito step is not run
    - Audit `reset_database` via `backup_service.write_audit` AFTER the purge with `outcome`, `sets` (implied included), `deleted`, `delete_cognito`, `cognito_deleted`, `cognito_failed`, `backup_taken`, `pre_reset_backup_id`, `environment`; an audit failure is logged and gives `audit_written: false`
    - Unexpected error before deletion: `INTERNAL_ERROR` without stack trace and `database_modified: false`; no boat number counter is created or updated
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8.1, 8.2, 8.3, 8.9, 8.12, 10.1, 11.2, 11.4, 12.1, 12.2, 12.7_

  - [x] 2.7 Write tests for execution in `tests/integration/test_database_reset.py`
    - `test_purge_scope_and_counts` (selections: default, all, each set alone with its closure, everything except `audit_logs`): remaining items equal before minus selected sets, Protected_Data and unselected sets unchanged, `deleted[set]` equals the Item_Count before the purge
    - `test_backup_taken_before_first_delete` (the `safety-pre-reset` JSON object and native backup exist, with an item set equal to the pre-purge table, before the first delete is issued) and `test_backup_failure_aborts` (JSON fails, native fails: `PRE_RESET_BACKUP_FAILED` naming the artifact, table unchanged)
    - `test_dev_purge_without_backup` (`backup_before: false` in dev returns `pre_reset_backup: null`, audit `backup_taken: false`)
    - `test_partial_failure_at_each_set` (inject a `batch_write_item` failure while deleting each set): `RESET_PARTIAL` with stage, counts reached, backup id, an audit record with outcome `partial`, no Cognito call; then restoring the pre-reset backup returns the original item set
    - `test_audit_record_fields` (sets with implied, per-set counts, Cognito flag and counts, backup id, admin identity, UTC timestamp, written after the purge) and `test_backup_audit_history_preserved` (every `AUDIT#DATABASE_BACKUP` record present before is present after, including when `audit_logs` is selected)
    - **Property 3: Purge deletes exactly the selected sets and reports exact counts**
    - **Property 6: The Pre_Reset_Backup precedes deletion and its failure aborts the purge**
    - **Property 10: Partial failure reports what was done and stops before Cognito**
    - **Property 11: Every purge is audited and the backup history is preserved**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 7.1, 7.2, 7.3, 7.4, 7.6, 7.7, 7.8, 7.9, 8.1, 8.2, 8.3, 8.9, 8.12, 11.2, 12.1, 12.2**

  - [x] 2.8 Implement the Cognito step in `reset_service.py`
    - `delete_cognito_accounts(subs) -> dict` (lazy boto3 client from `USER_POOL_ID`, injectable in tests): runs only after every DynamoDB deletion succeeded; per account `AdminListGroupsForUser`, skip members of `admins` (`skipped_admins`), else `AdminDeleteUser`; `UserNotFoundException` counts as `not_found`; any other error (including a failed group check, fail closed) is recorded in `failed` as `{sub, code}` and the loop continues
    - Wire it into `execute_reset` and the result (`cognito: {requested, deleted, skipped_admins, not_found, failed}`; zeros and `requested: false` when the option is unchecked); `cognito_deleted` and `cognito_failed` go in the audit record
    - _Requirements: 6.6, 6.7, 6.9, 6.10, 6.11, 7.5, 11.3_

  - [x] 2.9 Write tests for the Cognito step in `tests/integration/test_database_reset.py`
    - `test_cognito_deletion` with `cognito_pool`: team managers deleted, admins (`admins` group) skipped and still present, a ghost profile without Cognito account counted as `not_found`, an injected `admin_delete_user` failure for chosen subs reported in `failed` while the rest are processed, a failing group check skips the account and reports it, option unchecked deletes nothing
    - `test_cognito_runs_after_dynamodb` (no Cognito call happens when a DynamoDB deletion failed)
    - **Property 9: Cognito deletion rules**
    - **Validates: Requirements 6.6, 6.7, 6.9, 6.10, 6.11, 11.3**

  - [x] 2.10 Implement the adapters `handle_counts` and `handle_reset`
    - Both go through `backup_service._run` so the error classes map to `error_response(status, code, message, details)`
    - `handle_counts(event, user)`: `200` `{environment, backup_required, counts, cognito_accounts_max}` with `environment` read from `ENVIRONMENT` and `backup_required = (environment == "prod")`
    - `handle_reset(event, user)`: parse the JSON body (missing or invalid gives `INVALID_CONFIRMATION` / 400, never a 500), call `execute_reset`, return `PurgeResult`
    - _Requirements: 1.1, 2.3, 8.6, 10.1, 12.6, 12.7, 13.1, 13.3_

  - [x] 2.11 Write tests for the adapters in `tests/integration/test_database_reset.py`
    - `GET` payload (`environment`, `backup_required` true only in prod, counts, `cognito_accounts_max`); `POST` success envelope matches the `PurgeResult` model; error envelopes carry the right code, status and `details`; no stack trace in any error body
    - **Property 3 (counts part): Purge deletes exactly the selected sets and reports exact counts**
    - **Property 7: Production requires the backup, decided server-side (`backup_required`)**
    - **Validates: Requirements 2.3, 8.6, 10.1, 12.6, 12.7, 13.3**

- [x] 3. Routing on the existing Lambda
  - [x] 3.1 Add two entries to `ROUTES` in `functions/admin/manage_backups.py`
    - `('GET', '/admin/reset'): reset_service.handle_counts`, `('POST', '/admin/reset'): reset_service.handle_reset`; `@require_admin` already wraps the handler, admin identity from claims as for the backup routes
    - _Requirements: 1.1, 1.2, 13.4_

  - [x] 3.2 Write handler tests in `tests/integration/test_database_reset.py`
    - `test_non_admin_rejected` parametrized over `GET` and `POST /admin/reset`: 403 and no S3 object, native backup, table item or Cognito account changed (`event['resource']` set explicitly, `groups` without `admins`)
    - `test_handler_routes_reset`: `GET` then `POST` through `lambda_handler` with `resource='/admin/reset'` using the admin event pattern of `test_admin_api.py`; the five existing `/admin/backups` routes still route (unchanged behaviour), an unknown route is still 404
    - **Property 12: Non-admin requests are rejected without effect**
    - **Validates: Requirements 1.1, 1.2, 13.4**

- [x] 4. CDK infrastructure in `infrastructure/stacks/api_stack.py`
  - [x] 4.1 Add `/admin/reset` and the IAM statement
    - `admin_resource.add_resource('reset')` with `GET` and `POST` on the existing `manage_backups_integration` (same `add_method` arguments as the backups routes: Cognito authorizer, `AuthorizationType.COGNITO`); CORS preflight comes from the API-level default
    - `manage_backups_function.add_to_role_policy(iam.PolicyStatement(actions=['cognito-idp:AdminDeleteUser', 'cognito-idp:AdminListGroupsForUser'], resources=[self.auth_stack.user_pool.user_pool_arn]))` on the ManageBackups role ONLY, not in the shared statement of `_create_lambda_function`
    - No new Lambda, bucket, layer or table
    - _Requirements: 1.1, 6.6, 6.7, 13.1_

- [x] 5. Checkpoint - Backend and infrastructure
  - Run `cd infrastructure && make test-backend`; it must be green (including `test_database_backup_restore.py` after the fixture move)
  - Run `make synth ENV=dev` and review the output (the project has no CDK tests): two methods (GET, POST) plus the OPTIONS preflight on `/admin/reset`, still the single ManageBackups Lambda, exactly one added IAM statement limited to `AdminDeleteUser` and `AdminListGroupsForUser` on the user pool ARN, no other role changed
  - Recount the resources of the Api stack template (for example by counting the `Resources` entries of `cdk.out/ImpressionnistesApi-dev.template.json`). Expected 488 of 500 (480 + 1 resource + 3 methods + 4 permissions, minus nothing). Report the REAL number. If it is above about 495, apply the design fallback (single `POST /admin/reset` with `{"dry_run": true}` for the counts, saving 3 resources) and adapt tasks 2.10, 3.1, 4.1 and 7.3
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Command-line tools and Makefile
  - [x] 6.1 Create `scripts/database/purge_database.py`
    - `sys.path.insert(0, <repo>/functions/shared)` then `import reset_service` (no Lambda layer needed); `configure_environment(env)` sets `ENVIRONMENT`, `TABLE_NAME=impressionnistes-registration-{env}`, `BACKUP_BUCKET=rcpm-impressionnistes-backups-{env}`, `AWS_DEFAULT_REGION=eu-west-3`, `USER_POOL_ID` (CloudFormation output `UserPoolId` of `ImpressionnistesAuth-{env}`, same method as `delete_team_manager.py`)
    - Arguments `--env`, `--sets a,b` (default `boats`), `--delete-cognito`, `--dry-run`, `--backup-only`
    - Flow: resolve the closure with `resolve_closure` and print the sets added; print the Item_Count of each set of the selection; with `--dry-run` stop there (no backup, no deletion, no Cognito, no audit); otherwise the operator types `PURGER LA BASE` (a different text takes no backup and deletes nothing) and the script calls `reset_service.execute_reset(body, cli_user)` with the typed phrase, so validation, prod backup rule, backup, purge, Cognito exclusion, partial handling and audit are the same code as the Lambda
    - `--backup-only`: `backup_service.create_backup(CATEGORY_RESET, cli_user)` and print the id
    - User identity `{"user_id": "cli", "email": "cli:<os user>"}`; shebang, executable bit, no real AWS call at import time
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9, 14.10, 14.11, 14.12_

  - [x] 6.2 Add the Makefile targets in `infrastructure/Makefile`
    - `db-purge ENV= SETS=boats DELETE_COGNITO=0 DRY_RUN=0`: in prod and not a dry run, ask `Type 'PURGE PROD' to confirm` (same pattern as `DEPLOY PROD`), then run `purge_database.py` with `$(PYTHON)`
    - Alias `delete-all-data-keep-managers`: `$(MAKE) db-purge SETS=crew,temp_access,audit_logs` (keeps `managers`; `crew` implies boats and payments)
    - `db-reset` corrections: first step `purge_database.py --env $(ENV) --backup-only` and the target stops if it fails; the confirmation prompt becomes typed `PURGER LA BASE` (replaces `RESET`); the final summary runs `aws dynamodb query ... --select COUNT` on `PK = RACE` and prints the real race count (the hardcoded "42" is removed from the warning and the summary); purpose unchanged (delete `TEAM#`/`USER#`/`CONFIG` then `reinit_config.py`, `AUDIT#DATABASE_BACKUP` untouched)
    - Add the targets to `make help`; check with `make -n db-purge ENV=dev DRY_RUN=1` and `make -n delete-all-data-keep-managers ENV=dev` that the commands resolve (dry print only)
    - _Requirements: 14.1, 14.6, 14.9, 14.16, 14.17, 14.18, 14.19, 14.20_

  - [x] 6.3 Delete the old script and update references
    - Delete `scripts/database/delete_all_data_keep_team_managers.py` (replaced by `purge_database.py` + `make db-purge`)
    - Update `scripts/database/README.md`: remove the old script, document `purge_database.py` and `delete_admin.py` (purpose, usage, prerequisites, examples) as the script-organization rule requires
    - Search the repository (`grep_search`) for every other reference to `delete_all_data_keep_team_managers` and `delete-all-data-keep-managers` (Makefile, docs, scripts README, specs excluded) and update it
    - _Requirements: 14.1, 14.13, 14.14, 14.15, 14.16_

  - [x] 6.4 Make `scripts/database/delete_team_manager.py` refuse admin accounts
    - Add a small `is_admin(cognito, pool_id, username)` function (`admin_list_groups_for_user`, `admins` in the groups) reused by `delete_admin.py`
    - After the Cognito lookup and before any DynamoDB deletion: if the account is an admin, print the refusal and `sys.exit(1)`; nothing is deleted
    - _Requirements: 14.21_

  - [x] 6.5 Create `scripts/database/delete_admin.py`
    - Ordered checks, each stopping without modification: account exists (`admin_get_user`, else report), member of `admins` (else refuse and point to `delete-team-manager`), more than one member of `admins` (`list_users_in_group`, paginated; else refuse: last admin), print email, groups and environment, the operator types the email exactly (mismatch: no backup, nothing done)
    - `WITH_PROFILE=1` only: `backup_service.create_backup(CATEGORY_RESET, cli_user)` (failure aborts before any deletion), then query `PK = USER#<sub>` and delete the `PROFILE` and `CONSENT#...` items in chunks of 25; then `admin_delete_user`; default (no `WITH_PROFILE`) deletes only the Cognito account and leaves the Admin_Profile_Items
    - `backup_service.write_audit("delete_admin", cli_user, {sub, email, environment, profile_deleted, profile_items_deleted, pre_reset_backup_id})` (an audit failure prints a warning); final report: account deleted, items deleted, backup id
    - Logic in importable functions (`main` guarded by `__name__`); the page offers no admin deletion action
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8, 15.10, 15.11, 15.12, 15.13, 15.14, 15.15, 15.16_

  - [x] 6.6 Add `cognito-delete-admin` to `infrastructure/Makefile`
    - `cognito-delete-admin EMAIL= ENV= WITH_PROFILE=0`: requires `EMAIL`; in prod asks `DELETE ADMIN PROD` before running `delete_admin.py` (in addition to the typed email of the script); passes `--with-profile` when `WITH_PROFILE=1`; listed in `make help`; check with `make -n cognito-delete-admin EMAIL=x@y.z ENV=dev`
    - _Requirements: 15.1, 15.9, 15.10, 15.11_

  - [x] 6.7 Write tests for `purge_database.py` in `tests/integration/test_database_reset_scripts.py`
    - Create the file; load the scripts with `importlib` from `scripts/database`; reuse the shared fixtures; no real AWS
    - `test_cli_resolves_closure` (`--sets` values, default `boats` plus `payments`), `test_cli_dry_run_changes_nothing` (table, backup bucket, native backups, Cognito users and audit records unchanged; no backup taken), typed phrase mismatch takes no backup and deletes nothing, `--backup-only` creates a `safety-pre-reset` backup and nothing else, the CLI audit record has the same fields as the Lambda's and identity `cli:`, prod without backup is refused (`BACKUP_REQUIRED`), the alias set list `crew,temp_access,audit_logs` keeps `managers`
    - **Property 14: The CLI applies the same rules and a dry run changes nothing**
    - **Property 5 (CLI part): Only the exact confirmation phrase authorizes a purge**
    - **Validates: Requirements 14.2, 14.3, 14.4, 14.5, 14.6, 14.9, 14.10, 14.11, 14.12, 14.16**

  - [x] 6.8 Write tests for `delete_team_manager.py` and `delete_admin.py`, then run the backend suite
    - Extend `tests/integration/test_database_reset_scripts.py` with `mock_cognitoidp`
    - `test_delete_team_manager_refuses_admin` (admin account: exit non-zero, no Cognito or table deletion; a plain team manager is still deleted)
    - `test_delete_admin_guards` parametrized: unknown email, account not in `admins` (message points to `delete-team-manager`), last remaining admin, typed email different, backup failure with `WITH_PROFILE=1`: no Cognito account, no table item deleted, no `delete_admin` audit record, no backup when the typed email differs
    - `test_delete_admin_default_keeps_profile` (only the Cognito account is deleted, profile and consent items remain) and `test_delete_admin_with_profile` (backup taken first, `PROFILE` and `CONSENT#` items deleted, then the Cognito account, audit fields `sub`, `email`, `environment`, `profile_deleted`, `pre_reset_backup_id`)
    - Run `cd infrastructure && make test-backend` and make it green
    - **Property 14: delete_team_manager refuses admin accounts**
    - **Property 15: Admin deletion guards leave everything untouched**
    - **Validates: Requirements 14.21, 15.3, 15.4, 15.5, 15.8, 15.10, 15.11, 15.12, 15.13, 15.14, 15.15, 15.16**

- [x] 7. Frontend
  - [x] 7.1 Create `frontend/src/utils/resetRules.js`
    - Export `PURGE_SET_IDS` (UI order), `DEPENDENCIES`, `DEFAULT_SELECTION = ['boats']`, `CONFIRMATION_PHRASE`, `closure(ids)`, `requiredBy(id, selection)` (selected sets that imply `id`), `isPhraseValid(text)` (exact, case-sensitive); values identical to `reset_service.py`
    - _Requirements: 3.1, 3.2, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 9.1_

  - [x] 7.2 Write `frontend/src/utils/resetRules.test.js`
    - Table-driven: `closure` for all 64 subsets (against an expected table written explicitly), idempotence, `requiredBy`, `isPhraseValid` (exact match only: case, whitespace, empty, the restore phrase), default selection
    - **Property 2: Dependency closure (frontend part)**
    - **Validates: Requirements 3.1, 3.2, 4.1, 4.2, 4.3, 4.5, 4.6, 9.1**

  - [x] 7.3 Create `frontend/src/composables/useDatabaseReset.js`
    - Reuse `services/apiClient`; same structure as `useBackupRestore.js`; expose `state`, `busyLabel`, `counts`, `environment`, `backupRequired`, `cognitoAccountsMax`, `chosen`, `effective`, `locked`, `cognitoOption`, `backupBefore`, `phrase`, `result`, `error`, `load`, `toggle`, `selectAll` ("Tout purger"), `setPhrase`, `purge`, `dismiss`
    - 6 states `idle | busy | ready_to_purge | success | error | partial`; transitions only inside the composable, per the design diagram; `ready_to_purge` is entered from `idle` or `error` on the first change
    - On load: `chosen = ['boats']`, `payments` locked with the orphaned-payments message, empty phrase, Cognito unchecked and hidden unless `managers` is effective (reset to unchecked when it leaves `effective`; "Tout purger" leaves it unchecked), backup checked (checked and locked when `backupRequired`)
    - Enabled-actions table from the design per state; Purger disabled unless the phrase is valid, the effective selection is non-empty and the backup section is not busy (`externalBusy`); `busy` disables everything; in `partial` the selection is frozen
    - Exported `nextStateFromResetError(err)`: `RESET_PARTIAL` gives `partial`; any other envelope code gives `error` with the translated message; no `err.response`, `ECONNABORTED`, HTTP 401 or 504, non-envelope body gives `error` with the outcome-unknown message
    - On success reload the counts; expose the Pre_Reset_Backup id for the "Restaurer cette sauvegarde" action
    - _Requirements: 2.3, 2.6, 2.7, 2.8, 2.9, 3.1, 3.2, 3.4, 3.5, 4.4, 4.5, 6.1, 6.2, 6.3, 8.6, 8.7, 9.2, 9.3, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 11.7, 12.3, 12.6_

  - [x] 7.4 Write `frontend/src/composables/useDatabaseReset.test.js`
    - Mock `apiClient`; locking and unlocking over sequences of checks and unchecks (locked sets are exactly `closure(chosen) \ chosen`, unlock after unchecking), "Tout purger", Cognito visibility and reset, backup lock in prod and uncheck in dev, every transition of the 6-state diagram, enabled-actions table per state, Purger disabled with a wrong phrase, empty selection or busy backup section, counts load failure keeps Purger disabled
    - Table-driven `nextStateFromResetError`: `RESET_PARTIAL`, `INVALID_SELECTION`, `INVALID_CONFIRMATION`, `BACKUP_REQUIRED`, `PRE_RESET_BACKUP_FAILED`, `ECONNABORTED`, 401, 504, no response, non-envelope body
    - **Property 2: Dependency closure (UI locking)**
    - **Property 13: UI action availability and error classification**
    - **Validates: Requirements 2.7, 2.8, 2.9, 4.4, 4.5, 6.1, 6.2, 6.3, 9.2, 9.3, 10.3, 10.4, 10.5, 10.6, 10.7, 12.3, 12.6**

  - [x] 7.5 Add the reset i18n keys to `frontend/src/locales/fr.json` and `en.json`
    - `admin.database.reset.*`: title, six set labels and descriptions, "Tout purger", the orphaned-payments message and "requis par {labels}", Cognito option label "Supprimer aussi les comptes de connexion (Cognito)" with the irreversibility, restore-does-not-restore-Cognito, admin-exclusion and "can still log in without a profile" warnings, the modal texts (summary, "impliqué" mark, kept sets and Protected_Data "Configuration", "Courses", "Clubs", "Historique des sauvegardes", Cognito count as "jusqu'à N comptes" with the irreversible and admins-excluded statements), backup option (prod lock explanation, "la purge ne pourra pas être annulée"), state banners, the "Rien n'a été modifié dans la base" and outcome-unknown messages, the "ÉTAT PARTIEL : la purge n'est pas terminée" banner and recovery texts (including "aucune sauvegarde de pré-purge: restauration impossible"), result texts (counts, Cognito result, boat numbering restarts, "Restaurer cette sauvegarde"), and the next-edition reminder (registration dates, payment deadline, competition date; nothing changed automatically)
    - `admin.database.errors.<CODE>` for `INVALID_SELECTION`, `INVALID_CONFIRMATION`, `BACKUP_REQUIRED`, `PRE_RESET_BACKUP_FAILED`, `RESET_PARTIAL`, `INTERNAL_ERROR`
    - Remove the obsolete `reset.placeholder*` keys; the Confirmation_Phrase is interpolated, not translated
    - _Requirements: 2.1, 2.2, 3.3, 5.6, 5.7, 6.4, 6.5, 6.8, 6.12, 8.10, 8.11, 8.12, 9.5, 9.6, 9.7, 10.6, 10.7, 11.5, 11.6, 12.3, 12.5, 12.6_

  - [x] 7.6 Create `DatabaseResetSection.vue` and `DatabaseResetResultPanel.vue` in `frontend/src/components/admin/`
    - `DatabaseResetSection.vue`: State_Banner, one `DataCard` per set with a native checkbox in a label (the project has no checkbox component), description, Item_Count, lock text "requis par {labels}"; "Tout purger"; Cognito option (rendered only when `managers` is effective); backup option; phrase `FormGroup`; Purger… button (`danger`, `medium`); confirmation `BaseModal` (effective sets with count and "impliqué" mark, kept sets and Protected_Data, Cognito "jusqu'à N comptes", backup option; Annuler `secondary` / Confirmer `danger`, both `medium`); `MessageAlert` for errors; no purge controls rendered for a non-admin; section header and cards with the bottom-border separator
    - `DatabaseResetResultPanel.vue` (like `RestoreResultPanel.vue`): `success` (per-set counts, Cognito result with deleted, failed sub list, admins skipped and not found, boat numbering message when `boats` was purged, next-edition reminder, Pre_Reset_Backup id with category badge and "Restaurer cette sauvegarde" emitting `restore-backup(id)`, no-undo text without backup, Cognito not restored text), `error` ("Rien n'a été modifié dans la base" or the outcome-unknown instructions), `partial` (prominent banner, counts reached, set being deleted, backup id with the same restore action and a retry action, or the no-backup text)
    - `BaseButton` for every button (`small` in rows and cards, `medium` in the panel and modals), design tokens only, no custom badge or button CSS
    - _Requirements: 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.6, 3.1, 3.2, 3.3, 3.4, 3.5, 4.4, 4.6, 5.6, 5.7, 6.1, 6.4, 6.5, 6.8, 6.12, 8.6, 8.7, 8.10, 8.11, 8.12, 9.1, 9.4, 9.5, 9.6, 9.7, 10.2, 10.3, 10.5, 10.6, 10.7, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 12.3, 12.4, 12.5, 12.8_

  - [x] 7.7 Expose the backup section for the wiring in `frontend/src/components/admin/BackupRestoreSection.vue`
    - `defineExpose({ selectById, reload: load })` (`selectById(id)` selects the row of the backup for restoration; the phrase is still required), prop `externalBusy` (disables every action while the reset section is busy), emit `busy-change` (so the reset section disables Purger while a backup, download, delete or restore is in progress)
    - _Requirements: 8.10, 10.3, 10.4, 12.4_

  - [x] 7.8 Wire the page in `frontend/src/views/admin/AdminDatabaseManagement.vue` and delete the placeholder
    - Replace `DatabaseResetPlaceholder` with `DatabaseResetSection`; template ref on `BackupRestoreSection`; busy flags in both directions (`busy-change` from each section, `externalBusy` on the other)
    - On `restore-backup(id)`: `await backupSection.value.reload()` (the new backup is not in the loaded list), then `backupSection.value.selectById(id)` and scroll to the backup section; after a successful purge call `backupSection.value.reload()`
    - Delete `frontend/src/components/admin/DatabaseResetPlaceholder.vue` and any import of it
    - _Requirements: 1.3, 1.4, 8.10, 10.3, 10.4, 11.7, 12.4_

  - [x] 7.9 Add `test_frontend_backend_reset_rules_aligned` to `tests/integration/test_database_reset.py`
    - Read `frontend/src/utils/resetRules.js` as text (same method as `test_frontend_backend_constants_aligned`) and assert the same set ids, order, dependencies and phrase as `reset_service.py`; assert the i18n error code keys exist for every backend error code
    - **Property 2: Dependency closure (alignment)**
    - **Validates: Requirements 4.1, 4.2, 4.3, 9.1, 14.4**

- [x] 8. Checkpoint - Frontend
  - Run `cd infrastructure && make test-frontend` TWICE (the results must be identical and deterministic), then `make lint-frontend` (0 errors), then `make test` once more for the full suite
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. DEV deployment and verification (manual, performed by the user, not for automated execution)
  - [x] 9.1 Deploy to DEV
    - `cd infrastructure && make deploy-dev`, then `make deploy-frontend-dev`
    - _Requirements: 13.1, 13.2_

  - [x] 9.2 Run the manual verification checklist in DEV
    - Page: counts displayed next to each set; default selection (Équipages checked, Paiements checked and locked with the orphaned-payments message); dependency locks (Équipiers, Team managers) and unlocking; "Tout purger" selects everything and leaves Cognito unchecked; the Cognito option is hidden until Team managers is selected, unchecked, with its warnings; non-admin cannot see the controls
    - Dry run: `make db-purge ENV=dev DRY_RUN=1` prints the counts and changes nothing (`make db-view ENV=dev` before and after)
    - Purge with a pre-reset backup: phrase gate, confirmation modal content ("jusqu'à N comptes"), result counts, next-edition reminder, boat numbering message, `AUDIT#DATABASE_BACKUP` has a `reset_database` record; Protected_Data (`CONFIG`, `RACE`, `CLUB`, backup history) unchanged
    - Undo: "Restaurer cette sauvegarde" selects the `safety-pre-reset` backup (red badge "Sécurité avant purge"), restore with `RESTAURER LA BASE`, the data is back
    - Cognito: purge Team managers with the option on test accounts; the admin account is never deleted; deleted accounts are not restored by the backup restore
    - `make cognito-delete-admin EMAIL=<non-admin> ENV=dev` and `EMAIL=<last admin>` are refused; a throwaway admin is deleted with its typed email
    - _Requirements: 1.3, 2.1, 2.3, 3.1, 3.2, 3.3, 3.4, 3.5, 4.4, 4.5, 5.4, 5.6, 6.1, 6.2, 6.5, 6.7, 7.2, 8.5, 8.10, 9.1, 9.4, 11.1, 11.5, 14.11, 15.4, 15.5_

  - [x] 9.3 Run failure drills in DEV (required)
    - Partial state: provoke a failure during deletion (for example by temporarily removing the Lambda's delete permission or another safe fault on dev) and check the banner "ÉTAT PARTIEL : la purge n'est pas terminée", counts, the restore action and the retry; then restore the pre-reset backup and check the table
    - Outcome unknown: start a purge in DEV, cut the network (browser offline) while it runs, check the outcome-unknown message, restore connectivity, refresh the backup list and check that a new `safety-pre-reset` backup exists and that the data is in the expected state
    - `BACKUP_REQUIRED` cannot be produced from the page (checkbox locked in prod); its server-side rule is covered by the tests
    - _Requirements: 10.6, 10.7, 12.1, 12.2, 12.3, 12.4_

- [ ] 10. PROD rollout (manual, user-driven, only after DEV is validated; not for automated execution)
  - [ ] 10.1 Deploy to PROD
    - `cd infrastructure && make deploy-prod` and `make deploy-frontend-prod` (type the Makefile confirmation prompts)
    - _Requirements: 13.1, 13.3_

  - [ ] 10.2 Verify in PROD without purging
    - Open the page and check the counts and the locked backup option (prod); run `make db-purge ENV=prod DRY_RUN=1` (dry run ONLY)
    - Do NOT run a real purge in PROD without the explicit go-ahead of the user, and never during a registration period; if a purge is decided, take a fresh manual backup first and run it outside registration hours
    - _Requirements: 8.6, 13.1, 14.6, 14.11_

- [x] 11. Documentation and requirements sync (ask the user to confirm before editing, per the `documentation-updates` and `requirements-sync` rules)
  - [x] 11.1 Update `docs/reference/api-endpoints.md` with `GET /admin/reset` and `POST /admin/reset`: request, response (`PurgeResult`), error codes
    - _Requirements: 2.3, 8.8, 10.1, 12.1_

  - [x] 11.2 Add the purge section to the runbook in `docs/guides/operations/`: end-of-edition purge, undo with the `safety-pre-reset` backup, partial-failure recovery, outcome-unknown case, admin deletion, and the scripts
    - _Requirements: 8.10, 10.7, 12.4, 14.1, 15.1_

  - [x] 11.3 Update `docs/reference/commands.md` with `db-purge`, the alias `delete-all-data-keep-managers`, the `db-reset` changes (backup first, typed `PURGER LA BASE`, real race count) and `cognito-delete-admin`
    - _Requirements: 14.1, 14.16, 14.17, 14.18, 14.19, 14.20, 15.1_

  - [x] 11.4 Update `docs/reference/project-structure.md` with `reset_service.py`, `purge_database.py`, `delete_admin.py`, the new components, and update `docs/reference/terminology.md` (purge sets, `safety-pre-reset`)
    - _Requirements: 2.1, 8.3_

  - [x] 11.5 Complete `scripts/database/README.md` (first updated in task 6.3) and add the note of the third Backup_Category in the `database-backup-restore` spec ONLY after user confirmation
    - _Requirements: 14.16_

  - [x] 11.6 Sync `.kiro/specs/impressionnistes-registration-system/requirements.md` with a functional requirement entry for the selective purge, after explicit user confirmation
    - _Requirements: 5.1, 8.1, 9.1_

## Notes

- All test tasks (1.2, 1.4, 1.5, 2.3, 2.5, 2.7, 2.9, 2.11, 3.2, 6.7, 6.8, 7.2, 7.4, 7.9) are required; none is optional and nothing is skipped. A checkpoint passes only when `make test-backend`, `make test-frontend` and `make lint-frontend` are green.
- The correctness properties are covered by explicit parametrized pytest and table-driven vitest cases (no Hypothesis). The 64 subsets of the six sets are enumerated.
- Tasks 9 and 10 are manual and user-driven. They are not for automated execution. The agent never deploys, commits or pushes.
- The agent runs tests itself, only through Makefile targets. If an operation has no target, propose adding one instead of using a raw command.
- Backend files were changed, so remind the user to run `cd infrastructure && make test` at each checkpoint.
- Decisions: in prod a request with `backup_before=false` is rejected with `BACKUP_REQUIRED`; the Cognito count in the confirmation modal is a maximum ("jusqu'à N comptes"), admins are excluded at execution; `delete_all_data_keep_team_managers.py` is replaced by `purge_database.py`, and `make delete-all-data-keep-managers` is kept as an alias.
- Backend/frontend alignment: set ids, dependencies and phrase live in `reset_service.py` and `resetRules.js` (task 7.9); the category and regex live in `backup_service.py` and `backupNaming.js` (task 1.5).
- Documentation and requirements sync (task 11) need explicit user confirmation before any edit.
- The Api stack was at 480 of 500 resources; the expected total is 488. Task 5 reports the real number and applies the design fallback if it is above about 495.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.3", "1.6", "7.1"] },
    { "id": 1, "tasks": ["1.2", "1.4", "1.7", "2.2", "7.2", "7.3", "7.5"] },
    { "id": 2, "tasks": ["1.5", "2.4", "7.4", "7.6", "7.7"] },
    { "id": 3, "tasks": ["2.1", "2.6", "7.8"] },
    { "id": 4, "tasks": ["2.3", "2.8"] },
    { "id": 5, "tasks": ["2.5", "2.10"] },
    { "id": 6, "tasks": ["2.7", "3.1"] },
    { "id": 7, "tasks": ["2.9", "4.1"] },
    { "id": 8, "tasks": ["2.11"] },
    { "id": 9, "tasks": ["3.2"] },
    { "id": 10, "tasks": ["6.1", "6.4", "7.9"] },
    { "id": 11, "tasks": ["6.2", "6.5", "6.7"] },
    { "id": 12, "tasks": ["6.3", "6.6", "6.8"] },
    { "id": 13, "tasks": ["9.1"] },
    { "id": 14, "tasks": ["9.2"] },
    { "id": 15, "tasks": ["9.3"] },
    { "id": 16, "tasks": ["10.1"] },
    { "id": 17, "tasks": ["10.2"] },
    { "id": 18, "tasks": ["11.1", "11.2", "11.3", "11.4", "11.5", "11.6"] }
  ]
}
```
