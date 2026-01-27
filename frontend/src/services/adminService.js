/**
 * Admin Service
 * Handles API calls for admin-only endpoints
 */
import apiClient from './apiClient'

const adminService = {
  /**
   * List all crew members across all team managers
   * @param {Object} params - Query parameters
   * @param {string} params.team_manager_id - Filter by team manager ID
   * @param {string} params.club - Filter by club affiliation
   * @param {string} params.search - Search term
   * @returns {Promise<Object>} Response with crew_members array and count
   */
  async listAllCrewMembers(params = {}) {
    const queryParams = new URLSearchParams()
    
    if (params.team_manager_id) {
      queryParams.append('team_manager_id', params.team_manager_id)
    }
    if (params.club) {
      queryParams.append('club', params.club)
    }
    if (params.search) {
      queryParams.append('search', params.search)
    }

    const queryString = queryParams.toString()
    const url = `/admin/crew${queryString ? `?${queryString}` : ''}`
    
    const response = await apiClient.get(url)
    return response.data.data // Return the data object which contains crew_members
  },

  /**
   * List all boat registrations across all team managers
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Response with boat registrations
   */
  async listAllBoats(params = {}) {
    const queryParams = new URLSearchParams()
    
    if (params.team_manager_id) {
      queryParams.append('team_manager_id', params.team_manager_id)
    }
    if (params.club) {
      queryParams.append('club', params.club)
    }
    if (params.search) {
      queryParams.append('search', params.search)
    }

    const queryString = queryParams.toString()
    const url = `/admin/boat-registrations${queryString ? `?${queryString}` : ''}`
    
    const response = await apiClient.get(url)
    return response.data
  },

  /**
   * Get system statistics
   * @returns {Promise<Object>} System statistics
   */
  async getStats() {
    const response = await apiClient.get('/admin/stats')
    return response.data
  },

  /**
   * Get event configuration
   * @returns {Promise<Object>} Event configuration
   */
  async getEventConfig() {
    const response = await apiClient.get('/admin/event-config')
    return response.data
  },

  /**
   * Update event configuration
   * @param {Object} config - Event configuration
   * @returns {Promise<Object>} Updated configuration
   */
  async updateEventConfig(config) {
    const response = await apiClient.put('/admin/event-config', config)
    return response.data
  },

  /**
   * Get pricing configuration
   * @returns {Promise<Object>} Pricing configuration
   */
  async getPricingConfig() {
    const response = await apiClient.get('/admin/pricing-config')
    return response.data
  },

  /**
   * Update pricing configuration
   * @param {Object} config - Pricing configuration
   * @returns {Promise<Object>} Updated configuration
   */
  async updatePricingConfig(config) {
    const response = await apiClient.put('/admin/pricing-config', config)
    return response.data
  },

  /**
   * Export data to various formats
   * @param {string} type - Export type (crew-members, boat-registrations, crewtimer, event-program)
   * @returns {Promise<Blob>} File blob
   */
  async exportData(type) {
    const response = await apiClient.get(`/admin/exports/${type}`, {
      responseType: 'blob'
    })
    return response.data
  },

  /**
   * Get payment analytics
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Payment analytics data
   */
  async getPaymentAnalytics(params = {}) {
    const queryParams = new URLSearchParams()
    
    if (params.start_date) {
      queryParams.append('start_date', params.start_date)
    }
    if (params.end_date) {
      queryParams.append('end_date', params.end_date)
    }
    if (params.group_by) {
      queryParams.append('group_by', params.group_by)
    }

    const queryString = queryParams.toString()
    const url = `/admin/payment-analytics${queryString ? `?${queryString}` : ''}`
    
    const response = await apiClient.get(url)
    return response.data
  },

  /**
   * Update license verification status for a single crew member
   * @param {string} teamManagerId - Team manager ID
   * @param {string} crewMemberId - Crew member ID
   * @param {string} status - Verification status ('verified_valid', 'verified_invalid', 'manually_verified_valid', 'manually_verified_invalid')
   * @param {string} details - Verification details (optional, max 500 chars)
   * @returns {Promise<Object>} Updated crew member
   */
  async updateCrewMemberLicenseVerification(teamManagerId, crewMemberId, status, details = '') {
    const response = await apiClient.patch(
      `/admin/crew/${teamManagerId}/${crewMemberId}/license-verification`,
      {
        team_manager_id: teamManagerId,
        license_verification_status: status,
        license_verification_details: details
      }
    )
    return response.data
  },

  /**
   * Bulk update license verification status for multiple crew members
   * @param {Array} verifications - Array of verification objects
   * @param {string} verifications[].team_manager_id - Team manager ID
   * @param {string} verifications[].crew_member_id - Crew member ID
   * @param {string} verifications[].license_verification_status - Verification status
   * @param {string} verifications[].license_verification_details - Verification details (optional)
   * @returns {Promise<Object>} Bulk update results
   */
  async bulkUpdateLicenseVerification(verifications) {
    const response = await apiClient.post(
      '/admin/crew/bulk-license-verification',
      { verifications }
    )
    return response.data
  }
}

export default adminService
