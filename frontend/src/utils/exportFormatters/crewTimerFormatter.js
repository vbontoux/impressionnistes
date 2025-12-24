/**
 * CrewTimer Export Formatter
 * Converts JSON data from the backend API to CrewTimer Excel format
 */

import * as XLSX from 'xlsx'
import { formatDateForFilename } from './shared.js'

/**
 * Format time in 12-hour format with AM/PM (e.g., "7:00:00 AM")
 * @param {string} time24 - Time in 24-hour format (HH:MM)
 * @param {number} additionalSeconds - Additional seconds to add to the time
 * @returns {string} - Time in 12-hour format with AM/PM
 */
export function formatTime12Hour(time24, additionalSeconds = 0) {
  if (!time24) return ''
  
  try {
    // Parse HH:MM format
    const [hours, minutes] = time24.split(':').map(Number)
    
    // Calculate total seconds
    let totalSeconds = hours * 3600 + minutes * 60 + additionalSeconds
    
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
  
  // Get race timing configuration
  const marathonStartTime = config?.marathon_start_time || '07:45'
  const semiMarathonStartTime = config?.semi_marathon_start_time || '09:00'
  const semiMarathonIntervalSeconds = config?.semi_marathon_interval_seconds || 30
  const marathonBowStart = config?.marathon_bow_start || 1
  const semiMarathonBowStart = config?.semi_marathon_bow_start || 41
  
  // Create lookup dictionaries
  const crewMembersDict = {}
  for (const member of crew_members) {
    crewMembersDict[member.crew_member_id] = member
  }
  
  const teamManagersDict = {}
  for (const manager of team_managers || []) {
    teamManagersDict[manager.user_id] = manager
  }
  
  const racesDict = {}
  for (const race of races) {
    racesDict[race.race_id] = race
  }
  
  // Filter boats: complete/paid/free, exclude forfait
  const eligibleBoats = boats.filter(boat => {
    const status = boat.registration_status
    const isForfait = boat.forfait === true
    return (status === 'complete' || status === 'paid' || status === 'free') && !isForfait
  })
  
  // Group boats by race
  const boatsByRace = {}
  for (const boat of eligibleBoats) {
    const raceId = boat.race_id
    if (raceId) {
      if (!boatsByRace[raceId]) {
        boatsByRace[raceId] = []
      }
      boatsByRace[raceId].push(boat)
    }
  }
  
  // Sort races by display_order (if available), otherwise fall back to distance-based sorting
  let sortedRaces
  if (races.length > 0 && races[0].display_order !== undefined && races[0].display_order !== null) {
    // Use display_order for sorting
    sortedRaces = [...races].sort((a, b) => {
      const orderA = a.display_order || 999
      const orderB = b.display_order || 999
      return orderA - orderB
    })
  } else {
    // Fallback: marathon (42km) first, then semi-marathon (21km)
    const marathonRaces = races.filter(r => r.distance === 42 || r.event_type === '42km')
    const semiMarathonRaces = races.filter(r => r.distance === 21 || r.event_type === '21km')
    sortedRaces = [...marathonRaces, ...semiMarathonRaces]
  }
  
  // Build CrewTimer data
  const crewTimerData = []
  let eventNum = 0
  let marathonBowNum = marathonBowStart
  let semiMarathonBowNum = semiMarathonBowStart
  let semiMarathonBoatCount = 0 // Track boat count for semi-marathon interval calculation
  
  for (const race of sortedRaces) {
    const raceId = race.race_id
    const raceBoats = boatsByRace[raceId] || []
    
    if (raceBoats.length === 0) {
      continue // Skip races with no boats
    }
    
    // Increment event number for this race
    eventNum += 1
    
    // Determine if this is a marathon or semi-marathon race
    const isMarathon = race.distance === 42 || race.event_type === '42km'
    
    // Use the original race name from database (not the generated semi-marathon name)
    // This ensures proper translation via i18n
    const fullRaceName = t ? t(`races.${race.name}`, race.name) : race.name
    
    // Translate short name if locale is French
    const shortName = race.short_name || ''
    const translatedShortName = locale === 'fr' && shortName
      ? translateShortNameToFrench(shortName)
      : shortName
    
    for (const boat of raceBoats) {
      // Calculate event time and bow number based on race type
      let eventTime = ''
      let bowNum = 0
      
      if (isMarathon) {
        // All marathon boats start at the same time
        eventTime = formatTime12Hour(marathonStartTime, 0)
        bowNum = marathonBowNum
        marathonBowNum++
      } else {
        // Semi-marathon boats start with intervals
        const additionalSeconds = semiMarathonBoatCount * semiMarathonIntervalSeconds
        eventTime = formatTime12Hour(semiMarathonStartTime, additionalSeconds)
        bowNum = semiMarathonBowNum
        semiMarathonBowNum++
        semiMarathonBoatCount++
      }
      
      // Get team manager and club
      const teamManagerId = boat.team_manager_id
      const teamManager = teamManagersDict[teamManagerId] || {}
      const clubName = teamManager.club_affiliation || boat.club_affiliation || 'Unknown'
      
      // Get average age from boat's crew_composition (pre-calculated by backend)
      // This is more efficient and ensures consistency with backend logic
      const avgAge = boat.crew_composition?.avg_age 
        ? Math.round(boat.crew_composition.avg_age) 
        : 0
      
      // Get stroke seat name
      const seats = boat.seats || []
      const strokeName = getStrokeSeatName(seats, crewMembersDict)
      
      // Build row
      const row = {
        'Event Time': eventTime,
        'Event Num': eventNum,
        'Event': fullRaceName,
        'Event Abbrev': translatedShortName,
        'Crew': clubName,
        'Crew Abbrev': clubName,
        'Stroke': strokeName,
        'Bow': bowNum,
        'Race Info': 'Head',
        'Status': '',
        'Age': avgAge
      }
      
      crewTimerData.push(row)
    }
  }
  
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
