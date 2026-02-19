#!/bin/bash

# Script to create SSL certificates for CloudFront custom domains
# Certificates MUST be created in us-east-1 region for CloudFront

set -e

echo "=========================================="
echo "Creating SSL Certificates for CloudFront"
echo "=========================================="
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Error: AWS CLI is not configured or credentials are invalid"
    exit 1
fi

echo "✓ AWS CLI is configured"
echo ""

# Create certificate for dev domain
echo "1. Creating certificate for DEV domain: impressionnistes-dev.aviron-rcpm.fr"
echo "   Region: us-east-1 (required for CloudFront)"
echo ""

DEV_CERT_ARN=$(aws acm request-certificate \
    --domain-name impressionnistes-dev.aviron-rcpm.fr \
    --validation-method DNS \
    --region us-east-1 \
    --query 'CertificateArn' \
    --output text)

echo "✓ Dev certificate requested"
echo "   ARN: $DEV_CERT_ARN"
echo ""

# Create certificate for prod domain
echo "2. Creating certificate for PROD domain: impressionnistes.aviron-rcpm.fr"
echo "   Region: us-east-1 (required for CloudFront)"
echo ""

PROD_CERT_ARN=$(aws acm request-certificate \
    --domain-name impressionnistes.aviron-rcpm.fr \
    --validation-method DNS \
    --region us-east-1 \
    --query 'CertificateArn' \
    --output text)

echo "✓ Prod certificate requested"
echo "   ARN: $PROD_CERT_ARN"
echo ""

echo "=========================================="
echo "✓ Certificates Created Successfully"
echo "=========================================="
echo ""

# Get validation records for dev
echo "3. Getting DNS validation records for DEV certificate..."
echo ""
aws acm describe-certificate \
    --certificate-arn "$DEV_CERT_ARN" \
    --region us-east-1 \
    --query 'Certificate.DomainValidationOptions[0].ResourceRecord' \
    --output table

echo ""
echo "Add this CNAME record to your DNS for impressionnistes-dev.aviron-rcpm.fr"
echo ""

# Get validation records for prod
echo "4. Getting DNS validation records for PROD certificate..."
echo ""
aws acm describe-certificate \
    --certificate-arn "$PROD_CERT_ARN" \
    --region us-east-1 \
    --query 'Certificate.DomainValidationOptions[0].ResourceRecord' \
    --output table

echo ""
echo "Add this CNAME record to your DNS for impressionnistes.aviron-rcpm.fr"
echo ""

echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Add the DNS validation CNAME records shown above to your DNS"
echo "   (in your domain registrar or Route53)"
echo ""
echo "2. Wait for certificate validation (usually 5-10 minutes)"
echo "   Check status with:"
echo "   aws acm describe-certificate --certificate-arn $DEV_CERT_ARN --region us-east-1"
echo ""
echo "3. Update infrastructure/config.py with the certificate ARNs:"
echo ""
echo "   DEV_CONFIG = {"
echo "       ..."
echo "       \"certificate_arn\": \"$DEV_CERT_ARN\","
echo "   }"
echo ""
echo "   PROD_CONFIG = {"
echo "       ..."
echo "       \"certificate_arn\": \"$PROD_CERT_ARN\","
echo "   }"
echo ""
echo "4. Deploy the stacks:"
echo "   cd infrastructure"
echo "   make deploy-dev"
echo "   make deploy-prod"
echo ""
echo "5. Update your DNS with CNAME records pointing to CloudFront"
echo "   (shown in deployment output)"
echo ""
echo "=========================================="
