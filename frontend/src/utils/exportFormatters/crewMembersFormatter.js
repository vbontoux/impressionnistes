/**
 * Crew Members Export Formatter
 * Converts JSON data from the backend API to CSV format for download
 */

import { escapeCSVField, downloadFile, formatDateForFilename } from './shared.js'

/**
 * Convert crew members JSON data to CSV format
 * @param {Object} jsonData - The JSON response from the backend API
 * @returns {string} - CSV formatted string
 */
export function formatCrewMembersToCSV(jsonData) {
  if (!jsonData || !jsonData.data || !jsonData.data.crew_members) {
    throw new Error('Invalid data format: expected data.crew_members array')
  }
  
  const crewMembers = jsonData.data.crew_members
  
  // Define CSV headers
  const headers = [
    'Crew Member ID',
    'First Name',
    'Last Name',
    'Gender',
    'Date of Birth',
    'Age',
    'License Number',
    'Club Affiliation',
    'Team Manager Name',
    'Team Manager Email',
    'Team Manager Club',
    'Boat Assignment',
    'Boat Type',
    'Event Type',
    'Race Name',
    'Boat Number',
    'Seat Position',
    'Assigned Boat Identifier',
    'Assigned Boat Comment',
    'Created At',
    'Updated At'
  ]
  
  // Build CSV rows
  const rows = [headers]
  
  for (const member of crewMembers) {
    rows.push([
      escapeCSVField(member.crew_member_id || ''),
      escapeCSVField(member.first_name || ''),
      escapeCSVField(member.last_name || ''),
      escapeCSVField(member.gender || ''),
      escapeCSVField(member.date_of_birth || ''),
      escapeCSVField(member.age || ''),
      escapeCSVField(member.license_number || ''),
      escapeCSVField(member.club_affiliation || ''),
      escapeCSVField(member.team_manager_name || ''),
      escapeCSVField(member.team_manager_email || ''),
      escapeCSVField(member.team_manager_club || ''),
      escapeCSVField(member.assigned_boat_id ? 'Yes' : 'No'),
      escapeCSVField(member.boat_type || ''),
      escapeCSVField(member.event_type || ''),
      escapeCSVField(member.race_name || ''),
      escapeCSVField(member.boat_number || ''),
      escapeCSVField(member.seat_position || ''),
      escapeCSVField(member.assigned_boat_identifier || ''),
      escapeCSVField(member.assigned_boat_comment || ''),
      escapeCSVField(member.created_at || ''),
      escapeCSVField(member.updated_at || '')
    ])
  }
  
  // Convert rows to CSV string
  return rows.map(row => row.join(',')).join('\n')
}

/**
 * Download crew members data as CSV file
 * @param {Object} jsonData - The JSON response from the backend API
 * @param {string} filename - Optional custom filename (without extension)
 */
export function downloadCrewMembersCSV(jsonData, filename = null) {
  // Generate CSV content
  const csvContent = formatCrewMembersToCSV(jsonData)
  
  // Generate filename with timestamp if not provided
  const timestamp = formatDateForFilename()
  const finalFilename = filename || `crew_members_export_${timestamp}`
  
  // Create blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  downloadFile(blob, `${finalFilename}.csv`)
}
