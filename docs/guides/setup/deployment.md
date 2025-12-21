# Deployment Guide

Complete guide for deploying the Course des Impressionnistes Registration System to dev or production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Initial Deployment](#initial-deployment)
- [Updating Deployments](#updating-deployments)
- [Environment-Specific Commands](#environment-specific-commands)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

1. **AWS CLI** - Configured with appropriate credentials
   ```bash
   aws configure
   ```

2. **AWS CDK** - Installed globally
   ```bash
   npm install -g aws-cdk
   ```

3. **Python 3.11+** - For Lambda functions

4. **Node.js 20+** - For frontend build

### AWS Account Setup

**Dev Environment:**
- Uses your default AWS credentials
- Account: Your dev AWS account

**Production Environment:**
- Uses AWS profile named `rcpm`
- Account: Separate production AWS account
- Configure profile in `~/.aws/credentials`:
  ```ini
  [rcpm]
  aws_access_key_id = YOUR_PROD_ACCESS_KEY
  aws_secret_access_key = YOUR_PROD_SECRET_KEY
  region = eu-west-3
  ```

---

## Environment Configuration

### 1. Backend Secrets

Create environment-specific secrets files:

**Dev: `infrastructure/secrets.dev.json`**
```json
{
  "slack_webhook_admin": "https://hooks.slack.com/services/YOUR_DEV_ADMIN_WEBHOOK",
  "slack_webhook_devops": "https://hooks.slack.com/services/YOUR_DEV_DEVOPS_WEBHOOK",
  "stripe_secret_key": "sk_test_YOUR_TEST_KEY",
  "stripe_webhook_secret": "whsec_YOUR_TEST_WEBHOOK_SECRET"
}
```

**Prod: `infrastructure/secrets.prod.json`**
```json
{
  "slack_webhook_admin": "https://hooks.slack.com/services/YOUR_PROD_ADMIN_WEBHOOK",
  "slack_webhook_devops": "https://hooks.slack.com/services/YOUR_PROD_DEVOPS_WEBHOOK",
  "stripe_secret_key": "sk_live_YOUR_LIVE_KEY",
  "stripe_webhook_secret": "whsec_YOUR_PROD_WEBHOOK_SECRET"
}
```

### 2. Frontend Configuration

Create environment-specific Stripe publishable keys:

**Dev: `frontend/.env.dev`**
```env
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_TEST_PUBLISHABLE_KEY
```

**Prod: `frontend/.env.prod`**
```env
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_LIVE_PUBLISHABLE_KEY
```

**Local Development: `frontend/.env`**
```env
VITE_API_URL=https://YOUR_DEV_API_URL/dev/
VITE_COGNITO_DOMAIN=https://impressionnistes-dev.auth.eu-west-3.amazoncognito.com
VITE_COGNITO_CLIENT_ID=YOUR_CLIENT_ID
VITE_COGNITO_REDIRECT_URI=http://localhost:3000/callback
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_TEST_PUBLISHABLE_KEY
```

---

## Initial Deployment

### Dev Environment

1. **Setup infrastructure tools:**
   ```bash
   cd infrastructure
   make setup
   ```

2. **Bootstrap CDK (first time only):**
   ```bash
   make bootstrap ENV=dev
   ```

3. **Deploy all stacks:**
   ```bash
   make deploy-dev
   ```

4. **Deploy frontend (2-stage for correct CloudFront URL):**
   ```bash
   make deploy-frontend-complete-dev
   ```

5. **Get infrastructure details:**
   ```bash
   make describe-infra ENV=dev
   ```
   Copy the API URL and Cognito details to `frontend/.env` for local development.

### Production Environment

1. **Ensure AWS profile is configured** (see Prerequisites)

2. **Bootstrap CDK for production account (first time only):**
   ```bash
   make bootstrap ENV=prod
   ```

3. **Deploy all stacks:**
   ```bash
   make deploy-prod
   ```
   You'll be prompted to type `DEPLOY PROD` to confirm.

4. **Deploy frontend (2-stage):**
   ```bash
   make deploy-frontend-complete-prod
   ```
   You'll be prompted to type `DEPLOY PROD` to confirm.

5. **Get infrastructure details:**
   ```bash
   make describe-infra ENV=prod
   ```

---

## Updating Deployments

### Backend Updates (Lambda, API, Database)

**Dev:**
```bash
cd infrastructure
make deploy-dev
```

**Prod:**
```bash
cd infrastructure
make deploy-prod
```

### Frontend Updates

**Quick update (when CloudFront URL hasn't changed):**
```bash
# Dev
make deploy-frontend-dev

# Prod
make deploy-frontend-prod
```

**Complete update (2-stage, when CloudFront URL might have changed):**
```bash
# Dev
make deploy-frontend-complete-dev

# Prod
make deploy-frontend-complete-prod
```

### Specific Stack Updates

**Auth stack only:**
```bash
make deploy-auth ENV=dev
# or
make deploy-auth ENV=prod
```

**Secrets only:**
```bash
make deploy-secrets ENV=dev
# or
make deploy-secrets ENV=prod
```

---

## Environment-Specific Commands

All commands support `ENV=dev` or `ENV=prod`. The Makefile automatically uses the correct AWS profile.

### Database Management

**Export database:**
```bash
make db-export ENV=dev
make db-export ENV=prod
```

**View database contents:**
```bash
make db-view ENV=dev
make db-view ENV=prod
```

**Run migration:**
```bash
make db-migrate MIGRATION=migration_name TEAM_MANAGER_ID=your-user-id ENV=dev
```

### Cognito User Management

**List users:**
```bash
make cognito-list-users ENV=dev
make cognito-list-users ENV=prod
```

**Create admin user:**
```bash
make cognito-create-admin EMAIL=admin@example.com ENV=dev
make cognito-create-admin EMAIL=admin@example.com ENV=prod
```

**Add user to group:**
```bash
make cognito-add-to-group EMAIL=user@example.com GROUP=admins ENV=dev
```

### Infrastructure Info

**Get API URLs and Cognito config:**
```bash
make describe-infra ENV=dev
make describe-infra ENV=prod
```

**View AWS costs:**
```bash
make costs ENV=dev
make costs ENV=prod
```

---

## Troubleshooting

### CloudFront URL Issues

**Problem:** Frontend has wrong redirect URI (shows PLACEHOLDER)

**Solution:** Run complete 2-stage deployment:
```bash
make deploy-frontend-complete-dev
# or
make deploy-frontend-complete-prod
```

### AWS Profile Issues

**Problem:** "Unable to locate credentials" when deploying to prod

**Solution:** Verify AWS profile is configured:
```bash
aws configure list --profile rcpm
```

### Secrets Not Found

**Problem:** "secrets.dev.json not found"

**Solution:** Create the environment-specific secrets file:
```bash
cp infrastructure/secrets.json infrastructure/secrets.dev.json
# Edit secrets.dev.json with your dev secrets
```

### Build Failures

**Problem:** Frontend build fails

**Solution:** 
1. Check that infrastructure is deployed first (API and Auth stacks)
2. Verify `.env.dev` or `.env.prod` exists with Stripe key
3. Run build manually to see detailed errors:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

### Stack Update Failures

**Problem:** CDK deployment fails with "Resource already exists"

**Solution:** 
1. Check CloudFormation console for stuck stacks
2. Use fix command:
   ```bash
   make fix-stuck-stack ENV=dev
   ```

### Database Migration Issues

**Problem:** Migration fails or data is inconsistent

**Solution:**
1. Check migration logs in CloudWatch
2. Export database to verify state:
   ```bash
   make db-export ENV=dev
   ```
3. See `functions/migrations/README.md` for migration troubleshooting

---

## Deployment Checklist

### Before Deploying to Production

- [ ] All secrets configured in `secrets.prod.json`
- [ ] Production Stripe publishable key in `frontend/.env.prod`
- [ ] AWS profile `rcpm` configured and tested
- [ ] Tested thoroughly in dev environment
- [ ] Database backup created (if updating existing prod)
- [ ] Slack webhooks point to production channels
- [ ] Custom domain configured (if applicable)

### After Deployment

- [ ] Verify API is accessible: `make describe-infra ENV=prod`
- [ ] Test frontend URL in browser
- [ ] Verify Cognito login works
- [ ] Test a complete user registration flow
- [ ] Verify Stripe payment integration
- [ ] Check CloudWatch logs for errors
- [ ] Verify database has correct initial data

---

## Quick Reference

```bash
# Dev deployment (full stack)
make deploy-dev
make deploy-frontend-complete-dev

# Prod deployment (full stack)
make deploy-prod
make deploy-frontend-complete-prod

# Quick frontend update
make deploy-frontend-dev
make deploy-frontend-prod

# Get infrastructure info
make describe-infra ENV=dev
make describe-infra ENV=prod

# Database operations
make db-export ENV=dev
make db-view ENV=dev

# User management
make cognito-list-users ENV=dev
make cognito-create-admin EMAIL=admin@example.com ENV=dev
```

---

## Additional Resources

- [Makefile Commands](infrastructure/Makefile) - Run `make help` for full list
- [Database Migrations](functions/migrations/README.md)
- [Frontend Testing](FRONTEND_TESTING.md)
- [Lambda Testing](LAMBDA_TESTING_GUIDE.md)
- [API Gateway Implementation](API_GATEWAY_IMPLEMENTATION.md)
