/**
 * Crew Member Service
 * Handles all API calls related to crew member management
 */
import apiClient, { getErrorMessage } from './apiClient';

/**
 * Create a new crew member
 */
export const createCrewMember = async (crewMemberData) => {
  const response = await apiClient.post('/crew', crewMemberData);
  // API returns {success: true, data: {...}}
  return response.data.data || response.data;
};

/**
 * Get all crew members for the authenticated team manager
 */
export const listCrewMembers = async () => {
  const response = await apiClient.get('/crew');
  // API returns {success: true, data: {crew_members: [...]}}
  return response.data.data?.crew_members || [];
};

/**
 * Get a specific crew member by ID
 */
export const getCrewMember = async (crewMemberId) => {
  const response = await apiClient.get(`/crew/${crewMemberId}`);
  // API returns {success: true, data: {...}}
  return response.data.data || response.data;
};

/**
 * Update a crew member
 */
export const updateCrewMember = async (crewMemberId, updates) => {
  const response = await apiClient.put(`/crew/${crewMemberId}`, updates);
  // API returns {success: true, data: {...}}
  return response.data.data || response.data;
};

/**
 * Delete a crew member
 */
export const deleteCrewMember = async (crewMemberId) => {
  const response = await apiClient.delete(`/crew/${crewMemberId}`);
  // API returns {success: true, data: {...}}
  return response.data.data || response.data;
};
