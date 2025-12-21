# Stripe Email Receipts Configuration Guide

This guide explains how to configure automatic email receipts for payments in the Course des Impressionnistes registration system.

> **📝 Note**: This guide is updated for Stripe's new Dashboard interface (2024+). If you're using an older Stripe account, some menu locations may differ slightly.

## Overview

Stripe can automatically send email receipts to customers after successful payments. This is a built-in feature that requires minimal configuration.

### Key Points

- ✅ **Test/Sandbox mode**: Receipts are automatically enabled (viewable in Dashboard)
- ✅ **Live mode**: Receipts are automatically emailed to customers
- ✅ **Branding**: Add your logo and colors in Settings → Public details
- ✅ **Languages**: Automatic detection (FR/EN and 25+ languages)
- ✅ **Cost**: FREE - included with Stripe

## Prerequisites

- Stripe account (test or live mode)
- Access to Stripe Dashboard
- Completed payments to test with

## Step 1: Enable Automatic Receipts

### Important Note About Stripe's New Interface

Stripe has updated their dashboard. The new interface works differently:

- **Test/Sandbox mode**: Email receipts are automatically enabled by default
- **Live mode**: You need to configure email settings when you activate your account

### For Test/Sandbox Mode (Development)

**Good news**: Email receipts are **automatically enabled** in test mode! No configuration needed.

When you make a test payment:
- Stripe automatically sends a receipt to the email in your Stripe account
- You can view receipts in the Stripe Dashboard under each payment

### For Live Mode (Production)

1. Switch to **Live mode** in Stripe Dashboard
2. Complete account activation (if not done)
3. Go to **Settings** → **Business settings** → **Customer emails**
4. Configure receipt email settings
5. Enable **"Successful payment receipts"**

## Step 2: Customize Receipt Email Branding

### Add Your Branding (Works in Test & Live Mode)

1. Go to **Settings** (gear icon in top right)
2. Click **"Public details"** or **"Branding"** (depending on your Stripe version)
3. Configure:
   - **Business name**: "Course des Impressionnistes" or "RCPM"
   - **Support email**: Your support email (e.g., `support@rcpm.fr`)
   - **Logo**: Upload RCPM logo (recommended size: 200x50px or 512x512px)
   - **Brand color**: RCPM brand color (e.g., `#4CAF50`)
4. Click **"Save"**

The logo and colors will automatically appear in receipt emails.

### Email Customization (Live Mode Only)

In Live mode, you can further customize:
1. Go to **Settings** → **Business settings** → **Customer emails**
2. Customize email templates
3. Add custom footer text
4. Configure "From" name and reply-to address

## Step 3: Language Settings (Automatic)

**Good news**: Stripe automatically handles language detection!

- Receipts are automatically sent in the customer's language
- Supports **French** and **English** (and 25+ other languages)
- Based on:
  - Customer's browser language
  - Customer's location
  - Payment method country

**No configuration needed** - it just works! 🎉

## Step 4: Test Receipt Emails

### How to Test in Sandbox/Test Mode

1. **Make a test payment** using test card: `4242 4242 4242 4242`
2. **View the receipt** in Stripe Dashboard:
   - Go to **Payments** in Stripe Dashboard
   - Click on your test payment
   - Scroll down to find **"Receipt"** section
   - Click **"View receipt"** to see what customers will receive
   - You can manually **"Send receipt"** from here to test email delivery

### Important Notes for Testing

- **In test/sandbox mode**: 
  - Receipts are NOT automatically emailed
  - Emails can only be sent to:
    - Your own email (Stripe account owner)
    - Stripe team members
    - Verified test email addresses
  - This is a Stripe security feature to prevent spam during testing
  
- **To see receipts**: View them in the Stripe Dashboard (as shown above)

- **In live mode**: 
  - Receipts ARE automatically emailed to customers
  - No email restrictions
  
- **Our implementation**: 
  - ✅ We now pass the team manager's email to Stripe
  - ✅ Receipt email will be sent in live mode
  - ✅ In test mode, you can manually send receipts from Dashboard

## Step 5: Add Customer Email to Payments (Optional Enhancement)

To send receipts to the actual customer (team manager), you need to pass their email when creating the payment intent.

### Backend Update (Optional)

Update `functions/payment/create_payment_intent.py`:

```python
# Get team manager email
team_manager = db.get_item(
    pk=f'USER#{team_manager_id}',
    sk=f'PROFILE#{team_manager_id}'
)
customer_email = team_manager.get('email')

# Create Stripe Payment Intent with receipt_email
payment_intent = stripe_create_payment_intent(
    amount=total_amount,
    currency='EUR',
    metadata=metadata,
    description=description,
    receipt_email=customer_email  # Add this line
)
```

This will send the receipt to the team manager's email address.

## What's Included in Receipt Emails

Stripe receipt emails automatically include:

- ✅ Payment amount and currency
- ✅ Payment date and time
- ✅ Payment method (last 4 digits of card)
- ✅ Receipt number
- ✅ Business name and logo
- ✅ Link to view full receipt online
- ✅ Payment description (e.g., "Course des Impressionnistes - 1 boat(s): skiff")

## Receipt Email Preview

Here's what customers will see:

```
From: Course des Impressionnistes <receipts@stripe.com>
Subject: Receipt from Course des Impressionnistes [#1234-5678]

[RCPM Logo]

Receipt from Course des Impressionnistes

Amount paid: €20.00
Date: Nov 22, 2024
Payment method: Visa •••• 4242

Description: Course des Impressionnistes - 1 boat(s): skiff

View receipt online: [Link]

Questions? Contact us at support@rcpm.fr
```

## Customization Options

### Advanced Customization

1. **Custom footer text**:
   - Go to **Settings** → **Emails** → **Successful payments**
   - Add custom footer with contact information

2. **Custom CSS** (Stripe Billing customers only):
   - Advanced styling options
   - Requires Stripe Billing subscription

3. **Localization**:
   - Stripe automatically translates receipts
   - Supports 25+ languages

## Monitoring Receipt Delivery

### Check Receipt Status

1. Go to **Payments** in Stripe Dashboard
2. Click on a payment
3. Scroll to **"Receipt"** section
4. See:
   - Receipt sent status
   - Email address
   - Timestamp
   - Link to view receipt

### Troubleshooting

**Receipt not received?**

1. Check spam/junk folder
2. Verify email address in Stripe Dashboard
3. Check **Settings** → **Emails** is enabled
4. Look for bounce notifications in Stripe Dashboard

**Wrong email address?**

- Update the payment intent to include `receipt_email` parameter
- See "Add Customer Email to Payments" section above

## Production Checklist

Before going live:

- [ ] Enable receipt emails in Live mode
- [ ] Upload RCPM logo and set brand colors
- [ ] Configure "From name" and "Reply-to email"
- [ ] Test receipt delivery with a live payment
- [ ] Verify receipts are in correct language (FR/EN)
- [ ] Add customer email to payment intents (optional)
- [ ] Update support email in receipt footer

## Alternative: Custom Receipt System

If you need more control over receipts, you can build a custom system:

1. **Disable Stripe receipts**: Turn off automatic emails
2. **Create custom email template**: Design your own receipt
3. **Send via AWS SES**: Use SES to send custom receipts
4. **Trigger from webhook**: Send email when payment succeeds

This is covered in **Task 15: Basic Email Notifications** (V1) or **Task 24: Enhanced Notification System** (V2).

## Cost

Stripe receipt emails are **FREE** - no additional cost beyond standard Stripe fees.

## Support

- [Stripe Receipts Documentation](https://stripe.com/docs/receipts)
- [Stripe Email Settings](https://dashboard.stripe.com/settings/emails)
- [Stripe Branding Guide](https://stripe.com/docs/receipts/branding)

## Summary

**Minimum configuration (5 minutes):**
1. Enable "Send email receipts" in Stripe Dashboard
2. Upload RCPM logo
3. Set brand color
4. Done! ✅

**Enhanced configuration (15 minutes):**
1. All of the above
2. Customize email text
3. Add customer email to payment intents
4. Test in both languages
5. Done! ✅

Stripe handles all the complexity of email delivery, localization, and formatting automatically!
