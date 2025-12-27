/**
 * Shared Race and Bow Numbering Logic
 * Used by both CrewTimer and Event Program exports to ensure consistency
 */

/**
 * Assign race numbers and bow numbers to boats
 * This function ensures consistent numbering across all exports
 * 
 * @param {Array} races - Array of race objects
 * @param {Array} boats - Array of boat objects (already filtered for eligible boats)
 * @param {Object} config - Configuration object with timing and bow start numbers
 * @returns {Object} - Object with raceAssignments and boatAssignments
 */
export function assignRaceAndBowNumbers(races, boats, config) {
  const {
    marathon_start_time = '07:45',
    semi_marathon_start_time = '09:00',
    semi_marathon_interval_seconds = 30,
    marathon_bow_start = 1,
    semi_marathon_bow_start = 41
  } = config || {}
  
  // Group boats by race
  const boatsByRace = {}
  for (const boat of boats) {
    const raceId = boat.race_id
    if (raceId) {
      if (!boatsByRace[raceId]) {
        boatsByRace[raceId] = []
      }
      boatsByRace[raceId].push(boat)
    }
  }
  
  // Sort boats within each race by average age (oldest first), then by registration order
  for (const raceId in boatsByRace) {
    boatsByRace[raceId].sort((a, b) => {
      const avgAgeA = a.crew_composition?.avg_age || 0
      const avgAgeB = b.crew_composition?.avg_age || 0
      
      // Sort by age descending (oldest first)
      if (avgAgeB !== avgAgeA) {
        return avgAgeB - avgAgeA
      }
      
      // If ages are equal, maintain registration order (by boat_registration_id)
      return (a.boat_registration_id || '').localeCompare(b.boat_registration_id || '')
    })
  }
  
  // Sort races by display_order
  const sortedRaces = [...races].sort((a, b) => {
    const orderA = a.display_order !== undefined && a.display_order !== null ? a.display_order : 999
    const orderB = b.display_order !== undefined && b.display_order !== null ? b.display_order : 999
    return orderA - orderB
  })
  
  // Assign race numbers and bow numbers
  const raceAssignments = {} // race_id -> { raceNumber, startTime, isMarathon }
  const boatAssignments = {} // boat_registration_id -> { raceNumber, bowNumber, startTime }
  
  let raceNumber = 0
  let marathonBowNum = marathon_bow_start
  let semiMarathonBowNum = semi_marathon_bow_start
  let semiMarathonBoatCount = 0
  
  for (const race of sortedRaces) {
    const raceId = race.race_id
    const raceBoats = boatsByRace[raceId] || []
    
    if (raceBoats.length === 0) {
      continue // Skip races with no boats
    }
    
    // Increment race number
    raceNumber += 1
    
    // Determine if this is a marathon or semi-marathon race
    const isMarathon = race.distance === 42 || race.event_type === '42km'
    const startTime = isMarathon ? marathon_start_time : semi_marathon_start_time
    
    // Track the first boat's start time for this race
    let firstBoatStartTime = ''
    
    // Assign bow numbers to boats in this race
    for (let i = 0; i < raceBoats.length; i++) {
      const boat = raceBoats[i]
      let bowNum = 0
      let boatStartTime = ''
      
      if (isMarathon) {
        // All marathon boats start at the same time
        bowNum = marathonBowNum
        marathonBowNum++
        // Convert HH:MM to HH:MM:SS format
        boatStartTime = addSecondsToTime(marathon_start_time, 0)
      } else {
        // Semi-marathon boats start with intervals
        const additionalSeconds = semiMarathonBoatCount * semi_marathon_interval_seconds
        bowNum = semiMarathonBowNum
        semiMarathonBowNum++
        semiMarathonBoatCount++
        
        // Calculate actual start time with interval
        boatStartTime = addSecondsToTime(semi_marathon_start_time, additionalSeconds)
      }
      
      // Store the first boat's start time for the race
      if (i === 0) {
        firstBoatStartTime = boatStartTime
      }
      
      // Store boat assignment
      boatAssignments[boat.boat_registration_id] = {
        raceNumber,
        bowNumber: bowNum,
        startTime: boatStartTime,
        raceId
      }
    }
    
    // Store race assignment with the first boat's start time
    raceAssignments[raceId] = {
      raceNumber,
      startTime: firstBoatStartTime,
      isMarathon,
      shortName: race.short_name,
      name: race.name
    }
  }
  
  return {
    raceAssignments,
    boatAssignments
  }
}

/**
 * Add seconds to a time string in HH:MM format
 * @param {string} time24 - Time in 24-hour format (HH:MM)
 * @param {number} additionalSeconds - Seconds to add
 * @returns {string} - New time in HH:MM:SS format
 */
function addSecondsToTime(time24, additionalSeconds) {
  if (!time24) return ''
  
  try {
    const [hours, minutes] = time24.split(':').map(Number)
    let totalSeconds = hours * 3600 + minutes * 60 + additionalSeconds
    totalSeconds = totalSeconds % 86400 // Handle day overflow
    
    const finalHours = Math.floor(totalSeconds / 3600)
    const finalMinutes = Math.floor((totalSeconds % 3600) / 60)
    const finalSeconds = totalSeconds % 60
    
    return `${String(finalHours).padStart(2, '0')}:${String(finalMinutes).padStart(2, '0')}:${String(finalSeconds).padStart(2, '0')}`
  } catch (error) {
    console.error('Error adding seconds to time:', error)
    return time24
  }
}

/**
 * Filter boats to only include eligible ones (complete/paid/free, not forfait)
 * @param {Array} boats - Array of all boats
 * @returns {Array} - Filtered array of eligible boats
 */
export function filterEligibleBoats(boats) {
  return boats.filter(boat => {
    const status = boat.registration_status
    const isForfait = boat.forfait === true
    return (status === 'complete' || status === 'paid' || status === 'free') && !isForfait
  })
}
