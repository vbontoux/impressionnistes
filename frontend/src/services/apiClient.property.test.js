/**
 * API Client Interceptor Property-Based Tests
 * Feature: admin-impersonation
 * 
 * Property-based tests for API client impersonation parameter injection using fast-check
 */
import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest';
import * as fc from 'fast-check';

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

describe('API Client - Property-Based Tests', () => {
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
    
    // Capture the request interceptor
    const calls = mockAxios.interceptors.request.use.mock.calls;
    if (calls.length > 0) {
      requestInterceptor = calls[calls.length - 1][0];
    }
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  /**
   * Feature: admin-impersonation, Property 6: API client parameter injection
   * Validates: Requirements 6.1
   * 
   * For any API request while impersonating, the API client automatically adds
   * team_manager_id as a query parameter.
   */
  test('Property 6: API client adds team_manager_id parameter when impersonating', () => {
    fc.assert(
      fc.property(
        fc.record({
          endpoint: fc.webPath().filter(path => path !== '' && path !== '/' && !path.startsWith('//')),
          teamManagerId: fc.string({ minLength: 1, maxLength: 50 }).filter(id => id.trim().length > 0),
          isImpersonating: fc.constant(true),
        }),
        ({ endpoint, teamManagerId, isImpersonating }) => {
          // Set up mock auth store
          mockAuthStore.isImpersonating = isImpersonating;
          mockAuthStore.impersonatedTeamManagerId = teamManagerId;

          // Create a mock config
          const config = {
            url: endpoint,
            baseURL: 'http://localhost:3000',
            headers: {}
          };

          // Call the interceptor
          const result = requestInterceptor(config);

          // Property: URL should contain the team_manager_id parameter
          expect(result.url).toContain('team_manager_id=');
          // Check that the ID is present (URL encoded or not)
          const url = new URL(result.url, 'http://localhost:3000');
          expect(url.searchParams.get('team_manager_id')).toBe(teamManagerId);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Feature: admin-impersonation, Property 14: Request parameter preservation
   * Validates: Requirements 6.3
   * 
   * For any API request with existing query parameters, adding team_manager_id
   * does not overwrite or remove existing parameters.
   */
  test('Property 14: Existing query parameters are preserved when adding team_manager_id', () => {
    fc.assert(
      fc.property(
        fc.record({
          endpoint: fc.webPath().filter(path => path !== '' && path !== '/' && !path.startsWith('//')),
          teamManagerId: fc.string({ minLength: 1, maxLength: 50 }).filter(id => id.trim().length > 0),
          existingParams: fc.dictionary(
            fc.string({ minLength: 1, maxLength: 20 }).filter(key => key.trim().length > 0),
            fc.string({ minLength: 1, maxLength: 50 }).filter(val => val.trim().length > 0),
            { minKeys: 1, maxKeys: 5 }
          ),
        }),
        ({ endpoint, teamManagerId, existingParams }) => {
          // Set up mock auth store
          mockAuthStore.isImpersonating = true;
          mockAuthStore.impersonatedTeamManagerId = teamManagerId;

          // Build URL with existing parameters
          const params = new URLSearchParams(existingParams);
          const urlWithParams = `${endpoint}?${params.toString()}`;

          // Create a mock config
          const config = {
            url: urlWithParams,
            baseURL: 'http://localhost:3000',
            headers: {}
          };

          // Call the interceptor
          const result = requestInterceptor(config);

          // Property: All existing parameters should still be present
          const resultUrl = new URL(result.url, 'http://localhost:3000');
          for (const [key, value] of Object.entries(existingParams)) {
            expect(resultUrl.searchParams.get(key)).toBe(value);
          }

          // And team_manager_id should be added
          expect(resultUrl.searchParams.get('team_manager_id')).toBe(teamManagerId);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Feature: admin-impersonation, Property 15: Request integrity preservation
   * Validates: Requirements 6.4
   * 
   * For any API request, the interceptor preserves the original request method,
   * headers, and body.
   */
  test('Property 15: Request method, headers, and body are preserved', () => {
    fc.assert(
      fc.property(
        fc.record({
          endpoint: fc.webPath().filter(path => path !== '' && path !== '/' && !path.startsWith('//')),
          teamManagerId: fc.string({ minLength: 1, maxLength: 50 }).filter(id => id.trim().length > 0),
          method: fc.constantFrom('GET', 'POST', 'PUT', 'DELETE', 'PATCH'),
          headers: fc.dictionary(
            fc.string({ minLength: 1, maxLength: 20 }),
            fc.string({ minLength: 1, maxLength: 50 }),
            { minKeys: 0, maxKeys: 5 }
          ),
          body: fc.option(
            fc.record({
              name: fc.string({ minLength: 1, maxLength: 50 }),
              value: fc.string({ minLength: 1, maxLength: 100 }),
            }),
            { nil: null }
          ),
        }),
        ({ endpoint, teamManagerId, method, headers, body }) => {
          // Set up mock auth store
          mockAuthStore.isImpersonating = true;
          mockAuthStore.impersonatedTeamManagerId = teamManagerId;

          // Create a mock config
          const config = {
            url: endpoint,
            baseURL: 'http://localhost:3000',
            method: method,
            headers: headers,
            data: body
          };

          // Call the interceptor
          const result = requestInterceptor(config);

          // Property: Method, headers, and body should be preserved
          expect(result.method).toBe(method);
          expect(result.headers).toEqual(headers);
          expect(result.data).toEqual(body);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Additional property: No parameter injection when not impersonating
   * 
   * For any API request when not impersonating, the team_manager_id parameter
   * should not be added.
   */
  test('Property: No team_manager_id parameter when not impersonating', () => {
    fc.assert(
      fc.property(
        fc.record({
          endpoint: fc.webPath().filter(path => path !== '' && path !== '/' && !path.startsWith('//')),
          isImpersonating: fc.constant(false),
        }),
        ({ endpoint, isImpersonating }) => {
          // Set up mock auth store
          mockAuthStore.isImpersonating = isImpersonating;
          mockAuthStore.impersonatedTeamManagerId = null;

          // Create a mock config
          const config = {
            url: endpoint,
            baseURL: 'http://localhost:3000',
            headers: {}
          };

          // Call the interceptor
          const result = requestInterceptor(config);

          // Property: URL should NOT contain the team_manager_id parameter
          expect(result.url).not.toContain('team_manager_id');
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Additional property: Parameter not added with invalid team manager ID
   * 
   * For any API request with null or empty team manager ID, the parameter
   * should not be added even if isImpersonating is true.
   */
  test('Property: No parameter with null or empty team manager ID', () => {
    fc.assert(
      fc.property(
        fc.record({
          endpoint: fc.webPath().filter(path => path !== '' && path !== '/' && !path.startsWith('//')),
          teamManagerId: fc.constantFrom(null, '', undefined),
        }),
        ({ endpoint, teamManagerId }) => {
          // Set up mock auth store
          mockAuthStore.isImpersonating = true;
          mockAuthStore.impersonatedTeamManagerId = teamManagerId;

          // Create a mock config
          const config = {
            url: endpoint,
            baseURL: 'http://localhost:3000',
            headers: {}
          };

          // Call the interceptor
          const result = requestInterceptor(config);

          // Property: URL should NOT contain the team_manager_id parameter
          expect(result.url).not.toContain('team_manager_id');
        }
      ),
      { numRuns: 100 }
    );
  });
});
