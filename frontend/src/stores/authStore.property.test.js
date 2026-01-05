/**
 * Auth Store Property-Based Tests
 * Feature: admin-impersonation
 * 
 * Property-based tests for impersonation functionality using fast-check
 */
import { describe, test, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useAuthStore } from './authStore';
import * as fc from 'fast-check';

// Mock authService
vi.mock('../services/authService', () => ({
  getUser: () => null,
  getToken: () => null,
  isAuthenticated: () => false,
  setUser: vi.fn(),
  setToken: vi.fn(),
  logout: vi.fn(),
}));

describe('Auth Store - Property-Based Tests', () => {
  beforeEach(() => {
    // Create a fresh pinia instance for each test
    setActivePinia(createPinia());
  });

  /**
   * Feature: admin-impersonation, Property 11: Effective user ID getter
   * Validates: Requirements 10.3
   * 
   * For any impersonation state (impersonating or not), the effectiveUserId getter
   * returns the impersonated ID when impersonating, or the admin's ID when not.
   */
  test('Property 11: effectiveUserId returns impersonated ID when impersonating, admin ID when not', () => {
    fc.assert(
      fc.property(
        fc.record({
          adminUserId: fc.string({ minLength: 1, maxLength: 50 }),
          teamManagerId: fc.option(fc.string({ minLength: 1, maxLength: 50 }), { nil: null }),
          isAdmin: fc.boolean(),
        }),
        ({ adminUserId, teamManagerId, isAdmin }) => {
          // Create a fresh pinia instance for each property iteration
          setActivePinia(createPinia());
          const store = useAuthStore();
          
          // Set up user
          store.user = {
            user_id: adminUserId,
            email: 'test@example.com',
            groups: isAdmin ? ['admins'] : ['team_managers']
          };

          // Set impersonation if teamManagerId is provided
          if (teamManagerId) {
            store.setImpersonation(teamManagerId, {
              user_id: teamManagerId,
              first_name: 'Test',
              last_name: 'User',
              email: 'tm@example.com',
              club_affiliation: 'Test Club'
            });
          }

          // Property: effectiveUserId should return impersonated ID if set, otherwise admin ID
          const expectedId = teamManagerId || adminUserId;
          expect(store.effectiveUserId).toBe(expectedId);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Feature: admin-impersonation, Property 12: Impersonation status getter
   * Validates: Requirements 10.4
   * 
   * For any impersonation state, the isImpersonating getter returns true when
   * impersonating and false when not.
   */
  test('Property 12: isImpersonating returns true only when admin is impersonating', () => {
    fc.assert(
      fc.property(
        fc.record({
          adminUserId: fc.string({ minLength: 1, maxLength: 50 }),
          teamManagerId: fc.option(fc.string({ minLength: 1, maxLength: 50 }), { nil: null }),
          isAdmin: fc.boolean(),
        }),
        ({ adminUserId, teamManagerId, isAdmin }) => {
          // Create a fresh pinia instance for each property iteration
          setActivePinia(createPinia());
          const store = useAuthStore();
          
          // Set up user
          store.user = {
            user_id: adminUserId,
            email: 'test@example.com',
            groups: isAdmin ? ['admins'] : ['team_managers']
          };

          // Set impersonation if teamManagerId is provided
          if (teamManagerId) {
            store.setImpersonation(teamManagerId, {
              user_id: teamManagerId,
              first_name: 'Test',
              last_name: 'User',
              email: 'tm@example.com',
              club_affiliation: 'Test Club'
            });
          }

          // Property: isImpersonating should be true only when admin AND teamManagerId is set
          const expectedImpersonating = isAdmin && !!teamManagerId;
          expect(store.isImpersonating).toBe(expectedImpersonating);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Additional property: State consistency after setImpersonation
   * 
   * For any valid team manager ID and info, after calling setImpersonation,
   * both state properties should be set correctly.
   */
  test('Property: setImpersonation maintains state consistency', () => {
    fc.assert(
      fc.property(
        fc.record({
          teamManagerId: fc.string({ minLength: 1, maxLength: 50 }),
          firstName: fc.string({ minLength: 1, maxLength: 50 }),
          lastName: fc.string({ minLength: 1, maxLength: 50 }),
          email: fc.emailAddress(),
          clubAffiliation: fc.string({ minLength: 1, maxLength: 100 }),
        }),
        ({ teamManagerId, firstName, lastName, email, clubAffiliation }) => {
          // Create a fresh pinia instance for each property iteration
          setActivePinia(createPinia());
          const store = useAuthStore();
          
          const teamManagerInfo = {
            user_id: teamManagerId,
            first_name: firstName,
            last_name: lastName,
            email: email,
            club_affiliation: clubAffiliation
          };

          store.setImpersonation(teamManagerId, teamManagerInfo);

          // Property: Both state properties should be set correctly
          expect(store.impersonatedTeamManagerId).toBe(teamManagerId);
          expect(store.impersonatedTeamManager).toEqual(teamManagerInfo);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Additional property: State consistency after clearImpersonation
   * 
   * For any impersonation state, after calling clearImpersonation,
   * both state properties should be null.
   */
  test('Property: clearImpersonation resets state completely', () => {
    fc.assert(
      fc.property(
        fc.record({
          teamManagerId: fc.string({ minLength: 1, maxLength: 50 }),
          firstName: fc.string({ minLength: 1, maxLength: 50 }),
          lastName: fc.string({ minLength: 1, maxLength: 50 }),
          email: fc.emailAddress(),
          clubAffiliation: fc.string({ minLength: 1, maxLength: 100 }),
        }),
        ({ teamManagerId, firstName, lastName, email, clubAffiliation }) => {
          // Create a fresh pinia instance for each property iteration
          setActivePinia(createPinia());
          const store = useAuthStore();
          
          const teamManagerInfo = {
            user_id: teamManagerId,
            first_name: firstName,
            last_name: lastName,
            email: email,
            club_affiliation: clubAffiliation
          };

          // Set impersonation first
          store.setImpersonation(teamManagerId, teamManagerInfo);
          
          // Clear impersonation
          store.clearImpersonation();

          // Property: Both state properties should be null
          expect(store.impersonatedTeamManagerId).toBeNull();
          expect(store.impersonatedTeamManager).toBeNull();
        }
      ),
      { numRuns: 100 }
    );
  });
});
