# Course des impressionnistes competition application requirements

## Functionnal requirement 

### Initial functionnal requirement PDF file

- [Requerement initial document in french](./web-application-impressionnistes-initial-functionnal-requirements.pdf)

### Additions or modifications from the initial functionnal requirements
Below, the "user" is the person in charge or registering one or more boats and crews for the impressionnist competition on behalf of their rowing club. This is typically a coach but it could be any individual.
1. We want to have a simple approach for registering crews boats. 
  - The user will pay for the seats (rowing seat and cox seat have different prices - this is a parameter to add to the admin interface). 
  - So the user must be able to define crew members in a page. 
  - Then in another page she will be able to associate each crew member to a seat in a boat (rower seat or cox seat) in the different categories.
2. The list of crew members and boats remains and these things are editable by the user each time she logs in until the RCPM organization is ending the registration period at the established time.
  - after that point the user can view the registered boats/crews but can't edit anything
3. Payment happens at any time once the user has finalised her boats/crews registrations.
4. Before the end of the registration period
  - the RCPM organization is checking the crew members' licence and other parameters. Through the admin page, the RCPM admin should be able to point issues like this (like wrong licence number) and the user should notice it when viewing its boats/crews registrations. This helps her fixing the issues autonomously.
5. After the end of the registration period
   - If payment is not done (or partially done) before end of the registration period, the user will be notified a short delay (typically few days - a parameter to be added in the admin config) before which the registration will be canceled.
   - The RCPM organization is checking the crew members' licence and other parameters. But the user can't change the boats/crews. So in case or irregularities, the RCPM admin must be able to notify the user and edit some items manually. An alternative would be that the RCPM admin would enable this particular user to edit the registration as an exception and disable it after the user has fixed the issue.
6. The language of the user interface in primarily in french and in english. We base the language on the user browser language or the language chosen by the user afterwards

### Additional questions / answers

### 1. Registration Period Management
* What is the default registration period duration?
  * Usually starting 2 months before the competition and ending 2 weeks before it
* How should the system handle timezone differences?
  * one single time zone Paris - France
* Should there be early-bird registration periods?
  * not specifically
* How are users notified of approaching deadlines?
  * in the application on a banner or equivalent. By email in addition ideally
* Can RCPM admins extend the registration period for specific users?
  * yes

### 2. Crew and Boat Registration Flow
* Should users be able to save crew member information as templates for future use?
  * Not as templates. the crew is saved in a boat and is visible and editable until the end of the registration period
* How should the system handle crew member substitutions?
  * The user that is accessing the application is actually a team manager in charge of registering the crews she is in charge of. She is typically a reprentent of her club adding the name and attribute or other rowers.
* Is there a minimum number of crew members needed before a boat can be registered?
  * The user can save a boat with partial crew and come back later to finish. a boat is complete when all the seats are associated by a crew member
* Should there be a preview/summary step before finalizing registration?
  * There is a page where the boats are listed and the user can click on an edit button to edit a boat.
* How should seat assignments be visualized in the interface?
  * a boat is a list of seats numbers. for each number there is an associated name of a crew member. A SKIFF (or 1x) is one rowing seat, a QUATRE AVEC BARREUR is 4 rowing seats and a cox seat, a QUATRE SANS BARREUR in 4 rowing seats without cox, a HUIT is 8 rowing seats and a cox seat.

### 3. Meal Management
* Actually we no longer want any meal management in the application

### 4. Admin Configuration
* What parameters should be configurable by admins?
  * Registration period
  * seats prices for rowers and cox (different prices)
  * the list of possible categories is:
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
  
* Should there be different levels of admin access?
  * No one single is ok
* What reporting capabilities are needed?
  * We need to be able to exporte all the saved boats with crew details as a CSV or Excel to be downloaded
* How should admin actions be logged?
  * nothing particular just regular logs with Admin vs regular user as a tag
* What bulk operations should be available to admins?
  * nothing special

### 5. Payment and Cancellation
* How should partial payments be tracked?
  * yes see above, after the registration period, the user will be notified.
* What is the cancellation policy?
  * If a user wants to cancel one or more boats after payment or after the registration period, RCPM should be contacted by email by the user.
* Should there be automatic cancellation for unpaid registrations?
  * no, we must notify the user by email saying that in case the payment is not done before the day of the competition, they will not be able to take place in the competition.
* How are refunds handled for cancelled registrations?
  * The refund will be done manually by RCPM organization after the user has contacted RCPM by email
* Should there be an option for payment plans?
  * No

### 6. License Validation
* What are the specific license validation rules?
  * There an alpha numeric string. 
* How should invalid licenses be flagged?
  * we can't directly validate ourself for the moment unfortunately. in the future, this will be checked by calling a third party API.
* Should there be automatic license validation?
  * no
* What documentation is required for license verification?
  * no documentation
* How are international licenses handled?
  * we will not validate apart that this is alphanumeric value

### 7. Notification System
* What types of notifications are needed?
  * By email and as banners or popup in the application
* Should users be able to choose their notification preferences?
  * no
* How should urgent notifications be handled?
  * by email. there is in general nothing urgent.
* Should there be an in-app notification center?
  * yes
* What notification channels should be supported (email, SMS, etc.)?
  * email

### 8. Exception Handling
* How should registration exceptions be handled?
  * No documentation
  * the Admin decides to extend the registration period for chosen users for them to adjust registration information that are not valid.
  * The Admin decides to activate this extension with a toggle button for the chosen user for a default duration of 2 days (adjustable)

### 9. Reporting and Analytics
* What reports are needed for event management?
  * no specific report
* Should there be real-time registration statistics?
  * Yes, ideally the admin should see this kind of statistics on he's home page.
* What financial reports are required?
  * the ratio of payed seats compared to the registered seats
* How should registration data be exported?
  * export of all the boats/crew members as CSV or Excel file
* What metrics should be tracked?
  * Number of participants already registered
  * Number of boats in each category

### 10. Multi-language Support
* Which languages need to be supported?
  * French and english
* How should language preferences be managed?
  * French is the default but inglish can be chosen
* Should admin communications be multilingual?
  * yes
* How should language switching be handled?
  * We can have the default laguage taken from the browser configuration and if this is different than French of english, we should stick to english. But we need to be able to manually switch to/from english/frensh at any time
* Are there specific regional requirements
  * no time zone in Paris France.

# Comprehensive Functional Requirements - Course des Impressionnistes Competition Application

## 1. Overview

The Course des Impressionnistes competition application is designed to manage the registration of rowing teams, boats, and crew members for the competition organized by RCPM. The system allows team managers to register crew members, assign them to specific seats in boats across various categories, and process payments for participation.

## 2. User Roles and Authentication

### 2.1 User Roles
- **Team Manager**: Represents a rowing club and registers boats and crews
- **Admin**: RCPM organization staff who manages the system, validates registrations, and handles exceptions

### 2.2 Authentication
- Standard email/password authentication
- Password recovery via email
- Session persistence with automatic logout after inactivity
- User data includes: name, email, rowing club affiliation, contact information (mobile number is mandatory)

## 3. Registration Process

### 3.1 Registration Period
- Default period: Starting 2 months before competition, ending 2 weeks before
- Single timezone: Paris, France
- Approaching deadline notifications via email and in-app banner
- Admin can extend registration period for specific users

### 3.2 Crew Member Management
- Team managers can add crew members with required information:
  - Name
  - Date of birth
  - Gender
  - License number (alphanumeric)
  - Category (Cadet, Junior, Senior, Master)
- Crew members can be edited until the end of the registration period
- No templates, but crew information persists throughout the registration period

### 3.3 Boat Registration
- Team managers can register multiple boats across different categories
- Boats can be saved with partial crew and completed later
- A boat is complete when all required seats are filled
- Seat types:
  - Rowing seats (paid)
  - Cox seats (paid, different price)
- Boat types include:
  - SKIFF (1x): One rowing seat
  - QUATRE AVEC BARREUR: Four rowing seats and one cox seat
  - QUATRE SANS BARREUR: Four rowing seats, no cox
  - HUIT: Eight rowing seats and one cox seat
- 28 different categories as specified in the requirements
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
  
### 3.4 Registration Interface
- Crew member registration page
- Boat configuration page with seat assignment
- Summary page showing all registered boats with edit options
- Visualization of seat assignments with crew member names

## 4. Payment System

### 4.1 Payment Process
- Payment via Stripe integration
- Different pricing for rowing seats and cox seats (configurable by admin)
- Payment can occur at any time after boat/crew registration
- Partial payments are tracked and visible to users
- No payment plans available

### 4.2 Cancellation and Refunds
- Unpaid registrations after the registration period receive notification with grace period
- No automatic cancellation for unpaid registrations
- Cancellations after payment require email contact with RCPM
- Refunds handled manually by RCPM organization

## 5. Admin Functions

### 5.1 Configuration
- Set registration period start/end dates
- Configure seat prices (rowing and cox)
- Manage category list
- Set grace period for payment after registration closes

### 5.2 Validation Process
- Admin can review crew member information
- Flag issues with license numbers or other parameters
- Issues are visible to team managers for correction before registration period ends
- After registration period, admin can:
  - Manually edit registration information
  - Grant temporary extension to specific users to fix issues
  - Set extension duration (default: 2 days)

### 5.3 Reporting
- Export all registered boats with crew details (CSV/Excel)
- View real-time registration statistics on admin dashboard
- Financial reports showing paid vs. registered seat ratio
- Track number of participants and boats per category

## 6. User Experience

### 6.1 Multilingual Support
- Primary languages: French and English
- Default language based on browser settings (defaulting to English if neither French nor English)
- Manual language switching available at any time
- Admin communications in both languages

### 6.2 Notifications
- Email notifications for:
  - Registration confirmation
  - Issues requiring attention
  - Payment confirmation
  - Registration period ending
  - Grace period for payment
- In-app notifications via banner or popup
- Simple notification center within the application

### 6.3 User Interface
- Mobile responsive design
- Clear visualization of boat configurations and seat assignments
- Summary views of registered boats and crews
- Status indicators for registration completion, payment, and validation

## 7. Post-Registration Period

### 7.1 View-Only Access
- After registration period ends, team managers can view but not edit registrations
- Exception: When granted temporary extension by admin

### 7.2 Exception Handling
- Admin can enable editing for specific users after registration period
- Extension has configurable duration (default: 2 days)
- User notified of extension via email and in-app notification

### 7.3 Final Validation
- RCPM performs final validation of all registrations
- Issues handled through manual admin edits or temporary user extensions
- Unpaid registrations allowed to participate only if payment received before competition day

## 8. Technical Details

### 8.1 Data Export
- Export functionality for all registration data (CSV/Excel)
- Data retention according to legal requirements

### 8.2 Error Handling
- Clear error messages for validation issues
- Graceful handling of payment processing failures
- Connection issue recovery

### 8.3 Logging
- Admin actions logged with user role tags
- Standard application logging


# Technical Requirements

## 1. Technology Stack

### 1.1 Frontend
- **Framework**: Vue.js (Vue 3 with Composition API)
- **Responsive Design**: Support for mobile, tablet, and laptop screen sizes
- **Languages**: JavaScript/TypeScript
- **UI Components**: Consider Tailwind CSS, Vuetify, or Bootstrap Vue

### 1.2 Backend
- **Language**: Python
- **Architecture**: Serverless with AWS Lambda
- **API**: RESTful API via AWS API Gateway
- **Documentation**: OpenAPI/Swagger documentation for all endpoints

### 1.3 Database
- **Type**: NoSQL - Amazon DynamoDB
- **Data Model**: Document-based structure for flexible schema
- **Encryption**: At-rest encryption enabled

## 2. AWS Infrastructure

### 2.1 Core Services
- **Compute**: AWS Lambda for serverless functions
- **API Management**: API Gateway for RESTful endpoints
- **Database**: DynamoDB for data storage
- **Authentication**: Amazon Cognito with social login (Google, Microsoft, Apple)
- **Static Hosting**: S3 for frontend assets
- **CDN**: CloudFront for content delivery

### 2.2 Supporting Services
- **Deployment**: AWS CDK for infrastructure as code
- **CI/CD**: AWS CodePipeline, CodeBuild, and CodeDeploy
- **Monitoring**: CloudWatch for logs and alerts
- **Backup**: DynamoDB Point-in-Time Recovery and scheduled backups

## 3. Security Requirements

### 3.1 Authentication & Authorization
- Cognito user pools for authentication
- JWT token-based authorization
- Role-based access control (user vs. admin)
- Social login integration (Google, Microsoft, Apple)

### 3.2 Data Protection
- Encryption at rest for all data stores
- HTTPS/TLS for all data in transit
- Secure handling of payment information via Stripe
- Proper IAM roles with least privilege principle

### 3.3 Compliance
- GDPR compliance for user data
- Implementation of user rights (access, deletion, portability)
- Data minimization principles
- Clear consent mechanisms

## 4. Integration Requirements

### 4.1 Payment Processing
- Stripe integration for payment processing
- Secure API key management
- Webhook implementation for payment events
- Frontend integration using Stripe Elements

## 5. Performance & Scalability

### 5.1 Performance Targets
- Page load times under 3 seconds
- Optimized frontend bundle size
- Efficient database queries

### 5.2 Scalability Approach
- On-demand Lambda scaling
- DynamoDB on-demand capacity
- No pre-provisioning initially, but capability in place
- CloudFront caching for static assets

## 6. Browser Compatibility

- Support for latest two versions of major browsers:
  - Google Chrome
  - Mozilla Firefox
  - Apple Safari
  - Microsoft Edge

## 7. Localization

- Bilingual support (French and English)
- Default to browser language (French if detected, English otherwise)
- User-selectable language toggle
- Localized content for all UI elements and notifications

## 8. Testing Strategy

- Unit tests for frontend components and backend functions
- Test automation as part of CI/CD pipeline
- Focus on critical business logic and user flows

## 9. Monitoring & Operations

- CloudWatch logs for application monitoring
- CloudWatch alarms for error conditions
- Structured logging in JSON format
- Email alerts for critical issues

## 10. Backup & Recovery

- Daily DynamoDB backups
- 35-day point-in-time recovery capability
- Documented recovery procedures
- Infrastructure as code for quick redeployment

# Development Timeline

## Phase 1: Core User Journey MVP (1-2 months)

### Focus Areas
- Basic authentication with Cognito and social login
- Crew member management functionality
- Boat registration and seat assignment
- Simple admin dashboard for viewing registrations
- Responsive UI for core screens with bilingual support

### Deliverables
- Functional user registration and login
- Crew member creation and management
- Boat configuration and registration flow
- Basic admin view of registrations
- Deployment pipeline and environments

## Phase 2: Payment and Validation (Additional 1-2 months)

### Focus Areas
- Stripe payment integration
- Enhanced validation workflows
- User dashboard for registration status
- Admin validation capabilities
- Notification system

### Deliverables
- Complete payment processing flow
- Registration validation functionality
- User dashboard showing registration status
- Admin tools for validation and issue flagging
- Email and in-app notifications

## Phase 3: Refinement and Additional Features (Ongoing)

### Focus Areas
- UI/UX improvements based on user feedback
- Performance optimizations
- Enhanced admin reporting
- Additional features identified during testing

### Deliverables
- Polished user interface
- Optimized application performance
- Comprehensive admin reporting tools
- Implementation of feedback-driven features
