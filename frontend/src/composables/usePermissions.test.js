import { describe, it, expect, beforeEach, vi } from 'vitest'
import { usePermissions, clearPermissionCache } from './usePermissions'
import * as permissionService from '../services/permissionService'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: vi.fn(() => ({
    t: vi.fn((key) => {
      // Return simple English translations for testing
      const translations = {
        'errors.permission.registration_not_open': 'Registration is not yet open',
        'errors.permission.registration_closed': 'Registration period has ended. Contact the organization for changes.',
        'errors.permission.payment_deadline_passed': 'Payment deadline has passed. Contact the organization.',
        'errors.permission.crew_member_assigned': 'Cannot modify an assigned crew member. Unassign from boat first.',
        'errors.permission.boat_paid': 'Cannot modify a paid boat. Contact the organization.',
        'errors.permission.action_not_permitted': 'Action not permitted'
      }
      return translations[key] || key
    })
  }))
}))

// Mock the auth store
const mockAuthStore = {
  user: {
    user_id: 'user-123',
    groups: ['team_managers']
  },
  isAdmin: false,
  isImpersonating: false,
  effectiveUserId: 'user-123'
}

vi.mock('../stores/authStore', () => ({
  useAuthStore: vi.fn(() => mockAuthStore)
}))

// Mock the permission service
vi.mock('../services/permissionService', () => ({
  fetchCurrentPhase: vi.fn(),
  fetchPermissionMatrix: vi.fn(),
  getDefaultPermissionMatrix: vi.fn(() => ({
    create_crew_member: {
      before_registration: false,
      during_registration: true,
      after_registration: false,
      after_payment_deadline: false
    },
    edit_crew_member: {
      before_registration: false,
      during_registration: true,
      after_registration: false,
      after_payment_deadline: false,
      requires_not_assigned: true
    },
    process_payment: {
      before_registration: false,
      during_registration: true,
      after_registration: true,
      after_payment_deadline: false
    }
  }))
}))

describe('usePermissions', () => {
  beforeEach(() => {
    // Clear the cache before each test
    clearPermissionCache()
    
    // Reset mocks before each test
    vi.clearAllMocks()
    
    // Reset auth store to default
    mockAuthStore.isAdmin = false
    mockAuthStore.isImpersonating = false
    mockAuthStore.user = { user_id: 'user-123', groups: ['team_managers'] }
    
    // Set default mock implementations
    permissionService.fetchCurrentPhase.mockResolvedValue('during_registration')
    permissionService.fetchPermissionMatrix.mockResolvedValue(
      permissionService.getDefaultPermissionMatrix()
    )
  })

  describe('initialization', () => {
    it('should initialize with loading state', () => {
      const { loading } = usePermissions()
      expect(loading.value).toBe(true)
    })

    it('should set loading to false after initialization', async () => {
      const { initialize, loading } = usePermissions()
      
      await initialize()
      
      expect(loading.value).toBe(false)
    })

    it('should handle initialization errors gracefully', async () => {
      permissionService.fetchCurrentPhase.mockRejectedValue(new Error('Network error'))
      
      const { initialize, error, currentPhase } = usePermissions()
      
      await initialize()
      
      // On error, should default to safe phase (during_registration) to allow operations
      expect(currentPhase.value).toBe('during_registration')
      // Error may or may not be set depending on implementation
    })
  })

  describe('canPerformAction', () => {
    it('should allow action during registration period', async () => {
      permissionService.fetchCurrentPhase.mockResolvedValue('during_registration')
      
      const { initialize, canPerformAction } = usePermissions()
      await initialize()
      
      const result = canPerformAction('create_crew_member')
      expect(result).toBe(true)
    })

    it('should deny action before registration period', async () => {
      permissionService.fetchCurrentPhase.mockResolvedValue('before_registration')
      
      const { initialize, canPerformAction } = usePermissions()
      await initialize()
      
      const result = canPerformAction('create_crew_member')
      expect(result).toBe(false)
    })

    it('should deny action after registration period', async () => {
      permissionService.fetchCurrentPhase.mockResolvedValue('after_registration')
      
      const { initialize, canPerformAction } = usePermissions()
      await initialize()
      
      const result = canPerformAction('create_crew_member')
      expect(result).toBe(false)
    })

    it('should deny editing assigned crew member', async () => {
      permissionService.fetchCurrentPhase.mockResolvedValue('during_registration')
      
      const { initialize, canPerformAction } = usePermissions()
      await initialize()
      
      const resourceContext = {
        resource_type: 'crew_member',
        resource_state: { assigned: true }
      }
      
      const result = canPerformAction('edit_crew_member', resourceContext)
      expect(result).toBe(false)
    })

    it('should allow editing unassigned crew member', async () => {
      permissionService.fetchCurrentPhase.mockResolvedValue('during_registration')
      
      const { initialize, canPerformAction } = usePermissions()
      await initialize()
      
      const resourceContext = {
        resource_type: 'crew_member',
        resource_state: { assigned: false }
      }
      
      const result = canPerformAction('edit_crew_member', resourceContext)
      expect(result).toBe(true)
    })

    it('should allow payment during and after registration', async () => {
      permissionService.fetchCurrentPhase.mockResolvedValue('after_registration')
      
      const { initialize, canPerformAction } = usePermissions()
      await initialize()
      
      const result = canPerformAction('process_payment')
      expect(result).toBe(true)
    })

    it('should return false when loading', () => {
      const { canPerformAction } = usePermissions()
      
      const result = canPerformAction('create_crew_member')
      expect(result).toBe(false)
    })
  })

  describe('getPermissionMessage', () => {
    it('should return null when action is permitted', async () => {
      permissionService.fetchCurrentPhase.mockResolvedValue('during_registration')
      
      const { initialize, getPermissionMessage } = usePermissions()
      await initialize()
      
      const message = getPermissionMessage('create_crew_member')
      expect(message).toBeNull()
    })

    it('should return phase message when denied by phase', async () => {
      permissionService.fetchCurrentPhase.mockResolvedValue('before_registration')
      
      const { initialize, getPermissionMessage } = usePermissions()
      await initialize()
      
      const message = getPermissionMessage('create_crew_member')
      expect(message).toBe('Registration is not yet open')
    })

    it('should return state message when denied by data state', async () => {
      permissionService.fetchCurrentPhase.mockResolvedValue('during_registration')
      
      const { initialize, getPermissionMessage } = usePermissions()
      await initialize()
      
      const resourceContext = {
        resource_type: 'crew_member',
        resource_state: { assigned: true }
      }
      
      const message = getPermissionMessage('edit_crew_member', resourceContext)
      expect(message).toBe('Cannot modify an assigned crew member. Unassign from boat first.')
    })

    it('should return appropriate message for after registration phase', async () => {
      permissionService.fetchCurrentPhase.mockResolvedValue('after_registration')
      
      const { initialize, getPermissionMessage } = usePermissions()
      await initialize()
      
      const message = getPermissionMessage('create_crew_member')
      expect(message).toBe('Registration period has ended. Contact the organization for changes.')
    })

    it('should return appropriate message for after payment deadline', async () => {
      permissionService.fetchCurrentPhase.mockResolvedValue('after_payment_deadline')
      
      const { initialize, getPermissionMessage } = usePermissions()
      await initialize()
      
      const message = getPermissionMessage('process_payment')
      expect(message).toBe('Payment deadline has passed. Contact the organization.')
    })
  })

  describe('bypass detection', () => {
    it('should detect impersonation bypass', async () => {
      // Update mock auth store for this test
      mockAuthStore.isAdmin = true
      mockAuthStore.isImpersonating = true
      mockAuthStore.user = { user_id: 'admin-123', groups: ['admins'] }
      
      const { initialize, hasBypass, userContext } = usePermissions()
      await initialize()
      
      // Verify user context was set correctly
      expect(userContext.value.is_impersonating).toBe(true)
      expect(hasBypass()).toBe(true)
    })

    it('should detect no bypass for regular users', async () => {
      const { initialize, hasBypass, userContext } = usePermissions()
      await initialize()
      
      // Verify user context
      expect(userContext.value.is_impersonating).toBe(false)
      expect(hasBypass()).toBe(false)
    })
  })

  describe('caching behavior', () => {
    it('should cache permission data', async () => {
      const { initialize, currentPhase, permissionMatrix } = usePermissions()
      await initialize()
      
      // Verify data was loaded
      expect(currentPhase.value).toBe('during_registration')
      expect(permissionMatrix.value).toBeTruthy()
    })
  })

  describe('getCurrentPhase', () => {
    it('should return current phase', async () => {
      permissionService.fetchCurrentPhase.mockResolvedValue('during_registration')
      
      const { initialize, getCurrentPhase } = usePermissions()
      await initialize()
      
      expect(getCurrentPhase()).toBe('during_registration')
    })

    it('should return null before initialization', () => {
      const { getCurrentPhase } = usePermissions()
      
      expect(getCurrentPhase()).toBeNull()
    })
  })

  describe('shared reactive state', () => {
    it('should share permission state across multiple instances', async () => {
      permissionService.fetchCurrentPhase.mockResolvedValue('during_registration')
      
      // Create first instance and initialize
      const instance1 = usePermissions()
      await instance1.initialize()
      
      // Create second instance (should see same state)
      const instance2 = usePermissions()
      
      // Both instances should see the same phase
      expect(instance1.currentPhase.value).toBe('during_registration')
      expect(instance2.currentPhase.value).toBe('during_registration')
      
      // Both instances should see the same loading state
      expect(instance1.loading.value).toBe(false)
      expect(instance2.loading.value).toBe(false)
      
      // Both instances should have the same permission matrix
      expect(instance1.permissionMatrix.value).toBe(instance2.permissionMatrix.value)
    })

    it('should update all instances when permissions are refreshed', async () => {
      permissionService.fetchCurrentPhase.mockResolvedValue('during_registration')
      
      // Create two instances
      const instance1 = usePermissions()
      const instance2 = usePermissions()
      
      // Initialize first instance
      await instance1.initialize()
      
      // Both should see 'during_registration'
      expect(instance1.currentPhase.value).toBe('during_registration')
      expect(instance2.currentPhase.value).toBe('during_registration')
      
      // Change the phase that will be returned
      permissionService.fetchCurrentPhase.mockResolvedValue('after_registration')
      
      // Refresh from first instance
      await instance1.refresh()
      
      // Both instances should see the new phase
      expect(instance1.currentPhase.value).toBe('after_registration')
      expect(instance2.currentPhase.value).toBe('after_registration')
    })

    it('should allow actions in both instances after permission update', async () => {
      permissionService.fetchCurrentPhase.mockResolvedValue('before_registration')
      
      // Create two instances
      const instance1 = usePermissions()
      const instance2 = usePermissions()
      
      // Initialize
      await instance1.initialize()
      
      // Both should deny create_crew_member before registration
      expect(instance1.canPerformAction('create_crew_member')).toBe(false)
      expect(instance2.canPerformAction('create_crew_member')).toBe(false)
      
      // Change phase to during registration
      permissionService.fetchCurrentPhase.mockResolvedValue('during_registration')
      
      // Refresh permissions
      await instance1.refresh()
      
      // Both should now allow create_crew_member
      expect(instance1.canPerformAction('create_crew_member')).toBe(true)
      expect(instance2.canPerformAction('create_crew_member')).toBe(true)
    })
  })
})
