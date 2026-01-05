<template>
  <!-- Only show when actively impersonating -->
  <div v-if="authStore.isImpersonating" class="impersonation-bar">
    <div class="impersonation-container">
      <div class="impersonation-info">
        <span class="warning-icon" aria-label="Warning">⚠️</span>
        <span class="label">{{ $t('admin.impersonation.viewing_as') }}:</span>
        <span class="team-manager-name">{{ impersonatedTeamManager?.first_name }} {{ impersonatedTeamManager?.last_name }}</span>
        <span class="team-manager-email">({{ impersonatedTeamManager?.email }})</span>
      </div>
      <div class="impersonation-controls">
        <button 
          @click="exitImpersonation" 
          class="exit-btn"
          :disabled="loading"
          :aria-label="$t('admin.impersonation.exit')"
        >
          {{ $t('admin.impersonation.exit') }} ✕
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const loading = ref(false)

const impersonatedTeamManager = computed(() => authStore.impersonatedTeamManager)

/**
 * Exit impersonation mode
 */
const exitImpersonation = () => {
  console.log('🚪 [ImpersonationBar] exitImpersonation called')
  console.log('🚪 [ImpersonationBar] Timestamp:', Date.now())
  
  loading.value = true
  
  // Clear impersonation from store (this clears localStorage)
  authStore.clearImpersonation()
  
  console.log('🚪 [ImpersonationBar] Impersonation cleared from store and localStorage')
  
  // Navigate to current URL without parameter (this triggers a full page load)
  const url = new URL(window.location.href)
  url.searchParams.delete('team_manager_id')
  console.log('🚪 [ImpersonationBar] Navigating to:', url.toString())
  window.location.href = url.toString()
}
</script>

<style scoped>
.impersonation-bar {
  position: sticky;
  top: 60px; /* Position below the header (header is ~60px tall) */
  z-index: 101; /* Above both sidebar (99) and header (100) */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-bottom: 3px solid #5568d3;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.875rem 1.5rem;
  margin-left: 0;
}

/* Mobile: Ensure sidebar appears below impersonation bar */
@media (max-width: 767px) {
  .impersonation-bar {
    z-index: 102; /* Above sidebar on mobile */
  }
}

/* When sidebar is visible on desktop, add left margin */
@media (min-width: 768px) {
  .impersonation-bar {
    margin-left: 280px; /* Match sidebar width */
  }
}

.impersonation-container {
  display: flex;
  flex-direction: row;
  gap: 1.5rem;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  flex-wrap: wrap;
}

.impersonation-info {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex-wrap: wrap;
  color: white;
  font-weight: 500;
  flex: 1;
  min-width: 300px;
}

.warning-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.label {
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.8125rem;
  letter-spacing: 1px;
  color: rgba(255, 255, 255, 0.95);
}

.team-manager-name {
  font-weight: 700;
  color: #fff;
  font-size: 1rem;
}

.team-manager-email {
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.875rem;
}

.impersonation-controls {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-shrink: 0;
}

.team-manager-selector {
  min-width: 320px;
  max-width: 450px;
  padding: 0.625rem 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background-color: rgba(255, 255, 255, 0.95);
  color: #2c3e50;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 42px;
}

.team-manager-selector:hover:not(:disabled) {
  border-color: rgba(255, 255, 255, 0.6);
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.team-manager-selector:focus {
  outline: none;
  border-color: white;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3);
  background-color: white;
}

.team-manager-selector:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.exit-btn {
  padding: 0.625rem 1.25rem;
  background-color: #e74c3c;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  font-size: 0.9375rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  min-height: 42px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.exit-btn:hover:not(:disabled) {
  background-color: #c0392b;
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.exit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.exit-btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3);
}

.exit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  margin-top: 0.75rem;
  padding: 0.75rem 1rem;
  background-color: rgba(231, 76, 60, 0.95);
  color: white;
  border: 2px solid #c0392b;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

.info-message {
  margin-top: 0.75rem;
  padding: 0.75rem 1rem;
  background-color: rgba(255, 255, 255, 0.95);
  color: #667eea;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

/* Mobile Optimization */
@media (max-width: 767px) {
  .impersonation-bar {
    padding: 0.75rem 1rem;
  }

  .impersonation-container {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .impersonation-info {
    font-size: 0.875rem;
    min-width: 100%;
  }

  .warning-icon {
    font-size: 1.25rem;
  }

  .label {
    font-size: 0.75rem;
  }

  .team-manager-name {
    font-size: 0.9375rem;
  }

  .team-manager-email {
    font-size: 0.8125rem;
  }

  .impersonation-controls {
    flex-direction: column;
    width: 100%;
    gap: 0.75rem;
  }

  .team-manager-selector {
    min-width: 100%;
    max-width: 100%;
    font-size: 0.875rem;
  }

  .exit-btn {
    width: 100%;
    font-size: 0.875rem;
  }
}
</style>
