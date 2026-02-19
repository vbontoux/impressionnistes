#!/usr/bin/env python3
"""
Test script to verify boat access with admin impersonation
"""
import boto3
import sys

def test_boat_access(env='dev'):
    """Test if boat exists for Philippe"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(f'impressionnistes-registration-{env}')
    
    # Philippe's user ID
    philippe_id = 'f1a9805e-6061-707f-b00d-c4944975b7c3'
    
    # Boat ID from error
    boat_id = '297cc054-456e-4f36-b4c8-f464ac6ce626'
    
    print(f"Testing boat access for Philippe")
    print(f"Environment: {env}")
    print(f"Team Manager ID: {philippe_id}")
    print(f"Boat ID: {boat_id}")
    print("=" * 60)
    print()
    
    # Try to get the boat
    pk = f'TEAM#{philippe_id}'
    sk = f'BOAT#{boat_id}'
    
    print(f"Querying DynamoDB:")
    print(f"  PK: {pk}")
    print(f"  SK: {sk}")
    print()
    
    try:
        response = table.get_item(
            Key={
                'PK': pk,
                'SK': sk
            }
        )
        
        if 'Item' in response:
            print("✓ Boat found!")
            print()
            item = response['Item']
            print(f"Boat details:")
            print(f"  Boat Name: {item.get('boat_name', 'N/A')}")
            print(f"  Boat Type: {item.get('boat_type', 'N/A')}")
            print(f"  Race ID: {item.get('race_id', 'N/A')}")
            print(f"  Status: {item.get('registration_status', 'N/A')}")
        else:
            print("✗ Boat NOT found!")
            print()
            print("This boat does not exist for Philippe.")
            print()
            print("Let's list all boats for Philippe:")
            print()
            
            # List all boats for Philippe
            response = table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':pk': pk,
                    ':sk_prefix': 'BOAT#'
                }
            )
            
            boats = response.get('Items', [])
            if boats:
                print(f"Found {len(boats)} boats for Philippe:")
                for boat in boats:
                    boat_id_from_sk = boat['SK'].replace('BOAT#', '')
                    print(f"  - {boat.get('boat_name', 'Unnamed')} (ID: {boat_id_from_sk})")
            else:
                print("Philippe has no boats registered!")
                
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    env = sys.argv[1] if len(sys.argv) > 1 else 'dev'
    test_boat_access(env)
