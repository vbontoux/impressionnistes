.PHONY: help check-prereqs setup venv install bootstrap synth diff deploy deploy-dev deploy-prod deploy-auth redeploy destroy destroy-dev destroy-prod fix-stuck-stack clean-aws list describe-infra costs db-export db-view db-reset db-migrate cognito-create-admin cognito-list-users cognito-add-to-group ses-verify-email ses-list-verified ses-check-email ses-get-quota ses-get-statistics ses-request-production ses-verify-domain ses-get-domain-token ses-enable-dkim ses-check-domain secrets-list secrets-get secrets-create secrets-update test-setup test test-coverage test-email cleanoduction clean test test-backend test-frontend test-email test-setup test-clean test-coverage

# Virtual environment paths
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Test virtual environment paths (relative to project root)
TEST_VENV = tests/venv
TEST_PYTHON = $(TEST_VENV)/bin/python
TEST_PIP = $(TEST_VENV)/bin/pip
TEST_PYTEST = $(TEST_VENV)/bin/pytest

# CDK should be installed globally
CDK = cdk

# Default environment
ENV ?= dev

# AWS Profile configuration
# Automatically use 'rcpm' profile for prod environment
ifeq ($(ENV),prod)
    export AWS_PROFILE=rcpm
endif

help:
	@echo "Course des Impressionnistes - Infrastructure Commands"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - AWS CLI configured (aws configure)"
	@echo "  - CDK CLI installed globally (npm install -g aws-cdk)"
	@echo ""
	@echo "Setup:"
	@echo "  make check-prereqs  - Verify AWS CLI and CDK are installed"
	@echo "  make setup          - Create venv and install dependencies"
	@echo "  make venv           - Create virtual environment only"
	@echo "  make install        - Install dependencies in existing venv"
	@echo "  make bootstrap      - Bootstrap CDK (first time only)"
	@echo ""
	@echo "Deployment:"
	@echo "  make synth          - Synthesize CloudFormation templates"
	@echo "  make diff           - Show what will change"
	@echo "  make deploy         - Deploy all stacks (default: dev)"
	@echo "  make deploy-dev     - Deploy to dev environment"
	@echo "  make deploy-prod    - Deploy to prod environment"
	@echo "  make deploy-secrets - Deploy only secrets stack (Stripe, Slack, etc.)"
	@echo "  make deploy-auth    - Deploy only auth stack"
	@echo "  make redeploy       - Quick redeploy (destroy + deploy for dev)"
	@echo ""
	@echo "Management:"
	@echo "  make list           - List all stacks"
	@echo "  make describe-infra - Show API URL and Cognito details for frontend config"
	@echo "  make costs          - Show AWS costs for last month (default: last 30 days)"
	@echo "  make db-backup         - Create AWS-managed on-demand backup (recommended)"
	@echo "  make db-backup-local   - Create local JSON backup file"
	@echo "  make db-list-backups   - List all AWS backups"
	@echo "  make db-restore-backup - Restore from AWS backup (BACKUP_ARN=<arn>)"
	@echo "  make db-export         - Export DynamoDB table to CSV (default: dev)"
	@echo "  make db-view           - View DynamoDB table contents (default: dev)"
	@echo "  make db-migrate        - Run database migration (optional, see functions/migrations/)"
	@echo "  make db-reset          - Reset database to initial state (⚠️  DELETES ALL DATA)"
	@echo "  make db-cleanup-rental-boats-dry-run - Preview old RENTAL_BOAT records to delete"
	@echo "  make db-cleanup-rental-boats         - Delete old RENTAL_BOAT records (⚠️  destructive!)"
	@echo "  make destroy        - Destroy all stacks (default: dev)"
	@echo "  make destroy-dev    - Destroy dev environment"
	@echo "  make destroy-prod   - Destroy prod environment (with confirmation)"
	@echo ""
	@echo "Cognito User Management:"
	@echo "  make cognito-create-admin EMAIL=user@example.com - Create admin user"
	@echo "  make cognito-list-users                          - List all Cognito users"
	@echo "  make cognito-add-to-group EMAIL=user@example.com GROUP=admins - Add user to group"
	@echo "  make delete-team-manager EMAIL=user@example.com  - Delete team manager and all data (⚠️  destructive!)"
	@echo ""
	@echo "Secrets Management:"
	@echo "  make secrets-list                                    - List all secrets"
	@echo "  make secrets-show                                    - Show all secret values (⚠️  sensitive!)"
	@echo "  make secrets-show-stripe                             - Show Stripe secrets (partial)"
	@echo "  make secrets-sync ENV=dev                            - Sync all secrets from secrets.ENV.json to AWS"
	@echo "  make secrets-sync-dev                                - Sync secrets from secrets.dev.json"
	@echo "  make secrets-sync-prod                               - Sync secrets from secrets.prod.json (with confirmation)"
	@echo "  make secrets-delete-all ENV=dev                      - Delete all 4 secrets from AWS (with confirmation)"
	@echo "  make secrets-delete-all-prod                         - Delete all 4 secrets from PROD (with confirmation)"
	@echo "  make secrets-update-stripe STRIPE_API_KEY=sk_xxx     - Update Stripe API key manually"
	@echo ""
	@echo "Stack Management:"
	@echo "  make destroy-secrets ENV=dev                         - Destroy Secrets stack (with confirmation)"
	@echo "  make destroy-secrets-prod                            - Destroy Secrets stack in PROD (with confirmation)"
	@echo ""
	@echo "Email/SES Management:"
	@echo "  make ses-verify-email EMAIL=your@email.com           - Verify email address in SES"
	@echo "  make ses-list-verified                               - List all verified emails"
	@echo "  make ses-check-email EMAIL=your@email.com            - Check if email is verified"
	@echo "  make ses-get-quota                                   - Show SES sending quota"
	@echo "  make ses-get-statistics                              - Show SES sending statistics"
	@echo "  make ses-request-production                          - Instructions for production access"
	@echo ""
	@echo "Boat Payment Management (Debug/Demo):"
	@echo "  make boat-unpay TEAM_MANAGER_ID=xxx BOAT_ID=xxx      - Reset single boat to unpaid"
	@echo "  make boat-unpay-all TEAM_MANAGER_ID=xxx              - Reset all boats to unpaid"
	@echo "  make boat-list-paid TEAM_MANAGER_ID=xxx              - List all paid boats"
	@echo ""
	@echo "Testing:"
	@echo "  make test-setup     - Set up test environment (create venv, install deps)"
	@echo "  make test           - Run all tests (backend + frontend)"
	@echo "  make test-backend   - Run backend integration tests only"
	@echo "  make test-frontend  - Run frontend formatter tests only"
	@echo "  make test-email EMAIL=your@email.com - Test email notification system"
	@echo "  make test-slack     - Test Slack notification system"
	@echo "  make test-coverage  - Run backend tests with HTML coverage report"
	@echo "  make test-clean     - Remove test venv and cache files"
	@echo ""
	@echo "Troubleshooting:"
	@echo "  make fix-stuck-stack - Fix stuck CloudFormation stack"
	@echo "  make clean-aws      - Complete AWS cleanup (stacks + orphaned resources)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove venv and cache files"
	@echo ""
	@echo "Environment variable:"
	@echo "  ENV=dev|prod        - Set environment (default: dev)"
	@echo "  Example: make deploy ENV=prod"

check-prereqs:
	@echo "Checking prerequisites..."
	@if ! command -v aws >/dev/null 2>&1; then \
		echo "❌ AWS CLI not found. Install from: https://aws.amazon.com/cli/"; \
		exit 1; \
	fi
	@if ! command -v cdk >/dev/null 2>&1; then \
		echo "❌ CDK CLI not found. Install with: npm install -g aws-cdk"; \
		exit 1; \
	fi
	@if ! aws sts get-caller-identity >/dev/null 2>&1; then \
		echo "❌ AWS credentials not configured. Run: aws configure"; \
		exit 1; \
	fi
	@echo "✓ AWS CLI: $$(aws --version)"
	@echo "✓ CDK CLI: $$(cdk --version)"
	@echo "✓ AWS Account: $$(aws sts get-caller-identity --query Account --output text)"
	@echo "✓ All prerequisites met"

setup: check-prereqs venv install
	@echo "✓ Setup complete"

venv:
	@echo "Creating virtual environment..."
	@python3 -m venv $(VENV)
	@echo "✓ Virtual environment created"

install:
	@echo "Installing dependencies..."
	@$(PIP) install --upgrade pip -q
	@$(PIP) install -r requirements.txt -q
	@echo "✓ Dependencies installed"

bootstrap:
	@echo "Bootstrapping CDK for environment: $(ENV)"
	@echo "This is only needed once per AWS account/region"
	@if ! command -v cdk >/dev/null 2>&1; then \
		echo "❌ Error: CDK CLI not found"; \
		echo "Install with: npm install -g aws-cdk"; \
		exit 1; \
	fi
	@. $(VENV)/bin/activate && $(CDK) bootstrap --context env=$(ENV)
	@echo "✓ CDK bootstrap complete"

bootstrap-dev:
	@$(MAKE) bootstrap ENV=dev

bootstrap-prod:
	@echo "⚠️  WARNING: Bootstrapping CDK in PRODUCTION AWS Account"
	@echo "This will create CDK resources in the production account"
	@read -p "Type 'BOOTSTRAP PROD' to confirm: " confirm; \
	if [ "$$confirm" = "BOOTSTRAP PROD" ]; then \
		$(MAKE) bootstrap ENV=prod; \
	else \
		echo "Bootstrap cancelled"; \
		exit 1; \
	fi

synth:
	@echo "Synthesizing CloudFormation templates for $(ENV)..."
	@. $(VENV)/bin/activate && $(CDK) synth --context env=$(ENV)

diff:
	@echo "Showing changes for $(ENV) environment..."
	@. $(VENV)/bin/activate && $(CDK) diff --all --context env=$(ENV)

deploy: build-layer 
	@echo "Deploying to $(ENV) environment..."
	@. $(VENV)/bin/activate && $(CDK) deploy --all --context env=$(ENV) --require-approval never
	@echo "✓ Deployment complete"

deploy-dev:
	@$(MAKE) deploy ENV=dev

deploy-prod:
	@echo "⚠️  WARNING: Deploying to PRODUCTION"
	@read -p "Type 'DEPLOY PROD' to confirm: " confirm; \
	if [ "$$confirm" = "DEPLOY PROD" ]; then \
		$(MAKE) deploy ENV=prod; \
	else \
		echo "Deployment cancelled"; \
		exit 1; \
	fi

deploy-backend: build-layer
	@echo "Deploying backend stacks to $(ENV) environment..."
	@echo "Excluding: ImpressiornistesFrontend-$(ENV)"
	@. $(VENV)/bin/activate && $(CDK) deploy ImpressionnistesSecrets-$(ENV) ImpressionnistesDatabase-$(ENV) ImpressionnistesAuth-$(ENV) ImpressionnistesApi-$(ENV) ImpressionnistesMonitoring-$(ENV) --context env=$(ENV) --require-approval never
	@echo "✓ Backend deployment complete"

deploy-backend-dev:
	@$(MAKE) deploy-backend ENV=dev

deploy-backend-prod:
	@echo "⚠️  WARNING: Deploying BACKEND to PRODUCTION"
	@read -p "Type 'DEPLOY BACKEND PROD' to confirm: " confirm; \
	if [ "$$confirm" = "DEPLOY BACKEND PROD" ]; then \
		$(MAKE) deploy-backend ENV=prod; \
	else \
		echo "Deployment cancelled"; \
		exit 1; \
	fi

deploy-frontend:
	@echo "Deploying frontend stack to $(ENV) environment..."
	@. $(VENV)/bin/activate && $(CDK) deploy ImpressiornistesFrontend-$(ENV) --context env=$(ENV) --require-approval never
	@echo "✓ Frontend deployment complete"

deploy-frontend-dev:
	@$(MAKE) deploy-frontend ENV=dev

deploy-frontend-prod:
	@echo "⚠️  WARNING: Deploying FRONTEND to PRODUCTION"
	@read -p "Type 'DEPLOY FRONTEND PROD' to confirm: " confirm; \
	if [ "$$confirm" = "DEPLOY FRONTEND PROD" ]; then \
		$(MAKE) deploy-frontend ENV=prod; \
	else \
		echo "Deployment cancelled"; \
		exit 1; \
	fi

list:
	@echo "Listing stacks for $(ENV) environment..."
	@. $(VENV)/bin/activate && $(CDK) list --context env=$(ENV)

describe-infra:
	@echo "=========================================="
	@echo "Infrastructure Details"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@echo "API Gateway:"
	@API_URL=$$(aws cloudformation describe-stacks \
		--stack-name ImpressionnistesApi-$(ENV) \
		--query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
		--output text 2>/dev/null); \
	if [ -n "$$API_URL" ]; then \
		echo "  URL: $$API_URL"; \
	else \
		echo "  ⚠️  API stack not deployed yet"; \
	fi
	@echo ""
	@echo "Cognito Configuration:"
	@USER_POOL_ID=$$(aws cloudformation describe-stacks \
		--stack-name ImpressionnistesAuth-$(ENV) \
		--query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
		--output text 2>/dev/null); \
	CLIENT_ID=$$(aws cloudformation describe-stacks \
		--stack-name ImpressionnistesAuth-$(ENV) \
		--query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' \
		--output text 2>/dev/null); \
	DOMAIN=$$(aws cloudformation describe-stacks \
		--stack-name ImpressionnistesAuth-$(ENV) \
		--query 'Stacks[0].Outputs[?OutputKey==`UserPoolDomain`].OutputValue' \
		--output text 2>/dev/null); \
	if [ -n "$$USER_POOL_ID" ]; then \
		echo "  User Pool ID: $$USER_POOL_ID"; \
		echo "  Client ID: $$CLIENT_ID"; \
		echo "  Domain: $$DOMAIN"; \
	else \
		echo "  ⚠️  Auth stack not deployed yet"; \
	fi
	@echo ""
	@echo ""
	@echo "Frontend (CloudFront):"
	@CLOUDFRONT_URL=$$(aws cloudformation describe-stacks --stack-name ImpressiornistesFrontend-$(ENV) --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' --output text 2>/dev/null); \
	CLOUDFRONT_DOMAIN=$$(aws cloudformation describe-stacks --stack-name ImpressiornistesFrontend-$(ENV) --query 'Stacks[0].Outputs[?OutputKey==`DistributionDomainName`].OutputValue' --output text 2>/dev/null); \
	BUCKET_NAME=$$(aws cloudformation describe-stacks --stack-name ImpressiornistesFrontend-$(ENV) --query 'Stacks[0].Outputs[?OutputKey==`WebsiteBucketName`].OutputValue' --output text 2>/dev/null); \
	if [ -n "$$CLOUDFRONT_URL" ]; then echo "  Website URL: $$CLOUDFRONT_URL"; echo "  CloudFront Domain: $$CLOUDFRONT_DOMAIN"; echo "  S3 Bucket: $$BUCKET_NAME"; else echo "  ⚠️  Frontend stack not deployed yet"; fi
	@echo "Frontend .env configuration:"
	@echo "=========================================="
	@API_URL=$$(aws cloudformation describe-stacks \
		--stack-name ImpressionnistesApi-$(ENV) \
		--query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
		--output text 2>/dev/null); \
	CLIENT_ID=$$(aws cloudformation describe-stacks \
		--stack-name ImpressionnistesAuth-$(ENV) \
		--query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' \
		--output text 2>/dev/null); \
	DOMAIN=$$(aws cloudformation describe-stacks \
		--stack-name ImpressionnistesAuth-$(ENV) \
		--query 'Stacks[0].Outputs[?OutputKey==`UserPoolDomain`].OutputValue' \
		--output text 2>/dev/null); \
	if [ -n "$$API_URL" ] && [ -n "$$CLIENT_ID" ]; then \
		echo "VITE_API_URL=$$API_URL"; \
		echo "VITE_COGNITO_DOMAIN=$$DOMAIN"; \
		echo "VITE_COGNITO_CLIENT_ID=$$CLIENT_ID"; \
		CLOUDFRONT_DOMAIN=$$(aws cloudformation describe-stacks --stack-name ImpressiornistesFrontend-$(ENV) --query 'Stacks[0].Outputs[?OutputKey==`DistributionDomainName`].OutputValue' --output text 2>/dev/null); if [ -n "$$CLOUDFRONT_DOMAIN" ]; then echo "VITE_COGNITO_REDIRECT_URI=https://$$CLOUDFRONT_DOMAIN/callback"; else echo "VITE_COGNITO_REDIRECT_URI=http://localhost:3000/callback"; fi; \
	else \
		echo "⚠️  Stacks not fully deployed yet"; \
	fi
	@echo "=========================================="
	@echo ""
	@echo "Copy the configuration above to frontend/.env"
	@echo ""

describe-infra-dev:
	@$(MAKE) describe-infra ENV=dev

describe-infra-prod:
	@$(MAKE) describe-infra ENV=prod

deploy-secrets:
	@echo "=========================================="
	@echo "Deploying Secrets Stack"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ ! -f "secrets.json" ]; then \
		echo "❌ Error: secrets.json not found"; \
		echo ""; \
		echo "Please create secrets.json from secrets.json.example:"; \
		echo "  cp secrets.json.example secrets.json"; \
		echo "  # Edit secrets.json with your actual secrets"; \
		echo ""; \
		exit 1; \
	fi
	@echo "✓ Found secrets.json"
	@echo ""
	@echo "This will create/update the following secrets in AWS Secrets Manager:"
	@echo "  - impressionnistes/stripe/api_key"
	@echo "  - impressionnistes/stripe/webhook_secret"
	@echo "  - impressionnistes/slack/admin_webhook"
	@echo "  - impressionnistes/slack/devops_webhook"
	@echo ""
	@echo "Deploying secrets..."
	@echo ""
	@. $(VENV)/bin/activate && $(CDK) deploy ImpressionnistesSecrets-$(ENV) --context env=$(ENV) --require-approval never
	@echo ""
	@echo "=========================================="
	@echo "✓ Secrets deployed successfully!"
	@echo ""
	@echo "Secrets are now available in AWS Secrets Manager."
	@echo "Lambda functions will automatically retrieve them at runtime."
	@echo "=========================================="

deploy-secrets-dev:
	@$(MAKE) deploy-secrets ENV=dev

deploy-secrets-prod:
	@echo "⚠️  WARNING: Deploying Secrets to PRODUCTION"
	@read -p "Type 'DEPLOY PROD' to confirm: " confirm; \
	if [ "$$confirm" = "DEPLOY PROD" ]; then \
		$(MAKE) deploy-secrets ENV=prod; \
	else \
		echo "Deployment cancelled"; \
		exit 1; \
	fi

deploy-auth:
	@echo "Deploying Auth stack for $(ENV) environment..."
	@$(CDK) deploy ImpressionnistesAuth-$(ENV) --context env=$(ENV)

deploy-auth-dev:
	@$(MAKE) deploy-auth ENV=dev

deploy-auth-prod:
	@echo "⚠️  WARNING: Deploying Auth to PRODUCTION"
	@read -p "Type 'DEPLOY PROD' to confirm: " confirm; \
	if [ "$$confirm" = "DEPLOY PROD" ]; then \
		$(MAKE) deploy-auth ENV=prod; \
	else \
		echo "Deployment cancelled"; \
		exit 1; \
	fi
	@echo "✓ Auth stack deployed"

build-layer:
	@echo "Building Lambda layer..."
	@cd ../functions && ./build-layer.sh
	@echo "✓ Lambda layer built"

deploy-api: build-layer
	@echo "Deploying API stack for $(ENV) environment..."
	@$(CDK) deploy ImpressionnistesApi-$(ENV) --context env=$(ENV)
	@echo "✓ API stack deployed"

deploy-api-dev:
	@$(MAKE) deploy-api ENV=dev

deploy-api-prod:
	@echo "⚠️  WARNING: Deploying API to PRODUCTION"
	@read -p "Type 'DEPLOY PROD' to confirm: " confirm; \
	if [ "$$confirm" = "DEPLOY PROD" ]; then \
		$(MAKE) deploy-api ENV=prod; \
	else \
		echo "Deployment cancelled"; \
		exit 1; \
	fi

deploy-frontend: build-frontend
	@echo "Deploying Frontend stack for $(ENV) environment..."
	@. $(VENV)/bin/activate && $(CDK) deploy ImpressiornistesFrontend-$(ENV) --context env=$(ENV) --require-approval never
	@echo "✓ Frontend stack deployed"
	@echo ""
	@echo "=========================================="
	@echo "Frontend URL:"
	@aws cloudformation describe-stacks --stack-name ImpressiornistesFrontend-$(ENV) --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' --output text
	@echo "=========================================="

deploy-frontend-dev:
	@$(MAKE) deploy-frontend ENV=dev

deploy-frontend-prod:
	@echo "⚠️  WARNING: Deploying Frontend to PRODUCTION"
	@read -p "Type 'DEPLOY PROD' to confirm: " confirm; \
	if [ "$$confirm" = "DEPLOY PROD" ]; then \
		$(MAKE) deploy-frontend ENV=prod; \
	else \
		echo "Deployment cancelled"; \
		exit 1; \
	fi

deploy-frontend-complete:
	@echo "=========================================="
	@echo "Complete Frontend Deployment (2-stage)"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@echo "Stage 1: Initial deployment (with placeholder redirect URI)..."
	@$(MAKE) deploy-frontend ENV=$(ENV)
	@echo ""
	@echo "Stage 2: Rebuilding with correct CloudFront URL..."
	@$(MAKE) deploy-frontend ENV=$(ENV)
	@echo ""
	@echo "=========================================="
	@echo "✓ Complete frontend deployment finished!"
	@echo "=========================================="

deploy-frontend-complete-dev:
	@$(MAKE) deploy-frontend-complete ENV=dev

deploy-frontend-complete-prod:
	@echo "⚠️  WARNING: Complete Frontend Deployment to PRODUCTION"
	@read -p "Type 'DEPLOY PROD' to confirm: " confirm; \
	if [ "$$confirm" = "DEPLOY PROD" ]; then \
		$(MAKE) deploy-frontend-complete ENV=prod; \
	else \
		echo "Deployment cancelled"; \
		exit 1; \
	fi

build-frontend:
	@echo "=========================================="
	@echo "Building Frontend for $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ ! -d "../frontend" ]; then echo "❌ Error: frontend directory not found"; exit 1; fi
	@echo "1. Fetching infrastructure configuration..."
	@API_URL=$$(aws cloudformation describe-stacks --stack-name ImpressionnistesApi-$(ENV) --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' --output text 2>/dev/null); \
	CLIENT_ID=$$(aws cloudformation describe-stacks --stack-name ImpressionnistesAuth-$(ENV) --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' --output text 2>/dev/null); \
	DOMAIN=$$(aws cloudformation describe-stacks --stack-name ImpressionnistesAuth-$(ENV) --query 'Stacks[0].Outputs[?OutputKey==`UserPoolDomain`].OutputValue' --output text 2>/dev/null); \
	if [ -z "$$API_URL" ] || [ -z "$$CLIENT_ID" ]; then echo "❌ Error: Could not fetch infrastructure details"; echo "Make sure API and Auth stacks are deployed first:"; echo "  make deploy-dev"; exit 1; fi; \
	echo "   API URL: $$API_URL"; echo "   Cognito Client ID: $$CLIENT_ID"; echo "   Cognito Domain: $$DOMAIN"; echo ""; \
	echo "2. Creating production .env file..."; \
	CLOUDFRONT_DOMAIN=$$(aws cloudformation describe-stacks --stack-name ImpressiornistesFrontend-$(ENV) --query 'Stacks[0].Outputs[?OutputKey==`DistributionDomainName`].OutputValue' --output text 2>/dev/null); \
	WEBSITE_URL=$$(aws cloudformation describe-stacks --stack-name ImpressiornistesFrontend-$(ENV) --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' --output text 2>/dev/null); \
	if [ -z "$$CLOUDFRONT_DOMAIN" ] || [ "$$CLOUDFRONT_DOMAIN" = "None" ]; then echo "   ⚠️  Frontend stack not deployed yet, using placeholder"; CLOUDFRONT_DOMAIN="PLACEHOLDER-DEPLOY-FRONTEND-FIRST"; WEBSITE_URL="https://PLACEHOLDER-DEPLOY-FRONTEND-FIRST"; fi; \
	cd ../frontend && echo "VITE_API_URL=$$API_URL" > .env.production && echo "VITE_COGNITO_DOMAIN=$$DOMAIN" >> .env.production && echo "VITE_COGNITO_CLIENT_ID=$$CLIENT_ID" >> .env.production && echo "VITE_COGNITO_REDIRECT_URI=$$WEBSITE_URL/callback" >> .env.production && if [ -f ".env.$(ENV)" ]; then grep VITE_STRIPE_PUBLISHABLE_KEY .env.$(ENV) >> .env.production 2>/dev/null || true; fi; \
	echo "   ✓ Created .env.production"; echo ""; \
	echo "3. Installing dependencies..."; npm install --silent; echo "   ✓ Dependencies installed"; echo ""; \
	echo "4. Building production bundle..."; npm run build; echo "   ✓ Build complete"; echo ""; \
	echo "=========================================="
	@echo "✓ Frontend built successfully"
	@echo "Build output: frontend/dist/"
	@echo "=========================================="

destroy:
	@echo "Destroying $(ENV) environment..."
	@. $(VENV)/bin/activate && $(CDK) destroy --all --context env=$(ENV) --force
	@echo "✓ Destruction complete"

destroy-dev:
	@$(MAKE) destroy ENV=dev

destroy-prod:
	@echo "⚠️  WARNING: Destroying PRODUCTION environment"
	@echo "This will remove all infrastructure (tables may be retained based on removal_policy)"
	@read -p "Type 'DESTROY PRODUCTION' to confirm: " confirm; \
	if [ "$$confirm" = "DESTROY PRODUCTION" ]; then \
		$(MAKE) destroy ENV=prod; \
	else \
		echo "Destruction cancelled"; \
		exit 1; \
	fi

clean:
	@echo "Cleaning up..."
	@rm -rf $(VENV)
	@rm -rf cdk.out
	@rm -rf .cdk.staging
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Cleanup complete"


fix-stuck-stack:
	@echo "Fixing stuck CloudFormation stack..."
	@chmod +x fix-stuck-stack.sh
	@./fix-stuck-stack.sh

clean-aws:
	@echo "Complete AWS cleanup for $(ENV) environment..."
	@chmod +x clean-all-aws.sh
	@./clean-all-aws.sh $(ENV)


redeploy:
	@echo "Quick redeploy for $(ENV) environment..."
	@echo "This will destroy and redeploy all stacks"
	@$(MAKE) destroy ENV=$(ENV)
	@echo ""
	@echo "Waiting 5 seconds before redeploying..."
	@sleep 5
	@$(MAKE) deploy ENV=$(ENV)
	@echo "✓ Redeploy complete"


costs:
	@echo "=========================================="
	@echo "AWS Cost Report"
	@echo "Environment: $(ENV)"
	@echo "Period: Last 30 days"
	@echo "=========================================="
	@echo ""
	@echo "Cost by Service (last 30 days):"
	@aws ce get-cost-and-usage \
		--time-period Start=$$(date -v-30d +%Y-%m-%d),End=$$(date +%Y-%m-%d) \
		--granularity MONTHLY \
		--metrics BlendedCost \
		--group-by Type=SERVICE \
		--query 'ResultsByTime[0].Groups[?Metrics.BlendedCost.Amount > `0.01`].[Keys[0], Metrics.BlendedCost.Amount]' \
		--output table | awk 'NR==1 || NR==2 || NR==3 {print} NR>3 {printf "| %-40s | $$%-10.2f |\n", $$2, $$4}'
	@echo ""
	@echo "Total cost for last 30 days:"
	@aws ce get-cost-and-usage \
		--time-period Start=$$(date -v-30d +%Y-%m-%d),End=$$(date +%Y-%m-%d) \
		--granularity MONTHLY \
		--metrics BlendedCost \
		--query 'ResultsByTime[0].Total.BlendedCost.[Amount, Unit]' \
		--output text | awk '{printf "  $$%.2f %s\n", $$1, $$2}'
	@echo ""
	@echo "Daily breakdown (last 7 days):"
	@aws ce get-cost-and-usage \
		--time-period Start=$$(date -v-7d +%Y-%m-%d),End=$$(date +%Y-%m-%d) \
		--granularity DAILY \
		--metrics BlendedCost \
		--query 'ResultsByTime[].[TimePeriod.Start, Total.BlendedCost.Amount]' \
		--output text | awk '{printf "  %s: $$%.2f\n", $$1, $$2}'
	@echo ""
	@echo "=========================================="
	@echo "Note: Shows costs for all resources in your AWS account."
	@echo "=========================================="


db-backup:
	@echo "=========================================="
	@echo "Creating DynamoDB On-Demand Backup"
	@echo "Environment: $(ENV)"
	@echo "Table: impressionnistes-registration-$(ENV)"
	@echo "=========================================="
	@echo ""
	@TIMESTAMP=$$(date +%Y%m%d-%H%M%S); \
	BACKUP_NAME="impressionnistes-$(ENV)-$$TIMESTAMP"; \
	echo "Creating AWS backup: $$BACKUP_NAME"; \
	echo ""; \
	BACKUP_ARN=$$(aws dynamodb create-backup \
		--table-name impressionnistes-registration-$(ENV) \
		--backup-name $$BACKUP_NAME \
		--query 'BackupDetails.BackupArn' \
		--output text); \
	echo "Backup initiated..."; \
	echo ""; \
	echo "Waiting for backup to complete..."; \
	aws dynamodb describe-backup --backup-arn $$BACKUP_ARN --query 'BackupDescription.BackupDetails.BackupStatus' --output text | \
		while read status; do \
			if [ "$$status" = "AVAILABLE" ]; then \
				break; \
			fi; \
			sleep 2; \
		done; \
	echo ""; \
	echo "=========================================="
	@echo "✓ Backup created successfully!"
	@echo ""
	@echo "Backup Name: $$BACKUP_NAME"
	@echo "Backup ARN: $$BACKUP_ARN"
	@echo ""
	@echo "To list all backups: make db-list-backups"
	@echo "To restore: make db-restore-backup BACKUP_ARN=<arn>"
	@echo "=========================================="

db-backup-local:
	@echo "=========================================="
	@echo "Creating Local Database Backup"
	@echo "Environment: $(ENV)"
	@echo "Table: impressionnistes-registration-$(ENV)"
	@echo "=========================================="
	@echo ""
	@mkdir -p exports
	@TIMESTAMP=$$(date +%Y%m%d-%H%M%S); \
	BACKUP_FILE="exports/backup-$(ENV)-$$TIMESTAMP.json"; \
	echo "Creating local backup..."; \
	aws dynamodb scan \
		--table-name impressionnistes-registration-$(ENV) \
		--output json > $$BACKUP_FILE; \
	ITEM_COUNT=$$(cat $$BACKUP_FILE | python3 -c "import json, sys; print(len(json.load(sys.stdin).get('Items', [])))"); \
	FILE_SIZE=$$(ls -lh $$BACKUP_FILE | awk '{print $$5}'); \
	echo ""; \
	echo "=========================================="
	@echo "✓ Local backup created successfully!"
	@echo ""
	@echo "File: $$BACKUP_FILE"
	@echo "Items: $$ITEM_COUNT"
	@echo "Size: $$FILE_SIZE"
	@echo ""
	@echo "Note: This is a local file backup. For AWS-managed backups, use 'make db-backup'"
	@echo "=========================================="

db-list-backups:
	@echo "=========================================="
	@echo "DynamoDB Backups"
	@echo "Environment: $(ENV)"
	@echo "Table: impressionnistes-registration-$(ENV)"
	@echo "=========================================="
	@echo ""
	@aws dynamodb list-backups \
		--table-name impressionnistes-registration-$(ENV) \
		--query 'BackupSummaries[].{Name:BackupName,Status:BackupStatus,Created:BackupCreationDateTime,Size:BackupSizeBytes}' \
		--output table
	@echo ""
	@echo "To restore a backup: make db-restore-backup BACKUP_ARN=<arn>"

db-restore-backup:
	@echo "=========================================="
	@echo "Restore DynamoDB Backup"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ -z "$(BACKUP_ARN)" ]; then \
		echo "❌ Error: BACKUP_ARN parameter required"; \
		echo ""; \
		echo "Usage:"; \
		echo "  make db-restore-backup BACKUP_ARN=<backup-arn>"; \
		echo ""; \
		echo "To list available backups:"; \
		echo "  make db-list-backups"; \
		echo ""; \
		exit 1; \
	fi
	@echo "⚠️  WARNING: This will restore the table from backup"
	@echo ""
	@echo "Backup ARN: $(BACKUP_ARN)"
	@echo "Target Table: impressionnistes-registration-$(ENV)-restored"
	@echo ""
	@echo "Note: This creates a NEW table. You'll need to manually:"
	@echo "  1. Verify the restored data"
	@echo "  2. Delete the old table"
	@echo "  3. Rename the restored table"
	@echo ""
	@read -p "Continue? (yes/no): " confirm; \
	if [ "$confirm" != "yes" ]; then \
		echo "Restore cancelled"; \
		exit 1; \
	fi
	@echo ""
	@echo "Restoring backup..."
	@aws dynamodb restore-table-from-backup \
		--target-table-name impressionnistes-registration-$(ENV)-restored \
		--backup-arn $(BACKUP_ARN)
	@echo ""
	@echo "=========================================="
	@echo "✓ Restore initiated!"
	@echo ""
	@echo "Table: impressionnistes-registration-$(ENV)-restored"
	@echo ""
	@echo "The restore process may take several minutes."
	@echo "Check status with: aws dynamodb describe-table --table-name impressionnistes-registration-$(ENV)-restored"
	@echo "=========================================="

db-view:
	@echo "=========================================="
	@echo "DynamoDB Table Contents"
	@echo "Environment: $(ENV)"
	@echo "Table: impressionnistes-registration-$(ENV)"
	@echo "=========================================="
	@echo ""
	@echo "Configuration items:"
	@aws dynamodb scan \
		--table-name impressionnistes-registration-$(ENV) \
		--filter-expression "PK = :pk" \
		--expression-attribute-values '{":pk":{"S":"CONFIG"}}' \
		--query 'Items[].{Type:SK.S,UpdatedAt:updated_at.S}' \
		--output table
	@echo ""
	@echo "Race definitions (showing first 10):"
	@aws dynamodb scan \
		--table-name impressionnistes-registration-$(ENV) \
		--filter-expression "PK = :pk" \
		--expression-attribute-values '{":pk":{"S":"RACE"}}' \
		--max-items 10 \
		--query 'Items[].{ID:SK.S,Name:name.S,Event:event_type.S,Boat:boat_type.S}' \
		--output table
	@echo ""
	@echo "Total items in table:"
	@aws dynamodb scan \
		--table-name impressionnistes-registration-$(ENV) \
		--select COUNT \
		--query 'Count' \
		--output text | awk '{print "  " $$1 " items"}'
	@echo ""
	@echo "For full export, use: make db-export"

db-export:
	@echo "=========================================="
	@echo "Exporting DynamoDB Table to CSV"
	@echo "Environment: $(ENV)"
	@echo "Table: impressionnistes-registration-$(ENV)"
	@echo "=========================================="
	@echo ""
	@mkdir -p exports
	@TIMESTAMP=$$(date +%Y%m%d-%H%M%S); \
	JSON_FILE="exports/dynamodb-$(ENV)-$$TIMESTAMP.json"; \
	echo "1. Scanning DynamoDB table..."; \
	aws dynamodb scan \
		--table-name impressionnistes-registration-$(ENV) \
		--output json > $$JSON_FILE; \
	ITEM_COUNT=$$(cat $$JSON_FILE | python3 -c "import json, sys; print(len(json.load(sys.stdin).get('Items', [])))"); \
	echo "   ✓ Exported $$ITEM_COUNT items to $$JSON_FILE"; \
	echo ""; \
	echo "2. Converting to CSV..."; \
	chmod +x export-db.py; \
	./export-db.py $$JSON_FILE; \
	echo ""; \
	echo "3. Splitting by entity type..."; \
	./export-db.py $$JSON_FILE --split --output-dir exports; \
	echo ""; \
	echo "=========================================="
	@echo "✓ Export complete!"
	@echo ""
	@echo "Files created:"
	@ls -lh exports/ | tail -n +2 | grep "$$(date +%Y%m%d)" | awk '{print "  " $$9 " (" $$5 ")"}'
	@echo ""
	@echo "To view: open exports/"
	@echo "=========================================="


cognito-create-admin:
	@echo "=========================================="
	@echo "Creating Admin User in Cognito"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ -z "$(EMAIL)" ]; then \
		echo "❌ Error: EMAIL parameter required"; \
		echo "Usage: make cognito-create-admin EMAIL=admin@example.com"; \
		exit 1; \
	fi
	@echo "Getting User Pool ID..."
	@USER_POOL_ID=$$(aws cloudformation describe-stacks \
		--stack-name ImpressionnistesAuth-$(ENV) \
		--query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
		--output text 2>/dev/null); \
	if [ -z "$$USER_POOL_ID" ]; then \
		echo "❌ Error: Could not find User Pool. Has the auth stack been deployed?"; \
		exit 1; \
	fi; \
	echo "User Pool ID: $$USER_POOL_ID"; \
	echo ""; \
	echo "Creating user: $(EMAIL)"; \
	aws cognito-idp admin-create-user \
		--user-pool-id $$USER_POOL_ID \
		--username $(EMAIL) \
		--user-attributes \
			Name=email,Value=$(EMAIL) \
			Name=email_verified,Value=true \
			Name=given_name,Value=Admin \
			Name=family_name,Value=RCPM \
			Name=custom:role,Value=admin \
		--desired-delivery-mediums EMAIL 2>/dev/null || echo "User may already exist"; \
	echo ""; \
	echo "Adding user to 'admins' group..."; \
	aws cognito-idp admin-add-user-to-group \
		--user-pool-id $$USER_POOL_ID \
		--username $(EMAIL) \
		--group-name admins; \
	echo ""; \
	echo "=========================================="
	@echo "✓ Admin user created successfully!"
	@echo ""
	@echo "User: $(EMAIL)"
	@echo "Group: admins"
	@echo ""
	@echo "The user will receive an email with a temporary password."
	@echo "They must change it on first login."
	@echo "=========================================="

cognito-list-users:
	@echo "=========================================="
	@echo "Cognito Users"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@USER_POOL_ID=$$(aws cloudformation describe-stacks \
		--stack-name ImpressionnistesAuth-$(ENV) \
		--query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
		--output text 2>/dev/null); \
	if [ -z "$$USER_POOL_ID" ]; then \
		echo "❌ Error: Could not find User Pool"; \
		exit 1; \
	fi; \
	echo "Fetching users..."; \
	echo ""; \
	aws cognito-idp list-users \
		--user-pool-id $$USER_POOL_ID \
		--query 'Users[].[Username, UserStatus, Enabled, join(`, `, Attributes[?Name==`email`].Value)]' \
		--output table; \
	echo ""; \
	echo "Groups:"; \
	for group in admins team_managers devops; do \
		echo ""; \
		echo "  $$group:"; \
		aws cognito-idp list-users-in-group \
			--user-pool-id $$USER_POOL_ID \
			--group-name $$group \
			--query 'Users[].Username' \
			--output text 2>/dev/null | sed 's/^/    /' || echo "    (none)"; \
	done
	@echo ""
	@echo "=========================================="

cognito-add-to-group:
	@echo "=========================================="
	@echo "Add User to Cognito Group"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ -z "$(EMAIL)" ]; then \
		echo "❌ Error: EMAIL parameter required"; \
		echo "Usage: make cognito-add-to-group EMAIL=user@example.com GROUP=admins"; \
		exit 1; \
	fi
	@if [ -z "$(GROUP)" ]; then \
		echo "❌ Error: GROUP parameter required"; \
		echo "Available groups: admins, team_managers, devops"; \
		echo "Usage: make cognito-add-to-group EMAIL=user@example.com GROUP=admins"; \
		exit 1; \
	fi
	@USER_POOL_ID=$$(aws cloudformation describe-stacks \
		--stack-name ImpressionnistesAuth-$(ENV) \
		--query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
		--output text 2>/dev/null); \
	if [ -z "$$USER_POOL_ID" ]; then \
		echo "❌ Error: Could not find User Pool"; \
		exit 1; \
	fi; \
	echo "Adding $(EMAIL) to group '$(GROUP)'..."; \
	aws cognito-idp admin-add-user-to-group \
		--user-pool-id $$USER_POOL_ID \
		--username $(EMAIL) \
		--group-name $(GROUP); \
	echo ""; \
	echo "✓ User added to group successfully!"
	@echo "=========================================="


delete-team-manager:
	@echo "=========================================="
	@echo "Delete Team Manager Account"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ -z "$(EMAIL)" ]; then \
		echo "❌ Error: EMAIL parameter required"; \
		echo "Usage: make delete-team-manager EMAIL=user@example.com"; \
		echo "       make delete-team-manager EMAIL=user@example.com ENV=prod"; \
		echo ""; \
		echo "⚠️  This will delete:"; \
		echo "  - Cognito user account"; \
		echo "  - User profile in DynamoDB"; \
		echo "  - All crew members"; \
		echo "  - All boat registrations"; \
		echo "  - All consent records"; \
		echo "  - All rental requests"; \
		exit 1; \
	fi
	@echo "⚠️  WARNING: This will permanently delete $(EMAIL) and ALL related data!"
	@echo ""
	@. venv/bin/activate && \
		python3 scripts/delete_team_manager.py $(EMAIL) --environment $(ENV)
	@echo ""


db-migrate:
	@echo "=========================================="
	@echo "Running Database Migration"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ -z "$(MIGRATION)" ]; then \
		echo "❌ Error: MIGRATION parameter required"; \
		echo "Usage: make db-migrate MIGRATION=your_migration [TEAM_MANAGER_ID=your-id]"; \
		echo ""; \
		echo "Available migrations:"; \
		if ls ../functions/migrations/*.py 2>/dev/null | grep -v __pycache__ >/dev/null; then \
			ls -1 ../functions/migrations/*.py 2>/dev/null | grep -v __pycache__ | xargs -n1 basename | sed 's/.py//' | sed 's/^/  - /'; \
		else \
			echo "  (none - see functions/migrations/README.md for template)"; \
		fi; \
		exit 1; \
	fi
	@if [ ! -f "../functions/migrations/$(MIGRATION).py" ]; then \
		echo "❌ Error: Migration '$(MIGRATION)' not found"; \
		echo ""; \
		echo "Available migrations:"; \
		if ls ../functions/migrations/*.py 2>/dev/null | grep -v __pycache__ >/dev/null; then \
			ls -1 ../functions/migrations/*.py 2>/dev/null | grep -v __pycache__ | xargs -n1 basename | sed 's/.py//' | sed 's/^/  - /'; \
		else \
			echo "  (none - see functions/migrations/README.md for template)"; \
		fi; \
		exit 1; \
	fi
	@echo "Migration: $(MIGRATION)"
	@if [ -n "$(TEAM_MANAGER_ID)" ]; then \
		echo "Team Manager ID: $(TEAM_MANAGER_ID)"; \
	else \
		echo "Team Manager ID: (not provided - running as system)"; \
	fi
	@echo "Table: impressionnistes-registration-$(ENV)"
	@echo ""
	@read -p "Continue? (yes/no): " confirm; \
	if [ "$$confirm" != "yes" ]; then \
		echo "Migration cancelled"; \
		exit 1; \
	fi
	@echo ""
	@echo "Running migration..."
	@cd ../functions/migrations && \
		export TABLE_NAME=impressionnistes-registration-$(ENV) && \
		export TEAM_MANAGER_ID=$(TEAM_MANAGER_ID) && \
		../../infrastructure/$(VENV)/bin/python $(MIGRATION).py
	@echo ""
	@echo "=========================================="
	@echo "✓ Migration complete!"
	@echo "=========================================="


db-reset:
	@echo "=========================================="
	@echo "Reset Database to Initial State"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@echo "⚠️  WARNING: This will DELETE ALL DATA and reset to initial configuration!"
	@echo ""
	@echo "This will:"
	@echo "  - Delete all team manager profiles"
	@echo "  - Delete all crew members"
	@echo "  - Delete all boat registrations"
	@echo "  - Delete all payment records"
	@echo "  - Reset configuration to defaults"
	@echo "  - Keep race definitions (42 races)"
	@echo ""
	@echo "Table: impressionnistes-registration-$(ENV)"
	@echo ""
	@read -p "Type 'RESET' to confirm: " confirm; \
	if [ "$$confirm" != "RESET" ]; then \
		echo "Reset cancelled"; \
		exit 1; \
	fi
	@echo ""
	@echo "Step 1: Scanning for user data..."
	@aws dynamodb scan \
		--table-name impressionnistes-registration-$(ENV) \
		--filter-expression "begins_with(PK, :team) OR begins_with(PK, :user)" \
		--expression-attribute-values '{":team":{"S":"TEAM"},":user":{"S":"USER"}}' \
		--projection-expression "PK,SK" \
		--region eu-west-3 \
		--output json > /tmp/db-reset-items.json
	@echo "✓ Found items to delete"
	@echo ""
	@echo "Step 2: Deleting user data..."
	@jq -r '.Items[] | "{\"PK\": {\"S\": \"\(.PK.S)\"}, \"SK\": {\"S\": \"\(.SK.S)\"}}"' /tmp/db-reset-items.json | \
		while read -r key; do \
			aws dynamodb delete-item \
				--table-name impressionnistes-registration-$(ENV) \
				--key "$$key" \
				--region eu-west-3 2>/dev/null; \
		done
	@echo "✓ User data deleted"
	@echo ""
	@echo "Step 3: Resetting configuration..."
	@aws dynamodb delete-item \
		--table-name impressionnistes-registration-$(ENV) \
		--key '{"PK":{"S":"CONFIG"},"SK":{"S":"SYSTEM"}}' \
		--region eu-west-3 2>/dev/null || true
	@aws dynamodb delete-item \
		--table-name impressionnistes-registration-$(ENV) \
		--key '{"PK":{"S":"CONFIG"},"SK":{"S":"PRICING"}}' \
		--region eu-west-3 2>/dev/null || true
	@aws dynamodb delete-item \
		--table-name impressionnistes-registration-$(ENV) \
		--key '{"PK":{"S":"CONFIG"},"SK":{"S":"NOTIFICATION"}}' \
		--region eu-west-3 2>/dev/null || true
	@echo "✓ Configuration deleted"
	@echo ""
	@echo "Step 4: Reinitializing configuration..."
	@$(PYTHON) scripts/reinit_config.py eu-west-3
	@echo ""
	@echo "=========================================="
	@echo "✓ Database reset complete!"
	@echo "=========================================="
	@echo ""
	@echo "Summary:"
	@echo "  - All user data deleted"
	@echo "  - Configuration reset to defaults"
	@echo "  - Race definitions preserved (42 races)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Users need to re-register"
	@echo "  2. Check configuration: make db-view"
	@echo "  3. Verify races: aws dynamodb query --table-name impressionnistes-registration-$(ENV) --key-condition-expression 'PK = :pk' --expression-attribute-values '{\":pk\":{\"S\":\"RACE\"}}' --query 'Count'"


db-cleanup-rental-boats:
	@echo "=========================================="
	@echo "Delete Old Rental Boat Records"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@echo "This will delete all RENTAL_BOAT records from the database."
	@echo "These are old inventory-based rental records that have been"
	@echo "replaced by the new RENTAL_REQUEST system."
	@echo ""
	@chmod +x delete_old_rental_boats.py
	@$(PYTHON) delete_old_rental_boats.py --env $(ENV)
	@echo ""

db-cleanup-rental-boats-dry-run:
	@echo "=========================================="
	@echo "Preview Old Rental Boat Records (Dry Run)"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@chmod +x delete_old_rental_boats.py
	@$(PYTHON) delete_old_rental_boats.py --env $(ENV) --dry-run
	@echo ""

# ==========================================
# Email/SES Management Commands
# ==========================================

ses-verify-email:
	@echo "=========================================="
	@echo "Verify Email Address in AWS SES"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ -z "$(EMAIL)" ]; then \
		echo "❌ Error: EMAIL parameter required"; \
		echo ""; \
		echo "Usage:"; \
		echo "  make ses-verify-email EMAIL=your-email@example.com"; \
		echo "  make ses-verify-email EMAIL=your-email@example.com ENV=prod"; \
		echo ""; \
		echo "Examples:"; \
		echo "  make ses-verify-email EMAIL=course.impressionnistes@rcpm-aviron.fr"; \
		echo "  make ses-verify-email EMAIL=vincent.bontoux@outlook.fr ENV=prod"; \
		echo ""; \
		exit 1; \
	fi
	@echo "Sending verification email to: $(EMAIL)"
	@echo "Region: eu-west-1"
	@echo ""
	@aws ses verify-email-identity \
		--email-address $(EMAIL) \
		--region eu-west-1
	@echo ""
	@echo "=========================================="
	@echo "✓ Verification email sent!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Check inbox for $(EMAIL)"
	@echo "  2. Click the verification link in the email"
	@echo "  3. Wait ~1 minute for AWS to process"
	@echo "  4. Verify status: make ses-list-verified ENV=$(ENV)"
	@echo "=========================================="

ses-list-verified:
	@echo "=========================================="
	@echo "List Verified Email Addresses"
	@echo "Environment: $(ENV)"
	@echo "Region: eu-west-1"
	@echo "=========================================="
	@echo ""
	@aws ses list-verified-email-addresses \
		--region eu-west-1 \
		--query 'VerifiedEmailAddresses' \
		--output table
	@echo ""
	@echo "To verify a new email: make ses-verify-email EMAIL=your@email.com ENV=$(ENV)"

ses-check-email:
	@echo "=========================================="
	@echo "Check Email Verification Status"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ -z "$(EMAIL)" ]; then \
		echo "❌ Error: EMAIL parameter required"; \
		echo ""; \
		echo "Usage:"; \
		echo "  make ses-check-email EMAIL=your-email@example.com"; \
		echo "  make ses-check-email EMAIL=your-email@example.com ENV=prod"; \
		echo ""; \
		exit 1; \
	fi
	@echo "Checking: $(EMAIL)"
	@echo "Region: eu-west-1"
	@echo ""
	@VERIFIED=$$(aws ses list-verified-email-addresses --region eu-west-1 --query 'VerifiedEmailAddresses' --output text | grep -w "$(EMAIL)" || echo ""); \
	if [ -n "$$VERIFIED" ]; then \
		echo "✅ $(EMAIL) is VERIFIED"; \
	else \
		echo "❌ $(EMAIL) is NOT verified"; \
		echo ""; \
		echo "To verify: make ses-verify-email EMAIL=$(EMAIL) ENV=$(ENV)"; \
	fi
	@echo ""

ses-get-quota:
	@echo "=========================================="
	@echo "AWS SES Sending Quota"
	@echo "Environment: $(ENV)"
	@echo "Region: eu-west-1"
	@echo "=========================================="
	@echo ""
	@aws ses get-send-quota \
		--region eu-west-1 \
		--output table
	@echo ""
	@echo "Note: In sandbox mode, you can only send to verified addresses."
	@echo "To request production access: make ses-request-production"

ses-get-statistics:
	@echo "=========================================="
	@echo "AWS SES Sending Statistics"
	@echo "Environment: $(ENV)"
	@echo "Region: eu-west-1"
	@echo "=========================================="
	@echo ""
	@aws ses get-send-statistics \
		--region eu-west-1 \
		--query 'SendDataPoints[-10:]' \
		--output table
	@echo ""
	@echo "Showing last 10 data points (15-minute intervals)"

ses-request-production:
	@echo "=========================================="
	@echo "Request AWS SES Production Access"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@echo "To move out of sandbox mode and send to any email address:"
	@echo ""
	@echo "1. Go to AWS SES Console:"
	@echo "   https://console.aws.amazon.com/ses/"
	@echo ""
	@echo "2. Select region: eu-west-1 (Paris)"
	@echo ""
	@echo "3. Navigate to: Account dashboard"
	@echo ""
	@echo "4. Click: Request production access"
	@echo ""
	@echo "5. Fill out the form:"
	@echo "   - Mail type: Transactional"
	@echo "   - Website URL: Your registration website"
	@echo "   - Use case: Payment confirmation emails for rowing race registrations"
	@echo "   - Compliance: Explain bounce/complaint handling"
	@echo ""
	@echo "6. Submit and wait for approval (usually 24 hours)"
	@echo ""
	@echo "=========================================="

ses-verify-domain:
	@if [ -z "$(DOMAIN)" ]; then \
		echo "❌ Error: DOMAIN parameter required"; \
		echo "Usage: make ses-verify-domain DOMAIN=rcpm-aviron.fr ENV=$(ENV)"; \
		exit 1; \
	fi
	@echo "=========================================="
	@echo "Verify Domain in AWS SES"
	@echo "Environment: $(ENV)"
	@echo "Domain: $(DOMAIN)"
	@echo "=========================================="
	@echo ""
	@echo "Starting domain verification..."
	@aws ses verify-domain-identity --domain $(DOMAIN) --region eu-west-1
	@echo ""
	@echo "✅ Domain verification initiated!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Get the verification token:"
	@echo "   make ses-get-domain-token DOMAIN=$(DOMAIN) ENV=$(ENV)"
	@echo ""
	@echo "2. Add TXT record to your DNS:"
	@echo "   Name: _amazonses.$(DOMAIN)"
	@echo "   Type: TXT"
	@echo "   Value: [token from step 1]"
	@echo ""
	@echo "3. Enable DKIM (recommended for deliverability):"
	@echo "   make ses-enable-dkim DOMAIN=$(DOMAIN) ENV=$(ENV)"
	@echo ""
	@echo "=========================================="

ses-get-domain-token:
	@if [ -z "$(DOMAIN)" ]; then \
		echo "❌ Error: DOMAIN parameter required"; \
		echo "Usage: make ses-get-domain-token DOMAIN=rcpm-aviron.fr ENV=$(ENV)"; \
		exit 1; \
	fi
	@echo "=========================================="
	@echo "Get Domain Verification Token"
	@echo "Environment: $(ENV)"
	@echo "Domain: $(DOMAIN)"
	@echo "=========================================="
	@echo ""
	@aws ses get-identity-verification-attributes \
		--identities $(DOMAIN) \
		--region eu-west-1 \
		--query 'VerificationAttributes."$(DOMAIN)".VerificationToken' \
		--output text
	@echo ""
	@echo "Add this as a TXT record in your DNS:"
	@echo "  Name: _amazonses.$(DOMAIN)"
	@echo "  Type: TXT"
	@echo "  Value: [token above]"
	@echo ""
	@echo "=========================================="

ses-enable-dkim:
	@if [ -z "$(DOMAIN)" ]; then \
		echo "❌ Error: DOMAIN parameter required"; \
		echo "Usage: make ses-enable-dkim DOMAIN=rcpm-aviron.fr ENV=$(ENV)"; \
		exit 1; \
	fi
	@echo "=========================================="
	@echo "Enable DKIM for Domain"
	@echo "Environment: $(ENV)"
	@echo "Domain: $(DOMAIN)"
	@echo "=========================================="
	@echo ""
	@echo "Getting DKIM tokens..."
	@aws ses verify-domain-dkim \
		--domain $(DOMAIN) \
		--region eu-west-1 \
		--query 'DkimTokens' \
		--output table
	@echo ""
	@echo "✅ DKIM tokens generated!"
	@echo ""
	@echo "Add these 3 CNAME records to your DNS:"
	@echo "For each token above, create:"
	@echo "  Name: [token]._domainkey.$(DOMAIN)"
	@echo "  Type: CNAME"
	@echo "  Value: [token].dkim.amazonses.com"
	@echo ""
	@echo "Example for first token:"
	@FIRST_TOKEN=$$(aws ses verify-domain-dkim --domain $(DOMAIN) --region eu-west-1 --query 'DkimTokens[0]' --output text); \
	echo "  Name: $$FIRST_TOKEN._domainkey.$(DOMAIN)"; \
	echo "  Type: CNAME"; \
	echo "  Value: $$FIRST_TOKEN.dkim.amazonses.com"
	@echo ""
	@echo "After adding all 3 CNAME records, DKIM will be automatically enabled."
	@echo "Check status with: make ses-check-domain DOMAIN=$(DOMAIN) ENV=$(ENV)"
	@echo ""
	@echo "=========================================="

ses-check-domain:
	@if [ -z "$(DOMAIN)" ]; then \
		echo "❌ Error: DOMAIN parameter required"; \
		echo "Usage: make ses-check-domain DOMAIN=rcpm-aviron.fr ENV=$(ENV)"; \
		exit 1; \
	fi
	@echo "=========================================="
	@echo "Check Domain Verification Status"
	@echo "Environment: $(ENV)"
	@echo "Domain: $(DOMAIN)"
	@echo "=========================================="
	@echo ""
	@aws ses get-identity-verification-attributes \
		--identities $(DOMAIN) \
		--region eu-west-1 \
		--output table
	@echo ""
	@echo "Check DKIM status:"
	@aws ses get-identity-dkim-attributes \
		--identities $(DOMAIN) \
		--region eu-west-1 \
		--output table
	@echo ""
	@echo "=========================================="

# ==========================================
# Secrets Management Commands
# ==========================================

secrets-list:
	@echo "=========================================="
	@echo "Listing Secrets"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@echo "Stripe Secrets:"
	@aws secretsmanager list-secrets \
		--filters Key=name,Values=impressionnistes/stripe \
		--query 'SecretList[].{Name:Name,LastChanged:LastChangedDate}' \
		--output table
	@echo ""
	@echo "Slack Secrets:"
	@aws secretsmanager list-secrets \
		--filters Key=name,Values=impressionnistes/slack \
		--query 'SecretList[].{Name:Name,LastChanged:LastChangedDate}' \
		--output table

secrets-show:
	@echo "=========================================="
	@echo "Showing All Secret Values"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@echo "⚠️  WARNING: This will display sensitive secret values!"
	@echo ""
	@echo "Stripe API Key:"
	@aws secretsmanager get-secret-value \
		--secret-id impressionnistes/stripe/api_key \
		--query 'SecretString' \
		--output text | python3 -m json.tool
	@echo ""
	@echo "Stripe Webhook Secret:"
	@aws secretsmanager get-secret-value \
		--secret-id impressionnistes/stripe/webhook_secret \
		--query 'SecretString' \
		--output text | python3 -m json.tool
	@echo ""
	@echo "Slack Admin Webhook:"
	@aws secretsmanager get-secret-value \
		--secret-id impressionnistes/slack/admin_webhook \
		--query 'SecretString' \
		--output text | python3 -m json.tool
	@echo ""
	@echo "Slack DevOps Webhook:"
	@aws secretsmanager get-secret-value \
		--secret-id impressionnistes/slack/devops_webhook \
		--query 'SecretString' \
		--output text | python3 -m json.tool

secrets-show-stripe:
	@echo "=========================================="
	@echo "Showing Stripe Secrets"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@echo "Stripe API Key:"
	@aws secretsmanager get-secret-value \
		--secret-id impressionnistes/stripe/api_key \
		--query 'SecretString' \
		--output text | python3 -c "import json, sys; data=json.load(sys.stdin); print(f\"  API Key: {data['api_key'][:20]}...{data['api_key'][-4:]}\")"
	@echo ""
	@echo "Stripe Webhook Secret:"
	@aws secretsmanager get-secret-value \
		--secret-id impressionnistes/stripe/webhook_secret \
		--query 'SecretString' \
		--output text | python3 -c "import json, sys; data=json.load(sys.stdin); print(f\"  Webhook Secret: {data['webhook_secret'][:20]}...{data['webhook_secret'][-4:]}\")"
	@echo ""
	@echo "Note: Showing partial values for security. Use 'make secrets-show' to see full values."

secrets-update-stripe:
	@echo "=========================================="
	@echo "Update Stripe Secrets"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ -z "$(STRIPE_API_KEY)" ]; then \
		echo "❌ Error: STRIPE_API_KEY not provided"; \
		echo ""; \
		echo "Usage:"; \
		echo "  make secrets-update-stripe STRIPE_API_KEY=sk_test_xxx"; \
		echo "  make secrets-update-stripe STRIPE_API_KEY=sk_test_xxx STRIPE_WEBHOOK_SECRET=whsec_xxx"; \
		echo ""; \
		exit 1; \
	fi
	@echo "Updating Stripe API Key..."
	@aws secretsmanager update-secret \
		--secret-id impressionnistes/stripe/api_key \
		--secret-string '{"api_key":"$(STRIPE_API_KEY)"}' \
		--output text > /dev/null
	@echo "✓ Stripe API Key updated"
	@if [ -n "$(STRIPE_WEBHOOK_SECRET)" ]; then \
		echo ""; \
		echo "Updating Stripe Webhook Secret..."; \
		aws secretsmanager update-secret \
			--secret-id impressionnistes/stripe/webhook_secret \
			--secret-string '{"webhook_secret":"$(STRIPE_WEBHOOK_SECRET)"}' \
			--output text > /dev/null; \
		echo "✓ Stripe Webhook Secret updated"; \
	fi
	@echo ""
	@echo "=========================================="
	@echo "✓ Secrets updated successfully!"
	@echo "=========================================="

secrets-sync:
	@echo "=========================================="
	@echo "Sync Secrets from secrets.$(ENV).json to AWS"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ ! -f "secrets.$(ENV).json" ]; then \
		echo "❌ Error: secrets.$(ENV).json not found"; \
		echo ""; \
		echo "Please create secrets.$(ENV).json with your secrets"; \
		exit 1; \
	fi
	@echo "Reading secrets from secrets.$(ENV).json..."
	@echo ""
	@STRIPE_API_KEY=$$(python3 -c "import json; f=open('secrets.$(ENV).json'); data=json.load(f); print(data.get('stripe_secret_key', ''))"); \
	STRIPE_WEBHOOK=$$(python3 -c "import json; f=open('secrets.$(ENV).json'); data=json.load(f); print(data.get('stripe_webhook_secret', ''))"); \
	SLACK_ADMIN=$$(python3 -c "import json; f=open('secrets.$(ENV).json'); data=json.load(f); print(data.get('slack_webhook_admin', ''))"); \
	SLACK_DEVOPS=$$(python3 -c "import json; f=open('secrets.$(ENV).json'); data=json.load(f); print(data.get('slack_webhook_devops', ''))"); \
	if [ -n "$$STRIPE_API_KEY" ]; then \
		echo "Updating Stripe API Key..."; \
		aws secretsmanager update-secret \
			--secret-id impressionnistes/stripe/api_key \
			--secret-string "{\"api_key\":\"$$STRIPE_API_KEY\"}" \
			--output text > /dev/null && echo "  ✓ Stripe API Key updated"; \
	fi; \
	if [ -n "$$STRIPE_WEBHOOK" ]; then \
		echo "Updating Stripe Webhook Secret..."; \
		aws secretsmanager update-secret \
			--secret-id impressionnistes/stripe/webhook_secret \
			--secret-string "{\"webhook_secret\":\"$$STRIPE_WEBHOOK\"}" \
			--output text > /dev/null && echo "  ✓ Stripe Webhook Secret updated"; \
	fi; \
	if [ -n "$$SLACK_ADMIN" ]; then \
		echo "Updating Slack Admin Webhook..."; \
		aws secretsmanager update-secret \
			--secret-id impressionnistes/slack/admin_webhook \
			--secret-string "{\"webhook_url\":\"$$SLACK_ADMIN\"}" \
			--output text > /dev/null && echo "  ✓ Slack Admin Webhook updated"; \
	fi; \
	if [ -n "$$SLACK_DEVOPS" ]; then \
		echo "Updating Slack DevOps Webhook..."; \
		aws secretsmanager update-secret \
			--secret-id impressionnistes/slack/devops_webhook \
			--secret-string "{\"webhook_url\":\"$$SLACK_DEVOPS\"}" \
			--output text > /dev/null && echo "  ✓ Slack DevOps Webhook updated"; \
	fi
	@echo ""
	@echo "=========================================="
	@echo "✓ All secrets synced from secrets.$(ENV).json!"
	@echo "=========================================="

secrets-sync-dev:
	@$(MAKE) secrets-sync ENV=dev

secrets-sync-prod:
	@echo "⚠️  WARNING: Syncing secrets to PRODUCTION"
	@read -p "Type 'SYNC PROD' to confirm: " confirm; \
	if [ "$$confirm" = "SYNC PROD" ]; then \
		$(MAKE) secrets-sync ENV=prod; \
	else \
		echo "Sync cancelled"; \
		exit 1; \
	fi

secrets-delete-all:
	@echo "=========================================="
	@echo "Delete All Secrets from AWS Secrets Manager"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@echo "⚠️  WARNING: This will delete all 4 secrets:"
	@echo "  - impressionnistes/stripe/api_key"
	@echo "  - impressionnistes/stripe/webhook_secret"
	@echo "  - impressionnistes/slack/admin_webhook"
	@echo "  - impressionnistes/slack/devops_webhook"
	@echo ""
	@if [ "$(ENV)" = "prod" ]; then \
		echo "⚠️  PRODUCTION ENVIRONMENT"; \
		read -p "Type 'DELETE PROD SECRETS' to confirm: " confirm; \
		if [ "$$confirm" != "DELETE PROD SECRETS" ]; then \
			echo "Deletion cancelled"; \
			exit 1; \
		fi; \
	else \
		read -p "Type 'DELETE' to confirm: " confirm; \
		if [ "$$confirm" != "DELETE" ]; then \
			echo "Deletion cancelled"; \
			exit 1; \
		fi; \
	fi
	@echo ""
	@echo "Deleting secrets (force delete, no recovery)..."
	@for secret in "impressionnistes/stripe/api_key" "impressionnistes/stripe/webhook_secret" "impressionnistes/slack/admin_webhook" "impressionnistes/slack/devops_webhook"; do \
		echo "Deleting $$secret..."; \
		aws secretsmanager delete-secret \
			--secret-id $$secret \
			--force-delete-without-recovery \
			--output text > /dev/null 2>&1 && echo "  ✓ Deleted $$secret" || echo "  ⚠️  $$secret not found or already deleted"; \
	done
	@echo ""
	@echo "=========================================="
	@echo "✓ All secrets deleted!"
	@echo "=========================================="

secrets-delete-all-prod:
	@$(MAKE) secrets-delete-all ENV=prod AWS_PROFILE=rcpm

destroy-secrets:
	@echo "=========================================="
	@echo "Destroy Secrets Stack"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ "$(ENV)" = "prod" ]; then \
		echo "⚠️  WARNING: Destroying PRODUCTION Secrets Stack"; \
		read -p "Type 'DESTROY PROD' to confirm: " confirm; \
		if [ "$$confirm" != "DESTROY PROD" ]; then \
			echo "Destruction cancelled"; \
			exit 1; \
		fi; \
	else \
		read -p "Type 'DESTROY' to confirm: " confirm; \
		if [ "$$confirm" != "DESTROY" ]; then \
			echo "Destruction cancelled"; \
			exit 1; \
		fi; \
	fi
	@echo ""
	@echo "Destroying ImpressionnistesSecrets-$(ENV) stack..."
	@. $(VENV)/bin/activate && $(CDK) destroy ImpressionnistesSecrets-$(ENV) --context env=$(ENV) --force
	@echo ""
	@echo "=========================================="
	@echo "✓ Secrets stack destroyed!"
	@echo "=========================================="

destroy-secrets-prod:
	@$(MAKE) destroy-secrets ENV=prod

# ==========================================
# Boat Payment Management (Debug/Demo)
# ==========================================

boat-list-paid:
	@echo "=========================================="
	@echo "Listing Paid Boats"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ -z "$(TEAM_MANAGER_ID)" ]; then \
		echo "❌ Error: TEAM_MANAGER_ID not provided"; \
		echo ""; \
		echo "Usage:"; \
		echo "  make boat-list-paid TEAM_MANAGER_ID=your-user-id"; \
		echo ""; \
		exit 1; \
	fi
	@echo "Team Manager: $(TEAM_MANAGER_ID)"
	@echo "Table: impressionnistes-registration-$(ENV)"
	@echo ""
	@aws dynamodb query \
		--table-name impressionnistes-registration-$(ENV) \
		--key-condition-expression "PK = :pk AND begins_with(SK, :sk)" \
		--filter-expression "registration_status = :status" \
		--expression-attribute-values '{":pk":{"S":"TEAM#$(TEAM_MANAGER_ID)"},":sk":{"S":"BOAT#"},":status":{"S":"paid"}}' \
		--query 'Items[].{BoatID:boat_registration_id.S,EventType:event_type.S,BoatType:boat_type.S,Status:registration_status.S,PaidAt:paid_at.S}' \
		--output table

boat-unpay:
	@echo "=========================================="
	@echo "Reset Boat to Unpaid Status"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ -z "$(TEAM_MANAGER_ID)" ] || [ -z "$(BOAT_ID)" ]; then \
		echo "❌ Error: Missing required parameters"; \
		echo ""; \
		echo "Usage:"; \
		echo "  make boat-unpay TEAM_MANAGER_ID=your-user-id BOAT_ID=boat-id"; \
		echo ""; \
		echo "Example:"; \
		echo "  make boat-unpay TEAM_MANAGER_ID=717940ae-6051-70cb-9437-fac29614d317 BOAT_ID=1c33fcfa-b13c-4f34-a1fe-c9abaddba6e3"; \
		echo ""; \
		exit 1; \
	fi
	@echo "Team Manager: $(TEAM_MANAGER_ID)"
	@echo "Boat ID: $(BOAT_ID)"
	@echo "Table: impressionnistes-registration-$(ENV)"
	@echo ""
	@echo "⚠️  This will reset the boat to 'complete' status (unpaid)"
	@echo ""
	@read -p "Continue? (yes/no): " confirm; \
	if [ "$$confirm" != "yes" ]; then \
		echo "Operation cancelled"; \
		exit 1; \
	fi
	@echo ""
	@echo "Resetting boat status..."
	@aws dynamodb update-item \
		--table-name impressionnistes-registration-$(ENV) \
		--key '{"PK":{"S":"TEAM#$(TEAM_MANAGER_ID)"},"SK":{"S":"BOAT#$(BOAT_ID)"}}' \
		--update-expression "SET registration_status = :status, updated_at = :timestamp REMOVE paid_at, payment_id, stripe_payment_intent_id, locked_pricing" \
		--expression-attribute-values '{":status":{"S":"complete"},":timestamp":{"S":"'$$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}}' \
		--return-values ALL_NEW \
		--output json | python3 -c "import json, sys; data=json.load(sys.stdin); print(f\"✓ Boat {data['Attributes']['boat_registration_id']['S']} reset to 'complete' status\")"
	@echo ""
	@echo "=========================================="
	@echo "✓ Boat reset successfully!"
	@echo "=========================================="

boat-unpay-all:
	@echo "=========================================="
	@echo "Reset ALL Boats to Unpaid Status"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ -z "$(TEAM_MANAGER_ID)" ]; then \
		echo "❌ Error: TEAM_MANAGER_ID not provided"; \
		echo ""; \
		echo "Usage:"; \
		echo "  make boat-unpay-all TEAM_MANAGER_ID=your-user-id"; \
		echo ""; \
		echo "Example:"; \
		echo "  make boat-unpay-all TEAM_MANAGER_ID=717940ae-6051-70cb-9437-fac29614d317"; \
		echo ""; \
		exit 1; \
	fi
	@echo "Team Manager: $(TEAM_MANAGER_ID)"
	@echo "Table: impressionnistes-registration-$(ENV)"
	@echo ""
	@echo "⚠️  WARNING: This will reset ALL paid boats to 'complete' status"
	@echo ""
	@echo "Finding paid boats..."
	@PAID_BOATS=$$(aws dynamodb query \
		--table-name impressionnistes-registration-$(ENV) \
		--key-condition-expression "PK = :pk AND begins_with(SK, :sk)" \
		--filter-expression "registration_status = :status" \
		--expression-attribute-values '{":pk":{"S":"TEAM#$(TEAM_MANAGER_ID)"},":sk":{"S":"BOAT#"},":status":{"S":"paid"}}' \
		--query 'Items[].boat_registration_id.S' \
		--output text); \
	if [ -z "$$PAID_BOATS" ]; then \
		echo "No paid boats found."; \
		exit 0; \
	fi; \
	BOAT_COUNT=$$(echo $$PAID_BOATS | wc -w | tr -d ' '); \
	echo "Found $$BOAT_COUNT paid boat(s):"; \
	echo "$$PAID_BOATS" | tr '\t' '\n' | sed 's/^/  - /'; \
	echo ""; \
	read -p "Reset all $$BOAT_COUNT boat(s) to unpaid? (yes/no): " confirm; \
	if [ "$$confirm" != "yes" ]; then \
		echo "Operation cancelled"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "Resetting boats..."; \
	for BOAT_ID in $$PAID_BOATS; do \
		echo "  Resetting $$BOAT_ID..."; \
		aws dynamodb update-item \
			--table-name impressionnistes-registration-$(ENV) \
			--key "{\"PK\":{\"S\":\"TEAM#$(TEAM_MANAGER_ID)\"},\"SK\":{\"S\":\"BOAT#$$BOAT_ID\"}}" \
			--update-expression "SET registration_status = :status, updated_at = :timestamp REMOVE paid_at, payment_id, stripe_payment_intent_id, locked_pricing" \
			--expression-attribute-values "{\":status\":{\"S\":\"complete\"},\":timestamp\":{\"S\":\"$$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"}}" \
			--output text > /dev/null; \
		echo "    ✓ Done"; \
	done; \
	echo ""; \
	echo "=========================================="; \
	echo "✓ All boats reset successfully!"; \
	echo "=========================================="

# ==========================================
# Testing Commands
# ==========================================

test-setup:
	@echo "=========================================="
	@echo "Setting Up Test Environment"
	@echo "=========================================="
	@echo ""
	@if [ ! -d "../$(TEST_VENV)" ]; then \
		echo "Creating test virtual environment..."; \
		cd .. && python3 -m venv $(TEST_VENV); \
		echo "✓ Virtual environment created"; \
		echo ""; \
	else \
		echo "✓ Virtual environment already exists"; \
		echo ""; \
	fi
	@echo "Installing test dependencies..."
	@cd .. && $(TEST_PIP) install --upgrade pip -q
	@cd .. && $(TEST_PIP) install -r tests/requirements.txt -q
	@echo "✓ Dependencies installed"
	@echo ""
	@echo "=========================================="
	@echo "✓ Test environment ready!"
	@echo ""
	@echo "Run tests with: make test"
	@echo "=========================================="

test-email: test-setup
	@echo "=========================================="
	@echo "Testing Email Notification System"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ -z "$(EMAIL)" ]; then \
		echo "❌ Error: EMAIL parameter required"; \
		echo ""; \
		echo "Usage:"; \
		echo "  make test-email EMAIL=your-email@example.com"; \
		echo "  make test-email EMAIL=your-email@example.com SENDER=custom@aviron-rcpm.fr"; \
		echo "  make test-email EMAIL=your-email@example.com ENV=prod"; \
		echo ""; \
		echo "Parameters:"; \
		echo "  EMAIL  - Recipient email address (required)"; \
		echo "  SENDER - Sender email address (optional, defaults to course.impressionnistes@aviron-rcpm.fr)"; \
		echo "  ENV    - Environment: dev or prod (optional, defaults to dev)"; \
		echo ""; \
		echo "Prerequisites:"; \
		echo "  1. AWS credentials configured (aws configure)"; \
		echo "  2. Sender email verified in SES"; \
		echo "  3. Recipient email verified (if sandbox mode)"; \
		echo ""; \
		echo "To verify emails in SES:"; \
		echo "  make ses-verify-email EMAIL=course.impressionnistes@aviron-rcpm.fr ENV=$(ENV)"; \
		echo "  make ses-verify-email EMAIL=$(EMAIL) ENV=$(ENV)"; \
		echo ""; \
		exit 1; \
	fi
	@echo "Testing email sending to: $(EMAIL)"
	@if [ -n "$(SENDER)" ]; then \
		echo "Using sender: $(SENDER)"; \
	else \
		echo "Using default sender from email_utils.py"; \
	fi
	@echo ""
	@echo "Prerequisites check:"
	@echo "  ✓ AWS credentials configured"
	@echo "  ✓ Sender email should be verified in SES"
	@echo "  ✓ Recipient email should be verified (if sandbox mode)"
	@echo ""
	@echo "Running email tests..."
	@echo ""
	@if [ -n "$(SENDER)" ]; then \
		cd .. && $(TEST_PYTHON) functions/shared/test_email_utils.py $(EMAIL) $(SENDER); \
	else \
		cd .. && $(TEST_PYTHON) functions/shared/test_email_utils.py $(EMAIL); \
	fi
	@echo ""
	@echo "=========================================="
	@echo "✓ Email test complete!"
	@echo ""
	@echo "Check your inbox (and spam folder) for test emails."
	@echo "=========================================="

test-slack: test-setup
	@echo "=========================================="
	@echo "Testing Slack Notification System"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@echo "Prerequisites check:"
	@echo "  ✓ AWS credentials configured"
	@echo "  ✓ Slack webhooks should be configured in DynamoDB"
	@echo ""
	@echo "Running Slack notification tests..."
	@echo ""
	@cd .. && ENVIRONMENT=$(ENV) $(TEST_PYTHON) functions/shared/test_slack_utils.py
	@echo ""
	@echo "=========================================="
	@echo "✓ Slack test complete!"
	@echo ""
	@echo "Check your Slack channel for test notifications."
	@echo "=========================================="

test: test-setup
	@echo "=========================================="
	@echo "Running All Tests"
	@echo "=========================================="
	@echo ""
	@echo "1. Backend Integration Tests"
	@echo "----------------------------"
	@cd .. && $(TEST_PYTEST) tests/ -v
	@echo ""
	@echo "2. Frontend Formatter Tests"
	@echo "----------------------------"
	@cd ../frontend/src/utils/exportFormatters && ./runTests.sh
	@echo ""
	@echo "=========================================="
	@echo "✓ All tests complete!"
	@echo "  - Backend integration tests: PASSED"
	@echo "  - Frontend formatter tests: PASSED"
	@echo "=========================================="

test-backend: test-setup
	@echo "=========================================="
	@echo "Running Backend Integration Tests"
	@echo "=========================================="
	@echo ""
	@cd .. && $(TEST_PYTEST) tests/ -v
	@echo ""
	@echo "=========================================="
	@echo "✓ Backend tests complete!"
	@echo "=========================================="

test-frontend:
	@echo "=========================================="
	@echo "Running Frontend Formatter Tests"
	@echo "=========================================="
	@echo ""
	@cd ../frontend/src/utils/exportFormatters && ./runTests.sh
	@echo ""
	@echo "=========================================="
	@echo "✓ Frontend tests complete!"
	@echo "=========================================="

test-coverage: test-setup
	@echo "=========================================="
	@echo "Running Tests with Coverage"
	@echo "=========================================="
	@echo ""
	@cd .. && $(TEST_PYTEST) tests/ -v --cov=functions --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "=========================================="
	@echo "✓ Tests complete!"
	@echo ""
	@echo "📊 Coverage report: htmlcov/index.html"
	@echo "=========================================="

test-clean:
	@echo "Cleaning test environment..."
	@rm -rf ../$(TEST_VENV)
	@rm -rf ../tests/__pycache__
	@rm -rf ../tests/integration/__pycache__
	@rm -rf ../.pytest_cache
	@rm -rf ../htmlcov
	@rm -rf ../.coverage
	@echo "✓ Test environment cleaned"
