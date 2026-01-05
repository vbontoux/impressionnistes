/**
 * Cross-Export Consistency Tests
 * Ensures CrewTimer and Event Program exports produce consistent race and bow numbers
 */

import { describe, it, expect } from 'vitest'
import { formatRacesToCrewTimer } from './crewTimerFormatter.js'
import { generateCrewMemberList, generateRaceSchedule } from './eventProgramFormatter.js'
import { assignRaceAndBowNumbers, filterEligibleBoats } from './raceNumbering.js'

describe('Cross-Export Consistency', () => {
  const mockJsonData = {
    data: {
      config: {
        marathon_start_time: '07:45',
        semi_marathon_start_time: '09:00',
        semi_marathon_interval_seconds: 30,
        marathon_bow_start: 1,
        semi_marathon_bow_start: 41
      },
      races: [
        { race_id: 'race1', display_order: 1, distance: 42, event_type: '42km', short_name: 'MW4X+', name: 'Master Women 4X+' },
        { race_id: 'race2', display_order: 2, distance: 21, event_type: '21km', short_name: 'SW2X', name: 'Senior Women 2X' },
        { race_id: 'race3', display_order: 3, distance: 42, event_type: '42km', short_name: 'MH8+', name: 'Master Men 8+' }
      ],
      boats: [
        {
          boat_registration_id: 'boat1',
          race_id: 'race1',
          registration_status: 'complete',
          forfait: false,
          team_manager_id: 'user1',
          club_affiliation: 'Club A',
          crew_composition: { avg_age: 55 },
          seats: [
            { crew_member_id: 'crew1', position: 1, type: 'rower' },
            { crew_member_id: 'crew2', position: 2, type: 'rower' }
          ]
        },
        {
          boat_registration_id: 'boat2',
          race_id: 'race1',
          registration_status: 'paid',
          forfait: false,
          team_manager_id: 'user1',
          club_affiliation: 'Club A',
          crew_composition: { avg_age: 60 },
          seats: [
            { crew_member_id: 'crew3', position: 1, type: 'rower' },
            { crew_member_id: 'crew4', position: 2, type: 'rower' }
          ]
        },
        {
          boat_registration_id: 'boat3',
          race_id: 'race2',
          registration_status: 'free',
          forfait: false,
          team_manager_id: 'user2',
          club_affiliation: 'Club B',
          crew_composition: { avg_age: 30 },
          seats: [
            { crew_member_id: 'crew5', position: 1, type: 'rower' },
            { crew_member_id: 'crew6', position: 2, type: 'rower' }
          ]
        },
        {
          boat_registration_id: 'boat4',
          race_id: 'race3',
          registration_status: 'complete',
          forfait: false,
          team_manager_id: 'user1',
          club_affiliation: 'Club A',
          crew_composition: { avg_age: 58 },
          seats: [
            { crew_member_id: 'crew7', position: 1, type: 'rower' },
            { crew_member_id: 'crew8', position: 2, type: 'rower' }
          ]
        },
        {
          boat_registration_id: 'boat5',
          race_id: 'race1',
          registration_status: 'incomplete',
          forfait: false,
          team_manager_id: 'user1',
          club_affiliation: 'Club A',
          crew_composition: { avg_age: 50 },
          seats: []
        },
        {
          boat_registration_id: 'boat6',
          race_id: 'race2',
          registration_status: 'complete',
          forfait: true,
          team_manager_id: 'user2',
          club_affiliation: 'Club B',
          crew_composition: { avg_age: 35 },
          seats: []
        }
      ],
      crew_members: [
        { crew_member_id: 'crew1', first_name: 'Alice', last_name: 'Anderson', club_affiliation: 'Club A' },
        { crew_member_id: 'crew2', first_name: 'Bob', last_name: 'Brown', club_affiliation: 'Club A' },
        { crew_member_id: 'crew3', first_name: 'Charlie', last_name: 'Clark', club_affiliation: 'Club A' },
        { crew_member_id: 'crew4', first_name: 'Diana', last_name: 'Davis', club_affiliation: 'Club A' },
        { crew_member_id: 'crew5', first_name: 'Eve', last_name: 'Evans', club_affiliation: 'Club B' },
        { crew_member_id: 'crew6', first_name: 'Frank', last_name: 'Foster', club_affiliation: 'Club B' },
        { crew_member_id: 'crew7', first_name: 'Grace', last_name: 'Green', club_affiliation: 'Club A' },
        { crew_member_id: 'crew8', first_name: 'Henry', last_name: 'Harris', club_affiliation: 'Club A' }
      ],
      team_managers: [
        { user_id: 'user1', club_affiliation: 'Club A' },
        { user_id: 'user2', club_affiliation: 'Club B' }
      ]
    }
  }

  it('should produce identical race numbers across both exports', () => {
    // Generate CrewTimer export
    const crewTimerData = formatRacesToCrewTimer(mockJsonData, 'fr')

    // Generate Event Program exports
    const eligibleBoats = filterEligibleBoats(mockJsonData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(
      mockJsonData.data.races,
      eligibleBoats,
      mockJsonData.data.config
    )
    const crewMemberList = generateCrewMemberList(mockJsonData, boatAssignments, raceAssignments, 'fr')
    const raceSchedule = generateRaceSchedule(mockJsonData, raceAssignments, 'fr')

    // Extract race numbers from CrewTimer export
    const crewTimerRaceNumbers = new Set(crewTimerData.map(row => row['Event Num']))

    // Extract race numbers from Event Program exports
    const eventProgramRaceNumbers = new Set([
      ...crewMemberList.map(row => row['N° Course']),
      ...raceSchedule.map(row => row['N° Course'])
    ])

    // Race numbers should be identical
    expect(crewTimerRaceNumbers).toEqual(eventProgramRaceNumbers)
    // With the business rule: all marathons get 1, semi-marathons get 2, 3, 4...
    // race1 (marathon) = 1, race2 (semi) = 2, race3 (marathon) = 1
    // So we should have race numbers [1, 2]
    expect(Array.from(crewTimerRaceNumbers).sort()).toEqual([1, 2])
  })

  it('should produce identical bow numbers across both exports', () => {
    // Generate CrewTimer export
    const crewTimerData = formatRacesToCrewTimer(mockJsonData, 'fr')

    // Generate Event Program crew member list
    const eligibleBoats = filterEligibleBoats(mockJsonData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(
      mockJsonData.data.races,
      eligibleBoats,
      mockJsonData.data.config
    )

    // Both exports use the same boatAssignments, so bow numbers should be identical
    // Verify that CrewTimer export uses the bow numbers from boatAssignments
    const crewTimerBowNumbers = crewTimerData.map(row => row['Bow']).sort((a, b) => a - b)
    const eventProgramBowNumbers = Object.values(boatAssignments)
      .map(a => a.bowNumber)
      .sort((a, b) => a - b)

    // Both should have the same bow numbers
    expect(crewTimerBowNumbers).toEqual(eventProgramBowNumbers)
    
    // Verify specific bow numbers
    expect(crewTimerBowNumbers).toEqual([1, 2, 3, 41])
  })

  it('should filter boats identically across both exports', () => {
    // Generate CrewTimer export
    const crewTimerData = formatRacesToCrewTimer(mockJsonData, 'fr')

    // Generate Event Program exports
    const eligibleBoats = filterEligibleBoats(mockJsonData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(
      mockJsonData.data.races,
      eligibleBoats,
      mockJsonData.data.config
    )
    const crewMemberList = generateCrewMemberList(mockJsonData, boatAssignments, raceAssignments, 'fr')

    // CrewTimer should have 4 boats (boat1, boat2, boat3, boat4)
    // boat5 is incomplete, boat6 is forfait
    expect(crewTimerData).toHaveLength(4)

    // Event Program should have crew members from the same 4 boats
    // Each boat has 2 crew members, so 8 total
    expect(crewMemberList).toHaveLength(8)

    // Verify the boats are the same
    const crewTimerBoatCount = crewTimerData.length
    const eventProgramBoatCount = eligibleBoats.length
    expect(crewTimerBoatCount).toBe(eventProgramBoatCount)
  })

  it('should assign marathon bow numbers starting from 1', () => {
    const crewTimerData = formatRacesToCrewTimer(mockJsonData, 'fr')

    // Find marathon boats (race1 and race3 - both have Event Num 1)
    const marathonBoats = crewTimerData.filter(row => row['Event Num'] === 1)

    // Marathon bow numbers should be 1, 2, 3
    const marathonBowNumbers = marathonBoats.map(row => row['Bow']).sort((a, b) => a - b)
    expect(marathonBowNumbers).toEqual([1, 2, 3])
  })

  it('should assign semi-marathon bow numbers starting from 41', () => {
    const crewTimerData = formatRacesToCrewTimer(mockJsonData, 'fr')

    // Find semi-marathon boats (race2)
    const semiMarathonBoats = crewTimerData.filter(row => row['Event Num'] === 2)

    // Semi-marathon bow numbers should start at 41
    const semiMarathonBowNumbers = semiMarathonBoats.map(row => row['Bow']).sort((a, b) => a - b)
    expect(semiMarathonBowNumbers).toEqual([41])
  })

  it('should maintain consistency with custom bow start numbers', () => {
    const customData = {
      ...mockJsonData,
      data: {
        ...mockJsonData.data,
        config: {
          ...mockJsonData.data.config,
          marathon_bow_start: 100,
          semi_marathon_bow_start: 200
        }
      }
    }

    // Generate CrewTimer export with custom config
    const crewTimerData = formatRacesToCrewTimer(customData, 'fr')

    // Generate Event Program exports with custom config
    const eligibleBoats = filterEligibleBoats(customData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(
      customData.data.races,
      eligibleBoats,
      customData.data.config
    )

    // Find marathon boats (both race1 and race3 have Event Num 1)
    const marathonBoats = crewTimerData.filter(row => row['Event Num'] === 1)
    const marathonBowNumbers = marathonBoats.map(row => row['Bow']).sort((a, b) => a - b)
    expect(marathonBowNumbers).toEqual([100, 101, 102])

    // Find semi-marathon boats (race2 has Event Num 2)
    const semiMarathonBoats = crewTimerData.filter(row => row['Event Num'] === 2)
    const semiMarathonBowNumbers = semiMarathonBoats.map(row => row['Bow']).sort((a, b) => a - b)
    expect(semiMarathonBowNumbers).toEqual([200])

    // Verify Event Program uses same bow numbers
    for (const boat of eligibleBoats) {
      const assignment = boatAssignments[boat.boat_registration_id]
      if (assignment) {
        const crewTimerRow = crewTimerData.find(row => row['Bow'] === assignment.bowNumber)
        expect(crewTimerRow).toBeDefined()
      }
    }
  })

  it('should produce race schedule with one row per race', () => {
    const crewTimerData = formatRacesToCrewTimer(mockJsonData, 'fr')

    const eligibleBoats = filterEligibleBoats(mockJsonData.data.boats)
    const { raceAssignments } = assignRaceAndBowNumbers(
      mockJsonData.data.races,
      eligibleBoats,
      mockJsonData.data.config
    )
    const raceSchedule = generateRaceSchedule(mockJsonData, raceAssignments, 'fr')

    // Count unique race numbers in CrewTimer export
    const crewTimerRaceCount = new Set(crewTimerData.map(row => row['Event Num'])).size

    // Event Program race schedule has one row per race definition
    const eventProgramRaceCount = raceSchedule.length

    // CrewTimer groups marathons under race number 1, so it has 2 unique numbers
    expect(crewTimerRaceCount).toBe(2)
    // Event Program has one row per race definition (3 races)
    expect(eventProgramRaceCount).toBe(3)
    
    // They count different things, so they won't be equal when there are multiple marathons
    // CrewTimer counts unique race numbers, Event Program counts race definitions
  })
})
