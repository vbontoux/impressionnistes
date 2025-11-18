import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

/**
 * Get authorization header with JWT token
 */
const getAuthHeader = () => {
  // Use ID token for Cognito User Pool authorizer (not access token)
  const token = localStorage.getItem('id_token') || localStorage.getItem('access_token') || localStorage.getItem('auth_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const boatService = {
  /**
   * Create a new boat registration
   */
  async createBoatRegistration(boatData) {
    const response = await axios.post(`${API_URL}/boat`, boatData, {
      headers: getAuthHeader()
    })
    return response.data
  },

  /**
   * Get all boat registrations for the current team manager
   */
  async getBoatRegistrations() {
    const response = await axios.get(`${API_URL}/boat`, {
      headers: getAuthHeader()
    })
    return response.data
  },

  /**
   * Get a specific boat registration
   */
  async getBoatRegistration(boatRegistrationId) {
    const response = await axios.get(`${API_URL}/boat/${boatRegistrationId}`, {
      headers: getAuthHeader()
    })
    return response.data
  },

  /**
   * Update a boat registration
   */
  async updateBoatRegistration(boatRegistrationId, updates) {
    const response = await axios.put(`${API_URL}/boat/${boatRegistrationId}`, updates, {
      headers: getAuthHeader()
    })
    return response.data
  },

  /**
   * Delete a boat registration
   */
  async deleteBoatRegistration(boatRegistrationId) {
    const response = await axios.delete(`${API_URL}/boat/${boatRegistrationId}`, {
      headers: getAuthHeader()
    })
    return response.data
  }
}

export default boatService
