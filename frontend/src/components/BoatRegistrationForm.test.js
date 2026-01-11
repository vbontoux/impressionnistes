/**
 * Tests for BoatRegistrationForm Component
 * Ensures boat request fields render correctly and handle user interactions
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createPinia, setActivePinia } from 'pinia'
import BoatRegistrationForm from './BoatRegistrationForm.vue'
import { useBoatStore } from '@/stores/boatStore'
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

describe('BoatRegistrationForm.vue - Boat Request Feature', () => {
  let pinia
  let boatStore

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    boatStore = useBoatStore()
    
    // Mock the createBoatRegistration method
    boatStore.createBoatRegistration = vi.fn(() => Promise.resolve({
      boat_registration_id: 'test-id',
      event_type: '21km',
      boat_type: '4+',
      boat_request_enabled: false
    }))
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Boat Request Toggle', () => {
    it('should show boat request fields when toggle is enabled', async () => {
      const i18n = createI18nInstance('en')
      const wrapper = mount(BoatRegistrationForm, {
        global: {
          plugins: [i18n, pinia]
        }
      })

      // Select event type and boat type to show boat request section
      await wrapper.find('#event_type').setValue('21km')
      await wrapper.vm.$nextTick()
      await wrapper.find('#boat_type').setValue('4+')
      await wrapper.vm.$nextTick()

      // Initially, boat request fields should not be visible
      expect(wrapper.find('.boat-request-fields').exists()).toBe(false)

      // Enable boat request
      const checkbox = wrapper.find('input[type="checkbox"]')
      await checkbox.setValue(true)
      await wrapper.vm.$nextTick()

      // Boat request fields should now be visible
      expect(wrapper.find('.boat-request-fields').exists()).toBe(true)
      expect(wrapper.find('#boat_request_comment').exists()).toBe(true)
      expect(wrapper.find('.read-only').exists()).toBe(true)
    })

    it('should hide boat request fields when toggle is disabled', async () => {
      const i18n = createI18nInstance('en')
      const wrapper = mount(BoatRegistrationForm, {
        global: {
          plugins: [i18n, pinia]
        }
      })

      // Select event type and boat type
      await wrapper.find('#event_type').setValue('21km')
      await wrapper.vm.$nextTick()
      await wrapper.find('#boat_type').setValue('4+')
      await wrapper.vm.$nextTick()

      // Enable boat request
      const checkbox = wrapper.find('input[type="checkbox"]')
      await checkbox.setValue(true)
      await wrapper.vm.$nextTick()

      // Fields should be visible
      expect(wrapper.find('.boat-request-fields').exists()).toBe(true)

      // Disable boat request
      await checkbox.setValue(false)
      await wrapper.vm.$nextTick()

      // Fields should be hidden
      expect(wrapper.find('.boat-request-fields').exists()).toBe(false)
    })

    it('should not show boat request section before boat type is selected', async () => {
      const i18n = createI18nInstance('en')
      const wrapper = mount(BoatRegistrationForm, {
        global: {
          plugins: [i18n, pinia]
        }
      })

      // Select only event type
      await wrapper.find('#event_type').setValue('21km')
      await wrapper.vm.$nextTick()

      // Boat request section should not be visible
      expect(wrapper.find('.boat-request-section').exists()).toBe(false)
    })
  })

  describe('Character Counter', () => {
    it('should display character count for boat request comment', async () => {
      const i18n = createI18nInstance('en')
      const wrapper = mount(BoatRegistrationForm, {
        global: {
          plugins: [i18n, pinia]
        }
      })

      // Setup form
      await wrapper.find('#event_type').setValue('21km')
      await wrapper.find('#boat_type').setValue('4+')
      const checkbox = wrapper.find('input[type="checkbox"]')
      await checkbox.setValue(true)
      await wrapper.vm.$nextTick()

      // Initially should show 0 / 500
      expect(wrapper.find('.char-count').text()).toBe('0 / 500')

      // Type some text
      const textarea = wrapper.find('#boat_request_comment')
      await textarea.setValue('Test comment')
      await wrapper.vm.$nextTick()

      // Should update character count
      expect(wrapper.find('.char-count').text()).toBe('12 / 500')
    })

    it('should enforce 500 character limit on textarea', async () => {
      const i18n = createI18nInstance('en')
      const wrapper = mount(BoatRegistrationForm, {
        global: {
          plugins: [i18n, pinia]
        }
      })

      // Setup form
      await wrapper.find('#event_type').setValue('21km')
      await wrapper.find('#boat_type').setValue('4+')
      const checkbox = wrapper.find('input[type="checkbox"]')
      await checkbox.setValue(true)
      await wrapper.vm.$nextTick()

      // Check textarea has maxlength attribute
      const textarea = wrapper.find('#boat_request_comment')
      expect(textarea.attributes('maxlength')).toBe('500')
    })
  })

  describe('Field Clearing on Disable', () => {
    it('should clear boat request comment when disabling boat request', async () => {
      const i18n = createI18nInstance('en')
      const wrapper = mount(BoatRegistrationForm, {
        global: {
          plugins: [i18n, pinia]
        }
      })

      // Setup form
      await wrapper.find('#event_type').setValue('21km')
      await wrapper.find('#boat_type').setValue('4+')
      const checkbox = wrapper.find('input[type="checkbox"]')
      await checkbox.setValue(true)
      await wrapper.vm.$nextTick()

      // Enter comment
      const textarea = wrapper.find('#boat_request_comment')
      await textarea.setValue('Test comment that should be cleared')
      await wrapper.vm.$nextTick()

      // Verify comment is set
      expect(wrapper.vm.formData.boat_request_comment).toBe('Test comment that should be cleared')

      // Disable boat request
      await checkbox.setValue(false)
      await wrapper.vm.$nextTick()

      // Comment should be cleared
      expect(wrapper.vm.formData.boat_request_comment).toBe('')
    })
  })

  describe('Read-Only Fields', () => {
    it('should display assigned boat field as read-only', async () => {
      const i18n = createI18nInstance('en')
      const wrapper = mount(BoatRegistrationForm, {
        global: {
          plugins: [i18n, pinia]
        }
      })

      // Setup form
      await wrapper.find('#event_type').setValue('21km')
      await wrapper.find('#boat_type').setValue('4+')
      const checkbox = wrapper.find('input[type="checkbox"]')
      await checkbox.setValue(true)
      await wrapper.vm.$nextTick()

      // Find assigned boat field
      const assignedBoatField = wrapper.find('.read-only')
      
      // Should be disabled
      expect(assignedBoatField.attributes('disabled')).toBeDefined()
      
      // Should have read-only class
      expect(assignedBoatField.classes()).toContain('read-only')
    })

    it('should show "Not yet assigned" when no boat is assigned', async () => {
      const i18n = createI18nInstance('en')
      const wrapper = mount(BoatRegistrationForm, {
        global: {
          plugins: [i18n, pinia]
        }
      })

      // Setup form
      await wrapper.find('#event_type').setValue('21km')
      await wrapper.find('#boat_type').setValue('4+')
      const checkbox = wrapper.find('input[type="checkbox"]')
      await checkbox.setValue(true)
      await wrapper.vm.$nextTick()

      // Assigned boat field should show placeholder
      const assignedBoatField = wrapper.find('.read-only')
      expect(assignedBoatField.element.value).toBe('Not yet assigned')
    })

    it('should not display assigned boat comment section when no comment exists', async () => {
      const i18n = createI18nInstance('en')
      const wrapper = mount(BoatRegistrationForm, {
        global: {
          plugins: [i18n, pinia]
        }
      })

      // Setup form
      await wrapper.find('#event_type').setValue('21km')
      await wrapper.find('#boat_type').setValue('4+')
      const checkbox = wrapper.find('input[type="checkbox"]')
      await checkbox.setValue(true)
      await wrapper.vm.$nextTick()

      // Assigned comment section should not exist
      expect(wrapper.find('.assigned-comment').exists()).toBe(false)
    })

    it('should display assigned boat comment when it exists', async () => {
      const i18n = createI18nInstance('en')
      const wrapper = mount(BoatRegistrationForm, {
        global: {
          plugins: [i18n, pinia]
        }
      })

      // Setup form
      await wrapper.find('#event_type').setValue('21km')
      await wrapper.find('#boat_type').setValue('4+')
      const checkbox = wrapper.find('input[type="checkbox"]')
      await checkbox.setValue(true)
      await wrapper.vm.$nextTick()

      // Manually set assigned boat comment (simulating data from backend)
      wrapper.vm.formData.assigned_boat_comment = 'Boat is in rack 3, oars in locker B'
      await wrapper.vm.$nextTick()

      // Assigned comment section should exist and display the comment
      expect(wrapper.find('.assigned-comment').exists()).toBe(true)
      expect(wrapper.find('.assigned-comment').text()).toBe('Boat is in rack 3, oars in locker B')
    })
  })

  describe('Form Submission', () => {
    it('should include boat request fields in submission payload', async () => {
      const i18n = createI18nInstance('en')
      const wrapper = mount(BoatRegistrationForm, {
        global: {
          plugins: [i18n, pinia]
        }
      })

      // Setup form
      await wrapper.find('#event_type').setValue('21km')
      await wrapper.find('#boat_type').setValue('4+')
      const checkbox = wrapper.find('input[type="checkbox"]')
      await checkbox.setValue(true)
      await wrapper.vm.$nextTick()

      // Enter comment
      const textarea = wrapper.find('#boat_request_comment')
      await textarea.setValue('Need beginner-friendly boat')
      await wrapper.vm.$nextTick()

      // Submit form
      await wrapper.find('form').trigger('submit.prevent')
      await wrapper.vm.$nextTick()

      // Check that createBoatRegistration was called with correct payload
      expect(boatStore.createBoatRegistration).toHaveBeenCalledWith({
        event_type: '21km',
        boat_type: '4+',
        boat_request_enabled: true,
        boat_request_comment: 'Need beginner-friendly boat'
      })
    })

    it('should not include assigned boat fields in submission payload', async () => {
      const i18n = createI18nInstance('en')
      const wrapper = mount(BoatRegistrationForm, {
        global: {
          plugins: [i18n, pinia]
        }
      })

      // Setup form
      await wrapper.find('#event_type').setValue('21km')
      await wrapper.find('#boat_type').setValue('4+')
      const checkbox = wrapper.find('input[type="checkbox"]')
      await checkbox.setValue(true)
      await wrapper.vm.$nextTick()

      // Manually set assigned boat fields (simulating data from backend)
      wrapper.vm.formData.assigned_boat_identifier = 'Boat 42'
      wrapper.vm.formData.assigned_boat_comment = 'Test comment'
      await wrapper.vm.$nextTick()

      // Submit form
      await wrapper.find('form').trigger('submit.prevent')
      await wrapper.vm.$nextTick()

      // Check that payload does NOT include assigned boat fields
      const callArgs = boatStore.createBoatRegistration.mock.calls[0][0]
      expect(callArgs).not.toHaveProperty('assigned_boat_identifier')
      expect(callArgs).not.toHaveProperty('assigned_boat_comment')
    })

    it('should submit with boat_request_enabled=false when not checked', async () => {
      const i18n = createI18nInstance('en')
      const wrapper = mount(BoatRegistrationForm, {
        global: {
          plugins: [i18n, pinia]
        }
      })

      // Setup form without enabling boat request
      await wrapper.find('#event_type').setValue('21km')
      await wrapper.find('#boat_type').setValue('4+')
      await wrapper.vm.$nextTick()

      // Submit form
      await wrapper.find('form').trigger('submit.prevent')
      await wrapper.vm.$nextTick()

      // Check that boat_request_enabled is false
      expect(boatStore.createBoatRegistration).toHaveBeenCalledWith({
        event_type: '21km',
        boat_type: '4+',
        boat_request_enabled: false,
        boat_request_comment: ''
      })
    })
  })

  describe('Translations', () => {
    it('should display English translations', async () => {
      const i18n = createI18nInstance('en')
      const wrapper = mount(BoatRegistrationForm, {
        global: {
          plugins: [i18n, pinia]
        }
      })

      // Setup form
      await wrapper.find('#event_type').setValue('21km')
      await wrapper.find('#boat_type').setValue('4+')
      await wrapper.vm.$nextTick()

      // Check English translations
      expect(wrapper.text()).toContain('Boat Request')
      expect(wrapper.text()).toContain('Request boat assignment from organizers')
    })

    it('should display French translations', async () => {
      const i18n = createI18nInstance('fr')
      const wrapper = mount(BoatRegistrationForm, {
        global: {
          plugins: [i18n, pinia]
        }
      })

      // Setup form
      await wrapper.find('#event_type').setValue('21km')
      await wrapper.find('#boat_type').setValue('4+')
      await wrapper.vm.$nextTick()

      // Check French translations
      expect(wrapper.text()).toContain('Demande de bateau')
      expect(wrapper.text()).toContain("Demander l'attribution d'un bateau par les organisateurs")
    })
  })
})
