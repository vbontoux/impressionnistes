/**
 * Tests for Cookie Banner Component
 * Ensures the banner appears correctly and handles consent preferences
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import CookieBanner from './CookieBanner.vue'
import en from '../../locales/en.json'
import fr from '../../locales/fr.json'

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
      { path: '/privacy-policy', component: { template: '<div>Privacy Policy</div>' } }
    ]
  })
}

describe('CookieBanner.vue', () => {
  let localStorageMock

  beforeEach(() => {
    // Mock localStorage
    localStorageMock = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn()
    }
    global.localStorage = localStorageMock
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should appear when no preference exists', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(CookieBanner, {
      global: {
        plugins: [i18n, router]
      }
    })

    // Wait for component to mount
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.cookie-banner').exists()).toBe(true)
    expect(wrapper.text()).toContain('We use cookies to improve your experience')
  })

  it('should not appear when preference exists', async () => {
    const existingConsent = JSON.stringify({
      essential: true,
      analytics: false,
      marketing: false,
      timestamp: '2025-01-02T10:00:00Z',
      version: '1.0'
    })
    localStorageMock.getItem.mockReturnValue(existingConsent)
    
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(CookieBanner, {
      global: {
        plugins: [i18n, router]
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.find('.cookie-banner').exists()).toBe(false)
  })

  it('should set all preferences to true when "Accept All" is clicked', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(CookieBanner, {
      global: {
        plugins: [i18n, router]
      }
    })

    await wrapper.vm.$nextTick()

    // Click "Accept All" button
    const acceptButton = wrapper.find('.btn-primary')
    await acceptButton.trigger('click')

    // Check localStorage was called
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'cookie-consent',
      expect.stringContaining('"essential":true')
    )
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'cookie-consent',
      expect.stringContaining('"analytics":true')
    )
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'cookie-consent',
      expect.stringContaining('"marketing":true')
    )

    // Banner should be hidden
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.cookie-banner').exists()).toBe(false)
  })

  it('should set non-essential to false when "Reject All" is clicked', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(CookieBanner, {
      global: {
        plugins: [i18n, router]
      }
    })

    await wrapper.vm.$nextTick()

    // Click "Reject All" button
    const rejectButton = wrapper.findAll('.btn-secondary')[0]
    await rejectButton.trigger('click')

    // Check localStorage was called with correct values
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'cookie-consent',
      expect.stringContaining('"essential":true')
    )
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'cookie-consent',
      expect.stringContaining('"analytics":false')
    )
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'cookie-consent',
      expect.stringContaining('"marketing":false')
    )

    // Banner should be hidden
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.cookie-banner').exists()).toBe(false)
  })

  it('should update localStorage correctly with timestamp and version', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(CookieBanner, {
      global: {
        plugins: [i18n, router]
      }
    })

    await wrapper.vm.$nextTick()

    // Click "Accept All" button
    const acceptButton = wrapper.find('.btn-primary')
    await acceptButton.trigger('click')

    // Check localStorage was called with timestamp and version
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'cookie-consent',
      expect.stringContaining('"timestamp"')
    )
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'cookie-consent',
      expect.stringContaining('"version":"1.0"')
    )
  })

  it('should emit consent-changed event when preferences are saved', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(CookieBanner, {
      global: {
        plugins: [i18n, router]
      }
    })

    await wrapper.vm.$nextTick()

    // Click "Accept All" button
    const acceptButton = wrapper.find('.btn-primary')
    await acceptButton.trigger('click')

    // Check event was emitted
    expect(wrapper.emitted('consent-changed')).toBeTruthy()
    expect(wrapper.emitted('consent-changed')[0][0]).toMatchObject({
      essential: true,
      analytics: true,
      marketing: true,
      version: '1.0'
    })
  })

  it('should emit customize event when "Customize" is clicked', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(CookieBanner, {
      global: {
        plugins: [i18n, router]
      }
    })

    await wrapper.vm.$nextTick()

    // Click "Customize" button
    const customizeButton = wrapper.findAll('.btn-secondary')[1]
    await customizeButton.trigger('click')

    // Check event was emitted
    expect(wrapper.emitted('customize')).toBeTruthy()

    // Banner should be hidden
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.cookie-banner').exists()).toBe(false)
  })

  it('should handle localStorage errors gracefully', async () => {
    localStorageMock.getItem.mockImplementation(() => {
      throw new Error('localStorage error')
    })
    
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(CookieBanner, {
      global: {
        plugins: [i18n, router]
      }
    })

    await wrapper.vm.$nextTick()

    // Banner should still appear (default to no consent)
    expect(wrapper.find('.cookie-banner').exists()).toBe(true)
    expect(consoleSpy).toHaveBeenCalled()
    
    consoleSpy.mockRestore()
  })

  it('should render in French', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const i18n = createI18nInstance('fr')
    const router = createRouterInstance()
    
    const wrapper = mount(CookieBanner, {
      global: {
        plugins: [i18n, router]
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Nous utilisons des cookies pour améliorer votre expérience')
    expect(wrapper.find('.btn-primary').text()).toBe('Tout accepter')
    expect(wrapper.findAll('.btn-secondary')[0].text()).toBe('Tout refuser')
  })
})
