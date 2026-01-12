<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="show"
        class="modal-overlay"
        :class="{ 'modal-overlay--visible': show }"
        @click="handleOverlayClick"
      >
        <Transition name="modal-slide">
          <div
            v-if="show"
            :class="modalClasses"
            @click.stop
            role="dialog"
            aria-modal="true"
            :aria-labelledby="title ? 'modal-title' : undefined"
          >
            <!-- Header -->
            <div v-if="title || $slots.header || showCloseButton" class="modal-header">
              <slot name="header">
                <h2 v-if="title" id="modal-title" class="modal-title">{{ title }}</h2>
              </slot>
              <button
                v-if="showCloseButton"
                class="modal-close"
                @click="handleClose"
                aria-label="Close modal"
                type="button"
              >
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>

            <!-- Body -->
            <div class="modal-body">
              <slot></slot>
            </div>

            <!-- Footer -->
            <div v-if="$slots.footer" class="modal-footer">
              <slot name="footer"></slot>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
export default {
  name: 'BaseModal',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: ''
    },
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },
    closeOnOverlay: {
      type: Boolean,
      default: true
    },
    showCloseButton: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    modalClasses() {
      return [
        'modal-content',
        `modal-content--${this.size}`
      ]
    }
  },
  watch: {
    show(newValue) {
      if (newValue) {
        this.disableBodyScroll()
      } else {
        this.enableBodyScroll()
      }
    }
  },
  beforeUnmount() {
    this.enableBodyScroll()
  },
  methods: {
    handleOverlayClick() {
      if (this.closeOnOverlay) {
        this.handleClose()
      }
    },
    handleClose() {
      this.$emit('close')
    },
    disableBodyScroll() {
      document.body.style.overflow = 'hidden'
    },
    enableBodyScroll() {
      document.body.style.overflow = ''
    }
  }
}
</script>

<style scoped>
/* Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--modal-overlay-bg, rgba(0, 0, 0, 0.5));
  z-index: var(--z-index-modal-backdrop, 900);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
}

/* Mobile: Bottom sheet positioning */
@media (max-width: 767px) {
  .modal-overlay {
    align-items: flex-end;
    padding: 0;
  }
}

/* Modal Content */
.modal-content {
  background-color: var(--color-bg-white, #ffffff);
  box-shadow: var(--modal-shadow, 0 4px 8px rgba(0, 0, 0, 0.1));
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  overflow: hidden;
  position: relative;
  z-index: var(--z-index-modal, 1000);
}

/* Desktop: Centered modal */
@media (min-width: 768px) {
  .modal-content {
    border-radius: var(--modal-border-radius-desktop, 8px);
    width: 100%;
  }
  
  .modal-content--small {
    max-width: 400px;
  }
  
  .modal-content--medium {
    max-width: var(--modal-max-width, 600px);
  }
  
  .modal-content--large {
    max-width: 800px;
  }
}

/* Mobile: Bottom sheet */
@media (max-width: 767px) {
  .modal-content {
    border-radius: var(--modal-border-radius-mobile, 12px 12px 0 0);
    width: 100%;
    max-height: 90vh;
  }
}

/* Header */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--modal-padding, 1rem 1.5rem);
  border-bottom: 1px solid var(--color-border, #dee2e6);
  flex-shrink: 0;
}

.modal-title {
  margin: 0;
  font-size: var(--font-size-xl, 1.125rem);
  font-weight: var(--font-weight-semibold, 600);
  color: var(--color-dark, #212529);
}

.modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  background: none;
  color: var(--color-muted, #666);
  cursor: pointer;
  border-radius: var(--button-border-radius, 4px);
  transition: var(--transition-normal, 0.2s ease);
  flex-shrink: 0;
}

.modal-close:hover {
  background-color: var(--color-bg-hover, rgba(0, 0, 0, 0.05));
  color: var(--color-dark, #212529);
}

.modal-close:focus {
  outline: 2px solid var(--color-primary, #007bff);
  outline-offset: 2px;
}

.modal-close:focus:not(:focus-visible) {
  outline: none;
}

/* Body */
.modal-body {
  padding: var(--modal-padding, 1rem 1.5rem);
  overflow-y: auto;
  flex: 1;
}

/* Footer */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--spacing-sm, 0.5rem);
  padding: var(--modal-padding, 1rem 1.5rem);
  border-top: 1px solid var(--color-border, #dee2e6);
  flex-shrink: 0;
}

/* Mobile: Stack footer buttons */
@media (max-width: 767px) {
  .modal-footer {
    flex-direction: column-reverse;
    gap: var(--spacing-md, 0.75rem);
  }
  
  .modal-footer > * {
    width: 100%;
  }
}

/* Transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity var(--transition-normal, 0.2s ease);
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* Desktop: Fade and scale */
@media (min-width: 768px) {
  .modal-slide-enter-active,
  .modal-slide-leave-active {
    transition: all var(--transition-normal, 0.2s ease);
  }

  .modal-slide-enter-from,
  .modal-slide-leave-to {
    opacity: 0;
    transform: scale(0.95);
  }
}

/* Mobile: Slide up from bottom */
@media (max-width: 767px) {
  .modal-slide-enter-active,
  .modal-slide-leave-active {
    transition: transform var(--transition-slow, 0.3s ease);
  }

  .modal-slide-enter-from,
  .modal-slide-leave-to {
    transform: translateY(100%);
  }
}

/* Accessibility: Reduce motion */
@media (prefers-reduced-motion: reduce) {
  .modal-fade-enter-active,
  .modal-fade-leave-active,
  .modal-slide-enter-active,
  .modal-slide-leave-active {
    transition: none;
  }
}
</style>
