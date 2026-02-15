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
  const { races } = jsonData.data
  
  // Get column headers based on locale
  const headers = getRaceScheduleHeaders(locale)
  
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
    
    raceRows.push({
      [headers.raceShort]: translatedRaceShort,
      [headers.race]: raceName,
      [headers.raceNumber]: race.display_order || assignment.raceNumber,
      [headers.startTime]: formatTime24Hour(assignment.startTime)
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
  
  // Create workbook
  const workbook = XLSX.utils.book_new()
  
  // Sheet names based on locale
  const crewListSheetName = locale === 'en' ? 'Crew Member List' : 'Liste des équipiers'
  const raceScheduleSheetName = locale === 'en' ? 'Race Schedule' : 'Programme des courses'
  const crewsInRacesSheetName = locale === 'en' ? 'Crews in Races' : 'Équipages par course'
  const synthesisSheetName = locale === 'en' ? 'Synthesis' : 'Synthèse'
  
  // Add crew member list sheet
  const crewSheet = XLSX.utils.json_to_sheet(crewMemberList)
  XLSX.utils.book_append_sheet(workbook, crewSheet, crewListSheetName)
  
  // Add race schedule sheet
  const raceSheet = XLSX.utils.json_to_sheet(raceSchedule)
  XLSX.utils.book_append_sheet(workbook, raceSheet, raceScheduleSheetName)
  
  // Add crews in races sheet (Sheet 3)
  // Note: generateCrewsInRaces returns 2D array with headers, use aoa_to_sheet
  const crewsInRacesSheet = XLSX.utils.aoa_to_sheet(crewsInRacesData)
  XLSX.utils.book_append_sheet(workbook, crewsInRacesSheet, crewsInRacesSheetName)
  
  // Add synthesis sheet (Sheet 4)
  // Note: generateSynthesis returns 2D array with headers, use aoa_to_sheet
  const synthesisSheet = XLSX.utils.aoa_to_sheet(synthesisData)
  XLSX.utils.book_append_sheet(workbook, synthesisSheet, synthesisSheetName)
  
  // Generate filename with timestamp if not provided
  const timestamp = formatDateForFilename()
  const finalFilename = filename || `programme_evenement_${timestamp}`
  
  // Write file
  XLSX.writeFile(workbook, `${finalFilename}.xlsx`)
}
