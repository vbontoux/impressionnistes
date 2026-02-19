#!/usr/bin/env python3
"""
Migration Script: Generate Boat Numbers and Simplify Club Display

This migration performs two updates to all boat registrations:

Phase 1: Update all boat_club_display to simplified format
- Recalculate boat_club_display using new comma-separated format
- Update is_multi_club_crew based on club_list length
- Keep club_list unchanged

Phase 2: Generate boat_numbers for all boats with races
- Group boats by race_id
- Sort boats by created_at within each race
- Assign sequence numbers starting from 1
- Generate and store boat_number for each boat

Requirements: 1.1, 2.1, 2.4, 2.5, 4.3
"""
import os
import sys
import boto3
from datetime import datetime
from collections import defaultdict

# Add parent directory to path to import shared utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
from boat_registration_utils import calculate_boat_club_info, generate_boat_number


def get_assigned_crew_members(seats, all_crew_members):
    """
    Extract assigned crew members from seats
    
    Args:
        seats: List of seat dictionaries with crew_member_id
        all_crew_members: List of all crew member objects
        
    Returns:
        List of assigned crew member objects
    """
    # Create a map for quick lookup
    crew_map = {cm['crew_member_id']: cm for cm in all_crew_members}
    
    # Get assigned crew members
    assigned = []
    for seat in seats:
        crew_id = seat.get('crew_member_id')
        if crew_id and crew_id in crew_map:
            assigned.append(crew_map[crew_id])
    
    return assigned


def phase1_simplify_club_display(table, boats_by_team, items):
    """
    Phase 1: Update all boat_club_display to simplified format
    
    Args:
        table: DynamoDB table resource
        boats_by_team: Dictionary of boats grouped by team manager ID
        items: All items from database (for looking up team managers)
    
    Returns:
        Tuple of (boats_updated, boats_errors)
    """
    print("=" * 60)
    print("PHASE 1: Simplify Club Display")
    print("=" * 60)
    print()
    
    boats_updated = 0
    boats_errors = 0
    
    # Create a map of team managers for quick lookup
    team_managers = {}
    for item in items:
        if item.get('SK') == 'PROFILE':
            user_id = item.get('PK', '').replace('USER#', '')
            team_managers[user_id] = item
    
    # Process each team manager's boats
    for team_id, team_boats in boats_by_team.items():
        print(f"Team Manager: {team_id} ({len(team_boats)} boats)")
        
        # Get team manager profile for club affiliation
        team_manager = team_managers.get(team_id, {})
        team_manager_club = team_manager.get('club_affiliation', '')
        
        # Get all crew members for this team
        try:
            crew_response = table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
                ExpressionAttributeValues={
                    ':pk': f'TEAM#{team_id}',
                    ':sk': 'CREW#'
                }
            )
            all_crew_members = crew_response.get('Items', [])
        except Exception as e:
            print(f"  ⚠️  Could not fetch crew members: {e}")
            all_crew_members = []
        
        # Process each boat
        for boat in team_boats:
            boat_id = boat.get('boat_registration_id', 'unknown')
            
            try:
                # Get assigned crew members
                seats = boat.get('seats', [])
                assigned_members = get_assigned_crew_members(seats, all_crew_members)
                
                # Calculate new club info
                club_info = calculate_boat_club_info(assigned_members, team_manager_club)
                
                # Update boat with new club display format
                table.update_item(
                    Key={
                        'PK': boat['PK'],
                        'SK': boat['SK']
                    },
                    UpdateExpression='SET boat_club_display = :display, club_list = :list, is_multi_club_crew = :multi, updated_at = :updated',
                    ExpressionAttributeValues={
                        ':display': club_info['boat_club_display'],
                        ':list': club_info['club_list'],
                        ':multi': club_info['is_multi_club_crew'],
                        ':updated': datetime.utcnow().isoformat() + 'Z'
                    }
                )
                
                print(f"  ✓ {boat_id}: {club_info['boat_club_display']}")
                boats_updated += 1
                
            except Exception as e:
                print(f"  ❌ {boat_id}: Error - {e}")
                boats_errors += 1
        
        print()
    
    print("Phase 1 Summary:")
    print(f"  Boats updated: {boats_updated}")
    print(f"  Boats errors:  {boats_errors}")
    print()
    
    return boats_updated, boats_errors


def phase2_generate_boat_numbers(table, boats_by_team, items):
    """
    Phase 2: Generate boat_numbers for all boats with races
    
    Args:
        table: DynamoDB table resource
        boats_by_team: Dictionary of boats grouped by team manager ID
        items: All items from database (for looking up races)
    
    Returns:
        Tuple of (boats_updated, boats_skipped, boats_errors)
    """
    print("=" * 60)
    print("PHASE 2: Generate Boat Numbers")
    print("=" * 60)
    print()
    
    boats_updated = 0
    boats_skipped = 0
    boats_errors = 0
    
    # Create a map of races for quick lookup
    # Races have PK='RACE' and SK=race_id (e.g., 'M01', 'SM15')
    races = {}
    for item in items:
        if item.get('PK') == 'RACE':
            race_id = item.get('race_id')
            if race_id:
                races[race_id] = item
    
    print(f"Found {len(races)} races in database")
    print()
    
    # Collect all boats with races and group by race_id
    boats_by_race = defaultdict(list)
    all_boats = []
    
    for team_id, team_boats in boats_by_team.items():
        for boat in team_boats:
            all_boats.append(boat)
            race_id = boat.get('race_id')
            if race_id:
                boats_by_race[race_id].append(boat)
    
    print(f"Found {len(all_boats)} total boats")
    print(f"Found {len(boats_by_race)} races with boats")
    print()
    
    # Process each race
    for race_id, race_boats in boats_by_race.items():
        race = races.get(race_id)
        
        if not race:
            print(f"⚠️  Race {race_id}: Race not found in database")
            for boat in race_boats:
                boat_id = boat.get('boat_registration_id', 'unknown')
                print(f"  ⚠️  {boat_id}: Skipping (race not found)")
                boats_skipped += 1
            print()
            continue
        
        race_name = race.get('name', race_id)
        event_type = race.get('event_type')
        display_order = race.get('display_order')
        
        if not event_type or display_order is None:
            print(f"⚠️  Race {race_name}: Missing event_type or display_order")
            for boat in race_boats:
                boat_id = boat.get('boat_registration_id', 'unknown')
                print(f"  ⚠️  {boat_id}: Skipping (invalid race data)")
                boats_skipped += 1
            print()
            continue
        
        print(f"Race: {race_name} ({event_type}, order {display_order})")
        print(f"  Boats in race: {len(race_boats)}")
        
        # Sort boats by created_at (first-come-first-served for initial numbers)
        sorted_boats = sorted(race_boats, key=lambda b: b.get('created_at', ''))
        
        # Generate boat numbers for each boat
        for boat in sorted_boats:
            boat_id = boat.get('boat_registration_id', 'unknown')
            
            try:
                # Generate boat number
                boat_number = generate_boat_number(
                    event_type=event_type,
                    display_order=display_order,
                    race_id=race_id,
                    all_boats_in_race=sorted_boats[:sorted_boats.index(boat)]  # Only boats processed so far
                )
                
                # Update boat with boat_number
                table.update_item(
                    Key={
                        'PK': boat['PK'],
                        'SK': boat['SK']
                    },
                    UpdateExpression='SET boat_number = :number, updated_at = :updated',
                    ExpressionAttributeValues={
                        ':number': boat_number,
                        ':updated': datetime.utcnow().isoformat() + 'Z'
                    }
                )
                
                print(f"  ✓ {boat_id}: {boat_number}")
                boats_updated += 1
                
                # Update the boat in our list so subsequent boats see it
                boat['boat_number'] = boat_number
                
            except Exception as e:
                print(f"  ❌ {boat_id}: Error - {e}")
                boats_errors += 1
        
        print()
    
    # Count boats without races
    boats_without_race = len([b for b in all_boats if not b.get('race_id')])
    if boats_without_race > 0:
        print(f"ℹ️  {boats_without_race} boats have no race assigned (boat_number will remain null)")
        print()
    
    print("Phase 2 Summary:")
    print(f"  Boats updated: {boats_updated}")
    print(f"  Boats skipped: {boats_skipped}")
    print(f"  Boats errors:  {boats_errors}")
    print()
    
    return boats_updated, boats_skipped, boats_errors


def run_migration(table_name):
    """
    Main migration logic
    
    Args:
        table_name: DynamoDB table name
    
    Returns:
        True if migration succeeded, False otherwise
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    print("Scanning database...")
    
    # Get all items from the table
    try:
        response = table.scan()
        items = response.get('Items', [])
        
        # Continue scanning if there are more items
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        print(f"Found {len(items)} total items in database")
        print()
        
    except Exception as e:
        print(f"❌ Error scanning database: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Filter for boat registrations
    boats = [item for item in items if item.get('SK', '').startswith('BOAT#')]
    print(f"Found {len(boats)} boat registrations")
    print()
    
    if not boats:
        print("⚠️  No boat registrations found - nothing to migrate")
        return True
    
    # Group boats by team manager for efficient processing
    boats_by_team = {}
    for boat in boats:
        team_id = boat.get('PK', '').replace('TEAM#', '')
        if team_id not in boats_by_team:
            boats_by_team[team_id] = []
        boats_by_team[team_id].append(boat)
    
    print(f"Processing boats for {len(boats_by_team)} team managers")
    print()
    
    # Phase 1: Simplify club display
    phase1_updated, phase1_errors = phase1_simplify_club_display(table, boats_by_team, items)
    
    # Phase 2: Generate boat numbers
    phase2_updated, phase2_skipped, phase2_errors = phase2_generate_boat_numbers(table, boats_by_team, items)
    
    # Overall summary
    print("=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Phase 1 - Club Display:")
    print(f"  Boats updated: {phase1_updated}")
    print(f"  Errors:        {phase1_errors}")
    print()
    print(f"Phase 2 - Boat Numbers:")
    print(f"  Boats updated: {phase2_updated}")
    print(f"  Boats skipped: {phase2_skipped}")
    print(f"  Errors:        {phase2_errors}")
    print()
    print(f"Total errors: {phase1_errors + phase2_errors}")
    print("=" * 60)
    
    return (phase1_errors + phase2_errors) == 0


def main():
    """Main migration function"""
    # Get table name from environment variable (set by Makefile)
    table_name = os.environ.get('TABLE_NAME')
    
    if not table_name:
        print("❌ Error: TABLE_NAME environment variable not set")
        print("This migration should be run via: make db-migrate MIGRATION=generate_boat_numbers_and_simplify_clubs ENV=dev")
        sys.exit(1)
    
    env = 'prod' if 'prod' in table_name else 'dev'
    
    print("=" * 60)
    print("Generate Boat Numbers and Simplify Club Display")
    print("=" * 60)
    print(f"Table: {table_name}")
    print(f"Environment: {env}")
    print("=" * 60)
    print()
    
    # Confirmation prompt
    if env == 'prod':
        print("⚠️  WARNING: You are about to modify PRODUCTION data!")
        print()
        response = input("Type 'yes' to continue: ")
        if response.lower() != 'yes':
            print("Migration cancelled")
            sys.exit(0)
        print()
    
    success = run_migration(table_name)
    
    if success:
        print()
        print("=" * 60)
        print("✓ Migration completed successfully")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Verify data with: make db-export ENV=" + env)
        print("  2. Check a few boats manually to ensure:")
        print("     - boat_club_display is comma-separated")
        print("     - boat_number is generated for boats with races")
        print("     - boat_number is null for boats without races")
        print("     - No duplicate boat_numbers within same race")
        if env == 'dev':
            print("  3. Test in dev environment")
            print("  4. Run migration on prod: make db-migrate MIGRATION=generate_boat_numbers_and_simplify_clubs ENV=prod")
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("❌ Migration failed")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
