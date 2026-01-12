<template>
  <div class="sortable-table-wrapper">
    <div class="table-container">
      <table class="sortable-table">
        <thead>
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              :class="[
                'table-header',
                {
                  'sortable': column.sortable !== false,
                  'sorted': isSortedBy(column.key),
                  [`align-${column.align || 'left'}`]: true
                }
              ]"
              :style="column.width ? { width: column.width } : {}"
              @click="column.sortable !== false ? sortBy(column.key) : null"
            >
              <span class="header-content">
                {{ column.label }}
                <span v-if="column.sortable !== false" class="sort-indicator">
                  {{ getSortIndicator(column.key) }}
                </span>
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, index) in sortedData"
            :key="row.id || index"
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
              :class="[
                'table-cell',
                `align-${column.align || 'left'}`
              ]"
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
</template>

<script setup>
import { toRef } from 'vue'
import { useTableSort } from '@/composables/useTableSort'

const props = defineProps({
  // Column definitions with key, label, sortable, width, align
  columns: {
    type: Array,
    required: true,
    validator: (columns) => {
      return columns.every(col => col.key && col.label)
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
  }
})

const emit = defineEmits(['sort'])

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

// Wrap sortBy to emit event
const sortBy = (field) => {
  sortByField(field)
  emit('sort', {
    field: sortField.value,
    direction: sortDirection.value
  })
}
</script>

<style scoped>
.sortable-table-wrapper {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.table-container {
  min-width: 100%;
  display: inline-block;
}

.sortable-table {
  width: 100%;
  border-collapse: collapse;
  background-color: var(--color-bg-white, #ffffff);
}

/* Table Header */
.table-header {
  background-color: var(--table-header-bg, #f8f9fa);
  font-weight: var(--table-header-font-weight, 600);
  font-size: var(--font-size-base, 0.875rem);
  color: var(--color-dark, #212529);
  text-align: left;
  padding: var(--table-cell-padding-mobile, 0.75rem);
  border-bottom: 1px solid var(--table-border-color, #dee2e6);
  white-space: nowrap;
  user-select: none;
}

.table-header.sortable {
  cursor: pointer;
  transition: background-color var(--transition-fast, 0.15s ease);
}

.table-header.sortable:hover {
  background-color: var(--color-bg-hover, rgba(0, 0, 0, 0.05));
}

.table-header.sorted {
  color: var(--color-primary, #007bff);
}

.header-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 0.5rem);
}

.sort-indicator {
  font-size: var(--font-size-xs, 0.75rem);
  color: var(--color-primary, #007bff);
  min-width: 12px;
  display: inline-block;
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
  border-bottom: 1px solid var(--table-border-color, #dee2e6);
  transition: background-color var(--transition-fast, 0.15s ease);
}

.table-row.hoverable:hover {
  background-color: var(--table-hover-bg, #f8f9fa);
}

/* Status-based row styling (left border) */
.table-row.status-incomplete {
  border-left: 4px solid var(--color-warning, #ffc107);
}

.table-row.status-complete {
  border-left: 4px solid var(--color-success, #28a745);
}

.table-row.status-paid {
  border-left: 4px solid var(--color-primary, #007bff);
}

.table-row.status-forfait {
  border-left: 4px solid var(--color-danger, #dc3545);
}

.table-cell {
  padding: var(--table-cell-padding-mobile, 0.75rem);
  font-size: var(--font-size-base, 0.875rem);
  color: var(--color-dark, #212529);
  vertical-align: middle;
}

/* Responsive adjustments */
@media (min-width: 768px) {
  .table-header,
  .table-cell {
    padding: var(--table-cell-padding-desktop, 1rem);
  }
}

/* Mobile: Show scroll indicator */
@media (max-width: 767px) {
  .sortable-table-wrapper {
    position: relative;
  }
  
  .sortable-table-wrapper::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    width: 20px;
    background: linear-gradient(to left, rgba(255, 255, 255, 0.9), transparent);
    pointer-events: none;
  }
  
  .sortable-table-wrapper::-webkit-scrollbar {
    height: 6px;
  }
  
  .sortable-table-wrapper::-webkit-scrollbar-track {
    background: var(--color-light, #f8f9fa);
  }
  
  .sortable-table-wrapper::-webkit-scrollbar-thumb {
    background: var(--color-secondary, #6c757d);
    border-radius: 3px;
  }
}
</style>
