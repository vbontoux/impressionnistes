# Implementation Plan - Course des Impressionnistes Registration System

## Overview

This implementation plan is organized into two versions:
- **V1 (Tasks 1-99)**: Core MVP features required for production launch
- **V2 (Tasks 100+)**: Enhanced features and optimizations for future releases

Tasks are marked with status:
- ✅ **COMPLETED**: Fully implemented and tested
- 🔄 **IN PROGRESS**: Currently being worked on
- ⏸️ **PARTIALLY COMPLETED**: Some sub-tasks done, others remaining
- ⏳ **PENDING**: Not yet started

---

## V1 - PRODUCTION MVP

### COMPLETED TASKS ✅

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
- [x] 2.2 Create club manager registration and profile management
- [x] 2.3 Build frontend authentication components

### 3. Crew Member Management ✅ PARTIALLY COMPLETED

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
  - Store: boat_registration_ids (array), club_manager_id
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

### 9. Post-Payment Boat Management ✅ COMPLETED

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

### 10. Admin Mode - Configuration Management ✅ COMPLETED

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

### 11. Boat Rental Management ✅ COMPLETED

- [x] 11.1 Add recommended rower weight field to rental boat data model
  - Update create_rental_boat Lambda to accept rower_weight_range (text field, optional)
  - Update update_rental_boat Lambda to allow editing rower_weight_range
  - Add rower_weight_range to rental boat database schema (e.g., "70-90kg", "60-75kg")
  - Update list_rental_boats Lambda to include rower_weight_range in response
  - Add validation for rower_weight_range format (text, max 50 characters)
  - Add paid_at timestamp field to track when rental is paid
  - Set paid_at automatically when status changes to "paid"
  - _Requirements: FR-8.12, FR-8.13_

- [x] 11.2 Update admin boat inventory UI to include rower weight range
  - Add rower_weight_range field to AdminBoatInventory.vue create form
  - Display rower_weight_range in boat list table
  - Add inline editing for rower_weight_range
  - Add translations for rower weight field (French: "Portance", English: "Weight capacity")
  - Add placeholder text examples (e.g., "70-90kg", "60-75kg")
  - Add help text (French: "Poids moyen recommandé des rameurs", English: "Recommended average rower weight")
  - _Requirements: FR-8.12_

- [x] 11.3 Create club manager boat rental Lambda functions
  - Implement list_available_rental_boats Lambda (club manager accessible)
    - Return boats with status "available" or "new"
    - Exclude boats with status "requested", "confirmed", or "paid"
    - Include boat_type, boat_name, rower_weight_range, status
  - Implement request_rental_boat Lambda (club manager accessible)
    - Validate boat is available (status is "available" or "new")
    - Update rental_boat status to "requested"
    - Store requester (club_manager_id) on rental_boat
    - Store requested_at timestamp
    - Return confirmation with boat details
  - Implement get_my_rental_requests Lambda (club manager accessible)
    - Query boats where requester = authenticated club_manager_id
    - Return list with boat details and current status
  - _Requirements: FR-8.1, FR-8.2, FR-8.3, FR-8.4_

- [x] 11.4 Create admin boat rental management Lambda functions
  - Update list_rental_boats Lambda to support filtering by requester
  - Implement confirm_rental_request Lambda (admin only)
    - Update rental_boat status from "requested" to "confirmed"
    - Store confirmed_by admin_user_id and confirmed_at timestamp
    - Trigger notification to club manager (requester)
  - Implement reject_rental_request Lambda (admin only)
    - Update rental_boat status back to "available"
    - Clear requester field
    - Clear requested_at timestamp
    - Trigger notification to club manager
  - _Requirements: FR-8.7, FR-8.10_

- [x] 11.5 Add API Gateway routes for boat rental
  - Add GET /rental/boats (club manager) - list available boats
  - Add POST /rental/request (club manager) - request a boat (boat_id in request body)
  - Add GET /rental/my-requests (club manager) - get my rental requests
  - Add PUT /admin/rental-boats/{boat_id}/confirm (admin) - confirm request
  - Add PUT /admin/rental-boats/{boat_id}/reject (admin) - reject request
  - Configure Cognito authorization for all routes
  - _Requirements: FR-8.1, FR-8.2, FR-8.7, FR-8.10_

- [x] 11.6 Build club manager boat rental frontend
  - Create BoatRentalPage.vue for club managers
  - Display list of available rental boats with filters (boat type)
  - Show boat details: type, name, weight capacity (portance), status
  - Add "Request Boat" button for each available boat
  - Create request confirmation dialog
  - Display "My Rental Requests" section showing boats where user is requester
  - Show visual indicators for request status (requested, confirmed, rejected/available)
  - Add route /boat-rentals with authentication guard
  - Add translations (French: "Portance", English: "Weight capacity")
  - _Requirements: FR-8.1, FR-8.2, FR-8.3, FR-8.4_

- [x] 11.7 Enhance admin boat inventory to manage rental requests
  - Display requester information in the admin boat inventory table (already done)
  - Admin can change status using existing inline editing (requested → confirmed, or back to available)
  - Display requested_at timestamp for requested boats (if needed)
  - Show confirmed_by and confirmed_at for confirmed boats (if needed)
  - Add filter for "boats with pending requests" (status = "requested") - optional
  - Note: No separate Confirm/Reject buttons needed - admin uses status dropdown
  - _Requirements: FR-8.7, FR-8.10_

- [x] 11.8 Add boat rental payment to payment page
  - Display confirmed rental boats in payment page alongside boat registrations
  - Calculate rental fee: 2.5x Base_Seat_Price for skiffs, Base_Seat_Price per seat for crew boats
  - Allow club managers to select confirmed rentals for payment
  - Display rental fees separately in payment breakdown
  - Include rental fees in total payment calculation
  - Update payment confirmation to mark rental boat status as "paid" and set paid_at timestamp
  - Prevent admin from changing status or deleting paid rental boats
  - _Requirements: FR-8.9, FR-8.11, FR-8.13_

### 12. Home Page and Public Information ✅ COMPLETED

- [x] 12.1 Create home page with competition information ✅ COMPLETED
  - Build HomePage.vue with competition overview ✅
  - Add event descriptions (21km and 42km) ✅
  - Display race categories and boat types ✅
  - Create registration process explanation ✅
  - Add pricing information display ✅
  - Show important dates and deadlines ✅
  - Add contact email link (no contact form in V1) ✅
  - _Requirements: FR-11.1, FR-11.2, FR-11.4_

- [x] 12.2 Implement navigation and language switching ✅ COMPLETED
  - Create Navigation in App.vue with authentication-aware menu ✅
  - Build LanguageSwitcher.vue for French/English switching ✅
  - Implement browser language detection ✅
  - Add language persistence in user preferences ✅
  - Create multilingual routing ✅
  - _Requirements: FR-11.3, FR-11.5, NFR-4.1, NFR-4.2, NFR-4.3_

### 13. Internationalization (i18n) ✅ COMPLETED

- [x] 13.1 Set up Vue i18n infrastructure ✅ COMPLETED
  - Configure Vue i18n plugin with French and English locales ✅
  - Create translation file structure (fr.json, en.json) ✅
  - Implement language detection and fallback logic ✅
  - Add language switching functionality ✅
  - Create translation helper utilities ✅
  - _Requirements: NFR-4.1, NFR-4.2, NFR-4.3_

- [x] 13.2 Create comprehensive translation files ✅ COMPLETED
  - Translate all UI components and labels ✅
  - Create error message translations ✅
  - Add validation message translations ✅
  - Translate email templates - TODO: When email system is implemented
  - Create notification message translations - TODO: When notification system is implemented
  - Add home page content translations ✅
  - _Requirements: NFR-4.1, NFR-4.5, FR-11.5_

### 15. Frontend Application Structure ✅ COMPLETED

- [x] 15.1 Set up Vue.js 3 application with Vite ✅ COMPLETED
  - Initialize Vite project with Vue 3 ✅
  - Configure Vue Router with authentication guards ✅
  - Set up Pinia stores for state management ✅
  - Configure Axios for API communication ✅
  - Add environment variable configuration ✅
  - Set up development and production builds ✅
  - _Requirements: TC-1.4, NFR-1.1, NFR-1.2_

- [x] 15.2 Create main application views ✅ COMPLETED
  - Build HomePage.vue for public landing page ✅
  - Create DashboardView.vue for club managers ✅
  - Build boat registration workflow (BoatDetail.vue) ✅
  - Implement responsive layouts for mobile/tablet/desktop ✅
  - Add loading states and error boundaries ✅
  - _Requirements: NFR-4.4, NFR-4.5_

- [x] 15.3 Implement common UI components ✅ COMPLETED
  - Create reusable form components (CrewMemberForm, BoatRegistrationForm) ✅
  - Build button components with loading states ✅
  - Create modal/dialog components ✅
  - Implement toast notification component (error messages) ✅
  - Add loading spinner and skeleton screens ✅
  - Create error message display components ✅
  - _Requirements: NFR-5.2_

### 16. API Gateway Integration ✅ COMPLETED

- [x] 16.1 Set up API Gateway REST API ✅ COMPLETED
  - Create API Gateway REST API with CORS configuration
  - Configure API Gateway stages (dev, prod)
  - Set up API Gateway authorizers with Cognito
  - Implement request/response transformations
  - Add API Gateway logging and monitoring
  - _Requirements: TC-1.1, NFR-3.2_

- [x] 16.2 Implement API Gateway routes ✅ PARTIALLY COMPLETED
  - Create authentication endpoints (/auth/*) ✅
  - Add crew member endpoints (/crew/*) ✅
  - Create boat registration endpoints (/boat/*) ✅
  - Create race endpoints (/races) ✅
  - Implement payment endpoints (/payment/*) ✅
  - Add boat rental endpoints (/rentals/*) ✅
  - _Requirements: TC-1.5_

### 17. Frontend Deployment and CDN ✅ COMPLETED

- [x] 17.1 Set up S3 bucket for static website hosting ✅ COMPLETED
  - Create S3 bucket with static website configuration ✅
  - Configure bucket policies via Origin Access Identity (more secure than public) ✅
  - Set up bucket versioning for rollback capability ✅
  - Implement lifecycle policies for old versions ✅
  - Add bucket encryption (S3_MANAGED) ✅
  - _Requirements: TC-1.4_
  - _Implementation: infrastructure/stacks/frontend_stack.py_

- [x] 17.2 Configure CloudFront distribution ✅ COMPLETED
  - Create CloudFront distribution with S3 origin ✅
  - Configure Origin Access Identity for secure S3 access ✅
  - Set up cache behaviors and TTLs (CACHING_OPTIMIZED policy) ✅
  - Add HTTPS enforcement (REDIRECT_TO_HTTPS) ✅
  - Configure error pages and redirects (404/403 → index.html for SPA) ✅
  - Note: Custom domain and SSL certificate deferred to production setup
  - _Requirements: TC-1.4, NFR-1.1, NFR-3.2_
  - _Implementation: infrastructure/stacks/frontend_stack.py_

- [x] 17.3 Implement frontend build and deployment pipeline ✅ COMPLETED
  - Create build script for production optimization (Makefile: build-frontend) ✅
  - Implement asset minification and compression (Vite handles automatically) ✅
  - Add cache busting for static assets (Vite hashed filenames) ✅
  - Create deployment in CDK with BucketDeployment ✅
  - Implement CloudFront cache invalidation (distribution_paths=["/*"]) ✅
  - Added environment variable handling (.env.production with CloudFront URL) ✅
  - Updated Cognito callback URLs to include CloudFront domain ✅
  - _Requirements: TC-2.1, NFR-1.1_
  - _Implementation: infrastructure/Makefile (build-frontend, deploy-frontend), infrastructure/stacks/frontend_stack.py, infrastructure/stacks/auth_stack.py, infrastructure/app.py_

---

## V1 - REMAINING TASKS ⏳

### 3. Crew Member Management (Remaining) ⏸️

- [x] 3.5 Write property test for license number uniqueness
  - **Feature: impressionnistes-registration-system, Property 1: License Number Uniqueness**
  - Generate random crew members with random license numbers
  - Attempt to add a second crew member with the same license number
  - Verify the system rejects the duplicate and returns 409 Conflict error
  - Test across different club managers to ensure competition-wide uniqueness
  - **Validates: Requirements FR-2.4, FR-2.5**

### 14. CrewTimer Export Enhancement ✅ COMPLETED

- [x] 14.1 Add CrewTimer export button to admin export page ✅ COMPLETED
  - Added CrewTimer.com icon (favicon from crewtimer.com)
  - Added button to trigger CrewTimer export
  - Added translations for CrewTimer export button (French/English)
  - Implemented in AdminDataExport.vue with prominent card layout
  - _Requirements: FR-7.6_

- [x] 14.2 Implement CrewTimer export backend ✅ COMPLETED
  - Created export_races_json Lambda (admin only)
  - Queries database to retrieve races with all boats that are complete, paid, or free (excludes forfait)
  - Returns JSON data with comprehensive race information
  - Backend provides raw data; frontend handles Excel generation
  - Implemented in functions/admin/export_races_json.py
  - _Requirements: FR-7.6_

- [x] 14.3 Update frontend to download CrewTimer export ✅ COMPLETED
  - Added API call to fetch CrewTimer export data
  - Implemented crewTimerFormatter.js to convert JSON to Excel format
  - Generates Excel file following CrewTimer import specification
  - Maps columns correctly:
    - Event time: empty
    - Event Num: incremental integer (marathon races first, then semi-marathon)
    - Event name: race name
    - Event Abbrev: abbreviated race name
    - Crew: club name
    - Crew Abbrev: abbreviated club name (unique)
    - Stroke: stroke seat crew member last name
    - Bow: incremental bow numbers
    - Race info: "Sprint" for marathon, "Head" for semi-marathon
    - Status: empty
    - Age: average boat age
  - Triggers file download when button is clicked
  - Shows loading state during export generation
  - Displays success/error messages
  - Implemented in frontend/src/utils/exportFormatters/crewTimerFormatter.js
  - _Requirements: FR-7.6_

### 18. Total Participant Limit (400 Max) ⏳

- [ ] 18.1 Add max_total_participants to system configuration
  - Add `max_total_participants` field to system configuration in DynamoDB (default: 400)
  - Update `init_config.py` to include `max_total_participants: 400` in `initialize_system_config()`
  - Update `get_event_config` Lambda to return `max_total_participants`
  - Update `update_event_config` Lambda to allow admins to modify `max_total_participants`
  - Add validation: must be positive integer, reasonable range (100-1000)
  - Update AdminEventConfig.vue to display and allow editing of max participants
  - Add translations for "Maximum Total Participants" field (French: "Nombre maximum de participants")
  - _Requirements: FR-3.1, FR-10.8_

- [ ] 18.2 Implement total participant limit backend
  - Count total crew members in all boats with status "complete", "paid", or "free" (ready to race)
  - When saving a boat (create or update to complete/paid/free status), check if adding this boat would exceed the limit
  - Prevent saving the boat if the total would exceed `max_total_participants` from config
  - Return clear error message: "Cannot save boat: Total participant limit of {max} would be exceeded. Current: {current} participants, this boat adds: {boat_count} participants."
  - Allow admins to bypass limit (with warning)
  - _Requirements: FR-3.1, FR-10.8_

- [ ] 18.3 Implement total participant limit frontend
  - Display current total participant count prominently (e.g., "385/400 participants registered")
  - Show warning banner when approaching limit (e.g., at 90% = 360 participants)
  - Display error message when boat cannot be saved due to limit
  - Show informational message explaining the participant limit
  - Update count in real-time when boats are added/removed/modified
  - _Requirements: FR-3.1, FR-10.8_

### 19. Boat Registration Form Clarity ✅ COMPLETED

- [x] 19.1 Improve boat registration form messaging ✅ COMPLETED
  - When a club manager selects a boat type with no matching races, displays clear detailed message
  - Example: Shows specific reason like "Your crew is women, but only men, mixed races are available for this boat type and event"
  - Explains why no races are available (age category, gender, boat type mismatch)
  - Suggests alternative boat types, event distances, or crew composition adjustments
  - Added expandable help text explaining race eligibility rules (age categories, gender categories, coxswain rules)
  - Implemented in RaceSelector.vue component
  - Added comprehensive translations in English and French
  - _Requirements: FR-3.4, NFR-5.2_

### 20. Mixed Club Display Enhancement ⏳

- [ ] 20.1 Improve mixed club crew display
  - Display club manager's club name prominently
  - Add "Mixed Club" badge or indicator when crew contains external members
  - Show breakdown of clubs represented in the crew
  - Display seat rental fees clearly for external members
  - Add tooltip explaining mixed club pricing
  - _Requirements: FR-9.1, FR-9.5, FR-9.6_

### 21. Registration Period Enforcement with Temporary Access ⏳

- [ ] 21.1 Add temporary access data model
  - Add `temporary_access_expires_at` field to team manager profile (nullable timestamp)
  - When set, club manager can bypass all date restrictions until expiration
  - Store `temporary_access_granted_by` (admin user_id) and `temporary_access_granted_at` for audit
  - Automatically expires when timestamp is reached (no cleanup needed - just check timestamp)
  - _Requirements: FR-2.2, FR-3.6, FR-10.2_

- [ ] 21.2 Implement backend date enforcement with temporary access check
  - Check registration period dates before allowing operations
  - **Registration period ended**: Prevent deletion of boats, prevent adding new boats, allow modifications
  - **Payment period ended**: Prevent all modifications (except admin or temporary access)
  - **Temporary access bypass**: If club manager has `temporary_access_expires_at` > current time, bypass all date restrictions
  - Respect existing limits (e.g., cannot delete paid boats, even with temporary access)
  - Return clear error messages when operations are blocked
  - _Requirements: FR-2.2, FR-3.6, FR-4.1, FR-4.9, FR-10.2_

- [ ] 21.3 Implement admin UI to grant temporary access
  - Add "Grant Temporary Access" button in admin view (e.g., on team manager list or boat details)
  - Simple modal: Select club manager, set expiration (preset options: 24h, 48h, 1 week, or custom date/time)
  - Update team manager record with `temporary_access_expires_at`, `temporary_access_granted_by`, `temporary_access_granted_at`
  - Show list of club managers with active temporary access (expires_at > now)
  - Allow revoking access early (set expires_at to now)
  - _Requirements: FR-10.2_

- [ ] 21.4 Implement frontend date enforcement with temporary access display
  - Check if current user has active temporary access (`temporary_access_expires_at` > now)
  - If temporary access active: Show banner "You have temporary editing access until [date/time]", enable all buttons
  - If no temporary access and registration period ended: Hide "Delete" and "Add New Boat" buttons, show info message
  - If no temporary access and payment period ended: Disable all edit buttons, show "Contact admin for access" message
  - Display registration/payment period dates prominently
  - _Requirements: FR-2.2, FR-3.6, FR-4.1, FR-4.9, FR-10.2_

### 22. Admin Impersonation and Date Override ⏳

- [ ] 22.1 Implement admin impersonation backend
  - Add admin override flag to bypass date restrictions
  - Allow admins to modify boats at any time (before, during, after registration/payment periods)
  - Allow admins to delete boats at any time (except paid boats)
  - Allow admins to add new boats at any time
  - Log all admin actions with timestamps and user identification
  - _Requirements: FR-6.5, FR-10.1_

- [ ] 22.2 Implement admin impersonation frontend
  - Show all edit/delete/add buttons for admins regardless of dates
  - Add visual indicator when admin is bypassing date restrictions
  - Display warning message when admin performs actions outside normal periods
  - Ensure admin can access all functionality at all times
  - _Requirements: FR-6.5, FR-10.1_

### 23. Basic Email Notifications (Essential Only) ⏳

- [ ] 23.1 Set up AWS SES for email delivery
  - Configure SES domain verification
  - Create essential email templates (registration confirmation, payment confirmation)
  - Implement multilingual email templates (French/English)
  - Set up email sending Lambda function
  - Configure bounce and complaint handling
  - _Requirements: NFR-6.1, NFR-6.5_

- [ ] 23.2 Implement essential notification Lambda functions
  - Create send_notification Lambda for immediate notifications
  - Implement payment confirmation emails
  - Add registration confirmation emails
  - Implement notification tracking in DynamoDB
  - _Requirements: NFR-6.1_

### 24. Error Handling and Resilience ⏳

- [ ] 24.1 Implement comprehensive error handling
  - Create standardized error response format
  - Implement frontend global error handler
  - Add backend Lambda error handling wrappers
  - Create user-friendly error messages
  - Implement error logging and tracking
  - _Requirements: NFR-5.2_

- [ ] 24.2 Add retry logic and circuit breakers
  - Implement exponential backoff for API retries
  - Add circuit breaker for external service calls (Stripe)
  - Create fallback mechanisms for service failures
  - Implement graceful degradation
  - Add timeout handling for long-running operations
  - _Requirements: NFR-5.3, NFR-5.4_

### 25. Security Implementation ⏳

- [ ] 25.1 Implement input sanitization and validation
  - Create input sanitization utilities to prevent XSS
  - Add CSRF protection for state-changing operations
  - Create rate limiting for API endpoints
  - Implement request size limits
  - _Requirements: NFR-3.1, NFR-3.2_

- [ ] 25.2 Configure encryption and secure communication
  - Verify DynamoDB encryption at rest
  - Ensure all API Gateway endpoints use HTTPS
  - Implement secure environment variable management
  - Add Secrets Manager for sensitive credentials (Stripe keys)
  - _Requirements: NFR-3.1, NFR-3.2_

### 26. Testing and Quality Assurance ⏳

- [ ] 26.1 Create integration test suite
  - Write integration tests for complete registration flow
  - Create payment processing integration tests
  - Add boat rental workflow integration tests
  - _Requirements: General quality assurance_

- [ ] 26.2 Perform load and performance testing
  - Create load testing scenarios
  - Test concurrent user scenarios (100-200 users)
  - Validate payment processing under load
  - Test DynamoDB throughput
  - _Requirements: NFR-1.1, NFR-1.3, NFR-2.1_

### 27. Production Deployment (V1) ⏸️

- [x] 27.1 Production environment setup
  - Create production AWS environment
  - Configure production domain and SSL certificates
  - Set up production Stripe account
  - Configure production SES and verify domain
  - Deploy production infrastructure with CDK
  - _Requirements: TC-1.1, TC-2.1_

- [ ] 27.2 Production monitoring and backup
  - Configure production CloudWatch dashboards
  - Set up critical alarms for Lambda errors, DynamoDB throttling
  - Verify DynamoDB point-in-time recovery is enabled
  - Test backup restoration procedures
  - _Requirements: TC-3.1, TC-3.2, TC-2.2_

- [ ] 27.3 Production launch
  - Conduct UAT with RCPM stakeholders
  - Create user training materials
  - Perform production smoke tests
  - Plan go-live and rollback strategies
  - Execute production launch
  - _Requirements: NFR-5.1_

---

## V2 - ENHANCED FEATURES (Tasks 100+)

### 100. Age Calculation Based on Competition Year ⏳

- [ ] 100.1 Update age calculation logic
  - Modify age calculation to use competition year instead of current year
  - Update backend race_eligibility.py to use configured competition date
  - Update frontend raceEligibility.js to use configured competition date
  - Ensure both backend and frontend use the same calculation
  - Test with crew members born in different years
  - _Requirements: FR-3.4, FR-7.10_

- [ ] 100.2 Update age display throughout application
  - Update crew member display to show age as of competition date
  - Update boat registration display to show correct ages
  - Update admin exports to use competition-year-based ages
  - Add tooltip explaining age calculation (e.g., "Age on May 1, 2025")
  - _Requirements: FR-3.4, FR-7.10_

### 101. Payment History and Advanced Features ⏳

- [ ] 101.1 Implement payment history page
  - Create PaymentHistory.vue to display all payments
  - Show payment date, amount, boats included
  - Add download receipt functionality
  - Display payment method and status
  - Implement filtering by date range
  - _Requirements: FR-4.3, FR-4.7_

- [ ] 101.2 Add payment receipt generation
  - Create receipt PDF generation Lambda
  - Include itemized breakdown in receipt
  - Add RCPM branding to receipts
  - Store receipts in S3 for download
  - Implement receipt email sending (beyond Stripe)
  - _Requirements: FR-4.7_

### 102. Advanced Admin Configuration ✅ COMPLETED (Moved from V2)

**Note:** This task was originally planned for V2 but was actually completed in V1 as Task 10 (Admin Mode - Configuration Management). The following features are already implemented:

- [x] 102.1 Admin configuration Lambda functions ✅ COMPLETED
  - Event date configuration (get/update event config)
  - Pricing configuration (get/update pricing config)
  - Boat inventory management (create/update/delete/list boats)
  - Configuration validation and audit logging
  - _Implemented in: Task 10.2, 10.4, 10.6_
  - _Requirements: FR-5.1, FR-5.2, FR-10.1-FR-10.8_

- [x] 102.2 Admin configuration frontend interface ✅ COMPLETED
  - AdminEventConfig.vue for event dates and periods
  - AdminPricingConfig.vue for pricing configuration
  - AdminBoatInventory.vue for boat inventory management
  - AdminDashboard.vue with navigation to all admin sections
  - _Implemented in: Task 10.3, 10.5, 10.7, 10.10_
  - _Requirements: FR-5.1, FR-5.2, FR-10.1, FR-10.2, FR-10.3_

### 103. Registration Validation and Admin Management ⏳

- [ ] 103.1 Implement registration validation Lambda functions
  - Create get_all_registrations Lambda for admin review
  - Implement flag_registration_issue Lambda with notification trigger
  - Create resolve_flagged_issue Lambda for club manager actions
  - Implement grant_editing_access Lambda with time limits
  - Add manual registration editing for admins
  - _Requirements: FR-6.1, FR-6.2, FR-6.3, FR-6.4, FR-6.5, FR-6.6_

- [ ] 103.2 Build admin validation frontend interface
  - Create RegistrationValidation.vue with filterable list
  - Add issue flagging interface with notification preview
  - Create editing access grant interface with time limits
  - Implement manual registration editing for admins
  - Display validation status indicators
  - Add bulk operations for common admin tasks
  - _Requirements: FR-6.1, FR-6.2, FR-6.5, FR-6.6_

- [ ] 103.3 Create admin dashboard with real-time statistics
  - Implement get_dashboard_stats Lambda with aggregations
  - Create Dashboard.vue with key metrics display
  - Add participant counts by category
  - Display payment status and financial summary
  - Show registration progress over time
  - Add boat rental status overview
  - _Requirements: FR-7.1, FR-7.3, FR-7.4_

### 104. Advanced Reporting and Analytics ⏳

- [ ] 104.1 Implement advanced reporting Lambda functions
  - Create export_payments Lambda for financial reports
  - Implement multi_club_crew revenue reporting
  - Add financial reports with revenue breakdown
  - Create audit log export functionality
  - _Requirements: FR-7.2, FR-9.7_

- [ ] 104.2 Build advanced reporting frontend interface
  - Create AdvancedReports.vue with multiple report types
  - Add date range filtering for reports
  - Display multi_club_crew statistics
  - Add audit log viewer for admin actions
  - Create financial dashboards
  - _Requirements: FR-7.2, FR-7.5, FR-9.6, FR-9.7_

### 105. Enhanced Notification System ⏳

- [ ] 105.1 Implement advanced notification features
  - Create schedule_notifications Lambda for recurring alerts
  - Implement process_notification_queue Lambda for batch processing
  - Add notification frequency management
  - Create notification preferences interface
  - _Requirements: NFR-6.2, NFR-6.3, NFR-6.4_

- [ ] 105.2 Set up EventBridge schedulers for automated notifications
  - Create daily notification check scheduler
  - Implement payment reminder scheduler
  - Add deadline warning scheduler
  - Create recurring issue notification scheduler
  - Implement daily summary scheduler
  - _Requirements: NFR-6.2, NFR-6.3_

- [ ] 105.3 Build notification center frontend component
  - Create NotificationCenter.vue with message history
  - Add unread notification counter in navigation
  - Implement notification filtering and search
  - Add real-time notification updates
  - _Requirements: NFR-6.4, FR-11.7_

### 106. Slack Integration for Admin and DevOps ⏳

- [ ] 106.1 Implement Slack webhook configuration
  - Add Slack webhook URL fields to notification config
  - Create webhook validation and testing functionality
  - Implement secure storage of webhook URLs
  - Add test notification sending capability
  - _Requirements: NFR-6.6, NFR-6.7_

- [ ] 106.2 Implement Slack notification Lambda function
  - Create send_slack_notification function with webhook integration
  - Implement Slack message block builders for different event types
  - Add rate limiting to prevent API abuse
  - Create CloudWatch metrics tracking for Slack notifications
  - Implement error handling and fallback mechanisms
  - _Requirements: NFR-6.6, NFR-6.7_

- [ ] 106.3 Integrate Slack notifications into event handlers
  - Add Slack notifications to boat registration events
  - Implement payment completion Slack alerts
  - Create boat rental request notifications
  - Add system error notifications to DevOps channel
  - Implement daily summary Slack messages
  - _Requirements: NFR-6.6, NFR-6.7_

### 107. Contact Us Feature ⏳

- [ ] 107.1 Implement contact form Lambda function
  - Create submit_contact_form Lambda with validation
  - Implement email sending to admin contact address
  - Add auto-reply email to user
  - Create Slack notification for contact submissions
  - Implement contact form logging in DynamoDB
  - _Requirements: FR-12.1, FR-12.2, FR-12.3, FR-12.4, FR-12.5, FR-12.6_

- [ ] 107.2 Build contact form frontend component
  - Create ContactForm.vue with all required fields
  - Add subject selection dropdown
  - Implement form validation and error handling
  - Create multilingual contact form (French/English)
  - Add user context pre-filling for authenticated users
  - Display contact information and alternative contact methods
  - _Requirements: FR-12.1, FR-12.7, FR-12.8_

### 108. GDPR Compliance Features ⏳

- [ ] 108.1 Implement GDPR compliance features
  - Create data deletion request handler
  - Implement user data anonymization
  - Add data export functionality for user requests
  - Create consent management system
  - Implement audit logging for data access
  - _Requirements: NFR-3.4_

- [ ] 108.2 Create privacy and legal pages
  - Create privacy policy and terms of service
  - Set up cookie consent management
  - Implement data retention policies
  - Document compliance procedures
  - _Requirements: NFR-3.4_

### 109. Performance Optimization ⏳

- [ ] 109.1 Implement frontend performance optimizations
  - Add code splitting for route-based lazy loading
  - Implement component lazy loading
  - Create service worker for offline support
  - Add asset preloading and prefetching
  - Implement virtual scrolling for large lists
  - Optimize images and assets
  - _Requirements: NFR-1.1, NFR-1.2_

- [ ] 109.2 Optimize backend Lambda functions
  - Implement connection pooling for DynamoDB
  - Add Lambda function warming to reduce cold starts
  - Optimize Lambda memory allocation
  - Implement caching for frequently accessed data
  - Add batch operations for bulk updates
  - _Requirements: NFR-1.2, NFR-1.3, NFR-2.1_

- [ ] 109.3 Implement DynamoDB query optimization
  - Use GSI indexes for efficient queries
  - Implement pagination for large result sets
  - Add DynamoDB query result caching
  - Optimize partition key design for even distribution
  - Implement batch get operations
  - _Requirements: NFR-1.2, NFR-2.3_

### 110. Advanced Testing ⏳

- [ ] 110.1 Implement end-to-end testing
  - Set up Cypress for E2E testing
  - Create E2E tests for user registration and login
  - Write E2E tests for crew member and boat registration
  - Add E2E tests for payment flow
  - Create E2E tests for admin workflows
  - _Requirements: General quality assurance_

- [ ] 110.2 Advanced load testing
  - Test concurrent user scenarios (1000+ users)
  - Validate system under peak load
  - Measure and optimize page load times
  - Test DynamoDB auto-scaling
  - _Requirements: NFR-1.1, NFR-1.3, NFR-2.1_

### 111. DevOps Utilities and Tools ⏳

- [ ] 111.1 Create DevOps configuration access tools
  - Build CLI tool for emergency configuration updates
  - Implement configuration backup and restore scripts
  - Create database query utilities for DevOps
  - Add system health check scripts
  - Implement log analysis tools
  - _Requirements: TC-4.5, TC-4.6_

- [ ] 111.2 Set up advanced deployment automation
  - Implement blue-green deployment strategy
  - Add rollback procedures and scripts
  - Create deployment validation tests
  - Implement automated smoke tests post-deployment
  - _Requirements: TC-2.1, TC-2.4_

### 112. Documentation ⏳

- [ ] 112.1 Create comprehensive API documentation
  - Document all API endpoints with request/response examples
  - Create authentication flow documentation
  - Add error code reference guide
  - Document rate limits and quotas
  - Create integration examples
  - _Requirements: General best practice_

- [ ] 112.2 Write deployment and operations guides
  - Create infrastructure deployment guide
  - Write configuration management guide
  - Document backup and restore procedures
  - Create troubleshooting guide
  - Add monitoring and alerting guide
  - _Requirements: TC-2.1, TC-3.1_

---

## Notes

### V1 Scope (MVP - Tasks 1-99)
V1 focuses on the core registration system with essential features for production launch:
- ✅ User authentication and crew/boat management (COMPLETED)
- ✅ Race eligibility and seat assignment (COMPLETED)
- ✅ Payment processing with Stripe (COMPLETED)
- ✅ Admin mode with configuration management (COMPLETED)
- ✅ Boat rental management (COMPLETED)
- ✅ Basic home page with contact email link (COMPLETED)
- ✅ Frontend deployment (COMPLETED)
- ✅ Admin data exports (crew members, boat registrations, CrewTimer format) (COMPLETED)
- ⏳ CrewTimer export enhancements (IN PROGRESS)
- ⏳ Registration and payment period enforcement
- ⏳ Admin impersonation and date override
- ⏳ Marathon skiff registration limit (40 boats)
- ⏳ Boat registration form clarity improvements
- ⏳ Mixed club display enhancements
- ⏳ Essential email notifications
- ⏳ Error handling and resilience
- ⏳ Security implementation
- ⏳ Testing and quality assurance
- ⏳ Production monitoring and launch

### V2 Scope (Enhanced Features - Tasks 100+)
V2 adds advanced features and optimizations after V1 launch:
- Age calculation based on competition year (not current year)
- Payment history and advanced receipt generation
- Advanced admin configuration management
- Enhanced validation and admin tools
- Advanced reporting and analytics
- Full notification system with scheduling
- Slack integration for admin/DevOps
- Contact form feature
- GDPR compliance features
- Performance optimizations
- Advanced testing (E2E, load testing)
- DevOps tools and automation
- Comprehensive documentation

### Key V1 Remaining Tasks Summary

**Critical for Production:**
1. **Registration Period Enforcement** (Tasks 18.1-18.4)
   - Prevent boat deletion/addition after registration period ends
   - Prevent all modifications after payment period ends
   
2. **Admin Impersonation** (Tasks 19.1-19.2)
   - Allow admins to bypass date restrictions
   - Enable admin modifications at any time

3. **Marathon Skiff Limit** (Tasks 20.1-20.2)
   - Enforce 40 skiff maximum for marathon event
   - Display count and warnings to users

4. **CrewTimer Export** (Tasks 14.1-14.3)
   - Complete CrewTimer.com export format
   - Ensure proper race ordering and data mapping

**Important for User Experience:**
5. **Form Clarity** (Task 21.1)
   - Clear messaging when no races match boat configuration
   
6. **Mixed Club Display** (Task 22.1)
   - Better visualization of mixed club crews and pricing

**Essential for Operations:**
7. **Email Notifications** (Tasks 23.1-23.2)
   - Payment and registration confirmations
   
8. **Error Handling** (Tasks 24.1-24.2)
   - Comprehensive error handling and user-friendly messages

9. **Security** (Tasks 25.1-25.2)
   - Input sanitization, rate limiting, encryption verification

10. **Testing & Launch** (Tasks 26.1-27.3)
    - Integration tests, load testing, production monitoring, UAT

### Migration Notes
- All completed tasks clearly marked with ✅
- V1 tasks numbered 1-99 for easy insertion of new tasks
- V2 tasks start at 100 to avoid renumbering
- Tasks organized by priority and dependencies
- Production-ready checklist integrated into task structure
