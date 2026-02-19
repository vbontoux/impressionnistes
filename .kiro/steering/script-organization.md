# Script Organization Rule

## Purpose
Ensure all operational scripts are placed in the correct location within the `/scripts/` directory structure.

## Directory Structure

```
scripts/
├── deployment/     # Infrastructure deployment and AWS management
├── database/       # Database operations, utilities, and migrations
├── testing/        # Testing and verification utilities
└── external/       # External/third-party tools not part of main app
```

## Rules

### WHEN creating or moving a script, you MUST:

1. **Identify the script's purpose** and place it in the correct category
2. **Use the flat structure** - no subdirectories within categories
3. **Update the Makefile** if the script is referenced there
4. **Document the script** in the category's README.md

---

## Script Placement Guide

### 🚀 Deployment Scripts → `scripts/deployment/`

**Purpose:** Infrastructure deployment, AWS resource management, CloudFormation operations

**Examples:**
- `deploy.sh` - Deploy infrastructure to AWS
- `destroy.sh` - Destroy infrastructure stacks
- `clean-all-aws.sh` - Complete AWS cleanup
- `create-certificates.sh` - Create SSL certificates
- `clear-cloudfront-cache.sh` - Invalidate CloudFront cache

**When to use:**
- Script deploys or destroys AWS infrastructure
- Script manages CloudFormation stacks
- Script handles AWS resource cleanup
- Script configures AWS services (certificates, domains, etc.)

**File types:** Shell scripts (`.sh`)

---

### 🗄️ Database Scripts → `scripts/database/`

**Purpose:** Database operations, data management, one-time migrations

**Examples:**

**Utilities:**
- `export-db.py` - Export DynamoDB to CSV
- `compare_config_details.py` - Compare dev vs prod
- `delete_team_manager.py` - Delete user and all data
- `reinit_config.py` - Reinitialize configuration

**Migrations (one-time):**
- `add_*.py` - Add new features/fields
- `update_*.py` - Update existing data
- `migrate_*.py` - Data transformations
- `delete_*.py` - Remove obsolete data
- `reset_*.py` - Reset specific data

**When to use:**
- Script reads/writes DynamoDB data
- Script exports or analyzes database contents
- Script performs one-time data migration
- Script manages database configuration
- Script deletes or resets data

**File types:** Python scripts (`.py`)

**Important:** Migrations are one-time scripts - delete after running on all environments

---

### 🧪 Testing Scripts → `scripts/testing/`

**Purpose:** Testing, verification, and validation utilities

**Examples:**
- `verify-receipt-email.sh` - Verify Stripe receipt email
- `test-api-endpoints.sh` - Test API endpoints
- `validate-configuration.py` - Validate config files

**When to use:**
- Script tests functionality
- Script verifies configuration
- Script validates data or setup
- Script checks integration with external services

**File types:** Shell scripts (`.sh`) or Python scripts (`.py`)

---

### 🔧 External Tools → `scripts/external/`

**Purpose:** Third-party tools, external utilities, unrelated to main application

**Examples:**
- `license_checker.py` - FFAviron license validation
- External data processing tools
- Third-party integrations not part of core app

**When to use:**
- Script is not directly related to the main application
- Script is a standalone utility
- Script integrates with external systems (not AWS/app infrastructure)
- Script is for manual/ad-hoc operations

**File types:** Any (`.py`, `.sh`, `.js`, etc.)

---

## Red Flags - Wrong Locations

❌ **DON'T put scripts in these locations:**
- `infrastructure/` - Only CDK code (app.py, config.py, stacks/)
- `functions/` - Only Lambda function code
- `frontend/` - Only frontend application code
- Project root - Keep root clean

❌ **DON'T create subdirectories:**
- `scripts/database/migrations/` - Use flat structure
- `scripts/database/utilities/` - Use flat structure
- Keep all scripts in category root

---

## Checklist for New Scripts

When creating a new script:

- [ ] Identified correct category (deployment/database/testing/external)
- [ ] Placed in correct directory (no subdirectories)
- [ ] Added executable permissions if shell script (`chmod +x`)
- [ ] Added shebang line (`#!/bin/bash` or `#!/usr/bin/env python3`)
- [ ] Documented in category README.md
- [ ] Updated Makefile if script should be called via make command
- [ ] Tested script works from both direct execution and Makefile

---

## Makefile Integration

**If script should be run via Makefile:**

1. Add make target in `infrastructure/Makefile`
2. Use relative path from infrastructure directory
3. Handle environment variables properly

**Example:**
```makefile
my-script:
	@echo "Running my script..."
	@$(PYTHON) ../scripts/database/my_script.py $(ARGS)
```

**Path patterns:**
- Deployment: `../scripts/deployment/script.sh`
- Database: `../scripts/database/script.py`
- Testing: `../scripts/testing/script.sh`

---

## Examples

### ✅ CORRECT Placement

**Database export utility:**
```
scripts/database/export-db.py
```

**Deployment script:**
```
scripts/deployment/deploy.sh
```

**Testing utility:**
```
scripts/testing/verify-receipt-email.sh
```

**External tool:**
```
scripts/external/license_checker.py
```

### ❌ WRONG Placement

**Database script in infrastructure:**
```
infrastructure/export-db.py  ❌
```

**Migration in subdirectory:**
```
scripts/database/migrations/add_feature.py  ❌
```

**Deployment script in root:**
```
deploy.sh  ❌
```

---

## Migration from Old Structure

If you find scripts in old locations:

**Old locations (deprecated):**
- `infrastructure/*.py` (except CDK files)
- `infrastructure/*.sh`
- `infrastructure/scripts/`
- `functions/migrations/`

**Action:**
1. Move to appropriate `scripts/` subdirectory
2. Update Makefile references
3. Update documentation
4. Remove old empty directories

---

## Documentation Requirements

**Each category MUST have:**
- `README.md` - Explains all scripts in that category
- Usage examples
- Prerequisites
- Troubleshooting section

**When adding a script:**
- Add entry to category README.md
- Include purpose, usage, and examples
- Document any prerequisites or dependencies

---

## Related Documentation

- Master index: `scripts/README.md`
- Deployment guide: `scripts/deployment/README.md`
- Database guide: `scripts/database/README.md`
- Testing guide: `scripts/testing/README.md`
- External tools: `scripts/external/README.md`
- Makefile commands: Run `make help` in `infrastructure/`

---

## Enforcement

**Before committing any script:**
1. Verify it's in the correct `scripts/` subdirectory
2. Verify no subdirectories were created within categories
3. Verify Makefile paths are updated (if applicable)
4. Verify documentation is updated
5. Test the script works from its new location

**If you see a script in the wrong location:**
- Move it to the correct location immediately
- Update all references
- Document the change
