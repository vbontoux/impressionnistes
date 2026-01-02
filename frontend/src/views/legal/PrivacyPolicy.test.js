/**
 * Tests for Privacy Policy Component
 * Ensures the component renders correctly in both languages
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import PrivacyPolicy from './PrivacyPolicy.vue'
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

describe('PrivacyPolicy.vue', () => {
  it('should render in English', () => {
    const i18n = createI18nInstance('en')
    const wrapper = mount(PrivacyPolicy, {
      global: {
        plugins: [i18n]
      }
    })

    expect(wrapper.find('h1').text()).toBe('Privacy Policy')
    expect(wrapper.text()).toContain('Data Controller')
    expect(wrapper.text()).toContain('Personal Data We Collect')
  })

  it('should render in French', () => {
    const i18n = createI18nInstance('fr')
    const wrapper = mount(PrivacyPolicy, {
      global: {
        plugins: [i18n]
      }
    })

    expect(wrapper.find('h1').text()).toBe('Politique de confidentialité')
    expect(wrapper.text()).toContain('Responsable du traitement')
    expect(wrapper.text()).toContain('Données personnelles collectées')
  })

  it('should display last updated date', () => {
    const i18n = createI18nInstance('en')
    const wrapper = mount(PrivacyPolicy, {
      global: {
        plugins: [i18n]
      }
    })

    expect(wrapper.find('.last-updated').exists()).toBe(true)
    expect(wrapper.find('.last-updated').text()).toContain('2025-01-02')
  })

  it('should have responsive layout classes', () => {
    const i18n = createI18nInstance('en')
    const wrapper = mount(PrivacyPolicy, {
      global: {
        plugins: [i18n]
      }
    })

    expect(wrapper.find('.privacy-policy-page').exists()).toBe(true)
    expect(wrapper.find('.privacy-policy-container').exists()).toBe(true)
    expect(wrapper.find('.policy-content').exists()).toBe(true)
  })
})
