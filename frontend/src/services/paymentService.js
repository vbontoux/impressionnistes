/**
 * Payment Service
 * Handles payment-related API calls
 */
import apiClient from './apiClient'

const paymentService = {
  /**
   * Create a payment intent for selected boat registrations and/or rental boats
   * @param {Array<string>} boatRegistrationIds - Array of boat registration IDs
   * @param {Array<string>} rentalBoatIds - Array of rental boat IDs
   * @returns {Promise} Payment intent data with client_secret
   */
  async createPaymentIntent(boatRegistrationIds, rentalBoatIds = []) {
    const response = await apiClient.post('/payment/create-intent', {
      boat_registration_ids: boatRegistrationIds,
      rental_boat_ids: rentalBoatIds
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
  }
}

export default paymentService
