/**
 * Password Strength Property-Based Tests
 * Feature: self-hosted-authentication
 * 
 * Property-based tests for password validation rules
 */
import { describe, test, expect } from 'vitest';
import * as fc from 'fast-check';
import { calculatePasswordStrength, isPasswordValid } from './passwordStrength';

describe('Password Strength - Property-Based Tests', () => {
  /**
   * Property 10: Password Validation Rules
   * Validates: Requirements 4.2, 4.3, 4.6
   * 
   * For any password meeting all requirements (12+ chars, uppercase, lowercase,
   * number, special char), isPasswordValid returns true.
   * For any password missing requirements, isPasswordValid returns false with
   * specific feedback.
   */
  test('Property 10: Valid passwords meeting all requirements are accepted', () => {
    fc.assert(
      fc.property(
        fc.record({
          // Generate password components using array() instead of stringOf()
          prefix: fc.array(fc.constantFrom('x', 'y', 'z'), { minLength: 5, maxLength: 10 }),
          uppercase: fc.array(fc.constantFrom('A', 'B', 'C'), { minLength: 1, maxLength: 3 }),
          lowercase: fc.array(fc.constantFrom('a', 'b', 'c'), { minLength: 1, maxLength: 3 }),
          number: fc.array(fc.constantFrom('0', '1', '2'), { minLength: 1, maxLength: 3 }),
          special: fc.array(fc.constantFrom('!', '@', '#'), { minLength: 1, maxLength: 3 }),
        }),
        ({ prefix, uppercase, lowercase, number, special }) => {
          // Construct a password that meets all requirements
          const password = [...prefix, ...uppercase, ...lowercase, ...number, ...special].join('');
          
          // Only test if password is at least 12 characters
          if (password.length >= 12) {
            const isValid = isPasswordValid(password);
            const strength = calculatePasswordStrength(password);
            
            // Property: Password meeting all requirements should be valid
            expect(isValid).toBe(true);
            expect(strength.score).toBe(5);
            expect(strength.feedback).toHaveLength(0);
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  test('Property 10: Passwords under 12 characters are rejected', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 11 }),
        (password) => {
          const isValid = isPasswordValid(password);
          const strength = calculatePasswordStrength(password);
          
          // Property: Short passwords should be invalid
          expect(isValid).toBe(false);
          expect(strength.feedback.some(f => f.includes('12 caractères'))).toBe(true);
        }
      ),
      { numRuns: 50 }
    );
  });

  test('Property 10: Passwords without uppercase are rejected', () => {
    fc.assert(
      fc.property(
        fc.record({
          lowercase: fc.array(fc.constantFrom('a', 'b', 'c', 'd', 'e', 'f'), { minLength: 8, maxLength: 15 }),
          number: fc.array(fc.constantFrom('0', '1', '2', '3', '4', '5'), { minLength: 1, maxLength: 3 }),
          special: fc.array(fc.constantFrom('!', '@', '#', '$'), { minLength: 1, maxLength: 3 }),
        }),
        ({ lowercase, number, special }) => {
          // Password with no uppercase letters
          const password = [...lowercase, ...number, ...special].join('');
          
          if (password.length >= 12) {
            const isValid = isPasswordValid(password);
            const strength = calculatePasswordStrength(password);
            
            // Property: Password without uppercase should be invalid
            expect(isValid).toBe(false);
            expect(strength.feedback.some(f => f.includes('majuscule'))).toBe(true);
          }
        }
      ),
      { numRuns: 50 }
    );
  });

  test('Property 10: Passwords without lowercase are rejected', () => {
    fc.assert(
      fc.property(
        fc.record({
          uppercase: fc.array(fc.constantFrom('A', 'B', 'C', 'D', 'E', 'F'), { minLength: 8, maxLength: 15 }),
          number: fc.array(fc.constantFrom('0', '1', '2', '3', '4', '5'), { minLength: 1, maxLength: 3 }),
          special: fc.array(fc.constantFrom('!', '@', '#', '$'), { minLength: 1, maxLength: 3 }),
        }),
        ({ uppercase, number, special }) => {
          // Password with no lowercase letters
          const password = [...uppercase, ...number, ...special].join('');
          
          if (password.length >= 12) {
            const isValid = isPasswordValid(password);
            const strength = calculatePasswordStrength(password);
            
            // Property: Password without lowercase should be invalid
            expect(isValid).toBe(false);
            expect(strength.feedback.some(f => f.includes('minuscule'))).toBe(true);
          }
        }
      ),
      { numRuns: 50 }
    );
  });

  test('Property 10: Passwords without numbers are rejected', () => {
    fc.assert(
      fc.property(
        fc.record({
          uppercase: fc.array(fc.constantFrom('A', 'B', 'C', 'D', 'E', 'F'), { minLength: 4, maxLength: 8 }),
          lowercase: fc.array(fc.constantFrom('a', 'b', 'c', 'd', 'e', 'f'), { minLength: 4, maxLength: 8 }),
          special: fc.array(fc.constantFrom('!', '@', '#', '$'), { minLength: 1, maxLength: 3 }),
        }),
        ({ uppercase, lowercase, special }) => {
          // Password with no numbers
          const password = [...uppercase, ...lowercase, ...special].join('');
          
          if (password.length >= 12) {
            const isValid = isPasswordValid(password);
            const strength = calculatePasswordStrength(password);
            
            // Property: Password without numbers should be invalid
            expect(isValid).toBe(false);
            expect(strength.feedback.some(f => f.includes('chiffre'))).toBe(true);
          }
        }
      ),
      { numRuns: 50 }
    );
  });

  test('Property 10: Passwords without special characters are rejected', () => {
    fc.assert(
      fc.property(
        fc.record({
          uppercase: fc.array(fc.constantFrom('A', 'B', 'C', 'D', 'E', 'F'), { minLength: 4, maxLength: 8 }),
          lowercase: fc.array(fc.constantFrom('a', 'b', 'c', 'd', 'e', 'f'), { minLength: 4, maxLength: 8 }),
          number: fc.array(fc.constantFrom('0', '1', '2', '3', '4', '5'), { minLength: 1, maxLength: 3 }),
        }),
        ({ uppercase, lowercase, number }) => {
          // Password with no special characters
          const password = [...uppercase, ...lowercase, ...number].join('');
          
          if (password.length >= 12) {
            const isValid = isPasswordValid(password);
            const strength = calculatePasswordStrength(password);
            
            // Property: Password without special characters should be invalid
            expect(isValid).toBe(false);
            expect(strength.feedback.some(f => f.includes('caractère spécial'))).toBe(true);
          }
        }
      ),
      { numRuns: 50 }
    );
  });

  test('Property 10: Strength score increases with password complexity', () => {
    fc.assert(
      fc.property(
        fc.record({
          base: fc.array(fc.constantFrom('x', 'y', 'z'), { minLength: 8, maxLength: 15 }),
          uppercase: fc.array(fc.constantFrom('A', 'B', 'C'), { minLength: 1, maxLength: 3 }),
          lowercase: fc.array(fc.constantFrom('a', 'b', 'c'), { minLength: 1, maxLength: 3 }),
          number: fc.array(fc.constantFrom('0', '1', '2'), { minLength: 1, maxLength: 3 }),
          special: fc.array(fc.constantFrom('!', '@', '#'), { minLength: 1, maxLength: 3 }),
        }),
        ({ base, uppercase, lowercase, number, special }) => {
          // Weak password (short, missing requirements)
          const weakPassword = 'abc123';
          const weakResult = calculatePasswordStrength(weakPassword);
          
          // Strong password (long, all requirements)
          const strongPassword = [...base, ...uppercase, ...lowercase, ...number, ...special].join('');
          const strongResult = calculatePasswordStrength(strongPassword);
          
          // Property: Strong passwords should have higher or equal score
          if (strongPassword.length >= 12) {
            expect(strongResult.score).toBeGreaterThanOrEqual(weakResult.score);
          }
        }
      ),
      { numRuns: 50 }
    );
  });

  test('Property 10: Feedback is specific to missing requirements', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 30 }),
        (password) => {
          const strength = calculatePasswordStrength(password);
          
          // Property: Each missing requirement should have specific feedback
          if (password.length < 12) {
            expect(strength.feedback.some(f => f.includes('12 caractères'))).toBe(true);
          }
          
          if (!/[A-Z]/.test(password)) {
            expect(strength.feedback.some(f => f.includes('majuscule'))).toBe(true);
          }
          
          if (!/[a-z]/.test(password)) {
            expect(strength.feedback.some(f => f.includes('minuscule'))).toBe(true);
          }
          
          if (!/[0-9]/.test(password)) {
            expect(strength.feedback.some(f => f.includes('chiffre'))).toBe(true);
          }
          
          if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
            expect(strength.feedback.some(f => f.includes('caractère spécial'))).toBe(true);
          }
        }
      ),
      { numRuns: 100 }
    );
  });
});
