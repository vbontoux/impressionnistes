<template>
  <div class="list-filters">
    <div class="search-row">
      <input
        :value="localSearchQuery"
        @input="handleSearchInput"
        type="text"
        :placeholder="searchPlaceholder"
        class="search-input"
      />
      <button @click="$emit('clear')" class="filter-btn clear-btn">
        {{ clearLabel || $t('admin.boats.clearFilters') }}
      </button>
    </div>
    
    <div v-if="$slots.filters" class="filter-row">
      <slot name="filters"></slot>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  },
  searchPlaceholder: {
    type: String,
    default: ''
  },
  clearLabel: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:searchQuery', 'clear'])

// Local search query for immediate UI feedback
const localSearchQuery = ref(props.searchQuery)

// Debounce timer
let debounceTimer = null

// Handle search input with debouncing
const handleSearchInput = (event) => {
  const value = event.target.value
  localSearchQuery.value = value
  
  // Clear existing timer
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  
  // Set new timer - emit after 300ms of no typing
  debounceTimer = setTimeout(() => {
    emit('update:searchQuery', value)
  }, 300)
}

// Watch for external changes (e.g., clear filters)
watch(() => props.searchQuery, (newValue) => {
  localSearchQuery.value = newValue
})
</script>

<style scoped>
.list-filters {
  background: var(--color-bg-white);
  padding: var(--spacing-lg);
  border-radius: var(--card-border-radius);
  margin-bottom: var(--spacing-xl);
  box-shadow: var(--card-shadow);
}

.search-row {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.search-input {
  flex: 1;
  padding: var(--form-input-padding);
  border: 1px solid var(--form-input-border-color);
  border-radius: var(--form-input-border-radius);
  font-size: var(--font-size-lg);
  min-height: var(--form-input-min-height);
  background: var(--color-bg-white);
}

.search-input::placeholder {
  color: #999;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
  align-items: end; /* Align items to bottom so filters align properly */
}

.filter-btn {
  padding: var(--form-input-padding) var(--spacing-lg);
  border: 1px solid var(--form-input-border-color);
  background: var(--color-bg-white);
  border-radius: var(--form-input-border-radius);
  cursor: pointer;
  font-size: var(--font-size-base);
  white-space: nowrap;
  transition: var(--transition-slow);
  min-height: var(--form-input-min-height);
}

.filter-btn:hover {
  background: var(--color-bg-light);
}

.filter-btn:active {
  background: var(--color-light);
}

.clear-btn {
  flex-shrink: 0;
  min-width: 150px;
}

/* Global styles for filter groups and selects used in slot */
:deep(.filter-group) {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  min-width: 200px;
}

:deep(.filter-group label) {
  font-weight: var(--font-weight-medium);
  color: var(--color-dark);
  font-size: var(--font-size-base);
  white-space: nowrap;
}

:deep(.filter-select),
:deep(.filter-input) {
  padding: var(--form-input-padding);
  border: 1px solid var(--form-input-border-color);
  border-radius: var(--form-input-border-radius);
  font-size: var(--font-size-base);
  min-height: var(--form-input-min-height);
  background: var(--color-bg-white); /* Always white background */
  cursor: pointer;
}

:deep(.filter-select:focus),
:deep(.filter-input:focus) {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .list-filters {
    padding: var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
    border-radius: 0;
  }

  .search-row {
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .search-input {
    font-size: var(--form-input-font-size-mobile); /* Prevents iOS zoom */
  }

  .clear-btn {
    width: 100%;
    min-height: var(--touch-target-min-size);
  }

  .filter-row {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }

  :deep(.filter-group) {
    width: 100%;
  }

  :deep(.filter-select),
  :deep(.filter-input) {
    width: 100%;
    font-size: var(--form-input-font-size-mobile); /* Prevents iOS zoom */
  }
}

/* Tablet screens - 2 columns for better spacing */
@media (min-width: 768px) and (max-width: 1023px) {
  .filter-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* MDPI screens (1024px - 1439px) - 3 columns for optimal layout */
@media (min-width: 1024px) and (max-width: 1439px) {
  .filter-row {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* HDPI screens and larger - 4 columns */
@media (min-width: 1440px) {
  .filter-row {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
