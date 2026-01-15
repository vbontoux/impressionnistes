/**
 * Centralized API Client with Authentication Error Handling
 * Handles token expiration, permission errors, and automatic redirects
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Track if we're already redirecting to avoid multiple redirects
let isRedirecting = false;

/**
 * Check if a JWT token is expired
 * @param {string} token - JWT token
 * @returns {boolean} True if expired or invalid
 */
function isTokenExpired(token) {
  if (!token) return true;
  
  try {
    // JWT format: header.payload.signature
    const parts = token.split('.');
    if (parts.length !== 3) return true;
    
    // Decode payload (base64url)
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
    
    // Check expiration (exp is in seconds, Date.now() is in milliseconds)
    if (payload.exp) {
      const now = Math.floor(Date.now() / 1000);
      return payload.exp < now;
    }
    
    return false;
  } catch (e) {
    console.error('Error parsing token:', e);
    return true; // If we can't parse it, consider it expired
  }
}

// Store reference to auth store (will be set on first use)
let authStoreInstance = null;

/**
 * Get auth store instance
 * We cache the instance to avoid repeated imports
 */
function getAuthStore() {
  if (authStoreInstance) {
    return authStoreInstance;
  }
  
  try {
    // Try to get the store using the mocked version (for tests) or real version
    if (typeof vi !== 'undefined' && vi.isMockFunction) {
      // In test environment with mocks
      const { useAuthStore } = require('../stores/authStore.js');
      authStoreInstance = useAuthStore();
    } else {
      // In production, we need to handle this differently
      // The store will be available through the global Pinia instance
      // For now, return null and let the app work without impersonation
      return null;
    }
    return authStoreInstance;
  } catch (error) {
    console.warn('Failed to load auth store:', error);
    return null;
  }
}

/**
 * Set auth store instance (called by the app on initialization)
 */
export function setAuthStoreInstance(store) {
  authStoreInstance = store;
}

/**
 * Request interceptor - Add auth token and impersonation parameter to requests
 */
apiClient.interceptors.request.use(
  (config) => {
    console.log('🔧 [apiClient] Request interceptor START')
    console.log('🔧 [apiClient] Timestamp:', Date.now())
    console.log('🔧 [apiClient] Request URL:', config.url)
    console.log('🔧 [apiClient] Full window.location.href:', window.location.href)
    
    // Use ID token for Cognito User Pool authorizer
    const hasLocalStorage = typeof localStorage !== 'undefined' && typeof localStorage.getItem === 'function'
    const token = hasLocalStorage ? (localStorage.getItem('id_token') || 
                  localStorage.getItem('access_token') || 
                  localStorage.getItem('auth_token')) : null
    
    console.log('🔧 [apiClient] Token exists:', !!token)
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Get team_manager_id from multiple sources (in order of priority):
    // 1. URL parameter (for page refreshes and URL sharing)
    // 2. Auth store (for programmatic impersonation changes) - but only if actually impersonating
    // 3. localStorage (fallback) - but verify it's a valid impersonation state
    let teamManagerId = null
    
    // Check URL first
    if (typeof window !== 'undefined' && window.location) {
      const urlParams = new URLSearchParams(window.location.search)
      teamManagerId = urlParams.get('team_manager_id')
      console.log('🔧 [apiClient] URL search params:', window.location.search)
      console.log('🔧 [apiClient] URL team_manager_id:', teamManagerId)
    }
    
    // If not in URL, check auth store (only if actually impersonating)
    if (!teamManagerId && authStoreInstance) {
      // Check if we're actually impersonating (not just have a stale ID)
      if (authStoreInstance.isImpersonating) {
        teamManagerId = authStoreInstance.impersonatedTeamManagerId
        console.log('🔧 [apiClient] AuthStore team_manager_id (impersonating):', teamManagerId)
      } else {
        console.log('🔧 [apiClient] AuthStore has ID but not impersonating - ignoring')
      }
    }
    
    // If not in store and not in URL, check localStorage as fallback
    // (This handles the case where page refreshes before authStore initializes)
    if (!teamManagerId && hasLocalStorage && !authStoreInstance) {
      teamManagerId = localStorage.getItem('impersonatedTeamManagerId')
      console.log('🔧 [apiClient] localStorage team_manager_id (fallback):', teamManagerId)
    }
    
    console.log('🔧 [apiClient] localStorage check:', {
      impersonatedTeamManagerId: hasLocalStorage ? localStorage.getItem('impersonatedTeamManagerId') : null,
      impersonatedTeamManager: hasLocalStorage ? localStorage.getItem('impersonatedTeamManager') : null
    })
    
    if (teamManagerId) {
      // Parse the URL to add query parameter
      const url = new URL(config.url, config.baseURL || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000'));
      url.searchParams.set('team_manager_id', teamManagerId);
      
      // Update config with new URL (pathname + search)
      config.url = url.pathname + url.search;
      
      console.log('🔧 [apiClient] Added team_manager_id parameter, new URL:', config.url);
    } else {
      console.log('🔧 [apiClient] No team_manager_id found - using admin context')
    }
    
    console.log('🔧 [apiClient] Request interceptor END')
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor - Handle authentication and permission errors
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    console.log('🔧 API Client interceptor triggered');
    console.log('🔧 Error:', error);
    
    const originalRequest = error.config;

    // Handle network errors
    if (!error.response) {
      console.error('❌ Network error:', error.message);
      console.log('🔍 Error details:', {
        message: error.message,
        code: error.code,
        config: error.config?.url
      });
      
      // IMPORTANT: When API Gateway Cognito authorizer returns 401, 
      // it doesn't include CORS headers, causing a CORS error in the browser.
      // This appears as a network error, not a 401 response.
      // We need to detect this and treat it as an authentication error.
      
      // Check if this is likely a CORS error due to 401
      // (Network Error on an authenticated endpoint)
      const token = localStorage.getItem('id_token') || 
                   localStorage.getItem('access_token') || 
                   localStorage.getItem('auth_token');
      
      if (token && error.message === 'Network Error') {
        console.warn('⚠️ Network error with auth token present - likely CORS error from 401');
        
        // Check if token is actually expired
        const tokenExpired = isTokenExpired(token);
        console.log('🔍 Token expired?', tokenExpired);
        
        if (tokenExpired) {
          console.log('✅ Token is expired - treating as authentication error');
          // This is definitely a 401 CORS error - treat as session expired
          error.userMessage = 'Your session has expired. Please log in again.';
        } else {
          console.log('⚠️ Token appears valid but got network error - likely 401 CORS issue');
          // Token looks valid but we got network error - still likely 401 CORS
          // (API Gateway might have rejected it for other reasons)
          error.userMessage = 'Your session has expired. Please log in again.';
        }
        
        if (!isRedirecting) {
          isRedirecting = true;
          console.log('🚪 Redirecting to login due to suspected authentication error (CORS)...');
          
          // Clear authentication from localStorage
          localStorage.removeItem('access_token');
          localStorage.removeItem('id_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user');
          
          // Store the intended destination
          const currentPath = window.location.pathname;
          if (currentPath !== '/login' && currentPath !== '/') {
            sessionStorage.setItem('redirectAfterLogin', currentPath);
            console.log('💾 Saved redirect path:', currentPath);
          }
          
          // Redirect to login
          console.log('➡️ Redirecting to /login?reason=session_expired');
          window.location.href = '/login?reason=session_expired';
          
          setTimeout(() => {
            isRedirecting = false;
          }, 1000);
        }
        
        return Promise.reject(error);
      }
      
      // Regular network error
      error.userMessage = 'Network error. Please check your connection.';
      return Promise.reject(error);
    }

    const status = error.response.status;
    const errorData = error.response.data;
    
    console.log('📊 Response status:', status);
    console.log('📊 Response data:', errorData);

    // Handle 401 Unauthorized - Token expired or invalid
    if (status === 401) {
      console.warn('🔒 Authentication error (401):', errorData);

      // API Gateway Cognito authorizer returns: {"message":"The incoming token has expired"}
      // Backend returns: {"success": false, "error": {"code": "UNAUTHORIZED", "message": "..."}}
      const errorMessage = errorData?.message || errorData?.error?.message || '';
      
      // For 401, we always treat it as session expired/invalid
      error.userMessage = 'Your session has expired. Please log in again.';
      
      // Clear auth data and redirect to login (only once)
      if (!isRedirecting) {
        isRedirecting = true;
        console.log('🚪 Redirecting to login due to authentication error...');
        console.log('🔍 Error message was:', errorMessage);
        
        // Clear authentication from localStorage
        localStorage.removeItem('access_token');
        localStorage.removeItem('id_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        
        // Store the intended destination
        const currentPath = window.location.pathname;
        if (currentPath !== '/login' && currentPath !== '/') {
          sessionStorage.setItem('redirectAfterLogin', currentPath);
          console.log('💾 Saved redirect path:', currentPath);
        }
        
        // Redirect to login using window.location to avoid circular dependencies
        console.log('➡️ Redirecting to /login?reason=session_expired');
        window.location.href = '/login?reason=session_expired';
        
        // Reset redirect flag after a delay
        setTimeout(() => {
          isRedirecting = false;
        }, 1000);
      } else {
        console.log('⏳ Already redirecting, skipping...');
      }

      return Promise.reject(error);
    }

    // Handle 403 Forbidden - Permission denied
    if (status === 403) {
      console.warn('Permission error (403):', errorData);
      
      const errorMessage = errorData?.error?.message || errorData?.message || '';
      
      // Check if it's a specific permission issue
      if (errorMessage.toLowerCase().includes('permission') ||
          errorMessage.toLowerCase().includes('forbidden') ||
          errorMessage.toLowerCase().includes('access denied')) {
        error.userMessage = 'You do not have permission to perform this action.';
      } else {
        error.userMessage = errorMessage || 'Access forbidden.';
      }

      return Promise.reject(error);
    }

    // Handle 404 Not Found
    if (status === 404) {
      error.userMessage = 'The requested resource was not found.';
      return Promise.reject(error);
    }

    // Handle 400 Bad Request - Validation errors
    if (status === 400) {
      const errorMessage = errorData?.error?.message || errorData?.message;
      
      if (typeof errorData?.error === 'object' && !errorMessage) {
        // Field-level validation errors
        error.userMessage = 'Please check your input and try again.';
        error.validationErrors = errorData.error;
      } else {
        error.userMessage = errorMessage || 'Invalid request. Please check your input.';
      }
      
      return Promise.reject(error);
    }

    // Handle 500 Internal Server Error
    if (status >= 500) {
      console.error('Server error:', errorData);
      error.userMessage = 'A server error occurred. Please try again later.';
      return Promise.reject(error);
    }

    // Handle other errors
    const genericMessage = errorData?.error?.message || 
                          errorData?.message || 
                          'An unexpected error occurred.';
    error.userMessage = genericMessage;

    return Promise.reject(error);
  }
);

/**
 * Helper function to get user-friendly error message
 * @param {Error} error - Axios error object
 * @param {Function} t - i18n translate function (optional)
 * @returns {string} User-friendly error message
 */
export function getErrorMessage(error, t = null) {
  // Use the userMessage set by the interceptor
  if (error.userMessage) {
    return error.userMessage;
  }

  // Check for i18n key in response data
  if (error.response?.data) {
    const data = error.response.data;
    
    // If we have a translation function and a reason_key, use it
    if (t && data.reason_key) {
      try {
        return t(data.reason_key);
      } catch (e) {
        console.warn('Failed to translate error key:', data.reason_key, e);
        // Fall through to use the reason or message
      }
    }
    
    // Handle both API Gateway format {"message": "..."} and backend format {"error": {"message": "..."}}
    return data.reason || data.error?.message || data.message || 'An error occurred';
  }

  // Network error
  if (error.message === 'Network Error') {
    return 'Network error. Please check your connection.';
  }

  // Timeout
  if (error.code === 'ECONNABORTED') {
    return 'Request timeout. Please try again.';
  }

  // Generic fallback
  return error.message || 'An unexpected error occurred';
}

/**
 * Helper function to check if error is authentication-related
 * @param {Error} error - Axios error object
 * @returns {boolean}
 */
export function isAuthError(error) {
  return error.response?.status === 401;
}

/**
 * Helper function to check if error is permission-related
 * @param {Error} error - Axios error object
 * @returns {boolean}
 */
export function isPermissionError(error) {
  return error.response?.status === 403;
}

/**
 * Helper function to check if error is validation-related
 * @param {Error} error - Axios error object
 * @returns {boolean}
 */
export function isValidationError(error) {
  return error.response?.status === 400 && error.validationErrors;
}

/**
 * Legacy Rental Boat API Methods (Deprecated)
 * These will be removed after migration
 */

/**
 * Get available rental boats (DEPRECATED - use getMyRentalRequests instead)
 * @deprecated
 * @returns {Promise} API response
 */
export async function getAvailableRentalBoats() {
  return apiClient.get('/rental/boats');
}

/**
 * Request a rental boat (DEPRECATED - use createRentalRequest instead)
 * @deprecated
 * @param {string} rentalBoatId - ID of the rental boat to request
 * @returns {Promise} API response
 */
export async function requestRentalBoat(rentalBoatId) {
  return apiClient.post('/rental/request', { rental_boat_id: rentalBoatId });
}

/**
 * Cancel a rental boat request (DEPRECATED - use cancelRentalRequest instead)
 * @deprecated
 * @param {string} rentalBoatId - ID of the rental boat to cancel
 * @returns {Promise} API response
 */
export async function cancelRentalBoat(rentalBoatId) {
  return apiClient.delete(`/rental/cancel/${encodeURIComponent(rentalBoatId)}`);
}

export default apiClient;
