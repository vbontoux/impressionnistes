# Requirements Document: GDPR Compliance

## Introduction

This specification defines the mandatory GDPR (General Data Protection Regulation) compliance requirements for the Impressionnistes registration system. The system processes personal data of rowing event participants and must comply with EU data protection law. This document focuses strictly on legally mandatory requirements under GDPR Articles 6, 7, 12-22, and 32-34.

## Glossary

- **Personal_Data**: Any information relating to an identified or identifiable natural person (email, name, date of birth, phone number, etc.)
- **Data_Subject**: An individual whose personal data is processed by the system (registered users, crew members)
- **Data_Controller**: The organization responsible for determining purposes and means of processing personal data (event organizers)
- **Processing**: Any operation performed on personal data (collection, storage, use, disclosure, deletion)
- **Consent**: Freely given, specific, informed, and unambiguous indication of the data subject's agreement to processing
- **Legal_Basis**: The lawful ground for processing personal data under GDPR Article 6
- **Privacy_Policy**: Document explaining what data is collected, why, how it's used, and data subject rights
- **Cookie**: Small text file stored on user's device by the website
- **Data_Retention**: How long personal data is kept before deletion
- **Right_to_Access**: Data subject's right to obtain confirmation and copy of their personal data (Article 15)
- **Right_to_Erasure**: Data subject's right to have their personal data deleted (Article 17)
- **Right_to_Portability**: Data subject's right to receive their data in a structured, machine-readable format (Article 20)

## Requirements

### Requirement 1: Lawful Basis and Consent (GDPR Article 6 & 7)

**User Story:** As a data controller, I want to establish a lawful basis for processing personal data and obtain valid consent, so that data processing is legally compliant.

#### Acceptance Criteria

1. WHEN a user registers, THE System SHALL obtain explicit consent before processing personal data
2. WHEN displaying the consent request, THE System SHALL clearly state what data is collected and for what purpose
3. WHEN a user provides consent, THE System SHALL record the timestamp and consent version
4. WHEN a user has not consented, THE System SHALL NOT allow registration to proceed
5. THE System SHALL provide a link to the Privacy Policy before consent is given
6. THE System SHALL make consent optional for non-essential processing (marketing) and mandatory for essential processing (registration)
7. WHEN consent is given, THE System SHALL store it in a way that proves consent was obtained

### Requirement 2: Privacy Policy (GDPR Article 13 & 14)

**User Story:** As a data subject, I want to read a clear privacy policy, so that I understand how my personal data will be processed.

#### Acceptance Criteria

1. THE System SHALL provide a Privacy Policy accessible from all pages
2. THE Privacy Policy SHALL be available in both French and English
3. THE Privacy Policy SHALL identify the data controller (organization name and contact)
4. THE Privacy Policy SHALL list all types of personal data collected (email, name, DOB, phone, club, gender, license number)
5. THE Privacy Policy SHALL explain the purpose of data collection (event registration, race management, results publication)
6. THE Privacy Policy SHALL state the legal basis for processing (consent and legitimate interest)
7. THE Privacy Policy SHALL explain data retention periods (how long data is kept)
8. THE Privacy Policy SHALL list all data subject rights (access, rectification, erasure, portability, objection)
9. THE Privacy Policy SHALL explain how to exercise these rights (contact information)
10. THE Privacy Policy SHALL disclose any third-party data sharing (payment processor, email service)
11. THE Privacy Policy SHALL explain security measures in place
12. THE Privacy Policy SHALL include the date of last update

### Requirement 3: Cookie Consent (ePrivacy Directive)

**User Story:** As a website visitor, I want to control which cookies are stored on my device, so that my privacy preferences are respected.

#### Acceptance Criteria

1. WHEN a user first visits the site, THE System SHALL display a cookie consent banner
2. THE cookie consent banner SHALL appear before any non-essential cookies are set
3. THE banner SHALL clearly explain what cookies are used and for what purpose
4. THE banner SHALL provide options to accept all, reject all, or customize cookie preferences
5. THE System SHALL distinguish between essential cookies (required for functionality) and non-essential cookies (analytics, marketing)
6. WHEN a user rejects non-essential cookies, THE System SHALL NOT set those cookies
7. WHEN a user accepts cookies, THE System SHALL record their consent preference
8. THE System SHALL provide a way to change cookie preferences after initial consent
9. THE cookie banner SHALL be available in both French and English
10. THE System SHALL respect the user's cookie choices across sessions

### Requirement 4: Right to Access (GDPR Article 15)

**User Story:** As a data subject, I want to download all my personal data, so that I can see what information the system holds about me.

#### Acceptance Criteria

1. WHEN a logged-in user requests data export, THE System SHALL provide all their personal data in a structured format
2. THE exported data SHALL include: user profile (email, name, phone, club), all crew member records, all boat registrations, payment history, and consent records
3. THE export format SHALL be JSON (machine-readable and structured)
4. WHEN generating the export, THE System SHALL include metadata (export date, data categories)
5. THE System SHALL provide the export within a reasonable timeframe (immediately for automated export)
6. THE System SHALL authenticate the user before providing data export
7. THE exported data SHALL be complete and accurate

### Requirement 5: Right to Erasure (GDPR Article 17)

**User Story:** As a data subject, I want to delete my account and all associated data, so that I can exercise my right to be forgotten.

#### Acceptance Criteria

1. WHEN a logged-in user requests account deletion, THE System SHALL provide a clear deletion interface
2. WHEN confirming deletion, THE System SHALL warn the user that this action is irreversible
3. WHEN a user confirms deletion, THE System SHALL delete all personal data including: user account, profile information, crew member records, and consent records
4. WHEN deleting data, THE System SHALL handle foreign key constraints (anonymize or delete related records)
5. THE System SHALL complete deletion within 30 days of the request
6. WHEN deletion is complete, THE System SHALL send a confirmation email to the user's registered email
7. THE System SHALL retain only data required by law (financial records for tax purposes) and anonymize it
8. WHEN a user has active boat registrations, THE System SHALL either prevent deletion or transfer ownership/anonymize the registrations

### Requirement 6: Data Retention Policy (GDPR Article 5)

**User Story:** As a data controller, I want to define and enforce data retention periods, so that personal data is not kept longer than necessary.

#### Acceptance Criteria

1. THE System SHALL define retention periods for each data category
2. THE retention period for user accounts SHALL be: active accounts retained indefinitely, inactive accounts (no login for 3 years) flagged for review
3. THE retention period for event registrations SHALL be: 5 years after the event date (for historical records and dispute resolution)
4. THE retention period for payment records SHALL be: 7 years (legal requirement for financial records)
5. THE retention period for consent records SHALL be: duration of processing plus 3 years (proof of consent)
6. THE System SHALL document the retention policy in the Privacy Policy
7. THE System SHALL provide a mechanism to review and delete data that exceeds retention periods

### Requirement 7: Data Security (GDPR Article 32)

**User Story:** As a data controller, I want to implement appropriate security measures, so that personal data is protected from unauthorized access and breaches.

#### Acceptance Criteria

1. THE System SHALL encrypt passwords using industry-standard hashing (bcrypt or similar)
2. THE System SHALL use HTTPS for all data transmission
3. THE System SHALL implement authentication and authorization controls
4. THE System SHALL use AWS Cognito for secure user authentication
5. THE System SHALL store data in AWS with appropriate access controls
6. THE System SHALL log access to personal data for audit purposes
7. THE System SHALL implement rate limiting to prevent brute force attacks
8. THE System SHALL validate and sanitize all user inputs to prevent injection attacks

### Requirement 8: Data Breach Notification (GDPR Article 33 & 34)

**User Story:** As a data controller, I want to have a process for handling data breaches, so that I can comply with notification requirements.

#### Acceptance Criteria

1. THE System SHALL document a data breach response procedure
2. THE procedure SHALL include steps to: detect breach, contain breach, assess impact, notify authorities (within 72 hours if required), notify affected users (if high risk)
3. THE System SHALL maintain contact information for the supervisory authority (CNIL in France)
4. THE System SHALL log security incidents for breach assessment
5. THE documentation SHALL be accessible to administrators

### Requirement 9: Terms and Conditions

**User Story:** As a data controller, I want users to agree to terms and conditions, so that the legal relationship and responsibilities are clear.

#### Acceptance Criteria

1. THE System SHALL provide Terms and Conditions accessible from all pages
2. THE Terms and Conditions SHALL be available in both French and English
3. THE Terms and Conditions SHALL define: service description, user responsibilities, liability limitations, dispute resolution, governing law
4. WHEN a user registers, THE System SHALL require acceptance of Terms and Conditions
5. THE System SHALL record acceptance of Terms and Conditions with timestamp
6. THE Terms and Conditions SHALL include the date of last update

### Requirement 10: User Interface for Rights Exercise

**User Story:** As a data subject, I want an easy way to exercise my GDPR rights, so that I can manage my personal data without technical barriers.

#### Acceptance Criteria

1. THE System SHALL provide a "Privacy & Data" section in user account settings
2. THE section SHALL include buttons/links for: Download my data, Delete my account, View Privacy Policy, Manage cookie preferences
3. WHEN a user clicks "Download my data", THE System SHALL generate and download the data export
4. WHEN a user clicks "Delete my account", THE System SHALL show a confirmation dialog with warnings
5. THE interface SHALL be available in both French and English
6. THE interface SHALL be accessible to logged-in users only
7. THE System SHALL provide clear instructions for each action

## Phase Implementation

### Phase 1: Critical Legal Requirements (Immediate Implementation)

**Scope:** Minimum requirements to legally process personal data

**Requirements:** 1 (Consent), 2 (Privacy Policy), 3 (Cookie Consent), 9 (Terms and Conditions)

**Deliverables:**
- Privacy Policy page (French & English)
- Terms and Conditions page (French & English)
- Consent checkbox in registration form
- Cookie consent banner component
- Consent storage in database

### Phase 2: User Rights Implementation

**Scope:** Enable data subjects to exercise their GDPR rights

**Requirements:** 4 (Right to Access), 5 (Right to Erasure), 10 (User Interface)

**Deliverables:**
- Data export API endpoint
- Data export UI in account settings
- Account deletion API endpoint
- Account deletion UI with confirmation
- Privacy & Data settings page

### Phase 3: Operational Compliance

**Scope:** Ongoing compliance and documentation

**Requirements:** 6 (Data Retention), 7 (Data Security), 8 (Data Breach)

**Deliverables:**
- Data retention policy documentation
- Security measures documentation
- Data breach response procedure
- Automated retention enforcement (optional)

## Notes

- This specification focuses on GDPR compliance for a French rowing event registration system
- The system processes personal data of EU residents and must comply with GDPR
- Non-compliance can result in fines up to €20 million or 4% of annual turnover
- Phase 1 is legally required before processing any personal data
- Phases 2 and 3 should be implemented as soon as practically possible
- Legal review of Privacy Policy and Terms by a qualified attorney is strongly recommended
