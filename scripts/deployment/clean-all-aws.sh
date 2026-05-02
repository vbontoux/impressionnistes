#!/bin/bash
# Complete AWS cleanup for Course des Impressionnistes Registration System
#
# This script performs a full teardown:
#   1. Destroys all CloudFormation stacks (handles stuck/failed stacks)
#   2. Cleans up retained resources (DynamoDB, Cognito, Secrets Manager)
#   3. Removes orphaned resources (Lambda functions, CloudWatch log groups)
#
# Usage: ./clean-all-aws.sh --profile <aws-profile> [--env dev|prod]

set -e

# ==========================================
# Parse arguments
# ==========================================
PROFILE=""
ENV="dev"

while [[ $# -gt 0 ]]; do
    case $1 in
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --env)
            ENV="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 --profile <aws-profile> [--env dev|prod]"
            echo ""
            echo "Complete AWS cleanup: destroys stacks + retained + orphaned resources."
            echo ""
            echo "Required:"
            echo "  --profile <name>   AWS CLI profile to use (no default)"
            echo ""
            echo "Optional:"
            echo "  --env <env>        Environment: dev or prod (default: dev)"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "Example:"
            echo "  $0 --profile my-profile --env dev"
            exit 0
            ;;
        *)
            echo "Error: Unknown argument: $1"
            echo "Run '$0 --help' for usage"
            exit 1
            ;;
    esac
done

# ==========================================
# Validate arguments
# ==========================================
if [ -z "$PROFILE" ]; then
    echo "Error: --profile is required"
    echo "Run '$0 --help' for usage"
    exit 1
fi

if [ "$ENV" != "dev" ] && [ "$ENV" != "prod" ]; then
    echo "Error: --env must be 'dev' or 'prod'"
    exit 1
fi

REGION="eu-west-3"
AWS="aws --profile $PROFILE --region $REGION"
STACK_PREFIX="Impressionnistes"
TABLE_NAME="impressionnistes-registration-$ENV"

echo "=========================================="
echo "Complete AWS Cleanup"
echo "=========================================="
echo "  Profile:     $PROFILE"
echo "  Environment: $ENV"
echo "  Region:      $REGION"
echo "=========================================="
echo ""

# Verify credentials
echo "Verifying AWS credentials..."
if ! $AWS sts get-caller-identity > /dev/null 2>&1; then
    echo "Error: Could not authenticate with profile '$PROFILE'"
    echo "Check your AWS credentials configuration"
    exit 1
fi
ACCOUNT=$($AWS sts get-caller-identity --query Account --output text)
echo "  Account: $ACCOUNT"
echo ""

# Extra confirmation for production
if [ "$ENV" == "prod" ]; then
    echo "⚠️  WARNING: You are about to destroy the PRODUCTION environment!"
    echo "This will delete ALL stacks, data, users, and secrets."
    read -p "Type 'DELETE PRODUCTION' to confirm: " confirmation
    if [ "$confirmation" != "DELETE PRODUCTION" ]; then
        echo "Cleanup cancelled"
        exit 0
    fi
    echo ""
fi

# ==========================================
# Helper: delete CloudFormation stack
# ==========================================
delete_stack() {
    local stack_name=$1
    echo "   Deleting stack: $stack_name"

    # Check if stack exists
    if ! $AWS cloudformation describe-stacks --stack-name "$stack_name" > /dev/null 2>&1; then
        echo "   Not found, skipping"
        return 0
    fi

    # Get stack status
    local status
    status=$($AWS cloudformation describe-stacks --stack-name "$stack_name" \
        --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_FOUND")

    if [ "$status" = "DELETE_FAILED" ] || [ "$status" = "UPDATE_ROLLBACK_FAILED" ]; then
        echo "   Stack is in failed state: $status"
        echo "   Attempting to delete with resource retention..."

        local failed_resources
        failed_resources=$($AWS cloudformation describe-stack-resources --stack-name "$stack_name" \
            --query 'StackResources[?ResourceStatus==`DELETE_FAILED`].LogicalResourceId' --output text)

        if [ -n "$failed_resources" ]; then
            echo "   Retaining failed resources: $failed_resources"
            $AWS cloudformation delete-stack --stack-name "$stack_name" --retain-resources $failed_resources
        else
            $AWS cloudformation delete-stack --stack-name "$stack_name"
        fi
    else
        $AWS cloudformation delete-stack --stack-name "$stack_name"
    fi

    echo "   Waiting for deletion..."
    $AWS cloudformation wait stack-delete-complete --stack-name "$stack_name" 2>/dev/null || true
    echo "   ✓ Done"
}

# ==========================================
# 1. Destroy CloudFormation stacks
# ==========================================
echo "1. Destroying CloudFormation stacks..."
echo ""

# Order matters: dependents first
# Note: Frontend stack has a typo in the actual stack name (ImpressiornistesFrontend)
delete_stack "ImpressiornistesFrontend-$ENV"
delete_stack "${STACK_PREFIX}Api-$ENV"
delete_stack "${STACK_PREFIX}Auth-$ENV"
delete_stack "${STACK_PREFIX}Monitoring-$ENV"
delete_stack "${STACK_PREFIX}Database-$ENV"
delete_stack "${STACK_PREFIX}Secrets-$ENV"
echo ""

# ==========================================
# 2. DynamoDB table (retained by RemovalPolicy)
# ==========================================
echo "2. DynamoDB Table: $TABLE_NAME"
if $AWS dynamodb describe-table --table-name "$TABLE_NAME" > /dev/null 2>&1; then
    ITEM_COUNT=$($AWS dynamodb describe-table --table-name "$TABLE_NAME" \
        --query 'Table.ItemCount' --output text)
    echo "   Found table ($ITEM_COUNT items)"
    read -p "   Delete table? (y/n): " confirm
    if [ "$confirm" = "y" ]; then
        $AWS dynamodb delete-table --table-name "$TABLE_NAME" > /dev/null
        echo "   ✓ Table deletion initiated"
    else
        echo "   Skipped"
    fi
else
    echo "   Not found, skipping"
fi
echo ""

# ==========================================
# 3. Cognito User Pool (retained by RemovalPolicy)
# ==========================================
echo "3. Cognito User Pool: impressionnistes-users-$ENV"
POOL_ID=$($AWS cognito-idp list-user-pools --max-results 60 \
    --query "UserPools[?Name=='impressionnistes-users-$ENV'].Id" \
    --output text 2>/dev/null)

if [ -n "$POOL_ID" ] && [ "$POOL_ID" != "None" ]; then
    USER_COUNT=$($AWS cognito-idp describe-user-pool --user-pool-id "$POOL_ID" \
        --query 'UserPool.EstimatedNumberOfUsers' --output text 2>/dev/null || echo "unknown")
    echo "   Found pool: $POOL_ID ($USER_COUNT users)"

    # Check for Cognito domain (must be deleted before the pool)
    DOMAIN=$($AWS cognito-idp describe-user-pool --user-pool-id "$POOL_ID" \
        --query 'UserPool.Domain' --output text 2>/dev/null)
    if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "None" ]; then
        echo "   Found Cognito domain: $DOMAIN"
    fi

    read -p "   Delete user pool (and domain)? (y/n): " confirm
    if [ "$confirm" = "y" ]; then
        if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "None" ]; then
            echo "   Deleting Cognito domain..."
            $AWS cognito-idp delete-user-pool-domain \
                --user-pool-id "$POOL_ID" \
                --domain "$DOMAIN" 2>/dev/null || true
            echo "   ✓ Domain deleted"
        fi
        $AWS cognito-idp delete-user-pool --user-pool-id "$POOL_ID"
        echo "   ✓ User pool deleted"
    else
        echo "   Skipped"
    fi
else
    echo "   Not found, skipping"
fi
echo ""

# ==========================================
# 4. Secrets Manager (retained by RemovalPolicy)
# ==========================================
echo "4. Secrets Manager Secrets"

SECRETS=(
    "impressionnistes/stripe/api_key"
    "impressionnistes/stripe/webhook_secret"
    "impressionnistes/slack/admin_webhook"
    "impressionnistes/slack/devops_webhook"
)

FOUND_SECRETS=()
for SECRET_NAME in "${SECRETS[@]}"; do
    if $AWS secretsmanager describe-secret --secret-id "$SECRET_NAME" > /dev/null 2>&1; then
        echo "   Found: $SECRET_NAME"
        FOUND_SECRETS+=("$SECRET_NAME")
    fi
done

if [ ${#FOUND_SECRETS[@]} -eq 0 ]; then
    echo "   No secrets found, skipping"
else
    echo ""
    read -p "   Delete all ${#FOUND_SECRETS[@]} secrets? (y/n): " confirm
    if [ "$confirm" = "y" ]; then
        for SECRET_NAME in "${FOUND_SECRETS[@]}"; do
            $AWS secretsmanager delete-secret \
                --secret-id "$SECRET_NAME" \
                --force-delete-without-recovery > /dev/null
            echo "   ✓ Deleted: $SECRET_NAME"
        done
    else
        echo "   Skipped"
    fi
fi
echo ""

# ==========================================
# 5. Orphaned Lambda functions
# ==========================================
echo "5. Orphaned Lambda functions"
FUNCTIONS=$($AWS lambda list-functions \
    --query "Functions[?starts_with(FunctionName, '${STACK_PREFIX}')].FunctionName" \
    --output text 2>/dev/null)

if [ -n "$FUNCTIONS" ]; then
    for func in $FUNCTIONS; do
        echo "   Deleting: $func"
        $AWS lambda delete-function --function-name "$func" 2>/dev/null || true
    done
    echo "   ✓ Done"
else
    echo "   None found, skipping"
fi
echo ""

# ==========================================
# 6. Orphaned CloudWatch log groups
# ==========================================
echo "6. Orphaned CloudWatch log groups"
LOG_GROUPS=$($AWS logs describe-log-groups \
    --query "logGroups[?starts_with(logGroupName, '/aws/lambda/${STACK_PREFIX}')].logGroupName" \
    --output text 2>/dev/null)

if [ -n "$LOG_GROUPS" ]; then
    for lg in $LOG_GROUPS; do
        echo "   Deleting: $lg"
        $AWS logs delete-log-group --log-group-name "$lg" 2>/dev/null || true
    done
    echo "   ✓ Done"
else
    echo "   None found, skipping"
fi
echo ""

# ==========================================
# Summary
# ==========================================
echo "=========================================="
echo "✓ Cleanup complete!"
echo "=========================================="
echo ""
echo "To verify nothing remains:"
echo "  $AWS cloudformation list-stacks --query \"StackSummaries[?contains(StackName, 'Impressionnistes') && StackStatus!='DELETE_COMPLETE'].StackName\""
echo "  $AWS dynamodb list-tables --query 'TableNames[?contains(@, \`impressionnistes\`)]'"
echo "  $AWS cognito-idp list-user-pools --max-results 10 --query 'UserPools[?contains(Name, \`impressionnistes\`)]'"
echo "  $AWS secretsmanager list-secrets --query 'SecretList[?contains(Name, \`impressionnistes\`)]'"
