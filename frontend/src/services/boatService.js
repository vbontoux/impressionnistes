import apiClient, { getErrorMessage } from './apiClient'

const boatService = {
  /**
   * Create a new boat registration
   */
  async createBoatRegistration(boatData) {
    const response = await apiClient.post('/boat', boatData)
    return response.data
  },

  /**
   * Get all boat registrations for the current team manager
   */
  async getBoatRegistrations() {
    const response = await apiClient.get('/boat')
    return response.data
  },

  /**
   * Get a specific boat registration
   */
  async getBoatRegistration(boatRegistrationId) {
    const response = await apiClient.get(`/boat/${boatRegistrationId}`)
    return response.data
  },

  /**
   * Update a boat registration
   */
  async updateBoatRegistration(boatRegistrationId, updates) {
    const response = await apiClient.put(`/boat/${boatRegistrationId}`, updates)
    return response.data
  },

  /**
   * Delete a boat registration
   */
  async deleteBoatRegistration(boatRegistrationId) {
    const response = await apiClient.delete(`/boat/${boatRegistrationId}`)
    return response.data
  },

  /**
   * Get confirmed rental boats ready for payment
   */
  async getRentalsForPayment() {
    const response = await apiClient.get('/rental/requests-for-payment')
    return response.data
  },

  /**
   * Cancel a rental request
   */
  async cancelRentalRequest(rentalBoatId) {
    const response = await apiClient.delete(`/rental/cancel/${rentalBoatId}`)
    return response.data
  }
}

export default boatService
