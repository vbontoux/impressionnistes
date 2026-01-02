/**
 * Tests for Terms and Conditions Component
 * Ensures the component renders correctly in both languages
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import TermsConditions from './TermsConditions.vue'
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

describe('TermsConditions.vue', () => {
  it('should render in English', () => {
    const i18n = createI18nInstance('en')
    const wrapper = mount(TermsConditions, {
      global: {
        plugins: [i18n]
      }
    })

    expect(wrapper.find('h1').text()).toBe('Terms & Conditions')
    expect(wrapper.text()).toContain('Acceptance of Terms')
    expect(wrapper.text()).toContain('Service Description')
  })

  it('should render in French', () => {
    const i18n = createI18nInstance('fr')
    const wrapper = mount(TermsConditions, {
      global: {
        plugins: [i18n]
      }
    })

    expect(wrapper.find('h1').text()).toBe('Conditions générales')
    expect(wrapper.text()).toContain('Acceptation des conditions')
    expect(wrapper.text()).toContain('Description du service')
  })

  it('should display last updated date', () => {
    const i18n = createI18nInstance('en')
    const wrapper = mount(TermsConditions, {
      global: {
        plugins: [i18n]
      }
    })

    expect(wrapper.find('.last-updated').exists()).toBe(true)
    expect(wrapper.find('.last-updated').text()).toContain('2025-01-02')
  })

  it('should have responsive layout classes', () => {
    const i18n = createI18nInstance('en')
    const wrapper = mount(TermsConditions, {
      global: {
        plugins: [i18n]
      }
    })

    expect(wrapper.find('.terms-conditions-page').exists()).toBe(true)
    expect(wrapper.find('.terms-conditions-container').exists()).toBe(true)
    expect(wrapper.find('.policy-content').exists()).toBe(true)
  })
})
