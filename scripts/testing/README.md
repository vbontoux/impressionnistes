# Testing Scripts

Testing and verification utilities for the Impressionnistes Registration System.

## Scripts

### verify-receipt-email.sh
Verify that receipt email is being passed to Stripe payment intents.

**Usage:**
```bash
./verify-receipt-email.sh <payment_intent_id>
```

**Example:**
```bash
./verify-receipt-email.sh pi_3SWJkLEJhMh6g9v01WoGIHlH
```

**What it checks:**
- Payment intent details (amount, status, description)
- Receipt email configuration
- Whether email will be sent by Stripe

**Requirements:**
- Stripe CLI installed (`stripe` command)
- Stripe API key configured

**Output:**
```
Payment Details:
  Amount: 150.00 EUR
  Status: succeeded
  Description: Payment for boat registrations

✅ Receipt Email: user@example.com

Receipt will be sent to this email in LIVE mode.
In TEST mode, view receipt in Stripe Dashboard.
```

**Where to get payment_intent_id:**
- Stripe Dashboard → Payments
- Payment success page in application
- Webhook logs

## Related Testing

### Email Testing
Test email notification system:
```bash
cd infrastructure
make test-email EMAIL=your@email.com ENV=dev
```

### Slack Testing
Test Slack notification system:
```bash
cd infrastructure
make test-slack ENV=dev
```

### Backend Tests
Run integration tests:
```bash
cd infrastructure
make test
make test-backend
make test-coverage
```

### Frontend Tests
Run frontend formatter tests:
```bash
cd infrastructure
make test-frontend
```

## Troubleshooting

**Error: "stripe: command not found"**
- Install Stripe CLI: https://stripe.com/docs/stripe-cli

**Error: "No such payment_intent"**
- Check payment intent ID is correct
- Verify you're using the correct Stripe account (test vs live)

**Receipt email not set**
- Check Lambda logs for payment creation
- Verify `receipt_email` is passed in payment intent creation
- See `functions/payment/create_payment_intent.py`

## Best Practices

1. **Test in sandbox mode first** before production
2. **Verify email addresses** in SES before testing
3. **Check Stripe Dashboard** for payment details
4. **Review Lambda logs** for debugging

## Related Documentation

- Email system: `docs/guides/EMAIL_TESTING_GUIDE.md`
- Payment testing: `docs/guides/PAYMENT_TESTING.md`
- Stripe docs: https://stripe.com/docs
