#!/bin/bash
# Setup script for Python virtual environments
# Course des Impressionnistes Registration System

set -e

echo "=========================================="
echo "Setting up Python virtual environments"
echo "=========================================="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "Error: Python 3.11+ is required"
    exit 1
fi

# Setup backend virtual environment
echo ""
echo "Setting up backend virtual environment..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Created backend/venv"
else
    echo "✓ backend/venv already exists"
fi

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
echo "✓ Installed backend dependencies"

# Setup infrastructure virtual environment
echo ""
echo "Setting up infrastructure virtual environment..."
cd ../infrastructure
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Created infrastructure/venv"
else
    echo "✓ infrastructure/venv already exists"
fi

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
echo "✓ Installed infrastructure dependencies"

cd ..

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To activate virtual environments:"
echo "  Backend:        cd backend && source venv/bin/activate"
echo "  Infrastructure: cd infrastructure && source venv/bin/activate"
echo ""
echo "To deactivate: deactivate"
echo ""
