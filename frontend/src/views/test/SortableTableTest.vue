<template>
  <div class="sortable-table-test">
    <div class="test-header">
      <h1>SortableTable Component Test Page</h1>
      <p>Test all features on different screen sizes (HDPI: 1440x900, MDPI: 1024x768, Tablet: 768px)</p>
    </div>

    <div class="test-controls">
      <label>
        <input type="checkbox" v-model="compactMode" />
        Compact Mode
      </label>
      <label>
        <input type="checkbox" v-model="showSticky" />
        Sticky Columns
      </label>
      <label>
        <input type="checkbox" v-model="showResponsive" />
        Responsive Hiding
      </label>
    </div>

    <div class="test-section">
      <h2>Test 1: All Features Combined</h2>
      <p>Sticky columns (ID left, Actions right), responsive hiding, compact mode, custom widths</p>
      
      <SortableTable
        :columns="allFeaturesColumns"
        :data="sampleData"
        :compact="compactMode"
        :initial-sort-field="'name'"
        :initial-sort-direction="'asc'"
        aria-label="All features test table"
        @sort="handleSort"
      >
        <template #cell-id="{ value }">
          <span class="boat-number-text">{{ value }}</span>
        </template>
        
        <template #cell-status="{ value }">
          <span :class="`badge badge-${value}`">{{ value }}</span>
        </template>
        
        <template #cell-actions="{ row }">
          <div class="action-buttons">
            <button class="btn-small btn-secondary">Edit</button>
            <button class="btn-small btn-danger">Delete</button>
          </div>
        </template>
      </SortableTable>
    </div>

    <div class="test-section">
      <h2>Test 2: Horizontal Scrolling</h2>
      <p>Wide table with many columns to test horizontal scroll</p>
      
      <SortableTable
        :columns="wideTableColumns"
        :data="sampleData"
        :compact="compactMode"
        aria-label="Wide table test"
      />
    </div>

    <div class="test-section">
      <h2>Test 3: Backward Compatibility</h2>
      <p>Minimal props - should work exactly like original SortableTable</p>
      
      <SortableTable
        :columns="minimalColumns"
        :data="sampleData"
      />
    </div>

    <div class="test-section">
      <h2>Test 4: Empty Data</h2>
      <p>Table with no data rows</p>
      
      <SortableTable
        :columns="minimalColumns"
        :data="[]"
      />
    </div>

    <div class="test-section">
      <h2>Test 5: Null Values</h2>
      <p>Table with null and undefined values</p>
      
      <SortableTable
        :columns="minimalColumns"
        :data="nullData"
      />
    </div>

    <div class="test-info">
      <h3>Screen Size Information</h3>
      <p>Current viewport: {{ viewportWidth }}px × {{ viewportHeight }}px</p>
      <p>Screen category: {{ screenCategory }}</p>
      <ul>
        <li>HDPI: 1440x900 or larger</li>
        <li>MDPI: 1024x768 to 1439x899</li>
        <li>Tablet: 768px to 1023px</li>
        <li>Mobile: < 768px</li>
      </ul>
    </div>

    <div class="test-info">
      <h3>Last Sort Event</h3>
      <pre>{{ lastSortEvent }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import SortableTable from '@/components/composite/SortableTable.vue'

// Test controls
const compactMode = ref(false)
const showSticky = ref(true)
const showResponsive = ref(true)

// Viewport tracking
const viewportWidth = ref(window.innerWidth)
const viewportHeight = ref(window.innerHeight)

const screenCategory = computed(() => {
  if (viewportWidth.value >= 1440) return 'HDPI (1440x900+)'
  if (viewportWidth.value >= 1024) return 'MDPI (1024x768 - 1439x899)'
  if (viewportWidth.value >= 768) return 'Tablet (768px - 1023px)'
  return 'Mobile (< 768px)'
})

const updateViewport = () => {
  viewportWidth.value = window.innerWidth
  viewportHeight.value = window.innerHeight
}

onMounted(() => {
  window.addEventListener('resize', updateViewport)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateViewport)
})

// Sample data
const sampleData = ref([
  {
    id: 1,
    name: 'Alice Johnson',
    email: 'alice@example.com',
    phone: '555-0101',
    age: 28,
    department: 'Engineering',
    status: 'active',
    city: 'New York',
    country: 'USA'
  },
  {
    id: 2,
    name: 'Bob Smith',
    email: 'bob@example.com',
    phone: '555-0102',
    age: 35,
    department: 'Marketing',
    status: 'inactive',
    city: 'Los Angeles',
    country: 'USA'
  },
  {
    id: 3,
    name: 'Charlie Brown',
    email: 'charlie@example.com',
    phone: '555-0103',
    age: 42,
    department: 'Sales',
    status: 'active',
    city: 'Chicago',
    country: 'USA'
  },
  {
    id: 4,
    name: 'Diana Prince',
    email: 'diana@example.com',
    phone: '555-0104',
    age: 31,
    department: 'Engineering',
    status: 'active',
    city: 'San Francisco',
    country: 'USA'
  },
  {
    id: 5,
    name: 'Eve Anderson',
    email: 'eve@example.com',
    phone: '555-0105',
    age: 29,
    department: 'Design',
    status: 'inactive',
    city: 'Seattle',
    country: 'USA'
  }
])

const nullData = ref([
  { id: 1, name: 'Alice', email: null },
  { id: 2, name: null, email: 'bob@example.com' },
  { id: 3, name: undefined, email: undefined }
])

// Column configurations
const allFeaturesColumns = computed(() => [
  {
    key: 'id',
    label: 'ID',
    sortable: true,
    width: '80px',
    sticky: showSticky.value ? 'left' : undefined,
    responsive: 'always'
  },
  {
    key: 'name',
    label: 'Name',
    sortable: true,
    minWidth: '150px',
    responsive: 'always'
  },
  {
    key: 'email',
    label: 'Email',
    sortable: true,
    width: '200px',
    responsive: showResponsive.value ? 'hide-below-1024' : 'always'
  },
  {
    key: 'phone',
    label: 'Phone',
    sortable: false,
    width: '120px',
    responsive: showResponsive.value ? 'hide-below-1024' : 'always'
  },
  {
    key: 'age',
    label: 'Age',
    sortable: true,
    width: '80px',
    align: 'center',
    responsive: 'always'
  },
  {
    key: 'department',
    label: 'Department',
    sortable: true,
    minWidth: '120px',
    responsive: showResponsive.value ? 'hide-below-768' : 'always'
  },
  {
    key: 'status',
    label: 'Status',
    sortable: false,
    width: '100px',
    align: 'center',
    responsive: 'always'
  },
  {
    key: 'actions',
    label: 'Actions',
    sortable: false,
    width: '180px',
    align: 'right',
    sticky: showSticky.value ? 'right' : undefined,
    responsive: 'always'
  }
])

const wideTableColumns = computed(() => [
  { key: 'id', label: 'ID', width: '80px' },
  { key: 'name', label: 'Name', width: '200px' },
  { key: 'email', label: 'Email', width: '250px' },
  { key: 'phone', label: 'Phone', width: '150px' },
  { key: 'age', label: 'Age', width: '100px' },
  { key: 'department', label: 'Department', width: '200px' },
  { key: 'city', label: 'City', width: '150px' },
  { key: 'country', label: 'Country', width: '150px' },
  { key: 'status', label: 'Status', width: '120px' }
])

const minimalColumns = ref([
  { key: 'id', label: 'ID', sortable: true },
  { key: 'name', label: 'Name', sortable: true },
  { key: 'email', label: 'Email', sortable: true }
])

// Event handling
const lastSortEvent = ref(null)

const handleSort = (event) => {
  lastSortEvent.value = event
  console.log('Sort event:', event)
}
</script>

<style scoped>
.sortable-table-test {
  padding: var(--spacing-xl);
  max-width: 100%;
}

.test-header {
  margin-bottom: var(--spacing-xl);
}

.test-header h1 {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
  margin-bottom: var(--spacing-sm);
}

.test-header p {
  color: var(--color-muted);
  font-size: var(--font-size-base);
}

.test-controls {
  display: flex;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-md);
  background-color: var(--color-light);
  border-radius: var(--border-radius-md);
}

.test-controls label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-base);
  cursor: pointer;
}

.test-section {
  margin-bottom: var(--spacing-3xl);
}

.test-section h2 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
  margin-bottom: var(--spacing-sm);
}

.test-section p {
  color: var(--color-muted);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-md);
}

.test-info {
  margin-top: var(--spacing-xl);
  padding: var(--spacing-md);
  background-color: var(--color-light);
  border-radius: var(--border-radius-md);
}

.test-info h3 {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
  margin-bottom: var(--spacing-sm);
}

.test-info p {
  font-size: var(--font-size-base);
  color: var(--color-dark);
  margin-bottom: var(--spacing-xs);
}

.test-info ul {
  list-style: disc;
  padding-left: var(--spacing-lg);
  color: var(--color-muted);
  font-size: var(--font-size-sm);
}

.test-info pre {
  background-color: var(--color-bg-white);
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
  overflow-x: auto;
}

/* Custom badge styling for test */
.badge {
  display: inline-block;
  padding: var(--badge-padding);
  font-size: var(--badge-font-size);
  font-weight: var(--font-weight-medium);
  border-radius: var(--badge-border-radius);
  width: fit-content;
}

.badge-active {
  background-color: var(--color-success);
  color: white;
}

.badge-inactive {
  background-color: var(--color-secondary);
  color: white;
}

/* Custom button styling for test */
.action-buttons {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: flex-end;
}

.btn-small {
  padding: var(--button-padding-sm);
  font-size: var(--font-size-sm);
  border-radius: var(--border-radius-sm);
  border: none;
  cursor: pointer;
  min-height: var(--button-min-height-sm);
  transition: background-color var(--transition-fast);
}

.btn-secondary {
  background-color: var(--color-secondary);
  color: white;
}

.btn-secondary:hover {
  background-color: var(--color-dark);
}

.btn-danger {
  background-color: var(--color-danger);
  color: white;
}

.btn-danger:hover {
  opacity: 0.9;
}

.boat-number-text {
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}
</style>
