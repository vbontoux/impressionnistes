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
        <BaseButton v-if="actionLabel" variant="primary" @click="$emit('action')">
          {{ actionLabel }}
        </BaseButton>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseButton from '@/components/base/BaseButton.vue'

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
  margin-bottom: var(--spacing-xxl);
  flex-wrap: wrap;
  gap: var(--spacing-lg);
}

.header-title h1 {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
}

.subtitle {
  color: var(--color-muted);
  margin: 0;
  font-size: var(--font-size-lg);
}

.header-actions {
  display: flex;
  gap: var(--spacing-lg);
  align-items: center;
}

.view-toggle {
  display: flex;
  gap: var(--spacing-xs);
  background-color: var(--color-light);
  border-radius: var(--button-border-radius);
  padding: var(--spacing-xs);
}

.btn-view {
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: transparent;
  border: none;
  cursor: pointer;
  font-size: var(--font-size-2xl);
  border-radius: var(--button-border-radius);
  transition: var(--transition-normal);
  min-width: var(--touch-target-min-size);
  min-height: var(--touch-target-min-size);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-muted);
}

.btn-view:hover {
  background-color: var(--color-border);
}

.btn-view.active {
  background-color: var(--color-bg-white);
  box-shadow: var(--card-shadow);
  color: var(--color-dark);
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .list-header {
    flex-direction: column;
    align-items: stretch;
    margin-bottom: var(--spacing-xl);
    gap: var(--spacing-lg);
  }

  .header-title h1 {
    font-size: var(--font-size-2xl);
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
    padding: var(--spacing-md);
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
    padding: var(--spacing-sm) var(--spacing-md);
  }
}
</style>
