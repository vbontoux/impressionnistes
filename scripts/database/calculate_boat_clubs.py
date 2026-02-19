#!/usr/bin/env python3
"""
Calculate and populate boat_club_display and club_list fields for all boat registrations
This migration adds the new club display fields based on assigned crew members
"""
import os
import sys
import boto3
from datetime import datetime

# Add parent directory to path to import shared utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
from boat_registration_utils import calculate_boat_club_info


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


def calculate_boat_clubs(table_name):
    """Calculate boat_club_display and club_list for all boat registrations"""
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    print("Scanning for boat registrations...")
    
    # Scan for all boat registrations
    boats_updated = 0
    boats_skipped = 0
    boats_errors = 0
    
    try:
        # Get all items from the table
        response = table.scan()
        items = response.get('Items', [])
        
        # Continue scanning if there are more items
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        print(f"Found {len(items)} total items in database")
        
        # Filter for boat registrations
        boats = [item for item in items if item.get('SK', '').startswith('BOAT#')]
        print(f"Found {len(boats)} boat registrations")
        
        if not boats:
            print("⚠️  No boat registrations found - nothing to migrate")
            return True
        
        # Group boats by team manager for efficient crew member lookup
        boats_by_team = {}
        for boat in boats:
            team_id = boat.get('PK', '').replace('TEAM#', '')
            if team_id not in boats_by_team:
                boats_by_team[team_id] = []
            boats_by_team[team_id].append(boat)
        
        print(f"Processing boats for {len(boats_by_team)} team managers...")
        print("")
        
        # Process each team manager's boats
        for team_id, team_boats in boats_by_team.items():
            print(f"Team Manager: {team_id} ({len(team_boats)} boats)")
            
            # Get team manager profile for club affiliation
            try:
                tm_response = table.get_item(
                    Key={
                        'PK': f'USER#{team_id}',
                        'SK': 'PROFILE'
                    }
                )
                team_manager = tm_response.get('Item', {})
                team_manager_club = team_manager.get('club_affiliation', '')
            except Exception as e:
                print(f"  ⚠️  Could not fetch team manager profile: {e}")
                team_manager_club = ''
            
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
                    # Check if already has club fields
                    if 'boat_club_display' in boat and 'club_list' in boat:
                        print(f"  ✓ {boat_id}: Already has club fields - skipping")
                        boats_skipped += 1
                        continue
                    
                    # Get assigned crew members
                    seats = boat.get('seats', [])
                    assigned_members = get_assigned_crew_members(seats, all_crew_members)
                    
                    # Calculate club info
                    club_info = calculate_boat_club_info(assigned_members, team_manager_club)
                    
                    # Update boat with club fields
                    table.update_item(
                        Key={
                            'PK': boat['PK'],
                            'SK': boat['SK']
                        },
                        UpdateExpression='SET boat_club_display = :display, club_list = :list, updated_at = :updated',
                        ExpressionAttributeValues={
                            ':display': club_info['boat_club_display'],
                            ':list': club_info['club_list'],
                            ':updated': datetime.utcnow().isoformat() + 'Z'
                        }
                    )
                    
                    print(f"  ✓ {boat_id}: {club_info['boat_club_display']} (clubs: {len(club_info['club_list'])})")
                    boats_updated += 1
                    
                except Exception as e:
                    print(f"  ❌ {boat_id}: Error - {e}")
                    boats_errors += 1
            
            print("")
        
        # Summary
        print("=" * 60)
        print("Migration Summary:")
        print(f"  Boats updated: {boats_updated}")
        print(f"  Boats skipped: {boats_skipped}")
        print(f"  Boats errors:  {boats_errors}")
        print("=" * 60)
        
        return boats_errors == 0
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    # Get table name from environment variable (set by Makefile)
    table_name = os.environ.get('TABLE_NAME')
    
    if not table_name:
        print("❌ Error: TABLE_NAME environment variable not set")
        print("This migration should be run via: make db-migrate MIGRATION=calculate_boat_clubs ENV=dev")
        sys.exit(1)
    
    env = 'prod' if 'prod' in table_name else 'dev'
    
    print("=" * 60)
    print("Calculate Boat Club Display Fields")
    print("=" * 60)
    print(f"Table: {table_name}")
    print(f"Environment: {env}")
    print("=" * 60)
    print("")
    
    success = calculate_boat_clubs(table_name)
    
    if success:
        print("")
        print("=" * 60)
        print("✓ Migration completed successfully")
        print("=" * 60)
        print("")
        print("Next steps:")
        print("  1. Verify data with: make db-export ENV=" + env)
        print("  2. Check a few boats manually to ensure club fields are correct")
        if env == 'dev':
            print("  3. Deploy backend to dev: make deploy-dev")
            print("  4. Test in dev environment")
            print("  5. Run migration on prod: make db-migrate MIGRATION=calculate_boat_clubs ENV=prod")
        sys.exit(0)
    else:
        print("")
        print("=" * 60)
        print("❌ Migration failed")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
