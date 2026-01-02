<template>
  <div class="club-list-popover">
    <button
      ref="triggerButton"
      @click="togglePopover"
      @keydown.escape="closePopover"
      class="popover-trigger"
      :aria-expanded="isOpen"
      aria-haspopup="true"
      :aria-label="$t('admin.boats.viewClubList')"
    >
      <slot name="trigger">
        <span class="multi-club-badge">{{ $t('boat.multiClub') }}</span>
      </slot>
    </button>

    <Teleport to="body">
      <div
        v-if="isOpen"
        ref="popoverContent"
        class="popover-content"
        :style="popoverStyle"
        role="dialog"
        aria-modal="false"
      >
        <div class="popover-header">
          <h4>{{ $t('admin.boats.clubList') }}</h4>
          <button
            @click="closePopover"
            class="close-btn"
            :aria-label="$t('common.close')"
          >
            &times;
          </button>
        </div>
        <ul class="club-list">
          <li v-for="(club, index) in clubs" :key="index" class="club-item">
            {{ club }}
          </li>
        </ul>
      </div>
    </Teleport>

    <!-- Backdrop for mobile -->
    <Teleport to="body">
      <div
        v-if="isOpen"
        class="popover-backdrop"
        @click="closePopover"
      ></div>
    </Teleport>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'

export default {
  name: 'ClubListPopover',
  props: {
    clubs: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  setup(props) {
    const isOpen = ref(false)
    const triggerButton = ref(null)
    const popoverContent = ref(null)
    const popoverStyle = ref({})

    const togglePopover = async () => {
      isOpen.value = !isOpen.value
      if (isOpen.value) {
        await nextTick()
        calculatePosition()
      }
    }

    const closePopover = () => {
      isOpen.value = false
    }

    const calculatePosition = () => {
      if (!triggerButton.value || !popoverContent.value) return

      const trigger = triggerButton.value.getBoundingClientRect()
      const popover = popoverContent.value.getBoundingClientRect()
      const viewport = {
        width: window.innerWidth,
        height: window.innerHeight
      }

      // Default position: below and centered
      let top = trigger.bottom + 8
      let left = trigger.left + (trigger.width / 2) - (popover.width / 2)

      // Adjust if popover goes off right edge
      if (left + popover.width > viewport.width - 16) {
        left = viewport.width - popover.width - 16
      }

      // Adjust if popover goes off left edge
      if (left < 16) {
        left = 16
      }

      // If popover goes off bottom, show above trigger instead
      if (top + popover.height > viewport.height - 16) {
        top = trigger.top - popover.height - 8
      }

      // If still off screen, position at top of viewport
      if (top < 16) {
        top = 16
      }

      popoverStyle.value = {
        top: `${top}px`,
        left: `${left}px`
      }
    }

    const handleClickOutside = (event) => {
      if (
        isOpen.value &&
        popoverContent.value &&
        triggerButton.value &&
        !popoverContent.value.contains(event.target) &&
        !triggerButton.value.contains(event.target)
      ) {
        closePopover()
      }
    }

    const handleEscape = (event) => {
      if (event.key === 'Escape' && isOpen.value) {
        closePopover()
      }
    }

    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
      document.addEventListener('keydown', handleEscape)
      window.addEventListener('resize', calculatePosition)
      window.addEventListener('scroll', calculatePosition, true)
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
      window.removeEventListener('resize', calculatePosition)
      window.removeEventListener('scroll', calculatePosition, true)
    })

    return {
      isOpen,
      triggerButton,
      popoverContent,
      popoverStyle,
      togglePopover,
      closePopover
    }
  }
}
</script>

<style scoped>
.club-list-popover {
  display: inline-block;
}

.popover-trigger {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
}

.multi-club-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  background-color: #ffc107;
  color: #000;
  transition: background-color 0.2s;
}

.popover-trigger:hover .multi-club-badge {
  background-color: #e0a800;
}

.popover-trigger:focus {
  outline: 2px solid #007bff;
  outline-offset: 2px;
}

.popover-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.3);
  z-index: 999;
  display: none;
}

.popover-content {
  position: fixed;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 200px;
  max-width: 300px;
}

.popover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #dee2e6;
}

.popover-header h4 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #212529;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
  line-height: 1;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #212529;
}

.close-btn:focus {
  outline: 2px solid #007bff;
  outline-offset: 2px;
}

.club-list {
  list-style: none;
  padding: 0.5rem 0;
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
}

.club-item {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  color: #212529;
  border-bottom: 1px solid #f5f5f5;
}

.club-item:last-child {
  border-bottom: none;
}

.club-item:hover {
  background-color: #f8f9fa;
}

/* Mobile styles */
@media (max-width: 768px) {
  .popover-backdrop {
    display: block;
  }

  .popover-content {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    top: auto !important;
    max-width: 100%;
    border-radius: 12px 12px 0 0;
    transform: none !important;
  }

  .popover-header {
    padding: 1rem;
  }

  .popover-header h4 {
    font-size: 1rem;
  }

  .close-btn {
    width: 32px;
    height: 32px;
    font-size: 2rem;
  }

  .club-list {
    max-height: 50vh;
  }

  .club-item {
    padding: 0.75rem 1rem;
    font-size: 1rem;
  }
}
</style>
