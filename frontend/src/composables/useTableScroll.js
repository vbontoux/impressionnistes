/**
 * Composable for table scroll management
 * 
 * Provides:
 * - Scroll event handling with passive listeners for better performance
 * - Track scrollLeft state for advanced use cases
 * - Debounced scroll state updates to reduce re-renders
 * - Emit scroll events for parent components
 * - Proper cleanup on unmount
 * 
 * @param {Ref} wrapperRef - Reference to the table wrapper element
 * @param {Function} emitScroll - Function to emit scroll events to parent
 * @returns {Object} Scroll state and methods
 */
import { ref, onMounted, onUnmounted } from 'vue'

export function useTableScroll(wrapperRef, emitScroll) {
  // Track current scroll position
  const scrollLeft = ref(0)
  
  // Track if currently scrolling (for potential visual feedback)
  const isScrolling = ref(false)
  
  // Debounce timeout reference
  let scrollTimeout = null
  
  /**
   * Handle scroll events on the wrapper element
   * Uses debouncing to reduce the frequency of state updates
   * @param {Event} event - Scroll event
   */
  const handleScroll = (event) => {
    const target = event.target
    
    // Update scroll position immediately for smooth tracking
    scrollLeft.value = target.scrollLeft
    
    // Mark as scrolling
    isScrolling.value = true
    
    // Debounce the scroll end detection
    clearTimeout(scrollTimeout)
    scrollTimeout = setTimeout(() => {
      isScrolling.value = false
      
      // Emit scroll event to parent component (if provided)
      if (emitScroll) {
        emitScroll({
          scrollLeft: target.scrollLeft,
          scrollWidth: target.scrollWidth,
          clientWidth: target.clientWidth
        })
      }
    }, 150) // 150ms debounce as specified in requirements
  }
  
  /**
   * Programmatically scroll to a specific position
   * Useful for parent components that need to control scroll position
   * @param {Number} position - Scroll position in pixels
   */
  const scrollTo = (position) => {
    if (wrapperRef.value) {
      wrapperRef.value.scrollLeft = position
    }
  }
  
  /**
   * Scroll to the start of the table
   */
  const scrollToStart = () => {
    scrollTo(0)
  }
  
  /**
   * Scroll to the end of the table
   */
  const scrollToEnd = () => {
    if (wrapperRef.value) {
      scrollTo(wrapperRef.value.scrollWidth - wrapperRef.value.clientWidth)
    }
  }
  
  // Set up event listener on mount
  onMounted(() => {
    if (wrapperRef.value) {
      // Use passive listener for better scroll performance
      // Passive listeners tell the browser that preventDefault() won't be called
      // This allows the browser to optimize scrolling performance
      wrapperRef.value.addEventListener('scroll', handleScroll, { passive: true })
    }
  })
  
  // Clean up event listener and timeout on unmount
  onUnmounted(() => {
    if (wrapperRef.value) {
      wrapperRef.value.removeEventListener('scroll', handleScroll)
    }
    
    // Clear any pending timeout to prevent memory leaks
    clearTimeout(scrollTimeout)
  })
  
  return {
    scrollLeft,
    isScrolling,
    scrollTo,
    scrollToStart,
    scrollToEnd
  }
}
