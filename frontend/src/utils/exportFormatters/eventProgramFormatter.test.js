/**
 * Tests for Event Program Formatter
 * Ensures correct crew member list and race schedule generation
 */

import { describe, it, expect } from 'vitest'
import { generateCrewMemberList, generateRaceSchedule } from './eventProgramFormatter.js'
import { assignRaceAndBowNumbers, filterEligibleBoats } from './raceNumbering.js'

describe('generateCrewMemberList', () => {
  const mockData = {
    data: {
      boats: [
        {
          boat_registration_id: 'boat1',
          race_id: 'race1',
          registration_status: 'complete',
          forfait: false,
          team_manager_id: 'user1',
          club_affiliation: 'Club A',
          seats: [
            { crew_member_id: 'crew1', position: 1, type: 'rower' },
            { crew_member_id: 'crew2', position: 2, type: 'rower' }
          ]
        }
      ],
      crew_members: [
        { crew_member_id: 'crew1', first_name: 'John', last_name: 'Doe', club_affiliation: 'Club A' },
        { crew_member_id: 'crew2', first_name: 'Jane', last_name: 'Smith', club_affiliation: 'Club A' }
      ],
      team_managers: [
        { user_id: 'user1', club_affiliation: 'Club A' }
      ]
    }
  }

  const config = {
    marathon_bow_start: 1,
    semi_marathon_bow_start: 41
  }

  it('should generate crew member list with correct columns', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')

    expect(result).toHaveLength(2)
    expect(result[0]).toHaveProperty('Nom')
    expect(result[0]).toHaveProperty('Prénom')
    expect(result[0]).toHaveProperty('Club')
    expect(result[0]).toHaveProperty('Course (abrégé)')
    expect(result[0]).toHaveProperty('Course')
    expect(result[0]).toHaveProperty('N° Course')
    expect(result[0]).toHaveProperty('Nage')
    expect(result[0]).toHaveProperty('N° Dossard')
  })

  it('should generate crew member list with English columns when locale is en', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'en')

    expect(result).toHaveLength(2)
    expect(result[0]).toHaveProperty('Last Name')
    expect(result[0]).toHaveProperty('First Name')
    expect(result[0]).toHaveProperty('Club')
    expect(result[0]).toHaveProperty('Race (abbrev)')
    expect(result[0]).toHaveProperty('Race')
    expect(result[0]).toHaveProperty('Race #')
    expect(result[0]).toHaveProperty('Stroke')
    expect(result[0]).toHaveProperty('Bow #')
  })

  it('should sort crew members alphabetically by last name', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')

    // Doe comes before Smith alphabetically
    expect(result[0]['Nom']).toBe('Doe')
    expect(result[1]['Nom']).toBe('Smith')
  })

  it('should include correct race number and bow number', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')

    expect(result[0]['N° Course']).toBe(1)
    expect(result[0]['N° Dossard']).toBe(1)
  })

  it('should not include crew members from ineligible boats', () => {
    const dataWithIneligible = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'incomplete',
            forfait: false,
            team_manager_id: 'user1',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower' }
            ]
          }
        ],
        crew_members: [
          { crew_member_id: 'crew1', first_name: 'John', last_name: 'Doe' }
        ],
        team_managers: []
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(dataWithIneligible.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(dataWithIneligible, boatAssignments, raceAssignments, 'fr')

    expect(result).toHaveLength(0)
  })

  it('should include stroke seat name', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')

    // Stroke seat is position 2 (highest position rower)
    expect(result[0]['Nage']).toBe('Smith')
  })

  it('should use boat_club_display for single club', () => {
    const dataWithClubDisplay = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'RCPM',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower' }
            ]
          }
        ],
        crew_members: [
          { crew_member_id: 'crew1', first_name: 'John', last_name: 'Doe' }
        ],
        team_managers: []
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(dataWithClubDisplay.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(dataWithClubDisplay, boatAssignments, raceAssignments, 'fr')

    expect(result[0]['Club']).toBe('RCPM')
  })

  it('should use boat_club_display for multi-club crews', () => {
    const dataWithMultiClub = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'RCPM (Multi-Club)',
            club_list: ['RCPM', 'Club Elite', 'SN Versailles'],
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower' },
              { crew_member_id: 'crew2', position: 2, type: 'rower' }
            ]
          }
        ],
        crew_members: [
          { crew_member_id: 'crew1', first_name: 'John', last_name: 'Doe' },
          { crew_member_id: 'crew2', first_name: 'Jane', last_name: 'Smith' }
        ],
        team_managers: []
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(dataWithMultiClub.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(dataWithMultiClub, boatAssignments, raceAssignments, 'fr')

    expect(result[0]['Club']).toBe('RCPM (Multi-Club)')
    expect(result[1]['Club']).toBe('RCPM (Multi-Club)')
  })

  it('should display boat_club_display in English locale', () => {
    const dataWithClubDisplay = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'RCPM (Multi-Club)',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower' }
            ]
          }
        ],
        crew_members: [
          { crew_member_id: 'crew1', first_name: 'John', last_name: 'Doe' }
        ],
        team_managers: []
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(dataWithClubDisplay.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(dataWithClubDisplay, boatAssignments, raceAssignments, 'en')

    // "Multi-Club" works in both languages - no translation needed
    expect(result[0]['Club']).toBe('RCPM (Multi-Club)')
  })

  it('should use boat_club_display for external crew', () => {
    const dataWithExternalCrew = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'RCPM (Club Elite)',
            club_list: ['Club Elite'],
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower' }
            ]
          }
        ],
        crew_members: [
          { crew_member_id: 'crew1', first_name: 'John', last_name: 'Doe' }
        ],
        team_managers: []
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(dataWithExternalCrew.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(dataWithExternalCrew, boatAssignments, raceAssignments, 'fr')

    expect(result[0]['Club']).toBe('RCPM (Club Elite)')
  })
})

describe('generateRaceSchedule', () => {
  const mockData = {
    data: {
      races: [
        { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' },
        { race_id: 'race2', display_order: 2, distance: 21, short_name: 'SW2X', name: 'Senior Women 2X' }
      ]
    }
  }

  const config = {
    marathon_start_time: '07:45',
    semi_marathon_start_time: '09:00',
    marathon_bow_start: 1,
    semi_marathon_bow_start: 41
  }

  it('should generate race schedule with correct columns', () => {
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1', registration_status: 'complete', forfait: false }
    ]
    const eligibleBoats = filterEligibleBoats(boats)
    const { raceAssignments } = assignRaceAndBowNumbers(mockData.data.races, eligibleBoats, config)

    const result = generateRaceSchedule(mockData, raceAssignments, 'fr')

    expect(result).toHaveLength(1)
    expect(result[0]).toHaveProperty('Course (abrégé)')
    expect(result[0]).toHaveProperty('Course')
    expect(result[0]).toHaveProperty('N° Course')
    expect(result[0]).toHaveProperty('Heure de départ')
  })

  it('should sort races by race number', () => {
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race2', registration_status: 'complete', forfait: false },
      { boat_registration_id: 'boat2', race_id: 'race1', registration_status: 'complete', forfait: false }
    ]
    const eligibleBoats = filterEligibleBoats(boats)
    const { raceAssignments } = assignRaceAndBowNumbers(mockData.data.races, eligibleBoats, config)

    const result = generateRaceSchedule(mockData, raceAssignments, 'fr')

    expect(result[0]['N° Course']).toBe(1)
    expect(result[1]['N° Course']).toBe(2)
  })

  it('should include correct start times', () => {
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1', registration_status: 'complete', forfait: false },
      { boat_registration_id: 'boat2', race_id: 'race2', registration_status: 'complete', forfait: false }
    ]
    const eligibleBoats = filterEligibleBoats(boats)
    const { raceAssignments } = assignRaceAndBowNumbers(mockData.data.races, eligibleBoats, config)

    const result = generateRaceSchedule(mockData, raceAssignments, 'fr')

    expect(result[0]['Heure de départ']).toBe('07:45') // Marathon
    expect(result[1]['Heure de départ']).toBe('09:00') // Semi-marathon
  })

  it('should show first boat start time for each race', () => {
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1', registration_status: 'complete', forfait: false },
      { boat_registration_id: 'boat2', race_id: 'race1', registration_status: 'complete', forfait: false },
      { boat_registration_id: 'boat3', race_id: 'race1', registration_status: 'complete', forfait: false },
      { boat_registration_id: 'boat4', race_id: 'race2', registration_status: 'complete', forfait: false },
      { boat_registration_id: 'boat5', race_id: 'race2', registration_status: 'complete', forfait: false }
    ]
    const eligibleBoats = filterEligibleBoats(boats)
    const { raceAssignments } = assignRaceAndBowNumbers(mockData.data.races, eligibleBoats, config)

    const result = generateRaceSchedule(mockData, raceAssignments, 'fr')

    // Race 1 (marathon) - all boats start at same time
    expect(result[0]['Heure de départ']).toBe('07:45')
    
    // Race 2 (semi-marathon) - first boat starts at 09:00, but race shows first boat time
    // Since race 1 has 3 boats (all marathon), semi-marathon counter starts at 0
    // First boat of race 2 starts at 09:00 + (0 * 30) = 09:00
    expect(result[1]['Heure de départ']).toBe('09:00')
  })

  it('should not include races without boats', () => {
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1', registration_status: 'complete', forfait: false }
    ]
    const eligibleBoats = filterEligibleBoats(boats)
    const { raceAssignments } = assignRaceAndBowNumbers(mockData.data.races, eligibleBoats, config)

    const result = generateRaceSchedule(mockData, raceAssignments, 'fr')

    expect(result).toHaveLength(1)
    expect(result[0]['N° Course']).toBe(1)
  })
})

describe('Consistency Tests - Event Program vs CrewTimer', () => {
  it('should use same race numbers as CrewTimer export', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' },
      { race_id: 'race2', display_order: 2, distance: 21, short_name: 'SW2X', name: 'Senior Women 2X' }
    ]
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1', registration_status: 'complete', forfait: false },
      { boat_registration_id: 'boat2', race_id: 'race2', registration_status: 'complete', forfait: false }
    ]
    const config = {
      marathon_bow_start: 1,
      semi_marathon_bow_start: 41
    }

    const eligibleBoats = filterEligibleBoats(boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    // Both exports use the same assignments
    expect(raceAssignments['race1'].raceNumber).toBe(1)
    expect(raceAssignments['race2'].raceNumber).toBe(2)
    expect(boatAssignments['boat1'].raceNumber).toBe(1)
    expect(boatAssignments['boat2'].raceNumber).toBe(2)
  })

  it('should use same bow numbers as CrewTimer export', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1', registration_status: 'complete', forfait: false },
      { boat_registration_id: 'boat2', race_id: 'race1', registration_status: 'complete', forfait: false },
      { boat_registration_id: 'boat3', race_id: 'race1', registration_status: 'complete', forfait: false }
    ]
    const config = {
      marathon_bow_start: 1,
      semi_marathon_bow_start: 41
    }

    const eligibleBoats = filterEligibleBoats(boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    // Both exports use the same bow numbers
    expect(boatAssignments['boat1'].bowNumber).toBe(1)
    expect(boatAssignments['boat2'].bowNumber).toBe(2)
    expect(boatAssignments['boat3'].bowNumber).toBe(3)
  })

  it('should filter boats identically to CrewTimer export', () => {
    const boats = [
      { boat_registration_id: 'boat1', registration_status: 'complete', forfait: false },
      { boat_registration_id: 'boat2', registration_status: 'incomplete', forfait: false },
      { boat_registration_id: 'boat3', registration_status: 'paid', forfait: true },
      { boat_registration_id: 'boat4', registration_status: 'free', forfait: false }
    ]

    const result = filterEligibleBoats(boats)

    // Same filtering logic as CrewTimer
    expect(result).toHaveLength(2)
    expect(result.map(b => b.boat_registration_id)).toEqual(['boat1', 'boat4'])
  })
})


describe('Payment Balance Integration', () => {
  it('should include payment balance columns in crew member list', () => {
    const mockDataWithPayments = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'Club A',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower' }
            ]
          }
        ],
        crew_members: [
          { crew_member_id: 'crew1', first_name: 'John', last_name: 'Doe' }
        ],
        team_managers: [
          {
            user_id: 'user1',
            club_affiliation: 'Club A',
            total_paid: 150.00,
            outstanding_balance: 50.00,
            payment_status: 'Partial Payment'
          }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const config = {
      marathon_bow_start: 1,
      semi_marathon_bow_start: 41
    }

    const eligibleBoats = filterEligibleBoats(mockDataWithPayments.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(mockDataWithPayments, boatAssignments, raceAssignments, 'fr')

    expect(result).toHaveLength(1)
    expect(result[0]).toHaveProperty('Total payé (EUR)')
    expect(result[0]).toHaveProperty('Solde impayé (EUR)')
    expect(result[0]).toHaveProperty('Statut de paiement')
    expect(result[0]['Total payé (EUR)']).toBe('150.00')
    expect(result[0]['Solde impayé (EUR)']).toBe('50.00')
    expect(result[0]['Statut de paiement']).toBe('Partial Payment')
  })

  it('should format currency values with 2 decimal places', () => {
    const mockDataWithPayments = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'Club A',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower' }
            ]
          }
        ],
        crew_members: [
          { crew_member_id: 'crew1', first_name: 'John', last_name: 'Doe' }
        ],
        team_managers: [
          {
            user_id: 'user1',
            club_affiliation: 'Club A',
            total_paid: 100.5,  // Should become 100.50
            outstanding_balance: 25.123,  // Should become 25.12
            payment_status: 'Partial Payment'
          }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const config = {
      marathon_bow_start: 1,
      semi_marathon_bow_start: 41
    }

    const eligibleBoats = filterEligibleBoats(mockDataWithPayments.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(mockDataWithPayments, boatAssignments, raceAssignments, 'fr')

    // Verify currency formatting with exactly 2 decimal places
    expect(result[0]['Total payé (EUR)']).toBe('100.50')
    expect(result[0]['Solde impayé (EUR)']).toBe('25.12')
  })

  it('should include payment balance columns in English locale', () => {
    const mockDataWithPayments = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'Club A',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower' }
            ]
          }
        ],
        crew_members: [
          { crew_member_id: 'crew1', first_name: 'John', last_name: 'Doe' }
        ],
        team_managers: [
          {
            user_id: 'user1',
            club_affiliation: 'Club A',
            total_paid: 200.00,
            outstanding_balance: 0.00,
            payment_status: 'Paid in Full'
          }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const config = {
      marathon_bow_start: 1,
      semi_marathon_bow_start: 41
    }

    const eligibleBoats = filterEligibleBoats(mockDataWithPayments.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(mockDataWithPayments, boatAssignments, raceAssignments, 'en')

    expect(result[0]).toHaveProperty('Total Paid (EUR)')
    expect(result[0]).toHaveProperty('Outstanding Balance (EUR)')
    expect(result[0]).toHaveProperty('Payment Status')
    expect(result[0]['Total Paid (EUR)']).toBe('200.00')
    expect(result[0]['Outstanding Balance (EUR)']).toBe('0.00')
    expect(result[0]['Payment Status']).toBe('Paid in Full')
  })

  it('should handle missing payment data gracefully', () => {
    const mockDataWithoutPayments = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'Club A',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower' }
            ]
          }
        ],
        crew_members: [
          { crew_member_id: 'crew1', first_name: 'John', last_name: 'Doe' }
        ],
        team_managers: [
          {
            user_id: 'user1',
            club_affiliation: 'Club A'
            // No payment data
          }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const config = {
      marathon_bow_start: 1,
      semi_marathon_bow_start: 41
    }

    const eligibleBoats = filterEligibleBoats(mockDataWithoutPayments.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(mockDataWithoutPayments, boatAssignments, raceAssignments, 'fr')

    // Should default to 0.00 and 'No Payment'
    expect(result[0]['Total payé (EUR)']).toBe('0.00')
    expect(result[0]['Solde impayé (EUR)']).toBe('0.00')
    expect(result[0]['Statut de paiement']).toBe('No Payment')
  })
})
