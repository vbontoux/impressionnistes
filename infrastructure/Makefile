.PHONY: help check-prereqs setup venv install bootstrap synth diff deploy deploy-dev deploy-prod deploy-auth redeploy destroy destroy-dev destroy-prod fix-stuck-stack clean-aws list describe-infra costs db-export db-view cognito-create-admin cognito-list-users cognito-add-to-group clean

# Virtual environment paths
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# CDK should be installed globally
CDK = cdk

# Default environment
ENV ?= dev

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
	@echo "  make deploy-auth    - Deploy only auth stack"
	@echo "  make redeploy       - Quick redeploy (destroy + deploy for dev)"
	@echo ""
	@echo "Management:"
	@echo "  make list           - List all stacks"
	@echo "  make describe-infra - Show API URL and Cognito details for frontend config"
	@echo "  make costs          - Show AWS costs for last month (default: last 30 days)"
	@echo "  make db-export      - Export DynamoDB table to CSV (default: dev)"
	@echo "  make db-view        - View DynamoDB table contents (default: dev)"
	@echo "  make db-migrate     - Run database migration (optional, see functions/migrations/)"
	@echo "  make destroy        - Destroy all stacks (default: dev)"
	@echo "  make destroy-dev    - Destroy dev environment"
	@echo "  make destroy-prod   - Destroy prod environment (with confirmation)"
	@echo ""
	@echo "Cognito User Management:"
	@echo "  make cognito-create-admin EMAIL=user@example.com - Create admin user"
	@echo "  make cognito-list-users                          - List all Cognito users"
	@echo "  make cognito-add-to-group EMAIL=user@example.com GROUP=admins - Add user to group"
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
		echo "VITE_COGNITO_REDIRECT_URI=http://localhost:3000/callback"; \
	else \
		echo "⚠️  Stacks not fully deployed yet"; \
	fi
	@echo "=========================================="
	@echo ""
	@echo "Copy the configuration above to frontend/.env"
	@echo ""

deploy-auth:
	@echo "Deploying Auth stack for $(ENV) environment..."
	@$(CDK) deploy ImpressionnistesAuth-$(ENV) --context env=$(ENV)
	@echo "✓ Auth stack deployed"

build-layer:
	@echo "Building Lambda layer..."
	@cd ../functions && ./build-layer.sh
	@echo "✓ Lambda layer built"

deploy-api: build-layer
	@echo "Deploying API stack for $(ENV) environment..."
	@$(CDK) deploy ImpressionnistesApi-$(ENV) --context env=$(ENV)
	@echo "✓ API stack deployed"

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


db-migrate:
	@echo "=========================================="
	@echo "Running Database Migration"
	@echo "Environment: $(ENV)"
	@echo "=========================================="
	@echo ""
	@if [ -z "$(MIGRATION)" ]; then \
		echo "❌ Error: MIGRATION parameter required"; \
		echo "Usage: make db-migrate MIGRATION=your_migration TEAM_MANAGER_ID=your-id"; \
		echo ""; \
		echo "Available migrations:"; \
		if ls ../functions/migrations/*.py 2>/dev/null | grep -v __pycache__ >/dev/null; then \
			ls -1 ../functions/migrations/*.py 2>/dev/null | grep -v __pycache__ | xargs -n1 basename | sed 's/.py//' | sed 's/^/  - /'; \
		else \
			echo "  (none - see functions/migrations/README.md for template)"; \
		fi; \
		exit 1; \
	fi
	@if [ -z "$(TEAM_MANAGER_ID)" ]; then \
		echo "❌ Error: TEAM_MANAGER_ID parameter required"; \
		echo "Usage: make db-migrate MIGRATION=your_migration TEAM_MANAGER_ID=your-id"; \
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
	@echo "Team Manager ID: $(TEAM_MANAGER_ID)"
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
		export DYNAMODB_TABLE_NAME=impressionnistes-registration-$(ENV) && \
		../../infrastructure/$(VENV)/bin/python $(MIGRATION).py --team-manager-id $(TEAM_MANAGER_ID)
	@echo ""
	@echo "=========================================="
	@echo "✓ Migration complete!"
	@echo "=========================================="
