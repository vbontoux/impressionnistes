/**
 * Shared utility functions for export formatters
 */

/**
 * Escape special characters in CSV fields
 * Handles commas, quotes, and newlines by wrapping in quotes and escaping existing quotes
 * @param {any} value - The value to escape
 * @returns {string} - Escaped value safe for CSV
 */
export function escapeCSVField(value) {
  if (value == null || value === '') {
    return ''
  }
  
  const stringValue = String(value)
  
  // If the value contains comma, quote, or newline, wrap it in quotes
  if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
    // Escape existing quotes by doubling them
    return `"${stringValue.replace(/"/g, '""')}"`
  }
  
  return stringValue
}

/**
 * Convert boat type code to display format
 * @param {string} boatType - The boat type code (e.g., 'skiff', '4+')
 * @returns {string} - Display format (e.g., '1X', '4+')
 */
export function getBoatTypeDisplay(boatType) {
  const typeMap = {
    'skiff': '1X',
    '4-': '4-',
    '4+': '4+',
    '4x-': '4X-',
    '4x+': '4X+',
    '8+': '8+',
    '8x+': '8X+'
  }
  return typeMap[boatType] || boatType
}

/**
 * Trigger browser download of a file
 * @param {Blob} blob - The file content as a Blob
 * @param {string} filename - The filename including extension
 */
export function downloadFile(blob, filename) {
  const link = document.createElement('a')
  
  if (link.download !== undefined) {
    // Create a link to the file
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    // Clean up the URL object
    setTimeout(() => URL.revokeObjectURL(url), 100)
  }
}

/**
 * Format a date for use in filenames
 * Converts ISO date to a filename-safe format: YYYYMMDD-HHMMSS
 * @param {Date} date - The date to format (defaults to now)
 * @returns {string} - Formatted date string
 */
export function formatDateForFilename(date = new Date()) {
  return date.toISOString().replace(/[:.]/g, '-').slice(0, -5)
}

/**
 * Format a date for display
 * Converts ISO date string to a human-readable format
 * @param {string} isoDate - ISO date string
 * @param {string} locale - Locale for formatting (defaults to 'en-US')
 * @returns {string} - Formatted date string
 */
export function formatDateForDisplay(isoDate, locale = 'en-US') {
  if (!isoDate) {
    return ''
  }
  
  try {
    const date = new Date(isoDate)
    return date.toLocaleDateString(locale, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch (error) {
    console.error('Error formatting date:', error)
    return isoDate
  }
}

/**
 * Format a datetime for display
 * Converts ISO datetime string to a human-readable format
 * @param {string} isoDateTime - ISO datetime string
 * @param {string} locale - Locale for formatting (defaults to 'en-US')
 * @returns {string} - Formatted datetime string
 */
export function formatDateTimeForDisplay(isoDateTime, locale = 'en-US') {
  if (!isoDateTime) {
    return ''
  }
  
  try {
    const date = new Date(isoDateTime)
    return date.toLocaleString(locale, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    console.error('Error formatting datetime:', error)
    return isoDateTime
  }
}

/**
 * Format boolean value as Yes/No
 * @param {boolean} value - The boolean value
 * @returns {string} - "Yes" or "No"
 */
export function formatBoolean(value) {
  return value ? 'Yes' : 'No'
}
