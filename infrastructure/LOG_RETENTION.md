# Lambda Log Retention Configuration

## Current Setup

To stay under the CloudFormation 500 resource limit, we've removed explicit log retention configuration from Lambda functions. This saves **54 CloudFormation resources** (one `Custom::LogRetention` resource per Lambda function).

## How Logs Work Now

**Before:**
- Each Lambda had `log_retention=logs.RetentionDays.ONE_WEEK`
- Created 54 `Custom::LogRetention` CloudFormation resources
- Logs automatically deleted after 7 days

**After:**
- Logs use AWS account default retention policy
- No extra CloudFormation resources
- Logs still created normally in CloudWatch

## Setting Log Retention

You can set log retention at the AWS account level or per log group:

### Option 1: Account-Level Default (Recommended)
Set a default retention for all new log groups in your AWS account:

1. Go to AWS CloudWatch Console
2. Navigate to "Settings" in the left sidebar
3. Set "Default log retention" (e.g., 30 days, 90 days, Never expire)
4. All new Lambda log groups will use this default

### Option 2: Per Log Group
Set retention for specific Lambda functions:

1. Go to CloudWatch → Log groups
2. Find the log group: `/aws/lambda/<function-name>`
3. Click "Actions" → "Edit retention setting"
4. Choose retention period (1 day to Never expire)

### Option 3: Automated with AWS CLI
Set retention for all Lambda log groups:

```bash
# Set 30-day retention for all Lambda log groups
for log_group in $(aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/" --query 'logGroups[].logGroupName' --output text); do
  aws logs put-retention-policy --log-group-name "$log_group" --retention-in-days 30
done
```

## Recommended Retention Periods

- **Development:** 7-14 days (logs are mainly for debugging)
- **Production:** 30-90 days (compliance and troubleshooting)
- **Compliance-heavy:** 365 days or Never expire

## Cost Considerations

CloudWatch Logs pricing (as of 2024):
- **Storage:** $0.03 per GB per month
- **Ingestion:** $0.50 per GB

For this application:
- ~55 Lambda functions
- Average 10 MB logs per function per day
- **Daily:** ~550 MB = ~$0.28/day ingestion
- **Monthly storage (30 days):** ~16.5 GB = ~$0.50/month

**Total estimated cost:** ~$8-10/month for logs

Setting retention to 30 days instead of "Never expire" can save storage costs over time.

## Monitoring Log Usage

Check your log storage:
```bash
# Get total log storage across all Lambda functions
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/" \
  --query 'sum(logGroups[].storedBytes)' --output text | \
  awk '{print $1/1024/1024/1024 " GB"}'
```

## Why We Made This Change

**Problem:** CloudFormation has a hard limit of 500 resources per stack. With 55 Lambda functions and ~9 resources per function, we hit 503 resources.

**Solution:** Removing log retention configuration saves 54 resources, bringing us to ~425 resources with room to grow.

**Impact:** 
- ✅ No functionality lost - logs still work
- ✅ More flexible - can set retention per environment
- ✅ Simpler stack - fewer resources to manage
- ⚠️ Manual step - need to set retention via console or CLI

## Future Optimization

If we hit the 500 resource limit again, consider:
1. **Split into multiple stacks** (auth, team manager, admin APIs)
2. **Consolidate Lambda functions** (group related operations)
3. **Use HTTP API instead of REST API** (fewer resources per endpoint)

See the main README for more details on scaling strategies.
