<template>
  <div class="loading-spinner-container">
    <div 
      class="loading-spinner" 
      :class="`loading-spinner--${size}`"
      role="status"
      aria-live="polite"
    ></div>
    <p v-if="message" class="loading-message">{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: 'LoadingSpinner',
  props: {
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },
    message: {
      type: String,
      default: ''
    }
  }
}
</script>

<style scoped>
.loading-spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl, 1.5rem);
}

.loading-spinner {
  border: var(--spinner-border-width, 4px) solid var(--spinner-border-color, #f3f3f3);
  border-top: var(--spinner-border-width, 4px) solid var(--spinner-border-top-color, #4CAF50);
  border-radius: 50%;
  animation: spin var(--spinner-animation-duration, 1s) linear infinite;
}

.loading-spinner--small {
  width: 24px;
  height: 24px;
  border-width: 3px;
}

.loading-spinner--medium {
  width: var(--spinner-size, 40px);
  height: var(--spinner-size, 40px);
}

.loading-spinner--large {
  width: 56px;
  height: 56px;
  border-width: 5px;
}

.loading-message {
  margin-top: var(--spacing-md, 0.75rem);
  color: var(--color-muted, #666);
  font-size: var(--font-size-base, 0.875rem);
  text-align: center;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
