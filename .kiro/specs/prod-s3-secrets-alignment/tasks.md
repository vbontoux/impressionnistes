# Implementation Plan: Production S3 Secrets Alignment

## Overview

This plan deploys the S3-based secrets migration to production. The only code change is updating the certificate ARN in `config.py`. All other tasks are operational: CDK deployments in strict order, secrets upload, verification, and cleanup of the old SecretsStack.

**Critical constraints:**
- Deploy stacks individually — never use `make deploy-backend`, `make deploy`, or `cdk deploy --all`
- Always run `cdk diff` before `cdk deploy` and review for unexpected DynamoDB/Cognito changes
- AWS profile `rcpm-prod` is set automatically by the Makefile when `ENV=prod`
- AuthStack must NOT be deployed during this migration

## Tasks

- [x] 1. Update config.py with wildcard certificate for prod
  - [x] 1.1 Update PROD_CONFIG certificate_arn in `infrastructure/config.py`
    - Change `"certificate_arn": "arn:aws:acm:us-east-1:206478392268:certificate/dbdc7ccc-f905-45b0-94e3-906fcbb2aabe"` to `"certificate_arn": "arn:aws:acm:us-east-1:206478392268:certificate/38b35b2f-317e-48e6-9e1a-08a625f9fd62"`
    - Verify DEV_CONFIG certificate_arn remains unchanged
    - Verify all other PROD_CONFIG values remain unchanged (table_name, region, removal_policy, throttle limits)
    - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Pre-deployment checks
  - [x] 2.1 Verify wildcard certificate is valid
    - Run: `aws acm describe-certificate --certificate-arn arn:aws:acm:us-east-1:206478392268:certificate/38b35b2f-317e-48e6-9e1a-08a625f9fd62 --region us-east-1 --profile rcpm-prod --query 'Certificate.Status'`
    - Expected: `ISSUED`
    - _Requirements: 10.6_
  - [x] 2.2 Verify secrets.prod.json exists and is valid JSON
    - Run: `python3 -c "import json; json.load(open('secrets.prod.json'))"`
    - Confirm it contains keys: `stripe_secret_key`, `stripe_webhook_secret`, `slack_webhook_admin`, `slack_webhook_devops`
    - _Requirements: 3.1_
  - [x] 2.3 Verify CDK synth succeeds for prod
    - Run from `infrastructure/`: `. venv/bin/activate && cdk synth -c env=prod --quiet`
    - Expected: No errors
    - _Requirements: 10.6_

- [x] 3. Deploy DatabaseStack (creates S3 secrets bucket)
  - [x] 3.1 Run cdk diff for DatabaseStack and review changes
    - Run from `infrastructure/`: `. venv/bin/activate && cdk diff ImpressionnistesDatabase-prod -c env=prod`
    - **SAFETY CHECK**: Confirm diff shows ONLY S3 bucket creation (`rcpm-impressionnistes-secrets-prod`)
    - **ABORT if**: Any DynamoDB table modification, replacement, or deletion appears
    - **ABORT if**: Any Cognito resource changes appear
    - _Requirements: 2.2, 7.4, 10.6_
  - [x] 3.2 Deploy DatabaseStack
    - Run from `infrastructure/`: `make deploy-database ENV=prod`
    - Wait for CloudFormation to complete successfully
    - _Requirements: 2.1, 2.3, 2.4, 2.5_

- [x] 4. Upload production secrets to S3
  - [x] 4.1 Sync secrets from secrets.prod.json to S3 bucket
    - Run from `infrastructure/`: `make secrets-sync ENV=prod`
    - Confirm the sync completes without errors
    - _Requirements: 3.1_
  - [x] 4.2 Verify secrets are in S3
    - Run from `infrastructure/`: `make secrets-list ENV=prod`
    - Confirm 4 objects listed: `stripe/api_key`, `stripe/webhook_secret`, `slack/admin_webhook`, `slack/devops_webhook`
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 5. Checkpoint - Verify pre-API state
  - Ensure DatabaseStack deployed successfully and S3 bucket contains all 4 secrets
  - Ensure DynamoDB table is untouched (no schema changes, no data loss)
  - Ask the user if questions arise.

- [x] 6. Build Lambda layer and deploy ApiStack
  - [x] 6.1 Build Lambda layer
    - Run from `infrastructure/`: `make build-layer`
    - Confirm build completes successfully (exit code 0)
    - _Requirements: 4.4, 10.7_
  - [x] 6.2 Run cdk diff for ApiStack and review changes
    - Run from `infrastructure/`: `. venv/bin/activate && cdk diff ImpressionnistesApi-prod -c env=prod`
    - **EXPECTED**: Lambda function updates (SECRETS_BUCKET env var), IAM policy changes (add S3, remove Secrets Manager), layer update
    - **ABORT if**: Any DynamoDB table modification appears
    - **ABORT if**: Any Cognito User Pool changes appear
    - _Requirements: 4.1, 4.2, 4.3, 6.4, 7.4, 10.6_
  - [x] 6.3 Deploy ApiStack
    - Run from `infrastructure/`: `make deploy-api ENV=prod`
    - This runs `build-layer` again (safe) then deploys `ImpressionnistesApi-prod`
    - Wait for CloudFormation to complete successfully
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [x] 7. Deploy FrontendStack with wildcard certificate
  - [x] 7.1 Run cdk diff for FrontendStack and review changes
    - Run from `infrastructure/`: `. venv/bin/activate && cdk diff ImpressiornistesFrontend-prod -c env=prod`
    - **EXPECTED**: CloudFront distribution certificate update (from old cert to wildcard cert)
    - **ABORT if**: S3 bucket replacement or deletion appears
    - **ABORT if**: Any Cognito or DynamoDB changes appear
    - _Requirements: 5.1, 5.2, 6.4, 7.4, 10.6_
  - [x] 7.2 Deploy FrontendStack
    - Run from `infrastructure/`: `make deploy-frontend ENV=prod`
    - Note: CloudFront distribution update takes 5-15 minutes to propagate
    - Wait for CloudFormation to complete successfully
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 8. Checkpoint - Verify all deployments succeeded
  - Ensure all three stacks (Database, Api, Frontend) deployed without errors
  - Ensure no AuthStack was deployed (check with `aws cloudformation describe-stacks --stack-name ImpressionnistesAuth-prod --profile rcpm-prod --query 'Stacks[0].LastUpdatedTime'` — should be older than today)
  - Ask the user if questions arise.

- [x] 9. Verify production functionality
  - [ ] 9.1 Verify S3 secrets are accessible by Lambdas
    - Check CloudWatch logs for recent Lambda invocations: look for successful secret retrieval (no S3 errors)
    - Run: `aws logs filter-log-events --log-group-name /aws/lambda/ImpressionnistesApi-prod --filter-pattern "error" --start-time $(date -v-10M +%s000) --profile rcpm-prod --limit 5`
    - Expected: No S3-related errors
    - _Requirements: 8.4_
  - [ ] 9.2 Verify frontend is accessible with valid HTTPS
    - Run: `curl -sI https://impressionnistes.aviron-rcpm.fr | head -20`
    - Expected: HTTP 200 (or 301/302 redirect), valid TLS connection with wildcard cert
    - _Requirements: 8.3_
  - [ ] 9.3 Verify Stripe payment webhook (check CloudWatch logs)
    - Check recent `confirm_payment_webhook` Lambda logs for successful processing
    - Run: `aws logs filter-log-events --log-group-name /aws/lambda/ImpressionnistesApi-prod --filter-pattern "webhook" --start-time $(date -v-30M +%s000) --profile rcpm-prod --limit 5`
    - If no recent events, trigger a test payment or wait for next real event
    - _Requirements: 8.1_
  - [ ] 9.4 Verify Slack notifications
    - Check recent Lambda logs for Slack webhook delivery
    - Or trigger a test event and confirm Slack message arrives
    - _Requirements: 8.2_
  - [ ] 9.5 Verify infrastructure details
    - Run from `infrastructure/`: `make describe-infra ENV=prod`
    - Confirm API URL, Cognito config, and CloudFront URL are all correct
    - _Requirements: 8.3, 8.5_

- [x] 10. Destroy old SecretsStack
  - [x] 10.1 Confirm old SecretsStack still exists
    - Run: `aws cloudformation describe-stacks --stack-name ImpressionnistesSecrets-prod --profile rcpm-prod --query 'Stacks[0].StackStatus'`
    - Expected: Some active status (CREATE_COMPLETE or UPDATE_COMPLETE)
    - _Requirements: 9.1_
  - [x] 10.2 Delete old SecretsStack
    - Run: `aws cloudformation delete-stack --stack-name ImpressionnistesSecrets-prod --profile rcpm-prod`
    - Wait for deletion: `aws cloudformation wait stack-delete-complete --stack-name ImpressionnistesSecrets-prod --profile rcpm-prod`
    - _Requirements: 9.2, 9.3_
  - [x] 10.3 Verify old SecretsStack is deleted
    - Run: `aws cloudformation describe-stacks --stack-name ImpressionnistesSecrets-prod --profile rcpm-prod`
    - Expected: Stack not found error (or DELETE_COMPLETE status)
    - If deletion failed, investigate dependencies before retrying
    - _Requirements: 9.4, 9.5_

- [x] 11. Final checkpoint - Migration complete
  - Ensure all verifications passed
  - Ensure old SecretsStack is destroyed
  - Confirm production is fully operational on S3-based secrets
  - Ask the user if questions arise.

## Notes

- All tasks are required — none are optional
- Deployment order is strict: Database → Secrets Upload → API → Frontend → Verify → Cleanup
- The `rcpm-prod` AWS profile is set automatically by the Makefile when `ENV=prod`
- If any `cdk diff` shows unexpected DynamoDB or Cognito changes, ABORT immediately
- The old SecretsStack is destroyed LAST as a safety net — Secrets Manager secrets remain available as fallback until step 10
- CloudFront distribution updates (step 7) take 5-15 minutes to propagate globally
- Each task references specific requirements for traceability
