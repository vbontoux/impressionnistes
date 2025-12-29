"""
Migration: Update boat interval from 30 to 60 seconds
Updates the semi_marathon_interval_seconds in RACE_TIMING configuration
"""
import boto3
import os
from datetime import datetime

def update_boat_interval():
    """
    Update the boat interval configuration from 30 to 60 seconds
    Uses environment variables set by Makefile
    """
    # Get configuration from environment variables
    table_name = os.environ.get('TABLE_NAME')
    region = os.environ.get('AWS_REGION', 'eu-west-3')
    
    if not table_name:
        print("❌ Error: TABLE_NAME environment variable not set")
        return False
    
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    
    print(f"Updating boat interval in table: {table_name}")
    print(f"Region: {region}")
    print()
    
    # Get current configuration
    try:
        response = table.get_item(
            Key={
                'PK': 'CONFIG',
                'SK': 'RACE_TIMING'
            }
        )
        
        if 'Item' not in response:
            print("❌ RACE_TIMING configuration not found!")
            return False
        
        current_config = response['Item']
        current_interval = current_config.get('semi_marathon_interval_seconds', 'NOT SET')
        
        print(f"Current boat interval: {current_interval} seconds")
        
        if current_interval == 60:
            print("✅ Boat interval is already set to 60 seconds. No update needed.")
            return True
        
        # Update the configuration
        print(f"Updating boat interval from {current_interval} to 60 seconds...")
        
        table.update_item(
            Key={
                'PK': 'CONFIG',
                'SK': 'RACE_TIMING'
            },
            UpdateExpression='SET semi_marathon_interval_seconds = :interval, updated_at = :updated_at, updated_by = :updated_by',
            ExpressionAttributeValues={
                ':interval': 60,
                ':updated_at': datetime.utcnow().isoformat() + 'Z',
                ':updated_by': 'migration:update_boat_interval'
            }
        )
        
        print("✅ Boat interval updated successfully!")
        
        # Verify the update
        response = table.get_item(
            Key={
                'PK': 'CONFIG',
                'SK': 'RACE_TIMING'
            }
        )
        
        new_interval = response['Item'].get('semi_marathon_interval_seconds')
        print(f"Verified new boat interval: {new_interval} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating boat interval: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main migration function"""
    print("=" * 60)
    print("Migration: Update Boat Interval to 60 seconds")
    print("=" * 60)
    print()
    
    success = update_boat_interval()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
