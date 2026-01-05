/**
 * Tests for AdminImpersonationBar Component
 * Ensures impersonation bar renders correctly and handles user interactions
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createPinia, setActivePinia } from 'pinia'
import AdminImpersonationBar from './AdminImpersonationBar.vue'
import { useAuthStore } from '@/stores/authStore'
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

// Mock apiClient
vi.mock('@/services/apiClient', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({
      data: {
        team_managers: [
          {
            user_id: 'tm1',
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
            club_affiliation: 'Test Club'
          },
          {
            user_id: 'tm2',
            first_name: 'Jane',
            last_name: 'Smith',
            email: 'jane@example.com',
            club_affiliation: 'Another Club'
          }
        ]
      }
    }))
  }
}))

describe('AdminImpersonationBar.vue', () => {
  let pinia
  let authStore
  let reloadSpy

  beforeEach(() => {
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
    
    // Mock window.location with a valid URL
    reloadSpy = vi.fn()
    delete window.location
    window.location = {
      href: 'http://localhost:3000/dashboard?team_manager_id=tm1',
      reload: reloadSpy
    }
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should render when impersonating', async () => {
    // Set up admin user with impersonation
    authStore.user = {
      user_id: 'admin1',
      email: 'admin@example.com',
      first_name: 'Admin',
      last_name: 'User',
      groups: ['admins']
    }
    authStore.impersonatedTeamManagerId = 'tm1'
    authStore.impersonatedTeamManager = {
      user_id: 'tm1',
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      club_affiliation: 'Test Club'
    }

    const i18n = createI18nInstance('en')
    const wrapper = mount(AdminImpersonationBar, {
      global: {
        plugins: [i18n, pinia]
      }
    })

    await wrapper.vm.$nextTick()

    // Component should be visible
    expect(wrapper.find('.impersonation-bar').exists()).toBe(true)
    
    // Should display team manager info
    expect(wrapper.text()).toContain('John Doe')
    expect(wrapper.text()).toContain('john@example.com')
    expect(wrapper.text()).toContain('ADMIN MODE: Viewing as')
  })

  it('should not render when not impersonating', async () => {
    // Set up admin user WITHOUT impersonation
    authStore.user = {
      user_id: 'admin1',
      email: 'admin@example.com',
      first_name: 'Admin',
      last_name: 'User',
      groups: ['admins']
    }
    authStore.impersonatedTeamManagerId = null
    authStore.impersonatedTeamManager = null

    const i18n = createI18nInstance('en')
    const wrapper = mount(AdminImpersonationBar, {
      global: {
        plugins: [i18n, pinia]
      }
    })

    await wrapper.vm.$nextTick()

    // Component should not be visible
    expect(wrapper.find('.impersonation-bar').exists()).toBe(false)
  })

  it('should display correct team manager info', async () => {
    // Set up admin user with impersonation
    authStore.user = {
      user_id: 'admin1',
      email: 'admin@example.com',
      first_name: 'Admin',
      last_name: 'User',
      groups: ['admins']
    }
    authStore.impersonatedTeamManagerId = 'tm2'
    authStore.impersonatedTeamManager = {
      user_id: 'tm2',
      first_name: 'Jane',
      last_name: 'Smith',
      email: 'jane@example.com',
      club_affiliation: 'Another Club'
    }

    const i18n = createI18nInstance('en')
    const wrapper = mount(AdminImpersonationBar, {
      global: {
        plugins: [i18n, pinia]
      }
    })

    await wrapper.vm.$nextTick()

    // Should display correct team manager info
    expect(wrapper.find('.team-manager-name').text()).toBe('Jane Smith')
    expect(wrapper.find('.team-manager-email').text()).toBe('(jane@example.com)')
  })

  it('should clear impersonation when exit button is clicked', async () => {
    // Set up admin user with impersonation
    authStore.user = {
      user_id: 'admin1',
      email: 'admin@example.com',
      first_name: 'Admin',
      last_name: 'User',
      groups: ['admins']
    }
    authStore.impersonatedTeamManagerId = 'tm1'
    authStore.impersonatedTeamManager = {
      user_id: 'tm1',
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      club_affiliation: 'Test Club'
    }

    const i18n = createI18nInstance('en')
    const wrapper = mount(AdminImpersonationBar, {
      global: {
        plugins: [i18n, pinia]
      }
    })

    await wrapper.vm.$nextTick()

    // Click exit button
    const exitButton = wrapper.find('.exit-btn')
    expect(exitButton.exists()).toBe(true)
    
    // Call the method directly to test the logic
    wrapper.vm.exitImpersonation()
    
    // Should clear impersonation from store
    expect(authStore.impersonatedTeamManagerId).toBeNull()
    expect(authStore.impersonatedTeamManager).toBeNull()
    
    // Should navigate to URL without team_manager_id parameter
    expect(window.location.href).toBe('http://localhost:3000/dashboard')
  })

  it('should display exit button with correct styling', async () => {
    // Set up admin user with impersonation
    authStore.user = {
      user_id: 'admin1',
      email: 'admin@example.com',
      first_name: 'Admin',
      last_name: 'User',
      groups: ['admins']
    }
    authStore.impersonatedTeamManagerId = 'tm1'
    authStore.impersonatedTeamManager = {
      user_id: 'tm1',
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      club_affiliation: 'Test Club'
    }

    const i18n = createI18nInstance('en')
    const wrapper = mount(AdminImpersonationBar, {
      global: {
        plugins: [i18n, pinia]
      }
    })

    await wrapper.vm.$nextTick()

    // Find exit button
    const exitButton = wrapper.find('.exit-btn')
    expect(exitButton.exists()).toBe(true)
    
    // Should have correct text
    expect(exitButton.text()).toContain('Exit Impersonation')
    
    // Should not be disabled
    expect(exitButton.attributes('disabled')).toBeUndefined()
  })

  it('should display warning icon', async () => {
    // Set up admin user with impersonation
    authStore.user = {
      user_id: 'admin1',
      email: 'admin@example.com',
      first_name: 'Admin',
      last_name: 'User',
      groups: ['admins']
    }
    authStore.impersonatedTeamManagerId = 'tm1'
    authStore.impersonatedTeamManager = {
      user_id: 'tm1',
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      club_affiliation: 'Test Club'
    }

    const i18n = createI18nInstance('en')
    const wrapper = mount(AdminImpersonationBar, {
      global: {
        plugins: [i18n, pinia]
      }
    })

    await wrapper.vm.$nextTick()

    // Should display warning icon
    const warningIcon = wrapper.find('.warning-icon')
    expect(warningIcon.exists()).toBe(true)
    expect(warningIcon.text()).toBe('⚠️')
  })

  it('should render in French', async () => {
    // Set up admin user with impersonation
    authStore.user = {
      user_id: 'admin1',
      email: 'admin@example.com',
      first_name: 'Admin',
      last_name: 'User',
      groups: ['admins']
    }
    authStore.impersonatedTeamManagerId = 'tm1'
    authStore.impersonatedTeamManager = {
      user_id: 'tm1',
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      club_affiliation: 'Test Club'
    }

    const i18n = createI18nInstance('fr')
    const wrapper = mount(AdminImpersonationBar, {
      global: {
        plugins: [i18n, pinia]
      }
    })

    await wrapper.vm.$nextTick()

    // Should display French text
    expect(wrapper.text()).toContain('MODE ADMIN : Affichage en tant que')
    
    const exitButton = wrapper.find('.exit-btn')
    expect(exitButton.text()).toContain("Quitter l'emprunt d'identité")
  })

  it('should display impersonation info correctly', async () => {
    // Set up admin user with impersonation
    authStore.user = {
      user_id: 'admin1',
      email: 'admin@example.com',
      first_name: 'Admin',
      last_name: 'User',
      groups: ['admins']
    }
    authStore.impersonatedTeamManagerId = 'tm1'
    authStore.impersonatedTeamManager = {
      user_id: 'tm1',
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      club_affiliation: 'Test Club'
    }

    const i18n = createI18nInstance('en')
    const wrapper = mount(AdminImpersonationBar, {
      global: {
        plugins: [i18n, pinia]
      }
    })

    await wrapper.vm.$nextTick()

    // Should display impersonation info section
    const impersonationInfo = wrapper.find('.impersonation-info')
    expect(impersonationInfo.exists()).toBe(true)
    
    // Should contain all required elements
    expect(impersonationInfo.text()).toContain('ADMIN MODE: Viewing as')
    expect(impersonationInfo.text()).toContain('John Doe')
    expect(impersonationInfo.text()).toContain('john@example.com')
  })

  it('should disable exit button while loading', async () => {
    // Set up admin user with impersonation
    authStore.user = {
      user_id: 'admin1',
      email: 'admin@example.com',
      first_name: 'Admin',
      last_name: 'User',
      groups: ['admins']
    }
    authStore.impersonatedTeamManagerId = 'tm1'
    authStore.impersonatedTeamManager = {
      user_id: 'tm1',
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      club_affiliation: 'Test Club'
    }

    const i18n = createI18nInstance('en')
    const wrapper = mount(AdminImpersonationBar, {
      global: {
        plugins: [i18n, pinia]
      }
    })

    // Set loading state
    wrapper.vm.loading = true
    await wrapper.vm.$nextTick()

    // Exit button should be disabled
    const exitButton = wrapper.find('.exit-btn')
    expect(exitButton.attributes('disabled')).toBeDefined()
  })
})
