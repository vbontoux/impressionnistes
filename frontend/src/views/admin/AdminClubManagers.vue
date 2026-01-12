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
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <!-- Error state -->
    <div v-if="error" class="error-message">
      {{ error }}
      <button @click="fetchClubManagers" class="btn-retry">{{ $t('common.retry') }}</button>
    </div>

    <!-- Empty state -->
    <div v-if="!loading && !error && managers.length === 0" class="empty-state">
      <p>{{ $t('admin.clubManagers.noManagers') }}</p>
    </div>

    <!-- No search results -->
    <div v-if="!loading && !error && managers.length > 0 && filteredManagers.length === 0" class="empty-state">
      <p>{{ $t('admin.clubManagers.noSearchResults') }}</p>
      <button @click="clearFilters" class="btn-secondary">{{ $t('admin.clubManagers.clearSearch') }}</button>
    </div>

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
          <button 
            @click="selectAll" 
            class="btn-secondary"
            :disabled="allSelected"
          >
            {{ $t('admin.clubManagers.selectAll') }}
          </button>
          <button 
            @click="deselectAll" 
            class="btn-secondary"
            :disabled="selectedIds.size === 0"
          >
            {{ $t('admin.clubManagers.deselectAll') }}
          </button>
          <button 
            @click="emailSelected" 
            class="btn-primary"
            :disabled="selectedIds.size === 0"
          >
            {{ $t('admin.clubManagers.emailSelected') }}
          </button>
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

export default {
  name: 'AdminClubManagers',
  components: {
    ListHeader,
    ListFilters
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
@import '@/assets/responsive.css';

.admin-club-managers {
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
}

/* Loading State */
.loading {
  text-align: center;
  padding: 3rem;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error State */
.error-message {
  padding: 1rem;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  color: #c33;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.btn-retry {
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  white-space: nowrap;
  transition: background-color 0.2s;
  min-height: 44px;
}

.btn-retry:hover {
  background-color: #0056b3;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
  font-size: 1.125rem;
}

.empty-state .btn-secondary {
  margin-top: 1rem;
}

/* Count */
.count {
  margin: 0 0 1rem 0;
  color: #6c757d;
  font-size: 0.875rem;
}

/* Table View */
.managers-table-container {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.managers-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

.managers-table thead {
  background-color: #f8f9fa;
}

.managers-table th {
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
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
  padding: 0.75rem;
  border-bottom: 1px solid #dee2e6;
}

.managers-table td.checkbox-col {
  width: 50px;
}

.managers-table tbody tr {
  transition: background-color 0.2s;
}

.managers-table tbody tr:hover {
  background-color: #f8f9fa;
}

.managers-table tbody tr.selected {
  background-color: #f0f8ff;
}

.managers-table input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #007bff;
}

.email-link {
  color: #007bff;
  text-decoration: none;
  transition: color 0.2s;
}

.email-link:hover {
  color: #0056b3;
  text-decoration: underline;
}

.email-link:focus {
  outline: 2px solid #007bff;
  outline-offset: 2px;
  border-radius: 2px;
}

.phone-link {
  color: #28a745;
  text-decoration: none;
  transition: color 0.2s;
  font-weight: 500;
}

.phone-link:hover {
  color: #1e7e34;
  text-decoration: underline;
}

.phone-link:focus {
  outline: 2px solid #28a745;
  outline-offset: 2px;
  border-radius: 2px;
}

.no-data {
  color: #999;
  font-style: italic;
}

.club-box {
  display: inline-block;
  max-width: 200px;
  padding: 0.25rem 0.5rem;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.75rem;
  line-height: 1.3;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.admin-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background-color: #667eea;
  color: white;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Card View */
.manager-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  padding: 1rem 0;
}

.manager-card {
  background-color: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s;
}

.manager-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.manager-card.selected {
  border-color: #007bff;
  background-color: #f0f8ff;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e0e0e0;
}

.card-checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
  flex-shrink: 0;
  accent-color: #007bff;
}

.card-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
  flex: 1;
}

.card-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f5f5f5;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row .label {
  font-weight: 500;
  color: #666;
  font-size: 0.875rem;
}

.detail-row .email-link,
.detail-row .club-box {
  color: #333;
}

/* Selection Actions */
.selection-actions {
  background-color: white;
  border-radius: 8px;
  padding: 1rem 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 1.5rem;
}

.selection-info {
  color: #495057;
  font-weight: 500;
  font-size: 0.875rem;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

/* Buttons */
.btn-primary,
.btn-secondary {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
  min-height: 44px;
  white-space: nowrap;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #545b62;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(108, 117, 125, 0.3);
}

.btn-secondary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled,
.btn-secondary:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

.btn-primary:focus,
.btn-secondary:focus,
.btn-retry:focus {
  outline: 2px solid #007bff;
  outline-offset: 2px;
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .admin-club-managers {
    padding: 0;
  }

  /* Hide table view on mobile - cards are better */
  .managers-table-container {
    padding: 0.75rem;
    border-radius: 8px;
    margin: 0 0.5rem;
  }

  .managers-table {
    font-size: 0.8125rem;
    min-width: 700px; /* Force horizontal scroll for table */
  }

  .managers-table th,
  .managers-table td {
    padding: 0.5rem 0.375rem;
  }

  .managers-table th {
    font-size: 0.75rem;
  }

  /* Optimize card view for mobile */
  .manager-cards {
    grid-template-columns: 1fr;
    gap: 1rem;
    padding: 0 0.5rem;
  }

  .manager-card {
    border-radius: 8px;
    padding: 1.25rem;
  }

  .card-header h3 {
    font-size: 1rem;
  }

  .card-checkbox {
    width: 24px;
    height: 24px;
  }

  .detail-row {
    padding: 0.625rem 0;
  }

  .detail-row .label {
    font-size: 0.8125rem;
    margin-bottom: 0.25rem;
  }

  .detail-row .email-link {
    word-break: break-all;
    font-size: 0.875rem;
  }

  .club-box {
    max-width: 100%;
    font-size: 0.8125rem;
  }

  /* Selection actions - stack vertically on mobile */
  .selection-actions {
    flex-direction: column;
    align-items: stretch;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0.5rem 0;
    gap: 0.75rem;
  }

  .selection-info {
    text-align: center;
    font-size: 0.9375rem;
  }

  .action-buttons {
    flex-direction: column;
    width: 100%;
    gap: 0.625rem;
  }

  .btn-primary,
  .btn-secondary,
  .btn-retry {
    width: 100%;
    padding: 0.75rem 1rem;
    font-size: 0.9375rem;
    min-height: 48px; /* Better touch target */
  }

  /* Empty states */
  .empty-state {
    padding: 2rem 1rem;
    font-size: 0.9375rem;
  }

  .empty-state .btn-secondary {
    width: 100%;
    max-width: 300px;
    margin-left: auto;
    margin-right: auto;
  }

  /* Error message */
  .error-message {
    flex-direction: column;
    align-items: stretch;
    margin: 0 0.5rem 1rem;
    padding: 1rem;
  }

  .error-message .btn-retry {
    width: 100%;
  }

  /* Count text */
  .count {
    padding: 0 0.5rem;
    font-size: 0.8125rem;
  }

  /* Loading spinner */
  .loading {
    padding: 2rem 1rem;
  }
}

/* Tablet Responsive */
@media (min-width: 768px) and (max-width: 1023px) {
  .manager-cards {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
  }

  .managers-table-container {
    padding: 1.25rem;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .manager-card,
  .btn-primary,
  .btn-secondary,
  .managers-table tbody tr,
  .email-link {
    transition: none;
  }

  .manager-card:hover {
    transform: none;
  }

  .btn-primary:hover:not(:disabled),
  .btn-secondary:hover:not(:disabled) {
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
