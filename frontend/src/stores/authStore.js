/**
 * Authentication Store (Pinia)
 * Manages authentication state and user session
 */
import { defineStore } from 'pinia';
import * as authService from '../services/authService';
import * as cognitoService from '../services/cognitoService';
import { mapAuthError } from '../utils/authErrorMapper';

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
      // Session timeout tracking
      sessionTimeoutReason: null,
      sessionCheckInterval: null,
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
     * Login user with email and password using Cognito SDK
     * @param {string} email
     * @param {string} password
     * @param {boolean} rememberMe
     */
    async login(email, password, rememberMe = false) {
      this.loading = true;
      this.error = null;

      try {
        // Authenticate with Cognito
        const tokens = await cognitoService.signIn(email, password);
        
        // Store tokens based on rememberMe preference
        cognitoService.storeTokens(tokens, rememberMe);
        
        // Store login time for session tracking
        sessionStorage.setItem('loginTime', Date.now().toString());
        sessionStorage.setItem('lastActivityTime', Date.now().toString());
        
        // Get user information (pass both accessToken and idToken)
        const cognitoUser = await cognitoService.getCurrentUser(tokens.accessToken, tokens.idToken);
        
        // Fetch full profile from API
        try {
          const response = await authService.getProfile();
          this.user = {
            ...response.data,
            groups: cognitoUser.groups || [],
          };
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
        }
        
        this.token = tokens.idToken;
        this.isAuthenticated = true;
        
        authService.setToken(tokens.idToken);
        authService.setUser(this.user);
        
        // Initialize activity tracking for session timeout
        this.initializeActivityTracking();
        
        return true;
      } catch (error) {
        console.error('Login error:', error);
        this.error = mapAuthError(error);
        return false;
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
     * Request password reset using Cognito
     * @param {string} email
     */
    async forgotPassword(email) {
      this.loading = true;
      this.error = null;

      try {
        await cognitoService.forgotPassword(email);
        return { success: true };
      } catch (error) {
        console.error('Forgot password error:', error);
        this.error = mapAuthError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Confirm password reset with verification code
     * @param {string} email
     * @param {string} code
     * @param {string} newPassword
     */
    async resetPassword(email, code, newPassword) {
      this.loading = true;
      this.error = null;

      try {
        await cognitoService.confirmForgotPassword(email, code, newPassword);
        return { success: true };
      } catch (error) {
        console.error('Reset password error:', error);
        this.error = mapAuthError(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Logout user
     */
    async logout() {
      // Sign out from Cognito
      const tokens = cognitoService.getStoredTokens();
      if (tokens && tokens.accessToken) {
        await cognitoService.signOut(tokens.accessToken);
      }
      
      // Clear all stored data
      authService.logout();
      cognitoService.clearTokens();
      
      this.user = null;
      this.token = null;
      this.isAuthenticated = false;
      this.error = null;
      
      // Clear session check interval
      if (this.sessionCheckInterval) {
        clearInterval(this.sessionCheckInterval);
        this.sessionCheckInterval = null;
      }
    },

    /**
     * Initialize auth state from stored tokens
     */
    async initializeAuth() {
      const tokens = cognitoService.getStoredTokens();
      
      if (tokens && !cognitoService.areTokensExpired(tokens)) {
        try {
          const cognitoUser = await cognitoService.getCurrentUser(tokens.accessToken, tokens.idToken);
          
          // Fetch full profile from API
          try {
            const response = await authService.getProfile();
            this.user = {
              ...response.data,
              groups: cognitoUser.groups || [],
            };
          } catch (error) {
            console.error('Failed to fetch user profile:', error);
            this.user = {
              email: cognitoUser.email,
              first_name: cognitoUser.given_name,
              last_name: cognitoUser.family_name,
              user_id: cognitoUser.sub,
              groups: cognitoUser.groups || [],
            };
          }
          
          this.token = tokens.idToken;
          this.isAuthenticated = true;
          
          authService.setToken(tokens.idToken);
          authService.setUser(this.user);
          
          // Initialize activity tracking
          this.initializeActivityTracking();
        } catch (error) {
          console.error('Token validation failed:', error);
          // Token expired or invalid, clear storage
          await this.logout();
        }
      }
    },

    /**
     * Initialize activity tracking for session timeout
     * - 5 hour maximum session duration
     * - 30 minute inactivity timeout
     */
    initializeActivityTracking() {
      const SESSION_MAX_DURATION = 5 * 60 * 60 * 1000; // 5 hours in ms
      const INACTIVITY_TIMEOUT = 30 * 60 * 1000; // 30 minutes in ms
      
      // Update last activity on user interaction
      const updateActivity = () => {
        sessionStorage.setItem('lastActivityTime', Date.now().toString());
      };
      
      // Track user activity
      const events = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'];
      events.forEach(event => {
        document.addEventListener(event, updateActivity, { passive: true });
      });
      
      // Check session validity periodically
      this.sessionCheckInterval = setInterval(() => {
        const now = Date.now();
        const storedLoginTime = parseInt(sessionStorage.getItem('loginTime') || '0');
        const storedLastActivity = parseInt(sessionStorage.getItem('lastActivityTime') || '0');
        
        // Check if session exceeded max duration
        if (now - storedLoginTime > SESSION_MAX_DURATION) {
          this.sessionTimeoutReason = 'max_duration';
          this.logout();
          return;
        }
        
        // Check if user has been inactive too long
        if (now - storedLastActivity > INACTIVITY_TIMEOUT) {
          this.sessionTimeoutReason = 'inactivity';
          this.logout();
          return;
        }
      }, 60000); // Check every minute
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
