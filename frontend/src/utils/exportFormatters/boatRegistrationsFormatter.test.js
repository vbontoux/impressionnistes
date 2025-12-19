/**
 * Boat Registrations Formatter Tests
 * Test CSV generation and formatting for boat registrations export
 */
import { formatBoatRegistrationsToCSV, calculateFilledSeats } from './boatRegistrationsFormatter.js';

console.log('=== Testing Boat Registrations Formatter ===\n');

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

const csv1 = formatBoatRegistrationsToCSV(testData1);
const lines1 = csv1.split('\n');
const headers1 = lines1[0];

assert(headers1.includes('Boat Registration ID'), 'Headers include Boat Registration ID');
assert(headers1.includes('Event Type'), 'Headers include Event Type');
assert(headers1.includes('Boat Type'), 'Headers include Boat Type');
assert(headers1.includes('Race Name'), 'Headers include Race Name');
assert(headers1.includes('Registration Status'), 'Headers include Registration Status');
assert(headers1.includes('Forfait'), 'Headers include Forfait');
assert(headers1.includes('Filled Seats'), 'Headers include Filled Seats');
assert(headers1.includes('Gender Category'), 'Headers include Gender Category');
assert(headers1.includes('Age Category'), 'Headers include Age Category');
assert(lines1.length === 2, 'CSV has header + 1 data row');
assert(lines1[1].includes('boat-123'), 'Data row contains boat ID');
assert(lines1[1].includes('21km'), 'Data row contains event type');
console.log('');

// Test 2: Filled seats calculation
console.log('Test 2: Filled seats calculation');

// Test with crew_composition
const boat1 = {
  crew_composition: {
    filled_seats: 4,
    total_seats: 5
  }
};
assert(calculateFilledSeats(boat1) === '4/5', 'Calculates from crew_composition');

// Test with seats array (fallback)
const boat2 = {
  seats: [
    { position: 1, type: 'rower', crew_member_id: 'crew-1' },
    { position: 2, type: 'rower', crew_member_id: 'crew-2' },
    { position: 3, type: 'rower', crew_member_id: null },
    { position: 4, type: 'rower', crew_member_id: null }
  ]
};
assert(calculateFilledSeats(boat2) === '2/4', 'Calculates from seats array when crew_composition missing');

// Test with empty seats
const boat3 = {
  seats: []
};
assert(calculateFilledSeats(boat3) === '0/0', 'Handles empty seats array');

// Test with no data
const boat4 = {};
assert(calculateFilledSeats(boat4) === '0/0', 'Handles missing data');
console.log('');

// Test 3: Boolean formatting (Yes/No)
console.log('Test 3: Boolean formatting (Yes/No)');
const testData3 = {
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

const csv3 = formatBoatRegistrationsToCSV(testData3);
const lines3 = csv3.split('\n');

assert(lines3[1].includes('Yes'), 'Forfait true formatted as Yes');
assert(lines3[2].includes('No'), 'Forfait false formatted as No');
console.log('');

// Test 4: Nested data handling
console.log('Test 4: Nested data handling');
const testData4 = {
  success: true,
  data: {
    boats: [
      {
        boat_registration_id: 'boat-nested',
        event_type: '21km',
        boat_type: '4+',
        registration_status: 'complete',
        forfait: false,
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

const csv4 = formatBoatRegistrationsToCSV(testData4);
const lines4 = csv4.split('\n');

assert(lines4[1].includes('mixed'), 'Nested gender_category extracted');
assert(lines4[1].includes('senior'), 'Nested age_category extracted');
assert(lines4[1].includes('28.5'), 'Nested avg_age extracted');
assert(lines4[1].includes('5/5'), 'Filled seats calculated from nested data');
console.log('');

// Test 5: Empty dataset handling
console.log('Test 5: Empty dataset handling');
const testData5 = {
  success: true,
  data: {
    boats: []
  }
};

const csv5 = formatBoatRegistrationsToCSV(testData5);
const lines5 = csv5.split('\n');

assert(lines5.length === 1, 'Empty dataset returns only headers');
assert(lines5[0].includes('Boat Registration ID'), 'Headers present even with empty data');
console.log('');

// Test 6: Missing field handling
console.log('Test 6: Missing field handling');
const testData6 = {
  success: true,
  data: {
    boats: [
      {
        boat_registration_id: 'boat-minimal',
        event_type: '21km',
        boat_type: '4+',
        registration_status: 'incomplete',
        forfait: false
        // Missing race_name, crew_composition, team manager fields, etc.
      }
    ]
  }
};

const csv6 = formatBoatRegistrationsToCSV(testData6);
const lines6 = csv6.split('\n');

assert(lines6.length === 2, 'CSV generated with missing fields');
assert(lines6[1].includes('boat-minimal'), 'Present fields are included');
const fieldCount = lines6[1].split(',').length;
const headerCount = lines6[0].split(',').length;
assert(fieldCount === headerCount, 'Missing fields result in empty CSV values');
console.log('');

// Test 7: Invalid data format error handling
console.log('Test 7: Invalid data format error handling');
try {
  formatBoatRegistrationsToCSV(null);
  assert(false, 'Should throw error for null data');
} catch (error) {
  assert(error.message.includes('Invalid data format'), 'Throws error for null data');
}

try {
  formatBoatRegistrationsToCSV({ data: {} });
  assert(false, 'Should throw error for missing boats array');
} catch (error) {
  assert(error.message.includes('Invalid data format'), 'Throws error for missing boats');
}
console.log('');

// Test 8: Multiple boats
console.log('Test 8: Multiple boats');
const testData8 = {
  success: true,
  data: {
    boats: [
      {
        boat_registration_id: 'boat-1',
        event_type: '21km',
        boat_type: '4+',
        registration_status: 'complete',
        forfait: false,
        crew_composition: { filled_seats: 5, total_seats: 5 }
      },
      {
        boat_registration_id: 'boat-2',
        event_type: '42km',
        boat_type: 'skiff',
        registration_status: 'paid',
        forfait: false,
        crew_composition: { filled_seats: 1, total_seats: 1 }
      },
      {
        boat_registration_id: 'boat-3',
        event_type: '21km',
        boat_type: '8+',
        registration_status: 'free',
        forfait: true,
        crew_composition: { filled_seats: 9, total_seats: 9 }
      }
    ]
  }
};

const csv8 = formatBoatRegistrationsToCSV(testData8);
const lines8 = csv8.split('\n');

assert(lines8.length === 4, 'CSV has header + 3 data rows');
assert(lines8[1].includes('boat-1'), 'First boat present');
assert(lines8[2].includes('boat-2'), 'Second boat present');
assert(lines8[3].includes('boat-3'), 'Third boat present');
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
