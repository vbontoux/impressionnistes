# Monitoring and Alerting Guide

Complete guide for CloudWatch monitoring, logging, and alerting.

## Overview

The monitoring stack provides:
- **CloudWatch Log Groups** - Centralized logging for all Lambda functions
- **CloudWatch Alarms** - Automated alerts for errors and throttling
- **SNS Topics** - Notification delivery to DevOps and Admin teams
- **Health Checks** - Automated system health monitoring
- **CloudWatch Dashboard** - Visual metrics and system overview

## Components

### SNS Topics

**DevOps Topic**: `impressionnistes-devops-{env}`
- System errors and failures
- DynamoDB throttling
- Health check failures
- Infrastructure issues

**Admin Topic**: `impressionnistes-admin-{env}`
- Application-level notifications
- User registration events
- Payment notifications
- Business logic alerts

### CloudWatch Log Groups

All Lambda functions log to CloudWatch with structured JSON formatting:

```
/aws/lambda/ImpressionnistesDatabase-{env}-InitConfigFunction
/aws/lambda/Impressionnistes{env}-HealthCheckFunction
/aws/lambda/... (more functions added in later tasks)
```

**Retention**:
- Dev: 7 days
- Prod: 30 days

### CloudWatch Alarms

**1. DynamoDB Read Throttle Alarm**
- **Metric**: User errors on read operations
- **Threshold**: > 10 errors in 5 minutes
- **Evaluation**: 2 consecutive periods
- **Action**: Notify DevOps topic

**2. DynamoDB Write Throttle Alarm**
- **Metric**: System errors on write operations  
- **Threshold**: > 10 errors in 5 minutes
- **Evaluation**: 2 consecutive periods
- **Action**: Notify DevOps topic

**3. Health Check Failure Alarm**
- **Metric**: Health check function errors
- **Threshold**: > 3 errors in 5 minutes
- **Evaluation**: 2 consecutive periods
- **Action**: Notify DevOps topic

### Health Check Function

Runs every 5 minutes to verify system health.

**Checks**:
- ✅ DynamoDB table accessibility
- ✅ Configuration loaded
- ✅ System components operational

**Endpoint**: Invoke Lambda function directly or via API Gateway (when added)

**Response Format**:
```json
{
  "status": "healthy",
  "timestamp": "2024-11-11T10:00:00Z",
  "environment": "dev",
  "components": {
    "dynamodb": {
      "status": "healthy",
      "table_name": "impressionnistes-registration-dev"
    },
    "configuration": {
      "status": "healthy",
      "message": "Configuration loaded"
    }
  }
}
```

**Status Values**:
- `healthy` - All systems operational
- `degraded` - Some non-critical issues
- `unhealthy` - Critical failures

### CloudWatch Dashboard

**Dashboard Name**: `Impressionnistes-{env}`

**Widgets**:
1. **DynamoDB Read/Write Capacity** - Consumed capacity units
2. **DynamoDB Throttled Requests** - User and system errors
3. **Health Check Function** - Invocations and errors
4. **Health Check Duration** - Function execution time

## Viewing Logs

### Via AWS Console

1. Go to CloudWatch → Log groups
2. Select log group (e.g., `/aws/lambda/ImpressionnistesDatabase-dev-InitConfigFunction`)
3. View log streams

### Via AWS CLI

```bash
# List log groups
aws logs describe-log-groups --query 'logGroups[?starts_with(logGroupName, `/aws/lambda/Impressionnistes`)].logGroupName'

# Tail logs in real-time
aws logs tail /aws/lambda/ImpressionnistesDatabase-dev-InitConfigFunction --follow

# Get recent logs
aws logs tail /aws/lambda/ImpressionnistesDatabase-dev-InitConfigFunction --since 1h

# Search logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/ImpressionnistesDatabase-dev-InitConfigFunction \
  --filter-pattern "ERROR"
```

### Via Makefile

```bash
# View logs for specific function
aws logs tail /aws/lambda/ImpressionnistesDatabase-dev-InitConfigFunction --follow
```

## Viewing Alarms

### Via AWS Console

1. Go to CloudWatch → Alarms
2. Filter by `impressionnistes-{env}`
3. View alarm status and history

### Via AWS CLI

```bash
# List all alarms
aws cloudwatch describe-alarms \
  --alarm-name-prefix impressionnistes-dev

# Get alarm state
aws cloudwatch describe-alarms \
  --alarm-names impressionnistes-dev-dynamodb-read-throttle

# View alarm history
aws cloudwatch describe-alarm-history \
  --alarm-name impressionnistes-dev-health-check-failed \
  --max-records 10
```

## Viewing Dashboard

### Via AWS Console

1. Go to CloudWatch → Dashboards
2. Select `Impressionnistes-{env}`
3. View metrics and graphs

### Via AWS CLI

```bash
# Get dashboard
aws cloudwatch get-dashboard \
  --dashboard-name Impressionnistes-dev
```

## SNS Subscriptions

### Add Email Subscription

```bash
# Subscribe to DevOps topic
aws sns subscribe \
  --topic-arn arn:aws:sns:eu-west-3:ACCOUNT_ID:impressionnistes-devops-dev \
  --protocol email \
  --notification-endpoint your-email@example.com

# Confirm subscription via email link
```

### Add Slack Webhook (via Lambda)

Create a Lambda function to forward SNS to Slack:

```python
import json
import urllib3

def lambda_handler(event, context):
    message = event['Records'][0]['Sns']['Message']
    
    http = urllib3.PoolManager()
    response = http.request(
        'POST',
        'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
        body=json.dumps({'text': message}),
        headers={'Content-Type': 'application/json'}
    )
    
    return {'statusCode': 200}
```

## Running Health Check Manually

```bash
# Invoke health check function
aws lambda invoke \
  --function-name Impressionnistes-dev-HealthCheckFunction \
  --output json \
  response.json

# View response
cat response.json | python3 -m json.tool
```

## Troubleshooting

### No Logs Appearing

**Check log group exists**:
```bash
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/Impressionnistes
```

**Check Lambda has permissions**:
- Lambda execution role should have `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`

### Alarms Not Triggering

**Check alarm state**:
```bash
aws cloudwatch describe-alarms --alarm-names impressionnistes-dev-health-check-failed
```

**Check SNS topic subscriptions**:
```bash
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:eu-west-3:ACCOUNT_ID:impressionnistes-devops-dev
```

**Confirm email subscription**:
- Check email for confirmation link
- Click to confirm subscription

### Health Check Failing

**Check Lambda logs**:
```bash
aws logs tail /aws/lambda/Impressionnistes-dev-HealthCheckFunction --follow
```

**Check DynamoDB table**:
```bash
aws dynamodb describe-table --table-name impressionnistes-registration-dev
```

**Check configuration**:
```bash
make db-view
```

## Metrics to Monitor

### DynamoDB

- **ConsumedReadCapacityUnits** - Read usage
- **ConsumedWriteCapacityUnits** - Write usage
- **UserErrors** - Client-side errors (throttling)
- **SystemErrors** - Server-side errors
- **SuccessfulRequestLatency** - Response time

### Lambda

- **Invocations** - Number of executions
- **Errors** - Failed executions
- **Duration** - Execution time
- **Throttles** - Concurrent execution limits hit
- **ConcurrentExecutions** - Active executions

## Best Practices

1. **Set up email notifications** - Subscribe to SNS topics
2. **Review dashboard daily** - Check for anomalies
3. **Monitor alarm history** - Identify patterns
4. **Adjust thresholds** - Based on actual usage
5. **Enable detailed monitoring** - For production
6. **Set up log insights** - For advanced queries
7. **Create custom metrics** - For business KPIs
8. **Regular health checks** - Verify system status

## Custom Metrics

Add custom metrics to your Lambda functions:

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def put_metric(metric_name, value, unit='Count'):
    cloudwatch.put_metric_data(
        Namespace='Impressionnistes',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit
            }
        ]
    )

# Example usage
put_metric('RegistrationsCreated', 1)
put_metric('PaymentProcessed', amount, 'None')
```

## Log Insights Queries

### Find Errors

```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 20
```

### Function Duration

```
fields @timestamp, @duration
| stats avg(@duration), max(@duration), min(@duration)
```

### Error Rate

```
fields @timestamp
| filter @message like /ERROR/
| stats count() as error_count by bin(5m)
```

## Cost Optimization

- **Log retention**: Shorter retention for dev (7 days)
- **Dashboard refresh**: Manual refresh instead of auto-refresh
- **Alarm evaluation**: Longer periods for non-critical alarms
- **Health check frequency**: Every 5 minutes (adjust if needed)

## Related Commands

```bash
# View all monitoring resources
aws cloudformation describe-stack-resources \
  --stack-name ImpressionnistesMonitoring-dev

# Export dashboard
aws cloudwatch get-dashboard --dashboard-name Impressionnistes-dev > dashboard.json

# Delete old log streams
aws logs delete-log-stream \
  --log-group-name /aws/lambda/ImpressionnistesDatabase-dev-InitConfigFunction \
  --log-stream-name 2024/11/01/[$LATEST]abc123
```

## Support

For monitoring issues:
- Check CloudWatch logs first
- Review alarm history
- Verify SNS subscriptions
- Test health check manually
- Contact DevOps team
