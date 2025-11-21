/**
 * Authentication Service
 * Handles API calls for authentication and user management
 */
import apiClient, { getErrorMessage } from './apiClient';

/**
 * Register a new team manager
 * @param {Object} userData - User registration data
 * @returns {Promise} API response
 */
export async function register(userData) {
  const response = await apiClient.post('/auth/register', userData);
  return response.data;
}

/**
 * Login with email and password (via Cognito)
 * Note: This is a placeholder - actual login should use AWS Cognito SDK
 * @param {string} email
 * @param {string} password
 * @returns {Promise} Auth tokens
 */
export async function login(email, password) {
  // TODO: Implement Cognito authentication
  // For now, this is a placeholder that would call Cognito
  throw new Error('Login should be implemented using AWS Cognito SDK');
}

/**
 * Get current user profile
 * @returns {Promise} User profile data
 */
export async function getProfile() {
  const response = await apiClient.get('/auth/profile');
  return response.data;
}

/**
 * Update user profile
 * @param {Object} profileData - Profile fields to update
 * @returns {Promise} Updated profile data
 */
export async function updateProfile(profileData) {
  const response = await apiClient.put('/auth/profile', profileData);
  return response.data;
}

/**
 * Request password reset
 * @param {string} email
 * @returns {Promise} API response
 */
export async function forgotPassword(email) {
  const response = await apiClient.post('/auth/forgot-password', { email });
  return response.data;
}

/**
 * Confirm password reset with code
 * @param {string} email
 * @param {string} code - Verification code from email
 * @param {string} newPassword
 * @returns {Promise} API response
 */
export async function resetPassword(email, code, newPassword) {
  const response = await apiClient.post('/auth/reset-password', {
    email,
    code,
    new_password: newPassword,
  });
  return response.data;
}

/**
 * Logout user
 */
export function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('id_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user');
  // TODO: Call Cognito signOut
}

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
export function isAuthenticated() {
  return !!(localStorage.getItem('id_token') || localStorage.getItem('access_token') || localStorage.getItem('auth_token'));
}

/**
 * Get stored auth token
 * @returns {string|null}
 */
export function getToken() {
  return localStorage.getItem('id_token') || localStorage.getItem('access_token') || localStorage.getItem('auth_token');
}

/**
 * Store auth token
 * @param {string} token
 */
export function setToken(token) {
  localStorage.setItem('access_token', token);
}

/**
 * Get stored user data
 * @returns {Object|null}
 */
export function getUser() {
  const userJson = localStorage.getItem('user');
  return userJson ? JSON.parse(userJson) : null;
}

/**
 * Store user data
 * @param {Object} user
 */
export function setUser(user) {
  localStorage.setItem('user', JSON.stringify(user));
}

export default {
  register,
  login,
  getProfile,
  updateProfile,
  forgotPassword,
  resetPassword,
  logout,
  isAuthenticated,
  getToken,
  setToken,
  getUser,
  setUser,
};
