#!/bin/bash
# Destroy script for Course des Impressionnistes Registration System
# Usage: ./destroy.sh [dev|prod]

set -e

# Get environment from argument or default to 'dev'
ENV=${1:-dev}

echo "=========================================="
echo "WARNING: Destroying environment: $ENV"
echo "=========================================="

# Validate environment
if [ "$ENV" != "dev" ] && [ "$ENV" != "prod" ]; then
    echo "Error: Environment must be 'dev' or 'prod'"
    exit 1
fi

# Extra confirmation for production
if [ "$ENV" == "prod" ]; then
    echo "You are about to destroy the PRODUCTION environment!"
    read -p "Type 'DELETE PRODUCTION' to confirm: " confirmation
    if [ "$confirmation" != "DELETE PRODUCTION" ]; then
        echo "Destruction cancelled"
        exit 0
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found"
    echo "Please run '../setup-venv.sh' first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Destroy all stacks
echo "Destroying stacks..."
cdk destroy --all --context env=$ENV --force

echo "=========================================="
echo "Environment destroyed"
echo "=========================================="

# Deactivate virtual environment
deactivate
