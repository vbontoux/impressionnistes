# Payment Testing Guide

This guide explains how to test the Stripe payment integration in the Course des Impressionnistes registration system.

## Prerequisites

Before testing payments, ensure you have:

1. **Stripe Account** (Test Mode)
   - Sign up at https://stripe.com
   - Use test mode (API keys start with `sk_test_` and `pk_test_`)

2. **Backend Deployed**
   - Secrets deployed: `cd infrastructure && make deploy-secrets`
   - Infrastructure deployed: `make deploy-dev`
   - Lambda layer built with Stripe: `cd ../functions && ./build-layer.sh`

3. **Frontend Configuration**
   - Copy `.env.example` to `.env`
   - Add your Stripe publishable key

## Setup

### 1. Get Stripe Keys

1. Log in to [Stripe Dashboard](https://dashboard.stripe.com/test/dashboard)
2. Go to **Developers** → **API keys**
3. Copy your **Publishable key** (starts with `pk_test_`)
4. Copy your **Secret key** (starts with `sk_test_`)

### 2. Configure Backend

Update secrets with your Stripe keys:

```bash
cd infrastructure
make secrets-update-stripe \
  STRIPE_API_KEY=sk_test_YOUR_SECRET_KEY \
  STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET
```

### 3. Configure Frontend

Create `frontend/.env` file:

```bash
cd frontend
cp .env.example .env
```

Edit `.env` and add your Stripe publishable key:

```env
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY
```

### 4. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

## Test Payment Flow

### Step 1: Create Boat Registrations

1. Log in to the application
2. Go to **Crew Members** and add crew members
3. Go to **Boats** and create boat registrations
4. Assign crew members to seats
5. Select a race
6. Ensure boat status is "Complete"

### Step 2: Navigate to Payment

1. Click **Payment** in the navigation
2. You should see your completed boats
3. Select boats to pay for
4. Click **Proceed to Payment**

### Step 3: Enter Payment Details

Use these **test card numbers**:

#### ✅ Successful Payment
```
Card Number: 4242 4242 4242 4242
Expiry: 12/25 (any future date)
CVC: 123 (any 3 digits)
ZIP: 12345 (any 5 digits)
```

#### 🔐 3D Secure Authentication
```
Card Number: 4000 0025 0000 3155
Expiry: 12/25
CVC: 123
ZIP: 12345
```
This will trigger a 3D Secure authentication popup.

#### ❌ Declined Payment
```
Card Number: 4000 0000 0000 9995
Expiry: 12/25
CVC: 123
ZIP: 12345
```
This will simulate a declined payment.

### Step 4: Complete Payment

1. Enter test card details
2. Click **Pay [Amount]**
3. Wait for processing
4. You should be redirected to success page

### Step 5: Verify Payment

**In the Application:**
- Go to **Boats** page
- Boats should now show "Paid" status
- Payment date should be displayed

**In Stripe Dashboard:**
- Go to https://dashboard.stripe.com/test/payments
- You should see your test payment
- Click on it to see details

**In Database:**
- Payment record created in DynamoDB
- Boat status updated to "paid"
- Pricing locked

## Webhook Testing

### Local Webhook Testing with Stripe CLI

1. **Install Stripe CLI**
   ```bash
   brew install stripe/stripe-cli/stripe
   ```

2. **Login to Stripe**
   ```bash
   stripe login
   ```

3. **Forward Webhooks**
   ```bash
   stripe listen --forward-to https://YOUR_API_URL/dev/payment/webhook
   ```

4. **Trigger Test Events**
   ```bash
   stripe trigger payment_intent.succeeded
   stripe trigger payment_intent.payment_failed
   ```

### Production Webhook Setup

1. Go to **Developers** → **Webhooks** in Stripe Dashboard
2. Click **Add endpoint**
3. Enter webhook URL: `https://YOUR_API_URL/dev/payment/webhook`
4. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
5. Copy the signing secret
6. Update secrets: `make secrets-update-stripe STRIPE_WEBHOOK_SECRET=whsec_xxx`

## Troubleshooting

### Payment Intent Creation Fails

**Check:**
- Backend is deployed: `make describe-infra`
- Secrets are set: `make secrets-show-stripe`
- Lambda has Secrets Manager permissions
- CloudWatch logs: Check Lambda function logs

**Common Issues:**
- Invalid Stripe API key
- Boat not in "complete" status
- Boat doesn't belong to user

### Stripe.js Fails to Load

**Check:**
- Publishable key is set in `.env`
- Key starts with `pk_test_` (not `sk_test_`)
- No browser console errors
- Internet connection

**Fix:**
```bash
# Verify .env file
cat frontend/.env | grep STRIPE

# Restart dev server
npm run dev
```

### Card Element Not Showing

**Check:**
- Stripe.js loaded successfully
- No JavaScript errors in console
- Element container exists in DOM

**Debug:**
```javascript
// In browser console
console.log(window.Stripe)
```

### Payment Succeeds but Boat Status Not Updated

**Check:**
- Webhook is configured correctly
- Webhook secret is correct
- CloudWatch logs for webhook Lambda
- DynamoDB for payment record

**Verify Webhook:**
```bash
# Check webhook events in Stripe Dashboard
# Developers → Webhooks → [Your endpoint] → Events
```

### 3D Secure Authentication Not Working

**Check:**
- Using correct test card: `4000 0025 0000 3155`
- Popup blockers disabled
- Browser allows popups from Stripe

## Test Scenarios

### Scenario 1: Single Boat Payment
1. Create one boat registration
2. Complete it (assign crew, select race)
3. Pay for it
4. Verify status changes to "paid"

### Scenario 2: Multiple Boats Payment
1. Create 3 boat registrations
2. Complete all of them
3. Select all for payment
4. Pay in one transaction
5. Verify all boats show "paid" status

### Scenario 3: Declined Payment
1. Select boats for payment
2. Use declined test card: `4000 0000 0000 9995`
3. Verify error message is displayed
4. Verify boats remain in "complete" status (not paid)

### Scenario 4: 3D Secure Flow
1. Select boats for payment
2. Use 3D Secure test card: `4000 0025 0000 3155`
3. Complete authentication in popup
4. Verify payment succeeds
5. Verify boats are marked as paid

## Monitoring

### CloudWatch Logs

**Payment Intent Creation:**
```bash
aws logs tail /aws/lambda/ImpressionnistesApi-dev-CreatePaymentIntentFunction --follow
```

**Webhook Handler:**
```bash
aws logs tail /aws/lambda/ImpressionnistesApi-dev-ConfirmPaymentWebhookFunction --follow
```

### Stripe Dashboard

Monitor in real-time:
- **Payments**: https://dashboard.stripe.com/test/payments
- **Webhooks**: https://dashboard.stripe.com/test/webhooks
- **Logs**: https://dashboard.stripe.com/test/logs

## Security Notes

### Test Mode vs Live Mode

**Test Mode** (Current):
- API keys start with `sk_test_` and `pk_test_`
- No real money charged
- Test card numbers only
- Separate from production data

**Live Mode** (Production):
- API keys start with `sk_live_` and `pk_live_`
- Real money charged
- Real card numbers
- Requires business verification

### Never Commit Secrets

- `.env` is in `.gitignore`
- Never commit API keys
- Use environment variables
- Rotate keys periodically

## Additional Resources

- [Stripe Testing Guide](https://stripe.com/docs/testing)
- [Stripe Test Cards](https://stripe.com/docs/testing#cards)
- [Stripe.js Reference](https://stripe.com/docs/js)
- [Payment Intents API](https://stripe.com/docs/api/payment_intents)
- [Webhooks Guide](https://stripe.com/docs/webhooks)

## Support

If you encounter issues:
1. Check CloudWatch logs
2. Check Stripe Dashboard logs
3. Verify configuration with `make secrets-show-stripe`
4. Review this guide's troubleshooting section
