/**
 * useResponsive Composable
 * 
 * Provides reactive viewport size detection for Vue components.
 * Automatically updates when the window is resized.
 * 
 * Usage:
 * import { useResponsive } from '@/composables/useResponsive'
 * 
 * const { isMobile, isTablet, isDesktop, currentBreakpoint } = useResponsive()
 * 
 * // In template:
 * <div v-if="isMobile">Mobile view</div>
 * <div v-else>Desktop view</div>
 */

import { ref, onMounted, onUnmounted } from 'vue'
import { BREAKPOINTS, getCurrentBreakpoint } from '@/utils/responsive'

/**
 * Debounce function to limit resize event frequency
 * @param {Function} func - Function to debounce
 * @param {number} wait - Milliseconds to wait
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 150) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Composable for responsive viewport detection
 * @returns {Object} Reactive viewport state
 */
export function useResponsive() {
  // Reactive viewport width
  const viewportWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 0)
  
  // Reactive breakpoint flags
  const isMobile = ref(false)
  const isTablet = ref(false)
  const isDesktop = ref(false)
  const isXlDesktop = ref(false)
  
  // Current breakpoint name
  const currentBreakpoint = ref('mobile')
  
  /**
   * Update all reactive values based on current viewport width
   */
  const updateBreakpoints = () => {
    if (typeof window === 'undefined') return
    
    const width = window.innerWidth
    viewportWidth.value = width
    
    // Update breakpoint flags
    isMobile.value = width < BREAKPOINTS.TABLET
    isTablet.value = width >= BREAKPOINTS.TABLET && width < BREAKPOINTS.DESKTOP
    isDesktop.value = width >= BREAKPOINTS.DESKTOP && width < BREAKPOINTS.XL_DESKTOP
    isXlDesktop.value = width >= BREAKPOINTS.XL_DESKTOP
    
    // Update current breakpoint name
    currentBreakpoint.value = getCurrentBreakpoint()
  }
  
  // Debounced resize handler
  const debouncedUpdate = debounce(updateBreakpoints, 150)
  
  // Set up resize listener on mount
  onMounted(() => {
    // Initial update
    updateBreakpoints()
    
    // Add resize listener
    window.addEventListener('resize', debouncedUpdate)
  })
  
  // Clean up on unmount
  onUnmounted(() => {
    window.removeEventListener('resize', debouncedUpdate)
  })
  
  return {
    // Viewport width
    viewportWidth,
    
    // Breakpoint flags
    isMobile,
    isTablet,
    isDesktop,
    isXlDesktop,
    
    // Current breakpoint name
    currentBreakpoint,
    
    // Helper computed properties
    isTabletUp: ref(false), // tablet or larger
    isDesktopUp: ref(false) // desktop or larger
  }
}

/**
 * Simplified version that only tracks mobile vs non-mobile
 * Useful for components that only need basic mobile detection
 * 
 * Usage:
 * const { isMobile } = useIsMobile()
 */
export function useIsMobile() {
  const isMobile = ref(typeof window !== 'undefined' ? window.innerWidth < BREAKPOINTS.TABLET : false)
  
  const updateMobile = () => {
    if (typeof window === 'undefined') return
    isMobile.value = window.innerWidth < BREAKPOINTS.TABLET
  }
  
  const debouncedUpdate = debounce(updateMobile, 150)
  
  onMounted(() => {
    updateMobile()
    window.addEventListener('resize', debouncedUpdate)
  })
  
  onUnmounted(() => {
    window.removeEventListener('resize', debouncedUpdate)
  })
  
  return { isMobile }
}

/**
 * Hook for detecting orientation changes
 * Useful for handling landscape/portrait transitions
 * 
 * Usage:
 * const { isPortrait, isLandscape } = useOrientation()
 */
export function useOrientation() {
  const isPortrait = ref(typeof window !== 'undefined' ? window.innerHeight > window.innerWidth : true)
  const isLandscape = ref(typeof window !== 'undefined' ? window.innerWidth > window.innerHeight : false)
  
  const updateOrientation = () => {
    if (typeof window === 'undefined') return
    isPortrait.value = window.innerHeight > window.innerWidth
    isLandscape.value = window.innerWidth > window.innerHeight
  }
  
  const debouncedUpdate = debounce(updateOrientation, 150)
  
  onMounted(() => {
    updateOrientation()
    window.addEventListener('resize', debouncedUpdate)
  })
  
  onUnmounted(() => {
    window.removeEventListener('resize', debouncedUpdate)
  })
  
  return {
    isPortrait,
    isLandscape
  }
}
