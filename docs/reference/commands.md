# CDK Quick Reference Commands

## Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap --context env=dev
```

**Important:** Always activate the virtual environment before running CDK commands:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

## Development Workflow

**Note:** All commands assume virtual environment is activated.

```bash
# Activate virtual environment
source venv/bin/activate

# Synthesize templates (check for errors)
cdk synth --context env=dev

# Show what will change
cdk diff --context env=dev

# Deploy all stacks
cdk deploy --all --context env=dev

# Deploy specific stack
cdk deploy ImpressionnistesDatabase-dev --context env=dev

# Watch mode (auto-deploy on changes)
cdk watch --context env=dev

# When done
deactivate
```

## Stack Management

```bash
# List all stacks
cdk list --context env=dev

# Show stack outputs
aws cloudformation describe-stacks --stack-name ImpressionnistesDatabase-dev

# Destroy all stacks
cdk destroy --all --context env=dev

# Destroy specific stack
cdk destroy ImpressionnistesDatabase-dev --context env=dev
```

## Production Deployment

```bash
# Deploy to production
cdk deploy --all --context env=prod --require-approval broadening

# Destroy production (use with caution!)
./destroy.sh prod
```

## Troubleshooting

```bash
# View CloudFormation events
aws cloudformation describe-stack-events --stack-name ImpressionnistesDatabase-dev

# Check CDK version
cdk --version

# Clear CDK cache
rm -rf cdk.out

# Force re-synthesis
cdk synth --force --context env=dev
```

## Environment Variables

```bash
# Set AWS region
export CDK_DEFAULT_REGION=eu-west-3

# Set AWS account
export CDK_DEFAULT_ACCOUNT=123456789012

# Use specific AWS profile
export AWS_PROFILE=my-profile
```

## Useful AWS CLI Commands

```bash
# Check current AWS identity
aws sts get-caller-identity

# List CloudFormation stacks
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE

# Get DynamoDB table info
aws dynamodb describe-table --table-name impressionnistes-registration-dev

# List Lambda functions
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `Impressionnistes`)].FunctionName'
```

## Cost Management

See [Cost Management Guide](../guides/operations/cost-management.md) for detailed information.

```bash
# View project costs (after Feb 10, 2026)
make costs

# View costs grouped by tags (works immediately)
make costs-by-tag

# View all AWS account costs
make costs-all
```

## Database Backup and Restore

All commands run from the `infrastructure/` directory. `ENV` defaults to the Makefile default (`dev`).

```bash
# Create an AWS native on-demand backup (waits until it is AVAILABLE)
make db-backup ENV=dev

# Export the whole table to a local JSON file (exports/backup-<env>-<timestamp>.json)
make db-backup-local ENV=dev

# List native backups of the table
make db-list-backups ENV=dev

# Restore a native backup into a NEW table (asks for confirmation)
make db-restore-backup BACKUP_ARN=<arn> ENV=dev
```

### Relation to the admin page "Gestion de la base"

The admin page "Gestion de la base" and the Makefile targets complement each other:

- `make db-backup` creates the same kind of AWS native on-demand backup that the page creates alongside every JSON backup. When run from the Makefile, the backup is named `impressionnistes-<env>-<timestamp>`.
- `make db-list-backups ENV=<env>` is where the native backups created by the page are visible. They are named `impressionnistes-registration-<env>-<category>_<timestamp>`. The page itself lists only JSON backups, not native ones.
- `make db-restore-backup BACKUP_ARN=<arn>` restores a native backup into a NEW table named `impressionnistes-registration-<env>-restored`. It is the out-of-band fallback: the original table is untouched, and you must verify the restored data, then delete the old table and rename the restored one manually.
- The page restores differently: it does an in-place full replacement of the table content from a JSON backup.

## Testing and Linting

```bash
# Run all backend integration tests
make test-backend

# Run one backend test with full traceback (stops at first failure, verbose)
make test-backend-one TEST=tests/integration/test_crew_member_api.py::test_create_crew_member

# Run frontend formatter tests and unit tests (vitest)
make test-frontend

# Lint frontend code with ESLint
make lint-frontend
```

- `make test-backend-one TEST=<path::test>` runs a single backend test (or a whole file if you omit `::test`) with `-x -vv --tb=long`, so you get the full traceback.
- `make lint-frontend` now works. It uses `frontend/.eslintrc.cjs` for the rules and `frontend/.gitignore` for the files to skip.
