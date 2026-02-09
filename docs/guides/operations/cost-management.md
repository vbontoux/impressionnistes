# AWS Cost Management

## Overview

This guide explains how to monitor AWS costs for the Course des Impressionnistes project using cost allocation tags.

## Quick Start

```bash
cd infrastructure

# See project costs right now
make costs-by-tag

# See all AWS costs
make costs-all

# See detailed project costs (available after Feb 10, 2026)
make costs
```

## Cost Commands

### `make costs` - Project Costs with Service Breakdown

Shows costs filtered to CourseDesImpressionnistes project only.

**Provides:**
- Cost by AWS service (Lambda, DynamoDB, CloudFront, etc.)
- Total project cost
- Daily breakdown (last 7 days)

**Note:** Requires 24-48 hours after tag activation to show data.

### `make costs-by-tag` - Costs Grouped by Tags

Shows costs grouped by Project and Environment tags.

**Provides:**
- Total cost by project
- Total cost by environment (dev/prod)

**Advantage:** Works immediately after tag activation.

### `make costs-all` - All AWS Account Costs

Shows all costs in your AWS account (no filtering).

**Provides:**
- Cost by AWS service (all services)
- Total account cost
- Daily breakdown

**Use when:** You need to see total AWS spending including non-project costs (domain registrar, support plans, etc.)

## Cost Allocation Tags

All project resources are tagged with:
- `Project` = `CourseDesImpressionnistes`
- `Environment` = `dev` or `prod`
- `CostCenter` = `RCPM`
- `ManagedBy` = `CDK`

**Status:** Tags activated on February 8, 2026.

## Typical Costs

Expected monthly costs for this project:
- **DynamoDB** - Database storage and operations
- **Lambda** - Function invocations (~$0.50/month)
- **API Gateway** - API requests (~$0.30/month)
- **CloudFront** - CDN data transfer (~$0.60/month)
- **S3** - Storage and requests (~$0.20/month)
- **CloudWatch** - Logs and metrics (~$0.20/month)
- **Cognito** - User authentication (mostly free tier)

**Average:** ~$2-3/month for dev environment

## Cost Optimization Tips

1. **Monitor regularly:** Run `make costs` weekly
2. **Check service breakdown:** Identify which services cost the most
3. **Review daily trends:** Catch unexpected cost spikes
4. **Compare environments:** Use `make costs-by-tag` to compare dev vs prod

## Verification

Check that cost allocation tags are active:
```bash
aws ce list-cost-allocation-tags --status Active
```

Check that resources are tagged:
```bash
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Project,Values=CourseDesImpressionnistes \
  --query 'length(ResourceTagMappingList)'
```

Should return: 77 resources

## Troubleshooting

### `make costs` shows $0.00

**Cause:** Cost allocation tags need 24-48 hours to populate billing data.

**Solution:** 
- Use `make costs-by-tag` in the meantime
- Wait 24-48 hours after tag activation
- Check tag activation status (see Verification above)

### Costs seem too high

**Steps:**
1. Run `make costs-all` to see breakdown by service
2. Check for unexpected resources
3. Review CloudWatch logs for unusual activity
4. Check for data transfer costs (CloudFront, S3)

## Cost Explorer API Pricing

AWS Cost Explorer API charges:
- First query per month: Free
- Additional queries: $0.01 per query
- Running `make costs`: ~$0.02-0.03 per run
- Monthly cost for occasional checks: < $1.00

## Related Documentation

- [Infrastructure Quickstart](infrastructure-quickstart.md) - Deployment commands
- [Monitoring](monitoring.md) - CloudWatch logs and alarms
- [Database Export](database-export.md) - Database backup and export
