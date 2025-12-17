/**
 * Date formatting utilities
 */

/**
 * Format a date string (YYYY-MM-DD) to a localized display format
 * @param {string} dateString - Date in YYYY-MM-DD format
 * @param {string} locale - Locale code (e.g., 'fr', 'en')
 * @returns {string} Formatted date string
 */
export function formatDate(dateString, locale = 'fr') {
  if (!dateString) return ''
  
  try {
    const date = new Date(dateString)
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      return dateString
    }
    
    const options = { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    }
    
    return date.toLocaleDateString(locale === 'fr' ? 'fr-FR' : 'en-US', options)
  } catch (error) {
    console.error('Error formatting date:', error)
    return dateString
  }
}

/**
 * Format a date string to short format (e.g., "19 mars 2025")
 * @param {string} dateString - Date in YYYY-MM-DD format
 * @param {string} locale - Locale code (e.g., 'fr', 'en')
 * @returns {string} Formatted date string
 */
export function formatDateShort(dateString, locale = 'fr') {
  if (!dateString) return ''
  
  try {
    const date = new Date(dateString)
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      return dateString
    }
    
    const options = { 
      month: 'long', 
      day: 'numeric',
      year: 'numeric'
    }
    
    return date.toLocaleDateString(locale === 'fr' ? 'fr-FR' : 'en-US', options)
  } catch (error) {
    console.error('Error formatting date:', error)
    return dateString
  }
}
