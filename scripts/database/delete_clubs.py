#!/usr/bin/env python3
"""Delete all clubs from DynamoDB"""
import boto3

dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')
table = dynamodb.Table('impressionnistes-registration-dev')

# Query all clubs
response = table.query(
    KeyConditionExpression='PK = :pk',
    ExpressionAttributeValues={':pk': 'CLUB'}
)

items = response['Items']
print(f'Found {len(items)} clubs to delete')

# Delete all clubs
for item in items:
    table.delete_item(Key={'PK': 'CLUB', 'SK': item['SK']})
    print(f"Deleted: {item['name']}")

print(f'Deleted {len(items)} clubs')
