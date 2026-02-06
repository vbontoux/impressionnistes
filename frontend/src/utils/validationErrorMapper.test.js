/**
 * Tests for validation error mapper
 */
import { describe, it, expect } from 'vitest';
import { mapValidationError, mapValidationErrors } from './validationErrorMapper';

// Mock translation function
const mockT = (key) => {
  const translations = {
    'auth.validation.invalidPhoneFormat': 'Le numéro de téléphone doit être au format international',
    'auth.validation.invalidEmail': 'Format d\'email invalide',
    'auth.validation.passwordTooShort': 'Le mot de passe doit contenir au moins 8 caractères',
    'auth.validation.passwordNeedsUppercase': 'Le mot de passe doit contenir au moins une majuscule',
    'auth.validation.passwordNeedsLowercase': 'Le mot de passe doit contenir au moins une minuscule',
    'auth.validation.passwordNeedsNumber': 'Le mot de passe doit contenir au moins un chiffre',
    'auth.validation.passwordNeedsSymbol': 'Le mot de passe doit contenir au moins un caractère spécial',
    'auth.validation.fieldRequired': 'Ce champ est obligatoire',
    'auth.validation.fieldTooLong': 'Ce champ est trop long',
    'auth.validation.fieldTooShort': 'Ce champ est trop court',
    'auth.register.consentRequired': 'Vous devez accepter la Politique de confidentialité'
  };
  return translations[key] || key;
};

describe('validationErrorMapper', () => {
  describe('mapValidationError', () => {
    it('should map phone number errors', () => {
      const result = mapValidationError(
        'mobile_number',
        'Phone number must be in international format (e.g., +33612345678)',
        mockT
      );
      expect(result).toBe('Le numéro de téléphone doit être au format international');
    });

    it('should map email errors', () => {
      const result = mapValidationError(
        'email',
        'Invalid email format',
        mockT
      );
      expect(result).toBe('Format d\'email invalide');
    });

    it('should map password length errors', () => {
      const result = mapValidationError(
        'password',
        'Password must be at least 8 characters',
        mockT
      );
      expect(result).toBe('Le mot de passe doit contenir au moins 8 caractères');
    });

    it('should map password uppercase errors', () => {
      const result = mapValidationError(
        'password',
        'Password must contain uppercase',
        mockT
      );
      expect(result).toBe('Le mot de passe doit contenir au moins une majuscule');
    });

    it('should map required field errors', () => {
      const result = mapValidationError(
        'first_name',
        'Field is required',
        mockT
      );
      expect(result).toBe('Ce champ est obligatoire');
    });

    it('should map consent errors', () => {
      const result = mapValidationError(
        'consent',
        'You must accept the Privacy Policy',
        mockT
      );
      expect(result).toBe('Vous devez accepter la Politique de confidentialité');
    });

    it('should return original error if no mapping found', () => {
      const result = mapValidationError(
        'unknown_field',
        'Some unknown error',
        mockT
      );
      expect(result).toBe('Some unknown error');
    });
  });

  describe('mapValidationErrors', () => {
    it('should map multiple errors', () => {
      const backendErrors = {
        mobile_number: 'Phone number must be in international format',
        email: 'Invalid email format',
        password: 'Password must be at least 8 characters'
      };

      const result = mapValidationErrors(backendErrors, mockT);

      expect(result).toEqual({
        mobile_number: 'Le numéro de téléphone doit être au format international',
        email: 'Format d\'email invalide',
        password: 'Le mot de passe doit contenir au moins 8 caractères'
      });
    });

    it('should handle empty errors object', () => {
      const result = mapValidationErrors({}, mockT);
      expect(result).toEqual({});
    });

    it('should handle null errors', () => {
      const result = mapValidationErrors(null, mockT);
      expect(result).toEqual({});
    });

    it('should handle undefined errors', () => {
      const result = mapValidationErrors(undefined, mockT);
      expect(result).toEqual({});
    });
  });
});
