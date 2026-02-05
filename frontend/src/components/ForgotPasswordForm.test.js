/**
 * ForgotPasswordForm Component Tests
 * Feature: self-hosted-authentication
 * 
 * Property tests for forgot password flow
 */
import { describe, test, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { createRouter, createMemoryHistory } from 'vue-router';
import ForgotPasswordForm from './ForgotPasswordForm.vue';
import { useAuthStore } from '../stores/authStore';

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = value.toString(); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();

global.localStorage = localStorageMock;

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

// Mock i18n
const mockT = (key) => key;
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: mockT,
  }),
}));

// Create mock router
const createMockRouter = () => {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div>Home</div>' } },
      { path: '/login', component: { template: '<div>Login</div>' } },
      { path: '/reset-password', component: { template: '<div>Reset Password</div>' } },
    ],
  });
};

describe('ForgotPasswordForm - Property Tests', () => {
  let wrapper;
  let authStore;
  let router;

  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    setActivePinia(createPinia());
    authStore = useAuthStore();
    router = createMockRouter();
    
    wrapper = mount(ForgotPasswordForm, {
      global: {
        plugins: [router],
        mocks: {
          $t: mockT,
        },
        stubs: {
          FormGroup: {
            template: '<div class="form-group"><slot /></div>',
          },
          BaseButton: {
            template: '<button><slot /></button>',
            props: ['type', 'variant', 'size', 'fullWidth', 'loading', 'disabled'],
          },
          MessageAlert: {
            template: '<div class="message-alert"><slot /></div>',
            props: ['type', 'message', 'dismissible'],
          },
        },
      },
    });
  });

  /**
   * Property 5: Forgot Password API Call
   * Validates: Requirements 2.2, 2.3
   */
  test('Property 5: valid email triggers correct API call', async () => {
    // Mock successful forgot password
    authStore.forgotPassword = vi.fn().mockResolvedValue({ success: true });
    
    // Fill in email
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    
    // Property: forgotPassword was called with correct email
    expect(authStore.forgotPassword).toHaveBeenCalledWith('test@example.com');
    expect(authStore.forgotPassword).toHaveBeenCalledTimes(1);
  });

  /**
   * Property 6: Forgot Password Success Flow
   * Validates: Requirements 2.2, 2.3
   */
  test('Property 6: success displays message and redirects', async () => {
    // Mock successful forgot password
    authStore.forgotPassword = vi.fn().mockResolvedValue({ success: true });
    
    // Mock router push
    const pushSpy = vi.spyOn(router, 'push');
    
    // Fill in email
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    
    // Wait for async operations
    await new Promise(resolve => setTimeout(resolve, 10));
    await wrapper.vm.$nextTick();
    
    // Property: success message is displayed
    expect(wrapper.vm.successMessage).toBeTruthy();
    
    // Property: form is hidden after success
    expect(wrapper.find('form').exists()).toBe(false);
    
    // Wait for redirect timeout (3 seconds)
    await new Promise(resolve => setTimeout(resolve, 3100));
    
    // Property: redirects to reset password page with email
    expect(pushSpy).toHaveBeenCalledWith({
      path: '/reset-password',
      query: { email: 'test@example.com' },
    });
  });

  test('displays error message on API failure', async () => {
    // Mock failed forgot password
    authStore.forgotPassword = vi.fn().mockRejectedValue(new Error('User not found'));
    authStore.error = 'Utilisateur non trouvé';
    
    // Fill in email
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    
    // Wait for async operations
    await new Promise(resolve => setTimeout(resolve, 10));
    await wrapper.vm.$nextTick();
    
    // Verify error is displayed
    expect(wrapper.vm.errorMessage).toBeTruthy();
  });

  test('validates email format before submission', async () => {
    authStore.forgotPassword = vi.fn();
    
    // Try to submit with invalid email
    await wrapper.find('input[type="email"]').setValue('invalid-email');
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    
    // Verify API was not called
    expect(authStore.forgotPassword).not.toHaveBeenCalled();
    
    // Verify error is set
    expect(wrapper.vm.errors.email).toBeTruthy();
  });

  test('shows loading state during API call', async () => {
    // Mock forgot password that takes time
    authStore.forgotPassword = vi.fn().mockImplementation(() => {
      return new Promise(resolve => setTimeout(() => resolve({ success: true }), 100));
    });
    
    // Fill in email
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    
    // Submit form
    const submitPromise = wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    
    // Verify loading state is true
    expect(wrapper.vm.loading).toBe(true);
    
    // Wait for API call to complete
    await submitPromise;
    await new Promise(resolve => setTimeout(resolve, 150));
    await wrapper.vm.$nextTick();
    
    // Verify loading state is false
    expect(wrapper.vm.loading).toBe(false);
  });
});
