#!/usr/bin/env python3
"""
Migration Script: Reset Paid Crews to Appropriate Status

This migration resets all crews with registration_status='paid' back to their
appropriate status based on current crew state. This is necessary before
implementing the boat request feature which changes pricing logic.

The script will:
1. Find all crews with registration_status='paid'
2. Recalculate their status based on current state:
   - Check if all seats are filled
   - Check if race is selected
   - Determine if all crew members are RCPM (→ 'free')
   - Otherwise → 'complete' or 'incomplete'
3. Update each crew to the appropriate status

Note: This does NOT refund payments or modify payment records. It only updates
the registration_status field to reflect the current crew state.

Requirements: Preparation for boat request feature (pricing logic changes)
"""
import os
import sys
import boto3
from datetime import datetime

# Add parent directory to path to import shared utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
from boat_registration_utils import is_registration_complete, get_assigned_crew_members
from validation import is_rcpm_member


def is_all_rcpm_crew(crew_members):
    """
    Check if all crew members are RCPM members
    
    Args:
        crew_members: List of crew member objects
    
    Returns:
        True if all crew members are RCPM members
    """
    if not crew_members:
        return False
    
    for member in crew_members:
        club = member.get('club_affiliation', '')
        if not is_rcpm_member(club):
            return False
    
    return True


def calculate_new_status(boat, all_crew_members):
    """
    Calculate the appropriate status for a boat registration
    
    Args:
        boat: Boat registration dictionary
        all_crew_members: List of all crew members for this team
    
    Returns:
        New status string: 'incomplete', 'complete', or 'free'
    """
    # Check if registration is complete (all seats filled + race selected)
    if not is_registration_complete(boat):
        return 'incomplete'
    
    # Get assigned crew members
    seats = boat.get('seats', [])
    assigned_members = get_assigned_crew_members(seats, all_crew_members)
    
    # If all crew members are RCPM, the boat is free
    if assigned_members and is_all_rcpm_crew(assigned_members):
        return 'free'
    
    # Otherwise, it's complete
    return 'complete'


def run_migration(table_name):
    """
    Main migration logic
    
    Args:
        table_name: DynamoDB table name
    
    Returns:
        True if migration succeeded, False otherwise
    """
    # Use default AWS profile
    session = boto3.Session(profile_name='default')
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    print("Scanning database for paid crews...")
    
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
    
    # Filter for paid boat registrations
    paid_boats = [
        item for item in items 
        if item.get('SK', '').startswith('BOAT#') 
        and item.get('registration_status') == 'paid'
    ]
    
    print(f"Found {len(paid_boats)} paid boat registrations")
    print()
    
    if not paid_boats:
        print("✓ No paid boats found - nothing to migrate")
        return True
    
    # Group boats by team manager for efficient crew member lookup
    boats_by_team = {}
    for boat in paid_boats:
        team_id = boat.get('PK', '').replace('TEAM#', '')
        if team_id not in boats_by_team:
            boats_by_team[team_id] = []
        boats_by_team[team_id].append(boat)
    
    print(f"Processing paid boats for {len(boats_by_team)} team managers")
    print()
    
    boats_updated = 0
    boats_errors = 0
    status_counts = {
        'incomplete': 0,
        'complete': 0,
        'free': 0
    }
    
    # Process each team manager's boats
    for team_id, team_boats in boats_by_team.items():
        print(f"Team Manager: {team_id} ({len(team_boats)} paid boats)")
        
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
        
        # Process each paid boat
        for boat in team_boats:
            boat_id = boat.get('boat_registration_id', 'unknown')
            old_status = boat.get('registration_status', 'unknown')
            
            try:
                # Calculate new status based on current crew state
                new_status = calculate_new_status(boat, all_crew_members)
                
                # Update boat with new status
                table.update_item(
                    Key={
                        'PK': boat['PK'],
                        'SK': boat['SK']
                    },
                    UpdateExpression='SET registration_status = :status, updated_at = :updated',
                    ExpressionAttributeValues={
                        ':status': new_status,
                        ':updated': datetime.utcnow().isoformat() + 'Z'
                    }
                )
                
                print(f"  ✓ {boat_id}: {old_status} → {new_status}")
                boats_updated += 1
                status_counts[new_status] += 1
                
            except Exception as e:
                print(f"  ❌ {boat_id}: Error - {e}")
                boats_errors += 1
        
        print()
    
    # Summary
    print("=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Boats processed: {len(paid_boats)}")
    print(f"Boats updated:   {boats_updated}")
    print(f"Errors:          {boats_errors}")
    print()
    print("New status distribution:")
    print(f"  incomplete: {status_counts['incomplete']}")
    print(f"  complete:   {status_counts['complete']}")
    print(f"  free:       {status_counts['free']}")
    print("=" * 60)
    
    return boats_errors == 0


def main():
    """Main migration function"""
    # Get table name from environment variable (set by Makefile)
    table_name = os.environ.get('TABLE_NAME')
    
    if not table_name:
        print("❌ Error: TABLE_NAME environment variable not set")
        print("This migration should be run via: make db-migrate MIGRATION=reset_paid_crews ENV=dev")
        sys.exit(1)
    
    env = 'prod' if 'prod' in table_name else 'dev'
    
    print("=" * 60)
    print("Reset Paid Crews Migration")
    print("=" * 60)
    print(f"Table: {table_name}")
    print(f"Environment: {env}")
    print("=" * 60)
    print()
    print("This migration will:")
    print("  1. Find all crews with registration_status='paid'")
    print("  2. Recalculate their status based on current state")
    print("  3. Update to 'incomplete', 'complete', or 'free'")
    print()
    print("⚠️  Note: This does NOT refund payments or modify payment records")
    print("   It only updates the registration_status field")
    print()
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
        print("     - Paid boats are now 'complete', 'free', or 'incomplete'")
        print("     - Status matches current crew state (seats filled, race selected)")
        print("     - All-RCPM crews are marked as 'free'")
        if env == 'dev':
            print("  3. Test in dev environment")
            print("  4. Run migration on prod: make db-migrate MIGRATION=reset_paid_crews ENV=prod")
        print()
        print("  5. Proceed with boat request feature implementation")
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("❌ Migration failed")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
