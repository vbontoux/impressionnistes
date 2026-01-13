<template>
  <div class="admin-club-managers">
    <ListHeader
      :title="$t('admin.clubManagers.title')"
      :subtitle="$t('admin.clubManagers.subtitle')"
      v-model:viewMode="viewMode"
    />

    <ListFilters
      v-model:searchQuery="searchTerm"
      :searchPlaceholder="$t('admin.clubManagers.searchPlaceholder')"
      @clear="clearFilters"
    />

    <!-- Loading state -->
    <LoadingSpinner v-if="loading" :message="$t('common.loading')" />

    <!-- Error state -->
    <MessageAlert 
      v-if="error" 
      type="error" 
      :message="error"
    >
      <BaseButton size="small" variant="primary" @click="fetchClubManagers">
        {{ $t('common.retry') }}
      </BaseButton>
    </MessageAlert>

    <!-- Empty state -->
    <EmptyState 
      v-if="!loading && !error && managers.length === 0"
      :message="$t('admin.clubManagers.noManagers')"
    />

    <!-- No search results -->
    <EmptyState 
      v-if="!loading && !error && managers.length > 0 && filteredManagers.length === 0"
      :message="$t('admin.clubManagers.noSearchResults')"
    >
      <template #action>
        <BaseButton size="small" variant="secondary" @click="clearFilters">
          {{ $t('admin.clubManagers.clearSearch') }}
        </BaseButton>
      </template>
    </EmptyState>

    <!-- Club managers table/cards -->
    <div v-if="!loading && !error && managers.length > 0 && filteredManagers.length > 0">
      <p class="count">{{ $t('admin.clubManagers.totalCount', { count: filteredManagers.length }) }}</p>
      
      <!-- Table View -->
      <div v-if="viewMode === 'table'" class="managers-table-container">
        <table class="managers-table">
          <thead>
            <tr>
              <th class="checkbox-col">
                <input 
                  type="checkbox" 
                  :checked="allSelected"
                  @change="toggleSelectAll"
                  :aria-label="$t('admin.clubManagers.selectAll')"
                />
              </th>
              <th @click="sortBy('last_name')">
                {{ $t('admin.clubManagers.name') }}
                <span v-if="sortField === 'last_name'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
              </th>
              <th @click="sortBy('email')">
                {{ $t('admin.clubManagers.email') }}
                <span v-if="sortField === 'email'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
              </th>
              <th @click="sortBy('phone_number')">
                {{ $t('admin.clubManagers.phone') }}
                <span v-if="sortField === 'phone_number'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
              </th>
              <th @click="sortBy('club_affiliation')">
                {{ $t('admin.clubManagers.clubAffiliation') }}
                <span v-if="sortField === 'club_affiliation'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
              </th>
              <th @click="sortBy('is_admin')">
                {{ $t('admin.clubManagers.role') }}
                <span v-if="sortField === 'is_admin'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="manager in filteredManagers" 
              :key="manager.user_id"
              :class="{ 'selected': selectedIds.has(manager.user_id) }"
            >
              <td class="checkbox-col">
                <input 
                  type="checkbox" 
                  :checked="selectedIds.has(manager.user_id)"
                  @change="toggleSelection(manager.user_id)"
                  :aria-label="$t('admin.clubManagers.selectManager', { name: `${manager.first_name} ${manager.last_name}` })"
                />
              </td>
              <td>{{ manager.first_name }} {{ manager.last_name }}</td>
              <td>
                <a :href="`mailto:${manager.email}`" class="email-link">
                  {{ manager.email }}
                </a>
              </td>
              <td>
                <a 
                  v-if="manager.phone_number" 
                  :href="`tel:${manager.phone_number}`" 
                  class="phone-link"
                >
                  {{ manager.phone_number }}
                </a>
                <span v-else class="no-data">-</span>
              </td>
              <td><span class="club-box">{{ manager.club_affiliation || '-' }}</span></td>
              <td>
                <span v-if="manager.is_admin" class="admin-badge">{{ $t('admin.clubManagers.admin') }}</span>
                <span v-else class="no-data">-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Card View -->
      <div v-else class="manager-cards">
        <div
          v-for="manager in filteredManagers"
          :key="manager.user_id"
          class="manager-card"
          :class="{ 'selected': selectedIds.has(manager.user_id) }"
        >
          <div class="card-header">
            <input 
              type="checkbox" 
              :checked="selectedIds.has(manager.user_id)"
              @change="toggleSelection(manager.user_id)"
              :aria-label="$t('admin.clubManagers.selectManager', { name: `${manager.first_name} ${manager.last_name}` })"
              class="card-checkbox"
            />
            <h3>{{ manager.first_name }} {{ manager.last_name }}</h3>
          </div>

          <div class="card-details">
            <div class="detail-row">
              <span class="label">{{ $t('admin.clubManagers.email') }}&nbsp;:</span>
              <a :href="`mailto:${manager.email}`" class="email-link">
                {{ manager.email }}
              </a>
            </div>
            <div class="detail-row" v-if="manager.phone_number">
              <span class="label">{{ $t('admin.clubManagers.phone') }}&nbsp;:</span>
              <a :href="`tel:${manager.phone_number}`" class="phone-link">
                {{ manager.phone_number }}
              </a>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('admin.clubManagers.clubAffiliation') }}&nbsp;:</span>
              <span class="club-box">{{ manager.club_affiliation || '-' }}</span>
            </div>
            <div class="detail-row" v-if="manager.is_admin">
              <span class="label">{{ $t('admin.clubManagers.role') }}&nbsp;:</span>
              <span class="admin-badge">{{ $t('admin.clubManagers.admin') }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Selection actions -->
      <div v-if="filteredManagers.length > 0" class="selection-actions">
        <div class="selection-info">
          <span v-if="selectedIds.size > 0">
            {{ $t('admin.clubManagers.selectedCount', { count: selectedIds.size }) }}
          </span>
        </div>
        <div class="action-buttons">
          <BaseButton 
            size="small"
            variant="secondary"
            @click="selectAll" 
            :disabled="allSelected"
          >
            {{ $t('admin.clubManagers.selectAll') }}
          </BaseButton>
          <BaseButton 
            size="small"
            variant="secondary"
            @click="deselectAll" 
            :disabled="selectedIds.size === 0"
          >
            {{ $t('admin.clubManagers.deselectAll') }}
          </BaseButton>
          <BaseButton 
            size="small"
            variant="primary"
            @click="emailSelected" 
            :disabled="selectedIds.size === 0"
          >
            {{ $t('admin.clubManagers.emailSelected') }}
          </BaseButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import apiClient from '../../services/apiClient'
import ListHeader from '../../components/shared/ListHeader.vue'
import ListFilters from '../../components/shared/ListFilters.vue'
import BaseButton from '../../components/base/BaseButton.vue'
import LoadingSpinner from '../../components/base/LoadingSpinner.vue'
import EmptyState from '../../components/base/EmptyState.vue'
import MessageAlert from '../../components/composite/MessageAlert.vue'

export default {
  name: 'AdminClubManagers',
  components: {
    ListHeader,
    ListFilters,
    BaseButton,
    LoadingSpinner,
    EmptyState,
    MessageAlert
  },
  setup() {
    const { t } = useI18n()

    // Detect if mobile on mount
    const isMobile = ref(window.innerWidth < 768)
    
    // State
    const managers = ref([])
    const loading = ref(false)
    const error = ref(null)
    const searchTerm = ref('')
    const sortField = ref('last_name')
    const sortDirection = ref('asc')
    // Default to cards view on mobile, table on desktop (use 'cards' to match ListHeader)
    const savedViewMode = localStorage.getItem('adminClubManagersViewMode')
    const defaultViewMode = isMobile.value ? 'cards' : (savedViewMode || 'table')
    const viewMode = ref(defaultViewMode)
    const selectedIds = ref(new Set())

    // Handle window resize
    const handleResize = () => {
      isMobile.value = window.innerWidth < 768
    }

    // Fetch club managers
    const fetchClubManagers = async () => {
      loading.value = true
      error.value = null
      
      try {
        const response = await apiClient.get('/admin/team-managers')
        managers.value = response.data.data?.team_managers || []
      } catch (err) {
        console.error('Failed to fetch club managers:', err)
        error.value = t('admin.clubManagers.fetchError')
      } finally {
        loading.value = false
      }
    }

    // Computed: filtered managers
    const filteredManagers = computed(() => {
      let result = managers.value

      // Apply search filter
      if (searchTerm.value) {
        const search = searchTerm.value.toLowerCase()
        result = result.filter(manager => {
          return (
            manager.first_name?.toLowerCase().includes(search) ||
            manager.last_name?.toLowerCase().includes(search) ||
            manager.email?.toLowerCase().includes(search) ||
            manager.phone_number?.toLowerCase().includes(search) ||
            manager.club_affiliation?.toLowerCase().includes(search)
          )
        })
      }

      // Apply sorting
      result = [...result].sort((a, b) => {
        let aVal = a[sortField.value] || ''
        let bVal = b[sortField.value] || ''
        
        if (typeof aVal === 'string') {
          aVal = aVal.toLowerCase()
          bVal = bVal.toLowerCase()
        }

        if (sortDirection.value === 'asc') {
          return aVal > bVal ? 1 : -1
        } else {
          return aVal < bVal ? 1 : -1
        }
      })

      return result
    })

    // Computed: all selected
    const allSelected = computed(() => {
      return filteredManagers.value.length > 0 && 
             filteredManagers.value.every(m => selectedIds.value.has(m.user_id))
    })

    // Methods
    const sortBy = (field) => {
      if (sortField.value === field) {
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
      } else {
        sortField.value = field
        sortDirection.value = 'asc'
      }
    }

    const clearFilters = () => {
      searchTerm.value = ''
    }

    const toggleSelection = (userId) => {
      const newSet = new Set(selectedIds.value)
      if (newSet.has(userId)) {
        newSet.delete(userId)
      } else {
        newSet.add(userId)
      }
      selectedIds.value = newSet
    }

    const toggleSelectAll = () => {
      if (allSelected.value) {
        deselectAll()
      } else {
        selectAll()
      }
    }

    const selectAll = () => {
      const newSet = new Set()
      filteredManagers.value.forEach(manager => {
        newSet.add(manager.user_id)
      })
      selectedIds.value = newSet
    }

    const deselectAll = () => {
      selectedIds.value = new Set()
    }

    const emailSelected = () => {
      const selectedManagers = managers.value.filter(m => selectedIds.value.has(m.user_id))
      const emails = selectedManagers.map(m => m.email).join(',')
      
      // Open email client with BCC field
      window.location.href = `mailto:?bcc=${encodeURIComponent(emails)}`
    }

    // Lifecycle
    onMounted(() => {
      fetchClubManagers()
      window.addEventListener('resize', handleResize)
    })

    // Cleanup
    const onUnmounted = () => {
      window.removeEventListener('resize', handleResize)
    }

    // Watch for view mode changes and save to localStorage
    watch(viewMode, (newMode) => {
      localStorage.setItem('adminClubManagersViewMode', newMode)
    })

    return {
      managers,
      loading,
      error,
      searchTerm,
      sortField,
      sortDirection,
      viewMode,
      selectedIds,
      filteredManagers,
      allSelected,
      isMobile,
      fetchClubManagers,
      sortBy,
      clearFilters,
      toggleSelection,
      toggleSelectAll,
      selectAll,
      deselectAll,
      emailSelected,
      onUnmounted
    }
  }
}
</script>

<style scoped>
.admin-club-managers {
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
}

/* Count */
.count {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--color-muted);
  font-size: var(--font-size-sm);
}

/* Table View */
.managers-table-container {
  background-color: white;
  border-radius: var(--border-radius);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  overflow-x: auto;
}

.managers-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

.managers-table thead {
  background-color: var(--color-light);
}

.managers-table th {
  padding: var(--spacing-md);
  text-align: left;
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
  border-bottom: 2px solid var(--color-border);
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
  transition: background-color 0.2s;
}

.managers-table th.checkbox-col {
  width: 50px;
  cursor: default;
}

.managers-table th:not(.checkbox-col):hover {
  background-color: #e9ecef;
}

.managers-table td {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.managers-table td.checkbox-col {
  width: 50px;
}

.managers-table tbody tr {
  transition: background-color 0.2s;
}

.managers-table tbody tr:hover {
  background-color: var(--color-light);
}

.managers-table tbody tr.selected {
  background-color: #f0f8ff;
}

.managers-table input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-primary);
}

.email-link {
  color: var(--color-primary);
  text-decoration: none;
  transition: color 0.2s;
}

.email-link:hover {
  color: #0056b3;
  text-decoration: underline;
}

.email-link:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  border-radius: 2px;
}

.phone-link {
  color: var(--color-success);
  text-decoration: none;
  transition: color 0.2s;
  font-weight: var(--font-weight-medium);
}

.phone-link:hover {
  color: #1e7e34;
  text-decoration: underline;
}

.phone-link:focus {
  outline: 2px solid var(--color-success);
  outline-offset: 2px;
  border-radius: 2px;
}

.no-data {
  color: var(--color-muted);
  font-style: italic;
}

.club-box {
  display: inline-block;
  max-width: 200px;
  padding: var(--spacing-xs) var(--spacing-sm);
  background-color: var(--color-light);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  line-height: 1.3;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.admin-badge {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-sm);
  background-color: var(--color-primary);
  color: white;
  border-radius: var(--badge-border-radius);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  letter-spacing: 0.5px;
  width: fit-content;
}

/* Card View */
.manager-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-xl);
  padding: var(--spacing-md) 0;
}

.manager-card {
  background-color: white;
  border: 2px solid var(--color-border);
  border-radius: var(--border-radius);
  padding: var(--spacing-xl);
  transition: all 0.3s;
}

.manager-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.manager-card.selected {
  border-color: var(--color-primary);
  background-color: #f0f8ff;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2);
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.card-checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
  flex-shrink: 0;
  accent-color: var(--color-primary);
}

.card-header h3 {
  margin: 0;
  font-size: var(--font-size-lg);
  color: var(--color-dark);
  flex: 1;
}

.card-details {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-light);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row .label {
  font-weight: var(--font-weight-medium);
  color: var(--color-muted);
  font-size: var(--font-size-sm);
}

.detail-row .email-link,
.detail-row .club-box {
  color: var(--color-dark);
}

/* Selection Actions */
.selection-actions {
  background-color: white;
  border-radius: var(--border-radius);
  padding: var(--spacing-md) var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-md);
  flex-wrap: wrap;
  margin-top: var(--spacing-xl);
}

.selection-info {
  color: var(--color-dark);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
}

.action-buttons {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .admin-club-managers {
    padding: 0;
  }

  /* Hide table view on mobile - cards are better */
  .managers-table-container {
    padding: var(--spacing-md);
    border-radius: var(--border-radius);
    margin: 0 var(--spacing-sm);
  }

  .managers-table {
    font-size: var(--font-size-sm);
    min-width: 700px; /* Force horizontal scroll for table */
  }

  .managers-table th,
  .managers-table td {
    padding: var(--spacing-sm) var(--spacing-xs);
  }

  .managers-table th {
    font-size: var(--font-size-xs);
  }

  /* Optimize card view for mobile */
  .manager-cards {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
    padding: 0 var(--spacing-sm);
  }

  .manager-card {
    border-radius: var(--border-radius);
    padding: var(--spacing-lg);
  }

  .card-header h3 {
    font-size: var(--font-size-base);
  }

  .card-checkbox {
    width: 24px;
    height: 24px;
  }

  .detail-row {
    padding: 10px 0;
  }

  .detail-row .label {
    font-size: var(--font-size-sm);
    margin-bottom: var(--spacing-xs);
  }

  .detail-row .email-link {
    word-break: break-all;
    font-size: var(--font-size-sm);
  }

  .club-box {
    max-width: 100%;
    font-size: var(--font-size-sm);
  }

  /* Selection actions - stack vertically on mobile */
  .selection-actions {
    flex-direction: column;
    align-items: stretch;
    padding: var(--spacing-md);
    border-radius: var(--border-radius);
    margin: var(--spacing-md) var(--spacing-sm) 0;
    gap: var(--spacing-md);
  }

  .selection-info {
    text-align: center;
    font-size: var(--font-size-base);
  }

  .action-buttons {
    flex-direction: column;
    width: 100%;
    gap: 10px;
  }

  /* Count text */
  .count {
    padding: 0 var(--spacing-sm);
    font-size: var(--font-size-sm);
  }
}

/* Tablet Responsive */
@media (min-width: 768px) and (max-width: 1023px) {
  .manager-cards {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--spacing-md);
  }

  .managers-table-container {
    padding: var(--spacing-lg);
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .manager-card,
  .managers-table tbody tr,
  .email-link {
    transition: none;
  }

  .manager-card:hover {
    transform: none;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .managers-table th {
    border-bottom: 3px solid #000;
  }

  .managers-table td {
    border-bottom: 2px solid #666;
  }

  .manager-card {
    border-width: 3px;
  }

  .manager-card.selected {
    border-width: 4px;
  }
}
</style>
