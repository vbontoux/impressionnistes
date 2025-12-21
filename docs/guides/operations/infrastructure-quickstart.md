# Quick Start Guide

## Prerequisites Installation

### 1. Install AWS CLI

**macOS (using Homebrew):**
```bash
brew install awscli
```

**Or download from AWS:**
https://aws.amazon.com/cli/

### 2. Install Node.js and npm

**macOS (using Homebrew):**
```bash
brew install node
```

**Verify installation:**
```bash
node --version  # Should be v18+
npm --version
```

### 3. Install AWS CDK CLI (globally)

```bash
npm install -g aws-cdk
```

**Verify installation:**
```bash
cdk --version
```

**Note:** CDK CLI is installed globally, but it needs the Python virtual environment activated to run because it executes the Python CDK app.

### 4. Configure AWS Credentials

```bash
aws configure
```

You'll be prompted for:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `eu-west-3` (Paris)
- Default output format: `json`

**Verify credentials:**
```bash
aws sts get-caller-identity
```

## Quick Deployment

### 1. Check Prerequisites

```bash
cd infrastructure
make check-prereqs
```

This will verify:
- ✓ AWS CLI is installed
- ✓ CDK CLI is installed
- ✓ AWS credentials are configured

### 2. Setup Python Environment

```bash
make setup
```

This will:
- Create a Python virtual environment
- Install all Python dependencies
- Verify prerequisites

### 3. Bootstrap CDK (First Time Only)

```bash
make bootstrap
```

This creates the CDK toolkit stack in your AWS account. Only needed once per account/region.

**Note:** The Makefile automatically activates the virtual environment before running CDK commands.

### 4. Deploy to AWS

```bash
make deploy
```

This will:
- Synthesize CloudFormation templates
- Deploy all stacks to your AWS account
- Initialize the DynamoDB table with default configuration

### 5. Verify Deployment

```bash
# List deployed stacks
make list

# Check DynamoDB table
aws dynamodb describe-table --table-name impressionnistes-registration-dev

# Check if configuration was initialized
aws dynamodb scan \
  --table-name impressionnistes-registration-dev \
  --filter-expression "PK = :pk" \
  --expression-attribute-values '{":pk":{"S":"CONFIG"}}' \
  --max-items 3
```

## Common Commands

```bash
# Show help
make help

# Preview changes before deploying
make diff

# Synthesize CloudFormation templates
make synth

# Deploy to production (with confirmation)
make deploy-prod

# Destroy dev environment
make destroy-dev

# Clean up local files
make clean
```

## Manual Deployment (Alternative)

If you prefer to run commands manually:

```bash
# Activate virtual environment
source venv/bin/activate

# Bootstrap CDK
cdk bootstrap --context env=dev

# Deploy
cdk deploy --all --context env=dev

# Deactivate when done
deactivate
```

## Troubleshooting

### "CDK CLI not found"

Install CDK globally:
```bash
npm install -g aws-cdk
```

### "Module not found" errors

Make sure the virtual environment is activated. The Makefile does this automatically, but if running CDK manually:
```bash
source venv/bin/activate
```

### "AWS credentials not configured"

Configure your AWS credentials:
```bash
aws configure
```

### "Bootstrap required"

Run bootstrap first:
```bash
make bootstrap
```

### "Permission denied" errors

Ensure your AWS user has permissions for:
- CloudFormation
- DynamoDB
- Lambda
- IAM (for role creation)
- CloudWatch

### Check CDK version

```bash
cdk --version
```

Should be 2.120.0 or higher.

## What Gets Deployed

### DatabaseStack
- DynamoDB table: `impressionnistes-registration-dev`
- GSI1: Registration status index
- GSI2: Race lookup index
- Lambda function for initialization
- Default configuration (system, pricing, notifications)
- 42 race definitions (14 marathon + 28 semi-marathon)

### Cost Estimate

For testing/development:
- DynamoDB: Pay-per-request (minimal cost for testing)
- Lambda: Free tier covers most testing
- **Estimated**: < $1/month for light testing

## Next Steps

After successful deployment:

1. **Verify data was initialized:**
   ```bash
   aws dynamodb scan --table-name impressionnistes-registration-dev --max-items 10
   ```

2. **Continue with task 1.4:** Implement shared backend utilities

3. **Deploy frontend** (when ready)

## Cleanup

To remove everything from AWS:

```bash
# Destroy all stacks
make destroy

# Clean local files
make clean
```

**Note:** With `removal_policy: RETAIN`, the DynamoDB table will be kept even after destroying the stack. You'll need to manually delete it from AWS Console if desired.

## Support

For issues:
1. Check CloudFormation events in AWS Console
2. Check CloudWatch logs for Lambda errors
3. Run `make diff` to see what will change
4. Refer to [README.md](README.md) for detailed documentation
