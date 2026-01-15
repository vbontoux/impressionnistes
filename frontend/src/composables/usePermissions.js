/**
 * Composable for permission checking
 * Provides reactive permission state and checking functions
 */
import { computed, reactive } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { useI18n } from 'vue-i18n'
import * as permissionService from '../services/permissionService'

// Cache duration in milliseconds (60 seconds)
const CACHE_TTL = 60 * 1000

// Shared reactive state across all instances

const sharedPermissionState = reactive({
  currentPhase: null,
  permissionMatrix: null,
  userContext: null,
  timestamp: null,
  loading: true,
  error: null
})

// Export for testing purposes
export function clearPermissionCache() {
  sharedPermissionState.currentPhase = null
  sharedPermissionState.permissionMatrix = null
  sharedPermissionState.userContext = null
  sharedPermissionState.timestamp = null
}

export function usePermissions() {
  const authStore = useAuthStore()
  const { t } = useI18n()
  
  // Use shared reactive state instead of local refs
  // This ensures all components see the same permission state
  const currentPhase = computed(() => sharedPermissionState.currentPhase)
  const permissionMatrix = computed(() => sharedPermissionState.permissionMatrix)
  const userContext = computed(() => sharedPermissionState.userContext)
  const loading = computed(() => sharedPermissionState.loading)
  const error = computed(() => sharedPermissionState.error)

  /**
   * Check if cache is still valid
   */
  function isCacheValid() {
    if (!sharedPermissionState.timestamp) return false
    const now = Date.now()
    return (now - sharedPermissionState.timestamp) < CACHE_TTL
  }

  /**
   * Update cache
   */
  function updateCache(phase, matrix, context) {
    sharedPermissionState.currentPhase = phase
    sharedPermissionState.permissionMatrix = matrix
    sharedPermissionState.userContext = context
    sharedPermissionState.timestamp = Date.now()
  }

  /**
   * Fetch current event phase from API
   */
  async function fetchCurrentPhase() {
    try {
      return await permissionService.fetchCurrentPhase()
    } catch (err) {
      console.error('Failed to fetch current phase:', err)
      // Fallback to a safe default phase
      // Use 'during_registration' as default to allow normal operations
      return 'during_registration'
    }
  }

  /**
   * Fetch permission matrix from API
   * Note: This requires admin access, so we'll use a default matrix for non-admins
   */
  async function fetchPermissionMatrix() {
    try {
      console.log('[usePermissions] Fetching permission matrix from API...')
      console.log('[usePermissions] User is admin:', authStore.isAdmin)
      
      // Try to fetch from API
      const matrix = await permissionService.fetchPermissionMatrix()
      console.log('[usePermissions] Successfully fetched permission matrix:', matrix)
      return matrix
    } catch (err) {
      console.error('[usePermissions] Failed to fetch permission matrix:', err)
      console.log('[usePermissions] Falling back to default matrix')
      // Fallback to default matrix
      return permissionService.getDefaultPermissionMatrix()
    }
  }

  /**
   * Extract user context from auth store
   */
  function fetchUserContext() {
    return {
      user_id: authStore.user?.user_id || null,
      role: authStore.isAdmin ? 'admin' : 'team_manager',
      is_impersonating: authStore.isImpersonating,
      has_temporary_access: false, // TODO: Fetch from API when temporary access is implemented
      team_manager_id: authStore.effectiveUserId
    }
  }

  /**
   * Initialize permission state
   * Fetches current phase, permission matrix, and user context
   */
  async function initialize() {
    sharedPermissionState.loading = true
    sharedPermissionState.error = null

    try {
      // Check if cache is valid
      if (isCacheValid()) {
        console.log('[usePermissions] Using cached permissions')
        sharedPermissionState.loading = false
        return
      }

      console.log('[usePermissions] Fetching fresh permissions...')
      
      // Fetch fresh data - use Promise.allSettled to handle failures gracefully
      const results = await Promise.allSettled([
        fetchCurrentPhase(),
        fetchPermissionMatrix()
      ])
      
      // Extract results, using defaults if any promise rejected
      const phase = results[0].status === 'fulfilled' 
        ? results[0].value 
        : 'during_registration'
      
      const matrix = results[1].status === 'fulfilled'
        ? results[1].value
        : permissionService.getDefaultPermissionMatrix()
      
      const context = fetchUserContext()

      console.log('[usePermissions] Fetched permissions:', { phase, matrix, context })

      // Update cache (which updates shared reactive state)
      updateCache(phase, matrix, context)
    } catch (err) {
      console.error('Failed to initialize permissions:', err)
      sharedPermissionState.error = err.message || 'Failed to load permissions'
      
      // Set safe defaults on error - allow operations during registration
      sharedPermissionState.currentPhase = 'during_registration'
      sharedPermissionState.permissionMatrix = permissionService.getDefaultPermissionMatrix()
      sharedPermissionState.userContext = fetchUserContext()
      sharedPermissionState.timestamp = Date.now()
    } finally {
      sharedPermissionState.loading = false
    }
  }

  /**
   * Check if user has bypass (impersonation or temporary access)
   */
  function hasBypass() {
    if (!userContext.value) return false
    return userContext.value.is_impersonating || userContext.value.has_temporary_access
  }

  /**
   * Check phase-based permission
   */
  function checkPhasePermission(action, phase) {
    if (!permissionMatrix.value || !phase) return false
    
    const actionRules = permissionMatrix.value[action]
    if (!actionRules) return false
    
    return actionRules[phase] === true
  }

  /**
   * Check data state restrictions
   */
  function checkStatePermission(action, resourceContext = {}) {
    if (!permissionMatrix.value) return false
    
    const actionRules = permissionMatrix.value[action]
    if (!actionRules) return false
    
    // Check if action requires crew member to not be assigned
    if (actionRules.requires_not_assigned && resourceContext.resource_state?.assigned) {
      return false
    }
    
    // Check if action requires boat to not be paid
    if (actionRules.requires_not_paid && resourceContext.resource_state?.paid) {
      return false
    }
    
    return true
  }

  /**
   * Check if action is permitted
   * @param {string} action - Action to check (e.g., 'create_crew_member')
   * @param {Object} resourceContext - Resource context with state information
   * @returns {boolean} True if action is permitted
   */
  function canPerformAction(action, resourceContext = {}) {
    if (sharedPermissionState.loading) {
      console.log(`[usePermissions] canPerformAction(${action}): Still loading, returning false`)
      return false
    }
    if (!sharedPermissionState.currentPhase || !sharedPermissionState.permissionMatrix) {
      console.log(`[usePermissions] canPerformAction(${action}): Missing phase or matrix, returning false`)
      return false
    }
    
    console.log(`[usePermissions] canPerformAction(${action}):`, {
      currentPhase: sharedPermissionState.currentPhase,
      permissionMatrix: sharedPermissionState.permissionMatrix[action],
      resourceContext,
      hasBypass: hasBypass()
    })
    
    // Check event phase restrictions
    const phaseAllowed = checkPhasePermission(action, sharedPermissionState.currentPhase)
    console.log(`[usePermissions] Phase allowed for ${action}:`, phaseAllowed)
    
    // If phase not allowed and user has bypass, allow (unless data state restricts)
    if (!phaseAllowed && !hasBypass()) {
      console.log(`[usePermissions] Phase not allowed and no bypass, denying ${action}`)
      return false
    }
    
    // Check data state restrictions (applies even with bypass for impersonation)
    // Note: Impersonation bypasses data state restrictions in backend, but we show
    // the restriction in frontend for clarity
    const stateAllowed = checkStatePermission(action, resourceContext)
    console.log(`[usePermissions] State allowed for ${action}:`, stateAllowed)
    if (!stateAllowed && !sharedPermissionState.userContext?.is_impersonating) {
      console.log(`[usePermissions] State not allowed and not impersonating, denying ${action}`)
      return false
    }
    
    console.log(`[usePermissions] Allowing ${action}`)
    return true
  }

  /**
   * Get user-friendly message explaining why action is denied
   * @param {string} action - Action that was denied
   * @param {Object} resourceContext - Resource context
   * @returns {string|null} Denial message or null if action is permitted
   */
  function getPermissionMessage(action, resourceContext = {}) {
    if (canPerformAction(action, resourceContext)) {
      return null
    }
    
    // Check phase restriction
    const phaseAllowed = checkPhasePermission(action, currentPhase.value)
    if (!phaseAllowed && !hasBypass()) {
      return getPhaseMessage(currentPhase.value)
    }
    
    // Check data state restriction
    const stateAllowed = checkStatePermission(action, resourceContext)
    if (!stateAllowed) {
      return getStateMessage(action, resourceContext)
    }
    
    return 'Action not permitted'
  }

  /**
   * Get phase-specific message
   */
  function getPhaseMessage(phase) {
    const messageKeys = {
      before_registration: 'errors.permission.registration_not_open',
      after_registration: 'errors.permission.registration_closed',
      after_payment_deadline: 'errors.permission.payment_deadline_passed'
    }
    
    const key = messageKeys[phase]
    if (key) {
      return t(key, { date: '' }) // TODO: Pass actual date when available
    }
    
    return t('errors.permission.action_not_permitted')
  }

  /**
   * Get data state-specific message
   */
  function getStateMessage(action, resourceContext) {
    const actionRules = permissionMatrix.value?.[action]
    if (!actionRules) return t('errors.permission.action_not_permitted')
    
    if (actionRules.requires_not_assigned && resourceContext.resource_state?.assigned) {
      return t('errors.permission.crew_member_assigned')
    }
    
    if (actionRules.requires_not_paid && resourceContext.resource_state?.paid) {
      return t('errors.permission.boat_paid')
    }
    
    return t('errors.permission.action_not_permitted')
  }

  /**
   * Force refresh permissions (clears cache and refetches)
   */
  async function refresh() {
    console.log('[usePermissions] Forcing refresh of permissions...')
    
    // Clear cache
    clearPermissionCache()
    
    // Re-initialize
    await initialize()
    
    console.log('[usePermissions] Refresh complete. New state:', {
      currentPhase: sharedPermissionState.currentPhase,
      permissionMatrix: sharedPermissionState.permissionMatrix
    })
  }

  /**
   * Get current event phase
   */
  function getCurrentPhase() {
    return currentPhase.value
  }

  // Computed property for bypass status
  const hasPermissionBypass = computed(() => hasBypass())

  return {
    // State
    currentPhase,
    permissionMatrix,
    userContext,
    loading,
    error,
    hasPermissionBypass,
    
    // Methods
    initialize,
    refresh,
    canPerformAction,
    getPermissionMessage,
    getCurrentPhase,
    hasBypass
  }
}
