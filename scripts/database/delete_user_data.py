#!/usr/bin/env python3
"""
Delete user data from DynamoDB table
Used by db-reset Makefile target
"""
import json
import sys
import boto3

def main():
    if len(sys.argv) != 3:
        print("Usage: delete_user_data.py <table_name> <items_file>")
        sys.exit(1)
    
    table_name = sys.argv[1]
    items_file = sys.argv[2]
    
    # Load items to delete
    with open(items_file, 'r') as f:
        data = json.load(f)
        items = data.get('Items', [])
    
    if not items:
        print("✓ No items to delete")
        return
    
    # Connect to DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')
    table = dynamodb.Table(table_name)
    
    # Delete items
    count = 0
    for item in items:
        pk = item['PK']['S']
        sk = item['SK']['S']
        table.delete_item(Key={'PK': pk, 'SK': sk})
        count += 1
    
    print(f"✓ Deleted {count} items")

if __name__ == '__main__':
    main()
