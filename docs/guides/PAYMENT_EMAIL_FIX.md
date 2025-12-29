# Payment Confirmation Email Fix

## Problem
Stripe's `receipt_email` parameter doesn't send emails in test mode, and even in live mode, it's not always reliable.

## Solution
Implemented custom confirmation emails using AWS SES that are sent immediately after successful payment.

## What Changed

### 1. New Email Utility (Centralized)
**File:** `functions/shared/email_utils.py`

- Centralized email sending logic (follows code reusability rule)
- Can be reused across all Lambda functions
- Sends branded confirmation emails with payment details
- Includes boat registrations, rental details, and Stripe receipt link
- Automatically copied to `functions/layer/python/` during build

### 2. Updated Webhook Handler
**File:** `functions/payment/confirm_payment_webhook.py`

- Now sends confirmation email after successful payment
- Fetches boat and rental details for email content
- Gets team manager name for personalization
- Logs email sending status

### 3. Added SES Permissions
**File:** `infrastructure/stacks/api_stack.py`

- Added `ses:SendEmail` and `ses:SendRawEmail` permissions to webhook Lambda
- Allows Lambda to send emails via AWS SES

## Setup Required

### Quick Setup (5 minutes)

1. **Verify sender email in AWS SES:**
   ```bash
   cd infrastructure
   make ses-verify-email EMAIL=course.impressionnistes@rcpm-aviron.fr
   ```
   Then click the verification link in your email.

2. **Update sender email in code:**
   Edit `functions/shared/email_utils.py` line 145:
   ```python
   Source='your-verified-email@yourdomain.com',
   ```

3. **Rebuild Lambda layer:**
   ```bash
   cd functions
   ./build-layer.sh
   ```

4. **Deploy:**
   ```bash
   cd infrastructure
   make deploy-dev
   ```

### Testing in Sandbox Mode

If SES is in sandbox mode (default), you must also verify recipient emails:

```bash
cd infrastructure
make ses-verify-email EMAIL=your-test-email@example.com
```

### Production Setup

For production, request SES production access:
1. Go to [AWS SES Console](https://console.aws.amazon.com/ses/)
2. Navigate to **Account dashboard**
3. Click **Request production access**
4. Fill out the form (usually approved in 24 hours)

See `docs/guides/SES_EMAIL_SETUP.md` for detailed instructions.

## Email Features

The confirmation email includes:
- ✅ Payment confirmation message
- ✅ Total amount paid
- ✅ List of boat registrations with race details
- ✅ List of rental boats
- ✅ Payment ID for reference
- ✅ Link to Stripe receipt
- ✅ Professional HTML formatting
- ✅ Plain text fallback

## Benefits

- **Works in test mode** - Unlike Stripe receipts
- **Immediate delivery** - Sent right after payment
- **Custom branding** - Matches your organization
- **Detailed information** - Includes all registration details
- **Reliable** - Full control over email delivery
- **Centralized** - Email logic can be reused for other notifications

## Monitoring

Check if emails are being sent:

```bash
# Check SES statistics
cd infrastructure
make ses-get-statistics
```

View Lambda logs in AWS CloudWatch console.

Look for log messages:
- `Payment confirmation email sent to {email}` ✅
- `Failed to send payment confirmation email: {error}` ❌

## Next Steps

1. Complete SES setup (verify sender email)
2. Update sender email in code
3. Rebuild and deploy
4. Test with a payment
5. Request production access for SES (if needed)

## Future Enhancements

You can now easily add more email notifications using the centralized `functions/shared/email_utils.py`:
- Registration confirmation (when boat is created)
- Reminder emails before the race
- Admin notifications
- Rental confirmation emails

The build script (`functions/build-layer.sh`) automatically copies all shared code to `layer/python/` during deployment.
