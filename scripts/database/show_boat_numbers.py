#!/usr/bin/env python3
"""Show what boat numbers would be generated for current boats"""
import json
from collections import defaultdict

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

with open('exports/dynamodb-dev-20260103-214940.json', 'r') as f:
    data = json.load(f)

items = data.get('Items', [])

# Get all boats
boats = [item for item in items if get_value(item, 'SK') and get_value(item, 'SK').startswith('BOAT#')]

# Get all races
races = {}
for item in items:
    sk = get_value(item, 'SK')
    if sk and sk.startswith('RACE#'):
        race_id = get_value(item, 'race_id')
        if race_id:
            races[race_id] = {
                'name': get_value(item, 'name'),
                'event_type': get_value(item, 'event_type'),
                'display_order': get_value(item, 'display_order')
            }

print("=" * 80)
print("BOAT NUMBERS - CURRENT STATUS")
print("=" * 80)
print()

# Group boats by race_id
boats_by_race = defaultdict(list)
boats_without_race = []

for boat in boats:
    race_id = get_value(boat, 'race_id')
    boat_id = get_value(boat, 'boat_registration_id')
    club_display = get_value(boat, 'boat_club_display')
    created_at = get_value(boat, 'created_at')
    
    if race_id:
        boats_by_race[race_id].append({
            'boat_id': boat_id,
            'race_id': race_id,
            'club_display': club_display,
            'created_at': created_at
        })
    else:
        boats_without_race.append({
            'boat_id': boat_id,
            'club_display': club_display
        })

print(f"Total boats: {len(boats)}")
print(f"Boats with race assigned: {len(boats) - len(boats_without_race)}")
print(f"Boats without race: {len(boats_without_race)}")
print(f"Unique races referenced: {len(boats_by_race)}")
print(f"Actual races in database: {len(races)}")
print()

# Show boats grouped by race
print("=" * 80)
print("BOATS BY RACE (with hypothetical boat numbers)")
print("=" * 80)
print()

for race_id, race_boats in sorted(boats_by_race.items()):
    race = races.get(race_id)
    
    if race:
        print(f"✓ Race: {race['name']} (ID: {race_id})")
        print(f"  Event: {race['event_type']}, Display Order: {race['display_order']}")
        
        # Sort boats by created_at
        sorted_boats = sorted(race_boats, key=lambda b: b['created_at'])
        
        # Generate hypothetical boat numbers
        prefix = "M" if race['event_type'] == "42km" else "SM"
        display_order = race['display_order']
        
        for i, boat in enumerate(sorted_boats, 1):
            boat_number = f"{prefix}.{display_order}.{i}"
            print(f"    {boat_number} - {boat['club_display'][:60]}")
    else:
        print(f"✗ Race ID: {race_id} (NOT FOUND IN DATABASE)")
        print(f"  Boats: {len(race_boats)}")
        for boat in race_boats:
            print(f"    (no number) - {boat['club_display'][:60]}")
    
    print()

if boats_without_race:
    print("=" * 80)
    print("BOATS WITHOUT RACE ASSIGNED")
    print("=" * 80)
    print()
    for boat in boats_without_race:
        print(f"  (no number) - {boat['club_display'][:60]}")
    print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("Current situation:")
print("  - All boats have race IDs like 'M06', 'SM16', etc.")
print("  - These race IDs don't match actual race records in the database")
print("  - Therefore, NO boat numbers were generated during migration")
print()
print("To generate boat numbers:")
print("  1. Boats need to be assigned to valid race IDs from the race table")
print("  2. Or races need to be created with IDs matching the current race_id values")
print("  3. Then the migration can generate proper boat numbers")
print()
