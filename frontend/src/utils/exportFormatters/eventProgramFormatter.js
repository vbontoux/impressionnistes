/**
 * Event Program Export Formatter
 * Creates an Excel file with crew member list and race schedule for race day printing
 */

import ExcelJS from 'exceljs'
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
      race: 'Race',
      raceNumber: 'Race #',
      raceShort: 'Race (abbrev)',
      boatNumber: 'Crew #',
      bowNumber: 'Bow #',
      lastName: 'Last Name',
      firstName: 'First Name',
      club: 'Club',
      age: 'Age',
      gender: 'Gender',
      licenseNumber: 'License #',
      placeInBoat: 'Place in boat',
      assignedBoat: 'Assigned Boat'
    }
  }
  // Default to French
  return {
    race: 'Course',
    raceNumber: 'N° Course',
    raceShort: 'Course (abrégé)',
    boatNumber: 'N° Équipage',
    bowNumber: 'N° Dossard',
    lastName: 'Nom',
    firstName: 'Prénom',
    club: 'Club',
    age: 'Âge',
    gender: 'Genre',
    licenseNumber: 'N° Licence',
    placeInBoat: 'Place dans le bateau',
    assignedBoat: 'Bateau assigné'
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
      startTime: 'Start Time',
      boatCount: 'Number of Boats',
      participantCount: 'Number of Participants'
    }
  }
  // Default to French
  return {
    raceShort: 'Course (abrégé)',
    race: 'Course',
    raceNumber: 'N° Course',
    startTime: 'Heure de départ',
    boatCount: 'Nombre de bateaux',
    participantCount: 'Nombre de participants'
  }
}

/**
 * Get column headers for crews in races sheet based on locale
 * @param {string} locale - Locale ('en' or 'fr')
 * @returns {Array} - Array of column header names (51 columns total)
 */
function getCrewsInRacesHeaders(locale) {
  const isEnglish = locale === 'en'
  
  const baseHeaders = [
    isEnglish ? 'Race' : 'Course',
    isEnglish ? 'Start Time' : 'Heure de départ',
    isEnglish ? 'Race #' : 'N° Course',
    isEnglish ? 'Race (abbrev)' : 'Course (abrégé)',
    isEnglish ? 'Crew #' : 'N° Équipage',
    isEnglish ? 'Bow #' : 'N° Dossard',
    isEnglish ? 'Boat assignment' : 'Bateau assigné'
  ]
  
  // Add headers for 9 crew members (5 fields each = 45 columns)
  const memberHeaders = []
  for (let i = 1; i <= 9; i++) {
    const memberPrefix = isEnglish ? `Member ${i}` : `Équipier ${i}`
    memberHeaders.push(
      `${memberPrefix} ${isEnglish ? 'Last Name' : 'Nom'}`,
      `${memberPrefix} ${isEnglish ? 'First Name' : 'Prénom'}`,
      `${memberPrefix} ${isEnglish ? 'Club' : 'Club'}`,
      `${memberPrefix} ${isEnglish ? 'Age' : 'Âge'}`,
      `${memberPrefix} ${isEnglish ? 'Gender' : 'Genre'}`
    )
  }
  
  return [...baseHeaders, ...memberHeaders]
}

/**
 * Get column headers for synthesis sheet based on locale
 * @param {string} locale - Locale ('en' or 'fr')
 * @returns {Array} - Array of column header names (7 columns total)
 */
function getSynthesisHeaders(locale) {
  const isEnglish = locale === 'en'
  
  return [
    isEnglish ? 'Club' : 'Club',
    isEnglish ? 'First name + Last name' : 'Prénom + Nom',
    isEnglish ? 'Email' : 'Email',
    isEnglish ? 'Phone #' : 'N° Téléphone',
    isEnglish ? 'Number of assigned boats' : 'Nombre de bateaux assignés',
    isEnglish ? 'Number of crews in marathon' : 'Nombre d\'équipages en marathon',
    isEnglish ? 'Number of crews in semi-marathon' : 'Nombre d\'équipages en semi-marathon'
  ]
}

/**
 * Format team manager name
 * @param {Object} manager - Team manager object
 * @returns {string} - Formatted name "FirstName LastName"
 */
export function formatTeamManagerName(manager) {
  if (!manager) return ''
  
  const firstName = manager.first_name || ''
  const lastName = manager.last_name || ''
  
  // Handle missing names gracefully
  if (firstName && lastName) {
    return `${firstName} ${lastName}`
  }
  
  if (firstName) {
    return firstName
  }
  
  if (lastName) {
    return lastName
  }
  
  return ''
}

/**
 * Format gender for display based on locale
 * @param {string} gender - Gender code ('M' or 'F')
 * @param {string} locale - Locale for translations
 * @returns {string} - Formatted gender
 */
export function formatGender(gender, locale = 'fr') {
  if (!gender) return ''
  
  const genderUpper = gender.toUpperCase()
  
  if (locale === 'en') {
    // English: M for Men, W for Women
    return genderUpper === 'M' ? 'M' : genderUpper === 'F' ? 'W' : gender
  }
  
  // French: H for Homme, F for Femme
  return genderUpper === 'M' ? 'H' : genderUpper === 'F' ? 'F' : gender
}

/**
 * Format seat type for display
 * @param {Object} seat - Seat object with type and position
 * @param {string} locale - Locale for translations
 * @returns {string} - Formatted seat type (e.g., "Rower 1", "Cox")
 */
export function formatSeatType(seat, locale = 'fr') {
  if (!seat) return ''
  
  // If seat_type is already provided (from test data or backend), use it
  if (seat.seat_type) {
    return seat.seat_type
  }
  
  // Otherwise, generate it from type and position
  const type = seat.type || 'rower'
  const position = seat.position || 0
  
  if (type === 'cox') {
    return locale === 'en' ? 'Cox' : 'Barreur'
  }
  
  // For rowers, show position
  if (locale === 'en') {
    return `Rower ${position}`
  }
  
  return `Rameur ${position}`
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
 * Format assigned boat information
 * @param {Object} boat - Boat object with assigned boat fields
 * @returns {string} - Formatted assigned boat string
 */
export function formatAssignedBoat(boat) {
  if (!boat) return ''
  
  const name = boat.assigned_boat_name || ''
  const comment = boat.assigned_boat_comment || ''
  
  if (name && comment) {
    return `${name} - ${comment}`
  }
  
  if (name) {
    return name
  }
  
  return ''
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
  const { boats, crew_members, team_managers, races } = jsonData.data
  
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
  
  // Create race lookup by race_id to get display_order
  const racesDict = {}
  for (const race of races || []) {
    racesDict[race.race_id] = race
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
    const race = racesDict[boat.race_id]
    // Use display_order if available, otherwise fall back to raceNumber
    const raceNumber = race?.display_order ?? assignment.raceNumber
    const raceName = t ? t(`races.${raceAssignment.name}`, raceAssignment.name) : raceAssignment.name
    const raceShortName = race?.short_name || ''
    // Translate race abbreviation to French if locale is French
    const translatedRaceShort = locale === 'fr' ? translateShortNameToFrench(raceShortName) : raceShortName
    
    // Get club from boat_club_display (simplified comma-separated format)
    const clubName = boat.boat_club_display || ''
    
    // Get boat number (handle null gracefully)
    const boatNumber = boat.boat_number || (locale === 'en' ? 'TBD' : 'À déterminer')
    
    // Get assigned boat information
    const assignedBoat = formatAssignedBoat(boat)
    
    // Process each seat
    for (const seat of (boat.seats || [])) {
      if (!seat.crew_member_id) {
        console.warn(`Boat ${boatId} has a seat without crew_member_id`)
        continue
      }
      
      const crewMember = crewMembersDict[seat.crew_member_id]
      if (!crewMember) {
        console.warn(`Crew member ${seat.crew_member_id} not found in crew_members list for boat ${boatId}`)
        // Use placeholder values for missing crew member
        const placeholderMember = {
          last_name: locale === 'en' ? 'Unknown' : 'Inconnu',
          first_name: '',
          age: '',
          gender: '',
          license_number: ''
        }
        
        // Create unique key for this placeholder
        const uniqueKey = `${seat.crew_member_id}-${boatId}`
        
        if (processedCrewMembers.has(uniqueKey)) continue
        processedCrewMembers.add(uniqueKey)
        
        // Add row with placeholder data
        crewMemberRows.push({
          [headers.race]: raceName,
          [headers.raceNumber]: raceNumber,
          [headers.raceShort]: translatedRaceShort,
          [headers.boatNumber]: boatNumber,
          [headers.bowNumber]: assignment.bowNumber,
          [headers.lastName]: placeholderMember.last_name,
          [headers.firstName]: placeholderMember.first_name,
          [headers.club]: clubName,
          [headers.age]: placeholderMember.age,
          [headers.gender]: placeholderMember.gender,
          [headers.licenseNumber]: placeholderMember.license_number,
          [headers.placeInBoat]: formatSeatType(seat, locale),
          [headers.assignedBoat]: assignedBoat
        })
        continue
      }
      
      // Create unique key for this crew member in this boat
      const uniqueKey = `${seat.crew_member_id}-${boatId}`
      
      if (processedCrewMembers.has(uniqueKey)) continue
      processedCrewMembers.add(uniqueKey)
      
      // Column order: Race, Race #, Race (abbrev), Crew #, Bow #, Last name, First name, Club, Age, Gender, License #, Place in boat, Assigned Boat
      crewMemberRows.push({
        [headers.race]: raceName,
        [headers.raceNumber]: raceNumber,
        [headers.raceShort]: translatedRaceShort,
        [headers.boatNumber]: boatNumber,
        [headers.bowNumber]: assignment.bowNumber,
        [headers.lastName]: crewMember.last_name || '',
        [headers.firstName]: crewMember.first_name || '',
        [headers.club]: clubName,
        [headers.age]: crewMember.age || '',
        [headers.gender]: formatGender(crewMember.gender, locale),
        [headers.licenseNumber]: crewMember.license_number || '',
        [headers.placeInBoat]: formatSeatType(seat, locale),
        [headers.assignedBoat]: assignedBoat
      })
    }
  }
  
  // Sort by race number (display_order) first, then by last name alphabetically
  crewMemberRows.sort((a, b) => {
    // First sort by race number (display_order)
    const raceA = a[headers.raceNumber] || 0
    const raceB = b[headers.raceNumber] || 0
    
    if (raceA !== raceB) {
      return raceA - raceB
    }
    
    // Then sort by last name
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
  const { races, boats } = jsonData.data
  
  // Get column headers based on locale
  const headers = getRaceScheduleHeaders(locale)
  
  // Filter eligible boats
  const eligibleBoats = filterEligibleBoats(boats)
  
  // Count boats and participants per race
  const raceStats = {}
  for (const boat of eligibleBoats) {
    const raceId = boat.race_id
    if (!raceStats[raceId]) {
      raceStats[raceId] = {
        boatCount: 0,
        participantCount: 0
      }
    }
    
    raceStats[raceId].boatCount++
    // Count crew members (seats) in this boat
    const crewCount = (boat.seats || []).length
    raceStats[raceId].participantCount += crewCount
  }
  
  const raceRows = []
  
  // Debug logging
  console.log('Total races in data:', races.length)
  console.log('Races with assignments:', Object.keys(raceAssignments).length)
  console.log('Race assignments:', raceAssignments)
  
  // Sort races by display_order
  const racesWithNumbers = races
    .filter(race => raceAssignments[race.race_id])
    .map(race => ({
      race,
      assignment: raceAssignments[race.race_id]
    }))
    .sort((a, b) => (a.race.display_order || 0) - (b.race.display_order || 0))
  
  console.log('Races with numbers:', racesWithNumbers.length)
  
  for (const { race, assignment } of racesWithNumbers) {
    const raceShortName = race.short_name || ''
    // Translate race abbreviation to French if locale is French
    const translatedRaceShort = locale === 'fr' ? translateShortNameToFrench(raceShortName) : raceShortName
    
    const raceName = t ? t(`races.${race.name}`, race.name) : race.name
    
    // Get stats for this race (default to 0 if no boats)
    const stats = raceStats[race.race_id] || { boatCount: 0, participantCount: 0 }
    
    raceRows.push({
      [headers.raceShort]: translatedRaceShort,
      [headers.race]: raceName,
      [headers.raceNumber]: race.display_order || assignment.raceNumber,
      [headers.startTime]: formatTime24Hour(assignment.startTime),
      [headers.boatCount]: stats.boatCount,
      [headers.participantCount]: stats.participantCount
    })
  }
  
  return raceRows
}

/**
 * Generate crews in races sheet
 * Lists all crews organized by race with full member details (up to 9 members)
 * 
 * @param {Object} jsonData - The JSON response from backend
 * @param {Object} boatAssignments - Boat assignments from raceNumbering
 * @param {Object} raceAssignments - Race assignments from raceNumbering
 * @param {string} locale - Locale for translations
 * @param {Function} t - Translation function
 * @returns {Array} - 2D array with headers and data rows
 */
export function generateCrewsInRaces(jsonData, boatAssignments, raceAssignments, locale = 'fr', t = null) {
  const { boats, crew_members, races } = jsonData.data
  
  // Get column headers based on locale
  const headers = getCrewsInRacesHeaders(locale)
  
  // Create lookup dictionary for crew members
  const crewMembersDict = {}
  for (const member of crew_members) {
    crewMembersDict[member.crew_member_id] = member
  }
  
  // Create race lookup by race_id to get display_order
  const racesDict = {}
  for (const race of races || []) {
    racesDict[race.race_id] = race
  }
  
  // Filter eligible boats
  const eligibleBoats = filterEligibleBoats(boats)
  
  // Sort boats by race display_order
  const sortedBoats = eligibleBoats
    .map(boat => {
      const assignment = boatAssignments[boat.boat_registration_id]
      const race = racesDict[boat.race_id]
      // Use display_order if available, otherwise fall back to raceNumber
      const raceNumber = race?.display_order ?? assignment?.raceNumber ?? 0
      return {
        boat,
        assignment,
        raceNumber
      }
    })
    .filter(item => item.assignment) // Only include boats with assignments
    .sort((a, b) => a.raceNumber - b.raceNumber)
  
  // Build data rows
  const dataRows = []
  
  for (const { boat, assignment, raceNumber } of sortedBoats) {
    const raceAssignment = raceAssignments[boat.race_id]
    if (!raceAssignment) continue
    
    // Get race info
    const race = racesDict[boat.race_id]
    const raceName = t ? t(`races.${raceAssignment.name}`, raceAssignment.name) : raceAssignment.name
    const raceShortName = race?.short_name || ''
    // Translate race abbreviation to French if locale is French
    const translatedRaceShort = locale === 'fr' ? translateShortNameToFrench(raceShortName) : raceShortName
    
    // Get start time from race assignment
    const startTime = formatTime24Hour(raceAssignment.startTime)
    
    // Get boat number (handle null gracefully)
    const boatNumber = boat.boat_number || (locale === 'en' ? 'TBD' : 'À déterminer')
    
    // Get assigned boat information
    const assignedBoat = formatAssignedBoat(boat)
    
    // Start building the row with base columns
    const row = [
      raceName,
      startTime,
      raceNumber,
      translatedRaceShort,
      boatNumber,
      assignment.bowNumber,
      assignedBoat
    ]
    
    // Get crew members for this boat (up to 9)
    const seats = boat.seats || []
    const crewMembers = seats
      .map(seat => {
        if (!seat.crew_member_id) {
          console.warn(`Boat ${boat.boat_registration_id} has a seat without crew_member_id`)
          return null
        }
        const member = crewMembersDict[seat.crew_member_id]
        if (!member) {
          console.warn(`Crew member ${seat.crew_member_id} not found for boat ${boat.boat_registration_id}`)
          // Return placeholder for missing crew member
          return {
            last_name: locale === 'en' ? 'Unknown' : 'Inconnu',
            first_name: '',
            club_affiliation: '',
            age: '',
            gender: ''
          }
        }
        return member
      })
      .filter(member => member !== null)
    
    // Add crew member data (5 fields per member, up to 9 members)
    for (let i = 0; i < 9; i++) {
      if (i < crewMembers.length) {
        const member = crewMembers[i]
        row.push(
          member.last_name || '',
          member.first_name || '',
          member.club_affiliation || '',
          member.age || '',
          formatGender(member.gender, locale)
        )
      } else {
        // Empty columns for missing members
        row.push('', '', '', '', '')
      }
    }
    
    dataRows.push(row)
  }
  
  // Return 2D array with headers and data
  return [headers, ...dataRows]
}

/**
 * Generate synthesis sheet by club manager
 * Aggregates boat and crew counts by team manager
 * 
 * @param {Object} jsonData - The JSON response from backend
 * @param {Object} boatAssignments - Boat assignments from raceNumbering
 * @param {string} locale - Locale for translations
 * @param {Function} t - Translation function
 * @returns {Array} - 2D array with headers and data rows
 */
export function generateSynthesis(jsonData, boatAssignments, locale = 'fr', t = null) {
  const { boats, team_managers } = jsonData.data
  
  // Get column headers based on locale
  const headers = getSynthesisHeaders(locale)
  
  // Create lookup dictionary for team managers
  const teamManagersDict = {}
  for (const manager of team_managers || []) {
    teamManagersDict[manager.user_id] = manager
  }
  
  // Filter eligible boats
  const eligibleBoats = filterEligibleBoats(boats)
  
  // Group boats by team manager and calculate counts
  const managerStats = {}
  
  for (const boat of eligibleBoats) {
    const managerId = boat.team_manager_id
    if (!managerId) {
      console.warn(`Boat ${boat.boat_registration_id} has no team_manager_id - skipping from synthesis`)
      continue
    }
    
    const manager = teamManagersDict[managerId]
    if (!manager) {
      console.warn(`Team manager ${managerId} not found for boat ${boat.boat_registration_id} - skipping from synthesis`)
      continue
    }
    
    // Initialize stats for this manager if not exists
    if (!managerStats[managerId]) {
      managerStats[managerId] = {
        manager,
        assignedBoats: 0,
        marathonCrews: 0,
        semiMarathonCrews: 0
      }
    }
    
    const stats = managerStats[managerId]
    
    // Count assigned boats (non-empty assigned_boat_identifier)
    if (boat.assigned_boat_identifier) {
      stats.assignedBoats++
    }
    
    // Count by event type (42km = Marathon, 21km = Semi-Marathon)
    if (boat.event_type === '42km' || boat.event_type === 'Marathon') {
      stats.marathonCrews++
    } else if (boat.event_type === '21km' || boat.event_type === 'Semi-Marathon') {
      stats.semiMarathonCrews++
    }
  }
  
  // Build data rows
  const dataRows = []
  
  for (const stats of Object.values(managerStats)) {
    const manager = stats.manager
    
    dataRows.push([
      manager.club_affiliation || '',
      formatTeamManagerName(manager),
      manager.email || '',
      manager.phone || '',
      stats.assignedBoats,
      stats.marathonCrews,
      stats.semiMarathonCrews
    ])
  }
  
  // Return 2D array with headers and data
  return [headers, ...dataRows]
}

/**
 * Apply print formatting to a worksheet using ExcelJS
 * Adds borders, colors, and print area settings
 * 
 * @param {Object} worksheet - ExcelJS worksheet object
 * @param {Object} options - Formatting options
 * @param {string} options.printArea - Print area range (e.g., "B:M")
 * @param {string} options.alternateBy - Alternate colors by 'crew', 'race', or 'row'
 * @param {Array} options.data - Original data array for grouping logic
 * @param {string} options.groupColumn - Column name to group by (e.g., 'Crew #', 'Race #')
 * @param {Array} options.wrapTextColumns - Array of column letters to enable text wrapping (e.g., ['G', 'H'])
 */
function applyPrintFormatting(worksheet, options = {}) {
  const { printArea, alternateBy, data, groupColumn, wrapTextColumns = [] } = options
  
  // Define colors (blue/gray tones)
  const headerBg = 'D0E0F0' // Light blue for header
  const altColor1 = 'F5F5F5' // Light gray
  const altColor2 = 'FFFFFF' // White
  
  // Border styles
  const thinBorder = {
    top: { style: 'thin', color: { argb: 'FF000000' } },
    bottom: { style: 'thin', color: { argb: 'FF000000' } },
    left: { style: 'thin', color: { argb: 'FF000000' } },
    right: { style: 'thin', color: { argb: 'FF000000' } }
  }
  
  const thickBorder = {
    top: { style: 'medium', color: { argb: 'FF000000' } },
    bottom: { style: 'medium', color: { argb: 'FF000000' } },
    left: { style: 'medium', color: { argb: 'FF000000' } },
    right: { style: 'medium', color: { argb: 'FF000000' } }
  }
  
  // Track current group for alternating colors
  let currentGroup = null
  let groupIndex = 0
  
  // Apply formatting to each row
  worksheet.eachRow((row, rowNumber) => {
    // Determine if this is a new group (for alternating colors)
    if (alternateBy && data && groupColumn && rowNumber > 1) {
      const dataRow = data[rowNumber - 2] // -2 because rowNumber is 1-based and row 1 is header
      if (dataRow) {
        const groupValue = dataRow[groupColumn]
        if (groupValue !== currentGroup) {
          currentGroup = groupValue
          groupIndex++
        }
      }
    }
    
    // Determine background color
    let bgColor = null
    if (rowNumber === 1) {
      // Header row
      bgColor = headerBg
    } else if (alternateBy === 'row') {
      // Alternate every row
      bgColor = (rowNumber % 2 === 0) ? altColor1 : altColor2
    } else if (alternateBy && groupColumn) {
      // Alternate by group
      bgColor = (groupIndex % 2 === 0) ? altColor1 : altColor2
    }
    
    // Apply formatting to each cell in the row
    row.eachCell({ includeEmpty: true }, (cell, colNumber) => {
      // Apply borders
      if (rowNumber === 1) {
        // Header row gets thick border and bold font
        cell.border = thickBorder
        cell.font = { bold: true, size: 11 }
      } else {
        // Data rows get thin border
        cell.border = thinBorder
        cell.font = { size: 10 }
      }
      
      // Apply background color
      if (bgColor) {
        cell.fill = {
          type: 'pattern',
          pattern: 'solid',
          fgColor: { argb: 'FF' + bgColor }
        }
      }
      
      // Determine if this column should have text wrapping
      const columnLetter = String.fromCharCode(64 + colNumber) // Convert column number to letter (1=A, 2=B, etc.)
      const shouldWrapText = wrapTextColumns.includes(columnLetter)
      
      // Center alignment for better readability
      cell.alignment = {
        vertical: 'middle',
        horizontal: 'left',
        wrapText: shouldWrapText
      }
    })
  })
  
  // Set print area if specified
  if (printArea) {
    worksheet.pageSetup.printArea = printArea
  }
  
  // Auto-fit columns with reasonable limits
  worksheet.columns.forEach(column => {
    let maxLength = 10
    column.eachCell({ includeEmpty: false }, cell => {
      const cellValue = cell.value ? cell.value.toString() : ''
      maxLength = Math.max(maxLength, cellValue.length)
    })
    column.width = Math.min(maxLength + 2, 50)
  })
  
  // Set page setup for printing
  worksheet.pageSetup = {
    ...worksheet.pageSetup,
    orientation: 'landscape',
    fitToPage: true,
    fitToWidth: 1,
    fitToHeight: 0, // Allow multiple pages vertically
    paperSize: 9, // A4
    margins: {
      left: 0.5,
      right: 0.5,
      top: 0.75,
      bottom: 0.75,
      header: 0.3,
      footer: 0.3
    }
  }
}

/**
 * Download Event Program Excel file with multiple sheets using ExcelJS
 * @param {Object} jsonData - The JSON response from backend API
 * @param {string} filename - Optional custom filename (without extension)
 * @param {string} locale - Locale for internationalization ('en' or 'fr')
 * @param {Function} t - The i18n translation function
 */
export async function downloadEventProgramExcel(jsonData, filename = null, locale = 'fr', t = null) {
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
  
  // Generate crews in races (Sheet 3)
  const crewsInRacesData = generateCrewsInRaces(jsonData, boatAssignments, raceAssignments, locale, t)
  
  // Generate synthesis (Sheet 4)
  const synthesisData = generateSynthesis(jsonData, boatAssignments, locale, t)
  
  if (crewMemberList.length === 0) {
    throw new Error('No crew members to export')
  }
  
  if (raceSchedule.length === 0) {
    throw new Error('No races to export')
  }
  
  if (crewsInRacesData.length === 0) {
    throw new Error('No crews in races to export')
  }
  
  if (synthesisData.length === 0) {
    throw new Error('No synthesis data to export')
  }
  
  // Create workbook using ExcelJS
  const workbook = new ExcelJS.Workbook()
  workbook.creator = 'Course des Impressionnistes'
  workbook.created = new Date()
  
  // Sheet names based on locale
  const crewListSheetName = locale === 'en' ? 'Crew Member List' : 'Liste des équipiers'
  const raceScheduleSheetName = locale === 'en' ? 'Race Schedule' : 'Programme des courses'
  const crewsInRacesSheetName = locale === 'en' ? 'Crews in Races' : 'Équipages par course'
  const synthesisSheetName = locale === 'en' ? 'Synthesis' : 'Synthèse'
  
  // Get header objects for grouping
  const crewHeaders = getCrewMemberListHeaders(locale)
  const raceHeaders = getRaceScheduleHeaders(locale)
  
  // Add crew member list sheet (Sheet 1)
  const crewSheet = workbook.addWorksheet(crewListSheetName)
  const crewColumns = Object.keys(crewMemberList[0] || {}).map(key => ({
    header: key,
    key: key
  }))
  crewSheet.columns = crewColumns
  crewSheet.addRows(crewMemberList)
  applyPrintFormatting(crewSheet, {
    printArea: 'B:M', // Columns B to M
    alternateBy: 'crew',
    data: crewMemberList,
    groupColumn: crewHeaders.boatNumber, // Group by Crew #
    wrapTextColumns: ['H', 'M'] // Enable text wrapping for Club (H) and Assigned Boat (M) columns
  })
  
  // Add race schedule sheet (Sheet 2)
  const raceSheet = workbook.addWorksheet(raceScheduleSheetName)
  const raceColumns = Object.keys(raceSchedule[0] || {}).map(key => ({
    header: key,
    key: key
  }))
  raceSheet.columns = raceColumns
  raceSheet.addRows(raceSchedule)
  applyPrintFormatting(raceSheet, {
    printArea: 'A:F', // Columns A to F (all columns)
    alternateBy: 'race',
    data: raceSchedule,
    groupColumn: raceHeaders.raceNumber // Group by Race #
  })
  
  // Add crews in races sheet (Sheet 3)
  const crewsInRacesSheet = workbook.addWorksheet(crewsInRacesSheetName)
  const crewsInRacesHeaders = crewsInRacesData[0]
  const crewsInRacesRows = crewsInRacesData.slice(1)
  
  // Convert 2D array to object format for ExcelJS
  const crewsInRacesObjects = crewsInRacesRows.map(row => {
    const obj = {}
    crewsInRacesHeaders.forEach((header, index) => {
      obj[header] = row[index]
    })
    return obj
  })
  
  const crewsInRacesColumns = crewsInRacesHeaders.map(header => ({
    header: header,
    key: header
  }))
  crewsInRacesSheet.columns = crewsInRacesColumns
  crewsInRacesSheet.addRows(crewsInRacesObjects)
  
  const raceNumHeader = locale === 'en' ? 'Race #' : 'N° Course'
  applyPrintFormatting(crewsInRacesSheet, {
    printArea: 'B:L', // Columns B to L (includes Member 1 Club, Age, Gender)
    alternateBy: 'race',
    data: crewsInRacesObjects,
    groupColumn: raceNumHeader, // Group by Race #
    wrapTextColumns: ['G', 'J'] // Enable text wrapping for Boat assignment (G) and Member 1 Club (J)
  })
  
  // Add synthesis sheet (Sheet 4)
  const synthesisSheet = workbook.addWorksheet(synthesisSheetName)
  const synthesisHeaders = synthesisData[0]
  const synthesisRows = synthesisData.slice(1)
  
  // Convert 2D array to object format for ExcelJS
  const synthesisObjects = synthesisRows.map(row => {
    const obj = {}
    synthesisHeaders.forEach((header, index) => {
      obj[header] = row[index]
    })
    return obj
  })
  
  const synthesisColumns = synthesisHeaders.map(header => ({
    header: header,
    key: header
  }))
  synthesisSheet.columns = synthesisColumns
  synthesisSheet.addRows(synthesisObjects)
  
  applyPrintFormatting(synthesisSheet, {
    printArea: null, // All columns
    alternateBy: 'row', // Alternate every row
    wrapTextColumns: ['A'] // Enable text wrapping for Club column (A)
  })
  
  // Generate filename with timestamp if not provided
  const timestamp = formatDateForFilename()
  const finalFilename = filename || `programme_evenement_${timestamp}`
  
  // Write file to buffer and trigger download
  const buffer = await workbook.xlsx.writeBuffer()
  const blob = new Blob([buffer], { 
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
  })
  
  // Create download link
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${finalFilename}.xlsx`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}
