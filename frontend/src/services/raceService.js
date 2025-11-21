/**
 * Race Service
 * API calls for race-related operations
 */
import apiClient, { getErrorMessage } from './apiClient'

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
  const url = queryString ? `/races?${queryString}` : '/races'
  
  const response = await apiClient.get(url)
  return response
}

export default {
  listRaces
}
