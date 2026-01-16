# Requirements Document

## Introduction

This specification defines the payment history and balance tracking feature for the Impressionnistes Registration System. The feature provides visibility into payment transactions for both team managers and administrators, enabling them to track payments, view outstanding balances, and export payment data for accounting and event management purposes.

## Glossary

- **Team_Manager**: A user who manages boat registrations and crew members for their club
- **Payment_Record**: A database record representing a completed payment transaction
- **Outstanding_Balance**: The total amount owed for boats that are registered (status='complete') but not yet paid
- **Payment_History**: A chronological list of all payment transactions for a team manager
- **Payment_Summary**: Aggregated payment statistics including total paid and outstanding amounts
- **Admin_Export**: Excel file export functionality for event program that includes team manager payment balances
- **System**: The Impressionnistes Registration System

## Requirements

### Requirement 1: View Payment History

**User Story:** As a team manager, I want to view all my past payments, so that I can track what I've paid and when.

#### Acceptance Criteria

1. WHEN a team manager requests their payment history, THE System SHALL return a list of all payment records sorted by payment date (newest first)
2. WHEN displaying a payment record, THE System SHALL show payment date, amount, currency, number of boats, and receipt URL
3. WHEN a team manager filters by date range, THE System SHALL return only payments within the specified date range
4. WHEN a team manager has no payments, THE System SHALL return an empty list with appropriate messaging
5. WHEN a team manager clicks a receipt link, THE System SHALL open the Stripe receipt in a new tab

### Requirement 2: View Payment Summary

**User Story:** As a team manager, I want to see my total paid amount and outstanding balance, so that I know how much I still owe.

#### Acceptance Criteria

1. WHEN a team manager requests their payment summary, THE System SHALL calculate and return the total amount paid across all successful payments
2. WHEN calculating outstanding balance, THE System SHALL sum the estimated amounts for all boats with status='complete' (unpaid)
3. WHEN displaying outstanding balance, THE System SHALL list each unpaid boat with its event type, boat type, and estimated amount
4. WHEN a boat has no pricing information, THE System SHALL calculate the estimated amount using current pricing configuration
5. WHEN a team manager has no outstanding balance, THE System SHALL display zero with appropriate messaging

### Requirement 3: List Payment Transactions

**User Story:** As an administrator, I want to view all payment transactions across all team managers, so that I can track total revenue and payment activity.

#### Acceptance Criteria

1. WHEN an administrator requests all payments, THE System SHALL return payment records from all team managers
2. WHEN displaying payment records, THE System SHALL include team manager name, club affiliation, and email
3. WHEN an administrator filters by date range, THE System SHALL return only payments within the specified range
4. WHEN an administrator filters by team manager, THE System SHALL return only payments for that specific team manager
5. WHEN sorting payment records, THE System SHALL support sorting by date, amount, team manager name, and club

### Requirement 4: View Payment Analytics

**User Story:** As an administrator, I want to see payment analytics and trends, so that I can understand revenue patterns and outstanding balances.

#### Acceptance Criteria

1. WHEN an administrator requests payment analytics, THE System SHALL calculate total revenue across all successful payments
2. WHEN displaying analytics, THE System SHALL show total payment count, total boats paid, and number of team managers who have paid
3. WHEN calculating system-wide outstanding balance, THE System SHALL sum all unpaid boats across all team managers
4. WHEN grouping payments by time period, THE System SHALL support grouping by day, week, or month
5. WHEN displaying top payers, THE System SHALL rank team managers by total amount paid

### Requirement 5: Export Payment Data in Event Program

**User Story:** As an administrator, I want to see each team manager's payment balance in the event program export, so that I can track who has paid and who still owes money.

#### Acceptance Criteria

1. WHEN exporting the event program to Excel, THE System SHALL include a payment balance column for each team manager in the crew member list sheet
2. WHEN calculating payment balance for export, THE System SHALL show total paid amount for each team manager
3. WHEN calculating outstanding balance for export, THE System SHALL show total unpaid amount for each team manager
4. WHEN a team manager has no payments, THE System SHALL display zero for total paid
5. WHEN a team manager has no outstanding balance, THE System SHALL display zero for outstanding amount
6. WHEN displaying payment balance in Excel, THE System SHALL format amounts as currency with two decimal places

### Requirement 6: Access Control for Payment Data

**User Story:** As a system administrator, I want to ensure team managers can only see their own payment data, so that financial information remains private.

#### Acceptance Criteria

1. WHEN a team manager requests payment history, THE System SHALL return only their own payment records
2. WHEN a team manager requests payment summary, THE System SHALL calculate only their own totals
3. WHEN an administrator requests payment data, THE System SHALL return data for all team managers
4. WHEN an administrator impersonates a team manager, THE System SHALL show that team manager's payment data
5. WHEN a user without proper permissions requests payment data, THE System SHALL return an authorization error

### Requirement 7: Payment Record Integrity

**User Story:** As a system administrator, I want payment records to be immutable and accurate, so that financial data is trustworthy.

#### Acceptance Criteria

1. WHEN a payment succeeds via Stripe webhook, THE System SHALL create a payment record with payment intent ID, amount, currency, and timestamp
2. WHEN creating a payment record, THE System SHALL link it to the specific boat registration IDs that were paid
3. WHEN a payment record is created, THE System SHALL store the Stripe receipt URL for future reference
4. WHEN a boat is marked as paid, THE System SHALL lock the pricing information to preserve the amount paid
5. WHEN querying payment records, THE System SHALL never modify or delete existing payment records

### Requirement 8: Performance and Scalability

**User Story:** As a system administrator, I want payment queries to be fast and efficient, so that users have a responsive experience.

#### Acceptance Criteria

1. WHEN querying payment history for a team manager, THE System SHALL use DynamoDB partition key queries (not scans)
2. WHEN calculating payment summaries, THE System SHALL cache team manager lookups to minimize database queries
3. WHEN exporting payment data, THE System SHALL handle pagination for large datasets
4. WHEN displaying payment lists, THE System SHALL support pagination with configurable page size
5. WHEN multiple users request payment data simultaneously, THE System SHALL handle concurrent requests without performance degradation

### Requirement 9: Payment History UI

**User Story:** As a team manager, I want an intuitive payment history page, so that I can easily find and review my payment information.

#### Acceptance Criteria

1. WHEN viewing the payment history page, THE System SHALL display payments in a sortable table with date, amount, boats, and receipt link
2. WHEN viewing on mobile devices, THE System SHALL display payments in a card layout for better readability
3. WHEN filtering by date range, THE System SHALL provide date picker inputs with clear labels
4. WHEN clicking a receipt link, THE System SHALL open the Stripe receipt in a new browser tab
5. WHEN the payment history is empty, THE System SHALL display a friendly message indicating no payments have been made

### Requirement 10: Payment Summary Widget

**User Story:** As a team manager, I want to see my payment summary on the dashboard, so that I can quickly check my balance without navigating to a separate page.

#### Acceptance Criteria

1. WHEN viewing the dashboard, THE System SHALL display a payment summary widget showing total paid and outstanding balance
2. WHEN the outstanding balance is greater than zero, THE System SHALL highlight it with a visual indicator
3. WHEN clicking the payment summary widget, THE System SHALL navigate to the full payment history page
4. WHEN the widget loads, THE System SHALL show loading state while fetching payment data
5. WHEN payment data fails to load, THE System SHALL display an error message with retry option

### Requirement 11: Admin Payment Analytics UI

**User Story:** As an administrator, I want a payment analytics dashboard, so that I can visualize revenue trends and outstanding balances.

#### Acceptance Criteria

1. WHEN viewing the admin payment analytics page, THE System SHALL display total revenue, payment count, and outstanding balance
2. WHEN viewing payment timeline, THE System SHALL show a chart visualizing payments over time
3. WHEN viewing top payers, THE System SHALL display a sortable table of team managers ranked by total paid
4. WHEN filtering by date range, THE System SHALL update all analytics to reflect the selected period
5. WHEN exporting analytics data, THE System SHALL generate a CSV file with all payment details

### Requirement 12: Export Payment Invoice as PDF

**User Story:** As a team manager, I want to export a payment invoice as PDF, so that I can submit it as an expense report to my club.

#### Acceptance Criteria

1. WHEN a team manager views a payment record, THE System SHALL provide an option to download the payment invoice as PDF
2. WHEN generating a PDF invoice, THE System SHALL include payment date, amount, currency, payment ID, and list of boats paid
3. WHEN generating a PDF invoice, THE System SHALL include team manager name, club affiliation, and email
4. WHEN generating a PDF invoice, THE System SHALL include system branding and event name (Course des Impressionnistes)
5. WHEN a PDF invoice is downloaded, THE System SHALL name the file with payment ID and date (e.g., "invoice-payment-123-2026-01-15.pdf")
6. WHEN the Stripe receipt URL is available, THE System SHALL include a link to the Stripe receipt in the PDF invoice

### Requirement 13: Error Handling and Validation

**User Story:** As a developer, I want robust error handling for payment queries, so that users receive clear feedback when issues occur.

#### Acceptance Criteria

1. WHEN a payment query fails due to database error, THE System SHALL return a 500 error with descriptive message
2. WHEN invalid date range is provided, THE System SHALL return a 400 error indicating the validation failure
3. WHEN a team manager requests a payment that doesn't belong to them, THE System SHALL return a 404 error
4. WHEN pagination parameters are invalid, THE System SHALL return a 400 error with validation details
5. WHEN the Stripe receipt URL is unavailable, THE System SHALL display a message indicating the receipt cannot be accessed

## Appendix A: Payment Record Data Structure

```
Payment Record (DynamoDB):
PK: TEAM#{team_manager_id}
SK: PAYMENT#{payment_id}

Attributes:
- payment_id: UUID
- stripe_payment_intent_id: String
- team_manager_id: String
- boat_registration_ids: List<String>
- amount: Decimal
- currency: String (e.g., "EUR")
- status: String (e.g., "succeeded")
- paid_at: ISO 8601 timestamp
- stripe_receipt_url: String
- created_at: ISO 8601 timestamp
- updated_at: ISO 8601 timestamp
```

## Appendix B: API Endpoints

```
Team Manager Endpoints:
GET  /payments                       - List all payments for authenticated team manager
GET  /payments/summary               - Get payment summary (total paid + outstanding balance)
GET  /payments/{payment_id}          - Get single payment details (existing)
GET  /payments/{payment_id}/receipt  - Get payment receipt (existing)
GET  /payments/{payment_id}/invoice  - Download payment invoice as PDF (new)

Admin Endpoints:
GET  /admin/payments                 - List all payments across all team managers
GET  /admin/payments/analytics       - Get payment analytics and trends
GET  /admin/payments/outstanding     - Get all outstanding balances by team manager
```

## Appendix C: Permissions

```
New Permissions:
- view_payment_history: View own payment history (team managers)
- view_payment_analytics: View all payment data and analytics (admins)
- download_payment_invoice: Download payment invoice as PDF (team managers)

Permission Matrix:
| Action                    | Team Manager | Admin |
|---------------------------|--------------|-------|
| View own payment history  | ✓            | ✓     |
| View own payment summary  | ✓            | ✓     |
| Download payment invoice  | ✓            | ✓     |
| View all payments         | ✗            | ✓     |
| View payment analytics    | ✗            | ✓     |
| Export payment data       | ✗            | ✓     |
```

## Appendix D: Outstanding Balance Calculation

Outstanding balance is calculated as follows:

1. Query all boat registrations for team manager with `registration_status = 'complete'`
2. For each unpaid boat:
   - Get boat's pricing information (or calculate using current pricing config)
   - Sum the total amount
3. Return total outstanding amount

Note: Boats with status 'paid' are excluded from outstanding balance calculation.

## Appendix E: Event Program Export Integration

The event program export (Excel file) will be enhanced to include payment balance information:

**Crew Member List Sheet - New Columns:**
- Total Paid (EUR): Total amount paid by team manager
- Outstanding Balance (EUR): Total unpaid amount for team manager
- Payment Status: "Paid in Full", "Partial Payment", or "No Payment"

**Implementation:**
- Backend: `export_races_json.py` will include payment summary for each team manager
- Frontend: `eventProgramFormatter.js` will add payment columns to crew member list
- Format: Currency values with 2 decimal places (e.g., "150.00")
