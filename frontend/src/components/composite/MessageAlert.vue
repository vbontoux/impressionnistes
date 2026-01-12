<template>
  <transition name="alert-fade">
    <div
      v-if="isVisible"
      :class="['message-alert', `message-alert--${type}`]"
      role="alert"
      :aria-live="type === 'error' ? 'assertive' : 'polite'"
    >
      <div class="message-alert__content">
        <span class="message-alert__icon">{{ icon }}</span>
        <span class="message-alert__message">{{ message }}</span>
      </div>
      
      <button
        v-if="dismissible"
        class="message-alert__close"
        @click="handleDismiss"
        aria-label="Close alert"
        type="button"
      >
        ×
      </button>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['error', 'success', 'warning', 'info'].includes(value)
  },
  message: {
    type: String,
    required: true
  },
  dismissible: {
    type: Boolean,
    default: true
  },
  autoDismiss: {
    type: Number,
    default: 0, // 0 means no auto-dismiss
    validator: (value) => value >= 0
  }
})

const emit = defineEmits(['dismiss'])

const isVisible = ref(true)
let autoDismissTimer = null

const icon = computed(() => {
  const icons = {
    error: '✕',
    success: '✓',
    warning: '⚠',
    info: 'ℹ'
  }
  return icons[props.type] || icons.info
})

const handleDismiss = () => {
  isVisible.value = false
  emit('dismiss')
}

onMounted(() => {
  if (props.autoDismiss > 0) {
    autoDismissTimer = setTimeout(() => {
      handleDismiss()
    }, props.autoDismiss)
  }
})

onUnmounted(() => {
  if (autoDismissTimer) {
    clearTimeout(autoDismissTimer)
  }
})
</script>

<style scoped>
.message-alert {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border-radius: var(--button-border-radius);
  border: 1px solid;
  font-size: var(--font-size-base);
  margin-bottom: var(--spacing-lg);
  transition: var(--transition-normal);
}

.message-alert__content {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  flex: 1;
}

.message-alert__icon {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  line-height: 1;
  flex-shrink: 0;
}

.message-alert__message {
  flex: 1;
  line-height: var(--line-height-normal);
}

.message-alert__close {
  background: none;
  border: none;
  font-size: var(--font-size-2xl);
  line-height: 1;
  cursor: pointer;
  padding: 0;
  margin-left: var(--spacing-md);
  color: inherit;
  opacity: 0.7;
  transition: opacity var(--transition-fast);
  flex-shrink: 0;
}

.message-alert__close:hover {
  opacity: 1;
}

.message-alert__close:focus {
  outline: 2px solid currentColor;
  outline-offset: 2px;
  border-radius: 2px;
}

/* Error Type */
.message-alert--error {
  background-color: var(--color-danger-light);
  border-color: var(--color-danger-border);
  color: var(--color-danger-text);
}

/* Success Type */
.message-alert--success {
  background-color: var(--color-success-light);
  border-color: var(--color-success-border);
  color: var(--color-success-text);
}

/* Warning Type */
.message-alert--warning {
  background-color: var(--color-warning-light);
  border-color: var(--color-warning-border);
  color: var(--color-warning-text);
}

/* Info Type */
.message-alert--info {
  background-color: var(--color-info-light);
  border-color: var(--color-info-border);
  color: var(--color-info-text);
}

/* Fade Transition */
.alert-fade-enter-active,
.alert-fade-leave-active {
  transition: opacity var(--transition-normal), transform var(--transition-normal);
}

.alert-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.alert-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Responsive Adjustments */
@media (max-width: 767px) {
  .message-alert {
    font-size: var(--font-size-base);
  }
  
  .message-alert__icon {
    font-size: var(--font-size-lg);
  }
}
</style>
