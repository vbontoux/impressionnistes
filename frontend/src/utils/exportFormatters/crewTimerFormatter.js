/**
 * CrewTimer Export Formatter
 * Converts JSON data from the backend API to CrewTimer Excel format
 */

import * as XLSX from 'xlsx'
import { formatDateForFilename } from './shared.js'
import { assignRaceAndBowNumbers, filterEligibleBoats } from './raceNumbering.js'
import { formatAverageAge } from '../formatters.js'

/**
 * Format time in 12-hour format with AM/PM (e.g., "7:00:00 AM")
 * @param {string} time24 - Time in 24-hour format (HH:MM or HH:MM:SS)
 * @param {number} additionalSeconds - Additional seconds to add to the time
 * @returns {string} - Time in 12-hour format with AM/PM
 */
export function formatTime12Hour(time24, additionalSeconds = 0) {
  if (!time24) return ''
  
  try {
    // Parse HH:MM or HH:MM:SS format
    const parts = time24.split(':').map(Number)
    const hours = parts[0] || 0
    const minutes = parts[1] || 0
    const seconds = parts[2] || 0
    
    // Calculate total seconds
    let totalSeconds = hours * 3600 + minutes * 60 + seconds + additionalSeconds
    
    // Handle day overflow (shouldn't happen in practice)
    totalSeconds = totalSeconds % 86400
    
    // Convert back to hours, minutes, seconds
    const finalHours = Math.floor(totalSeconds / 3600)
    const finalMinutes = Math.floor((totalSeconds % 3600) / 60)
    const finalSeconds = totalSeconds % 60
    
    // Convert to 12-hour format
    const period = finalHours >= 12 ? 'PM' : 'AM'
    const hours12 = finalHours === 0 ? 12 : (finalHours > 12 ? finalHours - 12 : finalHours)
    
    // Format as H:MM:SS AM/PM (no leading zero for hours)
    return `${hours12}:${String(finalMinutes).padStart(2, '0')}:${String(finalSeconds).padStart(2, '0')} ${period}`
  } catch (error) {
    console.error('Error formatting time:', error)
    return ''
  }
}

/**
 * Translate short_name from English to French
 * Only translates gender markers (second position): W (woman) → F (femme), X (mixed) → M (mixte), M (men) → H (homme)
 * Age category markers (first position like M for Master, S for Senior, J for Junior) remain unchanged
 * @param {string} shortName - The short name in English (e.g., "MW4X+Y")
 * @returns {string} - Translated short name (e.g., "MF4X+Y")
 */
export function translateShortNameToFrench(shortName) {
  if (!shortName) return ''
  
  // Short name format: [AgeCategory][Gender][BoatType]
  // Examples: MW4X+Y (Master Women), SH8+ (Senior Men), J16F2X (Junior 16 Women)
  
  // Only translate the gender marker (typically position 1, or after J16/J18)
  let translated = ''
  
  for (let i = 0; i < shortName.length; i++) {
    const char = shortName[i]
    const prevChar = i > 0 ? shortName[i - 1] : ''
    
    // Check if this is a gender marker (comes after age category or at position 1)
    const isGenderPosition = (
      // Position 1 (after single letter age category like M, S)
      (i === 1 && /[MSJX]/.test(prevChar)) ||
      // After J16 or J18
      (i === 3 && shortName.substring(0, 3).match(/J1[68]/))
    )
    
    if (isGenderPosition) {
      // Translate gender markers
      if (char === 'W') {
        translated += 'F' // Women → Femme
      } else if (char === 'X') {
        translated += 'M' // Mixed → Mixte
      } else if (char === 'M') {
        translated += 'H' // Men → Homme
      } else {
        translated += char
      }
    } else {
      // Keep all other characters unchanged (age category, boat type, etc.)
      translated += char
    }
  }
  
  return translated
}

/**
 * Calculate average age of crew members
 * @param {Array} crewMembers - Array of crew member objects with age field
 * @returns {number} - Average age rounded to nearest integer
 */
export function calculateAverageAge(crewMembers) {
  if (!crewMembers || crewMembers.length === 0) {
    return 0
  }
  
  try {
    const ages = []
    
    for (const member of crewMembers) {
      // Use the age provided by the backend
      if (member.age !== null && member.age !== undefined) {
        ages.push(member.age)
      }
    }
    
    if (ages.length > 0) {
      return Math.round(ages.reduce((sum, age) => sum + age, 0) / ages.length)
    }
    return 0
  } catch (error) {
    console.error('Error calculating average age:', error)
    return 0
  }
}

/**
 * Get the last name of the stroke seat rower
 * The stroke seat is the highest position rower (not cox)
 * @param {Array} seats - Array of seat objects
 * @param {Object} crewMembersDict - Dictionary mapping crew_member_id to crew member data
 * @returns {string} - Last name of stroke seat rower
 */
export function getStrokeSeatName(seats, crewMembersDict) {
  if (!seats || !crewMembersDict) {
    return ''
  }
  
  // Find all rower seats (exclude cox)
  const rowerSeats = seats.filter(s => s.type === 'rower' && s.crew_member_id)
  
  if (rowerSeats.length === 0) {
    return ''
  }
  
  // Find the highest position rower (stroke seat)
  const strokeSeat = rowerSeats.reduce((max, seat) => 
    (seat.position > max.position) ? seat : max
  )
  
  const crewMemberId = strokeSeat.crew_member_id
  if (!crewMemberId) {
    return ''
  }
  
  // Get crew member data
  const crewMember = crewMembersDict[crewMemberId]
  if (!crewMember) {
    return ''
  }
  
  return crewMember.last_name || ''
}

/**
 * Convert races JSON data to CrewTimer format
 * @param {Object} jsonData - The JSON response from the backend API
 * @param {string} locale - The locale for internationalization ('en' or 'fr')
 * @param {Function} t - The i18n translation function
 * @returns {Array} - Array of CrewTimer row objects
 */
export function formatRacesToCrewTimer(jsonData, locale = 'en', t = null) {
  if (!jsonData || !jsonData.data) {
    throw new Error('Invalid data format: expected data object')
  }
  
  const { races, boats, crew_members, team_managers, config } = jsonData.data
  
  if (!races || !boats || !crew_members) {
    throw new Error('Invalid data format: expected races, boats, and crew_members arrays')
  }
  
  // Create lookup dictionaries
  const crewMembersDict = {}
  for (const member of crew_members) {
    crewMembersDict[member.crew_member_id] = member
  }
  
  const teamManagersDict = {}
  for (const manager of team_managers || []) {
    teamManagersDict[manager.user_id] = manager
  }
  
  // Filter eligible boats using shared logic
  const eligibleBoats = filterEligibleBoats(boats)
  
  // Assign race and bow numbers using shared logic
  const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)
  
  // Build CrewTimer data
  const crewTimerData = []
  
  for (const boat of eligibleBoats) {
    const boatId = boat.boat_registration_id
    const assignment = boatAssignments[boatId]
    
    if (!assignment) continue
    
    const raceAssignment = raceAssignments[boat.race_id]
    if (!raceAssignment) continue
    
    // Get race info
    const fullRaceName = t ? t(`races.${raceAssignment.name}`, raceAssignment.name) : raceAssignment.name
    
    // Translate short name if locale is French
    const shortName = raceAssignment.shortName || ''
    const translatedShortName = locale === 'fr' && shortName
      ? translateShortNameToFrench(shortName)
      : shortName
    
    // Format event time in 12-hour format for CrewTimer
    const eventTime = formatTime12Hour(assignment.startTime, 0)
    
    // Get team manager and club
    const teamManagerId = boat.team_manager_id
    const teamManager = teamManagersDict[teamManagerId] || {}
    
    // Use boat_club_display for Crew column (simplified comma-separated clubs)
    const crewValue = boat.boat_club_display || teamManager.club_affiliation || 'Unknown'
    
    // Use boat_number for Crew Abbrev column (e.g., "M.1.3", "SM.15.42")
    const crewAbbrevValue = boat.boat_number || ''
    
    // Get average age from boat's crew_composition (pre-calculated by backend)
    const avgAge = boat.crew_composition?.avg_age 
      ? formatAverageAge(boat.crew_composition.avg_age) 
      : 0
    
    // Get stroke seat name
    const seats = boat.seats || []
    const strokeName = getStrokeSeatName(seats, crewMembersDict)
    
    // Get crew member names for Note column (comma-separated)
    const crewMemberNames = []
    for (const seat of seats) {
      if (seat.crew_member_id) {
        const member = crewMembersDict[seat.crew_member_id]
        if (member) {
          const fullName = `${member.first_name || ''} ${member.last_name || ''}`.trim()
          if (fullName) {
            crewMemberNames.push(fullName)
          }
        }
      }
    }
    const noteValue = crewMemberNames.join(', ')
    
    // Build row
    const row = {
      'Event Time': eventTime,
      'Event Num': assignment.raceNumber,
      'Event': fullRaceName,
      'Event Abbrev': translatedShortName,
      'Crew': crewValue,
      'Crew Abbrev': crewAbbrevValue,
      'Stroke': strokeName,
      'Bow': assignment.bowNumber,
      'Race Info': 'Head',
      'Status': '',
      'Age': avgAge,
      'Handicap': '',
      'Note': noteValue
    }
    
    crewTimerData.push(row)
  }
  
  // Sort by Event Num (race number), then by Bow number within each race
  crewTimerData.sort((a, b) => {
    if (a['Event Num'] !== b['Event Num']) {
      return a['Event Num'] - b['Event Num']
    }
    return a['Bow'] - b['Bow']
  })
  
  return crewTimerData
}

/**
 * Download races data as CrewTimer Excel file
 * @param {Object} jsonData - The JSON response from the backend API
 * @param {string} filename - Optional custom filename (without extension)
 * @param {string} locale - The locale for internationalization ('en' or 'fr')
 * @param {Function} t - The i18n translation function
 */
export function downloadCrewTimerExcel(jsonData, filename = null, locale = 'en', t = null) {
  // Generate CrewTimer data with locale and translation function
  const crewTimerData = formatRacesToCrewTimer(jsonData, locale, t)
  
  if (crewTimerData.length === 0) {
    throw new Error('No data to export')
  }
  
  // Create worksheet from data
  const worksheet = XLSX.utils.json_to_sheet(crewTimerData)
  
  // Create workbook
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, 'CrewTimer')
  
  // Generate filename with timestamp if not provided
  const timestamp = formatDateForFilename()
  const finalFilename = filename || `crewtimer_export_${timestamp}`
  
  // Write file
  XLSX.writeFile(workbook, `${finalFilename}.xlsx`)
}
