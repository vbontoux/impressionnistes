#!/usr/bin/env python3
"""
Migration Script: Reset All Payments and Paid Crews

This migration completely resets the payment system by:
1. Deleting ALL payment records (PAYMENT# items)
2. Resetting all crews with registration_status='paid' to their appropriate status
3. Clearing payment-related fields from boat registrations

This is useful for testing payment features with clean data.

The script will:
1. Find and DELETE all payment records (SK starts with 'PAYMENT#')
2. Find all crews with registration_status='paid'
3. Recalculate their status based on current state:
   - Check if all seats are filled
   - Check if race is selected
   - Determine if all crew members are RCPM (→ 'free')
   - Otherwise → 'complete' or 'incomplete'
4. Clear payment-related fields: payment_id, paid_at, locked_pricing, pricing
5. Update each crew to the appropriate status

⚠️  WARNING: This PERMANENTLY DELETES all payment records!
Use only for testing or when you need to completely reset payment data.

Run with:
    cd infrastructure && make db-migrate MIGRATION=reset_all_payments_and_crews ENV=dev
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


def delete_all_payments(table):
    """
    Delete all payment records from the database
    
    Args:
        table: DynamoDB table resource
    
    Returns:
        Number of payments deleted
    """
    print("=" * 60)
    print("STEP 1: Delete All Payment Records")
    print("=" * 60)
    print()
    
    # Scan for all payment records
    print("Scanning for payment records...")
    try:
        response = table.scan(
            FilterExpression='begins_with(SK, :sk)',
            ExpressionAttributeValues={
                ':sk': 'PAYMENT#'
            }
        )
        payments = response.get('Items', [])
        
        # Continue scanning if there are more items
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                FilterExpression='begins_with(SK, :sk)',
                ExpressionAttributeValues={
                    ':sk': 'PAYMENT#'
                },
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            payments.extend(response.get('Items', []))
        
        print(f"Found {len(payments)} payment records")
        print()
        
    except Exception as e:
        print(f"❌ Error scanning for payments: {e}")
        import traceback
        traceback.print_exc()
        return 0
    
    if not payments:
        print("✓ No payment records found")
        print()
        return 0
    
    # Delete each payment record
    deleted_count = 0
    error_count = 0
    
    for payment in payments:
        payment_id = payment.get('payment_id', 'unknown')
        team_id = payment.get('PK', '').replace('TEAM#', '')
        
        try:
            table.delete_item(
                Key={
                    'PK': payment['PK'],
                    'SK': payment['SK']
                }
            )
            print(f"  ✓ Deleted payment {payment_id} (Team: {team_id})")
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ Error deleting payment {payment_id}: {e}")
            error_count += 1
    
    print()
    print(f"Payments deleted: {deleted_count}")
    print(f"Errors: {error_count}")
    print()
    
    return deleted_count


def reset_paid_crews(table):
    """
    Reset all paid crews to their appropriate status
    
    Args:
        table: DynamoDB table resource
    
    Returns:
        Tuple of (boats_updated, boats_errors)
    """
    print("=" * 60)
    print("STEP 2: Reset Paid Crews")
    print("=" * 60)
    print()
    
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
        return 0, 0
    
    # Filter for paid boat registrations
    paid_boats = [
        item for item in items 
        if item.get('SK', '').startswith('BOAT#') 
        and item.get('registration_status') == 'paid'
    ]
    
    print(f"Found {len(paid_boats)} paid boat registrations")
    print()
    
    if not paid_boats:
        print("✓ No paid boats found - nothing to reset")
        print()
        return 0, 0
    
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
                
                # Update boat: reset status and clear payment fields
                update_expression = 'SET registration_status = :status, updated_at = :updated'
                expression_values = {
                    ':status': new_status,
                    ':updated': datetime.utcnow().isoformat() + 'Z'
                }
                
                # Remove payment-related fields if they exist
                remove_parts = []
                if 'payment_id' in boat:
                    remove_parts.append('payment_id')
                if 'paid_at' in boat:
                    remove_parts.append('paid_at')
                if 'locked_pricing' in boat:
                    remove_parts.append('locked_pricing')
                if 'pricing' in boat:
                    remove_parts.append('pricing')
                
                if remove_parts:
                    update_expression += ' REMOVE ' + ', '.join(remove_parts)
                
                table.update_item(
                    Key={
                        'PK': boat['PK'],
                        'SK': boat['SK']
                    },
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_values
                )
                
                print(f"  ✓ {boat_id}: {old_status} → {new_status} (cleared payment fields)")
                boats_updated += 1
                status_counts[new_status] += 1
                
            except Exception as e:
                print(f"  ❌ {boat_id}: Error - {e}")
                boats_errors += 1
        
        print()
    
    print(f"Boats updated: {boats_updated}")
    print(f"Errors: {boats_errors}")
    print()
    print("New status distribution:")
    print(f"  incomplete: {status_counts['incomplete']}")
    print(f"  complete:   {status_counts['complete']}")
    print(f"  free:       {status_counts['free']}")
    print()
    
    return boats_updated, boats_errors


def run_migration(table_name, delete_payments):
    """
    Main migration logic
    
    Args:
        table_name: DynamoDB table name
        delete_payments: Boolean - whether to delete payment records
    
    Returns:
        True if migration succeeded, False otherwise
    """
    # Use default AWS profile
    session = boto3.Session(profile_name='default')
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    payments_deleted = 0
    
    # Step 1: Delete all payment records (optional)
    if delete_payments:
        payments_deleted = delete_all_payments(table)
    else:
        print("=" * 60)
        print("STEP 1: Delete Payment Records - SKIPPED")
        print("=" * 60)
        print("Payment records will be kept")
        print()
    
    # Step 2: Reset paid crews
    boats_updated, boats_errors = reset_paid_crews(table)
    
    # Summary
    print("=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    if delete_payments:
        print(f"Payment records deleted: {payments_deleted}")
    else:
        print(f"Payment records deleted: 0 (skipped)")
    print(f"Boats updated:           {boats_updated}")
    print(f"Errors:                  {boats_errors}")
    print("=" * 60)
    
    return boats_errors == 0


def main():
    """Main migration function"""
    # Get table name from environment variable (set by Makefile)
    table_name = os.environ.get('TABLE_NAME')
    
    if not table_name:
        print("❌ Error: TABLE_NAME environment variable not set")
        print("This migration should be run via: make db-migrate MIGRATION=reset_all_payments_and_crews ENV=dev")
        sys.exit(1)
    
    env = 'prod' if 'prod' in table_name else 'dev'
    
    print("=" * 60)
    print("Reset All Payments and Crews Migration")
    print("=" * 60)
    print(f"Table: {table_name}")
    print(f"Environment: {env}")
    print("=" * 60)
    print()
    print("This migration will:")
    print("  1. (Optional) DELETE all payment records (PAYMENT# items)")
    print("  2. Find all crews with registration_status='paid'")
    print("  3. Recalculate their status based on current state")
    print("  4. Clear payment fields: payment_id, paid_at, locked_pricing, pricing")
    print("  5. Update to 'incomplete', 'complete', or 'free'")
    print()
    print("Use this migration to:")
    print("  - Test payment features with clean data")
    print("  - Reset payment system after testing")
    print("  - Clear old payment data before new feature deployment")
    print()
    print("=" * 60)
    print()
    
    # Ask if user wants to delete payment history
    print("Do you want to DELETE all payment history records?")
    print("  - Type 'yes' to DELETE payment records")
    print("  - Type 'no' to KEEP payment records (only reset boat status)")
    print()
    delete_response = input("Delete payment history? (yes/no): ").lower()
    delete_payments = (delete_response == 'yes')
    print()
    
    if delete_payments:
        print("⚠️  Payment history will be DELETED")
    else:
        print("✓ Payment history will be KEPT")
    print()
    
    # Confirmation prompt
    if env == 'prod':
        if delete_payments:
            print("⚠️  WARNING: You are about to DELETE PRODUCTION PAYMENT DATA!")
            print()
            response = input("Type 'DELETE PRODUCTION PAYMENTS' to continue: ")
            if response != 'DELETE PRODUCTION PAYMENTS':
                print("Migration cancelled")
                sys.exit(0)
        else:
            print("⚠️  WARNING: You are about to modify PRODUCTION data!")
            print()
            response = input("Type 'yes' to continue: ")
            if response.lower() != 'yes':
                print("Migration cancelled")
                sys.exit(0)
        print()
    else:
        if delete_payments:
            print("⚠️  WARNING: This will DELETE all payment data in dev!")
        else:
            print("⚠️  This will reset boat statuses in dev")
        print()
        response = input("Type 'yes' to continue: ")
        if response.lower() != 'yes':
            print("Migration cancelled")
            sys.exit(0)
        print()
    
    success = run_migration(table_name, delete_payments)
    
    if success:
        print()
        print("=" * 60)
        print("✓ Migration completed successfully")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Verify data with: make db-export ENV=" + env)
        print("  2. Check that:")
        if delete_payments:
            print("     - All payment records are deleted")
        else:
            print("     - Payment records are still present")
        print("     - Paid boats are now 'complete', 'free', or 'incomplete'")
        print("     - Payment fields (payment_id, paid_at, pricing) are cleared from boats")
        print("  3. Test payment flow" + (" with clean data" if delete_payments else ""))
        if env == 'dev':
            print("  4. If needed, run on prod: make db-migrate MIGRATION=reset_all_payments_and_crews ENV=prod")
        print()
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("❌ Migration failed")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
