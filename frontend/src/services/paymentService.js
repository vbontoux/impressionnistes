/**
 * Payment Service
 * Handles payment-related API calls
 */
import apiClient from './apiClient'

const paymentService = {
  /**
   * Create a payment intent for selected boat registrations and/or rental requests
   * @param {Array<string>} boatRegistrationIds - Array of boat registration IDs
   * @param {Array<string>} rentalRequestIds - Array of rental request IDs
   * @returns {Promise} Payment intent data with client_secret
   */
  async createPaymentIntent(boatRegistrationIds, rentalRequestIds = []) {
    const response = await apiClient.post('/payment/create-intent', {
      boat_registration_ids: boatRegistrationIds,
      rental_request_ids: rentalRequestIds
    })
    return response.data
  },

  /**
   * Get payment receipt details
   * @param {string} paymentId - Payment ID
   * @returns {Promise} Payment receipt data
   */
  async getPaymentReceipt(paymentId) {
    const response = await apiClient.get(`/payment/receipt/${paymentId}`)
    return response.data
  },

  /**
   * Get payment history for the current team manager
   * @param {Object} params - Query parameters
   * @param {string} params.start_date - Optional start date filter (ISO format)
   * @param {string} params.end_date - Optional end date filter (ISO format)
   * @param {number} params.limit - Optional limit (default 50)
   * @param {string} params.sort - Optional sort order ('asc' or 'desc', default 'desc')
   * @returns {Promise} Payment history data
   */
  async getPaymentHistory(params = {}) {
    const response = await apiClient.get('/payment/history', { params })
    // Backend wraps response in { success: true, data: { payments: [...], summary: {...} } }
    return response.data.data || response.data
  },

  /**
   * Get payment summary for the current team manager
   * @returns {Promise} Payment summary with total paid and outstanding balance
   */
  async getPaymentSummary() {
    const response = await apiClient.get('/payment/summary')
    // Backend wraps response in { success: true, data: {...} }
    return response.data.data || response.data
  },

  /**
   * Download payment invoice PDF
   * @param {string} paymentId - Payment ID
   * @returns {Promise} PDF blob
   */
  async downloadInvoice(paymentId) {
    const response = await apiClient.get(`/payment/invoice/${paymentId}`, {
      responseType: 'blob'
    })
    return response.data
  },

  /**
   * Get all payments (admin only)
   * @param {Object} params - Query parameters
   * @param {string} params.start_date - Optional start date filter
   * @param {string} params.end_date - Optional end date filter
   * @param {string} params.team_manager_id - Optional team manager filter
   * @param {number} params.limit - Optional limit
   * @param {string} params.sort_by - Optional sort field
   * @param {string} params.sort_order - Optional sort order
   * @returns {Promise} All payments data
   */
  async getAllPayments(params = {}) {
    const response = await apiClient.get('/admin/payments', { params })
    // Backend wraps response in { success: true, data: {...} }
    return response.data.data || response.data
  },

  /**
   * Get payment analytics (admin only)
   * @param {Object} params - Query parameters
   * @param {string} params.start_date - Optional start date filter
   * @param {string} params.end_date - Optional end date filter
   * @param {string} params.group_by - Optional grouping (day, week, month)
   * @returns {Promise} Payment analytics data
   */
  async getPaymentAnalytics(params = {}) {
    const response = await apiClient.get('/admin/payments/analytics', { params })
    // Backend wraps response in { success: true, data: {...} }
    return response.data.data || response.data
  }
}

export default paymentService
