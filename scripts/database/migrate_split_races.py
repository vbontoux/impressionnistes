"""
Migration: Split SWEEP OR SCULL races into separate SWEEP and SCULL races

This migration:
1. Deletes 20 old races that have "OR QUAD" or "OR SCULL" in their names
2. Creates 40 new races (20 SWEEP + 20 SCULL)
3. Updates any boat registrations that reference the old races

Run with: make db-migrate MIGRATION=migrate_split_races TEAM_MANAGER_ID=your-user-id
"""

import boto3
import os
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')


# Old races to delete (20 races with "OR QUAD/SCULL")
OLD_RACES_TO_DELETE = [
    'SM01', 'SM02', 'SM03',  # J16 coxed four or quad
    'SM06', 'SM07', 'SM08',  # J18 four or quad without cox
    'SM12', 'SM13',          # Senior four or quad without cox
    'SM17', 'SM18', 'SM19',  # Master coxed four or quad yolette
    'SM20', 'SM21', 'SM22',  # Master coxed four or quad
    'SM23', 'SM24', 'SM25',  # Master four or quad without cox
    'SM26', 'SM27', 'SM28',  # Master eight or octuple with cox
]


# New races to create (40 races: 20 SWEEP + 20 SCULL)
NEW_RACES = [
    # J16 Category - Split from SM01, SM02, SM03
    {'race_id': 'SM01A', 'name': 'WOMEN-JUNIOR J16-COXED SWEEP FOUR', 'boat_type': '4+', 'age_category': 'j16', 'gender_category': 'women'},
    {'race_id': 'SM01B', 'name': 'WOMEN-JUNIOR J16-COXED QUAD SCULL', 'boat_type': '4x+', 'age_category': 'j16', 'gender_category': 'women'},
    {'race_id': 'SM02A', 'name': 'MEN-JUNIOR J16-COXED SWEEP FOUR', 'boat_type': '4+', 'age_category': 'j16', 'gender_category': 'men'},
    {'race_id': 'SM02B', 'name': 'MEN-JUNIOR J16-COXED QUAD SCULL', 'boat_type': '4x+', 'age_category': 'j16', 'gender_category': 'men'},
    {'race_id': 'SM03A', 'name': 'MIXED-GENDER-JUNIOR J16-COXED SWEEP FOUR', 'boat_type': '4+', 'age_category': 'j16', 'gender_category': 'mixed'},
    {'race_id': 'SM03B', 'name': 'MIXED-GENDER-JUNIOR J16-COXED QUAD SCULL', 'boat_type': '4x+', 'age_category': 'j16', 'gender_category': 'mixed'},
    
    # J18 Category - Split from SM06, SM07, SM08
    {'race_id': 'SM06A', 'name': 'WOMEN-JUNIOR J18-SWEEP FOUR WITHOUT COXSWAIN', 'boat_type': '4-', 'age_category': 'j18', 'gender_category': 'women'},
    {'race_id': 'SM06B', 'name': 'WOMEN-JUNIOR J18-QUAD SCULL WITHOUT COXSWAIN', 'boat_type': '4x-', 'age_category': 'j18', 'gender_category': 'women'},
    {'race_id': 'SM07A', 'name': 'MEN-JUNIOR J18-SWEEP FOUR WITHOUT COXSWAIN', 'boat_type': '4-', 'age_category': 'j18', 'gender_category': 'men'},
    {'race_id': 'SM07B', 'name': 'MEN-JUNIOR J18-QUAD SCULL WITHOUT COXSWAIN', 'boat_type': '4x-', 'age_category': 'j18', 'gender_category': 'men'},
    {'race_id': 'SM08A', 'name': 'MIXED-GENDER-JUNIOR J18-SWEEP FOUR WITHOUT COXSWAIN', 'boat_type': '4-', 'age_category': 'j18', 'gender_category': 'mixed'},
    {'race_id': 'SM08B', 'name': 'MIXED-GENDER-JUNIOR J18-QUAD SCULL WITHOUT COXSWAIN', 'boat_type': '4x-', 'age_category': 'j18', 'gender_category': 'mixed'},
    
    # Senior Category - Split from SM12, SM13
    {'race_id': 'SM12A', 'name': 'WOMEN-SENIOR-SWEEP FOUR WITHOUT COXSWAIN', 'boat_type': '4-', 'age_category': 'senior', 'gender_category': 'women'},
    {'race_id': 'SM12B', 'name': 'WOMEN-SENIOR-QUAD SCULL WITHOUT COXSWAIN', 'boat_type': '4x-', 'age_category': 'senior', 'gender_category': 'women'},
    {'race_id': 'SM13A', 'name': 'MEN-SENIOR-SWEEP FOUR WITHOUT COXSWAIN', 'boat_type': '4-', 'age_category': 'senior', 'gender_category': 'men'},
    {'race_id': 'SM13B', 'name': 'MEN-SENIOR-QUAD SCULL WITHOUT COXSWAIN', 'boat_type': '4x-', 'age_category': 'senior', 'gender_category': 'men'},
    
    # Master Category - Split from SM17, SM18, SM19 (Yolette)
    {'race_id': 'SM17A', 'name': 'WOMEN-MASTER-COXED SWEEP FOUR YOLETTE', 'boat_type': '4+', 'age_category': 'master', 'gender_category': 'women'},
    {'race_id': 'SM17B', 'name': 'WOMEN-MASTER-COXED QUAD SCULL YOLETTE', 'boat_type': '4x+', 'age_category': 'master', 'gender_category': 'women'},
    {'race_id': 'SM18A', 'name': 'MEN-MASTER-COXED SWEEP FOUR YOLETTE', 'boat_type': '4+', 'age_category': 'master', 'gender_category': 'men'},
    {'race_id': 'SM18B', 'name': 'MEN-MASTER-COXED QUAD SCULL YOLETTE', 'boat_type': '4x+', 'age_category': 'master', 'gender_category': 'men'},
    {'race_id': 'SM19A', 'name': 'MIXED-GENDER-MASTER-COXED SWEEP FOUR YOLETTE', 'boat_type': '4+', 'age_category': 'master', 'gender_category': 'mixed'},
    {'race_id': 'SM19B', 'name': 'MIXED-GENDER-MASTER-COXED QUAD SCULL YOLETTE', 'boat_type': '4x+', 'age_category': 'master', 'gender_category': 'mixed'},
    
    # Master Category - Split from SM20, SM21, SM22
    {'race_id': 'SM20A', 'name': 'WOMEN-MASTER-COXED SWEEP FOUR', 'boat_type': '4+', 'age_category': 'master', 'gender_category': 'women'},
    {'race_id': 'SM20B', 'name': 'WOMEN-MASTER-COXED QUAD SCULL', 'boat_type': '4x+', 'age_category': 'master', 'gender_category': 'women'},
    {'race_id': 'SM21A', 'name': 'MEN-MASTER-COXED SWEEP FOUR', 'boat_type': '4+', 'age_category': 'master', 'gender_category': 'men'},
    {'race_id': 'SM21B', 'name': 'MEN-MASTER-COXED QUAD SCULL', 'boat_type': '4x+', 'age_category': 'master', 'gender_category': 'men'},
    {'race_id': 'SM22A', 'name': 'MIXED-GENDER-MASTER-COXED SWEEP FOUR', 'boat_type': '4+', 'age_category': 'master', 'gender_category': 'mixed'},
    {'race_id': 'SM22B', 'name': 'MIXED-GENDER-MASTER-COXED QUAD SCULL', 'boat_type': '4x+', 'age_category': 'master', 'gender_category': 'mixed'},
    
    # Master Category - Split from SM23, SM24, SM25
    {'race_id': 'SM23A', 'name': 'WOMEN-MASTER-SWEEP FOUR WITHOUT COXSWAIN', 'boat_type': '4-', 'age_category': 'master', 'gender_category': 'women'},
    {'race_id': 'SM23B', 'name': 'WOMEN-MASTER-QUAD SCULL WITHOUT COXSWAIN', 'boat_type': '4x-', 'age_category': 'master', 'gender_category': 'women'},
    {'race_id': 'SM24A', 'name': 'MEN-MASTER-SWEEP FOUR WITHOUT COXSWAIN', 'boat_type': '4-', 'age_category': 'master', 'gender_category': 'men'},
    {'race_id': 'SM24B', 'name': 'MEN-MASTER-QUAD SCULL WITHOUT COXSWAIN', 'boat_type': '4x-', 'age_category': 'master', 'gender_category': 'men'},
    {'race_id': 'SM25A', 'name': 'MIXED-GENDER-MASTER-SWEEP FOUR WITHOUT COXSWAIN', 'boat_type': '4-', 'age_category': 'master', 'gender_category': 'mixed'},
    {'race_id': 'SM25B', 'name': 'MIXED-GENDER-MASTER-QUAD SCULL WITHOUT COXSWAIN', 'boat_type': '4x-', 'age_category': 'master', 'gender_category': 'mixed'},
    
    # Master Category - Split from SM26, SM27, SM28 (Eight or Octuple)
    {'race_id': 'SM26A', 'name': 'WOMEN-MASTER-SWEEP EIGHT WITH COXSWAIN', 'boat_type': '8+', 'age_category': 'master', 'gender_category': 'women'},
    {'race_id': 'SM26B', 'name': 'WOMEN-MASTER-OCTUPLE SCULL WITH COXSWAIN', 'boat_type': '8x+', 'age_category': 'master', 'gender_category': 'women'},
    {'race_id': 'SM27A', 'name': 'MEN-MASTER-SWEEP EIGHT WITH COXSWAIN', 'boat_type': '8+', 'age_category': 'master', 'gender_category': 'men'},
    {'race_id': 'SM27B', 'name': 'MEN-MASTER-OCTUPLE SCULL WITH COXSWAIN', 'boat_type': '8x+', 'age_category': 'master', 'gender_category': 'men'},
    {'race_id': 'SM28A', 'name': 'MIXED-GENDER-MASTER-SWEEP EIGHT WITH COXSWAIN', 'boat_type': '8+', 'age_category': 'master', 'gender_category': 'mixed'},
    {'race_id': 'SM28B', 'name': 'MIXED-GENDER-MASTER-OCTUPLE SCULL WITH COXSWAIN', 'boat_type': '8x+', 'age_category': 'master', 'gender_category': 'mixed'},
]


def migrate(table_name, team_manager_id=None):
    """
    Execute the migration
    
    Args:
        table_name: DynamoDB table name
        team_manager_id: User ID of the team manager running the migration (optional, for audit)
    """
    table = dynamodb.Table(table_name)
    
    print(f"Starting race split migration...")
    print(f"Table: {table_name}")
    if team_manager_id:
        print(f"Executed by: {team_manager_id}")
    else:
        print(f"Executed by: system (no user ID provided)")
    
    # Step 1: Check for existing boat registrations using old races
    print("\n=== Step 1: Checking for boat registrations ===")
    boats_to_update = []
    
    for old_race_id in OLD_RACES_TO_DELETE:
        response = table.query(
            IndexName='GSI1',
            KeyConditionExpression='GSI1PK = :pk',
            ExpressionAttributeValues={':pk': f'RACE#{old_race_id}'}
        )
        
        if response['Items']:
            print(f"WARNING: Found {len(response['Items'])} boat(s) registered for race {old_race_id}")
            boats_to_update.extend(response['Items'])
    
    if boats_to_update:
        print(f"\nERROR: Cannot proceed with migration!")
        print(f"Found {len(boats_to_update)} boat registrations using old race IDs.")
        print("Please manually update or delete these registrations first.")
        return False
    
    print("✓ No boat registrations found for old races")
    
    # Step 2: Delete old races
    print("\n=== Step 2: Deleting old races ===")
    deleted_count = 0
    
    for old_race_id in OLD_RACES_TO_DELETE:
        try:
            table.delete_item(
                Key={'PK': 'RACE', 'SK': old_race_id}
            )
            print(f"✓ Deleted race {old_race_id}")
            deleted_count += 1
        except Exception as e:
            print(f"✗ Error deleting race {old_race_id}: {str(e)}")
    
    print(f"\nDeleted {deleted_count}/{len(OLD_RACES_TO_DELETE)} old races")
    
    # Step 3: Create new races
    print("\n=== Step 3: Creating new races ===")
    created_count = 0
    
    for race in NEW_RACES:
        race_item = {
            'PK': 'RACE',
            'SK': race['race_id'],
            'GSI2PK': f"21km#{race['boat_type']}",
            'GSI2SK': f"{race['age_category']}#{race['gender_category']}",
            'race_id': race['race_id'],
            'name': race['name'],
            'event_type': '21km',
            'boat_type': race['boat_type'],
            'age_category': race['age_category'],
            'gender_category': race['gender_category'],
            'distance': 21,
            'created_at': datetime.utcnow().isoformat() + 'Z',
        }
        
        try:
            table.put_item(Item=race_item)
            print(f"✓ Created race {race['race_id']}: {race['name']}")
            created_count += 1
        except Exception as e:
            print(f"✗ Error creating race {race['race_id']}: {str(e)}")
    
    print(f"\nCreated {created_count}/{len(NEW_RACES)} new races")
    
    # Summary
    print("\n=== Migration Summary ===")
    print(f"Deleted: {deleted_count} old races")
    print(f"Created: {created_count} new races")
    print(f"Total races now: 14 marathon + {8 + created_count} semi-marathon = {14 + 8 + created_count} races")
    
    if deleted_count == len(OLD_RACES_TO_DELETE) and created_count == len(NEW_RACES):
        print("\n✓ Migration completed successfully!")
        return True
    else:
        print("\n⚠ Migration completed with errors. Please review the output above.")
        return False


if __name__ == '__main__':
    # Get environment variables
    table_name = os.environ.get('TABLE_NAME')
    team_manager_id = os.environ.get('TEAM_MANAGER_ID')  # Optional for this migration
    
    if not table_name:
        print("Error: TABLE_NAME environment variable must be set")
        exit(1)
    
    success = migrate(table_name, team_manager_id)
    exit(0 if success else 1)
