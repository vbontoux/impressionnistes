<template>
  <div :class="cardClasses">
    <!-- Header slot or default header with title and status badge -->
    <div v-if="$slots.header || title" class="data-card__header">
      <slot name="header">
        <div class="data-card__header-content">
          <h3 v-if="title" class="data-card__title">{{ title }}</h3>
          <StatusBadge 
            v-if="statusBadge && status" 
            :status="status"
            class="data-card__status-badge"
          />
        </div>
      </slot>
    </div>

    <!-- Default slot for card body content -->
    <div v-if="$slots.default" class="data-card__body">
      <slot></slot>
    </div>

    <!-- Actions slot for buttons -->
    <div v-if="$slots.actions" class="data-card__actions">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script>
import StatusBadge from '../base/StatusBadge.vue'

export default {
  name: 'DataCard',
  components: {
    StatusBadge
  },
  props: {
    title: {
      type: String,
      default: ''
    },
    status: {
      type: String,
      default: '',
      validator: (value) => !value || ['incomplete', 'complete', 'paid', 'forfait', 'free'].includes(value.toLowerCase())
    },
    statusBadge: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    cardClasses() {
      return [
        'data-card',
        {
          [`data-card--status-${this.status.toLowerCase()}`]: this.status
        }
      ]
    }
  }
}
</script>

<style scoped>
.data-card {
  /* Base card styles using design tokens */
  background-color: var(--color-bg-white);
  border: var(--card-border-width) solid var(--card-border-color);
  border-radius: var(--card-border-radius);
  box-shadow: var(--card-shadow);
  transition: box-shadow var(--transition-normal);
  
  /* Responsive padding */
  padding: var(--card-padding-mobile);
  
  /* Status-based left border */
  border-left-width: 4px;
  border-left-style: solid;
  border-left-color: var(--card-border-color);
}

/* Desktop padding */
@media (min-width: 768px) {
  .data-card {
    padding: var(--card-padding-desktop);
  }
}

/* Hover effect on desktop */
@media (hover: hover) {
  .data-card:hover {
    box-shadow: var(--card-shadow-hover);
  }
}

/* Status-based border colors */
.data-card--status-incomplete {
  border-left-color: var(--color-warning);
}

.data-card--status-complete {
  border-left-color: var(--color-success);
}

.data-card--status-paid,
.data-card--status-free {
  border-left-color: var(--color-primary);
}

.data-card--status-forfait {
  border-left-color: var(--color-danger);
}

/* Header */
.data-card__header {
  margin-bottom: var(--spacing-md);
}

.data-card__header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.data-card__title {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
  flex: 1;
  min-width: 0; /* Allow text truncation */
}

.data-card__status-badge {
  flex-shrink: 0;
}

/* Body */
.data-card__body {
  color: var(--color-dark);
}

/* Actions */
.data-card__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}

/* Desktop: larger gap */
@media (min-width: 768px) {
  .data-card__actions {
    gap: var(--spacing-md);
  }
}

/* Utility class for detail rows (common pattern in cards) */
.data-card__body :deep(.detail-row) {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-light);
  gap: var(--spacing-md);
}

.data-card__body :deep(.detail-row:last-child) {
  border-bottom: none;
}

.data-card__body :deep(.detail-row .label) {
  font-weight: var(--font-weight-medium);
  color: var(--color-muted);
  flex-shrink: 0;
}

.data-card__body :deep(.detail-row .value) {
  text-align: right;
  word-break: break-word;
}
</style>
