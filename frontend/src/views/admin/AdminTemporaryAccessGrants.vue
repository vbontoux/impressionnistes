<template>
  <div class="admin-temp-access">
    <div class="page-header">
      <router-link to="/admin" class="back-link">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        {{ $t('common.back') }}
      </router-link>
      <h1>{{ $t('admin.tempAccess.title') }}</h1>
      <p class="subtitle">{{ $t('admin.tempAccess.subtitle') }}</p>
    </div>

    <LoadingSpinner v-if="initialLoading" :message="$t('common.loading')" />

    <MessageAlert 
      v-else-if="loadError" 
      type="error" 
      :message="loadError"
    >
      <template #action>
        <BaseButton variant="secondary" size="small" @click="loadGrants">
          {{ $t('common.retry') }}
        </BaseButton>
      </template>
    </MessageAlert>

    <div v-else class="content-container">
      <!-- Grant Form -->
      <div class="grant-form-section">
        <TemporaryAccessGrantForm @grant-created="handleGrantCreated" />
      </div>

      <!-- Active Grants -->
      <div class="grants-section">
        <div class="section-header">
          <h2>{{ $t('admin.tempAccess.activeGrants') }}</h2>
          <span class="grant-count">{{ activeGrants.length }}</span>
        </div>

        <MessageAlert
          v-if="revokeError"
          type="error"
          :message="revokeError"
          :dismissible="true"
          @dismiss="revokeError = ''"
        />

        <MessageAlert 
          v-if="activeGrants.length === 0" 
          type="info" 
          :message="$t('admin.tempAccess.noActiveGrants')"
        />

        <div v-else class="grants-list">
          <div 
            v-for="grant in activeGrants" 
            :key="grant.user_id" 
            class="grant-card"
          >
            <div class="grant-header">
              <div class="grant-user">
                <h3>{{ getUserName(grant.user_id) }}</h3>
                <span class="grant-email">{{ getUserEmail(grant.user_id) }}</span>
              </div>
              <StatusBadge status="complete" size="medium" />
            </div>

            <div class="grant-details">
              <div class="grant-field">
                <span class="label">{{ $t('admin.tempAccess.grantedAt') }}:</span>
                <span class="value">{{ formatDateTime(grant.grant_timestamp) }}</span>
              </div>
              <div class="grant-field">
                <span class="label">{{ $t('admin.tempAccess.expiresAt') }}:</span>
                <span class="value">{{ formatDateTime(grant.expiration_timestamp) }}</span>
              </div>
              <div class="grant-field">
                <span class="label">{{ $t('admin.tempAccess.remainingTime') }}:</span>
                <span class="value remaining-time" :class="getRemainingTimeClass(grant.remaining_hours)">
                  {{ formatRemainingTime(grant.remaining_hours) }}
                </span>
              </div>
              <div class="grant-field">
                <span class="label">{{ $t('admin.tempAccess.grantedBy') }}:</span>
                <span class="value">{{ grant.granted_by_admin_id }}</span>
              </div>
              <div v-if="grant.notes" class="grant-field">
                <span class="label">{{ $t('admin.tempAccess.notes') }}:</span>
                <span class="value">{{ grant.notes }}</span>
              </div>
            </div>

            <div class="grant-actions">
              <BaseButton
                variant="danger"
                size="small"
                :disabled="revokingGrants.has(grant.user_id)"
                :loading="revokingGrants.has(grant.user_id)"
                @click="handleRevoke(grant)"
              >
                {{ $t('admin.tempAccess.revoke') }}
              </BaseButton>
            </div>
          </div>
        </div>
      </div>

      <!-- Grant History -->
      <div class="grants-section">
        <div class="section-header">
          <h2>{{ $t('admin.tempAccess.grantHistory') }}</h2>
          <span class="grant-count">{{ inactiveGrants.length }}</span>
        </div>

        <MessageAlert 
          v-if="inactiveGrants.length === 0" 
          type="info" 
          :message="$t('admin.tempAccess.noHistory')"
        />

        <div v-else class="grants-list">
          <div 
            v-for="grant in inactiveGrants" 
            :key="`${grant.user_id}-${grant.grant_timestamp}`" 
            class="grant-card history-card"
          >
            <div class="grant-header">
              <div class="grant-user">
                <h3>{{ getUserName(grant.user_id) }}</h3>
                <span class="grant-email">{{ getUserEmail(grant.user_id) }}</span>
              </div>
              <StatusBadge 
                :status="grant.status === 'expired' ? 'forfait' : 'incomplete'" 
                size="medium" 
              />
            </div>

            <div class="grant-details">
              <div class="grant-field">
                <span class="label">{{ $t('admin.tempAccess.grantedAt') }}:</span>
                <span class="value">{{ formatDateTime(grant.grant_timestamp) }}</span>
              </div>
              <div class="grant-field">
                <span class="label">{{ $t('admin.tempAccess.expiresAt') }}:</span>
                <span class="value">{{ formatDateTime(grant.expiration_timestamp) }}</span>
              </div>
              <div class="grant-field">
                <span class="label">{{ $t('admin.tempAccess.status') }}:</span>
                <span class="value">{{ $t(`admin.tempAccess.status_${grant.status}`) }}</span>
              </div>
              <div v-if="grant.revoked_at" class="grant-field">
                <span class="label">{{ $t('admin.tempAccess.revokedAt') }}:</span>
                <span class="value">{{ formatDateTime(grant.revoked_at) }}</span>
              </div>
              <div v-if="grant.revoked_by_admin_id" class="grant-field">
                <span class="label">{{ $t('admin.tempAccess.revokedBy') }}:</span>
                <span class="value">{{ grant.revoked_by_admin_id }}</span>
              </div>
              <div v-if="grant.notes" class="grant-field">
                <span class="label">{{ $t('admin.tempAccess.notes') }}:</span>
                <span class="value">{{ grant.notes }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useConfirm } from '../../composables/useConfirm'
import apiClient from '../../services/apiClient'
import BaseButton from '../../components/base/BaseButton.vue'
import LoadingSpinner from '../../components/base/LoadingSpinner.vue'
import MessageAlert from '../../components/composite/MessageAlert.vue'
import StatusBadge from '../../components/base/StatusBadge.vue'
import TemporaryAccessGrantForm from '../../components/admin/TemporaryAccessGrantForm.vue'

const { t } = useI18n()
const { confirm } = useConfirm()

const initialLoading = ref(true)
const loadError = ref(null)
const revokeError = ref('')
const grants = ref([])
const teamManagers = ref([])
const revokingGrants = ref(new Set())
const refreshInterval = ref(null)

const activeGrants = computed(() => {
  return grants.value.filter(g => g.status === 'active')
})

const inactiveGrants = computed(() => {
  return grants.value.filter(g => g.status !== 'active')
})

const getUserName = (userId) => {
  const manager = teamManagers.value.find(m => m.user_id === userId)
  if (manager) {
    return `${manager.first_name} ${manager.last_name}`
  }
  return userId
}

const getUserEmail = (userId) => {
  const manager = teamManagers.value.find(m => m.user_id === userId)
  return manager?.email || ''
}

const formatDateTime = (timestamp) => {
  if (!timestamp) return '-'
  try {
    const date = new Date(timestamp)
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return timestamp
  }
}

const formatRemainingTime = (hours) => {
  if (hours <= 0) return t('admin.tempAccess.expired')
  
  if (hours < 1) {
    const minutes = Math.round(hours * 60)
    return t('admin.tempAccess.minutesRemaining', { minutes })
  }
  
  if (hours < 24) {
    return t('admin.tempAccess.hoursRemaining', { hours: Math.round(hours * 10) / 10 })
  }
  
  const days = Math.floor(hours / 24)
  const remainingHours = Math.round(hours % 24)
  return t('admin.tempAccess.daysRemaining', { days, hours: remainingHours })
}

const getRemainingTimeClass = (hours) => {
  if (hours <= 0) return 'expired'
  if (hours < 6) return 'warning'
  return 'active'
}

const loadTeamManagers = async () => {
  try {
    const response = await apiClient.get('/admin/team-managers')
    teamManagers.value = response.data.data.team_managers || []
  } catch (err) {
    console.error('Failed to load team managers:', err)
    // Don't fail the whole page if team managers can't load
    // The form will still work with user IDs
  }
}

const loadGrants = async () => {
  loadError.value = null
  
  try {
    console.log('Loading grants from /admin/temporary-access/list...')
    const response = await apiClient.get('/admin/temporary-access/list')
    console.log('Grants response:', response.data)
    grants.value = response.data.data.grants || []
  } catch (err) {
    console.error('Failed to load grants:', err)
    console.error('Error details:', err.response?.data || err.message)
    loadError.value = t('admin.tempAccess.loadError')
  } finally {
    initialLoading.value = false
  }
}

const handleGrantCreated = async (newGrant) => {
  // Reload grants to get the updated list
  await loadGrants()
}

const handleRevoke = async (grant) => {
  const confirmed = await confirm({
    title: t('admin.tempAccess.confirmRevokeTitle'),
    message: t('admin.tempAccess.confirmRevoke', { user: getUserName(grant.user_id) }),
    confirmText: t('admin.tempAccess.revoke'),
    cancelText: t('common.cancel'),
    variant: 'danger'
  })
  
  if (!confirmed) {
    return
  }
  
  revokingGrants.value.add(grant.user_id)
  revokeError.value = ''
  
  try {
    await apiClient.post('/admin/temporary-access/revoke', {
      user_id: grant.user_id
    })
    
    // Reload grants to get the updated list
    await loadGrants()
  } catch (err) {
    console.error('Failed to revoke grant:', err)
    revokeError.value = t('admin.tempAccess.revokeError')
  } finally {
    revokingGrants.value.delete(grant.user_id)
  }
}

const startAutoRefresh = () => {
  // Refresh every 60 seconds
  refreshInterval.value = setInterval(() => {
    loadGrants()
  }, 60000)
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

onMounted(async () => {
  try {
    await loadTeamManagers()
    await loadGrants()
    startAutoRefresh()
  } catch (err) {
    console.error('Error during component mount:', err)
    loadError.value = t('admin.tempAccess.loadError')
    initialLoading.value = false
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.admin-temp-access {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-xxl);
}

.page-header {
  margin-bottom: var(--spacing-xxl);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--color-primary);
  text-decoration: none;
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-sm);
}

.back-link:hover {
  text-decoration: underline;
}

.page-header h1 {
  font-size: var(--font-size-3xl);
  color: var(--color-dark);
  margin-bottom: var(--spacing-sm);
  font-weight: var(--font-weight-semibold);
}

.subtitle {
  color: var(--color-muted);
  font-size: var(--font-size-lg);
}

.content-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xxl);
}

.grant-form-section {
  margin-bottom: var(--spacing-xl);
}

.grants-section {
  background: var(--color-white);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-xxl);
  box-shadow: var(--shadow-sm);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.section-header h2 {
  font-size: var(--font-size-xl);
  color: var(--color-dark);
  font-weight: var(--font-weight-semibold);
}

.grant-count {
  background: var(--color-light);
  color: var(--color-dark);
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--badge-border-radius);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.grants-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.grant-card {
  background: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-lg);
}

.history-card {
  opacity: 0.8;
}

.grant-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.grant-user h3 {
  font-size: var(--font-size-lg);
  color: var(--color-dark);
  margin-bottom: var(--spacing-xs);
  font-weight: var(--font-weight-semibold);
}

.grant-email {
  color: var(--color-muted);
  font-size: var(--font-size-sm);
}

.grant-details {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
}

.grant-field {
  display: flex;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.grant-field .label {
  color: var(--color-muted);
  min-width: 120px;
  font-weight: var(--font-weight-medium);
}

.grant-field .value {
  color: var(--color-dark);
  flex: 1;
}

.remaining-time.active {
  color: var(--color-success);
  font-weight: var(--font-weight-semibold);
}

.remaining-time.warning {
  color: var(--color-warning);
  font-weight: var(--font-weight-semibold);
}

.remaining-time.expired {
  color: var(--color-danger);
  font-weight: var(--font-weight-semibold);
}

.grant-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .admin-temp-access {
    padding: var(--spacing-lg);
    max-width: 100%;
  }

  .page-header {
    margin-bottom: var(--spacing-xl);
  }

  .page-header h1 {
    font-size: var(--font-size-2xl);
  }

  .subtitle {
    font-size: var(--font-size-base);
  }

  .back-link {
    font-size: var(--form-input-font-size-mobile);
    min-height: var(--touch-target-min-size);
    display: inline-flex;
    align-items: center;
  }

  .content-container {
    gap: var(--spacing-xl);
  }

  .grants-section {
    padding: var(--spacing-lg);
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }

  .section-header h2 {
    font-size: var(--font-size-lg);
  }

  .grant-card {
    padding: var(--spacing-md);
  }

  .grant-header {
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .grant-field {
    flex-direction: column;
    gap: var(--spacing-xs);
  }

  .grant-field .label {
    min-width: auto;
  }

  .grant-actions :deep(button) {
    width: 100%;
  }
}
</style>
