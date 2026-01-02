# Implementation Plan: GDPR Compliance - Phase 1

## Overview

This implementation plan covers Phase 1 of GDPR compliance: Privacy Policy, Terms & Conditions, Cookie Consent Banner, and Consent Collection in Registration. Tasks are organized to enable incremental development with early validation.

## Tasks

- [x] 1. Add i18n translations for legal components
  - Add all legal-related translation keys to `frontend/src/locales/en.json`
  - Add all legal-related translation keys to `frontend/src/locales/fr.json`
  - Include translations for: Privacy Policy, Terms, Cookie Banner, Consent checkboxes
  - _Requirements: 2.2, 3.9, 9.2_

- [x] 2. Create Privacy Policy page
  - [x] 2.1 Create PrivacyPolicy.vue component
    - Create `frontend/src/views/legal/PrivacyPolicy.vue`
    - Implement bilingual content using vue-i18n
    - Include all GDPR Article 13 & 14 required information
    - Add responsive layout and print-friendly styles
    - Display last updated date
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12_

  - [x] 2.2 Write unit tests for PrivacyPolicy.vue
    - Test component renders in both languages
    - Test last updated date displays
    - Test responsive layout
    - _Requirements: 2.1, 2.2_

  - [x] 2.3 Add Privacy Policy route
    - Add `/privacy-policy` route to `frontend/src/router/index.js`
    - Configure route as public (no authentication required)
    - _Requirements: 2.1_

- [x] 3. Create Terms and Conditions page
  - [x] 3.1 Create TermsConditions.vue component
    - Create `frontend/src/views/legal/TermsConditions.vue`
    - Implement bilingual content using vue-i18n
    - Include all required legal terms
    - Add responsive layout and print-friendly styles
    - Display last updated date
    - _Requirements: 9.1, 9.2, 9.3, 9.6_

  - [x] 3.2 Write unit tests for TermsConditions.vue
    - Test component renders in both languages
    - Test last updated date displays
    - Test responsive layout
    - _Requirements: 9.1, 9.2_

  - [x] 3.3 Add Terms and Conditions route
    - Add `/terms-conditions` route to `frontend/src/router/index.js`
    - Configure route as public (no authentication required)
    - _Requirements: 9.1_

- [x] 4. Create Cookie Consent Banner
  - [x] 4.1 Create CookieBanner.vue component
    - Create `frontend/src/components/legal/CookieBanner.vue`
    - Implement sticky bottom banner with bilingual content
    - Add "Accept All", "Reject All", and "Customize" buttons
    - Check localStorage for existing consent on mount
    - Show banner only if no consent preference exists
    - Store consent preference in localStorage
    - Emit events for consent changes
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.9_

  - [x] 4.2 Write unit tests for CookieBanner.vue
    - Test banner appears when no preference exists
    - Test banner doesn't appear when preference exists
    - Test "Accept All" sets all preferences to true
    - Test "Reject All" sets non-essential to false
    - Test localStorage is updated correctly
    - _Requirements: 3.1, 3.6, 3.7_

- [x] 5. Create Cookie Preferences Modal
  - [x] 5.1 Create CookiePreferences.vue component
    - Create `frontend/src/components/legal/CookiePreferences.vue`
    - Implement modal dialog with cookie category toggles
    - Add descriptions for each cookie category (Essential, Analytics, Marketing)
    - Essential cookies always enabled (disabled toggle)
    - Save preferences to localStorage
    - Emit events for preference changes
    - _Requirements: 3.4, 3.5, 3.8_

  - [x] 5.2 Write unit tests for CookiePreferences.vue
    - Test modal opens and closes
    - Test essential cookies cannot be disabled
    - Test preferences are saved to localStorage
    - Test preferences are loaded from localStorage
    - _Requirements: 3.5, 3.8_

- [x] 6. Create or update Footer component
  - [x] 6.1 Create Footer.vue component
    - Create `frontend/src/components/layout/Footer.vue` (or update if exists)
    - Add links to Privacy Policy, Terms & Conditions
    - Add link to open Cookie Preferences modal
    - Add copyright notice
    - Implement bilingual content
    - Add responsive layout
    - _Requirements: 2.1, 9.1, 3.8_

  - [x] 6.2 Add Footer to App.vue
    - Import and add Footer component to `frontend/src/App.vue`
    - Position footer at bottom of all pages
    - _Requirements: 2.1, 9.1_

- [x] 7. Add Cookie Banner to App.vue
  - Import and add CookieBanner component to `frontend/src/App.vue`
  - Position banner to appear on all pages
  - Handle cookie preference events
  - _Requirements: 3.1_

- [x] 8. Checkpoint - Test legal pages and cookie consent
  - Verify Privacy Policy displays correctly in French and English
  - Verify Terms & Conditions displays correctly in French and English
  - Verify Cookie Banner appears on first visit
  - Verify Cookie Banner respects localStorage preferences
  - Verify Cookie Preferences modal works correctly
  - Verify Footer links work on all pages
  - Test responsive design on mobile devices

- [x] 9. Modify Registration Form for consent
  - [x] 9.1 Add consent checkboxes to RegisterForm.vue
    - Add consent checkbox group before submit button in `frontend/src/components/RegisterForm.vue`
    - Add checkbox for Privacy Policy consent with link
    - Add checkbox for Terms & Conditions consent with link
    - Add `privacy_consent` and `terms_consent` to form reactive data
    - Add `consent_version` field (default '1.0')
    - Make checkboxes required
    - _Requirements: 1.1, 1.2, 1.5_

  - [x] 9.2 Add consent validation to RegisterForm.vue
    - Validate both consent checkboxes are checked before submission
    - Display error message if consent not provided
    - Prevent form submission if consent not given
    - _Requirements: 1.4_

  - [x] 9.3 Update form submission to include consent data
    - Include `privacy_consent`, `terms_consent`, and `consent_version` in registration request
    - Handle consent-related errors from backend
    - _Requirements: 1.1, 1.7_

  - [x] 9.4 Write unit tests for RegisterForm consent
    - Test consent checkboxes are required
    - Test form submission blocked without consent
    - Test consent data is included in request
    - Test links to Privacy Policy and Terms open correctly
    - _Requirements: 1.1, 1.4_

- [x] 10. Modify backend registration to validate and store consent
  - [x] 10.1 Add consent validation to register.py
    - Modify `functions/auth/register.py` to validate consent fields
    - Check `privacy_consent` and `terms_consent` are boolean true
    - Return validation error if consent not provided
    - Extract `consent_version` from request
    - _Requirements: 1.1, 1.4_

  - [x] 10.2 Add consent storage to register.py
    - Store Privacy Policy consent record in DynamoDB
    - Store Terms & Conditions consent record in DynamoDB
    - Use SK pattern: `CONSENT#{type}#{timestamp}`
    - Capture IP address from request context
    - Include consent_version in records
    - _Requirements: 1.3, 1.7_

  - [x] 10.3 Write integration tests for consent validation
    - Test registration fails without privacy_consent
    - Test registration fails without terms_consent
    - Test registration succeeds with both consents
    - Test consent records are created in DynamoDB
    - Test IP address is captured
    - _Requirements: 1.1, 1.4, 1.7_

- [x] 11. Checkpoint - Test complete registration flow
  - Test registration form shows consent checkboxes
  - Test registration fails without consent (frontend validation)
  - Test registration fails without consent (backend validation)
  - Test registration succeeds with consent
  - Verify consent records exist in DynamoDB
  - Test error messages display correctly
  - Test in both French and English

- [x] 12. Update deployment configuration
  - [x] 12.1 Update frontend build configuration
    - Ensure all new components are included in build
    - Verify translation files are bundled
    - Test production build locally
    - _Requirements: All_

  - [x] 12.2 Deploy to dev environment
    - Deploy frontend to dev S3/CloudFront
    - Deploy backend Lambda to dev
    - Test complete flow in dev environment
    - _Requirements: All_

  - [x] 12.3 Deploy to production
    - Deploy frontend to production S3/CloudFront
    - Deploy backend Lambda to production
    - Monitor for errors
    - Test complete flow in production
    - _Requirements: All_

- [-] 13. Final validation and documentation
  - [x] 13.1 Complete manual testing checklist
    - Test all legal pages in both languages
    - Test cookie consent flow
    - Test registration consent flow
    - Test mobile responsiveness
    - Test accessibility (keyboard navigation, screen readers)
    - _Requirements: All_

  - [x] 13.2 Update project documentation
    - Document new legal pages and routes
    - Document consent storage schema
    - Document cookie consent mechanism
    - Add notes about legal review requirements
    - _Requirements: All_

## Notes

- All tasks are required for comprehensive GDPR compliance
- Legal content (Privacy Policy and Terms) should be reviewed by a qualified attorney
- Consent version '1.0' should be updated if legal documents change
- Cookie consent currently only tracks preferences (no actual analytics/marketing cookies implemented)
- IP address capture is optional but recommended for audit trail
- All components must be fully bilingual (French and English)
- Test thoroughly in dev before deploying to production

## Deployment Strategy

**Phase 1A: Legal Pages (Non-Breaking)**
- Tasks 1-8: Deploy legal pages and cookie banner
- No impact on existing functionality
- Can be deployed immediately

**Phase 1B: Consent Enforcement (Breaking Change)**
- Tasks 9-11: Deploy consent requirements
- Blocks new registrations without consent
- Deploy during low-traffic period
- Monitor for errors

## Rollback Plan

If issues occur after deployment:
1. **Frontend:** Revert to previous CloudFront distribution or S3 version
2. **Backend:** Revert Lambda function to previous version using AWS Console
3. **Database:** No cleanup needed (consent records are additive)

## Legal Review Required

⚠️ **IMPORTANT:** Before deploying to production, have the following reviewed by legal counsel:
- Privacy Policy content
- Terms & Conditions content
- Consent language and flow
- Data retention periods
- Cookie descriptions
