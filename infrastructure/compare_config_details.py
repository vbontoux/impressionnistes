#!/usr/bin/env python3
"""
Compare Configuration Details Between Dev and Prod

This script compares clubs and configuration records in detail.
"""
import boto3
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def scan_table(table_name, profile_name='default'):
    """Scan a DynamoDB table and return all items"""
    session = boto3.Session(profile_name=profile_name)
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    items = []
    response = table.scan()
    items.extend(response.get('Items', []))
    
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    
    return items

def compare_configs(dev_items, prod_items):
    """Compare configuration records"""
    print("=" * 80)
    print("CONFIGURATION COMPARISON")
    print("=" * 80)
    print()
    
    dev_configs = {item['SK']: item for item in dev_items if item.get('PK') == 'CONFIG'}
    prod_configs = {item['SK']: item for item in prod_items if item.get('PK') == 'CONFIG'}
    
    all_config_keys = sorted(set(list(dev_configs.keys()) + list(prod_configs.keys())))
    
    for config_key in all_config_keys:
        print(f"Configuration: {config_key}")
        print("-" * 80)
        
        dev_config = dev_configs.get(config_key)
        prod_config = prod_configs.get(config_key)
        
        if not dev_config:
            print("⚠️  Missing in DEV")
            print()
            continue
        
        if not prod_config:
            print("⚠️  Missing in PROD")
            print()
            continue
        
        # Compare all keys
        all_keys = sorted(set(list(dev_config.keys()) + list(prod_config.keys())))
        
        differences = []
        for key in all_keys:
            if key in ['PK', 'SK', 'created_at', 'updated_at', 'updated_by']:
                continue  # Skip metadata
            
            dev_value = dev_config.get(key)
            prod_value = prod_config.get(key)
            
            if dev_value != prod_value:
                differences.append((key, dev_value, prod_value))
        
        if differences:
            print("⚠️  DIFFERENCES FOUND:")
            for key, dev_val, prod_val in differences:
                print(f"\n  Field: {key}")
                print(f"  DEV:  {json.dumps(dev_val, indent=4, cls=DecimalEncoder)}")
                print(f"  PROD: {json.dumps(prod_val, indent=4, cls=DecimalEncoder)}")
        else:
            print("✓ Identical")
        
        print()

def compare_clubs(dev_items, prod_items):
    """Compare club records"""
    print("=" * 80)
    print("CLUBS COMPARISON")
    print("=" * 80)
    print()
    
    dev_clubs = {item['SK']: item for item in dev_items if item.get('PK') == 'CLUB'}
    prod_clubs = {item['SK']: item for item in prod_items if item.get('PK') == 'CLUB'}
    
    print(f"DEV clubs:  {len(dev_clubs)}")
    print(f"PROD clubs: {len(prod_clubs)}")
    print()
    
    # Check if same clubs exist
    dev_only = set(dev_clubs.keys()) - set(prod_clubs.keys())
    prod_only = set(prod_clubs.keys()) - set(dev_clubs.keys())
    common = set(dev_clubs.keys()) & set(prod_clubs.keys())
    
    if dev_only:
        print(f"⚠️  {len(dev_only)} clubs only in DEV:")
        for club_id in sorted(list(dev_only)[:5]):
            print(f"   - {club_id}: {dev_clubs[club_id].get('name', 'N/A')}")
        if len(dev_only) > 5:
            print(f"   ... and {len(dev_only) - 5} more")
        print()
    
    if prod_only:
        print(f"⚠️  {len(prod_only)} clubs only in PROD:")
        for club_id in sorted(list(prod_only)[:5]):
            print(f"   - {club_id}: {prod_clubs[club_id].get('name', 'N/A')}")
        if len(prod_only) > 5:
            print(f"   ... and {len(prod_only) - 5} more")
        print()
    
    if len(dev_clubs) == len(prod_clubs) and not dev_only and not prod_only:
        print("✓ Same clubs in both databases")
        print()
        
        # Sample a few clubs to check if data is identical
        print("Checking sample clubs for data differences...")
        sample_clubs = sorted(list(common))[:3]
        
        for club_id in sample_clubs:
            dev_club = dev_clubs[club_id]
            prod_club = prod_clubs[club_id]
            
            # Compare all fields except timestamps
            all_keys = set(list(dev_club.keys()) + list(prod_club.keys()))
            differences = []
            
            for key in all_keys:
                if key in ['created_at', 'updated_at']:
                    continue
                
                if dev_club.get(key) != prod_club.get(key):
                    differences.append(key)
            
            if differences:
                print(f"\n⚠️  Club {club_id} ({dev_club.get('name', 'N/A')}) has differences:")
                for key in differences:
                    print(f"   - {key}")
                    print(f"     DEV:  {dev_club.get(key)}")
                    print(f"     PROD: {prod_club.get(key)}")
            else:
                print(f"✓ Club {club_id} ({dev_club.get('name', 'N/A')}) is identical")
        
        print()

def compare_races(dev_items, prod_items):
    """Compare race records in detail"""
    print("=" * 80)
    print("RACES COMPARISON")
    print("=" * 80)
    print()
    
    dev_races = {item['SK']: item for item in dev_items if item.get('PK') == 'RACE'}
    prod_races = {item['SK']: item for item in prod_items if item.get('PK') == 'RACE'}
    
    print(f"DEV races:  {len(dev_races)}")
    print(f"PROD races: {len(prod_races)}")
    print()
    
    # Check if same races exist
    dev_only = set(dev_races.keys()) - set(prod_races.keys())
    prod_only = set(prod_races.keys()) - set(dev_races.keys())
    common = set(dev_races.keys()) & set(prod_races.keys())
    
    if dev_only:
        print(f"⚠️  {len(dev_only)} races only in DEV:")
        for race_id in sorted(list(dev_only)):
            race = dev_races[race_id]
            print(f"   - {race_id}: {race.get('short_name', 'N/A')} - {race.get('name', 'N/A')}")
        print()
    
    if prod_only:
        print(f"⚠️  {len(prod_only)} races only in PROD:")
        for race_id in sorted(list(prod_only)):
            race = prod_races[race_id]
            print(f"   - {race_id}: {race.get('short_name', 'N/A')} - {race.get('name', 'N/A')}")
        print()
    
    if not dev_only and not prod_only:
        print("✓ Same races in both databases")
        print()
    
    # Compare race details for common races
    if common:
        print(f"Comparing {len(common)} common races...")
        print()
        
        # Group races by event type
        marathon_races = []
        semi_marathon_races = []
        
        for race_id in sorted(common):
            dev_race = dev_races[race_id]
            prod_race = prod_races[race_id]
            
            event_type = dev_race.get('event_type', prod_race.get('event_type', 'unknown'))
            
            if event_type == '42km':
                marathon_races.append(race_id)
            elif event_type == '21km':
                semi_marathon_races.append(race_id)
        
        print(f"Marathon races (42km): {len(marathon_races)}")
        print(f"Semi-marathon races (21km): {len(semi_marathon_races)}")
        print()
        
        # Check for differences
        differences_found = False
        races_with_differences = []
        
        for race_id in sorted(common):
            dev_race = dev_races[race_id]
            prod_race = prod_races[race_id]
            
            # Compare all fields except timestamps
            all_keys = set(list(dev_race.keys()) + list(prod_race.keys()))
            field_differences = []
            
            for key in all_keys:
                if key in ['created_at', 'updated_at', 'PK', 'SK']:
                    continue
                
                dev_val = dev_race.get(key)
                prod_val = prod_race.get(key)
                
                if dev_val != prod_val:
                    field_differences.append((key, dev_val, prod_val))
            
            if field_differences:
                differences_found = True
                races_with_differences.append((race_id, dev_race, prod_race, field_differences))
        
        if differences_found:
            print(f"⚠️  DIFFERENCES FOUND in {len(races_with_differences)} races:")
            print()
            
            for race_id, dev_race, prod_race, field_diffs in races_with_differences:
                print(f"Race: {race_id} - {dev_race.get('short_name', 'N/A')}")
                print(f"  Name: {dev_race.get('name', 'N/A')}")
                print(f"  Differences:")
                
                for key, dev_val, prod_val in field_diffs:
                    print(f"    - {key}:")
                    print(f"      DEV:  {json.dumps(dev_val, cls=DecimalEncoder)}")
                    print(f"      PROD: {json.dumps(prod_val, cls=DecimalEncoder)}")
                print()
        else:
            print("✓ All races are identical between DEV and PROD")
            print()
        
        # Show detailed one-by-one comparison
        print("=" * 80)
        print("DETAILED ONE-BY-ONE RACE COMPARISON")
        print("=" * 80)
        print()
        
        # Marathon races
        print(f"MARATHON RACES (42km) - {len(marathon_races)} races:")
        print("-" * 80)
        for race_id in sorted(marathon_races):
            dev_race = dev_races[race_id]
            prod_race = prod_races[race_id]
            
            # Check if identical
            all_keys = set(list(dev_race.keys()) + list(prod_race.keys()))
            is_identical = True
            for key in all_keys:
                if key in ['created_at', 'updated_at', 'PK', 'SK']:
                    continue
                if dev_race.get(key) != prod_race.get(key):
                    is_identical = False
                    break
            
            status = "✓" if is_identical else "⚠️"
            print(f"{status} {race_id}: {dev_race.get('short_name', 'N/A'):12} | {dev_race.get('name', 'N/A')}")
            print(f"   Display Order: {dev_race.get('display_order', 'N/A'):3} | "
                  f"Event: {dev_race.get('event_type', 'N/A'):5} | "
                  f"Boat: {dev_race.get('boat_type', 'N/A'):8} | "
                  f"Age: {dev_race.get('age_category', 'N/A'):8} | "
                  f"Gender: {dev_race.get('gender_category', 'N/A'):8}")
            if dev_race.get('master_category'):
                print(f"   Master Category: {dev_race.get('master_category', 'N/A')}")
            print()
        
        # Semi-marathon races
        print(f"SEMI-MARATHON RACES (21km) - {len(semi_marathon_races)} races:")
        print("-" * 80)
        for race_id in sorted(semi_marathon_races):
            dev_race = dev_races[race_id]
            prod_race = prod_races[race_id]
            
            # Check if identical
            all_keys = set(list(dev_race.keys()) + list(prod_race.keys()))
            is_identical = True
            for key in all_keys:
                if key in ['created_at', 'updated_at', 'PK', 'SK']:
                    continue
                if dev_race.get(key) != prod_race.get(key):
                    is_identical = False
                    break
            
            status = "✓" if is_identical else "⚠️"
            print(f"{status} {race_id}: {dev_race.get('short_name', 'N/A'):12} | {dev_race.get('name', 'N/A')}")
            print(f"   Display Order: {dev_race.get('display_order', 'N/A'):3} | "
                  f"Event: {dev_race.get('event_type', 'N/A'):5} | "
                  f"Boat: {dev_race.get('boat_type', 'N/A'):8} | "
                  f"Age: {dev_race.get('age_category', 'N/A'):8} | "
                  f"Gender: {dev_race.get('gender_category', 'N/A'):8}")
            print()
    
    print()

def main():
    print("=" * 80)
    print("DETAILED CONFIGURATION COMPARISON: DEV vs PROD")
    print("=" * 80)
    print()
    
    # Scan databases
    print("Scanning databases...")
    dev_items = scan_table('impressionnistes-registration-dev', profile_name='default')
    prod_items = scan_table('impressionnistes-registration-prod', profile_name='rcpm')
    print(f"✓ DEV: {len(dev_items)} items")
    print(f"✓ PROD: {len(prod_items)} items")
    print()
    
    # Compare configurations
    compare_configs(dev_items, prod_items)
    
    # Compare clubs
    compare_clubs(dev_items, prod_items)
    
    # Compare races
    compare_races(dev_items, prod_items)
    
    print("=" * 80)
    print("COMPARISON COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
