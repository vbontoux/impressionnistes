# Implementation Plan: Self-Hosted Authentication

## Overview

This implementation plan converts the self-hosted authentication design into actionable coding tasks. The approach focuses on building the authentication infrastructure first, then implementing each authentication flow (login, forgot password, reset password), and finally integrating session management and accessibility features.

## Tasks

- [x] 1. Set up Cognito SDK integration and core services
  - Install AWS Amplify or AWS SDK for JavaScript
  - Create `frontend/src/services/cognitoService.js` with Cognito configuration
  - Implement `initializeCognito()`, `signIn()`, `signOut()`, `getCurrentUser()`, `getTokens()` methods
  - Configure Cognito with User Pool ID and Client ID from environment variables
  - _Requirements: 10.1, 10.2, 10.5_

- [-] 2. Create shared authentication utilities
  - [x] 2.1 Create password strength utility
    - Create `frontend/src/utils/passwordStrength.js`
    - Implement `calculatePasswordStrength(password)` function
    - Implement `isPasswordValid(password)` function
    - Validate: minimum 12 characters, uppercase, lowercase, number, special character
    - _Requirements: 4.2, 4.3, 4.6_
  
  - [x] 2.2 Write property test for password strength validation
    - **Property 10: Password Validation Rules**
    - **Validates: Requirements 4.2, 4.3, 4.6**
    - Test that all passwords meeting requirements are accepted
    - Test that passwords missing requirements are rejected with specific feedback
  
  - [x] 2.3 Create error mapper utility
    - Create `frontend/src/utils/authErrorMapper.js`
    - Implement `mapAuthError(error)` function
    - Map Cognito error codes to French user-friendly messages
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [x] 2.4 Write unit tests for error mapper
    - Test specific error code mappings (NotAuthorizedException, UserNotConfirmedException, etc.)
    - Test fallback for unknown errors
    - _Requirements: 5.1_

- [-] 3. Update authentication store with new actions
  - [x] 3.1 Modify `frontend/src/stores/authStore.js`
    - Add `sessionTimeoutReason` to state
    - Implement `login(email, password, rememberMe)` action using cognitoService
    - Implement `logout()` action with session cleanup
    - Implement `initializeAuth()` action with activity tracking
    - Implement `initializeActivityTracking()` for session timeout (5 hours max, 30 min inactivity)
    - Implement `forgotPassword(email)` action calling `/auth/forgot-password`
    - Implement `resetPassword(email, code, newPassword)` action calling `/auth/reset-password`
    - _Requirements: 1.2, 1.3, 1.6, 2.2, 3.3, 6.1, 6.2, 6.5, 6.7_
  
  - [x] 3.2 Write property test for token storage behavior
    - **Property 2: Token Storage Based on Remember Me**
    - **Validates: Requirements 1.3, 6.1, 6.2**
    - Test that remember me = false stores in sessionStorage
    - Test that remember me = true stores in localStorage
  
  - [x] 3.3 Write property test for session timeout
    - **Property 22: Session Timeout Management**
    - **Validates: Requirements 6.7, 6.8, 6.9**
    - Test that sessions expire after 5 hours
    - Test that sessions expire after 30 minutes of inactivity
    - Test that appropriate timeout reason is set

- [x] 4. Create PasswordStrengthIndicator component
  - Create `frontend/src/components/PasswordStrengthIndicator.vue`
  - Accept `strength` prop with score and feedback
  - Display strength bar with color coding (red/yellow/green)
  - Display strength label (Faible/Moyen/Fort)
  - Display feedback list for missing requirements
  - Use design system colors and spacing
  - _Requirements: 3.8, 4.1, 4.4, 4.5_

- [x] 5. Implement self-hosted login page
  - [x] 5.1 Modify `frontend/src/components/LoginForm.vue`
    - Remove Cognito Hosted UI redirect logic
    - Add email and password input fields using FormGroup
    - Add "Remember Me" checkbox
    - Add links to forgot password, register, and verify email pages
    - Implement `handleLogin()` using authStore.login()
    - Implement `checkSessionTimeout()` to display timeout messages
    - Display session timeout message if present (inactivity or max duration)
    - Display error messages inline using MessageAlert
    - Show loading state during authentication
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 6.8, 6.9_
  
  - [x] 5.2 Write property test for direct Cognito authentication
    - **Property 1: Direct Cognito SDK Authentication**
    - **Validates: Requirements 1.2, 1.7, 10.2, 10.3**
    - Test that login uses Cognito SDK (not Hosted UI redirect)
    - Test that no redirect to Hosted UI occurs
  
  - [x] 5.3 Write unit tests for login form
    - Test successful login flow
    - Test login with invalid credentials
    - Test session timeout message display
    - Test form validation
    - _Requirements: 1.1, 1.4_

- [x] 6. Implement forgot password page
  - [x] 6.1 Create `frontend/src/components/ForgotPasswordForm.vue`
    - Add email input field using FormGroup
    - Implement email format validation
    - Implement `handleSubmit()` using authStore.forgotPassword()
    - Display success message on successful request
    - Display error messages for failures (user not found, rate limiting)
    - Redirect to reset password page on success with email pre-filled
    - Add link back to login page
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  
  - [x] 6.2 Create `frontend/src/views/ForgotPasswordView.vue`
    - Wrap ForgotPasswordForm in consistent auth page layout
    - Use design system components
    - _Requirements: 7.1, 7.2_
  
  - [x] 6.3 Write property test for forgot password flow
    - **Property 5: Forgot Password API Call**
    - **Property 6: Forgot Password Success Flow**
    - **Validates: Requirements 2.2, 2.3**
    - Test that valid email triggers correct API call
    - Test that success displays message and redirects

- [x] 7. Implement reset password page
  - [x] 7.1 Create `frontend/src/components/ResetPasswordForm.vue`
    - Add email, verification code, new password, and confirm password fields
    - Pre-fill email if coming from forgot password page
    - Integrate PasswordStrengthIndicator component
    - Implement real-time password strength checking
    - Implement password confirmation matching validation
    - Implement `handleSubmit()` using authStore.resetPassword()
    - Display success message and redirect to login after 3 seconds
    - Display error messages for invalid code, weak password, etc.
    - Add link back to login page
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_
  
  - [x] 7.2 Create `frontend/src/views/ResetPasswordView.vue`
    - Wrap ResetPasswordForm in consistent auth page layout
    - Use design system components
    - _Requirements: 7.1, 7.2_
  
  - [x] 7.3 Write property test for password validation
    - **Property 10: Password Validation Rules**
    - **Property 11: Password Strength Indicator**
    - **Property 12: Password Confirmation Match**
    - **Validates: Requirements 3.6, 3.7, 4.2, 4.3**
    - Test that weak passwords are rejected
    - Test that strength indicator updates correctly
    - Test that mismatched passwords prevent submission
  
  - [x] 7.4 Write property test for reset password flow
    - **Property 8: Reset Password API Call**
    - **Property 9: Reset Password Success Flow**
    - **Validates: Requirements 3.3, 3.4**
    - Test that valid submission calls correct API
    - Test that success redirects after 3 seconds

- [x] 8. Update Vue Router configuration
  - Modify `frontend/src/router/index.js`
  - Add route for `/forgot-password` → ForgotPasswordView
  - Add route for `/reset-password` → ResetPasswordView
  - Update navigation guard to check auth state using authStore
  - Redirect to login with session timeout reason if token expired
  - Prevent authenticated users from accessing login/register pages
  - _Requirements: 6.4, 6.6_

- [ ] 9. Checkpoint - Test authentication flows
  - Ensure all tests pass
  - Manually test login flow (valid/invalid credentials)
  - Manually test forgot password flow
  - Manually test reset password flow
  - Manually test session timeout (inactivity and max duration)
  - Ask the user if questions arise

- [ ] 10. Implement accessibility features
  - [ ] 10.1 Add keyboard navigation support
    - Ensure all forms support Tab navigation
    - Ensure Enter submits forms
    - Ensure Escape dismisses messages
    - Test keyboard-only navigation on all auth pages
    - _Requirements: 7.3_
  
  - [ ] 10.2 Add ARIA labels and attributes
    - Add aria-label to all form inputs
    - Add aria-describedby for error messages
    - Add aria-live for dynamic messages
    - Add role attributes where appropriate
    - _Requirements: 7.4_
  
  - [ ] 10.3 Write property test for accessibility
    - **Property 15: Keyboard Navigation Support**
    - **Property 16: ARIA Labels Present**
    - **Validates: Requirements 7.3, 7.4**
    - Test that all interactive elements are keyboard accessible
    - Test that all form fields have ARIA labels

- [ ] 11. Implement loading states and success messages
  - [ ] 11.1 Add loading states to all forms
    - Disable submit buttons during API calls
    - Show loading spinner on buttons
    - Prevent multiple submissions
    - _Requirements: 7.6_
  
  - [ ] 11.2 Implement auto-dismiss for success messages
    - Add auto-dismiss after 5 seconds for success messages
    - Allow manual dismissal
    - _Requirements: 7.7_
  
  - [ ] 11.3 Write property tests for UI feedback
    - **Property 17: Loading State Display**
    - **Property 18: Success Message Auto-Dismiss**
    - **Validates: Requirements 7.6, 7.7**
    - Test that form submission shows loading state
    - Test that success messages dismiss after 5 seconds

- [ ] 12. Implement security measures
  - [ ] 12.1 Ensure no sensitive data in storage or URLs
    - Verify passwords are never stored in localStorage/sessionStorage
    - Verify no sensitive data in URL parameters
    - Verify tokens are stored securely
    - _Requirements: 9.2, 9.3, 9.4_
  
  - [ ] 12.2 Write property test for security
    - **Property 19: No Sensitive Data in Storage or URLs**
    - **Validates: Requirements 9.2, 9.3**
    - Test that passwords never appear in storage
    - Test that sensitive data never appears in URLs

- [ ] 13. Integration testing and polish
  - [ ] 13.1 Test complete authentication flows end-to-end
    - Test login → dashboard flow
    - Test forgot password → reset → login flow
    - Test session timeout → login flow
    - Test remember me persistence
    - _Requirements: 1.3, 1.6, 6.7_
  
  - [ ] 13.2 Verify integration with existing registration flow
    - Ensure registration still works
    - Ensure email verification still works
    - Ensure links between pages work correctly
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ] 13.3 Mobile responsiveness testing
    - Test all auth pages on mobile devices
    - Verify touch targets are at least 44px
    - Verify forms work on small screens
    - _Requirements: 7.2_

- [ ] 14. Final checkpoint - Complete testing
  - Run all unit tests and property tests
  - Perform manual accessibility testing
  - Test on multiple browsers (Chrome, Firefox, Safari)
  - Test on mobile and desktop
  - Verify no Cognito Hosted UI redirects occur
  - Ensure all error messages are user-friendly
  - Ask the user if questions arise

## Notes

- All tasks are required for complete implementation
- Tests are kept simple and focused on key behaviors
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties with simple test cases
- Unit tests validate specific examples and edge cases
- The implementation maintains the existing registration and verification flows without modification
- Session timeout uses simple messages (no countdown timer) as per user preference
