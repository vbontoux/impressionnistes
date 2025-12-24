/**
 * CrewTimer Formatter Tests
 * Test CrewTimer transformations and formatting
 */
import { 
  formatRacesToCrewTimer,
  calculateAverageAge,
  getStrokeSeatName,
  formatTime12Hour
} from './crewTimerFormatter.js';

console.log('=== Testing CrewTimer Formatter ===\n');

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

// Test 1: Boat filtering (complete/paid/free, exclude forfait)
console.log('Test 1: Boat filtering (complete/paid/free, exclude forfait)');
const testData1 = {
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

const result1 = formatRacesToCrewTimer(testData1);
assert(result1.length === 3, 'Only complete/paid/free boats included');
assert(result1.every(r => r.Bow >= 41 && r.Bow <= 43), 'Semi-marathon bow numbers 41-43 for 3 boats');
console.log('');

// Test 2: Race sorting (marathon before semi-marathon)
console.log('Test 2: Race sorting (marathon before semi-marathon)');
const testData2 = {
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
      { race_id: 'SM1', name: 'Semi Race 1', distance: 21, event_type: '21km', boat_type: '4+' },
      { race_id: 'M1', name: 'Marathon Race 1', distance: 42, event_type: '42km', boat_type: 'skiff' },
      { race_id: 'SM2', name: 'Semi Race 2', distance: 21, event_type: '21km', boat_type: '8+' },
      { race_id: 'M2', name: 'Marathon Race 2', distance: 42, event_type: '42km', boat_type: '4+' }
    ],
    boats: [
      { boat_registration_id: 'b1', race_id: 'SM1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 25 } },
      { boat_registration_id: 'b2', race_id: 'M1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 30 } },
      { boat_registration_id: 'b3', race_id: 'SM2', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 28 } },
      { boat_registration_id: 'b4', race_id: 'M2', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 35 } }
    ],
    crew_members: [],
    team_managers: []
  }
};

const result2 = formatRacesToCrewTimer(testData2);
assert(result2.length === 4, 'All 4 boats included');
// Marathon races should come first (Event Num 1 and 2), then semi-marathon (Event Num 3 and 4)
const marathonRows = result2.filter(r => r['Event Num'] <= 2);
const semiRows = result2.filter(r => r['Event Num'] > 2);
assert(marathonRows.length === 2, 'Two marathon boats first');
assert(semiRows.length === 2, 'Two semi-marathon boats after');
assert(marathonRows.every(r => r.Event.includes('Marathon Race')), 'Marathon races first');
console.log('');

// Test 3: Event numbering (same race = same event num)
console.log('Test 3: Event numbering (same race = same event num)');
const testData3 = {
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
      { boat_registration_id: 'b3', race_id: 'R1', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 28 } },
      { boat_registration_id: 'b4', race_id: 'R2', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 35 } },
      { boat_registration_id: 'b5', race_id: 'R2', registration_status: 'complete', forfait: false, seats: [], crew_composition: { avg_age: 32 } }
    ],
    crew_members: [],
    team_managers: []
  }
};

const result3 = formatRacesToCrewTimer(testData3);
const r1Boats = result3.filter(r => r.Bow >= 41 && r.Bow <= 43);
const r2Boats = result3.filter(r => r.Bow >= 44 && r.Bow <= 45);
assert(r1Boats.every(r => r['Event Num'] === 1), 'All Race 1 boats have Event Num 1');
assert(r2Boats.every(r => r['Event Num'] === 2), 'All Race 2 boats have Event Num 2');
console.log('');

// Test 4: Bow numbering (separate sequences for marathon and semi-marathon)
console.log('Test 4: Bow numbering (separate sequences for marathon and semi-marathon)');
const testData4 = {
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

const result4 = formatRacesToCrewTimer(testData4);
const bowNumbers = result4.map(r => r.Bow);
assert(bowNumbers.length === 4, 'Four boats total');
assert(bowNumbers[0] === 41, 'First semi-marathon bow is 41');
assert(bowNumbers[1] === 42, 'Second semi-marathon bow is 42');
assert(bowNumbers[2] === 43, 'Third semi-marathon bow is 43');
assert(bowNumbers[3] === 44, 'Fourth semi-marathon bow is 44');
assert(JSON.stringify(bowNumbers) === JSON.stringify([41, 42, 43, 44]), 'Semi-marathon bow numbers are sequential starting at 41');
console.log('');

// Test 5: Stroke seat extraction
console.log('Test 5: Stroke seat extraction');
console.log('Test 9: Stroke seat extraction');
const seats1 = [
  { position: 1, type: 'rower', crew_member_id: 'crew-1' },
  { position: 2, type: 'rower', crew_member_id: 'crew-2' },
  { position: 3, type: 'rower', crew_member_id: 'crew-3' },
  { position: 4, type: 'rower', crew_member_id: 'crew-4' },
  { position: 5, type: 'cox', crew_member_id: 'crew-5' }
];
const crewDict1 = {
  'crew-1': { first_name: 'Alice', last_name: 'Smith' },
  'crew-2': { first_name: 'Bob', last_name: 'Jones' },
  'crew-3': { first_name: 'Charlie', last_name: 'Brown' },
  'crew-4': { first_name: 'Diana', last_name: 'Wilson' },
  'crew-5': { first_name: 'Eve', last_name: 'Cox' }
};

const strokeName1 = getStrokeSeatName(seats1, crewDict1);
assert(strokeName1 === 'Wilson', 'Stroke seat is highest position rower (position 4)');

// Test with skiff (no cox)
const seats2 = [
  { position: 1, type: 'rower', crew_member_id: 'crew-1' }
];
const strokeName2 = getStrokeSeatName(seats2, crewDict1);
assert(strokeName2 === 'Smith', 'Skiff stroke seat is the only rower');

// Test with empty seats
const strokeName3 = getStrokeSeatName([], crewDict1);
assert(strokeName3 === '', 'Empty seats returns empty string');
console.log('');

// Test 6: Average age calculation
console.log('Test 6: Average age calculation');
const crewMembers1 = [
  { age: 35 },
  { age: 33 },
  { age: 37 },
  { age: 34 }
];
const avgAge1 = calculateAverageAge(crewMembers1);
// Ages: 35, 33, 37, 34 -> Average: 34.75 -> Rounded: 35
assert(avgAge1 === 35, 'Average age calculated and rounded correctly');

// Test with empty crew
const avgAge2 = calculateAverageAge([]);
assert(avgAge2 === 0, 'Empty crew returns 0');

// Test with missing ages
const crewMembers3 = [
  { age: 35 },
  { age: null },
  { age: 33 }
];
const avgAge3 = calculateAverageAge(crewMembers3);
// Only valid ages: 35, 33 -> Average: 34
assert(avgAge3 === 34, 'Handles missing ages correctly');
console.log('');

// Test 7: Empty dataset handling
console.log('Test 7: Empty dataset handling');
const testData7 = {
  success: true,
  data: {
    config: { competition_date: '2025-05-01' },
    races: [],
    boats: [],
    crew_members: [],
    team_managers: []
  }
};

const result7 = formatRacesToCrewTimer(testData7);
assert(result7.length === 0, 'Empty dataset returns empty array');
console.log('');

// Test 8: Invalid data format error handling
console.log('Test 8: Invalid data format error handling');
try {
  formatRacesToCrewTimer(null);
  assert(false, 'Should throw error for null data');
} catch (error) {
  assert(error.message.includes('Invalid data format'), 'Throws error for null data');
}

try {
  formatRacesToCrewTimer({ data: {} });
  assert(false, 'Should throw error for missing required arrays');
} catch (error) {
  assert(error.message.includes('Invalid data format'), 'Throws error for missing arrays');
}
console.log('');

// Test 9: Complete integration test (uses crew_composition.avg_age from backend)
console.log('Test 9: Complete integration test (uses crew_composition.avg_age from backend)');
const testData9 = {
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
        crew_composition: {
          avg_age: 35.0,  // Pre-calculated by backend
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
        crew_composition: {
          avg_age: 16.25,  // Pre-calculated by backend (average of rowers only)
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

const result9 = formatRacesToCrewTimer(testData9);
assert(result9.length === 2, 'Two boats in output');
assert(result9[0]['Event Num'] === 1, 'Marathon is Event 1');
assert(result9[1]['Event Num'] === 2, 'Semi-marathon is Event 2');
assert(result9[0].Bow === 1, 'Marathon boat starts at Bow 1');
assert(result9[1].Bow === 41, 'Semi-marathon boat starts at Bow 41');
assert(result9[0].Event === '1X SENIOR MAN', 'Marathon Event uses original race name');
assert(result9[0]['Event Abbrev'] === '', 'Marathon Event Abbrev is empty (no short_name in test data)');
assert(result9[1].Event === 'WOMEN-JUNIOR J16-COXED SWEEP FOUR', 'Semi-marathon Event uses original race name');
assert(result9[1]['Event Abbrev'] === '', 'Semi-marathon Event Abbrev is empty (no short_name in test data)');
assert(result9[0].Crew === 'RCPM', 'First boat club correct');
assert(result9[1].Crew === 'Club Elite', 'Second boat club correct');
assert(result9[0].Stroke === 'Doe', 'First boat stroke correct');
assert(result9[1].Stroke === 'Wilson', 'Second boat stroke correct (highest rower)');
assert(result9[0].Age === 35, 'First boat age correct (from crew_composition)');
assert(result9[1].Age === 16, 'Second boat age correct (from crew_composition, rounded from 16.25)');
console.log('');

// Test 10: Time formatting (12-hour format with AM/PM)
console.log('Test 10: Time formatting (12-hour format with AM/PM)');
assert(formatTime12Hour('07:45', 0) === '7:45:00 AM', '7:45 AM formatted correctly');
assert(formatTime12Hour('09:00', 0) === '9:00:00 AM', '9:00 AM formatted correctly');
assert(formatTime12Hour('12:00', 0) === '12:00:00 PM', '12:00 PM formatted correctly');
assert(formatTime12Hour('13:30', 0) === '1:30:00 PM', '1:30 PM formatted correctly');
assert(formatTime12Hour('00:00', 0) === '12:00:00 AM', 'Midnight formatted correctly');
assert(formatTime12Hour('09:00', 30) === '9:00:30 AM', '30 seconds added correctly');
assert(formatTime12Hour('09:00', 90) === '9:01:30 AM', '90 seconds (1:30) added correctly');
assert(formatTime12Hour('09:00', 3600) === '10:00:00 AM', '1 hour added correctly');
console.log('');

// Test 11: Event times in CrewTimer export
console.log('Test 11: Event times in CrewTimer export');
const testData11 = {
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

const result11 = formatRacesToCrewTimer(testData11);
assert(result11.length === 5, 'All 5 boats included');
// Marathon boats should all have same start time
assert(result11[0]['Event Time'] === '7:45:00 AM', 'First marathon boat at 7:45 AM');
assert(result11[1]['Event Time'] === '7:45:00 AM', 'Second marathon boat at 7:45 AM');
// Semi-marathon boats should have incremental times
assert(result11[2]['Event Time'] === '9:00:00 AM', 'First semi-marathon boat at 9:00 AM');
assert(result11[3]['Event Time'] === '9:00:30 AM', 'Second semi-marathon boat at 9:00:30 AM');
assert(result11[4]['Event Time'] === '9:01:00 AM', 'Third semi-marathon boat at 9:01:00 AM');
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

