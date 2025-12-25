/**
 * Crew Members Formatter Tests
 * Test CSV generation and formatting for crew members export
 */
import { describe, test, expect } from 'vitest';
import { formatCrewMembersToCSV } from './crewMembersFormatter.js';

describe('Crew Members Formatter', () => {
  describe('CSV structure and headers', () => {
    test('should generate correct CSV structure with all headers', () => {
      const testData = {
        success: true,
        data: {
          crew_members: [
            {
              crew_member_id: 'crew-123',
              first_name: 'Alice',
              last_name: 'Smith',
              gender: 'F',
              date_of_birth: '1990-01-15',
              age: 35,
              license_number: 'LIC001',
              club_affiliation: 'RCPM',
              team_manager_name: 'John Doe',
              team_manager_email: 'john@example.com',
              team_manager_club: 'RCPM',
              created_at: '2025-01-01T10:00:00Z',
              updated_at: '2025-01-02T15:30:00Z'
            }
          ]
        }
      };

      const csv = formatCrewMembersToCSV(testData);
      const lines = csv.split('\n');
      const headers = lines[0];

      expect(headers).toContain('Crew Member ID');
      expect(headers).toContain('First Name');
      expect(headers).toContain('Last Name');
      expect(headers).toContain('Gender');
      expect(headers).toContain('Team Manager Name');
      expect(lines.length).toBe(2);
      expect(lines[1]).toContain('Alice');
      expect(lines[1]).toContain('Smith');
    });
  });

  describe('Special character escaping', () => {
    test('should properly escape commas and quotes in CSV fields', () => {
      const testData = {
        success: true,
        data: {
          crew_members: [
            {
              crew_member_id: 'crew-456',
              first_name: 'Bob',
              last_name: 'O\'Brien',
              gender: 'M',
              date_of_birth: '1985-05-20',
              age: 40,
              license_number: 'LIC,002',
              club_affiliation: 'Club "Elite"',
              team_manager_name: 'Jane, Manager',
              team_manager_email: 'jane@example.com',
              team_manager_club: 'RCPM',
              created_at: '2025-01-01T10:00:00Z',
              updated_at: '2025-01-02T15:30:00Z'
            }
          ]
        }
      };

      const csv = formatCrewMembersToCSV(testData);
      const lines = csv.split('\n');

      expect(lines[1]).toContain('"LIC,002"');
      expect(lines[1]).toContain('"Club ""Elite"""');
      expect(lines[1]).toContain('"Jane, Manager"');
    });
  });

  describe('Empty dataset handling', () => {
    test('should return only headers for empty dataset', () => {
      const testData = {
        success: true,
        data: {
          crew_members: []
        }
      };

      const csv = formatCrewMembersToCSV(testData);
      const lines = csv.split('\n');

      expect(lines.length).toBe(1);
      expect(lines[0]).toContain('Crew Member ID');
    });
  });

  describe('Missing field handling', () => {
    test('should handle missing optional fields gracefully', () => {
      const testData = {
        success: true,
        data: {
          crew_members: [
            {
              crew_member_id: 'crew-789',
              first_name: 'Charlie',
              last_name: 'Brown',
              gender: 'M',
              date_of_birth: '1995-03-10',
              age: 30
            }
          ]
        }
      };

      const csv = formatCrewMembersToCSV(testData);
      const lines = csv.split('\n');

      expect(lines.length).toBe(2);
      expect(lines[1]).toContain('Charlie');
      
      const fieldCount = lines[1].split(',').length;
      const headerCount = lines[0].split(',').length;
      expect(fieldCount).toBe(headerCount);
    });
  });

  describe('Invalid data format error handling', () => {
    test('should throw error for null data', () => {
      expect(() => formatCrewMembersToCSV(null)).toThrow('Invalid data format');
    });

    test('should throw error for missing crew_members array', () => {
      expect(() => formatCrewMembersToCSV({ data: {} })).toThrow('Invalid data format');
    });
  });

  describe('Multiple crew members', () => {
    test('should handle multiple crew members correctly', () => {
      const testData = {
        success: true,
        data: {
          crew_members: [
            {
              crew_member_id: 'crew-1',
              first_name: 'Alice',
              last_name: 'Smith',
              gender: 'F',
              date_of_birth: '1990-01-15',
              age: 35
            },
            {
              crew_member_id: 'crew-2',
              first_name: 'Bob',
              last_name: 'Jones',
              gender: 'M',
              date_of_birth: '1985-05-20',
              age: 40
            },
            {
              crew_member_id: 'crew-3',
              first_name: 'Charlie',
              last_name: 'Brown',
              gender: 'M',
              date_of_birth: '1995-03-10',
              age: 30
            }
          ]
        }
      };

      const csv = formatCrewMembersToCSV(testData);
      const lines = csv.split('\n');

      expect(lines.length).toBe(4);
      expect(lines[1]).toContain('Alice');
      expect(lines[2]).toContain('Bob');
      expect(lines[3]).toContain('Charlie');
    });
  });
});
