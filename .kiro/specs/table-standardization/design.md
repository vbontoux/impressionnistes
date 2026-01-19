# Design Document: Table Standardization

## Overview

This design document specifies the technical approach for enhancing the existing SortableTable component to provide a consistent, accessible, and performant table experience across all views in the Impressionnistes Registration System. The enhanced component will support horizontal scrolling with visible scrollbars, optional sticky columns, optional responsive column hiding, compact display modes, and comprehensive customization through slots and props.

### Goals

1. **Consistency**: Standardize table implementation across all admin and user views
2. **Accessibility**: Ensure WCAG 2.1 Level AA compliance with keyboard navigation and screen reader support
3. **Performance**: Maintain smooth rendering and scrolling for tables with 50-100 rows
4. **Flexibility**: Support diverse use cases through configuration without code duplication
5. **Maintainability**: Centralize table logic in a single, well-tested component
6. **Backward Compatibility**: Preserve existing SortableTable functionality during migration

### Non-Goals

- Virtual scrolling for extremely large datasets (>500 rows)
- Built-in pagination (handled by parent components)
- Built-in filtering (handled by parent components)
- Card view implementation (remains separate, view-specific)
- Data fetching or state management (handled by parent components)

## Architecture

### Component Structure


```
SortableTable.vue (Enhanced)
├── Template
│   ├── .sortable-table-wrapper (scroll container)
│   │   └── .table-container
│   │       └── table.sortable-table
│   │           ├── thead (headers with sort indicators)
│   │           └── tbody (data rows with slots)
├── Script (Composition API)
│   ├── Props (column config, data, options)
│   ├── Composables
│   │   ├── useTableSort (existing)
│   │   ├── useTableScroll (new - scroll management)
│   │   └── useTableResize (new - responsive behavior)
│   └── Emits (sort, scroll events)
└── Styles (scoped CSS with design tokens)
    ├── Base table styles
    ├── Horizontal scroll styles
    ├── Sticky column styles (optional)
    ├── Responsive column hiding (optional)
    └── Compact mode styles
```

### Key Design Decisions


**1. Horizontal Scrolling: CSS-based with Visible Scrollbar**
- Use CSS `overflow-x: auto` on wrapper element
- Style scrollbar using `::-webkit-scrollbar` pseudo-elements for visibility
- Minimum scrollbar height: 8px for easy interaction
- Scrollbar always visible on HDPI/MDPI screens (not auto-hide)

**2. Sticky Columns: CSS `position: sticky`**
- Use CSS `position: sticky` instead of JavaScript for better performance
- Support `sticky-left` and `sticky-right` configurations
- Add visual separator (box-shadow) to indicate fixed position
- Z-index management to ensure proper layering
- Optional feature: configured per-column during migration

**3. Responsive Column Hiding: CSS Media Queries**
- Use CSS `@media` queries for responsive behavior
- Column visibility controlled by CSS classes
- Priority levels: `always-visible`, `hide-below-1024`, `hide-below-768`
- No JavaScript resize observers needed (simpler, more performant)
- Optional feature: configured per-column during migration

**4. Column Width: Flexible Configuration**
- Support fixed widths (px), percentages (%), and auto-sizing
- Use CSS `min-width` for minimum column constraints
- Table uses `table-layout: auto` for flexible sizing
- Horizontal scroll activates when total width exceeds container

**5. Compact Mode: CSS Class Toggle**
- Single CSS class `.compact-mode` reduces padding by 50%
- Controlled by boolean prop `compact`
- Optional localStorage persistence handled by parent component
- Maintains 44px minimum touch targets for interactive elements

## Components and Interfaces

### Enhanced SortableTable Component

**Location**: `frontend/src/components/composite/SortableTable.vue`


#### Props API

```javascript
defineProps({
  // Column definitions array (required)
  columns: {
    type: Array,
    required: true,
    validator: (columns) => {
      return columns.every(col => col.key && col.label)
    }
  },
  
  // Data array to display (required)
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
```

#### Column Configuration Schema

Each column object in the `columns` array supports:

```javascript
{
  // Required fields
  key: String,              // Data property key
  label: String,            // Display label (i18n key or text)
  
  // Sorting
  sortable: Boolean,        // Default: true
  
  // Layout
  width: String,            // CSS width (e.g., '150px', '20%')
  minWidth: String,         // CSS min-width (e.g., '100px')
  align: String,            // 'left' | 'center' | 'right' (default: 'left')
  
  // Sticky columns (optional feature)
  sticky: String,           // 'left' | 'right' | undefined
  
  // Responsive hiding (optional feature)
  responsive: String,       // 'always' | 'hide-below-1024' | 'hide-below-768'
  
  // Custom rendering
  // Use slot with name `cell-${key}` for custom content
}
```

**Example Column Definitions:**

```javascript
const columns = [
  {
    key: 'boat_number',
    label: 'Boat #',
    sortable: true,
    width: '100px',
    sticky: 'left',           // Optional: stays visible while scrolling
    responsive: 'always'       // Always visible
  },
  {
    key: 'event_type',
    label: 'Event',
    sortable: true,
    minWidth: '120px',
    responsive: 'always'
  },
  {
    key: 'team_manager_email',
    label: 'Email',
    sortable: true,
    responsive: 'hide-below-1024'  // Optional: hidden on tablets
  },
  {
    key: 'actions',
    label: 'Actions',
    sortable: false,
    width: '200px',
    align: 'right',
    sticky: 'right'           // Optional: actions always accessible
  }
]
```


#### Slot System

**Named Slots for Custom Cell Rendering:**

```vue
<!-- Parent component usage -->
<SortableTable :columns="columns" :data="boats">
  <!-- Custom cell rendering using slot -->
  <template #cell-boat_number="{ row, value, column }">
    <span v-if="value" class="boat-number-text">{{ value }}</span>
    <span v-else class="no-race-text">-</span>
  </template>
  
  <template #cell-status="{ row, value }">
    <StatusBadge :status="value" size="medium" />
  </template>
  
  <template #cell-actions="{ row }">
    <div class="action-buttons">
      <BaseButton size="small" @click="edit(row)">Edit</BaseButton>
      <BaseButton size="small" variant="danger" @click="delete(row)">Delete</BaseButton>
    </div>
  </template>
</SortableTable>
```

**Slot Props:**
- `row`: Complete row data object
- `value`: Cell value (row[column.key])
- `column`: Column definition object

**Default Behavior:**
- If no slot provided, displays raw value: `{{ row[column.key] }}`
- Handles null/undefined values gracefully

#### Events

```javascript
// Emitted when sort changes
emit('sort', {
  field: String,      // Column key being sorted
  direction: String   // 'asc' or 'desc'
})

// Emitted on horizontal scroll (for advanced use cases)
emit('scroll', {
  scrollLeft: Number,
  scrollWidth: Number,
  clientWidth: Number
})
```

## Data Models

### Column Definition Type

```javascript
/**
 * @typedef {Object} ColumnDefinition
 * @property {string} key - Data property key
 * @property {string} label - Display label
 * @property {boolean} [sortable=true] - Enable sorting
 * @property {string} [width] - CSS width value
 * @property {string} [minWidth] - CSS min-width value
 * @property {'left'|'center'|'right'} [align='left'] - Text alignment
 * @property {'left'|'right'} [sticky] - Sticky position (optional)
 * @property {'always'|'hide-below-1024'|'hide-below-768'} [responsive='always'] - Responsive behavior
 */
```

### Table Data Type

```javascript
/**
 * @typedef {Object} TableRow
 * @property {string} id - Unique identifier (optional, uses index if missing)
 * @property {*} [key] - Dynamic properties matching column keys
 */
```

## Styling Approach

### CSS Architecture


**1. Design Token Usage (100% compliance)**

All styling MUST use design tokens from `design-tokens.css`:

```css
/* Colors */
--color-primary, --color-success, --color-warning, --color-danger
--color-secondary, --color-light, --color-dark, --color-muted
--color-border, --color-bg-white, --color-bg-hover

/* Spacing */
--spacing-xs, --spacing-sm, --spacing-md, --spacing-lg
--spacing-xl, --spacing-xxl, --spacing-3xl

/* Typography */
--font-size-xs, --font-size-sm, --font-size-base, --font-size-lg
--font-weight-normal, --font-weight-medium, --font-weight-semibold

/* Table-specific */
--table-header-bg, --table-header-font-weight
--table-cell-padding-mobile, --table-cell-padding-desktop
--table-border-color, --table-hover-bg

/* Transitions */
--transition-fast, --transition-normal

/* Z-index */
--z-index-sticky
```

**2. Horizontal Scroll Implementation**

```css
.sortable-table-wrapper {
  width: 100%;
  overflow-x: auto;
  overflow-y: visible;
  -webkit-overflow-scrolling: touch;
  position: relative;
}

/* Visible scrollbar styling */
.sortable-table-wrapper::-webkit-scrollbar {
  height: 8px;
}

.sortable-table-wrapper::-webkit-scrollbar-track {
  background: var(--color-light);
  border-radius: 4px;
}

.sortable-table-wrapper::-webkit-scrollbar-thumb {
  background: var(--color-secondary);
  border-radius: 4px;
}

.sortable-table-wrapper::-webkit-scrollbar-thumb:hover {
  background: var(--color-dark);
}

/* Firefox scrollbar */
.sortable-table-wrapper {
  scrollbar-width: thin;
  scrollbar-color: var(--color-secondary) var(--color-light);
}
```

**3. Sticky Column Implementation**

```css
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

/* Visual separator for sticky columns */
.table-header.sticky-left::after,
.table-cell.sticky-left::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 1px;
  background: linear-gradient(
    to bottom,
    transparent,
    var(--color-border) 10%,
    var(--color-border) 90%,
    transparent
  );
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.05);
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

.table-header.sticky-right::before,
.table-cell.sticky-right::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 1px;
  background: linear-gradient(
    to bottom,
    transparent,
    var(--color-border) 10%,
    var(--color-border) 90%,
    transparent
  );
  box-shadow: -2px 0 4px rgba(0, 0, 0, 0.05);
}
```

**4. Responsive Column Hiding**

```css
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
```

**5. Compact Mode**

```css
/* Normal mode padding */
.table-header,
.table-cell {
  padding: var(--table-cell-padding-mobile);
}

@media (min-width: 768px) {
  .table-header,
  .table-cell {
    padding: var(--table-cell-padding-desktop);
  }
}

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

/* Maintain minimum touch targets */
.sortable-table-wrapper.compact-mode .table-cell button,
.sortable-table-wrapper.compact-mode .table-cell a {
  min-height: var(--touch-target-min-size);
  min-width: var(--touch-target-min-size);
}
```


## Migration Patterns

### Step-by-Step Migration Guide

**Phase 1: Preparation**
1. Review existing table implementation in the view
2. Identify all columns and their properties
3. Determine which columns should be sticky (if any)
4. Determine which columns can be hidden responsively (if any)
5. Document custom cell rendering requirements

**Phase 2: Column Configuration**
1. Create column definitions array
2. Map existing columns to new schema
3. Configure sticky columns based on user workflow analysis
4. Configure responsive hiding based on screen real estate
5. Set appropriate widths and alignments

**Phase 3: Implementation**
1. Replace custom table markup with `<SortableTable>`
2. Pass column definitions and data as props
3. Implement custom cell slots for badges, buttons, formatted data
4. Remove custom table CSS (now handled by component)
5. Test on multiple screen sizes

**Phase 4: Verification**
1. Test sorting functionality
2. Test horizontal scrolling on HDPI (1440x900) and MDPI (1024x768)
3. Test sticky columns (if configured)
4. Test responsive column hiding (if configured)
5. Verify card view still works (should be unchanged)
6. Test accessibility with keyboard and screen reader

### Migration Example: AdminBoats View

**Before (Custom Table):**

```vue
<template>
  <div class="boats-table-container">
    <TableScrollIndicator>
      <table class="boats-table">
        <thead>
          <tr>
            <th @click="sortBy('boat_number')">
              Boat #
              <span v-if="sortField === 'boat_number'">
                {{ sortDirection === 'asc' ? '▲' : '▼' }}
              </span>
            </th>
            <th @click="sortBy('event_type')">Event</th>
            <!-- ... more columns ... -->
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="boat in boats" :key="boat.id">
            <td>
              <span v-if="boat.boat_number" class="boat-number-cell">
                {{ boat.boat_number }}
              </span>
              <span v-else class="no-race-cell">-</span>
            </td>
            <td>{{ boat.event_type }}</td>
            <!-- ... more cells ... -->
            <td class="actions-cell">
              <BaseButton size="small" @click="edit(boat)">Edit</BaseButton>
            </td>
          </tr>
        </tbody>
      </table>
    </TableScrollIndicator>
  </div>
</template>

<script>
// Custom sorting logic
const sortBy = (field) => { /* ... */ }
</script>

<style>
/* Custom table styles (100+ lines) */
.boats-table { /* ... */ }
.boats-table th { /* ... */ }
/* ... */
</style>
```

**After (SortableTable):**

```vue
<template>
  <div class="boats-view">
    <SortableTable
      :columns="tableColumns"
      :data="boats"
      :initial-sort-field="'boat_number'"
      :initial-sort-direction="'asc'"
      :compact="compactMode"
      aria-label="Boats table"
      @sort="handleSort"
    >
      <!-- Custom cell: Boat number with styling -->
      <template #cell-boat_number="{ value }">
        <span v-if="value" class="boat-number-text">{{ value }}</span>
        <span v-else class="no-race-text">-</span>
      </template>
      
      <!-- Custom cell: Status badge -->
      <template #cell-status="{ row }">
        <StatusBadge :status="getBoatStatus(row)" size="medium" />
      </template>
      
      <!-- Custom cell: Actions -->
      <template #cell-actions="{ row }">
        <div class="action-buttons">
          <BaseButton size="small" variant="secondary" @click="editBoat(row)">
            {{ $t('admin.boats.assignBoat') }}
          </BaseButton>
          <BaseButton 
            size="small" 
            :variant="row.forfait ? 'secondary' : 'warning'"
            @click="toggleForfait(row)"
          >
            {{ row.forfait ? $t('admin.boats.removeForfait') : $t('admin.boats.setForfait') }}
          </BaseButton>
          <BaseButton 
            size="small" 
            variant="danger" 
            @click="deleteBoat(row)"
            :disabled="row.registration_status === 'paid'"
          >
            {{ $t('common.delete') }}
          </BaseButton>
        </div>
      </template>
    </SortableTable>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import SortableTable from '@/components/composite/SortableTable.vue'
import StatusBadge from '@/components/base/StatusBadge.vue'
import BaseButton from '@/components/base/BaseButton.vue'

const { t } = useI18n()

// Column definitions with sticky and responsive configuration
const tableColumns = computed(() => [
  {
    key: 'boat_number',
    label: t('admin.boats.boatNumber'),
    sortable: true,
    width: '100px',
    sticky: 'left',              // Sticky: always visible
    responsive: 'always'
  },
  {
    key: 'event_type',
    label: t('boat.eventType'),
    sortable: true,
    minWidth: '120px',
    responsive: 'always'
  },
  {
    key: 'boat_type',
    label: t('boat.boatType'),
    sortable: false,
    responsive: 'always'
  },
  {
    key: 'first_rower',
    label: t('boat.firstRower'),
    sortable: false,
    responsive: 'hide-below-1024'  // Hidden on tablets
  },
  {
    key: 'team_manager_name',
    label: t('admin.boats.teamManager'),
    sortable: true,
    responsive: 'hide-below-1024'
  },
  {
    key: 'team_manager_email',
    label: t('admin.boats.email'),
    sortable: false,
    responsive: 'hide-below-1024'
  },
  {
    key: 'boat_club_display',
    label: t('admin.boats.club'),
    sortable: true,
    responsive: 'always'
  },
  {
    key: 'boat_request_status',
    label: t('boat.boatRequest.status'),
    sortable: false,
    responsive: 'hide-below-1024'
  },
  {
    key: 'status',
    label: t('boat.status.label'),
    sortable: false,
    width: '120px',
    align: 'center',
    responsive: 'always'
  },
  {
    key: 'actions',
    label: t('common.actions'),
    sortable: false,
    width: '250px',
    align: 'right',
    sticky: 'right',             // Sticky: actions always accessible
    responsive: 'always'
  }
])

const handleSort = ({ field, direction }) => {
  console.log(`Sorted by ${field} ${direction}`)
  // Optional: persist sort state or emit to parent
}
</script>

<style scoped>
/* Minimal custom styles - most handled by SortableTable */
.action-buttons {
  display: flex;
  gap: var(--spacing-sm);
  flex-direction: column;
}
</style>
```

**Benefits of Migration:**
- ✅ Reduced code: ~200 lines → ~100 lines
- ✅ No custom table CSS needed
- ✅ Consistent styling across all views
- ✅ Horizontal scroll with visible scrollbar
- ✅ Sticky columns for better UX
- ✅ Responsive column hiding
- ✅ Accessibility built-in
- ✅ Easier maintenance


### Column Configuration Decision Matrix

When migrating a view, use this matrix to decide column configuration:

| Column Type | Sticky? | Responsive Hiding? | Reasoning |
|-------------|---------|-------------------|-----------|
| Identifier (boat #, ID) | Consider `sticky: 'left'` | `responsive: 'always'` | Users need context while scrolling |
| Primary data (name, type) | No | `responsive: 'always'` | Core information, always needed |
| Secondary data (email, phone) | No | `responsive: 'hide-below-1024'` | Nice to have, can hide on tablets |
| Metadata (dates, counts) | No | `responsive: 'hide-below-1024'` | Supplementary information |
| Status indicators | No | `responsive: 'always'` | Important for quick scanning |
| Actions | Consider `sticky: 'right'` | `responsive: 'always'` | Users need access to actions |

**Guidelines:**
- **Sticky columns**: Only use if users frequently need to reference that column while scrolling horizontally
- **Responsive hiding**: Only hide columns that are truly optional for the workflow
- **When in doubt**: Start with no sticky columns and no responsive hiding, add later if needed

### Backward Compatibility Strategy

The enhanced SortableTable maintains 100% backward compatibility:

1. **Existing props still work**: All current props (`columns`, `data`, `initialSortField`, etc.) unchanged
2. **New props are optional**: `compact`, sticky/responsive column configs are opt-in
3. **Default behavior preserved**: Without new configs, table behaves exactly as before
4. **Gradual adoption**: Views can migrate incrementally, using new features as needed

**Migration Priority:**
1. High-traffic admin views (AdminBoats, AdminCrewMembers)
2. Views with horizontal scroll issues
3. Views with many columns (>8 columns)
4. Lower-priority views as time permits

## Performance Considerations

### Rendering Performance

**Target Metrics:**
- 50 rows: < 500ms initial render
- 100 rows: < 1000ms initial render
- Horizontal scroll: > 30fps
- Sort operation: < 300ms

**Optimization Strategies:**

1. **Efficient Vue Reactivity**
   - Use `v-for` with stable `:key` (row.id or index)
   - Avoid unnecessary computed properties in tight loops
   - Use `v-once` for static content where appropriate

2. **CSS Performance**
   - Use `transform` and `opacity` for animations (GPU-accelerated)
   - Avoid layout thrashing with sticky positioning
   - Minimize repaints with `will-change` on scroll container

3. **Slot Rendering**
   - Slots are compiled efficiently by Vue 3
   - No performance penalty compared to inline rendering
   - Custom components (BaseButton, StatusBadge) already optimized

4. **Memory Management**
   - No memory leaks: component properly cleans up on unmount
   - Event listeners properly removed
   - No global state pollution

### Virtual Scrolling Evaluation

**Decision: NOT implementing virtual scrolling**

**Reasoning:**
- Current dataset sizes: 50-100 rows typical, 200 rows maximum
- Virtual scrolling adds complexity: windowing, scroll position management, dynamic heights
- Performance is acceptable without it: 100 rows renders in < 1 second
- Sticky columns complicate virtual scrolling implementation
- Pagination already limits visible rows

**Future Consideration:**
- If datasets grow to 500+ rows, revisit virtual scrolling
- Consider libraries like `vue-virtual-scroller` if needed
- Current architecture doesn't prevent future addition

### Scroll Performance

**Horizontal Scroll Optimization:**

```javascript
// Composable: useTableScroll.js
import { ref, onMounted, onUnmounted } from 'vue'

export function useTableScroll(wrapperRef) {
  const scrollLeft = ref(0)
  const isScrolling = ref(false)
  
  let scrollTimeout = null
  
  const handleScroll = (event) => {
    scrollLeft.value = event.target.scrollLeft
    
    // Debounce scroll events for performance
    isScrolling.value = true
    clearTimeout(scrollTimeout)
    scrollTimeout = setTimeout(() => {
      isScrolling.value = false
    }, 150)
  }
  
  onMounted(() => {
    if (wrapperRef.value) {
      wrapperRef.value.addEventListener('scroll', handleScroll, { passive: true })
    }
  })
  
  onUnmounted(() => {
    if (wrapperRef.value) {
      wrapperRef.value.removeEventListener('scroll', handleScroll)
    }
    clearTimeout(scrollTimeout)
  })
  
  return {
    scrollLeft,
    isScrolling
  }
}
```

**Benefits:**
- Passive event listeners for better scroll performance
- Debounced scroll state updates
- Proper cleanup on unmount


## Accessibility Implementation

### WCAG 2.1 Level AA Compliance

**1. Semantic HTML**

```vue
<table role="table" :aria-label="ariaLabel">
  <thead role="rowgroup">
    <tr role="row">
      <th 
        role="columnheader"
        :aria-sort="getSortState(column.key)"
        :tabindex="column.sortable !== false ? 0 : -1"
      >
        {{ column.label }}
      </th>
    </tr>
  </thead>
  <tbody role="rowgroup">
    <tr role="row">
      <td role="cell">{{ value }}</td>
    </tr>
  </tbody>
</table>
```

**2. Keyboard Navigation**

```javascript
// Composable: useTableKeyboard.js
import { onMounted, onUnmounted } from 'vue'

export function useTableKeyboard(tableRef, sortByField) {
  const handleKeyDown = (event) => {
    const target = event.target
    
    // Sort on Enter or Space for sortable headers
    if (target.tagName === 'TH' && target.hasAttribute('data-sortable')) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault()
        const field = target.getAttribute('data-field')
        sortByField(field)
      }
    }
    
    // Arrow key navigation between cells
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) {
      handleArrowNavigation(event)
    }
  }
  
  const handleArrowNavigation = (event) => {
    const target = event.target
    if (target.tagName !== 'TD' && target.tagName !== 'TH') return
    
    const cell = target
    const row = cell.parentElement
    const table = tableRef.value
    
    let nextCell = null
    
    switch (event.key) {
      case 'ArrowLeft':
        nextCell = cell.previousElementSibling
        break
      case 'ArrowRight':
        nextCell = cell.nextElementSibling
        break
      case 'ArrowUp':
        const prevRow = row.previousElementSibling
        if (prevRow) {
          const cellIndex = Array.from(row.children).indexOf(cell)
          nextCell = prevRow.children[cellIndex]
        }
        break
      case 'ArrowDown':
        const nextRow = row.nextElementSibling
        if (nextRow) {
          const cellIndex = Array.from(row.children).indexOf(cell)
          nextCell = nextRow.children[cellIndex]
        }
        break
    }
    
    if (nextCell) {
      event.preventDefault()
      nextCell.focus()
    }
  }
  
  onMounted(() => {
    if (tableRef.value) {
      tableRef.value.addEventListener('keydown', handleKeyDown)
    }
  })
  
  onUnmounted(() => {
    if (tableRef.value) {
      tableRef.value.removeEventListener('keydown', handleKeyDown)
    }
  })
}
```

**3. Screen Reader Support**

```vue
<th
  :aria-sort="isSortedBy(column.key) ? 
    (sortDirection === 'asc' ? 'ascending' : 'descending') : 
    'none'"
  :aria-label="`${column.label}${column.sortable !== false ? ', sortable' : ''}`"
>
  {{ column.label }}
  <span 
    v-if="column.sortable !== false" 
    class="sort-indicator"
    aria-hidden="true"
  >
    {{ getSortIndicator(column.key) }}
  </span>
</th>
```

**4. Focus Management**

```css
/* Visible focus indicators */
.table-header:focus,
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
```

**5. Color Contrast**

All text meets WCAG AA contrast requirements:
- Normal text: 4.5:1 minimum
- Large text (18px+): 3:1 minimum
- Interactive elements: 3:1 minimum

**6. Reduced Motion**

```css
@media (prefers-reduced-motion: reduce) {
  .sortable-table-wrapper,
  .table-row,
  .table-header {
    transition: none;
    animation: none;
  }
}
```

### Accessibility Testing Checklist

- [ ] All table elements have proper ARIA roles
- [ ] Sortable headers are keyboard accessible (Tab, Enter, Space)
- [ ] Sort state is announced to screen readers
- [ ] Arrow keys navigate between cells
- [ ] Focus indicators are visible
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] Works with screen readers (NVDA, JAWS, VoiceOver)
- [ ] Respects prefers-reduced-motion
- [ ] Interactive elements have 44px minimum touch targets


## Testing Strategy

### Dual Testing Approach

The testing strategy combines unit tests for specific scenarios and property-based tests for universal behaviors:

**Unit Tests:**
- Specific examples and edge cases
- Component mounting and rendering
- Event emission verification
- Accessibility compliance checks
- Performance benchmarks

**Property-Based Tests:**
- Universal behaviors across all inputs
- Column configuration variations
- Data type handling
- Responsive behavior patterns
- Minimum 100 iterations per property test

### Test Organization

```
tests/
├── unit/
│   └── components/
│       └── SortableTable.spec.js
├── integration/
│   └── table-migration.spec.js
└── e2e/
    └── admin-boats-table.spec.js
```

### Testing Tools

- **Vue Test Utils**: Component testing
- **Vitest**: Test runner
- **Testing Library**: DOM queries and user interactions
- **Axe-core**: Accessibility testing
- **Playwright**: E2E testing for visual regression

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified the following redundancies:
- Requirements 2.3 is redundant with 2.1 and 2.2 (sticky positioning)
- Requirements 4.5 is redundant with 1.1 (horizontal scroll activation)
- Requirements 6.6 is redundant with 6.1 (no hardcoded colors)
- Requirements 6.7 is redundant with 6.2 (no hardcoded spacing)

These redundant properties have been consolidated into comprehensive properties below.

### Core Table Rendering Properties

**Property 1: Semantic HTML Structure**
*For any* table configuration, the rendered DOM SHALL contain semantic HTML elements (table, thead, tbody, th, td) in the correct hierarchy.
**Validates: Requirements 9.1**

**Property 2: Column Rendering Completeness**
*For any* array of column definitions and data rows, the table SHALL render exactly one header cell per column and one data cell per column per row.
**Validates: Requirements 7.3**

**Property 3: Default Cell Value Display**
*For any* column without a custom slot, the table SHALL display the raw value from row[column.key].
**Validates: Requirements 7.3**

**Property 4: Custom Slot Rendering**
*For any* column with a provided slot, the table SHALL render the slot content instead of the raw value.
**Validates: Requirements 7.1**

### Horizontal Scrolling Properties

**Property 5: Scrollbar Visibility When Needed**
*For any* table where total column width exceeds container width, a horizontal scrollbar SHALL be displayed.
**Validates: Requirements 1.1**

**Property 6: No Scrollbar When Not Needed**
*For any* table where total column width fits within container width, no horizontal scrollbar SHALL be displayed.
**Validates: Requirements 1.7**

**Property 7: Design Token Usage for Scrollbar**
*For any* rendered scrollbar, all styling properties (colors, dimensions) SHALL reference CSS custom properties (design tokens) rather than hardcoded values.
**Validates: Requirements 1.4**

### Sticky Column Properties

**Property 8: Sticky Left Positioning**
*For any* column marked with sticky: 'left', the column SHALL maintain position: sticky with left: 0 and remain visible during horizontal scroll.
**Validates: Requirements 2.1**

**Property 9: Sticky Right Positioning**
*For any* column marked with sticky: 'right', the column SHALL maintain position: sticky with right: 0 and remain visible during horizontal scroll.
**Validates: Requirements 2.2**

**Property 10: Sticky Column Order Preservation**
*For any* set of multiple sticky columns on the same side, their relative DOM order SHALL be preserved in the rendered output.
**Validates: Requirements 2.5**

**Property 11: Optional Sticky Configuration**
*For any* column without a sticky property, the column SHALL NOT have position: sticky applied.
**Validates: Requirements 2.6**

### Responsive Column Hiding Properties

**Property 12: Responsive Column Visibility**
*For any* column with responsive configuration, the column's visibility SHALL change based on viewport width matching the configured breakpoint.
**Validates: Requirements 3.1**

**Property 13: Responsive Configuration Respected**
*For any* column with responsive: 'hide-below-1024', the column SHALL be hidden when viewport width < 1024px and visible when >= 1024px.
**Validates: Requirements 3.7**

**Property 14: Sorting Unaffected by Hidden Columns**
*For any* hidden column that is sortable, clicking its header (if visible at larger viewport) SHALL still sort the data correctly.
**Validates: Requirements 3.5**

### Column Width Properties

**Property 15: Width Property Application**
*For any* column with a width property, the rendered th/td elements SHALL have that width value applied in their computed styles.
**Validates: Requirements 4.1**

**Property 16: MinWidth Property Application**
*For any* column with a minWidth property, the rendered th/td elements SHALL have that min-width value applied in their computed styles.
**Validates: Requirements 4.2**

**Property 17: Multiple Width Unit Support**
*For any* column width specified in px, %, or other valid CSS units, the table SHALL render correctly with that unit type.
**Validates: Requirements 4.6**

### Compact Mode Properties

**Property 18: Compact Mode Padding Reduction**
*For any* table with compact: true, all cell padding values SHALL be 50% of the normal mode padding values.
**Validates: Requirements 5.1**

**Property 19: Compact Mode Toggleability**
*For any* table, toggling the compact prop SHALL immediately update the CSS class and padding without page reload.
**Validates: Requirements 5.3**

### Design Token Integration Properties

**Property 20: No Hardcoded Colors**
*For any* CSS property in the SortableTable component that specifies a color, the value SHALL be a CSS custom property (var(--color-*)) rather than a hex, rgb, or named color value.
**Validates: Requirements 6.1, 6.6**

**Property 21: No Hardcoded Spacing**
*For any* CSS property in the SortableTable component that specifies spacing (padding, margin, gap), the value SHALL be a CSS custom property (var(--spacing-*)) rather than a hardcoded pixel or rem value.
**Validates: Requirements 6.2, 6.7**

**Property 22: No Hardcoded Typography**
*For any* CSS property in the SortableTable component that specifies typography (font-size, font-weight, line-height), the value SHALL be a CSS custom property (var(--font-*)) rather than a hardcoded value.
**Validates: Requirements 6.3**

**Property 23: No Hardcoded Borders and Shadows**
*For any* CSS property in the SortableTable component that specifies border-radius or box-shadow, the value SHALL be a CSS custom property rather than a hardcoded value.
**Validates: Requirements 6.4**

### Sorting Properties

**Property 24: Sortable Column Activation**
*For any* sortable column header that is clicked, the table data SHALL be re-ordered based on that column's values.
**Validates: Requirements 8.1**

**Property 25: Sort Direction Toggle**
*For any* column that is already sorted, clicking its header again SHALL toggle the sort direction between ascending and descending.
**Validates: Requirements 8.2**

**Property 26: Non-Sortable Column Immunity**
*For any* column with sortable: false, clicking its header SHALL NOT trigger any sort operation or emit sort events.
**Validates: Requirements 8.4**

**Property 27: Multi-Type Sorting Support**
*For any* column containing string, number, or date values, the sorting algorithm SHALL correctly order the values according to their data type.
**Validates: Requirements 8.5**

### Accessibility Properties

**Property 28: Keyboard Header Activation**
*For any* sortable column header, pressing Enter or Space while focused SHALL trigger the sort operation.
**Validates: Requirements 9.2**

**Property 29: Arrow Key Cell Navigation**
*For any* focused table cell, pressing arrow keys SHALL move focus to the adjacent cell in the corresponding direction (up, down, left, right).
**Validates: Requirements 9.5**

### Backward Compatibility Properties

**Property 30: Existing Props Compatibility**
*For any* table using only the original props (columns, data, initialSortField, initialSortDirection, hoverable), the table SHALL render and function identically to the pre-enhancement version.
**Validates: Requirements 12.1**

**Property 31: Gradual Feature Adoption**
*For any* table that omits the new optional props (compact, sticky configs, responsive configs), the table SHALL function correctly with default behavior.
**Validates: Requirements 12.6**


## Error Handling

### Component Error Boundaries

**Invalid Props Handling:**

```javascript
// Validate column definitions
const validateColumns = (columns) => {
  if (!Array.isArray(columns)) {
    console.error('[SortableTable] columns prop must be an array')
    return false
  }
  
  for (const col of columns) {
    if (!col.key) {
      console.error('[SortableTable] Each column must have a "key" property', col)
      return false
    }
    if (!col.label) {
      console.error('[SortableTable] Each column must have a "label" property', col)
      return false
    }
    if (col.sticky && !['left', 'right'].includes(col.sticky)) {
      console.error('[SortableTable] sticky must be "left" or "right"', col)
      return false
    }
    if (col.responsive && !['always', 'hide-below-1024', 'hide-below-768'].includes(col.responsive)) {
      console.error('[SortableTable] responsive must be "always", "hide-below-1024", or "hide-below-768"', col)
      return false
    }
  }
  
  return true
}
```

**Data Handling:**

```javascript
// Handle missing or invalid data gracefully
const safeData = computed(() => {
  if (!Array.isArray(props.data)) {
    console.warn('[SortableTable] data prop must be an array, received:', typeof props.data)
    return []
  }
  return props.data
})

// Handle missing cell values
const getCellValue = (row, columnKey) => {
  const value = row[columnKey]
  return value !== undefined && value !== null ? value : ''
}
```

**Sort Error Handling:**

```javascript
const sortBy = (field) => {
  try {
    sortByField(field)
    emit('sort', {
      field: sortField.value,
      direction: sortDirection.value
    })
  } catch (error) {
    console.error('[SortableTable] Sort operation failed:', error)
    // Maintain current sort state on error
  }
}
```

### User-Facing Error States

**Empty Data State:**

```vue
<tbody v-if="sortedData.length === 0">
  <tr>
    <td :colspan="columns.length" class="empty-state">
      <slot name="empty">
        {{ $t('common.noData') }}
      </slot>
    </td>
  </tr>
</tbody>
```

**Loading State (Optional Slot):**

```vue
<div v-if="loading" class="table-loading">
  <slot name="loading">
    <LoadingSpinner />
  </slot>
</div>
```

## Implementation Details

### Component File Structure

```vue
<!-- SortableTable.vue -->
<template>
  <div 
    ref="wrapperRef"
    :class="[
      'sortable-table-wrapper',
      { 'compact-mode': compact }
    ]"
    :aria-label="ariaLabel"
  >
    <div class="table-container">
      <table 
        ref="tableRef"
        class="sortable-table"
        role="table"
      >
        <thead role="rowgroup">
          <tr role="row">
            <th
              v-for="column in columns"
              :key="column.key"
              role="columnheader"
              :class="getHeaderClass(column)"
              :style="getColumnStyle(column)"
              :aria-sort="getAriaSort(column.key)"
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
            :class="getRowClass(row)"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              role="cell"
              :class="getCellClass(column)"
              :style="getColumnStyle(column)"
              tabindex="0"
            >
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
</template>

<script setup>
import { ref, computed, toRef } from 'vue'
import { useTableSort } from '@/composables/useTableSort'
import { useTableScroll } from '@/composables/useTableScroll'
import { useTableKeyboard } from '@/composables/useTableKeyboard'

const props = defineProps({
  columns: {
    type: Array,
    required: true,
    validator: (columns) => {
      return columns.every(col => col.key && col.label)
    }
  },
  data: {
    type: Array,
    required: true
  },
  initialSortField: {
    type: String,
    default: ''
  },
  initialSortDirection: {
    type: String,
    default: 'asc',
    validator: (value) => ['asc', 'desc'].includes(value)
  },
  hoverable: {
    type: Boolean,
    default: true
  },
  compact: {
    type: Boolean,
    default: false
  },
  ariaLabel: {
    type: String,
    default: 'Data table'
  }
})

const emit = defineEmits(['sort', 'scroll'])

// Refs
const wrapperRef = ref(null)
const tableRef = ref(null)

// Composables
const dataRef = toRef(props, 'data')
const {
  sortField,
  sortDirection,
  sortedData,
  sortBy: sortByField,
  isSortedBy,
  getSortIndicator
} = useTableSort(dataRef, props.initialSortField, props.initialSortDirection)

const { scrollLeft } = useTableScroll(wrapperRef, emit)

useTableKeyboard(tableRef, sortByField)

// Methods
const sortBy = (field) => {
  sortByField(field)
  emit('sort', {
    field: sortField.value,
    direction: sortDirection.value
  })
}

const getHeaderClass = (column) => {
  return [
    'table-header',
    {
      'sortable': column.sortable !== false,
      'sorted': isSortedBy(column.key),
      [`align-${column.align || 'left'}`]: true,
      [`sticky-${column.sticky}`]: column.sticky,
      [`column-${column.responsive || 'always'}`]: true
    }
  ]
}

const getCellClass = (column) => {
  return [
    'table-cell',
    `align-${column.align || 'left'}`,
    {
      [`sticky-${column.sticky}`]: column.sticky,
      [`column-${column.responsive || 'always'}`]: true
    }
  ]
}

const getRowClass = (row) => {
  return [
    'table-row',
    {
      'hoverable': props.hoverable,
      [`status-${row.registration_status}`]: row.registration_status
    }
  ]
}

const getColumnStyle = (column) => {
  const style = {}
  if (column.width) style.width = column.width
  if (column.minWidth) style.minWidth = column.minWidth
  return style
}

const getAriaSort = (columnKey) => {
  if (!isSortedBy(columnKey)) return 'none'
  return sortDirection.value === 'asc' ? 'ascending' : 'descending'
}
</script>

<style scoped>
/* Styles already defined in previous sections */
/* See "Styling Approach" section for complete CSS */
</style>
```

### Composable: useTableScroll

```javascript
// composables/useTableScroll.js
import { ref, onMounted, onUnmounted } from 'vue'

export function useTableScroll(wrapperRef, emit) {
  const scrollLeft = ref(0)
  const isScrolling = ref(false)
  
  let scrollTimeout = null
  
  const handleScroll = (event) => {
    scrollLeft.value = event.target.scrollLeft
    
    // Emit scroll event for advanced use cases
    emit('scroll', {
      scrollLeft: event.target.scrollLeft,
      scrollWidth: event.target.scrollWidth,
      clientWidth: event.target.clientWidth
    })
    
    // Debounce scroll state
    isScrolling.value = true
    clearTimeout(scrollTimeout)
    scrollTimeout = setTimeout(() => {
      isScrolling.value = false
    }, 150)
  }
  
  onMounted(() => {
    if (wrapperRef.value) {
      wrapperRef.value.addEventListener('scroll', handleScroll, { passive: true })
    }
  })
  
  onUnmounted(() => {
    if (wrapperRef.value) {
      wrapperRef.value.removeEventListener('scroll', handleScroll)
    }
    clearTimeout(scrollTimeout)
  })
  
  return {
    scrollLeft,
    isScrolling
  }
}
```

### Composable: useTableKeyboard

```javascript
// composables/useTableKeyboard.js
import { onMounted, onUnmounted } from 'vue'

export function useTableKeyboard(tableRef, sortByField) {
  const handleKeyDown = (event) => {
    const target = event.target
    
    // Sort on Enter or Space for sortable headers
    if (target.tagName === 'TH' && target.getAttribute('data-sortable') === 'true') {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault()
        const field = target.getAttribute('data-field')
        sortByField(field)
      }
    }
    
    // Arrow key navigation between cells
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) {
      handleArrowNavigation(event)
    }
  }
  
  const handleArrowNavigation = (event) => {
    const target = event.target
    if (target.tagName !== 'TD' && target.tagName !== 'TH') return
    
    const cell = target
    const row = cell.parentElement
    
    let nextCell = null
    
    switch (event.key) {
      case 'ArrowLeft':
        nextCell = cell.previousElementSibling
        break
      case 'ArrowRight':
        nextCell = cell.nextElementSibling
        break
      case 'ArrowUp': {
        const prevRow = row.previousElementSibling
        if (prevRow) {
          const cellIndex = Array.from(row.children).indexOf(cell)
          nextCell = prevRow.children[cellIndex]
        }
        break
      }
      case 'ArrowDown': {
        const nextRow = row.nextElementSibling
        if (nextRow) {
          const cellIndex = Array.from(row.children).indexOf(cell)
          nextCell = nextRow.children[cellIndex]
        }
        break
      }
    }
    
    if (nextCell) {
      event.preventDefault()
      nextCell.focus()
    }
  }
  
  onMounted(() => {
    if (tableRef.value) {
      tableRef.value.addEventListener('keydown', handleKeyDown)
    }
  })
  
  onUnmounted(() => {
    if (tableRef.value) {
      tableRef.value.removeEventListener('keydown', handleKeyDown)
    }
  })
}
```

## Summary

This design provides a comprehensive enhancement to the SortableTable component that:

1. **Solves horizontal scroll issues** with visible, styled scrollbars on HDPI/MDPI screens
2. **Adds optional sticky columns** for improved UX when scrolling wide tables
3. **Supports optional responsive column hiding** to optimize for different screen sizes
4. **Maintains 100% backward compatibility** with existing implementations
5. **Uses design tokens exclusively** for consistent styling
6. **Implements full accessibility** with keyboard navigation and ARIA support
7. **Provides flexible customization** through slots and column configuration
8. **Includes clear migration patterns** for converting existing custom tables
9. **Optimizes performance** for 50-100 row datasets without virtual scrolling
10. **Preserves card view implementations** without modification

The design enables incremental migration of 9 priority views, starting with high-traffic admin views (AdminBoats, AdminCrewMembers, PaymentHistory) and progressing through medium and low-priority views. Each migration will reduce code duplication, improve consistency, and enhance the user experience across the application.

