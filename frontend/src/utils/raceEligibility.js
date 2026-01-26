/**
 * Race Eligibility Calculation Engine (Frontend)
 * Determines which races a crew is eligible for based on age and gender composition
 */

import { formatAverageAge } from './formatters.js'

/**
 * Calculate age based on date of birth
 * Age is calculated as the age the person will reach during the current year,
 * regardless of whether their birthday has passed yet.
 * 
 * @param {string} dateOfBirth - Date string in YYYY-MM-DD format
 * @param {Date} referenceDate - Reference date for age calculation (defaults to today)
 * @returns {number} Age the person will reach during the reference year
 */
export function calculateAge(dateOfBirth, referenceDate = new Date()) {
  const birthDate = new Date(dateOfBirth);
  // Age is simply the difference in years - no adjustment for birthday
  const age = referenceDate.getFullYear() - birthDate.getFullYear();
  
  return age;
}

/**
 * Determine age category based on age for display purposes
 * @param {number} age - Age in years
 * @returns {string} Age category (j14, j16, j18, senior, master)
 * 
 * Note: J14 can only be cox. J15 competes in J16 races. J17 competes in J18 races.
 */
export function getAgeCategory(age) {
  if (age === 14) {
    return "j14";
  } else if (age === 15 || age === 16) {
    return "j16";
  } else if (age === 17 || age === 18) {
    return "j18";
  } else if (age < 27) {
    return "senior";
  } else {
    return "master";
  }
}

/**
 * Determine master category letter based on average age of crew
 * @param {number} avgAge - Average age of crew members
 * @returns {string} Master category letter (A, B, C, D, E, F, G, H)
 */
export function getMasterCategory(avgAge) {
  if (avgAge < 36) {
    return "A";  // 27-35
  } else if (avgAge < 43) {
    return "B";  // 36-42
  } else if (avgAge < 50) {
    return "C";  // 43-49
  } else if (avgAge < 55) {
    return "D";  // 50-54
  } else if (avgAge < 60) {
    return "E";  // 55-59
  } else if (avgAge < 65) {
    return "F";  // 60-64
  } else if (avgAge < 70) {
    return "G";  // 65-69
  } else {
    return "H";  // 70+
  }
}

/**
 * Analyze crew composition for race eligibility
 * @param {Array} crewMembers - Array of crew member objects with date_of_birth and gender
 * @returns {Object} Crew composition analysis
 */
export function analyzeCrewComposition(crewMembers) {
  if (!crewMembers || crewMembers.length === 0) {
    return {
      crewSize: 0,
      genders: [],
      ages: [],
      ageCategories: [],
      genderCategory: null,
      ageCategory: null,
      eligibleBoatTypes: []
    };
  }
  
  // Calculate ages and determine categories
  // Note: Age and gender categories are based on ROWERS ONLY (excluding coxswains)
  const ages = [];
  const genders = [];
  const ageCategories = [];
  const rowerAges = [];  // Ages of rowers only (for age category calculation)
  const rowerAgeCategories = [];  // Age categories of rowers only
  const rowerGenders = [];  // Genders of rowers only (for gender category calculation)
  
  crewMembers.forEach(member => {
    const age = calculateAge(member.date_of_birth);
    ages.push(age);
    genders.push(member.gender);
    ageCategories.push(getAgeCategory(age));
    
    // Track rower data separately (exclude coxswains from age and gender category calculations)
    const seatType = member.seat_type || 'rower';
    if (seatType === 'rower') {
      rowerAges.push(age);
      rowerAgeCategories.push(getAgeCategory(age));
      rowerGenders.push(member.gender);
    }
  });
  
  // Determine gender category based on ROWERS ONLY (excluding coxswains)
  // Competition rules:
  // - Women's crews: 100% women rowers
  // - Men's crews: More than 50% men rowers
  // - Mixed-gender crews: At least 1 man AND at least 50% women rowers
  
  // Use rowerGenders instead of genders to exclude coxswains
  let genderCategory;
  let maleCount = 0;
  let femaleCount = 0;
  let malePercentage = 0;
  let femalePercentage = 0;
  
  if (rowerGenders.length > 0) {
    maleCount = rowerGenders.filter(g => g === 'M').length;
    femaleCount = rowerGenders.filter(g => g === 'F').length;
    const totalCount = rowerGenders.length;
    malePercentage = (maleCount / totalCount) * 100;
    femalePercentage = (femaleCount / totalCount) * 100;
    
    if (femaleCount === totalCount) {
      // 100% women rowers
      genderCategory = "women";
    } else if (maleCount > 0 && femalePercentage >= 50) {
      // At least 1 man AND at least 50% women rowers -> Mixed
      genderCategory = "mixed";
    } else if (malePercentage > 50) {
      // More than 50% men rowers -> Men's crew
      genderCategory = "men";
    } else {
      // Edge case: shouldn't happen with valid data
      genderCategory = maleCount >= femaleCount ? "men" : "women";
    }
  } else {
    // Fallback if no rowers (shouldn't happen in valid data)
    maleCount = genders.filter(g => g === 'M').length;
    femaleCount = genders.filter(g => g === 'F').length;
    const totalCount = genders.length;
    malePercentage = totalCount > 0 ? (maleCount / totalCount) * 100 : 0;
    femalePercentage = totalCount > 0 ? (femaleCount / totalCount) * 100 : 0;
    genderCategory = femaleCount === genders.length ? "women" : (maleCount >= femaleCount ? "men" : "women");
  }
  
  // Determine age category (most restrictive) based on ROWERS ONLY
  // Priority: master > senior > j18 > j16
  // Use rowerAgeCategories instead of ageCategories to exclude coxswains
  let crewAgeCategory;
  if (rowerAgeCategories.length > 0) {
    if (rowerAgeCategories.includes("master")) {
      crewAgeCategory = "master";
    } else if (rowerAgeCategories.includes("senior")) {
      crewAgeCategory = "senior";
    } else if (rowerAgeCategories.includes("j18")) {
      crewAgeCategory = "j18";
    } else {
      crewAgeCategory = "j16";
    }
  } else {
    // Fallback if no rowers (shouldn't happen in valid data)
    crewAgeCategory = "j16";
  }
  
  // Determine eligible boat types based on crew size
  // Include both sweep and scull variants where applicable
  const crewSize = crewMembers.length;
  const eligibleBoatTypes = [];
  
  if (crewSize === 1) {
    eligibleBoatTypes.push("skiff");
  } else if (crewSize === 4) {
    eligibleBoatTypes.push("4-");   // Coxless four (sweep)
    eligibleBoatTypes.push("4x-");  // Coxless quad (scull)
  } else if (crewSize === 5) {
    eligibleBoatTypes.push("4+");   // Coxed four (sweep)
    eligibleBoatTypes.push("4x+");  // Coxed quad (scull)
  } else if (crewSize === 8 || crewSize === 9) {
    eligibleBoatTypes.push("8+");   // Eight (sweep)
    eligibleBoatTypes.push("8x+");  // Octuple (scull)
  }
  
  // Calculate average age based on ROWERS ONLY (for master category)
  const avgAge = ages.length > 0 ? ages.reduce((sum, age) => sum + age, 0) / ages.length : 0;
  const rowerAvgAge = rowerAges.length > 0 ? rowerAges.reduce((sum, age) => sum + age, 0) / rowerAges.length : 0;
  const masterCategory = crewAgeCategory === "master" ? getMasterCategory(rowerAvgAge) : null;
  
  return {
    crewSize,
    rowerCount: rowerAges.length,  // Number of rowers (excluding cox)
    genders,
    ages,
    ageCategories,
    genderCategory,
    ageCategory: crewAgeCategory,
    masterCategory,
    eligibleBoatTypes,
    minAge: rowerAges.length > 0 ? Math.min(...rowerAges) : 0,
    maxAge: rowerAges.length > 0 ? Math.max(...rowerAges) : 0,
    avgAge: rowerAvgAge,  // Use rower average age (excluding cox)
    // Gender composition details
    maleCount,
    femaleCount,
    malePercentage: Math.round(malePercentage),
    femalePercentage: Math.round(femalePercentage)
  };
}

/**
 * Get races that a crew is eligible for
 * @param {Array} crewMembers - Array of crew member objects
 * @param {Array} availableRaces - Array of available race definitions
 * @returns {Array} Array of eligible race objects
 */
export function getEligibleRaces(crewMembers, availableRaces) {
  const crewAnalysis = analyzeCrewComposition(crewMembers);
  
  console.log('getEligibleRaces - Crew analysis:', crewAnalysis);
  
  if (crewAnalysis.eligibleBoatTypes.length === 0) {
    console.log('getEligibleRaces - No eligible boat types for crew size:', crewAnalysis.crewSize);
    return [];
  }
  
  const eligibleRaces = [];
  
  availableRaces.forEach(race => {
    // Check boat type compatibility
    if (!crewAnalysis.eligibleBoatTypes.includes(race.boat_type)) {
      return;
    }
    
    // Check gender category compatibility
    const raceGender = race.gender_category;
    const crewGender = crewAnalysis.genderCategory;
    
    // Gender matching rules:
    // - "men" race: only all-men crews
    // - "women" race: only all-women crews
    // - "mixed" race: only crews with both genders (truly mixed)
    if (raceGender !== crewGender) {
      console.log(`getEligibleRaces - Gender mismatch: race=${raceGender}, crew=${crewGender} (${race.race_id})`);
      return;
    }
    
    // Check age category compatibility
    const raceAge = race.age_category;
    const crewAge = crewAnalysis.ageCategory;
    
    // Age category rules:
    // - J16 can only compete in j16 races
    // - J18 can only compete in j18 races
    // - Senior can compete in senior races
    // - Master can compete in master races with matching category
    if (raceAge === "j16" && crewAge !== "j16") {
      return;
    }
    if (raceAge === "j18" && crewAge !== "j18") {
      return;
    }
    if (raceAge === "senior" && crewAge !== "senior") {
      return;
    }
    if (raceAge === "master" && crewAge !== "master") {
      return;
    }
    
    // For master races, check if the race has a specific master category
    // Special rule: Category G can race in F (since no G races exist)
    // All other categories must match exactly
    if (crewAge === "master" && race.master_category) {
      const crewMasterCat = crewAnalysis.masterCategory;
      const raceMasterCat = race.master_category;
      
      console.log(`getEligibleRaces - Master category check: crew=${crewMasterCat}, race=${raceMasterCat} (${race.race_id})`);
      
      // Special exception: G can race in F
      if (crewMasterCat === 'G' && raceMasterCat === 'F') {
        // Allow this combination
      } else if (crewMasterCat !== raceMasterCat) {
        // All other categories must match exactly
        console.log(`getEligibleRaces - Category mismatch, race filtered out`);
        return;
      }
    }
    
    eligibleRaces.push(race);
  });
  
  console.log('getEligibleRaces - Final eligible races:', eligibleRaces.length);
  return eligibleRaces;
}

/**
 * Validate that a crew is eligible for a selected race
 * @param {Array} crewMembers - Array of crew member objects
 * @param {Object} selectedRace - Selected race object
 * @returns {Object} Validation result with details
 */
export function validateRaceSelection(crewMembers, selectedRace) {
  const crewAnalysis = analyzeCrewComposition(crewMembers);
  
  // Check crew size
  if (crewAnalysis.eligibleBoatTypes.length === 0) {
    return {
      valid: false,
      reason: `Invalid crew size: ${crewAnalysis.crewSize}. Must be 1, 4, 5, 8, or 9 members.`,
      crewAnalysis
    };
  }
  
  // Check boat type
  if (!crewAnalysis.eligibleBoatTypes.includes(selectedRace.boat_type)) {
    return {
      valid: false,
      reason: `Boat type '${selectedRace.boat_type}' not compatible with crew size ${crewAnalysis.crewSize}`,
      crewAnalysis
    };
  }
  
  // Check gender category
  const raceGender = selectedRace.gender_category;
  const crewGender = crewAnalysis.genderCategory;
  
  // Strict gender matching: race gender must exactly match crew gender
  if (raceGender !== crewGender) {
    const genderLabels = {
      'men': 'all men',
      'women': 'all women',
      'mixed': 'mixed gender (both men and women)'
    };
    return {
      valid: false,
      reason: `Gender mismatch: Race requires ${genderLabels[raceGender] || raceGender} but crew is ${genderLabels[crewGender] || crewGender}`,
      crewAnalysis
    };
  }
  
  // Check age category
  const raceAge = selectedRace.age_category;
  const crewAge = crewAnalysis.ageCategory;
  
  if (raceAge === "j16" && crewAge !== "j16") {
    return {
      valid: false,
      reason: `Age category mismatch: J16 race requires crew members aged 15-16`,
      crewAnalysis
    };
  }
  if (raceAge === "j18" && crewAge !== "j18") {
    return {
      valid: false,
      reason: `Age category mismatch: J18 race requires crew members aged 17-18`,
      crewAnalysis
    };
  }
  if (raceAge === "senior" && crewAge !== "senior") {
    return {
      valid: false,
      reason: `Age category mismatch: Senior race requires crew members aged 19-26`,
      crewAnalysis
    };
  }
  if (raceAge === "master" && crewAge !== "master") {
    return {
      valid: false,
      reason: `Age category mismatch: Master race requires crew members aged 27+`,
      crewAnalysis
    };
  }
  
  // For master races with specific categories, validate category matching
  // Special rule: Category G can race in F (since no G races exist)
  // All other categories must match exactly
  if (raceAge === "master" && selectedRace.master_category) {
    const crewMasterCat = crewAnalysis.masterCategory;
    const raceMasterCat = selectedRace.master_category;
    
    // Special exception: G can race in F
    if (crewMasterCat === 'G' && raceMasterCat === 'F') {
      // Allow this combination
    } else if (crewMasterCat !== raceMasterCat) {
      return {
        valid: false,
        reason: `Master category mismatch: Category ${crewMasterCat} crew must race in category ${crewMasterCat} (or F if category G)`,
        crewAnalysis
      };
    }
  }
  
  return {
    valid: true,
    reason: 'Crew is eligible for this race',
    crewAnalysis
  };
}

/**
 * Boat type requirements for reference
 */
export const BOAT_TYPE_REQUIREMENTS = {
  'skiff': {
    crewSize: 1,
    description: 'Single sculler'
  },
  '4-': {
    crewSize: 4,
    description: 'Four without coxswain'
  },
  '4+': {
    crewSize: 5,
    description: 'Four with coxswain'
  },
  '8+': {
    crewSize: [8, 9],
    description: 'Eight with coxswain'
  }
};

/**
 * Get human-readable description of crew composition
 * @param {Object} crewAnalysis - Result from analyzeCrewComposition
 * @returns {string} Human-readable description
 */
export function getCrewDescription(crewAnalysis) {
  if (crewAnalysis.crewSize === 0) {
    return "No crew members";
  }
  
  const { rowerCount, genderCategory, ageCategory, masterCategory, avgAge } = crewAnalysis;
  const masterCat = masterCategory ? ` ${masterCategory}` : '';
  return `${rowerCount} ${genderCategory} ${ageCategory}${masterCat} (avg age: ${formatAverageAge(avgAge)})`;
}

/**
 * Get race difficulty/category display
 * @param {Object} race - Race object
 * @returns {string} Display string for race category
 */
export function getRaceDisplay(race) {
  const distance = race.event_type;
  const boat = race.boat_type;
  const gender = race.gender_category;
  const age = race.age_category;
  const masterCat = race.master_category ? ` ${race.master_category}` : '';
  
  return `${distance} ${gender} ${age}${masterCat} ${boat}`;
}
