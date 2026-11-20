# Database Scripts

Database management utilities and one-time migrations for DynamoDB.

## Categories

### 📊 Export & Analysis
- `export-db.py` - Export DynamoDB table to CSV
- `compare_config_details.py` - Compare dev vs prod configurations
- `list_boat_numbers.py` - List all generated boat numbers
- `show_boat_numbers.py` - Show hypothetical boat numbers
- `check_migration.py` - Verify migration results

### 🗑️ Data Management
- `delete_clubs.py` - Delete all clubs from database
- `purge_database.py` - Selective purge of data sets (`make db-purge`), also takes the safety backup for `db-reset`
- `delete_admin.py` - Delete an admin account (`make cognito-delete-admin`)
- `delete_team_manager.py` - Delete team manager and all related data (refuses admin accounts)
- `delete_user_data.py` - Delete the items listed in a JSON file (`delete_user_data.py <table_name> <items_file>`); not called by `db-reset`
- `reinit_config.py` - Reinitialize database configuration (`reinit_config.py <region>`, last step of `db-reset`)

### 🔄 Migrations (One-Time Scripts)
See `MIGRATIONS.md` for detailed migration documentation.

**Migration files:**
- `add_*.py` - Add new features/fields
- `update_*.py` - Update existing data
- `migrate_*.py` - Data transformations
- `delete_*.py` - Remove obsolete data
- `reset_*.py` - Reset specific data

## Common Operations

### Export Database

**Via Makefile (recommended):**
```bash
cd infrastructure
make db-export ENV=dev
```

**Direct execution:**
```bash
python3 scripts/database/export-db.py exports/dynamodb-dev-20260219.json
```

**Output:**
- Single CSV with all data
- Split CSVs by entity type (with `--split`)

---

### Compare Dev vs Prod

```bash
python3 scripts/database/compare_config_details.py
```

**What it compares:**
- Configuration records
- Club records
- Race definitions

**Requirements:**
- AWS credentials for both dev and prod
- Correct AWS profiles configured

---

### Delete Team Manager

**Via Makefile (recommended):**
```bash
cd infrastructure
make delete-team-manager EMAIL=user@example.com ENV=dev
```

**What it deletes:**
- User profile
- All consent records
- All boats and crew registrations
- All crew members
- All payment records
- Cognito user account

**Confirmation:** type `DELETE <email>` (skipped with `--yes` when run directly). No backup is taken.

**Warning:** Permanent deletion! Cannot be undone.

**Admin accounts are refused:** if the account belongs to the Cognito `admins` group, the script exits with an error and deletes nothing. Use `make cognito-delete-admin` instead.

---

### Selective Purge

**Via Makefile (recommended):**
```bash
cd infrastructure
make db-purge ENV=dev SETS=boats DRY_RUN=1                 # preview counts only
make db-purge ENV=dev SETS=crew,temp_access
make db-purge ENV=prod SETS=boats DELETE_COGNITO=1         # asks 'PURGE PROD', then 'PURGER LA BASE'

# Alias: purge crew, temp_access and audit_logs, keep team managers
make delete-all-data-keep-managers ENV=dev
```

**Parameters:** `ENV` (dev/prod), `SETS` (comma list, default `boats`), `DELETE_COGNITO` (`1` to also delete team manager Cognito accounts), `DRY_RUN` (`1` to only report counts).

**Sets:** `payments`, `boats`, `crew`, `temp_access`, `managers`, `audit_logs`.

**Dependency closure:** selecting a set also selects the sets that depend on it (for example `crew` implies `boats` and `payments`). The script prints the sets it added before asking for confirmation.

**Never purged:** `CONFIG`, `RACE`, `CLUB` and the backup history (`AUDIT#DATABASE_BACKUP`).

**Confirmation:**
- Production: the Makefile first asks you to type `PURGE PROD` (skipped with `DRY_RUN=1`).
- All environments: the script asks you to type `PURGER LA BASE`. Any other text takes no backup and deletes nothing.
- `DRY_RUN=1` takes no backup, deletes nothing, writes no audit record.

**What it does:** takes a `safety-pre-reset` backup (always, in every environment; the CLI has no option to skip it), deletes the selected sets, optionally deletes Cognito accounts (members of `admins` are always skipped), then writes a `reset_database` audit record. It uses the same code (`functions/shared/reset_service.py`) as the admin page, so the rules are identical.

**Direct options:** `purge_database.py --env ENV --sets a,b [--delete-cognito] [--dry-run] [--backup-only]` (`--env` is `dev` or `prod`, default `dev`; `--delete-cognito` requires `managers` in the resulting selection). `--backup-only` only creates a `safety-pre-reset` backup and prints its id; `make db-reset` uses it as its first step.

**Prerequisites:** AWS credentials for the target environment, the stacks deployed (the script reads the user pool id from `ImpressionnistesAuth-{env}`).

**Warning:** Permanent deletion! Restore the `safety-pre-reset` backup to undo.

---

### Delete Admin

**Via Makefile (recommended):**
```bash
cd infrastructure
make cognito-delete-admin EMAIL=admin@example.com ENV=dev
make cognito-delete-admin EMAIL=admin@example.com ENV=dev WITH_PROFILE=1
```

**Checks (each stops the script without any change):**
- The account exists.
- The account is a member of `admins` (otherwise use `make delete-team-manager`).
- It is not the last remaining admin.
- You type the exact email when asked.
- Production: the Makefile also asks you to type `DELETE ADMIN PROD`.

**What it deletes:** by default only the Cognito account; the profile and consent items stay in the table. With `WITH_PROFILE=1` it first takes a `safety-pre-reset` backup (a backup failure aborts), then deletes the `PROFILE` and `CONSENT#` items, then the Cognito account. A `delete_admin` audit record is written.

**Direct execution:** `delete_admin.py EMAIL --env ENV [--with-profile]`.

**Prerequisites:** AWS credentials for the target environment, at least two admins.

---

### Run Migration

**Via Makefile (recommended):**
```bash
cd infrastructure
make db-migrate MIGRATION=add_permission_matrix ENV=dev
```

**Direct execution:**
```bash
cd scripts/database
export TABLE_NAME=impressionnistes-registration-dev
python3 add_permission_matrix.py
```

**Important:**
1. Always test on dev first
2. Migrations should be idempotent (safe to run multiple times)
3. Delete migration files after running on all environments

See `MIGRATIONS.md` for detailed migration guide.

---

### Reset Database

**Via Makefile:**
```bash
cd infrastructure
make db-reset ENV=dev
```

**What it does:**
- First takes a `safety-pre-reset` backup (`purge_database.py --backup-only`); the target stops if it fails
- Deletes every `TEAM#` and `USER#` item (team manager profiles, boats, crew members, payments) and the `CONFIG` items `SYSTEM`, `PRICING` and `NOTIFICATION`, then reinitializes them with `reinit_config.py`
- Does not delete Cognito accounts (use `make db-purge ... DELETE_COGNITO=1` or `make delete-team-manager`)
- Preserves race definitions and the backup history (`AUDIT#DATABASE_BACKUP`)
- Prints the real race count at the end

**Warning:** Destructive operation! You must type `PURGER LA BASE` to confirm (asked before the backup; any other text cancels).

## Script Details

### export-db.py

Export DynamoDB table to CSV format.

**Usage:**
```bash
python3 export-db.py <json_file> [options]

Options:
  -o, --output FILE       Output CSV file
  -s, --split            Split by entity type
  -d, --output-dir DIR   Output directory for split files
```

**Example:**
```bash
# Export to single CSV
python3 export-db.py exports/dynamodb-dev.json -o exports/all-data.csv

# Split by entity type
python3 export-db.py exports/dynamodb-dev.json --split --output-dir exports/
```

---

### delete_team_manager.py

Delete a team manager account and all related data.

**Usage:**
```bash
python3 delete_team_manager.py <email> [options]

Options:
  --environment ENV    Environment (dev or prod)
  --yes               Skip confirmation prompt
```

**Example:**
```bash
python3 delete_team_manager.py user@example.com --environment dev
```

---

### purge_database.py / delete_admin.py

See the "Selective Purge" and "Delete Admin" sections above. Both import the shared modules from `functions/shared/` and are tested with moto (no real AWS call in tests).

---

### compare_config_details.py

Compare database configurations between dev and prod.

**Usage:**
```bash
python3 compare_config_details.py
```

**Requirements:**
- AWS credentials configured for both environments
- Profiles: `default` (dev) and `rcpm` (prod)

---

### list_boat_numbers.py / show_boat_numbers.py

Analyze boat number generation.

**Usage:**
```bash
# List actual boat numbers
python3 list_boat_numbers.py

# Show hypothetical boat numbers
python3 show_boat_numbers.py
```

**Note:** Reads from latest export in `infrastructure/exports/`

## Best Practices

1. **Always use Makefile commands** when available
2. **Test on dev first** before running on prod
3. **Backup before destructive operations** (`make db-backup`)
4. **Verify results** after migrations
5. **Delete migration files** after running on all environments
6. **Document custom scripts** with clear usage instructions

## Troubleshooting

**Error: "Unable to locate credentials"**
- Run `aws configure` or set AWS environment variables

**Error: "Table not found"**
- Check table name: `impressionnistes-registration-{env}`
- Verify environment is deployed

**Error: "Float types are not supported"**
- Use `Decimal` type for numbers in DynamoDB
- See migration template in `MIGRATIONS.md`

**Error: "BACKUP_REQUIRED" (purge)**
- Raised by the admin page API when prod is purged with the backup option off. The CLI always takes the backup

**Error: "PRE_RESET_BACKUP_FAILED"**
- The backup failed, nothing was deleted. Check the backup bucket and DynamoDB backup permissions, then retry

**Error: "RESET_PARTIAL"**
- A deletion failed midway. Restore the `safety-pre-reset` backup from the admin page, then retry

**delete_admin refuses**
- Unknown email, not an admin, or last remaining admin: nothing was changed

**Migration already applied**
- Migrations should check if already applied
- Safe to run multiple times (idempotent)

## Related Documentation

- Migration guide: `MIGRATIONS.md`
- Makefile commands: Run `make help` in `infrastructure/`
- DynamoDB docs: https://docs.aws.amazon.com/dynamodb/
