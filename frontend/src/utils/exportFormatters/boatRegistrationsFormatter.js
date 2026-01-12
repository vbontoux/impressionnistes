/**
 * Boat Registrations Export Formatter
 * Converts JSON data from the backend API to CSV format for download
 */

import { escapeCSVField, downloadFile, formatDateForFilename, formatBoolean } from './shared.js'

/**
 * Calculate filled seats in "X/Y" format
 * @param {Object} boat - The boat registration object
 * @returns {string} - Filled seats formatted as "X/Y"
 */
export function calculateFilledSeats(boat) {
  if (!boat.crew_composition) {
    // Fallback: count from seats array
    const seats = boat.seats || []
    const filled = seats.filter(seat => seat.crew_member_id).length
    const total = seats.length
    return `${filled}/${total}`
  }
  
  const filled = boat.crew_composition.filled_seats || 0
  const total = boat.crew_composition.total_seats || 0
  return `${filled}/${total}`
}



/**
 * Convert boat registrations JSON data to CSV format
 * @param {Object} jsonData - The JSON response from the backend API
 * @returns {string} - CSV formatted string
 */
export function formatBoatRegistrationsToCSV(jsonData) {
  if (!jsonData || !jsonData.data || !jsonData.data.boats) {
    throw new Error('Invalid data format: expected data.boats array')
  }
  
  const boats = jsonData.data.boats
  
  // Find the maximum number of crew members across all boats
  let maxCrewMembers = 0
  for (const boat of boats) {
    const crewDetails = boat.crew_details || []
    if (crewDetails.length > maxCrewMembers) {
      maxCrewMembers = crewDetails.length
    }
  }
  
  // Define base CSV headers
  const baseHeaders = [
    'Boat Registration ID',
    'Boat Number',
    'Event Type',
    'Boat Type',
    'Race Name',
    'Registration Status',
    'Forfait',
    'Filled Seats',
    'Gender Category',
    'Age Category',
    'Average Age',
    'Is Multi-Club Crew',
    'Club',
    'Club List',
    'Assigned Boat Identifier',
    'Assigned Boat Comment',
    'Team Manager Name',
    'Team Manager Email',
    'Team Manager Club',
    'Created At',
    'Updated At',
    'Paid At'
  ]
  
  // Add crew member headers dynamically based on max crew size
  const crewHeaders = []
  for (let i = 1; i <= maxCrewMembers; i++) {
    crewHeaders.push(
      `${i}. Position`,
      `${i}. First Name`,
      `${i}. Last Name`,
      `${i}. Gender`,
      `${i}. Date of Birth`,
      `${i}. Age`,
      `${i}. License Number`,
      `${i}. Club Affiliation`
    )
  }
  
  const headers = [...baseHeaders, ...crewHeaders]
  
  // Build CSV rows
  const rows = [headers]
  
  for (const boat of boats) {
    const crewComp = boat.crew_composition || {}
    const crewDetails = boat.crew_details || []
    
    // Base boat information
    const baseRow = [
      escapeCSVField(boat.boat_registration_id || ''),
      escapeCSVField(boat.boat_number || ''),
      escapeCSVField(boat.event_type || ''),
      escapeCSVField(boat.boat_type || ''),
      escapeCSVField(boat.race_name || ''),
      escapeCSVField(boat.registration_status || ''),
      escapeCSVField(formatBoolean(boat.forfait)),
      escapeCSVField(calculateFilledSeats(boat)),
      escapeCSVField(crewComp.gender_category || ''),
      escapeCSVField(crewComp.age_category || ''),
      escapeCSVField(crewComp.avg_age || ''),
      escapeCSVField(formatBoolean(boat.is_multi_club_crew)),
      escapeCSVField(boat.boat_club_display || ''),
      escapeCSVField((boat.club_list || []).join('; ')),
      escapeCSVField(boat.assigned_boat_identifier || ''),
      escapeCSVField(boat.assigned_boat_comment || ''),
      escapeCSVField(boat.team_manager_name || ''),
      escapeCSVField(boat.team_manager_email || ''),
      escapeCSVField(boat.team_manager_club || ''),
      escapeCSVField(boat.created_at || ''),
      escapeCSVField(boat.updated_at || ''),
      escapeCSVField(boat.paid_at || '')
    ]
    
    // Add crew member details
    const crewRow = []
    for (let i = 0; i < maxCrewMembers; i++) {
      const crew = crewDetails[i] || {}
      crewRow.push(
        escapeCSVField(crew.type || ''),
        escapeCSVField(crew.first_name || ''),
        escapeCSVField(crew.last_name || ''),
        escapeCSVField(crew.gender || ''),
        escapeCSVField(crew.date_of_birth || ''),
        escapeCSVField(crew.age || ''),
        escapeCSVField(crew.license_number || ''),
        escapeCSVField(crew.club_affiliation || '')
      )
    }
    
    rows.push([...baseRow, ...crewRow])
  }
  
  // Convert rows to CSV string
  return rows.map(row => row.join(',')).join('\n')
}

/**
 * Download boat registrations data as CSV file
 * @param {Object} jsonData - The JSON response from the backend API
 * @param {string} filename - Optional custom filename (without extension)
 */
export function downloadBoatRegistrationsCSV(jsonData, filename = null) {
  // Generate CSV content
  const csvContent = formatBoatRegistrationsToCSV(jsonData)
  
  // Generate filename with timestamp if not provided
  const timestamp = formatDateForFilename()
  const finalFilename = filename || `boat_registrations_export_${timestamp}`
  
  // Create blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  downloadFile(blob, `${finalFilename}.csv`)
}
