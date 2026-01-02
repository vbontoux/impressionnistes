# GDPR Compliance Guide

## Overview

This guide documents the GDPR (General Data Protection Regulation) compliance implementation for the Course des Impressionnistes registration system. The implementation ensures the system meets EU data protection requirements when processing personal data of event participants.

**Implementation Status**: Phase 1 Complete (Critical Legal Requirements)

## Table of Contents

1. [Legal Pages](#legal-pages)
2. [Cookie Consent System](#cookie-consent-system)
3. [Registration Consent](#registration-consent)
4. [Consent Storage Schema](#consent-storage-schema)
5. [Routes and Navigation](#routes-and-navigation)
6. [Internationalization](#internationalization)
7. [Testing](#testing)
8. [Legal Review Requirements](#legal-review-requirements)
9. [Future Phases](#future-phases)

---

## Legal Pages

### Privacy Policy

**Location**: `frontend/src/views/legal/PrivacyPolicy.vue`

**Route**: `/privacy-policy`

**Purpose**: Provides comprehensive information about data collection, processing, and user rights as required by GDPR Articles 13 & 14.

**Content Includes**:
- Data controller information
- Types of personal data collected
- Purpose of data collection
- Legal basis for processing
- Data retention periods
- Data subject rights (access, rectification, erasure, portability)
- How to exercise rights
- Third-party data sharing
- Security measures
- Contact information
- Last updated date

**Features**:
- Fully bilingual (French and English)
- Responsive design for mobile devices
- Print-friendly layout
- Accessible from footer on all pages
- Linked from registration form

**Accessibility**: Public (no authentication required)

### Terms and Conditions

**Location**: `frontend/src/views/legal/TermsConditions.vue`

**Route**: `/terms-conditions`

**Purpose**: Defines the legal agreement between users and the event organizers.

**Content Includes**:
- Service description
- User responsibilities
- Registration requirements
- Payment terms
- Cancellation policy
- Liability limitations
- Intellectual property
- Dispute resolution
- Governing law
- Contact information
- Last updated date

**Features**:
- Fully bilingual (French and English)
- Responsive design
- Print-friendly layout
- Accessible from footer on all pages
- Linked from registration form

**Accessibility**: Public (no authentication required)

---

## Cookie Consent System

### Cookie Banner

**Location**: `frontend/src/components/legal/CookieBanner.vue`

**Purpose**: Obtains user consent for non-essential cookies before they are set, as required by the ePrivacy Directive.

**Behavior**:
- Appears on first visit (before any non-essential cookies are set)
- Displays as a sticky banner at the bottom of the page
- Does not appear if user has already made a choice
- Respects user choice across sessions

**Actions**:
- **Accept All**: Sets all cookie preferences to true
- **Reject All**: Sets non-essential cookies to false (essential cookies remain enabled)
- **Customize**: Opens the Cookie Preferences modal

**Cookie Categories**:
1. **Essential Cookies** (always enabled)
   - Authentication tokens
   - Session management
   - Security features
   
2. **Analytics Cookies** (optional, currently not implemented)
   - Usage tracking
   - Performance monitoring
   
3. **Marketing Cookies** (optional, currently not implemented)
   - Advertising
   - Personalization

**Storage**: Preferences stored in browser localStorage

**Internationalization**: Fully bilingual (French and English)

### Cookie Preferences Modal

**Location**: `frontend/src/components/legal/CookiePreferences.vue`

**Purpose**: Allows users to customize their cookie preferences with detailed information about each category.

**Features**:
- Modal dialog with toggle switches for each cookie category
- Detailed descriptions of what each category does
- Essential cookies toggle is disabled (always required)
- Save button to persist preferences
- Accessible from Cookie Banner and footer

**Access Points**:
- "Customize" button in Cookie Banner
- "Cookie Preferences" link in footer

### Cookie Consent Storage

**Storage Location**: Browser localStorage

**Key**: `cookie-consent`

**Data Structure**:
```javascript
{
  essential: true,      // Always true (required for functionality)
  analytics: false,     // User preference
  marketing: false,     // User preference
  timestamp: "2025-01-02T10:00:00Z",  // ISO 8601 timestamp
  version: "1.0"        // Consent version
}
```

**Persistence**: Stored indefinitely until user clears browser data or changes preferences

---

## Registration Consent

### Consent Collection

**Location**: `frontend/src/components/RegisterForm.vue` (modified)

**Implementation**: Two required checkboxes added to registration form:

1. **Privacy Policy Consent**
   - Checkbox with link to Privacy Policy
   - Required for registration
   - Text: "I have read and accept the [Privacy Policy]"

2. **Terms & Conditions Consent**
   - Checkbox with link to Terms & Conditions
   - Required for registration
   - Text: "I have read and accept the [Terms & Conditions]"

**Validation**:
- Frontend: Form submission blocked if either checkbox is unchecked
- Backend: Registration request rejected if consent fields are not true
- Error message displayed if validation fails

**Form Data**:
```javascript
{
  // ... existing registration fields
  privacy_consent: boolean,      // Must be true
  terms_consent: boolean,        // Must be true
  consent_version: "1.0"         // Current version
}
```

### Backend Validation

**Location**: `functions/auth/register.py` (modified)

**Validation Logic**:
```python
# Extract consent fields
privacy_consent = body.get('privacy_consent', False)
terms_consent = body.get('terms_consent', False)
consent_version = body.get('consent_version', '1.0')

# Validate consent is explicitly true
if not privacy_consent or not terms_consent:
    return validation_error({
        'consent': 'You must accept the Privacy Policy and Terms & Conditions to register'
    })
```

**Error Response** (400 Bad Request):
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "You must accept the Privacy Policy and Terms & Conditions to register",
    "details": {
      "consent": "Consent is required"
    }
  },
  "timestamp": "2025-01-02T10:00:00Z"
}
```

---

## Consent Storage Schema

### DynamoDB Schema

**Table**: Same table as user data (single-table design)

**Partition Key (PK)**: `USER#{user_id}`

**Sort Key (SK)**: `CONSENT#{consent_type}#{timestamp}`

### Consent Record Structure

```python
{
  'PK': 'USER#{user_id}',                    # Partition key
  'SK': 'CONSENT#{consent_type}#{timestamp}', # Sort key
  'user_id': 'uuid-string',                   # User identifier
  'consent_type': 'privacy_policy' | 'terms_conditions',
  'consent_version': '1.0',                   # Version of legal document
  'consented': True,                          # Always true for consent records
  'consented_at': '2025-01-02T10:00:00Z',    # ISO 8601 timestamp
  'ip_address': '192.168.1.1',               # Optional, for audit trail
  'created_at': '2025-01-02T10:00:00Z'       # Record creation timestamp
}
```

### Consent Types

1. **privacy_policy**: User accepted the Privacy Policy
2. **terms_conditions**: User accepted the Terms & Conditions

### Query Patterns

**Get all consents for a user**:
```python
response = table.query(
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
    ExpressionAttributeValues={
        ':pk': f'USER#{user_id}',
        ':sk': 'CONSENT#'
    }
)
```

**Get specific consent type**:
```python
response = table.query(
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
    ExpressionAttributeValues={
        ':pk': f'USER#{user_id}',
        ':sk': 'CONSENT#PRIVACY#'
    }
)
```

### Consent Record Creation

**When**: During user registration (after Cognito user creation)

**Process**:
1. User submits registration form with consent checkboxes checked
2. Backend validates consent fields are true
3. Backend creates Cognito user
4. Backend stores two consent records in DynamoDB:
   - One for Privacy Policy consent
   - One for Terms & Conditions consent
5. Both records include timestamp and optional IP address

**Code Location**: `functions/auth/register.py`

### Consent Immutability

- Consent records are **never updated** (immutable)
- New consent records are created if user re-consents (e.g., after document updates)
- Historical consent records are preserved for audit trail
- Timestamp in SK ensures unique records for each consent event

### IP Address Capture

**Purpose**: Provides proof of consent for audit trail

**Source**: Extracted from API Gateway request context

**Optional**: System functions without IP address if not available

**Privacy Note**: IP addresses are personal data under GDPR and subject to same protections

---

## Routes and Navigation

### New Routes

Added to `frontend/src/router/index.js`:

```javascript
{
  path: '/privacy-policy',
  name: 'PrivacyPolicy',
  component: () => import('@/views/legal/PrivacyPolicy.vue'),
  meta: { requiresAuth: false }
},
{
  path: '/terms-conditions',
  name: 'TermsConditions',
  component: () => import('@/views/legal/TermsConditions.vue'),
  meta: { requiresAuth: false }
}
```

**Access Level**: Public (no authentication required)

### Footer Component

**Location**: `frontend/src/components/layout/Footer.vue`

**Purpose**: Provides consistent access to legal pages from all pages

**Links**:
- Privacy Policy → `/privacy-policy`
- Terms & Conditions → `/terms-conditions`
- Cookie Preferences → Opens modal
- Copyright notice

**Placement**: Added to `frontend/src/App.vue` at bottom of all pages

### Cookie Banner Placement

**Location**: Added to `frontend/src/App.vue`

**Behavior**: Appears on all pages if user has not made a cookie choice

---

## Internationalization

### Translation Files

**English**: `frontend/src/locales/en.json`

**French**: `frontend/src/locales/fr.json`

### New Translation Keys

```json
{
  "legal": {
    "privacyPolicy": "Privacy Policy",
    "termsConditions": "Terms & Conditions",
    "cookiePreferences": "Cookie Preferences",
    "lastUpdated": "Last updated",
    "acceptAll": "Accept All",
    "rejectAll": "Reject All",
    "customize": "Customize",
    "savePreferences": "Save Preferences",
    "essentialCookies": "Essential Cookies",
    "analyticsCookies": "Analytics Cookies",
    "marketingCookies": "Marketing Cookies",
    "essentialCookiesDesc": "Required for the website to function properly",
    "analyticsCookiesDesc": "Help us understand how visitors use our website",
    "marketingCookiesDesc": "Used to deliver personalized advertisements",
    "cookieBannerText": "We use cookies to improve your experience...",
    "learnMore": "Learn more"
  },
  "auth": {
    "register": {
      "privacyConsent": "I have read and accept the",
      "termsConsent": "I have read and accept the",
      "consentRequired": "You must accept the Privacy Policy and Terms & Conditions to register"
    }
  }
}
```

### Language Switching

- All legal components respect the current language setting
- Language can be changed using the LanguageSwitcher component
- Legal page content updates immediately when language changes

---

## Testing

### Unit Tests

**Frontend Tests**:

1. **PrivacyPolicy.vue** (`frontend/src/views/legal/PrivacyPolicy.test.js`)
   - Component renders in both languages
   - Last updated date displays correctly
   - Responsive layout works

2. **TermsConditions.vue** (`frontend/src/views/legal/TermsConditions.test.js`)
   - Component renders in both languages
   - Last updated date displays correctly
   - Responsive layout works

3. **CookieBanner.vue** (`frontend/src/components/legal/CookieBanner.test.js`)
   - Banner appears when no preference exists
   - Banner doesn't appear when preference exists
   - "Accept All" sets all preferences to true
   - "Reject All" sets non-essential to false
   - localStorage is updated correctly

4. **CookiePreferences.vue** (`frontend/src/components/legal/CookiePreferences.test.js`)
   - Modal opens and closes
   - Essential cookies cannot be disabled
   - Preferences are saved to localStorage
   - Preferences are loaded from localStorage

5. **RegisterForm.vue** (`frontend/src/components/RegisterForm.test.js`)
   - Consent checkboxes are required
   - Form submission blocked without consent
   - Consent data is included in request
   - Links to Privacy Policy and Terms open correctly

6. **Footer.vue** (`frontend/src/components/layout/Footer.test.js`)
   - Footer renders correctly
   - Links to legal pages work
   - Cookie preferences link opens modal

**Backend Tests**:

1. **register.py** (`tests/integration/test_auth_api.py`)
   - Registration fails without privacy_consent
   - Registration fails without terms_consent
   - Registration succeeds with both consents
   - Consent records are created in DynamoDB
   - IP address is captured (if available)

### Running Tests

**Frontend Tests**:
```bash
cd frontend
npm test
```

**Backend Tests**:
```bash
cd infrastructure
make test
```

### Manual Testing Checklist

- [ ] Privacy Policy displays correctly in French and English
- [ ] Terms & Conditions displays correctly in French and English
- [ ] Cookie banner appears on first visit
- [ ] Cookie banner doesn't appear on subsequent visits
- [ ] Cookie preferences can be customized
- [ ] Registration form shows consent checkboxes
- [ ] Registration fails without consent (frontend validation)
- [ ] Registration fails without consent (backend validation)
- [ ] Registration succeeds with consent
- [ ] Consent records are stored in DynamoDB
- [ ] Links to legal pages work from all locations
- [ ] Footer appears on all pages
- [ ] Mobile responsive design works
- [ ] Accessibility (keyboard navigation, screen readers)

---

## Legal Review Requirements

⚠️ **CRITICAL**: Before deploying to production, the following MUST be reviewed by qualified legal counsel familiar with EU data protection law and French law:

### Required Legal Reviews

1. **Privacy Policy Content**
   - Accuracy of data controller information
   - Completeness of data processing descriptions
   - Accuracy of legal basis claims
   - Appropriateness of retention periods
   - Completeness of data subject rights information
   - Accuracy of third-party disclosures

2. **Terms & Conditions Content**
   - Enforceability of terms
   - Compliance with French consumer protection law
   - Appropriateness of liability limitations
   - Validity of dispute resolution clauses
   - Compliance with distance selling regulations

3. **Consent Mechanism**
   - Validity of consent collection method
   - Clarity of consent language
   - Granularity of consent options
   - Ease of withdrawing consent

4. **Cookie Consent**
   - Compliance with ePrivacy Directive
   - Appropriateness of cookie categories
   - Clarity of cookie descriptions
   - Validity of consent mechanism

5. **Data Retention**
   - Appropriateness of retention periods
   - Compliance with legal requirements
   - Justification for retention periods

### Legal Counsel Checklist

- [ ] Privacy Policy reviewed and approved
- [ ] Terms & Conditions reviewed and approved
- [ ] Consent collection mechanism approved
- [ ] Cookie consent mechanism approved
- [ ] Data retention policy approved
- [ ] Data subject rights procedures approved
- [ ] Third-party data sharing agreements reviewed
- [ ] Data processing agreements in place (if applicable)
- [ ] Data Protection Impact Assessment (DPIA) completed (if required)
- [ ] Data Protection Officer (DPO) appointed (if required)

### Updating Legal Documents

**When to Update**:
- Changes to data collection practices
- Changes to data processing purposes
- Changes to third-party data sharing
- Changes to retention periods
- Changes to user rights procedures
- Legal or regulatory changes

**Update Process**:
1. Update content in translation files
2. Increment `consent_version` in code
3. Have legal counsel review changes
4. Deploy updated content
5. Notify existing users of changes (if material changes)
6. Obtain new consent if required by changes

**Version Tracking**:
- Current version: `1.0`
- Version stored in consent records
- Allows tracking which version user consented to
- Enables re-consent requests if needed

---

## Future Phases

### Phase 2: User Rights Implementation

**Status**: Not yet implemented

**Scope**: Enable data subjects to exercise their GDPR rights

**Features**:
- Data export functionality (Right to Access)
- Account deletion functionality (Right to Erasure)
- Privacy & Data settings page in user account
- Consent withdrawal mechanism
- Data portability (JSON export)

**Requirements**: See `.kiro/specs/gdpr-compliance/requirements.md` Requirements 4, 5, 10

### Phase 3: Operational Compliance

**Status**: Not yet implemented

**Scope**: Ongoing compliance and documentation

**Features**:
- Data retention policy enforcement
- Automated data deletion for expired records
- Data breach response procedures
- Security measures documentation
- Audit logging for data access
- Admin dashboard for consent management

**Requirements**: See `.kiro/specs/gdpr-compliance/requirements.md` Requirements 6, 7, 8

---

## Deployment

### Deployment Strategy

**Phase 1A: Legal Pages (Non-Breaking)**
- Deploy Privacy Policy and Terms pages
- Deploy Cookie Banner
- No impact on existing functionality
- Can be deployed immediately

**Phase 1B: Consent Enforcement (Breaking Change)**
- Deploy modified registration form
- Deploy backend consent validation
- **Blocks new registrations without consent**
- Deploy during low-traffic period
- Monitor for errors

### Deployment Commands

**Frontend**:
```bash
cd frontend
npm run build
# Deploy to S3/CloudFront via CDK
cd ../infrastructure
make deploy-frontend ENV=prod
```

**Backend**:
```bash
cd infrastructure
make deploy-api ENV=prod
```

### Rollback Plan

If issues occur after deployment:

1. **Frontend Rollback**:
   - Revert to previous CloudFront distribution
   - Or restore previous S3 version
   - No data cleanup needed

2. **Backend Rollback**:
   - Revert Lambda function to previous version using AWS Console
   - Or redeploy previous code version
   - No data cleanup needed (consent records are additive)

3. **Database**:
   - No cleanup needed
   - Consent records are immutable and additive
   - Old records do not cause issues

### Monitoring

**After Deployment, Monitor**:
- Registration success/failure rates
- Consent validation errors
- Cookie banner display issues
- Legal page load times
- Mobile responsiveness issues
- Browser compatibility issues

**CloudWatch Metrics**:
- Lambda function errors
- API Gateway 4xx/5xx errors
- DynamoDB throttling
- Frontend error logs

---

## Security Considerations

### Consent Integrity

- Consent records are immutable (never updated)
- Timestamp and version tracked for audit trail
- IP address captured for proof of consent
- Records stored securely in DynamoDB

### Data Protection

- No sensitive data in localStorage (only cookie preferences)
- Consent data encrypted at rest in DynamoDB
- HTTPS enforced for all communication
- Authentication required for consent record access

### Input Validation

- Backend validates consent is explicitly true (not just truthy)
- All user inputs sanitized
- Injection attack prevention
- CORS properly configured

---

## Support and Maintenance

### Updating Legal Content

**Location**: `frontend/src/locales/en.json` and `fr.json`

**Keys**: Under `legal.privacyPolicy` and `legal.termsConditions`

**Process**:
1. Update translation keys
2. Increment version number
3. Have legal counsel review
4. Deploy changes
5. Update last modified date

### Troubleshooting

**Cookie Banner Not Appearing**:
- Check browser localStorage for `cookie-consent` key
- Clear localStorage to reset
- Check browser console for errors

**Registration Failing with Consent Error**:
- Verify checkboxes are checked in frontend
- Check network tab for request payload
- Verify backend validation logic
- Check DynamoDB for consent records

**Legal Pages Not Loading**:
- Verify routes are configured correctly
- Check translation keys exist
- Verify component imports
- Check browser console for errors

### Contact

For questions about GDPR compliance implementation:
- Review this documentation
- Check `.kiro/specs/gdpr-compliance/` for detailed specs
- Consult with legal counsel for legal questions
- Contact development team for technical questions

---

## References

- [GDPR Official Text](https://gdpr-info.eu/)
- [ePrivacy Directive](https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32002L0058)
- [CNIL (French Data Protection Authority)](https://www.cnil.fr/)
- [Requirements Document](../../.kiro/specs/gdpr-compliance/requirements.md)
- [Design Document](../../.kiro/specs/gdpr-compliance/design.md)
- [Implementation Tasks](../../.kiro/specs/gdpr-compliance/tasks.md)

---

**Last Updated**: January 2, 2026

**Document Version**: 1.0

**Implementation Phase**: Phase 1 Complete
