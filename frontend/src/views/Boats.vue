<template>
  <div class="boats-view">
    <div class="header">
      <h1>{{ $t('nav.boats') }}</h1>
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
        <button @click="showCreateForm = true" class="btn-primary">
          {{ $t('boat.addNew') }}
        </button>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="$t('boat.searchPlaceholder')"
          class="search-input"
        />
      </div>
      
      <div class="filter-row">
        <div class="filter-group">
          <label>{{ $t('boat.status.label') }}&nbsp;:</label>
          <select v-model="statusFilter" class="filter-select">
            <option value="all">{{ $t('boat.filter.all') }}</option>
            <option value="incomplete">{{ $t('boat.status.incomplete') }}</option>
            <option value="complete">{{ $t('boat.status.complete') }}</option>
            <option value="paid">{{ $t('boat.status.paid') }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Create Form Modal -->
    <div v-if="showCreateForm" class="modal-overlay" @click.self="showCreateForm = false">
      <div class="modal-content">
        <BoatRegistrationForm
          @created="handleBoatCreated"
          @cancel="showCreateForm = false"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="boatStore.loading && boatRegistrations.length === 0" class="loading">
      <div class="spinner"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="boatStore.error" class="error-message">
      {{ boatStore.error }}
    </div>

    <!-- Boat Registrations List -->
    <div v-else-if="boatRegistrations.length > 0 || !boatStore.loading" class="boats-list">
      <div v-if="boatRegistrations.length === 0 && !boatStore.loading" class="empty-state">
        <p>{{ $t('boat.noBoats') }}</p>
      </div>

      <!-- Card View -->
      <div v-else-if="viewMode === 'cards'" class="boat-cards">
        <div
          v-for="boat in boatRegistrations"
          :key="boat.boat_registration_id"
          class="boat-card"
          :class="`status-${boat.registration_status}`"
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
              <span>{{ getFirstRowerLastName(boat) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('boat.gender') }}&nbsp;:</span>
              <span>{{ getCrewGenderCategory(boat) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('boat.averageAge') }}&nbsp;:</span>
              <span>{{ getCrewAverageAge(boat) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('boat.filledSeats') }}&nbsp;:</span>
              <span>
                <span v-if="boat.is_multi_club_crew || boat.registration_status === 'free'" class="multi-club-badge">{{ $t('boat.multiClub') }}</span>
                {{ getFilledSeatsCount(boat) }} / {{ boat.seats?.length || 0 }}
              </span>
            </div>
            <div v-if="boat.registration_status === 'paid' && boat.paid_at" class="detail-row">
              <span class="label">{{ $t('boat.paidOn') }}&nbsp;:</span>
              <span>{{ formatDate(boat.paid_at) }}</span>
            </div>
          </div>

          <div v-if="getRaceName(boat)" class="race-name">
            <strong>{{ $t('boat.selectedRace') }}&nbsp;:</strong> {{ getRaceName(boat) }}
          </div>

          <div class="boat-actions">
            <button @click="viewBoat(boat)" class="btn-secondary">
              {{ $t('common.view') }}
            </button>
            <button 
              @click="deleteBoat(boat)" 
              class="btn-danger"
              :disabled="boat.registration_status === 'paid'"
              :title="boat.registration_status === 'paid' ? $t('boat.cannotDeletePaid') : ''"
            >
              {{ $t('common.delete') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Table View -->
      <div v-else class="boat-table-container">
        <table class="boat-table">
          <thead>
            <tr>
              <th>{{ $t('boat.eventType') }}</th>
              <th>{{ $t('boat.boatType') }}</th>
              <th>{{ $t('boat.firstRower') }}</th>
              <th>{{ $t('boat.gender') }}</th>
              <th>{{ $t('boat.averageAge') }}</th>
              <th>{{ $t('boat.status.label') }}</th>
              <th>{{ $t('boat.seats') }}</th>
              <th>{{ $t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="boat in boatRegistrations" :key="boat.boat_registration_id">
              <tr 
                :class="getRowClass(boat)"
              >
                <td>{{ boat.event_type }}</td>
                <td>{{ boat.boat_type }}</td>
                <td>{{ getFirstRowerLastName(boat) }}</td>
                <td>{{ getCrewGenderCategory(boat) }}</td>
                <td>{{ getCrewAverageAge(boat) }}</td>
                <td>
                  <span class="status-badge" :class="`status-${getBoatStatus(boat)}`">
                    {{ getBoatStatusLabel(boat) }}
                  </span>
                </td>
                <td>
                  {{ getFilledSeatsCount(boat) }} / {{ boat.seats?.length || 0 }}
                  <span v-if="boat.is_multi_club_crew || boat.registration_status === 'free'" class="multi-club-badge-small">{{ $t('boat.multiClub') }}</span>
                </td>
                <td class="actions-cell">
                  <button @click="viewBoat(boat)" class="btn-table btn-view-table">
                    {{ $t('common.view') }}
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
              <tr v-if="getRaceName(boat)" class="race-row" :class="`row-status-${boat.registration_status}`">
                <td colspan="8" class="race-cell">
                  <span class="race-label">{{ $t('boat.selectedRace') }}&nbsp;:</span> {{ getRaceName(boat) }}
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useBoatStore } from '../stores/boatStore'
import { useRaceStore } from '../stores/raceStore'
import { useI18n } from 'vue-i18n'
import BoatRegistrationForm from '../components/BoatRegistrationForm.vue'

export default {
  name: 'BoatsView',
  components: {
    BoatRegistrationForm
  },
  setup() {
    const router = useRouter()
    const boatStore = useBoatStore()
    const raceStore = useRaceStore()
    const { t } = useI18n()

    const showCreateForm = ref(false)
    // Load view mode from localStorage or default to 'cards'
    const viewMode = ref(localStorage.getItem('boatsViewMode') || 'cards')
    const statusFilter = ref('all')
    const searchQuery = ref('')

    // Watch for view mode changes and save to localStorage
    watch(viewMode, (newMode) => {
      localStorage.setItem('boatsViewMode', newMode)
    })

    const boatRegistrations = computed(() => {
      let boats = boatStore.boatRegistrations
      
      // Apply status filter
      if (statusFilter.value !== 'all') {
        boats = boats.filter(boat => boat.registration_status === statusFilter.value)
      }

      // Apply search query
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        boats = boats.filter(boat => {
          const firstRower = getFirstRowerLastName(boat).toLowerCase()
          const eventType = boat.event_type?.toLowerCase() || ''
          const boatType = boat.boat_type?.toLowerCase() || ''
          const raceName = getRaceName(boat)?.toLowerCase() || ''
          
          return firstRower.includes(query) ||
                 eventType.includes(query) ||
                 boatType.includes(query) ||
                 raceName.includes(query)
        })
      }

      return boats
    })

    const getFilledSeatsCount = (boat) => {
      if (!boat.seats) return 0
      return boat.seats.filter(seat => seat.crew_member_id).length
    }

    const getFirstRowerLastName = (boat) => {
      if (!boat.seats || boat.seats.length === 0) return '-'
      // Find stroke seat (highest position number that is a rower)
      const rowers = boat.seats.filter(seat => seat.type === 'rower')
      if (rowers.length === 0) return '-'
      const strokeSeat = rowers.reduce((max, seat) => seat.position > max.position ? seat : max, rowers[0])
      return strokeSeat?.crew_member_last_name || '-'
    }

    const getBoatStatus = (boat) => {
      if (boat.forfait) return 'forfait'
      return boat.registration_status || 'incomplete'
    }

    const getBoatStatusLabel = (boat) => {
      if (boat.forfait) return t('boat.status.forfait')
      return t(`boat.status.${boat.registration_status || 'incomplete'}`)
    }

    const getRowClass = (boat) => {
      if (boat.forfait) return 'row-forfait'
      return `row-status-${boat.registration_status || 'incomplete'}`
    }

    const getCrewGenderCategory = (boat) => {
      if (!boat.crew_composition) return '-'
      const gender = boat.crew_composition.gender_category
      if (gender === 'men') return t('boat.men')
      if (gender === 'women') return t('boat.women')
      if (gender === 'mixed') return t('boat.mixed')
      return '-'
    }

    const getCrewAverageAge = (boat) => {
      if (!boat.crew_composition || !boat.crew_composition.avg_age) return '-'
      return Math.round(boat.crew_composition.avg_age)
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleDateString(undefined, { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      })
    }

    const getRaceName = (boat) => {
      if (!boat.race_id) return null
      const race = raceStore.races.find(r => r.race_id === boat.race_id)
      if (!race || !race.name) return null
      
      // Try to get translation, fallback to original name if not found
      const translationKey = `races.${race.name}`
      const translated = t(translationKey)
      // If translation key is returned as-is, it means no translation exists
      return translated === translationKey ? race.name : translated
    }

    const handleBoatCreated = (newBoat) => {
      showCreateForm.value = false
      // Navigate to boat detail page
      router.push(`/boats/${newBoat.boat_registration_id}`)
    }

    const viewBoat = (boat) => {
      router.push(`/boats/${boat.boat_registration_id}`)
    }

    const deleteBoat = async (boat) => {
      if (confirm(t('boat.confirmDelete', { name: `${boat.event_type} ${boat.boat_type}` }))) {
        try {
          await boatStore.deleteBoatRegistration(boat.boat_registration_id)
        } catch (error) {
          console.error('Failed to delete boat:', error)
        }
      }
    }

    onMounted(async () => {
      // Load races if not already loaded
      if (raceStore.races.length === 0) {
        await raceStore.fetchRaces()
      }
      await boatStore.fetchBoatRegistrations()
    })

    return {
      boatStore,
      showCreateForm,
      viewMode,
      statusFilter,
      searchQuery,
      boatRegistrations,
      getFilledSeatsCount,
      getFirstRowerLastName,
      getBoatStatus,
      getBoatStatusLabel,
      getRowClass,
      getCrewGenderCategory,
      getCrewAverageAge,
      formatDate,
      getRaceName,
      handleBoatCreated,
      viewBoat,
      deleteBoat
    }
  }
}
</script>

<style scoped>
/* Mobile-first base styles */
.boats-view {
  padding: 0;
  max-width: 1200px;
  margin: 0 auto;
}

.loading {
  text-align: center;
  padding: 2rem 1rem;
  color: #666;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4CAF50;
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

.header {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
}

.filters {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.search-box {
  margin-bottom: 0.75rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  min-height: 44px;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.filter-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  white-space: nowrap;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  min-width: 120px;
  min-height: 44px;
}

.filter-select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.view-toggle {
  display: flex;
  gap: 0.25rem;
  background-color: #e9ecef;
  border-radius: 4px;
  padding: 0.25rem;
  width: 100%;
}

.btn-view {
  flex: 1;
  padding: 0.75rem;
  min-height: 44px;
  background-color: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  border-radius: 4px;
  transition: background-color 0.2s;
  touch-action: manipulation;
}

.btn-view:active {
  background-color: #dee2e6;
}

.btn-view.active {
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  width: 100%;
  padding: 0.875rem 1rem;
  min-height: 44px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: background-color 0.2s;
  touch-action: manipulation;
}

.btn-primary:active {
  background-color: #0056b3;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
  padding: 0;
}

.modal-content {
  background-color: white;
  border-radius: 12px 12px 0 0;
  width: 100%;
  max-width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.error-message {
  padding: 1rem;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  color: #c33;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.empty-state {
  text-align: center;
  padding: 2rem 1rem;
}

.empty-state p {
  color: #666;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.boat-cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.boat-card {
  background-color: white;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  transition: box-shadow 0.2s;
}

.boat-card.status-complete {
  border-color: #28a745;
}

.boat-card.status-free {
  border-color: #007bff;
  background: linear-gradient(to bottom, #f0f7ff 0%, white 100%);
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.15);
}

.boat-card.status-paid {
  border-color: #007bff;
  background: linear-gradient(to bottom, #f0f7ff 0%, white 100%);
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.15);
}

.boat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 0.5rem;
}

.boat-header h3 {
  margin: 0;
  color: #212529;
  font-size: 1rem;
  word-break: break-word;
  flex: 1;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}

.status-badge.status-incomplete {
  background-color: #ffc107;
  color: #000;
}

.status-badge.status-complete {
  background-color: #28a745;
  color: white;
}

.status-badge.status-free {
  background-color: #007bff;
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

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 0.875rem;
  gap: 0.5rem;
}

.detail-row .label {
  font-weight: 500;
  color: #666;
  flex-shrink: 0;
}

.detail-row span:last-child {
  text-align: right;
  word-break: break-word;
}

.rental-badge,
.multi-club-badge {
  display: inline-block;
  margin-left: 0.5rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.multi-club-badge-small {
  display: inline-block;
  margin-left: 0.5rem;
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
  font-size: 0.65rem;
  font-weight: 500;
}

.rental-badge {
  background-color: #17a2b8;
  color: white;
}

.multi-club-badge {
  background-color: #ffc107;
  color: #000;
}

.multi-club-badge-small {
  background-color: #ffc107;
  color: #000;
}

.race-name {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  font-size: 0.875rem;
  line-height: 1.4;
  color: #495057;
  word-break: break-word;
}

.race-name strong {
  color: #212529;
}

.boat-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}

.btn-secondary,
.btn-danger {
  width: 100%;
  min-height: 44px;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
  touch-action: manipulation;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:active {
  background-color: #545b62;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:active:not(:disabled) {
  background-color: #c82333;
}

.btn-danger:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Table View Styles */
.boat-table-container {
  background-color: white;
  border-radius: 0;
  overflow-x: auto;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin: 0 -1rem;
  -webkit-overflow-scrolling: touch;
}

.boat-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 900px;
}

.boat-table thead {
  background-color: #f8f9fa;
}

.boat-table th {
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
  font-size: 0.875rem;
}

.boat-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #dee2e6;
  font-size: 0.875rem;
}

.boat-table tbody tr.row-status-complete {
  border-left: 4px solid #28a745;
}

.boat-table tbody tr.row-status-free {
  border-left: 4px solid #007bff;
}

.boat-table tbody tr.row-status-paid {
  border-left: 4px solid #007bff;
}

.boat-table tbody tr.row-status-incomplete {
  border-left: 4px solid #ffc107;
}

.boat-table tbody tr.row-forfait {
  border-left: 4px solid #dc3545;
  background-color: #fff5f5;
}

.boat-table .race-row {
  background-color: #f8f9fa;
  border-left-width: 4px;
}

.boat-table .race-cell {
  padding: 0.5rem 0.75rem;
  font-size: 0.8125rem;
  font-style: italic;
  color: #495057;
}

.boat-table .race-label {
  font-weight: 600;
  font-style: normal;
  color: #212529;
}

.actions-cell {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.btn-table {
  width: 100%;
  padding: 0.5rem 0.75rem;
  min-height: 36px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8125rem;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.btn-view-table {
  background-color: #6c757d;
  color: white;
}

.btn-view-table:active {
  background-color: #545b62;
}

.btn-delete-table {
  background-color: #dc3545;
  color: white;
}

.btn-delete-table:active:not(:disabled) {
  background-color: #c82333;
}

.btn-delete-table:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .header-actions {
    flex-direction: column;
    gap: 0.75rem;
    width: 100%;
  }

  .filters {
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 0;
  }

  .search-input {
    font-size: 16px; /* Prevents iOS zoom */
  }

  .filter-row {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }

  .filter-group {
    width: 100%;
  }

  .filter-select {
    width: 100%;
    font-size: 16px; /* Prevents iOS zoom */
  }
}

/* Tablet and larger screens */
@media (min-width: 768px) {
  .header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .header h1 {
    font-size: 2rem;
  }

  .header-actions {
    gap: 1rem;
    width: auto;
  }

  .filter-group {
    width: auto;
  }

  .view-toggle {
    width: auto;
  }

  .btn-view {
    flex: 0;
    padding: 0.5rem 0.75rem;
  }

  .btn-view:hover {
    background-color: #dee2e6;
  }

  .btn-primary {
    width: auto;
    padding: 0.5rem 1rem;
  }

  .btn-primary:hover {
    background-color: #0056b3;
  }

  .modal-overlay {
    align-items: center;
    padding: 1rem;
  }

  .modal-content {
    border-radius: 8px;
    width: 90%;
    max-width: 600px;
  }

  .loading {
    padding: 3rem;
  }

  .empty-state {
    padding: 3rem;
  }

  .boat-cards {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
  }

  .boat-card {
    padding: 1.5rem;
  }

  .boat-card:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .boat-header h3 {
    font-size: 1.125rem;
  }

  .boat-actions {
    flex-direction: row;
    gap: 0.5rem;
  }

  .btn-secondary,
  .btn-danger {
    width: auto;
    flex: 1;
    padding: 0.5rem 1rem;
  }

  .btn-secondary:hover {
    background-color: #545b62;
  }

  .btn-danger:hover:not(:disabled) {
    background-color: #c82333;
  }

  .boat-table-container {
    border-radius: 8px;
    margin: 0;
  }

  .boat-table th {
    padding: 1rem;
    font-size: 0.95rem;
  }

  .boat-table td {
    padding: 1rem;
    font-size: 0.95rem;
  }

  .boat-table tbody tr:hover {
    background-color: #f8f9fa;
  }

  .boat-table .race-cell {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
  }

  .actions-cell {
    flex-direction: row;
  }

  .btn-table {
    width: auto;
    padding: 0.4rem 0.8rem;
  }

  .btn-view-table:hover {
    background-color: #545b62;
  }

  .btn-delete-table:hover:not(:disabled) {
    background-color: #c82333;
  }
}
</style>
