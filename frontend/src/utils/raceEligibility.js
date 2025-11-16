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
 * @returns {string} Age category
 */
export function getAgeCategory(age) {
  if (age < 18) {
    return "youth";
  } else if (age < 27) {
    return "senior";
  } else {
    return "master";
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
  
  // Determine age category (most restrictive - if any master, then master)
  let crewAgeCategory;
  if (ageCategories.includes("master")) {
    crewAgeCategory = "master";
  } else if (ageCategories.includes("senior")) {
    crewAgeCategory = "senior";
  } else {
    crewAgeCategory = "youth";
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
  
  return {
    crewSize,
    genders,
    ages,
    ageCategories,
    genderCategory,
    ageCategory: crewAgeCategory,
    eligibleBoatTypes,
    minAge: ages.length > 0 ? Math.min(...ages) : 0,
    maxAge: ages.length > 0 ? Math.max(...ages) : 0,
    avgAge: ages.length > 0 ? ages.reduce((sum, age) => sum + age, 0) / ages.length : 0
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
  
  if (crewAnalysis.eligibleBoatTypes.length === 0) {
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
    // - Youth can only compete in youth races
    // - Senior can compete in senior or master races
    // - Master can compete in master races
    if (raceAge === "youth" && crewAge !== "youth") {
      return;
    }
    if (raceAge === "senior" && !["senior", "master"].includes(crewAge)) {
      return;
    }
    if (raceAge === "master" && crewAge !== "master") {
      return;
    }
    
    eligibleRaces.push(race);
  });
  
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
  
  if (raceAge === "youth" && crewAge !== "youth") {
    return {
      valid: false,
      reason: `Age category mismatch: Youth race requires all youth crew members`,
      crewAnalysis
    };
  }
  if (raceAge === "senior" && !["senior", "master"].includes(crewAge)) {
    return {
      valid: false,
      reason: `Age category mismatch: Senior race not available for ${crewAge} crew`,
      crewAnalysis
    };
  }
  if (raceAge === "master" && crewAge !== "master") {
    return {
      valid: false,
      reason: `Age category mismatch: Master race requires at least one master crew member`,
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
  
  const { crewSize, genderCategory, ageCategory, avgAge } = crewAnalysis;
  return `${crewSize} ${genderCategory} ${ageCategory} (avg age: ${Math.round(avgAge)})`;
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
  
  return `${distance} ${gender} ${age} ${boat}`;
}
