/**
 * Race Eligibility Calculation Engine (Frontend)
 * Determines which races a crew is eligible for based on age and gender composition
 */

/**
 * Calculate age based on date of birth
 * @param {string} dateOfBirth - Date string in YYYY-MM-DD format
 * @param {Date} referenceDate - Reference date for age calculation (defaults to today)
 * @returns {number} Age in years
 */
export function calculateAge(dateOfBirth, referenceDate = new Date()) {
  const birthDate = new Date(dateOfBirth);
  let age = referenceDate.getFullYear() - birthDate.getFullYear();
  
  // Adjust if birthday hasn't occurred this year
  const monthDiff = referenceDate.getMonth() - birthDate.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && referenceDate.getDate() < birthDate.getDate())) {
    age--;
  }
  
  return age;
}

/**
 * Determine age category based on age
 * @param {number} age - Age in years
 * @returns {string} Age category (j16, j18, senior, master)
 */
export function getAgeCategory(age) {
  if (age <= 16) {
    return "j16";
  } else if (age <= 18) {
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
  const ages = [];
  const genders = [];
  const ageCategories = [];
  
  crewMembers.forEach(member => {
    const age = calculateAge(member.date_of_birth);
    ages.push(age);
    genders.push(member.gender);
    ageCategories.push(getAgeCategory(age));
  });
  
  // Determine gender category
  const uniqueGenders = new Set(genders);
  let genderCategory;
  if (uniqueGenders.size === 1) {
    genderCategory = genders[0] === "M" ? "men" : "women";
  } else {
    genderCategory = "mixed";
  }
  
  // Determine age category (most restrictive)
  // Priority: master > senior > j18 > j16
  let crewAgeCategory;
  if (ageCategories.includes("master")) {
    crewAgeCategory = "master";
  } else if (ageCategories.includes("senior")) {
    crewAgeCategory = "senior";
  } else if (ageCategories.includes("j18")) {
    crewAgeCategory = "j18";
  } else {
    crewAgeCategory = "j16";
  }
  
  // Determine eligible boat types based on crew size
  const crewSize = crewMembers.length;
  const eligibleBoatTypes = [];
  
  if (crewSize === 1) {
    eligibleBoatTypes.push("skiff");
  } else if (crewSize === 4) {
    eligibleBoatTypes.push("4-");
  } else if (crewSize === 5) {
    eligibleBoatTypes.push("4+");
  } else if (crewSize === 8 || crewSize === 9) {
    eligibleBoatTypes.push("8+");
  }
  
  const avgAge = ages.length > 0 ? ages.reduce((sum, age) => sum + age, 0) / ages.length : 0;
  const masterCategory = crewAgeCategory === "master" ? getMasterCategory(avgAge) : null;
  
  return {
    crewSize,
    genders,
    ages,
    ageCategories,
    genderCategory,
    ageCategory: crewAgeCategory,
    masterCategory,
    eligibleBoatTypes,
    minAge: ages.length > 0 ? Math.min(...ages) : 0,
    maxAge: ages.length > 0 ? Math.max(...ages) : 0,
    avgAge
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
    
    // Mixed races accept any gender composition
    // Gender-specific races only accept that gender or mixed crews
    if (raceGender !== "mixed" && raceGender !== crewGender && crewGender !== "mixed") {
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
    if (crewAge === "master" && race.master_category) {
      const crewMasterCat = crewAnalysis.masterCategory;
      const raceMasterCat = race.master_category;
      console.log(`getEligibleRaces - Master category check: crew=${crewMasterCat}, race=${raceMasterCat} (${race.race_id})`);
      if (crewMasterCat !== raceMasterCat) {
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
  
  if (raceGender !== "mixed" && raceGender !== crewGender && crewGender !== "mixed") {
    return {
      valid: false,
      reason: `Gender mismatch: Race requires '${raceGender}' but crew is '${crewGender}'`,
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
  
  const { crewSize, genderCategory, ageCategory, masterCategory, avgAge } = crewAnalysis;
  const masterCat = masterCategory ? ` ${masterCategory}` : '';
  return `${crewSize} ${genderCategory} ${ageCategory}${masterCat} (avg age: ${Math.round(avgAge)})`;
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
