# Design Document: GDPR Compliance - Phase 1

## Overview

This design document covers Phase 1 of GDPR compliance implementation for the Impressionnistes registration system. Phase 1 focuses on the critical legal requirements that must be in place before processing personal data: Privacy Policy, Terms and Conditions, explicit consent collection, and cookie consent management.

The implementation will be bilingual (French and English) to serve the French rowing community while maintaining accessibility for international participants.

## Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Vue 3)                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  Privacy Policy  │  │ Terms & Conditions│               │
│  │      Page        │  │      Page         │               │
│  └──────────────────┘  └──────────────────┘               │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Cookie Consent Banner Component             │  │
│  │  (Appears on first visit, stores preference)         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Registration Form (Modified)                 │  │
│  │  - Consent checkbox (required)                        │  │
│  │  - Links to Privacy Policy & Terms                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ POST /auth/register
                              │ (includes consent data)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (AWS Lambda)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         register.py (Modified)                        │  │
│  │  - Validate consent is provided                       │  │
│  │  - Store consent record in DynamoDB                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Store consent
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    DynamoDB                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  USER#{user_id}#CONSENT#{timestamp}                         │
│  - consent_type: 'privacy_policy' | 'terms_conditions'      │
│  - consent_version: '1.0'                                    │
│  - consented_at: ISO timestamp                               │
│  - ip_address: (optional)                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Privacy Policy Page

**Location:** `frontend/src/views/legal/PrivacyPolicy.vue`

**Purpose:** Display comprehensive privacy policy in French and English

**Features:**
- Bilingual content using vue-i18n
- Responsive layout
- Accessible from footer and registration form
- Includes all GDPR Article 13 & 14 requirements
- Last updated date displayed
- Printable format

**Route:** `/privacy-policy`

**Content Structure:**
1. Data Controller Information
2. Types of Personal Data Collected
3. Purpose of Data Collection
4. Legal Basis for Processing
5. Data Recipients (third parties)
6. Data Retention Periods
7. Data Subject Rights
8. How to Exercise Rights
9. Security Measures
10. Contact Information
11. Last Updated Date

### 2. Terms and Conditions Page

**Location:** `frontend/src/views/legal/TermsConditions.vue`

**Purpose:** Display terms of service and legal agreement

**Features:**
- Bilingual content using vue-i18n
- Responsive layout
- Accessible from footer and registration form
- Last updated date displayed

**Route:** `/terms-conditions`

**Content Structure:**
1. Service Description
2. User Responsibilities
3. Registration Requirements
4. Payment Terms
5. Cancellation Policy
6. Liability Limitations
7. Intellectual Property
8. Dispute Resolution
9. Governing Law
10. Contact Information
11. Last Updated Date

### 3. Cookie Consent Banner

**Location:** `frontend/src/components/legal/CookieBanner.vue`

**Purpose:** Obtain user consent for non-essential cookies

**Features:**
- Appears on first visit (before any non-essential cookies)
- Sticky bottom banner
- Three action buttons: Accept All, Reject All, Customize
- Stores preference in localStorage
- Bilingual using vue-i18n
- Respects user choice across sessions
- Link to Privacy Policy

**Cookie Categories:**
- **Essential:** Authentication, session management (always enabled)
- **Analytics:** Usage tracking (optional, currently none)
- **Marketing:** Advertising (optional, currently none)

**Storage:**
```javascript
localStorage.setItem('cookie-consent', JSON.stringify({
  essential: true,  // Always true
  analytics: false,
  marketing: false,
  timestamp: '2025-01-02T10:00:00Z',
  version: '1.0'
}));
```

### 4. Cookie Preferences Modal

**Location:** `frontend/src/components/legal/CookiePreferences.vue`

**Purpose:** Allow users to customize cookie preferences

**Features:**
- Modal dialog with detailed cookie information
- Toggle switches for each category
- Explanation of each cookie type
- Save preferences button
- Accessible from Cookie Banner and footer

### 5. Modified Registration Form

**Location:** `frontend/src/components/RegisterForm.vue` (existing, modified)

**Changes:**
1. Add consent checkbox group before submit button
2. Add links to Privacy Policy and Terms
3. Validate consent is checked before submission
4. Send consent data to backend

**New Form Fields:**
```vue
<div class="consent-group">
  <div class="consent-item">
    <input
      id="privacyConsent"
      v-model="form.privacy_consent"
      type="checkbox"
      required
    />
    <label for="privacyConsent">
      {{ $t('auth.register.privacyConsent') }}
      <router-link to="/privacy-policy" target="_blank">
        {{ $t('legal.privacyPolicy') }}
      </router-link>
    </label>
  </div>
  
  <div class="consent-item">
    <input
      id="termsConsent"
      v-model="form.terms_consent"
      type="checkbox"
      required
    />
    <label for="termsConsent">
      {{ $t('auth.register.termsConsent') }}
      <router-link to="/terms-conditions" target="_blank">
        {{ $t('legal.termsConditions') }}
      </router-link>
    </label>
  </div>
</div>
```

**Form Data:**
```javascript
const form = reactive({
  // ... existing fields
  privacy_consent: false,
  terms_consent: false,
  consent_version: '1.0'
});
```

### 6. Modified Registration Lambda

**Location:** `functions/auth/register.py` (existing, modified)

**Changes:**
1. Validate consent fields are present and true
2. Store consent records in DynamoDB
3. Return error if consent not provided

**Consent Validation:**
```python
# Validate consent
privacy_consent = body.get('privacy_consent', False)
terms_consent = body.get('terms_consent', False)
consent_version = body.get('consent_version', '1.0')

if not privacy_consent or not terms_consent:
    return validation_error({
        'consent': 'You must accept the Privacy Policy and Terms & Conditions to register'
    })
```

**Consent Storage:**
```python
# Store consent records
timestamp = get_timestamp()
ip_address = event.get('requestContext', {}).get('identity', {}).get('sourceIp')

# Privacy Policy consent
privacy_consent_item = {
    'PK': f'USER#{user_sub}',
    'SK': f'CONSENT#PRIVACY#{timestamp}',
    'user_id': user_sub,
    'consent_type': 'privacy_policy',
    'consent_version': consent_version,
    'consented': True,
    'consented_at': timestamp,
    'ip_address': ip_address,
    'created_at': timestamp
}
db.put_item(privacy_consent_item)

# Terms & Conditions consent
terms_consent_item = {
    'PK': f'USER#{user_sub}',
    'SK': f'CONSENT#TERMS#{timestamp}',
    'user_id': user_sub,
    'consent_type': 'terms_conditions',
    'consent_version': consent_version,
    'consented': True,
    'consented_at': timestamp,
    'ip_address': ip_address,
    'created_at': timestamp
}
db.put_item(terms_consent_item)
```

### 7. Footer Component

**Location:** `frontend/src/components/layout/Footer.vue` (new or modify existing)

**Purpose:** Provide consistent access to legal pages

**Links:**
- Privacy Policy
- Terms & Conditions
- Cookie Preferences
- Contact

**Layout:**
```vue
<footer class="site-footer">
  <div class="footer-content">
    <div class="footer-links">
      <router-link to="/privacy-policy">{{ $t('legal.privacyPolicy') }}</router-link>
      <router-link to="/terms-conditions">{{ $t('legal.termsConditions') }}</router-link>
      <a href="#" @click.prevent="showCookiePreferences">{{ $t('legal.cookiePreferences') }}</a>
    </div>
    <div class="footer-copyright">
      © {{ currentYear }} Course des Impressionnistes
    </div>
  </div>
</footer>
```

## Data Models

### Consent Record (DynamoDB)

```
PK: USER#{user_id}
SK: CONSENT#{consent_type}#{timestamp}

Attributes:
- user_id: string (UUID from Cognito)
- consent_type: string ('privacy_policy' | 'terms_conditions')
- consent_version: string (e.g., '1.0')
- consented: boolean (true)
- consented_at: string (ISO 8601 timestamp)
- ip_address: string (optional, for audit trail)
- created_at: string (ISO 8601 timestamp)
```

**Query Pattern:**
- Get all consents for a user: `PK = USER#{user_id} AND begins_with(SK, 'CONSENT#')`
- Get specific consent type: `PK = USER#{user_id} AND begins_with(SK, 'CONSENT#PRIVACY#')`

### Cookie Consent (localStorage)

```javascript
{
  essential: true,      // Always true
  analytics: false,     // User preference
  marketing: false,     // User preference
  timestamp: string,    // ISO 8601
  version: string       // '1.0'
}
```

## Internationalization (i18n)

### Translation Keys

**Location:** `frontend/src/locales/en.json` and `frontend/src/locales/fr.json`

**New Keys:**

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
    "cookieBannerText": "We use cookies to improve your experience. Essential cookies are required for the site to work.",
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

**French translations** in `fr.json`:

```json
{
  "legal": {
    "privacyPolicy": "Politique de confidentialité",
    "termsConditions": "Conditions générales",
    "cookiePreferences": "Préférences des cookies",
    "lastUpdated": "Dernière mise à jour",
    "acceptAll": "Tout accepter",
    "rejectAll": "Tout refuser",
    "customize": "Personnaliser",
    "savePreferences": "Enregistrer les préférences",
    "essentialCookies": "Cookies essentiels",
    "analyticsCookies": "Cookies analytiques",
    "marketingCookies": "Cookies marketing",
    "essentialCookiesDesc": "Nécessaires au bon fonctionnement du site",
    "analyticsCookiesDesc": "Nous aident à comprendre comment les visiteurs utilisent notre site",
    "marketingCookiesDesc": "Utilisés pour diffuser des publicités personnalisées",
    "cookieBannerText": "Nous utilisons des cookies pour améliorer votre expérience. Les cookies essentiels sont requis pour le fonctionnement du site.",
    "learnMore": "En savoir plus"
  },
  "auth": {
    "register": {
      "privacyConsent": "J'ai lu et j'accepte la",
      "termsConsent": "J'ai lu et j'accepte les",
      "consentRequired": "Vous devez accepter la Politique de confidentialité et les Conditions générales pour vous inscrire"
    }
  }
}
```

## Error Handling

### Frontend Validation

1. **Registration Form:**
   - Consent checkboxes must be checked before submission
   - Display error message if unchecked
   - Prevent form submission

2. **Cookie Banner:**
   - Handle localStorage errors gracefully
   - Default to no consent if storage fails
   - Log errors to console

### Backend Validation

1. **Registration Lambda:**
   - Validate `privacy_consent` and `terms_consent` are boolean true
   - Return 400 Bad Request if missing or false
   - Include clear error message

**Error Response:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "You must accept the Privacy Policy and Terms & Conditions to register",
    "details": {
      "consent": "Consent is required"
    }
  }
}
```

## Testing Strategy

### Unit Tests

**Frontend:**
1. **CookieBanner.vue:**
   - Test banner appears on first visit
   - Test "Accept All" sets all preferences to true
   - Test "Reject All" sets non-essential to false
   - Test localStorage is updated correctly
   - Test banner doesn't appear if preference exists

2. **RegisterForm.vue:**
   - Test consent checkboxes are required
   - Test form submission blocked without consent
   - Test consent data is sent to backend
   - Test links to Privacy Policy and Terms open correctly

3. **PrivacyPolicy.vue & TermsConditions.vue:**
   - Test content renders in both languages
   - Test last updated date displays
   - Test responsive layout

**Backend:**
1. **register.py:**
   - Test registration fails without consent
   - Test consent records are created in DynamoDB
   - Test consent validation logic
   - Test IP address is captured (if available)

### Integration Tests

1. **End-to-End Registration Flow:**
   - User visits site → sees cookie banner
   - User accepts cookies → preference stored
   - User navigates to register → sees consent checkboxes
   - User checks consents → registration succeeds
   - Consent records exist in DynamoDB

2. **Cookie Preference Flow:**
   - User customizes cookies → preferences saved
   - User refreshes page → preferences respected
   - User changes preferences → updates saved

### Manual Testing Checklist

- [ ] Privacy Policy displays correctly in French and English
- [ ] Terms & Conditions displays correctly in French and English
- [ ] Cookie banner appears on first visit
- [ ] Cookie banner doesn't appear on subsequent visits
- [ ] Cookie preferences can be customized
- [ ] Registration form shows consent checkboxes
- [ ] Registration fails without consent
- [ ] Registration succeeds with consent
- [ ] Consent records are stored in DynamoDB
- [ ] Links to legal pages work from all locations
- [ ] Mobile responsive design works
- [ ] Accessibility (keyboard navigation, screen readers)

## Security Considerations

1. **Consent Integrity:**
   - Consent records are immutable (never updated, only new records created)
   - Timestamp and version tracked for audit trail
   - IP address captured for proof of consent

2. **Data Protection:**
   - No sensitive data in localStorage (only cookie preferences)
   - Consent data encrypted at rest in DynamoDB
   - HTTPS enforced for all communication

3. **Input Validation:**
   - Backend validates consent is explicitly true (not just truthy)
   - Sanitize all user inputs
   - Prevent injection attacks

## Deployment Considerations

### Frontend Deployment

1. **New Files:**
   - `frontend/src/views/legal/PrivacyPolicy.vue`
   - `frontend/src/views/legal/TermsConditions.vue`
   - `frontend/src/components/legal/CookieBanner.vue`
   - `frontend/src/components/legal/CookiePreferences.vue`
   - `frontend/src/components/layout/Footer.vue` (if new)

2. **Modified Files:**
   - `frontend/src/components/RegisterForm.vue`
   - `frontend/src/router/index.js` (add routes)
   - `frontend/src/locales/en.json` (add translations)
   - `frontend/src/locales/fr.json` (add translations)
   - `frontend/src/App.vue` (add Footer and CookieBanner)

3. **Build and Deploy:**
   ```bash
   cd frontend
   npm run build
   # Deploy to S3/CloudFront
   ```

### Backend Deployment

1. **Modified Files:**
   - `functions/auth/register.py`

2. **No Database Migration Required:**
   - Consent records use existing DynamoDB table
   - New SK pattern: `CONSENT#{type}#{timestamp}`

3. **Deploy:**
   ```bash
   cd infrastructure
   make deploy-dev  # or deploy-prod
   ```

### Rollout Strategy

**Phase 1A: Legal Pages (No Breaking Changes)**
1. Deploy Privacy Policy and Terms pages
2. Deploy Cookie Banner (informational only)
3. Test in dev environment
4. Deploy to production

**Phase 1B: Consent Enforcement (Breaking Change)**
1. Deploy modified registration form with consent checkboxes
2. Deploy modified backend with consent validation
3. Test complete flow in dev
4. Deploy to production during low-traffic period
5. Monitor for errors

**Rollback Plan:**
- Frontend: Revert to previous build
- Backend: Revert Lambda function to previous version
- No data cleanup needed (consent records are additive)

## Future Enhancements (Phase 2 & 3)

**Phase 2:**
- Data export API endpoint
- Account deletion functionality
- Privacy & Data settings page in user account

**Phase 3:**
- Automated data retention enforcement
- Data breach notification system
- Admin dashboard for consent management

## Legal Disclaimer

**IMPORTANT:** This design provides technical implementation for GDPR compliance. The actual Privacy Policy and Terms & Conditions content should be reviewed and approved by a qualified attorney familiar with EU data protection law and French law. The technical implementation alone does not guarantee legal compliance.

**Recommended Actions:**
1. Have Privacy Policy reviewed by legal counsel
2. Have Terms & Conditions reviewed by legal counsel
3. Ensure data retention periods align with legal requirements
4. Verify all personal data processing has a lawful basis
5. Consider appointing a Data Protection Officer (DPO) if required
