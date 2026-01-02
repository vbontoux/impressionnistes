/**
 * CrewTimer Formatter Tests
 * Test CrewTimer transformations and formatting
 */
import { describe, test, expect } from 'vitest';
import { 
  formatRacesToCrewTimer,
  calculateAverageAge,
  getStrokeSeatName,
  formatTime12Hour
} from './crewTimerFormatter.js';

describe('CrewTimer Formatter', () => {
  describe('Boat filtering', () => {
    test('should include only complete/paid/free boats and exclude forfait', () => {
      const testData = {
        success: true,
        data: {
          config: { 
            competition_date: '2025-05-01',
            marathon_start_time: '07:45',
            semi_marathon_start_time: '09:00',
            semi_marathon_interval_seconds: 30,
            marathon_bow_start: 1,
            semi_marathon_bow_start: 41
          },
          races: [
            { race_id: 'R1', name: 'Test Race', distance: 21, event_type: '21km', boat_type: '4+' }
          ],
          boats: [
            { boat_registration_id: 'b1', race_id: 'R1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 25 } },
            { boat_registration_id: 'b2', race_id: 'R1', registration_status: 'paid', forfait: false, seats: [], crew_composition: { avg_age: 30 } },
            { boat_registration_id: 'b3', race_id: 'R1', registration_status: 'free', forfait: false, seats: [], crew_composition: { avg_age: 28 } },
            { boat_registration_id: 'b4', race_id: 'R1', registration_status: 'incomplete', forfait: false, seats: [], crew_composition: { avg_age: 35 } },
            { boat_registration_id: 'b5', race_id: 'R1', registration_status: 'complete', forfait: true, seats: [], crew_composition: { avg_age: 32 } }
          ],
          crew_members: [],
          team_managers: []
        }
      };

      const result = formatRacesToCrewTimer(testData);
      
      expect(result.length).toBe(3);
      expect(result.every(r => r.Bow >= 41 && r.Bow <= 43)).toBe(true);
    });
  });

  describe('Race sorting', () => {
    test('should sort marathon races before semi-marathon', () => {
      const testData = {
        success: true,
        data: {
          config: { 
            competition_date: '2025-05-01',
            marathon_start_time: '07:45',
            semi_marathon_start_time: '09:00',
            semi_marathon_interval_seconds: 30,
            marathon_bow_start: 1,
            semi_marathon_bow_start: 41
          },
          races: [
            { race_id: 'SM1', name: 'Semi Race 1', distance: 21, event_type: '21km', boat_type: '4+', display_order: 3 },
            { race_id: 'M1', name: 'Marathon Race 1', distance: 42, event_type: '42km', boat_type: 'skiff', display_order: 1 },
            { race_id: 'SM2', name: 'Semi Race 2', distance: 21, event_type: '21km', boat_type: '8+', display_order: 4 },
            { race_id: 'M2', name: 'Marathon Race 2', distance: 42, event_type: '42km', boat_type: '4+', display_order: 2 }
          ],
          boats: [
            { boat_registration_id: 'b1', race_id: 'SM1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 25 }, boat_club_display: 'Club A' },
            { boat_registration_id: 'b2', race_id: 'M1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 30 }, boat_club_display: 'Club B' },
            { boat_registration_id: 'b3', race_id: 'SM2', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 28 }, boat_club_display: 'Club C' },
            { boat_registration_id: 'b4', race_id: 'M2', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 35 }, boat_club_display: 'Club D' }
          ],
          crew_members: [],
          team_managers: []
        }
      };

      const result = formatRacesToCrewTimer(testData);
      const marathonRows = result.filter(r => r['Event Num'] <= 2);
      const semiRows = result.filter(r => r['Event Num'] > 2);
      
      expect(result.length).toBe(4);
      expect(marathonRows.length).toBe(2);
      expect(semiRows.length).toBe(2);
      expect(marathonRows.every(r => r.Event.includes('Marathon Race'))).toBe(true);
    });
  });

  describe('Event numbering', () => {
    test('should assign same event number to boats in same race', () => {
      const testData = {
        success: true,
        data: {
          config: { 
            competition_date: '2025-05-01',
            marathon_start_time: '07:45',
            semi_marathon_start_time: '09:00',
            semi_marathon_interval_seconds: 30,
            marathon_bow_start: 1,
            semi_marathon_bow_start: 41
          },
          races: [
            { race_id: 'R1', name: 'Race 1', distance: 21, event_type: '21km', boat_type: '4+' },
            { race_id: 'R2', name: 'Race 2', distance: 21, event_type: '21km', boat_type: '8+' }
          ],
          boats: [
            { boat_registration_id: 'b1', race_id: 'R1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 25 }, boat_club_display: 'Club A' },
            { boat_registration_id: 'b2', race_id: 'R1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 30 }, boat_club_display: 'Club B' },
            { boat_registration_id: 'b3', race_id: 'R1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 28 }, boat_club_display: 'Club C' },
            { boat_registration_id: 'b4', race_id: 'R2', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 35 }, boat_club_display: 'Club D' },
            { boat_registration_id: 'b5', race_id: 'R2', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 32 }, boat_club_display: 'Club E' }
          ],
          crew_members: [],
          team_managers: []
        }
      };

      const result = formatRacesToCrewTimer(testData);
      const r1Boats = result.filter(r => r.Bow >= 41 && r.Bow <= 43);
      const r2Boats = result.filter(r => r.Bow >= 44 && r.Bow <= 45);
      
      expect(r1Boats.every(r => r['Event Num'] === 1)).toBe(true);
      expect(r2Boats.every(r => r['Event Num'] === 2)).toBe(true);
    });
  });

  describe('Bow numbering', () => {
    test('should assign sequential bow numbers starting at configured value', () => {
      const testData = {
        success: true,
        data: {
          config: { 
            competition_date: '2025-05-01',
            marathon_start_time: '07:45',
            semi_marathon_start_time: '09:00',
            semi_marathon_interval_seconds: 30,
            marathon_bow_start: 1,
            semi_marathon_bow_start: 41
          },
          races: [
            { race_id: 'R1', name: 'Race 1', distance: 21, event_type: '21km', boat_type: '4+' },
            { race_id: 'R2', name: 'Race 2', distance: 21, event_type: '21km', boat_type: '8+' }
          ],
          boats: [
            { boat_registration_id: 'b1', race_id: 'R1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 25 } },
            { boat_registration_id: 'b2', race_id: 'R1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 30 } },
            { boat_registration_id: 'b3', race_id: 'R2', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 28 } },
            { boat_registration_id: 'b4', race_id: 'R2', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 35 } }
          ],
          crew_members: [],
          team_managers: []
        }
      };

      const result = formatRacesToCrewTimer(testData);
      const bowNumbers = result.map(r => r.Bow);
      
      expect(bowNumbers.length).toBe(4);
      expect(bowNumbers).toEqual([41, 42, 43, 44]);
    });
  });

  describe('Stroke seat extraction', () => {
    test('should extract stroke seat from highest position rower', () => {
      const seats = [
        { position: 1, type: 'rower', crew_member_id: 'crew-1' },
        { position: 2, type: 'rower', crew_member_id: 'crew-2' },
        { position: 3, type: 'rower', crew_member_id: 'crew-3' },
        { position: 4, type: 'rower', crew_member_id: 'crew-4' },
        { position: 5, type: 'cox', crew_member_id: 'crew-5' }
      ];
      const crewDict = {
        'crew-1': { first_name: 'Alice', last_name: 'Smith' },
        'crew-2': { first_name: 'Bob', last_name: 'Jones' },
        'crew-3': { first_name: 'Charlie', last_name: 'Brown' },
        'crew-4': { first_name: 'Diana', last_name: 'Wilson' },
        'crew-5': { first_name: 'Eve', last_name: 'Cox' }
      };

      const strokeName = getStrokeSeatName(seats, crewDict);
      expect(strokeName).toBe('Wilson');
    });

    test('should handle skiff with single rower', () => {
      const seats = [
        { position: 1, type: 'rower', crew_member_id: 'crew-1' }
      ];
      const crewDict = {
        'crew-1': { first_name: 'Alice', last_name: 'Smith' }
      };

      const strokeName = getStrokeSeatName(seats, crewDict);
      expect(strokeName).toBe('Smith');
    });

    test('should return empty string for empty seats', () => {
      const strokeName = getStrokeSeatName([], {});
      expect(strokeName).toBe('');
    });
  });

  describe('Average age calculation', () => {
    test('should calculate and round average age correctly', () => {
      const crewMembers = [
        { age: 35 },
        { age: 33 },
        { age: 37 },
        { age: 34 }
      ];
      
      const avgAge = calculateAverageAge(crewMembers);
      expect(avgAge).toBe(35);
    });

    test('should return 0 for empty crew', () => {
      const avgAge = calculateAverageAge([]);
      expect(avgAge).toBe(0);
    });

    test('should handle missing ages', () => {
      const crewMembers = [
        { age: 35 },
        { age: null },
        { age: 33 }
      ];
      
      const avgAge = calculateAverageAge(crewMembers);
      expect(avgAge).toBe(34);
    });
  });

  describe('Empty dataset handling', () => {
    test('should return empty array for empty dataset', () => {
      const testData = {
        success: true,
        data: {
          config: { competition_date: '2025-05-01' },
          races: [],
          boats: [],
          crew_members: [],
          team_managers: []
        }
      };

      const result = formatRacesToCrewTimer(testData);
      expect(result.length).toBe(0);
    });
  });

  describe('Invalid data format error handling', () => {
    test('should throw error for null data', () => {
      expect(() => formatRacesToCrewTimer(null)).toThrow('Invalid data format');
    });

    test('should throw error for missing required arrays', () => {
      expect(() => formatRacesToCrewTimer({ data: {} })).toThrow('Invalid data format');
    });
  });

  describe('Complete integration test', () => {
    test('should use crew_composition.avg_age from backend', () => {
      const testData = {
        success: true,
        data: {
          config: { competition_date: '2025-05-01' },
          races: [
            { 
              race_id: 'M1', 
              name: '1X SENIOR MAN', 
              distance: 42, 
              event_type: '42km', 
              boat_type: 'skiff',
              age_category: 'senior',
              gender_category: 'men'
            },
            { 
              race_id: 'SM1', 
              name: 'WOMEN-JUNIOR J16-COXED SWEEP FOUR', 
              distance: 21, 
              event_type: '21km', 
              boat_type: '4+',
              age_category: 'j16',
              gender_category: 'women'
            }
          ],
          boats: [
            { 
              boat_registration_id: 'b1', 
              race_id: 'M1', 
              registration_status: 'complete', 
              forfait: false,
              team_manager_id: 'tm1',
              boat_club_display: 'RCPM',
              club_list: ['RCPM'],
              crew_composition: {
                avg_age: 35.0,
                gender_category: 'men',
                age_category: 'senior'
              },
              seats: [
                { position: 1, type: 'rower', crew_member_id: 'crew-1' }
              ]
            },
            { 
              boat_registration_id: 'b2', 
              race_id: 'SM1', 
              registration_status: 'paid', 
              forfait: false,
              team_manager_id: 'tm2',
              boat_club_display: 'Club Elite',
              club_list: ['Club Elite'],
              crew_composition: {
                avg_age: 16.25,
                gender_category: 'women',
                age_category: 'j16'
              },
              seats: [
                { position: 1, type: 'rower', crew_member_id: 'crew-2' },
                { position: 2, type: 'rower', crew_member_id: 'crew-3' },
                { position: 3, type: 'rower', crew_member_id: 'crew-4' },
                { position: 4, type: 'rower', crew_member_id: 'crew-5' },
                { position: 5, type: 'cox', crew_member_id: 'crew-6' }
              ]
            }
          ],
          crew_members: [
            { crew_member_id: 'crew-1', first_name: 'John', last_name: 'Doe', date_of_birth: '1990-01-01', age: 35 },
            { crew_member_id: 'crew-2', first_name: 'Jane', last_name: 'Smith', date_of_birth: '2009-01-01', age: 16 },
            { crew_member_id: 'crew-3', first_name: 'Bob', last_name: 'Jones', date_of_birth: '2009-06-15', age: 16 },
            { crew_member_id: 'crew-4', first_name: 'Alice', last_name: 'Brown', date_of_birth: '2008-12-31', age: 17 },
            { crew_member_id: 'crew-5', first_name: 'Charlie', last_name: 'Wilson', date_of_birth: '2009-03-20', age: 16 },
            { crew_member_id: 'crew-6', first_name: 'Eve', last_name: 'Cox', date_of_birth: '2010-01-01', age: 15 }
          ],
          team_managers: [
            { user_id: 'tm1', club_affiliation: 'RCPM', email: 'tm1@example.com' },
            { user_id: 'tm2', club_affiliation: 'Club Elite', email: 'tm2@example.com' }
          ]
        }
      };

      const result = formatRacesToCrewTimer(testData);
      
      expect(result.length).toBe(2);
      expect(result[0]['Event Num']).toBe(1);
      expect(result[1]['Event Num']).toBe(2);
      expect(result[0].Bow).toBe(1);
      expect(result[1].Bow).toBe(41);
      expect(result[0].Event).toBe('1X SENIOR MAN');
      expect(result[0]['Event Abbrev']).toBe('');
      expect(result[1].Event).toBe('WOMEN-JUNIOR J16-COXED SWEEP FOUR');
      expect(result[1]['Event Abbrev']).toBe('');
      expect(result[0].Crew).toBe('RCPM');
      expect(result[1].Crew).toBe('Club Elite');
      expect(result[0].Stroke).toBe('Doe');
      expect(result[1].Stroke).toBe('Wilson');
      expect(result[0].Age).toBe(35);
      expect(result[1].Age).toBe(16);
      expect(result[0].Handicap).toBe('');
      expect(result[0].Note).toBe('RCPM');
      expect(result[1].Handicap).toBe('');
      expect(result[1].Note).toBe('Club Elite');
    });
  });

  describe('Club list in Note column', () => {
    test('should display single club in Note column', () => {
      const testData = {
        success: true,
        data: {
          config: { 
            competition_date: '2025-05-01',
            marathon_start_time: '07:45',
            semi_marathon_start_time: '09:00',
            semi_marathon_interval_seconds: 30,
            marathon_bow_start: 1,
            semi_marathon_bow_start: 41
          },
          races: [
            { race_id: 'R1', name: 'Test Race', distance: 21, event_type: '21km', boat_type: '4+' }
          ],
          boats: [
            { 
              boat_registration_id: 'b1', 
              race_id: 'R1', 
              registration_status: 'complete', 
              forfait: false, 
              seats: [], 
              crew_composition: { avg_age: 25 },
              club_list: ['RCPM']
            }
          ],
          crew_members: [],
          team_managers: []
        }
      };

      const result = formatRacesToCrewTimer(testData);
      
      expect(result.length).toBe(1);
      expect(result[0].Note).toBe('RCPM');
    });

    test('should display multiple clubs comma-separated in Note column', () => {
      const testData = {
        success: true,
        data: {
          config: { 
            competition_date: '2025-05-01',
            marathon_start_time: '07:45',
            semi_marathon_start_time: '09:00',
            semi_marathon_interval_seconds: 30,
            marathon_bow_start: 1,
            semi_marathon_bow_start: 41
          },
          races: [
            { race_id: 'R1', name: 'Test Race', distance: 21, event_type: '21km', boat_type: '4+' }
          ],
          boats: [
            { 
              boat_registration_id: 'b1', 
              race_id: 'R1', 
              registration_status: 'complete', 
              forfait: false, 
              seats: [], 
              crew_composition: { avg_age: 25 },
              club_list: ['Club Elite', 'RCPM', 'SN Versailles']
            }
          ],
          crew_members: [],
          team_managers: []
        }
      };

      const result = formatRacesToCrewTimer(testData);
      
      expect(result.length).toBe(1);
      expect(result[0].Note).toBe('Club Elite, RCPM, SN Versailles');
    });

    test('should display empty string when club_list is missing', () => {
      const testData = {
        success: true,
        data: {
          config: { 
            competition_date: '2025-05-01',
            marathon_start_time: '07:45',
            semi_marathon_start_time: '09:00',
            semi_marathon_interval_seconds: 30,
            marathon_bow_start: 1,
            semi_marathon_bow_start: 41
          },
          races: [
            { race_id: 'R1', name: 'Test Race', distance: 21, event_type: '21km', boat_type: '4+' }
          ],
          boats: [
            { 
              boat_registration_id: 'b1', 
              race_id: 'R1', 
              registration_status: 'complete', 
              forfait: false, 
              seats: [], 
              crew_composition: { avg_age: 25 }
            }
          ],
          crew_members: [],
          team_managers: []
        }
      };

      const result = formatRacesToCrewTimer(testData);
      
      expect(result.length).toBe(1);
      expect(result[0].Note).toBe('');
    });

    test('should display empty string when club_list is empty array', () => {
      const testData = {
        success: true,
        data: {
          config: { 
            competition_date: '2025-05-01',
            marathon_start_time: '07:45',
            semi_marathon_start_time: '09:00',
            semi_marathon_interval_seconds: 30,
            marathon_bow_start: 1,
            semi_marathon_bow_start: 41
          },
          races: [
            { race_id: 'R1', name: 'Test Race', distance: 21, event_type: '21km', boat_type: '4+' }
          ],
          boats: [
            { 
              boat_registration_id: 'b1', 
              race_id: 'R1', 
              registration_status: 'complete', 
              forfait: false, 
              seats: [], 
              crew_composition: { avg_age: 25 },
              club_list: []
            }
          ],
          crew_members: [],
          team_managers: []
        }
      };

      const result = formatRacesToCrewTimer(testData);
      
      expect(result.length).toBe(1);
      expect(result[0].Note).toBe('');
    });
  });

  describe('Handicap column', () => {
    test('should have empty Handicap column for all boats', () => {
      const testData = {
        success: true,
        data: {
          config: { 
            competition_date: '2025-05-01',
            marathon_start_time: '07:45',
            semi_marathon_start_time: '09:00',
            semi_marathon_interval_seconds: 30,
            marathon_bow_start: 1,
            semi_marathon_bow_start: 41
          },
          races: [
            { race_id: 'R1', name: 'Test Race', distance: 21, event_type: '21km', boat_type: '4+' }
          ],
          boats: [
            { boat_registration_id: 'b1', race_id: 'R1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 25 } },
            { boat_registration_id: 'b2', race_id: 'R1', registration_status: 'paid', forfait: false, seats: [], crew_composition: { avg_age: 30 } }
          ],
          crew_members: [],
          team_managers: []
        }
      };

      const result = formatRacesToCrewTimer(testData);
      
      expect(result.length).toBe(2);
      expect(result[0].Handicap).toBe('');
      expect(result[1].Handicap).toBe('');
    });
  });

  describe('Time formatting', () => {
    test('should format times in 12-hour format with AM/PM', () => {
      expect(formatTime12Hour('07:45', 0)).toBe('7:45:00 AM');
      expect(formatTime12Hour('09:00', 0)).toBe('9:00:00 AM');
      expect(formatTime12Hour('12:00', 0)).toBe('12:00:00 PM');
      expect(formatTime12Hour('13:30', 0)).toBe('1:30:00 PM');
      expect(formatTime12Hour('00:00', 0)).toBe('12:00:00 AM');
    });

    test('should add seconds offset correctly', () => {
      expect(formatTime12Hour('09:00', 30)).toBe('9:00:30 AM');
      expect(formatTime12Hour('09:00', 90)).toBe('9:01:30 AM');
      expect(formatTime12Hour('09:00', 3600)).toBe('10:00:00 AM');
    });
  });

  describe('Event times in CrewTimer export', () => {
    test('should assign correct start times with intervals', () => {
      const testData = {
        success: true,
        data: {
          config: { 
            competition_date: '2025-05-01',
            marathon_start_time: '07:45',
            semi_marathon_start_time: '09:00',
            semi_marathon_interval_seconds: 30,
            marathon_bow_start: 1,
            semi_marathon_bow_start: 41
          },
          races: [
            { race_id: 'M1', name: 'Marathon Skiff', distance: 42, event_type: '42km', boat_type: 'skiff' },
            { race_id: 'SM1', name: 'Semi 4+', distance: 21, event_type: '21km', boat_type: '4+' }
          ],
          boats: [
            { boat_registration_id: 'b1', race_id: 'M1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 35 } },
            { boat_registration_id: 'b2', race_id: 'M1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 40 } },
            { boat_registration_id: 'b3', race_id: 'SM1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 25 } },
            { boat_registration_id: 'b4', race_id: 'SM1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 30 } },
            { boat_registration_id: 'b5', race_id: 'SM1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 28 } }
          ],
          crew_members: [],
          team_managers: []
        }
      };

      const result = formatRacesToCrewTimer(testData);
      
      expect(result.length).toBe(5);
      expect(result[0]['Event Time']).toBe('7:45:00 AM');
      expect(result[1]['Event Time']).toBe('7:45:00 AM');
      expect(result[2]['Event Time']).toBe('9:00:00 AM');
      expect(result[3]['Event Time']).toBe('9:00:30 AM');
      expect(result[4]['Event Time']).toBe('9:01:00 AM');
    });
  });
});
