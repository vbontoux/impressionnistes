/**
 * Event Program Export Formatter
 * Creates an Excel file with crew member list and race schedule for race day printing
 */

import * as XLSX from 'xlsx'
import { formatDateForFilename } from './shared.js'
import { assignRaceAndBowNumbers, filterEligibleBoats } from './raceNumbering.js'
import { translateShortNameToFrench } from './crewTimerFormatter.js'

/**
 * Get column headers for crew member list based on locale
 * @param {string} locale - Locale ('en' or 'fr')
 * @returns {Object} - Object with column header names
 */
function getCrewMemberListHeaders(locale) {
  if (locale === 'en') {
    return {
      lastName: 'Last Name',
      firstName: 'First Name',
      club: 'Club',
      boatNumber: 'Crew #',
      raceShort: 'Race (abbrev)',
      race: 'Race',
      raceNumber: 'Race #',
      stroke: 'Stroke',
      bowNumber: 'Bow #',
      totalPaid: 'Total Paid (EUR)',
      outstandingBalance: 'Outstanding Balance (EUR)',
      paymentStatus: 'Payment Status'
    }
  }
  // Default to French
  return {
    lastName: 'Nom',
    firstName: 'Prénom',
    club: 'Club',
    boatNumber: 'N° Équipage',
    raceShort: 'Course (abrégé)',
    race: 'Course',
    raceNumber: 'N° Course',
    stroke: 'Nage',
    bowNumber: 'N° Dossard',
    totalPaid: 'Total payé (EUR)',
    outstandingBalance: 'Solde impayé (EUR)',
    paymentStatus: 'Statut de paiement'
  }
}

/**
 * Get column headers for race schedule based on locale
 * @param {string} locale - Locale ('en' or 'fr')
 * @returns {Object} - Object with column header names
 */
function getRaceScheduleHeaders(locale) {
  if (locale === 'en') {
    return {
      raceShort: 'Race (abbrev)',
      race: 'Race',
      raceNumber: 'Race #',
      startTime: 'Start Time'
    }
  }
  // Default to French
  return {
    raceShort: 'Course (abrégé)',
    race: 'Course',
    raceNumber: 'N° Course',
    startTime: 'Heure de départ'
  }
}

/**
 * Get the stroke seat name for a boat
 * @param {Array} seats - Array of seat objects
 * @param {Object} crewMembersDict - Dictionary of crew members
 * @returns {string} - Last name of stroke seat rower
 */
function getStrokeSeatName(seats, crewMembersDict) {
  if (!seats || !crewMembersDict) {
    return ''
  }
  
  const rowerSeats = seats.filter(s => s.type === 'rower' && s.crew_member_id)
  
  if (rowerSeats.length === 0) {
    return ''
  }
  
  const strokeSeat = rowerSeats.reduce((max, seat) => 
    (seat.position > max.position) ? seat : max
  )
  
  const crewMember = crewMembersDict[strokeSeat.crew_member_id]
  return crewMember ? (crewMember.last_name || '') : ''
}

/**
 * Format time in 24-hour format (HH:MM)
 * Converts HH:MM:SS to HH:MM by removing seconds
 * @param {string} time - Time string (HH:MM or HH:MM:SS)
 * @returns {string} - Formatted time (HH:MM)
 */
function formatTime24Hour(time) {
  if (!time) return ''
  
  // If time is in HH:MM:SS format, convert to HH:MM
  const parts = time.split(':')
  if (parts.length >= 2) {
    return `${parts[0]}:${parts[1]}`
  }
  
  return time
}

/**
 * Generate crew member list sheet
 * Lists all crew members participating in eligible boats, sorted by last name
 * 
 * @param {Object} jsonData - The JSON response from backend
 * @param {Object} boatAssignments - Boat assignments from raceNumbering
 * @param {Object} raceAssignments - Race assignments from raceNumbering
 * @param {string} locale - Locale for translations
 * @param {Function} t - Translation function
 * @returns {Array} - Array of crew member row objects
 */
export function generateCrewMemberList(jsonData, boatAssignments, raceAssignments, locale = 'fr', t = null) {
  const { boats, crew_members, team_managers } = jsonData.data
  
  // Get column headers based on locale
  const headers = getCrewMemberListHeaders(locale)
  
  // Create lookup dictionaries
  const crewMembersDict = {}
  for (const member of crew_members) {
    crewMembersDict[member.crew_member_id] = member
  }
  
  const teamManagersDict = {}
  for (const manager of team_managers || []) {
    teamManagersDict[manager.user_id] = manager
  }
  
  // Filter eligible boats
  const eligibleBoats = filterEligibleBoats(boats)
  
  // Collect all crew members from eligible boats
  const crewMemberRows = []
  const processedCrewMembers = new Set() // Track to avoid duplicates
  
  for (const boat of eligibleBoats) {
    const boatId = boat.boat_registration_id
    const assignment = boatAssignments[boatId]
    
    if (!assignment) continue
    
    const raceAssignment = raceAssignments[boat.race_id]
    if (!raceAssignment) continue
    
    // Get race info
    const raceShortName = locale === 'fr' && raceAssignment.shortName
      ? translateShortNameToFrench(raceAssignment.shortName)
      : raceAssignment.shortName
    
    const raceName = t ? t(`races.${raceAssignment.name}`, raceAssignment.name) : raceAssignment.name
    
    // Get stroke seat name
    const strokeName = getStrokeSeatName(boat.seats || [], crewMembersDict)
    
    // Get club from boat_club_display (simplified comma-separated format)
    const clubName = boat.boat_club_display || ''
    
    // Get boat number (handle null gracefully)
    const boatNumber = boat.boat_number || (locale === 'en' ? 'TBD' : 'À déterminer')
    
    // Process each seat
    for (const seat of (boat.seats || [])) {
      if (!seat.crew_member_id) continue
      
      const crewMember = crewMembersDict[seat.crew_member_id]
      if (!crewMember) continue
      
      // Create unique key for this crew member in this boat
      const uniqueKey = `${seat.crew_member_id}-${boatId}`
      
      if (processedCrewMembers.has(uniqueKey)) continue
      processedCrewMembers.add(uniqueKey)
      
      // Get team manager payment data
      const teamManager = teamManagersDict[boat.team_manager_id] || {}
      const totalPaid = teamManager.total_paid !== undefined ? teamManager.total_paid.toFixed(2) : '0.00'
      const outstandingBalance = teamManager.outstanding_balance !== undefined ? teamManager.outstanding_balance.toFixed(2) : '0.00'
      const paymentStatus = teamManager.payment_status || 'No Payment'
      
      crewMemberRows.push({
        [headers.lastName]: crewMember.last_name || '',
        [headers.firstName]: crewMember.first_name || '',
        [headers.club]: clubName,
        [headers.boatNumber]: boatNumber,
        [headers.raceShort]: raceShortName,
        [headers.race]: raceName,
        [headers.raceNumber]: assignment.raceNumber,
        [headers.stroke]: strokeName,
        [headers.bowNumber]: assignment.bowNumber,
        [headers.totalPaid]: totalPaid,
        [headers.outstandingBalance]: outstandingBalance,
        [headers.paymentStatus]: paymentStatus
      })
    }
  }
  
  // Sort by last name alphabetically
  crewMemberRows.sort((a, b) => {
    const nameA = (a[headers.lastName] || '').toLowerCase()
    const nameB = (b[headers.lastName] || '').toLowerCase()
    return nameA.localeCompare(nameB, locale)
  })
  
  return crewMemberRows
}

/**
 * Generate race schedule sheet
 * Lists all races that have boats attached, with race number and start time
 * 
 * @param {Object} jsonData - The JSON response from backend
 * @param {Object} raceAssignments - Race assignments from raceNumbering
 * @param {string} locale - Locale for translations
 * @param {Function} t - Translation function
 * @returns {Array} - Array of race row objects
 */
export function generateRaceSchedule(jsonData, raceAssignments, locale = 'fr', t = null) {
  const { races } = jsonData.data
  
  // Get column headers based on locale
  const headers = getRaceScheduleHeaders(locale)
  
  const raceRows = []
  
  // Debug logging
  console.log('Total races in data:', races.length)
  console.log('Races with assignments:', Object.keys(raceAssignments).length)
  console.log('Race assignments:', raceAssignments)
  
  // Sort races by race number
  const racesWithNumbers = races
    .filter(race => raceAssignments[race.race_id])
    .map(race => ({
      race,
      assignment: raceAssignments[race.race_id]
    }))
    .sort((a, b) => a.assignment.raceNumber - b.assignment.raceNumber)
  
  console.log('Races with numbers:', racesWithNumbers.length)
  
  for (const { race, assignment } of racesWithNumbers) {
    const raceShortName = locale === 'fr' && race.short_name
      ? translateShortNameToFrench(race.short_name)
      : race.short_name
    
    const raceName = t ? t(`races.${race.name}`, race.name) : race.name
    
    raceRows.push({
      [headers.raceShort]: raceShortName,
      [headers.race]: raceName,
      [headers.raceNumber]: assignment.raceNumber,
      [headers.startTime]: formatTime24Hour(assignment.startTime)
    })
  }
  
  return raceRows
}

/**
 * Download Event Program Excel file with multiple sheets
 * @param {Object} jsonData - The JSON response from backend API
 * @param {string} filename - Optional custom filename (without extension)
 * @param {string} locale - Locale for internationalization ('en' or 'fr')
 * @param {Function} t - The i18n translation function
 */
export function downloadEventProgramExcel(jsonData, filename = null, locale = 'fr', t = null) {
  if (!jsonData || !jsonData.data) {
    throw new Error('Invalid data format: expected data object')
  }
  
  const { races, boats, crew_members, config } = jsonData.data
  
  if (!races || !boats || !crew_members) {
    throw new Error('Invalid data format: expected races, boats, and crew_members arrays')
  }
  
  // Filter eligible boats
  const eligibleBoats = filterEligibleBoats(boats)
  
  if (eligibleBoats.length === 0) {
    throw new Error('No eligible boats to export')
  }
  
  // Assign race and bow numbers using shared logic
  const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)
  
  // Generate crew member list
  const crewMemberList = generateCrewMemberList(jsonData, boatAssignments, raceAssignments, locale, t)
  
  // Generate race schedule
  const raceSchedule = generateRaceSchedule(jsonData, raceAssignments, locale, t)
  
  if (crewMemberList.length === 0) {
    throw new Error('No crew members to export')
  }
  
  if (raceSchedule.length === 0) {
    throw new Error('No races to export')
  }
  
  // Create workbook
  const workbook = XLSX.utils.book_new()
  
  // Sheet names based on locale
  const crewListSheetName = locale === 'en' ? 'Crew Member List' : 'Liste des équipiers'
  const raceScheduleSheetName = locale === 'en' ? 'Race Schedule' : 'Programme des courses'
  
  // Add crew member list sheet
  const crewSheet = XLSX.utils.json_to_sheet(crewMemberList)
  XLSX.utils.book_append_sheet(workbook, crewSheet, crewListSheetName)
  
  // Add race schedule sheet
  const raceSheet = XLSX.utils.json_to_sheet(raceSchedule)
  XLSX.utils.book_append_sheet(workbook, raceSheet, raceScheduleSheetName)
  
  // Generate filename with timestamp if not provided
  const timestamp = formatDateForFilename()
  const finalFilename = filename || `programme_evenement_${timestamp}`
  
  // Write file
  XLSX.writeFile(workbook, `${finalFilename}.xlsx`)
}
