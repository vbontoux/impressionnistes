<template>
  <div class="sortable-table-container">
    <div 
      ref="wrapperRef"
      class="sortable-table-wrapper" 
      :class="{ 
        'compact-mode': compact,
        'has-scroll': hasHorizontalScroll,
        'scrolled-left': scrollLeft > 0,
        'scrolled-right': scrollLeft < maxScrollLeft
      }"
    >
      <div class="table-container">
      <table 
        ref="tableRef"
        class="sortable-table" 
        role="table"
        :aria-label="ariaLabel"
      >
        <thead role="rowgroup">
          <tr role="row">
            <th
              v-for="column in columns"
              :key="column.key"
              role="columnheader"
              :class="[
                'table-header',
                {
                  'sortable': column.sortable !== false,
                  'sorted': isSortedBy(column.key),
                  [`align-${column.align || 'left'}`]: true,
                  [`sticky-${column.sticky}`]: column.sticky,
                  'column-shrink': shouldShrinkColumn(column)
                },
                getResponsiveClass(column)
              ]"
              :style="getColumnStyle(column)"
              :aria-sort="getAriaSort(column)"
              :tabindex="column.sortable !== false ? 0 : -1"
              :data-field="column.key"
              :data-sortable="column.sortable !== false"
              @click="column.sortable !== false ? sortBy(column.key) : null"
              @keydown.enter.prevent="column.sortable !== false ? sortBy(column.key) : null"
              @keydown.space.prevent="column.sortable !== false ? sortBy(column.key) : null"
            >
              <span class="header-content">
                {{ column.label }}
                <span 
                  v-if="column.sortable !== false" 
                  class="sort-indicator"
                  aria-hidden="true"
                >
                  {{ getSortIndicator(column.key) }}
                </span>
              </span>
            </th>
          </tr>
        </thead>
        <tbody role="rowgroup">
          <tr
            v-for="(row, index) in sortedData"
            :key="row.id || index"
            role="row"
            :class="[
              'table-row',
              {
                'hoverable': hoverable,
                [`status-${row.registration_status}`]: row.registration_status
              }
            ]"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              role="cell"
              :class="[
                'table-cell',
                `align-${column.align || 'left'}`,
                {
                  [`sticky-${column.sticky}`]: column.sticky,
                  'column-shrink': shouldShrinkColumn(column)
                },
                getResponsiveClass(column)
              ]"
              :style="getColumnStyle(column)"
              tabindex="0"
            >
              <!-- Use slot if provided, otherwise display value -->
              <slot
                :name="`cell-${column.key}`"
                :row="row"
                :value="row[column.key]"
                :column="column"
              >
                {{ row[column.key] }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    </div>
    
    <!-- Sticky horizontal scrollbar that stays at bottom of viewport -->
    <div 
      v-if="hasHorizontalScroll"
      ref="stickyScrollbarRef"
      class="sticky-scrollbar"
      :class="{ 'is-sticky': isStickyScrollbarVisible }"
      :style="{
        left: stickyScrollbarLeft + 'px',
        width: stickyScrollbarWidth + 'px'
      }"
    >
      <div 
        class="sticky-scrollbar-track"
        @mousedown="handleStickyScrollbarMouseDown"
      >
        <div 
          class="sticky-scrollbar-thumb"
          :style="{ 
            width: thumbWidth + 'px',
            transform: `translateX(${thumbPosition}px)`
          }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, toRef, computed, onMounted, onUnmounted } from 'vue'
import { useTableSort } from '@/composables/useTableSort'
import { useTableKeyboard } from '@/composables/useTableKeyboard'
import { useTableScroll } from '@/composables/useTableScroll'

const props = defineProps({
  // Column definitions with key, label, sortable, width, align, sticky, responsive
  columns: {
    type: Array,
    required: true,
    validator: (columns) => {
      return columns.every(col => {
        // Required properties
        if (!col.key || !col.label) {
          console.error('Column must have key and label:', col)
          return false
        }
        
        // Validate sticky property if present
        if (col.sticky !== undefined && col.sticky !== 'left' && col.sticky !== 'right') {
          console.error(`Invalid sticky value "${col.sticky}" for column "${col.key}". Must be 'left' or 'right'.`)
          return false
        }
        
        // Validate responsive property if present
        if (col.responsive !== undefined && 
            col.responsive !== 'always' && 
            col.responsive !== 'hide-below-1024' && 
            col.responsive !== 'hide-below-768') {
          console.error(`Invalid responsive value "${col.responsive}" for column "${col.key}". Must be 'always', 'hide-below-1024', or 'hide-below-768'.`)
          return false
        }
        
        return true
      })
    }
  },
  
  // Data array to display
  data: {
    type: Array,
    required: true
  },
  
  // Initial field to sort by
  initialSortField: {
    type: String,
    default: ''
  },
  
  // Initial sort direction ('asc' or 'desc')
  initialSortDirection: {
    type: String,
    default: 'asc',
    validator: (value) => ['asc', 'desc'].includes(value)
  },
  
  // Enable hover effect on rows
  hoverable: {
    type: Boolean,
    default: true
  },
  
  // Enable compact mode (reduced padding)
  compact: {
    type: Boolean,
    default: false
  },
  
  // ARIA label for accessibility
  ariaLabel: {
    type: String,
    default: 'Data table'
  }
})

const emit = defineEmits(['sort', 'scroll'])

// Ref for the table element (used by keyboard navigation)
const tableRef = ref(null)

// Ref for the wrapper element (used by scroll management)
const wrapperRef = ref(null)

// Track horizontal scroll state
const hasHorizontalScroll = ref(false)
const maxScrollLeft = ref(0)
const isStickyScrollbarVisible = ref(false)
const stickyScrollbarRef = ref(null)
const thumbWidth = ref(100)
const thumbPosition = ref(0)
const stickyScrollbarLeft = ref(0)
const stickyScrollbarWidth = ref(0)

// Calculate sticky scrollbar dimensions and position
const updateStickyScrollbar = () => {
  if (!wrapperRef.value) return
  
  const wrapper = wrapperRef.value
  const scrollWidth = wrapper.scrollWidth
  const clientWidth = wrapper.clientWidth
  
  // Add tolerance to account for:
  // - Scrollbar width (12px)
  // - Sticky column shadows/borders
  // - Browser rounding errors
  // If the difference is less than 20px, consider it as no scroll needed
  const scrollDifference = scrollWidth - clientWidth
  if (scrollDifference <= 20) {
    hasHorizontalScroll.value = false
    return
  }
  
  hasHorizontalScroll.value = true
  maxScrollLeft.value = scrollDifference
  
  // Get wrapper's position relative to viewport
  const wrapperRect = wrapper.getBoundingClientRect()
  stickyScrollbarLeft.value = wrapperRect.left
  stickyScrollbarWidth.value = wrapperRect.width
  
  // Calculate thumb width (proportional to visible area)
  const ratio = clientWidth / scrollWidth
  thumbWidth.value = Math.max(50, clientWidth * ratio)
  
  // Calculate thumb position
  const scrollRatio = scrollLeft.value / maxScrollLeft.value
  const maxThumbPosition = clientWidth - thumbWidth.value
  thumbPosition.value = scrollRatio * maxThumbPosition
}

// Check if sticky scrollbar should be visible
const checkStickyScrollbarVisibility = () => {
  if (!wrapperRef.value || !hasHorizontalScroll.value) {
    isStickyScrollbarVisible.value = false
    return
  }
  
  const wrapperRect = wrapperRef.value.getBoundingClientRect()
  const wrapperBottom = wrapperRect.bottom
  const viewportHeight = window.innerHeight
  
  // Show sticky scrollbar when native scrollbar is below viewport
  isStickyScrollbarVisible.value = wrapperBottom > viewportHeight
}

// Handle sticky scrollbar dragging
const handleStickyScrollbarMouseDown = (event) => {
  if (!wrapperRef.value) return
  
  event.preventDefault()
  
  const wrapper = wrapperRef.value
  const trackRect = event.currentTarget.getBoundingClientRect()
  const clickX = event.clientX - trackRect.left
  
  // Check if clicked on thumb
  const thumbStart = thumbPosition.value
  const thumbEnd = thumbStart + thumbWidth.value
  
  if (clickX >= thumbStart && clickX <= thumbEnd) {
    // Dragging thumb
    const startX = event.clientX
    const startScrollLeft = wrapper.scrollLeft
    
    const handleMouseMove = (e) => {
      const deltaX = e.clientX - startX
      const scrollRatio = deltaX / (trackRect.width - thumbWidth.value)
      wrapper.scrollLeft = startScrollLeft + (scrollRatio * maxScrollLeft.value)
    }
    
    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
    
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  } else {
    // Clicked on track - jump to position
    const clickRatio = clickX / trackRect.width
    wrapper.scrollLeft = clickRatio * maxScrollLeft.value
  }
}

// Check if table has horizontal scroll
const checkHorizontalScroll = () => {
  updateStickyScrollbar()
  checkStickyScrollbarVisibility()
}

// Set up resize observer to detect when scrolling is needed
onMounted(() => {
  checkHorizontalScroll()
  
  if (wrapperRef.value) {
    const resizeObserver = new ResizeObserver(() => {
      checkHorizontalScroll()
    })
    resizeObserver.observe(wrapperRef.value)
    
    // Cleanup
    onUnmounted(() => {
      resizeObserver.disconnect()
    })
  }
  
  // Check on window resize and scroll
  const handleWindowUpdate = () => {
    checkHorizontalScroll()
    checkStickyScrollbarVisibility()
  }
  
  window.addEventListener('resize', handleWindowUpdate)
  window.addEventListener('scroll', handleWindowUpdate)
  
  onUnmounted(() => {
    window.removeEventListener('resize', handleWindowUpdate)
    window.removeEventListener('scroll', handleWindowUpdate)
  })
})

// Use the table sort composable
const dataRef = toRef(props, 'data')
const {
  sortField,
  sortDirection,
  sortedData,
  sortBy: sortByField,
  isSortedBy,
  getSortIndicator
} = useTableSort(dataRef, props.initialSortField, props.initialSortDirection)

// Use the keyboard navigation composable
useTableKeyboard(tableRef, sortByField)

// Use the scroll management composable
const emitScrollEvent = (scrollData) => {
  emit('scroll', scrollData)
  
  // Update sticky scrollbar
  updateStickyScrollbar()
}

const {
  scrollLeft,
  isScrolling,
  scrollTo,
  scrollToStart,
  scrollToEnd
} = useTableScroll(wrapperRef, emitScrollEvent)

// Wrap sortBy to emit event
const sortBy = (field) => {
  sortByField(field)
  emit('sort', {
    field: sortField.value,
    direction: sortDirection.value
  })
}

// Get responsive CSS class for column
const getResponsiveClass = (column) => {
  const responsive = column.responsive || 'always'
  return `column-${responsive}`
}

// Get column style object for width and minWidth
const getColumnStyle = (column) => {
  const style = {}
  
  // Apply width if explicitly set
  if (column.width) {
    style.width = column.width
  }
  
  // Apply minWidth if set (can be used with or without width)
  if (column.minWidth) {
    style.minWidth = column.minWidth
  }
  
  // If neither width nor minWidth is set, don't add any width style
  // The CSS class .column-shrink will handle it
  
  return style
}

// Check if column should shrink to content
const shouldShrinkColumn = (column) => {
  return !column.width && !column.minWidth
}

// Get ARIA sort attribute for column header
const getAriaSort = (column) => {
  // Non-sortable columns don't have aria-sort
  if (column.sortable === false) {
    return undefined
  }
  
  // If this column is currently sorted, return the direction
  if (isSortedBy(column.key)) {
    return sortDirection.value === 'asc' ? 'ascending' : 'descending'
  }
  
  // Sortable but not currently sorted
  return 'none'
}
</script>

<style scoped>
/* Container for table and sticky scrollbar */
.sortable-table-container {
  position: relative;
  width: 100%;
}

.sortable-table-wrapper {
  width: 100%;
  overflow-x: auto;
  overflow-y: visible;
  -webkit-overflow-scrolling: touch;
  position: relative;
}

/* Scroll Indicators - Disabled to avoid visual effects */
.scroll-indicator {
  display: none;
}

/* Enhanced visible scrollbar styling for all screen sizes */
.sortable-table-wrapper::-webkit-scrollbar {
  height: var(--scrollbar-height);
  background: var(--color-light);
}

.sortable-table-wrapper::-webkit-scrollbar-track {
  background: var(--color-light);
  border-radius: var(--scrollbar-border-radius);
  border: 1px solid var(--color-border);
  margin: 0 var(--spacing-sm);
}

.sortable-table-wrapper::-webkit-scrollbar-thumb {
  background: var(--color-primary);
  border-radius: var(--scrollbar-border-radius);
  border: 2px solid var(--color-light);
  min-width: 50px;
}

.sortable-table-wrapper::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary-hover);
  border-color: var(--color-bg-white);
}

.sortable-table-wrapper::-webkit-scrollbar-thumb:active {
  background: var(--color-primary-active);
}

/* Firefox scrollbar - make it more visible */
.sortable-table-wrapper {
  scrollbar-width: auto;
  scrollbar-color: var(--color-primary) var(--color-light);
}

/* Sticky Scrollbar - Stays at bottom of viewport */
.sticky-scrollbar {
  position: fixed;
  bottom: 0;
  /* left and width set dynamically via inline styles */
  height: calc(var(--scrollbar-height) + 8px);
  background: var(--color-bg-white);
  border-top: 2px solid var(--color-primary);
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
  z-index: var(--z-index-fixed);
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--transition-normal);
  padding: 4px 0;
}

.sticky-scrollbar.is-sticky {
  opacity: 1;
  pointer-events: auto;
}

.sticky-scrollbar-track {
  width: 100%;
  height: var(--scrollbar-height);
  background: var(--color-light);
  border-radius: var(--scrollbar-border-radius);
  border: 1px solid var(--color-border);
  position: relative;
  cursor: pointer;
  margin: 0 auto;
  max-width: 100%;
}

.sticky-scrollbar-thumb {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: var(--color-primary);
  border-radius: var(--scrollbar-border-radius);
  border: 2px solid var(--color-light);
  cursor: grab;
  transition: background-color var(--transition-fast);
}

.sticky-scrollbar-thumb:hover {
  background: var(--color-primary-hover);
}

.sticky-scrollbar-thumb:active {
  background: var(--color-primary-active);
  cursor: grabbing;
}

.table-container {
  min-width: 100%;
  display: inline-block;
}

.sortable-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: auto; /* Allow columns to size based on content */
  background-color: var(--color-bg-white);
}

/* Shrink-to-content columns */
.table-header.column-shrink,
.table-cell.column-shrink {
  width: 1%;
  white-space: nowrap;
}

/* Table Header */
.table-header {
  background-color: var(--table-header-bg);
  font-weight: var(--table-header-font-weight);
  font-size: var(--font-size-base);
  color: var(--color-dark);
  text-align: left;
  padding: var(--table-cell-padding-mobile);
  border-bottom: 1px solid var(--table-border-color);
  white-space: normal; /* Allow wrapping */
  word-wrap: break-word;
  user-select: none;
  vertical-align: top; /* Align to top when multi-line */
}

.table-header.sortable {
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.table-header.sortable:hover {
  background-color: var(--color-bg-hover);
}

.table-header.sorted {
  color: var(--color-primary);
}

.header-content {
  display: flex;
  align-items: flex-start; /* Align to top for multi-line */
  gap: var(--spacing-sm);
  line-height: 1.4; /* Better line height for multi-line text */
}

.sort-indicator {
  font-size: var(--font-size-xs);
  color: var(--color-primary);
  min-width: var(--table-sort-indicator-width);
  display: inline-block;
  flex-shrink: 0; /* Prevent sort indicator from shrinking */
}

/* Focus Indicators for Keyboard Navigation */
.table-header:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
  position: relative;
  z-index: 1;
}

.table-cell:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
  position: relative;
  z-index: 1;
}

/* High contrast focus for accessibility */
@media (prefers-contrast: high) {
  .table-header:focus,
  .table-cell:focus {
    outline-width: 3px;
    outline-color: var(--color-dark);
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .table-header,
  .table-row {
    transition: none;
  }
}

/* Alignment */
.align-left {
  text-align: left;
}

.align-center {
  text-align: center;
}

.align-right {
  text-align: right;
}

/* Table Body */
.table-row {
  border-bottom: 1px solid var(--table-border-color);
  transition: background-color var(--transition-fast);
}

.table-row.hoverable:hover {
  background-color: var(--table-hover-bg);
}

/* Status-based row styling (left border) */
.table-row.status-incomplete {
  border-left: var(--table-status-border-width) solid var(--color-warning);
}

.table-row.status-complete {
  border-left: var(--table-status-border-width) solid var(--color-success);
}

.table-row.status-paid {
  border-left: var(--table-status-border-width) solid var(--color-primary);
}

.table-row.status-forfait {
  border-left: var(--table-status-border-width) solid var(--color-danger);
}

.table-cell {
  padding: var(--table-cell-padding-mobile);
  font-size: var(--font-size-base);
  color: var(--color-dark);
  vertical-align: middle;
}

/* Responsive adjustments */
@media (min-width: 768px) {
  .table-header,
  .table-cell {
    padding: var(--table-cell-padding-desktop);
  }
}

/* Sticky Column Support */

/* Sticky left columns */
.table-header.sticky-left,
.table-cell.sticky-left {
  position: sticky;
  left: 0;
  z-index: var(--z-index-sticky);
  background-color: var(--color-bg-white);
}

.table-header.sticky-left {
  z-index: calc(var(--z-index-sticky) + 1);
  background-color: var(--table-header-bg);
}

/* Sticky right columns */
.table-header.sticky-right,
.table-cell.sticky-right {
  position: sticky;
  right: 0;
  z-index: var(--z-index-sticky);
  background-color: var(--color-bg-white);
}

.table-header.sticky-right {
  z-index: calc(var(--z-index-sticky) + 1);
  background-color: var(--table-header-bg);
}

/* Responsive Column Visibility */

/* Always visible columns - no hiding */
.column-always {
  display: table-cell;
}

/* Hide below 1024px (tablets) */
@media (max-width: 1023px) {
  .column-hide-below-1024 {
    display: none;
  }
}

/* Hide below 768px (mobile - but card view used instead) */
@media (max-width: 767px) {
  .column-hide-below-768 {
    display: none;
  }
}

/* Compact Mode */

/* Compact mode - 50% reduced padding */
.sortable-table-wrapper.compact-mode .table-header,
.sortable-table-wrapper.compact-mode .table-cell {
  padding: calc(var(--table-cell-padding-mobile) * 0.5);
}

@media (min-width: 768px) {
  .sortable-table-wrapper.compact-mode .table-header,
  .sortable-table-wrapper.compact-mode .table-cell {
    padding: calc(var(--table-cell-padding-desktop) * 0.5);
  }
}

/* Maintain minimum touch targets for interactive elements in compact mode */
.sortable-table-wrapper.compact-mode .table-cell button,
.sortable-table-wrapper.compact-mode .table-cell a,
.sortable-table-wrapper.compact-mode .table-cell .base-button {
  min-height: var(--touch-target-min-size);
  min-width: var(--touch-target-min-size);
}
</style>
