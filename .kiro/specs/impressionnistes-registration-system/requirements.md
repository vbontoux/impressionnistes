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

1. WHEN a team manager creates a boat registration, THE Registration_System SHALL display available categories from the predefined list of 28 competition categories
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

### FR-8: Dynamic Configuration Management

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

### A.1 Competition Categories

The system shall support the following 28 predefined competition categories:

| Category Number | Category Name (French) |
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

### A.2 Boat Type Configurations

The system shall support the following boat types with their seat configurations:

| Boat Type | Rowing Seats | Cox Seats | Total Seats |
| --------- | ------------ | --------- | ----------- |
| SKIFF (1x) | 1 | 0 | 1 |
| QUATRE AVEC BARREUR | 4 | 1 | 5 |
| QUATRE SANS BARREUR | 4 | 0 | 4 |
| HUIT | 8 | 1 | 9 |