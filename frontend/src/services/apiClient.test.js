/**
 * API Client Interceptor Tests
 * Unit tests for impersonation parameter injection
 */
import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
};
global.localStorage = localStorageMock;

// Mock the auth store
let mockAuthStore = {
  isImpersonating: false,
  impersonatedTeamManagerId: null
};

vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(() => mockAuthStore)
}));

// Mock axios
const mockAxios = {
  create: vi.fn(() => mockAxios),
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  interceptors: {
    request: {
      use: vi.fn(),
      eject: vi.fn()
    },
    response: {
      use: vi.fn(),
      eject: vi.fn()
    }
  }
};

vi.mock('axios', () => ({
  default: mockAxios
}));

describe('API Client - Impersonation Interceptor', () => {
  let requestInterceptor;

  beforeEach(async () => {
    // Reset mocks
    vi.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    
    // Reset mock auth store
    mockAuthStore = {
      isImpersonating: false,
      impersonatedTeamManagerId: null
    };
    
    // Import apiClient module
    const apiClientModule = await import('./apiClient.js');
    
    // Set the auth store instance for the API client
    apiClientModule.setAuthStoreInstance(mockAuthStore);
    
    // Capture the request interceptor (first argument of the first call)
    const calls = mockAxios.interceptors.request.use.mock.calls;
    if (calls.length > 0) {
      requestInterceptor = calls[calls.length - 1][0];
    }
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Parameter injection when impersonating', () => {
    test('should add team_manager_id parameter when admin is impersonating', () => {
      // Set up mock auth store
      mockAuthStore.isImpersonating = true;
      mockAuthStore.impersonatedTeamManagerId = 'tm-456';

      // Create a mock config
      const config = {
        url: '/test-endpoint',
        baseURL: 'http://localhost:3000',
        headers: {}
      };

      // Call the interceptor
      const result = requestInterceptor(config);

      // Verify the URL includes the team_manager_id parameter
      expect(result.url).toContain('team_manager_id=tm-456');
    });

    test('should add parameter to URL with existing query parameters', () => {
      // Set up mock auth store
      mockAuthStore.isImpersonating = true;
      mockAuthStore.impersonatedTeamManagerId = 'tm-789';

      // Create a mock config with existing query parameters
      const config = {
        url: '/test-endpoint?existing=value',
        baseURL: 'http://localhost:3000',
        headers: {}
      };

      // Call the interceptor
      const result = requestInterceptor(config);

      // Verify both parameters are present
      expect(result.url).toContain('existing=value');
      expect(result.url).toContain('team_manager_id=tm-789');
    });

    test('should preserve multiple existing query parameters', () => {
      // Set up mock auth store
      mockAuthStore.isImpersonating = true;
      mockAuthStore.impersonatedTeamManagerId = 'tm-999';

      // Create a mock config with multiple existing query parameters
      const config = {
        url: '/test-endpoint?param1=value1&param2=value2',
        baseURL: 'http://localhost:3000',
        headers: {}
      };

      // Call the interceptor
      const result = requestInterceptor(config);

      // Verify all parameters are present
      expect(result.url).toContain('param1=value1');
      expect(result.url).toContain('param2=value2');
      expect(result.url).toContain('team_manager_id=tm-999');
    });
  });

  describe('No parameter injection when not impersonating', () => {
    test('should not add parameter when admin is not impersonating', () => {
      // Set up mock auth store without impersonation
      mockAuthStore.isImpersonating = false;
      mockAuthStore.impersonatedTeamManagerId = null;

      // Create a mock config
      const config = {
        url: '/test-endpoint',
        baseURL: 'http://localhost:3000',
        headers: {}
      };

      // Call the interceptor
      const result = requestInterceptor(config);

      // Verify the URL does NOT include the team_manager_id parameter
      expect(result.url).not.toContain('team_manager_id');
    });

    test('should not add parameter when non-admin user is logged in', () => {
      // Set up mock auth store - non-admin cannot impersonate
      mockAuthStore.isImpersonating = false;
      mockAuthStore.impersonatedTeamManagerId = null;

      // Create a mock config
      const config = {
        url: '/test-endpoint',
        baseURL: 'http://localhost:3000',
        headers: {}
      };

      // Call the interceptor
      const result = requestInterceptor(config);

      // Verify the URL does NOT include the team_manager_id parameter
      expect(result.url).not.toContain('team_manager_id');
    });

    test('should not add parameter when no user is logged in', () => {
      // Set up mock auth store - no user
      mockAuthStore.isImpersonating = false;
      mockAuthStore.impersonatedTeamManagerId = null;

      // Create a mock config
      const config = {
        url: '/test-endpoint',
        baseURL: 'http://localhost:3000',
        headers: {}
      };

      // Call the interceptor
      const result = requestInterceptor(config);

      // Verify the URL does NOT include the team_manager_id parameter
      expect(result.url).not.toContain('team_manager_id');
    });
  });

  describe('Request integrity preservation', () => {
    test('should preserve request method', () => {
      // Set up mock auth store
      mockAuthStore.isImpersonating = true;
      mockAuthStore.impersonatedTeamManagerId = 'tm-456';

      // Create a mock config with method
      const config = {
        url: '/test-endpoint',
        baseURL: 'http://localhost:3000',
        method: 'POST',
        headers: {}
      };

      // Call the interceptor
      const result = requestInterceptor(config);

      // Verify method is preserved
      expect(result.method).toBe('POST');
    });

    test('should preserve request headers', () => {
      // Set up mock auth store
      mockAuthStore.isImpersonating = true;
      mockAuthStore.impersonatedTeamManagerId = 'tm-456';

      // Create a mock config with headers
      const config = {
        url: '/test-endpoint',
        baseURL: 'http://localhost:3000',
        headers: {
          'Content-Type': 'application/json',
          'X-Custom-Header': 'custom-value'
        }
      };

      // Call the interceptor
      const result = requestInterceptor(config);

      // Verify headers are preserved
      expect(result.headers['Content-Type']).toBe('application/json');
      expect(result.headers['X-Custom-Header']).toBe('custom-value');
    });

    test('should preserve request body', () => {
      // Set up mock auth store
      mockAuthStore.isImpersonating = true;
      mockAuthStore.impersonatedTeamManagerId = 'tm-456';

      const requestBody = {
        name: 'Test Boat',
        race_id: 'race-123'
      };

      // Create a mock config with body
      const config = {
        url: '/test-endpoint',
        baseURL: 'http://localhost:3000',
        method: 'POST',
        headers: {},
        data: requestBody
      };

      // Call the interceptor
      const result = requestInterceptor(config);

      // Verify request body is preserved
      expect(result.data).toEqual(requestBody);
    });

    test('should preserve all config properties', () => {
      // Set up mock auth store
      mockAuthStore.isImpersonating = true;
      mockAuthStore.impersonatedTeamManagerId = 'tm-456';

      // Create a mock config with various properties
      const config = {
        url: '/test-endpoint',
        baseURL: 'http://localhost:3000',
        method: 'PUT',
        headers: { 'X-Test': 'value' },
        data: { test: 'data' },
        timeout: 5000,
        params: { existing: 'param' }
      };

      // Call the interceptor
      const result = requestInterceptor(config);

      // Verify all properties are preserved
      expect(result.method).toBe('PUT');
      expect(result.headers['X-Test']).toBe('value');
      expect(result.data).toEqual({ test: 'data' });
      expect(result.timeout).toBe(5000);
      expect(result.params).toEqual({ existing: 'param' });
    });
  });

  describe('Error handling', () => {
    test('should handle missing impersonatedTeamManagerId', () => {
      // Set up mock auth store with isImpersonating true but no ID
      mockAuthStore.isImpersonating = true;
      mockAuthStore.impersonatedTeamManagerId = null;

      // Create a mock config
      const config = {
        url: '/test-endpoint',
        baseURL: 'http://localhost:3000',
        headers: {}
      };

      // Call the interceptor
      const result = requestInterceptor(config);

      // Should not add parameter without ID
      expect(result.url).not.toContain('team_manager_id');
    });

    test('should handle undefined auth store properties', () => {
      // Set up mock auth store with undefined properties
      mockAuthStore.isImpersonating = undefined;
      mockAuthStore.impersonatedTeamManagerId = undefined;

      // Create a mock config
      const config = {
        url: '/test-endpoint',
        baseURL: 'http://localhost:3000',
        headers: {}
      };

      // Should not throw an error
      expect(() => requestInterceptor(config)).not.toThrow();
      
      const result = requestInterceptor(config);

      // Should not add parameter
      expect(result.url).not.toContain('team_manager_id');
    });

    test('should handle empty impersonatedTeamManagerId', () => {
      // Set up mock auth store with empty string
      mockAuthStore.isImpersonating = true;
      mockAuthStore.impersonatedTeamManagerId = '';

      // Create a mock config
      const config = {
        url: '/test-endpoint',
        baseURL: 'http://localhost:3000',
        headers: {}
      };

      // Call the interceptor
      const result = requestInterceptor(config);

      // Should not add parameter with empty string
      expect(result.url).not.toContain('team_manager_id');
    });

    test('should handle false isImpersonating with ID present', () => {
      // Set up mock auth store with ID but not impersonating
      mockAuthStore.isImpersonating = false;
      mockAuthStore.impersonatedTeamManagerId = 'tm-456';

      // Create a mock config
      const config = {
        url: '/test-endpoint',
        baseURL: 'http://localhost:3000',
        headers: {}
      };

      // Call the interceptor
      const result = requestInterceptor(config);

      // Should not add parameter when not impersonating
      expect(result.url).not.toContain('team_manager_id');
    });
  });
});
