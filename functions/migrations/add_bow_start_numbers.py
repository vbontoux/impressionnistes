"""
Migration: Add bow start numbers to race timing configuration

This migration adds the bow starting numbers for marathon and semi-marathon races:
- marathon_bow_start: 1 (default starting bow number for marathon races)
- semi_marathon_bow_start: 41 (default starting bow number for semi-marathon races)

Run with: make db-migrate MIGRATION=add_bow_start_numbers ENV=dev
Run with: make db-migrate MIGRATION=add_bow_start_numbers ENV=prod
"""

import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')


def migrate(table_name, team_manager_id=None):
    """
    Add bow start numbers to race timing configuration
    
    Args:
        table_name: DynamoDB table name
        team_manager_id: User ID running the migration (optional)
    """
    table = dynamodb.Table(table_name)
    
    print(f"Adding bow start numbers to race timing configuration in table: {table_name}")
    if team_manager_id:
        print(f"Executed by: {team_manager_id}")
    
    try:
        # Get existing race timing config
        response = table.get_item(
            Key={'PK': 'CONFIG', 'SK': 'RACE_TIMING'}
        )
        
        if 'Item' not in response:
            print("\n✗ Race timing configuration not found. Please run init_config first.")
            return False
        
        existing_config = response['Item']
        
        # Check if bow start numbers already exist
        if 'marathon_bow_start' in existing_config and 'semi_marathon_bow_start' in existing_config:
            print("\n⚠ Bow start numbers already exist in race timing configuration")
            print(f"  - Marathon bow start: {existing_config['marathon_bow_start']}")
            print(f"  - Semi-marathon bow start: {existing_config['semi_marathon_bow_start']}")
            return False
        
        # Update with bow start numbers
        current_time = datetime.utcnow().isoformat() + 'Z'
        update_expression = 'SET marathon_bow_start = :marathon_bow, semi_marathon_bow_start = :semi_bow, updated_at = :time'
        expression_attribute_values = {
            ':marathon_bow': 1,
            ':semi_bow': 41,
            ':time': current_time
        }
        
        # Add updated_by if team_manager_id provided
        if team_manager_id:
            update_expression += ', updated_by = :user'
            expression_attribute_values[':user'] = team_manager_id
        
        table.update_item(
            Key={'PK': 'CONFIG', 'SK': 'RACE_TIMING'},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        
        print("\n✓ Bow start numbers added successfully")
        print(f"  - Marathon bow start: 1")
        print(f"  - Semi-marathon bow start: 41")
        return True
        
    except Exception as e:
        print(f"\n✗ Error adding bow start numbers: {str(e)}")
        raise


if __name__ == '__main__':
    # Support running directly with TABLE_NAME environment variable
    table_name = os.environ.get('TABLE_NAME')
    team_manager_id = os.environ.get('TEAM_MANAGER_ID')
    
    if not table_name:
        print("ERROR: TABLE_NAME environment variable not set")
        print("Usage: TABLE_NAME=your-table-name python add_bow_start_numbers.py")
        exit(1)
    
    migrate(table_name, team_manager_id)
