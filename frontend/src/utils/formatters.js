/**
 * Formatting utilities for display purposes
 */

/**
 * Format average age for display
 * Uses floor rounding as per business requirements
 * @param {number} avgAge - Average age (can be float)
 * @returns {number} - Floored integer age
 */
export function formatAverageAge(avgAge) {
  if (avgAge === null || avgAge === undefined || isNaN(avgAge)) {
    return 0
  }
  return Math.floor(avgAge)
}

/**
 * Format date for display
 * @param {string} dateString - ISO date string
 * @returns {string} - Formatted date
 */
export function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString(undefined, { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

/**
 * Translate short_name from English to French
 * Only translates gender markers: W (woman) → F (femme), X (mixed) → M (mixte), M (men) → H (homme)
 * Age category markers (M for Master, S for Senior, J for Junior) remain unchanged
 * @param {string} shortName - The short name in English (e.g., "MW4X+Y")
 * @returns {string} - Translated short name (e.g., "MF4X+Y")
 */
function translateShortNameToFrench(shortName) {
  if (!shortName) return ''
  
  // Short name format: [AgeCategory][Gender][BoatType]
  // Examples: MW4X+Y (Master Women), SH8+ (Senior Men), J16F2X (Junior 16 Women)
  
  let translated = ''
  
  for (let i = 0; i < shortName.length; i++) {
    const char = shortName[i]
    const prevChar = i > 0 ? shortName[i - 1] : ''
    
    // Check if this is a gender marker (comes after age category or at position 1)
    const isGenderPosition = (
      // Position 1 (after single letter age category like M, S)
      (i === 1 && /[MSJX]/.test(prevChar)) ||
      // After J16 or J18
      (i === 3 && shortName.substring(0, 3).match(/J1[68]/))
    )
    
    if (isGenderPosition) {
      // Translate gender markers
      if (char === 'W') {
        translated += 'F' // Women → Femme
      } else if (char === 'X') {
        translated += 'M' // Mixed → Mixte
      } else if (char === 'M') {
        translated += 'H' // Men → Homme
      } else {
        translated += char
      }
    } else {
      // Keep all other characters unchanged (age category, boat type, etc.)
      translated += char
    }
  }
  
  return translated
}

/**
 * Get translated race name (short version)
 * Uses short_name if available, translates gender markers to French
 * Falls back to full name translation if short_name not available
 * @param {Object} race - Race object with name and/or short_name
 * @param {Function} t - i18n translation function
 * @returns {string|null} - Translated race name or null if no race
 */
export function formatRaceName(race, t) {
  if (!race) return null
  
  // If we have a short_name, translate it to French
  if (race.short_name) {
    return translateShortNameToFrench(race.short_name)
  }
  
  // Fall back to full name translation
  if (race.name) {
    const nameTranslationKey = `races.${race.name}`
    const nameTranslated = t(nameTranslationKey)
    
    // If name has a translation, use it
    if (nameTranslated !== nameTranslationKey) {
      return nameTranslated
    }
    
    // No translation found, return original name
    return race.name
  }
  
  return null
}
