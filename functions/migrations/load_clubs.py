"""
Migration: Load rowing clubs into database

This migration loads all rowing clubs from rowing_clubs_detailed.json
into the database. Safe to run multiple times (uses put_item with condition).

Run with: make db-migrate MIGRATION=load_clubs TEAM_MANAGER_ID=system ENV=prod
"""
import boto3
import os
import json
from datetime import datetime
from pathlib import Path

dynamodb = boto3.resource('dynamodb')


def migrate(table_name, team_manager_id=None):
    """
    Load rowing clubs from JSON file into database
    
    Args:
        table_name: DynamoDB table name
        team_manager_id: User ID running the migration (optional)
    """
    table = dynamodb.Table(table_name)
    
    print(f"Loading clubs into table: {table_name}")
    if team_manager_id:
        print(f"Executed by: {team_manager_id}")
    
    # Load clubs from JSON file
    clubs_file = Path(__file__).parent.parent / 'init' / 'rowing_clubs_detailed.json'
    
    if not clubs_file.exists():
        print(f"ERROR: {clubs_file} not found")
        return False
    
    with open(clubs_file, 'r', encoding='utf-8') as f:
        clubs_data = json.load(f)
    
    print(f"Found {len(clubs_data)} clubs in JSON file")
    
    # Load clubs into database
    clubs_added = 0
    clubs_skipped = 0
    
    for club in clubs_data:
        club_item = {
            'PK': 'CLUB',
            'SK': club['club_id'],
            'club_id': club['club_id'],
            'name': club['name'],
            'url': club.get('url', ''),
            'structure_number': club.get('structure_number', ''),
            'phone': club.get('phone', []),
            'management_team': club.get('management_team', []),
            'created_at': datetime.utcnow().isoformat() + 'Z',
        }
        
        try:
            table.put_item(
                Item=club_item,
                ConditionExpression='attribute_not_exists(PK) AND attribute_not_exists(SK)'
            )
            clubs_added += 1
            if clubs_added % 50 == 0:
                print(f"  Loaded {clubs_added} clubs...")
        except table.meta.client.exceptions.ConditionalCheckFailedException:
            # Club already exists, skip
            clubs_skipped += 1
        except Exception as e:
            print(f"ERROR loading club {club['name']}: {str(e)}")
            clubs_skipped += 1
    
    print(f"\nMigration complete:")
    print(f"  Added: {clubs_added} clubs")
    print(f"  Skipped: {clubs_skipped} clubs (already exist)")
    print(f"  Total: {len(clubs_data)} clubs")
    
    return True


if __name__ == '__main__':
    table_name = os.environ.get('TABLE_NAME')
    team_manager_id = os.environ.get('TEAM_MANAGER_ID', 'system')
    
    if not table_name:
        print("ERROR: TABLE_NAME environment variable must be set")
        exit(1)
    
    success = migrate(table_name, team_manager_id)
    exit(0 if success else 1)
