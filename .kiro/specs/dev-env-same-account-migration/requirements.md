# Requirements Document

## Introduction

This feature migrates the dev environment into the same AWS account as production (account `206478392268`). The migration involves three key changes:

1. **Replace AWS Secrets Manager with S3-based secrets storage** — Secrets Manager creates naming conflicts when dev and prod share an account (secret names are global within an account) and incurs per-secret costs. S3 buckets with environment-specific names (`impressionnistes-secrets-{env}`) provide isolated, cost-effective storage with prefix-based IAM scoping.

2. **Create a new ACM certificate for the dev custom domain** — The current dev certificate lives in the old dev AWS account (`458847123929`). A new certificate must be provisioned in the prod account (`206478392268`) in `us-east-1` (required by CloudFront) for `impressionnistes-dev.aviron-rcpm.fr`.

3. **Remove the SecretsStack entirely** and update all Lambda functions, shared code, IAM policies, and operational tooling to use S3 instead of Secrets Manager.

## Glossary

- **Secrets_Bucket**: An S3 bucket named `impressionnistes-secrets-{env}` that stores application secrets as JSON objects, one per secret, organized by prefix (`stripe/`, `slack/`).
- **CDK_App**: The AWS CDK application entry point (`infrastructure/app.py`) that instantiates and wires all CloudFormation stacks.
- **ApiStack**: The CDK stack (`infrastructure/stacks/api_stack.py`) that defines API Gateway, Lambda functions, and their IAM permissions.
- **SecretsStack**: The CDK stack (`infrastructure/stacks/secrets_stack.py`) that currently provisions AWS Secrets Manager secrets. To be removed.
- **FrontendStack**: The CDK stack (`infrastructure/stacks/frontend_stack.py`) that provisions S3, CloudFront, and the custom domain certificate for the frontend.
- **Secrets_Module**: The shared Python module (`functions/shared/secrets_manager.py`) used by Lambda functions at runtime to retrieve secrets with caching.
- **Config_Module**: The Python configuration helper (`infrastructure/config.py`) that provides environment-specific settings including certificate ARNs.
- **Payment_Lambda**: Lambda functions handling Stripe payment operations (`create_payment_intent`, `confirm_payment_webhook`) that require access to Stripe secrets under the `stripe/*` prefix.
- **Makefile**: The operational command interface (`infrastructure/Makefile`) providing `make` targets for deployment, secrets management, and other operations.
- **Secrets_JSON**: The local JSON files (`infrastructure/secrets.{env}.json`) containing secret values used for uploading to the secrets store.

## Requirements

### Requirement 1: Create S3 Secrets Bucket per Environment

**User Story:** As a DevOps engineer, I want an S3 bucket per environment for storing secrets, so that dev and prod secrets are isolated without naming conflicts.

#### Acceptance Criteria

1. WHEN the CDK_App is deployed with environment context `env={env_name}`, THE CDK_App SHALL create an S3 bucket named `impressionnistes-secrets-{env_name}`.
2. THE Secrets_Bucket SHALL have all public access blocked via `BlockPublicAccess.BLOCK_ALL`.
3. THE Secrets_Bucket SHALL have server-side encryption enabled using SSE-S3 (AES-256).
4. THE Secrets_Bucket SHALL have versioning enabled.
5. WHILE the environment is `dev`, THE Secrets_Bucket SHALL have a removal policy of `DESTROY` with auto-delete objects enabled.
6. WHILE the environment is `prod`, THE Secrets_Bucket SHALL have a removal policy of `RETAIN`.

### Requirement 2: Prefix-Based IAM Isolation for S3 Secrets

**User Story:** As a DevOps engineer, I want IAM policies that restrict Lambda access to only the secret prefixes they need, so that the principle of least privilege is enforced.

#### Acceptance Criteria

1. THE ApiStack SHALL grant each Payment_Lambda read access to S3 objects under the `stripe/*` prefix in the Secrets_Bucket for the current environment.
2. THE ApiStack SHALL grant all Lambda functions read access to S3 objects under the `slack/*` prefix in the Secrets_Bucket for the current environment.
3. THE ApiStack SHALL remove all `secretsmanager:GetSecretValue` IAM policy statements from every Lambda function.
4. THE ApiStack SHALL pass the Secrets_Bucket name as the `SECRETS_BUCKET` environment variable to all Lambda functions.

### Requirement 3: Update Secrets Module to Read from S3

**User Story:** As a developer, I want the shared secrets module to read secrets from S3 instead of Secrets Manager, so that Lambda functions retrieve secrets from the new storage without code changes in each handler.

#### Acceptance Criteria

1. THE Secrets_Module SHALL use the S3 client (`boto3.client('s3')`) instead of the Secrets Manager client to retrieve secrets.
2. THE Secrets_Module SHALL read the bucket name from the `SECRETS_BUCKET` environment variable.
3. WHEN `get_stripe_api_key()` is called, THE Secrets_Module SHALL retrieve the object at key `stripe/api_key` from the Secrets_Bucket and return the `api_key` field from the parsed JSON content.
4. WHEN `get_stripe_webhook_secret()` is called, THE Secrets_Module SHALL retrieve the object at key `stripe/webhook_secret` from the Secrets_Bucket and return the `webhook_secret` field from the parsed JSON content.
5. WHEN `get_slack_admin_webhook()` is called, THE Secrets_Module SHALL retrieve the object at key `slack/admin_webhook` from the Secrets_Bucket and return the `webhook_url` field from the parsed JSON content.
6. WHEN `get_slack_devops_webhook()` is called, THE Secrets_Module SHALL retrieve the object at key `slack/devops_webhook` from the Secrets_Bucket and return the `webhook_url` field from the parsed JSON content.
7. THE Secrets_Module SHALL maintain the existing in-memory caching behavior for retrieved secrets.
8. IF an S3 `GetObject` call fails, THEN THE Secrets_Module SHALL log the error and raise an exception, preserving the existing error-handling contract.
9. THE Secrets_Module public API (`get_stripe_api_key`, `get_stripe_webhook_secret`, `get_slack_admin_webhook`, `get_slack_devops_webhook`, `clear_cache`) SHALL remain unchanged so that calling Lambda functions require no modifications.

### Requirement 4: Remove SecretsStack

**User Story:** As a DevOps engineer, I want the SecretsStack removed from the CDK infrastructure, so that the codebase no longer references AWS Secrets Manager resources.

#### Acceptance Criteria

1. THE CDK_App SHALL remove the `SecretsStack` instantiation from `app.py`.
2. THE CDK_App SHALL remove the `SecretsStack` import from `app.py`.
3. THE CDK_App SHALL remove the `secrets_stack` variable from the tags loop in `app.py`.
4. THE CDK_App SHALL delete the file `infrastructure/stacks/secrets_stack.py`.

### Requirement 5: Create ACM Certificate for Dev Custom Domain

**User Story:** As a DevOps engineer, I want a new ACM certificate for the dev custom domain in the prod AWS account, so that CloudFront can serve the dev site over HTTPS on the custom domain.

#### Acceptance Criteria

1. THE Config_Module SHALL update the dev environment `certificate_arn` to reference a certificate in AWS account `206478392268` in region `us-east-1`.
2. THE Config_Module SHALL retain the prod environment `certificate_arn` unchanged.
3. THE FrontendStack SHALL continue to import the certificate from the ARN provided by the Config_Module and associate it with the CloudFront distribution for the custom domain.

### Requirement 6: Update Makefile and Operational Scripts

**User Story:** As a DevOps engineer, I want the Makefile secrets management commands to upload and manage secrets via S3 instead of Secrets Manager, so that operational workflows match the new storage backend.

#### Acceptance Criteria

1. THE Makefile SHALL replace the `secrets-sync` target to upload each secret from `secrets.{env}.json` as individual JSON objects to the Secrets_Bucket under the appropriate prefix (`stripe/api_key`, `stripe/webhook_secret`, `slack/admin_webhook`, `slack/devops_webhook`).
2. THE Makefile SHALL replace the `secrets-list` target to list objects in the Secrets_Bucket for the current environment.
3. THE Makefile SHALL replace the `secrets-show` target to retrieve and display secret values from the Secrets_Bucket.
4. THE Makefile SHALL remove the `deploy-secrets` target and all references to the `ImpressionnistesSecrets-{env}` stack name.
5. THE Makefile SHALL remove the `destroy-secrets` target.
6. THE Makefile SHALL update the `deploy-backend` target to exclude the `ImpressionnistesSecrets-{env}` stack.
7. THE Makefile SHALL update the `secrets-delete-all` target to delete secret objects from the Secrets_Bucket instead of Secrets Manager.
8. THE Makefile SHALL update the help text to reflect the new S3-based secrets management commands.

### Requirement 7: S3 Secret Object Format

**User Story:** As a developer, I want a consistent JSON format for secrets stored in S3, so that the Secrets_Module can parse them reliably.

#### Acceptance Criteria

1. THE Secrets_Bucket SHALL store each secret as a separate S3 object with a JSON body.
2. WHEN the Stripe API key secret is stored, THE object key SHALL be `stripe/api_key` and the JSON body SHALL contain the field `api_key`.
3. WHEN the Stripe webhook secret is stored, THE object key SHALL be `stripe/webhook_secret` and the JSON body SHALL contain the field `webhook_secret`.
4. WHEN the Slack admin webhook secret is stored, THE object key SHALL be `slack/admin_webhook` and the JSON body SHALL contain the field `webhook_url`.
5. WHEN the Slack devops webhook secret is stored, THE object key SHALL be `slack/devops_webhook` and the JSON body SHALL contain the field `webhook_url`.
6. FOR ALL secrets stored in the Secrets_Bucket, reading the object, parsing the JSON, and extracting the expected field SHALL return the original secret value (round-trip property).
