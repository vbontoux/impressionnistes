import { ref, computed } from 'vue'

/**
 * Composable for table sorting functionality
 * Handles different data types including alphanumeric sorting (e.g., boat numbers)
 * 
 * @param {Array} data - The data array to sort
 * @param {String} initialSortField - Initial field to sort by
 * @param {String} initialSortDirection - Initial sort direction ('asc' or 'desc')
 * @returns {Object} Sorting state and methods
 */
export function useTableSort(data, initialSortField = '', initialSortDirection = 'asc') {
  const sortField = ref(initialSortField)
  const sortDirection = ref(initialSortDirection)

  /**
   * Parse boat number format (e.g., "M.1.1", "SM.2.3")
   * @param {String} num - Boat number string
   * @returns {Object} Parsed components { prefix, order, seq }
   */
  const parseBoatNumber = (num) => {
    if (!num || typeof num !== 'string') {
      return { prefix: '', order: 0, seq: 0 }
    }
    
    const parts = num.split('.')
    if (parts.length !== 3) {
      return { prefix: '', order: 0, seq: 0 }
    }
    
    return {
      prefix: parts[0],
      order: parseInt(parts[1]) || 0,
      seq: parseInt(parts[2]) || 0
    }
  }

  /**
   * Compare two boat numbers with proper alphanumeric sorting
   * @param {String} aNum - First boat number
   * @param {String} bNum - Second boat number
   * @param {String} direction - Sort direction ('asc' or 'desc')
   * @returns {Number} Comparison result (-1, 0, 1)
   */
  const compareBoatNumbers = (aNum, bNum, direction) => {
    const aParsed = parseBoatNumber(aNum)
    const bParsed = parseBoatNumber(bNum)
    
    // Sort by prefix (M before SM)
    if (aParsed.prefix !== bParsed.prefix) {
      const prefixOrder = { 'M': 1, 'SM': 2, 'VM': 3 }
      const aOrder = prefixOrder[aParsed.prefix] || 999
      const bOrder = prefixOrder[bParsed.prefix] || 999
      return direction === 'asc' ? aOrder - bOrder : bOrder - aOrder
    }
    
    // Then by display order
    if (aParsed.order !== bParsed.order) {
      return direction === 'asc' 
        ? aParsed.order - bParsed.order 
        : bParsed.order - aParsed.order
    }
    
    // Finally by sequence
    return direction === 'asc' 
      ? aParsed.seq - bParsed.seq 
      : bParsed.seq - aParsed.seq
  }

  /**
   * Compare two values with type-aware sorting
   * @param {*} aVal - First value
   * @param {*} bVal - Second value
   * @param {String} direction - Sort direction ('asc' or 'desc')
   * @returns {Number} Comparison result (-1, 0, 1)
   */
  const compareValues = (aVal, bVal, direction) => {
    // Handle null/undefined
    if (aVal == null && bVal == null) return 0
    if (aVal == null) return direction === 'asc' ? 1 : -1
    if (bVal == null) return direction === 'asc' ? -1 : 1

    // Handle numbers
    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return direction === 'asc' ? aVal - bVal : bVal - aVal
    }

    // Handle strings (case-insensitive)
    if (typeof aVal === 'string' && typeof bVal === 'string') {
      const aLower = aVal.toLowerCase()
      const bLower = bVal.toLowerCase()
      
      if (aLower < bLower) return direction === 'asc' ? -1 : 1
      if (aLower > bLower) return direction === 'asc' ? 1 : -1
      return 0
    }

    // Handle booleans
    if (typeof aVal === 'boolean' && typeof bVal === 'boolean') {
      if (aVal === bVal) return 0
      return direction === 'asc' 
        ? (aVal ? 1 : -1) 
        : (aVal ? -1 : 1)
    }

    // Default comparison
    if (aVal < bVal) return direction === 'asc' ? -1 : 1
    if (aVal > bVal) return direction === 'asc' ? 1 : -1
    return 0
  }

  /**
   * Sorted data computed property
   */
  const sortedData = computed(() => {
    if (!data.value || !Array.isArray(data.value)) {
      return []
    }

    if (!sortField.value) {
      return data.value
    }

    return [...data.value].sort((a, b) => {
      const aVal = a[sortField.value]
      const bVal = b[sortField.value]

      // Special handling for boat_number field
      if (sortField.value === 'boat_number') {
        return compareBoatNumbers(aVal, bVal, sortDirection.value)
      }

      // Default type-aware comparison
      return compareValues(aVal, bVal, sortDirection.value)
    })
  })

  /**
   * Toggle sort for a field
   * If clicking the same field, toggle direction
   * If clicking a new field, set to ascending
   * @param {String} field - Field name to sort by
   */
  const sortBy = (field) => {
    if (sortField.value === field) {
      // Toggle direction
      sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
    } else {
      // New field, default to ascending
      sortField.value = field
      sortDirection.value = 'asc'
    }
  }

  /**
   * Check if a field is currently being sorted
   * @param {String} field - Field name to check
   * @returns {Boolean}
   */
  const isSortedBy = (field) => {
    return sortField.value === field
  }

  /**
   * Get sort indicator for a field
   * @param {String} field - Field name
   * @returns {String} Sort indicator ('▲', '▼', or '')
   */
  const getSortIndicator = (field) => {
    if (!isSortedBy(field)) return ''
    return sortDirection.value === 'asc' ? '▲' : '▼'
  }

  return {
    sortField,
    sortDirection,
    sortedData,
    sortBy,
    isSortedBy,
    getSortIndicator
  }
}
