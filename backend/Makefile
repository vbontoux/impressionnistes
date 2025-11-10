.PHONY: help setup venv install test test-cov lint clean

# Virtual environment paths
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest

help:
	@echo "Course des Impressionnistes - Backend Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Create venv and install dependencies"
	@echo "  make venv           - Create virtual environment only"
	@echo "  make install        - Install dependencies in existing venv"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run tests"
	@echo "  make test-cov       - Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           - Run linters (when implemented)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove venv and cache files"

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

test:
	@echo "Running tests..."
	@. $(VENV)/bin/activate && $(PYTEST)

test-cov:
	@echo "Running tests with coverage..."
	@. $(VENV)/bin/activate && $(PYTEST) --cov=functions --cov=shared --cov-report=html --cov-report=term

lint:
	@echo "Linting code..."
	@echo "TODO: Implement linting"

clean:
	@echo "Cleaning up..."
	@rm -rf $(VENV)
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf .coverage
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleanup complete"
