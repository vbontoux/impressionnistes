/**
 * Crew Member Service
 * Handles all API calls related to crew member management
 */
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

/**
 * Get authorization header with JWT token
 */
const getAuthHeader = () => {
  // Use ID token for Cognito User Pool authorizer (not access token)
  const token = localStorage.getItem('id_token') || localStorage.getItem('access_token') || localStorage.getItem('auth_token');
  
  if (!token) {
    console.warn('No authentication token found in localStorage');
  } else {
    console.log('Using auth token (first 20 chars):', token.substring(0, 20) + '...');
    console.log('Token type:', localStorage.getItem('id_token') ? 'ID Token' : 'Access Token');
  }
  
  return token ? { Authorization: `Bearer ${token}` } : {};
};

/**
 * Create a new crew member
 */
export const createCrewMember = async (crewMemberData) => {
  console.log('Creating crew member with data:', crewMemberData);
  console.log('API URL:', API_URL);
  console.log('Full URL:', `${API_URL}/crew`);
  console.log('Headers:', getAuthHeader());
  
  try {
    const response = await axios.post(
      `${API_URL}/crew`,
      crewMemberData,
      { headers: getAuthHeader() }
    );
    console.log('Crew member created successfully:', response.data);
    // API returns {success: true, data: {...}}
    return response.data.data || response.data;
  } catch (error) {
    console.error('Failed to create crew member:', error);
    console.error('Error response:', error.response);
    throw error;
  }
};

/**
 * Get all crew members for the authenticated team manager
 */
export const listCrewMembers = async () => {
  const response = await axios.get(
    `${API_URL}/crew`,
    { headers: getAuthHeader() }
  );
  // API returns {success: true, data: {crew_members: [...]}}
  return response.data.data?.crew_members || [];
};

/**
 * Get a specific crew member by ID
 */
export const getCrewMember = async (crewMemberId) => {
  const response = await axios.get(
    `${API_URL}/crew/${crewMemberId}`,
    { headers: getAuthHeader() }
  );
  // API returns {success: true, data: {...}}
  return response.data.data || response.data;
};

/**
 * Update a crew member
 */
export const updateCrewMember = async (crewMemberId, updates) => {
  const response = await axios.put(
    `${API_URL}/crew/${crewMemberId}`,
    updates,
    { headers: getAuthHeader() }
  );
  // API returns {success: true, data: {...}}
  return response.data.data || response.data;
};

/**
 * Delete a crew member
 */
export const deleteCrewMember = async (crewMemberId) => {
  const response = await axios.delete(
    `${API_URL}/crew/${crewMemberId}`,
    { headers: getAuthHeader() }
  );
  // API returns {success: true, data: {...}}
  return response.data.data || response.data;
};
