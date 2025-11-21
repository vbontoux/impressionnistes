/**
 * Race Eligibility Tests
 * Verify gender category logic matches requirements
 */
import { analyzeCrewComposition } from './raceEligibility.js';

// Test helper to create crew member
function createCrewMember(gender, age) {
  const birthYear = new Date().getFullYear() - age;
  return {
    gender,
    date_of_birth: `${birthYear}-01-01`
  };
}

console.log('=== Testing Gender Category Logic ===\n');

// Test 1: 100% Women -> Women's crew
console.log('Test 1: 100% Women (4 women)');
const test1 = analyzeCrewComposition([
  createCrewMember('F', 25),
  createCrewMember('F', 26),
  createCrewMember('F', 27),
  createCrewMember('F', 28)
]);
console.log(`Result: ${test1.genderCategory}`);
console.log(`Expected: women`);
console.log(`✓ PASS: ${test1.genderCategory === 'women'}\n`);

// Test 2: More than 50% men -> Men's crew
console.log('Test 2: More than 50% men (3 men, 1 woman = 75% men)');
const test2 = analyzeCrewComposition([
  createCrewMember('M', 25),
  createCrewMember('M', 26),
  createCrewMember('M', 27),
  createCrewMember('F', 28)
]);
console.log(`Result: ${test2.genderCategory}`);
console.log(`Male %: ${test2.malePercentage}%, Female %: ${test2.femalePercentage}%`);
console.log(`Expected: men`);
console.log(`✓ PASS: ${test2.genderCategory === 'men'}\n`);

// Test 3: At least 1 man AND at least 50% women -> Mixed crew
console.log('Test 3: Mixed (2 men, 2 women = 50% women)');
const test3 = analyzeCrewComposition([
  createCrewMember('M', 25),
  createCrewMember('M', 26),
  createCrewMember('F', 27),
  createCrewMember('F', 28)
]);
console.log(`Result: ${test3.genderCategory}`);
console.log(`Male %: ${test3.malePercentage}%, Female %: ${test3.femalePercentage}%`);
console.log(`Expected: mixed`);
console.log(`✓ PASS: ${test3.genderCategory === 'mixed'}\n`);

// Test 4: At least 1 man AND more than 50% women -> Mixed crew
console.log('Test 4: Mixed (1 man, 3 women = 75% women)');
const test4 = analyzeCrewComposition([
  createCrewMember('M', 25),
  createCrewMember('F', 26),
  createCrewMember('F', 27),
  createCrewMember('F', 28)
]);
console.log(`Result: ${test4.genderCategory}`);
console.log(`Male %: ${test4.malePercentage}%, Female %: ${test4.femalePercentage}%`);
console.log(`Expected: mixed`);
console.log(`✓ PASS: ${test4.genderCategory === 'mixed'}\n`);

// Test 5: 100% Men -> Men's crew
console.log('Test 5: 100% Men (4 men)');
const test5 = analyzeCrewComposition([
  createCrewMember('M', 25),
  createCrewMember('M', 26),
  createCrewMember('M', 27),
  createCrewMember('M', 28)
]);
console.log(`Result: ${test5.genderCategory}`);
console.log(`Expected: men`);
console.log(`✓ PASS: ${test5.genderCategory === 'men'}\n`);

// Test 6: Edge case - 8+ boat with mixed crew
console.log('Test 6: 8+ boat (5 men, 4 women = 55.5% men)');
const test6 = analyzeCrewComposition([
  createCrewMember('M', 25),
  createCrewMember('M', 26),
  createCrewMember('M', 27),
  createCrewMember('M', 28),
  createCrewMember('M', 29),
  createCrewMember('F', 25),
  createCrewMember('F', 26),
  createCrewMember('F', 27),
  createCrewMember('F', 28)
]);
console.log(`Result: ${test6.genderCategory}`);
console.log(`Male %: ${test6.malePercentage}%, Female %: ${test6.femalePercentage}%`);
console.log(`Expected: men (more than 50% men)`);
console.log(`✓ PASS: ${test6.genderCategory === 'men'}\n`);

// Test 7: Edge case - 8+ boat with exactly 50% women and at least 1 man
console.log('Test 7: 8+ boat (4 men, 4 women = 50% women)');
const test7 = analyzeCrewComposition([
  createCrewMember('M', 25),
  createCrewMember('M', 26),
  createCrewMember('M', 27),
  createCrewMember('M', 28),
  createCrewMember('F', 25),
  createCrewMember('F', 26),
  createCrewMember('F', 27),
  createCrewMember('F', 28)
]);
console.log(`Result: ${test7.genderCategory}`);
console.log(`Male %: ${test7.malePercentage}%, Female %: ${test7.femalePercentage}%`);
console.log(`Expected: mixed (at least 1 man AND at least 50% women)`);
console.log(`✓ PASS: ${test7.genderCategory === 'mixed'}\n`);

console.log('=== Summary ===');
console.log('Gender Category Rules:');
console.log('- Women\'s crews: 100% women');
console.log('- Men\'s crews: More than 50% men');
console.log('- Mixed-gender crews: At least 1 man AND at least 50% women');
