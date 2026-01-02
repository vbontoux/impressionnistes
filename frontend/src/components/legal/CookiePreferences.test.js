/**
 * Tests for Cookie Preferences Modal Component
 * Ensures the modal opens/closes correctly and manages cookie preferences
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import CookiePreferences from './CookiePreferences.vue'
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

describe('CookiePreferences.vue', () => {
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

  it('should open when isOpen prop is true', async () => {
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.find('.modal-overlay').exists()).toBe(true)
    expect(wrapper.find('.modal-container').exists()).toBe(true)
    expect(wrapper.text()).toContain('Manage Cookie Preferences')
  })

  it('should not render when isOpen prop is false', async () => {
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: false
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.find('.modal-overlay').exists()).toBe(false)
  })

  it('should close when close button is clicked', async () => {
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    // Click close button
    const closeButton = wrapper.find('.close-button')
    await closeButton.trigger('click')

    // Check event was emitted
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should close when overlay is clicked', async () => {
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    // Click overlay (not the modal container)
    const overlay = wrapper.find('.modal-overlay')
    await overlay.trigger('click.self')

    // Check event was emitted
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should close when cancel button is clicked', async () => {
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    // Click cancel button
    const cancelButton = wrapper.find('.btn-secondary')
    await cancelButton.trigger('click')

    // Check event was emitted
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should have essential cookies always enabled and disabled toggle', async () => {
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    // Find all toggle switches
    const toggles = wrapper.findAll('.toggle-switch input[type="checkbox"]')
    
    // First toggle should be essential cookies (checked and disabled)
    expect(toggles[0].element.checked).toBe(true)
    expect(toggles[0].element.disabled).toBe(true)
    
    // Check for "Always enabled" label
    expect(wrapper.text()).toContain('Always enabled')
  })

  it('should allow toggling analytics cookies', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    // Find analytics toggle (second checkbox)
    const toggles = wrapper.findAll('.toggle-switch input[type="checkbox"]')
    const analyticsToggle = toggles[1]
    
    // Initially should be unchecked
    expect(analyticsToggle.element.checked).toBe(false)
    
    // Toggle it
    await analyticsToggle.setValue(true)
    
    // Should now be checked
    expect(analyticsToggle.element.checked).toBe(true)
  })

  it('should allow toggling marketing cookies', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    // Find marketing toggle (third checkbox)
    const toggles = wrapper.findAll('.toggle-switch input[type="checkbox"]')
    const marketingToggle = toggles[2]
    
    // Initially should be unchecked
    expect(marketingToggle.element.checked).toBe(false)
    
    // Toggle it
    await marketingToggle.setValue(true)
    
    // Should now be checked
    expect(marketingToggle.element.checked).toBe(true)
  })

  it('should save preferences to localStorage when save button is clicked', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    // Toggle analytics on
    const toggles = wrapper.findAll('.toggle-switch input[type="checkbox"]')
    await toggles[1].setValue(true)

    // Click save button
    const saveButton = wrapper.find('.btn-primary')
    await saveButton.trigger('click')

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
      expect.stringContaining('"marketing":false')
    )
  })

  it('should include timestamp and version when saving', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    // Click save button
    const saveButton = wrapper.find('.btn-primary')
    await saveButton.trigger('click')

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

  it('should emit preferences-changed event when saving', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    // Toggle analytics on
    const toggles = wrapper.findAll('.toggle-switch input[type="checkbox"]')
    await toggles[1].setValue(true)

    // Click save button
    const saveButton = wrapper.find('.btn-primary')
    await saveButton.trigger('click')

    // Check event was emitted
    expect(wrapper.emitted('preferences-changed')).toBeTruthy()
    expect(wrapper.emitted('preferences-changed')[0][0]).toMatchObject({
      essential: true,
      analytics: true,
      marketing: false,
      version: '1.0'
    })
  })

  it('should emit close event after saving', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    // Click save button
    const saveButton = wrapper.find('.btn-primary')
    await saveButton.trigger('click')

    // Check close event was emitted
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should load existing preferences from localStorage when opened', async () => {
    const existingConsent = JSON.stringify({
      essential: true,
      analytics: true,
      marketing: false,
      timestamp: '2025-01-02T10:00:00Z',
      version: '1.0'
    })
    localStorageMock.getItem.mockReturnValue(existingConsent)
    
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    // Wait for watcher to execute and component to update
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()

    // Check toggles reflect loaded preferences
    const toggles = wrapper.findAll('.toggle-switch input[type="checkbox"]')
    
    // Essential (always true)
    expect(toggles[0].element.checked).toBe(true)
    // Analytics (loaded as true)
    expect(toggles[1].element.checked).toBe(true)
    // Marketing (loaded as false)
    expect(toggles[2].element.checked).toBe(false)
  })

  it('should handle localStorage read errors gracefully', async () => {
    localStorageMock.getItem.mockImplementation(() => {
      throw new Error('localStorage error')
    })
    
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    const i18n = createI18nInstance('en')
    
    // Start with modal closed, then open it to trigger the watcher
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: false
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    // Now open the modal to trigger loadPreferences
    await wrapper.setProps({ isOpen: true })
    await wrapper.vm.$nextTick()

    // Modal should still render with default values
    expect(wrapper.find('.modal-overlay').exists()).toBe(true)
    
    const toggles = wrapper.findAll('.toggle-switch input[type="checkbox"]')
    expect(toggles[1].element.checked).toBe(false) // Analytics default
    expect(toggles[2].element.checked).toBe(false) // Marketing default
    
    expect(consoleSpy).toHaveBeenCalled()
    consoleSpy.mockRestore()
  })

  it('should handle localStorage write errors gracefully', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    localStorageMock.setItem.mockImplementation(() => {
      throw new Error('localStorage error')
    })
    
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    // Click save button
    const saveButton = wrapper.find('.btn-primary')
    await saveButton.trigger('click')

    // Should log error but not crash
    expect(consoleSpy).toHaveBeenCalled()
    consoleSpy.mockRestore()
  })

  it('should render in French', async () => {
    const i18n = createI18nInstance('fr')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Gérer les préférences des cookies')
    expect(wrapper.text()).toContain('Cookies essentiels')
    expect(wrapper.text()).toContain('Cookies analytiques')
    expect(wrapper.text()).toContain('Cookies marketing')
    expect(wrapper.find('.btn-primary').text()).toBe('Enregistrer les préférences')
    expect(wrapper.find('.btn-secondary').text()).toBe('Annuler')
  })

  it('should display all three cookie categories', async () => {
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Essential Cookies')
    expect(wrapper.text()).toContain('Analytics Cookies')
    expect(wrapper.text()).toContain('Marketing Cookies')
    
    // Check descriptions
    expect(wrapper.text()).toContain('Required for the website to function properly')
    expect(wrapper.text()).toContain('Help us understand how visitors use our website')
    expect(wrapper.text()).toContain('Used to deliver personalized advertisements')
  })

  it('should have proper ARIA attributes for accessibility', async () => {
    const i18n = createI18nInstance('en')
    
    const wrapper = mount(CookiePreferences, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [i18n]
      }
    })

    await wrapper.vm.$nextTick()

    const modalContainer = wrapper.find('.modal-container')
    expect(modalContainer.attributes('role')).toBe('dialog')
    expect(modalContainer.attributes('aria-labelledby')).toBe('modal-title')
    expect(modalContainer.attributes('aria-modal')).toBe('true')
    
    const closeButton = wrapper.find('.close-button')
    expect(closeButton.attributes('aria-label')).toBe('Close')
  })
})
