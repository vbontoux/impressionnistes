---
inclusion: always
---

# Database Migrations Rule

## Purpose
Ensure database schema and configuration changes are properly managed through migrations and init_config updates.

## Critical Rules

### 1. ALWAYS Update Both init_config.py AND Create Migration

When adding new configuration (permissions, settings, etc.), you MUST:

1. **Update `functions/init/init_config.py`** - For new deployments from scratch
2. **Create migration script in `functions/migrations/`** - For existing databases

**Why both?**
- `init_config.py` only runs ONCE during initial stack deployment
- Existing databases need migrations to add new configuration
- Future deployments from scratch need the updated init_config

### 2. NEVER Run Migrations Directly

**❌ WRONG:**
```bash
python functions/migrations/my_migration.py
```

**✅ CORRECT:**
```bash
cd infrastructure
make db-migrate MIGRATION=my_migration ENV=dev
```

**Why?**
- Makefile sets up proper environment variables (TABLE_NAME, AWS credentials)
- Ensures consistent execution across dev and prod
- Provides proper error handling and logging

### 3. Migration Workflow

**Step 1: Update init_config.py**
```python
# functions/init/init_config.py
def initialize_permission_matrix(table):
    permission_matrix = {
        'PK': 'CONFIG',
        'SK': 'PERMISSION_MATRIX',
        'permissions': {
            'existing_permission': {...},
            'new_permission': {...}  # ADD NEW PERMISSION HERE
        }
    }
```

**Step 2: Create migration script**
```python
# functions/migrations/add_new_permission.py
"""
Migration: Add new_permission to permission matrix

Run with:
cd infrastructure && make db-migrate MIGRATION=add_new_permission ENV=dev
"""
import boto3
import os
from datetime import datetime

def migrate():
    table_name = os.environ.get('TABLE_NAME')
    if not table_name:
        raise ValueError("TABLE_NAME environment variable not set")
    
    # Migration logic here
    pass

if __name__ == '__main__':
    success = migrate()
    exit(0 if success else 1)
```

**Step 3: Run migration on dev**
```bash
cd infrastructure
make db-migrate MIGRATION=add_new_permission ENV=dev
```

**Step 4: Test thoroughly on dev**

**Step 5: Run migration on prod**
```bash
cd infrastructure
make db-migrate MIGRATION=add_new_permission ENV=prod
```

**Step 6: Delete migration file after running on all environments**

### 4. Migration Best Practices

**Check if already applied:**
```python
def migrate():
    # Get current config
    response = table.get_item(Key={'PK': 'CONFIG', 'SK': 'PERMISSION_MATRIX'})
    
    # Check if already applied
    if 'new_permission' in response['Item'].get('permissions', {}):
        print("Migration already applied. Skipping.")
        return True
    
    # Apply migration
    # ...
```

**Update timestamps:**
```python
config['updated_at'] = datetime.utcnow().isoformat() + 'Z'
config['updated_by'] = 'migration:migration_name'
```

**Provide clear output:**
```python
print("Starting migration: migration_name")
print("✓ Added new_permission")
print("✓ Updated configuration")
print("Migration completed successfully")
```

### 5. Common Migration Types

**Adding permissions:**
- Update `functions/init/init_config.py` → `initialize_permission_matrix()`
- Create migration to add to existing `CONFIG#PERMISSION_MATRIX`

**Adding configuration:**
- Update `functions/init/init_config.py` → relevant `initialize_*()` function
- Create migration to add to existing `CONFIG#SYSTEM` or other config

**Schema changes:**
- Update init_config if it affects new records
- Create migration to update existing records

### 6. Testing Migrations

**For integration tests:**
- Tests use a fresh database each time
- No need to run migrations manually
- Update test fixtures if needed

**For local dev database:**
```bash
cd infrastructure
make db-migrate MIGRATION=migration_name ENV=dev
```

**For production:**
```bash
cd infrastructure
make db-migrate MIGRATION=migration_name ENV=prod
```

## Examples

### Example 1: Adding a Permission

**Update init_config.py:**
```python
def initialize_permission_matrix(table):
    permission_matrix = {
        'permissions': {
            # ... existing permissions ...
            'view_payment_history': {
                'description': 'View payment history',
                'resource_type': 'payment',
                'roles': {
                    'team_manager': {'allowed': True, 'phases': ['all']},
                    'admin': {'allowed': True, 'phases': ['all']}
                }
            }
        }
    }
```

**Create migration:**
```python
# functions/migrations/add_payment_permissions.py
def migrate():
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    
    response = table.get_item(Key={'PK': 'CONFIG', 'SK': 'PERMISSION_MATRIX'})
    matrix = response['Item']
    
    if 'view_payment_history' in matrix.get('permissions', {}):
        print("Already applied")
        return True
    
    matrix['permissions']['view_payment_history'] = {
        'description': 'View payment history',
        'resource_type': 'payment',
        'roles': {
            'team_manager': {'allowed': True, 'phases': ['all']},
            'admin': {'allowed': True, 'phases': ['all']}
        }
    }
    
    matrix['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    table.put_item(Item=matrix)
    
    print("✓ Added view_payment_history permission")
    return True
```

**Run migration:**
```bash
cd infrastructure
make db-migrate MIGRATION=add_payment_permissions ENV=dev
# Test thoroughly
make db-migrate MIGRATION=add_payment_permissions ENV=prod
# Delete migration file
```

## Red Flags

🚩 Running migration script directly with `python`
🚩 Forgetting to update init_config.py
🚩 Not checking if migration already applied
🚩 Not testing on dev before prod
🚩 Leaving migration files after running on all environments

## Checklist

When adding new configuration:
- [ ] Updated `functions/init/init_config.py`
- [ ] Created migration script in `functions/migrations/`
- [ ] Migration checks if already applied
- [ ] Migration updates timestamps
- [ ] Ran migration on dev: `make db-migrate MIGRATION=name ENV=dev`
- [ ] Tested thoroughly on dev
- [ ] Ran migration on prod: `make db-migrate MIGRATION=name ENV=prod`
- [ ] Deleted migration file after running on all environments
