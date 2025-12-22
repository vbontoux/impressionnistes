<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click.self="$emit('continue')">
        <div class="modal-content session-warning">
          <div class="warning-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <path d="M12 8V12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <circle cx="12" cy="16" r="1" fill="currentColor"/>
            </svg>
          </div>
          
          <h2>{{ $t('session.warningTitle') }}</h2>
          <p>{{ $t('session.warningMessage', { seconds: timeRemaining }) }}</p>
          
          <div class="countdown">
            <div class="countdown-circle">
              <svg viewBox="0 0 100 100">
                <circle 
                  cx="50" 
                  cy="50" 
                  r="45" 
                  fill="none" 
                  stroke="#e0e0e0" 
                  stroke-width="8"
                />
                <circle 
                  cx="50" 
                  cy="50" 
                  r="45" 
                  fill="none" 
                  stroke="#ff9800" 
                  stroke-width="8"
                  :stroke-dasharray="circumference"
                  :stroke-dashoffset="dashOffset"
                  transform="rotate(-90 50 50)"
                  class="countdown-progress"
                />
              </svg>
              <div class="countdown-text">{{ timeRemaining }}s</div>
            </div>
          </div>
          
          <div class="modal-actions">
            <button @click="$emit('continue')" class="btn btn-primary">
              {{ $t('session.continueSession') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    required: true,
  },
  timeRemaining: {
    type: Number,
    required: true,
  },
});

defineEmits(['continue']);

const circumference = 2 * Math.PI * 45;
const maxTime = 120; // 2 minutes in seconds

const dashOffset = computed(() => {
  const progress = props.timeRemaining / maxTime;
  return circumference * (1 - progress);
});
</script>

<style scoped>
/* Mobile-first base styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 9999;
  padding: 0;
}

.modal-content {
  background: white;
  border-radius: 12px 12px 0 0;
  padding: 1.5rem;
  width: 100%;
  max-width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.session-warning {
  text-align: center;
}

.warning-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 1rem;
  color: #ff9800;
  flex-shrink: 0;
}

.warning-icon svg {
  width: 100%;
  height: 100%;
}

.session-warning h2 {
  font-size: 1.25rem;
  margin-bottom: 0.75rem;
  color: #333;
  line-height: 1.3;
}

.session-warning p {
  font-size: 1rem;
  color: #666;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.countdown {
  margin: 1.5rem 0;
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}

.countdown-circle {
  position: relative;
  width: 100px;
  height: 100px;
}

.countdown-circle svg {
  width: 100%;
  height: 100%;
}

.countdown-progress {
  transition: stroke-dashoffset 1s linear;
}

.countdown-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.75rem;
  font-weight: bold;
  color: #ff9800;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  margin-top: 1rem;
  flex-shrink: 0;
}

.btn {
  padding: 0.875rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  min-height: 44px;
  min-width: 44px;
  width: 100%;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background-color: #45a049;
}

.btn-primary:active {
  background-color: #3d8b40;
  transform: scale(0.98);
}

/* Modal transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: translateY(100%);
}

/* Tablet and desktop styles */
@media (min-width: 768px) {
  .modal-overlay {
    align-items: center;
    padding: 1rem;
  }

  .modal-content {
    border-radius: 12px;
    max-width: 450px;
    padding: 2rem;
    max-height: 90vh;
  }

  .warning-icon {
    width: 64px;
    height: 64px;
    margin-bottom: 1.5rem;
  }

  .session-warning h2 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
  }

  .session-warning p {
    margin-bottom: 1.5rem;
  }

  .countdown {
    margin: 2rem 0;
  }

  .countdown-circle {
    width: 120px;
    height: 120px;
  }

  .countdown-text {
    font-size: 2rem;
  }

  .modal-actions {
    margin-top: 1.5rem;
  }

  .btn {
    padding: 0.75rem 2rem;
    width: auto;
  }

  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
  }

  .modal-enter-from .modal-content,
  .modal-leave-to .modal-content {
    transform: scale(0.9);
  }
}
</style>
