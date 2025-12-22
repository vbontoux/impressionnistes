<!--
  TableScrollIndicator Component
  
  A reusable component that wraps tables and provides visual scroll indicators
  on mobile devices. Shows gradient shadows on left/right to indicate more content.
  
  Props:
    - indicatorColor: Color of the gradient indicators (default: 'rgba(0, 0, 0, 0.1)')
    - indicatorWidth: Width of the gradient indicators in pixels (default: 20)
    - disabled: Disable scroll indicators (default: false)
    - ariaLabel: Accessibility label for the scrollable region
  
  Features:
    - Automatically detects scroll position
    - Shows/hides indicators based on scroll state
    - Smooth touch scrolling on mobile
    - Automatically disables on tablet/desktop
    - Accessible with keyboard navigation
-->

<template>
  <div class="table-scroll-container" ref="containerRef">
    <!-- Left scroll indicator -->
    <div 
      v-if="showLeftIndicator && !disabled" 
      class="scroll-indicator scroll-indicator-left"
      :style="indicatorStyle"
      aria-hidden="true"
    ></div>
    
    <!-- Scrollable table wrapper -->
    <div 
      class="table-wrapper" 
      ref="wrapperRef"
      @scroll="handleScroll"
      role="region"
      :aria-label="ariaLabel"
      tabindex="0"
    >
      <slot></slot>
    </div>
    
    <!-- Right scroll indicator -->
    <div 
      v-if="showRightIndicator && !disabled" 
      class="scroll-indicator scroll-indicator-right"
      :style="indicatorStyle"
      aria-hidden="true"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useIsMobile } from '../composables/useResponsive'

const props = defineProps({
  indicatorColor: {
    type: String,
    default: 'rgba(0, 0, 0, 0.1)'
  },
  indicatorWidth: {
    type: Number,
    default: 20
  },
  disabled: {
    type: Boolean,
    default: false
  },
  ariaLabel: {
    type: String,
    default: 'Scrollable table'
  }
})

const { isMobile } = useIsMobile()

const containerRef = ref(null)
const wrapperRef = ref(null)
const showLeftIndicator = ref(false)
const showRightIndicator = ref(false)

// Computed style for indicators
const indicatorStyle = computed(() => ({
  width: `${props.indicatorWidth}px`,
  '--indicator-color': props.indicatorColor
}))

/**
 * Check scroll position and update indicator visibility
 */
const checkScrollPosition = () => {
  if (!wrapperRef.value || props.disabled || !isMobile.value) {
    showLeftIndicator.value = false
    showRightIndicator.value = false
    return
  }

  const wrapper = wrapperRef.value
  const scrollLeft = wrapper.scrollLeft
  const scrollWidth = wrapper.scrollWidth
  const clientWidth = wrapper.clientWidth

  // Show left indicator if scrolled right
  showLeftIndicator.value = scrollLeft > 5

  // Show right indicator if not scrolled to the end
  showRightIndicator.value = scrollLeft < scrollWidth - clientWidth - 5
}

/**
 * Handle scroll event with debouncing
 */
let scrollTimeout = null
const handleScroll = () => {
  if (scrollTimeout) {
    clearTimeout(scrollTimeout)
  }
  
  scrollTimeout = setTimeout(() => {
    checkScrollPosition()
  }, 10)
}

/**
 * Handle window resize
 */
let resizeTimeout = null
const handleResize = () => {
  if (resizeTimeout) {
    clearTimeout(resizeTimeout)
  }
  
  resizeTimeout = setTimeout(() => {
    checkScrollPosition()
  }, 100)
}

// Initialize on mount
onMounted(() => {
  // Initial check after a short delay to ensure content is rendered
  setTimeout(() => {
    checkScrollPosition()
  }, 100)
  
  // Listen for window resize
  window.addEventListener('resize', handleResize)
})

// Cleanup on unmount
onUnmounted(() => {
  if (scrollTimeout) {
    clearTimeout(scrollTimeout)
  }
  if (resizeTimeout) {
    clearTimeout(resizeTimeout)
  }
  window.removeEventListener('resize', handleResize)
})

// Expose method to manually trigger check (useful for dynamic content)
defineExpose({
  checkScrollPosition
})
</script>

<style scoped>
.table-scroll-container {
  position: relative;
  width: 100%;
}

.table-wrapper {
  width: 100%;
  overflow-x: auto;
  overflow-y: visible;
  -webkit-overflow-scrolling: touch; /* Smooth scrolling on iOS */
  scroll-behavior: smooth;
}

/* Hide scrollbar on mobile for cleaner look (optional) */
.table-wrapper::-webkit-scrollbar {
  height: 6px;
}

.table-wrapper::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.table-wrapper::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.table-wrapper::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Scroll indicators */
.scroll-indicator {
  position: absolute;
  top: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
  transition: opacity 0.3s ease;
}

.scroll-indicator-left {
  left: 0;
  background: linear-gradient(
    to right,
    var(--indicator-color),
    transparent
  );
}

.scroll-indicator-right {
  right: 0;
  background: linear-gradient(
    to left,
    var(--indicator-color),
    transparent
  );
}

/* Disable scroll and indicators on tablet and up */
@media (min-width: 768px) {
  .table-wrapper {
    overflow-x: visible;
  }
  
  .scroll-indicator {
    display: none;
  }
}

/* Focus styles for accessibility */
.table-wrapper:focus {
  outline: 2px solid #4A90E2;
  outline-offset: 2px;
}

.table-wrapper:focus:not(:focus-visible) {
  outline: none;
}
</style>
