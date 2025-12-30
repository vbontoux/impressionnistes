#!/usr/bin/env python3
"""
Remove Slack webhook URLs from DynamoDB notification config
These should be stored in AWS Secrets Manager, not in the database
"""
import os
import sys
import boto3
from datetime import datetime

def remove_slack_webhooks(table_name):
    """Remove Slack webhook fields from notification config"""
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    try:
        # Get current notification config
        response = table.get_item(
            Key={
                'PK': 'CONFIG',
                'SK': 'NOTIFICATION'
            }
        )
        
        if 'Item' not in response:
            print("⚠️  No notification config found - nothing to clean")
            return True
        
        item = response['Item']
        
        # Check if Slack webhooks exist
        has_admin = 'slack_webhook_admin' in item
        has_devops = 'slack_webhook_devops' in item
        
        if not has_admin and not has_devops:
            print("✓ No Slack webhooks in database - already clean")
            return True
        
        print(f"Found Slack webhooks in database:")
        if has_admin:
            print(f"  - slack_webhook_admin: {item['slack_webhook_admin'][:50]}...")
        if has_devops:
            print(f"  - slack_webhook_devops: {item['slack_webhook_devops'][:50]}...")
        
        # Remove the webhook fields
        if has_admin:
            del item['slack_webhook_admin']
        if has_devops:
            del item['slack_webhook_devops']
        
        # Update timestamp
        item['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        item['updated_by'] = 'migration-cleanup'
        
        # Save back to database
        table.put_item(Item=item)
        
        print("✓ Removed Slack webhooks from database")
        print("  Slack webhooks are now managed in AWS Secrets Manager")
        return True
        
    except Exception as e:
        print(f"❌ Error removing Slack webhooks: {e}")
        return False

def main():
    # Get table name from environment variable (set by Makefile)
    table_name = os.environ.get('TABLE_NAME')
    
    if not table_name:
        print("❌ Error: TABLE_NAME environment variable not set")
        print("This migration should be run via: make db-migrate MIGRATION=remove_slack_webhooks_from_db")
        sys.exit(1)
    
    env = 'prod' if 'prod' in table_name else 'dev'
    
    print("=" * 60)
    print("Remove Slack Webhooks from DynamoDB")
    print("=" * 60)
    print(f"Table: {table_name}")
    print(f"Environment: {env}")
    print("=" * 60)
    print("")
    
    success = remove_slack_webhooks(table_name)
    
    if success:
        print("")
        print("=" * 60)
        print("✓ Cleanup completed successfully")
        print("=" * 60)
        sys.exit(0)
    else:
        print("")
        print("=" * 60)
        print("❌ Cleanup failed")
        print("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    main()
