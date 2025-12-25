/**
 * Boat Registrations Formatter Tests
 * Test CSV generation and formatting for boat registrations export
 */
import { describe, test, expect } from 'vitest';
import { formatBoatRegistrationsToCSV, calculateFilledSeats } from './boatRegistrationsFormatter.js';

describe('Boat Registrations Formatter', () => {
  describe('CSV structure and headers', () => {
    test('should generate correct CSV structure with all headers', () => {
      const testData = {
        success: true,
        data: {
          boats: [
            {
              boat_registration_id: 'boat-123',
              event_type: '21km',
              boat_type: '4+',
              race_name: 'WOMEN-JUNIOR J16-COXED SWEEP FOUR',
              registration_status: 'complete',
              forfait: false,
              seats: [
                { position: 1, type: 'rower', crew_member_id: 'crew-1' },
                { position: 2, type: 'rower', crew_member_id: 'crew-2' },
                { position: 3, type: 'rower', crew_member_id: 'crew-3' },
                { position: 4, type: 'rower', crew_member_id: 'crew-4' },
                { position: 5, type: 'cox', crew_member_id: 'crew-5' }
              ],
              crew_details: [
                { position: 1, type: 'rower', crew_member_id: 'crew-1', first_name: 'Alice', last_name: 'Smith', gender: 'F', date_of_birth: '2008-05-15', age: 16, license_number: 'LIC001', club_affiliation: 'RCPM' },
                { position: 2, type: 'rower', crew_member_id: 'crew-2', first_name: 'Bob', last_name: 'Jones', gender: 'F', date_of_birth: '2008-08-20', age: 16, license_number: 'LIC002', club_affiliation: 'RCPM' },
                { position: 3, type: 'rower', crew_member_id: 'crew-3', first_name: 'Carol', last_name: 'White', gender: 'F', date_of_birth: '2008-03-10', age: 17, license_number: 'LIC003', club_affiliation: 'RCPM' },
                { position: 4, type: 'rower', crew_member_id: 'crew-4', first_name: 'Diana', last_name: 'Brown', gender: 'F', date_of_birth: '2008-11-25', age: 16, license_number: 'LIC004', club_affiliation: 'RCPM' },
                { position: 5, type: 'cox', crew_member_id: 'crew-5', first_name: 'Eve', last_name: 'Davis', gender: 'F', date_of_birth: '2009-01-05', age: 16, license_number: 'LIC005', club_affiliation: 'RCPM' }
              ],
              crew_composition: {
                gender_category: 'women',
                age_category: 'j16',
                avg_age: 16.5,
                filled_seats: 5,
                total_seats: 5
              },
              is_multi_club_crew: false,
              team_manager_name: 'John Doe',
              team_manager_email: 'john@example.com',
              team_manager_club: 'RCPM',
              created_at: '2025-01-01T10:00:00Z',
              updated_at: '2025-01-02T15:30:00Z',
              paid_at: '2025-01-03T09:00:00Z'
            }
          ]
        }
      };

      const csv = formatBoatRegistrationsToCSV(testData);
      const lines = csv.split('\n');
      const headers = lines[0];

      expect(headers).toContain('Boat Registration ID');
      expect(headers).toContain('Event Type');
      expect(headers).toContain('Boat Type');
      expect(headers).toContain('Race Name');
      expect(headers).toContain('Registration Status');
      expect(headers).toContain('Forfait');
      expect(headers).toContain('Filled Seats');
      expect(headers).toContain('Gender Category');
      expect(headers).toContain('Age Category');
      expect(headers).toContain('1. First Name');
      expect(headers).toContain('1. Last Name');
      expect(headers).toContain('5. Club Affiliation');
      expect(lines.length).toBe(2);
      expect(lines[1]).toContain('boat-123');
      expect(lines[1]).toContain('21km');
      expect(lines[1]).toContain('Alice');
      expect(lines[1]).toContain('Smith');
    });
  });

  describe('Filled seats calculation', () => {
    test('should calculate from crew_composition when available', () => {
      const boat = {
        crew_composition: {
          filled_seats: 4,
          total_seats: 5
        }
      };
      
      expect(calculateFilledSeats(boat)).toBe('4/5');
    });

    test('should calculate from seats array as fallback', () => {
      const boat = {
        seats: [
          { position: 1, type: 'rower', crew_member_id: 'crew-1' },
          { position: 2, type: 'rower', crew_member_id: 'crew-2' },
          { position: 3, type: 'rower', crew_member_id: null },
          { position: 4, type: 'rower', crew_member_id: null }
        ]
      };
      
      expect(calculateFilledSeats(boat)).toBe('2/4');
    });

    test('should handle empty seats array', () => {
      const boat = { seats: [] };
      expect(calculateFilledSeats(boat)).toBe('0/0');
    });

    test('should handle missing data', () => {
      const boat = {};
      expect(calculateFilledSeats(boat)).toBe('0/0');
    });
  });

  describe('Boolean formatting', () => {
    test('should format boolean values as Yes/No', () => {
      const testData = {
        success: true,
        data: {
          boats: [
            {
              boat_registration_id: 'boat-456',
              event_type: '42km',
              boat_type: 'skiff',
              registration_status: 'paid',
              forfait: true,
              is_multi_club_crew: true,
              crew_composition: {
                filled_seats: 1,
                total_seats: 1
              }
            },
            {
              boat_registration_id: 'boat-789',
              event_type: '21km',
              boat_type: '8+',
              registration_status: 'complete',
              forfait: false,
              is_multi_club_crew: false,
              crew_composition: {
                filled_seats: 9,
                total_seats: 9
              }
            }
          ]
        }
      };

      const csv = formatBoatRegistrationsToCSV(testData);
      const lines = csv.split('\n');

      expect(lines[1]).toContain('Yes');
      expect(lines[2]).toContain('No');
    });
  });

  describe('Nested data handling', () => {
    test('should extract nested crew composition data', () => {
      const testData = {
        success: true,
        data: {
          boats: [
            {
              boat_registration_id: 'boat-nested',
              event_type: '21km',
              boat_type: '4+',
              registration_status: 'complete',
              forfait: false,
              crew_details: [
                { position: 1, type: 'rower', crew_member_id: 'crew-1', first_name: 'John', last_name: 'Doe', gender: 'M', date_of_birth: '1995-05-15', age: 30, license_number: 'LIC100', club_affiliation: 'Club A' },
                { position: 2, type: 'rower', crew_member_id: 'crew-2', first_name: 'Jane', last_name: 'Smith', gender: 'F', date_of_birth: '1997-08-20', age: 28, license_number: 'LIC101', club_affiliation: 'Club B' }
              ],
              crew_composition: {
                gender_category: 'mixed',
                age_category: 'senior',
                avg_age: 28.5,
                filled_seats: 5,
                total_seats: 5
              }
            }
          ]
        }
      };

      const csv = formatBoatRegistrationsToCSV(testData);
      const lines = csv.split('\n');

      expect(lines[1]).toContain('mixed');
      expect(lines[1]).toContain('senior');
      expect(lines[1]).toContain('28.5');
      expect(lines[1]).toContain('5/5');
      expect(lines[1]).toContain('John');
      expect(lines[1]).toContain('Club A');
    });
  });

  describe('Empty dataset handling', () => {
    test('should return only headers for empty dataset', () => {
      const testData = {
        success: true,
        data: {
          boats: []
        }
      };

      const csv = formatBoatRegistrationsToCSV(testData);
      const lines = csv.split('\n');

      expect(lines.length).toBe(1);
      expect(lines[0]).toContain('Boat Registration ID');
    });
  });

  describe('Missing field handling', () => {
    test('should handle missing optional fields gracefully', () => {
      const testData = {
        success: true,
        data: {
          boats: [
            {
              boat_registration_id: 'boat-minimal',
              event_type: '21km',
              boat_type: '4+',
              registration_status: 'incomplete',
              forfait: false
            }
          ]
        }
      };

      const csv = formatBoatRegistrationsToCSV(testData);
      const lines = csv.split('\n');

      expect(lines.length).toBe(2);
      expect(lines[1]).toContain('boat-minimal');
      
      const fieldCount = lines[1].split(',').length;
      const headerCount = lines[0].split(',').length;
      expect(fieldCount).toBe(headerCount);
    });
  });

  describe('Invalid data format error handling', () => {
    test('should throw error for null data', () => {
      expect(() => formatBoatRegistrationsToCSV(null)).toThrow('Invalid data format');
    });

    test('should throw error for missing boats array', () => {
      expect(() => formatBoatRegistrationsToCSV({ data: {} })).toThrow('Invalid data format');
    });
  });

  describe('Multiple boats', () => {
    test('should handle multiple boats correctly', () => {
      const testData = {
        success: true,
        data: {
          boats: [
            {
              boat_registration_id: 'boat-1',
              event_type: '21km',
              boat_type: '4+',
              registration_status: 'complete',
              forfait: false,
              crew_details: [
                { position: 1, type: 'rower', crew_member_id: 'crew-1', first_name: 'Alice', last_name: 'A', gender: 'F', date_of_birth: '2000-01-01', age: 25, license_number: 'L1', club_affiliation: 'C1' }
              ],
              crew_composition: { filled_seats: 5, total_seats: 5 }
            },
            {
              boat_registration_id: 'boat-2',
              event_type: '42km',
              boat_type: 'skiff',
              registration_status: 'paid',
              forfait: false,
              crew_details: [
                { position: 1, type: 'rower', crew_member_id: 'crew-2', first_name: 'Bob', last_name: 'B', gender: 'M', date_of_birth: '1995-05-05', age: 30, license_number: 'L2', club_affiliation: 'C2' }
              ],
              crew_composition: { filled_seats: 1, total_seats: 1 }
            },
            {
              boat_registration_id: 'boat-3',
              event_type: '21km',
              boat_type: '8+',
              registration_status: 'free',
              forfait: true,
              crew_details: [],
              crew_composition: { filled_seats: 9, total_seats: 9 }
            }
          ]
        }
      };

      const csv = formatBoatRegistrationsToCSV(testData);
      const lines = csv.split('\n');

      expect(lines.length).toBe(4);
      expect(lines[1]).toContain('boat-1');
      expect(lines[2]).toContain('boat-2');
      expect(lines[3]).toContain('boat-3');
      expect(lines[1]).toContain('Alice');
      expect(lines[2]).toContain('Bob');
    });
  });
});
