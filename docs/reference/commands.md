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
