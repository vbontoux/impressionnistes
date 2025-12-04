/**
 * Authentication Store (Pinia)
 * Manages authentication state and user session
 */
import { defineStore } from 'pinia';
import * as authService from '../services/authService';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: authService.getUser(),
    token: authService.getToken(),
    isAuthenticated: authService.isAuthenticated(),
    loading: false,
    error: null,
  }),

  getters: {
    /**
     * Get current user
     */
    currentUser: (state) => state.user,

    /**
     * Check if user is admin
     */
    isAdmin: (state) => {
      return state.user?.groups?.includes('admins') || false;
    },

    /**
     * Check if user is team manager
     */
    isTeamManager: (state) => {
      return state.user?.groups?.includes('team_managers') || false;
    },

    /**
     * Check if user is devops
     */
    isDevOps: (state) => {
      return state.user?.groups?.includes('devops') || false;
    },

    /**
     * Get user's full name
     */
    fullName: (state) => {
      if (!state.user) return '';
      return `${state.user.first_name} ${state.user.last_name}`;
    },
  },

  actions: {
    /**
     * Register a new user
     */
    async register(userData) {
      this.loading = true;
      this.error = null;

      try {
        const response = await authService.register(userData);
        
        // Registration successful
        // Note: User needs to verify email before they can login
        return response;
      } catch (error) {
        this.error = error.response?.data?.error?.message || 'Registration failed';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Login user
     * Note: This should use AWS Cognito SDK
     */
    async login(email, password) {
      this.loading = true;
      this.error = null;

      try {
        // TODO: Implement Cognito authentication
        // This is a placeholder
        throw new Error('Login should be implemented using AWS Cognito SDK');
      } catch (error) {
        this.error = error.message || 'Login failed';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Set authentication from Cognito
     * Call this after successful Cognito authentication
     */
    async setAuthFromCognito(token, cognitoUser) {
      this.token = token;
      this.isAuthenticated = true;
      
      authService.setToken(token);

      // Fetch full profile from API
      try {
        const response = await authService.getProfile();
        // Merge profile data with Cognito groups
        this.user = {
          ...response.data,
          groups: cognitoUser.groups || [],
        };
        authService.setUser(this.user);
      } catch (error) {
        console.error('Failed to fetch user profile:', error);
        // Use Cognito user data as fallback
        this.user = {
          email: cognitoUser.email,
          first_name: cognitoUser.given_name,
          last_name: cognitoUser.family_name,
          user_id: cognitoUser.sub,
          groups: cognitoUser.groups || [],
        };
        authService.setUser(this.user);
      }
    },

    /**
     * Fetch current user profile
     */
    async fetchProfile() {
      if (!this.isAuthenticated) return;

      this.loading = true;
      this.error = null;

      try {
        const response = await authService.getProfile();
        this.user = response.data;
        authService.setUser(this.user);
        return this.user;
      } catch (error) {
        this.error = error.response?.data?.error?.message || 'Failed to fetch profile';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Update user profile
     */
    async updateProfile(profileData) {
      this.loading = true;
      this.error = null;

      try {
        const response = await authService.updateProfile(profileData);
        this.user = { ...this.user, ...response.data };
        authService.setUser(this.user);
        return this.user;
      } catch (error) {
        this.error = error.response?.data?.error?.message || 'Failed to update profile';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Request password reset
     */
    async forgotPassword(email) {
      this.loading = true;
      this.error = null;

      try {
        const response = await authService.forgotPassword(email);
        return response;
      } catch (error) {
        this.error = error.response?.data?.error?.message || 'Failed to request password reset';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Confirm password reset
     */
    async resetPassword(email, code, newPassword) {
      this.loading = true;
      this.error = null;

      try {
        const response = await authService.resetPassword(email, code, newPassword);
        return response;
      } catch (error) {
        this.error = error.response?.data?.error?.message || 'Failed to reset password';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Logout user
     */
    logout() {
      authService.logout();
      this.user = null;
      this.token = null;
      this.isAuthenticated = false;
      this.error = null;
    },

    /**
     * Clear error
     */
    clearError() {
      this.error = null;
    },
  },
});
