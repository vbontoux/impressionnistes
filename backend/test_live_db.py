#!/usr/bin/env python3
"""
Live database test script
Tests read/write operations against actual DynamoDB dev environment
"""
import os
import sys
import json
from datetime import datetime
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared import (
    get_config_manager,
    get_db_client,
    generate_id,
    get_timestamp,
    validate_crew_member,
    sanitize_dict,
    is_registration_active,
    get_base_seat_price
)


def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_success(message):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message):
    """Print error message"""
    print(f"❌ {message}")


def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")


def test_configuration_read():
    """Test reading configuration from DynamoDB"""
    print_section("Test 1: Configuration Read")
    
    try:
        config_manager = get_config_manager()
        
        # Test system config
        print_info("Reading system configuration...")
        system_config = config_manager.get_system_config()
        print_success(f"System config loaded")
        print(f"   Registration period: {system_config.get('registration_start_date')} to {system_config.get('registration_end_date')}")
        print(f"   Competition date: {system_config.get('competition_date')}")
        
        # Test pricing config
        print_info("Reading pricing configuration...")
        pricing_config = config_manager.get_pricing_config()
        print_success(f"Pricing config loaded")
        print(f"   Base seat price: {pricing_config.get('base_seat_price')} {pricing_config.get('currency')}")
        print(f"   Boat rental multiplier: {pricing_config.get('boat_rental_multiplier_skiff')}")
        
        # Test notification config
        print_info("Reading notification configuration...")
        notification_config = config_manager.get_notification_config()
        print_success(f"Notification config loaded")
        print(f"   Channels: {', '.join(notification_config.get('notification_channels', []))}")
        print(f"   Slack webhook configured: {'Yes' if notification_config.get('slack_webhook_admin') else 'No'}")
        
        return True
    except Exception as e:
        print_error(f"Configuration read failed: {str(e)}")
        return False


def test_helper_functions():
    """Test helper functions"""
    print_section("Test 2: Helper Functions")
    
    try:
        # Test registration status
        print_info("Checking registration status...")
        is_active = is_registration_active()
        print_success(f"Registration active: {is_active}")
        
        # Test base seat price
        print_info("Getting base seat price...")
        price = get_base_seat_price()
        print_success(f"Base seat price: {price}")
        
        # Test ID generation
        print_info("Generating IDs...")
        crew_id = generate_id('crew')
        boat_id = generate_id('boat')
        print_success(f"Generated crew ID: {crew_id}")
        print_success(f"Generated boat ID: {boat_id}")
        
        # Test timestamp
        print_info("Getting timestamp...")
        timestamp = get_timestamp()
        print_success(f"Timestamp: {timestamp}")
        
        return True
    except Exception as e:
        print_error(f"Helper functions failed: {str(e)}")
        return False


def test_database_read():
    """Test reading from DynamoDB"""
    print_section("Test 3: Database Read Operations")
    
    try:
        db = get_db_client()
        
        # Read configuration items
        print_info("Reading CONFIG items...")
        config_items = db.query_by_pk('CONFIG')
        print_success(f"Found {len(config_items)} configuration items")
        for item in config_items:
            print(f"   - {item.get('SK')}")
        
        # Read race definitions
        print_info("Reading RACE items...")
        race_items = db.query_by_pk('RACE', limit=10)
        print_success(f"Found {len(race_items)} races (showing first 10)")
        for item in race_items[:5]:
            print(f"   - {item.get('SK')}: {item.get('name')}")
        
        # Test get_item
        print_info("Testing get_item...")
        system_config = db.get_item('CONFIG', 'SYSTEM')
        if system_config:
            print_success(f"Retrieved SYSTEM config")
        else:
            print_error("SYSTEM config not found")
            return False
        
        return True
    except Exception as e:
        print_error(f"Database read failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_database_write():
    """Test writing to DynamoDB"""
    print_section("Test 4: Database Write Operations")
    
    try:
        db = get_db_client()
        
        # Create a test item
        test_id = generate_id('test')
        test_item = {
            'PK': 'TEST',
            'SK': test_id,
            'test_data': 'This is a test item',
            'created_at': get_timestamp(),
            'test_number': Decimal('42.5')
        }
        
        print_info(f"Writing test item: TEST#{test_id}")
        db.put_item(test_item)
        print_success("Test item written")
        
        # Read it back
        print_info("Reading test item back...")
        retrieved_item = db.get_item('TEST', test_id)
        if retrieved_item:
            print_success("Test item retrieved")
            print(f"   Data: {retrieved_item.get('test_data')}")
            print(f"   Number: {retrieved_item.get('test_number')}")
        else:
            print_error("Failed to retrieve test item")
            return False
        
        # Update the item
        print_info("Updating test item...")
        updated_item = db.update_item('TEST', test_id, {
            'test_data': 'Updated test data',
            'updated_at': get_timestamp()
        })
        print_success("Test item updated")
        print(f"   New data: {updated_item.get('test_data')}")
        
        # Delete the item
        print_info("Deleting test item...")
        db.delete_item('TEST', test_id)
        print_success("Test item deleted")
        
        # Verify deletion
        print_info("Verifying deletion...")
        deleted_item = db.get_item('TEST', test_id)
        if deleted_item is None:
            print_success("Test item successfully deleted")
        else:
            print_error("Test item still exists!")
            return False
        
        return True
    except Exception as e:
        print_error(f"Database write failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_validation():
    """Test validation functions"""
    print_section("Test 5: Validation")
    
    try:
        # Valid crew member
        print_info("Testing valid crew member...")
        valid_crew = {
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'date_of_birth': '1990-05-15',
            'gender': 'M',
            'license_number': 'ABC123456',
            'club_affiliation': 'RCPM'
        }
        
        is_valid, errors = validate_crew_member(valid_crew)
        if is_valid:
            print_success("Valid crew member passed validation")
        else:
            print_error(f"Valid crew member failed: {errors}")
            return False
        
        # Invalid crew member
        print_info("Testing invalid crew member...")
        invalid_crew = {
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'date_of_birth': 'invalid-date',
            'gender': 'X',  # Invalid gender
            'license_number': '123'  # Too short
        }
        
        is_valid, errors = validate_crew_member(invalid_crew)
        if not is_valid:
            print_success(f"Invalid crew member correctly rejected")
            print(f"   Errors: {list(errors.keys())}")
        else:
            print_error("Invalid crew member passed validation!")
            return False
        
        # Test sanitization
        print_info("Testing sanitization...")
        dirty_data = {
            'first_name': '  Jean  ',
            'last_name': 'Dupont\x00\x01',  # Null bytes
            'notes': 'A' * 200  # Long string
        }
        
        clean_data = sanitize_dict(dirty_data)
        print_success("Data sanitized")
        print(f"   First name: '{clean_data['first_name']}'")
        print(f"   Last name: '{clean_data['last_name']}'")
        
        return True
    except Exception as e:
        print_error(f"Validation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_crew_member_workflow():
    """Test complete crew member workflow"""
    print_section("Test 6: Crew Member Workflow")
    
    try:
        db = get_db_client()
        user_id = 'test-user-123'
        
        # Create crew member
        crew_id = generate_id('crew')
        crew_data = {
            'first_name': 'Marie',
            'last_name': 'Martin',
            'date_of_birth': '1995-03-20',
            'gender': 'F',
            'license_number': 'XYZ789012',
            'club_affiliation': 'RCPM',
            'is_rcpm_member': True
        }
        
        print_info("Validating crew member data...")
        is_valid, errors = validate_crew_member(crew_data)
        if not is_valid:
            print_error(f"Validation failed: {errors}")
            return False
        print_success("Crew member data valid")
        
        print_info(f"Creating crew member: {crew_id}")
        crew_item = {
            'PK': f'USER#{user_id}',
            'SK': f'CREW#{crew_id}',
            **crew_data,
            'created_at': get_timestamp(),
            'updated_at': get_timestamp()
        }
        db.put_item(crew_item)
        print_success("Crew member created")
        
        # Read crew member
        print_info("Reading crew member...")
        retrieved_crew = db.get_item(f'USER#{user_id}', f'CREW#{crew_id}')
        if retrieved_crew:
            print_success(f"Crew member retrieved: {retrieved_crew['first_name']} {retrieved_crew['last_name']}")
        else:
            print_error("Failed to retrieve crew member")
            return False
        
        # Update crew member
        print_info("Updating crew member...")
        updated_crew = db.update_item(
            f'USER#{user_id}',
            f'CREW#{crew_id}',
            {
                'license_number': 'NEW123456',
                'updated_at': get_timestamp()
            }
        )
        print_success(f"Crew member updated: new license = {updated_crew['license_number']}")
        
        # List all crew members for user
        print_info("Listing all crew members for user...")
        all_crew = db.query_by_pk(f'USER#{user_id}', sk_prefix='CREW#')
        print_success(f"Found {len(all_crew)} crew member(s)")
        
        # Delete crew member
        print_info("Deleting crew member...")
        db.delete_item(f'USER#{user_id}', f'CREW#{crew_id}')
        print_success("Crew member deleted")
        
        # Verify deletion
        deleted_crew = db.get_item(f'USER#{user_id}', f'CREW#{crew_id}')
        if deleted_crew is None:
            print_success("Crew member successfully removed")
        else:
            print_error("Crew member still exists!")
            return False
        
        return True
    except Exception as e:
        print_error(f"Crew member workflow failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  Live Database Test Suite")
    print("  Environment: dev")
    print(f"  Table: {os.environ.get('TABLE_NAME', 'impressionnistes-registration-dev')}")
    print("="*60)
    
    # Set table name if not set
    if 'TABLE_NAME' not in os.environ:
        os.environ['TABLE_NAME'] = 'impressionnistes-registration-dev'
        print_info(f"Using default table: {os.environ['TABLE_NAME']}")
    
    results = []
    
    # Run tests
    results.append(("Configuration Read", test_configuration_read()))
    results.append(("Helper Functions", test_helper_functions()))
    results.append(("Database Read", test_database_read()))
    results.append(("Database Write", test_database_write()))
    results.append(("Validation", test_validation()))
    results.append(("Crew Member Workflow", test_crew_member_workflow()))
    
    # Summary
    print_section("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
