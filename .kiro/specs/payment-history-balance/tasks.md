# Implementation Plan: Payment History and Balance Tracking

## Overview

This implementation plan breaks down the payment history and balance tracking feature into discrete, incremental tasks. Each task builds on previous work and includes testing to validate functionality early.

## Tasks

- [x] 1. Set up shared payment utilities in Lambda layer
  - Create `functions/layer/python/payment_queries.py` for shared query logic
  - Create `functions/layer/python/payment_calculations.py` for shared calculation logic
  - Create `functions/layer/python/payment_formatters.py` for shared formatting logic
  - _Requirements: Foundation for all payment functions_

- [x] 1.1 Write minimal unit tests for shared payment utilities
  - Test one query helper function (basic case)
  - Test total paid calculation (basic case)
  - Test formatting function (basic case)
  - _Requirements: Foundation for all payment functions_

- [x] 2. Implement list_payments Lambda function
  - [x] 2.1 Create `functions/payment/list_payments.py`
    - Implement query logic using DynamoDB partition key
    - Add date range filtering
    - Add sorting by paid_at (descending)
    - Calculate summary statistics
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 2.2 Write minimal property test for payment list sorting
    - Test with 3-5 payment records only
    - **Property 1: Payment List Sorting**
    - **Validates: Requirements 1.1**

  - [x] 2.3 Write minimal property test for date range filtering
    - Test with 3-5 payment records only
    - **Property 2: Date Range Filtering**
    - **Validates: Requirements 1.3**

  - [x] 2.4 Write minimal property test for payment record completeness
    - Test with 1-2 payment records only
    - **Property 3: Payment Record Completeness**
    - **Validates: Requirements 1.2, 7.1, 7.2, 7.3**

- [x] 3. Implement get_payment_summary Lambda function
  - [x] 3.1 Create `functions/payment/get_payment_summary.py`
    - Query all payments for team manager
    - Calculate total paid amount
    - Query unpaid boats (status='complete')
    - Calculate outstanding balance
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.2 Write minimal property test for total paid calculation
    - Test with 2-3 payment records only
    - **Property 4: Total Paid Calculation**
    - **Validates: Requirements 2.1**

  - [x] 3.3 Write minimal property test for outstanding balance calculation
    - Test with 2-3 boat records only
    - **Property 5: Outstanding Balance Calculation**
    - **Validates: Requirements 2.2**

  - [x] 3.4 Write minimal property test for unpaid boat fields
    - Test with 1-2 boat records only
    - **Property 6: Unpaid Boat Fields**
    - **Validates: Requirements 2.3**

  - [x] 3.5 Write minimal property test for pricing fallback
    - Test with 1 boat record without pricing
    - **Property 7: Pricing Fallback**
    - **Validates: Requirements 2.4**

- [x] 4. Add API Gateway routes for team manager endpoints
  - Add `GET /payment/history` route → list_payments
  - Add `GET /payment/summary` route → get_payment_summary
  - Configure CORS and authentication
  - _Requirements: 1.1, 2.1_

- [x] 4.1 Write minimal integration tests for team manager payment endpoints
  - Test GET /payment/history with authentication (1 test case)
  - Test GET /payment/summary with authentication (1 test case)
  - Test access control - team manager only sees own payments (1 test case)
  - _Requirements: 1.1, 2.1, 6.1, 6.2_

- [x] 5. Checkpoint - Ensure team manager payment endpoints work
  - Ensure all tests pass, ask the user if questions arise.


- [x] 6. Implement admin payment endpoints
  - [x] 6.1 Create `functions/admin/list_all_payments.py`
    - Scan all PAYMENT# records across teams
    - Cache team manager lookups
    - Add filtering by team manager and date range
    - Add sorting by multiple fields
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 6.2 Write minimal property test for admin query completeness
    - Test with 2-3 team managers only
    - **Property 8: Admin Query Completeness**
    - **Validates: Requirements 3.1**

  - [x] 6.3 Write minimal property test for team manager filtering
    - Test with 2 team managers only
    - **Property 9: Team Manager Filtering**
    - **Validates: Requirements 3.4**

  - [x] 6.4 Write minimal property test for multi-field sorting
    - Test sorting by date only (1 field)
    - **Property 10: Multi-Field Sorting**
    - **Validates: Requirements 3.5**

  - [x] 6.5 Create `functions/admin/get_payment_analytics.py`
    - Calculate total revenue and payment statistics
    - Group payments by time period (day/week/month)
    - Calculate system-wide outstanding balance
    - Rank team managers by total paid
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 6.6 Write minimal property test for analytics counting
    - Test with 2-3 payment records only
    - **Property 11: Analytics Counting**
    - **Validates: Requirements 4.2**

  - [x] 6.7 Write minimal property test for time period grouping
    - Test with 3-5 payments across 2 days only
    - **Property 12: Time Period Grouping**
    - **Validates: Requirements 4.4**

  - [x] 6.8 Write minimal property test for top payers ranking
    - Test with 2-3 team managers only
    - **Property 13: Top Payers Ranking**
    - **Validates: Requirements 4.5**

- [x] 7. Add API Gateway routes for admin endpoints
  - Add `GET /admin/payments` route → list_all_payments
  - Add `GET /admin/payments/analytics` route → get_payment_analytics
  - Configure admin-only access control
  - _Requirements: 3.1, 4.1_

- [x] 7.1 Write minimal integration tests for admin payment endpoints
  - Test GET /admin/payments with admin authentication (1 test case)
  - Test GET /admin/payments/analytics with admin authentication (1 test case)
  - Test access control - non-admin gets 403 (1 test case)
  - _Requirements: 3.1, 4.1, 6.3_

- [x] 8. Checkpoint - Ensure admin payment endpoints work
  - Ensure all tests pass, ask the user if questions arise.

- [-] 9. Implement PDF invoice generation
  - [x] 9.1 Add ReportLab to Lambda layer dependencies
    - Update `functions/layer/requirements.txt`
    - Rebuild Lambda layer
    - _Requirements: 12.2_

  - [x] 9.2 Create `functions/payment/get_payment_invoice.py`
    - Retrieve payment record and boat details
    - Generate PDF using ReportLab
    - Include all required fields (payment info, team manager info, boat list)
    - Add event branding and Stripe receipt link
    - Return PDF as base64-encoded response
    - _Requirements: 12.2, 12.3, 12.4, 12.5, 12.6_

  - [x] 9.3 Write minimal property test for PDF invoice completeness
    - Test with 1 payment record only
    - **Property 21: PDF Invoice Completeness**
    - **Validates: Requirements 12.2, 12.3, 12.4**

  - [x] 9.4 Write minimal property test for PDF filename format
    - Test with 1 payment record only
    - **Property 22: PDF Filename Format**
    - **Validates: Requirements 12.5**

  - [x] 9.5 Write minimal property test for PDF receipt link inclusion
    - Test with 1 payment record with receipt URL
    - **Property 23: PDF Receipt Link Inclusion**
    - **Validates: Requirements 12.6**

- [x] 10. Add API Gateway route for PDF invoice
  - Add `GET /payments/{payment_id}/invoice` route → get_payment_invoice
  - Configure response headers for PDF download
  - _Requirements: 12.1_

- [x] 10.1 Write minimal integration test for PDF invoice endpoint
  - Test GET /payments/{id}/invoice returns PDF (1 test case)
  - Test access control - team manager can only download own invoices (1 test case)
  - _Requirements: 12.1, 6.1_


- [x] 11. Enhance event program export with payment balance
  - [x] 11.1 Update `functions/admin/export_races_json.py`
    - For each team manager, query payment records
    - Calculate total paid and outstanding balance
    - Add payment fields to team_managers array in response
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 11.2 Write minimal property test for currency formatting
    - Test with 2-3 amounts only
    - **Property 14: Currency Formatting**
    - **Validates: Requirements 5.6**

  - [x] 11.3 Update `frontend/src/utils/exportFormatters/eventProgramFormatter.js`
    - Add payment balance columns to crew member list
    - Format currency values with 2 decimal places
    - Add payment status column
    - _Requirements: 5.1, 5.6_

  - [x] 11.4 Write minimal unit test for event program export enhancement
    - Test payment balance columns are added (1 test case)
    - Test currency formatting (1 test case)
    - _Requirements: 5.1, 5.6_

- [x] 12. Checkpoint - Ensure export enhancement works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Implement frontend payment history page
  - [x] 13.1 Create `frontend/src/views/PaymentHistory.vue`
    - Create sortable table for desktop view
    - Create card layout for mobile view
    - Add date range filter inputs
    - Add loading and error states
    - Add empty state messaging
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 13.2 Write minimal component tests for PaymentHistory
    - Test table renders with payment data (1 test case)
    - Test empty state rendering (1 test case)
    - _Requirements: 9.1, 9.5_

  - [x] 13.3 Add route to `frontend/src/router/index.js`
    - Add `/payments` route
    - Configure authentication requirement
    - _Requirements: 9.1_

  - [x] 13.4 Add navigation link to payment history
    - Add link in team manager navigation menu
    - _Requirements: 9.1_

- [x] 14. Implement frontend payment summary widget
  - [x] 14.1 Create `frontend/src/components/PaymentSummaryWidget.vue`
    - Display total paid and outstanding balance
    - Highlight outstanding balance if > 0
    - Add link to full payment history
    - Add loading and error states
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 14.2 Write minimal component tests for PaymentSummaryWidget
    - Test summary data display (1 test case)
    - Test outstanding balance highlighting (1 test case)
    - _Requirements: 10.1, 10.2_

  - [x] 14.3 Add widget to team manager dashboard
    - Import and use PaymentSummaryWidget in Dashboard.vue
    - _Requirements: 10.1_

- [x] 15. Implement frontend admin payment analytics page
  - [x] 15.1 Create `frontend/src/views/admin/AdminPaymentAnalytics.vue`
    - Create summary cards for total revenue, payments, outstanding
    - Add payment timeline chart using Chart.js
    - Create sortable table for top payers
    - Add date range filters
    - Add CSV export functionality
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [x] 15.2 Write minimal component tests for AdminPaymentAnalytics
    - Test summary cards rendering (1 test case)
    - Test top payers table (1 test case)
    - _Requirements: 11.1, 11.3_

  - [x] 15.3 Add route to admin router
    - Add `/admin/payment-analytics` route
    - Configure admin-only access
    - _Requirements: 11.1_

  - [x] 15.4 Add navigation link to admin menu
    - Add link in admin navigation menu
    - _Requirements: 11.1_

- [x] 16. Add access control permissions
  - [x] 16.1 Update `functions/init/init_config.py`
    - Add `view_payment_history` permission
    - Add `view_payment_analytics` permission
    - Add `download_payment_invoice` permission
    - Configure permission matrix for team managers and admins
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 16.2 Write minimal property tests for access control
    - Test with 2 team managers only
    - **Property 15: Access Control Isolation**
    - **Property 16: Admin Access Completeness**
    - **Property 18: Permission Enforcement**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.5**

- [x] 17. Add minimal property test for pricing lock on payment
  - [x] 17.1 Write minimal property test for pricing lock
    - Test with 1 boat record only
    - **Property 19: Pricing Lock on Payment**
    - **Validates: Requirements 7.4**

- [x] 18. Add minimal property test for pagination
  - [x] 18.1 Write minimal property test for pagination consistency
    - Test with 5-10 records and page size of 3
    - **Property 20: Pagination Consistency**
    - **Validates: Requirements 8.3, 8.4**

- [x] 19. Final checkpoint - End-to-end testing
  - Test complete flow: Create payment → View history → Download invoice
  - Test admin flow: View all payments → Filter → Export analytics
  - Test access control: Team manager can't see others' payments
  - Test event program export includes payment balance
  - Ensure all tests pass, ask the user if questions arise.

- [x] 20. Update documentation
  - Update API documentation with new endpoints
  - Update user guide with payment history feature
  - Update admin guide with payment analytics feature
  - _Requirements: All_

## Notes

- All tests are required but use minimal test data (2-5 records) for consistency checking
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties with small datasets
- Unit tests validate specific examples and edge cases
- Integration tests verify API endpoints work correctly
