<template>
  <div class="list-filters">
    <div class="search-box">
      <input
        :value="searchQuery"
        @input="$emit('update:searchQuery', $event.target.value)"
        type="text"
        :placeholder="searchPlaceholder"
        class="search-input"
      />
    </div>
    
    <div class="filter-row">
      <slot name="filters"></slot>
      
      <button @click="$emit('clear')" class="filter-btn">
        {{ clearLabel || $t('admin.boats.clearFilters') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
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

defineEmits(['update:searchQuery', 'clear'])
</script>

<style scoped>
.list-filters {
  background: var(--color-bg-white);
  padding: var(--spacing-lg);
  border-radius: var(--card-border-radius);
  margin-bottom: var(--spacing-xl);
  box-shadow: var(--card-shadow);
}

.search-box {
  margin-bottom: var(--spacing-md);
}

.search-input {
  width: 100%;
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
  display: flex;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
  align-items: center;
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

/* Mobile Responsive */
@media (max-width: 767px) {
  .list-filters {
    padding: var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
    border-radius: 0;
  }

  .search-input {
    font-size: var(--form-input-font-size-mobile); /* Prevents iOS zoom */
  }

  .filter-row {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }

  .filter-btn {
    width: 100%;
    min-height: var(--touch-target-min-size);
  }
}

/* Tablet and larger screens */
@media (min-width: 768px) {
  .filter-row {
    flex-direction: row;
    align-items: center;
  }

  .filter-btn {
    width: auto;
  }
}
</style>
