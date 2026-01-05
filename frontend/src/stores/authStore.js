/**
 * Authentication Store (Pinia)
 * Manages authentication state and user session
 */
import { defineStore } from 'pinia';
import * as authService from '../services/authService';

export const useAuthStore = defineStore('auth', {
  state: () => {
    console.log('🏪 [authStore] Initializing state')
    console.log('🏪 [authStore] Timestamp:', Date.now())
    
    // Check if localStorage is available (not available in some test environments)
    const hasLocalStorage = typeof localStorage !== 'undefined' && typeof localStorage.getItem === 'function'
    
    console.log('🏪 [authStore] localStorage check:', {
      impersonatedTeamManagerId: hasLocalStorage ? localStorage.getItem('impersonatedTeamManagerId') : null,
      impersonatedTeamManager: hasLocalStorage ? localStorage.getItem('impersonatedTeamManager') : null
    })
    
    const impersonatedId = hasLocalStorage ? (localStorage.getItem('impersonatedTeamManagerId') || null) : null
    const impersonatedManager = hasLocalStorage ? JSON.parse(localStorage.getItem('impersonatedTeamManager') || 'null') : null
    
    console.log('🏪 [authStore] Parsed values:', {
      impersonatedId,
      impersonatedManager
    })
    
    return {
      user: authService.getUser(),
      token: authService.getToken(),
      isAuthenticated: authService.isAuthenticated(),
      loading: false,
      error: null,
      // Impersonation state - restore from localStorage
      impersonatedTeamManagerId: impersonatedId,
      impersonatedTeamManager: impersonatedManager,
    }
  },

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

    /**
     * Get the effective user ID for API requests
     * Returns impersonated ID if impersonating, otherwise admin's ID
     */
    effectiveUserId: (state) => {
      return state.impersonatedTeamManagerId || state.user?.user_id;
    },

    /**
     * Check if currently impersonating
     */
    isImpersonating: (state) => {
      return !!(state.user?.groups?.includes('admins') && state.impersonatedTeamManagerId);
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
        // Preserve groups from Cognito when updating profile from DynamoDB
        const groups = this.user?.groups || [];
        this.user = { ...response.data, groups };
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

    /**
     * Start impersonating a team manager
     */
    setImpersonation(teamManagerId, teamManagerInfo) {
      this.impersonatedTeamManagerId = teamManagerId;
      this.impersonatedTeamManager = teamManagerInfo;
      // Persist to localStorage so it survives page reloads (if available)
      if (typeof localStorage !== 'undefined' && typeof localStorage.setItem === 'function') {
        localStorage.setItem('impersonatedTeamManagerId', teamManagerId);
        localStorage.setItem('impersonatedTeamManager', JSON.stringify(teamManagerInfo));
      }
    },

    /**
     * Stop impersonating
     */
    clearImpersonation() {
      this.impersonatedTeamManagerId = null;
      this.impersonatedTeamManager = null;
      // Clear from localStorage (if available)
      if (typeof localStorage !== 'undefined' && typeof localStorage.removeItem === 'function') {
        localStorage.removeItem('impersonatedTeamManagerId');
        localStorage.removeItem('impersonatedTeamManager');
      }
    },
  },
});
