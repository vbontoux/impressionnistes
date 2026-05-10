# Requirements Document

## Introduction

This feature deploys the S3-based secrets migration to the production environment. The code changes are already complete (implemented in the `dev-env-same-account-migration` spec) — all stacks use S3 for secrets, SecretsStack is removed from `app.py`, the Makefile is updated, and the Stripe SDK 7+ webhook fix is in place. This spec covers the safe, incremental deployment of those changes to production.

The migration is critical because:

1. **Live data must be preserved** — The DynamoDB table `impressionnistes-registration-prod` contains real user registrations and payment records. The Cognito User Pool has active users.
2. **Incremental deployment** — Stacks must be deployed individually in a specific order to avoid downtime or data loss.
3. **Secrets must be available before Lambda deployment** — The new S3-based Lambdas will fail if secrets are not uploaded to the S3 bucket before the API stack is deployed.
4. **Wildcard certificate** — The prod environment must switch from its current single-domain certificate to the shared wildcard certificate (`*.aviron-rcpm.fr`).
5. **Old SecretsStack cleanup** — The existing `ImpressionnistesSecrets-prod` CloudFormation stack must be destroyed only after verifying the migration works.

## Glossary

- **DatabaseStack**: The CDK stack (`ImpressionnistesDatabase-prod`) that manages the DynamoDB table and the S3 secrets bucket. Deploying this stack adds the secrets bucket without touching the existing table (RETAIN policy).
- **ApiStack**: The CDK stack (`ImpressionnistesApi-prod`) that manages API Gateway, Lambda functions, and IAM policies. Deploying this stack updates Lambdas to use S3 secrets and includes the Stripe SDK 7+ fix.
- **FrontendStack**: The CDK stack (`ImpressiornistesFrontend-prod`) that manages S3 hosting, CloudFront distribution, and the custom domain certificate.
- **AuthStack**: The CDK stack (`ImpressionnistesAuth-prod`) that manages the Cognito User Pool. This stack MUST NOT be redeployed during this migration.
- **Old_SecretsStack**: The existing CloudFormation stack `ImpressionnistesSecrets-prod` that provisions AWS Secrets Manager secrets. To be destroyed after migration verification.
- **Secrets_Bucket**: The S3 bucket `rcpm-impressionnistes-secrets-prod` that stores production secrets as JSON objects.
- **Config_Module**: The Python configuration helper (`infrastructure/config.py`) that provides environment-specific settings including certificate ARNs.
- **Wildcard_Certificate**: The ACM certificate `arn:aws:acm:us-east-1:206478392268:certificate/38b35b2f-317e-48e6-9e1a-08a625f9fd62` covering `*.aviron-rcpm.fr`, shared across all environments.
- **Old_Certificate**: The current prod ACM certificate `arn:aws:acm:us-east-1:206478392268:certificate/dbdc7ccc-f905-45b0-94e3-906fcbb2aabe` for `impressionnistes.aviron-rcpm.fr`.
- **DynamoDB_Table**: The production table `impressionnistes-registration-prod` containing live registration and payment data.
- **Cognito_User_Pool**: The production Cognito User Pool containing active user accounts.
- **AWS_Profile**: The AWS CLI profile `rcpm-prod` used for all production deployments.

## Requirements

### Requirement 1: Update Config Module with Wildcard Certificate for Prod

**User Story:** As a DevOps engineer, I want the prod configuration to reference the wildcard certificate, so that CloudFront uses the shared certificate for the custom domain.

#### Acceptance Criteria

1. THE Config_Module SHALL update `PROD_CONFIG["certificate_arn"]` to `arn:aws:acm:us-east-1:206478392268:certificate/38b35b2f-317e-48e6-9e1a-08a625f9fd62` (the Wildcard_Certificate).
2. THE Config_Module SHALL retain `DEV_CONFIG["certificate_arn"]` unchanged.
3. THE Config_Module SHALL retain all other `PROD_CONFIG` values unchanged (table name, region, removal policy, throttle limits).

### Requirement 2: Deploy DatabaseStack Without Touching DynamoDB Table

**User Story:** As a DevOps engineer, I want to deploy the DatabaseStack to create the S3 secrets bucket, so that secrets can be uploaded before the API stack is deployed, without modifying the existing DynamoDB table.

#### Acceptance Criteria

1. WHEN the DatabaseStack is deployed to prod, THE DatabaseStack SHALL create the Secrets_Bucket (`rcpm-impressionnistes-secrets-prod`).
2. WHEN the DatabaseStack is deployed to prod, THE DynamoDB_Table SHALL remain unchanged (no schema modifications, no data loss, no table replacement).
3. THE Secrets_Bucket SHALL have a removal policy of `RETAIN` in the prod environment.
4. THE Secrets_Bucket SHALL have versioning enabled, public access blocked, and SSE-S3 encryption.
5. THE DatabaseStack SHALL be deployed individually using `cdk deploy ImpressionnistesDatabase-prod -c env=prod` with the `rcpm-prod` AWS profile.

### Requirement 3: Upload Production Secrets to S3 Before API Deployment

**User Story:** As a DevOps engineer, I want production secrets uploaded to the S3 bucket before deploying the API stack, so that Lambda functions can read secrets from S3 immediately upon deployment.

#### Acceptance Criteria

1. WHEN `make secrets-sync ENV=prod` is executed, THE Makefile SHALL upload all secrets from `secrets.prod.json` to the Secrets_Bucket as individual JSON objects.
2. THE Secrets_Bucket SHALL contain the object `stripe/api_key` with the production Stripe API key.
3. THE Secrets_Bucket SHALL contain the object `stripe/webhook_secret` with the production Stripe webhook secret.
4. THE Secrets_Bucket SHALL contain the object `slack/admin_webhook` with the production Slack admin webhook URL.
5. THE Secrets_Bucket SHALL contain the object `slack/devops_webhook` with the production Slack devops webhook URL.
6. THE secrets upload SHALL be completed and verified (via `make secrets-list ENV=prod`) BEFORE the ApiStack is deployed.

### Requirement 4: Deploy ApiStack with S3 Secrets and Stripe Fix

**User Story:** As a DevOps engineer, I want to deploy the API stack so that Lambda functions use S3 for secrets and include the Stripe SDK 7+ webhook fix, so that payments and notifications work correctly.

#### Acceptance Criteria

1. WHEN the ApiStack is deployed to prod, THE ApiStack SHALL update all Lambda functions to read secrets from the Secrets_Bucket via the `SECRETS_BUCKET` environment variable.
2. WHEN the ApiStack is deployed to prod, THE ApiStack SHALL grant Payment Lambdas `s3:GetObject` access to the `stripe/*` prefix in the Secrets_Bucket.
3. WHEN the ApiStack is deployed to prod, THE ApiStack SHALL grant all Lambda functions `s3:GetObject` access to the `slack/*` prefix in the Secrets_Bucket.
4. WHEN the ApiStack is deployed to prod, THE ApiStack SHALL deploy the updated Lambda layer containing the S3-based secrets module.
5. WHEN the ApiStack is deployed to prod, THE ApiStack SHALL deploy the `confirm_payment_webhook` Lambda with the Stripe SDK 7+ fix (JSON body parsing for event data).
6. THE ApiStack SHALL be deployed individually using `cdk deploy ImpressionnistesApi-prod -c env=prod` with the `rcpm-prod` AWS profile.
7. THE ApiStack deployment SHALL occur AFTER secrets are uploaded to S3 (Requirement 3).

### Requirement 5: Deploy FrontendStack with Wildcard Certificate

**User Story:** As a DevOps engineer, I want to deploy the frontend stack with the wildcard certificate, so that CloudFront serves the prod site using the shared certificate.

#### Acceptance Criteria

1. WHEN the FrontendStack is deployed to prod, THE FrontendStack SHALL associate the Wildcard_Certificate with the CloudFront distribution.
2. WHEN the FrontendStack is deployed to prod, THE CloudFront distribution SHALL continue serving the custom domain `impressionnistes.aviron-rcpm.fr`.
3. THE FrontendStack SHALL be deployed individually using `cdk deploy ImpressiornistesFrontend-prod -c env=prod` with the `rcpm-prod` AWS profile.
4. IF the CloudFront distribution requires an update due to the certificate change, THEN THE deployment SHALL wait for the distribution update to complete before marking success.

### Requirement 6: Preserve AuthStack and Cognito User Pool

**User Story:** As a DevOps engineer, I want the Cognito User Pool to remain untouched during the migration, so that existing production users are not affected.

#### Acceptance Criteria

1. THE AuthStack SHALL NOT be deployed during this migration unless explicitly required by a dependency.
2. THE Cognito_User_Pool SHALL retain all existing user accounts, groups, and settings.
3. THE deployment commands SHALL NOT include `ImpressionnistesAuth-prod` in any `cdk deploy` invocation.
4. IF a CDK deployment attempts to modify the Cognito_User_Pool, THEN THE operator SHALL abort the deployment and investigate.

### Requirement 7: Preserve DynamoDB Table Data

**User Story:** As a DevOps engineer, I want the DynamoDB table to remain completely untouched during the migration, so that no live registration or payment data is lost.

#### Acceptance Criteria

1. THE DynamoDB_Table SHALL retain all existing items (registrations, payments, configuration) throughout the migration.
2. THE DynamoDB_Table SHALL retain its current schema (partition key, sort key, GSIs) unchanged.
3. THE DynamoDB_Table removal policy SHALL remain `RETAIN` in the prod environment.
4. IF a CDK deployment shows a planned change to the DynamoDB_Table resource, THEN THE operator SHALL abort the deployment and investigate.

### Requirement 8: Verify Production Functionality After Migration

**User Story:** As a DevOps engineer, I want to verify that payments, Slack notifications, and the frontend work correctly after migration, so that I can confirm the migration succeeded before cleanup.

#### Acceptance Criteria

1. WHEN the migration is complete, THE operator SHALL verify that the Stripe payment webhook processes events correctly (test payment or check CloudWatch logs).
2. WHEN the migration is complete, THE operator SHALL verify that Slack notifications are delivered to the configured channels.
3. WHEN the migration is complete, THE operator SHALL verify that the frontend is accessible at `impressionnistes.aviron-rcpm.fr` with a valid HTTPS certificate.
4. WHEN the migration is complete, THE operator SHALL verify that Lambda functions can read secrets from S3 by checking CloudWatch logs for successful secret retrieval.
5. IF any verification fails, THEN THE operator SHALL check CloudWatch logs and the Secrets_Bucket contents before proceeding to cleanup.

### Requirement 9: Destroy Old SecretsStack After Verification

**User Story:** As a DevOps engineer, I want to destroy the old SecretsStack after verifying the migration works, so that obsolete Secrets Manager resources are cleaned up.

#### Acceptance Criteria

1. THE Old_SecretsStack SHALL be destroyed only AFTER all verifications in Requirement 8 pass.
2. WHEN the Old_SecretsStack is destroyed, THE operator SHALL execute `aws cloudformation delete-stack --stack-name ImpressionnistesSecrets-prod --profile rcpm-prod`.
3. THE Old_SecretsStack destruction SHALL NOT affect any other CloudFormation stacks or resources.
4. IF the Old_SecretsStack deletion fails, THEN THE operator SHALL investigate dependencies before retrying.
5. THE Secrets Manager secrets MAY be retained temporarily as a fallback (they are not deleted by stack destruction if they have a RETAIN policy).

### Requirement 10: Deployment Order and Safety Constraints

**User Story:** As a DevOps engineer, I want a strict deployment order with safety checks, so that the migration proceeds without downtime or data loss.

#### Acceptance Criteria

1. THE deployment SHALL follow this exact order: (1) Update config.py, (2) Deploy DatabaseStack, (3) Upload secrets to S3, (4) Deploy ApiStack, (5) Deploy FrontendStack, (6) Verify, (7) Destroy Old_SecretsStack.
2. THE operator SHALL NOT execute `make deploy-backend` (which deploys all stacks including AuthStack).
3. THE operator SHALL NOT execute `make deploy` or `cdk deploy --all` (which deploys all stacks).
4. EACH stack SHALL be deployed individually using targeted `cdk deploy <stack-name>` commands.
5. THE operator SHALL use the `rcpm-prod` AWS profile for all production deployments.
6. BEFORE each `cdk deploy` command, THE operator SHALL run `cdk diff <stack-name> -c env=prod` to review planned changes and confirm no unexpected modifications to DynamoDB or Cognito resources.
7. THE Lambda layer SHALL be rebuilt (`cd functions && ./build-layer.sh`) before deploying the ApiStack to ensure the latest secrets module is included.
