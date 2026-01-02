/**
 * Tests for Footer Component
 * Ensures the footer displays correctly with all required links
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import Footer from './Footer.vue'
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
      { path: '/privacy-policy', component: { template: '<div>Privacy Policy</div>' } },
      { path: '/terms-conditions', component: { template: '<div>Terms</div>' } }
    ]
  })
}

describe('Footer.vue', () => {
  it('should render footer with all links', () => {
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(Footer, {
      global: {
        plugins: [i18n, router]
      }
    })

    expect(wrapper.find('.site-footer').exists()).toBe(true)
    expect(wrapper.find('.footer-content').exists()).toBe(true)
    expect(wrapper.find('.footer-links').exists()).toBe(true)
    expect(wrapper.find('.footer-copyright').exists()).toBe(true)
  })

  it('should display Privacy Policy link', () => {
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(Footer, {
      global: {
        plugins: [i18n, router]
      }
    })

    const privacyLink = wrapper.findAll('.footer-link')[0]
    expect(privacyLink.text()).toBe('Privacy Policy')
    // Router-link components have 'to' as a prop, not an attribute
    expect(privacyLink.element.getAttribute('href')).toBe('/privacy-policy')
  })

  it('should display Terms & Conditions link', () => {
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(Footer, {
      global: {
        plugins: [i18n, router]
      }
    })

    const termsLink = wrapper.findAll('.footer-link')[1]
    expect(termsLink.text()).toBe('Terms & Conditions')
    // Router-link components have 'to' as a prop, not an attribute
    expect(termsLink.element.getAttribute('href')).toBe('/terms-conditions')
  })

  it('should display Cookie Preferences link', () => {
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(Footer, {
      global: {
        plugins: [i18n, router]
      }
    })

    const cookieLink = wrapper.findAll('.footer-link')[2]
    expect(cookieLink.text()).toBe('Cookie Preferences')
    expect(cookieLink.attributes('href')).toBe('#')
  })

  it('should emit open-cookie-preferences event when cookie link is clicked', async () => {
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(Footer, {
      global: {
        plugins: [i18n, router]
      }
    })

    const cookieLink = wrapper.findAll('.footer-link')[2]
    await cookieLink.trigger('click')

    expect(wrapper.emitted('open-cookie-preferences')).toBeTruthy()
  })

  it('should display copyright notice with current year', () => {
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(Footer, {
      global: {
        plugins: [i18n, router]
      }
    })

    const currentYear = new Date().getFullYear()
    const copyright = wrapper.find('.footer-copyright')
    expect(copyright.text()).toContain(`© ${currentYear}`)
    expect(copyright.text()).toContain('Course des Impressionnistes')
  })

  it('should render in French', () => {
    const i18n = createI18nInstance('fr')
    const router = createRouterInstance()
    
    const wrapper = mount(Footer, {
      global: {
        plugins: [i18n, router]
      }
    })

    const privacyLink = wrapper.findAll('.footer-link')[0]
    expect(privacyLink.text()).toBe('Politique de confidentialité')

    const termsLink = wrapper.findAll('.footer-link')[1]
    expect(termsLink.text()).toBe('Conditions générales')

    const cookieLink = wrapper.findAll('.footer-link')[2]
    expect(cookieLink.text()).toBe('Préférences des cookies')
  })

  it('should have proper accessibility attributes', () => {
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(Footer, {
      global: {
        plugins: [i18n, router]
      }
    })

    // All links should have minimum touch target size (handled by CSS)
    const links = wrapper.findAll('.footer-link')
    expect(links.length).toBe(3)
    
    // Links should be keyboard accessible
    links.forEach(link => {
      expect(link.element.tagName).toMatch(/^(A|ROUTER-LINK)$/i)
    })
  })

  it('should apply with-sidebar class when prop is passed', () => {
    const i18n = createI18nInstance('en')
    const router = createRouterInstance()
    
    const wrapper = mount(Footer, {
      global: {
        plugins: [i18n, router]
      },
      attrs: {
        class: 'with-sidebar'
      }
    })

    expect(wrapper.classes()).toContain('with-sidebar')
  })
})
