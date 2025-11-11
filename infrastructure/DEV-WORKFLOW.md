# Development Workflow Guide

Quick reference for iterative development and testing with AWS CDK.

## After Completing Each Task

When you complete a task that modifies infrastructure (like tasks 1.3, 1.4, 1.5, etc.), follow this workflow:

### Option 1: Quick Redeploy (Recommended for Dev)

```bash
cd infrastructure
make redeploy
```

This will:
1. Destroy all dev stacks
2. Wait 5 seconds
3. Deploy fresh stacks
4. Initialize configuration

**Use when**: You want a clean slate to test changes

### Option 2: Incremental Deploy (Faster)

```bash
cd infrastructure
make diff    # Preview changes
make deploy  # Apply changes
```

**Use when**: You're making small changes and want to keep existing data

### Option 3: Deploy Specific Stack

```bash
cd infrastructure
cdk deploy ImpressionnistesDatabase-dev --context env=dev
```

**Use when**: You only changed one stack

## Common Development Commands

### Before Deploying

```bash
# Check what will change
make diff

# Synthesize templates (check for errors)
make synth

# Verify prerequisites
make check-prereqs
```

### Deploying

```bash
# Deploy all stacks
make deploy

# Quick destroy + deploy
make redeploy

# Deploy to production (with confirmation)
make deploy-prod
```

### After Deploying

```bash
# List deployed stacks
make list

# Check DynamoDB table
aws dynamodb describe-table --table-name impressionnistes-registration-dev

# Scan configuration
aws dynamodb scan \
  --table-name impressionnistes-registration-dev \
  --filter-expression "PK = :pk" \
  --expression-attribute-values '{":pk":{"S":"CONFIG"}}' \
  --max-items 5

# Check Lambda functions
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `Impressionnistes`)].FunctionName'

# View CloudWatch logs
aws logs tail /aws/lambda/ImpressionnistesDatabase-dev-InitConfigFunction --follow
```

### Cleaning Up

```bash
# Destroy all stacks
make destroy

# Complete cleanup (stacks + orphaned resources)
make clean-aws

# Fix stuck stack
make fix-stuck-stack

# Clean local files
make clean
```

## Task-by-Task Workflow

### Example: After Completing Task 1.3 (DynamoDB Table)

```bash
# 1. Check your changes
cd infrastructure
make diff

# 2. Deploy
make deploy

# 3. Verify table was created
aws dynamodb describe-table --table-name impressionnistes-registration-dev

# 4. Check configuration was initialized
aws dynamodb scan \
  --table-name impressionnistes-registration-dev \
  --filter-expression "PK = :pk" \
  --expression-attribute-values '{":pk":{"S":"CONFIG"}}' \
  --max-items 3

# 5. Test Slack notification (if configured)
# Check the app-impressionnistes channel for any deployment notifications
```

### Example: After Completing Task 1.4 (Shared Utilities)

```bash
# 1. Deploy changes
make deploy

# 2. Test Lambda function locally (if applicable)
cd ../backend
source venv/bin/activate
python -c "from shared.configuration import ConfigurationManager; print('Import successful')"

# 3. Redeploy if needed
cd ../infrastructure
make redeploy
```

### Example: After Completing Task 1.5 (Monitoring)

```bash
# 1. Deploy
make deploy

# 2. Check CloudWatch log groups
aws logs describe-log-groups --query 'logGroups[?starts_with(logGroupName, `/aws/lambda/Impressionnistes`)].logGroupName'

# 3. Check SNS topics
aws sns list-topics --query 'Topics[?contains(TopicArn, `Impressionnistes`)]'

# 4. Verify alarms
aws cloudwatch describe-alarms --query 'MetricAlarms[?starts_with(AlarmName, `Impressionnistes`)]'
```

## Troubleshooting During Development

### Stack is Stuck

```bash
make fix-stuck-stack
```

### Want Fresh Start

```bash
make clean-aws
make deploy
```

### Changes Not Applying

```bash
# Clear CDK cache
rm -rf cdk.out

# Redeploy
make redeploy
```

### Lambda Function Not Updating

```bash
# Force update by changing code
# Then redeploy
make redeploy
```

### Configuration Not Initializing

```bash
# Check Lambda logs
aws logs tail /aws/lambda/ImpressionnistesDatabase-dev-InitConfigFunction --follow

# Manually trigger (if needed)
aws lambda invoke \
  --function-name ImpressionnistesDatabase-dev-InitConfigFunction \
  --payload '{"RequestType":"Update"}' \
  response.json
```

## Cost Management During Development

### Check Current Costs

```bash
# Get cost estimate for last 7 days
aws ce get-cost-and-usage \
  --time-period Start=$(date -v-7d +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

### Minimize Costs

1. **Destroy when not testing**:
   ```bash
   make destroy
   ```

2. **Use on-demand billing** (already configured for DynamoDB)

3. **Clean up old resources**:
   ```bash
   make clean-aws
   ```

## Best Practices

1. **Always run `make diff` before deploying** to see what will change

2. **Use `make redeploy` for major changes** to ensure clean state

3. **Check logs after deployment** to verify everything initialized correctly

4. **Destroy dev environment when not in use** to save costs

5. **Test incrementally** - deploy and test after each task

6. **Keep production separate** - never use `make redeploy` on prod!

## Quick Reference

```bash
# Most common workflow
make diff       # See changes
make deploy     # Deploy changes
make destroy    # Clean up when done

# For major changes
make redeploy   # Fresh deployment

# When stuck
make fix-stuck-stack
make clean-aws
```

## Environment Variables

Set these for convenience:

```bash
# Add to ~/.zshrc or ~/.bashrc
export AWS_REGION=eu-west-3
export AWS_PROFILE=default  # or your profile name

# For CDK
export CDK_DEFAULT_REGION=eu-west-3
```

## Next Steps

After each task completion:
1. ✅ Complete the code changes
2. ✅ Run `make diff` to preview
3. ✅ Run `make deploy` or `make redeploy`
4. ✅ Verify deployment with AWS CLI commands
5. ✅ Test functionality
6. ✅ Mark task as complete in tasks.md
7. ✅ Move to next task

Happy developing! 🚀
