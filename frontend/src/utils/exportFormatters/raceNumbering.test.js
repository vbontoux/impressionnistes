/**
 * Tests for Race and Bow Numbering Logic
 * Ensures consistent numbering across all exports
 */

import { describe, it, expect } from 'vitest'
import { assignRaceAndBowNumbers, filterEligibleBoats } from './raceNumbering.js'

describe('filterEligibleBoats', () => {
  it('should include complete boats', () => {
    const boats = [
      { boat_registration_id: '1', registration_status: 'complete', forfait: false }
    ]
    const result = filterEligibleBoats(boats)
    expect(result).toHaveLength(1)
    expect(result[0].boat_registration_id).toBe('1')
  })

  it('should include paid boats', () => {
    const boats = [
      { boat_registration_id: '1', registration_status: 'paid', forfait: false }
    ]
    const result = filterEligibleBoats(boats)
    expect(result).toHaveLength(1)
  })

  it('should include free boats', () => {
    const boats = [
      { boat_registration_id: '1', registration_status: 'free', forfait: false }
    ]
    const result = filterEligibleBoats(boats)
    expect(result).toHaveLength(1)
  })

  it('should exclude incomplete boats', () => {
    const boats = [
      { boat_registration_id: '1', registration_status: 'incomplete', forfait: false }
    ]
    const result = filterEligibleBoats(boats)
    expect(result).toHaveLength(0)
  })

  it('should exclude forfait boats', () => {
    const boats = [
      { boat_registration_id: '1', registration_status: 'complete', forfait: true }
    ]
    const result = filterEligibleBoats(boats)
    expect(result).toHaveLength(0)
  })

  it('should filter mixed boat statuses correctly', () => {
    const boats = [
      { boat_registration_id: '1', registration_status: 'complete', forfait: false },
      { boat_registration_id: '2', registration_status: 'incomplete', forfait: false },
      { boat_registration_id: '3', registration_status: 'paid', forfait: true },
      { boat_registration_id: '4', registration_status: 'free', forfait: false }
    ]
    const result = filterEligibleBoats(boats)
    expect(result).toHaveLength(2)
    expect(result.map(b => b.boat_registration_id)).toEqual(['1', '4'])
  })
})

describe('assignRaceAndBowNumbers', () => {
  const config = {
    marathon_start_time: '07:45',
    semi_marathon_start_time: '09:00',
    semi_marathon_interval_seconds: 30,
    marathon_bow_start: 1,
    semi_marathon_bow_start: 41
  }

  it('should assign race numbers: marathons get 1, semi-marathons get 2, 3, 4...', () => {
    const races = [
      { race_id: 'race1', display_order: 2, distance: 42 }, // Marathon
      { race_id: 'race2', display_order: 1, distance: 21 }, // Semi-marathon
      { race_id: 'race3', display_order: 3, distance: 42 }  // Marathon
    ]
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1' },
      { boat_registration_id: 'boat2', race_id: 'race2' },
      { boat_registration_id: 'boat3', race_id: 'race3' }
    ]

    const { raceAssignments } = assignRaceAndBowNumbers(races, boats, config)

    // All marathon races get race number 1
    expect(raceAssignments['race1'].raceNumber).toBe(1) // Marathon
    expect(raceAssignments['race3'].raceNumber).toBe(1) // Marathon
    // Semi-marathon races get incremental numbers starting at 2
    expect(raceAssignments['race2'].raceNumber).toBe(2) // Semi-marathon
  })

  it('should assign marathon bow numbers starting from config value', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, event_type: '42km' }
    ]
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1' },
      { boat_registration_id: 'boat2', race_id: 'race1' },
      { boat_registration_id: 'boat3', race_id: 'race1' }
    ]

    const { boatAssignments } = assignRaceAndBowNumbers(races, boats, config)

    expect(boatAssignments['boat1'].bowNumber).toBe(1)
    expect(boatAssignments['boat2'].bowNumber).toBe(2)
    expect(boatAssignments['boat3'].bowNumber).toBe(3)
  })

  it('should assign semi-marathon bow numbers starting from config value', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 21, event_type: '21km' }
    ]
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1' },
      { boat_registration_id: 'boat2', race_id: 'race1' }
    ]

    const { boatAssignments } = assignRaceAndBowNumbers(races, boats, config)

    expect(boatAssignments['boat1'].bowNumber).toBe(41)
    expect(boatAssignments['boat2'].bowNumber).toBe(42)
  })

  it('should assign same start time to all marathon boats', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, event_type: '42km' }
    ]
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1' },
      { boat_registration_id: 'boat2', race_id: 'race1' }
    ]

    const { boatAssignments } = assignRaceAndBowNumbers(races, boats, config)

    expect(boatAssignments['boat1'].startTime).toBe('07:45:00')
    expect(boatAssignments['boat2'].startTime).toBe('07:45:00')
  })

  it('should assign different start times to semi-marathon boats with intervals', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 21, event_type: '21km' }
    ]
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1' },
      { boat_registration_id: 'boat2', race_id: 'race1' },
      { boat_registration_id: 'boat3', race_id: 'race1' }
    ]

    const { boatAssignments } = assignRaceAndBowNumbers(races, boats, config)

    expect(boatAssignments['boat1'].startTime).toBe('09:00:00') // 0 seconds
    expect(boatAssignments['boat2'].startTime).toBe('09:00:30') // 30 seconds
    expect(boatAssignments['boat3'].startTime).toBe('09:01:00') // 60 seconds
  })

  it('should skip races with no boats', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42 },
      { race_id: 'race2', display_order: 2, distance: 21 }
    ]
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1' }
    ]

    const { raceAssignments } = assignRaceAndBowNumbers(races, boats, config)

    expect(raceAssignments['race1']).toBeDefined()
    expect(raceAssignments['race1'].raceNumber).toBe(1)
    expect(raceAssignments['race2']).toBeUndefined()
  })

  it('should maintain separate bow number sequences for marathon and semi-marathon', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, event_type: '42km' },
      { race_id: 'race2', display_order: 2, distance: 21, event_type: '21km' },
      { race_id: 'race3', display_order: 3, distance: 42, event_type: '42km' }
    ]
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1' },
      { boat_registration_id: 'boat2', race_id: 'race1' },
      { boat_registration_id: 'boat3', race_id: 'race2' },
      { boat_registration_id: 'boat4', race_id: 'race3' }
    ]

    const { boatAssignments } = assignRaceAndBowNumbers(races, boats, config)

    // Marathon boats: 1, 2, 3
    expect(boatAssignments['boat1'].bowNumber).toBe(1)
    expect(boatAssignments['boat2'].bowNumber).toBe(2)
    expect(boatAssignments['boat4'].bowNumber).toBe(3)

    // Semi-marathon boats: 41
    expect(boatAssignments['boat3'].bowNumber).toBe(41)
  })

  it('should assign same race number to all boats in the same race', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42 }
    ]
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1' },
      { boat_registration_id: 'boat2', race_id: 'race1' },
      { boat_registration_id: 'boat3', race_id: 'race1' }
    ]

    const { boatAssignments } = assignRaceAndBowNumbers(races, boats, config)

    expect(boatAssignments['boat1'].raceNumber).toBe(1)
    expect(boatAssignments['boat2'].raceNumber).toBe(1)
    expect(boatAssignments['boat3'].raceNumber).toBe(1)
  })

  it('should handle custom bow start numbers', () => {
    const customConfig = {
      ...config,
      marathon_bow_start: 100,
      semi_marathon_bow_start: 200
    }

    const races = [
      { race_id: 'race1', display_order: 1, distance: 42, event_type: '42km' },
      { race_id: 'race2', display_order: 2, distance: 21, event_type: '21km' }
    ]
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1' },
      { boat_registration_id: 'boat2', race_id: 'race2' }
    ]

    const { boatAssignments } = assignRaceAndBowNumbers(races, boats, customConfig)

    expect(boatAssignments['boat1'].bowNumber).toBe(100)
    expect(boatAssignments['boat2'].bowNumber).toBe(200)
  })
})

describe('Consistency Tests - Race and Bow Numbers', () => {
  it('should produce identical race numbers for the same input data', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42 },
      { race_id: 'race2', display_order: 2, distance: 21 }
    ]
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1' },
      { boat_registration_id: 'boat2', race_id: 'race2' }
    ]
    const config = {
      marathon_bow_start: 1,
      semi_marathon_bow_start: 41
    }

    const result1 = assignRaceAndBowNumbers(races, boats, config)
    const result2 = assignRaceAndBowNumbers(races, boats, config)

    expect(result1.raceAssignments).toEqual(result2.raceAssignments)
    expect(result1.boatAssignments).toEqual(result2.boatAssignments)
  })

  it('should produce identical bow numbers for the same input data', () => {
    const races = [
      { race_id: 'race1', display_order: 1, distance: 42 }
    ]
    const boats = [
      { boat_registration_id: 'boat1', race_id: 'race1' },
      { boat_registration_id: 'boat2', race_id: 'race1' },
      { boat_registration_id: 'boat3', race_id: 'race1' }
    ]
    const config = {
      marathon_bow_start: 1,
      semi_marathon_bow_start: 41
    }

    const result1 = assignRaceAndBowNumbers(races, boats, config)
    const result2 = assignRaceAndBowNumbers(races, boats, config)

    expect(result1.boatAssignments['boat1'].bowNumber).toBe(result2.boatAssignments['boat1'].bowNumber)
    expect(result1.boatAssignments['boat2'].bowNumber).toBe(result2.boatAssignments['boat2'].bowNumber)
    expect(result1.boatAssignments['boat3'].bowNumber).toBe(result2.boatAssignments['boat3'].bowNumber)
  })
})
