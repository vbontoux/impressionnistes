import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LoadingSpinner from './LoadingSpinner.vue'

describe('LoadingSpinner', () => {
  it('renders with default props', () => {
    const wrapper = mount(LoadingSpinner)
    expect(wrapper.find('.loading-spinner').exists()).toBe(true)
    expect(wrapper.find('.loading-spinner--medium').exists()).toBe(true)
  })

  it('renders with small size', () => {
    const wrapper = mount(LoadingSpinner, {
      props: { size: 'small' }
    })
    expect(wrapper.find('.loading-spinner--small').exists()).toBe(true)
  })

  it('renders with large size', () => {
    const wrapper = mount(LoadingSpinner, {
      props: { size: 'large' }
    })
    expect(wrapper.find('.loading-spinner--large').exists()).toBe(true)
  })

  it('renders message when provided', () => {
    const message = 'Loading boats...'
    const wrapper = mount(LoadingSpinner, {
      props: { message }
    })
    expect(wrapper.find('.loading-message').exists()).toBe(true)
    expect(wrapper.find('.loading-message').text()).toBe(message)
  })

  it('does not render message when not provided', () => {
    const wrapper = mount(LoadingSpinner)
    expect(wrapper.find('.loading-message').exists()).toBe(false)
  })

  it('has proper accessibility attributes', () => {
    const wrapper = mount(LoadingSpinner)
    const spinner = wrapper.find('.loading-spinner')
    expect(spinner.attributes('role')).toBe('status')
    expect(spinner.attributes('aria-live')).toBe('polite')
  })

  it('validates size prop', () => {
    const validator = LoadingSpinner.props.size.validator
    expect(validator('small')).toBe(true)
    expect(validator('medium')).toBe(true)
    expect(validator('large')).toBe(true)
    expect(validator('invalid')).toBe(false)
  })
})
