<template>
  <span :class="badgeClasses">
    <slot>{{ displayText }}</slot>
  </span>
</template>

<script>
export default {
  name: 'StatusBadge',
  props: {
    status: {
      type: String,
      required: true,
      validator: (value) => ['incomplete', 'complete', 'paid', 'forfait', 'free'].includes(value.toLowerCase())
    },
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium'].includes(value)
    }
  },
  computed: {
    normalizedStatus() {
      return this.status.toLowerCase()
    },
    badgeClasses() {
      return [
        'status-badge',
        `status-badge--${this.normalizedStatus}`,
        `status-badge--${this.size}`
      ]
    },
    displayText() {
      // Capitalize first letter for display (sentence case)
      const statusMap = {
        'incomplete': 'Incomplete',
        'complete': 'Complete',
        'paid': 'Paid',
        'forfait': 'Forfait',
        'free': 'Free'
      }
      return statusMap[this.normalizedStatus] || this.status
    }
  }
}
</script>

<style scoped>
.status-badge {
  /* Base styles using design tokens */
  display: inline-block;
  padding: var(--badge-padding);
  border-radius: var(--badge-border-radius);
  font-size: var(--badge-font-size);
  font-weight: var(--badge-font-weight);
  white-space: nowrap;
  text-align: center;
}

/* Size variants */
.status-badge--small {
  padding: 0.125rem 0.5rem;
  font-size: 0.6875rem; /* 11px */
}

.status-badge--medium {
  padding: var(--badge-padding); /* 0.25rem 0.75rem */
  font-size: var(--badge-font-size); /* 0.75rem / 12px */
}

/* Status color variants */
.status-badge--incomplete {
  background-color: var(--color-warning);
  color: var(--color-dark);
}

.status-badge--complete {
  background-color: var(--color-success);
  color: white;
}

.status-badge--paid {
  background-color: var(--color-primary);
  color: white;
}

.status-badge--free {
  background-color: var(--color-primary);
  color: white;
}

.status-badge--forfait {
  background-color: var(--color-danger);
  color: white;
}
</style>
