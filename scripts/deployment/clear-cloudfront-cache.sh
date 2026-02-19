#!/bin/bash

# Clear CloudFront Cache Script
# This script invalidates the CloudFront distribution cache to force fresh content delivery

set -e

ENV=${1:-dev}

echo "=========================================="
echo "Clearing CloudFront Cache for $ENV"
echo "=========================================="

# Get the CloudFront distribution ID
DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
  --stack-name ImpressiornistesFrontend-$ENV \
  --query 'Stacks[0].Outputs[?OutputKey==`DistributionId`].OutputValue' \
  --output text 2>/dev/null)

if [ -z "$DISTRIBUTION_ID" ] || [ "$DISTRIBUTION_ID" = "None" ]; then
  echo "❌ Could not find CloudFront distribution for $ENV environment"
  echo "Make sure the frontend stack is deployed first"
  exit 1
fi

echo "Distribution ID: $DISTRIBUTION_ID"
echo ""
echo "Creating invalidation for all files (/*) ..."

# Create invalidation
INVALIDATION_ID=$(aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*" \
  --query 'Invalidation.Id' \
  --output text)

echo "✓ Invalidation created: $INVALIDATION_ID"
echo ""
echo "Waiting for invalidation to complete..."
echo "(This usually takes 1-3 minutes)"

# Wait for invalidation to complete
aws cloudfront wait invalidation-completed \
  --distribution-id $DISTRIBUTION_ID \
  --id $INVALIDATION_ID

echo ""
echo "✓ CloudFront cache cleared successfully!"
echo ""
echo "Next steps:"
echo "1. Wait 1-2 minutes for changes to propagate"
echo "2. Hard refresh your browser (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)"
echo "3. If still seeing old content, try incognito/private browsing mode"
echo ""
