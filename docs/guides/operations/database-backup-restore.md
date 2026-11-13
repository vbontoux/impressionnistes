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

## 8. Limits

- Synchronous design sized for the current table (~1 250 items, ~630 KB). A restore takes about 8-10 s.
- Revisit (asynchronous job) above ~10 000 items / 5 MB, or if a restore takes more than 15 s.
- Downloads are returned in the API response; revisit above ~4 MB.
- No lock between admins: only one admin should run a restore at a time.
- If you add a DynamoDB Streams consumer, make it idempotent or disable it before restoring.
- The backup bucket is retained on stack teardown; empty and delete it manually before redeploying with the same name.
