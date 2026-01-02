#!/usr/bin/env python3
"""
Delete a team manager account and all related data from DynamoDB and Cognito
Usage: python delete_team_manager.py <email> [--environment dev|prod]
"""
import sys
import boto3
import argparse
from botocore.exceptions import ClientError

def get_user_sub_from_email(cognito_client, user_pool_id, email):
    """Get user sub (user_id) from email address"""
    try:
        response = cognito_client.admin_get_user(
            UserPoolId=user_pool_id,
            Username=email
        )
        # Extract sub from user attributes
        for attr in response['UserAttributes']:
            if attr['Name'] == 'sub':
                return attr['Value']
        return None
    except ClientError as e:
        if e.response['Error']['Code'] == 'UserNotFoundException':
            return None
        raise

def delete_dynamodb_data(table, user_sub):
    """Delete all DynamoDB data for a user"""
    deleted_count = 0
    
    # Query all items with PK = USER#{user_sub}
    print(f"  Querying USER#{user_sub} items...")
    response = table.query(
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={':pk': f'USER#{user_sub}'}
    )
    
    items = response.get('Items', [])
    print(f"  Found {len(items)} USER items")
    
    for item in items:
        table.delete_item(Key={'PK': item['PK'], 'SK': item['SK']})
        deleted_count += 1
        print(f"    Deleted: {item['SK']}")
    
    # Query all items with PK = TEAM#{user_sub}
    print(f"  Querying TEAM#{user_sub} items...")
    response = table.query(
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={':pk': f'TEAM#{user_sub}'}
    )
    
    items = response.get('Items', [])
    print(f"  Found {len(items)} TEAM items")
    
    for item in items:
        table.delete_item(Key={'PK': item['PK'], 'SK': item['SK']})
        deleted_count += 1
        print(f"    Deleted: {item['SK']}")
    
    return deleted_count

def delete_cognito_user(cognito_client, user_pool_id, email):
    """Delete user from Cognito"""
    try:
        cognito_client.admin_delete_user(
            UserPoolId=user_pool_id,
            Username=email
        )
        print(f"  ✓ Deleted Cognito user: {email}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'UserNotFoundException':
            print(f"  ⚠ User not found in Cognito: {email}")
            return False
        raise

def main():
    parser = argparse.ArgumentParser(
        description='Delete a team manager account and all related data'
    )
    parser.add_argument('email', help='Email address of the team manager to delete')
    parser.add_argument(
        '--environment',
        choices=['dev', 'prod'],
        default='dev',
        help='Environment (dev or prod, default: dev)'
    )
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    args = parser.parse_args()
    
    email = args.email.lower().strip()
    env = args.environment
    
    # Get AWS resources
    table_name = f'impressionnistes-registration-{env}'
    stack_name = f'ImpressionnistesAuth-{env}'
    
    print(f"\n{'='*60}")
    print(f"Delete Team Manager Account")
    print(f"{'='*60}")
    print(f"Email: {email}")
    print(f"Environment: {env}")
    print(f"Table: {table_name}")
    print(f"Stack: {stack_name}")
    print(f"{'='*60}\n")
    
    # Confirm deletion
    if not args.yes:
        confirm = input(f"⚠️  Are you sure you want to delete {email} and ALL related data? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            sys.exit(0)
    
    try:
        # Initialize AWS clients
        print("Initializing AWS clients...")
        cfn = boto3.client('cloudformation', region_name='eu-west-3')
        cognito = boto3.client('cognito-idp', region_name='eu-west-3')
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')
        
        # Get User Pool ID from CloudFormation
        print("Getting User Pool ID from CloudFormation...")
        try:
            response = cfn.describe_stacks(StackName=stack_name)
            stacks = response.get('Stacks', [])
            if not stacks:
                raise Exception(f"Stack {stack_name} not found")
            
            outputs = stacks[0].get('Outputs', [])
            user_pool_id = None
            for output in outputs:
                if output['OutputKey'] == 'UserPoolId':
                    user_pool_id = output['OutputValue']
                    break
            
            if not user_pool_id:
                raise Exception("UserPoolId output not found in stack")
            
            print(f"  User Pool ID: {user_pool_id}")
        except ClientError as e:
            print(f"❌ Error getting User Pool ID from CloudFormation: {e}")
            print(f"   Make sure the {env} environment is deployed")
            print(f"   Stack name: {stack_name}")
            sys.exit(1)
        
        # Get user_sub from Cognito
        print(f"\nLooking up user in Cognito...")
        user_sub = get_user_sub_from_email(cognito, user_pool_id, email)
        
        if not user_sub:
            print(f"❌ User not found in Cognito: {email}")
            print("   Checking DynamoDB anyway...")
        else:
            print(f"  Found user_sub: {user_sub}")
        
        # Delete from DynamoDB
        if user_sub:
            print(f"\nDeleting DynamoDB data...")
            table = dynamodb.Table(table_name)
            deleted_count = delete_dynamodb_data(table, user_sub)
            print(f"  ✓ Deleted {deleted_count} DynamoDB items")
        else:
            print(f"\n⚠ Skipping DynamoDB deletion (no user_sub found)")
        
        # Delete from Cognito
        print(f"\nDeleting Cognito user...")
        delete_cognito_user(cognito, user_pool_id, email)
        
        print(f"\n{'='*60}")
        print(f"✅ Successfully deleted team manager: {email}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
