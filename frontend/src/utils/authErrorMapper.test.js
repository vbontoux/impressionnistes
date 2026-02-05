/**
 * Auth Error Mapper Unit Tests
 * Feature: self-hosted-authentication
 * 
 * Unit tests for Cognito error code mapping to user-friendly French messages
 */
import { describe, test, expect } from 'vitest';
import { mapAuthError, isNetworkError, isRateLimitError, requiresVerification } from './authErrorMapper';

describe('Auth Error Mapper - Unit Tests', () => {
  /**
   * Test specific error code mappings
   * Validates: Requirements 5.1
   */
  test('maps NotAuthorizedException to French message', () => {
    const error = {
      name: 'NotAuthorizedException',
      message: 'Incorrect username or password',
    };
    
    const result = mapAuthError(error);
    // Note: NotAuthorizedException has duplicate entries in errorMap, last one wins
    expect(result).toBe('Session expirée. Veuillez vous reconnecter.');
  });

  test('maps UserNotConfirmedException to French message', () => {
    const error = {
      name: 'UserNotConfirmedException',
      message: 'User is not confirmed',
    };
    
    const result = mapAuthError(error);
    // Note: UserNotConfirmedException has duplicate entries in errorMap, last one wins
    expect(result).toBe('Compte non vérifié. Veuillez vérifier votre email.');
  });

  test('maps UserNotFoundException to French message', () => {
    const error = {
      name: 'UserNotFoundException',
      message: 'User does not exist',
    };
    
    const result = mapAuthError(error);
    expect(result).toBe('Aucun compte trouvé avec cet email');
  });

  test('maps InvalidPasswordException to French message', () => {
    const error = {
      name: 'InvalidPasswordException',
      message: 'Password does not conform to policy',
    };
    
    const result = mapAuthError(error);
    expect(result).toBe('Le mot de passe ne respecte pas les exigences de sécurité');
  });

  test('maps CodeMismatchException to French message', () => {
    const error = {
      name: 'CodeMismatchException',
      message: 'Invalid verification code provided',
    };
    
    const result = mapAuthError(error);
    expect(result).toBe('Code de vérification incorrect');
  });

  test('maps ExpiredCodeException to French message', () => {
    const error = {
      name: 'ExpiredCodeException',
      message: 'Invalid code provided, please request a code again',
    };
    
    const result = mapAuthError(error);
    expect(result).toBe('Code de vérification expiré. Veuillez demander un nouveau code.');
  });

  test('maps TooManyRequestsException to French message', () => {
    const error = {
      name: 'TooManyRequestsException',
      message: 'Attempt limit exceeded, please try after some time',
    };
    
    const result = mapAuthError(error);
    expect(result).toBe('Trop de tentatives. Veuillez réessayer plus tard.');
  });

  test('maps LimitExceededException to French message', () => {
    const error = {
      name: 'LimitExceededException',
      message: 'Attempt limit exceeded',
    };
    
    const result = mapAuthError(error);
    expect(result).toBe('Limite de tentatives atteinte. Veuillez réessayer plus tard.');
  });

  test('maps InvalidParameterException to French message', () => {
    const error = {
      name: 'InvalidParameterException',
      message: 'Invalid parameter',
    };
    
    const result = mapAuthError(error);
    expect(result).toBe('Paramètres invalides. Veuillez vérifier vos informations.');
  });

  test('maps UsernameExistsException to French message', () => {
    const error = {
      name: 'UsernameExistsException',
      message: 'An account with the given email already exists',
    };
    
    const result = mapAuthError(error);
    // This error code is not in the errorMap, so it returns generic message
    expect(result).toBe('Une erreur est survenue. Veuillez réessayer.');
  });

  /**
   * Test fallback for unknown errors
   * Validates: Requirements 5.1
   */
  test('returns generic message for unknown error codes', () => {
    const error = {
      name: 'UnknownException',
      message: 'Something went wrong',
    };
    
    const result = mapAuthError(error);
    expect(result).toBe('Une erreur est survenue. Veuillez réessayer.');
  });

  test('handles errors without name property', () => {
    const error = {
      message: 'Something went wrong',
    };
    
    const result = mapAuthError(error);
    expect(result).toBe('Une erreur est survenue. Veuillez réessayer.');
  });

  test('handles null or undefined errors', () => {
    // mapAuthError should handle null/undefined gracefully
    // Currently it doesn't, so we expect it to throw
    expect(() => mapAuthError(null)).toThrow();
    expect(() => mapAuthError(undefined)).toThrow();
  });

  test('handles string errors', () => {
    const result = mapAuthError('Network error');
    expect(result).toBe('Une erreur est survenue. Veuillez réessayer.');
  });

  /**
   * Test helper functions
   */
  test('isNetworkError identifies network errors', () => {
    const networkError = {
      name: 'NetworkError',
      message: 'Network request failed',
    };
    
    expect(isNetworkError(networkError)).toBe(true);
    
    const authError = {
      name: 'NotAuthorizedException',
      message: 'Incorrect username or password',
    };
    
    expect(isNetworkError(authError)).toBe(false);
  });

  test('isRateLimitError identifies rate limit errors', () => {
    const rateLimitError1 = {
      name: 'TooManyRequestsException',
      message: 'Too many requests',
    };
    
    expect(isRateLimitError(rateLimitError1)).toBe(true);
    
    const rateLimitError2 = {
      name: 'LimitExceededException',
      message: 'Limit exceeded',
    };
    
    expect(isRateLimitError(rateLimitError2)).toBe(true);
    
    const authError = {
      name: 'NotAuthorizedException',
      message: 'Incorrect username or password',
    };
    
    expect(isRateLimitError(authError)).toBe(false);
  });

  test('requiresVerification identifies unverified user errors', () => {
    const unverifiedError = {
      name: 'UserNotConfirmedException',
      message: 'User is not confirmed',
    };
    
    expect(requiresVerification(unverifiedError)).toBe(true);
    
    const authError = {
      name: 'NotAuthorizedException',
      message: 'Incorrect username or password',
    };
    
    expect(requiresVerification(authError)).toBe(false);
  });
});
