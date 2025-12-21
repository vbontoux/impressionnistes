# Secrets Management

This document explains how secrets are managed in the Course des Impressionnistes registration system.

## Overview

All application secrets (Stripe API keys, Slack webhooks, etc.) are managed through:
1. **Local file**: `infrastructure/secrets.json` (not committed to git)
2. **CDK Stack**: `SecretsStack` reads `secrets.json` and creates AWS Secrets Manager secrets
3. **AWS Secrets Manager**: Stores encrypted secrets that Lambda functions retrieve at runtime

## Quick Start

### 1. Create secrets.json

```bash
cd infrastructure
cp secrets.json.example secrets.json
# Edit secrets.json with your actual secrets
```

### 2. Deploy Secrets

```bash
# Development environment
make deploy-secrets ENV=dev

# Production environment  
make deploy-secrets ENV=prod
```

That's it! All secrets are now in AWS Secrets Manager.

## Quick Reference - Common Commands

```bash
# List all secrets
make secrets-list

# Show Stripe secrets (partial, safe)
make secrets-show-stripe

# Update Stripe API key
make secrets-update-stripe STRIPE_API_KEY=sk_test_xxx

# Deploy all secrets from secrets.json
make deploy-secrets

# For production environment
make secrets-list ENV=prod
```

## secrets.json Format

```json
{
  "slack_webhook_admin": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  "slack_webhook_devops": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  "stripe_secret_key_dev": "sk_test_...",
  "stripe_secret_key_prod": "sk_live_...",
  "stripe_webhook_secret_dev": "whsec_...",
  "stripe_webhook_secret_prod": "whsec_..."
}
```

## Secrets Created in AWS

The secrets stack creates the following secrets in AWS Secrets Manager:

### Stripe Secrets
- **Name**: `impressionnistes/stripe/api_key`
  - **Content**: `{"api_key": "sk_test_..." or "sk_live_..."}`
  - **Used by**: Payment Lambda functions
  - **Environment-specific**: Yes (uses `stripe_secret_key_dev` or `stripe_secret_key_prod`)

- **Name**: `impressionnistes/stripe/webhook_secret`
  - **Content**: `{"webhook_secret": "whsec_..."}`
  - **Used by**: Webhook handler Lambda
  - **Environment-specific**: Yes (uses `stripe_webhook_secret_dev` or `stripe_webhook_secret_prod`)

### Slack Secrets
- **Name**: `impressionnistes/slack/admin_webhook`
  - **Content**: `{"webhook_url": "https://hooks.slack.com/..."}`
  - **Used by**: Admin notification functions
  - **Environment-specific**: No (same for dev and prod)

- **Name**: `impressionnistes/slack/devops_webhook`
  - **Content**: `{"webhook_url": "https://hooks.slack.com/..."}`
  - **Used by**: DevOps/error notification functions
  - **Environment-specific**: No (same for dev and prod)

## How Lambda Functions Access Secrets

Lambda functions use the `stripe_client.py` utility:

```python
from stripe_client import get_stripe_api_key, get_webhook_secret

# Automatically retrieves from AWS Secrets Manager
api_key = get_stripe_api_key()
webhook_secret = get_webhook_secret()
```

The secrets are:
- Retrieved from AWS Secrets Manager at runtime
- Cached in memory for performance
- Never logged or exposed

## IAM Permissions

Lambda functions need these permissions (automatically granted by CDK):

```python
{
    "Effect": "Allow",
    "Action": "secretsmanager:GetSecretValue",
    "Resource": "arn:aws:secretsmanager:*:*:secret:impressionnistes/*"
}
```

## Viewing Secrets

### List All Secrets

View all secrets without showing their values:

```bash
make secrets-list
```

Output shows:
- Secret names
- Last changed date
- Organized by type (Stripe, Slack)

### Show Stripe Secrets (Partial)

Show Stripe secrets with partial masking for security:

```bash
make secrets-show-stripe
```

Shows:
- First 20 characters + last 4 characters of API key
- First 20 characters + last 4 characters of webhook secret

### Show All Secrets (Full Values)

⚠️ **WARNING**: This displays full secret values!

```bash
make secrets-show
```

Shows complete values for:
- Stripe API key
- Stripe webhook secret
- Slack admin webhook
- Slack DevOps webhook

## Updating Secrets

### Method 1: Using Makefile Commands (Recommended)

Update Stripe API key only:
```bash
make secrets-update-stripe STRIPE_API_KEY=sk_test_your_key_here
```

Update both API key and webhook secret:
```bash
make secrets-update-stripe \
  STRIPE_API_KEY=sk_test_your_key_here \
  STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
```

### Method 2: Using CDK (For All Secrets)

1. Edit `infrastructure/secrets.json`
2. Run: `make deploy-secrets ENV=dev`

### Method 3: Using AWS CLI

```bash
aws secretsmanager update-secret \
    --secret-id impressionnistes/stripe/api_key \
    --secret-string '{"api_key":"sk_test_NEW_KEY"}' \
    --region eu-west-3
```

### Method 4: Using AWS Console

1. Go to AWS Secrets Manager console
2. Find the secret (e.g., `impressionnistes/stripe/api_key`)
3. Click "Retrieve secret value"
4. Click "Edit"
5. Update the JSON value
6. Click "Save"

## Security Best Practices

### ✅ DO
- Keep `secrets.json` out of version control (already in `.gitignore`)
- Use different Stripe keys for dev and prod
- Rotate secrets periodically
- Use AWS Secrets Manager rotation for sensitive secrets
- Monitor CloudWatch logs for secret access failures
- Use least-privilege IAM permissions

### ❌ DON'T
- Commit `secrets.json` to git
- Share secrets via email or chat
- Use production secrets in development
- Log secret values
- Hard-code secrets in Lambda functions

## Troubleshooting

### Error: "secrets.json not found"

```bash
cd infrastructure
cp secrets.json.example secrets.json
# Edit with your secrets
```

### Error: "Access Denied" when Lambda retrieves secret

Check IAM permissions:
```bash
aws iam get-role-policy \
    --role-name YOUR_LAMBDA_ROLE \
    --policy-name SecretsManagerPolicy
```

### Error: "Secret not found"

Deploy the secrets stack:
```bash
make deploy-secrets ENV=dev
```

### Verify secrets exist

Using Makefile commands:
```bash
# List all secrets
make secrets-list

# Show Stripe secrets (partial, safe)
make secrets-show-stripe
```

Using AWS CLI directly:
```bash
# List all secrets
aws secretsmanager list-secrets \
    --query 'SecretList[?starts_with(Name, `impressionnistes/`)].Name' \
    --output table

# Get a specific secret value
aws secretsmanager get-secret-value \
    --secret-id impressionnistes/stripe/api_key \
    --query SecretString \
    --output text | python3 -m json.tool
```

## Cost

AWS Secrets Manager pricing (as of 2024):
- **Storage**: $0.40 per secret per month
- **API calls**: $0.05 per 10,000 API calls

For this application (4 secrets):
- **Monthly cost**: ~$1.60/month
- **API calls**: Minimal (Lambda caches secrets)

## Secrets Lifecycle

### Development Workflow
1. Developer creates `secrets.json` locally
2. Runs `make deploy-secrets ENV=dev`
3. Secrets are created in AWS Secrets Manager
4. Lambda functions retrieve secrets at runtime

### Production Deployment
1. Update `secrets.json` with production keys
2. Run `make deploy-secrets ENV=prod`
3. Production secrets are created/updated
4. Production Lambda functions use production secrets

### Secret Rotation
1. Generate new secret (e.g., new Stripe API key)
2. Update `secrets.json`
3. Run `make deploy-secrets`
4. Old secret is replaced
5. Lambda functions automatically use new secret (may need restart)

## Stack Removal Policy

Secrets have `RemovalPolicy.RETAIN`:
- When you delete the CDK stack, secrets are **NOT** deleted
- This prevents accidental data loss
- To delete secrets, use AWS Console or CLI manually

## References

- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [Stripe API Keys](https://stripe.com/docs/keys)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
