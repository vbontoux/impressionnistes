#!/usr/bin/env python3
"""
Migration Script: Delete All Data Except Team Managers

⚠️  DESTRUCTIVE OPERATION ⚠️

This migration deletes ALL data from the database EXCEPT:
- Team manager user accounts (USER# records)
- System configuration (CONFIG# records)
- Race definitions (RACE# records)
- Club definitions (CLUB# records)

This will DELETE:
- All boat registrations (TEAM#xxx#BOAT# records)
- All crew members (TEAM#xxx#CREW_MEMBER# records)
- All payments (TEAM#xxx#PAYMENT# records)
- All temporary access grants (TEMP_ACCESS# records)
- All audit logs (AUDIT# records)

Team managers will remain in:
- DynamoDB (can still log in)
- Cognito (authentication still works)

Use case: Reset production after smoke testing, keeping team manager accounts intact.

Run with:
    cd infrastructure && make delete-all-data-keep-managers ENV=prod
"""
import os
import sys
import boto3
from datetime import datetime
from decimal import Decimal

def run_migration(table_name):
    """
    Delete all data except team managers and system configuration
    
    Args:
        table_name: DynamoDB table name
    
    Returns:
        True if migration succeeded, False otherwise
    """
    # Use AWS profile from environment variable if set, otherwise use default
    profile_name = os.environ.get('AWS_PROFILE', 'default')
    session = boto3.Session(profile_name=profile_name)
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    print("=" * 60)
    print("⚠️  DESTRUCTIVE OPERATION - DELETE ALL DATA EXCEPT TEAM MANAGERS")
    print("=" * 60)
    print()
    print(f"Table: {table_name}")
    print(f"AWS Profile: {profile_name}")
    print()
    print("This will DELETE:")
    print("  ✗ All boat registrations")
    print("  ✗ All crew members")
    print("  ✗ All payments")
    print("  ✗ All temporary access grants")
    print("  ✗ All audit logs")
    print()
    print("This will KEEP:")
    print("  ✓ Team manager accounts (USER# records)")
    print("  ✓ System configuration (CONFIG# records)")
    print("  ✓ Race definitions (RACE# records)")
    print("  ✓ Club definitions (CLUB# records)")
    print()
    
    # Scan database to find items to delete
    print("Scanning database...")
    try:
        response = table.scan()
        items = response.get('Items', [])
        
        # Continue scanning if there are more items
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        print(f"Found {len(items)} total items in database")
        print()
        
    except Exception as e:
        print(f"❌ Error scanning database: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Categorize items
    items_to_keep = []
    items_to_delete = []
    
    for item in items:
        pk = item.get('PK', '')
        sk = item.get('SK', '')
        
        # Keep: USER records (team managers)
        if pk.startswith('USER#'):
            items_to_keep.append(('Team Manager', pk, sk))
            continue
        
        # Keep: CONFIG records (system configuration)
        if pk == 'CONFIG':
            items_to_keep.append(('Configuration', pk, sk))
            continue
        
        # Keep: RACE records (race definitions) - PK is exactly 'RACE', not 'RACE#'
        if pk == 'RACE':
            items_to_keep.append(('Race', pk, sk))
            continue
        
        # Keep: CLUB records (club definitions) - PK is exactly 'CLUB', not 'CLUB#'
        if pk == 'CLUB':
            items_to_keep.append(('Club', pk, sk))
            continue
        
        # Delete everything else
        item_type = 'Unknown'
        if pk.startswith('TEAM#') and 'BOAT#' in sk:
            item_type = 'Boat Registration'
        elif pk.startswith('TEAM#') and 'CREW_MEMBER#' in sk:
            item_type = 'Crew Member'
        elif pk.startswith('TEAM#') and 'PAYMENT#' in sk:
            item_type = 'Payment'
        elif pk.startswith('TEMP_ACCESS#'):
            item_type = 'Temporary Access'
        elif pk.startswith('AUDIT#'):
            item_type = 'Audit Log'
        
        items_to_delete.append((item_type, pk, sk))
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print(f"Items to KEEP: {len(items_to_keep)}")
    for item_type, pk, sk in items_to_keep[:5]:  # Show first 5
        print(f"  ✓ {item_type}: {pk} / {sk}")
    if len(items_to_keep) > 5:
        print(f"  ... and {len(items_to_keep) - 5} more")
    print()
    
    print(f"Items to DELETE: {len(items_to_delete)}")
    
    # Count by type
    delete_counts = {}
    for item_type, pk, sk in items_to_delete:
        delete_counts[item_type] = delete_counts.get(item_type, 0) + 1
    
    for item_type, count in sorted(delete_counts.items()):
        print(f"  ✗ {item_type}: {count}")
    print()
    
    if len(items_to_delete) == 0:
        print("✓ No items to delete. Database is already clean.")
        return True
    
    # Confirm deletion
    print("=" * 60)
    print("⚠️  FINAL CONFIRMATION")
    print("=" * 60)
    print()
    print(f"About to DELETE {len(items_to_delete)} items from {table_name}")
    print()
    
    # Delete items
    print("Deleting items...")
    deleted_count = 0
    failed_count = 0
    
    for item_type, pk, sk in items_to_delete:
        try:
            table.delete_item(Key={'PK': pk, 'SK': sk})
            deleted_count += 1
            
            # Progress indicator
            if deleted_count % 10 == 0:
                print(f"  Deleted {deleted_count}/{len(items_to_delete)} items...")
        
        except Exception as e:
            print(f"  ❌ Failed to delete {pk} / {sk}: {e}")
            failed_count += 1
    
    print()
    print("=" * 60)
    print("DELETION COMPLETE")
    print("=" * 60)
    print()
    print(f"✓ Successfully deleted: {deleted_count} items")
    if failed_count > 0:
        print(f"❌ Failed to delete: {failed_count} items")
    print()
    print(f"✓ Kept {len(items_to_keep)} items (team managers, config, races, clubs)")
    print()
    
    # Reset boat number counter
    print("Resetting boat number counter...")
    try:
        config_response = table.get_item(Key={'PK': 'CONFIG', 'SK': 'SYSTEM'})
        if 'Item' in config_response:
            config = config_response['Item']
            config['boat_number_counter'] = 0
            config['updated_at'] = datetime.utcnow().isoformat() + 'Z'
            config['updated_by'] = 'migration:delete_all_data_keep_team_managers'
            table.put_item(Item=config)
            print("✓ Boat number counter reset to 0")
        else:
            print("⚠️  CONFIG#SYSTEM not found, skipping counter reset")
    except Exception as e:
        print(f"⚠️  Failed to reset boat number counter: {e}")
    
    print()
    print("=" * 60)
    print("✓ Migration complete!")
    print("=" * 60)
    print()
    print("Team managers can still log in and create new boats/crew members.")
    print()
    
    return failed_count == 0


if __name__ == '__main__':
    # Get table name from environment
    table_name = os.environ.get('TABLE_NAME')
    
    if not table_name:
        print("❌ Error: TABLE_NAME environment variable not set")
        print()
        print("Run this migration using:")
        print("  cd infrastructure && make delete-all-data-keep-managers ENV=prod")
        sys.exit(1)
    
    print()
    success = run_migration(table_name)
    print()
    
    sys.exit(0 if success else 1)
