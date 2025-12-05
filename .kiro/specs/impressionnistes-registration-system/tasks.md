# Implementation Plan - Course des Impressionnistes Registration System

## VERSION 1 (MVP) - Core Registration System

### 0. Prerequisites and Local Development Setup ✅ COMPLETED

- [x] 0.1 Verify local development environment
- [x] 0.2 Set up AWS account prerequisites
- [x] 0.3 Set up external service accounts

### 1. Project Setup and Infrastructure Foundation ✅ COMPLETED

- [x] 1.1 Initialize project structure and development environment
- [x] 1.2 Set up AWS CDK infrastructure project
- [x] 1.3 Implement DynamoDB table with single-table design
- [x] 1.4 Create shared backend utilities and configuration management
- [x] 1.5 Set up CloudWatch logging and monitoring infrastructure

### 2. Authentication and User Management ✅ COMPLETED

- [x] 2.1 Implement Amazon Cognito user pool and authentication
- [x] 2.2 Create team manager registration and profile management
- [x] 2.3 Build frontend authentication components

### 3. Crew Member Management

- [x] 3.1 Implement crew member data model and validation
- [x] 3.2 Create crew member CRUD Lambda functions
- [x] 3.3 Build crew member management frontend components

- [x] 3.4 Implement license number uniqueness validation
  - Add GSI3 (License Number Uniqueness Index) to DynamoDB table in CDK
  - Update crew member creation Lambda to check for duplicate license numbers using GSI3
  - Return 409 Conflict error with clear message when duplicate detected
  - Ensure uniqueness check is performed atomically before creating crew member
  - Update crew member update Lambda to check for duplicates when license number changes
  - _Requirements: FR-2.4, FR-2.5_
  - _Validates: Property 1 - License Number Uniqueness_

- [ ] 3.5 Write property test for license number uniqueness
  - **Feature: impressionnistes-registration-system, Property 1: License Number Uniqueness**
  - Generate random crew members with random license numbers
  - Attempt to add a second crew member with the same license number
  - Verify the system rejects the duplicate and returns 409 Conflict error
  - Test across different team managers to ensure competition-wide uniqueness
  - **Validates: Requirements FR-2.4, FR-2.5**

### 4. Race Configuration and Management ✅ COMPLETED

- [x] 4.1 Initialize race definitions in DynamoDB
- [x] 4.2 Implement race eligibility calculation engine

### 5. Boat Registration and Seat Assignment ✅ COMPLETED

- [x] 5.1 Implement boat registration data model
- [x] 5.2 Create boat registration CRUD Lambda functions
- [x] 5.3 Build boat registration frontend components
- [x] 5.4 Implement seat assignment and validation logic

### 6. Pricing Calculation Engine ✅ COMPLETED

- [x] 6.1 Implement backend pricing calculation
  - Create pricing calculation utility in shared/pricing.py
  - Implement base seat pricing logic (Base_Seat_Price per seat)
  - Add multi-club crew detection and surcharge calculation
  - Implement boat rental pricing (2.5x for skiffs, Base_Seat_Price per seat for crew boats)
  - Create detailed price breakdown structure (base, rental, multi-club, total)
  - Add pricing configuration retrieval from DynamoDB
  - Convert all prices to Decimal for DynamoDB compatibility
  - _Requirements: FR-4.2, FR-8.6, FR-9.2, FR-9.3, FR-9.5_

- [x] 6.2 Add pricing to boat registration endpoints
  - Update get_boat_registration to include calculated pricing
  - Update list_boat_registrations to include pricing for each boat
  - Add price locking when boat status becomes "complete"
  - Ensure server-side price calculation (never trust frontend)
  - _Requirements: FR-4.2, FR-9.2_

### 7. Payment Page and Cart System ✅ COMPLETED

- [x] 7.1 Create payment page frontend
  - Create PaymentPage.vue as main payment interface
  - Display list of "complete" boats (ready for payment)
  - Add checkbox selection for boats to pay
  - Implement "Select All" / "Deselect All" functionality
  - Show price breakdown per boat (base, rental, multi-club)
  - Display running total that updates with selection
  - Add empty state when no boats ready for payment
  - _Requirements: FR-4.1, FR-4.2_

- [x] 7.2 Build payment components
  - Create BoatPaymentCard.vue for each boat in payment list
  - Display boat details (event, boat type, race, crew count)
  - Show itemized price breakdown
  - Add visual indicators for rental and multi-club fees
  - Create PaymentSummary.vue for total calculation
  - Show grand total with currency formatting
  - _Requirements: FR-4.2, FR-4.3_

- [x] 7.3 Implement payment store (Pinia)
  - Create paymentStore.js for payment state management
  - Add actions to fetch boats ready for payment
  - Implement selection state management
  - Add total calculation logic
  - Create payment submission action
  - Handle payment success/failure states
  - _Requirements: FR-4.1, FR-4.3_

### 8. Stripe Payment Integration ✅ FULLY COMPLETED

- [x] 8.1 Set up Stripe backend infrastructure
  - Add Stripe SDK to Lambda layer dependencies
  - Configure Stripe API keys in AWS Secrets Manager
  - Create Stripe client initialization utility
  - Set up Stripe webhook endpoint in API Gateway
  - Implement webhook signature verification
  - _Requirements: FR-4.6, NFR-3.1, NFR-3.2_

- [x] 8.2 Implement payment Lambda functions
  - Create create_payment_intent Lambda
    - Validate boat ownership and "complete" status
    - Calculate total amount server-side
    - Create Stripe Payment Intent with metadata
    - Return client_secret to frontend
  - Create confirm_payment Lambda (webhook handler)
    - Verify webhook signature
    - Handle payment_intent.succeeded event
    - Update boat status to "paid" in DynamoDB
    - Store payment record with Stripe payment_intent_id
    - Handle payment_intent.payment_failed event
  - Add get_payment_receipt Lambda
    - Retrieve payment details from DynamoDB
    - Return receipt data with Stripe receipt URL
  - _Requirements: FR-4.6, FR-4.7_

- [x] 8.3 Create payment data model
  - Design payment record structure in DynamoDB
  - Store: payment_id, stripe_payment_intent_id, amount, currency
  - Store: boat_registration_ids (array), team_manager_id
  - Store: paid_at timestamp, stripe_receipt_url
  - Add payment status tracking (pending, succeeded, failed)
  - _Requirements: FR-4.3, FR-4.4_

- [x] 8.4 Build Stripe checkout frontend
  - Create StripeCheckout.vue component
  - Integrate Stripe.js and Stripe Elements
  - Implement payment form with card element
  - Add payment submission with loading states
  - Handle 3D Secure authentication flow
  - Display payment errors clearly
  - Show success confirmation with receipt link
  - _Requirements: FR-4.6, FR-4.7_

- [x] 8.5 Configure Stripe email receipts
  - Enable automatic receipt emails in Stripe dashboard
  - Configure receipt email branding (logo, colors)
  - Set receipt email language based on user preference
  - Test receipt email delivery
  - _Requirements: FR-4.7_

### 9. Post-Payment Boat Management

- [x] 9.1 Implement paid boat editing rules ✅ COMPLETED
  - ✅ Prevent deletion of paid boats (already implemented)
  - ✅ Boat type cannot be changed (not editable in UI by design - set at creation)
  - ✅ Race changes allowed on paid boats (already working)
  - ✅ Crew member changes allowed on paid boats (already working)
  - ✅ Seat reassignments allowed on paid boats (already working)
  - _Requirements: FR-4.5_
  - _Note: No additional work needed - current implementation already supports the desired behavior_

- [x] 9.2 Update boat list to show payment status ✅ COMPLETED
  - ✅ Add "Paid" status badge to boat cards (already implemented)
  - ✅ Filter paid boats from payment page (already implemented in paymentStore)
  - ✅ Show payment date on boat details (added to boat cards)
  - ✅ Add visual distinction for paid boats (enhanced with gradient background and shadow)
  - ✅ Update boat status filter to include "paid" (added dropdown filter)
  - _Requirements: FR-4.3_

### 10. Admin Mode - Configuration Management (PRIORITY)

- [x] 10.1 Implement admin data model and access control ✅ COMPLETED
  - Add admin role to Cognito user groups (already exists)
  - Create admin authorization middleware for Lambda functions (already exists)
  - Implement admin-only route guards in frontend ✅
  - Add admin menu/navigation in frontend ✅
  - Created AdminDashboard.vue component ✅
  - Added translations for admin section ✅
  - Fixed Cognito groups extraction in Callback.vue ✅
  - _Requirements: FR-5.1, FR-10.1_

- [x] 10.2 Backend: Event date configuration ✅ COMPLETED
  - Create get_event_config Lambda to retrieve event dates ✅
  - Create update_event_config Lambda (admin only) ✅
  - Store event configuration in DynamoDB (event_id, date, registration_open, registration_close) ✅
  - Add validation for date ranges (close > open, event > close) ✅
  - Added API Gateway routes: GET/PUT /admin/event-config ✅
  - Deployed to AWS successfully ✅
  - _Requirements: FR-5.1, FR-10.1, FR-10.2_

- [x] 10.3 Frontend: Event date configuration ✅ COMPLETED
  - Create AdminEventConfig.vue component ✅
  - Display current event dates in editable form ✅
  - Add date pickers for registration open/close dates ✅
  - Show validation errors for invalid date ranges ✅
  - Add save/cancel functionality with confirmation ✅
  - Added route /admin/events with admin guard ✅
  - Added French and English translations ✅
  - Connected to backend API ✅
  - _Requirements: FR-5.1, FR-10.1, FR-10.2_

- [x] 10.4 Backend: Pricing configuration ✅ COMPLETED
  - Create get_pricing_config Lambda to retrieve all pricing ✅
  - Create update_pricing_config Lambda (admin only) ✅
  - Store pricing in DynamoDB (base_seat_price, boat_rental_multiplier_skiff, boat_rental_price_crew) ✅
  - Add validation for positive numbers and reasonable ranges ✅
  - Added API routes GET/PUT /admin/pricing-config ✅
  - _Requirements: FR-5.2, FR-9.2, FR-9.3, FR-10.3_

- [x] 10.5 Frontend: Pricing configuration ✅ COMPLETED
  - Create AdminPricingConfig.vue component ✅
  - Display base seat price editor ✅
  - Add boat rental multiplier editor (skiff) ✅
  - Add crew boat rental price editor ✅
  - Add save/cancel functionality with confirmation ✅
  - Display pricing preview/calculator ✅
  - Added route /admin/pricing with admin guard ✅
  - Added French and English translations ✅
  - Connected to backend API ✅
  - _Requirements: FR-5.2, FR-9.2, FR-9.3, FR-10.3_

- [x] 10.6 Backend: Boat inventory management ✅ COMPLETED
  - Create boat_inventory data model in DynamoDB ✅
  - Implement create_boat Lambda (admin only) - boat_id, boat_type, boat_name, status ✅
  - Implement update_boat Lambda (admin only) - update name, status, requester ✅
  - Implement delete_boat Lambda (admin only) - with validation (cannot delete confirmed) ✅
  - Create list_boats Lambda (admin only) - list all boats with filters ✅
  - Added API routes: POST/GET /admin/boats, PUT/DELETE /admin/boats/{boat_id} ✅
  - Boat statuses: new, available, requested, confirmed ✅
  - Boat types: skiff, 4-, 4+, 4x-, 4x+, 8+, 8x+ ✅
  - _Requirements: FR-8.1, FR-10.4_

- [x] 10.7 Frontend: Boat inventory management ✅ COMPLETED
  - Create AdminBoatInventory.vue component ✅
  - Display list of all boats with type, name, status, requester ✅
  - Add "Add Boat" button with modal form (boat type, name, initial status) ✅
  - Implement inline editing for boat name and status ✅
  - Add delete button with confirmation dialog ✅
  - Show boat availability status with color-coded badges ✅
  - Add filters by boat type and status ✅
  - Added route /admin/boats with admin guard ✅
  - Added French and English translations ✅
  - Connected to backend API ✅
  - _Requirements: FR-8.1, FR-10.4_

- [ ] 10.8 Backend: Data export for admin
  - Create export_crew_members Lambda (admin only) - CSV with all crew details
  - Create export_boat_registrations Lambda (admin only) - CSV with boat and race details
  - Add filtering options (by event, by race, by payment status)
  - Implement CSV generation with proper formatting
  - Return downloadable file or S3 URL
  - _Requirements: FR-7.2, FR-10.5_

- [ ] 10.9 Frontend: Data export interface
  - Create AdminDataExport.vue component
  - Add export type selector (crew members, boat registrations)
  - Implement filter options (event, race, payment status)
  - Add "Export" button that triggers download
  - Show export progress/loading state
  - Display success message with download link
  - _Requirements: FR-7.2, FR-10.5_

- [ ] 10.10 Create admin dashboard landing page
  - Create AdminDashboard.vue as main admin page
  - Add navigation to all admin sections (events, pricing, boats, exports)
  - Display quick stats (total registrations, total payments, boats available)
  - Add links to configuration sections
  - Show recent activity or alerts
  - _Requirements: FR-10.1_

### 11. Boat Rental Management

- [ ] 11.1 Implement boat rental data model and availability tracking
  - Create rental request tracking in DynamoDB (pending, confirmed, rejected)
  - Add rental priority period logic (15 days before closure)
  - Create RCPM member priority validation
  - Implement automatic confirmation after priority period
  - Link rental requests to boat inventory from admin section
  - _Requirements: FR-8.1, FR-8.2, FR-8.3, FR-8.4_

- [ ] 11.2 Create boat rental Lambda functions
  - Implement request_boat_rental Lambda with availability check
  - Create confirm_boat_rental Lambda for admin approval
  - Implement list_boat_rentals Lambda for admin management
  - Add automatic rental confirmation scheduler
  - Create rental fee calculation and integration with payment
  - Update boat inventory status when rental confirmed
  - _Requirements: FR-8.2, FR-8.4, FR-8.5, FR-8.6, FR-8.7, FR-8.8_

- [ ] 11.3 Build boat rental frontend components
  - Create BoatRentalRequest.vue for external clubs
  - Add boat availability display with real-time updates (from inventory)
  - Create admin boat rental management interface
  - Implement rental status tracking and notifications
  - Add rental fee display in payment summary
  - _Requirements: FR-8.1, FR-8.5, FR-8.7_

### 12. Home Page and Public Information ✅ COMPLETED

- [x] 11.1 Create home page with competition information ✅ COMPLETED
  - Build HomePage.vue with competition overview ✅
  - Add event descriptions (21km and 42km) ✅
  - Display race categories and boat types ✅
  - Create registration process explanation ✅
  - Add pricing information display ✅
  - Show important dates and deadlines ✅
  - Add contact email link (no contact form in V1) ✅
  - _Requirements: FR-11.1, FR-11.2, FR-11.4_

- [x] 11.2 Implement navigation and language switching ✅ COMPLETED
  - Create Navigation in App.vue with authentication-aware menu ✅
  - Build LanguageSwitcher.vue for French/English switching ✅
  - Implement browser language detection ✅
  - Add language persistence in user preferences ✅
  - Create multilingual routing ✅
  - _Requirements: FR-11.3, FR-11.5, NFR-4.1, NFR-4.2, NFR-4.3_

### 13. Internationalization (i18n) ✅ COMPLETED

- [x] 12.1 Set up Vue i18n infrastructure ✅ COMPLETED
  - Configure Vue i18n plugin with French and English locales ✅
  - Create translation file structure (fr.json, en.json) ✅
  - Implement language detection and fallback logic ✅
  - Add language switching functionality ✅
  - Create translation helper utilities ✅
  - _Requirements: NFR-4.1, NFR-4.2, NFR-4.3_

- [x] 12.2 Create comprehensive translation files ✅ COMPLETED
  - Translate all UI components and labels ✅
  - Create error message translations ✅
  - Add validation message translations ✅
  - Translate email templates - TODO: When email system is implemented
  - Create notification message translations - TODO: When notification system is implemented
  - Add home page content translations ✅
  - _Requirements: NFR-4.1, NFR-4.5, FR-11.5_

### 14. Additional Data Export Features (Beyond Admin Exports)

- [ ] 14.1 Implement advanced export formats
  - Add Excel format support (beyond CSV)
  - Add JSON format for API integrations
  - Create export templates for race timing systems
  - Implement custom field selection for exports
  - Add export scheduling for recurring reports
  - _Requirements: FR-7.2_

- [ ] 14.2 Build public export interface (if needed)
  - Create public-facing export page for race results
  - Add export history tracking
  - Implement export notifications
  - _Requirements: FR-7.2_

### 15. Frontend Application Structure ✅ COMPLETED

- [x] 14.1 Set up Vue.js 3 application with Vite ✅ COMPLETED
  - Initialize Vite project with Vue 3 ✅
  - Configure Vue Router with authentication guards ✅
  - Set up Pinia stores for state management ✅
  - Configure Axios for API communication ✅
  - Add environment variable configuration ✅
  - Set up development and production builds ✅
  - _Requirements: TC-1.4, NFR-1.1, NFR-1.2_

- [x] 14.2 Create main application views ✅ COMPLETED
  - Build HomePage.vue for public landing page ✅
  - Create DashboardView.vue for team managers ✅
  - Build boat registration workflow (BoatDetail.vue) ✅
  - Implement responsive layouts for mobile/tablet/desktop ✅
  - Add loading states and error boundaries ✅
  - _Requirements: NFR-4.4, NFR-4.5_

- [x] 14.3 Implement common UI components ✅ COMPLETED
  - Create reusable form components (CrewMemberForm, BoatRegistrationForm) ✅
  - Build button components with loading states ✅
  - Create modal/dialog components ✅
  - Implement toast notification component (error messages) ✅
  - Add loading spinner and skeleton screens ✅
  - Create error message display components ✅
  - _Requirements: NFR-5.2_

### 16. API Gateway Integration

- [x] 15.1 Set up API Gateway REST API ✅ COMPLETED
  - Create API Gateway REST API with CORS configuration
  - Configure API Gateway stages (dev, prod)
  - Set up API Gateway authorizers with Cognito
  - Implement request/response transformations
  - Add API Gateway logging and monitoring
  - _Requirements: TC-1.1, NFR-3.2_

- [x] 15.2 Implement API Gateway routes ✅ PARTIALLY COMPLETED
  - Create authentication endpoints (/auth/*) ✅
  - Add crew member endpoints (/crew/*) ✅
  - Create boat registration endpoints (/boat/*) ✅
  - Create race endpoints (/races) ✅
  - Implement payment endpoints (/payment/*) - TODO
  - Add boat rental endpoints (/rentals/*) - TODO
  - _Requirements: TC-1.5_

### 17. Frontend Deployment and CDN ✅ COMPLETED

- [x] 16.1 Set up S3 bucket for static website hosting ✅ COMPLETED
  - Create S3 bucket with static website configuration ✅
  - Configure bucket policies via Origin Access Identity (more secure than public) ✅
  - Set up bucket versioning for rollback capability ✅
  - Implement lifecycle policies for old versions ✅
  - Add bucket encryption (S3_MANAGED) ✅
  - _Requirements: TC-1.4_
  - _Implementation: infrastructure/stacks/frontend_stack.py_

- [x] 16.2 Configure CloudFront distribution ✅ COMPLETED
  - Create CloudFront distribution with S3 origin ✅
  - Configure Origin Access Identity for secure S3 access ✅
  - Set up cache behaviors and TTLs (CACHING_OPTIMIZED policy) ✅
  - Add HTTPS enforcement (REDIRECT_TO_HTTPS) ✅
  - Configure error pages and redirects (404/403 → index.html for SPA) ✅
  - Note: Custom domain and SSL certificate deferred to production setup
  - _Requirements: TC-1.4, NFR-1.1, NFR-3.2_
  - _Implementation: infrastructure/stacks/frontend_stack.py_

- [x] 16.3 Implement frontend build and deployment pipeline ✅ COMPLETED
  - Create build script for production optimization (Makefile: build-frontend) ✅
  - Implement asset minification and compression (Vite handles automatically) ✅
  - Add cache busting for static assets (Vite hashed filenames) ✅
  - Create deployment in CDK with BucketDeployment ✅
  - Implement CloudFront cache invalidation (distribution_paths=["/*"]) ✅
  - Added environment variable handling (.env.production with CloudFront URL) ✅
  - Updated Cognito callback URLs to include CloudFront domain ✅
  - _Requirements: TC-2.1, NFR-1.1_
  - _Implementation: infrastructure/Makefile (build-frontend, deploy-frontend), infrastructure/stacks/frontend_stack.py, infrastructure/stacks/auth_stack.py, infrastructure/app.py_

### 18. Basic Email Notifications (Essential Only)

- [ ] 17.1 Set up AWS SES for email delivery
  - Configure SES domain verification
  - Create essential email templates (registration confirmation, payment confirmation)
  - Implement multilingual email templates (French/English)
  - Set up email sending Lambda function
  - Configure bounce and complaint handling
  - _Requirements: NFR-6.1, NFR-6.5_

- [ ] 17.2 Implement essential notification Lambda functions
  - Create send_notification Lambda for immediate notifications
  - Implement payment confirmation emails
  - Add registration confirmation emails
  - Implement notification tracking in DynamoDB
  - _Requirements: NFR-6.1_

### 19. Error Handling and Resilience

- [ ] 18.1 Implement comprehensive error handling
  - Create standardized error response format
  - Implement frontend global error handler
  - Add backend Lambda error handling wrappers
  - Create user-friendly error messages
  - Implement error logging and tracking
  - _Requirements: NFR-5.2_

- [ ] 18.2 Add retry logic and circuit breakers
  - Implement exponential backoff for API retries
  - Add circuit breaker for external service calls (Stripe)
  - Create fallback mechanisms for service failures
  - Implement graceful degradation
  - Add timeout handling for long-running operations
  - _Requirements: NFR-5.3, NFR-5.4_

### 20. Security Implementation

- [ ] 19.1 Implement input sanitization and validation
  - Create input sanitization utilities to prevent XSS
  - Add CSRF protection for state-changing operations
  - Create rate limiting for API endpoints
  - Implement request size limits
  - _Requirements: NFR-3.1, NFR-3.2_

- [ ] 19.2 Configure encryption and secure communication
  - Verify DynamoDB encryption at rest
  - Ensure all API Gateway endpoints use HTTPS
  - Implement secure environment variable management
  - Add Secrets Manager for sensitive credentials (Stripe keys)
  - _Requirements: NFR-3.1, NFR-3.2_

### 21. Testing and Quality Assurance

- [ ] 20.1 Create integration test suite
  - Write integration tests for complete registration flow
  - Create payment processing integration tests
  - Add boat rental workflow integration tests
  - _Requirements: General quality assurance_

- [ ] 20.2 Perform load and performance testing
  - Create load testing scenarios
  - Test concurrent user scenarios (100-200 users)
  - Validate payment processing under load
  - Test DynamoDB throughput
  - _Requirements: NFR-1.1, NFR-1.3, NFR-2.1_

### 22. Production Deployment (V1)

- [ ] 21.1 Production environment setup
  - Create production AWS environment
  - Configure production domain and SSL certificates
  - Set up production Stripe account
  - Configure production SES and verify domain
  - Deploy production infrastructure with CDK
  - _Requirements: TC-1.1, TC-2.1_

- [ ] 21.2 Production monitoring and backup
  - Configure production CloudWatch dashboards
  - Set up critical alarms for Lambda errors, DynamoDB throttling
  - Verify DynamoDB point-in-time recovery is enabled
  - Test backup restoration procedures
  - _Requirements: TC-3.1, TC-3.2, TC-2.2_

- [ ] 21.3 Production launch
  - Conduct UAT with RCPM stakeholders
  - Create user training materials
  - Perform production smoke tests
  - Plan go-live and rollback strategies
  - Execute production launch
  - _Requirements: NFR-5.1_

---

## VERSION 2 - Enhanced Features

### 23. Payment History and Advanced Features

- [ ] 22.1 Implement payment history page
  - Create PaymentHistory.vue to display all payments
  - Show payment date, amount, boats included
  - Add download receipt functionality
  - Display payment method and status
  - Implement filtering by date range
  - _Requirements: FR-4.3, FR-4.7_

- [ ] 22.2 Add payment receipt generation
  - Create receipt PDF generation Lambda
  - Include itemized breakdown in receipt
  - Add RCPM branding to receipts
  - Store receipts in S3 for download
  - Implement receipt email sending (beyond Stripe)
  - _Requirements: FR-4.7_

### 24. Advanced Admin Configuration (V2)

- [ ] 23.1 Implement admin configuration Lambda functions
  - Create get_configuration Lambda for retrieving all config types
  - Implement update_configuration Lambda with validation
  - Add configuration change audit logging
  - Create configuration validation rules (date ranges, pricing)
  - Implement admin confirmation for impactful changes
  - _Requirements: FR-5.1, FR-5.2, FR-5.4, FR-5.5, FR-10.1-FR-10.8_

- [ ] 23.2 Build admin configuration frontend interface
  - Create ConfigurationPanel.vue with tabbed sections
  - Add system configuration editor (dates, periods)
  - Create pricing configuration editor
  - Implement notification settings editor
  - Add race configuration management
  - Display configuration change history
  - _Requirements: FR-5.1, FR-5.2, FR-10.1, FR-10.2, FR-10.3_

### 25. Registration Validation and Admin Management

- [ ] 24.1 Implement registration validation Lambda functions
  - Create get_all_registrations Lambda for admin review
  - Implement flag_registration_issue Lambda with notification trigger
  - Create resolve_flagged_issue Lambda for team manager actions
  - Implement grant_editing_access Lambda with time limits
  - Add manual registration editing for admins
  - _Requirements: FR-6.1, FR-6.2, FR-6.3, FR-6.4, FR-6.5, FR-6.6_

- [ ] 24.2 Build admin validation frontend interface
  - Create RegistrationValidation.vue with filterable list
  - Add issue flagging interface with notification preview
  - Create editing access grant interface with time limits
  - Implement manual registration editing for admins
  - Display validation status indicators
  - Add bulk operations for common admin tasks
  - _Requirements: FR-6.1, FR-6.2, FR-6.5, FR-6.6_

- [ ] 24.3 Create admin dashboard with real-time statistics
  - Implement get_dashboard_stats Lambda with aggregations
  - Create Dashboard.vue with key metrics display
  - Add participant counts by category
  - Display payment status and financial summary
  - Show registration progress over time
  - Add boat rental status overview
  - _Requirements: FR-7.1, FR-7.3, FR-7.4_

### 26. Advanced Reporting and Analytics

- [ ] 25.1 Implement advanced reporting Lambda functions
  - Create export_payments Lambda for financial reports
  - Implement multi_club_crew revenue reporting
  - Add financial reports with revenue breakdown
  - Create audit log export functionality
  - _Requirements: FR-7.2, FR-9.7_

- [ ] 25.2 Build advanced reporting frontend interface
  - Create AdvancedReports.vue with multiple report types
  - Add date range filtering for reports
  - Display multi_club_crew statistics
  - Add audit log viewer for admin actions
  - Create financial dashboards
  - _Requirements: FR-7.2, FR-7.5, FR-9.6, FR-9.7_

### 27. Enhanced Notification System

- [ ] 26.1 Implement advanced notification features
  - Create schedule_notifications Lambda for recurring alerts
  - Implement process_notification_queue Lambda for batch processing
  - Add notification frequency management
  - Create notification preferences interface
  - _Requirements: NFR-6.2, NFR-6.3, NFR-6.4_

- [ ] 26.2 Set up EventBridge schedulers for automated notifications
  - Create daily notification check scheduler
  - Implement payment reminder scheduler
  - Add deadline warning scheduler
  - Create recurring issue notification scheduler
  - Implement daily summary scheduler
  - _Requirements: NFR-6.2, NFR-6.3_

- [ ] 26.3 Build notification center frontend component
  - Create NotificationCenter.vue with message history
  - Add unread notification counter in navigation
  - Implement notification filtering and search
  - Add real-time notification updates
  - _Requirements: NFR-6.4, FR-11.7_

### 28. Slack Integration for Admin and DevOps

- [ ] 27.1 Implement Slack webhook configuration
  - Add Slack webhook URL fields to notification config
  - Create webhook validation and testing functionality
  - Implement secure storage of webhook URLs
  - Add test notification sending capability
  - _Requirements: NFR-6.6, NFR-6.7_

- [ ] 27.2 Implement Slack notification Lambda function
  - Create send_slack_notification function with webhook integration
  - Implement Slack message block builders for different event types
  - Add rate limiting to prevent API abuse
  - Create CloudWatch metrics tracking for Slack notifications
  - Implement error handling and fallback mechanisms
  - _Requirements: NFR-6.6, NFR-6.7_

- [ ] 27.3 Integrate Slack notifications into event handlers
  - Add Slack notifications to boat registration events
  - Implement payment completion Slack alerts
  - Create boat rental request notifications
  - Add system error notifications to DevOps channel
  - Implement daily summary Slack messages
  - _Requirements: NFR-6.6, NFR-6.7_

### 29. Contact Us Feature

- [ ] 28.1 Implement contact form Lambda function
  - Create submit_contact_form Lambda with validation
  - Implement email sending to admin contact address
  - Add auto-reply email to user
  - Create Slack notification for contact submissions
  - Implement contact form logging in DynamoDB
  - _Requirements: FR-12.1, FR-12.2, FR-12.3, FR-12.4, FR-12.5, FR-12.6_

- [ ] 28.2 Build contact form frontend component
  - Create ContactForm.vue with all required fields
  - Add subject selection dropdown
  - Implement form validation and error handling
  - Create multilingual contact form (French/English)
  - Add user context pre-filling for authenticated users
  - Display contact information and alternative contact methods
  - _Requirements: FR-12.1, FR-12.7, FR-12.8_

### 30. GDPR Compliance Features

- [ ] 29.1 Implement GDPR compliance features
  - Create data deletion request handler
  - Implement user data anonymization
  - Add data export functionality for user requests
  - Create consent management system
  - Implement audit logging for data access
  - _Requirements: NFR-3.4_

- [ ] 29.2 Create privacy and legal pages
  - Create privacy policy and terms of service
  - Set up cookie consent management
  - Implement data retention policies
  - Document compliance procedures
  - _Requirements: NFR-3.4_

### 31. Performance Optimization

- [ ] 30.1 Implement frontend performance optimizations
  - Add code splitting for route-based lazy loading
  - Implement component lazy loading
  - Create service worker for offline support
  - Add asset preloading and prefetching
  - Implement virtual scrolling for large lists
  - Optimize images and assets
  - _Requirements: NFR-1.1, NFR-1.2_

- [ ] 30.2 Optimize backend Lambda functions
  - Implement connection pooling for DynamoDB
  - Add Lambda function warming to reduce cold starts
  - Optimize Lambda memory allocation
  - Implement caching for frequently accessed data
  - Add batch operations for bulk updates
  - _Requirements: NFR-1.2, NFR-1.3, NFR-2.1_

- [ ] 30.3 Implement DynamoDB query optimization
  - Use GSI indexes for efficient queries
  - Implement pagination for large result sets
  - Add DynamoDB query result caching
  - Optimize partition key design for even distribution
  - Implement batch get operations
  - _Requirements: NFR-1.2, NFR-2.3_

### 32. Advanced Testing

- [ ] 31.1 Implement end-to-end testing
  - Set up Cypress for E2E testing
  - Create E2E tests for user registration and login
  - Write E2E tests for crew member and boat registration
  - Add E2E tests for payment flow
  - Create E2E tests for admin workflows
  - _Requirements: General quality assurance_

- [ ] 31.2 Advanced load testing
  - Test concurrent user scenarios (1000+ users)
  - Validate system under peak load
  - Measure and optimize page load times
  - Test DynamoDB auto-scaling
  - _Requirements: NFR-1.1, NFR-1.3, NFR-2.1_

### 33. DevOps Utilities and Tools

- [ ] 32.1 Create DevOps configuration access tools
  - Build CLI tool for emergency configuration updates
  - Implement configuration backup and restore scripts
  - Create database query utilities for DevOps
  - Add system health check scripts
  - Implement log analysis tools
  - _Requirements: TC-4.5, TC-4.6_

- [ ] 32.2 Set up advanced deployment automation
  - Implement blue-green deployment strategy
  - Add rollback procedures and scripts
  - Create deployment validation tests
  - Implement automated smoke tests post-deployment
  - _Requirements: TC-2.1, TC-2.4_

### 34. Documentation

- [ ] 33.1 Create comprehensive API documentation
  - Document all API endpoints with request/response examples
  - Create authentication flow documentation
  - Add error code reference guide
  - Document rate limits and quotas
  - Create integration examples
  - _Requirements: General best practice_

- [ ] 33.2 Write deployment and operations guides
  - Create infrastructure deployment guide
  - Write configuration management guide
  - Document backup and restore procedures
  - Create troubleshooting guide
  - Add monitoring and alerting guide
  - _Requirements: TC-2.1, TC-3.1_

---

## Notes

### V1 Scope (MVP)
V1 focuses on the core registration system with essential features:
- User authentication and crew/boat management
- Race eligibility and seat assignment
- Payment processing with Stripe
- **Admin mode (PRIORITY before boat rental):**
  - Event date configuration
  - Pricing configuration
  - Boat inventory management
  - Data exports (crew members, boat registrations)
- Boat rental management (depends on admin boat inventory)
- Basic home page with contact email link
- Frontend deployment
- Essential email notifications only
- Basic security and error handling

### V2 Scope (Enhancements)
V2 adds advanced features and optimizations:
- Admin configuration management
- Advanced validation and admin tools
- Enhanced reporting and analytics
- Full notification system with scheduling
- Slack integration
- Contact form feature
- GDPR compliance features
- Performance optimizations
- Advanced testing
- DevOps tools
- Comprehensive documentation

### Migration Notes
- All completed tasks remain marked as completed
- API Gateway routes partially completed (auth, crew, boat, races done; payment and rentals pending)
- Frontend structure partially completed (Vite setup done; main views pending)
- Tasks reorganized by priority for V1 launch
- V2 tasks can be implemented incrementally after V1 launch
