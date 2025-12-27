# Requirements Document - Course des Impressionnistes Registration System

## Introduction

The Course des Impressionnistes Registration System is a web application that enables rowing club managers to register crews and boats for the RCPM Competition, while providing administrative tools for validation and management. The system supports multilingual interfaces, payment processing, and comprehensive registration management throughout the Competition lifecycle.

## Glossary

### Terminology Mapping: Database/API vs UI

**IMPORTANT:** The system uses different terminology in the database/API layer versus the user interface to maintain consistency with existing code while providing clear, user-friendly language in the UI.

| Database/API Term | UI Term (English) | UI Term (French) | Description |
|-------------------|-------------------|------------------|-------------|
| `boat` | Crew | Équipage | A team of rowers registered for a race. In the database and API, this is called "boat" (e.g., `boat_id`, `boat_registration`), but displayed as "Crew" in the UI. |
| `boat_registration` | Crew / Crew Registration | Équipage / Inscription d'équipage | A complete registration entry. Database uses `boat_registration`, UI shows "Crew". |
| `boat_type` | Boat Type | Type de bateau | The physical boat type (skiff, four, eight). This remains "boat" in both database and UI as it refers to equipment. |
| `boat_rental` | Boat Rental | Location de bateau | Renting physical boats. This remains "boat" in both database and UI as it refers to equipment. |

**Key Principle:** 
- **"Boat" in database/API** = **"Crew" in UI** (when referring to the team/registration)
- **"Boat" in database/API** = **"Boat" in UI** (when referring to physical equipment)

### Standard Glossary Terms

- **RCPM** : Rowing Club de Port Marly
- **Registration_System**: The complete web application for managing rowing competition registrations
- **Club_Manager**: A user representing a rowing club who registers boats and crews for the competition
- **Admin_User**: RCPM organization staff member who manages system configuration and validates registrations
- **DevOps_User**: Technical staff responsible for deploying and maintaining the serverless infrastructure
- **Crew_Member**: An individual rower or coxswain registered to participate in a boat
- **Boat_Registration**: A complete registration entry containing boat configuration and assigned crew members (displayed as "Crew" in UI)
- **Registration_Period**: The time window during which club managers can create and modify registrations
- **Payment_Period**: The time window during which club managers can make payments
- **Seat_Assignment**: The association of a crew member to a specific position (rowing or cox) in a boat
- **Payment_Gateway**: Stripe integration for processing registration fees
- **Validation_Process**: Admin review and approval of crew member licenses and registration details
- **Boat_Rental**: Service allowing external clubs to rent RCPM boats for the competition
- **Seat_Rental**: Fee charged to external club members rowing in Multi_Club_Crews with RCPM members
- **RCPM_Member**: Rower affiliated with the RCPM who has priority access to club boats. A crew member is identified as an RCPM_Member when their club_affiliation field contains "RCPM" or "Port-Marly" or "Port Marly" (case-insensitive matching)
- **External_Club**: Rowing club other than RCPM participating in the competition
- **Multi_Club_Crew**: Boat crew containing both RCPM members and external club members, where external members pay seat rental fees
- **Rental_Priority_Period**: The period from registration opening until 15 days before registration closure, during which RCPM members have exclusive access to RCPM boats for rental requests
- **Base_Seat_Price**: The standard pricing for any seat (rowing or cox) used for all registrations and rental calculations (default: 20 euros)
- **Competition**: The Course des Impressionnistes rowing regatta that takes place every year on May 1st, consisting of 2 main events (21 km and 42 km) with multiple races (see races list in appendix)

---

## 1. Functional Requirements

These requirements define what the system does from a business and user perspective.

### FR-1: Club Manager Authentication

**User Story:** As a club manager, I want to register and authenticate securely, so that I can manage my club's boat registrations for the competition.

#### Acceptance Criteria

1. WHEN a club manager accesses the registration portal, THE Registration_System SHALL display authentication options including email/password and social login providers
2. WHEN a club manager provides valid credentials, THE Registration_System SHALL authenticate the user and establish a secure session
3. WHEN a club manager remains inactive for 30 minutes, THE Registration_System SHALL automatically log out the user for security
4. WHEN a club manager requests password recovery, THE Registration_System SHALL send a secure reset link via email
5. THE Registration_System SHALL store club manager profile information including first and last name, email, a rowing club affiliation, and a mobile number (required for emergency contact)

### FR-2: Crew Member Management

**User Story:** As a club manager, I want to manage crew member information, so that I can maintain accurate records of all participants from my club.

#### Acceptance Criteria

1. WHEN a club manager adds a crew member, THE Registration_System SHALL require first and last name, date of birth, gender, license number, rowing club affiliation if different from the rowing club affiliation of the club manager
2. WHILE the registration period is active, THE Registration_System SHALL allow club managers to edit crew member information or to delete a crew member
3. WHEN a club manager enters a license number, THE Registration_System SHALL validate the alphanumeric format
4. WHEN a club manager enters a license number, THE Registration_System SHALL verify that the license number is unique across all crew members in the competition
5. IF a club manager attempts to add a crew member with a license number that already exists, THEN THE Registration_System SHALL prevent the addition and display an error message indicating the license number is already in use
6. WHILE a crew member registration is incomplete, THE Registration_System SHALL allow club managers to save partial configurations and return later
7. THE Registration_System SHALL persist crew member information throughout and after the registration period
8. WHEN the registration period ends, THE Registration_System SHALL prevent club managers from editing crew member information unless granted by the Admin_User

### FR-3: Boat Registration and Seat Assignment

**User Story:** As a club manager, I want to configure boat registrations with seat assignments, so that I can register complete crews for specific race categories.

#### Acceptance Criteria

1. WHEN a club manager creates a boat registration, THE Registration_System SHALL propose two different events (21 or 42 km races)
2. WHEN a club manager selects an event, THE Registration_System SHALL display the possible boat types: skiff for the 42km event; 4 without cox or 4 with cox or 8 with cox for the 21 km event
3. WHEN a club manager selects a boat type, THE Registration_System SHALL display available seats for crew member assignment
4. WHEN a club manager has assigned crew members to each seat, THE Registration_System SHALL display all possible races among the 14 marathon races or 41 semi-marathon races (see appendix), filtering out races that are not compatible with crew members' age and gender and boat configuration (sweep vs scull), allowing the club manager to select the race
5. WHILE a boat registration is incomplete, THE Registration_System SHALL allow club managers to save partial configurations and return later
6. WHILE the registration period is active, THE Registration_System SHALL allow club managers to edit boat registration information or to delete a boat registration
7. WHEN crew members are assigned to all required seats and a race is selected, THE Registration_System SHALL mark the boat registration as complete
8. WHEN a crew member is assigned a seat, THE Registration_System SHALL mark the crew member as assigned to a boat
9. IF a crew member is already assigned to a seat, THEN THE Registration_System SHALL not allow the club manager to assign the crew member to another boat seat
10. IF a crew member is flagged with issues (by the Admin_User), THEN THE Registration_System SHALL allow the club manager to mark the flagged issue as resolved
11. WHEN a race has been selected and the boat has a coxswain, THE Registration_System SHALL display crew members who can substitute as coxswain during the race while maintaining crew compatibility with the selected race
12. THE Registration_System SHALL display seat assignments with crew member names in a clear visual format with links to boat registration or crew member information and with potential flagged issues
13. THE Registration_System SHALL log all club manager changes with timestamps and user identification

### FR-4: Payment Processing

**User Story:** As a club manager, I want to process payments for my registrations, so that I can secure my club's participation in the competition.

#### Acceptance Criteria

1. WHILE the Payment_Period is active, THE Registration_System SHALL allow club managers to initiate and complete payments for their registrations
2. WHEN a club manager initiates payment, THE Registration_System SHALL calculate total fees based on Base_Seat_Price for all seats, applying zero cost for RCPM_Member seats and Base_Seat_Price for external club member seats
3. WHEN determining RCPM_Member status for pricing, THE Registration_System SHALL identify crew members as RCPM_Members if their club_affiliation contains "RCPM" or "Port-Marly" or "Port Marly" in any combination of uppercase and lowercase letters
4. THE Registration_System SHALL track partial payments and display payment status to club managers by showing the balance between the number of paid seats and the number of seats registered
5. THE Registration_System SHALL allow modifications to crew members, seat assignments, and race selection for boat registrations even after payment, but SHALL prevent deletion of paid boat registrations
6. THE Registration_System SHALL NOT allow reimbursement in case balance in favor of RCPM (in such case the situation will be fixed afterwards by email)
7. WHEN payment processing occurs, THE Registration_System SHALL integrate with Stripe Payment_Gateway for secure transaction handling
8. WHEN payment is completed, THE Registration_System SHALL send confirmation via email and update registration status
9. IF payment is not completed before the Payment_Period ends, THEN THE Registration_System SHALL notify the club manager that payment is required to secure participation
10. IF there are flagged issues for some crew members, THEN THE Registration_System SHALL still allow payment processing

### FR-5: System Configuration Management

**User Story:** As an admin user, I want to configure and modify system parameters dynamically, so that I can manage registration periods, pricing, races, and other system settings throughout the competition lifecycle.

#### Acceptance Criteria

1. WHEN an Admin_User accesses the system configuration interface, THE Registration_System SHALL display all configurable parameters (see [Appendix B](#appendix-b-system-configuration-parameters)) in an organized and editable format
2. WHEN an Admin_User modifies Base_Seat_Price, THE Registration_System SHALL update the seat price for all new registrations
3. THE Registration_System SHALL provide Admin_Users with access to the predefined list of races for semi-marathon and marathon races list
4. WHEN an Admin_User configures Payment_Period dates, THE Registration_System SHALL validate that the Payment_Period extends beyond or equals the Registration_Period
5. THE Registration_System SHALL log all Admin_User configuration changes with timestamps and user identification

### FR-6: Registration Validation and Management

**User Story:** As an admin user, I want to validate and manage registrations, so that I can ensure compliance with competition rules and handle exceptions.

#### Acceptance Criteria

1. WHEN an Admin_User reviews registrations, THE Registration_System SHALL display crew member information with validation status indicators
2. WHEN an Admin_User identifies registration issues, THE Registration_System SHALL allow flagging of problems visible to the corresponding club manager who will be notified immediately through the predefined channels and repeatedly based on the Notification Frequency
3. IF a club manager has resolved a flagged issue, THE Registration_System SHALL display the flagged issue as resolved by the club manager
4. WHILE the registration period is active, THE Registration_System SHALL enable club managers to correct flagged issues autonomously
5. WHEN the registration period ends, THE Registration_System SHALL allow Admin_Users to manually edit registration information or grant temporary editing access to relevant club managers
6. WHEN an Admin_User grants editing exceptions, THE Registration_System SHALL apply a configurable time limit with automatic expiration

### FR-7: Reporting and Analytics

**User Story:** As an admin user, I want to access comprehensive reporting and analytics, so that I can monitor registration progress and export data for competition management.

#### Acceptance Criteria

1. WHEN an Admin_User accesses the dashboard, THE Registration_System SHALL display real-time statistics including participant counts and boats per category
2. WHEN an Admin_User requests data export, THE Registration_System SHALL provide JSON API endpoints that return raw data for client-side formatting into CSV or Excel files
3. THE Registration_System SHALL provide three separate export endpoints:
   - `/admin/export/crew-members-json` - Returns all crew members with club manager information, age calculations, and sorting by club manager name then crew member last name
   - `/admin/export/boat-registrations-json` - Returns all boat registrations (regardless of status) with race names, club manager information, crew details, and seat assignments
   - `/admin/export/races-json` - Returns comprehensive race data including system configuration, all races, all boats, all crew members, and all club managers for CrewTimer integration
4. WHEN an Admin_User exports crew members, THE Registration_System SHALL format the data as CSV with columns for club manager name, club affiliation, crew member details (first name, last name, gender, date of birth, age), and license number
5. WHEN an Admin_User exports boat registrations, THE Registration_System SHALL format the data as CSV with columns for club manager name, club affiliation, event type, boat type, race name, registration status, forfait status, payment status, and detailed crew composition with seat positions
6. WHEN an Admin_User exports races for CrewTimer, THE Registration_System SHALL format the data as Excel (XLSX) following the CrewTimer import specification with columns for Event, Crew, Bow, and individual rower details
7. THE Registration_System SHALL provide Admin_Users with financial reports showing the ratio of paid seats to registered seats
8. THE Registration_System SHALL track and display registration metrics including total participants and category distribution
9. THE Registration_System SHALL maintain audit logs of all Admin_User actions with role-based tagging
10. THE Registration_System SHALL calculate crew member ages dynamically using the centralized age calculation function based on the configured competition date
11. THE Registration_System SHALL include all boats in exports regardless of registration status (draft, complete, paid, forfait) to provide comprehensive competition data

### FR-8: Boat Rental Management

**User Story:** As a club manager from an external club, I want to request boat rentals from RCPM, so that my crews can participate in the competition using available boats.

#### Acceptance Criteria

1. WHEN a Club_Manager accesses boat rental options, THE Registration_System SHALL display all RCPM rental boats with boat type, name, recommended rower weight range in kilograms, and current availability status
2. WHEN a Club_Manager views available boats, THE Registration_System SHALL show only boats with status "available" that are not currently requested by another club manager
3. WHEN a Club_Manager requests a Boat_Rental, THE Registration_System SHALL record the request with selected boat, boat type, races, club manager contact information, and set the boat status to "requested"
4. WHEN a boat status is "requested" by one Club_Manager, THE Registration_System SHALL prevent other club managers from requesting the same boat
5. WHILE the Rental_Priority_Period is active, THE Registration_System SHALL reserve requested boats for RCPM_Members and mark external rental requests as pending
6. WHEN the Rental_Priority_Period expires, THE Registration_System SHALL automatically confirm pending External_Club rental requests for unreserved boats
7. WHEN an Admin_User changes a Boat_Rental status to "confirmed", THE Registration_System SHALL update the boat status and notify the Club_Manager via the defined channels
8. WHEN a Boat_Rental is confirmed, THE Registration_System SHALL update the boat availability status to prevent additional requests
9. THE Registration_System SHALL calculate rental fees at 2.5 times the Base_Seat_Price for individual boats (skiffs) and Base_Seat_Price per seat for crew boats
10. WHEN an Admin_User manages boat rentals, THE Registration_System SHALL allow the admin to change boat status (to confirm requests by changing status to "confirmed", or to reject by changing status back to "available") and view requester information
11. THE Registration_System SHALL display confirmed boat rentals in the payment page alongside boat registrations, allowing club managers to pay for rentals separately from boat registrations
12. WHEN an Admin_User creates or updates a rental boat, THE Registration_System SHALL allow entry of recommended rower weight range in kilograms as a text field for informational purposes to help club managers select appropriate boats for their crew
13. WHEN a rental boat status changes to "paid", THE Registration_System SHALL record the payment timestamp in the paid_at field to track when the rental was paid

### FR-9: Seat Rental for Multi_Club_Crews

**User Story:** As a club manager, I want to manage seat rental fees for external club members in Multi_Club_Crews, so that I can properly account for all participation costs.

#### Acceptance Criteria

1. WHEN a Club_Manager creates a Multi_Club_Crew registration, THE Registration_System SHALL identify external club members rowing with RCPM_Members using the club_affiliation detection logic
2. WHEN external club members are assigned to seats in Multi_Club_Crews, THE Registration_System SHALL automatically apply Seat_Rental fees to the registration
3. THE Registration_System SHALL calculate Seat_Rental fees at the Base_Seat_Price for each external club member in a Multi_Club_Crew and a price of zero for RCPM_Members
4. WHEN payment is processed for Multi_Club_Crews, THE Registration_System SHALL include Seat_Rental fees in the total amount due
5. THE Registration_System SHALL display Seat_Rental charges separately in payment summaries and receipts for transparency
6. WHEN an Admin_User reviews registrations, THE Registration_System SHALL clearly identify Multi_Club_Crews and associated Seat_Rental fees
7. THE Registration_System SHALL generate reports showing Seat_Rental revenue to encourage RCPM club crew formation

### FR-10: Dynamic Configuration Management

**User Story:** As an admin user, I want to be able to change the configuration of the Registration_System, so that I can modify the list of races, registration period dates, and other system parameters dynamically.

#### Acceptance Criteria

1. WHEN an Admin_User accesses the system configuration interface, THE Registration_System SHALL display all configurable parameters in an organized and editable format
2. WHEN an Admin_User modifies the list of races, THE Registration_System SHALL validate the changes and update the available categories for new boat registrations
3. WHEN an Admin_User changes registration period or payment period start and end dates, THE Registration_System SHALL validate that the start date is before the end date and that the Payment_Period encompasses or extends beyond the Registration_Period, then apply the changes immediately
4. WHEN an Admin_User updates Base_Seat_Price configuration, THE Registration_System SHALL apply the new prices to all future registrations while preserving existing registration pricing
5. WHEN an Admin_User configures Early_Bird_Period dates and pricing, THE Registration_System SHALL validate that the Early_Bird_Period falls within the Registration_Period and that Early_Bird_Pricing is less than Base_Seat_Price
6. THE Registration_System SHALL require Admin_User confirmation before applying configuration changes that could affect existing registrations
7. WHEN configuration changes are applied, THE Registration_System SHALL log all modifications with timestamps, previous values, new values, and Admin_User identification
8. IF configuration changes fail validation, THEN THE Registration_System SHALL display clear error messages and prevent the invalid changes from being saved

### FR-11: Home Page Information Display

**User Story:** As any user, I want to view general information and subscription process details on the home page, so that I can understand the competition and registration procedures before creating an account.

#### Acceptance Criteria

1. WHEN any user accesses the Registration_System home page, THE Registration_System SHALL display general information about the Course des Impressionnistes competition, including access to the preliminary program and race regulations
2. THE Registration_System SHALL display the subscription process and registration procedures as defined in [Appendix C](#appendix-c-home-page-content)
3. THE Registration_System SHALL provide clear navigation options for users to either log in to an existing account or create a new account
4. THE Registration_System SHALL display current registration period dates and deadlines prominently on the home page
5. THE Registration_System SHALL show all home page content in the user's selected language (French or English)
6. THE Registration_System SHALL provide contact information for RCPM organization for users who need assistance
7. THE Registration_System SHALL provide a clear view of unread notification number with link to the notification center

### FR-12: Contact Us

**User Story:** As any user, I want to contact the RCPM organization with questions or issues, so that I can get assistance with my registration or general inquiries.

#### Acceptance Criteria

1. WHEN any user accesses the Contact Us page, THE Registration_System SHALL display a contact form with fields for name, email, subject, and message
2. WHEN a user submits a contact form, THE Registration_System SHALL validate that all required fields are completed
3. WHEN a contact form is submitted, THE Registration_System SHALL send an email to the configured admin contact email address with the user's message
4. WHEN a contact form is submitted, THE Registration_System SHALL send a Slack notification to the admin channel with the contact request details
5. WHEN a contact form is successfully submitted, THE Registration_System SHALL display a confirmation message to the user
6. WHEN a contact form is successfully submitted, THE Registration_System SHALL send an auto-reply email to the user confirming receipt of their message
7. THE Registration_System SHALL display the contact form in the user's selected language (French or English)
8. THE Registration_System SHALL include the user's registration information (if authenticated) in the contact form submission for context

### FR-13: Admin Crew Member Management

**User Story:** As an admin user, I want to view and manage all crew members across all club managers, so that I can oversee registrations and make corrections regardless of date restrictions.

#### Acceptance Criteria

1. WHEN an Admin_User accesses the crew member management interface, THE Registration_System SHALL display all crew members from all club managers with their associated club manager information
2. THE Registration_System SHALL allow Admin_Users to filter crew members by club manager, club affiliation, or search by name and license number
3. WHEN an Admin_User creates a crew member, THE Registration_System SHALL allow selection of any club manager and bypass registration period date restrictions
4. WHEN an Admin_User updates a crew member, THE Registration_System SHALL allow modifications regardless of registration period or payment deadline restrictions
5. WHEN an Admin_User deletes a crew member, THE Registration_System SHALL allow deletion regardless of date restrictions, provided the crew member is not assigned to a boat
6. THE Registration_System SHALL display crew member details including first name, last name, age, gender, license number, club affiliation, and associated club manager
7. THE Registration_System SHALL provide sorting capabilities by name, club, club manager, and other relevant fields
8. THE Registration_System SHALL log all Admin_User actions on crew members with timestamps and user identification for audit purposes

### FR-14: Admin Boat Registration Management

**User Story:** As an admin user, I want to view and manage all boat registrations across all club managers, so that I can oversee the competition and handle special cases like forfaits.

#### Acceptance Criteria

1. WHEN an Admin_User accesses the boat registration management interface, THE Registration_System SHALL display all boat registrations from all club managers with their associated club manager information
2. THE Registration_System SHALL allow Admin_Users to filter boats by club manager, club affiliation, registration status, or search by event type and boat type
3. WHEN an Admin_User views boat registrations, THE Registration_System SHALL display event type, boat type, crew composition, registration status, club manager name, and club affiliation
4. WHEN an Admin_User marks a boat as forfait, THE Registration_System SHALL update the boat status to indicate withdrawal from the competition
5. WHEN an Admin_User removes forfait status from a boat, THE Registration_System SHALL restore the boat to its previous registration status
6. THE Registration_System SHALL visually distinguish forfait boats from active registrations in the admin interface
7. WHEN an Admin_User deletes a boat registration, THE Registration_System SHALL allow deletion regardless of date restrictions, except for boats with paid status
8. THE Registration_System SHALL prevent deletion of paid boat registrations to maintain payment integrity
9. THE Registration_System SHALL display paid and complete boat registrations with consistent visual styling to indicate finalized status
10. THE Registration_System SHALL provide sorting capabilities by event type, boat type, club manager, club, and registration status
11. THE Registration_System SHALL log all Admin_User actions on boat registrations with timestamps and user identification for audit purposes

---

## 2. Non-Functional Requirements

These requirements define how the system performs and quality attributes.

### NFR-1: Performance Requirements

#### Acceptance Criteria

1. THE Registration_System SHALL load pages within 3 seconds under normal network conditions
2. THE Registration_System SHALL respond to user interactions within 1 second for standard operations
3. THE Registration_System SHALL handle concurrent payment processing without performance degradation
4. THE Registration_System SHALL maintain responsive performance during peak registration periods

### NFR-2: Scalability Requirements

#### Acceptance Criteria

1. THE Registration_System SHALL automatically scale to handle up to 1000 concurrent users without manual intervention
2. THE Registration_System SHALL support registration of up to 10,000 crew members and 2,000 boats per competition
3. THE Registration_System SHALL maintain performance levels as data volume increases throughout the registration period
4. THE Registration_System SHALL scale down to zero where possible outside the registration period

### NFR-3: Security Requirements

#### Acceptance Criteria

1. THE Registration_System SHALL encrypt all data at rest using industry-standard encryption algorithms
2. THE Registration_System SHALL encrypt all data in transit using HTTPS/TLS protocols
3. THE Registration_System SHALL implement secure authentication with multi-factor authentication options
4. THE Registration_System SHALL comply with GDPR requirements for user data protection and privacy
5. THE Registration_System SHALL implement role-based access control to restrict functionality based on user roles

### NFR-4: Usability Requirements

#### Acceptance Criteria

1. THE Registration_System SHALL provide multilingual support for French and English languages
2. THE Registration_System SHALL detect browser language and default to French or English accordingly
3. THE Registration_System SHALL provide manual language switching between French and English at any time during user sessions
4. THE Registration_System SHALL render responsively across mobile, tablet, and desktop screen sizes
5. THE Registration_System SHALL maintain consistent functionality and user experience across supported browsers including Chrome, Firefox, Safari, and Edge

### NFR-5: Reliability Requirements

#### Acceptance Criteria

1. THE Registration_System SHALL maintain 99.5% uptime during the registration period
2. THE Registration_System SHALL implement graceful error handling with user-friendly error messages
3. THE Registration_System SHALL provide automatic recovery from transient failures
4. THE Registration_System SHALL maintain data consistency during system failures

### NFR-6: Notification Requirements

#### Acceptance Criteria

1. WHEN registration events occur, THE Registration_System SHALL send notifications (according to defined notification channels) for confirmations, issues, and deadline reminders
2. THE Registration_System SHALL repeat notifications (according to defined notification channels) on a regular basis (based on notification frequency parameter) if there are ongoing issues
3. WHEN approaching registration deadlines, THE Registration_System SHALL notify club managers (according to defined notification channels) and highlight issues in the registration (missing information, information tagged as wrong, ...)
4. THE Registration_System SHALL provide a notification center within the web application for users to review message history
5. THE Registration_System SHALL ensure all notifications are delivered in the user's selected language preference
6. WHEN significant registration events occur (new registrations, payments, boat rentals), THE Registration_System SHALL send real-time notifications to Admin_Users and DevOps_Users via Slack
7. THE Registration_System SHALL send Slack notifications for system events including new boat registrations, payment completions, boat rental requests, and system errors

## 3. Technical Constraints

These requirements define the mandatory technical architecture and implementation constraints.

### TC-1: Serverless Architecture Constraint

**Constraint:** The system must be implemented using a serverless architecture on AWS.

#### Acceptance Criteria

1. THE Registration_System SHALL utilize AWS serverless services in general and Python language where script or lambda functions are necessary
2. THE Registration_System SHALL store all data in Amazon DynamoDB with encryption at rest enabled
3. WHEN traffic increases, THE Registration_System SHALL automatically scale without manual intervention
4. THE Registration_System SHALL serve the frontend application through Amazon S3 and CloudFront for optimal performance with custom domain support
5. THE Registration_System SHALL configure custom domains for both development and production environments using AWS Certificate Manager (ACM) certificates in the us-east-1 region (required for CloudFront)
6. THE Registration_System SHALL use the following custom domains:
   - Development: `impressionnistes-dev.aviron-rcpm.fr`
   - Production: `impressionnistes.aviron-rcpm.fr`
7. THE Registration_System SHALL NOT necessarily need an api layer

### TC-2: Infrastructure as Code Constraint

**Constraint:** All infrastructure must be defined and deployed using Infrastructure as Code practices.

#### Acceptance Criteria

1. THE Registration_System SHALL implement Infrastructure as Code using AWS CDK in Python language for reproducible deployments
2. THE Registration_System SHALL backup the application data to Amazon S3 on a regular basis (default daily) with a prefix of the current year and an object name with full date/time
3. WHEN a DevOps_User deploys the infrastructure, THE Registration_System SHALL allow either the specification of an existing database or the restoration of previous backup data or the creation of a new database
4. THE Registration_System SHALL maintain configuration versioning to allow DevOps_Users to track changes and rollback if necessary

### TC-3: Monitoring and Logging Constraint

**Constraint:** The system must provide comprehensive monitoring and logging capabilities.

#### Acceptance Criteria

1. THE Registration_System SHALL send all application logs to Amazon CloudWatch with structured JSON formatting
2. WHEN system errors occur, THE Registration_System SHALL trigger CloudWatch alarms and send email notifications to DevOps_Users
3. THE Registration_System SHALL implement health checks for all critical system components including Lambda functions and DynamoDB
4. WHEN performance thresholds are exceeded, THE Registration_System SHALL automatically alert DevOps_Users through configured notification channels
5. THE Registration_System SHALL maintain backup and recovery capabilities with daily DynamoDB backups and 35-day point-in-time recovery

### TC-4: Centralized Configuration Constraint

**Constraint:** All system configuration must be centrally managed and accessible to DevOps users.

#### Acceptance Criteria

1. THE Registration_System SHALL store all configuration parameters in a centralized configuration service accessible to DevOps_Users
2. WHEN a DevOps_User accesses the configuration store, THE Registration_System SHALL display all system parameters including registration periods, payment periods, Early_Bird_Period dates, pricing (including Early_Bird_Pricing), age categories, race categories, and notification settings
3. THE Registration_System SHALL provide DevOps_Users with read-only access to configuration values through AWS Systems Manager Parameter Store or equivalent service
4. WHEN configuration changes are made through the admin interface, THE Registration_System SHALL automatically update the centralized configuration store
5. WHEN a DevOps_User needs to manually modify configuration for emergency purposes, THE Registration_System SHALL provide secure CLI or API access with proper authentication
6. THE Registration_System SHALL validate all configuration changes to ensure system integrity before applying them

### TC-5: Export Architecture Constraint

**Constraint:** Data exports must use JSON APIs with client-side formatting to minimize backend processing and enable flexible output formats.

#### Acceptance Criteria

1. THE Registration_System SHALL implement data exports using JSON API endpoints that return raw structured data rather than pre-formatted files
2. THE Registration_System SHALL provide separate export endpoints for different data entities (crew members, boat registrations, races) to enable targeted data retrieval
3. THE Registration_System SHALL implement client-side formatting in the frontend application to convert JSON data into CSV or Excel formats
4. WHEN export data volumes are large, THE Registration_System SHALL implement pagination handling in the Lambda functions to retrieve all records across multiple DynamoDB scan operations
5. THE Registration_System SHALL cache frequently accessed data (club managers, crew members) during export operations to minimize database queries and improve performance
6. THE Registration_System SHALL convert DynamoDB Decimal types to standard float/integer types before returning JSON responses to ensure compatibility with frontend JavaScript
7. THE Registration_System SHALL set Lambda function timeouts to 60 seconds for export operations to accommodate large dataset processing
8. THE Registration_System SHALL include metadata in export responses (total count, export timestamp) to provide context for the exported data
9. WHEN formatting exports in the frontend, THE Registration_System SHALL provide reusable formatter utilities for consistent CSV and Excel generation across different export types

### TC-6: Custom Domain and SSL Certificate Constraint

**Constraint:** The system must use custom domains with SSL certificates for both development and production environments to provide professional URLs and secure HTTPS access.

#### Acceptance Criteria

1. THE Registration_System SHALL use custom domains for CloudFront distributions:
   - Development environment: `impressionnistes-dev.aviron-rcpm.fr`
   - Production environment: `impressionnistes.aviron-rcpm.fr`
2. THE Registration_System SHALL create SSL certificates using AWS Certificate Manager (ACM) in the us-east-1 region (required for CloudFront global distribution)
3. THE Registration_System SHALL use DNS validation method for certificate verification to automate the validation process
4. WHEN creating certificates, THE Registration_System SHALL provide clear DNS validation records (CNAME records) that must be added to the domain's DNS configuration
5. THE Registration_System SHALL store certificate ARNs in the environment-specific configuration file (`infrastructure/config.py`) for use during CDK deployment
6. THE Registration_System SHALL configure CloudFront distributions to use the custom domain and associated SSL certificate for HTTPS access
7. WHEN deploying the frontend stack, THE Registration_System SHALL output the CloudFront distribution domain name that must be configured as a CNAME record in DNS
8. THE Registration_System SHALL require the following DNS records for full custom domain setup:
   - Certificate validation CNAME records (for ACM validation)
   - CloudFront CNAME records (pointing custom domain to CloudFront distribution)
9. THE Registration_System SHALL provide automated scripts (`create-certificates.sh`) to simplify certificate creation and display required DNS records
10. THE Registration_System SHALL update Cognito callback URLs to include custom domains in addition to CloudFront distribution URLs
11. THE Registration_System SHALL provide comprehensive documentation (`SETUP_CUSTOM_DOMAINS.md`, `DNS_RECORDS_TO_ADD.md`) with step-by-step instructions for certificate creation, DNS configuration, and deployment
12. WHEN certificates are pending validation, THE Registration_System SHALL provide commands to check certificate status and troubleshoot validation issues

---

## Appendix A: Reference Data

### A.1 Competition structure and rules

The registration follows the French Rowing Federation (FFA) rules and competition structure:

#### Events
The Course des Impressionnistes competition consists of two distinct events:
- **Semi-marathon (21 km)**: Raced in fours and eights of all configurations
- **Marathon (42 km)**: Individual race in single sculls (skiffs)

#### Age Categories (based on average age of ROWERS ONLY)

Here is how the French Rowing Federation (FFA) defines categories based on age.

**Important:** Age category determination is based on ROWERS ONLY. Coxswains are excluded from age category calculations.

- **J14**: aged 14
- **J15**: aged 15
- **J16**: aged 16
- **J17**: aged 17
- **J18**: aged 18
- **Senior**: 19 years and older
- **Master**: 27 years and older (average age ≥ 27)
  - A: Minimum age 27 years
  - B: Average age 36 years or over
  - C: Average age 43 years or over
  - D: Average age 50 years or over
  - E: Average age 55 years or over
  - F: Average age 60 years or over
  - G: Average age 65 years or over
  - H: Average age 70 years or over
  - I: Average age 75 years or over
  - J: Average age 80 years or over
  - K: Average age 85 years or over

#### Gender Categories and Crew Composition Rules

**Important:** Gender category determination is based on ROWERS ONLY. Coxswains are excluded from gender category calculations.

- **Men's crews**: More than 50% men (among rowers)
- **Women's crews**: 100% women (among rowers)
- **Mixed-gender crews**: At least 1 man and at least 50% women (among rowers)
- **Substitution rules**: Women can substitute for men in men's or mixed-gender crews; men cannot substitute for women in women's or mixed-gender crews

#### Boat Types and Configurations
Boat notation format: [Gender][Boat Type][Number of Rowers][Oar Type][Coxswain]
- Gender: H (Homme/Men), F (Femme/Women), M (Mixte/Mixed-gender)
- Boat Type: o (outrigger), y (yolette)
- Number of rowers: 1, 4 or 8
- Oar Type: x (sculling/couple), / (sweep/pointe)
- Coxswain: + (with cox), - (without cox)

Example: H4x+ = Men's four with sculling oars and coxswain

#### Races
Races are numbered sequentially for race programming based on the boat configurations allowed for each age group.

##### Marathon event 42 km
The marathon is an individual event in single scull (skiff).

The races taken into account are as follows:
1.	1X SENIOR WOMAN
2.	1X SENIOR MAN
3.	1X MASTER A WOMAN
4.	1X MASTER A MAN
5.	1X MASTER B WOMAN
6.	1X MASTER B MAN
7.	1X MASTER C WOMAN
8.	1X MASTER C MAN
9.	1X MASTER D WOMAN
10.	1X MASTER D MAN
11.	1X MASTER E WOMAN
12.	1X MASTER E MAN
13.	1X MASTER F WOMAN
14.	1X MASTER F MAN

##### Semi-Marathon event 21 km

The races are organized by age category, gender, and boat configuration. Each race distinguishes between sweep rowing (one oar per rower) and sculling (two oars per rower). The 41 races are as follows:

**J16 Category (7 races):**
1. WOMEN-JUNIOR J16-COXED SWEEP FOUR (SM01A)
2. WOMEN-JUNIOR J16-COXED QUAD SCULL (SM01B)
3. MEN-JUNIOR J16-COXED SWEEP FOUR (SM02A)
4. MEN-JUNIOR J16-COXED QUAD SCULL (SM02B)
5. MIXED-GENDER-JUNIOR J16-COXED QUAD SCULL (SM03B)
6. WOMEN-JUNIOR J16-SWEEP EIGHT WITH COXSWAIN (SM04)
7. MEN-JUNIOR J16-SWEEP EIGHT WITH COXSWAIN (SM05)

**J18 Category (8 races):**
8. WOMEN-JUNIOR J18-SWEEP FOUR WITHOUT COXSWAIN (SM06A)
9. WOMEN-JUNIOR J18-QUAD SCULL WITHOUT COXSWAIN (SM06B)
10. MEN-JUNIOR J18-SWEEP FOUR WITHOUT COXSWAIN (SM07A)
11. MEN-JUNIOR J18-QUAD SCULL WITHOUT COXSWAIN (SM07B)
12. MIXED-GENDER-JUNIOR J18-QUAD SCULL WITHOUT COXSWAIN (SM08B)
13. WOMEN-JUNIOR J18-SWEEP EIGHT WITH COXSWAIN (SM10)
14. MEN-JUNIOR J18-SWEEP EIGHT WITH COXSWAIN (SM11)
15. MIXED-GENDER-JUNIOR J18-SWEEP EIGHT WITH COXSWAIN (SM12)

**Senior Category (8 races):**
16. WOMEN-SENIOR-SWEEP FOUR WITHOUT COXSWAIN (SM13A)
17. WOMEN-SENIOR-QUAD SCULL WITHOUT COXSWAIN (SM13B)
18. MEN-SENIOR-SWEEP FOUR WITHOUT COXSWAIN (SM14A)
19. MEN-SENIOR-QUAD SCULL WITHOUT COXSWAIN (SM14B)
20. MIXED-GENDER-SENIOR-QUAD SCULL WITHOUT COXSWAIN (SM15B)
21. WOMEN-SENIOR-SWEEP EIGHT WITH COXSWAIN (SM16)
22. MEN-SENIOR-SWEEP EIGHT WITH COXSWAIN (SM17)
23. MIXED-GENDER-SENIOR-SWEEP EIGHT WITH COXSWAIN (SM18)

**Master Category (18 races):**

*Yolette races (3 races):*
24. WOMEN-MASTER-COXED QUAD SCULL YOLETTE (SM19A)
25. MEN-MASTER-COXED QUAD SCULL YOLETTE (SM19B)
26. MIXED-GENDER-MASTER-COXED QUAD SCULL YOLETTE (SM19C)

*Coxed quad scull races (3 races):*
27. WOMEN-MASTER-COXED QUAD SCULL (SM20A)
28. MEN-MASTER-COXED QUAD SCULL (SM20B)
29. MIXED-GENDER-MASTER-COXED QUAD SCULL (SM20C)

*Octuple scull with coxswain races (3 races):*
30. WOMEN-MASTER-OCTUPLE SCULL WITH COXSWAIN (SM21A)
31. MEN-MASTER-OCTUPLE SCULL WITH COXSWAIN (SM21B)
32. MIXED-GENDER-MASTER-OCTUPLE SCULL WITH COXSWAIN (SM21C)

*Coxed sweep four (1 race):*
33. MEN-MASTER-COXED SWEEP FOUR (SM22A)

*Quad scull without coxswain races (3 races):*
34. WOMEN-MASTER-QUAD SCULL WITHOUT COXSWAIN (SM23A)
35. MEN-MASTER-QUAD SCULL WITHOUT COXSWAIN (SM23B)
36. MIXED-GENDER-MASTER-QUAD SCULL WITHOUT COXSWAIN (SM23C)

*Sweep four without coxswain races (2 races):*
37. MEN-MASTER-SWEEP FOUR WITHOUT COXSWAIN (SM24A)
38. WOMEN-MASTER-SWEEP FOUR WITHOUT COXSWAIN (SM24B)

*Sweep eight with coxswain races (3 races):*
39. MEN-MASTER-SWEEP EIGHT WITH COXSWAIN (SM25A)
40. WOMEN-MASTER-SWEEP EIGHT WITH COXSWAIN (SM25B)
41. MIXED-GENDER-MASTER-SWEEP EIGHT WITH COXSWAIN (SM25C)

**Note:** Races ending in "A" are sweep rowing races (one oar per rower), while races ending in "B" are sculling races (two oars per rower). The system automatically filters available races based on the boat type selected and crew composition.

### A.2 Boat and Seat Rental Rules

#### Boat Rental Priority System
1. RCPM boats are available for rental based on availability
2. RCPM members have exclusive priority from registration opening until 15 days before registration closure
3. During the final 15 days before registration closure, external clubs have equal access to unreserved boats
4. Rental pricing: 2.5x Base_Seat_Price for individual boats (skiffs), Base_Seat_Price per seat for crew boats

#### Seat Rental for Multi_Club_Crews
- External club members rowing in Multi_Club_Crews with RCPM members pay seat rental fees
- Seat rental fee equals Base_Seat_Price per external member
- RCPM members pay zero for their seats in any boat registration
- Purpose: Encourage RCPM members to form club-only crews while allowing mixed club participation

---

## Appendix B: System Configuration Parameters

This appendix lists all configurable parameters that must be managed through the centralized configuration system and accessible to Admin Users and DevOps Users.

### B.1 Registration Period Parameters
- **Registration Start Date** (default: March 19th, can be March 1st if ready)
- **Registration End Date** (default: April 19th)
- **Payment Deadline** (default: April 25th)
- **Rental Priority Period Duration** (default: 15 days before registration closure)

### B.2 Pricing Parameters
- **Base_Seat_Price** (standard price for any seat - rowing or cox - default: 20 euros)
- **Boat Rental Multiplier for Individual Boats** (default: 2.5x Base_Seat_Price for skiffs)
- **Boat Rental Price for Crew Boats** (default: Base_Seat_Price per seat)

### B.3 Notification Parameters
- **Notification Frequency** (default: weekly for ongoing issues)
- **Session Timeout Duration** (default: 30 minutes for automatic logout)
- **Notification Channels** (default: email and notification center in the web app)
- **Email From Address** (default: impressionnistes@rcpm-aviron.fr)
- **Slack Webhook URL for Admin Notifications** (Slack incoming webhook for admin channel)
- **Slack Webhook URL for DevOps Notifications** (Slack incoming webhook for devops channel)

### B.4 System Configuration Parameters
- **Temporary Editing Access Duration** (time limit for admin-granted editing exceptions)
- **Backup Frequency** (default: daily)
- **Backup Retention Period** (default: 35 days for point-in-time recovery)

### B.5 Competition Data Parameters
- **Race Categories List** (41 predefined race categories for semi-marathon, distinguishing sweep rowing and sculling)
- **Marathon Race Categories** (14 races: Men's and Women's Senior and Master A-F divisions)
- **Age Categories** (J14, J15, J16, J17, J18, Senior, Master A-K with age thresholds)
- **Distance Options** (21 km and 42 km)
- **Boat Type Configurations** (skiff for 42km, 4 without cox/4 with cox/8 with cox for 21km)

### B.6 Capacity Parameters
- **Maximum Concurrent Users** (default: 1000)
- **Maximum Crew Members per Competition** (default: 10,000)
- **Maximum Boats per Competition** (default: 2,000)

### B.7 Performance Parameters
- **Page Load Timeout** (default: 3 seconds)
- **User Interaction Response Time** (default: 1 second)
- **System Uptime Target** (default: 99.5% during registration period)

### B.8 Language and Localization Parameters
- **Supported Languages** (French and English)
- **Default Language Detection** (browser-based)

### B.9 Contact and Organization Parameters
- **RCPM Organization Contact Information**
- **Admin Contact Email** (email address for contact form submissions, default: contact@impressionnistes.rcpm.fr)
- **DevOps User Notification Channels**
- **Admin User Notification Settings**

## Appendix C: Home Page Content

### C.1 General Information About Course des Impressionnistes

**What is the Course des Impressionnistes?**

The Course des Impressionnistes is a rowing regatta featuring two distinct events:

**Semi-Marathon (21 km)**
- Event distance: 21 kilometers
- Boat types: Fours and eights in all configurations
- Boat Categories: Competitive outriggers and recreational yolettes
- Oar configurations: Sweep rowing (one oar per rower) or sculling (two oars per rower)
- Crew compositions: Men's, women's, and mixed-gender crews
- Age categories: J16, J18, Senior, and Master
- [41 different races for the semi-marathon](#semi-marathon-event-21-km) (each category split by sweep/scull configuration)

**Marathon (42 km)**  
- Event distance: 42 kilometers
- Boat type: Individual single sculls (skiffs)
- Races: Men's and women's in Senior and Master A-H divisions
- [14 different races for the marathon](#marathon-event-42-km)

**Competition Features:**
- Individual time trial format for the marathon
- Awards: Medals and trophies for winners, medals for single-entry categories
- Professional timing and results management

### C.2 Registration and Subscription Process

**Registration Period**
- Registration opens: March 19th (may open earlier on March 1st if ready)
- Registration closes: April 19th
- Payment deadline: April 25th
- Late changes: Crew substitutions and withdrawals accepted after closure

**Who Can Register**
- Rowing club club managers register on behalf of their clubs
- Multiple managers per club allowed (e.g., individual marathon participants)
- All participants must hold valid French Rowing Federation licenses

**Registration Flow for Club Managers**

**Getting Started**
Club managers register their club and crews through a simple online process. Each club can have multiple managers, and the system guides you through every step.

**The Registration Journey**

1. **Set Up Your Access**
   Create your manager account using your club's federation details and contact information. You'll receive secure login credentials to access the registration system throughout the season.

2. **Build Your Team Roster**  
   Add all potential participants to your club's roster with their essential information: name, birth date, gender, and FFA license number. This roster becomes your pool of available crew members for all boat registrations.

3. **Create Boat Entries**
   Select races and configure each boat entry by choosing the boat type, oar configuration, and assigning specific crew members to rowing and coxswain positions. The system automatically validates your crew against race rules.

4. **Handle Equipment Needs**
   If you need boats, submit rental requests through the system. RCPM boats are available on a priority basis, with RCPM club members having exclusive access from registration opening until two weeks before registration closes.

5. **Process Payments**
   Review your total costs and complete payment using the integrated secure payment system. You can pay for individual entries or process multiple registrations together, with flexibility to pay before the final deadline.

6. **Ongoing Management**
   Monitor your registrations, make permitted changes during the open period, and handle any crew substitutions or withdrawals that may be needed after registration closes.
   
**Key Benefits**
- Save partial registrations and complete them later
- Automatic validation against race rules  
- Flexible payment options with secure processing
- Real-time availability for boat rentals
- Complete registration history and status tracking

**Pricing Structure**
- Base_Seat_Price for any seat (rowing or cox) - default: 20 euros per seat
- Boat rental: 2.5x Base_Seat_Price (50 euros) for singles, Base_Seat_Price per seat for crew boats
- Seat rental: Base_Seat_Price for external club members, zero cost for RCPM members
- Examples: EIGHT WITH COXSWAIN = 180 euros (9 seats × 20 euros), QUAD WITHOUT COXSWAIN = 80 euros (4 seats × 20 euros)

**Support and Assistance**
- License verification handled automatically or manually
- Registration modification allowed during open period
- Administrative support for complex registrations
- Comprehensive reporting for club managers

**Important Dates to Remember**
- March 19: Registration opens
- April 19: Registration closes  
- April 25: Payment deadline
- 15 days before closure: RCPM boat exclusive priority ends, external clubs gain equal access

