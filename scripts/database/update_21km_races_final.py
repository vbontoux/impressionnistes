#!/usr/bin/env python3
"""
Migration: Update 21km races to final list of 41 races
Date: 2025-12-07
Description: Replace all 21km races with the final curated list of 41 races
"""
import boto3
import os
import sys
import csv
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def load_final_races_from_csv():
    """Load the final 41 races from CSV file"""
    csv_path = Path(__file__).parent.parent.parent / 'infrastructure' / 'exports' / 'races-21km-final-41.csv'
    
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    races = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            races.append(row)
    
    print(f"✓ Loaded {len(races)} races from CSV")
    return races

def delete_existing_21km_races(table):
    """Delete all existing 21km races"""
    print("\n1. Deleting existing 21km races...")
    
    # Query for all races
    response = table.query(
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={
            ':pk': 'RACE'
        }
    )
    
    items = response.get('Items', [])
    deleted_count = 0
    
    # Filter and delete only 21km races
    for item in items:
        if item.get('event_type') == '21km':
            table.delete_item(
                Key={
                    'PK': item['PK'],
                    'SK': item['SK']
                }
            )
            deleted_count += 1
            print(f"  Deleted: {item.get('name', item['SK'])}")
    
    print(f"✓ Deleted {deleted_count} existing 21km races")
    return deleted_count

def create_new_21km_races(table, races):
    """Create the new 41 races"""
    print("\n2. Creating new 21km races...")
    
    created_count = 0
    for race in races:
        # Prepare the item
        item = {
            'PK': race['PK'],
            'SK': race['SK'],
            'GSI2PK': race['GSI2PK'],
            'GSI2SK': race['GSI2SK'],
            'race_id': race['race_id'],
            'name': race['name'],
            'event_type': race['event_type'],
            'distance': int(race['distance']),
            'boat_type': race['boat_type'],
            'age_category': race['age_category'],
            'gender_category': race['gender_category'],
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Add master_category if present
        if race.get('master_category'):
            item['master_category'] = race['master_category']
        
        # Put item in table
        table.put_item(Item=item)
        created_count += 1
        print(f"  Created: {race['name']} ({race['race_id']})")
    
    print(f"✓ Created {created_count} new 21km races")
    return created_count

def verify_races(table):
    """Verify the final race count"""
    print("\n3. Verifying races...")
    
    # Scan for all races and count by event_type
    response = table.query(
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={
            ':pk': 'RACE'
        }
    )
    
    items = response.get('Items', [])
    
    # Count by event type
    count_21km = sum(1 for item in items if item.get('event_type') == '21km')
    count_42km = sum(1 for item in items if item.get('event_type') == '42km')
    
    print(f"  21km races: {count_21km}")
    print(f"  42km races: {count_42km}")
    print(f"  Total races: {count_21km + count_42km}")
    
    if count_21km == 41:
        print("✓ Race count verified: 41 races for 21km")
    else:
        print(f"✗ Warning: Expected 41 races for 21km, found {count_21km}")
    
    return count_21km == 41

def main():
    """Main migration function"""
    print("=" * 60)
    print("Migration: Update 21km races to final list of 41 races")
    print("=" * 60)
    
    # Get table name from environment
    table_name = os.environ.get('TABLE_NAME')
    if not table_name:
        print("✗ Error: TABLE_NAME environment variable not set")
        sys.exit(1)
    
    print(f"\nTarget table: {table_name}")
    
    # Confirm before proceeding
    response = input("\nThis will DELETE all existing 21km races and replace them. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled")
        sys.exit(0)
    
    try:
        # Initialize DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        
        # Load final races from CSV
        final_races = load_final_races_from_csv()
        
        # Delete existing 21km races
        deleted = delete_existing_21km_races(table)
        
        # Create new 21km races
        created = create_new_21km_races(table, final_races)
        
        # Verify
        verified = verify_races(table)
        
        print("\n" + "=" * 60)
        print("Migration Summary:")
        print(f"  Deleted: {deleted} races")
        print(f"  Created: {created} races")
        print(f"  Verified: {'✓ PASS' if verified else '✗ FAIL'}")
        print("=" * 60)
        
        if verified:
            print("\n✓ Migration completed successfully!")
            sys.exit(0)
        else:
            print("\n✗ Migration completed with warnings")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
