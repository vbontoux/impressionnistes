/**
 * Composable for keyboard navigation in tables
 * 
 * Provides:
 * - Enter/Space key support for sortable headers (already handled in template)
 * - Arrow key navigation between cells
 * - Tabindex management for focusable elements
 * 
 * @param {Ref} tableRef - Reference to the table element
 * @param {Function} sortByField - Function to sort by a field (from useTableSort)
 */
import { onMounted, onUnmounted } from 'vue'

export function useTableKeyboard(tableRef, sortByField) {
  /**
   * Handle keyboard events on the table
   * @param {KeyboardEvent} event
   */
  const handleKeyDown = (event) => {
    const target = event.target
    
    // Sort on Enter or Space for sortable headers
    // Note: This is also handled in the template with @keydown.enter and @keydown.space
    // but we keep it here for completeness and as a fallback
    if (target.tagName === 'TH' && target.getAttribute('data-sortable') === 'true') {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault()
        const field = target.getAttribute('data-field')
        if (field) {
          sortByField(field)
        }
      }
    }
    
    // Arrow key navigation between cells
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) {
      handleArrowNavigation(event)
    }
  }
  
  /**
   * Handle arrow key navigation between table cells
   * @param {KeyboardEvent} event
   */
  const handleArrowNavigation = (event) => {
    const target = event.target
    
    // Only handle navigation for table cells and headers
    if (target.tagName !== 'TD' && target.tagName !== 'TH') return
    
    const cell = target
    const row = cell.parentElement
    
    let nextCell = null
    
    switch (event.key) {
      case 'ArrowLeft':
        // Move to previous cell in the same row
        nextCell = cell.previousElementSibling
        break
        
      case 'ArrowRight':
        // Move to next cell in the same row
        nextCell = cell.nextElementSibling
        break
        
      case 'ArrowUp': {
        // Move to cell in previous row (same column)
        const prevRow = row.previousElementSibling
        if (prevRow) {
          const cellIndex = Array.from(row.children).indexOf(cell)
          nextCell = prevRow.children[cellIndex]
        }
        break
      }
        
      case 'ArrowDown': {
        // Move to cell in next row (same column)
        const nextRow = row.nextElementSibling
        if (nextRow) {
          const cellIndex = Array.from(row.children).indexOf(cell)
          nextCell = nextRow.children[cellIndex]
        }
        break
      }
    }
    
    // If we found a valid next cell, focus it and prevent default scroll behavior
    if (nextCell) {
      event.preventDefault()
      nextCell.focus()
    }
  }
  
  // Set up event listener on mount
  onMounted(() => {
    if (tableRef.value) {
      tableRef.value.addEventListener('keydown', handleKeyDown)
    }
  })
  
  // Clean up event listener on unmount
  onUnmounted(() => {
    if (tableRef.value) {
      tableRef.value.removeEventListener('keydown', handleKeyDown)
    }
  })
  
  return {
    // No return values needed - this composable manages side effects only
  }
}
