/**
 * CrewTimer Export Formatter
 * Converts JSON data from the backend API to CrewTimer Excel format
 */

import * as XLSX from 'xlsx'
import { getBoatTypeDisplay, formatDateForFilename } from './shared.js'

/**
 * Format semi-marathon race name
 * Pattern: boat_type [Y if yolette] age_category gender_category
 * @param {Object} race - The race object
 * @returns {string} - Formatted race name
 */
export function formatSemiMarathonRaceName(race) {
  const boatType = getBoatTypeDisplay(race.boat_type || '')
  
  // Check if "yolette" is in the race name (case insensitive)
  const raceName = (race.name || '').toLowerCase()
  const yoletteMarker = raceName.includes('yolette') ? 'Y' : ''
  
  // Get age category (j16, j18, senior, master)
  const ageCategory = (race.age_category || '').toUpperCase()
  
  // Get gender category (men, women, mixed)
  const genderCategory = race.gender_category || ''
  const genderMap = {
    'men': 'MAN',
    'women': 'WOMAN',
    'mixed': 'MIXED'
  }
  const genderDisplay = genderMap[genderCategory] || genderCategory.toUpperCase()
  
  // Compose the name - filter out empty strings and join with single space
  const parts = [boatType, yoletteMarker, ageCategory, genderDisplay]
  return parts.filter(part => part).join(' ').trim()
}

/**
 * Calculate average age of crew members
 * @param {Array} crewMembers - Array of crew member objects
 * @param {string} competitionDate - Competition date in YYYY-MM-DD format
 * @returns {number} - Average age rounded to nearest integer
 */
export function calculateAverageAge(crewMembers, competitionDate) {
  if (!crewMembers || crewMembers.length === 0) {
    return 0
  }
  
  try {
    const compYear = parseInt(competitionDate.split('-')[0])
    const ages = []
    
    for (const member of crewMembers) {
      const dob = member.date_of_birth
      if (dob) {
        const birthYear = parseInt(dob.split('-')[0])
        const age = compYear - birthYear
        ages.push(age)
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
 * @returns {Array} - Array of CrewTimer row objects
 */
export function formatRacesToCrewTimer(jsonData) {
  if (!jsonData || !jsonData.data) {
    throw new Error('Invalid data format: expected data object')
  }
  
  const { config, races, boats, crew_members, team_managers } = jsonData.data
  
  if (!races || !boats || !crew_members) {
    throw new Error('Invalid data format: expected races, boats, and crew_members arrays')
  }
  
  const competitionDate = config?.competition_date || '2025-05-01'
  
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
  
  // Sort races: marathon (42km) first, then semi-marathon (21km)
  const marathonRaces = races.filter(r => r.distance === 42 || r.event_type === '42km')
  const semiMarathonRaces = races.filter(r => r.distance === 21 || r.event_type === '21km')
  const sortedRaces = [...marathonRaces, ...semiMarathonRaces]
  
  // Build CrewTimer data
  const crewTimerData = []
  let eventNum = 0
  let bowNum = 1
  
  for (const race of sortedRaces) {
    const raceId = race.race_id
    const raceBoats = boatsByRace[raceId] || []
    
    if (raceBoats.length === 0) {
      continue // Skip races with no boats
    }
    
    // Increment event number for this race
    eventNum += 1
    
    // Format race name based on distance
    const distance = race.distance || (race.event_type === '42km' ? 42 : 21)
    const raceName = distance === 21 
      ? formatSemiMarathonRaceName(race)
      : race.name
    
    for (const boat of raceBoats) {
      // Get team manager and club
      const teamManagerId = boat.team_manager_id
      const teamManager = teamManagersDict[teamManagerId] || {}
      const clubName = teamManager.club_affiliation || boat.club_affiliation || 'Unknown'
      
      // Get crew members for this boat from seats
      const seats = boat.seats || []
      const boatCrewMembers = []
      for (const seat of seats) {
        const crewMemberId = seat.crew_member_id
        if (crewMemberId && crewMembersDict[crewMemberId]) {
          boatCrewMembers.push(crewMembersDict[crewMemberId])
        }
      }
      
      // Calculate average age
      const avgAge = calculateAverageAge(boatCrewMembers, competitionDate)
      
      // Get stroke seat name
      const strokeName = getStrokeSeatName(seats, crewMembersDict)
      
      // Build row
      const row = {
        'Event Time': '',
        'Event Num': eventNum,
        'Event': raceName,
        'Event Abbrev': raceName,
        'Crew': clubName,
        'Crew Abbrev': clubName,
        'Stroke': strokeName,
        'Bow': bowNum,
        'Race Info': 'Head',
        'Status': '',
        'Age': avgAge
      }
      
      crewTimerData.push(row)
      bowNum += 1
    }
  }
  
  return crewTimerData
}

/**
 * Download races data as CrewTimer Excel file
 * @param {Object} jsonData - The JSON response from the backend API
 * @param {string} filename - Optional custom filename (without extension)
 */
export function downloadCrewTimerExcel(jsonData, filename = null) {
  // Generate CrewTimer data
  const crewTimerData = formatRacesToCrewTimer(jsonData)
  
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
