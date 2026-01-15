/**
 * Permission Service
 * Handles API calls for permission checking and management
 */
import apiClient from './apiClient'

/**
 * Fetch current event phase
 * Uses public event info endpoint to determine phase
 * @returns {Promise<string>} Current event phase
 */
export async function fetchCurrentPhase() {
  try {
    const response = await apiClient.get('/public/event-info')
    const eventInfo = response.data.data
    
    // Determine phase based on dates
    const now = new Date()
    const startDate = eventInfo.registration_start_date ? new Date(eventInfo.registration_start_date) : null
    const endDate = eventInfo.registration_end_date ? new Date(eventInfo.registration_end_date) : null
    const paymentDeadline = eventInfo.payment_deadline ? new Date(eventInfo.payment_deadline) : null
    
    let phase = 'before_registration'
    
    if (startDate && endDate && paymentDeadline) {
      if (now < startDate) {
        phase = 'before_registration'
      } else if (now >= startDate && now <= endDate) {
        phase = 'during_registration'
      } else if (now > endDate && now <= paymentDeadline) {
        phase = 'after_registration'
      } else {
        phase = 'after_payment_deadline'
      }
    }
    
    return phase
  } catch (error) {
    console.error('Failed to fetch current phase:', error)
    // Default to most restrictive phase on error
    return 'after_payment_deadline'
  }
}

/**
 * Fetch permission matrix configuration
 * Requires admin access
 * @returns {Promise<Object>} Permission matrix
 */
export async function fetchPermissionMatrix() {
  try {
    const response = await apiClient.get('/admin/permissions/config')
    return response.data.permissions
  } catch (error) {
    console.error('Failed to fetch permission matrix:', error)
    throw error
  }
}

/**
 * Check if a specific action is permitted
 * @param {string} action - Action to check
 * @param {Object} resourceContext - Resource context
 * @returns {Promise<Object>} Permission result with is_permitted and denial_reason
 */
export async function checkPermission(action, resourceContext = {}) {
  try {
    const response = await apiClient.post('/api/permissions/check', {
      action,
      resource_context: resourceContext
    })
    return response.data
  } catch (error) {
    console.error('Failed to check permission:', error)
    // On error, deny by default
    return {
      is_permitted: false,
      denial_reason: 'Failed to check permission',
      denial_reason_key: 'errors.permission_check_failed'
    }
  }
}

/**
 * Get default permission matrix
 * Used as fallback when API is unavailable
 * @returns {Object} Default permission matrix
 */
export function getDefaultPermissionMatrix() {
  return {
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
    delete_crew_member: {
      before_registration: false,
      during_registration: true,
      after_registration: false,
      after_payment_deadline: false,
      requires_not_assigned: true
    },
    create_boat_registration: {
      before_registration: false,
      during_registration: true,
      after_registration: false,
      after_payment_deadline: false
    },
    edit_boat_registration: {
      before_registration: false,
      during_registration: true,
      after_registration: false,
      after_payment_deadline: false,
      requires_not_paid: true
    },
    delete_boat_registration: {
      before_registration: false,
      during_registration: true,
      after_registration: false,
      after_payment_deadline: false,
      requires_not_paid: true
    },
    process_payment: {
      before_registration: false,
      during_registration: true,
      after_registration: true,
      after_payment_deadline: false
    },
    view_data: {
      before_registration: true,
      during_registration: true,
      after_registration: true,
      after_payment_deadline: true
    },
    export_data: {
      before_registration: true,
      during_registration: true,
      after_registration: true,
      after_payment_deadline: true
    }
  }
}

export default {
  fetchCurrentPhase,
  fetchPermissionMatrix,
  checkPermission,
  getDefaultPermissionMatrix
}
