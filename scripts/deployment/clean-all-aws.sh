#!/bin/bash
# Complete cleanup script for AWS resources

set -e

ENV=${1:-dev}

echo "=========================================="
echo "AWS Cleanup Script"
echo "Environment: $ENV"
echo "=========================================="
echo ""

STACK_PREFIX="Impressionnistes"
TABLE_NAME="impressionnistes-registration-$ENV"

# Function to delete stack with retries
delete_stack_with_retry() {
    local stack_name=$1
    echo "Deleting stack: $stack_name"
    
    # Check if stack exists
    if ! aws cloudformation describe-stacks --stack-name $stack_name >/dev/null 2>&1; then
        echo "  Stack does not exist, skipping"
        return 0
    fi
    
    # Get stack status
    status=$(aws cloudformation describe-stacks --stack-name $stack_name --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$status" = "DELETE_FAILED" ] || [ "$status" = "UPDATE_ROLLBACK_FAILED" ]; then
        echo "  Stack is in failed state: $status"
        echo "  Attempting to delete with resource retention..."
        
        # Get failed resources
        failed_resources=$(aws cloudformation describe-stack-resources --stack-name $stack_name --query 'StackResources[?ResourceStatus==`DELETE_FAILED`].LogicalResourceId' --output text)
        
        if [ -n "$failed_resources" ]; then
            echo "  Retaining failed resources: $failed_resources"
            aws cloudformation delete-stack --stack-name $stack_name --retain-resources $failed_resources
        else
            aws cloudformation delete-stack --stack-name $stack_name
        fi
    else
        aws cloudformation delete-stack --stack-name $stack_name
    fi
    
    echo "  Waiting for deletion..."
    aws cloudformation wait stack-delete-complete --stack-name $stack_name 2>/dev/null || true
    echo "  ✓ Stack deleted"
}

# Delete application stacks
echo "1. Deleting application stacks..."
delete_stack_with_retry "${STACK_PREFIX}Frontend-$ENV"
delete_stack_with_retry "${STACK_PREFIX}Api-$ENV"
delete_stack_with_retry "${STACK_PREFIX}Monitoring-$ENV"
delete_stack_with_retry "${STACK_PREFIX}Database-$ENV"

# Delete DynamoDB table if it still exists
echo ""
echo "2. Checking for orphaned DynamoDB table..."
if aws dynamodb describe-table --table-name $TABLE_NAME >/dev/null 2>&1; then
    echo "  Found table: $TABLE_NAME"
    read -p "  Delete table? (y/n): " confirm
    if [ "$confirm" = "y" ]; then
        aws dynamodb delete-table --table-name $TABLE_NAME
        echo "  ✓ Table deleted"
    else
        echo "  Table retained"
    fi
else
    echo "  No orphaned table found"
fi

# Clean up Lambda functions
echo ""
echo "3. Checking for orphaned Lambda functions..."
functions=$(aws lambda list-functions --query "Functions[?starts_with(FunctionName, '${STACK_PREFIX}')].FunctionName" --output text)
if [ -n "$functions" ]; then
    echo "  Found functions: $functions"
    for func in $functions; do
        echo "  Deleting: $func"
        aws lambda delete-function --function-name $func 2>/dev/null || true
    done
    echo "  ✓ Functions deleted"
else
    echo "  No orphaned functions found"
fi

# Clean up CloudWatch log groups
echo ""
echo "4. Checking for orphaned CloudWatch log groups..."
log_groups=$(aws logs describe-log-groups --query "logGroups[?starts_with(logGroupName, '/aws/lambda/${STACK_PREFIX}')].logGroupName" --output text)
if [ -n "$log_groups" ]; then
    echo "  Found log groups: $log_groups"
    for lg in $log_groups; do
        echo "  Deleting: $lg"
        aws logs delete-log-group --log-group-name $lg 2>/dev/null || true
    done
    echo "  ✓ Log groups deleted"
else
    echo "  No orphaned log groups found"
fi

echo ""
echo "=========================================="
echo "✓ Cleanup complete!"
echo "=========================================="
echo ""
echo "You can now redeploy with: make deploy"
