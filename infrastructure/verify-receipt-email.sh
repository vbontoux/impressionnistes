#!/bin/bash

# Script to verify receipt email is being passed to Stripe
# Usage: ./verify-receipt-email.sh [payment_intent_id]

PAYMENT_INTENT_ID=$1

if [ -z "$PAYMENT_INTENT_ID" ]; then
    echo "Usage: ./verify-receipt-email.sh <payment_intent_id>"
    echo ""
    echo "Example:"
    echo "  ./verify-receipt-email.sh pi_3SWJkLEJhMh6g9v01WoGIHlH"
    echo ""
    echo "Get payment_intent_id from:"
    echo "  - Stripe Dashboard → Payments"
    echo "  - Or from the payment success page"
    exit 1
fi

echo "=========================================="
echo "Checking Receipt Email for Payment Intent"
echo "=========================================="
echo ""
echo "Payment Intent: $PAYMENT_INTENT_ID"
echo ""

# Get payment intent details from Stripe
stripe payment_intents retrieve $PAYMENT_INTENT_ID --format json | python3 -c "
import json
import sys

data = json.load(sys.stdin)

print('Payment Details:')
print(f\"  Amount: {data.get('amount', 0) / 100} {data.get('currency', 'EUR').upper()}\")
print(f\"  Status: {data.get('status')}\")
print(f\"  Description: {data.get('description')}\")
print()

receipt_email = data.get('receipt_email')
if receipt_email:
    print(f\"✅ Receipt Email: {receipt_email}\")
    print()
    print('Receipt will be sent to this email in LIVE mode.')
    print('In TEST mode, view receipt in Stripe Dashboard.')
else:
    print('❌ No receipt email set')
    print()
    print('Receipt email was not passed to Stripe.')
    print('Check Lambda logs for errors.')
"

echo ""
echo "To view the receipt:"
echo "  https://dashboard.stripe.com/test/payments/$PAYMENT_INTENT_ID"
