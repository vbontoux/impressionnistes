#!/usr/bin/env python3
"""
Update notification configuration in DynamoDB with Slack webhook URLs from secrets file
This is a one-time migration to add Slack webhooks to existing databases
"""
import sys
import json
import boto3
from datetime import datetime
from pathlib import Path

def load_secrets(env):
    """Load secrets from JSON file"""
    secrets_file = Path(__file__).parent.parent.parent / 'infrastructure' / f'secrets.{env}.json'
    
    if not secrets_file.exists():
        # Try secrets.json as fallback
        secrets_file = Path(__file__).parent.parent.parent / 'infrastructure' / 'secrets.json'
    
    if not secrets_file.exists():
        print(f"❌ Secrets file not found: {secrets_file}")
        return {}
    
    with open(secrets_file, 'r') as f:
        return json.load(f)

def update_notification_config(table_name, region, env):
    """Update notification configuration with Slack webhooks"""
    
    # Load secrets
    secrets = load_secrets(env)
    slack_webhook_admin = secrets.get('slack_webhook_admin', '')
    slack_webhook_devops = secrets.get('slack_webhook_devops', '')
    
    if not slack_webhook_admin and not slack_webhook_devops:
        print("⚠️  No Slack webhooks found in secrets file")
        print(f"   Checked: infrastructure/secrets.{env}.json")
        return False
    
    print(f"Slack webhook admin: {slack_webhook_admin[:50]}..." if slack_webhook_admin else "Slack webhook admin: NOT SET")
    print(f"Slack webhook devops: {slack_webhook_devops[:50]}..." if slack_webhook_devops else "Slack webhook devops: NOT SET")
    
    # Connect to DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    
    # Get current notification config
    try:
        response = table.get_item(
            Key={
                'PK': 'CONFIG',
                'SK': 'NOTIFICATION'
            }
        )
        
        if 'Item' in response:
            # Update existing config
            item = response['Item']
            item['slack_webhook_admin'] = slack_webhook_admin
            item['slack_webhook_devops'] = slack_webhook_devops
            item['updated_at'] = datetime.utcnow().isoformat() + 'Z'
            item['updated_by'] = 'migration'
            
            table.put_item(Item=item)
            print("✓ Updated existing notification configuration")
        else:
            # Create new config
            item = {
                'PK': 'CONFIG',
                'SK': 'NOTIFICATION',
                'notification_frequency_days': 7,
                'session_timeout_minutes': 30,
                'notification_channels': ['email', 'in_app', 'slack'],
                'email_from': 'impressionnistes@aviron-rcpm.fr',
                'slack_webhook_admin': slack_webhook_admin,
                'slack_webhook_devops': slack_webhook_devops,
                'created_at': datetime.utcnow().isoformat() + 'Z',
                'updated_at': datetime.utcnow().isoformat() + 'Z',
                'updated_by': 'migration'
            }
            
            table.put_item(Item=item)
            print("✓ Created new notification configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating notification config: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) != 3:
        print("Usage: python update_notification_config.py <region> <table_name>")
        print("")
        print("Examples:")
        print("  python update_notification_config.py eu-west-3 impressionnistes-registration-dev")
        print("  python update_notification_config.py eu-west-3 impressionnistes-registration-prod")
        sys.exit(1)
    
    region = sys.argv[1]
    table_name = sys.argv[2]
    
    # Determine environment from table name
    env = 'prod' if 'prod' in table_name else 'dev'
    
    print("=" * 60)
    print("Update Notification Configuration")
    print("=" * 60)
    print(f"Region: {region}")
    print(f"Table: {table_name}")
    print(f"Environment: {env}")
    print("=" * 60)
    print("")
    
    success = update_notification_config(table_name, region, env)
    
    if success:
        print("")
        print("=" * 60)
        print("✓ Migration completed successfully")
        print("=" * 60)
        print("")
        print("Next steps:")
        print("  1. Test Slack notifications:")
        print(f"     make test-slack ENV={env}")
        print("")
        print("  2. If you made a payment, check CloudWatch logs:")
        print(f"     aws logs tail /aws/lambda/ImpressionnistesApiStack-{env.capitalize()}-ConfirmPaymentWebhookFunction --follow")
        sys.exit(0)
    else:
        print("")
        print("=" * 60)
        print("❌ Migration failed")
        print("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    main()
