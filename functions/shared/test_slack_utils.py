#!/usr/bin/env python3
"""
Test script for Slack notification utilities
Tests all Slack notification functions with real webhook URLs from DynamoDB
"""
import sys
import os
import boto3
from decimal import Decimal

# Add shared directory to path for local testing
sys.path.insert(0, os.path.dirname(__file__))

from slack_utils import (
    notify_new_user_registration,
    notify_new_boat_registration,
    notify_payment_completed,
    notify_payment_failed,
    notify_system_error,
    set_webhook_urls
)
from secrets_manager import get_slack_admin_webhook, get_slack_devops_webhook


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def test_load_webhooks():
    """Test loading webhook URLs from AWS Secrets Manager"""
    print_header("Loading Slack Webhooks from AWS Secrets Manager")
    
    try:
        slack_webhook_admin = get_slack_admin_webhook()
        slack_webhook_devops = get_slack_devops_webhook()
        
        print(f"Admin webhook: {slack_webhook_admin[:50]}..." if slack_webhook_admin else "Admin webhook: NOT CONFIGURED")
        print(f"Devops webhook: {slack_webhook_devops[:50]}..." if slack_webhook_devops else "Devops webhook: NOT CONFIGURED")
        
        if not slack_webhook_admin:
            print("\n⚠️  WARNING: Admin webhook not configured in Secrets Manager")
            print("   Notifications will be skipped")
            return None, None
        
        print("✓ Webhooks loaded successfully")
        return slack_webhook_admin, slack_webhook_devops
        
    except Exception as e:
        print(f"✗ Failed to load webhooks: {e}")
        return None, None


def test_new_user_registration(admin_webhook, environment):
    """Test new user registration notification"""
    print_header("Testing New User Registration Notification")
    
    if not admin_webhook:
        print("⚠️  Skipping - webhook not configured")
        return False
    
    set_webhook_urls(admin_webhook=admin_webhook)
    
    print("Sending test notification...")
    print(f"  User: Test User")
    print(f"  Email: test@example.com")
    print(f"  Club: Test Rowing Club")
    print(f"  Environment: {environment}")
    
    result = notify_new_user_registration(
        user_name="Test User",
        user_email="test@example.com",
        club_name="Test Rowing Club",
        environment=environment
    )
    
    if result:
        print("✓ Notification sent successfully")
        return True
    else:
        print("✗ Failed to send notification")
        return False


def test_new_boat_registration(admin_webhook, environment):
    """Test new boat registration notification"""
    print_header("Testing New Boat Registration Notification")
    
    if not admin_webhook:
        print("⚠️  Skipping - webhook not configured")
        return False
    
    set_webhook_urls(admin_webhook=admin_webhook)
    
    print("Sending test notification...")
    print(f"  Boat: 21-001-05")
    print(f"  Event: 21km")
    print(f"  Boat Type: 8+")
    print(f"  Race: 21km - SM - 8+")
    print(f"  Team Manager: Test Manager")
    print(f"  Club: Test Rowing Club")
    print(f"  Status: incomplete")
    print(f"  Boat Request: Yes (with comment)")
    print(f"  Environment: {environment}")
    
    result = notify_new_boat_registration(
        boat_number="21-001-05",
        event_type="21km",
        boat_type="8+",
        race_name="21km - SM - 8+",
        team_manager_name="Test Manager",
        team_manager_email="manager@example.com",
        club_affiliation="Test Rowing Club",
        registration_status="incomplete",
        boat_request_enabled=True,
        boat_request_comment="We need a lightweight racing shell for our crew. Prefer carbon fiber if available.",
        environment=environment
    )
    
    if result:
        print("✓ Notification sent successfully")
        return True
    else:
        print("✗ Failed to send notification")
        return False


def test_payment_completed(admin_webhook, environment):
    """Test payment completed notification"""
    print_header("Testing Payment Completed Notification")
    
    if not admin_webhook:
        print("⚠️  Skipping - webhook not configured")
        return False
    
    set_webhook_urls(admin_webhook=admin_webhook)
    
    print("Sending test notification...")
    print(f"  User: Test Manager")
    print(f"  Email: manager@example.com")
    print(f"  Amount: 150.00 EUR")
    print(f"  Boats: 2")
    print(f"  Rentals: 1")
    print(f"  Environment: {environment}")
    
    result = notify_payment_completed(
        user_name="Test Manager",
        user_email="manager@example.com",
        amount=150.00,
        currency="EUR",
        boat_count=2,
        rental_count=1,
        payment_id="test_payment_123",
        environment=environment
    )
    
    if result:
        print("✓ Notification sent successfully")
        return True
    else:
        print("✗ Failed to send notification")
        return False


def test_payment_failed(admin_webhook, environment):
    """Test payment failed notification"""
    print_header("Testing Payment Failed Notification")
    
    if not admin_webhook:
        print("⚠️  Skipping - webhook not configured")
        return False
    
    set_webhook_urls(admin_webhook=admin_webhook)
    
    print("Sending test notification...")
    print(f"  User: Test Manager")
    print(f"  Email: manager@example.com")
    print(f"  Amount: 150.00 EUR")
    print(f"  Error: Card declined")
    print(f"  Environment: {environment}")
    
    result = notify_payment_failed(
        user_name="Test Manager",
        user_email="manager@example.com",
        amount=150.00,
        currency="EUR",
        error_message="Your card was declined",
        payment_id="test_payment_456",
        environment=environment
    )
    
    if result:
        print("✓ Notification sent successfully")
        return True
    else:
        print("✗ Failed to send notification")
        return False


def test_system_error(devops_webhook, environment):
    """Test system error notification"""
    print_header("Testing System Error Notification")
    
    if not devops_webhook:
        print("⚠️  Skipping - devops webhook not configured")
        return False
    
    set_webhook_urls(devops_webhook=devops_webhook)
    
    print("Sending test notification...")
    print(f"  Error Type: DatabaseError")
    print(f"  Function: test_lambda_function")
    print(f"  Environment: {environment}")
    
    result = notify_system_error(
        error_type="DatabaseError",
        error_message="Connection timeout after 30 seconds",
        function_name="test_lambda_function",
        additional_context={
            "table": "impressionnistes-registration-dev",
            "operation": "get_item"
        },
        environment=environment
    )
    
    if result:
        print("✓ Notification sent successfully")
        return True
    else:
        print("✗ Failed to send notification")
        return False


def main():
    """Run all Slack notification tests"""
    print_header("Slack Notification Test Script")
    
    # Get environment from environment variable or default to dev
    environment = os.environ.get('ENVIRONMENT', 'dev')
    print(f"Environment: {environment}")
    
    # Check AWS credentials
    try:
        boto3.client('sts').get_caller_identity()
        print("✓ AWS credentials configured")
    except Exception as e:
        print(f"✗ AWS credentials not configured: {e}")
        sys.exit(1)
    
    # Load webhooks from DynamoDB
    admin_webhook, devops_webhook = test_load_webhooks()
    
    if not admin_webhook and not devops_webhook:
        print("\n⚠️  No webhooks configured - cannot run tests")
        print("\nTo configure webhooks:")
        print("1. Add webhook URLs to infrastructure/secrets.dev.json or secrets.prod.json")
        print("2. Deploy secrets stack: cd infrastructure && make deploy-secrets ENV=dev")
        print("   (This will create/update secrets in AWS Secrets Manager)")
        sys.exit(1)
    
    # Run tests
    results = []
    
    # Test 1: New user registration
    results.append(("New User Registration", test_new_user_registration(admin_webhook, environment)))
    
    # Test 2: New boat registration
    results.append(("New Boat Registration", test_new_boat_registration(admin_webhook, environment)))
    
    # Test 3: Payment completed
    results.append(("Payment Completed", test_payment_completed(admin_webhook, environment)))
    
    # Test 4: Payment failed
    results.append(("Payment Failed", test_payment_failed(admin_webhook, environment)))
    
    # Test 5: System error (optional - uses devops webhook)
    if devops_webhook:
        results.append(("System Error", test_system_error(devops_webhook, environment)))
    
    # Print summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
