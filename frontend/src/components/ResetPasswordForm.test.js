/**
 * ResetPasswordForm Component Tests
 * Feature: self-hosted-authentication
 * 
 * Property tests for reset password flow and password validation
 */
import { describe, test, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { createRouter, createMemoryHistory } from 'vue-router';
import ResetPasswordForm from './ResetPasswordForm.vue';
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

describe('ResetPasswordForm - Property Tests', () => {
  let wrapper;
  let authStore;
  let router;

  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    setActivePinia(createPinia());
    authStore = useAuthStore();
    router = createMockRouter();
    
    wrapper = mount(ResetPasswordForm, {
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
          PasswordStrengthIndicator: {
            template: '<div class="password-strength"></div>',
            props: ['strength'],
          },
        },
      },
    });
  });

  /**
   * Property 10: Password Validation Rules
   * Validates: Requirements 3.6, 3.7, 4.2, 4.3
   */
  test('Property 10: weak passwords are rejected', async () => {
    authStore.resetPassword = vi.fn();
    
    // Fill in form with weak password
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.findAll('input[type="text"]')[0].setValue('123456'); // code
    await wrapper.findAll('input[type="password"]')[0].setValue('weak'); // weak password
    await wrapper.findAll('input[type="password"]')[1].setValue('weak'); // confirm
    
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    
    // Property: weak password is rejected
    expect(authStore.resetPassword).not.toHaveBeenCalled();
    expect(wrapper.vm.errors.newPassword).toBeTruthy();
  });

  test('Property 10: strong passwords are accepted', async () => {
    authStore.resetPassword = vi.fn().mockResolvedValue({ success: true });
    
    // Fill in form with strong password
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.findAll('input[type="text"]')[0].setValue('123456'); // code
    await wrapper.findAll('input[type="password"]')[0].setValue('StrongPassword123!'); // strong password
    await wrapper.findAll('input[type="password"]')[1].setValue('StrongPassword123!'); // confirm
    
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    
    // Property: strong password is accepted
    expect(authStore.resetPassword).toHaveBeenCalledWith('test@example.com', '123456', 'StrongPassword123!');
  });

  /**
   * Property 11: Password Strength Indicator
   * Validates: Requirements 3.6, 3.7, 4.2, 4.3
   */
  test('Property 11: strength indicator updates correctly', async () => {
    const passwordInput = wrapper.findAll('input[type="password"]')[0];
    
    // Type weak password
    await passwordInput.setValue('weak');
    await wrapper.vm.$nextTick();
    
    // Property: strength indicator shows low score
    expect(wrapper.vm.passwordStrength.score).toBeLessThan(3);
    
    // Type strong password
    await passwordInput.setValue('StrongPassword123!');
    await wrapper.vm.$nextTick();
    
    // Property: strength indicator shows high score
    expect(wrapper.vm.passwordStrength.score).toBeGreaterThanOrEqual(3);
  });

  test('Property 11: strength indicator is visible when password is entered', async () => {
    const passwordInput = wrapper.findAll('input[type="password"]')[0];
    
    // Initially no password
    expect(wrapper.find('.password-strength').exists()).toBe(false);
    
    // Type password
    await passwordInput.setValue('SomePassword123!');
    await wrapper.vm.$nextTick();
    
    // Property: strength indicator is now visible
    expect(wrapper.find('.password-strength').exists()).toBe(true);
  });

  /**
   * Property 12: Password Confirmation Match
   * Validates: Requirements 3.6, 3.7
   */
  test('Property 12: mismatched passwords prevent submission', async () => {
    authStore.resetPassword = vi.fn();
    
    // Fill in form with mismatched passwords
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.findAll('input[type="text"]')[0].setValue('123456'); // code
    await wrapper.findAll('input[type="password"]')[0].setValue('StrongPassword123!');
    await wrapper.findAll('input[type="password"]')[1].setValue('DifferentPassword123!');
    
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    
    // Property: mismatched passwords prevent submission
    expect(authStore.resetPassword).not.toHaveBeenCalled();
    expect(wrapper.vm.errors.confirmPassword).toBeTruthy();
  });

  test('Property 12: matched passwords allow submission', async () => {
    authStore.resetPassword = vi.fn().mockResolvedValue({ success: true });
    
    // Fill in form with matched passwords
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.findAll('input[type="text"]')[0].setValue('123456'); // code
    await wrapper.findAll('input[type="password"]')[0].setValue('StrongPassword123!');
    await wrapper.findAll('input[type="password"]')[1].setValue('StrongPassword123!');
    
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    
    // Property: matched passwords allow submission
    expect(authStore.resetPassword).toHaveBeenCalled();
  });

  /**
   * Property 8: Reset Password API Call
   * Validates: Requirements 3.3, 3.4
   */
  test('Property 8: valid submission calls correct API', async () => {
    authStore.resetPassword = vi.fn().mockResolvedValue({ success: true });
    
    // Fill in complete form
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.findAll('input[type="text"]')[0].setValue('123456');
    await wrapper.findAll('input[type="password"]')[0].setValue('NewPassword123!');
    await wrapper.findAll('input[type="password"]')[1].setValue('NewPassword123!');
    
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    
    // Property: resetPassword called with correct parameters
    expect(authStore.resetPassword).toHaveBeenCalledWith('test@example.com', '123456', 'NewPassword123!');
    expect(authStore.resetPassword).toHaveBeenCalledTimes(1);
  });

  /**
   * Property 9: Reset Password Success Flow
   * Validates: Requirements 3.3, 3.4
   */
  test('Property 9: success redirects after 3 seconds', async () => {
    authStore.resetPassword = vi.fn().mockResolvedValue({ success: true });
    
    // Mock router push
    const pushSpy = vi.spyOn(router, 'push');
    
    // Fill in complete form
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.findAll('input[type="text"]')[0].setValue('123456');
    await wrapper.findAll('input[type="password"]')[0].setValue('NewPassword123!');
    await wrapper.findAll('input[type="password"]')[1].setValue('NewPassword123!');
    
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
    
    // Property: redirects to login page
    expect(pushSpy).toHaveBeenCalledWith('/login');
  });

  test('pre-fills email from query parameter', async () => {
    // Create new wrapper with query parameter
    const routerWithQuery = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } },
        { path: '/reset-password', component: { template: '<div>Reset Password</div>' } },
      ],
    });
    
    await routerWithQuery.push({ path: '/reset-password', query: { email: 'prefilled@example.com' } });
    
    const wrapperWithQuery = mount(ResetPasswordForm, {
      global: {
        plugins: [routerWithQuery],
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
          PasswordStrengthIndicator: {
            template: '<div class="password-strength"></div>',
            props: ['strength'],
          },
        },
      },
    });
    
    await wrapperWithQuery.vm.$nextTick();
    
    // Property: email is pre-filled from query parameter
    expect(wrapperWithQuery.vm.form.email).toBe('prefilled@example.com');
  });

  test('displays error message on API failure', async () => {
    authStore.resetPassword = vi.fn().mockRejectedValue(new Error('Invalid code'));
    authStore.error = 'Code de vérification invalide';
    
    // Fill in complete form
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.findAll('input[type="text"]')[0].setValue('wrong-code');
    await wrapper.findAll('input[type="password"]')[0].setValue('NewPassword123!');
    await wrapper.findAll('input[type="password"]')[1].setValue('NewPassword123!');
    
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    
    // Wait for async operations
    await new Promise(resolve => setTimeout(resolve, 10));
    await wrapper.vm.$nextTick();
    
    // Verify error is displayed
    expect(wrapper.vm.errorMessage).toBeTruthy();
  });
});
