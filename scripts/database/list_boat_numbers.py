#!/usr/bin/env python3
"""List all boat numbers that were generated"""
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
        elif 'NULL' in val:
            return None
    return val

# Get the latest export
import glob
import os
json_files = glob.glob('exports/dynamodb-dev-*.json')
latest_file = max(json_files, key=os.path.getctime)

print(f"Reading: {latest_file}\n")

with open(latest_file, 'r') as f:
    data = json.load(f)

items = data.get('Items', [])
boats = [item for item in items if get_value(item, 'SK') and get_value(item, 'SK').startswith('BOAT#')]

print("=" * 80)
print("BOAT NUMBERS GENERATED")
print("=" * 80)
print()

boats_with_numbers = []
boats_without_numbers = []

for boat in boats:
    boat_number = get_value(boat, 'boat_number')
    boat_id = get_value(boat, 'boat_registration_id')
    race_id = get_value(boat, 'race_id')
    club_display = get_value(boat, 'boat_club_display')
    
    if boat_number:
        boats_with_numbers.append({
            'boat_number': boat_number,
            'race_id': race_id,
            'club_display': club_display,
            'boat_id': boat_id
        })
    else:
        boats_without_numbers.append({
            'race_id': race_id,
            'club_display': club_display,
            'boat_id': boat_id
        })

# Sort by boat number
boats_with_numbers.sort(key=lambda b: b['boat_number'])

print(f"Boats with boat numbers: {len(boats_with_numbers)}")
print(f"Boats without boat numbers: {len(boats_without_numbers)}")
print()

if boats_with_numbers:
    print("BOATS WITH NUMBERS:")
    print("-" * 80)
    for boat in boats_with_numbers:
        print(f"  {boat['boat_number']:12} | Race: {boat['race_id']:6} | {boat['club_display'][:50]}")
    print()

if boats_without_numbers:
    print("BOATS WITHOUT NUMBERS:")
    print("-" * 80)
    for boat in boats_without_numbers:
        race_display = boat['race_id'] if boat['race_id'] else '(no race)'
        print(f"  {'(none)':12} | Race: {race_display:6} | {boat['club_display'][:50]}")
    print()

print("=" * 80)
