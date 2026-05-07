# Implementation Plan: Dev Environment Same-Account Migration

## Overview

Migrate the dev environment into the same AWS account as production by replacing AWS Secrets Manager with S3-based secrets storage, updating IAM policies, removing the SecretsStack, and updating operational tooling. Tasks are ordered for safe incremental deployment: infrastructure first, then runtime code, then cleanup, then tooling.

## Tasks

- [x] 1. Add S3 secrets bucket to DatabaseStack
  - [x] 1.1 Add S3 bucket to `infrastructure/stacks/database_stack.py`
    - Import `aws_s3 as s3` in the stack file
    - Create `self.secrets_bucket` as an S3 bucket named `impressionnistes-secrets-{env_name}`
    - Configure: `BlockPublicAccess.BLOCK_ALL`, `BucketEncryption.S3_MANAGED`, `versioning=True`
    - Set `removal_policy=RemovalPolicy.DESTROY` and `auto_delete_objects=True` for dev, `RETAIN` for prod
    - Expose `self.secrets_bucket` for cross-stack reference by ApiStack
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 2. Update ApiStack IAM policies and environment variables
  - [x] 2.1 Add `SECRETS_BUCKET` environment variable and S3 slack/* IAM grant to `_create_lambda_function`
    - In `infrastructure/stacks/api_stack.py`, add `database_stack.secrets_bucket.bucket_name` as `SECRETS_BUCKET` to `self.common_env`
    - Replace the `secretsmanager:GetSecretValue` policy for `impressionnistes/slack/*` with an `s3:GetObject` policy on `{database_stack.secrets_bucket.bucket_arn}/slack/*`
    - _Requirements: 2.2, 2.3, 2.4_

  - [x] 2.2 Replace Stripe Secrets Manager IAM with S3 IAM in `_create_payment_functions`
    - Replace both `secretsmanager:GetSecretValue` grants (for `payment_intent_function` and `webhook_function`) with `s3:GetObject` on `{database_stack.secrets_bucket.bucket_arn}/stripe/*`
    - _Requirements: 2.1, 2.3_

- [x] 3. Rewrite secrets module to use S3
  - [x] 3.1 Rewrite `functions/shared/secrets_manager.py` to use S3 client
    - Replace `boto3.client('secretsmanager')` with `boto3.client('s3')`
    - Read bucket name from `os.environ['SECRETS_BUCKET']`
    - Rewrite `get_secret(object_key, field)` to call `s3_client.get_object(Bucket=bucket, Key=object_key)`, parse JSON body, extract field
    - Preserve in-memory caching behavior (`_secrets_cache` dict)
    - Keep the same public API: `get_stripe_api_key`, `get_stripe_webhook_secret`, `get_slack_admin_webhook`, `get_slack_devops_webhook`, `clear_cache`
    - Update `get_stripe_api_key()` to call `get_secret('stripe/api_key', 'api_key')`
    - Update `get_stripe_webhook_secret()` to call `get_secret('stripe/webhook_secret', 'webhook_secret')`
    - Update `get_slack_admin_webhook()` to call `get_secret('slack/admin_webhook', 'webhook_url')` with try/except returning empty string
    - Update `get_slack_devops_webhook()` to call `get_secret('slack/devops_webhook', 'webhook_url')` with try/except returning empty string
    - Preserve error handling: log + raise for S3 errors
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

  - [x] 3.2 Write unit tests for the S3-based secrets module
    - Create `tests/unit/test_secrets_manager.py`
    - Mock S3 client using `moto` or `unittest.mock`
    - Test `get_stripe_api_key` returns correct value from S3 object `stripe/api_key`
    - Test `get_stripe_webhook_secret` returns correct value from S3 object `stripe/webhook_secret`
    - Test `get_slack_admin_webhook` returns correct value from S3 object `slack/admin_webhook`
    - Test `get_slack_devops_webhook` returns correct value from S3 object `slack/devops_webhook`
    - Test caching: second call does not make another S3 request
    - Test `clear_cache` resets cache so next call hits S3 again
    - Test S3 error (NoSuchKey) raises exception
    - Test Slack getters return empty string on S3 error
    - Test bucket name is read from `SECRETS_BUCKET` env var
    - Test round-trip: store JSON `{"field": "value"}` in mock S3, retrieve via `get_secret`, assert equality (use parametrized test with edge cases: unicode, special JSON chars, long strings)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 7.6_

  - [x] 3.3 Write property test for secret value round-trip
    - **Property 1: Secret value round-trip**
    - **Validates: Requirements 7.6, 7.1, 3.3, 3.4, 3.5, 3.6**
    - Create parametrized test in `tests/unit/test_secrets_manager.py` with diverse edge-case values (unicode, JSON special chars, empty-ish strings, very long strings, strings with quotes and backslashes)
    - For each value: store as `{"test_field": value}` JSON in mock S3, retrieve via `get_secret("test/key", "test_field")`, assert result equals original value

- [x] 4. Checkpoint — Verify secrets module and infrastructure
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Remove SecretsStack from CDK app
  - [x] 5.1 Remove SecretsStack from `infrastructure/app.py`
    - Remove `from stacks.secrets_stack import SecretsStack` import
    - Remove `secrets_stack = SecretsStack(...)` instantiation
    - Remove `secrets_stack` from the `Tags.of(stack)` loop list
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 5.2 Delete `infrastructure/stacks/secrets_stack.py`
    - Delete the file entirely
    - _Requirements: 4.4_

- [x] 6. Update config.py with dev certificate ARN placeholder
  - Update `DEV_CONFIG["certificate_arn"]` in `infrastructure/config.py` to a placeholder value `arn:aws:acm:us-east-1:206478392268:certificate/PLACEHOLDER-CREATE-WILDCARD-CERT-FIRST`
  - Add a comment explaining a wildcard certificate (`*.aviron-rcpm.fr`) will be created in task 10.1 and shared across all environments
  - Leave `PROD_CONFIG["certificate_arn"]` unchanged for now (will be updated to use the wildcard cert in a future spec)
  - _Requirements: 5.1, 5.2_

- [x] 7. Update Makefile secrets management targets
  - [x] 7.1 Rewrite `secrets-sync` target for S3
    - Read `secrets.{env}.json` and upload each secret as individual S3 JSON objects using `aws s3 cp` or `echo | aws s3 cp - s3://...`
    - Upload to: `stripe/api_key`, `stripe/webhook_secret`, `slack/admin_webhook`, `slack/devops_webhook` in bucket `impressionnistes-secrets-{ENV}`
    - _Requirements: 6.1, 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x] 7.2 Rewrite `secrets-list` target for S3
    - Replace `aws secretsmanager list-secrets` with `aws s3 ls s3://impressionnistes-secrets-{ENV}/` (recursive)
    - _Requirements: 6.2_

  - [x] 7.3 Rewrite `secrets-show` target for S3
    - Replace `aws secretsmanager get-secret-value` calls with `aws s3 cp s3://impressionnistes-secrets-{ENV}/{key} -` for each of the 4 secrets
    - _Requirements: 6.3_

  - [x] 7.4 Rewrite `secrets-delete-all` target for S3
    - Replace `aws secretsmanager delete-secret` calls with `aws s3 rm s3://impressionnistes-secrets-{ENV}/ --recursive`
    - _Requirements: 6.7_

  - [x] 7.5 Remove `deploy-secrets` and `destroy-secrets` targets
    - Remove `deploy-secrets`, `deploy-secrets-dev`, `deploy-secrets-prod` targets
    - Remove `destroy-secrets`, `destroy-secrets-prod` targets
    - _Requirements: 6.4, 6.5_

  - [x] 7.6 Update `deploy-backend` target to exclude SecretsStack
    - Remove `ImpressionnistesSecrets-$(ENV)` from the `cdk deploy` stack list in `deploy-backend`
    - _Requirements: 6.6_

  - [x] 7.7 Update `secrets-show-stripe`, `secrets-update-stripe`, and help text
    - Rewrite `secrets-show-stripe` to read from S3 instead of Secrets Manager
    - Rewrite `secrets-update-stripe` to write to S3 instead of Secrets Manager
    - Update the `help` target text to reflect S3-based secrets management (remove deploy-secrets/destroy-secrets references, update descriptions)
    - _Requirements: 6.8_

- [x] 8. Update clean-all-aws.sh script
  - In `scripts/deployment/clean-all-aws.sh`, update section 4 ("Secrets Manager Secrets") to clean up S3 secrets bucket instead
    - Replace `aws secretsmanager describe-secret` / `delete-secret` calls with `aws s3 rb s3://impressionnistes-secrets-{ENV} --force` (or `aws s3 rm --recursive` then `aws s3api delete-bucket`)
    - Update the verification commands at the end to check for S3 bucket instead of Secrets Manager secrets
  - _Requirements: 6.7_

- [x] 9. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
  - Verify CDK synth succeeds: `cd infrastructure && make synth`

- [x] 10. Create ACM certificate and deploy dev environment
  - [x] 10.1 Create wildcard ACM certificate for `*.aviron-rcpm.fr` (manual/assisted)
    - Run `aws acm request-certificate --domain-name "*.aviron-rcpm.fr" --validation-method DNS --region us-east-1` in the prod account
    - Complete DNS validation (add the CNAME record to the domain's DNS)
    - Wait for certificate status to become `ISSUED`
    - Update `DEV_CONFIG["certificate_arn"]` in `infrastructure/config.py` with the actual wildcard certificate ARN (replacing the placeholder)
    - Note: `PROD_CONFIG["certificate_arn"]` will be updated to use this same wildcard cert in a future spec
    - _Requirements: 5.1_

  - [x] 10.2 Upload secrets to S3 bucket
    - Rebuild Lambda layer: `cd functions && ./build-layer.sh`
    - Deploy the database stack first to create the S3 bucket: `cd infrastructure && cdk deploy ImpressionnistesDatabase-dev -c env=dev --require-approval never`
    - Upload secrets: `cd infrastructure && make secrets-sync ENV=dev`
    - Verify secrets are in S3: `make secrets-list ENV=dev`
    - _Requirements: 6.1, 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x] 10.3 Deploy full dev environment
    - Deploy all backend stacks: `cd infrastructure && make deploy-backend ENV=dev`
    - Build frontend: `cd infrastructure && make build-frontend ENV=dev`
    - Deploy frontend stack: `cd infrastructure && make deploy-frontend ENV=dev`
    - Verify deployment: `cd infrastructure && make describe-infra ENV=dev`
    - _Requirements: 1.1, 2.1, 2.2, 2.4, 4.1, 5.3_

- [ ] 11. Verify Slack notifications on dev environment
  - [ ] 11.1 Trigger a Slack notification and verify delivery
    - Verify `make secrets-show ENV=dev` shows the Slack webhook URLs correctly from S3
    - Trigger an action in the dev environment that sends a Slack notification (e.g., create a test user registration, or invoke a Lambda that calls `get_slack_admin_webhook()` / `get_slack_devops_webhook()`)
    - Check the Slack channels to confirm notifications are received
    - If notifications fail, check CloudWatch logs for the Lambda to diagnose S3 access or webhook URL issues
    - _Requirements: 3.5, 3.6, 2.2_

## Notes

- Each task references specific requirements for traceability
- The ACM certificate for the dev custom domain must be created manually via AWS CLI before deploying the frontend (Requirement 5.1). This is a manual step documented in the config, not a coding task.
- Property tests use parametrized example-based testing (per workspace rule: no Hypothesis library)
- After completing all tasks, rebuild the Lambda layer (`cd functions && ./build-layer.sh`) before deploying
- Stripe payment testing is done manually by the user after deployment (not a task)
- Task 10 involves manual AWS CLI steps that Kiro will assist with but cannot fully automate (certificate DNS validation, waiting for issuance)
