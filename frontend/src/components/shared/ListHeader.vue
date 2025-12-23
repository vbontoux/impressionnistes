<template>
  <div class="list-header">
    <div class="header-title">
      <slot name="title">
        <h1>{{ title }}</h1>
      </slot>
      <slot name="subtitle">
        <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
      </slot>
    </div>
    <div class="header-actions">
      <div class="view-toggle">
        <button 
          @click="$emit('update:viewMode', 'cards')" 
          :class="{ active: viewMode === 'cards' }"
          class="btn-view"
          :title="$t('common.cardView')"
        >
          ⊞
        </button>
        <button 
          @click="$emit('update:viewMode', 'table')" 
          :class="{ active: viewMode === 'table' }"
          class="btn-view"
          :title="$t('common.tableView')"
        >
          ☰
        </button>
      </div>
      <slot name="action">
        <button v-if="actionLabel" @click="$emit('action')" class="btn-primary">
          {{ actionLabel }}
        </button>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  viewMode: {
    type: String,
    required: true,
    validator: (value) => ['cards', 'table'].includes(value)
  },
  actionLabel: {
    type: String,
    default: ''
  }
})

defineEmits(['update:viewMode', 'action'])
</script>

<style scoped>
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-title h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  color: #212529;
}

.subtitle {
  color: #6c757d;
  margin: 0;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.view-toggle {
  display: flex;
  gap: 0.25rem;
  background-color: #e9ecef;
  border-radius: 4px;
  padding: 0.25rem;
}

.btn-view {
  padding: 0.5rem 0.75rem;
  background-color: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  border-radius: 4px;
  transition: background-color 0.2s;
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-view:hover {
  background-color: #dee2e6;
}

.btn-view.active {
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: background-color 0.2s;
  min-height: 44px;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-primary:active {
  background-color: #004085;
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .list-header {
    flex-direction: column;
    align-items: stretch;
    margin-bottom: 1.5rem;
    gap: 1rem;
  }

  .header-title h1 {
    font-size: 1.5rem;
  }

  .header-actions {
    justify-content: space-between;
    width: 100%;
  }

  .view-toggle {
    flex-shrink: 0;
    width: auto;
  }

  .btn-view {
    padding: 0.75rem;
  }

  .btn-primary {
    flex-shrink: 0;
    width: auto;
    padding: 0.75rem 1rem;
    font-size: 0.9rem;
  }
}

/* Tablet and larger screens */
@media (min-width: 768px) {
  .list-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }

  .header-actions {
    width: auto;
  }

  .btn-view {
    padding: 0.5rem 0.75rem;
  }

  .btn-primary {
    width: auto;
    padding: 0.5rem 1rem;
  }
}
</style>
