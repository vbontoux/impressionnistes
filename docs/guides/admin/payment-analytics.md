# Admin Payment Analytics Guide

## Overview

The Payment Analytics feature provides administrators with comprehensive visibility into payment transactions, revenue trends, and outstanding balances across all team managers. This guide covers how to use the payment analytics dashboard and export payment data.

## Accessing Payment Analytics

### From Admin Dashboard

1. Log in with your admin account
2. Navigate to **Admin** → **Payment Analytics** in the main menu
3. The analytics dashboard will load with current payment data

## Payment Analytics Dashboard

### Summary Cards

The top of the dashboard displays key metrics:

#### Total Revenue
- Sum of all successful payments across all team managers
- Displayed in EUR with 2 decimal places
- Updates based on selected date range

#### Total Payments
- Count of all payment transactions
- Includes only successful payments (status: "succeeded")

#### Total Boats Paid
- Total number of boats (crews) included in all payments
- Useful for tracking registration completion

#### Unique Payers
- Number of distinct team managers who have made payments
- Helps track payment adoption

#### Outstanding Balance
- System-wide total of unpaid boats
- Includes all boats with status "complete" but not yet paid
- Highlighted in yellow if greater than zero

### Payment Timeline Chart

The timeline chart visualizes payment activity over time:

**Features:**
- Line chart showing payment amounts by time period
- Grouping options: Day, Week, or Month
- Hover over data points to see exact amounts
- Responsive design for mobile and desktop

**How to Use:**
1. Select grouping period (Day/Week/Month) from dropdown
2. Chart updates automatically
3. Use date range filters to focus on specific periods

### Top Payers Table

The top payers table ranks team managers by total amount paid:

**Columns:**
- **Team Manager**: Name of the team manager
- **Club**: Club affiliation
- **Total Paid**: Total amount paid (EUR)
- **Payments**: Number of payment transactions
- **Boats**: Total number of boats paid

**Features:**
- Sortable by any column (click column header)
- Default sort: Total Paid (descending)
- Shows top 10 payers by default
- Scroll to see more

## Filtering Payment Data

### Date Range Filters

Filter analytics by specific time periods:

1. **Start Date**: Select the beginning of the date range
2. **End Date**: Select the end of the date range
3. Click **Apply** to update all analytics
4. Click **Clear** to reset to all-time data

**Use Cases:**
- View payments for current month
- Compare different time periods
- Generate reports for specific events
- Track payment trends over time

### Team Manager Filter

Filter to view payments from a specific team manager:

1. Use the team manager dropdown
2. Select a specific team manager
3. All analytics update to show only that team manager's data
4. Clear filter to return to all team managers

## Viewing All Payments

### Payment List

Below the analytics, you'll find a complete list of all payments:

**Desktop View (Table):**
- Date: Payment date and time
- Team Manager: Name and club
- Amount: Payment amount in EUR
- Boats: Number of boats included
- Status: Payment status (succeeded, pending, failed)
- Receipt: Link to Stripe receipt
- Invoice: Download PDF invoice

**Mobile View (Cards):**
- Payments displayed as cards for better readability
- Same information as table view
- Swipe to scroll through payments

### Sorting Payments

Click any column header to sort:
- **Date**: Sort by payment date (newest first by default)
- **Amount**: Sort by payment amount
- **Team Manager**: Sort alphabetically by name
- **Club**: Sort alphabetically by club name

### Pagination

For large datasets:
- Payments are paginated (50 per page by default)
- Use **Next** and **Previous** buttons to navigate
- Page numbers displayed at bottom

## Exporting Payment Data

### CSV Export

Export all payment data to CSV for further analysis:

1. Click **Export CSV** button at top of page
2. CSV file downloads automatically
3. Filename format: `payments-export-{date}.csv`

**CSV Contents:**
- Payment ID
- Payment Date
- Team Manager Name
- Team Manager Email
- Club Affiliation
- Amount (EUR)
- Currency
- Number of Boats
- Status
- Stripe Payment Intent ID
- Receipt URL

**Use Cases:**
- Import into Excel or Google Sheets
- Financial reporting and accounting
- Revenue analysis and forecasting
- Audit trail and record keeping

### Event Program Export

Payment balance data is automatically included in the event program export:

1. Go to **Admin** → **Export** → **Event Program**
2. Download Excel file
3. Open the **Crew Member List** sheet
4. Payment columns are included:
   - Total Paid (EUR)
   - Outstanding Balance (EUR)
   - Payment Status

**Payment Status Values:**
- "Paid in Full": No outstanding balance
- "Partial Payment": Some payments made, balance remaining
- "No Payment": No payments made yet

## Understanding Payment Data

### Payment Status

**Succeeded**: Payment completed successfully
- Boats marked as paid
- Receipt available
- Included in revenue totals

**Pending**: Payment in progress
- Awaiting confirmation from Stripe
- Not included in revenue totals yet
- Will update automatically when confirmed

**Failed**: Payment failed
- Not included in revenue totals
- Team manager notified
- May need to retry payment

### Outstanding Balance Calculation

Outstanding balance includes:
- All boats with `registration_status = 'complete'`
- Boats not yet paid
- Estimated amounts based on locked pricing or current pricing

**Not Included:**
- Boats with status "incomplete"
- Boats already paid
- Deleted boat registrations

### Locked Pricing

When a payment is made:
- Pricing information is locked on the boat record
- Ensures payment amount is preserved
- Prevents pricing changes from affecting historical data
- Used for accurate outstanding balance calculations

## Access Control

### Admin-Only Access

Payment analytics is restricted to administrators:
- Team managers cannot access this page
- Attempting to access without admin role returns 403 Forbidden
- Admin impersonation does not grant access to analytics

### Data Privacy

- Admins can view all payment data for event management
- Payment data is encrypted in transit (HTTPS)
- Access is logged for audit purposes
- Complies with GDPR data protection requirements

## Common Use Cases

### Monthly Revenue Reports

1. Set date range to current month
2. Note total revenue from summary card
3. Export CSV for detailed breakdown
4. Compare with previous months

### Tracking Payment Completion

1. Check "Unique Payers" vs total registered team managers
2. Review outstanding balance
3. Identify team managers who haven't paid
4. Send payment reminders if needed

### Financial Reconciliation

1. Export CSV with all payments
2. Compare with Stripe dashboard
3. Verify payment amounts and dates
4. Reconcile with bank deposits

### Event Planning

1. Review payment timeline to identify peak payment periods
2. Use data to plan registration deadlines
3. Track payment trends year-over-year
4. Forecast revenue for future events

## Troubleshooting

### Analytics not loading

**Solution:**
1. Check your internet connection
2. Refresh the page
3. Clear browser cache
4. Try a different browser
5. Contact support if issue persists

### Payment amounts don't match Stripe

**Solution:**
1. Check date range filters (may be filtering out some payments)
2. Verify payment status (only "succeeded" included in totals)
3. Allow time for webhook processing (payments may take 10-15 seconds to appear)
4. Contact support with specific payment IDs for investigation

### CSV export fails

**Solution:**
1. Check browser download settings
2. Ensure pop-ups are not blocked
3. Try exporting smaller date range
4. Use a different browser
5. Contact support if issue persists

### Outstanding balance seems incorrect

**Solution:**
1. Outstanding balance only includes boats with status "complete"
2. Check boat registrations to verify statuses
3. Verify pricing configuration is correct
4. Contact support for detailed balance breakdown

## Best Practices

### Regular Monitoring

- Check payment analytics daily during registration period
- Monitor outstanding balance before deadlines
- Track payment trends to identify issues early
- Review top payers to thank high-value participants

### Financial Reporting

- Export CSV monthly for accounting records
- Reconcile with Stripe dashboard regularly
- Keep exports organized by month/year
- Archive exports for audit trail

### Data Analysis

- Compare payment patterns year-over-year
- Identify peak payment periods
- Track payment completion rates
- Use data to improve registration process

### Communication

- Use outstanding balance data to send payment reminders
- Share revenue milestones with stakeholders
- Provide payment statistics in event reports
- Thank team managers who pay early

## API Access

For programmatic access to payment data, see the [API Endpoints Documentation](../../reference/api-endpoints.md#admin-payment-endpoints).

**Available Endpoints:**
- `GET /admin/payments` - List all payments
- `GET /admin/payments/analytics` - Get analytics data

## Related Documentation

- [Payment History Guide](../payment-history.md) - Team manager payment features
- [API Endpoints](../../reference/api-endpoints.md) - Payment API documentation
- [Centralized Access Control](centralized-access-control.md) - Permission system
- [Database Export](../operations/database-export.md) - Data export tools

## Support

For questions or issues with payment analytics:

1. Check this guide first
2. Review the [API documentation](../../reference/api-endpoints.md)
3. Contact technical support with specific details
4. Include payment IDs or screenshots when reporting issues
