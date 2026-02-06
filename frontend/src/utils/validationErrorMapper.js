/**
 * Map backend validation errors to translated frontend messages
 * Backend returns errors in English, we need to translate them for the user
 */

/**
 * Map backend validation error to translation key
 * @param {string} field - Field name
 * @param {string} backendError - Error message from backend
 * @param {Function} t - i18n translate function
 * @returns {string} Translated error message
 */
export function mapValidationError(field, backendError, t) {
  if (!backendError) return '';
  
  const errorLower = backendError.toLowerCase();
  
  // Phone number errors
  if (field === 'mobile_number') {
    if (errorLower.includes('international format') || 
        errorLower.includes('e.164') ||
        errorLower.includes('phone number')) {
      return t('auth.validation.invalidPhoneFormat');
    }
  }
  
  // Email errors
  if (field === 'email') {
    if (errorLower.includes('email') || errorLower.includes('invalid')) {
      return t('auth.validation.invalidEmail');
    }
  }
  
  // Password errors
  if (field === 'password') {
    if (errorLower.includes('8 characters')) {
      return t('auth.validation.passwordTooShort');
    }
    if (errorLower.includes('uppercase')) {
      return t('auth.validation.passwordNeedsUppercase');
    }
    if (errorLower.includes('lowercase')) {
      return t('auth.validation.passwordNeedsLowercase');
    }
    if (errorLower.includes('number') || errorLower.includes('digit')) {
      return t('auth.validation.passwordNeedsNumber');
    }
    if (errorLower.includes('special') || errorLower.includes('symbol')) {
      return t('auth.validation.passwordNeedsSymbol');
    }
  }
  
  // First name / Last name errors
  if (field === 'first_name' || field === 'last_name') {
    if (errorLower.includes('required') || errorLower.includes('empty')) {
      return t('auth.validation.fieldRequired');
    }
    if (errorLower.includes('length')) {
      return t('auth.validation.fieldTooLong');
    }
  }
  
  // Club affiliation errors
  if (field === 'club_affiliation') {
    if (errorLower.includes('required') || errorLower.includes('empty')) {
      return t('auth.validation.fieldRequired');
    }
  }
  
  // Consent errors
  if (field === 'consent') {
    if (errorLower.includes('accept') || errorLower.includes('consent')) {
      return t('auth.register.consentRequired');
    }
  }
  
  // Generic errors
  if (errorLower.includes('required')) {
    return t('auth.validation.fieldRequired');
  }
  
  if (errorLower.includes('too long') || errorLower.includes('maxlength')) {
    return t('auth.validation.fieldTooLong');
  }
  
  if (errorLower.includes('too short') || errorLower.includes('minlength')) {
    return t('auth.validation.fieldTooShort');
  }
  
  // If no specific translation found, return the backend error
  // (better than nothing, but should be avoided)
  return backendError;
}

/**
 * Map all backend validation errors to translated messages
 * @param {Object} backendErrors - Errors object from backend
 * @param {Function} t - i18n translate function
 * @returns {Object} Translated errors object
 */
export function mapValidationErrors(backendErrors, t) {
  if (!backendErrors || typeof backendErrors !== 'object') {
    return {};
  }
  
  const translatedErrors = {};
  
  for (const [field, error] of Object.entries(backendErrors)) {
    translatedErrors[field] = mapValidationError(field, error, t);
  }
  
  return translatedErrors;
}
