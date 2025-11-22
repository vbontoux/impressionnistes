# Stripe Payment Integration Setup

This document explains how to set up Stripe payment integration for the Course des Impressionnistes registration system.

## Prerequisites

1. A Stripe account (sign up at https://stripe.com)
2. AWS CLI configured with appropriate permissions
3. Access to AWS Secrets Manager

## Step 1: Get Stripe API Keys

### For Development (Test Mode)
1. Log in to your Stripe Dashboard
2. Navigate to **Developers** → **API keys**
3. Copy your **Secret key** (starts with `sk_test_`)
4. Keep this key secure - never commit it to version control

### For Production (Live Mode)
1. In Stripe Dashboard, toggle to **Live mode**
2. Navigate to **Developers** → **API keys**
3. Copy your **Secret key** (starts with `sk_live_`)

## Step 2: Configure secrets.json

### Create secrets.json from template

```bash
cd infrastructure
cp secrets.json.example secrets.json
```

### Edit secrets.json with your Stripe keys

```json
{
  "slack_webhook_admin": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  "slack_webhook_devops": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  "stripe_secret_key_dev": "sk_test_YOUR_KEY_HERE",
  "stripe_secret_key_prod": "sk_live_YOUR_KEY_HERE",
  "stripe_webhook_secret_dev": "whsec_YOUR_DEV_SECRET",
  "stripe_webhook_secret_prod": "whsec_YOUR_PROD_SECRET"
}
```

**Important:** Never commit `secrets.json` to git! It's already in `.gitignore`.

## Step 3: Set Up Stripe Webhook

### Create Webhook Endpoint

1. In Stripe Dashboard, go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Enter your webhook URL:
   - Development: `https://YOUR_API_ID.execute-api.eu-west-3.amazonaws.com/dev/payment/webhook`
   - Production: `https://YOUR_API_ID.execute-api.eu-west-3.amazonaws.com/prod/payment/webhook`

4. Select events to listen to:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`

5. Click **Add endpoint**

### Get Webhook Signing Secret

After creating the webhook:
1. Click on the webhook endpoint
2. Click **Reveal** under **Signing secret**
3. Copy the secret (starts with `whsec_`)

### Add Webhook Secret to secrets.json

Edit `infrastructure/secrets.json` and add the webhook secret:

```json
{
  "stripe_webhook_secret_dev": "whsec_YOUR_DEV_SECRET_HERE",
  "stripe_webhook_secret_prod": "whsec_YOUR_PROD_SECRET_HERE"
}
```

## Step 4: Deploy Secrets to AWS

Deploy the secrets stack to create all secrets in AWS Secrets Manager:

```bash
cd infrastructure

# For development
make deploy-secrets ENV=dev

# For production
make deploy-secrets ENV=prod
```

This single command will create all secrets (Stripe API keys, webhook secrets, Slack webhooks) in AWS Secrets Manager.

## Step 5: Configure Stripe Receipt Emails

1. In Stripe Dashboard, go to **Settings** → **Emails**
2. Enable **Successful payments** emails
3. Customize the email template:
   - Add RCPM logo
   - Set brand colors
   - Configure email language settings

## Step 6: Deploy Infrastructure

After deploying secrets, deploy the rest of the infrastructure:

```bash
cd infrastructure
make deploy-dev  # For development
# or
make deploy-prod  # For production
```

## Step 7: Test Payment Integration

### Test with Stripe Test Cards

Use these test card numbers in development:

- **Successful payment**: `4242 4242 4242 4242`
- **Requires authentication (3D Secure)**: `4000 0025 0000 3155`
- **Declined payment**: `4000 0000 0000 9995`

Use any future expiry date, any 3-digit CVC, and any postal code.

### Test Webhook Locally

For local testing, use Stripe CLI:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login to Stripe
stripe login

# Forward webhooks to local endpoint
stripe listen --forward-to http://localhost:3000/payment/webhook

# Trigger test events
stripe trigger payment_intent.succeeded
```

## Updating Secrets

To update secrets:

1. Edit `infrastructure/secrets.json` with new values
2. Redeploy the secrets stack:

```bash
cd infrastructure
make deploy-secrets ENV=dev  # or ENV=prod
```

The secrets stack will update all secrets in AWS Secrets Manager.

## Security Best Practices

1. **Never commit secrets to version control**
2. **Use different keys for dev and production**
3. **Rotate API keys periodically**
4. **Monitor webhook signature verification failures**
5. **Set up CloudWatch alarms for payment failures**
6. **Restrict IAM permissions** - only Lambda functions should access secrets

## Troubleshooting

### Lambda can't access secrets

Check IAM permissions:
```bash
aws iam get-role-policy \
    --role-name YOUR_LAMBDA_ROLE \
    --policy-name SecretsManagerPolicy
```

### Webhook signature verification fails

1. Verify webhook secret is correct in Secrets Manager
2. Check that raw request body is used (not parsed JSON)
3. Ensure Stripe-Signature header is passed correctly

### Payment intent creation fails

1. Check Stripe API key is valid
2. Verify amount is in correct format (cents)
3. Check CloudWatch logs for detailed error messages

## Monitoring

Monitor payment operations in:
- **Stripe Dashboard** → **Payments**
- **AWS CloudWatch** → Lambda function logs
- **DynamoDB** → Payment records table

## Support

- Stripe Documentation: https://stripe.com/docs
- Stripe Support: https://support.stripe.com
- AWS Secrets Manager: https://docs.aws.amazon.com/secretsmanager/
