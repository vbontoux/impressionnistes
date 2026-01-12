<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    :type="type"
    @click="handleClick"
  >
    <span v-if="loading" class="button-spinner"></span>
    <span :class="{ 'button-content-loading': loading }">
      <slot></slot>
    </span>
  </button>
</template>

<script>
export default {
  name: 'BaseButton',
  props: {
    variant: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'secondary', 'danger', 'warning'].includes(value)
    },
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },
    disabled: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    fullWidth: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'button',
      validator: (value) => ['button', 'submit', 'reset'].includes(value)
    }
  },
  computed: {
    buttonClasses() {
      return [
        'base-button',
        `base-button--${this.variant}`,
        `base-button--${this.size}`,
        {
          'base-button--full-width': this.fullWidth,
          'base-button--loading': this.loading,
          'base-button--disabled': this.disabled
        }
      ]
    }
  },
  methods: {
    handleClick(event) {
      if (!this.disabled && !this.loading) {
        this.$emit('click', event)
      }
    }
  }
}
</script>

<style scoped>
.base-button {
  /* Base styles */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  border: none;
  border-radius: var(--button-border-radius);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: var(--button-transition);
  text-align: center;
  white-space: nowrap;
  user-select: none;
  position: relative;
  
  /* Prevent text selection on double-click */
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.base-button:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.base-button:focus:not(:focus-visible) {
  outline: none;
}

/* Size variants */
.base-button--small {
  min-height: var(--button-min-height-sm);
  padding: var(--button-padding-sm);
  font-size: var(--button-font-size-sm);
}

.base-button--medium {
  min-height: var(--button-min-height-md);
  padding: var(--button-padding-md);
  font-size: var(--button-font-size-md);
}

.base-button--large {
  min-height: var(--button-min-height-lg);
  padding: var(--button-padding-lg);
  font-size: var(--button-font-size-lg);
}

/* Color variants */
.base-button--primary {
  background-color: var(--color-primary);
  color: white;
}

.base-button--primary:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.base-button--primary:active:not(:disabled) {
  background-color: var(--color-primary-active);
}

.base-button--secondary {
  background-color: var(--color-secondary);
  color: white;
}

.base-button--secondary:hover:not(:disabled) {
  background-color: var(--color-secondary-hover);
}

.base-button--secondary:active:not(:disabled) {
  background-color: var(--color-secondary-active);
}

.base-button--danger {
  background-color: var(--color-danger);
  color: white;
}

.base-button--danger:hover:not(:disabled) {
  background-color: var(--color-danger-hover);
}

.base-button--danger:active:not(:disabled) {
  background-color: var(--color-danger-active);
}

.base-button--warning {
  background-color: var(--color-warning);
  color: var(--color-dark);
}

.base-button--warning:hover:not(:disabled) {
  background-color: var(--color-warning-hover);
}

.base-button--warning:active:not(:disabled) {
  background-color: var(--color-warning-active);
}

/* Disabled state */
.base-button:disabled,
.base-button--disabled {
  background-color: var(--color-disabled);
  color: var(--color-muted);
  cursor: not-allowed;
  opacity: var(--opacity-disabled);
}

/* Full width */
.base-button--full-width {
  width: 100%;
}

/* Loading state */
.base-button--loading {
  cursor: wait;
}

.button-content-loading {
  opacity: 0.6;
}

.button-spinner {
  display: inline-block;
  width: 1em;
  height: 1em;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: button-spin 0.6s linear infinite;
}

@keyframes button-spin {
  to {
    transform: rotate(360deg);
  }
}

/* Responsive adjustments */
@media (max-width: 767px) {
  .base-button {
    /* Ensure touch-friendly size on mobile */
    min-height: var(--touch-target-min-size);
  }
}
</style>
