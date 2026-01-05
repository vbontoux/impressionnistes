/**
 * Auth Store Impersonation Tests
 * Unit tests for impersonation functionality
 */
import { describe, test, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useAuthStore } from './authStore';

// Mock authService
vi.mock('../services/authService', () => ({
  getUser: () => null,
  getToken: () => null,
  isAuthenticated: () => false,
  setUser: vi.fn(),
  setToken: vi.fn(),
  logout: vi.fn(),
}));

describe('Auth Store - Impersonation', () => {
  beforeEach(() => {
    // Create a fresh pinia instance for each test
    setActivePinia(createPinia());
  });

  describe('setImpersonation()', () => {
    test('should update impersonatedTeamManagerId correctly', () => {
      const store = useAuthStore();
      const teamManagerId = 'tm-123';
      const teamManagerInfo = {
        user_id: 'tm-123',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        club_affiliation: 'Test Club'
      };

      store.setImpersonation(teamManagerId, teamManagerInfo);

      expect(store.impersonatedTeamManagerId).toBe(teamManagerId);
    });

    test('should update impersonatedTeamManager correctly', () => {
      const store = useAuthStore();
      const teamManagerId = 'tm-123';
      const teamManagerInfo = {
        user_id: 'tm-123',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        club_affiliation: 'Test Club'
      };

      store.setImpersonation(teamManagerId, teamManagerInfo);

      expect(store.impersonatedTeamManager).toEqual(teamManagerInfo);
    });

    test('should update both state properties together', () => {
      const store = useAuthStore();
      const teamManagerId = 'tm-456';
      const teamManagerInfo = {
        user_id: 'tm-456',
        first_name: 'Jane',
        last_name: 'Smith',
        email: 'jane@example.com',
        club_affiliation: 'Another Club'
      };

      store.setImpersonation(teamManagerId, teamManagerInfo);

      expect(store.impersonatedTeamManagerId).toBe(teamManagerId);
      expect(store.impersonatedTeamManager).toEqual(teamManagerInfo);
    });
  });

  describe('clearImpersonation()', () => {
    test('should clear impersonatedTeamManagerId', () => {
      const store = useAuthStore();
      const teamManagerId = 'tm-123';
      const teamManagerInfo = {
        user_id: 'tm-123',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        club_affiliation: 'Test Club'
      };

      // Set impersonation first
      store.setImpersonation(teamManagerId, teamManagerInfo);
      expect(store.impersonatedTeamManagerId).toBe(teamManagerId);

      // Clear impersonation
      store.clearImpersonation();

      expect(store.impersonatedTeamManagerId).toBeNull();
    });

    test('should clear impersonatedTeamManager', () => {
      const store = useAuthStore();
      const teamManagerId = 'tm-123';
      const teamManagerInfo = {
        user_id: 'tm-123',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        club_affiliation: 'Test Club'
      };

      // Set impersonation first
      store.setImpersonation(teamManagerId, teamManagerInfo);
      expect(store.impersonatedTeamManager).toEqual(teamManagerInfo);

      // Clear impersonation
      store.clearImpersonation();

      expect(store.impersonatedTeamManager).toBeNull();
    });

    test('should clear both state properties together', () => {
      const store = useAuthStore();
      const teamManagerId = 'tm-123';
      const teamManagerInfo = {
        user_id: 'tm-123',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        club_affiliation: 'Test Club'
      };

      // Set impersonation first
      store.setImpersonation(teamManagerId, teamManagerInfo);

      // Clear impersonation
      store.clearImpersonation();

      expect(store.impersonatedTeamManagerId).toBeNull();
      expect(store.impersonatedTeamManager).toBeNull();
    });
  });

  describe('effectiveUserId getter', () => {
    test('should return impersonated ID when impersonating', () => {
      const store = useAuthStore();
      // Set up admin user
      store.user = {
        user_id: 'admin-123',
        email: 'admin@example.com',
        groups: ['admins']
      };

      const teamManagerId = 'tm-123';
      const teamManagerInfo = {
        user_id: 'tm-123',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        club_affiliation: 'Test Club'
      };

      store.setImpersonation(teamManagerId, teamManagerInfo);

      expect(store.effectiveUserId).toBe(teamManagerId);
    });

    test('should return admin ID when not impersonating', () => {
      const store = useAuthStore();
      // Set up admin user
      store.user = {
        user_id: 'admin-123',
        email: 'admin@example.com',
        groups: ['admins']
      };

      expect(store.effectiveUserId).toBe('admin-123');
    });

    test('should return undefined when no user is logged in', () => {
      const store = useAuthStore();
      store.user = null;

      expect(store.effectiveUserId).toBeUndefined();
    });
  });

  describe('isImpersonating getter', () => {
    test('should return true when admin is impersonating', () => {
      const store = useAuthStore();
      // Set up admin user
      store.user = {
        user_id: 'admin-123',
        email: 'admin@example.com',
        groups: ['admins']
      };

      const teamManagerId = 'tm-123';
      const teamManagerInfo = {
        user_id: 'tm-123',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        club_affiliation: 'Test Club'
      };

      store.setImpersonation(teamManagerId, teamManagerInfo);

      expect(store.isImpersonating).toBe(true);
    });

    test('should return false when admin is not impersonating', () => {
      const store = useAuthStore();
      // Set up admin user
      store.user = {
        user_id: 'admin-123',
        email: 'admin@example.com',
        groups: ['admins']
      };

      expect(store.isImpersonating).toBe(false);
    });

    test('should return false when non-admin has impersonation state', () => {
      const store = useAuthStore();
      // Set up non-admin user
      store.user = {
        user_id: 'user-123',
        email: 'user@example.com',
        groups: ['team_managers']
      };

      // Try to set impersonation (shouldn't work for non-admin)
      store.impersonatedTeamManagerId = 'tm-123';

      expect(store.isImpersonating).toBe(false);
    });

    test('should return false when no user is logged in', () => {
      const store = useAuthStore();
      store.user = null;
      store.impersonatedTeamManagerId = 'tm-123';

      expect(store.isImpersonating).toBe(false);
    });
  });
});
