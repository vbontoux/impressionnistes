<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
        <div class="confirm-dialog" role="dialog" aria-modal="true" @click.stop>
          <div class="dialog-header">
            <div class="dialog-icon" :class="`dialog-icon--${variant}`">
              <svg v-if="variant === 'danger'" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="variant === 'warning'" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 9V13M12 17H12.01M10.29 3.86L1.82 18C1.64537 18.3024 1.55296 18.6453 1.55199 18.9945C1.55101 19.3437 1.64151 19.6871 1.81445 19.9905C1.98738 20.2939 2.23675 20.5467 2.53773 20.7239C2.83871 20.9011 3.18082 20.9962 3.53 21H20.47C20.8192 20.9962 21.1613 20.9011 21.4623 20.7239C21.7633 20.5467 22.0126 20.2939 22.1856 19.9905C22.3585 19.6871 22.449 19.3437 22.448 18.9945C22.447 18.6453 22.3546 18.3024 22.18 18L13.71 3.86C13.5317 3.56611 13.2807 3.32312 12.9812 3.15448C12.6817 2.98585 12.3437 2.89725 12 2.89725C11.6563 2.89725 11.3183 2.98585 11.0188 3.15448C10.7193 3.32312 10.4683 3.56611 10.29 3.86Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M13 16H12V12H11M12 8H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h2 class="dialog-title">{{ title }}</h2>
          </div>
          
          <div class="dialog-body">
            <p class="dialog-message">{{ message }}</p>
          </div>
          
          <div class="dialog-footer">
            <BaseButton
              variant="secondary"
              size="medium"
              @click="handleCancel"
            >
              {{ cancelText }}
            </BaseButton>
            <BaseButton
              :variant="confirmVariant"
              size="medium"
              @click="handleConfirm"
              autofocus
            >
              {{ confirmText }}
            </BaseButton>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import BaseButton from './BaseButton.vue'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    required: true
  },
  confirmText: {
    type: String,
    default: 'Confirmer'
  },
  cancelText: {
    type: String,
    default: 'Annuler'
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'danger', 'warning'].includes(value)
  },
  closeOnOverlay: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['confirm', 'cancel', 'close'])

const confirmVariant = props.variant === 'primary' ? 'primary' : props.variant

const handleConfirm = () => {
  emit('confirm')
  emit('close')
}

const handleCancel = () => {
  emit('cancel')
  emit('close')
}

const handleOverlayClick = () => {
  if (props.closeOnOverlay) {
    handleCancel()
  }
}

const handleEscape = (e) => {
  if (e.key === 'Escape' && props.show) {
    handleCancel()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: var(--spacing-lg);
}

.confirm-dialog {
  background: var(--color-white);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  max-width: 500px;
  width: 100%;
  overflow: hidden;
}

.dialog-header {
  padding: var(--spacing-xl);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--spacing-md);
}

.dialog-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog-icon--primary {
  background-color: var(--color-primary-light, #e3f2fd);
  color: var(--color-primary);
}

.dialog-icon--danger {
  background-color: var(--color-danger-light, #ffebee);
  color: var(--color-danger);
}

.dialog-icon--warning {
  background-color: var(--color-warning-light, #fff8e1);
  color: var(--color-warning);
}

.dialog-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
  margin: 0;
}

.dialog-body {
  padding: 0 var(--spacing-xl) var(--spacing-xl);
  text-align: center;
}

.dialog-message {
  font-size: var(--font-size-base);
  color: var(--color-secondary);
  margin: 0;
  line-height: 1.5;
}

.dialog-footer {
  padding: var(--spacing-lg) var(--spacing-xl) var(--spacing-xl);
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
}

/* Transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active .confirm-dialog,
.modal-leave-active .confirm-dialog {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .confirm-dialog,
.modal-leave-to .confirm-dialog {
  transform: scale(0.95);
  opacity: 0;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .modal-overlay {
    padding: var(--spacing-md);
  }

  .confirm-dialog {
    max-width: 100%;
  }

  .dialog-header {
    padding: var(--spacing-lg);
  }

  .dialog-icon {
    width: 40px;
    height: 40px;
  }

  .dialog-icon svg {
    width: 20px;
    height: 20px;
  }

  .dialog-title {
    font-size: var(--font-size-lg);
  }

  .dialog-body {
    padding: 0 var(--spacing-lg) var(--spacing-lg);
  }

  .dialog-message {
    font-size: var(--font-size-sm);
  }

  .dialog-footer {
    padding: var(--spacing-md) var(--spacing-lg) var(--spacing-lg);
    flex-direction: column-reverse;
  }

  .dialog-footer :deep(button) {
    width: 100%;
  }
}
</style>
