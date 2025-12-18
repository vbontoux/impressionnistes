#!/bin/bash
# Script to run integration tests with virtual environment

set -e

echo "🧪 Running Integration Tests"
echo "=============================="
echo ""

# Virtual environment path
VENV="tests/venv"

# Check if virtual environment exists
if [ ! -d "$VENV" ]; then
    echo "Creating test virtual environment..."
    python3 -m venv $VENV
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source $VENV/bin/activate

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "Installing test dependencies..."
    pip install --upgrade pip -q
    pip install -r tests/requirements.txt -q
    echo "✓ Dependencies installed"
    echo ""
fi

# Run tests with coverage
echo "Running tests..."
pytest tests/ -v --cov=functions --cov-report=term-missing --cov-report=html

echo ""
echo "✅ Tests complete!"
echo ""
echo "📊 Coverage report generated in htmlcov/index.html"

# Deactivate virtual environment
deactivate
