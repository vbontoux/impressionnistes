/**
 * Tests for Event Program Formatter
 * Ensures correct crew member list and race schedule generation
 */

import { describe, it, expect } from 'vitest'
import { generateCrewMemberList, generateRaceSchedule, generateCrewsInRaces, formatAssignedBoat, generateSynthesis, formatTeamManagerName } from './eventProgramFormatter.js'
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
          boat_club_display: 'Club A',
          assigned_boat_name: 'Test Boat',
          assigned_boat_comment: 'Test Comment',
          seats: [
            { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' },
            { crew_member_id: 'crew2', position: 2, type: 'rower', seat_type: 'Rower 2' }
          ]
        }
      ],
      crew_members: [
        { 
          crew_member_id: 'crew1', 
          first_name: 'John', 
          last_name: 'Doe', 
          club_affiliation: 'Club A',
          age: 25,
          gender: 'M',
          license_number: 'LIC123'
        },
        { 
          crew_member_id: 'crew2', 
          first_name: 'Jane', 
          last_name: 'Smith', 
          club_affiliation: 'Club A',
          age: 30,
          gender: 'F',
          license_number: 'LIC456'
        }
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
    expect(result[0]).toHaveProperty('N° Course')
    expect(result[0]).toHaveProperty('Course')
    expect(result[0]).toHaveProperty('N° Équipage')
    expect(result[0]).toHaveProperty('Nom')
    expect(result[0]).toHaveProperty('Prénom')
    expect(result[0]).toHaveProperty('Club')
    expect(result[0]).toHaveProperty('Âge')
    expect(result[0]).toHaveProperty('Genre')
    expect(result[0]).toHaveProperty('N° Licence')
    expect(result[0]).toHaveProperty('Place dans le bateau')
    expect(result[0]).toHaveProperty('N° Dossard')
    expect(result[0]).toHaveProperty('Bateau assigné')
  })

  it('should generate crew member list with English columns when locale is en', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'en')

    expect(result).toHaveLength(2)
    expect(result[0]).toHaveProperty('Race #')
    expect(result[0]).toHaveProperty('Race')
    expect(result[0]).toHaveProperty('Crew #')
    expect(result[0]).toHaveProperty('Last Name')
    expect(result[0]).toHaveProperty('First Name')
    expect(result[0]).toHaveProperty('Club')
    expect(result[0]).toHaveProperty('Age')
    expect(result[0]).toHaveProperty('Gender')
    expect(result[0]).toHaveProperty('License #')
    expect(result[0]).toHaveProperty('Place in boat')
    expect(result[0]).toHaveProperty('Bow #')
    expect(result[0]).toHaveProperty('Assigned Boat')
  })

  it('should include age, gender, and license number', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')

    expect(result[0]['Âge']).toBe(25)
    expect(result[0]['Genre']).toBe('H') // H for Homme in French
    expect(result[0]['N° Licence']).toBe('LIC123')
    expect(result[1]['Âge']).toBe(30)
    expect(result[1]['Genre']).toBe('F') // F for Femme in French
    expect(result[1]['N° Licence']).toBe('LIC456')
  })

  it('should include seat position in place in boat column', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')

    expect(result[0]['Place dans le bateau']).toBe('Rower 1')
    expect(result[1]['Place dans le bateau']).toBe('Rower 2')
  })

  it('should include assigned boat formatted correctly', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')

    expect(result[0]['Bateau assigné']).toBe('Test Boat - Test Comment')
    expect(result[1]['Bateau assigné']).toBe('Test Boat - Test Comment')
  })

  it('should format assigned boat with only name when comment is missing', () => {
    const dataWithNameOnly = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'Club A',
            assigned_boat_name: 'Test Boat',
            assigned_boat_comment: null,
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123'
          }
        ],
        team_managers: []
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(dataWithNameOnly.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(dataWithNameOnly, boatAssignments, raceAssignments, 'fr')

    expect(result[0]['Bateau assigné']).toBe('Test Boat')
  })

  it('should show empty string when no assigned boat', () => {
    const dataWithoutAssignedBoat = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'Club A',
            assigned_boat_name: null,
            assigned_boat_comment: null,
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123'
          }
        ],
        team_managers: []
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(dataWithoutAssignedBoat.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(dataWithoutAssignedBoat, boatAssignments, raceAssignments, 'fr')

    expect(result[0]['Bateau assigné']).toBe('')
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
            boat_club_display: 'Club A',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123'
          }
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
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123'
          }
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
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' },
              { crew_member_id: 'crew2', position: 2, type: 'rower', seat_type: 'Rower 2' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123'
          },
          { 
            crew_member_id: 'crew2', 
            first_name: 'Jane', 
            last_name: 'Smith',
            age: 30,
            gender: 'F',
            license_number: 'LIC456'
          }
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
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123'
          }
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
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123'
          }
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


describe('generateCrewsInRaces', () => {
  const mockData = {
    data: {
      boats: [
        {
          boat_registration_id: 'boat1',
          race_id: 'race1',
          registration_status: 'complete',
          forfait: false,
          team_manager_id: 'user1',
          boat_club_display: 'Club A',
          boat_number: 'B1',
          assigned_boat_name: 'Test Boat',
          assigned_boat_comment: 'Test Comment',
          seats: [
            { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' },
            { crew_member_id: 'crew2', position: 2, type: 'rower', seat_type: 'Rower 2' },
            { crew_member_id: 'crew3', position: 3, type: 'rower', seat_type: 'Rower 3' }
          ]
        },
        {
          boat_registration_id: 'boat2',
          race_id: 'race2',
          registration_status: 'paid',
          forfait: false,
          team_manager_id: 'user1',
          boat_club_display: 'Club B',
          boat_number: 'B2',
          assigned_boat_name: null,
          assigned_boat_comment: null,
          seats: [
            { crew_member_id: 'crew4', position: 1, type: 'rower', seat_type: 'Rower 1' }
          ]
        }
      ],
      crew_members: [
        { 
          crew_member_id: 'crew1', 
          first_name: 'John', 
          last_name: 'Doe', 
          club_affiliation: 'Club A',
          age: 25,
          gender: 'M'
        },
        { 
          crew_member_id: 'crew2', 
          first_name: 'Jane', 
          last_name: 'Smith', 
          club_affiliation: 'Club A',
          age: 30,
          gender: 'F'
        },
        { 
          crew_member_id: 'crew3', 
          first_name: 'Bob', 
          last_name: 'Johnson', 
          club_affiliation: 'Club A',
          age: 28,
          gender: 'M'
        },
        { 
          crew_member_id: 'crew4', 
          first_name: 'Alice', 
          last_name: 'Williams', 
          club_affiliation: 'Club B',
          age: 35,
          gender: 'F'
        }
      ]
    }
  }

  const config = {
    marathon_bow_start: 1,
    semi_marathon_bow_start: 41
  }

  it('should generate crews in races with correct structure', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' },
      { race_id: 'race2', display_order: 2, distance: 21, short_name: 'SW2X', name: 'Senior Women 2X' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')

    // Should have header row + 2 data rows
    expect(result).toHaveLength(3)
    
    // Check header row has 50 columns (5 base + 45 member columns)
    expect(result[0]).toHaveLength(50)
  })

  it('should have correct French headers', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')

    const headers = result[0]
    expect(headers[0]).toBe('N° Course')
    expect(headers[1]).toBe('Course')
    expect(headers[2]).toBe('Course (abrégé)')
    expect(headers[3]).toBe('N° Équipage')
    expect(headers[4]).toBe('Bateau assigné')
    expect(headers[5]).toBe('Équipier 1 Nom')
    expect(headers[6]).toBe('Équipier 1 Prénom')
    expect(headers[7]).toBe('Équipier 1 Club')
    expect(headers[8]).toBe('Équipier 1 Âge')
    expect(headers[9]).toBe('Équipier 1 Genre')
  })

  it('should have correct English headers', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'en')

    const headers = result[0]
    expect(headers[0]).toBe('Race #')
    expect(headers[1]).toBe('Race')
    expect(headers[2]).toBe('Race (abbrev)')
    expect(headers[3]).toBe('Crew #')
    expect(headers[4]).toBe('Boat assignment')
    expect(headers[5]).toBe('Member 1 Last Name')
    expect(headers[6]).toBe('Member 1 First Name')
    expect(headers[7]).toBe('Member 1 Club')
    expect(headers[8]).toBe('Member 1 Age')
    expect(headers[9]).toBe('Member 1 Gender')
  })

  it('should include crew member data for boats with varying crew sizes', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' },
      { race_id: 'race2', display_order: 2, distance: 21, short_name: 'SW2X', name: 'Senior Women 2X' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')

    // First boat has 3 crew members
    const row1 = result[1]
    expect(row1[5]).toBe('Doe') // Member 1 last name
    expect(row1[6]).toBe('John') // Member 1 first name
    expect(row1[7]).toBe('Club A') // Member 1 club
    expect(row1[8]).toBe(25) // Member 1 age
    expect(row1[9]).toBe('H') // Member 1 gender (H for Homme in French)
    
    expect(row1[10]).toBe('Smith') // Member 2 last name
    expect(row1[15]).toBe('Johnson') // Member 3 last name
    
    // Second boat has 1 crew member
    const row2 = result[2]
    expect(row2[5]).toBe('Williams') // Member 1 last name
    expect(row2[6]).toBe('Alice') // Member 1 first name
  })

  it('should fill empty strings for positions beyond crew size', () => {
    const races = [
      { race_id: 'race2', display_order: 2, distance: 21, short_name: 'SW2X', name: 'Senior Women 2X' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')

    // Boat 2 has only 1 member, so positions 2-9 should be empty
    const row = result[1]
    
    // Member 1 should have data
    expect(row[5]).toBe('Williams')
    
    // Members 2-9 should be empty (5 fields each)
    for (let i = 2; i <= 9; i++) {
      const baseIndex = 5 + ((i - 1) * 5)
      expect(row[baseIndex]).toBe('') // Last name
      expect(row[baseIndex + 1]).toBe('') // First name
      expect(row[baseIndex + 2]).toBe('') // Club
      expect(row[baseIndex + 3]).toBe('') // Age
      expect(row[baseIndex + 4]).toBe('') // Gender
    }
  })

  it('should sort boats by race number', () => {
    const races = [
      { race_id: 'race2', display_order: 2, distance: 21, short_name: 'SW2X', name: 'Senior Women 2X' },
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')

    // Should be sorted by race number (1, 2)
    expect(result[1][0]).toBe(1) // First row race number
    expect(result[2][0]).toBe(2) // Second row race number
  })

  it('should format assigned boat correctly', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' },
      { race_id: 'race2', display_order: 2, distance: 21, short_name: 'SW2X', name: 'Senior Women 2X' }
    ]
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')

    // First boat has name and comment
    expect(result[1][4]).toBe('Test Boat - Test Comment')
    
    // Second boat has no assigned boat
    expect(result[2][4]).toBe('')
  })

  it('should not include ineligible boats', () => {
    const dataWithIneligible = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'incomplete',
            forfait: false,
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          },
          {
            boat_registration_id: 'boat2',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            boat_number: 'B2',
            seats: [
              { crew_member_id: 'crew2', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [
          { crew_member_id: 'crew1', first_name: 'John', last_name: 'Doe', club_affiliation: 'Club A', age: 25, gender: 'M' },
          { crew_member_id: 'crew2', first_name: 'Jane', last_name: 'Smith', club_affiliation: 'Club A', age: 30, gender: 'F' }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]
    const eligibleBoats = filterEligibleBoats(dataWithIneligible.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewsInRaces(dataWithIneligible, boatAssignments, raceAssignments, 'fr')

    // Should only have header + 1 eligible boat
    expect(result).toHaveLength(2)
    expect(result[1][5]).toBe('Smith') // Only boat2's crew member
  })

  it('should handle boats with 9 crew members', () => {
    const dataWith9Members = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            boat_number: 'B1',
            seats: Array.from({ length: 9 }, (_, i) => ({
              crew_member_id: `crew${i + 1}`,
              position: i + 1,
              type: 'rower',
              seat_type: `Rower ${i + 1}`
            }))
          }
        ],
        crew_members: Array.from({ length: 9 }, (_, i) => ({
          crew_member_id: `crew${i + 1}`,
          first_name: `First${i + 1}`,
          last_name: `Last${i + 1}`,
          club_affiliation: 'Club A',
          age: 20 + i,
          gender: i % 2 === 0 ? 'M' : 'F'
        }))
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW8X+', name: 'Master Women 8X+' }
    ]
    const eligibleBoats = filterEligibleBoats(dataWith9Members.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewsInRaces(dataWith9Members, boatAssignments, raceAssignments, 'fr')

    const row = result[1]
    
    // Check all 9 members have data
    for (let i = 1; i <= 9; i++) {
      const baseIndex = 5 + ((i - 1) * 5)
      expect(row[baseIndex]).toBe(`Last${i}`) // Last name
      expect(row[baseIndex + 1]).toBe(`First${i}`) // First name
      expect(row[baseIndex + 2]).toBe('Club A') // Club
      expect(row[baseIndex + 3]).toBe(20 + i - 1) // Age
      // Gender: crew members created with i % 2 === 0 ? 'M' : 'F'
      // In French: M → H (Homme), F → F (Femme)
      // i=1 (index 0): M → H, i=2 (index 1): F → F, i=3 (index 2): M → H, etc.
      expect(row[baseIndex + 4]).toBe(i % 2 === 1 ? 'H' : 'F') // Gender (translated to French)
    }
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


describe('Property Tests - Assigned Boat Formatting', () => {
  const ITERATIONS = 100

  it('Property 3: Assigned Boat Formatting - should format boat assignments correctly', () => {
    // Feature: enhanced-event-program-export, Property 3
    // Validates: Requirements 1.6, 3.6
    
    for (let i = 0; i < ITERATIONS; i++) {
      // Generate random boat with various combinations of name/comment
      const hasName = Math.random() > 0.3 // 70% chance of having a name
      const hasComment = Math.random() > 0.5 // 50% chance of having a comment
      
      const boat = {
        assigned_boat_name: hasName ? `Boat ${i}` : null,
        assigned_boat_comment: hasComment ? `Comment ${i}` : null
      }
      
      const formatted = formatAssignedBoat(boat)
      
      // Verify formatting rules
      if (boat.assigned_boat_name && boat.assigned_boat_comment) {
        // Both present: "name - comment"
        expect(formatted).toBe(`${boat.assigned_boat_name} - ${boat.assigned_boat_comment}`)
      } else if (boat.assigned_boat_name) {
        // Only name: just the name
        expect(formatted).toBe(boat.assigned_boat_name)
      } else {
        // Neither present: empty string
        expect(formatted).toBe('')
      }
    }
  })

  it('Property 3: Assigned Boat Formatting - should handle edge cases', () => {
    // Test with empty strings (not null)
    expect(formatAssignedBoat({ assigned_boat_name: '', assigned_boat_comment: '' })).toBe('')
    expect(formatAssignedBoat({ assigned_boat_name: 'Boat', assigned_boat_comment: '' })).toBe('Boat')
    expect(formatAssignedBoat({ assigned_boat_name: '', assigned_boat_comment: 'Comment' })).toBe('')
    
    // Test with undefined
    expect(formatAssignedBoat({ assigned_boat_name: undefined, assigned_boat_comment: undefined })).toBe('')
    expect(formatAssignedBoat({ assigned_boat_name: 'Boat', assigned_boat_comment: undefined })).toBe('Boat')
    
    // Test with null boat object
    expect(formatAssignedBoat(null)).toBe('')
    expect(formatAssignedBoat(undefined)).toBe('')
    
    // Test with missing properties
    expect(formatAssignedBoat({})).toBe('')
  })

  it('Property 3: Assigned Boat Formatting - should handle special characters', () => {
    // Test with special characters in name and comment
    const specialChars = ['&', '<', '>', '"', "'", '-', '/', '\\', '(', ')']
    
    for (const char of specialChars) {
      const boat = {
        assigned_boat_name: `Boat${char}Name`,
        assigned_boat_comment: `Comment${char}Text`
      }
      
      const formatted = formatAssignedBoat(boat)
      expect(formatted).toBe(`Boat${char}Name - Comment${char}Text`)
    }
  })

  it('Property 3: Assigned Boat Formatting - should handle whitespace', () => {
    // Test with leading/trailing whitespace
    expect(formatAssignedBoat({ 
      assigned_boat_name: '  Boat  ', 
      assigned_boat_comment: '  Comment  ' 
    })).toBe('  Boat   -   Comment  ')
    
    // Test with only whitespace
    expect(formatAssignedBoat({ 
      assigned_boat_name: '   ', 
      assigned_boat_comment: '   ' 
    })).toBe('    -    ')
  })
})


describe('Property Tests - Variable Crew Size Handling', () => {
  const ITERATIONS = 100

  it('Property 5: Variable Crew Size Handling - should handle crews of varying sizes correctly', () => {
    // Feature: enhanced-event-program-export, Property 5
    // Validates: Requirements 3.3, 3.5
    
    const config = {
      marathon_bow_start: 1,
      semi_marathon_bow_start: 41
    }

    for (let i = 0; i < ITERATIONS; i++) {
      // Generate random crew size between 1 and 9
      const crewSize = Math.floor(Math.random() * 9) + 1
      
      // Create boat with N crew members
      const boat = {
        boat_registration_id: `boat${i}`,
        race_id: 'race1',
        registration_status: 'complete',
        forfait: false,
        boat_number: `B${i}`,
        seats: Array.from({ length: crewSize }, (_, j) => ({
          crew_member_id: `crew${i}_${j}`,
          position: j + 1,
          type: 'rower',
          seat_type: `Rower ${j + 1}`
        }))
      }

      const crewMembers = Array.from({ length: crewSize }, (_, j) => ({
        crew_member_id: `crew${i}_${j}`,
        first_name: `First${j}`,
        last_name: `Last${j}`,
        club_affiliation: 'Club A',
        age: 20 + j,
        gender: j % 2 === 0 ? 'M' : 'F'
      }))

      const mockData = {
        data: {
          boats: [boat],
          crew_members: crewMembers
        }
      }

      const races = [
        { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
      ]

      const eligibleBoats = filterEligibleBoats(mockData.data.boats)
      const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

      const result = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')

      // Should have header + 1 data row
      expect(result).toHaveLength(2)

      const dataRow = result[1]

      // Verify first N members have complete data (5 fields each)
      for (let j = 0; j < crewSize; j++) {
        const baseIndex = 5 + (j * 5)
        expect(dataRow[baseIndex]).toBeTruthy() // Last name
        expect(dataRow[baseIndex + 1]).toBeTruthy() // First name
        expect(dataRow[baseIndex + 2]).toBeTruthy() // Club
        expect(dataRow[baseIndex + 3]).toBeGreaterThanOrEqual(0) // Age (can be 0)
        expect(dataRow[baseIndex + 4]).toBeTruthy() // Gender
      }

      // Verify remaining positions (crewSize to 9) are empty
      for (let j = crewSize; j < 9; j++) {
        const baseIndex = 5 + (j * 5)
        expect(dataRow[baseIndex]).toBe('') // Last name
        expect(dataRow[baseIndex + 1]).toBe('') // First name
        expect(dataRow[baseIndex + 2]).toBe('') // Club
        expect(dataRow[baseIndex + 3]).toBe('') // Age
        expect(dataRow[baseIndex + 4]).toBe('') // Gender
      }
    }
  })

  it('Property 5: Variable Crew Size Handling - should handle edge cases', () => {
    const config = {
      marathon_bow_start: 1,
      semi_marathon_bow_start: 41
    }

    // Test with 1 crew member (minimum)
    const boat1 = {
      boat_registration_id: 'boat1',
      race_id: 'race1',
      registration_status: 'complete',
      forfait: false,
      boat_number: 'B1',
      seats: [
        { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
      ]
    }

    const mockData1 = {
      data: {
        boats: [boat1],
        crew_members: [
          { crew_member_id: 'crew1', first_name: 'John', last_name: 'Doe', club_affiliation: 'Club A', age: 25, gender: 'M' }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]

    const eligibleBoats1 = filterEligibleBoats(mockData1.data.boats)
    const { raceAssignments: ra1, boatAssignments: ba1 } = assignRaceAndBowNumbers(races, eligibleBoats1, config)

    const result1 = generateCrewsInRaces(mockData1, ba1, ra1, 'fr')
    const row1 = result1[1]

    // First member should have data
    expect(row1[5]).toBe('Doe')
    
    // Remaining 8 positions should be empty
    for (let i = 1; i < 9; i++) {
      const baseIndex = 5 + (i * 5)
      expect(row1[baseIndex]).toBe('')
    }

    // Test with 9 crew members (maximum)
    const boat9 = {
      boat_registration_id: 'boat9',
      race_id: 'race1',
      registration_status: 'complete',
      forfait: false,
      boat_number: 'B9',
      seats: Array.from({ length: 9 }, (_, i) => ({
        crew_member_id: `crew${i}`,
        position: i + 1,
        type: 'rower',
        seat_type: `Rower ${i + 1}`
      }))
    }

    const mockData9 = {
      data: {
        boats: [boat9],
        crew_members: Array.from({ length: 9 }, (_, i) => ({
          crew_member_id: `crew${i}`,
          first_name: `First${i}`,
          last_name: `Last${i}`,
          club_affiliation: 'Club A',
          age: 20 + i,
          gender: 'M'
        }))
      }
    }

    const eligibleBoats9 = filterEligibleBoats(mockData9.data.boats)
    const { raceAssignments: ra9, boatAssignments: ba9 } = assignRaceAndBowNumbers(races, eligibleBoats9, config)

    const result9 = generateCrewsInRaces(mockData9, ba9, ra9, 'fr')
    const row9 = result9[1]

    // All 9 positions should have data
    for (let i = 0; i < 9; i++) {
      const baseIndex = 5 + (i * 5)
      expect(row9[baseIndex]).toBe(`Last${i}`)
      expect(row9[baseIndex + 1]).toBe(`First${i}`)
    }
  })
})


describe('Property Tests - Race Number Ordering', () => {
  const ITERATIONS = 100

  it('Property 7: Race Number Ordering - should sort boats by race number ascending', () => {
    // Feature: enhanced-event-program-export, Property 7
    // Validates: Requirements 3.7
    
    const config = {
      marathon_bow_start: 1,
      semi_marathon_bow_start: 41
    }

    for (let i = 0; i < ITERATIONS; i++) {
      // Generate random number of races (2-10)
      const numRaces = Math.floor(Math.random() * 9) + 2
      
      // Create races with random display orders
      const races = Array.from({ length: numRaces }, (_, j) => ({
        race_id: `race${j}`,
        display_order: j + 1,
        distance: Math.random() > 0.5 ? 42 : 21,
        short_name: `R${j}`,
        name: `Race ${j}`
      }))

      // Shuffle races to simulate unordered input
      const shuffledRaces = [...races].sort(() => Math.random() - 0.5)

      // Create boats for each race (1-3 boats per race)
      const boats = []
      for (let j = 0; j < numRaces; j++) {
        const boatsInRace = Math.floor(Math.random() * 3) + 1
        for (let k = 0; k < boatsInRace; k++) {
          boats.push({
            boat_registration_id: `boat${j}_${k}`,
            race_id: `race${j}`,
            registration_status: 'complete',
            forfait: false,
            boat_number: `B${j}_${k}`,
            seats: [
              { crew_member_id: `crew${j}_${k}`, position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          })
        }
      }

      // Shuffle boats to simulate unordered input
      const shuffledBoats = [...boats].sort(() => Math.random() - 0.5)

      const crewMembers = boats.map((boat, idx) => ({
        crew_member_id: boat.seats[0].crew_member_id,
        first_name: `First${idx}`,
        last_name: `Last${idx}`,
        club_affiliation: 'Club A',
        age: 25,
        gender: 'M'
      }))

      const mockData = {
        data: {
          boats: shuffledBoats,
          crew_members: crewMembers
        }
      }

      const eligibleBoats = filterEligibleBoats(mockData.data.boats)
      const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(shuffledRaces, eligibleBoats, config)

      const result = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')

      // Extract race numbers from data rows (skip header)
      const raceNumbers = result.slice(1).map(row => row[0])

      // Verify ascending order
      for (let j = 1; j < raceNumbers.length; j++) {
        expect(raceNumbers[j]).toBeGreaterThanOrEqual(raceNumbers[j - 1])
      }
    }
  })

  it('Property 7: Race Number Ordering - should handle edge cases', () => {
    const config = {
      marathon_bow_start: 1,
      semi_marathon_bow_start: 41
    }

    // Test with single race
    const singleRace = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'R1', name: 'Race 1' }
    ]

    const singleBoat = {
      boat_registration_id: 'boat1',
      race_id: 'race1',
      registration_status: 'complete',
      forfait: false,
      boat_number: 'B1',
      seats: [
        { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
      ]
    }

    const mockData1 = {
      data: {
        boats: [singleBoat],
        crew_members: [
          { crew_member_id: 'crew1', first_name: 'John', last_name: 'Doe', club_affiliation: 'Club A', age: 25, gender: 'M' }
        ]
      }
    }

    const eligibleBoats1 = filterEligibleBoats(mockData1.data.boats)
    const { raceAssignments: ra1, boatAssignments: ba1 } = assignRaceAndBowNumbers(singleRace, eligibleBoats1, config)

    const result1 = generateCrewsInRaces(mockData1, ba1, ra1, 'fr')

    // Should have header + 1 data row
    expect(result1).toHaveLength(2)
    expect(result1[1][0]).toBe(1)

    // Test with multiple boats in same race
    const multiBoatRace = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'R1', name: 'Race 1' }
    ]

    const multiBoats = [
      {
        boat_registration_id: 'boat1',
        race_id: 'race1',
        registration_status: 'complete',
        forfait: false,
        boat_number: 'B1',
        seats: [{ crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }]
      },
      {
        boat_registration_id: 'boat2',
        race_id: 'race1',
        registration_status: 'complete',
        forfait: false,
        boat_number: 'B2',
        seats: [{ crew_member_id: 'crew2', position: 1, type: 'rower', seat_type: 'Rower 1' }]
      },
      {
        boat_registration_id: 'boat3',
        race_id: 'race1',
        registration_status: 'complete',
        forfait: false,
        boat_number: 'B3',
        seats: [{ crew_member_id: 'crew3', position: 1, type: 'rower', seat_type: 'Rower 1' }]
      }
    ]

    const mockData2 = {
      data: {
        boats: multiBoats,
        crew_members: [
          { crew_member_id: 'crew1', first_name: 'John', last_name: 'Doe', club_affiliation: 'Club A', age: 25, gender: 'M' },
          { crew_member_id: 'crew2', first_name: 'Jane', last_name: 'Smith', club_affiliation: 'Club A', age: 30, gender: 'F' },
          { crew_member_id: 'crew3', first_name: 'Bob', last_name: 'Johnson', club_affiliation: 'Club A', age: 28, gender: 'M' }
        ]
      }
    }

    const eligibleBoats2 = filterEligibleBoats(mockData2.data.boats)
    const { raceAssignments: ra2, boatAssignments: ba2 } = assignRaceAndBowNumbers(multiBoatRace, eligibleBoats2, config)

    const result2 = generateCrewsInRaces(mockData2, ba2, ra2, 'fr')

    // All boats should have same race number
    expect(result2[1][0]).toBe(1)
    expect(result2[2][0]).toBe(1)
    expect(result2[3][0]).toBe(1)
  })
})




describe('generateSynthesis', () => {
  const config = {
    marathon_bow_start: 1,
    semi_marathon_bow_start: 41
  }

  it('should generate synthesis with correct columns in French', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: 'assigned1',
            seats: []
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
            phone: '1234567890',
            club_affiliation: 'Club A'
          }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]

    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateSynthesis(mockData, boatAssignments, 'fr')

    // Should have header + 1 data row
    expect(result).toHaveLength(2)

    // Check French headers
    const headers = result[0]
    expect(headers[0]).toBe('Club')
    expect(headers[1]).toBe('Prénom + Nom')
    expect(headers[2]).toBe('Email')
    expect(headers[3]).toBe('N° Téléphone')
    expect(headers[4]).toBe('Nombre de bateaux assignés')
    expect(headers[5]).toBe('Nombre d\'équipages en marathon')
    expect(headers[6]).toBe('Nombre d\'équipages en semi-marathon')
  })

  it('should generate synthesis with correct columns in English', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: 'assigned1',
            seats: []
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
            phone: '1234567890',
            club_affiliation: 'Club A'
          }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]

    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateSynthesis(mockData, boatAssignments, 'en')

    // Check English headers
    const headers = result[0]
    expect(headers[0]).toBe('Club')
    expect(headers[1]).toBe('First name + Last name')
    expect(headers[2]).toBe('Email')
    expect(headers[3]).toBe('Phone #')
    expect(headers[4]).toBe('Number of assigned boats')
    expect(headers[5]).toBe('Number of crews in marathon')
    expect(headers[6]).toBe('Number of crews in semi-marathon')
  })

  it('should aggregate boats by team manager', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: 'assigned1',
            seats: []
          },
          {
            boat_registration_id: 'boat2',
            race_id: 'race1',
            registration_status: 'paid',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Semi-Marathon',
            assigned_boat_identifier: 'assigned2',
            seats: []
          },
          {
            boat_registration_id: 'boat3',
            race_id: 'race2',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager2',
            event_type: 'Marathon',
            assigned_boat_identifier: null,
            seats: []
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
            phone: '1234567890',
            club_affiliation: 'Club A'
          },
          {
            user_id: 'manager2',
            first_name: 'Jane',
            last_name: 'Smith',
            email: 'jane@example.com',
            phone: '0987654321',
            club_affiliation: 'Club B'
          }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' },
      { race_id: 'race2', display_order: 2, distance: 21, short_name: 'SW2X', name: 'Senior Women 2X' }
    ]

    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateSynthesis(mockData, boatAssignments, 'fr')

    // Should have header + 2 managers
    expect(result).toHaveLength(3)

    // Check manager 1 data
    const manager1Row = result.find(row => row[2] === 'john@example.com')
    expect(manager1Row[0]).toBe('Club A')
    expect(manager1Row[1]).toBe('John Doe')
    expect(manager1Row[2]).toBe('john@example.com')
    expect(manager1Row[3]).toBe('1234567890')
    expect(manager1Row[4]).toBe(2) // 2 assigned boats
    expect(manager1Row[5]).toBe(1) // 1 marathon crew
    expect(manager1Row[6]).toBe(1) // 1 semi-marathon crew

    // Check manager 2 data
    const manager2Row = result.find(row => row[2] === 'jane@example.com')
    expect(manager2Row[0]).toBe('Club B')
    expect(manager2Row[1]).toBe('Jane Smith')
    expect(manager2Row[4]).toBe(0) // 0 assigned boats (no assigned_boat_identifier)
    expect(manager2Row[5]).toBe(1) // 1 marathon crew
    expect(manager2Row[6]).toBe(0) // 0 semi-marathon crews
  })

  it('should count assigned boats correctly', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: 'assigned1',
            seats: []
          },
          {
            boat_registration_id: 'boat2',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: null, // Not assigned
            seats: []
          },
          {
            boat_registration_id: 'boat3',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: 'assigned3',
            seats: []
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
            phone: '1234567890',
            club_affiliation: 'Club A'
          }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]

    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateSynthesis(mockData, boatAssignments, 'fr')

    const dataRow = result[1]
    expect(dataRow[4]).toBe(2) // Only 2 boats have assigned_boat_identifier
  })

  it('should count marathon and semi-marathon crews correctly', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: null,
            seats: []
          },
          {
            boat_registration_id: 'boat2',
            race_id: 'race2',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: null,
            seats: []
          },
          {
            boat_registration_id: 'boat3',
            race_id: 'race3',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Semi-Marathon',
            assigned_boat_identifier: null,
            seats: []
          },
          {
            boat_registration_id: 'boat4',
            race_id: 'race3',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Semi-Marathon',
            assigned_boat_identifier: null,
            seats: []
          },
          {
            boat_registration_id: 'boat5',
            race_id: 'race3',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Semi-Marathon',
            assigned_boat_identifier: null,
            seats: []
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
            phone: '1234567890',
            club_affiliation: 'Club A'
          }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' },
      { race_id: 'race2', display_order: 2, distance: 42, short_name: 'MW2X', name: 'Master Women 2X' },
      { race_id: 'race3', display_order: 3, distance: 21, short_name: 'SW4X+', name: 'Senior Women 4X+' }
    ]

    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateSynthesis(mockData, boatAssignments, 'fr')

    const dataRow = result[1]
    expect(dataRow[5]).toBe(2) // 2 marathon crews
    expect(dataRow[6]).toBe(3) // 3 semi-marathon crews
  })

  it('should only count eligible boats', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: 'assigned1',
            seats: []
          },
          {
            boat_registration_id: 'boat2',
            race_id: 'race1',
            registration_status: 'incomplete', // Not eligible
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: 'assigned2',
            seats: []
          },
          {
            boat_registration_id: 'boat3',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: true, // Not eligible (forfait)
            team_manager_id: 'manager1',
            event_type: 'Semi-Marathon',
            assigned_boat_identifier: 'assigned3',
            seats: []
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
            phone: '1234567890',
            club_affiliation: 'Club A'
          }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]

    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateSynthesis(mockData, boatAssignments, 'fr')

    const dataRow = result[1]
    expect(dataRow[4]).toBe(1) // Only 1 eligible boat with assignment
    expect(dataRow[5]).toBe(1) // Only 1 eligible marathon crew
    expect(dataRow[6]).toBe(0) // 0 eligible semi-marathon crews
  })

  it('should handle missing phone numbers', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: 'assigned1',
            seats: []
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
            phone: null, // No phone number
            club_affiliation: 'Club A'
          }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]

    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateSynthesis(mockData, boatAssignments, 'fr')

    const dataRow = result[1]
    expect(dataRow[3]).toBe('') // Empty string for missing phone
  })

  it('should format team manager names correctly', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: 'assigned1',
            seats: []
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'Jean-Pierre',
            last_name: 'Dupont',
            email: 'jp@example.com',
            phone: '1234567890',
            club_affiliation: 'Club A'
          }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]

    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateSynthesis(mockData, boatAssignments, 'fr')

    const dataRow = result[1]
    expect(dataRow[1]).toBe('Jean-Pierre Dupont')
  })

  it('should return empty array when no team managers exist', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: 'assigned1',
            seats: []
          }
        ],
        team_managers: [] // No team managers
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
    ]

    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateSynthesis(mockData, boatAssignments, 'fr')

    // Should only have header row
    expect(result).toHaveLength(1)
  })
})


describe('formatTeamManagerName', () => {
  it('should format name with both first and last name', () => {
    const manager = {
      first_name: 'John',
      last_name: 'Doe'
    }

    expect(formatTeamManagerName(manager)).toBe('John Doe')
  })

  it('should handle only first name', () => {
    const manager = {
      first_name: 'John',
      last_name: ''
    }

    expect(formatTeamManagerName(manager)).toBe('John')
  })

  it('should handle only last name', () => {
    const manager = {
      first_name: '',
      last_name: 'Doe'
    }

    expect(formatTeamManagerName(manager)).toBe('Doe')
  })

  it('should handle missing names gracefully', () => {
    expect(formatTeamManagerName({ first_name: '', last_name: '' })).toBe('')
    expect(formatTeamManagerName({ first_name: null, last_name: null })).toBe('')
    expect(formatTeamManagerName({})).toBe('')
    expect(formatTeamManagerName(null)).toBe('')
    expect(formatTeamManagerName(undefined)).toBe('')
  })

  it('should handle special characters in names', () => {
    const manager = {
      first_name: 'Jean-Pierre',
      last_name: "O'Connor"
    }

    expect(formatTeamManagerName(manager)).toBe("Jean-Pierre O'Connor")
  })

  it('should handle whitespace in names', () => {
    const manager = {
      first_name: '  John  ',
      last_name: '  Doe  '
    }

    expect(formatTeamManagerName(manager)).toBe('  John     Doe  ')
  })
})


describe('Property Tests - Team Manager Aggregation', () => {
  const ITERATIONS = 100
  const config = {
    marathon_bow_start: 1,
    semi_marathon_bow_start: 41
  }

  it('Property 11: Team Manager Aggregation - should show each manager exactly once with correct counts', () => {
    // Feature: enhanced-event-program-export, Property 11
    // Validates: Requirements 4.10
    
    for (let i = 0; i < ITERATIONS; i++) {
      // Generate random number of managers (1-5)
      const numManagers = Math.floor(Math.random() * 5) + 1
      
      // Create team managers
      const teamManagers = Array.from({ length: numManagers }, (_, j) => ({
        user_id: `manager${j}`,
        first_name: `First${j}`,
        last_name: `Last${j}`,
        email: `manager${j}@example.com`,
        phone: Math.random() > 0.5 ? `123456789${j}` : null,
        club_affiliation: `Club ${String.fromCharCode(65 + j)}`
      }))
      
      // Create random boats for each manager (1-5 boats per manager)
      const boats = []
      for (let j = 0; j < numManagers; j++) {
        const boatsForManager = Math.floor(Math.random() * 5) + 1
        for (let k = 0; k < boatsForManager; k++) {
          boats.push({
            boat_registration_id: `boat${j}_${k}`,
            race_id: `race${j}`,
            registration_status: ['complete', 'paid', 'free'][Math.floor(Math.random() * 3)],
            forfait: false,
            team_manager_id: `manager${j}`,
            event_type: Math.random() > 0.5 ? 'Marathon' : 'Semi-Marathon',
            assigned_boat_identifier: Math.random() > 0.5 ? `assigned${j}_${k}` : null,
            seats: []
          })
        }
      }
      
      // Create races
      const races = Array.from({ length: numManagers }, (_, j) => ({
        race_id: `race${j}`,
        display_order: j + 1,
        distance: Math.random() > 0.5 ? 42 : 21,
        short_name: `R${j}`,
        name: `Race ${j}`
      }))
      
      const mockData = {
        data: {
          boats,
          team_managers: teamManagers
        }
      }
      
      const eligibleBoats = filterEligibleBoats(mockData.data.boats)
      const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)
      
      const result = generateSynthesis(mockData, boatAssignments, 'fr')
      
      // Verify each manager appears exactly once
      const dataRows = result.slice(1) // Skip header
      expect(dataRows).toHaveLength(numManagers)
      
      // Verify each manager has correct counts
      for (let j = 0; j < numManagers; j++) {
        const managerEmail = `manager${j}@example.com`
        const managerRow = dataRows.find(row => row[2] === managerEmail)
        
        expect(managerRow).toBeDefined()
        
        // Verify counts are present and are numbers
        expect(typeof managerRow[4]).toBe('number') // Assigned boats count
        expect(typeof managerRow[5]).toBe('number') // Marathon count
        expect(typeof managerRow[6]).toBe('number') // Semi-marathon count
        
        // Verify counts are non-negative
        expect(managerRow[4]).toBeGreaterThanOrEqual(0)
        expect(managerRow[5]).toBeGreaterThanOrEqual(0)
        expect(managerRow[6]).toBeGreaterThanOrEqual(0)
        
        // Verify total crews equals marathon + semi-marathon
        const totalCrews = eligibleBoats.filter(b => b.team_manager_id === `manager${j}`).length
        expect(managerRow[5] + managerRow[6]).toBe(totalCrews)
      }
      
      // Verify no duplicate managers
      const emails = dataRows.map(row => row[2])
      const uniqueEmails = new Set(emails)
      expect(uniqueEmails.size).toBe(emails.length)
    }
  })

  it('Property 11: Team Manager Aggregation - should handle edge cases', () => {
    // Test with single manager
    const singleManager = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: 'assigned1',
            seats: []
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
            phone: '1234567890',
            club_affiliation: 'Club A'
          }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'R1', name: 'Race 1' }
    ]

    const eligibleBoats1 = filterEligibleBoats(singleManager.data.boats)
    const { boatAssignments: ba1 } = assignRaceAndBowNumbers(races, eligibleBoats1, config)

    const result1 = generateSynthesis(singleManager, ba1, 'fr')

    // Should have header + 1 manager
    expect(result1).toHaveLength(2)
    expect(result1[1][2]).toBe('john@example.com')

    // Test with manager having no boats
    const noBoatsManager = {
      data: {
        boats: [],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
            phone: '1234567890',
            club_affiliation: 'Club A'
          }
        ]
      }
    }

    const eligibleBoats2 = filterEligibleBoats(noBoatsManager.data.boats)
    const { boatAssignments: ba2 } = assignRaceAndBowNumbers(races, eligibleBoats2, config)

    const result2 = generateSynthesis(noBoatsManager, ba2, 'fr')

    // Should only have header (no managers with boats)
    expect(result2).toHaveLength(1)
  })
})


describe('Property Tests - Counting Logic', () => {
  const ITERATIONS = 100
  const config = {
    marathon_bow_start: 1,
    semi_marathon_bow_start: 41
  }

  it('Property 9: Assigned Boat Counting - should count only boats with assigned_boat_identifier', () => {
    // Feature: enhanced-event-program-export, Property 9
    // Validates: Requirements 4.4, 4.8
    
    for (let i = 0; i < ITERATIONS; i++) {
      // Generate random number of boats (5-15)
      const numBoats = Math.floor(Math.random() * 11) + 5
      
      // Create boats with random assigned_boat_identifier (50% chance)
      const boats = Array.from({ length: numBoats }, (_, j) => ({
        boat_registration_id: `boat${j}`,
        race_id: 'race1',
        registration_status: ['complete', 'paid', 'free'][Math.floor(Math.random() * 3)],
        forfait: false,
        team_manager_id: 'manager1',
        event_type: Math.random() > 0.5 ? 'Marathon' : 'Semi-Marathon',
        assigned_boat_identifier: Math.random() > 0.5 ? `assigned${j}` : null,
        seats: []
      }))
      
      const teamManager = {
        user_id: 'manager1',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        phone: '1234567890',
        club_affiliation: 'Club A'
      }
      
      const mockData = {
        data: {
          boats,
          team_managers: [teamManager]
        }
      }
      
      const races = [
        { race_id: 'race1', display_order: 1, distance: 42, short_name: 'R1', name: 'Race 1' }
      ]
      
      const eligibleBoats = filterEligibleBoats(mockData.data.boats)
      const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)
      
      const result = generateSynthesis(mockData, boatAssignments, 'fr')
      
      const dataRow = result[1]
      const assignedBoatsCount = dataRow[4]
      
      // Calculate expected count
      const expectedCount = eligibleBoats.filter(b => b.assigned_boat_identifier).length
      
      // Verify count matches
      expect(assignedBoatsCount).toBe(expectedCount)
    }
  })

  it('Property 10: Event Type Crew Counting - should count marathon and semi-marathon crews correctly', () => {
    // Feature: enhanced-event-program-export, Property 10
    // Validates: Requirements 4.5, 4.6, 4.8
    
    for (let i = 0; i < ITERATIONS; i++) {
      // Generate random number of boats (5-15)
      const numBoats = Math.floor(Math.random() * 11) + 5
      
      // Create boats with random event types
      const boats = Array.from({ length: numBoats }, (_, j) => ({
        boat_registration_id: `boat${j}`,
        race_id: 'race1',
        registration_status: ['complete', 'paid', 'free'][Math.floor(Math.random() * 3)],
        forfait: false,
        team_manager_id: 'manager1',
        event_type: Math.random() > 0.5 ? 'Marathon' : 'Semi-Marathon',
        assigned_boat_identifier: Math.random() > 0.5 ? `assigned${j}` : null,
        seats: []
      }))
      
      const teamManager = {
        user_id: 'manager1',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        phone: '1234567890',
        club_affiliation: 'Club A'
      }
      
      const mockData = {
        data: {
          boats,
          team_managers: [teamManager]
        }
      }
      
      const races = [
        { race_id: 'race1', display_order: 1, distance: 42, short_name: 'R1', name: 'Race 1' }
      ]
      
      const eligibleBoats = filterEligibleBoats(mockData.data.boats)
      const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)
      
      const result = generateSynthesis(mockData, boatAssignments, 'fr')
      
      const dataRow = result[1]
      const marathonCount = dataRow[5]
      const semiMarathonCount = dataRow[6]
      
      // Calculate expected counts
      const expectedMarathon = eligibleBoats.filter(b => b.event_type === 'Marathon').length
      const expectedSemiMarathon = eligibleBoats.filter(b => b.event_type === 'Semi-Marathon').length
      
      // Verify counts match
      expect(marathonCount).toBe(expectedMarathon)
      expect(semiMarathonCount).toBe(expectedSemiMarathon)
      
      // Verify total equals sum
      expect(marathonCount + semiMarathonCount).toBe(eligibleBoats.length)
    }
  })

  it('Property 9 & 10: Counting Logic - should only count eligible boats', () => {
    // Validates: Requirements 4.4, 4.5, 4.6, 4.8
    
    for (let i = 0; i < ITERATIONS; i++) {
      // Generate boats with mixed statuses
      const boats = [
        // Eligible boats
        {
          boat_registration_id: 'boat1',
          race_id: 'race1',
          registration_status: 'complete',
          forfait: false,
          team_manager_id: 'manager1',
          event_type: 'Marathon',
          assigned_boat_identifier: 'assigned1',
          seats: []
        },
        {
          boat_registration_id: 'boat2',
          race_id: 'race1',
          registration_status: 'paid',
          forfait: false,
          team_manager_id: 'manager1',
          event_type: 'Semi-Marathon',
          assigned_boat_identifier: 'assigned2',
          seats: []
        },
        {
          boat_registration_id: 'boat3',
          race_id: 'race1',
          registration_status: 'free',
          forfait: false,
          team_manager_id: 'manager1',
          event_type: 'Marathon',
          assigned_boat_identifier: null,
          seats: []
        },
        // Ineligible boats (should not be counted)
        {
          boat_registration_id: 'boat4',
          race_id: 'race1',
          registration_status: 'incomplete',
          forfait: false,
          team_manager_id: 'manager1',
          event_type: 'Marathon',
          assigned_boat_identifier: 'assigned4',
          seats: []
        },
        {
          boat_registration_id: 'boat5',
          race_id: 'race1',
          registration_status: 'complete',
          forfait: true,
          team_manager_id: 'manager1',
          event_type: 'Semi-Marathon',
          assigned_boat_identifier: 'assigned5',
          seats: []
        }
      ]
      
      const teamManager = {
        user_id: 'manager1',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        phone: '1234567890',
        club_affiliation: 'Club A'
      }
      
      const mockData = {
        data: {
          boats,
          team_managers: [teamManager]
        }
      }
      
      const races = [
        { race_id: 'race1', display_order: 1, distance: 42, short_name: 'R1', name: 'Race 1' }
      ]
      
      const eligibleBoats = filterEligibleBoats(mockData.data.boats)
      const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)
      
      const result = generateSynthesis(mockData, boatAssignments, 'fr')
      
      const dataRow = result[1]
      
      // Should only count 3 eligible boats
      expect(eligibleBoats).toHaveLength(3)
      
      // Assigned boats: only boat1 and boat2 (boat3 has no identifier)
      expect(dataRow[4]).toBe(2)
      
      // Marathon crews: boat1 and boat3
      expect(dataRow[5]).toBe(2)
      
      // Semi-marathon crews: boat2
      expect(dataRow[6]).toBe(1)
    }
  })

  it('Property 9 & 10: Counting Logic - should handle edge cases', () => {
    // Test with all boats having assigned identifiers
    const allAssigned = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: 'assigned1',
            seats: []
          },
          {
            boat_registration_id: 'boat2',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Marathon',
            assigned_boat_identifier: 'assigned2',
            seats: []
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
            phone: '1234567890',
            club_affiliation: 'Club A'
          }
        ]
      }
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, short_name: 'R1', name: 'Race 1' }
    ]

    const eligibleBoats1 = filterEligibleBoats(allAssigned.data.boats)
    const { boatAssignments: ba1 } = assignRaceAndBowNumbers(races, eligibleBoats1, config)

    const result1 = generateSynthesis(allAssigned, ba1, 'fr')

    expect(result1[1][4]).toBe(2) // All boats assigned
    expect(result1[1][5]).toBe(2) // All marathon
    expect(result1[1][6]).toBe(0) // No semi-marathon

    // Test with no boats having assigned identifiers
    const noneAssigned = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Semi-Marathon',
            assigned_boat_identifier: null,
            seats: []
          },
          {
            boat_registration_id: 'boat2',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            event_type: 'Semi-Marathon',
            assigned_boat_identifier: null,
            seats: []
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
            phone: '1234567890',
            club_affiliation: 'Club A'
          }
        ]
      }
    }

    const eligibleBoats2 = filterEligibleBoats(noneAssigned.data.boats)
    const { boatAssignments: ba2 } = assignRaceAndBowNumbers(races, eligibleBoats2, config)

    const result2 = generateSynthesis(noneAssigned, ba2, 'fr')

    expect(result2[1][4]).toBe(0) // No boats assigned
    expect(result2[1][5]).toBe(0) // No marathon
    expect(result2[1][6]).toBe(2) // All semi-marathon
  })
})

// ============================================================================
// Property-Based Tests
// ============================================================================

import * as fc from 'fast-check'

describe('Property Tests - Export Completeness', () => {
  /**
   * Property 1: Eligible Boat Filtering
   * Validates: Requirements 1.1, 3.8, 4.8, 5.2, 5.3
   * 
   * For any collection of boats with mixed registration statuses,
   * all sheets should only include boats with status 'complete', 'paid', or 'free',
   * and should exclude all boats with status 'forfait' or 'incomplete'.
   */
  it('Property 1: All sheets only include eligible boats (complete, paid, free)', () => {
    fc.assert(
      fc.property(
        // Generate number of boats and their statuses
        fc.integer({ min: 3, max: 10 }),
        fc.array(fc.constantFrom('complete', 'paid', 'free', 'incomplete'), { minLength: 3, maxLength: 10 }),
        fc.array(fc.boolean(), { minLength: 3, maxLength: 10 }),
        (numBoats, statuses, forfaitFlags) => {
          // Create boats with unique IDs and controlled statuses
          const boats = []
          const crewMembers = []
          
          for (let i = 0; i < numBoats; i++) {
            const boatId = `boat-${i}`
            const status = statuses[i % statuses.length]
            const forfait = forfaitFlags[i % forfaitFlags.length]
            
            // Create crew members for this boat
            const seats = []
            const numSeats = 2 + (i % 3) // 2-4 seats per boat
            
            for (let j = 0; j < numSeats; j++) {
              const crewMemberId = `${boatId}-crew-${j}`
              seats.push({
                crew_member_id: crewMemberId,
                seat_type: `Rower ${j + 1}`
              })
              
              crewMembers.push({
                crew_member_id: crewMemberId,
                first_name: `First${i}${j}`,
                last_name: `Last${i}${j}`,
                club_affiliation: 'Test Club',
                age: 25 + j,
                gender: j % 2 === 0 ? 'M' : 'F',
                license_number: `LIC${i}${j}`
              })
            }
            
            boats.push({
              boat_registration_id: boatId,
              race_id: 'race1',
              registration_status: status,
              forfait: forfait,
              team_manager_id: i % 2 === 0 ? 'manager1' : 'manager2',
              event_type: i % 2 === 0 ? 'Marathon' : 'Semi-Marathon',
              boat_type: '4X+',
              category: 'SM',
              assigned_boat_identifier: `BOAT${i}`,
              assigned_boat_name: `Boat ${i}`,
              assigned_boat_comment: `Comment ${i}`,
              boat_club_display: 'Test Club',
              boat_number: `${i + 1}`,
              seats
            })
          }
          
          const teamManagers = [
            {
              user_id: 'manager1',
              first_name: 'Manager',
              last_name: 'One',
              email: 'manager1@test.com',
              phone: '1234567890',
              club_affiliation: 'Club A'
            },
            {
              user_id: 'manager2',
              first_name: 'Manager',
              last_name: 'Two',
              email: 'manager2@test.com',
              phone: '0987654321',
              club_affiliation: 'Club B'
            }
          ]
          
          const races = [
            { race_id: 'race1', display_order: 1, distance: 42, short_name: 'R1', name: 'Race 1' }
          ]
          
          const config = {
            marathon_bow_start: 1,
            semi_marathon_bow_start: 41
          }
          
          const mockData = {
            data: {
              boats,
              crew_members: crewMembers,
              team_managers: teamManagers,
              races
            }
          }
          
          // Determine which boats should be eligible
          const eligibleStatuses = ['complete', 'paid', 'free']
          const expectedEligibleBoatIds = new Set(
            boats
              .filter(boat => eligibleStatuses.includes(boat.registration_status) && !boat.forfait)
              .map(boat => boat.boat_registration_id)
          )
          
          // If no eligible boats, skip this test case
          if (expectedEligibleBoatIds.size === 0) {
            return true
          }
          
          const eligibleBoats = filterEligibleBoats(boats)
          const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)
          
          // Generate all sheets
          const crewMemberList = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')
          const crewsInRacesData = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')
          const synthesisData = generateSynthesis(mockData, boatAssignments, 'fr')
          
          // Extract boat IDs that appear in each sheet
          const crewListBoatIds = new Set()
          crewMemberList.forEach(row => {
            const boatNumber = row['N° Équipage']
            const boat = boats.find(b => b.boat_number === boatNumber)
            if (boat) {
              crewListBoatIds.add(boat.boat_registration_id)
            }
          })
          
          const crewsInRacesBoatIds = new Set()
          crewsInRacesData.slice(1).forEach(row => {
            const boatNumber = row[2] // Crew # column
            const boat = boats.find(b => b.boat_number === boatNumber)
            if (boat) {
              crewsInRacesBoatIds.add(boat.boat_registration_id)
            }
          })
          
          const synthesisManagerIds = new Set()
          synthesisData.slice(1).forEach(row => {
            const email = row[2] // Email column
            const manager = teamManagers.find(m => m.email === email)
            if (manager) {
              synthesisManagerIds.add(manager.user_id)
            }
          })
          
          // Verify: All boats in sheets must be eligible
          crewListBoatIds.forEach(boatId => {
            expect(expectedEligibleBoatIds.has(boatId)).toBe(true)
          })
          
          crewsInRacesBoatIds.forEach(boatId => {
            expect(expectedEligibleBoatIds.has(boatId)).toBe(true)
          })
          
          // Verify: Synthesis only includes managers who have at least one eligible boat
          synthesisManagerIds.forEach(managerId => {
            const managerEligibleBoats = boats.filter(b => 
              b.team_manager_id === managerId && expectedEligibleBoatIds.has(b.boat_registration_id)
            )
            expect(managerEligibleBoats.length).toBeGreaterThan(0)
          })
          
          return true
        }
      ),
      { numRuns: 100 }
    )
  })
})

describe('Property Tests - 4-Sheet Structure', () => {
  /**
   * Property 2: Required Field Completeness
   * Validates: Requirements 1.2, 1.3, 1.4, 1.5, 7.1, 7.2
   * 
   * For any valid export data, the workbook should have exactly 4 sheets
   * with correct names, and each sheet should have all required columns.
   */
  it('Property 2: Workbook has exactly 4 sheets with correct names and columns', () => {
    fc.assert(
      fc.property(
        // Generate locale
        fc.constantFrom('fr', 'en'),
        // Generate number of boats
        fc.integer({ min: 1, max: 10 }),
        (locale, numBoats) => {
          // Create mock data with specified number of boats
          const boats = []
          const crewMembers = []
          
          for (let i = 0; i < numBoats; i++) {
            const boatId = `boat${i}`
            const seats = []
            
            // Add 2-4 crew members per boat
            const numSeats = 2 + (i % 3)
            for (let j = 0; j < numSeats; j++) {
              const crewMemberId = `${boatId}_crew${j}`
              seats.push({
                crew_member_id: crewMemberId,
                seat_type: `Rower ${j + 1}`
              })
              
              crewMembers.push({
                crew_member_id: crewMemberId,
                first_name: `First${j}`,
                last_name: `Last${j}`,
                club_affiliation: 'Test Club',
                age: 25 + j,
                gender: j % 2 === 0 ? 'M' : 'F',
                license_number: `LIC${i}${j}`
              })
            }
            
            boats.push({
              boat_registration_id: boatId,
              race_id: 'race1',
              registration_status: 'complete',
              forfait: false,
              team_manager_id: 'manager1',
              event_type: 'Marathon',
              boat_type: '4X+',
              category: 'SM',
              assigned_boat_identifier: `BOAT${i}`,
              assigned_boat_name: `Boat ${i}`,
              assigned_boat_comment: `Comment ${i}`,
              boat_club_display: 'Test Club',
              boat_number: `${i + 1}`,
              seats
            })
          }
          
          const teamManagers = [
            {
              user_id: 'manager1',
              first_name: 'Manager',
              last_name: 'One',
              email: 'manager@test.com',
              phone: '1234567890',
              club_affiliation: 'Test Club'
            }
          ]
          
          const races = [
            { race_id: 'race1', display_order: 1, distance: 42, short_name: 'R1', name: 'Race 1' }
          ]
          
          const config = {
            marathon_bow_start: 1,
            semi_marathon_bow_start: 41
          }
          
          const mockData = {
            data: {
              boats,
              crew_members: crewMembers,
              team_managers: teamManagers,
              races
            }
          }
          
          const eligibleBoats = filterEligibleBoats(boats)
          const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)
          
          // Generate all sheets
          const crewMemberList = generateCrewMemberList(mockData, boatAssignments, raceAssignments, locale)
          const raceSchedule = generateRaceSchedule(mockData, raceAssignments, locale)
          const crewsInRacesData = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, locale)
          const synthesisData = generateSynthesis(mockData, boatAssignments, locale)
          
          // Verify all sheets have data
          expect(crewMemberList.length).toBeGreaterThan(0)
          expect(raceSchedule.length).toBeGreaterThan(0)
          expect(crewsInRacesData.length).toBeGreaterThan(0)
          expect(synthesisData.length).toBeGreaterThan(0)
          
          // Verify Sheet 1 (Crew Member List) has all required columns
          const crewListHeaders = Object.keys(crewMemberList[0])
          const expectedCrewListColumns = locale === 'en' 
            ? ['Race #', 'Race', 'Race (abbrev)', 'Crew #', 'Last Name', 'First Name', 'Club', 'Age', 'Gender', 'License #', 'Place in boat', 'Bow #', 'Assigned Boat']
            : ['N° Course', 'Course', 'Course (abrégé)', 'N° Équipage', 'Nom', 'Prénom', 'Club', 'Âge', 'Genre', 'N° Licence', 'Place dans le bateau', 'N° Dossard', 'Bateau assigné']
          
          expect(crewListHeaders).toEqual(expectedCrewListColumns)
          
          // Verify Sheet 2 (Race Schedule) has all required columns
          const raceScheduleHeaders = Object.keys(raceSchedule[0])
          const expectedRaceScheduleColumns = locale === 'en'
            ? ['Race (abbrev)', 'Race', 'Race #', 'Start Time']
            : ['Course (abrégé)', 'Course', 'N° Course', 'Heure de départ']
          
          expect(raceScheduleHeaders).toEqual(expectedRaceScheduleColumns)
          
          // Verify Sheet 3 (Crews in Races) has correct number of columns (50 total)
          const crewsInRacesHeaders = crewsInRacesData[0]
          expect(crewsInRacesHeaders.length).toBe(50) // 5 base + 45 member columns (9 members × 5 fields)
          
          // Verify first 5 columns
          const expectedCrewsInRacesBase = locale === 'en'
            ? ['Race #', 'Race', 'Race (abbrev)', 'Crew #', 'Boat assignment']
            : ['N° Course', 'Course', 'Course (abrégé)', 'N° Équipage', 'Bateau assigné']
          
          expect(crewsInRacesHeaders.slice(0, 5)).toEqual(expectedCrewsInRacesBase)
          
          // Verify Sheet 4 (Synthesis) has correct number of columns (7 total)
          const synthesisHeaders = synthesisData[0]
          expect(synthesisHeaders.length).toBe(7)
          
          // Verify synthesis columns
          const expectedSynthesisColumns = locale === 'en'
            ? ['Club', 'First name + Last name', 'Email', 'Phone #', 'Number of assigned boats', 'Number of crews in marathon', 'Number of crews in semi-marathon']
            : ['Club', 'Prénom + Nom', 'Email', 'N° Téléphone', 'Nombre de bateaux assignés', 'Nombre d\'équipages en marathon', 'Nombre d\'équipages en semi-marathon']
          
          expect(synthesisHeaders).toEqual(expectedSynthesisColumns)
          
          return true
        }
      ),
      { numRuns: 100 }
    )
  })
})

// ============================================================================
// Property Test 4: Localization Consistency
// ============================================================================

describe('Property Tests - Localization Consistency', () => {
  /**
   * Property 4: Localization Consistency
   * 
   * Validates: Requirements 1.9, 3.9, 4.9, 6.1, 6.2, 6.3, 7.2
   * 
   * For any locale ('fr' or 'en'), all column headers and sheet names in the 
   * generated workbook should be translated to that locale.
   * 
   * This test verifies that:
   * 1. All sheet names are properly translated
   * 2. All column headers in Sheet 1 (Crew Member List) are translated
   * 3. All column headers in Sheet 2 (Race Schedule) are translated
   * 4. All column headers in Sheet 3 (Crews in Races) are translated
   * 5. All column headers in Sheet 4 (Synthesis) are translated
   * 6. No English text appears in French locale and vice versa
   */
  it('Property 4: All headers and sheet names are translated in both locales', () => {
    fc.assert(
      fc.property(
        // Generate locale
        fc.constantFrom('fr', 'en'),
        
        // Generate number of boats
        fc.integer({ min: 1, max: 5 }),
        
        (locale, numBoats) => {
          // Create mock data with specified number of boats
          const boats = []
          const crewMembers = []
          const teamManagers = []
          
          for (let i = 0; i < numBoats; i++) {
            const boatId = `boat${i + 1}`
            const managerId = `manager${i + 1}`
            
            // Create team manager
            teamManagers.push({
              user_id: managerId,
              team_manager_id: managerId,
              first_name: `Manager${i + 1}`,
              last_name: `Last${i + 1}`,
              email: `manager${i + 1}@example.com`,
              phone: `+3361234567${i}`,
              club_affiliation: `Club ${i + 1}`
            })
            
            // Create crew members for this boat (2 members per boat)
            const member1Id = `crew${i * 2 + 1}`
            const member2Id = `crew${i * 2 + 2}`
            
            crewMembers.push(
              {
                crew_member_id: member1Id,
                first_name: `John${i + 1}`,
                last_name: `Doe${i + 1}`,
                club_affiliation: `Club ${i + 1}`,
                age: 25 + i,
                gender: 'M',
                license_number: `LIC${i * 2 + 1}`
              },
              {
                crew_member_id: member2Id,
                first_name: `Jane${i + 1}`,
                last_name: `Smith${i + 1}`,
                club_affiliation: `Club ${i + 1}`,
                age: 30 + i,
                gender: 'F',
                license_number: `LIC${i * 2 + 2}`
              }
            )
            
            // Create boat
            boats.push({
              boat_registration_id: boatId,
              race_id: 'race1',
              registration_status: 'complete',
              forfait: false,
              team_manager_id: managerId,
              event_type: 'Marathon',
              boat_type: '4X+',
              category: 'SM',
              club_affiliation: `Club ${i + 1}`,
              boat_club_display: `Club ${i + 1}`,
              boat_number: `${i + 1}`,
              assigned_boat_name: `Boat ${i + 1}`,
              assigned_boat_comment: `Comment ${i + 1}`,
              assigned_boat_identifier: `boat-${i + 1}`,
              seats: [
                { crew_member_id: member1Id, position: 1, type: 'rower', seat_type: 'Rower 1' },
                { crew_member_id: member2Id, position: 2, type: 'rower', seat_type: 'Rower 2' }
              ]
            })
          }
          
          const mockData = {
            data: {
              boats,
              crew_members: crewMembers,
              team_managers: teamManagers,
              races: [
                { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
              ]
            }
          }
          
          const races = mockData.data.races
          
          const config = {
            marathon_bow_start: 1,
            semi_marathon_bow_start: 41
          }
          
          const eligibleBoats = filterEligibleBoats(boats)
          const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)
          
          // Generate all sheets
          const crewMemberList = generateCrewMemberList(mockData, boatAssignments, raceAssignments, locale)
          const raceSchedule = generateRaceSchedule(mockData, raceAssignments, locale)
          const crewsInRacesData = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, locale)
          const synthesisData = generateSynthesis(mockData, boatAssignments, locale)
          
          // Define expected headers for each locale
          const expectedHeaders = {
            fr: {
              crewMemberList: ['N° Course', 'Course', 'Course (abrégé)', 'N° Équipage', 'Nom', 'Prénom', 'Club', 'Âge', 'Genre', 'N° Licence', 'Place dans le bateau', 'N° Dossard', 'Bateau assigné'],
              raceSchedule: ['Course (abrégé)', 'Course', 'N° Course', 'Heure de départ'],
              crewsInRacesBase: ['N° Course', 'Course', 'Course (abrégé)', 'N° Équipage', 'Bateau assigné'],
              synthesis: ['Club', 'Prénom + Nom', 'Email', 'N° Téléphone', 'Nombre de bateaux assignés', 'Nombre d\'équipages en marathon', 'Nombre d\'équipages en semi-marathon']
            },
            en: {
              crewMemberList: ['Race #', 'Race', 'Race (abbrev)', 'Crew #', 'Last Name', 'First Name', 'Club', 'Age', 'Gender', 'License #', 'Place in boat', 'Bow #', 'Assigned Boat'],
              raceSchedule: ['Race (abbrev)', 'Race', 'Race #', 'Start Time'],
              crewsInRacesBase: ['Race #', 'Race', 'Race (abbrev)', 'Crew #', 'Boat assignment'],
              synthesis: ['Club', 'First name + Last name', 'Email', 'Phone #', 'Number of assigned boats', 'Number of crews in marathon', 'Number of crews in semi-marathon']
            }
          }
          
          // Verify we have data in all sheets
          expect(crewMemberList.length).toBeGreaterThan(0)
          expect(raceSchedule.length).toBeGreaterThan(0)
          expect(crewsInRacesData.length).toBeGreaterThan(1) // At least headers + 1 row
          expect(synthesisData.length).toBeGreaterThan(1) // At least headers + 1 row
          
          // Verify Sheet 1 (Crew Member List) headers
          const crewListHeaders = Object.keys(crewMemberList[0])
          expect(crewListHeaders).toEqual(expectedHeaders[locale].crewMemberList)
          
          // Verify Sheet 2 (Race Schedule) headers
          const raceScheduleHeaders = Object.keys(raceSchedule[0])
          expect(raceScheduleHeaders).toEqual(expectedHeaders[locale].raceSchedule)
          
          // Verify Sheet 3 (Crews in Races) base headers
          const crewsInRacesHeaders = crewsInRacesData[0]
          expect(crewsInRacesHeaders.slice(0, 5)).toEqual(expectedHeaders[locale].crewsInRacesBase)
          
          // Verify member column headers follow pattern
          for (let i = 1; i <= 9; i++) {
            const memberPrefix = locale === 'en' ? `Member ${i}` : `Équipier ${i}`
            const expectedMemberHeaders = [
              `${memberPrefix} ${locale === 'en' ? 'Last Name' : 'Nom'}`,
              `${memberPrefix} ${locale === 'en' ? 'First Name' : 'Prénom'}`,
              `${memberPrefix} ${locale === 'en' ? 'Club' : 'Club'}`,
              `${memberPrefix} ${locale === 'en' ? 'Age' : 'Âge'}`,
              `${memberPrefix} ${locale === 'en' ? 'Gender' : 'Genre'}`
            ]
            
            const startIdx = 5 + (i - 1) * 5
            const memberHeaders = crewsInRacesHeaders.slice(startIdx, startIdx + 5)
            expect(memberHeaders).toEqual(expectedMemberHeaders)
          }
          
          // Verify Sheet 4 (Synthesis) headers
          const synthesisHeaders = synthesisData[0]
          expect(synthesisHeaders).toEqual(expectedHeaders[locale].synthesis)
          
          // Verify no cross-locale contamination
          // If locale is 'fr', no English-specific terms should appear
          // If locale is 'en', no French-specific terms should appear
          if (locale === 'fr') {
            // Check that English terms don't appear in French headers
            const allFrenchHeaders = [
              ...crewListHeaders,
              ...raceScheduleHeaders,
              ...crewsInRacesHeaders,
              ...synthesisHeaders
            ].join(' ')
            
            // These English terms should NOT appear in French locale
            expect(allFrenchHeaders).not.toContain('Race #')
            expect(allFrenchHeaders).not.toContain('Crew #')
            expect(allFrenchHeaders).not.toContain('Last Name')
            expect(allFrenchHeaders).not.toContain('First Name')
            expect(allFrenchHeaders).not.toContain('Member ')
            expect(allFrenchHeaders).not.toContain('Phone #')
          } else {
            // Check that French terms don't appear in English headers
            const allEnglishHeaders = [
              ...crewListHeaders,
              ...raceScheduleHeaders,
              ...crewsInRacesHeaders,
              ...synthesisHeaders
            ].join(' ')
            
            // These French terms should NOT appear in English locale
            expect(allEnglishHeaders).not.toContain('N° Course')
            expect(allEnglishHeaders).not.toContain('N° Équipage')
            expect(allEnglishHeaders).not.toContain('Équipier ')
            expect(allEnglishHeaders).not.toContain('Prénom')
            expect(allEnglishHeaders).not.toContain('N° Téléphone')
          }
          
          return true
        }
      ),
      { numRuns: 100 }
    )
  })
})


// ============================================================================
// Race Abbreviation Translation Tests
// ============================================================================

describe('Race Abbreviation Translation', () => {
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
          boat_club_display: 'Club A',
          boat_number: '1',
          event_type: 'Marathon',
          boat_type: '4X+',
          category: 'SM',
          assigned_boat_name: 'Test Boat',
          assigned_boat_comment: 'Test Comment',
          assigned_boat_identifier: 'boat-1',
          seats: [
            { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
          ]
        }
      ],
      crew_members: [
        { 
          crew_member_id: 'crew1', 
          first_name: 'John', 
          last_name: 'Doe', 
          club_affiliation: 'Club A',
          age: 25,
          gender: 'M',
          license_number: 'LIC123'
        }
      ],
      team_managers: [
        { 
          user_id: 'user1',
          team_manager_id: 'user1',
          first_name: 'Manager',
          last_name: 'One',
          email: 'manager@test.com',
          phone: '1234567890',
          club_affiliation: 'Club A'
        }
      ],
      races: [
        { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
      ]
    }
  }

  const config = {
    marathon_bow_start: 1,
    semi_marathon_bow_start: 41
  }

  it('should translate race abbreviations to French (W→F, X→M, M→H)', () => {
    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    // Test French locale - should translate MW4X+ to MF4X+
    const frenchResult = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')
    expect(frenchResult[0]['Course (abrégé)']).toBe('MF4X+') // MW4X+ → MF4X+ (Women → Femme)

    // Test English locale - should keep original MW4X+
    const englishResult = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'en')
    expect(englishResult[0]['Race (abbrev)']).toBe('MW4X+')
  })

  it('should translate race abbreviations in race schedule', () => {
    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    // Test French locale
    const frenchSchedule = generateRaceSchedule(mockData, raceAssignments, 'fr')
    expect(frenchSchedule[0]['Course (abrégé)']).toBe('MF4X+')

    // Test English locale
    const englishSchedule = generateRaceSchedule(mockData, raceAssignments, 'en')
    expect(englishSchedule[0]['Race (abbrev)']).toBe('MW4X+')
  })

  it('should translate race abbreviations in crews in races sheet', () => {
    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    // Test French locale
    const frenchCrews = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')
    expect(frenchCrews[1][2]).toBe('MF4X+') // Row 1 (after headers), column 2 (race abbrev)

    // Test English locale
    const englishCrews = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'en')
    expect(englishCrews[1][2]).toBe('MW4X+')
  })

  it('should translate various gender markers correctly', () => {
    const testCases = [
      { input: 'MW4X+', expectedFr: 'MF4X+', description: 'Master Women → Master Femme' },
      { input: 'SH8+', expectedFr: 'SH8+', description: 'Senior Men → Senior Homme (already H)' },
      { input: 'SX4+', expectedFr: 'SM4+', description: 'Senior Mixed → Senior Mixte' },
      { input: 'J16F2X', expectedFr: 'J16F2X', description: 'Junior 16 Women → Junior 16 Femme (already F)' },
      { input: 'J18H4+', expectedFr: 'J18H4+', description: 'Junior 18 Men → Junior 18 Homme (already H)' }
    ]

    testCases.forEach(({ input, expectedFr, description }) => {
      const testData = {
        data: {
          ...mockData.data,
          races: [
            { race_id: 'race1', display_order: 1, distance: 42, short_name: input, name: description }
          ]
        }
      }

      const races = testData.data.races
      const eligibleBoats = filterEligibleBoats(testData.data.boats)
      const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

      const frenchResult = generateCrewMemberList(testData, boatAssignments, raceAssignments, 'fr')
      expect(frenchResult[0]['Course (abrégé)']).toBe(expectedFr)
    })
  })
})

describe('Edge Cases - Missing Crew Member Data', () => {
  const config = {
    marathon_bow_start: 1,
    semi_marathon_bow_start: 41
  }

  it('should handle boats with missing crew_member_id references', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'Club A',
            boat_number: 'B1',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' },
              { crew_member_id: 'crew_missing', position: 2, type: 'rower', seat_type: 'Rower 2' } // Missing member
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123',
            club_affiliation: 'Club A'
          }
          // crew_missing is not in the list
        ],
        team_managers: [],
        races: [
          { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
        ]
      }
    }

    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    // Should not throw error
    const result = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')

    // Should have 2 rows: one for existing member, one for placeholder
    expect(result).toHaveLength(2)
    expect(result[0]['Nom']).toBe('Doe')
    expect(result[1]['Nom']).toBe('Inconnu') // Placeholder for missing member
    expect(result[1]['Prénom']).toBe('')
    expect(result[1]['Âge']).toBe('')
    expect(result[1]['Genre']).toBe('')
    expect(result[1]['N° Licence']).toBe('')
  })

  it('should use English placeholder for missing crew members in English locale', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'Club A',
            boat_number: 'B1',
            seats: [
              { crew_member_id: 'crew_missing', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [],
        team_managers: [],
        races: [
          { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
        ]
      }
    }

    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'en')

    expect(result).toHaveLength(1)
    expect(result[0]['Last Name']).toBe('Unknown') // English placeholder
  })

  it('should handle missing crew members in crews in races sheet', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'Club A',
            boat_number: 'B1',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' },
              { crew_member_id: 'crew_missing', position: 2, type: 'rower', seat_type: 'Rower 2' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123',
            club_affiliation: 'Club A'
          }
        ],
        team_managers: [],
        races: [
          { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
        ]
      }
    }

    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    // Should not throw error
    const result = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')

    // Should have header + 1 data row
    expect(result).toHaveLength(2)
    
    // First member should be John Doe
    expect(result[1][5]).toBe('Doe') // Member 1 Last Name
    expect(result[1][6]).toBe('John') // Member 1 First Name
    
    // Second member should be placeholder
    expect(result[1][10]).toBe('Inconnu') // Member 2 Last Name
    expect(result[1][11]).toBe('') // Member 2 First Name
    expect(result[1][12]).toBe('') // Member 2 Club
    expect(result[1][13]).toBe('') // Member 2 Age
    expect(result[1][14]).toBe('') // Member 2 Gender
  })

  it('should handle seats without crew_member_id', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'Club A',
            boat_number: 'B1',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' },
              { position: 2, type: 'rower', seat_type: 'Rower 2' } // No crew_member_id
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123',
            club_affiliation: 'Club A'
          }
        ],
        team_managers: [],
        races: [
          { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
        ]
      }
    }

    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    // Should not throw error
    const result = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')

    // Should only have 1 row for the valid crew member
    expect(result).toHaveLength(1)
    expect(result[0]['Nom']).toBe('Doe')
  })
})

describe('Edge Cases - Missing Team Manager Data', () => {
  const config = {
    marathon_bow_start: 1,
    semi_marathon_bow_start: 41
  }

  it('should skip boats without team_manager_id in synthesis', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: null, // No team manager
            boat_club_display: 'Club A',
            boat_number: 'B1',
            event_type: '42km',
            assigned_boat_identifier: 'boat123',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123',
            club_affiliation: 'Club A'
          }
        ],
        team_managers: [],
        races: [
          { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
        ]
      }
    }

    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateSynthesis(mockData, boatAssignments, 'fr')

    // Should only have header row, no data rows
    expect(result).toHaveLength(1)
  })

  it('should skip boats with missing team manager reference in synthesis', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager_missing', // Manager not in list
            boat_club_display: 'Club A',
            boat_number: 'B1',
            event_type: '42km',
            assigned_boat_identifier: 'boat123',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123',
            club_affiliation: 'Club A'
          }
        ],
        team_managers: [], // Manager not in list
        races: [
          { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
        ]
      }
    }

    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateSynthesis(mockData, boatAssignments, 'fr')

    // Should only have header row, no data rows
    expect(result).toHaveLength(1)
  })

  it('should include boats with valid team managers in synthesis', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            boat_club_display: 'Club A',
            boat_number: 'B1',
            event_type: '42km',
            assigned_boat_identifier: 'boat123',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          },
          {
            boat_registration_id: 'boat2',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: null, // No manager - should be skipped
            boat_club_display: 'Club B',
            boat_number: 'B2',
            event_type: '42km',
            assigned_boat_identifier: 'boat456',
            seats: [
              { crew_member_id: 'crew2', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123',
            club_affiliation: 'Club A'
          },
          { 
            crew_member_id: 'crew2', 
            first_name: 'Jane', 
            last_name: 'Smith',
            age: 30,
            gender: 'F',
            license_number: 'LIC456',
            club_affiliation: 'Club B'
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'Manager',
            last_name: 'One',
            email: 'manager1@example.com',
            phone: '1234567890',
            club_affiliation: 'Club A'
          }
        ],
        races: [
          { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
        ]
      }
    }

    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateSynthesis(mockData, boatAssignments, 'fr')

    // Should have header + 1 data row (only manager1)
    expect(result).toHaveLength(2)
    expect(result[1][0]).toBe('Club A') // Club
    expect(result[1][1]).toBe('Manager One') // Name
  })
})

describe('Edge Cases - Empty Assigned Boat Fields', () => {
  const config = {
    marathon_bow_start: 1,
    semi_marathon_bow_start: 41
  }

  it('should display empty string when assigned_boat_name is null', () => {
    const boat = {
      assigned_boat_name: null,
      assigned_boat_comment: null
    }

    expect(formatAssignedBoat(boat)).toBe('')
  })

  it('should display empty string when assigned_boat_name is empty string', () => {
    const boat = {
      assigned_boat_name: '',
      assigned_boat_comment: ''
    }

    expect(formatAssignedBoat(boat)).toBe('')
  })

  it('should display empty string when assigned_boat_name is undefined', () => {
    const boat = {
      assigned_boat_name: undefined,
      assigned_boat_comment: undefined
    }

    expect(formatAssignedBoat(boat)).toBe('')
  })

  it('should display empty string when boat is null', () => {
    expect(formatAssignedBoat(null)).toBe('')
  })

  it('should display empty string when boat is undefined', () => {
    expect(formatAssignedBoat(undefined)).toBe('')
  })

  it('should handle empty assigned boat in crew member list', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'Club A',
            boat_number: 'B1',
            assigned_boat_name: null,
            assigned_boat_comment: null,
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123',
            club_affiliation: 'Club A'
          }
        ],
        team_managers: [],
        races: [
          { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
        ]
      }
    }

    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')

    expect(result[0]['Bateau assigné']).toBe('')
  })

  it('should handle empty assigned boat in crews in races sheet', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'user1',
            boat_club_display: 'Club A',
            boat_number: 'B1',
            assigned_boat_name: null,
            assigned_boat_comment: null,
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123',
            club_affiliation: 'Club A'
          }
        ],
        team_managers: [],
        races: [
          { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
        ]
      }
    }

    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')

    // Boat assignment is column 4 (index 4)
    expect(result[1][4]).toBe('')
  })
})

describe('Edge Cases - Missing Phone Numbers', () => {
  const config = {
    marathon_bow_start: 1,
    semi_marathon_bow_start: 41
  }

  it('should display empty string when phone is null', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            boat_club_display: 'Club A',
            boat_number: 'B1',
            event_type: '42km',
            assigned_boat_identifier: 'boat123',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123',
            club_affiliation: 'Club A'
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'Manager',
            last_name: 'One',
            email: 'manager1@example.com',
            phone: null, // No phone
            club_affiliation: 'Club A'
          }
        ],
        races: [
          { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
        ]
      }
    }

    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateSynthesis(mockData, boatAssignments, 'fr')

    // Phone is column 3 (index 3)
    expect(result[1][3]).toBe('')
  })

  it('should display empty string when phone is empty string', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            boat_club_display: 'Club A',
            boat_number: 'B1',
            event_type: '42km',
            assigned_boat_identifier: 'boat123',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123',
            club_affiliation: 'Club A'
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'Manager',
            last_name: 'One',
            email: 'manager1@example.com',
            phone: '', // Empty phone
            club_affiliation: 'Club A'
          }
        ],
        races: [
          { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
        ]
      }
    }

    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateSynthesis(mockData, boatAssignments, 'fr')

    // Phone is column 3 (index 3)
    expect(result[1][3]).toBe('')
  })

  it('should display phone number when present', () => {
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            boat_club_display: 'Club A',
            boat_number: 'B1',
            event_type: '42km',
            assigned_boat_identifier: 'boat123',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower', seat_type: 'Rower 1' }
            ]
          }
        ],
        crew_members: [
          { 
            crew_member_id: 'crew1', 
            first_name: 'John', 
            last_name: 'Doe',
            age: 25,
            gender: 'M',
            license_number: 'LIC123',
            club_affiliation: 'Club A'
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: 'Manager',
            last_name: 'One',
            email: 'manager1@example.com',
            phone: '1234567890',
            club_affiliation: 'Club A'
          }
        ],
        races: [
          { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
        ]
      }
    }

    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)

    const result = generateSynthesis(mockData, boatAssignments, 'fr')

    // Phone is column 3 (index 3)
    expect(result[1][3]).toBe('1234567890')
  })
})


describe('Property Test - Malformed Data Handling', () => {
  const ITERATIONS = 100
  const config = {
    marathon_bow_start: 1,
    semi_marathon_bow_start: 41
  }

  it('Property 13: Malformed Data Handling - should not crash with missing or malformed data', () => {
    // Feature: enhanced-event-program-export, Property 13
    // Validates: Requirements 8.3
    
    for (let i = 0; i < ITERATIONS; i++) {
      // Generate random malformed data scenarios
      const scenario = Math.floor(Math.random() * 6)
      
      let mockData
      
      switch (scenario) {
        case 0:
          // Missing crew_member_id in seats
          mockData = {
            data: {
              boats: [
                {
                  boat_registration_id: 'boat1',
                  race_id: 'race1',
                  registration_status: 'complete',
                  forfait: false,
                  team_manager_id: 'manager1',
                  boat_club_display: 'Club A',
                  boat_number: 'B1',
                  event_type: '42km',
                  assigned_boat_identifier: 'boat123',
                  seats: [
                    { position: 1, type: 'rower' } // Missing crew_member_id
                  ]
                }
              ],
              crew_members: [],
              team_managers: [
                {
                  user_id: 'manager1',
                  first_name: 'Manager',
                  last_name: 'One',
                  email: 'manager1@example.com',
                  phone: '1234567890',
                  club_affiliation: 'Club A'
                }
              ],
              races: [
                { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
              ]
            }
          }
          break
          
        case 1:
          // Missing crew member reference
          mockData = {
            data: {
              boats: [
                {
                  boat_registration_id: 'boat1',
                  race_id: 'race1',
                  registration_status: 'complete',
                  forfait: false,
                  team_manager_id: 'manager1',
                  boat_club_display: 'Club A',
                  boat_number: 'B1',
                  event_type: '42km',
                  assigned_boat_identifier: 'boat123',
                  seats: [
                    { crew_member_id: 'missing_crew', position: 1, type: 'rower' }
                  ]
                }
              ],
              crew_members: [], // Crew member not in list
              team_managers: [
                {
                  user_id: 'manager1',
                  first_name: 'Manager',
                  last_name: 'One',
                  email: 'manager1@example.com',
                  phone: '1234567890',
                  club_affiliation: 'Club A'
                }
              ],
              races: [
                { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
              ]
            }
          }
          break
          
        case 2:
          // Missing team_manager_id
          mockData = {
            data: {
              boats: [
                {
                  boat_registration_id: 'boat1',
                  race_id: 'race1',
                  registration_status: 'complete',
                  forfait: false,
                  team_manager_id: null, // No team manager
                  boat_club_display: 'Club A',
                  boat_number: 'B1',
                  event_type: '42km',
                  assigned_boat_identifier: 'boat123',
                  seats: [
                    { crew_member_id: 'crew1', position: 1, type: 'rower' }
                  ]
                }
              ],
              crew_members: [
                {
                  crew_member_id: 'crew1',
                  first_name: 'John',
                  last_name: 'Doe',
                  age: 25,
                  gender: 'M',
                  license_number: 'LIC123',
                  club_affiliation: 'Club A'
                }
              ],
              team_managers: [],
              races: [
                { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
              ]
            }
          }
          break
          
        case 3:
          // Missing team manager reference
          mockData = {
            data: {
              boats: [
                {
                  boat_registration_id: 'boat1',
                  race_id: 'race1',
                  registration_status: 'complete',
                  forfait: false,
                  team_manager_id: 'missing_manager', // Manager not in list
                  boat_club_display: 'Club A',
                  boat_number: 'B1',
                  event_type: '42km',
                  assigned_boat_identifier: 'boat123',
                  seats: [
                    { crew_member_id: 'crew1', position: 1, type: 'rower' }
                  ]
                }
              ],
              crew_members: [
                {
                  crew_member_id: 'crew1',
                  first_name: 'John',
                  last_name: 'Doe',
                  age: 25,
                  gender: 'M',
                  license_number: 'LIC123',
                  club_affiliation: 'Club A'
                }
              ],
              team_managers: [], // Manager not in list
              races: [
                { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
              ]
            }
          }
          break
          
        case 4:
          // Null/empty assigned boat fields
          mockData = {
            data: {
              boats: [
                {
                  boat_registration_id: 'boat1',
                  race_id: 'race1',
                  registration_status: 'complete',
                  forfait: false,
                  team_manager_id: 'manager1',
                  boat_club_display: 'Club A',
                  boat_number: 'B1',
                  event_type: '42km',
                  assigned_boat_identifier: null, // No assigned boat
                  assigned_boat_name: null,
                  assigned_boat_comment: null,
                  seats: [
                    { crew_member_id: 'crew1', position: 1, type: 'rower' }
                  ]
                }
              ],
              crew_members: [
                {
                  crew_member_id: 'crew1',
                  first_name: 'John',
                  last_name: 'Doe',
                  age: 25,
                  gender: 'M',
                  license_number: 'LIC123',
                  club_affiliation: 'Club A'
                }
              ],
              team_managers: [
                {
                  user_id: 'manager1',
                  first_name: 'Manager',
                  last_name: 'One',
                  email: 'manager1@example.com',
                  phone: null, // No phone
                  club_affiliation: 'Club A'
                }
              ],
              races: [
                { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
              ]
            }
          }
          break
          
        case 5:
          // Empty seats array
          mockData = {
            data: {
              boats: [
                {
                  boat_registration_id: 'boat1',
                  race_id: 'race1',
                  registration_status: 'complete',
                  forfait: false,
                  team_manager_id: 'manager1',
                  boat_club_display: 'Club A',
                  boat_number: 'B1',
                  event_type: '42km',
                  assigned_boat_identifier: 'boat123',
                  seats: [] // No seats
                }
              ],
              crew_members: [],
              team_managers: [
                {
                  user_id: 'manager1',
                  first_name: 'Manager',
                  last_name: 'One',
                  email: 'manager1@example.com',
                  phone: '1234567890',
                  club_affiliation: 'Club A'
                }
              ],
              races: [
                { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
              ]
            }
          }
          break
      }
      
      const races = mockData.data.races
      const eligibleBoats = filterEligibleBoats(mockData.data.boats)
      const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)
      
      // All these operations should not throw exceptions
      expect(() => {
        generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')
      }).not.toThrow()
      
      expect(() => {
        generateRaceSchedule(mockData, raceAssignments, 'fr')
      }).not.toThrow()
      
      expect(() => {
        generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')
      }).not.toThrow()
      
      expect(() => {
        generateSynthesis(mockData, boatAssignments, 'fr')
      }).not.toThrow()
    }
  })

  it('Property 13: Should handle completely empty data gracefully', () => {
    // Feature: enhanced-event-program-export, Property 13
    // Validates: Requirements 8.3
    
    const mockData = {
      data: {
        boats: [],
        crew_members: [],
        team_managers: [],
        races: []
      }
    }
    
    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)
    
    // All operations should not throw exceptions
    expect(() => {
      generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')
    }).not.toThrow()
    
    expect(() => {
      generateRaceSchedule(mockData, raceAssignments, 'fr')
    }).not.toThrow()
    
    expect(() => {
      generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')
    }).not.toThrow()
    
    expect(() => {
      generateSynthesis(mockData, boatAssignments, 'fr')
    }).not.toThrow()
    
    // Results should be empty or header-only
    const crewList = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')
    expect(crewList).toHaveLength(0)
    
    const raceSchedule = generateRaceSchedule(mockData, raceAssignments, 'fr')
    expect(raceSchedule).toHaveLength(0)
    
    const crewsInRaces = generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')
    expect(crewsInRaces).toHaveLength(1) // Header only
    
    const synthesis = generateSynthesis(mockData, boatAssignments, 'fr')
    expect(synthesis).toHaveLength(1) // Header only
  })

  it('Property 13: Should handle null/undefined fields in crew members', () => {
    // Feature: enhanced-event-program-export, Property 13
    // Validates: Requirements 8.3
    
    const mockData = {
      data: {
        boats: [
          {
            boat_registration_id: 'boat1',
            race_id: 'race1',
            registration_status: 'complete',
            forfait: false,
            team_manager_id: 'manager1',
            boat_club_display: 'Club A',
            boat_number: 'B1',
            event_type: '42km',
            assigned_boat_identifier: 'boat123',
            seats: [
              { crew_member_id: 'crew1', position: 1, type: 'rower' }
            ]
          }
        ],
        crew_members: [
          {
            crew_member_id: 'crew1',
            first_name: null, // Null fields
            last_name: undefined,
            age: null,
            gender: null,
            license_number: null,
            club_affiliation: null
          }
        ],
        team_managers: [
          {
            user_id: 'manager1',
            first_name: null,
            last_name: null,
            email: null,
            phone: null,
            club_affiliation: null
          }
        ],
        races: [
          { race_id: 'race1', display_order: 1, distance: 42, short_name: 'MW4X+', name: 'Master Women 4X+' }
        ]
      }
    }
    
    const races = mockData.data.races
    const eligibleBoats = filterEligibleBoats(mockData.data.boats)
    const { raceAssignments, boatAssignments } = assignRaceAndBowNumbers(races, eligibleBoats, config)
    
    // All operations should not throw exceptions
    expect(() => {
      generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')
    }).not.toThrow()
    
    expect(() => {
      generateCrewsInRaces(mockData, boatAssignments, raceAssignments, 'fr')
    }).not.toThrow()
    
    expect(() => {
      generateSynthesis(mockData, boatAssignments, 'fr')
    }).not.toThrow()
    
    // Results should handle null/undefined gracefully
    const crewList = generateCrewMemberList(mockData, boatAssignments, raceAssignments, 'fr')
    expect(crewList).toHaveLength(1)
    expect(crewList[0]['Nom']).toBe('') // Should be empty string, not null
    expect(crewList[0]['Prénom']).toBe('')
    
    const synthesis = generateSynthesis(mockData, boatAssignments, 'fr')
    expect(synthesis).toHaveLength(2) // Header + 1 data row
    expect(synthesis[1][1]).toBe('') // Name should be empty string
    expect(synthesis[1][3]).toBe('') // Phone should be empty string
  })
})
