/**
 * Crew Members Formatter Tests
 * Test CSV generation and formatting for crew members export
 */
import { formatCrewMembersToCSV } from './crewMembersFormatter.js';

console.log('=== Testing Crew Members Formatter ===\n');

let passCount = 0;
let failCount = 0;

function assert(condition, testName) {
  if (condition) {
    console.log(`✓ PASS: ${testName}`);
    passCount++;
  } else {
    console.log(`✗ FAIL: ${testName}`);
    failCount++;
  }
}

// Test 1: CSV structure and headers
console.log('Test 1: CSV structure and headers');
const testData1 = {
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

const csv1 = formatCrewMembersToCSV(testData1);
const lines1 = csv1.split('\n');
const headers1 = lines1[0];

assert(headers1.includes('Crew Member ID'), 'Headers include Crew Member ID');
assert(headers1.includes('First Name'), 'Headers include First Name');
assert(headers1.includes('Last Name'), 'Headers include Last Name');
assert(headers1.includes('Gender'), 'Headers include Gender');
assert(headers1.includes('Team Manager Name'), 'Headers include Team Manager Name');
assert(lines1.length === 2, 'CSV has header + 1 data row');
assert(lines1[1].includes('Alice'), 'Data row contains first name');
assert(lines1[1].includes('Smith'), 'Data row contains last name');
console.log('');

// Test 2: Special character escaping
console.log('Test 2: Special character escaping');
const testData2 = {
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

const csv2 = formatCrewMembersToCSV(testData2);
const lines2 = csv2.split('\n');

// Fields with commas or quotes should be wrapped in quotes
assert(lines2[1].includes('"LIC,002"'), 'License with comma is quoted');
assert(lines2[1].includes('"Club ""Elite"""'), 'Club with quotes is escaped');
assert(lines2[1].includes('"Jane, Manager"'), 'Manager name with comma is quoted');
console.log('');

// Test 3: Empty dataset handling
console.log('Test 3: Empty dataset handling');
const testData3 = {
  success: true,
  data: {
    crew_members: []
  }
};

const csv3 = formatCrewMembersToCSV(testData3);
const lines3 = csv3.split('\n');

assert(lines3.length === 1, 'Empty dataset returns only headers');
assert(lines3[0].includes('Crew Member ID'), 'Headers present even with empty data');
console.log('');

// Test 4: Missing field handling
console.log('Test 4: Missing field handling');
const testData4 = {
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
        // Missing license_number, club_affiliation, team manager fields
      }
    ]
  }
};

const csv4 = formatCrewMembersToCSV(testData4);
const lines4 = csv4.split('\n');

assert(lines4.length === 2, 'CSV generated with missing fields');
assert(lines4[1].includes('Charlie'), 'Present fields are included');
// Missing fields should result in empty values (consecutive commas)
const fieldCount = lines4[1].split(',').length;
const headerCount = lines4[0].split(',').length;
assert(fieldCount === headerCount, 'Missing fields result in empty CSV values');
console.log('');

// Test 5: Invalid data format error handling
console.log('Test 5: Invalid data format error handling');
try {
  formatCrewMembersToCSV(null);
  assert(false, 'Should throw error for null data');
} catch (error) {
  assert(error.message.includes('Invalid data format'), 'Throws error for null data');
}

try {
  formatCrewMembersToCSV({ data: {} });
  assert(false, 'Should throw error for missing crew_members array');
} catch (error) {
  assert(error.message.includes('Invalid data format'), 'Throws error for missing crew_members');
}
console.log('');

// Test 6: Multiple crew members
console.log('Test 6: Multiple crew members');
const testData6 = {
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

const csv6 = formatCrewMembersToCSV(testData6);
const lines6 = csv6.split('\n');

assert(lines6.length === 4, 'CSV has header + 3 data rows');
assert(lines6[1].includes('Alice'), 'First crew member present');
assert(lines6[2].includes('Bob'), 'Second crew member present');
assert(lines6[3].includes('Charlie'), 'Third crew member present');
console.log('');

// Summary
console.log('=== Test Summary ===');
console.log(`Total: ${passCount + failCount} tests`);
console.log(`Passed: ${passCount}`);
console.log(`Failed: ${failCount}`);

if (failCount === 0) {
  console.log('\n✓ All tests passed!');
} else {
  console.log(`\n✗ ${failCount} test(s) failed`);
  process.exit(1);
}
