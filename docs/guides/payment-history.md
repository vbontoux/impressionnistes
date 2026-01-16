# Payment History Guide

## Overview

The Payment History feature allows team managers to view their payment transactions, track outstanding balances, and download payment invoices for expense reporting.

## Accessing Payment History

### From the Dashboard

1. Log in to your team manager account
2. On the dashboard, you'll see a **Payment Summary** widget showing:
   - Total amount paid
   - Outstanding balance (if any)
3. Click on the widget to view full payment history

### From the Navigation Menu

1. Click on **Payments** in the main navigation menu
2. This takes you to the full payment history page

## Payment History Page

### Desktop View

The payment history page displays your payments in a sortable table with the following columns:

- **Date**: When the payment was made
- **Amount**: Payment amount in EUR
- **Boats**: Number of boats (crews) included in the payment
- **Receipt**: Link to Stripe receipt
- **Invoice**: Download button for PDF invoice

### Mobile View

On mobile devices, payments are displayed as cards for better readability. Each card shows:
- Payment date
- Amount
- Number of boats
- Links to receipt and invoice

### Filtering by Date Range

1. Use the **Start Date** and **End Date** filters at the top of the page
2. Select your desired date range
3. Click **Apply** to filter payments
4. Click **Clear** to reset filters

### Sorting Payments

Click on any column header to sort by that field:
- **Date**: Sort by payment date (newest first by default)
- **Amount**: Sort by payment amount
- **Boats**: Sort by number of boats paid

## Payment Summary Widget

The Payment Summary widget on your dashboard provides a quick overview:

### Total Paid
Shows the total amount you've paid across all successful payments.

### Outstanding Balance
Shows the total amount owed for boats that are registered but not yet paid.

**Visual Indicator**: If you have an outstanding balance, it will be highlighted in yellow to draw your attention.

### Unpaid Boats
Click **View Details** to see a list of unpaid boats including:
- Event type (21km, 42km, etc.)
- Boat type (4+, skiff, etc.)
- Estimated amount

## Downloading Payment Invoices

### Why Download Invoices?

Payment invoices are useful for:
- Submitting expense reports to your rowing club
- Accounting and bookkeeping
- Tax documentation
- Record keeping

### How to Download

1. Go to your payment history page
2. Find the payment you want an invoice for
3. Click the **Download Invoice** button
4. The PDF will download automatically

### Invoice Contents

Each PDF invoice includes:
- **Event branding**: Course des Impressionnistes logo and name
- **Payment information**: Date, amount, currency, payment ID
- **Your information**: Name, club affiliation, email
- **Boats paid**: List of event types and boat types included
- **Stripe receipt link**: Direct link to your Stripe receipt

### Invoice Filename

Invoices are automatically named with the format:
```
invoice-payment-{payment_id}-{date}.pdf
```

Example: `invoice-payment-abc123-2026-01-15.pdf`

## Understanding Payment Status

### Successful Payments

Payments with status "succeeded" are complete and confirmed. You'll receive:
- Email confirmation from Stripe
- Payment record in your history
- Boats marked as "paid" in your registrations

### Outstanding Balance

Your outstanding balance includes:
- All boats with registration status "complete" (ready to pay)
- Boats that haven't been paid yet
- Estimated amounts based on current pricing

**Note**: Boats with status "incomplete" are not included in outstanding balance until they're ready to pay.

## Payment Receipts

### Stripe Receipts

Each payment includes a link to your Stripe receipt. Click the **View Receipt** link to:
- View detailed payment information
- See payment method used
- Access Stripe's official receipt

**Note**: Stripe receipts open in a new browser tab.

### Difference Between Receipt and Invoice

- **Stripe Receipt**: Official payment confirmation from Stripe (payment processor)
- **PDF Invoice**: Event-specific invoice for expense reporting (includes event branding and boat details)

Both documents are valid proof of payment, but the PDF invoice is more suitable for club expense reports.

## Troubleshooting

### I don't see a payment I just made

**Solution**: Payments may take a few seconds to appear after Stripe processes them. Refresh the page after 10-15 seconds.

### The receipt link doesn't work

**Solution**: Stripe receipt URLs expire after a certain period. Contact support if you need access to an old receipt.

### My outstanding balance seems incorrect

**Solution**: Outstanding balance only includes boats with status "complete". Check your boat registrations to ensure they're marked as complete.

### I can't download an invoice

**Solution**: 
1. Check your browser's download settings
2. Ensure pop-ups are not blocked
3. Try a different browser
4. Contact support if the issue persists

## Privacy and Security

### Data Access

- You can only see your own payment history
- Other team managers cannot see your payments
- Admins can view all payments for event management purposes

### Data Storage

- Payment records are stored securely in AWS DynamoDB
- All API requests use HTTPS encryption
- Payment data is never modified or deleted (immutable records)

### Stripe Integration

- Actual payment processing is handled by Stripe (PCI compliant)
- We only store payment metadata (amount, date, receipt URL)
- Credit card information is never stored in our system

## Best Practices

### Regular Monitoring

- Check your payment summary regularly on the dashboard
- Review outstanding balance before registration deadlines
- Download invoices promptly for your records

### Record Keeping

- Download and save PDF invoices for all payments
- Keep invoices organized by year for easy reference
- Submit invoices to your club treasurer promptly

### Payment Planning

- Review outstanding balance before making payments
- Consider paying for multiple boats at once to reduce transaction fees
- Plan payments before registration deadlines

## Support

If you have questions or issues with payment history:

1. Check this guide first
2. Review the [Payment Testing Guide](PAYMENT_TESTING.md) for technical details
3. Contact event administrators via the contact form
4. Email support with your payment ID for specific payment issues

## Related Documentation

- [Payment Testing Guide](PAYMENT_TESTING.md) - Technical payment testing
- [API Endpoints](../reference/api-endpoints.md) - Payment API documentation
- [GDPR Compliance](GDPR_COMPLIANCE.md) - Data privacy information
