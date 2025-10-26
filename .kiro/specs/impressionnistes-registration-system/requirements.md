# Requirements Document - Course des Impressionnistes Registration System

## Introduction

The Course des Impressionnistes Registration System is a serverless web application that enables rowing club team managers to register crews and boats for the RCPM competition, while providing administrative tools for validation and management. The system supports multilingual interfaces, payment processing, and comprehensive registration management throughout the competition lifecycle.

## Glossary

- **Registration_System**: The complete web application for managing rowing competition registrations
- **Team_Manager**: A user representing a rowing club who registers boats and crews for the competition
- **Admin_User**: RCPM organization staff member who manages system configuration and validates registrations
- **DevOps_User**: Technical staff responsible for deploying and maintaining the serverless infrastructure
- **Crew_Member**: An individual rower or coxswain registered to participate in a boat
- **Boat_Registration**: A complete registration entry containing boat configuration and assigned crew members
- **Registration_Period**: The time window during which team managers can create and modify registrations
- **Seat_Assignment**: The association of a crew member to a specific position (rowing or cox) in a boat
- **Payment_Gateway**: Stripe integration for processing registration fees
- **Validation_Process**: Admin review and approval of crew member licenses and registration details
- **Boat_Rental**: Service allowing external clubs to rent RCPM boats for the competition
- **Seat_Rental**: Fee charged to external club members rowing in mixed crews with RCPM members
- **RCPM_Member**: Rower affiliated with the Rowing Club Paris Métropole who has priority access to club boats
- **External_Club**: Rowing club other than RCPM participating in the competition
- **Mixed_Crew**: Boat crew containing both RCPM members and external club members
- **Rental_Priority_Period**: 15-day period before registration closure when RCPM members have exclusive access to their boats

## 1. Functional Requirements

These requirements define what the system does from a business and user perspective.

### FR-1: Team Manager Authentication

**User Story:** As a team manager, I want to register and authenticate securely, so that I can manage my club's boat registrations for the competition.

#### Acceptance Criteria

1. WHEN a team manager accesses the registration portal, THE Registration_System SHALL display authentication options including email/password and social login providers
2. WHEN a team manager provides valid credentials, THE Registration_System SHALL authenticate the user and establish a secure session
3. WHEN a team manager remains inactive for 30 minutes, THE Registration_System SHALL automatically log out the user for security
4. WHEN a team manager requests password recovery, THE Registration_System SHALL send a secure reset link via email
5. THE Registration_System SHALL store team manager profile information including name, email, rowing club affiliation, and mandatory mobile number

### FR-2: Crew Member Management

**User Story:** As a team manager, I want to manage crew member information, so that I can maintain accurate records of all participants from my club.

#### Acceptance Criteria

1. WHEN a team manager adds a crew member, THE Registration_System SHALL require name, date of birth, gender, license number, and category information
2. WHILE the registration period is active, THE Registration_System SHALL allow team managers to edit crew member information
3. WHEN a team manager enters a license number, THE Registration_System SHALL validate the alphanumeric format
4. THE Registration_System SHALL persist crew member information throughout the registration period for potential changes of member information or boat assignment
5. WHEN the registration period ends, THE Registration_System SHALL prevent team managers from editing crew member information unless granted admin exception

### FR-3: Boat Registration and Seat Assignment

**User Story:** As a team manager, I want to configure boat registrations with seat assignments, so that I can register complete crews for specific competition categories.

#### Acceptance Criteria

1. WHEN a team manager creates a boat registration, THE Registration_System SHALL follow the registration logic (see appendix).
2. WHEN a team manager selects a boat type, THE Registration_System SHALL configure the appropriate number of rowing seats and cox seats based on the boat configuration
3. WHILE a boat registration is incomplete, THE Registration_System SHALL allow team managers to save partial configurations and return later
4. WHEN all required seats are assigned crew members, THE Registration_System SHALL mark the boat registration as complete
5. WHEN a crew member is assigned a seat, THE Registration_System SHALL mark the crew member as assigned to a boat
6. IF a crew member is already marked as assigned to a seat, THEN THE Registration_System SHALL not allow the team manager to assign the crew member to another boat seat
7. IF a crew member is flagged with issues, THEN THE Registration_System SHALL allow the team manager to mark the issue as resolved 
8. THE Registration_System SHALL display seat assignments with crew member names in a clear visual format with links to boat registration or crew member information and with potential flagged issues
9. THE Registration_System SHALL log all team manager changes with timestamps and user identification

### FR-4: Payment Processing

**User Story:** As a team manager, I want to process payments for my registrations, so that I can secure my club's participation in the competition.

#### Acceptance Criteria

1. WHEN a team manager initiates payment, THE Registration_System SHALL calculate total fees based on configured rowing seat and cox seat prices
2. WHEN payment processing occurs, THE Registration_System SHALL integrate with Stripe Payment_Gateway for secure transaction handling
3. THE Registration_System SHALL track partial payments and display payment status to team managers
4. WHEN payment is completed, THE Registration_System SHALL send confirmation via email and update registration status
5. IF payment is not completed before the registration period ends, THEN THE Registration_System SHALL notify the team manager of the grace period deadline
6. IF there are flagged issues for some crew members, THEN THE Registration_System SHALL still allow payment processing

### FR-5: Admin System Configuration

**User Story:** As an admin user, I want to configure system parameters, so that I can manage registration periods, pricing, and competition categories.

#### Acceptance Criteria

1. WHEN an Admin_User accesses configuration settings, THE Registration_System SHALL display editable parameters for registration period dates
2. WHEN an Admin_User modifies seat pricing, THE Registration_System SHALL update rowing seat and cox seat prices for all new registrations
3. THE Registration_System SHALL provide Admin_Users with access to the predefined list of 28 competition categories
4. WHEN an Admin_User sets grace period duration, THE Registration_System SHALL apply the configured delay for payment notifications
5. THE Registration_System SHALL log all Admin_User configuration changes with timestamps and user identification

### FR-6: Registration Validation and Management

**User Story:** As an admin user, I want to validate and manage registrations, so that I can ensure compliance with competition rules and handle exceptions.

#### Acceptance Criteria

1. WHEN an Admin_User reviews registrations, THE Registration_System SHALL display crew member information with validation status indicators
2. WHEN an Admin_User identifies registration issues, THE Registration_System SHALL allow flagging of problems visible to the corresponding team manager
3. IF a team manager has resolved a flagged issue, THE Registration_System SHALL display the flagged issue as resolved by team manager
4. WHILE the registration period is active, THE Registration_System SHALL enable team managers to correct flagged issues autonomously
5. WHEN the registration period ends, THE Registration_System SHALL allow Admin_Users to manually edit registration information or grant temporary editing access to specific team managers
6. WHEN an Admin_User grants editing exceptions, THE Registration_System SHALL apply a configurable time limit with automatic expiration

### FR-7: Reporting and Analytics

**User Story:** As an admin user, I want to access comprehensive reporting and analytics, so that I can monitor registration progress and export data for competition management.

#### Acceptance Criteria

1. WHEN an Admin_User accesses the dashboard, THE Registration_System SHALL display real-time statistics including participant counts and boats per category
2. WHEN an Admin_User requests data export, THE Registration_System SHALL generate CSV or Excel files containing all boat and crew member details
3. THE Registration_System SHALL provide Admin_Users with financial reports showing the ratio of paid seats to registered seats
4. THE Registration_System SHALL track and display registration metrics including total participants and category distribution
5. THE Registration_System SHALL maintain audit logs of all Admin_User actions with role-based tagging

### FR-8: Boat Rental Management

**User Story:** As a team manager from an external club, I want to request boat rentals from RCPM, so that my crews can participate in the competition using available boats.

#### Acceptance Criteria

1. WHEN a Team_Manager from an External_Club accesses boat rental options, THE Registration_System SHALL display available RCPM boats for rental based on current availability
2. WHEN a Team_Manager requests a Boat_Rental, THE Registration_System SHALL record the request with boat type, competition category, and team manager contact information
3. WHILE the Rental_Priority_Period is active, THE Registration_System SHALL reserve requested boats for RCPM_Members and mark external rental requests as pending
4. WHEN the Rental_Priority_Period expires, THE Registration_System SHALL automatically confirm pending External_Club rental requests for unreserved boats
5. WHEN a Boat_Rental is confirmed, THE Registration_System SHALL notify the Team_Manager via email and update the boat availability status
6. THE Registration_System SHALL calculate rental fees at three times the standard seat price for individual boats (skiffs) and standard seat pricing for crew boats
7. WHEN an Admin_User manages boat rentals, THE Registration_System SHALL provide tools to manually assign boats to rental requests and override automatic allocation
8. THE Registration_System SHALL track all Boat_Rental transactions and include rental fees in the team's total payment calculation

### FR-9: Seat Rental for Mixed Crews

**User Story:** As a team manager, I want to manage seat rental fees for external club members in mixed crews, so that I can properly account for all participation costs.

#### Acceptance Criteria

1. WHEN a Team_Manager creates a Mixed_Crew registration, THE Registration_System SHALL identify external club members rowing with RCPM_Members
2. WHEN external club members are assigned to seats in Mixed_Crews, THE Registration_System SHALL automatically apply Seat_Rental fees to the registration
3. THE Registration_System SHALL calculate Seat_Rental fees at the standard seat price for each external club member in a Mixed_Crew
4. WHEN payment is processed for Mixed_Crews, THE Registration_System SHALL include Seat_Rental fees in the total amount due
5. THE Registration_System SHALL display Seat_Rental charges separately in payment summaries and receipts for transparency
6. WHEN an Admin_User reviews registrations, THE Registration_System SHALL clearly identify Mixed_Crews and associated Seat_Rental fees
7. THE Registration_System SHALL generate reports showing Seat_Rental revenue to encourage RCPM club crew formation

### FR-10: Dynamic Configuration Management

**User Story:** As an admin user, I want to be able to change the configuration of the Registration_System, so that I can modify the list of competition categories, registration period dates, and other system parameters dynamically.

#### Acceptance Criteria

1. WHEN an Admin_User accesses the system configuration interface, THE Registration_System SHALL display all configurable parameters in an organized and editable format
2. WHEN an Admin_User modifies the list of competition categories, THE Registration_System SHALL validate the changes and update the available categories for new boat registrations
3. WHEN an Admin_User changes registration period start and end dates, THE Registration_System SHALL validate that the start date is before the end date and apply the changes immediately
4. WHEN an Admin_User updates seat pricing configuration, THE Registration_System SHALL apply the new prices to all future registrations while preserving existing registration pricing
5. WHEN an Admin_User modifies grace period settings, THE Registration_System SHALL update the payment notification timeline for all affected registrations
6. THE Registration_System SHALL require Admin_User confirmation before applying configuration changes that could affect existing registrations
7. WHEN configuration changes are applied, THE Registration_System SHALL log all modifications with timestamps, previous values, new values, and Admin_User identification
8. IF configuration changes fail validation, THEN THE Registration_System SHALL display clear error messages and prevent the invalid changes from being saved

### FR-11: Home Page Information Display

**User Story:** As any user, I want to view general information and subscription process details on the home page, so that I can understand the competition and registration procedures before creating an account.

#### Acceptance Criteria

1. WHEN any user accesses the Registration_System home page, THE Registration_System SHALL display general information about the Course des Impressionnistes competition
2. THE Registration_System SHALL display the subscription process and registration procedures as defined in Appendix B
3. THE Registration_System SHALL provide clear navigation options for users to either log in to an existing account or create a new account
4. THE Registration_System SHALL display current registration period dates and deadlines prominently on the home page
5. THE Registration_System SHALL show all home page content in the user's selected language (French or English)
6. THE Registration_System SHALL provide contact information for RCPM organization for users who need assistance

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
4. THE Registration_System SHALL scale down to zero where possible out of the registration period

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

1. WHEN registration events occur, THE Registration_System SHALL send email notifications for confirmations, issues, and deadline reminders
2. THE Registration_System SHALL repeat notifications via email on a regular basis (default weekly) if there are ongoing issues
3. THE Registration_System SHALL display in-app notifications through banners or popups for immediate user attention
4. WHEN approaching registration deadlines, THE Registration_System SHALL notify team managers via both email and in-app notifications
5. THE Registration_System SHALL provide a notification center within the application for users to review message history
6. THE Registration_System SHALL ensure all notifications are delivered in the user's selected language preference

## 3. Technical Constraints

These requirements define the mandatory technical architecture and implementation constraints.

### TC-1: Serverless Architecture Constraint

**Constraint:** The system must be implemented using a serverless architecture on AWS.

#### Acceptance Criteria

1. THE Registration_System SHALL utilize AWS Lambda functions written in Python for all backend processing
2. THE Registration_System SHALL store all data in Amazon DynamoDB with encryption at rest enabled
3. WHEN traffic increases, THE Registration_System SHALL automatically scale Lambda functions and DynamoDB capacity without manual intervention
4. THE Registration_System SHALL serve the frontend application through Amazon S3 and CloudFront for optimal performance

### TC-2: Infrastructure as Code Constraint

**Constraint:** All infrastructure must be defined and deployed using Infrastructure as Code practices.

#### Acceptance Criteria

1. THE Registration_System SHALL implement Infrastructure as Code using AWS CDK in Python language for reproducible deployments
2. THE Registration_System SHALL backup the data to Amazon S3 on a regular basis (default daily) with a prefix of the current year and an object name with full date/time
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
2. WHEN a DevOps_User accesses the configuration store, THE Registration_System SHALL display all system parameters including registration periods, pricing, categories, and notification settings
3. THE Registration_System SHALL provide DevOps_Users with read-only access to configuration values through AWS Systems Manager Parameter Store or equivalent service
4. WHEN configuration changes are made through the admin interface, THE Registration_System SHALL automatically update the centralized configuration store
5. WHEN a DevOps_User needs to manually modify configuration for emergency purposes, THE Registration_System SHALL provide secure CLI or API access with proper authentication
6. THE Registration_System SHALL validate all configuration changes to ensure system integrity before applying them
7. THE Registration_System SHALL notify relevant Admin_Users when DevOps_Users make manual configuration changes

## Appendix A: Reference Data

### A.1 Registration Logic

The registration logic follows the French Rowing Federation (FFA) rules and competition structure:

#### Competition Structure
The Course des Impressionnistes consists of two distinct events:
- **Semi-marathon (21 km)**: Raced in fours and eights of all configurations
- **Marathon (42 km)**: Individual race in single sculls (skiffs)

#### Age Categories (based on average crew age)
- **J16**: 16 years old and under (safety requirement: must have coxswain)
- **J18**: 17-18 years old
- **Senior**: 19 years and older
- **Master**: 27 years and older (average age ≥ 27)

#### Gender Categories and Crew Composition Rules
- **Men's crews**: More than 50% men
- **Women's crews**: 100% women
- **Mixed crews**: At least 1 man and at least 50% women
- **Substitution rules**: Women can substitute for men in men's or mixed crews; men cannot substitute for women in women's or mixed crews

#### Boat Types and Configurations
Boat notation format: [Gender][Boat Type][Number of Rowers][Oar Type][Coxswain]
- Gender: H (Homme/Men), F (Femme/Women), M (Mixte/Mixed)
- Boat Type: o (outrigger), y (yolette)
- Oar Type: x (sculling/couple), / (sweep/pointe)
- Coxswain: + (with cox), - (without cox)

Example: H4x+ = Men's four with sculling oars and coxswain

#### Competition Categories (28 total)
Categories are numbered sequentially for race programming based on the boat configurations allowed for each age group.

| Category Number | category name (in french)                                    |
  | --------------- | ------------------------------------------------------------ |
  | 1               | FEMME-CADET-QUATRE DE POINTE OU COUPLE AVEC BARREUR          |
  | 2               | HOMME-CADET-QUATRE DE POINTE OU COUPLE AVEC BARREUR          |
  | 3               | MIXTE-CADET-QUATRE DE POINTE OU COUPLE AVEC BARREUR          |
  | 4               | FEMME-CADET-HUIT DE POINTE AVEC BARREUR                      |
  | 5               | HOMME-CADET-HUIT DE POINTE AVEC BARREUR                      |
  | 6               | FEMME-JUNIOR-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
  | 7               | HOMME-JUNIOR-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
  | 8               | MIXTE-JUNIOR-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
  | 9               | HOMME-JUNIOR-QUATRE DE POINTE AVEC BARREUR                   |
  | 10              | FEMME-JUNIOR-HUIT DE POINTE AVEC BARREUR                     |
  | 11              | HOMME-JUNIOR-HUIT DE POINTE AVEC BARREUR                     |
  | 12              | FEMME-SENIOR-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
  | 13              | HOMME-SENIOR-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
  | 14              | HOMME SENIOR-QUATRE DE POINTE AVEC BARREUR                   |
  | 15              | FEMME-SENIOR-HUIT DE POINTE AVEC BARREUR                     |
  | 16              | HOMME-SENIOR-HUIT DE POINTE AVEC BARREUR                     |
  | 17              | FEMME-MASTER-QUATRE DE POINTE OU COUPLE AVEC BARREUR YOLETTE |
  | 18              | HOMME-MASTER-QUATRE DE POINTE OU COUPLE AVEC BARREUR YOLETTE |
  | 19              | MIXTE-MASTER-QUATRE DE POINTE OU COUPLE AVEC BARREUR YOLETTE |
  | 20              | FEMME-MASTER-QUATRE DE POINTE OU COUPLE AVEC BARREUR         |
  | 21              | HOMME-MASTER-QUATRE DE POINTE OU COUPLE AVEC BARREUR         |
  | 22              | MIXTE-MASTER-QUATRE DE POINTE OU COUPLE AVEC BARREUR         |
  | 23              | FEMME-MASTER-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
  | 24              | HOMME-MASTER-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
  | 25              | MIXTE-MASTER-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
  | 26              | FEMME-MASTER-HUIT DE POINTE OU COUPLE AVEC BARREUR           |
  | 27              | HOMME-MASTER-HUIT DE POINTE OU COUPLE AVEC BARREUR           |
  | 28              | MIXTE-MASTER-HUIT DE POINTE OU COUPLE AVEC BARREUR           |

#### Registration Flow for Team Managers
1. **Select Event Type**: Choose between semi-marathon (21km) or marathon (42km) competition
2. **Configure Boat Setup**: Specify the number of rowers and whether the boat includes a coxswain
3. **Assign Crew Members**: Allocate registered crew members to specific seats within the boat
4. **Choose Competition Category**: Select from available categories that match the crew composition (system automatically filters categories based on crew member ages and genders)


### A.2 Boat and Seat Rental Rules

#### Boat Rental Priority System
1. RCPM boats are available for rental based on availability
2. RCPM members have priority until 15 days before registration closure
3. After priority period, unreserved boats are allocated to external club requests
4. Rental pricing: 3x seat price for individual boats (skiffs), standard seat price for crew boats

#### Seat Rental for Mixed Crews
- External club members rowing in mixed crews with RCPM members pay seat rental fees
- Seat rental fee equals standard seat price per external member
- Purpose: Encourage RCPM members to form club-only crews

## Appendix B: Home Page Content

### B.1 General Information About Course des Impressionnistes

**What is the Course des Impressionnistes?**

The Course des Impressionnistes is a rowing regatta featuring two distinct events:

**Semi-Marathon (21 km)**
- Distance: 21 kilometers
- Boat types: Fours and eights in all configurations
- Categories: Competitive outriggers and recreational yolettes
- Oar configurations: Sweep rowing (one oar per rower) or sculling (two oars per rower)
- Crew compositions: Men's, women's, and mixed crews
- Age categories: J16, J18, Senior, and Master

**Marathon (42 km)**  
- Distance: 42 kilometers
- Boat type: Individual single sculls (skiffs)
- Categories: Men's and women's in Senior and Master A-H divisions

**Competition Features:**
- 28 different race categories for the semi-marathon
- Individual time trial format for the marathon
- Awards: Medals and trophies for winners, medals for single-entry categories
- Professional timing and results management

### B.2 Registration and Subscription Process

**Registration Period**
- Registration opens: March 19th (may open earlier on March 1st if ready)
- Registration closes: April 19th
- Payment deadline: April 25th
- Late changes: Crew substitutions and withdrawals accepted after closure

**Who Can Register**
- Rowing club team managers register on behalf of their clubs
- Multiple managers per club allowed (e.g., individual marathon participants)
- All participants must hold valid French Rowing Federation licenses

**Registration Flow for Team Managers**

**Getting Started**
Team managers register their club and crews through a simple online process. Each club can have multiple managers, and the system guides you through every step.

**The Registration Journey**

1. **Set Up Your Access**
   Create your manager account using your club's federation details and contact information. You'll receive secure login credentials to access the registration system throughout the season.

2. **Build Your Team Roster**  
   Add all potential participants to your club's roster with their essential information: name, birth date, gender, and FFA license number. This roster becomes your pool of available crew members for all boat registrations.

3. **Create Boat Entries**
   Select from 28 race categories and configure each boat entry by choosing the boat type, oar configuration, and assigning specific crew members to rowing and coxswain positions. The system automatically validates your crew against competition rules.

4. **Handle Equipment Needs**
   If you need boats, submit rental requests through the system. RCPM boats are available on a priority basis, with club members having first access until two weeks before registration closes.

5. **Process Payments**
   Review your total costs and complete payment using the integrated secure payment system. You can pay for individual entries or process multiple registrations together, with flexibility to pay before the final deadline.

6. **Ongoing Management**
   Monitor your registrations, make permitted changes during the open period, and handle any crew substitutions or withdrawals that may be needed after registration closes.

**Key Benefits**
- Save partial registrations and complete them later
- Automatic validation against competition rules  
- Flexible payment options with secure processing
- Real-time availability for boat rentals
- Complete registration history and status tracking

**Pricing Structure**
- Standard seat fee (includes coxswain for coxed boats)
- Boat rental: 3x seat price for singles, standard rate for crew boats
- Seat rental: Standard seat price for external members in mixed crews

**Support and Assistance**
- License verification handled automatically or manually
- Registration modification allowed during open period
- Administrative support for complex registrations
- Comprehensive reporting for club managers

**Important Dates to Remember**
- March 19: Registration opens
- April 19: Registration closes  
- April 25: Payment deadline
- 15 days before closure: RCPM boat priority ends

