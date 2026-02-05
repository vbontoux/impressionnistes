/**
 * AuthStore Login Unit Tests
 * Feature: self-hosted-authentication
 * 
 * Unit tests for login functionality using Cognito SDK
 */
import { describe, test, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useAuthStore } from './authStore';
import * as cognitoService from '../services/cognitoService';

// Mock cognitoService
vi.mock('../services/cognitoService', () => ({
  signIn: vi.fn(),
  getCurrentUser: vi.fn(),
  storeTokens: vi.fn(),
  getStoredTokens: vi.fn(),
  clearTokens: vi.fn(),
  areTokensExpired: vi.fn(),
  signOut: vi.fn(),
  forgotPassword: vi.fn(),
  confirmForgotPassword: vi.fn(),
}));

// Mock authService
vi.mock('../services/authService', () => ({
  getUser: () => null,
  getToken: () => null,
  isAuthenticated: () => false,
  setUser: vi.fn(),
  setToken: vi.fn(),
  logout: vi.fn(),
  getProfile: vi.fn().mockResolvedValue({
    data: {
      user_id: 'test-user-id',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
    },
  }),
}));

// Mock sessionStorage
const sessionStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = value.toString(); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();

global.sessionStorage = sessionStorageMock;

describe('AuthStore Login - Unit Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  /**
   * Property 1: Direct Cognito SDK Authentication
   * Validates: Requirements 1.2, 1.7, 10.2, 10.3
   */
  test('Property 1: login() uses Cognito SDK directly', async () => {
    const authStore = useAuthStore();
    
    // Mock successful Cognito sign in
    cognitoService.signIn.mockResolvedValue({
      accessToken: 'test-access-token',
      idToken: 'test-id-token',
      refreshToken: 'test-refresh-token',
      expiresIn: 3600,
    });
    
    cognitoService.getCurrentUser.mockResolvedValue({
      email: 'test@example.com',
      given_name: 'Test',
      family_name: 'User',
      sub: 'test-user-id',
      groups: ['team_managers'],
    });
    
    // Call login
    const result = await authStore.login('test@example.com', 'TestPassword123!', false);
    
    // Property: login uses Cognito SDK (signIn called)
    expect(cognitoService.signIn).toHaveBeenCalledWith('test@example.com', 'TestPassword123!');
    expect(cognitoService.signIn).toHaveBeenCalledTimes(1);
    
    // Property: tokens are stored
    expect(cognitoService.storeTokens).toHaveBeenCalled();
    
    // Property: login succeeds
    expect(result).toBe(true);
    expect(authStore.isAuthenticated).toBe(true);
  });

  test('Property 1: login() does NOT redirect to Cognito Hosted UI', async () => {
    const authStore = useAuthStore();
    
    // Mock successful Cognito sign in
    cognitoService.signIn.mockResolvedValue({
      accessToken: 'test-access-token',
      idToken: 'test-id-token',
      refreshToken: 'test-refresh-token',
      expiresIn: 3600,
    });
    
    cognitoService.getCurrentUser.mockResolvedValue({
      email: 'test@example.com',
      given_name: 'Test',
      family_name: 'User',
      sub: 'test-user-id',
      groups: [],
    });
    
    // Spy on window.location
    const originalLocation = window.location;
    delete window.location;
    window.location = { href: '' };
    
    // Call login
    await authStore.login('test@example.com', 'TestPassword123!', false);
    
    // Property: No redirect to Cognito Hosted UI
    expect(window.location.href).not.toContain('cognito');
    expect(window.location.href).not.toContain('/login');
    
    // Restore window.location
    window.location = originalLocation;
  });

  test('login() stores tokens based on rememberMe flag', async () => {
    const authStore = useAuthStore();
    
    const mockTokens = {
      accessToken: 'test-access-token',
      idToken: 'test-id-token',
      refreshToken: 'test-refresh-token',
      expiresIn: 3600,
    };
    
    cognitoService.signIn.mockResolvedValue(mockTokens);
    cognitoService.getCurrentUser.mockResolvedValue({
      email: 'test@example.com',
      given_name: 'Test',
      family_name: 'User',
      sub: 'test-user-id',
      groups: [],
    });
    
    // Test with rememberMe = true
    await authStore.login('test@example.com', 'TestPassword123!', true);
    expect(cognitoService.storeTokens).toHaveBeenCalledWith(mockTokens, true);
    
    vi.clearAllMocks();
    cognitoService.signIn.mockResolvedValue(mockTokens);
    cognitoService.getCurrentUser.mockResolvedValue({
      email: 'test@example.com',
      given_name: 'Test',
      family_name: 'User',
      sub: 'test-user-id',
      groups: [],
    });
    
    // Test with rememberMe = false
    await authStore.login('test@example.com', 'TestPassword123!', false);
    expect(cognitoService.storeTokens).toHaveBeenCalledWith(mockTokens, false);
  });

  test('login() handles authentication errors', async () => {
    const authStore = useAuthStore();
    
    // Mock failed Cognito sign in
    cognitoService.signIn.mockRejectedValue({
      name: 'NotAuthorizedException',
      message: 'Incorrect username or password',
    });
    
    // Call login
    const result = await authStore.login('test@example.com', 'WrongPassword', false);
    
    // Property: login fails gracefully
    expect(result).toBe(false);
    expect(authStore.isAuthenticated).toBe(false);
    expect(authStore.error).toBeTruthy();
  });

  test('login() stores session tracking timestamps', async () => {
    const authStore = useAuthStore();
    
    cognitoService.signIn.mockResolvedValue({
      accessToken: 'test-access-token',
      idToken: 'test-id-token',
      refreshToken: 'test-refresh-token',
      expiresIn: 3600,
    });
    
    cognitoService.getCurrentUser.mockResolvedValue({
      email: 'test@example.com',
      given_name: 'Test',
      family_name: 'User',
      sub: 'test-user-id',
      groups: [],
    });
    
    await authStore.login('test@example.com', 'TestPassword123!', false);
    
    // Property: session timestamps are stored
    expect(sessionStorage.getItem('loginTime')).toBeTruthy();
    expect(sessionStorage.getItem('lastActivityTime')).toBeTruthy();
  });
});
