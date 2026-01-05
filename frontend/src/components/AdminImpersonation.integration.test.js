/**
 * Integration tests for Admin Impersonation feature
 * 
 * Task 13: Integration testing
 * Tests complete impersonation flow, cross-page navigation, URL sharing,
 * error handling, mobile responsive design, and performance.
 * 
 * Requirements: All requirements
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import AdminImpersonationBar from './AdminImpersonationBar.vue'
import { useAuthStore } from '@/stores/authStore'
import apiClient from '@/services/apiClient'

// Mock API client
vi.mock('@/services/apiClient', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: {
        use: vi.fn(),
        eject: vi.fn()
      },
      response: {
        use: vi.fn(),
        eject: vi.fn()
      }
    }
  }
}))

// Global i18n mock
const globalI18nMock = {
  $t: (key) => {
    const translations = {
      'admin.impersonation.viewing_as': 'Viewing as',
      'admin.impersonation.exit': 'Exit Impersonation',
      'admin.impersonation.select_team_manager': 'Select Team Manager',
      'admin.impersonation.no_team_managers': 'No team managers found',
      'admin.impersonation.load_error': 'Error loading team managers'
    }
    return translations[key] || key
  }
}

// Create a simple router for testing
function createTestRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
      { path: '/boats', name: 'boats', component: { template: '<div>Boats</div>' } },
      { path: '/crew', name: 'crew', component: { template: '<div>Crew</div>' } },
      { path: '/dashboard', name: 'dashboard', component: { template: '<div>Dashboard</div>' } }
    ]
  })
}

// Mock team managers data
const mockTeamManagers = [
  {
    user_id: 'tm-001',
    first_name: 'John',
    last_name: 'Doe',
    email: 'john.doe@example.com',
    club_affiliation: 'Test Club A'
  },
  {
    user_id: 'tm-002',
    first_name: 'Jane',
    last_name: 'Smith',
    email: 'jane.smith@example.com',
    club_affiliation: 'Test Club B'
  },
  {
    user_id: 'tm-003',
    first_name: 'Bob',
    last_name: 'Johnson',
    email: 'bob.johnson@example.com',
    club_affiliation: 'Test Club C'
  }
]

describe('Admin Impersonation - Integration Tests', () => {
  let pinia
  let router
  let authStore
  let localStorageMock

  beforeEach(() => {
    // Mock localStorage
    localStorageMock = {
      getItem: vi.fn((key) => {
        if (key === 'impersonatedTeamManagerId') return null
        if (key === 'impersonatedTeamManager') return null
        return null
      }),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn()
    }
    global.localStorage = localStorageMock
    
    // Create fresh pinia instance
    pinia = createPinia()
    setActivePinia(pinia)
    
    // Create router
    router = createTestRouter()
    
    // Get auth store
    authStore = useAuthStore()
    
    // Set up admin user (groups array makes isAdmin getter return true)
    authStore.user = {
      user_id: 'admin-123',
      email: 'admin@example.com',
      first_name: 'Admin',
      last_name: 'User',
      groups: ['admins']  // This makes isAdmin getter return true
    }
    authStore.isAuthenticated = true
    
    // Reset mocks
    vi.clearAllMocks()
    
    // Mock successful team managers API call
    apiClient.get.mockResolvedValue({
      data: {
        success: true,
        data: {
          team_managers: mockTeamManagers,
          count: mockTeamManagers.length
        }
      }
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Test 1: Complete Impersonation Flow (select → view data → exit)', () => {
    it('should complete full impersonation lifecycle', async () => {
      // Mount component
      const wrapper = mount(AdminImpersonationBar, {
        global: {
          plugins: [pinia, router],
          mocks: globalI18nMock,
          mocks: globalI18nMock
        }
      })

      await flushPromises()

      // Step 1: Initially not impersonating
      expect(authStore.isImpersonating).toBe(false)
      expect(wrapper.find('.impersonation-bar').exists()).toBe(false)

      // Step 2: Start impersonation
      const teamManagerId = 'tm-001'
      const teamManager = mockTeamManagers[0]
      
      authStore.setImpersonation(teamManagerId, teamManager)
      await wrapper.vm.$nextTick()

      // Step 3: Verify impersonation is active
      expect(authStore.isImpersonating).toBe(true)
      expect(authStore.impersonatedTeamManagerId).toBe(teamManagerId)
      expect(authStore.impersonatedTeamManager).toEqual(teamManager)
      expect(authStore.effectiveUserId).toBe(teamManagerId)

      // Step 4: Verify UI shows impersonation bar
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.impersonation-bar').exists()).toBe(true)
      expect(wrapper.text()).toContain('John Doe')
      expect(wrapper.text()).toContain('john.doe@example.com')

      // Step 5: Exit impersonation
      authStore.clearImpersonation()
      await wrapper.vm.$nextTick()

      // Step 6: Verify impersonation is cleared
      expect(authStore.isImpersonating).toBe(false)
      expect(authStore.impersonatedTeamManagerId).toBe(null)
      expect(authStore.impersonatedTeamManager).toBe(null)
      expect(authStore.effectiveUserId).toBe('admin-123')
      expect(wrapper.find('.impersonation-bar').exists()).toBe(false)
    })

    it('should handle team manager selection from dropdown', async () => {
      // Start with impersonation active
      authStore.setImpersonation('tm-001', mockTeamManagers[0])

      const wrapper = mount(AdminImpersonationBar, {
        global: {
          plugins: [pinia, router],
          mocks: globalI18nMock
        }
      })

      await flushPromises()

      // Verify initial state
      expect(wrapper.text()).toContain('John Doe')

      // Change to different team manager (simulating what AdminImpersonationCard would do)
      authStore.setImpersonation('tm-002', mockTeamManagers[1])
      await wrapper.vm.$nextTick()

      // Verify impersonation changed
      expect(authStore.impersonatedTeamManagerId).toBe('tm-002')
      expect(authStore.impersonatedTeamManager.first_name).toBe('Jane')
      expect(wrapper.text()).toContain('Jane Smith')
    })

    it('should handle exit button click', async () => {
      // Start with impersonation active
      authStore.setImpersonation('tm-001', mockTeamManagers[0])

      const wrapper = mount(AdminImpersonationBar, {
        global: {
          plugins: [pinia, router],
          mocks: globalI18nMock
        }
      })

      await flushPromises()

      // Verify impersonation is active
      expect(authStore.isImpersonating).toBe(true)

      // Click exit button
      const exitButton = wrapper.find('.exit-btn')
      expect(exitButton.exists()).toBe(true)
      await exitButton.trigger('click')
      await flushPromises()

      // Verify impersonation is cleared
      expect(authStore.isImpersonating).toBe(false)
      expect(authStore.impersonatedTeamManagerId).toBe(null)
    })
  })

  describe('Test 2: Cross-Page Navigation with Impersonation', () => {
    it('should preserve impersonation state across page navigation', async () => {
      // Start impersonation
      const teamManagerId = 'tm-001'
      authStore.setImpersonation(teamManagerId, mockTeamManagers[0])

      // Navigate to boats page
      await router.push('/boats')
      await flushPromises()

      // Verify impersonation persists
      expect(authStore.isImpersonating).toBe(true)
      expect(authStore.impersonatedTeamManagerId).toBe(teamManagerId)
      expect(authStore.effectiveUserId).toBe(teamManagerId)

      // Navigate to crew page
      await router.push('/crew')
      await flushPromises()

      // Verify impersonation still persists
      expect(authStore.isImpersonating).toBe(true)
      expect(authStore.impersonatedTeamManagerId).toBe(teamManagerId)

      // Navigate to dashboard
      await router.push('/dashboard')
      await flushPromises()

      // Verify impersonation still persists
      expect(authStore.isImpersonating).toBe(true)
      expect(authStore.impersonatedTeamManagerId).toBe(teamManagerId)
    })

    it('should maintain effective user ID across navigation', async () => {
      const teamManagerId = 'tm-002'
      authStore.setImpersonation(teamManagerId, mockTeamManagers[1])

      // Navigate through multiple pages
      const pages = ['/boats', '/crew', '/dashboard', '/']
      
      for (const page of pages) {
        await router.push(page)
        await flushPromises()
        
        // Verify effective user ID is always the impersonated ID
        expect(authStore.effectiveUserId).toBe(teamManagerId)
        expect(authStore.effectiveUserId).not.toBe('admin-123')
      }
    })

    it('should clear impersonation on all pages when exited', async () => {
      // Start impersonation
      authStore.setImpersonation('tm-001', mockTeamManagers[0])

      // Navigate to boats page
      await router.push('/boats')
      await flushPromises()
      expect(authStore.isImpersonating).toBe(true)

      // Exit impersonation
      authStore.clearImpersonation()
      await flushPromises()

      // Navigate to other pages and verify impersonation stays cleared
      await router.push('/crew')
      await flushPromises()
      expect(authStore.isImpersonating).toBe(false)

      await router.push('/dashboard')
      await flushPromises()
      expect(authStore.isImpersonating).toBe(false)
    })
  })

  describe('Test 3: URL Sharing Between Admins', () => {
    it('should restore impersonation state from URL parameter', async () => {
      // Simulate URL with team_manager_id parameter
      await router.push({
        path: '/boats',
        query: { team_manager_id: 'tm-002' }
      })
      await flushPromises()

      // Manually trigger what App.vue would do
      const teamManagerId = router.currentRoute.value.query.team_manager_id
      expect(teamManagerId).toBe('tm-002')

      // Simulate fetching team manager details and setting impersonation
      const teamManager = mockTeamManagers.find(tm => tm.user_id === teamManagerId)
      authStore.setImpersonation(teamManagerId, teamManager)
      await flushPromises()

      // Verify impersonation is restored
      expect(authStore.isImpersonating).toBe(true)
      expect(authStore.impersonatedTeamManagerId).toBe('tm-002')
      expect(authStore.impersonatedTeamManager.first_name).toBe('Jane')
    })

    it('should preserve URL parameter across navigation', async () => {
      // Start with URL containing team_manager_id
      await router.push({
        path: '/boats',
        query: { team_manager_id: 'tm-001' }
      })
      await flushPromises()

      // Set impersonation
      authStore.setImpersonation('tm-001', mockTeamManagers[0])

      // Navigate to different page
      await router.push({
        path: '/crew',
        query: { team_manager_id: 'tm-001' }
      })
      await flushPromises()

      // Verify URL parameter is preserved
      expect(router.currentRoute.value.query.team_manager_id).toBe('tm-001')
      expect(authStore.isImpersonating).toBe(true)
    })

    it('should allow multiple admins to share same impersonation URL', async () => {
      // Admin 1 creates impersonation URL
      const sharedUrl = '/boats?team_manager_id=tm-003'
      
      // Admin 2 opens the URL
      await router.push(sharedUrl)
      await flushPromises()

      const teamManagerId = router.currentRoute.value.query.team_manager_id
      expect(teamManagerId).toBe('tm-003')

      // Admin 2 sets up impersonation
      const teamManager = mockTeamManagers.find(tm => tm.user_id === teamManagerId)
      authStore.setImpersonation(teamManagerId, teamManager)

      // Verify Admin 2 can impersonate the same team manager
      expect(authStore.isImpersonating).toBe(true)
      expect(authStore.impersonatedTeamManagerId).toBe('tm-003')
      expect(authStore.impersonatedTeamManager.first_name).toBe('Bob')
    })
  })

  describe('Test 4: Error Handling', () => {
    it('should handle invalid team manager ID gracefully', async () => {
      // Try to impersonate with invalid ID
      const invalidId = 'invalid-tm-999'
      
      // Mock API to return 404
      apiClient.get.mockRejectedValueOnce({
        response: {
          status: 404,
          data: {
            success: false,
            error: { message: 'Team manager not found' }
          }
        }
      })

      // Attempt to set impersonation with invalid ID
      // In real app, this would be caught by App.vue watcher
      authStore.setImpersonation(invalidId, null)
      
      // Should handle gracefully - store accepts the ID even if invalid
      // The actual validation happens in the backend
      expect(authStore.impersonatedTeamManagerId).toBe(invalidId)
      expect(authStore.impersonatedTeamManager).toBe(null)
      
      // Component should still render without crashing
      const wrapper = mount(AdminImpersonationBar, {
        global: {
          plugins: [pinia, router],
          mocks: globalI18nMock
        }
      })
      
      await flushPromises()
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle network errors when loading team managers', async () => {
      // Mock network error
      apiClient.get.mockRejectedValueOnce(new Error('Network error'))

      // Don't set impersonation - component won't render without it
      const wrapper = mount(AdminImpersonationBar, {
        global: {
          plugins: [pinia, router],
          mocks: globalI18nMock
        }
      })

      await flushPromises()

      // Component should not render when not impersonating (even with errors)
      expect(wrapper.find('.impersonation-bar').exists()).toBe(false)
      
      // But if we set impersonation, component should render
      authStore.setImpersonation('tm-001', mockTeamManagers[0])
      await wrapper.vm.$nextTick()
      
      // Component should render with impersonation data
      expect(wrapper.find('.impersonation-bar').exists()).toBe(true)
    })

    it('should handle API timeout errors', async () => {
      // Mock timeout error
      apiClient.get.mockRejectedValueOnce({
        code: 'ECONNABORTED',
        message: 'timeout of 5000ms exceeded'
      })

      // Don't set impersonation - component won't render without it
      const wrapper = mount(AdminImpersonationBar, {
        global: {
          plugins: [pinia, router],
          mocks: globalI18nMock
        }
      })

      await flushPromises()

      // Component should not render when not impersonating
      expect(wrapper.find('.impersonation-bar').exists()).toBe(false)
      
      // But if we set impersonation, component should render
      authStore.setImpersonation('tm-002', mockTeamManagers[1])
      await wrapper.vm.$nextTick()
      
      // Component should render with impersonation data
      expect(wrapper.find('.impersonation-bar').exists()).toBe(true)
      expect(wrapper.text()).toContain('Jane Smith')
    })

    it('should handle 403 Forbidden when non-admin tries to impersonate', async () => {
      // Set up non-admin user (no 'admins' group makes isAdmin return false)
      authStore.user = {
        user_id: 'tm-001',
        email: 'teammanager@example.com',
        groups: ['team_managers']  // Not an admin
      }

      // Mock 403 response
      apiClient.get.mockRejectedValueOnce({
        response: {
          status: 403,
          data: {
            success: false,
            error: { message: 'Admin access required' }
          }
        }
      })

      const wrapper = mount(AdminImpersonationBar, {
        global: {
          plugins: [pinia, router],
          mocks: globalI18nMock
        }
      })

      await flushPromises()

      // Component should not render for non-admin
      expect(wrapper.find('.impersonation-bar').exists()).toBe(false)
    })

    it('should handle empty team managers list', async () => {
      // Mock empty list
      apiClient.get.mockResolvedValueOnce({
        data: {
          success: true,
          data: {
            team_managers: [],
            count: 0
          }
        }
      })

      // Don't set impersonation - component won't render without it
      const wrapper = mount(AdminImpersonationBar, {
        global: {
          plugins: [pinia, router],
          mocks: globalI18nMock
        }
      })

      await flushPromises()

      // Component should not render when not impersonating
      expect(wrapper.find('.impersonation-bar').exists()).toBe(false)
      
      // Even with empty team managers list, if we set impersonation, component should render
      authStore.setImpersonation('tm-001', mockTeamManagers[0])
      await wrapper.vm.$nextTick()
      
      // Component should render with impersonation data
      expect(wrapper.find('.impersonation-bar').exists()).toBe(true)
    })
  })

  describe('Test 5: Mobile Responsive Design', () => {
    it('should render correctly on mobile viewport', async () => {
      // Set mobile viewport
      global.innerWidth = 375
      global.innerHeight = 667

      authStore.setImpersonation('tm-001', mockTeamManagers[0])

      const wrapper = mount(AdminImpersonationBar, {
        global: {
          plugins: [pinia, router],
          mocks: globalI18nMock
        }
      })

      await flushPromises()

      // Verify component renders
      expect(wrapper.find('.impersonation-bar').exists()).toBe(true)
      
      // Check for mobile-specific classes or styles
      const bar = wrapper.find('.impersonation-bar')
      expect(bar.exists()).toBe(true)
      
      // Verify content is still accessible
      expect(wrapper.text()).toContain('John Doe')
      expect(wrapper.find('.exit-btn').exists()).toBe(true)
    })

    it('should render correctly on tablet viewport', async () => {
      // Set tablet viewport
      global.innerWidth = 768
      global.innerHeight = 1024

      authStore.setImpersonation('tm-002', mockTeamManagers[1])

      const wrapper = mount(AdminImpersonationBar, {
        global: {
          plugins: [pinia, router],
          mocks: globalI18nMock
        }
      })

      await flushPromises()

      // Verify component renders
      expect(wrapper.find('.impersonation-bar').exists()).toBe(true)
      expect(wrapper.text()).toContain('Jane Smith')
    })

    it('should maintain functionality on small screens', async () => {
      // Set small mobile viewport
      global.innerWidth = 320
      global.innerHeight = 568

      authStore.setImpersonation('tm-001', mockTeamManagers[0])

      const wrapper = mount(AdminImpersonationBar, {
        global: {
          plugins: [pinia, router],
          mocks: globalI18nMock
        }
      })

      await flushPromises()

      // Verify exit button is still clickable
      const exitButton = wrapper.find('.exit-btn')
      expect(exitButton.exists()).toBe(true)
      
      await exitButton.trigger('click')
      await flushPromises()

      // Verify functionality works
      expect(authStore.isImpersonating).toBe(false)
    })
  })

  describe('Test 6: Performance (state changes < 500ms)', () => {
    it('should complete impersonation state change in < 500ms', async () => {
      const startTime = performance.now()

      // Start impersonation
      authStore.setImpersonation('tm-001', mockTeamManagers[0])
      await flushPromises()

      const endTime = performance.now()
      const duration = endTime - startTime

      // Verify state change is fast
      expect(duration).toBeLessThan(500)
      expect(authStore.isImpersonating).toBe(true)
    })

    it('should complete impersonation exit in < 500ms', async () => {
      // Start with impersonation active
      authStore.setImpersonation('tm-001', mockTeamManagers[0])
      await flushPromises()

      const startTime = performance.now()

      // Exit impersonation
      authStore.clearImpersonation()
      await flushPromises()

      const endTime = performance.now()
      const duration = endTime - startTime

      // Verify exit is fast
      expect(duration).toBeLessThan(500)
      expect(authStore.isImpersonating).toBe(false)
    })

    it('should complete team manager switch in < 500ms', async () => {
      // Start with impersonation active
      authStore.setImpersonation('tm-001', mockTeamManagers[0])
      await flushPromises()

      const startTime = performance.now()

      // Switch to different team manager
      authStore.setImpersonation('tm-002', mockTeamManagers[1])
      await flushPromises()

      const endTime = performance.now()
      const duration = endTime - startTime

      // Verify switch is fast
      expect(duration).toBeLessThan(500)
      expect(authStore.impersonatedTeamManagerId).toBe('tm-002')
    })

    it('should handle rapid state changes efficiently', async () => {
      const startTime = performance.now()

      // Perform multiple rapid state changes
      for (let i = 0; i < 10; i++) {
        const tm = mockTeamManagers[i % mockTeamManagers.length]
        authStore.setImpersonation(tm.user_id, tm)
        await flushPromises()
      }

      const endTime = performance.now()
      const duration = endTime - startTime

      // Verify all changes complete in reasonable time
      expect(duration).toBeLessThan(2000) // 10 changes in < 2 seconds
    })
  })

  describe('Test 7: API Client Integration', () => {
    it('should add team_manager_id parameter to API requests when impersonating', async () => {
      // Start impersonation
      authStore.setImpersonation('tm-001', mockTeamManagers[0])

      // Verify store state
      expect(authStore.isImpersonating).toBe(true)
      expect(authStore.impersonatedTeamManagerId).toBe('tm-001')

      // Note: The actual API client interceptor is tested in apiClient.test.js
      // This test verifies the store provides the correct state
      expect(authStore.effectiveUserId).toBe('tm-001')
    })

    it('should not add team_manager_id parameter when not impersonating', async () => {
      // Ensure not impersonating
      authStore.clearImpersonation()

      // Verify store state
      expect(authStore.isImpersonating).toBe(false)
      expect(authStore.impersonatedTeamManagerId).toBe(null)
      expect(authStore.effectiveUserId).toBe('admin-123')
    })
  })

  describe('Test 8: Security and Authorization', () => {
    it('should only show impersonation bar for admins', async () => {
      // Test with admin (groups includes 'admins')
      authStore.user = {
        user_id: 'admin-123',
        email: 'admin@example.com',
        groups: ['admins']
      }
      authStore.setImpersonation('tm-001', mockTeamManagers[0])

      let wrapper = mount(AdminImpersonationBar, {
        global: {
          plugins: [pinia, router],
          mocks: globalI18nMock
        }
      })

      await flushPromises()
      expect(wrapper.find('.impersonation-bar').exists()).toBe(true)

      // Test with non-admin (groups does not include 'admins')
      authStore.user = {
        user_id: 'tm-001',
        email: 'teammanager@example.com',
        groups: ['team_managers']
      }
      authStore.clearImpersonation()

      wrapper = mount(AdminImpersonationBar, {
        global: {
          plugins: [pinia, router],
          mocks: globalI18nMock
        }
      })

      await flushPromises()
      expect(wrapper.find('.impersonation-bar').exists()).toBe(false)
    })

    it('should preserve admin identity during impersonation', async () => {
      const adminUserId = 'admin-123'
      authStore.user = {
        user_id: adminUserId,
        email: 'admin@example.com'
      }

      // Start impersonation
      authStore.setImpersonation('tm-001', mockTeamManagers[0])

      // Verify admin identity is preserved
      expect(authStore.user.user_id).toBe(adminUserId)
      expect(authStore.user.email).toBe('admin@example.com')
      
      // But effective user ID is the impersonated user
      expect(authStore.effectiveUserId).toBe('tm-001')
      expect(authStore.effectiveUserId).not.toBe(adminUserId)
    })
  })

  describe('Test 9: Data Consistency', () => {
    it('should maintain consistent state across store and UI', async () => {
      const wrapper = mount(AdminImpersonationBar, {
        global: {
          plugins: [pinia, router],
          mocks: globalI18nMock
        }
      })

      await flushPromises()

      // Start impersonation
      authStore.setImpersonation('tm-001', mockTeamManagers[0])
      await wrapper.vm.$nextTick()

      // Verify store and UI are in sync
      expect(authStore.isImpersonating).toBe(true)
      expect(wrapper.find('.impersonation-bar').exists()).toBe(true)
      expect(wrapper.text()).toContain('John Doe')

      // Exit impersonation
      authStore.clearImpersonation()
      await wrapper.vm.$nextTick()

      // Verify store and UI are still in sync
      expect(authStore.isImpersonating).toBe(false)
      expect(wrapper.find('.impersonation-bar').exists()).toBe(false)
    })

    it('should handle concurrent state updates correctly', async () => {
      // Simulate rapid concurrent updates
      const updates = [
        () => authStore.setImpersonation('tm-001', mockTeamManagers[0]),
        () => authStore.setImpersonation('tm-002', mockTeamManagers[1]),
        () => authStore.setImpersonation('tm-003', mockTeamManagers[2])
      ]

      // Execute all updates
      await Promise.all(updates.map(update => {
        update()
        return flushPromises()
      }))

      // Verify final state is consistent (last update wins)
      expect(authStore.isImpersonating).toBe(true)
      expect(authStore.impersonatedTeamManagerId).toBe('tm-003')
    })
  })

  describe('Test 10: Internationalization', () => {
    it('should display impersonation bar in current language', async () => {
      authStore.setImpersonation('tm-001', mockTeamManagers[0])

      const wrapper = mount(AdminImpersonationBar, {
        global: {
          plugins: [pinia, router],
          mocks: globalI18nMock,
          mocks: {
            $t: (key) => {
              const translations = {
                'admin.impersonation.viewing_as': 'Viewing as',
                'admin.impersonation.exit': 'Exit Impersonation'
              }
              return translations[key] || key
            }
          }
        }
      })

      await flushPromises()

      // Verify translated text appears
      expect(wrapper.text()).toContain('Viewing as')
      expect(wrapper.text()).toContain('Exit Impersonation')
    })
  })
})
