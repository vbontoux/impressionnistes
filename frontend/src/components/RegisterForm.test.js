/**
 * Tests for Register Form Component
 * Ensures consent checkboxes work correctly and form validation
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import RegisterForm from './RegisterForm.vue'
import en from '../locales/en.json'
import fr from '../locales/fr.json'

// Create i18n instance for testing
const createI18nInstance = (locale = 'en') => {
  return createI18n({
    legacy: false,
    locale,
    messages: { en, fr }
  })
}

// Create router instance for testing
const createRouterInstance = () => {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div>Home</div>' } },
      { path: '/login', component: { template: '<div>Login</div>' } },
      { path: '/verify-email', component: { template: '<div>Verify Email</div>' } },
      { path: '/privacy-policy', component: { template: '<div>Privacy Policy</div>' } },
      { path: '/terms-conditions', component: { template: '<div>Terms</div>' } }
    ]
  })
}

// Mock axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { data: { clubs: [] } } })),
    create: vi.fn(() => ({
      get: vi.fn(() => Promise.resolve({ data: { data: { clubs: [] } } })),
      post: vi.fn(() => Promise.resolve({ data: {} })),
      put: vi.fn(() => Promise.resolve({ data: {} })),
      delete: vi.fn(() => Promise.resolve({ data: {} })),
      interceptors: {
        request: { use: vi.fn(), eject: vi.fn() },
        response: { use: vi.fn(), eject: vi.fn() }
      }
    }))
  }
}))

describe('RegisterForm.vue - Consent Functionality', () => {
  let pinia
  let localStorageMock

  beforeEach(() => {
    // Mock localStorage
    localStorageMock = {
      getItem: vi.fn(() => null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn()
    }
    global.localStorage = localStorageMock

    pinia = createPinia()
    setActivePinia(pinia)
  })

  it('should render consent checkboxes', async () => {
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(RegisterForm, {
      global: {
        plugins: [i18n, router, pinia]
      }
    })

    await wrapper.vm.$nextTick()

    // Check privacy consent checkbox exists
    const privacyCheckbox = wrapper.find('#privacyConsent')
    expect(privacyCheckbox.exists()).toBe(true)
    expect(privacyCheckbox.attributes('type')).toBe('checkbox')
    expect(privacyCheckbox.attributes('required')).toBeDefined()

    // Check terms consent checkbox exists
    const termsCheckbox = wrapper.find('#termsConsent')
    expect(termsCheckbox.exists()).toBe(true)
    expect(termsCheckbox.attributes('type')).toBe('checkbox')
    expect(termsCheckbox.attributes('required')).toBeDefined()
  })

  it('should have links to Privacy Policy and Terms & Conditions', async () => {
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(RegisterForm, {
      global: {
        plugins: [i18n, router, pinia]
      }
    })

    await wrapper.vm.$nextTick()

    // Find all router links
    const links = wrapper.findAllComponents({ name: 'RouterLink' })
    
    // Check for privacy policy link
    const privacyLink = links.find(link => link.props('to') === '/privacy-policy')
    expect(privacyLink).toBeTruthy()
    expect(privacyLink.attributes('target')).toBe('_blank')

    // Check for terms link
    const termsLink = links.find(link => link.props('to') === '/terms-conditions')
    expect(termsLink).toBeTruthy()
    expect(termsLink.attributes('target')).toBe('_blank')
  })

  it('should block form submission without consent', async () => {
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(RegisterForm, {
      global: {
        plugins: [i18n, router, pinia]
      }
    })

    await wrapper.vm.$nextTick()

    // Fill in required fields
    await wrapper.find('#email').setValue('test@example.com')
    await wrapper.find('#password').setValue('TestPass123!')
    await wrapper.find('#firstName').setValue('John')
    await wrapper.find('#lastName').setValue('Doe')
    await wrapper.find('#mobileNumber').setValue('+33612345678')
    
    // Check foreign club checkbox to enable free text input
    await wrapper.find('#foreignClub').setValue(true)
    await wrapper.vm.$nextTick()
    await wrapper.find('#clubAffiliationForeign').setValue('Test Club')

    // Do NOT check consent boxes
    // Submit form
    await wrapper.find('form').trigger('submit.prevent')
    await wrapper.vm.$nextTick()

    // Should show error message
    const errorAlert = wrapper.find('.alert-error')
    expect(errorAlert.exists()).toBe(true)
    expect(errorAlert.text()).toContain('You must accept the Privacy Policy and Terms & Conditions')
  })

  it('should allow form submission with consent', async () => {
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    // Mock the authStore register method
    const mockRegister = vi.fn(() => Promise.resolve({ success: true }))
    
    const wrapper = mount(RegisterForm, {
      global: {
        plugins: [i18n, router, pinia],
        mocks: {
          $router: {
            push: vi.fn()
          }
        }
      }
    })

    // Mock the authStore
    const authStore = wrapper.vm.$pinia._s.get('auth')
    if (authStore) {
      authStore.register = mockRegister
    }

    await wrapper.vm.$nextTick()

    // Fill in required fields
    await wrapper.find('#email').setValue('test@example.com')
    await wrapper.find('#password').setValue('TestPass123!')
    await wrapper.find('#firstName').setValue('John')
    await wrapper.find('#lastName').setValue('Doe')
    await wrapper.find('#mobileNumber').setValue('+33612345678')
    
    // Check foreign club checkbox to enable free text input
    await wrapper.find('#foreignClub').setValue(true)
    await wrapper.vm.$nextTick()
    await wrapper.find('#clubAffiliationForeign').setValue('Test Club')

    // Check BOTH consent boxes
    await wrapper.find('#privacyConsent').setValue(true)
    await wrapper.find('#termsConsent').setValue(true)
    await wrapper.vm.$nextTick()

    // Submit form
    await wrapper.find('form').trigger('submit.prevent')
    await wrapper.vm.$nextTick()

    // Wait for async operations
    await new Promise(resolve => setTimeout(resolve, 100))

    // Should NOT show error message
    const errorAlert = wrapper.find('.alert-error')
    expect(errorAlert.exists()).toBe(false)
  })

  it('should include consent data in registration request', async () => {
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    // Mock the authStore register method to capture the data
    let capturedData = null
    const mockRegister = vi.fn((data) => {
      capturedData = data
      return Promise.resolve({ success: true })
    })
    
    const wrapper = mount(RegisterForm, {
      global: {
        plugins: [i18n, router, pinia]
      }
    })

    // Mock the authStore
    const authStore = wrapper.vm.$pinia._s.get('auth')
    if (authStore) {
      authStore.register = mockRegister
    }

    await wrapper.vm.$nextTick()

    // Fill in required fields
    await wrapper.find('#email').setValue('test@example.com')
    await wrapper.find('#password').setValue('TestPass123!')
    await wrapper.find('#firstName').setValue('John')
    await wrapper.find('#lastName').setValue('Doe')
    await wrapper.find('#mobileNumber').setValue('+33612345678')
    
    // Check foreign club checkbox
    await wrapper.find('#foreignClub').setValue(true)
    await wrapper.vm.$nextTick()
    await wrapper.find('#clubAffiliationForeign').setValue('Test Club')

    // Check consent boxes
    await wrapper.find('#privacyConsent').setValue(true)
    await wrapper.find('#termsConsent').setValue(true)
    await wrapper.vm.$nextTick()

    // Submit form
    await wrapper.find('form').trigger('submit.prevent')
    await wrapper.vm.$nextTick()

    // Wait for async operations
    await new Promise(resolve => setTimeout(resolve, 100))

    // Check that register was called with consent data
    expect(mockRegister).toHaveBeenCalled()
    expect(capturedData).toBeTruthy()
    expect(capturedData.privacy_consent).toBe(true)
    expect(capturedData.terms_consent).toBe(true)
    expect(capturedData.consent_version).toBe('1.0')
  })

  it('should block submission if only privacy consent is checked', async () => {
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(RegisterForm, {
      global: {
        plugins: [i18n, router, pinia]
      }
    })

    await wrapper.vm.$nextTick()

    // Fill in required fields
    await wrapper.find('#email').setValue('test@example.com')
    await wrapper.find('#password').setValue('TestPass123!')
    await wrapper.find('#firstName').setValue('John')
    await wrapper.find('#lastName').setValue('Doe')
    await wrapper.find('#mobileNumber').setValue('+33612345678')
    
    // Check foreign club checkbox
    await wrapper.find('#foreignClub').setValue(true)
    await wrapper.vm.$nextTick()
    await wrapper.find('#clubAffiliationForeign').setValue('Test Club')

    // Check ONLY privacy consent
    await wrapper.find('#privacyConsent').setValue(true)
    await wrapper.vm.$nextTick()

    // Submit form
    await wrapper.find('form').trigger('submit.prevent')
    await wrapper.vm.$nextTick()

    // Should show error message
    const errorAlert = wrapper.find('.alert-error')
    expect(errorAlert.exists()).toBe(true)
    expect(errorAlert.text()).toContain('You must accept the Privacy Policy and Terms & Conditions')
  })

  it('should block submission if only terms consent is checked', async () => {
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(RegisterForm, {
      global: {
        plugins: [i18n, router, pinia]
      }
    })

    await wrapper.vm.$nextTick()

    // Fill in required fields
    await wrapper.find('#email').setValue('test@example.com')
    await wrapper.find('#password').setValue('TestPass123!')
    await wrapper.find('#firstName').setValue('John')
    await wrapper.find('#lastName').setValue('Doe')
    await wrapper.find('#mobileNumber').setValue('+33612345678')
    
    // Check foreign club checkbox
    await wrapper.find('#foreignClub').setValue(true)
    await wrapper.vm.$nextTick()
    await wrapper.find('#clubAffiliationForeign').setValue('Test Club')

    // Check ONLY terms consent
    await wrapper.find('#termsConsent').setValue(true)
    await wrapper.vm.$nextTick()

    // Submit form
    await wrapper.find('form').trigger('submit.prevent')
    await wrapper.vm.$nextTick()

    // Should show error message
    const errorAlert = wrapper.find('.alert-error')
    expect(errorAlert.exists()).toBe(true)
    expect(errorAlert.text()).toContain('You must accept the Privacy Policy and Terms & Conditions')
  })

  it('should render consent section in French', async () => {
    const i18n = createI18nInstance('fr')
    const router = createRouterInstance()
    
    const wrapper = mount(RegisterForm, {
      global: {
        plugins: [i18n, router, pinia]
      }
    })

    await wrapper.vm.$nextTick()

    // Check French text is present
    const consentLabels = wrapper.findAll('.consent-label')
    expect(consentLabels.length).toBeGreaterThan(0)
    
    // Check for French privacy policy link text
    const privacyLink = wrapper.findAllComponents({ name: 'RouterLink' })
      .find(link => link.props('to') === '/privacy-policy')
    expect(privacyLink.text()).toBe('Politique de confidentialité')
    
    // Check for French terms link text
    const termsLink = wrapper.findAllComponents({ name: 'RouterLink' })
      .find(link => link.props('to') === '/terms-conditions')
    expect(termsLink.text()).toBe('Conditions générales')
  })
})
