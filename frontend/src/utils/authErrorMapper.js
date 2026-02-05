/**
 * Authentication Error Mapper
 * Map Cognito error codes to user-friendly French messages
 */

/**
 * Map Cognito error to user-friendly message
 * @param {Error} error - Cognito error object
 * @returns {string} - User-friendly error message in French
 */
export function mapAuthError(error) {
  const errorCode = error.code || error.name || error.__type;

  const errorMap = {
    // Authentication errors
    'NotAuthorizedException': 'Email ou mot de passe incorrect',
    'UserNotConfirmedException': 'Votre compte n\'est pas vérifié. Veuillez vérifier votre email.',
    'UserNotFoundException': 'Aucun compte trouvé avec cet email',
    'InvalidParameterException': 'Paramètres invalides. Veuillez vérifier vos informations.',
    
    // Rate limiting errors
    'TooManyRequestsException': 'Trop de tentatives. Veuillez réessayer plus tard.',
    'LimitExceededException': 'Limite de tentatives atteinte. Veuillez réessayer plus tard.',
    'TooManyFailedAttemptsException': 'Trop de tentatives échouées. Veuillez réessayer plus tard.',
    
    // Password reset errors
    'CodeMismatchException': 'Code de vérification incorrect',
    'ExpiredCodeException': 'Code de vérification expiré. Veuillez demander un nouveau code.',
    'InvalidPasswordException': 'Le mot de passe ne respecte pas les exigences de sécurité',
    
    // Network and service errors
    'NetworkError': 'Erreur de connexion. Veuillez vérifier votre connexion internet.',
    'TimeoutError': 'La requête a expiré. Veuillez réessayer.',
    'ServiceUnavailableException': 'Service temporairement indisponible. Veuillez réessayer.',
    'InternalErrorException': 'Erreur interne. Veuillez réessayer.',
    
    // Token errors
    'NotAuthorizedException': 'Session expirée. Veuillez vous reconnecter.',
    'InvalidTokenException': 'Session invalide. Veuillez vous reconnecter.',
    
    // User state errors
    'UserNotConfirmedException': 'Compte non vérifié. Veuillez vérifier votre email.',
    'PasswordResetRequiredException': 'Réinitialisation du mot de passe requise.',
    'UserLambdaValidationException': 'Erreur de validation. Veuillez contacter le support.',
  };

  // Return mapped error or generic message
  return errorMap[errorCode] || 'Une erreur est survenue. Veuillez réessayer.';
}

/**
 * Check if error is a network error
 * @param {Error} error - Error object
 * @returns {boolean}
 */
export function isNetworkError(error) {
  return (
    error.name === 'NetworkError' ||
    error.message?.includes('network') ||
    error.message?.includes('fetch') ||
    !navigator.onLine
  );
}

/**
 * Check if error is a rate limiting error
 * @param {Error} error - Error object
 * @returns {boolean}
 */
export function isRateLimitError(error) {
  const errorCode = error.code || error.name;
  return (
    errorCode === 'TooManyRequestsException' ||
    errorCode === 'LimitExceededException' ||
    errorCode === 'TooManyFailedAttemptsException'
  );
}

/**
 * Check if error requires user verification
 * @param {Error} error - Error object
 * @returns {boolean}
 */
export function requiresVerification(error) {
  const errorCode = error.code || error.name;
  return errorCode === 'UserNotConfirmedException';
}

export default {
  mapAuthError,
  isNetworkError,
  isRateLimitError,
  requiresVerification,
};
