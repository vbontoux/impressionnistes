# AWS SES Email Setup Guide

This guide explains how to configure AWS Simple Email Service (SES) to send payment confirmation emails.

## Overview

The system now sends custom confirmation emails after successful payments instead of relying on Stripe's automatic receipts. This provides:

- **Immediate delivery** - Emails sent right after payment confirmation
- **Custom branding** - Emails match your organization's style
- **Detailed information** - Include boat registrations, rental details, and receipt links
- **Works in test mode** - Unlike Stripe receipts, works with test payments

## Prerequisites

- AWS account with SES access
- Domain or email address to send from
- Access to AWS Console or AWS CLI

## Setup Steps

### 1. Verify Your Sender Email Address

AWS SES requires you to verify the email address you'll send from.

**Option A: Via Makefile (Recommended)**

```bash
cd infrastructure
make ses-verify-email EMAIL=course.impressionnistes@rcpm-aviron.fr
```

Check your email inbox for verification link and click it.

**Option B: Via AWS Console**

1. Go to [AWS SES Console](https://console.aws.amazon.com/ses/)
2. Select **eu-west-1** (Paris) region (or your preferred region)
3. Navigate to **Verified identities**
4. Click **Create identity**
5. Select **Email address**
6. Enter your sender email (e.g., `course.impressionnistes@rcpm-aviron.fr`)
7. Click **Create identity**
8. Check your email inbox for verification link
9. Click the verification link

### 2. Update the Sender Email in Code

Edit `functions/shared/email_utils.py` and replace the sender email:

```python
# Change this line (around line 145):
Source='course.impressionnistes@rcpm-aviron.fr',  # Replace with your verified email

# To your verified email:
Source='your-verified-email@yourdomain.com',
```

### 3. Request Production Access (Optional)

By default, SES is in **sandbox mode**, which means:
- You can only send to verified email addresses
- Limited to 200 emails per day
- 1 email per second

For production use, request production access:

1. Go to [AWS SES Console](https://console.aws.amazon.com/ses/)
2. Navigate to **Account dashboard**
3. Click **Request production access**
4. Fill out the form:
   - **Mail type**: Transactional
   - **Website URL**: Your registration website
   - **Use case description**: "Sending payment confirmation emails for rowing race registrations"
   - **Compliance**: Explain how you handle bounces and complaints
5. Submit the request

AWS typically approves within 24 hours.

### 4. Verify Recipient Emails (Sandbox Mode Only)

If you're still in sandbox mode, you must verify recipient email addresses:

```bash
cd infrastructure
make ses-verify-email EMAIL=test-user@example.com
```

The recipient will receive a verification email.

### 5. Deploy the Changes

Rebuild the Lambda layer and deploy:

```bash
# Rebuild Lambda layer with new email_utils.py
cd functions
./build-layer.sh

# Deploy infrastructure with SES permissions
cd ../infrastructure
make deploy-dev
```

### 6. Test Email Sending

You can test email sending using the Makefile:

```bash
cd infrastructure
make test-email EMAIL=your-email@example.com
```

Or test through a payment in your application.

## Email Configuration

### Sender Email

The sender email is configured in `functions/shared/email_utils.py`:

```python
Source='course.impressionnistes@rcpm-aviron.fr'
```

**Best practices:**
- Use a `noreply@` address for transactional emails
- Ensure the domain matches your organization
- Verify the email address in SES before deploying

### Email Region

The SES client is configured for `eu-west-1` (Paris):

```python
_ses_client = boto3.client('ses', region_name='eu-west-1')
```

**To change region:**
1. Update `region_name` in `functions/shared/email_utils.py`
2. Verify your sender email in the new region
3. Rebuild layer and redeploy

### Email Template

The email template is defined in `send_payment_confirmation_email()` function.

**To customize:**
- Edit HTML in `html_body` variable
- Update styling in `<style>` section
- Modify text in `text_body` for plain-text version

## Monitoring

### Check Email Sending Statistics

```bash
cd infrastructure
make ses-get-statistics
```

### View Sending Quota

```bash
cd infrastructure
make ses-get-quota
```

### CloudWatch Logs

Email sending is logged in Lambda CloudWatch logs. Use AWS CLI or CloudWatch console to view logs.

Look for:
- `Payment confirmation email sent to {email}`
- `Failed to send payment confirmation email: {error}`

## Troubleshooting

### Email Not Received

**Check:**
1. Sender email is verified in SES
2. Recipient email is verified (if in sandbox mode)
3. CloudWatch logs for errors
4. Spam/junk folder
5. SES sending statistics for bounces

**Common issues:**
- `Email address is not verified` - Verify sender in SES
- `MessageRejected` - Recipient email not verified (sandbox mode)
- `AccessDenied` - Lambda doesn't have SES permissions

### Verify SES Permissions

Check Lambda IAM role has SES permissions in the AWS IAM console. Should include:
```json
{
  "Effect": "Allow",
  "Action": ["ses:SendEmail", "ses:SendRawEmail"],
  "Resource": "*"
}
```

### Test Email Utility Directly

Create a test Lambda function:

```python
from email_utils import send_test_email

def lambda_handler(event, context):
    result = send_test_email('your-email@example.com')
    return {'success': result}
```

### Check SES Bounce/Complaint Rates

High bounce or complaint rates can pause your sending. Check this in the AWS SES console under "Account dashboard".

## Production Checklist

Before going to production:

- [ ] Sender email verified in SES
- [ ] Production access requested and approved
- [ ] Email template tested and reviewed
- [ ] Sender email updated in `functions/shared/email_utils.py`
- [ ] Lambda layer rebuilt (runs `./build-layer.sh` to copy shared code)
- [ ] Infrastructure deployed with SES permissions
- [ ] Test payment completed successfully
- [ ] Confirmation email received
- [ ] Email content is correct (amounts, boat details, links)
- [ ] CloudWatch monitoring set up
- [ ] Bounce and complaint handling configured

## Cost

AWS SES pricing (as of 2024):
- **First 62,000 emails per month**: Free (if sent from EC2 or Lambda)
- **Additional emails**: $0.10 per 1,000 emails

For a typical race with 500 registrations, email costs are negligible.

## Support

If you encounter issues:
1. Check CloudWatch logs for detailed error messages
2. Verify SES configuration in AWS Console
3. Test with AWS CLI to isolate issues
4. Review AWS SES documentation: https://docs.aws.amazon.com/ses/

## Alternative: Use a Custom Domain

For better deliverability, use a custom domain:

1. Verify your domain in SES (not just email)
2. Add DNS records (DKIM, SPF, DMARC)
3. Update sender email to use your domain
4. This improves email deliverability and trust
