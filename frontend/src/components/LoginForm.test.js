/**
 * LoginForm Component Unit Tests
 * Feature: self-hosted-authentication
 * 
 * Tests for LoginForm.vue component
 */
import { describe, test, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { createRouter, createMemoryHistory } from 'vue-router';
import LoginForm from './LoginForm.vue';
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
      { path: '/dashboard', component: { template: '<div>Dashboard</div>' } },
      { path: '/register', component: { template: '<div>Register</div>' } },
      { path: '/forgot-password', component: { template: '<div>Forgot Password</div>' } },
      { path: '/verify-email', component: { template: '<div>Verify Email</div>' } },
    ],
  });
};

describe('LoginForm Component - Unit Tests', () => {
  let wrapper;
  let authStore;
  let router;

  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    setActivePinia(createPinia());
    authStore = useAuthStore();
    router = createMockRouter();
    
    wrapper = mount(LoginForm, {
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

  test('renders login form with email and password fields', () => {
    expect(wrapper.find('input[type="email"]').exists()).toBe(true);
    expect(wrapper.find('input[type="password"]').exists()).toBe(true);
    expect(wrapper.find('input[type="checkbox"]').exists()).toBe(true); // Remember me
    expect(wrapper.find('button').exists()).toBe(true); // Submit button (stubbed)
  });

  test('successful login flow', async () => {
    // Mock successful login
    authStore.login = vi.fn().mockResolvedValue(true);
    authStore.error = null;
    
    // Fill in form
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.find('input[type="password"]').setValue('TestPassword123!');
    await wrapper.find('input[type="checkbox"]').setChecked(true);
    
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    
    // Verify login was called with correct parameters
    expect(authStore.login).toHaveBeenCalledWith('test@example.com', 'TestPassword123!', true);
  });

  test('displays error message on invalid credentials', async () => {
    // Mock failed login
    authStore.login = vi.fn().mockResolvedValue(false);
    authStore.error = 'Identifiants incorrects';
    
    // Fill in form
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.find('input[type="password"]').setValue('WrongPassword');
    
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    
    // Wait for error to be set
    await new Promise(resolve => setTimeout(resolve, 10));
    await wrapper.vm.$nextTick();
    
    // Verify error is displayed
    expect(wrapper.vm.errorMessage).toBeTruthy();
  });

  test('displays session timeout message for max duration', async () => {
    authStore.sessionTimeoutReason = 'max_duration';
    
    await wrapper.vm.$nextTick();
    
    // Verify timeout message is computed
    expect(wrapper.vm.sessionTimeoutMessage).toBe('auth.login.sessionExpiredMaxDuration');
  });

  test('displays session timeout message for inactivity', async () => {
    authStore.sessionTimeoutReason = 'inactivity';
    
    await wrapper.vm.$nextTick();
    
    // Verify timeout message is computed
    expect(wrapper.vm.sessionTimeoutMessage).toBe('auth.login.sessionExpiredInactivity');
  });

  test('validates email format', async () => {
    const emailInput = wrapper.find('input[type="email"]');
    
    // Test invalid email
    await emailInput.setValue('invalid-email');
    await emailInput.trigger('blur');
    await wrapper.vm.$nextTick();
    
    expect(wrapper.vm.errors.email).toBeTruthy();
    
    // Test valid email
    await emailInput.setValue('valid@example.com');
    await emailInput.trigger('blur');
    await wrapper.vm.$nextTick();
    
    expect(wrapper.vm.errors.email).toBe('');
  });

  test('validates password is required', async () => {
    const passwordInput = wrapper.find('input[type="password"]');
    
    // Test empty password
    await passwordInput.setValue('');
    await passwordInput.trigger('blur');
    await wrapper.vm.$nextTick();
    
    expect(wrapper.vm.errors.password).toBeTruthy();
    
    // Test with password
    await passwordInput.setValue('SomePassword123!');
    await passwordInput.trigger('blur');
    await wrapper.vm.$nextTick();
    
    expect(wrapper.vm.errors.password).toBe('');
  });

  test('prevents submission with validation errors', async () => {
    authStore.login = vi.fn();
    
    // Submit form without filling fields
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    
    // Verify login was not called
    expect(authStore.login).not.toHaveBeenCalled();
    
    // Verify errors are set
    expect(wrapper.vm.errors.email).toBeTruthy();
    expect(wrapper.vm.errors.password).toBeTruthy();
  });

  test('shows loading state during login', async () => {
    // Mock login that takes time
    authStore.login = vi.fn().mockImplementation(() => {
      return new Promise(resolve => setTimeout(() => resolve(true), 100));
    });
    
    // Fill in form
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.find('input[type="password"]').setValue('TestPassword123!');
    
    // Submit form
    const submitPromise = wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    
    // Verify loading state is true
    expect(wrapper.vm.loading).toBe(true);
    
    // Wait for login to complete
    await submitPromise;
    await new Promise(resolve => setTimeout(resolve, 150));
    await wrapper.vm.$nextTick();
    
    // Verify loading state is false
    expect(wrapper.vm.loading).toBe(false);
  });

  test('has links to forgot password, register, and verify email', () => {
    // Check that router-link components exist with correct 'to' props
    const routerLinks = wrapper.findAllComponents({ name: 'RouterLink' });
    
    expect(routerLinks.length).toBeGreaterThanOrEqual(3);
    
    // Find links by their 'to' prop
    const forgotPasswordLink = routerLinks.find(link => link.props('to') === '/forgot-password');
    const registerLink = routerLinks.find(link => link.props('to') === '/register');
    const verifyEmailLink = routerLinks.find(link => link.props('to') === '/verify-email');
    
    expect(forgotPasswordLink).toBeTruthy();
    expect(registerLink).toBeTruthy();
    expect(verifyEmailLink).toBeTruthy();
  });
});
