/**
 * Tests for Payment View with Permission Checks
 * Validates: Requirements 8.9
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import Payment from './Payment.vue'
import { useAuthStore } from '@/stores/authStore'
import { usePaymentStore } from '@/stores/paymentStore'
import { useRaceStore } from '@/stores/raceStore'
import { clearPermissionCache } from '@/composables/usePermissions'
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

// Create router for testing
const createTestRouter = () => {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/payment', component: Payment },
      { path: '/payment/checkout', component: { template: '<div>Checkout</div>' } },
      { path: '/boats', component: { template: '<div>Boats</div>' } }
    ]
  })
}

// Mock permission service
vi.mock('@/services/permissionService', () => ({
  fetchCurrentPhase: vi.fn(() => Promise.resolve('during_registration')),
  fetchPermissionMatrix: vi.fn(() => Promise.resolve({
    process_payment: {
      before_registration: false,
      during_registration: true,
      after_registration: true,
      after_payment_deadline: false
    }
  })),
  getDefaultPermissionMatrix: vi.fn(() => ({
    process_payment: {
      before_registration: false,
      during_registration: true,
      after_registration: true,
      after_payment_deadline: false
    }
  }))
}))

describe('Payment.vue - Permission Checks', () => {
  let pinia
  let authStore
  let paymentStore
  let raceStore
  let router

  const mockBoats = [
    {
      boat_registration_id: 'boat1',
      boat_number: 'B001',
      event_type: 'C4x',
      boat_type: 'Yolette',
      registration_status: 'complete',
      payment_status: 'unpaid',
      total_price: 100.00
    },
    {
      boat_registration_id: 'boat2',
      boat_number: 'B002',
      event_type: 'C2x',
      boat_type: 'Yolette',
      registration_status: 'complete',
      payment_status: 'unpaid',
      total_price: 80.00
    }
  ]

  beforeEach(() => {
    // Clear permission cache before each test
    clearPermissionCache()
    
    // Mock localStorage
    const localStorageMock = {
      getItem: vi.fn(() => null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn()
    }
    global.localStorage = localStorageMock

    pinia = createPinia()
    setActivePinia(pinia)
    authStore = useAuthStore()
    paymentStore = usePaymentStore()
    raceStore = useRaceStore()
    router = createTestRouter()
    
    // Set up team manager user
    authStore.user = {
      user_id: 'tm1',
      email: 'manager@example.com',
      first_name: 'Manager',
      last_name: 'User',
      groups: []
    }

    // Mock payment store methods and properties
    paymentStore.fetchAllForPayment = vi.fn(() => Promise.resolve())
    paymentStore.boatsReadyForPayment = mockBoats
    paymentStore.setSelectedBoats = vi.fn()
    paymentStore.loading = false
    paymentStore.error = null

    // Mock race store methods
    raceStore.fetchRaces = vi.fn(() => Promise.resolve())
    raceStore.races = []
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should enable payment button during registration period', async () => {
    const { fetchCurrentPhase } = await import('@/services/permissionService')
    fetchCurrentPhase.mockResolvedValue('during_registration')

    const i18n = createI18nInstance('en')
    const wrapper = mount(Payment, {
      global: {
        plugins: [i18n, pinia, router]
      }
    })

    // Wait for permissions to initialize
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    // Payment button should be enabled (not disabled by permissions)
    const canProcessPayment = wrapper.vm.canProcessPayment
    expect(canProcessPayment).toBe(true)
  })

  it('should enable payment button after registration closes', async () => {
    const { fetchCurrentPhase } = await import('@/services/permissionService')
    fetchCurrentPhase.mockResolvedValue('after_registration')

    const i18n = createI18nInstance('en')
    const wrapper = mount(Payment, {
      global: {
        plugins: [i18n, pinia, router]
      }
    })

    // Wait for permissions to initialize
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    // Payment button should be enabled during after_registration phase
    const canProcessPayment = wrapper.vm.canProcessPayment
    expect(canProcessPayment).toBe(true)
  })

  it('should disable payment button after payment deadline', async () => {
    const { fetchCurrentPhase } = await import('@/services/permissionService')
    fetchCurrentPhase.mockResolvedValue('after_payment_deadline')

    const i18n = createI18nInstance('en')
    const wrapper = mount(Payment, {
      global: {
        plugins: [i18n, pinia, router]
      }
    })

    // Wait for permissions to initialize
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    // Payment button should be disabled after payment deadline
    const canProcessPayment = wrapper.vm.canProcessPayment
    expect(canProcessPayment).toBe(false)
  })

  it('should display permission message when payment is disabled', async () => {
    const { fetchCurrentPhase } = await import('@/services/permissionService')
    fetchCurrentPhase.mockResolvedValue('after_payment_deadline')

    const i18n = createI18nInstance('en')
    const wrapper = mount(Payment, {
      global: {
        plugins: [i18n, pinia, router]
      }
    })

    // Wait for permissions to initialize
    await new Promise(resolve => setTimeout(resolve, 200))
    await wrapper.vm.$nextTick()

    // Permission message should be available
    const paymentDisabledMessage = wrapper.vm.paymentDisabledMessage
    expect(paymentDisabledMessage).toBeTruthy()
    expect(paymentDisabledMessage.length).toBeGreaterThan(0)
  })
})
