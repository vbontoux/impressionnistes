/**
 * Password Strength Utility
 * Calculate password strength and provide feedback
 */

/**
 * Calculate password strength
 * @param {string} password - Password to evaluate
 * @returns {Object} - { score: 0-5, feedback: string[] }
 */
export function calculatePasswordStrength(password) {
  const feedback = [];
  let score = 0;

  // Check length (minimum 12 characters)
  if (password.length < 12) {
    feedback.push('Le mot de passe doit contenir au moins 12 caractères');
  } else {
    score++;
  }

  // Check uppercase
  if (!/[A-Z]/.test(password)) {
    feedback.push('Ajoutez au moins une lettre majuscule');
  } else {
    score++;
  }

  // Check lowercase
  if (!/[a-z]/.test(password)) {
    feedback.push('Ajoutez au moins une lettre minuscule');
  } else {
    score++;
  }

  // Check numbers
  if (!/[0-9]/.test(password)) {
    feedback.push('Ajoutez au moins un chiffre');
  } else {
    score++;
  }

  // Check special characters
  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    feedback.push('Ajoutez au moins un caractère spécial');
  } else {
    score++;
  }

  return { score, feedback };
}

/**
 * Validate password meets minimum requirements
 * @param {string} password - Password to validate
 * @returns {boolean}
 */
export function isPasswordValid(password) {
  const { score } = calculatePasswordStrength(password);
  return score >= 5 && password.length >= 12;
}

/**
 * Get password strength label
 * @param {number} score - Password strength score (0-5)
 * @returns {string} - Strength label in French
 */
export function getPasswordStrengthLabel(score) {
  if (score === 0) return 'Très faible';
  if (score === 1) return 'Faible';
  if (score === 2) return 'Faible';
  if (score === 3) return 'Moyen';
  if (score === 4) return 'Bon';
  return 'Fort';
}

/**
 * Get password strength color class
 * @param {number} score - Password strength score (0-5)
 * @returns {string} - CSS class name
 */
export function getPasswordStrengthClass(score) {
  if (score <= 2) return 'strength-weak';
  if (score <= 3) return 'strength-medium';
  return 'strength-strong';
}

export default {
  calculatePasswordStrength,
  isPasswordValid,
  getPasswordStrengthLabel,
  getPasswordStrengthClass,
};
