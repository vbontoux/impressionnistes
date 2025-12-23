<template>
  <div class="admin-boats">
    <div class="list-header">
      <div>
        <h1>{{ $t('admin.boats.title') }}</h1>
        <p class="subtitle">{{ $t('admin.boats.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <div class="view-toggle">
          <button 
            @click="viewMode = 'cards'" 
            :class="{ active: viewMode === 'cards' }"
            class="btn-view"
            :title="$t('common.cardView')"
          >
            ⊞
          </button>
          <button 
            @click="viewMode = 'table'" 
            :class="{ active: viewMode === 'table' }"
            class="btn-view"
            :title="$t('common.tableView')"
          >
            ☰
          </button>
        </div>
        <button @click="showCreateModal = true" class="btn-primary">
          {{ $t('admin.boats.addBoat') }}
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="search-box">
        <input
          v-model="searchTerm"
          type="text"
          :placeholder="$t('admin.boats.searchPlaceholder')"
          class="search-input"
        />
      </div>

      <div class="filter-row">
        <div class="filter-group">
          <label>{{ $t('admin.boats.filterByTeamManager') }}&nbsp;:</label>
          <select v-model="filterTeamManager" class="filter-select">
            <option value="">{{ $t('admin.boats.allTeamManagers') }}</option>
            <option v-for="tm in teamManagers" :key="tm.id" :value="tm.id">
              {{ tm.name }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>{{ $t('admin.boats.filterByClub') }}&nbsp;:</label>
          <input
            v-model="filterClub"
            type="text"
            :placeholder="$t('admin.boats.clubPlaceholder')"
            class="filter-input"
          />
        </div>

        <div class="filter-group">
          <label>{{ $t('admin.boats.filterByStatus') }}&nbsp;:</label>
          <select v-model="filterStatus" class="filter-select">
            <option value="">{{ $t('admin.boats.allStatuses') }}</option>
            <option value="incomplete">{{ $t('boat.status.incomplete') }}</option>
            <option value="complete">{{ $t('boat.status.complete') }}</option>
            <option value="paid">{{ $t('boat.status.paid') }}</option>
            <option value="forfait">{{ $t('admin.boats.forfait') }}</option>
          </select>
        </div>

        <button @click="clearFilters" class="filter-btn">
          {{ $t('admin.boats.clearFilters') }}
        </button>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <!-- Error state -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- Boats table/cards -->
    <div v-if="!loading && !error">
      <p class="count">{{ $t('admin.boats.totalCount', { count: filteredBoats.length }) }}</p>
      
      <!-- Card View -->
      <div v-if="viewMode === 'cards'" class="boat-cards">
        <div
          v-for="boat in paginatedBoats"
          :key="boat.boat_registration_id"
          class="boat-card"
          :class="`status-${getBoatStatus(boat)}`"
        >
          <div class="boat-header">
            <h3>{{ boat.event_type }} - {{ boat.boat_type }}</h3>
            <span class="status-badge" :class="`status-${getBoatStatus(boat)}`">
              {{ getBoatStatusLabel(boat) }}
            </span>
          </div>

          <div class="boat-details">
            <div class="detail-row">
              <span class="label">{{ $t('boat.firstRower') }}&nbsp;:</span>
              <span>{{ getFirstRowerName(boat) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('boat.filledSeats') }}&nbsp;:</span>
              <span>{{ getFilledSeatsCount(boat) }} / {{ boat.seats?.length || 0 }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('admin.boats.teamManager') }}&nbsp;:</span>
              <span>
                <div class="team-manager-info">
                  <div>{{ boat.team_manager_name }}</div>
                  <div class="email">{{ boat.team_manager_email }}</div>
                </div>
              </span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('admin.boats.club') }}&nbsp;:</span>
              <span class="club-box">{{ boat.team_manager_club }}</span>
            </div>
            <div v-if="boat.registration_status === 'paid' && boat.paid_at" class="detail-row">
              <span class="label">{{ $t('boat.paidOn') }}&nbsp;:</span>
              <span>{{ formatDate(boat.paid_at) }}</span>
            </div>
          </div>

          <div v-if="boat.race_name" class="race-name">
            <strong>{{ $t('boat.selectedRace') }}&nbsp;:</strong> {{ boat.race_name }}
          </div>

          <div class="boat-actions">
            <button 
              v-if="boat.registration_status === 'forfait'"
              @click="removeForfait(boat)" 
              class="btn-secondary"
            >
              {{ $t('admin.boats.removeForfait') }}
            </button>
            <button 
              v-else
              @click="setForfait(boat)" 
              class="btn-warning"
            >
              {{ $t('admin.boats.setForfait') }}
            </button>
            <button @click="deleteBoat(boat)" class="btn-danger">
              {{ $t('common.delete') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Table View -->
      <div v-else class="boats-table-container">
        <TableScrollIndicator aria-label="Boats table">
          <table class="boats-table">
            <thead>
              <tr>
                <th @click="sortBy('event_type')">
                  {{ $t('boat.eventType') }}
                  <span v-if="sortField === 'event_type'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
                </th>
                <th>{{ $t('boat.boatType') }}</th>
                <th>{{ $t('boat.firstRower') }}</th>
                <th>{{ $t('boat.status.label') }}</th>
                <th>{{ $t('boat.seats') }}</th>
                <th @click="sortBy('team_manager_name')">
                  {{ $t('admin.boats.teamManager') }}
                  <span v-if="sortField === 'team_manager_name'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
                </th>
                <th @click="sortBy('team_manager_club')">
                  {{ $t('admin.boats.club') }}
                  <span v-if="sortField === 'team_manager_club'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
                </th>
                <th>{{ $t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="boat in paginatedBoats" :key="boat.boat_registration_id" :class="getRowClass(boat)">
                <td>{{ boat.event_type }}</td>
                <td>{{ boat.boat_type }}</td>
                <td>{{ getFirstRowerLastName(boat) }}</td>
                <td>
                  <span class="status-badge" :class="`status-${getBoatStatus(boat)}`">
                    {{ getBoatStatusLabel(boat) }}
                  </span>
                </td>
                <td>
                  {{ getFilledSeatsCount(boat) }} / {{ boat.seats?.length || 0 }}
                  <span v-if="boat.is_multi_club_crew" class="multi-club-badge-small">{{ $t('boat.multiClub') }}</span>
                </td>
                <td>{{ boat.team_manager_name }}</td>
                <td>{{ boat.team_manager_club }}</td>
                <td class="actions-cell">
                  <button 
                    @click="toggleForfait(boat)" 
                    class="btn-table btn-forfait-table"
                    :class="{ active: boat.forfait }"
                    :title="boat.forfait ? $t('admin.boats.removeForfait') : $t('admin.boats.setForfait')"
                  >
                    {{ boat.forfait ? $t('admin.boats.removeForfait') : $t('admin.boats.setForfait') }}
                  </button>
                  <button 
                    @click="deleteBoat(boat)" 
                    class="btn-table btn-delete-table"
                    :disabled="boat.registration_status === 'paid'"
                    :title="boat.registration_status === 'paid' ? $t('boat.cannotDeletePaid') : ''"
                  >
                    {{ $t('common.delete') }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </TableScrollIndicator>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="pagination-btn"
        >
          {{ $t('common.previous') }}
        </button>
        <span class="page-info">
          {{ $t('common.pageInfo', { current: currentPage, total: totalPages }) }}
        </span>
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="pagination-btn"
        >
          {{ $t('common.next') }}
        </button>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ showEditModal ? $t('admin.boats.editBoat') : $t('admin.boats.addBoat') }}</h2>
          <button @click="closeModals" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <p class="info-text">{{ $t('admin.boats.modalInfo') }}</p>
          <!-- For now, just show a message - full form can be added later -->
          <p>{{ $t('admin.boats.useTeamManagerInterface') }}</p>
        </div>
        <div class="modal-footer">
          <button @click="closeModals" class="btn-secondary">{{ $t('common.cancel') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import apiClient from '../../services/apiClient'
import TableScrollIndicator from '../../components/TableScrollIndicator.vue'

export default {
  name: 'AdminBoats',
  components: {
    TableScrollIndicator
  },
  setup() {
    const router = useRouter()
    const { t } = useI18n()

    const boats = ref([])
    const loading = ref(false)
    const error = ref(null)
    
    const searchTerm = ref('')
    const filterTeamManager = ref('')
    const filterClub = ref('')
    const filterStatus = ref('')
    
    const sortField = ref('team_manager_name')
    const sortDirection = ref('asc')
    
    const currentPage = ref(1)
    const itemsPerPage = 50
    const viewMode = ref(localStorage.getItem('adminBoatsViewMode') || 'table')
    
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const editingBoat = ref(null)

    // Fetch all boats
    const fetchBoats = async () => {
      loading.value = true
      error.value = null
      
      try {
        const params = {}
        if (filterTeamManager.value) params.team_manager_id = filterTeamManager.value
        if (filterClub.value) params.club = filterClub.value
        if (filterStatus.value) params.status = filterStatus.value
        if (searchTerm.value) params.search = searchTerm.value
        
        const response = await apiClient.get('/admin/boats', { params })
        boats.value = response.data.data?.boats || []
      } catch (err) {
        console.error('Failed to fetch boats:', err)
        error.value = t('admin.boats.fetchError')
      } finally {
        loading.value = false
      }
    }

    // Computed: unique team managers for filter
    const teamManagers = computed(() => {
      const unique = new Map()
      boats.value.forEach(boat => {
        if (boat.team_manager_id && boat.team_manager_name) {
          unique.set(boat.team_manager_id, {
            id: boat.team_manager_id,
            name: boat.team_manager_name
          })
        }
      })
      return Array.from(unique.values()).sort((a, b) => a.name.localeCompare(b.name))
    })

    // Computed: filtered boats
    const filteredBoats = computed(() => {
      let result = boats.value

      // Apply search filter
      if (searchTerm.value) {
        const search = searchTerm.value.toLowerCase()
        result = result.filter(boat =>
          boat.event_type?.toLowerCase().includes(search) ||
          boat.boat_type?.toLowerCase().includes(search) ||
          boat.team_manager_name?.toLowerCase().includes(search) ||
          boat.team_manager_club?.toLowerCase().includes(search) ||
          boat.boat_registration_id?.toLowerCase().includes(search)
        )
      }

      // Apply team manager filter
      if (filterTeamManager.value) {
        result = result.filter(boat => boat.team_manager_id === filterTeamManager.value)
      }

      // Apply club filter
      if (filterClub.value && filterClub.value.trim()) {
        const club = filterClub.value.toLowerCase().trim()
        result = result.filter(boat => {
          const teamManagerClub = (boat.team_manager_club || '').toLowerCase().trim()
          return teamManagerClub.includes(club)
        })
      }

      // Apply status filter
      if (filterStatus.value) {
        if (filterStatus.value === 'forfait') {
          result = result.filter(boat => boat.forfait === true)
        } else {
          result = result.filter(boat => boat.registration_status === filterStatus.value)
        }
      }

      // Apply sorting
      result.sort((a, b) => {
        let aVal = a[sortField.value] || ''
        let bVal = b[sortField.value] || ''
        
        if (typeof aVal === 'string') aVal = aVal.toLowerCase()
        if (typeof bVal === 'string') bVal = bVal.toLowerCase()
        
        if (aVal < bVal) return sortDirection.value === 'asc' ? -1 : 1
        if (aVal > bVal) return sortDirection.value === 'asc' ? 1 : -1
        return 0
      })

      return result
    })

    // Computed: paginated boats
    const paginatedBoats = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      return filteredBoats.value.slice(start, end)
    })

    const totalPages = computed(() => {
      return Math.ceil(filteredBoats.value.length / itemsPerPage)
    })

    // Helper functions
    const getFilledSeatsCount = (boat) => {
      if (!boat.seats) return 0
      return boat.seats.filter(seat => seat.crew_member_id).length
    }

    const getFirstRowerLastName = (boat) => {
      if (!boat.seats || boat.seats.length === 0) return '-'
      const rowers = boat.seats.filter(seat => seat.type === 'rower')
      if (rowers.length === 0) return '-'
      const strokeSeat = rowers.reduce((max, seat) => seat.position > max.position ? seat : max, rowers[0])
      return strokeSeat?.crew_member_last_name || '-'
    }

    const getFirstRowerName = (boat) => {
      if (!boat.seats || boat.seats.length === 0) return '-'
      const rowers = boat.seats.filter(seat => seat.type === 'rower')
      if (rowers.length === 0) return '-'
      const strokeSeat = rowers.reduce((max, seat) => seat.position > max.position ? seat : max, rowers[0])
      return strokeSeat?.crew_member_first_name && strokeSeat?.crew_member_last_name 
        ? `${strokeSeat.crew_member_first_name} ${strokeSeat.crew_member_last_name}`
        : '-'
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      const day = String(date.getDate()).padStart(2, '0')
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const year = date.getFullYear()
      return `${day}/${month}/${year}`
    }

    const getBoatStatus = (boat) => {
      if (boat.forfait) return 'forfait'
      return boat.registration_status || 'incomplete'
    }

    const getBoatStatusLabel = (boat) => {
      if (boat.forfait) return t('admin.boats.forfait')
      return t(`boat.status.${boat.registration_status || 'incomplete'}`)
    }

    const getRowClass = (boat) => {
      if (boat.forfait) return 'row-forfait'
      return `row-status-${boat.registration_status || 'incomplete'}`
    }

    // Actions
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
      filterTeamManager.value = ''
      filterClub.value = ''
      filterStatus.value = ''
      currentPage.value = 1
    }

    const toggleForfait = async (boat) => {
      if (!confirm(t(boat.forfait ? 'admin.boats.confirmRemoveForfait' : 'admin.boats.confirmSetForfait'))) {
        return
      }

      try {
        await apiClient.put(`/admin/boats/${boat.team_manager_id}/${boat.boat_registration_id}`, {
          forfait: !boat.forfait
        })
        
        // Update local state
        boat.forfait = !boat.forfait
      } catch (err) {
        console.error('Failed to toggle forfait:', err)
        error.value = t('admin.boats.updateError')
      }
    }

    const setForfait = async (boat) => {
      if (!confirm(t('admin.boats.confirmSetForfait'))) {
        return
      }

      try {
        await apiClient.put(`/admin/boats/${boat.team_manager_id}/${boat.boat_registration_id}`, {
          forfait: true
        })
        
        // Update local state
        boat.forfait = true
        boat.registration_status = 'forfait'
      } catch (err) {
        console.error('Failed to set forfait:', err)
        error.value = t('admin.boats.updateError')
      }
    }

    const removeForfait = async (boat) => {
      if (!confirm(t('admin.boats.confirmRemoveForfait'))) {
        return
      }

      try {
        await apiClient.put(`/admin/boats/${boat.team_manager_id}/${boat.boat_registration_id}`, {
          forfait: false
        })
        
        // Update local state
        boat.forfait = false
        // Recalculate status based on seats
        const filledSeats = getFilledSeatsCount(boat)
        boat.registration_status = filledSeats === boat.seats?.length ? 'complete' : 'incomplete'
      } catch (err) {
        console.error('Failed to remove forfait:', err)
        error.value = t('admin.boats.updateError')
      }
    }

    const deleteBoat = async (boat) => {
      if (!confirm(t('admin.boats.confirmDelete', { boat: `${boat.event_type} ${boat.boat_type}` }))) {
        return
      }

      try {
        await apiClient.delete(`/admin/boats/${boat.team_manager_id}/${boat.boat_registration_id}`)
        
        // Remove from local state
        boats.value = boats.value.filter(b => b.boat_registration_id !== boat.boat_registration_id)
      } catch (err) {
        console.error('Failed to delete boat:', err)
        error.value = t('admin.boats.deleteError')
      }
    }

    const closeModals = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingBoat.value = null
    }

    onMounted(() => {
      fetchBoats()
    })

    // Watch for view mode changes and save to localStorage
    watch(viewMode, (newMode) => {
      localStorage.setItem('adminBoatsViewMode', newMode)
    })

    return {
      boats,
      loading,
      error,
      searchTerm,
      filterTeamManager,
      filterClub,
      filterStatus,
      sortField,
      sortDirection,
      currentPage,
      totalPages,
      viewMode,
      showCreateModal,
      showEditModal,
      teamManagers,
      filteredBoats,
      paginatedBoats,
      getFilledSeatsCount,
      getFirstRowerLastName,
      getFirstRowerName,
      getBoatStatus,
      getBoatStatusLabel,
      getRowClass,
      sortBy,
      clearFilters,
      toggleForfait,
      setForfait,
      removeForfait,
      deleteBoat,
      closeModals,
      formatDate
    }
  }
}
</script>

<style scoped>
@import '@/assets/responsive.css';

/* Override responsive.css breakpoints for this component */
.desktop-only {
  display: none;
}

@media (min-width: 768px) {
  .desktop-only {
    display: block;
  }
}

.mobile-only {
  display: block;
}

@media (min-width: 768px) {
  .mobile-only {
    display: none;
  }
}

.admin-boats {
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.list-header h1 {
  margin: 0 0 0.5rem 0;
  color: #212529;
}

.subtitle {
  color: #6c757d;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.view-toggle {
  display: flex;
  gap: 0.5rem;
  background: white;
  padding: 0.25rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-view {
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 1.25rem;
  border-radius: 6px;
  transition: all 0.2s;
  color: #6c757d;
}

.btn-view:hover {
  background: #f8f9fa;
  color: #495057;
}

.btn-view.active {
  background: #007bff;
  color: white;
}

.filters {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-box {
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 1rem;
}

.filter-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  min-width: 200px;
}

.filter-group label {
  font-weight: 500;
  color: #495057;
  font-size: 0.875rem;
}

.filter-select,
.filter-input {
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 0.875rem;
}

.filter-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  white-space: nowrap;
  transition: all 0.3s;
}

.filter-btn:hover {
  background: #f5f5f5;
}

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

.error-message {
  padding: 1rem;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  color: #c33;
  margin-bottom: 1rem;
}

.boats-table-container {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.count {
  margin: 0 0 1rem 0;
  color: #6c757d;
  font-size: 0.875rem;
}

.boats-table {
  width: 100%;
  border-collapse: collapse;
}

.boats-table thead {
  background-color: #f8f9fa;
}

.boats-table th {
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
  cursor: pointer;
  user-select: none;
}

.boats-table th:hover {
  background-color: #e9ecef;
}

.boats-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #dee2e6;
}

.boats-table tbody tr:hover {
  background-color: #f8f9fa;
}

.boats-table tbody tr.row-status-complete {
  border-left: 4px solid #28a745;
}

.boats-table tbody tr.row-status-paid {
  border-left: 4px solid #007bff;
}

.boats-table tbody tr.row-status-free {
  border-left: 4px solid #007bff;
}

.boats-table tbody tr.row-status-incomplete {
  border-left: 4px solid #ffc107;
}

.boats-table tbody tr.row-forfait {
  border-left: 4px solid #dc3545;
  background-color: #fff5f5;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
}

.status-badge.status-incomplete {
  background-color: #ffc107;
  color: #000;
}

.status-badge.status-complete {
  background-color: #28a745;
  color: white;
}

.status-badge.status-paid {
  background-color: #007bff;
  color: white;
}

.status-badge.status-free {
  background-color: #007bff;
  color: white;
}

.status-badge.status-forfait {
  background-color: #dc3545;
  color: white;
}

.multi-club-badge-small {
  display: inline-block;
  margin-left: 0.5rem;
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
  font-size: 0.65rem;
  font-weight: 500;
  background-color: #ffc107;
  color: #000;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
}

.btn-table {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.btn-view-table {
  background-color: #6c757d;
  color: white;
}

.btn-view-table:hover {
  background-color: #545b62;
}

.btn-edit-table {
  background-color: #6c757d;
  color: white;
}

.btn-edit-table:hover {
  background-color: #545b62;
}

.btn-forfait-table {
  background-color: #ffc107;
  color: #000;
}

.btn-forfait-table:hover {
  background-color: #e0a800;
}

.btn-forfait-table.active {
  background-color: #dc3545;
  color: white;
}

.btn-forfait-table.active:hover {
  background-color: #c82333;
}

.btn-delete-table {
  background-color: #dc3545;
  color: white;
}

.btn-delete-table:hover:not(:disabled) {
  background-color: #c82333;
}

.btn-delete-table:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.pagination-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.page-info {
  color: #6c757d;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary:hover {
  background-color: #0056b3;
}

/* Modal styles */
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
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #dee2e6;
  flex-shrink: 0;
}

.modal-header h2 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #6c757d;
  line-height: 1;
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.close-btn:hover {
  color: #212529;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.info-text {
  color: #6c757d;
  margin-bottom: 1rem;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #dee2e6;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  min-height: 44px;
}

.btn-secondary:hover {
  background-color: #545b62;
}

@media (max-width: 768px) {
  .modal-overlay {
    align-items: flex-end;
    padding: 0;
  }

  .modal-content {
    border-radius: 12px 12px 0 0;
    width: 100%;
    max-width: 100%;
    max-height: 90vh;
  }

  .modal-header {
    padding: 1rem;
  }

  .modal-body {
    padding: 1rem;
  }

  .modal-footer {
    padding: 1rem;
    flex-direction: column;
  }

  .modal-footer .btn-secondary {
    width: 100%;
  }
}

/* Card View Styles */
.boat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  padding: 1rem 0;
}

.boat-card {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s;
}

.boat-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.boat-card.status-paid {
  border-left: 4px solid #007bff;
}

.boat-card.status-complete {
  border-left: 4px solid #28a745;
}

.boat-card.status-incomplete {
  border-left: 4px solid #ffc107;
}

.boat-card.status-forfait {
  border-left: 4px solid #dc3545;
  background-color: #fff5f5;
}

.boat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
  gap: 1rem;
}

.boat-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.1rem;
  flex: 1;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
}

.status-badge.status-incomplete {
  background-color: #ffc107;
  color: #000;
}

.status-badge.status-complete {
  background-color: #28a745;
  color: white;
}

.status-badge.status-paid {
  background-color: #007bff;
  color: white;
}

.status-badge.status-forfait {
  background-color: #dc3545;
  color: white;
}

.boat-details {
  margin-bottom: 1rem;
}

.boat-details .detail-row {
  display: flex;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f5f5f5;
  align-items: flex-start;
}

.boat-details .detail-row:last-child {
  border-bottom: none;
}

.boat-details .label {
  font-weight: 500;
  color: #666;
  min-width: 100px;
  max-width: 100px;
  flex-shrink: 0;
  word-wrap: break-word;
  line-height: 1.4;
}

.boat-details .detail-row span:not(.label) {
  color: #333;
  flex: 1;
}

.team-manager-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.team-manager-info .email {
  font-size: 0.85rem;
  color: #6c757d;
  word-break: break-all;
  overflow-wrap: break-word;
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

.race-name {
  background-color: #f8f9fa;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.boat-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.boat-actions .btn-secondary,
.boat-actions .btn-warning,
.boat-actions .btn-danger {
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
}

.btn-warning {
  background-color: #ff9800;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-warning:hover {
  background-color: #f57c00;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-danger:hover:not(:disabled) {
  background-color: #c82333;
}

.btn-danger:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}
</style>

@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
  }

  .filter-group {
    min-width: 100%;
  }

  .boats-table-container {
    overflow-x: auto;
  }

  .actions-cell {
    flex-direction: column;
  }

  .filter-select,
  .filter-input {
    font-size: 16px;
    min-height: 44px;
  }

  .filter-btn {
    min-height: 44px;
  }

  .btn-table {
    min-height: 44px;
    min-width: 44px;
  }
}

/* Mobile card styles */
.card-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.boat-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #dee2e6;
}

.boat-card.row-status-complete {
  border-left-color: #28a745;
}

.boat-card.row-status-paid {
  border-left-color: #007bff;
}

.boat-card.row-status-free {
  border-left-color: #007bff;
}

.boat-card.row-status-incomplete {
  border-left-color: #ffc107;
}

.boat-card.row-forfait {
  border-left-color: #dc3545;
  background-color: #fff5f5;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e0e0e0;
  gap: 0.5rem;
}

.card-title {
  font-size: 1rem;
  color: #212529;
  flex: 1;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0.5rem 0;
  gap: 1rem;
}

.card-label {
  font-weight: 600;
  color: #6c757d;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.card-value {
  color: #212529;
  font-size: 0.875rem;
  text-align: right;
  word-break: break-word;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.btn-card {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
  min-height: 44px;
}

.btn-forfait-card {
  background-color: #ffc107;
  color: #000;
}

.btn-forfait-card:hover {
  background-color: #e0a800;
}

.btn-forfait-card.active {
  background-color: #dc3545;
  color: white;
}

.btn-forfait-card.active:hover {
  background-color: #c82333;
}

.btn-delete-card {
  background-color: #dc3545;
  color: white;
}

.btn-delete-card:hover:not(:disabled) {
  background-color: #c82333;
}

.btn-delete-card:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Mobile responsive styles */
@media (max-width: 768px) {
  .admin-boats {
    padding: 0;
  }

  .list-header {
    flex-direction: column;
    align-items: stretch;
    margin-bottom: 1rem;
  }

  .list-header .btn-primary {
    width: 100%;
  }

  .filters {
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .search-input {
    font-size: 16px;
    min-height: 44px;
  }

  .filter-row {
    flex-direction: column;
    gap: 0.75rem;
  }

  .filter-group {
    min-width: 100%;
  }

  .filter-select,
  .filter-input {
    font-size: 16px;
    min-height: 44px;
  }

  .filter-btn {
    width: 100%;
    min-height: 44px;
  }

  .boats-table-container {
    padding: 1rem;
  }

  .boats-table {
    min-width: 900px;
  }

  .boats-table th,
  .boats-table td {
    white-space: nowrap;
  }

  .actions-cell {
    flex-wrap: nowrap;
  }

  .btn-table {
    min-height: 44px;
    min-width: 44px;
    padding: 0.5rem;
    font-size: 0.75rem;
  }

  .pagination {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .pagination-btn {
    flex: 1;
    min-width: 100px;
    min-height: 44px;
  }

  .page-info {
    width: 100%;
    text-align: center;
  }
}

@media (min-width: 768px) {
  .boats-table {
    min-width: auto;
  }

  .boats-table td,
  .boats-table th {
    white-space: normal;
  }
}
