# Script Reorganization Summary

## What Changed

All scripts have been reorganized from scattered locations into a centralized `/scripts/` directory with clear categorization.

## Before (Messy)

Scripts were scattered across 4 locations:
- `/scripts/` - License checker (unrelated tool)
- `/infrastructure/` - Mix of 14 Python utilities and shell scripts
- `/infrastructure/scripts/` - 4 database management scripts
- `/functions/migrations/` - 15 one-time database migrations

## After (Clean)

```
scripts/
├── README.md                    # Master index
├── deployment/                  # 5 deployment scripts
├── database/                    # 24 database scripts (utilities + migrations)
├── testing/                     # 1 testing script
└── external/                    # 3 external tool files
```

## File Movements

### Deployment Scripts (5 files)
**From:** `infrastructure/`  
**To:** `scripts/deployment/`
- deploy.sh
- destroy.sh
- clean-all-aws.sh
- create-certificates.sh
- clear-cloudfront-cache.sh

### Database Scripts (24 files)
**From:** `infrastructure/` (9 files)  
**To:** `scripts/database/`
- export-db.py
- check_migration.py
- compare_config_details.py
- list_boat_numbers.py
- show_boat_numbers.py

**From:** `infrastructure/scripts/` (4 files)  
**To:** `scripts/database/`
- delete_clubs.py
- delete_team_manager.py
- delete_user_data.py
- reinit_config.py

**From:** `functions/migrations/` (15 files + README)  
**To:** `scripts/database/`
- add_bow_start_numbers.py
- add_payment_history_permissions.py
- add_permission_matrix.py
- calculate_boat_clubs.py
- delete_all_data_keep_team_managers.py
- generate_boat_numbers_and_simplify_clubs.py
- load_clubs.py
- migrate_split_races.py
- remove_slack_webhooks_from_db.py
- reset_all_payments_and_crews.py
- reset_paid_crews.py
- update_21km_races_final.py
- update_boat_interval.py
- update_notification_config.py
- README.md → MIGRATIONS.md

### Testing Scripts (1 file)
**From:** `infrastructure/`  
**To:** `scripts/testing/`
- verify-receipt-email.sh

### External Tools (3 files)
**From:** `scripts/` (root)  
**To:** `scripts/external/`
- license_checker.py
- test_licenses.csv
- results.csv

## Makefile Updates

All script references in `infrastructure/Makefile` have been updated:

### Database Exports
```makefile
# OLD: ./export-db.py
# NEW: ../scripts/database/export-db.py
```

### Team Manager Deletion
```makefile
# OLD: python3 scripts/delete_team_manager.py
# NEW: python3 ../scripts/database/delete_team_manager.py
```

### Migrations
```makefile
# OLD: ../functions/migrations/*.py
# NEW: ../scripts/database/*.py

# OLD: functions/migrations/README.md
# NEW: scripts/database/MIGRATIONS.md
```

### Config Reinitialization
```makefile
# OLD: scripts/reinit_config.py
# NEW: ../scripts/database/reinit_config.py
```

## Documentation Added

### New README Files
1. `scripts/README.md` - Master index of all scripts
2. `scripts/deployment/README.md` - Deployment script documentation
3. `scripts/database/README.md` - Database operations guide
4. `scripts/testing/README.md` - Testing utilities guide
5. `scripts/external/README.md` - External tools documentation

### Existing Documentation
- `scripts/database/MIGRATIONS.md` - Migration guide (moved from functions/migrations/)

## Benefits

✅ **Clear Organization**
- All scripts in one place
- Logical categorization by purpose
- Easy to find what you need

✅ **Better Documentation**
- Each category has its own README
- Master index in scripts/README.md
- Clear usage examples

✅ **Simplified Paths**
- Flat structure within categories
- No unnecessary subdirectories
- Consistent naming

✅ **Easier Maintenance**
- One place to look for scripts
- Clear separation of concerns
- Reduced confusion

## Usage

### Via Makefile (Recommended)
```bash
cd infrastructure

# Deployment
make deploy-dev
make destroy-dev

# Database operations
make db-export ENV=dev
make db-migrate MIGRATION=script_name ENV=dev
make delete-team-manager EMAIL=user@example.com ENV=dev

# Testing
make test-email EMAIL=your@email.com
```

### Direct Execution
```bash
# Deployment
./scripts/deployment/deploy.sh dev

# Database
python3 scripts/database/export-db.py exports/data.json
python3 scripts/database/delete_team_manager.py user@example.com --environment dev

# Testing
./scripts/testing/verify-receipt-email.sh pi_xxxxx
```

## Migration Checklist

If you have local changes or scripts in progress:

- [ ] Update any local scripts that reference old paths
- [ ] Update documentation that references old script locations
- [ ] Update CI/CD pipelines if they reference script paths
- [ ] Update any bookmarks or notes with old paths
- [ ] Test Makefile commands to ensure they work
- [ ] Verify migrations can still be run

## Rollback (If Needed)

If you need to rollback this change:

1. The old empty directories were removed: `infrastructure/scripts/`, `functions/migrations/`
2. All files are in git history
3. Use `git revert` to undo the changes
4. Or manually move files back to original locations

## Questions?

See individual README files:
- `scripts/README.md` - Overview
- `scripts/deployment/README.md` - Deployment scripts
- `scripts/database/README.md` - Database operations
- `scripts/database/MIGRATIONS.md` - Migration guide
- `scripts/testing/README.md` - Testing utilities
- `scripts/external/README.md` - External tools
