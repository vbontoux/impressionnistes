/**
 * CrewTimer Formatter Tests
 * Test CrewTimer transformations and formatting
 */
import { 
  formatRacesToCrewTimer, 
  formatSemiMarathonRaceName,
  calculateAverageAge,
  getStrokeSeatName
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
    config: { competition_date: '2025-05-01' },
    races: [
      { race_id: 'R1', name: 'Test Race', distance: 21, event_type: '21km', boat_type: '4+' }
    ],
    boats: [
      { boat_registration_id: 'b1', race_id: 'R1', registration_status: 'complete', forfait: false, seats: [] },
      { boat_registration_id: 'b2', race_id: 'R1', registration_status: 'paid', forfait: false, seats: [] },
      { boat_registration_id: 'b3', race_id: 'R1', registration_status: 'free', forfait: false, seats: [] },
      { boat_registration_id: 'b4', race_id: 'R1', registration_status: 'incomplete', forfait: false, seats: [] },
      { boat_registration_id: 'b5', race_id: 'R1', registration_status: 'complete', forfait: true, seats: [] }
    ],
    crew_members: [],
    team_managers: []
  }
};

const result1 = formatRacesToCrewTimer(testData1);
assert(result1.length === 3, 'Only complete/paid/free boats included');
assert(result1.every(r => r.Bow >= 1 && r.Bow <= 3), 'Bow numbers 1-3 for 3 boats');
console.log('');

// Test 2: Race sorting (marathon before semi-marathon)
console.log('Test 2: Race sorting (marathon before semi-marathon)');
const testData2 = {
  success: true,
  data: {
    config: { competition_date: '2025-05-01' },
    races: [
      { race_id: 'SM1', name: 'Semi Race 1', distance: 21, event_type: '21km', boat_type: '4+' },
      { race_id: 'M1', name: 'Marathon Race 1', distance: 42, event_type: '42km', boat_type: 'skiff' },
      { race_id: 'SM2', name: 'Semi Race 2', distance: 21, event_type: '21km', boat_type: '8+' },
      { race_id: 'M2', name: 'Marathon Race 2', distance: 42, event_type: '42km', boat_type: '4+' }
    ],
    boats: [
      { boat_registration_id: 'b1', race_id: 'SM1', registration_status: 'complete', forfait: false, seats: [] },
      { boat_registration_id: 'b2', race_id: 'M1', registration_status: 'complete', forfait: false, seats: [] },
      { boat_registration_id: 'b3', race_id: 'SM2', registration_status: 'complete', forfait: false, seats: [] },
      { boat_registration_id: 'b4', race_id: 'M2', registration_status: 'complete', forfait: false, seats: [] }
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
    config: { competition_date: '2025-05-01' },
    races: [
      { race_id: 'R1', name: 'Race 1', distance: 21, event_type: '21km', boat_type: '4+' },
      { race_id: 'R2', name: 'Race 2', distance: 21, event_type: '21km', boat_type: '8+' }
    ],
    boats: [
      { boat_registration_id: 'b1', race_id: 'R1', registration_status: 'complete', forfait: false, seats: [] },
      { boat_registration_id: 'b2', race_id: 'R1', registration_status: 'complete', forfait: false, seats: [] },
      { boat_registration_id: 'b3', race_id: 'R1', registration_status: 'complete', forfait: false, seats: [] },
      { boat_registration_id: 'b4', race_id: 'R2', registration_status: 'complete', forfait: false, seats: [] },
      { boat_registration_id: 'b5', race_id: 'R2', registration_status: 'complete', forfait: false, seats: [] }
    ],
    crew_members: [],
    team_managers: []
  }
};

const result3 = formatRacesToCrewTimer(testData3);
const r1Boats = result3.filter(r => r.Bow <= 3);
const r2Boats = result3.filter(r => r.Bow > 3);
assert(r1Boats.every(r => r['Event Num'] === 1), 'All Race 1 boats have Event Num 1');
assert(r2Boats.every(r => r['Event Num'] === 2), 'All Race 2 boats have Event Num 2');
console.log('');

// Test 4: Bow numbering (global sequential)
console.log('Test 4: Bow numbering (global sequential)');
const testData4 = {
  success: true,
  data: {
    config: { competition_date: '2025-05-01' },
    races: [
      { race_id: 'R1', name: 'Race 1', distance: 21, event_type: '21km', boat_type: '4+' },
      { race_id: 'R2', name: 'Race 2', distance: 21, event_type: '21km', boat_type: '8+' }
    ],
    boats: [
      { boat_registration_id: 'b1', race_id: 'R1', registration_status: 'complete', forfait: false, seats: [] },
      { boat_registration_id: 'b2', race_id: 'R1', registration_status: 'complete', forfait: false, seats: [] },
      { boat_registration_id: 'b3', race_id: 'R2', registration_status: 'complete', forfait: false, seats: [] },
      { boat_registration_id: 'b4', race_id: 'R2', registration_status: 'complete', forfait: false, seats: [] }
    ],
    crew_members: [],
    team_managers: []
  }
};

const result4 = formatRacesToCrewTimer(testData4);
const bowNumbers = result4.map(r => r.Bow);
assert(bowNumbers.length === 4, 'Four boats total');
assert(bowNumbers[0] === 1, 'First bow is 1');
assert(bowNumbers[1] === 2, 'Second bow is 2');
assert(bowNumbers[2] === 3, 'Third bow is 3');
assert(bowNumbers[3] === 4, 'Fourth bow is 4');
assert(JSON.stringify(bowNumbers) === JSON.stringify([1, 2, 3, 4]), 'Bow numbers are sequential');
console.log('');

// Test 5: Semi-marathon race name formatting
console.log('Test 5: Semi-marathon race name formatting');
const race1 = {
  name: 'WOMEN-JUNIOR J16-COXED SWEEP FOUR',
  boat_type: '4+',
  age_category: 'j16',
  gender_category: 'women'
};
const formatted1 = formatSemiMarathonRaceName(race1);
assert(formatted1 === '4+ J16 WOMAN', 'Formats women j16 4+ correctly');

const race2 = {
  name: 'MEN-SENIOR-SKIFF',
  boat_type: 'skiff',
  age_category: 'senior',
  gender_category: 'men'
};
const formatted2 = formatSemiMarathonRaceName(race2);
assert(formatted2 === '1X SENIOR MAN', 'Formats men senior skiff correctly');

const race3 = {
  name: 'MIXED-MASTER-EIGHT',
  boat_type: '8+',
  age_category: 'master',
  gender_category: 'mixed'
};
const formatted3 = formatSemiMarathonRaceName(race3);
assert(formatted3 === '8+ MASTER MIXED', 'Formats mixed master 8+ correctly');
console.log('');

// Test 6: Marathon race name unchanged
console.log('Test 6: Marathon race name unchanged');
const testData6 = {
  success: true,
  data: {
    config: { competition_date: '2025-05-01' },
    races: [
      { race_id: 'M1', name: '1X SENIOR MAN', distance: 42, event_type: '42km', boat_type: 'skiff' }
    ],
    boats: [
      { boat_registration_id: 'b1', race_id: 'M1', registration_status: 'complete', forfait: false, seats: [] }
    ],
    crew_members: [],
    team_managers: []
  }
};

const result6 = formatRacesToCrewTimer(testData6);
assert(result6[0].Event === '1X SENIOR MAN', 'Marathon race name unchanged');
console.log('');

// Test 7: Gender mapping (MAN/WOMAN/MIXED)
console.log('Test 7: Gender mapping (MAN/WOMAN/MIXED)');
const raceWomen = { name: 'Test', boat_type: '4+', age_category: 'senior', gender_category: 'women' };
const raceMan = { name: 'Test', boat_type: '4+', age_category: 'senior', gender_category: 'men' };
const raceMixed = { name: 'Test', boat_type: '4+', age_category: 'senior', gender_category: 'mixed' };

assert(formatSemiMarathonRaceName(raceWomen).includes('WOMAN'), 'women -> WOMAN');
assert(formatSemiMarathonRaceName(raceMan).includes('MAN'), 'men -> MAN');
assert(formatSemiMarathonRaceName(raceMixed).includes('MIXED'), 'mixed -> MIXED');
console.log('');

// Test 8: Yolette detection (Y marker)
console.log('Test 8: Yolette detection (Y marker)');
const raceYolette = {
  name: 'WOMEN-JUNIOR J16-YOLETTE-COXED SWEEP FOUR',
  boat_type: '4+',
  age_category: 'j16',
  gender_category: 'women'
};
const formattedYolette = formatSemiMarathonRaceName(raceYolette);
assert(formattedYolette.includes('Y'), 'Yolette race includes Y marker');
assert(formattedYolette === '4+ Y J16 WOMAN', 'Yolette formatted correctly');

const raceNoYolette = {
  name: 'WOMEN-JUNIOR J16-COXED SWEEP FOUR',
  boat_type: '4+',
  age_category: 'j16',
  gender_category: 'women'
};
const formattedNoYolette = formatSemiMarathonRaceName(raceNoYolette);
assert(!formattedNoYolette.includes('Y '), 'Non-yolette race has no Y marker');
console.log('');

// Test 9: Stroke seat extraction
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

// Test 10: Average age calculation
console.log('Test 10: Average age calculation');
const crewMembers1 = [
  { date_of_birth: '1990-01-01' },
  { date_of_birth: '1992-06-15' },
  { date_of_birth: '1988-12-31' },
  { date_of_birth: '1991-03-20' }
];
const avgAge1 = calculateAverageAge(crewMembers1, '2025-05-01');
// Ages: 35, 33, 37, 34 -> Average: 34.75 -> Rounded: 35
assert(avgAge1 === 35, 'Average age calculated and rounded correctly');

// Test with empty crew
const avgAge2 = calculateAverageAge([], '2025-05-01');
assert(avgAge2 === 0, 'Empty crew returns 0');

// Test with missing dates
const crewMembers3 = [
  { date_of_birth: '1990-01-01' },
  { date_of_birth: null },
  { date_of_birth: '1992-06-15' }
];
const avgAge3 = calculateAverageAge(crewMembers3, '2025-05-01');
// Only valid dates: 35, 33 -> Average: 34
assert(avgAge3 === 34, 'Handles missing dates correctly');
console.log('');

// Test 11: Empty dataset handling
console.log('Test 11: Empty dataset handling');
const testData11 = {
  success: true,
  data: {
    config: { competition_date: '2025-05-01' },
    races: [],
    boats: [],
    crew_members: [],
    team_managers: []
  }
};

const result11 = formatRacesToCrewTimer(testData11);
assert(result11.length === 0, 'Empty dataset returns empty array');
console.log('');

// Test 12: Invalid data format error handling
console.log('Test 12: Invalid data format error handling');
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

// Test 13: Complete integration test
console.log('Test 13: Complete integration test');
const testData13 = {
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
      { crew_member_id: 'crew-1', first_name: 'John', last_name: 'Doe', date_of_birth: '1990-01-01' },
      { crew_member_id: 'crew-2', first_name: 'Jane', last_name: 'Smith', date_of_birth: '2009-01-01' },
      { crew_member_id: 'crew-3', first_name: 'Bob', last_name: 'Jones', date_of_birth: '2009-06-15' },
      { crew_member_id: 'crew-4', first_name: 'Alice', last_name: 'Brown', date_of_birth: '2008-12-31' },
      { crew_member_id: 'crew-5', first_name: 'Charlie', last_name: 'Wilson', date_of_birth: '2009-03-20' },
      { crew_member_id: 'crew-6', first_name: 'Eve', last_name: 'Cox', date_of_birth: '2010-01-01' }
    ],
    team_managers: [
      { user_id: 'tm1', club_affiliation: 'RCPM', email: 'tm1@example.com' },
      { user_id: 'tm2', club_affiliation: 'Club Elite', email: 'tm2@example.com' }
    ]
  }
};

const result13 = formatRacesToCrewTimer(testData13);
assert(result13.length === 2, 'Two boats in output');
assert(result13[0]['Event Num'] === 1, 'Marathon is Event 1');
assert(result13[1]['Event Num'] === 2, 'Semi-marathon is Event 2');
assert(result13[0].Bow === 1, 'First boat is Bow 1');
assert(result13[1].Bow === 2, 'Second boat is Bow 2');
assert(result13[0].Event === '1X SENIOR MAN', 'Marathon name unchanged');
assert(result13[1].Event === '4+ J16 WOMAN', 'Semi-marathon name formatted');
assert(result13[0].Crew === 'RCPM', 'First boat club correct');
assert(result13[1].Crew === 'Club Elite', 'Second boat club correct');
assert(result13[0].Stroke === 'Doe', 'First boat stroke correct');
assert(result13[1].Stroke === 'Wilson', 'Second boat stroke correct (highest rower)');
assert(result13[0].Age === 35, 'First boat age correct');
assert(result13[1].Age === 16, 'Second boat age correct (average of rowers)');
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
