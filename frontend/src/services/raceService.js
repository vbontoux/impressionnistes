/**
 * Race Service
 * API calls for race-related operations
 */
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

/**
 * Get all available races
 * @param {Object} filters - Optional filters (event_type, boat_type, age_category, gender_category)
 * @returns {Promise} API response with races array
 */
export async function listRaces(filters = {}) {
  const params = new URLSearchParams()
  
  if (filters.event_type) params.append('event_type', filters.event_type)
  if (filters.boat_type) params.append('boat_type', filters.boat_type)
  if (filters.age_category) params.append('age_category', filters.age_category)
  if (filters.gender_category) params.append('gender_category', filters.gender_category)
  
  const queryString = params.toString()
  const url = queryString ? `${API_URL}/races?${queryString}` : `${API_URL}/races`
  
  console.log('Fetching races from:', url)
  
  const response = await axios.get(url)
  return response
}

export default {
  listRaces
}
