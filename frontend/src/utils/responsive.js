/**
 * Responsive Design Utilities
 * 
 * This file contains standardized breakpoint values and utility functions
 * for implementing responsive design across the application.
 * 
 * Breakpoint Strategy: Mobile-First
 * - Base styles target mobile devices (< 768px)
 * - Media queries progressively enhance for larger screens
 */

/**
 * Standard breakpoint values (in pixels)
 * These values should be used consistently across all components
 */
export const BREAKPOINTS = {
  // Mobile devices: < 768px (base styles, no media query needed)
  MOBILE: 0,
  
  // Tablet devices: 768px - 1023px
  TABLET: 768,
  
  // Desktop devices: 1024px - 1199px
  DESKTOP: 1024,
  
  // Extra large desktop: >= 1200px
  XL_DESKTOP: 1200
}

/**
 * Media query strings for use in CSS-in-JS or computed styles
 * Example usage: if (window.matchMedia(MEDIA_QUERIES.TABLET).matches) { ... }
 */
export const MEDIA_QUERIES = {
  MOBILE: `(max-width: ${BREAKPOINTS.TABLET - 1}px)`,
  TABLET: `(min-width: ${BREAKPOINTS.TABLET}px) and (max-width: ${BREAKPOINTS.DESKTOP - 1}px)`,
  TABLET_UP: `(min-width: ${BREAKPOINTS.TABLET}px)`,
  DESKTOP: `(min-width: ${BREAKPOINTS.DESKTOP}px) and (max-width: ${BREAKPOINTS.XL_DESKTOP - 1}px)`,
  DESKTOP_UP: `(min-width: ${BREAKPOINTS.DESKTOP}px)`,
  XL_DESKTOP: `(min-width: ${BREAKPOINTS.XL_DESKTOP}px)`
}

/**
 * Touch target minimum size for accessibility (WCAG 2.1)
 * All interactive elements should meet this minimum size on mobile
 */
export const TOUCH_TARGET_MIN = 44 // pixels

/**
 * Minimum font size to prevent iOS zoom on input focus
 */
export const MIN_INPUT_FONT_SIZE = 16 // pixels

/**
 * Standard spacing values for mobile optimization
 */
export const MOBILE_SPACING = {
  PADDING_SM: '0.5rem',
  PADDING_MD: '1rem',
  PADDING_LG: '1.5rem',
  MARGIN_SM: '0.5rem',
  MARGIN_MD: '1rem',
  MARGIN_LG: '1.5rem',
  GAP_SM: '0.5rem',
  GAP_MD: '1rem',
  GAP_LG: '1.5rem'
}

/**
 * Helper function to check if current viewport matches a breakpoint
 * @param {string} breakpoint - One of 'mobile', 'tablet', 'desktop', 'xl-desktop'
 * @returns {boolean}
 */
export function matchesBreakpoint(breakpoint) {
  const queries = {
    mobile: MEDIA_QUERIES.MOBILE,
    tablet: MEDIA_QUERIES.TABLET,
    'tablet-up': MEDIA_QUERIES.TABLET_UP,
    desktop: MEDIA_QUERIES.DESKTOP,
    'desktop-up': MEDIA_QUERIES.DESKTOP_UP,
    'xl-desktop': MEDIA_QUERIES.XL_DESKTOP
  }
  
  const query = queries[breakpoint]
  if (!query) {
    console.warn(`Unknown breakpoint: ${breakpoint}`)
    return false
  }
  
  return window.matchMedia(query).matches
}

/**
 * Helper function to get current breakpoint name
 * @returns {string} - 'mobile', 'tablet', 'desktop', or 'xl-desktop'
 */
export function getCurrentBreakpoint() {
  const width = window.innerWidth
  
  if (width < BREAKPOINTS.TABLET) {
    return 'mobile'
  } else if (width < BREAKPOINTS.DESKTOP) {
    return 'tablet'
  } else if (width < BREAKPOINTS.XL_DESKTOP) {
    return 'desktop'
  } else {
    return 'xl-desktop'
  }
}
