---
inclusion: auto
---

# Deployment Order — Frontend Requires Two-Stage Deploy on Fresh Environments

## The Problem

On a fresh environment (first-ever deployment), the frontend stack is deployed BEFORE the API stack due to CDK's dependency resolution order:

1. DatabaseStack
2. MonitoringStack
3. **FrontendStack** ← deployed here (no API URL available yet)
4. AuthStack
5. ApiStack ← API URL only available after this

The frontend build (`npm run build`) bakes environment variables (API URL, Cognito config) into the static bundle. On first deploy, these values don't exist yet because the API stack hasn't been created.

## The Fix

After a fresh `make deploy-backend ENV=<env>`, you MUST redeploy the frontend:

```bash
make deploy-frontend ENV=<env>
```

This will rebuild the frontend with the correct environment variables (API URL, Cognito config) now that all backend stacks exist, and redeploy to S3/CloudFront.

## When This Applies

- **First deployment to a new environment** (fresh stacks) — ALWAYS needs two-stage frontend deploy
- **Subsequent deployments** — NOT needed (API URL doesn't change between deploys)
- **After destroying and recreating stacks** — ALWAYS needs two-stage frontend deploy

## When Assisting with Deployments

If you are helping deploy a fresh environment:
1. Deploy backend: `make deploy-backend ENV=<env>`
2. Redeploy frontend: `make deploy-frontend ENV=<env>`

Do NOT consider the deployment complete after step 1 alone on a fresh environment.
