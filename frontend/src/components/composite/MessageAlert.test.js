/**
 * MessageAlert Component Tests
 * 
 * Basic tests to verify the MessageAlert component functionality.
 * These tests verify the component renders correctly with different props.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import MessageAlert from './MessageAlert.vue'

describe('MessageAlert Component', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('Basic Rendering', () => {
    it('renders with default props', () => {
      wrapper = mount(MessageAlert, {
        props: {
          message: 'Test message'
        }
      })

      expect(wrapper.find('.message-alert').exists()).toBe(true)
      expect(wrapper.text()).toContain('Test message')
    })

    it('renders with error type', () => {
      wrapper = mount(MessageAlert, {
        props: {
          type: 'error',
          message: 'Error message'
        }
      })

      expect(wrapper.find('.message-alert--error').exists()).toBe(true)
      expect(wrapper.text()).toContain('Error message')
    })

    it('renders with success type', () => {
      wrapper = mount(MessageAlert, {
        props: {
          type: 'success',
          message: 'Success message'
        }
      })

      expect(wrapper.find('.message-alert--success').exists()).toBe(true)
      expect(wrapper.text()).toContain('Success message')
    })

    it('renders with warning type', () => {
      wrapper = mount(MessageAlert, {
        props: {
          type: 'warning',
          message: 'Warning message'
        }
      })

      expect(wrapper.find('.message-alert--warning').exists()).toBe(true)
      expect(wrapper.text()).toContain('Warning message')
    })

    it('renders with info type', () => {
      wrapper = mount(MessageAlert, {
        props: {
          type: 'info',
          message: 'Info message'
        }
      })

      expect(wrapper.find('.message-alert--info').exists()).toBe(true)
      expect(wrapper.text()).toContain('Info message')
    })
  })

  describe('Dismissible Functionality', () => {
    it('shows close button when dismissible is true', () => {
      wrapper = mount(MessageAlert, {
        props: {
          message: 'Test message',
          dismissible: true
        }
      })

      expect(wrapper.find('.message-alert__close').exists()).toBe(true)
    })

    it('hides close button when dismissible is false', () => {
      wrapper = mount(MessageAlert, {
        props: {
          message: 'Test message',
          dismissible: false
        }
      })

      expect(wrapper.find('.message-alert__close').exists()).toBe(false)
    })

    it('emits dismiss event when close button is clicked', async () => {
      wrapper = mount(MessageAlert, {
        props: {
          message: 'Test message',
          dismissible: true
        }
      })

      await wrapper.find('.message-alert__close').trigger('click')
      expect(wrapper.emitted('dismiss')).toBeTruthy()
      expect(wrapper.emitted('dismiss')).toHaveLength(1)
    })

    it('hides alert when close button is clicked', async () => {
      wrapper = mount(MessageAlert, {
        props: {
          message: 'Test message',
          dismissible: true
        }
      })

      expect(wrapper.find('.message-alert').exists()).toBe(true)
      await wrapper.find('.message-alert__close').trigger('click')
      
      // Wait for transition
      await wrapper.vm.$nextTick()
      
      // Alert should be hidden (isVisible = false)
      expect(wrapper.vm.isVisible).toBe(false)
    })
  })

  describe('Auto-dismiss Functionality', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.restoreAllMocks()
    })

    it('does not auto-dismiss when autoDismiss is 0', () => {
      wrapper = mount(MessageAlert, {
        props: {
          message: 'Test message',
          autoDismiss: 0
        }
      })

      vi.advanceTimersByTime(5000)
      expect(wrapper.emitted('dismiss')).toBeFalsy()
    })

    it('auto-dismisses after specified time', async () => {
      wrapper = mount(MessageAlert, {
        props: {
          message: 'Test message',
          autoDismiss: 3000
        }
      })

      expect(wrapper.emitted('dismiss')).toBeFalsy()
      
      vi.advanceTimersByTime(3000)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.emitted('dismiss')).toBeTruthy()
      expect(wrapper.emitted('dismiss')).toHaveLength(1)
    })
  })

  describe('Icon Display', () => {
    it('displays error icon for error type', () => {
      wrapper = mount(MessageAlert, {
        props: {
          type: 'error',
          message: 'Error'
        }
      })

      expect(wrapper.find('.message-alert__icon').text()).toBe('✕')
    })

    it('displays success icon for success type', () => {
      wrapper = mount(MessageAlert, {
        props: {
          type: 'success',
          message: 'Success'
        }
      })

      expect(wrapper.find('.message-alert__icon').text()).toBe('✓')
    })

    it('displays warning icon for warning type', () => {
      wrapper = mount(MessageAlert, {
        props: {
          type: 'warning',
          message: 'Warning'
        }
      })

      expect(wrapper.find('.message-alert__icon').text()).toBe('⚠')
    })

    it('displays info icon for info type', () => {
      wrapper = mount(MessageAlert, {
        props: {
          type: 'info',
          message: 'Info'
        }
      })

      expect(wrapper.find('.message-alert__icon').text()).toBe('ℹ')
    })
  })

  describe('Accessibility', () => {
    it('has proper role attribute', () => {
      wrapper = mount(MessageAlert, {
        props: {
          message: 'Test message'
        }
      })

      expect(wrapper.find('.message-alert').attributes('role')).toBe('alert')
    })

    it('has assertive aria-live for error type', () => {
      wrapper = mount(MessageAlert, {
        props: {
          type: 'error',
          message: 'Error message'
        }
      })

      expect(wrapper.find('.message-alert').attributes('aria-live')).toBe('assertive')
    })

    it('has polite aria-live for non-error types', () => {
      wrapper = mount(MessageAlert, {
        props: {
          type: 'success',
          message: 'Success message'
        }
      })

      expect(wrapper.find('.message-alert').attributes('aria-live')).toBe('polite')
    })

    it('close button has aria-label', () => {
      wrapper = mount(MessageAlert, {
        props: {
          message: 'Test message',
          dismissible: true
        }
      })

      expect(wrapper.find('.message-alert__close').attributes('aria-label')).toBe('Close alert')
    })
  })
})
