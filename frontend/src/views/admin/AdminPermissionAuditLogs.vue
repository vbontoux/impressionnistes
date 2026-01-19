<template>
  <div class="admin-audit-logs">
    <div class="page-header">
      <router-link to="/admin" class="back-link">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        {{ $t('common.back') }}
      </router-link>
      <h1>{{ $t('admin.auditLogs.title') }}</h1>
      <p class="subtitle">{{ $t('admin.auditLogs.subtitle') }}</p>
    </div>

    <LoadingSpinner v-if="initialLoading" :message="$t('common.loading')" />

    <MessageAlert 
      v-else-if="loadError" 
      type="error" 
      :message="loadError"
    >
      <template #action>
        <BaseButton variant="secondary" size="small" @click="loadLogs">
          {{ $t('common.retry') }}
        </BaseButton>
      </template>
    </MessageAlert>

    <div v-else class="content-container">
      <!-- Filters -->
      <div class="filters-section">
        <h2>{{ $t('admin.auditLogs.filters') }}</h2>
        
        <div class="filters-grid">
          <FormGroup :label="$t('admin.auditLogs.filterByUser')">
            <select v-model="filters.user_id" @change="applyFilters">
              <option value="">{{ $t('admin.auditLogs.allUsers') }}</option>
              <option v-for="manager in teamManagers" :key="manager.user_id" :value="manager.user_id">
                {{ manager.first_name }} {{ manager.last_name }} ({{ manager.email }})
              </option>
            </select>
          </FormGroup>

          <FormGroup :label="$t('admin.auditLogs.filterByAction')">
            <select v-model="filters.action" @change="applyFilters">
              <option value="">{{ $t('admin.auditLogs.allActions') }}</option>
              <option value="create_crew_member">{{ $t('admin.auditLogs.action_create_crew_member') }}</option>
              <option value="edit_crew_member">{{ $t('admin.auditLogs.action_edit_crew_member') }}</option>
              <option value="delete_crew_member">{{ $t('admin.auditLogs.action_delete_crew_member') }}</option>
              <option value="create_boat_registration">{{ $t('admin.auditLogs.action_create_boat_registration') }}</option>
              <option value="edit_boat_registration">{{ $t('admin.auditLogs.action_edit_boat_registration') }}</option>
              <option value="delete_boat_registration">{{ $t('admin.auditLogs.action_delete_boat_registration') }}</option>
              <option value="process_payment">{{ $t('admin.auditLogs.action_process_payment') }}</option>
            </select>
          </FormGroup>

          <FormGroup :label="$t('admin.auditLogs.filterByLogType')">
            <select v-model="filters.log_type" @change="applyFilters">
              <option value="all">{{ $t('admin.auditLogs.allLogTypes') }}</option>
              <option value="denial">{{ $t('admin.auditLogs.logType_denial') }}</option>
              <option value="bypass">{{ $t('admin.auditLogs.logType_bypass') }}</option>
              <option value="config">{{ $t('admin.auditLogs.logType_config') }}</option>
            </select>
          </FormGroup>

          <FormGroup :label="$t('admin.auditLogs.filterByDateRange')">
            <div class="date-range">
              <input 
                v-model="filters.start_date" 
                type="date" 
                @change="applyFilters"
                :max="filters.end_date || today"
              />
              <span>{{ $t('admin.auditLogs.to') }}</span>
              <input 
                v-model="filters.end_date" 
                type="date" 
                @change="applyFilters"
                :min="filters.start_date"
                :max="today"
              />
            </div>
          </FormGroup>
        </div>

        <div class="filter-actions">
          <BaseButton variant="secondary" size="small" @click="clearFilters">
            {{ $t('admin.auditLogs.clearFilters') }}
          </BaseButton>
          <BaseButton variant="primary" size="small" @click="exportToCSV" :disabled="logs.length === 0">
            {{ $t('admin.auditLogs.exportCSV') }}
          </BaseButton>
          <BaseButton 
            variant="danger" 
            size="small" 
            @click="confirmClearAllLogs" 
            :disabled="logs.length === 0 || clearingLogs"
            :loading="clearingLogs"
          >
            {{ clearingLogs ? $t('admin.auditLogs.clearing') : $t('admin.auditLogs.clearAllLogs') }}
          </BaseButton>
        </div>
      </div>

      <!-- Logs Table -->
      <div class="logs-section">
        <div class="section-header">
          <h2>{{ $t('admin.auditLogs.logs') }}</h2>
          <span class="log-count">{{ logs.length }} {{ $t('admin.auditLogs.entries') }}</span>
        </div>

        <MessageAlert 
          v-if="logs.length === 0" 
          type="info" 
          :message="$t('admin.auditLogs.noLogs')"
        />

        <div v-else class="logs-table-container">
          <table class="logs-table">
            <thead>
              <tr>
                <th @click="sortBy('timestamp')">
                  {{ $t('admin.auditLogs.timestamp') }}
                  <span v-if="sortColumn === 'timestamp'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('log_type')">
                  {{ $t('admin.auditLogs.logType') }}
                  <span v-if="sortColumn === 'log_type'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('user_id')">
                  {{ $t('admin.auditLogs.user') }}
                  <span v-if="sortColumn === 'user_id'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('action')">
                  {{ $t('admin.auditLogs.action') }}
                  <span v-if="sortColumn === 'action'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th>{{ $t('admin.auditLogs.details') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in sortedLogs" :key="`${log.PK}-${log.SK}`" :class="getLogRowClass(log)">
                <td class="timestamp-cell">{{ formatDateTime(log.SK) }}</td>
                <td>
                  <span :class="['log-type-badge', `log-type-badge-${log.log_type}`]">
                    {{ $t(`admin.auditLogs.logType_${log.log_type}`) }}
                  </span>
                </td>
                <td class="user-cell">
                  <div class="user-info">
                    <span class="user-name">{{ getUserName(log.user_id) }}</span>
                    <span class="user-email">{{ getUserEmail(log.user_id) }}</span>
                  </div>
                </td>
                <td class="action-cell">{{ formatAction(log.action) }}</td>
                <td class="details-cell">
                  <div class="log-details">
                    <div v-if="log.log_type === 'denial'" class="denial-details">
                      <span class="detail-label">{{ $t('admin.auditLogs.reason') }}:</span>
                      <span class="detail-value">{{ formatDenialReason(log.denial_reason) }}</span>
                    </div>
                    <div v-if="log.log_type === 'bypass'" class="bypass-details">
                      <span class="detail-label">{{ $t('admin.auditLogs.bypassReason') }}:</span>
                      <span class="detail-value">{{ formatBypassReason(log.bypass_reason) }}</span>
                      <span v-if="log.impersonated_user_id" class="impersonated-user">
                        ({{ $t('admin.auditLogs.impersonating') }}: {{ getUserName(log.impersonated_user_id) }})
                      </span>
                    </div>
                    <div v-if="log.resource_type" class="resource-info">
                      <span class="detail-label">{{ $t('admin.auditLogs.resource') }}:</span>
                      <span class="detail-value">{{ log.resource_type }}</span>
                      <span v-if="log.resource_id" class="resource-id">({{ log.resource_id }})</span>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="hasMore" class="pagination">
          <BaseButton 
            variant="secondary" 
            size="small" 
            @click="loadMore"
            :disabled="loadingMore"
            :loading="loadingMore"
          >
            {{ $t('admin.auditLogs.loadMore') }}
          </BaseButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useConfirm } from '../../composables/useConfirm'
import apiClient from '../../services/apiClient'
import BaseButton from '../../components/base/BaseButton.vue'
import LoadingSpinner from '../../components/base/LoadingSpinner.vue'
import MessageAlert from '../../components/composite/MessageAlert.vue'
import FormGroup from '../../components/composite/FormGroup.vue'

const { t } = useI18n()
const { confirm } = useConfirm()

const initialLoading = ref(true)
const loadingMore = ref(false)
const loadError = ref(null)
const clearingLogs = ref(false)
const logs = ref([])
const teamManagers = ref([])
const nextToken = ref(null)
const hasMore = ref(false)
const sortColumn = ref('timestamp')
const sortDirection = ref('desc')

const filters = ref({
  user_id: '',
  action: '',
  log_type: 'all',
  start_date: '',
  end_date: ''
})

const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

const sortedLogs = computed(() => {
  const sorted = [...logs.value]
  
  sorted.sort((a, b) => {
    let aVal = a[sortColumn.value]
    let bVal = b[sortColumn.value]
    
    // Handle timestamp sorting (SK field)
    if (sortColumn.value === 'timestamp') {
      aVal = a.SK
      bVal = b.SK
    }
    
    if (aVal < bVal) return sortDirection.value === 'asc' ? -1 : 1
    if (aVal > bVal) return sortDirection.value === 'asc' ? 1 : -1
    return 0
  })
  
  return sorted
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
    // Extract timestamp from SK format: "2026-01-14T10:00:00.123Z#user-123"
    const dateStr = timestamp.split('#')[0]
    const date = new Date(dateStr)
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (e) {
    return timestamp
  }
}

const formatAction = (action) => {
  if (!action) return '-'
  return t(`admin.auditLogs.action_${action}`, action)
}

const formatDenialReason = (reason) => {
  if (!reason) return '-'
  return t(`admin.auditLogs.denialReason_${reason}`, reason)
}

const formatBypassReason = (reason) => {
  if (!reason) return '-'
  return t(`admin.auditLogs.bypassReason_${reason}`, reason)
}

const getLogRowClass = (log) => {
  return `log-row log-type-${log.log_type}`
}

const sortBy = (column) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'desc'
  }
}

const loadTeamManagers = async () => {
  try {
    const response = await apiClient.get('/admin/team-managers')
    teamManagers.value = response.data.data.team_managers || []
  } catch (err) {
    console.error('Failed to load team managers:', err)
  }
}

const loadLogs = async (append = false) => {
  if (!append) {
    initialLoading.value = true
    logs.value = []
    nextToken.value = null
  } else {
    loadingMore.value = true
  }
  
  loadError.value = null
  
  try {
    const params = {
      limit: 50
    }
    
    if (filters.value.user_id) params.user_id = filters.value.user_id
    if (filters.value.action) params.action = filters.value.action
    if (filters.value.log_type) params.log_type = filters.value.log_type
    if (filters.value.start_date) params.start_date = filters.value.start_date
    if (filters.value.end_date) params.end_date = filters.value.end_date
    if (append && nextToken.value) params.next_token = nextToken.value
    
    const response = await apiClient.get('/admin/permissions/audit-logs', { params })
    
    if (append) {
      logs.value = [...logs.value, ...response.data.logs]
    } else {
      logs.value = response.data.logs || []
    }
    
    nextToken.value = response.data.next_token
    hasMore.value = response.data.has_more || false
  } catch (err) {
    console.error('Failed to load audit logs:', err)
    loadError.value = t('admin.auditLogs.loadError')
  } finally {
    initialLoading.value = false
    loadingMore.value = false
  }
}

const loadMore = async () => {
  await loadLogs(true)
}

const applyFilters = async () => {
  await loadLogs(false)
}

const clearFilters = async () => {
  filters.value = {
    user_id: '',
    action: '',
    log_type: 'all',
    start_date: '',
    end_date: ''
  }
  await loadLogs(false)
}

const exportToCSV = () => {
  const headers = [
    'Timestamp',
    'Log Type',
    'User',
    'Email',
    'Action',
    'Reason',
    'Resource Type',
    'Resource ID'
  ]
  
  const rows = logs.value.map(log => [
    formatDateTime(log.SK),
    log.log_type,
    getUserName(log.user_id),
    getUserEmail(log.user_id),
    log.action || '',
    log.denial_reason || log.bypass_reason || '',
    log.resource_type || '',
    log.resource_id || ''
  ])
  
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `audit-logs-${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const confirmClearAllLogs = async () => {
  const confirmed = await confirm({
    title: t('admin.auditLogs.confirmClearTitle'),
    message: t('admin.auditLogs.confirmClearMessage'),
    variant: 'danger'
  })
  
  if (confirmed) {
    await clearAllLogs()
  }
}

const clearAllLogs = async () => {
  clearingLogs.value = true
  
  try {
    // Step 1: Export logs automatically before clearing
    exportToCSV()
    
    // Step 2: Wait a moment to ensure export completes
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // Step 3: Call API to clear logs
    const response = await apiClient.delete('/admin/permissions/audit-logs')
    
    // Step 4: Show success message
    const deletedCount = response.data.deleted_count || 0
    alert(t('admin.auditLogs.clearSuccess', { count: deletedCount }))
    
    // Step 5: Reload logs (should be empty now)
    await loadLogs(false)
  } catch (err) {
    console.error('Failed to clear audit logs:', err)
    alert(t('admin.auditLogs.clearError'))
  } finally {
    clearingLogs.value = false
  }
}

onMounted(async () => {
  try {
    await loadTeamManagers()
    await loadLogs()
  } catch (err) {
    console.error('Error during component mount:', err)
    loadError.value = t('admin.auditLogs.loadError')
    initialLoading.value = false
  }
})
</script>

<style scoped>
.admin-audit-logs {
  max-width: 100%;
  width: 100%;
  margin: 0 auto;
  padding: var(--spacing-xxl);
  box-sizing: border-box;
  overflow-x: hidden;
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

.filters-section,
.logs-section {
  background: var(--color-white);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-xxl);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  box-sizing: border-box;
}

.filters-section h2,
.logs-section h2 {
  font-size: var(--font-size-xl);
  color: var(--color-dark);
  margin-bottom: var(--spacing-xl);
  font-weight: var(--font-weight-semibold);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(250px, 100%), 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.date-range {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.date-range input {
  flex: 1;
  min-width: 0;
  max-width: 100%;
}

.filter-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: flex-end;
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.log-count {
  background: var(--color-light);
  color: var(--color-dark);
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--badge-border-radius);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.logs-table-container {
  overflow-x: auto;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
}

.logs-table thead {
  background: var(--color-light);
}

.logs-table th {
  padding: var(--spacing-md);
  text-align: left;
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
  cursor: pointer;
  user-select: none;
}

.logs-table th:hover {
  background: var(--color-border);
}

.logs-table td {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.log-row.log-type-denial {
  background: rgba(220, 53, 69, 0.05);
}

.log-row.log-type-bypass {
  background: rgba(40, 167, 69, 0.05);
}

.log-row.log-type-config {
  background: rgba(0, 123, 255, 0.05);
}

.timestamp-cell {
  white-space: nowrap;
  color: var(--color-muted);
}

.log-type-badge {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--badge-border-radius);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  text-transform: capitalize;
}

.log-type-badge-denial {
  background: rgba(220, 53, 69, 0.1);
  color: var(--color-danger);
  border: 1px solid rgba(220, 53, 69, 0.3);
}

.log-type-badge-bypass {
  background: rgba(40, 167, 69, 0.1);
  color: var(--color-success);
  border: 1px solid rgba(40, 167, 69, 0.3);
}

.log-type-badge-config {
  background: rgba(0, 123, 255, 0.1);
  color: var(--color-primary);
  border: 1px solid rgba(0, 123, 255, 0.3);
}

.user-cell {
  min-width: 200px;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.user-name {
  color: var(--color-dark);
  font-weight: var(--font-weight-medium);
}

.user-email {
  color: var(--color-muted);
  font-size: var(--font-size-xs);
}

.action-cell {
  font-weight: var(--font-weight-medium);
  color: var(--color-dark);
}

.details-cell {
  min-width: 300px;
}

.log-details {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.detail-label {
  color: var(--color-muted);
  font-weight: var(--font-weight-medium);
  margin-right: var(--spacing-xs);
}

.detail-value {
  color: var(--color-dark);
}

.impersonated-user {
  color: var(--color-muted);
  font-style: italic;
  margin-left: var(--spacing-xs);
}

.resource-id {
  color: var(--color-muted);
  margin-left: var(--spacing-xs);
}

.pagination {
  display: flex;
  justify-content: center;
  padding-top: var(--spacing-xl);
  border-top: 1px solid var(--color-border);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .admin-audit-logs {
    padding: var(--spacing-lg);
  }

  .page-header h1 {
    font-size: var(--font-size-2xl);
  }

  .filters-grid {
    grid-template-columns: 1fr;
  }

  .filter-actions {
    flex-direction: column;
  }

  .filter-actions :deep(button) {
    width: 100%;
  }

  .logs-table {
    font-size: var(--font-size-xs);
  }

  .logs-table th,
  .logs-table td {
    padding: var(--spacing-sm);
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }
}
</style>
