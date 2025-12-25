/**
 * Race Eligibility Tests
 * Verify gender category logic matches requirements
 */
import { describe, test, expect } from 'vitest';
import { analyzeCrewComposition } from './raceEligibility.js';

// Test helper to create crew member
function createCrewMember(gender, age) {
  const birthYear = new Date().getFullYear() - age;
  return {
    gender,
    date_of_birth: `${birthYear}-01-01`
  };
}

describe('Race Eligibility - Gender Category Logic', () => {
  describe('Women\'s crews', () => {
    test('should classify 100% women as women\'s crew', () => {
      const result = analyzeCrewComposition([
        createCrewMember('F', 25),
        createCrewMember('F', 26),
        createCrewMember('F', 27),
        createCrewMember('F', 28)
      ]);

      expect(result.genderCategory).toBe('women');
    });
  });

  describe('Men\'s crews', () => {
    test('should classify more than 50% men as men\'s crew', () => {
      const result = analyzeCrewComposition([
        createCrewMember('M', 25),
        createCrewMember('M', 26),
        createCrewMember('M', 27),
        createCrewMember('F', 28)
      ]);

      expect(result.genderCategory).toBe('men');
      expect(result.malePercentage).toBe(75);
      expect(result.femalePercentage).toBe(25);
    });

    test('should classify 100% men as men\'s crew', () => {
      const result = analyzeCrewComposition([
        createCrewMember('M', 25),
        createCrewMember('M', 26),
        createCrewMember('M', 27),
        createCrewMember('M', 28)
      ]);

      expect(result.genderCategory).toBe('men');
    });
  });

  describe('Mixed-gender crews', () => {
    test('should classify 50% women with at least 1 man as mixed', () => {
      const result = analyzeCrewComposition([
        createCrewMember('M', 25),
        createCrewMember('M', 26),
        createCrewMember('F', 27),
        createCrewMember('F', 28)
      ]);

      expect(result.genderCategory).toBe('mixed');
      expect(result.malePercentage).toBe(50);
      expect(result.femalePercentage).toBe(50);
    });

    test('should classify more than 50% women with at least 1 man as mixed', () => {
      const result = analyzeCrewComposition([
        createCrewMember('M', 25),
        createCrewMember('F', 26),
        createCrewMember('F', 27),
        createCrewMember('F', 28)
      ]);

      expect(result.genderCategory).toBe('mixed');
      expect(result.malePercentage).toBe(25);
      expect(result.femalePercentage).toBe(75);
    });
  });

  describe('Edge cases - 8+ boats', () => {
    test('should classify 8+ boat with more than 50% men as men\'s crew', () => {
      const result = analyzeCrewComposition([
        createCrewMember('M', 25),
        createCrewMember('M', 26),
        createCrewMember('M', 27),
        createCrewMember('M', 28),
        createCrewMember('M', 29),
        createCrewMember('F', 25),
        createCrewMember('F', 26),
        createCrewMember('F', 27),
        createCrewMember('F', 28)
      ]);

      expect(result.genderCategory).toBe('men');
      expect(result.malePercentage).toBe(56);
      expect(result.femalePercentage).toBe(44);
    });

    test('should classify 8+ boat with exactly 50% women and at least 1 man as mixed', () => {
      const result = analyzeCrewComposition([
        createCrewMember('M', 25),
        createCrewMember('M', 26),
        createCrewMember('M', 27),
        createCrewMember('M', 28),
        createCrewMember('F', 25),
        createCrewMember('F', 26),
        createCrewMember('F', 27),
        createCrewMember('F', 28)
      ]);

      expect(result.genderCategory).toBe('mixed');
      expect(result.malePercentage).toBe(50);
      expect(result.femalePercentage).toBe(50);
    });
  });
});
