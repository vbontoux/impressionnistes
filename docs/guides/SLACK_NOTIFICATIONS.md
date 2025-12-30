# Slack Notifications Setup

## Overview

The system sends Slack notifications for key business events:
1. **New Team Manager Registration** - When a new user creates an account
2. **Payment Completed** - When a payment succeeds
3. **Payment Failed** - When a payment fails

## Setup

### 1. Create Slack Incoming Webhooks

1. Go to your Slack workspace
2. Navigate to **Apps** → **Incoming Webhooks**
3. Click **Add to Slack**
4. Choose the channel for notifications (e.g., `#registrations` or `#payments`)
5. Copy the webhook URL

You can create separate webhooks for:
- **Admin notifications** (registrations, payments) → `slack_webhook_admin`
- **DevOps notifications** (system errors) → `slack_webhook_devops`

### 2. Add Webhook URLs to Configuration

The webhook URLs are stored in the `NOTIFICATION` configuration in DynamoDB.

#### Option A: Via Admin Panel (Recommended)
1. Log in as admin
2. Go to **Event Configuration**
3. Find the Slack webhook fields
4. Paste your webhook URLs
5. Save

#### Option B: Via Database
Update the `CONFIG#NOTIFICATION` record in DynamoDB:

```json
{
  "PK": "CONFIG",
  "SK": "NOTIFICATION",
  "slack_webhook_admin": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  "slack_webhook_devops": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
}
```

### 3. Deploy

After adding the webhook URLs, rebuild and deploy:

```bash
cd functions && ./build-layer.sh
cd ../infrastructure && make deploy-dev
```

## Notification Examples

### New Team Manager Registration

```
🔵 New Team Manager Registration

Name: Jean Dupont
Email: jean.dupont@example.com
Club: Rowing Club Paris

Environment: dev
```

### Payment Completed

```
🔵 💰 Payment Completed

Team Manager: Jean Dupont
Amount: 120.00 EUR
Email: jean.dupont@example.com
Items: 2 boats + 1 rental

Payment ID: pi_abc123 | Environment: dev
```

### Payment Failed

```
🔵 ❌ Payment Failed

Team Manager: Jean Dupont
Amount: 120.00 EUR
Email: jean.dupont@example.com
Error: Your card was declined

Payment ID: pi_abc123 | Environment: dev
```

## Environment Indicators

- 🟢 = Production
- 🔵 = Development

## Testing

### Test Slack Notifications Locally

You can test the Slack notification utility:

```python
from slack_utils import notify_new_user_registration, set_webhook_urls

# Set your test webhook
set_webhook_urls(admin_webhook='https://hooks.slack.com/services/YOUR/TEST/WEBHOOK')

# Test notification
notify_new_user_registration(
    user_name='Test User',
    user_email='test@example.com',
    club_name='Test Club',
    environment='dev'
)
```

### Test in Dev Environment

1. Register a new user in dev
2. Complete a payment in dev
3. Check your Slack channel for notifications

## Disabling Notifications

To disable Slack notifications:
1. Remove the webhook URLs from the configuration
2. Or set them to empty strings

The system will log a warning but continue to function normally.

## Troubleshooting

### Notifications Not Appearing

1. **Check webhook URL is configured:**
   - Query the `CONFIG#NOTIFICATION` record in DynamoDB
   - Verify `slack_webhook_admin` is set

2. **Check CloudWatch logs:**
   ```bash
   # For registration notifications
   aws logs tail /aws/lambda/ImpressionnistesApi-dev-RegisterFunction --follow
   
   # For payment notifications
   aws logs tail /aws/lambda/ImpressionnistesApi-dev-ConfirmPaymentWebhookFunction --follow
   ```

3. **Verify webhook URL is valid:**
   - Test the webhook URL with curl:
   ```bash
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test message"}' \
     YOUR_WEBHOOK_URL
   ```

4. **Check Slack app permissions:**
   - Ensure the Incoming Webhook app is installed
   - Verify the webhook hasn't been revoked

### Notifications Going to Wrong Channel

- Each webhook URL is tied to a specific channel
- Create a new webhook for a different channel
- Update the configuration with the new webhook URL

## Available Notification Functions

The `slack_utils.py` module provides these functions:

| Function | Purpose | When Called |
|----------|---------|-------------|
| `notify_new_user_registration()` | New user signup | After user profile created |
| `notify_payment_completed()` | Successful payment | After payment confirmed |
| `notify_payment_failed()` | Failed payment | When payment fails |
| `notify_system_error()` | System errors | On critical errors (future) |

## Adding More Notifications

To add new notifications:

1. **Add function to `slack_utils.py`:**
   ```python
   def notify_your_event(param1, param2, environment='dev'):
       message = {
           "blocks": [
               {
                   "type": "header",
                   "text": {
                       "type": "plain_text",
                       "text": "Your Event Title"
                   }
               },
               # Add more blocks...
           ]
       }
       return send_slack_message(_slack_webhook_admin, message)
   ```

2. **Call from your Lambda function:**
   ```python
   from slack_utils import notify_your_event, set_webhook_urls
   from configuration_manager import ConfigurationManager
   
   config_manager = ConfigurationManager()
   notification_config = config_manager.get_notification_config()
   slack_webhook = notification_config.get('slack_webhook_admin', '')
   
   if slack_webhook:
       set_webhook_urls(admin_webhook=slack_webhook)
       notify_your_event(param1, param2, environment='dev')
   ```

3. **Rebuild and deploy:**
   ```bash
   cd functions && ./build-layer.sh
   cd ../infrastructure && make deploy-dev
   ```

## Slack Block Kit

Notifications use [Slack Block Kit](https://api.slack.com/block-kit) for rich formatting.

Use the [Block Kit Builder](https://app.slack.com/block-kit-builder) to design custom messages.

## Security

- **Never commit webhook URLs to git**
- Store webhooks in DynamoDB configuration
- Use separate webhooks for dev and prod
- Rotate webhooks if compromised

## Cost

Slack Incoming Webhooks are free for all Slack plans.

## Support

If notifications aren't working:
1. Check CloudWatch logs for errors
2. Verify webhook URL in configuration
3. Test webhook URL with curl
4. Check Slack app is installed and active
