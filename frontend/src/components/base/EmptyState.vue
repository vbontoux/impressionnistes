<template>
  <div class="empty-state">
    <div v-if="$slots.icon" class="empty-state__icon">
      <slot name="icon"></slot>
    </div>
    
    <p class="empty-state__message">{{ message }}</p>
    
    <div v-if="$slots.action || actionLabel" class="empty-state__action">
      <slot name="action">
        <button 
          v-if="actionLabel" 
          class="empty-state__button"
          @click="$emit('action')"
        >
          {{ actionLabel }}
        </button>
      </slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EmptyState',
  props: {
    message: {
      type: String,
      required: true
    },
    actionLabel: {
      type: String,
      default: ''
    }
  },
  emits: ['action']
}
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--spacing-2xl, 2rem);
}

/* Mobile: larger padding */
@media (max-width: 767px) {
  .empty-state {
    padding: var(--spacing-2xl, 2rem) var(--spacing-lg, 1rem);
  }
}

/* Desktop: extra large padding */
@media (min-width: 1024px) {
  .empty-state {
    padding: 3rem var(--spacing-xl, 1.5rem);
  }
}

.empty-state__icon {
  margin-bottom: var(--spacing-lg, 1rem);
  color: var(--color-muted, #666);
  font-size: 3rem;
}

.empty-state__message {
  color: var(--color-muted, #666);
  font-size: var(--font-size-base, 0.875rem);
  margin: 0 0 var(--spacing-lg, 1rem) 0;
  max-width: 400px;
}

/* Desktop: slightly larger text */
@media (min-width: 1024px) {
  .empty-state__message {
    font-size: var(--font-size-lg, 1rem);
  }
}

.empty-state__action {
  margin-top: var(--spacing-md, 0.75rem);
}

.empty-state__button {
  background-color: var(--color-primary, #007bff);
  color: white;
  border: none;
  border-radius: 4px;
  padding: var(--spacing-md, 0.75rem) var(--spacing-lg, 1rem);
  font-size: var(--font-size-base, 0.875rem);
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
  min-height: 44px;
}

.empty-state__button:hover {
  background-color: var(--color-primary-dark, #0056b3);
}

.empty-state__button:active {
  background-color: var(--color-primary-darker, #004085);
}
</style>
