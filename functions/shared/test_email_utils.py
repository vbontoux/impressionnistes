"""
Local test script for email_utils
Tests email sending functionality before deployment

Usage:
    python test_email_utils.py your-email@example.com
    python test_email_utils.py your-email@example.com sender@aviron-rcpm.fr
"""
import sys
import os
from decimal import Decimal

# Add shared directory to path
sys.path.insert(0, os.path.dirname(__file__))

from email_utils import send_payment_confirmation_email, send_test_email


def test_simple_email(recipient_email, sender_email=None):
    """Test sending a simple test email"""
    print(f"\n=== Testing Simple Email ===")
    print(f"Sending test email to: {recipient_email}")
    if sender_email:
        print(f"From: {sender_email}")
    
    result = send_test_email(recipient_email, sender_email=sender_email)
    
    if result:
        print("✅ Test email sent successfully!")
        print("Check your inbox (and spam folder)")
    else:
        print("❌ Failed to send test email")
        print("Check the error messages above")
    
    return result


def test_payment_confirmation_email(recipient_email, sender_email=None):
    """Test sending a payment confirmation email with mock data"""
    print(f"\n=== Testing Payment Confirmation Email ===")
    print(f"Sending payment confirmation to: {recipient_email}")
    if sender_email:
        print(f"From: {sender_email}")
    
    # Mock payment details
    payment_details = {
        'payment_id': 'test-payment-123',
        'amount': Decimal('120.00'),
        'currency': 'EUR',
        'paid_at': '2024-12-29T10:00:00Z'
    }
    
    # Mock boat registrations
    boat_registrations = [
        {
            'boat_type': '4x+',
            'crew_name': 'Les Rameurs Rapides',
            'selected_race': {
                'race_name': 'Course Mixte 6km'
            }
        },
        {
            'boat_type': '8+',
            'crew_name': 'Équipe des Champions',
            'selected_race': {
                'race_name': 'Course Senior 6km'
            }
        }
    ]
    
    # Mock rental boats
    rental_boats = [
        {
            'boat_type': 'skiff',
            'boat_name': 'Skiff de location #1'
        }
    ]
    
    result = send_payment_confirmation_email(
        recipient_email=recipient_email,
        team_manager_name='Jean Dupont',
        payment_details=payment_details,
        boat_registrations=boat_registrations,
        rental_boats=rental_boats,
        receipt_url='https://stripe.com/receipt/test-receipt-url',
        sender_email=sender_email
    )
    
    if result:
        print("✅ Payment confirmation email sent successfully!")
        print("Check your inbox for a detailed confirmation email")
    else:
        print("❌ Failed to send payment confirmation email")
        print("Check the error messages above")
    
    return result


def main():
    """Main test function"""
    if len(sys.argv) < 2:
        print("Usage: python test_email_utils.py your-email@example.com [sender@aviron-rcpm.fr]")
        print("\nThis script tests email sending functionality locally.")
        print("\nParameters:")
        print("  recipient_email  - Email address to send test emails to (required)")
        print("  sender_email     - Email address to send from (optional, uses default if not provided)")
        print("\nMake sure you have:")
        print("  1. AWS credentials configured (aws configure)")
        print("  2. Verified sender email in SES")
        print("  3. Verified recipient email in SES (if in sandbox mode)")
        sys.exit(1)
    
    recipient_email = sys.argv[1]
    sender_email = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("=" * 60)
    print("Email Utils Test Script")
    print("=" * 60)
    print(f"Recipient: {recipient_email}")
    if sender_email:
        print(f"Sender: {sender_email}")
    else:
        print("Sender: Using default from email_utils.py")
    print("\nPrerequisites:")
    print("  ✓ AWS credentials configured")
    print("  ✓ Sender email verified in SES")
    print("  ✓ Recipient email verified (if sandbox mode)")
    print("=" * 60)
    
    # Test 1: Simple test email
    test1_result = test_simple_email(recipient_email, sender_email)
    
    if not test1_result:
        print("\n⚠️  Simple test failed. Fix issues before testing payment confirmation.")
        sys.exit(1)
    
    # Ask user if they want to continue
    print("\n" + "=" * 60)
    response = input("Continue with payment confirmation email test? (y/n): ")
    if response.lower() != 'y':
        print("Test stopped by user.")
        sys.exit(0)
    
    # Test 2: Payment confirmation email
    test2_result = test_payment_confirmation_email(recipient_email, sender_email)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Simple test email:           {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Payment confirmation email:  {'✅ PASS' if test2_result else '❌ FAIL'}")
    print("=" * 60)
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed! Email system is ready for deployment.")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")


if __name__ == '__main__':
    main()
