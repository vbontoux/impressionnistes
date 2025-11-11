# Database Export Guide

Quick guide for exporting DynamoDB data to CSV.

## Quick Commands

### View Database Contents

```bash
make db-view
```

Shows:
- Configuration items
- First 10 races
- Total item count

### Export to CSV

```bash
make db-export
```

Creates:
- Full JSON export
- Combined CSV file
- Separate CSV files by entity type (CONFIG, RACE, USER, etc.)

All files saved to `exports/` directory.

### Export Specific Environment

```bash
# Export dev environment (default)
make db-export ENV=dev

# Export production environment
make db-export ENV=prod
```

## Output Files

After running `make db-export`, you'll get:

```
exports/
├── dynamodb-dev-20241111-120000.json    # Full JSON export
├── dynamodb-dev-20241111-120000.csv     # All items in one CSV
├── config-20241111-120000.csv           # Configuration items only
├── race-20241111-120000.csv             # Race definitions only
├── user-20241111-120000.csv             # User profiles (when added)
└── ...
```

## Manual Export with Python Script

For more control, use the export script directly:

```bash
cd infrastructure

# Export to single CSV
./export-db.py exports/dynamodb-dev-20241111-120000.json

# Split by entity type
./export-db.py exports/dynamodb-dev-20241111-120000.json --split

# Custom output location
./export-db.py exports/dynamodb-dev-20241111-120000.json -o my-export.csv
```

## Export Script Options

```bash
./export-db.py --help

Options:
  json_file              Input JSON file from DynamoDB scan
  -o, --output          Output CSV file
  -s, --split           Split by entity type into separate files
  -d, --output-dir      Output directory for split files (default: exports)
```

## Use Cases

### 1. Backup Before Major Changes

```bash
make db-export
# Files saved with timestamp for easy restoration
```

### 2. Data Analysis

```bash
make db-export
# Open CSV files in Excel, Google Sheets, or pandas
```

### 3. Migration Between Environments

```bash
# Export from dev
make db-export ENV=dev

# Review data
open exports/

# Import to prod (manual process via AWS Console or script)
```

### 4. Debugging

```bash
# Quick view
make db-view

# Full export for detailed analysis
make db-export
```

## CSV Format

The CSV files contain flattened DynamoDB items:

```csv
PK,SK,name,event_type,boat_type,age_category,gender_category,distance,created_at
RACE,M01,1X SENIOR WOMAN,42km,skiff,SENIOR,WOMEN,42,2024-11-11T10:00:00Z
RACE,M02,1X SENIOR MAN,42km,skiff,SENIOR,MEN,42,2024-11-11T10:00:00Z
...
```

## Entity Types

Current entity types in the database:

- **CONFIG** - System configuration (SYSTEM, PRICING, NOTIFICATION)
- **RACE** - Race definitions (42 races total)
- **USER** - Team manager profiles (added in later tasks)
- **CREW** - Crew members (added in later tasks)
- **BOAT** - Boat registrations (added in later tasks)
- **PAYMENT** - Payment records (added in later tasks)

## Importing Data

To import data back into DynamoDB:

### Option 1: AWS Console
1. Go to DynamoDB Console
2. Select table
3. Actions → Import from S3
4. Upload your JSON file

### Option 2: AWS CLI

```bash
# Restore from JSON export
aws dynamodb batch-write-item \
  --request-items file://exports/dynamodb-dev-20241111-120000.json
```

### Option 3: Python Script (for CSV)

```python
import csv
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('impressionnistes-registration-dev')

with open('exports/races-20241111-120000.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        table.put_item(Item=row)
```

## Scheduled Exports

To automate exports, add to cron:

```bash
# Daily export at 2 AM
0 2 * * * cd /path/to/infrastructure && make db-export ENV=prod
```

Or create a Lambda function for automated backups (covered in task 20.1).

## Troubleshooting

### "Table not found"

Make sure the table exists:
```bash
aws dynamodb describe-table --table-name impressionnistes-registration-dev
```

### "Permission denied"

Ensure AWS credentials have DynamoDB read permissions:
```bash
aws sts get-caller-identity
```

### "No items exported"

Check if table has data:
```bash
make db-view
```

### CSV encoding issues

The export script uses UTF-8 encoding. If you have issues opening in Excel:
1. Open Excel
2. Data → From Text/CSV
3. Select file
4. Choose UTF-8 encoding

## Best Practices

1. **Export before major changes** - Always backup before deploying significant updates

2. **Regular backups** - Export production data regularly (automated in task 20.1)

3. **Version control exports** - Keep timestamped exports for audit trail

4. **Separate by entity** - Use `--split` option for easier analysis

5. **Clean old exports** - Remove old export files periodically:
   ```bash
   # Keep only last 30 days
   find exports/ -name "*.csv" -mtime +30 -delete
   ```

## Related Commands

```bash
make db-view      # Quick view of database contents
make db-export    # Full export to CSV
make costs        # Check database costs
make list         # List deployed stacks
```

## Support

For issues with exports, check:
- CloudWatch logs for Lambda errors
- AWS CLI version: `aws --version`
- Python version: `python3 --version`
- DynamoDB table status: `make list`
