/**
 * Cognito Service
 * Handles AWS Cognito authentication operations using AWS SDK v3
 */
import {
  CognitoIdentityProviderClient,
  InitiateAuthCommand,
  GetUserCommand,
  GlobalSignOutCommand,
  ForgotPasswordCommand,
  ConfirmForgotPasswordCommand,
} from '@aws-sdk/client-cognito-identity-provider';

// Initialize Cognito client
const cognitoClient = new CognitoIdentityProviderClient({
  region: import.meta.env.VITE_AWS_REGION || 'eu-west-3',
});

// Get configuration from environment variables
const USER_POOL_ID = import.meta.env.VITE_USER_POOL_ID;
const CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID;

/**
 * Sign in user with email and password
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise<Object>} - Authentication result with tokens
 */
export async function signIn(email, password) {
  try {
    const command = new InitiateAuthCommand({
      AuthFlow: 'USER_PASSWORD_AUTH',
      ClientId: CLIENT_ID,
      AuthParameters: {
        USERNAME: email.toLowerCase().trim(),
        PASSWORD: password,
      },
    });

    const response = await cognitoClient.send(command);

    if (response.ChallengeName) {
      // Handle challenges (e.g., NEW_PASSWORD_REQUIRED, MFA)
      throw new Error(`Challenge required: ${response.ChallengeName}`);
    }

    return {
      accessToken: response.AuthenticationResult.AccessToken,
      idToken: response.AuthenticationResult.IdToken,
      refreshToken: response.AuthenticationResult.RefreshToken,
      expiresIn: response.AuthenticationResult.ExpiresIn,
    };
  } catch (error) {
    console.error('Sign in error:', error);
    throw error;
  }
}

/**
 * Get current authenticated user information
 * @param {string} accessToken - Access token from authentication
 * @param {string} idToken - ID token from authentication (contains groups)
 * @returns {Promise<Object>} - User attributes and groups
 */
export async function getCurrentUser(accessToken, idToken) {
  try {
    const command = new GetUserCommand({
      AccessToken: accessToken,
    });

    const response = await cognitoClient.send(command);

    // Convert attributes array to object
    const attributes = {};
    response.UserAttributes.forEach((attr) => {
      attributes[attr.Name] = attr.Value;
    });

    // Decode ID token to get groups (groups are in the ID token, not in GetUser response)
    let groups = [];
    if (idToken) {
      try {
        const payload = JSON.parse(atob(idToken.split('.')[1]));
        groups = payload['cognito:groups'] || [];
      } catch (error) {
        console.error('Error decoding ID token:', error);
      }
    }

    return {
      username: response.Username,
      attributes,
      email: attributes.email,
      email_verified: attributes.email_verified === 'true',
      sub: attributes.sub,
      given_name: attributes.given_name,
      family_name: attributes.family_name,
      groups: groups,
    };
  } catch (error) {
    console.error('Get current user error:', error);
    throw error;
  }
}

/**
 * Sign out current user globally (invalidates all tokens)
 * @param {string} accessToken - Access token from authentication
 * @returns {Promise<void>}
 */
export async function signOut(accessToken) {
  try {
    if (accessToken) {
      const command = new GlobalSignOutCommand({
        AccessToken: accessToken,
      });
      await cognitoClient.send(command);
    }
  } catch (error) {
    console.error('Sign out error:', error);
    // Don't throw - allow local cleanup even if global sign out fails
  }
}

/**
 * Get tokens from storage
 * @returns {Object|null} - Tokens object or null
 */
export function getStoredTokens() {
  const tokensFromLocal = localStorage.getItem('authTokens');
  const tokensFromSession = sessionStorage.getItem('authTokens');
  
  const tokensJson = tokensFromLocal || tokensFromSession;
  
  if (tokensJson) {
    try {
      return JSON.parse(tokensJson);
    } catch (error) {
      console.error('Error parsing stored tokens:', error);
      return null;
    }
  }
  
  return null;
}

/**
 * Store tokens in storage
 * @param {Object} tokens - Tokens object
 * @param {boolean} rememberMe - Whether to use localStorage (true) or sessionStorage (false)
 */
export function storeTokens(tokens, rememberMe = false) {
  const tokensJson = JSON.stringify(tokens);
  
  if (rememberMe) {
    localStorage.setItem('authTokens', tokensJson);
    sessionStorage.removeItem('authTokens');
  } else {
    sessionStorage.setItem('authTokens', tokensJson);
    localStorage.removeItem('authTokens');
  }
}

/**
 * Clear tokens from storage
 */
export function clearTokens() {
  localStorage.removeItem('authTokens');
  sessionStorage.removeItem('authTokens');
  sessionStorage.removeItem('loginTime');
  sessionStorage.removeItem('lastActivityTime');
}

/**
 * Check if tokens are expired
 * @param {Object} tokens - Tokens object
 * @returns {boolean} - True if expired
 */
export function areTokensExpired(tokens) {
  if (!tokens || !tokens.expiresIn) {
    return true;
  }
  
  // Get when tokens were stored
  const loginTime = parseInt(sessionStorage.getItem('loginTime') || '0');
  if (!loginTime) {
    return true;
  }
  
  const now = Date.now();
  const expiresAt = loginTime + (tokens.expiresIn * 1000);
  
  return now >= expiresAt;
}

/**
 * Initiate forgot password flow
 * @param {string} email - User email
 * @returns {Promise<void>}
 */
export async function forgotPassword(email) {
  try {
    const command = new ForgotPasswordCommand({
      ClientId: CLIENT_ID,
      Username: email.toLowerCase().trim(),
    });

    await cognitoClient.send(command);
  } catch (error) {
    console.error('Forgot password error:', error);
    throw error;
  }
}

/**
 * Confirm forgot password with verification code
 * @param {string} email - User email
 * @param {string} code - Verification code from email
 * @param {string} newPassword - New password
 * @returns {Promise<void>}
 */
export async function confirmForgotPassword(email, code, newPassword) {
  try {
    const command = new ConfirmForgotPasswordCommand({
      ClientId: CLIENT_ID,
      Username: email.toLowerCase().trim(),
      ConfirmationCode: code,
      Password: newPassword,
    });

    await cognitoClient.send(command);
  } catch (error) {
    console.error('Confirm forgot password error:', error);
    throw error;
  }
}

export default {
  signIn,
  getCurrentUser,
  signOut,
  getStoredTokens,
  storeTokens,
  clearTokens,
  areTokensExpired,
  forgotPassword,
  confirmForgotPassword,
};
