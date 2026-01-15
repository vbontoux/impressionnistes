#!/usr/bin/env python3
"""
Migration: Add Permission Matrix to Database

This migration adds the CONFIG#PERMISSIONS item to the database for existing
environments that were created before the centralized access control feature.

Usage:
    make db-migrate MIGRATION=add_permission_matrix

Safe to run multiple times - uses conditional write to avoid overwriting.
"""
import os
import sys
import boto3
from datetime import datetime

# Default permission matrix matching requirements
DEFAULT_PERMISSIONS = {
    'create_crew_member': {
        'before_registration': False,
        'during_registration': True,
        'after_registration': False,
        'after_payment_deadline': False,
    },
    'edit_crew_member': {
        'before_registration': False,
        'during_registration': True,
        'after_registration': False,
        'after_payment_deadline': False,
        'requires_not_assigned': True,
    },
    'delete_crew_member': {
        'before_registration': False,
        'during_registration': True,
        'after_registration': False,
        'after_payment_deadline': False,
        'requires_not_assigned': True,
    },
    'create_boat_registration': {
        'before_registration': False,
        'during_registration': True,
        'after_registration': False,
        'after_payment_deadline': False,
    },
    'edit_boat_registration': {
        'before_registration': False,
        'during_registration': True,
        'after_registration': False,
        'after_payment_deadline': False,
        'requires_not_paid': True,
    },
    'delete_boat_registration': {
        'before_registration': False,
        'during_registration': True,
        'after_registration': False,
        'after_payment_deadline': False,
        'requires_not_paid': True,
    },
    'process_payment': {
        'before_registration': False,
        'during_registration': True,
        'after_registration': True,
        'after_payment_deadline': False,
    },
    'view_data': {
        'before_registration': True,
        'during_registration': True,
        'after_registration': True,
        'after_payment_deadline': True,
    },
    'export_data': {
        'before_registration': True,
        'during_registration': True,
        'after_registration': True,
        'after_payment_deadline': True,
    },
}


def main():
    """Add permission matrix to database."""
    table_name = os.environ.get('TABLE_NAME')
    
    if not table_name:
        print("Error: TABLE_NAME environment variable not set")
        sys.exit(1)
    
    print(f"Table: {table_name}")
    print()
    
    # Initialize DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    # Check if permission matrix already exists
    print("Checking if permission matrix already exists...")
    try:
        response = table.get_item(
            Key={
                'PK': 'CONFIG',
                'SK': 'PERMISSIONS'
            }
        )
        
        if 'Item' in response:
            print("✓ Permission matrix already exists in database")
            print()
            print("Current permissions:")
            for action in response['Item'].get('permissions', {}).keys():
                print(f"  - {action}")
            print()
            print("No changes needed - migration already applied")
            return
            
    except Exception as e:
        print(f"Error checking for existing permission matrix: {e}")
        sys.exit(1)
    
    # Permission matrix doesn't exist, add it
    print("Permission matrix not found - adding it now...")
    print()
    
    permission_matrix = {
        'PK': 'CONFIG',
        'SK': 'PERMISSIONS',
        'permissions': DEFAULT_PERMISSIONS,
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'updated_at': datetime.utcnow().isoformat() + 'Z',
        'updated_by': 'migration_add_permission_matrix',
    }
    
    try:
        table.put_item(
            Item=permission_matrix,
            ConditionExpression='attribute_not_exists(PK)'
        )
        print("✓ Permission matrix added successfully")
        print()
        print("Added permissions:")
        for action in DEFAULT_PERMISSIONS.keys():
            print(f"  - {action}")
        print()
        
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        print("✓ Permission matrix already exists (race condition)")
        print("No changes needed")
        
    except Exception as e:
        print(f"✗ Error adding permission matrix: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
