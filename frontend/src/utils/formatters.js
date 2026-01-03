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
