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
- `delete_team_manager.py` - Delete team manager and all related data
- `delete_user_data.py` - Delete user data (used by db-reset)
- `reinit_config.py` - Reinitialize database configuration

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

**Warning:** Permanent deletion! Cannot be undone.

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
- Deletes all user data
- Deletes all team manager profiles
- Deletes all boats and crew members
- Deletes all payment records
- Resets configuration to defaults
- Preserves race definitions

**Warning:** Destructive operation! Requires confirmation.

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

**Migration already applied**
- Migrations should check if already applied
- Safe to run multiple times (idempotent)

## Related Documentation

- Migration guide: `MIGRATIONS.md`
- Makefile commands: Run `make help` in `infrastructure/`
- DynamoDB docs: https://docs.aws.amazon.com/dynamodb/
