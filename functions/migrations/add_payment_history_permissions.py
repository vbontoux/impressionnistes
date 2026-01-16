"""
Migration: Add payment history permissions to permission matrix

This migration adds the following permissions:
- view_payment_history: View payment history and summary
- view_payment_analytics: View payment analytics (admin only)
- download_payment_invoice: Download payment invoices

Run with:
cd infrastructure && make db-migrate MIGRATION=add_payment_history_permissions ENV=dev
"""
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')


def migrate():
    """Add payment history permissions to permission matrix"""
    table_name = os.environ.get('TABLE_NAME')
    if not table_name:
        raise ValueError("TABLE_NAME environment variable not set")
    
    table = dynamodb.Table(table_name)
    
    print("Starting migration: add_payment_history_permissions")
    
    # Get current permission matrix (SK='PERMISSIONS' for phase-based system)
    response = table.get_item(
        Key={'PK': 'CONFIG', 'SK': 'PERMISSIONS'}
    )
    
    if 'Item' not in response:
        print("ERROR: Permission matrix not found. Run init_config first.")
        return False
    
    permission_matrix = response['Item']
    
    # Check if permissions already exist
    if 'view_payment_history' in permission_matrix.get('permissions', {}):
        print("Permissions already exist. Skipping migration.")
        return True
    
    # Add new permissions
    if 'permissions' not in permission_matrix:
        permission_matrix['permissions'] = {}
    
    # 1. view_payment_history - Available in all phases
    permission_matrix['permissions']['view_payment_history'] = {
        'before_registration': True,
        'during_registration': True,
        'after_registration': True,
        'after_payment_deadline': True,
    }
    
    # 2. view_payment_analytics - Available in all phases (admin only, enforced by decorator)
    permission_matrix['permissions']['view_payment_analytics'] = {
        'before_registration': True,
        'during_registration': True,
        'after_registration': True,
        'after_payment_deadline': True,
    }
    
    # 3. download_payment_invoice - Available in all phases
    permission_matrix['permissions']['download_payment_invoice'] = {
        'before_registration': True,
        'during_registration': True,
        'after_registration': True,
        'after_payment_deadline': True,
    }
    
    # Update timestamp
    permission_matrix['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    permission_matrix['updated_by'] = 'migration:add_payment_history_permissions'
    
    # Save updated permission matrix
    table.put_item(Item=permission_matrix)
    
    print("✓ Added view_payment_history permission")
    print("✓ Added view_payment_analytics permission")
    print("✓ Added download_payment_invoice permission")
    print("Migration completed successfully")
    
    return True


if __name__ == '__main__':
    success = migrate()
    exit(0 if success else 1)
