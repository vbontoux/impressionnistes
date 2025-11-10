# Infrastructure - AWS CDK

This directory contains the AWS CDK infrastructure code for the Course des Impressionnistes Registration System.

## Prerequisites

- Python 3.11+
- AWS CLI configured with credentials
- AWS CDK CLI installed globally: `npm install -g aws-cdk`
- AWS account with appropriate permissions

## Project Structure

```
infrastructure/
├── app.py                    # CDK app entry point
├── cdk.json                  # CDK configuration
├── requirements.txt          # Python dependencies
├── deploy.sh                 # Deployment script
├── destroy.sh                # Destruction script
├── stacks/
│   ├── database_stack.py     # DynamoDB table
│   ├── api_stack.py          # API Gateway and Lambda
│   ├── frontend_stack.py     # S3 and CloudFront
│   └── monitoring_stack.py   # CloudWatch and SNS
└── lambda_layers/            # Shared Lambda dependencies
```

## Stack Architecture

### DatabaseStack
- DynamoDB table with single-table design
- GSI indexes for efficient querying
- Encryption at rest
- Point-in-time recovery (prod only)
- On-demand billing

### ApiStack
- API Gateway REST API
- Lambda functions for all endpoints
- Cognito authorizers
- CORS configuration
- Request/response transformations

### FrontendStack
- S3 bucket for static website hosting
- CloudFront distribution with CDN
- Custom domain and SSL certificate
- Cache behaviors and security headers

### MonitoringStack
- CloudWatch log groups
- CloudWatch alarms for errors and throttling
- SNS topics for notifications
- CloudWatch dashboards

## Environment Configuration

Two environments are supported:
- **dev**: Development environment with relaxed settings
- **prod**: Production environment with enhanced security and backups

Environment-specific configuration is defined in `cdk.json` under the `context` section.

## Installation

### Set Up Virtual Environment

**Automated (recommended):**
```bash
# From project root
./setup-venv.sh  # macOS/Linux
# or
.\setup-venv.ps1  # Windows PowerShell
```

**Manual:**
```bash
cd infrastructure
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Important:** Always activate the virtual environment before running CDK commands:
```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

## Deployment

### First-time Setup

Bootstrap CDK in your AWS account (only needed once per account/region):

```bash
source venv/bin/activate  # Activate virtual environment first
cdk bootstrap --context env=dev
```

### Deploy to Development

**Using deployment script (recommended - handles venv automatically):**
```bash
./deploy.sh dev
```

**Manual deployment:**
```bash
source venv/bin/activate
cdk deploy --all --context env=dev
deactivate
```

### Deploy to Production

**Using deployment script (recommended):**
```bash
./deploy.sh prod
```

**Manual deployment:**
```bash
source venv/bin/activate
cdk deploy --all --context env=prod
deactivate
```

### Deploy Specific Stack

```bash
source venv/bin/activate
cdk deploy ImpressionnistesDatabase-dev --context env=dev
deactivate
```

## Useful CDK Commands

**Note:** Always activate the virtual environment first: `source venv/bin/activate`

### Synthesize CloudFormation Templates

```bash
source venv/bin/activate
cdk synth --context env=dev
```

### Show Differences

```bash
source venv/bin/activate
cdk diff --context env=dev
```

### List All Stacks

```bash
source venv/bin/activate
cdk list --context env=dev
```

### Destroy Environment

**Using script (recommended):**
```bash
./destroy.sh dev
```

**Manual:**
```bash
source venv/bin/activate
cdk destroy --all --context env=dev
deactivate
```

## Environment Variables

The following environment variables are used:

- `CDK_DEFAULT_ACCOUNT`: AWS account ID (auto-detected)
- `CDK_DEFAULT_REGION`: AWS region (default: eu-west-3)

## Stack Dependencies

Stacks are deployed in the following order:

1. **DatabaseStack** - No dependencies
2. **MonitoringStack** - No dependencies
3. **ApiStack** - Depends on DatabaseStack
4. **FrontendStack** - Depends on ApiStack

## Configuration Parameters

Environment-specific parameters in `cdk.json`:

- `region`: AWS region for deployment
- `table_name`: DynamoDB table name
- `enable_point_in_time_recovery`: Enable PITR for DynamoDB
- `removal_policy`: Stack removal policy (DESTROY for dev, RETAIN for prod)

## Outputs

After deployment, CDK will output important values:

- API Gateway URL
- CloudFront distribution URL
- DynamoDB table name
- S3 bucket name

## Troubleshooting

### Bootstrap Issues

If you encounter bootstrap errors:

```bash
cdk bootstrap aws://ACCOUNT-ID/REGION
```

### Permission Errors

Ensure your AWS credentials have the following permissions:
- CloudFormation
- DynamoDB
- Lambda
- API Gateway
- S3
- CloudFront
- Cognito
- SES
- CloudWatch
- IAM (for role creation)

### Stack Rollback

If a deployment fails, CDK will automatically rollback. To retry:

```bash
cdk deploy --all --context env=dev --force
```

## Security Notes

- All data is encrypted at rest
- HTTPS/TLS enforced for all communications
- IAM roles follow least-privilege principle
- Secrets managed via AWS Secrets Manager
- CloudWatch logs for audit trail

## Cost Optimization

- DynamoDB uses on-demand billing
- Lambda functions scale to zero when not in use
- CloudFront caching reduces origin requests
- S3 lifecycle policies for old versions

## Backup and Recovery

- DynamoDB point-in-time recovery (prod)
- Daily backups to S3
- CloudFormation templates for infrastructure recovery
- Version control for all infrastructure code

## Support

For infrastructure issues, contact the DevOps team or refer to the main project README.
