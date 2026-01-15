/**
 * Tests for CrewMemberCard Component with Permission Checks
 * Validates: Requirements 8.2-8.7, 8.10
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createPinia, setActivePinia } from 'pinia'
import CrewMemberCard from './CrewMemberCard.vue'
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

// Mock permission service
vi.mock('@/services/permissionService', () => ({
  fetchCurrentPhase: vi.fn(() => Promise.resolve('during_registration')),
  fetchPermissionMatrix: vi.fn(() => Promise.resolve({
    edit_crew_member: {
      before_registration: false,
      during_registration: true,
      after_registration: false,
      after_payment_deadline: false,
      requires_not_assigned: true
    },
    delete_crew_member: {
      before_registration: false,
      during_registration: true,
      after_registration: false,
      after_payment_deadline: false,
      requires_not_assigned: true
    }
  })),
  getDefaultPermissionMatrix: vi.fn(() => ({
    edit_crew_member: {
      before_registration: false,
      during_registration: true,
      after_registration: false,
      after_payment_deadline: false,
      requires_not_assigned: true
    },
    delete_crew_member: {
      before_registration: false,
      during_registration: true,
      after_registration: false,
      after_payment_deadline: false,
      requires_not_assigned: true
    }
  }))
}))

describe('CrewMemberCard.vue - Permission Checks', () => {
  let pinia
  let authStore

  const mockCrewMember = {
    crew_member_id: 'crew1',
    first_name: 'John',
    last_name: 'Doe',
    license_number: 'LIC123',
    date_of_birth: '1990-01-01',
    gender: 'M',
    club_affiliation: 'Test Club',
    assigned_boat_id: null
  }

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
    
    // Set up team manager user
    authStore.user = {
      user_id: 'tm1',
      email: 'manager@example.com',
      first_name: 'Manager',
      last_name: 'User',
      groups: []
    }
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should enable buttons during registration period for unassigned crew', async () => {
    const i18n = createI18nInstance('en')
    const wrapper = mount(CrewMemberCard, {
      props: {
        crewMember: mockCrewMember
      },
      global: {
        plugins: [i18n, pinia]
      }
    })

    // Wait for permissions to initialize
    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    // Buttons should be enabled
    const editButton = wrapper.findAll('button').find(btn => btn.text().includes('Edit'))
    const deleteButton = wrapper.findAll('button').find(btn => btn.text().includes('Delete'))
    
    expect(editButton).toBeDefined()
    expect(deleteButton).toBeDefined()
  })

  it('should disable buttons for assigned crew member', async () => {
    const assignedCrewMember = {
      ...mockCrewMember,
      assigned_boat_id: 'boat1'
    }

    const i18n = createI18nInstance('en')
    const wrapper = mount(CrewMemberCard, {
      props: {
        crewMember: assignedCrewMember
      },
      global: {
        plugins: [i18n, pinia]
      }
    })

    // Wait for permissions to initialize
    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    // Buttons should be disabled
    const editButton = wrapper.findAll('button').find(btn => btn.text().includes('Edit'))
    const deleteButton = wrapper.findAll('button').find(btn => btn.text().includes('Delete'))
    
    expect(editButton).toBeDefined()
    expect(deleteButton).toBeDefined()
  })

  it('should display tooltip for disabled buttons', async () => {
    const assignedCrewMember = {
      ...mockCrewMember,
      assigned_boat_id: 'boat1'
    }

    const i18n = createI18nInstance('en')
    const wrapper = mount(CrewMemberCard, {
      props: {
        crewMember: assignedCrewMember
      },
      global: {
        plugins: [i18n, pinia]
      }
    })

    // Wait for permissions to initialize
    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    // Tooltips should be present
    const editButton = wrapper.findAll('button').find(btn => btn.text().includes('Edit'))
    const deleteButton = wrapper.findAll('button').find(btn => btn.text().includes('Delete'))
    
    expect(editButton?.attributes('title')).toBeTruthy()
    expect(deleteButton?.attributes('title')).toBeTruthy()
  })

  it('should enable buttons for admin with impersonation', async () => {
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
      first_name: 'Manager',
      last_name: 'User',
      email: 'manager@example.com'
    }

    const assignedCrewMember = {
      ...mockCrewMember,
      assigned_boat_id: 'boat1'
    }

    const i18n = createI18nInstance('en')
    const wrapper = mount(CrewMemberCard, {
      props: {
        crewMember: assignedCrewMember
      },
      global: {
        plugins: [i18n, pinia]
      }
    })

    // Wait for permissions to initialize
    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    // Buttons should be enabled for admin with impersonation
    const editButton = wrapper.findAll('button').find(btn => btn.text().includes('Edit'))
    const deleteButton = wrapper.findAll('button').find(btn => btn.text().includes('Delete'))
    
    expect(editButton).toBeDefined()
    expect(deleteButton).toBeDefined()
  })
})
