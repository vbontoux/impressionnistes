<template>
  <div class="impersonation-card">
    <h3 class="card-title">
      <span class="icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- Main user (front) -->
          <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M3 21V19C3 17.9391 3.42143 16.9217 4.17157 16.1716C4.92172 15.4214 5.93913 15 7 15H11C12.0609 15 13.0783 15.4214 13.8284 16.1716C14.5786 16.9217 15 17.9391 15 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <!-- Shadow user (back) - slightly offset and lighter -->
          <circle cx="15" cy="5" r="3.5" stroke="currentColor" stroke-width="1.5" opacity="0.4" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M18 13C18.7956 13 19.5587 13.3161 20.1213 13.8787C20.6839 14.4413 21 15.2044 21 16V17" stroke="currentColor" stroke-width="1.5" opacity="0.4" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </span>
      {{ $t('admin.impersonation.card_title') }}
    </h3>
    <p class="card-description">
      {{ $t('admin.impersonation.card_description') }}
    </p>
    
    <div class="selector-container">
      <select 
        v-model="selectedTeamManagerId" 
        @change="changeImpersonation"
        class="team-manager-selector"
        :disabled="loading"
        :aria-label="$t('admin.impersonation.select_team_manager')"
      >
        <option value="">{{ $t('admin.impersonation.select_team_manager') }}</option>
        <option 
          v-for="tm in teamManagers" 
          :key="tm.user_id" 
          :value="tm.user_id"
        >
          {{ tm.first_name }} {{ tm.last_name }} ({{ tm.email }}){{ tm.is_admin ? ' [ADMIN]' : '' }}
        </option>
      </select>
    </div>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <div v-if="teamManagers.length === 0 && !loading && !error" class="info-message">
      {{ $t('admin.impersonation.no_team_managers') }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import apiClient from '@/services/apiClient'

const authStore = useAuthStore()
const teamManagers = ref([])
const selectedTeamManagerId = ref('')
const loading = ref(false)
const error = ref(null)

/**
 * Fetch list of team managers from API
 */
const fetchTeamManagers = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await apiClient.get('/admin/team-managers')
    teamManagers.value = response.data?.data?.team_managers || []
  } catch (err) {
    console.error('Failed to fetch team managers:', err)
    error.value = err.response?.data?.error?.message || err.response?.data?.message || 'Failed to load team managers'
  } finally {
    loading.value = false
  }
}

/**
 * Change impersonation to a different team manager
 */
const changeImpersonation = async () => {
  const teamManagerId = selectedTeamManagerId.value

  if (!teamManagerId) {
    return
  }

  // Find the selected team manager info
  const teamManager = teamManagers.value.find(tm => tm.user_id === teamManagerId)
  
  if (teamManager) {
    // Set impersonation in store (this persists to localStorage)
    authStore.setImpersonation(teamManagerId, teamManager)
    
    // Navigate to dashboard with parameter (this triggers a full page load)
    const url = new URL(window.location.origin + '/dashboard')
    url.searchParams.set('team_manager_id', teamManagerId)
    window.location.href = url.toString()
  }
}

// Fetch team managers on mount
onMounted(() => {
  fetchTeamManagers()
})
</script>

<style scoped>
.impersonation-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 2px solid #667eea;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 0.75rem 0;
  font-size: 1.25rem;
  color: #2c3e50;
}

.icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  color: #667eea;
}

.icon svg {
  width: 100%;
  height: 100%;
}

.card-description {
  color: #666;
  margin: 0 0 1.5rem 0;
  font-size: 0.9375rem;
  line-height: 1.5;
}

.selector-container {
  margin-bottom: 1rem;
}

.team-manager-selector {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  background-color: white;
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.team-manager-selector:hover:not(:disabled) {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
}

.team-manager-selector:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.team-manager-selector:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #f5f5f5;
}

.error-message {
  padding: 0.75rem 1rem;
  background-color: #fee;
  color: #c33;
  border: 1px solid #fcc;
  border-radius: 6px;
  font-size: 0.875rem;
  margin-top: 1rem;
}

.info-message {
  padding: 0.75rem 1rem;
  background-color: #e3f2fd;
  color: #1976d2;
  border: 1px solid #bbdefb;
  border-radius: 6px;
  font-size: 0.875rem;
  margin-top: 1rem;
}
</style>
