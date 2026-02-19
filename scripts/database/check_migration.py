#!/usr/bin/env python3
"""Quick script to verify migration results"""
import json

def get_value(item, key):
    """Extract value from DynamoDB format"""
    if key not in item:
        return None
    val = item[key]
    if isinstance(val, dict):
        if 'S' in val:
            return val['S']
        elif 'N' in val:
            return val['N']
        elif 'BOOL' in val:
            return val['BOOL']
        elif 'L' in val:
            return [get_value({'v': v}, 'v') for v in val['L']]
        elif 'NULL' in val:
            return None
    return val

with open('exports/dynamodb-dev-20260103-214940.json', 'r') as f:
    data = json.load(f)

# Filter for boats
items = data.get('Items', [])
boats = [item for item in items if get_value(item, 'SK') and get_value(item, 'SK').startswith('BOAT#')]

print(f"Total boats: {len(boats)}\n")

# Check a few boats
print("Sample boats:")
print("=" * 80)
for i, boat in enumerate(boats[:5]):
    print(f"\nBoat {i+1}:")
    print(f"  ID: {get_value(boat, 'boat_registration_id')}")
    print(f"  Club Display: {get_value(boat, 'boat_club_display')}")
    print(f"  Club List: {get_value(boat, 'club_list')}")
    print(f"  Is Multi-Club: {get_value(boat, 'is_multi_club_crew')}")
    print(f"  Boat Number: {get_value(boat, 'boat_number')}")
    print(f"  Race ID: {get_value(boat, 'race_id')}")

# Check multi-club boats
print("\n" + "=" * 80)
print("Multi-club boats:")
print("=" * 80)
multi_club_boats = [b for b in boats if get_value(b, 'is_multi_club_crew') == True]
print(f"Found {len(multi_club_boats)} multi-club boats\n")
for boat in multi_club_boats[:3]:
    print(f"  {get_value(boat, 'boat_club_display')}")
    club_list = get_value(boat, 'club_list')
    print(f"    Clubs: {len(club_list) if club_list else 0}")
    print(f"    Multi-club flag: {get_value(boat, 'is_multi_club_crew')}")
    print()
