# Email Testing Guide

This guide shows how to test the email notification system locally before deployment.

## Prerequisites

1. **AWS CLI configured** with credentials:
   ```bash
   aws configure
   ```

2. **Sender email verified in SES:**
   ```bash
   cd infrastructure
   make ses-verify-email EMAIL=course.impressionnistes@rcpm-aviron.fr
   ```
   Check your email and click the verification link.

3. **Recipient email verified** (if SES is in sandbox mode):
   ```bash
   cd infrastructure
   make ses-verify-email EMAIL=your-test-email@example.com
   ```

4. **Python dependencies installed:**
   ```bash
   cd infrastructure
   make test-setup
   ```

## Running the Test Script

The test script sends two types of emails:
1. Simple test email (to verify basic functionality)
2. Payment confirmation email (with mock data)

### Basic Test

```bash
cd infrastructure
make test-email EMAIL=your-email@example.com
```

This uses the infrastructure venv and runs the test properly.

### For Production Environment

```bash
cd infrastructure
make test-email EMAIL=your-email@example.com ENV=prod
```

### What the Test Does

1. **Simple Test Email:**
   - Sends a basic test message
   - Verifies SES connectivity
   - Checks sender/recipient verification

2. **Payment Confirmation Email:**
   - Sends a full payment confirmation with mock data
   - Tests HTML formatting
   - Includes boat registrations and rental details
   - Tests receipt URL linking

### Expected Output

```
============================================================
Email Utils Test Script
============================================================
Recipient: your-email@example.com

Prerequisites:
  ✓ AWS credentials configured
  ✓ Sender email verified in SES
  ✓ Recipient email verified (if sandbox mode)
============================================================

=== Testing Simple Email ===
Sending test email to: your-email@example.com
✅ Test email sent successfully!
Check your inbox (and spam folder)

============================================================
Continue with payment confirmation email test? (y/n): y

=== Testing Payment Confirmation Email ===
Sending payment confirmation to: your-email@example.com
✅ Payment confirmation email sent successfully!
Check your inbox for a detailed confirmation email

============================================================
Test Summary
============================================================
Simple test email:           ✅ PASS
Payment confirmation email:  ✅ PASS
============================================================

🎉 All tests passed! Email system is ready for deployment.
```

## Troubleshooting

### Error: "Email address is not verified"

**Problem:** Sender email not verified in SES

**Solution:**
```bash
cd infrastructure
make ses-verify-email EMAIL=course.impressionnistes@rcpm-aviron.fr
```
Then click the verification link in your email.

### Error: "MessageRejected"

**Problem:** Recipient email not verified (sandbox mode)

**Solution:**
```bash
cd infrastructure
make ses-verify-email EMAIL=your-test-email@example.com
```

### Error: "AccessDenied"

**Problem:** AWS credentials don't have SES permissions

**Solution:** Add SES permissions to your IAM user:
```json
{
  "Effect": "Allow",
  "Action": ["ses:SendEmail", "ses:SendRawEmail"],
  "Resource": "*"
}
```

### Error: "Could not connect to the endpoint URL"

**Problem:** Wrong region or SES not available

**Solution:** Verify region in `email_utils.py`:
```python
_ses_client = boto3.client('ses', region_name='eu-west-1')
```

### Email Not Received

**Check:**
1. Spam/junk folder
2. SES sending statistics: `cd infrastructure && make ses-get-statistics`
3. CloudWatch logs (after deployment)
4. Verify both sender and recipient emails: `make ses-list-verified`

## Testing Individual Email Functions

You can also test individual email functions:

### Test Registration Confirmation

```python
from email_utils import send_registration_confirmation_email

boat_details = {
    'boat_type': '4x+',
    'crew_name': 'Les Rameurs',
    'selected_race': {'race_name': 'Course Mixte 6km'}
}

send_registration_confirmation_email(
    recipient_email='test@example.com',
    team_manager_name='Jean Dupont',
    boat_details=boat_details
)
```

### Test Race Reminder

```python
from email_utils import send_race_reminder_email

race_details = {
    'date': '15 juin 2025',
    'time': '9h00',
    'location': 'Base nautique de Chatou'
}

boats = [
    {'boat_type': '4x+', 'crew_name': 'Équipe A'},
    {'boat_type': '8+', 'crew_name': 'Équipe B'}
]

send_race_reminder_email(
    recipient_email='test@example.com',
    team_manager_name='Jean Dupont',
    race_details=race_details,
    boats=boats
)
```

### Test Rental Confirmation

```python
from email_utils import send_rental_confirmation_email

rental_details = {
    'boat_type': 'skiff',
    'boat_name': 'Skiff #1',
    'status': 'confirmed'
}

send_rental_confirmation_email(
    recipient_email='test@example.com',
    team_manager_name='Jean Dupont',
    rental_details=rental_details
)
```

## Verifying Email Content

After sending test emails, verify:

- ✅ Subject line is correct
- ✅ Recipient name is personalized
- ✅ HTML formatting displays correctly
- ✅ All data fields are populated
- ✅ Links work (receipt URL, etc.)
- ✅ Plain text version is readable
- ✅ French accents display correctly (é, è, à, etc.)

## Production Readiness Checklist

Before deploying to production:

- [ ] All test emails sent successfully
- [ ] HTML formatting verified in multiple email clients
- [ ] Sender email updated to production domain
- [ ] SES production access requested (if needed)
- [ ] Email content reviewed and approved
- [ ] French text verified for grammar/spelling
- [ ] Links tested and working
- [ ] Unsubscribe mechanism considered (if needed)

## Next Steps

Once local testing passes:

1. Update sender email in `functions/shared/email_utils.py`
2. Rebuild Lambda layer: `cd functions && ./build-layer.sh`
3. Deploy: `cd infrastructure && make deploy-dev`
4. Test with real payment in dev environment
5. Monitor CloudWatch logs for email sending
6. Deploy to production when ready

## Available Email Functions

The `email_utils.py` module provides these functions:

| Function | Purpose | When to Use |
|----------|---------|-------------|
| `send_payment_confirmation_email()` | Payment success | After successful payment webhook |
| `send_registration_confirmation_email()` | Boat registered | After boat registration created |
| `send_race_reminder_email()` | Race reminder | 1-2 days before race |
| `send_rental_confirmation_email()` | Rental confirmed | After rental boat confirmed |
| `send_test_email()` | Basic test | Testing SES configuration |

All functions follow the same pattern:
- Return `True` on success, `False` on failure
- Log detailed information
- Handle errors gracefully
- Support both HTML and plain text

## Future Email Notifications

You can easily add more notifications by following the same pattern in `email_utils.py`:

```python
def send_your_notification_email(
    recipient_email: str,
    team_manager_name: str,
    details: Dict[str, Any]
) -> bool:
    """
    Your email description
    """
    try:
        ses = get_ses_client()
        
        # Build email content
        subject = "Your Subject"
        html_body = """..."""
        text_body = """..."""
        
        # Send email
        response = ses.send_email(
            Source='course.impressionnistes@rcpm-aviron.fr',
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                    'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                }
            }
        )
        
        logger.info(f"Email sent to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False
```

## Support

If you encounter issues:
1. Run the test script with verbose output
2. Check AWS SES console for sending statistics
3. Verify email addresses are verified
4. Review error messages in the output
5. Check AWS IAM permissions
