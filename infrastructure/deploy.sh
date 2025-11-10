#!/bin/bash
# Deployment script for Course des Impressionnistes Registration System
# Usage: ./deploy.sh [dev|prod]

set -e

# Get environment from argument or default to 'dev'
ENV=${1:-dev}

echo "=========================================="
echo "Deploying to environment: $ENV"
echo "=========================================="

# Validate environment
if [ "$ENV" != "dev" ] && [ "$ENV" != "prod" ]; then
    echo "Error: Environment must be 'dev' or 'prod'"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "Error: AWS credentials not configured"
    echo "Please run 'aws configure' or set AWS environment variables"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found"
    echo "Please run '../setup-venv.sh' first"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Bootstrap CDK (only needed once per account/region)
echo "Checking CDK bootstrap status..."
if ! aws cloudformation describe-stacks --stack-name CDKToolkit > /dev/null 2>&1; then
    echo "Bootstrapping CDK..."
    cdk bootstrap --context env=$ENV
fi

# Synthesize CloudFormation templates
echo "Synthesizing CDK stacks..."
cdk synth --context env=$ENV

# Deploy all stacks
echo "Deploying stacks..."
cdk deploy --all --context env=$ENV --require-approval never

echo "=========================================="
echo "Deployment completed successfully!"
echo "=========================================="

# Deactivate virtual environment
deactivate
