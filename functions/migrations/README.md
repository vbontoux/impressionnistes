# Database Migrations

This directory contains database migration scripts for one-time data updates or schema changes.

## When to Create a Migration

Create a migration when you need to:
- Update existing data to match new schema requirements
- Backfill calculated fields
- Fix data inconsistencies
- Perform one-time data transformations

## Migration Template

```python
"""
Migration Script: [Brief Description]
[Detailed description of what this migration does]
"""
import sys
import os
from decimal import Decimal

# Add shared directory to path for imports
shared_path = os.path.join(os.path.dirname(__file__), '..', 'shared')
sys.path.insert(0, shared_path)

# Add layer directory to path (for boto3 and other dependencies)
layer_path = os.path.join(os.path.dirname(__file__), '..', 'layer', 'python')
if os.path.exists(layer_path):
    sys.path.insert(0, layer_path)

from database import get_db_client, get_timestamp


def convert_floats_to_decimal(obj):
    """
    Recursively convert all float values to Decimal for DynamoDB compatibility
    """
    if isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_floats_to_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj


def run_migration(team_manager_id=None):
    """
    Main migration logic
    
    Args:
        team_manager_id: Optional - migrate only for specific team manager
    """
    db = get_db_client()
    
    # Your migration logic here
    print("Migration logic goes here")
    
    # Example: Query items
    # items = db.query_by_pk(pk=f'TEAM#{team_manager_id}', sk_prefix='BOAT#')
    
    # Example: Update items
    # for item in items:
    #     item['new_field'] = 'value'
    #     item['updated_at'] = get_timestamp()
    #     db.put_item(item)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Migration description')
    parser.add_argument('--team-manager-id', type=str, help='Team manager ID to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        sys.exit(0)
    
    if not args.team_manager_id:
        print("ERROR: --team-manager-id is required")
        sys.exit(1)
    
    print(f"Starting migration for team manager: {args.team_manager_id}")
    
    response = input("Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled")
        sys.exit(0)
    
    run_migration(args.team_manager_id)
```

## Running Migrations

### Using Makefile (Recommended)
```bash
cd infrastructure
make db-migrate MIGRATION=your_migration_name TEAM_MANAGER_ID=your-user-id ENV=dev
```

### Direct Execution
```bash
cd functions/migrations
export DYNAMODB_TABLE_NAME=impressionnistes-registration-dev
python your_migration_name.py --team-manager-id your-user-id
```

## Best Practices

1. **Always test on dev first** - Never run migrations directly on production
2. **Make migrations idempotent** - Safe to run multiple times
3. **Add safety checks** - Verify data before updating
4. **Use Decimal for numbers** - DynamoDB requires Decimal, not float
5. **Log progress** - Print what's being updated
6. **Handle errors gracefully** - Don't leave data in inconsistent state
7. **Backup before running** - Use DynamoDB on-demand backup
8. **Document the migration** - Explain what it does and why
9. **Delete after running** - Remove migrations once applied to all environments

## Important Notes

- Migrations are one-time scripts, not permanent code
- Delete migrations after they've been run in all environments
- Keep this README as a template for future migrations
- Use the Makefile command for consistency and safety

## Troubleshooting

**Error: "Unable to locate credentials"**
- Configure AWS credentials: `aws configure`
- Or set environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

**Error: "Table not found"**
- Set correct table name: `export DYNAMODB_TABLE_NAME=impressionnistes-registration-dev`

**Error: "Float types are not supported"**
- Use the `convert_floats_to_decimal()` helper function before saving to DynamoDB

**Error: "Migration not found"**
- Check the migration file exists in `functions/migrations/`
- Ensure the filename matches what you're passing to the Makefile
