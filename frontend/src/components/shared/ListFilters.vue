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
  background: white;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.search-box {
  margin-bottom: 0.75rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  min-height: 44px;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.filter-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.filter-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  white-space: nowrap;
  transition: all 0.3s;
  min-height: 44px;
}

.filter-btn:hover {
  background: #f5f5f5;
}

.filter-btn:active {
  background: #e9ecef;
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .list-filters {
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 0;
  }

  .search-input {
    font-size: 16px; /* Prevents iOS zoom */
  }

  .filter-row {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }

  .filter-btn {
    width: 100%;
    min-height: 44px;
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
