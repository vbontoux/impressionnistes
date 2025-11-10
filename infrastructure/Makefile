.PHONY: help setup venv install synth diff deploy deploy-dev deploy-prod destroy destroy-dev destroy-prod clean test

# Default environment
ENV ?= dev

# Virtual environment paths
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
CDK = cdk

help:
	@echo "Course des Impressionnistes - Infrastructure Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Create venv and install dependencies"
	@echo "  make venv           - Create virtual environment only"
	@echo "  make install        - Install dependencies in existing venv"
	@echo ""
	@echo "Development:"
	@echo "  make synth          - Synthesize CloudFormation templates"
	@echo "  make diff           - Show deployment differences"
	@echo "  make deploy         - Deploy to default environment (dev)"
	@echo "  make deploy-dev     - Deploy to development"
	@echo "  make deploy-prod    - Deploy to production"
	@echo ""
	@echo "Cleanup:"
	@echo "  make destroy        - Destroy default environment (dev)"
	@echo "  make destroy-dev    - Destroy development"
	@echo "  make destroy-prod   - Destroy production"
	@echo "  make clean          - Remove venv and cdk.out"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Test CDK synthesis"
	@echo ""
	@echo "Environment variable:"
	@echo "  ENV=dev|prod        - Set target environment (default: dev)"

setup: venv install
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

synth:
	@echo "Synthesizing CDK stacks for $(ENV)..."
	@. $(VENV)/bin/activate && $(CDK) synth --context env=$(ENV)

diff:
	@echo "Showing differences for $(ENV)..."
	@. $(VENV)/bin/activate && $(CDK) diff --context env=$(ENV)

deploy:
	@echo "Deploying to $(ENV)..."
	@. $(VENV)/bin/activate && $(CDK) deploy --all --context env=$(ENV)

deploy-dev:
	@$(MAKE) deploy ENV=dev

deploy-prod:
	@$(MAKE) deploy ENV=prod

destroy:
	@echo "Destroying $(ENV)..."
	@. $(VENV)/bin/activate && $(CDK) destroy --all --context env=$(ENV) --force

destroy-dev:
	@$(MAKE) destroy ENV=dev

destroy-prod:
	@echo "WARNING: Destroying PRODUCTION environment!"
	@read -p "Type 'DELETE PRODUCTION' to confirm: " confirm && [ "$$confirm" = "DELETE PRODUCTION" ]
	@$(MAKE) destroy ENV=prod

clean:
	@echo "Cleaning up..."
	@rm -rf $(VENV)
	@rm -rf cdk.out
	@rm -rf .pytest_cache
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleanup complete"

test:
	@echo "Testing CDK synthesis..."
	@. $(VENV)/bin/activate && $(PYTHON) test_synth.py
