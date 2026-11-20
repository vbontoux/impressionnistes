# Database Backup & Restore Runbook

Practical guide for admins and operators. Page: **Admin > Gestion de la base** (`/admin/database`), admin-only.

## 1. What a backup contains

Each backup creates two artifacts:

- **JSON backup**: every item of the table `impressionnistes-registration-{env}`, in S3 bucket `rcpm-impressionnistes-backups-{env}` (encrypted, versioned, private). This is what the page lists, downloads and restores.
- **AWS native backup**: DynamoDB on-demand backup. Not listed in the page. Visible with `make db-list-backups`.

### Categories and names

The category is readable from the name alone and shown as a badge:

| Badge | Category | Name format |
|---|---|---|
| Manuelle | `manual` | `manual_<UTC timestamp>.json` |
| Sécurité avant restauration | `safety-pre-restore` | `safety-pre-restore_<UTC timestamp>_before-restore-of_<source>.json` |
| Sécurité avant purge | `safety-pre-reset` | `safety-pre-reset_<UTC timestamp>.json` (see section 8) |

- Timestamp format: `YYYY-MM-DDTHH-MM-SSZ` (UTC).
- Safety backups are created automatically before every restore. The part after `_before-restore-of_` is the **source reference** (category + timestamp of the backup that was about to be restored). The list also shows it as "avant restauration de : ...".

Example: `safety-pre-restore_2026-11-02T09-00-00Z_before-restore-of_manual_2026-11-01T14-30-00Z.json`

## 2. Create, download, delete

- **Create**: click "Créer une sauvegarde". The result shows the id and item count.
- **Download**: "Télécharger" saves the JSON file (off-system copy).
- **Delete**: "Supprimer", then confirm. This removes the **JSON backup only**:
  - the AWS native backup stays;
  - S3 versioning keeps the deleted version recoverable (S3 console, show versions).

## 3. Restore, step by step

Restore is a **full replacement** of the table.

1. In production, restore outside registration hours and create a fresh manual backup first.
2. Click "Restaurer…" on the chosen row.
3. Check the category badge and the item count in the "Restaurer la base" panel.
4. Type `RESTAURER LA BASE` exactly (case-sensitive). The "Restaurer" button stays disabled until it matches.
5. Click "Restaurer", read the modal, then "Confirmer la restauration".
6. Wait (usually under 15 s). Do not close the page.

What happens: safety backup (JSON + native) is created, the table is purged, the backup is written, the count is verified, an audit record is written.

### What is replaced and what is kept

| Data | Result |
|---|---|
| `AUDIT#DATABASE_BACKUP` (backup/restore/delete history) | **Kept**, merged with the audit records in the backup |
| All other data, including other `AUDIT#` partitions | **Fully replaced** by the backup content |
| Cognito accounts | **Not touched** (admin access comes from Cognito groups, so you cannot lock yourself out) |

Cognito side effects, because team managers are keyed by their Cognito sub:

- Users registered **after** the backup lose their profile and data (the Cognito account remains).
- Profiles of users **deleted from Cognito** since the backup come back as orphans.

The app may show empty data for a few seconds during a restore.

## 4. Undo a restore

After success, the page shows "Pour annuler cette restauration" with the safety backup. Click "Annuler cette restauration", type the phrase, confirm. The safety backup is restored (and itself produces a new safety backup). Audit history of both restores is kept.

## 5. Partial failure (`RESTORE_PARTIAL`)

The page shows "ÉTAT PARTIEL : la base est incomplète" with the safety backup id, the stage reached and the counts.

1. Do not use the application.
2. Click "Restaurer la sauvegarde de sécurité" (type the phrase), or "Réessayer avec la sauvegarde source". A restore is idempotent, so retrying is safe.
3. If it fails again, restore the native backup into a new table (out of band, the live table is not modified):
   ```bash
   cd infrastructure
   make db-restore-backup BACKUP_ARN=<arn> ENV=<env>
   ```
   The result is a table named `...-restored`; inspect it and copy data back or repoint as needed.
4. Last resort: DynamoDB point-in-time recovery (PITR), enabled in dev and prod.

If the failure happened before the purge (for example "La sauvegarde de sécurité a échoué"), the page says "Rien n'a été modifié dans la base."

## 6. Outcome unknown (no response / 504)

The page shows "Résultat inconnu". The restore may still be running: the Lambda runs up to 120 s even if the gateway gave up at about 30 s.

1. Wait about 1 minute.
2. Click "Actualiser".
3. Look for a **new** "Sécurité avant restauration" backup. If present, the restore started.
4. Verify the data (`make db-view ENV=<env>` or the app).
5. If data looks empty or wrong, restore that safety backup. If no new safety backup exists, nothing was changed.

After a session expiry, log back in and do the same checks.

## 7. Checking from the CLI

```bash
cd infrastructure
make db-list-backups ENV=<env>   # native backups (incl. those created by this feature)
make db-view ENV=<env>           # table contents and item count
```

Native backups are named `{table}-{category}_{timestamp}`.

## 8. End-of-edition purge

Same page (**Admin > Gestion de la base**), section "Purge de la base". It deletes the data of the previous edition and keeps everything else. Admin-only. Technical rules live in `functions/shared/reset_service.py` (the admin page and the CLI use the same code).

**Never purged**: configuration (`CONFIG`), races, clubs, and the backup history (`AUDIT#DATABASE_BACKUP`).

### Data sets

| Set (page label) | Id | Content |
|---|---|---|
| Équipages | `boats` | Boat registrations (seats, paid status, boat number, rental request) |
| Paiements | `payments` | Stripe payment history |
| Équipiers | `crew` | Crew members (rowers and coxswains) |
| Team managers | `managers` | Team manager profiles and GDPR consents |
| Accès temporaires | `temp_access` | Temporary accesses granted to users |
| Journaux d'audit | `audit_logs` | Permission and temporary-access audit logs |

### Dependency locks

Purging a set also requires purging the sets that depend on it:

| If checked | Also required |
|---|---|
| Équipages | Paiements |
| Équipiers | Équipages, Paiements |
| Team managers | Équipages, Paiements, Équipiers, Accès temporaires |

A set is **locked** (checked, "requis par ...", "impliqué") as soon as another checked set requires it. It is **unlocked** again when that set is unchecked. "Tout purger" checks every set. The server rejects a selection that is not closed under these rules (`INVALID_SELECTION`).

### Step by step

1. In production, purge outside registration hours. Read the item counts shown next to each set.
2. Default selection: **Équipages + Paiements** ("Paiements" is checked automatically, to avoid orphaned payments). Adjust the sets.
3. **Cognito option**: appears only when "Team managers" is checked, **unchecked by default**. If checked, the Cognito accounts of the purged team managers are deleted (irreversible). **Admins are never deleted**: members of the `admins` group are skipped.
4. **Backup**: "Créer une sauvegarde complète avant la purge" is checked by default. In **production it is mandatory** and cannot be unchecked (decided by the server, `BACKUP_REQUIRED` otherwise). In dev it can be unchecked, but the purge then cannot be undone.
5. Type `PURGER LA BASE` exactly (case-sensitive; the restore phrase is refused). Click "Purger…", read the modal, then "Confirmer la purge".
6. Wait (usually under 30 s). Do not close the page.

What happens: backup `safety-pre-reset` (JSON + native), deletion set by set, then Cognito accounts (only if every deletion succeeded), then an audit record `reset_database`. If the backup fails (`PRE_RESET_BACKUP_FAILED`), nothing is deleted.

The result lists the items deleted per set and the Cognito outcome (deleted, admins skipped, not found, failed). No event configuration is changed: update the registration dates, the payment deadline and the competition date in the event configuration for the next edition.

### License verifications

License verification fields live on the **crew items**. They are kept if only Équipages (and Paiements) is purged, and deleted with Équipiers.

### Undo a purge

The result shows "Pour annuler cette purge" with the `safety-pre-reset` backup (badge "Sécurité avant purge", red).

1. Click "Restaurer cette sauvegarde".
2. Type `RESTAURER LA BASE` and confirm (this is a normal restore, see section 3; it creates its own safety backup).
3. If the page was closed, restore the same backup from the backup list ("Restaurer…" on the `safety-pre-reset` row).

**Cognito accounts are not restored by a restore.** If the Cognito option was used, the accounts stay deleted: restored team manager profiles have no login until the managers register again.

### Partial failure (`RESET_PARTIAL`)

The page shows the banner "ÉTAT PARTIEL : la purge n'est pas terminée" with the set being deleted, the counts reached and the `safety-pre-reset` backup id. Cognito accounts were **not** touched.

1. Do not use the application.
2. Either relaunch the purge (a purge is idempotent, and a new backup of the partial state is taken), or restore the `safety-pre-reset` backup.
3. If it keeps failing, restore the native backup into a new table (`make db-restore-backup BACKUP_ARN=<arn> ENV=<env>`, see section 5).

If no backup exists (dev, backup unchecked), only the retry is possible.

### Outcome unknown (no response / 504)

The page shows "Résultat inconnu". The purge may still be running.

1. Wait about 1 minute.
2. Click "Actualiser" on the backup list.
3. Look for a **new** "Sécurité avant purge" backup. If present, the purge started: refresh the counts and check the data (`make db-view ENV=<env>`). If data is incomplete or wrong, restore that backup.
4. If no new backup exists (and the backup was enabled), nothing was changed.

After a session expiry, log back in and do the same checks.

## 9. Delete an admin account

Not available on the page. Command line only:

```bash
cd infrastructure
make cognito-delete-admin EMAIL=admin@example.com ENV=<env>                  # Cognito account only
make cognito-delete-admin EMAIL=admin@example.com WITH_PROFILE=1 ENV=<env>   # also profile and consents
```

Checks, in order. Any failure stops the command with nothing modified:

1. The account exists.
2. It is a member of `admins` (otherwise use `make delete-team-manager`, which refuses admin accounts).
3. It is **not the last admin** (at least two admins are required).
4. You type the admin's email exactly.
5. In production, the Makefile also asks `DELETE ADMIN PROD`.

By default only the Cognito account is deleted; the `PROFILE` and `CONSENT#` items stay in the table. With `WITH_PROFILE=1`, a `safety-pre-reset` backup is taken first (a backup failure aborts), then the profile and consent items, then the Cognito account. A `delete_admin` audit record is written.

## 10. Purge from the CLI (fallback)

Use when the page is unavailable. Same rules, same code, same audit record (identity `cli:<user>`).

```bash
cd infrastructure
make db-purge ENV=dev SETS=boats DRY_RUN=1                       # counts only, nothing modified
make db-purge ENV=dev SETS=crew,temp_access
make db-purge ENV=prod SETS=boats DELETE_COGNITO=1
```

- `SETS`: comma-separated ids from the table above (default `boats`). Implied sets are added and printed before confirmation.
- `DELETE_COGNITO=1`: delete Cognito accounts (needs `managers`; admins are skipped).
- `DRY_RUN=1`: prints the counts, takes no backup, deletes nothing, writes no audit record.
- Confirmation: in prod the Makefile asks `PURGE PROD` (skipped for a dry run), then the script asks `PURGER LA BASE`. Any other text takes no backup and deletes nothing.
- A `safety-pre-reset` backup is taken (mandatory in prod). Undo it from the page (see "Undo a purge").
- Alias `make delete-all-data-keep-managers ENV=<env>`: purges `crew`, `temp_access` and `audit_logs` (with the implied boats and payments) and **keeps the team managers**.
- `make db-reset ENV=<env>` is a full reset to the initial state (not selective): it first takes a `safety-pre-reset` backup (the target stops if it fails), asks `PURGER LA BASE`, deletes all `TEAM#` and `USER#` data, then recreates the default configuration. Races and the backup history are kept; the final summary prints the real race count.

## 11. Limits

- Synchronous design sized for the current table (~1 250 items, ~630 KB). A restore takes about 8-10 s.
- Revisit (asynchronous job) above ~10 000 items / 5 MB, or if a restore takes more than 15 s.
- Downloads are returned in the API response; revisit above ~4 MB.
- No lock between admins: only one admin should run a restore at a time.
- If you add a DynamoDB Streams consumer, make it idempotent or disable it before restoring.
- The backup bucket is retained on stack teardown; empty and delete it manually before redeploying with the same name.
