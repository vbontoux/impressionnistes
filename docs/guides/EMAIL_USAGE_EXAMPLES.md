# Email Utility Usage Examples

This guide shows how to use the centralized `email_utils.py` module for sending notifications throughout the application.

## Overview

The email utility is located in `functions/shared/email_utils.py` and provides reusable email functions for all Lambda functions.

**Benefits:**
- ✅ Centralized email logic (DRY principle)
- ✅ Consistent formatting across all emails
- ✅ Easy to maintain and update
- ✅ Proper error handling and logging
- ✅ Supports both HTML and plain text

## Available Email Functions

### 1. Payment Confirmation Email

**When to use:** After successful payment (already implemented in webhook)

**Example:**
```python
from email_utils import send_payment_confirmation_email

payment_details = {
    'payment_id': 'pay_123',
    'amount': Decimal('120.00'),
    'currency': 'EUR',
    'paid_at': '2024-12-29T10:00:00Z'
}

boat_registrations = [
    {
        'boat_type': '4x+',
        'crew_name': 'Les Rameurs',
        'selected_race': {'race_name': 'Course Mixte 6km'}
    }
]

rental_boats = [
    {
        'boat_type': 'skiff',
        'boat_name': 'Skiff #1'
    }
]

success = send_payment_confirmation_email(
    recipient_email='user@example.com',
    team_manager_name='Jean Dupont',
    payment_details=payment_details,
    boat_registrations=boat_registrations,
    rental_boats=rental_boats,
    receipt_url='https://stripe.com/receipt/xxx'
)

if success:
    logger.info("Payment confirmation sent")
else:
    logger.error("Failed to send payment confirmation")
```

### 2. Registration Confirmation Email

**When to use:** After a boat registration is created

**Implementation example:**

```python
# In functions/boat/create_boat_registration.py

from email_utils import send_registration_confirmation_email

@handle_exceptions
@require_team_manager
def lambda_handler(event, context):
    # ... existing boat creation logic ...
    
    # After boat is created successfully
    boat_details = {
        'boat_type': boat_type,
        'crew_name': crew_name,
        'selected_race': selected_race
    }
    
    # Get team manager details
    team_manager = db.get_item(pk=f'TEAM#{team_manager_id}', sk='METADATA')
    team_manager_name = f"{team_manager.get('first_name', '')} {team_manager.get('last_name', '')}".strip()
    team_manager_email = user.get('email')
    
    # Send confirmation email
    send_registration_confirmation_email(
        recipient_email=team_manager_email,
        team_manager_name=team_manager_name,
        boat_details=boat_details
    )
    
    return success_response(data=boat)
```

### 3. Race Reminder Email

**When to use:** 1-2 days before the race (scheduled Lambda or manual trigger)

**Implementation example:**

```python
# Create new function: functions/notifications/send_race_reminders.py

from email_utils import send_race_reminder_email
from database import get_db_client

def lambda_handler(event, context):
    """
    Send race reminder emails to all registered teams
    Triggered by EventBridge schedule (e.g., 2 days before race)
    """
    db = get_db_client()
    
    # Get all teams with paid boats
    # (Implementation depends on your data structure)
    teams = get_teams_with_paid_boats(db)
    
    race_details = {
        'date': '15 juin 2025',
        'time': '9h00',
        'location': 'Base nautique de Chatou'
    }
    
    for team in teams:
        team_manager_email = team.get('email')
        team_manager_name = f"{team.get('first_name', '')} {team.get('last_name', '')}".strip()
        boats = team.get('boats', [])
        
        success = send_race_reminder_email(
            recipient_email=team_manager_email,
            team_manager_name=team_manager_name,
            race_details=race_details,
            boats=boats
        )
        
        if success:
            logger.info(f"Reminder sent to {team_manager_email}")
        else:
            logger.error(f"Failed to send reminder to {team_manager_email}")
    
    return {'statusCode': 200, 'body': 'Reminders sent'}
```

### 4. Rental Confirmation Email

**When to use:** After admin confirms a rental boat request

**Implementation example:**

```python
# In functions/rental/confirm_rental.py (or admin function)

from email_utils import send_rental_confirmation_email

@handle_exceptions
@require_admin  # Only admins can confirm rentals
def lambda_handler(event, context):
    # ... existing rental confirmation logic ...
    
    # After rental is confirmed
    rental_details = {
        'boat_type': rental.get('boat_type'),
        'boat_name': rental.get('boat_name'),
        'status': 'confirmed'
    }
    
    # Get requester details
    requester_email = rental.get('requester')
    requester_name = rental.get('requester_name', 'Cher membre')
    
    # Send confirmation email
    send_rental_confirmation_email(
        recipient_email=requester_email,
        team_manager_name=requester_name,
        rental_details=rental_details
    )
    
    return success_response(data=rental)
```

## Adding New Email Types

To add a new email notification, follow this pattern:

### Step 1: Add Function to email_utils.py

```python
def send_your_notification_email(
    recipient_email: str,
    team_manager_name: str,
    details: Dict[str, Any]
) -> bool:
    """
    Send your notification email
    
    Args:
        recipient_email: Email address of the recipient
        team_manager_name: Name for personalization
        details: Dict with notification-specific data
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        ses = get_ses_client()
        
        # Extract details
        field1 = details.get('field1', 'N/A')
        field2 = details.get('field2', 'N/A')
        
        subject = "Your Subject - Course des Impressionnistes"
        
        # HTML version
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0066cc; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Your Title</h1>
                </div>
                <div class="content">
                    <p>Bonjour {team_manager_name},</p>
                    
                    <p>Your message content here.</p>
                    
                    <ul>
                        <li><strong>Field 1:</strong> {field1}</li>
                        <li><strong>Field 2:</strong> {field2}</li>
                    </ul>
                    
                    <p>Closing message.</p>
                    
                    <p>L'équipe de la Course des Impressionnistes</p>
                </div>
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement. Merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
Your Title - Course des Impressionnistes

Bonjour {team_manager_name},

Your message content here.

Field 1: {field1}
Field 2: {field2}

Closing message.

L'équipe de la Course des Impressionnistes
        """
        
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
        
        logger.info(f"Your notification email sent to {recipient_email}, MessageId: {response['MessageId']}")
        return True
        
    except ClientError as e:
        logger.error(f"Failed to send your notification email: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending your notification: {str(e)}")
        return False
```

### Step 2: Import and Use in Lambda Function

```python
from email_utils import send_your_notification_email

# In your Lambda handler
success = send_your_notification_email(
    recipient_email='user@example.com',
    team_manager_name='Jean Dupont',
    details={'field1': 'value1', 'field2': 'value2'}
)

if not success:
    logger.warning("Failed to send notification email")
    # Don't fail the request, just log the warning
```

### Step 3: Test Locally

```python
# Add test to test_email_utils.py
def test_your_notification_email(recipient_email):
    details = {
        'field1': 'test value 1',
        'field2': 'test value 2'
    }
    
    result = send_your_notification_email(
        recipient_email=recipient_email,
        team_manager_name='Test User',
        details=details
    )
    
    return result
```

### Step 4: Rebuild and Deploy

```bash
cd functions
./build-layer.sh

cd ../infrastructure
make deploy-dev
```

## Best Practices

### 1. Always Handle Failures Gracefully

```python
# ✅ Good: Log warning but don't fail the request
success = send_email(...)
if not success:
    logger.warning("Email failed but continuing")

# ❌ Bad: Fail the entire request if email fails
send_email(...)  # Raises exception if fails
```

### 2. Get Recipient Details from Database

```python
# Get team manager details
team_manager = db.get_item(pk=f'TEAM#{team_manager_id}', sk='METADATA')
team_manager_name = f"{team_manager.get('first_name', '')} {team_manager.get('last_name', '')}".strip()
team_manager_email = user.get('email')  # From Cognito token
```

### 3. Use Consistent Styling

All emails use the same CSS styling for consistency. Copy the style block from existing email functions.

### 4. Always Provide Plain Text Version

Some email clients don't support HTML. Always include a plain text version.

### 5. Log Email Sending

```python
if success:
    logger.info(f"Email sent to {recipient_email}")
else:
    logger.error(f"Failed to send email to {recipient_email}")
```

### 6. Test Before Deploying

Always test new email functions locally using `test_email_utils.py`.

## Common Use Cases

### Send Email After Database Update

```python
# Update database
db.put_item(item)

# Send notification
send_email(...)
```

### Send Email in Webhook Handler

```python
def handle_webhook_event(event_data, db):
    # Process event
    # ...
    
    # Send notification
    send_email(...)
```

### Send Bulk Emails (Scheduled)

```python
def lambda_handler(event, context):
    """Scheduled Lambda to send bulk emails"""
    db = get_db_client()
    
    # Get all recipients
    recipients = get_recipients(db)
    
    # Send to each
    for recipient in recipients:
        send_email(
            recipient_email=recipient['email'],
            team_manager_name=recipient['name'],
            details=recipient['details']
        )
```

## Monitoring

### CloudWatch Logs

Check Lambda logs for email sending:

```bash
aws logs tail /aws/lambda/YourLambdaFunction --follow
```

Look for:
- `Email sent to {email}, MessageId: {id}` ✅
- `Failed to send email: {error}` ❌

### SES Statistics

Check SES sending statistics:

```bash
cd infrastructure
make ses-get-statistics
```

### SES Quota

Check your sending quota:

```bash
cd infrastructure
make ses-get-quota
```

## Troubleshooting

### Email Not Sent

1. Check CloudWatch logs for errors
2. Verify sender email is verified in SES
3. Verify recipient email (if sandbox mode)
4. Check Lambda has SES permissions
5. Check SES sending quota

### Email in Spam

1. Request SES production access
2. Set up SPF/DKIM records
3. Use a verified domain (not just email)
4. Avoid spam trigger words

### HTML Not Rendering

1. Test in multiple email clients
2. Use inline CSS (not external)
3. Keep HTML simple
4. Always provide plain text fallback

## Summary

The centralized `email_utils.py` module makes it easy to add email notifications throughout your application:

1. ✅ All email logic in one place
2. ✅ Consistent formatting and styling
3. ✅ Easy to test locally
4. ✅ Proper error handling
5. ✅ Reusable across all Lambda functions

Just import the function you need and call it with the appropriate data!
