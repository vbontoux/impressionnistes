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
      {{ $t('common.loading') }}
    </div>

    <!-- Error State -->
    <div v-if="boatStore.error" class="error-message">
      {{ boatStore.error }}
    </div>

    <!-- Boat Registrations List -->
    <div v-if="!boatStore.loading || boatRegistrations.length > 0" class="boats-list">
      <div v-if="boatRegistrations.length === 0" class="empty-state">
        <p>{{ $t('boat.noBoats') }}</p>
        <button @click="showCreateForm = true" class="btn-primary">
          {{ $t('boat.createFirst') }}
        </button>
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
            <span class="status-badge" :class="`status-${boat.registration_status}`">
              {{ $t(`boat.status.${boat.registration_status}`) }}
            </span>
          </div>

          <div class="boat-details">
            <div class="detail-row">
              <span class="label">{{ $t('boat.firstRower') }}:</span>
              <span>{{ getFirstRowerLastName(boat) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('boat.gender') }}:</span>
              <span>{{ getCrewGenderCategory(boat) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('boat.averageAge') }}:</span>
              <span>{{ getCrewAverageAge(boat) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('boat.filledSeats') }}:</span>
              <span>{{ getFilledSeatsCount(boat) }} / {{ boat.seats?.length || 0 }}</span>
            </div>
            <div v-if="boat.is_multi_club_crew" class="detail-row">
              <span class="multi-club-badge">{{ $t('boat.multiClub') }}</span>
            </div>
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
            <tr 
              v-for="boat in boatRegistrations" 
              :key="boat.boat_registration_id"
              :class="`row-status-${boat.registration_status}`"
            >
              <td>{{ boat.event_type }}</td>
              <td>{{ boat.boat_type }}</td>
              <td>{{ getFirstRowerLastName(boat) }}</td>
              <td>{{ getCrewGenderCategory(boat) }}</td>
              <td>{{ getCrewAverageAge(boat) }}</td>
              <td>
                <span class="status-badge" :class="`status-${boat.registration_status}`">
                  {{ $t(`boat.status.${boat.registration_status}`) }}
                </span>
              </td>
              <td>
                {{ getFilledSeatsCount(boat) }} / {{ boat.seats?.length || 0 }}
                <span v-if="boat.is_multi_club_crew" class="multi-club-badge-small">{{ $t('boat.multiClub') }}</span>
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
    const { t } = useI18n()

    const showCreateForm = ref(false)
    // Load view mode from localStorage or default to 'cards'
    const viewMode = ref(localStorage.getItem('boatsViewMode') || 'cards')

    // Watch for view mode changes and save to localStorage
    watch(viewMode, (newMode) => {
      localStorage.setItem('boatsViewMode', newMode)
    })

    const boatRegistrations = computed(() => boatStore.boatRegistrations)

    const getFilledSeatsCount = (boat) => {
      if (!boat.seats) return 0
      return boat.seats.filter(seat => seat.crew_member_id).length
    }

    const getFirstRowerLastName = (boat) => {
      if (!boat.seats || boat.seats.length === 0) return '-'
      // Find first rower (position 1, type 'rower')
      const firstRower = boat.seats.find(seat => seat.position === 1 && seat.type === 'rower')
      return firstRower?.crew_member_last_name || '-'
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

    onMounted(() => {
      boatStore.fetchBoatRegistrations()
    })

    return {
      boatStore,
      showCreateForm,
      viewMode,
      boatRegistrations,
      getFilledSeatsCount,
      getFirstRowerLastName,
      getCrewGenderCategory,
      getCrewAverageAge,
      handleBoatCreated,
      viewBoat,
      deleteBoat
    }
  }
}
</script>

<style scoped>
.boats-view {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header h1 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.view-toggle {
  display: flex;
  gap: 0.25rem;
  background-color: #e9ecef;
  border-radius: 4px;
  padding: 0.25rem;
}

.btn-view {
  padding: 0.5rem 0.75rem;
  background-color: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.btn-view:hover {
  background-color: #dee2e6;
}

.btn-view.active {
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

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
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.error-message {
  padding: 1rem;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  color: #c33;
  margin-bottom: 1rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
}

.empty-state p {
  color: #666;
  margin-bottom: 1.5rem;
}

.boat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.boat-card {
  background-color: white;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  padding: 1.5rem;
  transition: box-shadow 0.2s;
}

.boat-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.boat-card.status-complete {
  border-color: #28a745;
}

.boat-card.status-paid {
  border-color: #007bff;
}

.boat-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 1rem;
}

.boat-header h3 {
  margin: 0;
  color: #212529;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
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

.boat-details {
  margin-bottom: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row .label {
  font-weight: 500;
  color: #666;
}

.rental-badge,
.multi-club-badge {
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

.boat-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.btn-primary,
.btn-secondary,
.btn-danger {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  flex: 1;
}

.btn-secondary:hover {
  background-color: #545b62;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
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
  border-radius: 8px;
  overflow-x: auto;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
}

.boat-table td {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.boat-table tbody tr:hover {
  background-color: #f8f9fa;
}

.boat-table tbody tr.row-status-complete {
  border-left: 4px solid #28a745;
}

.boat-table tbody tr.row-status-paid {
  border-left: 4px solid #007bff;
}

.boat-table tbody tr.row-status-incomplete {
  border-left: 4px solid #ffc107;
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

.btn-delete-table {
  background-color: #dc3545;
  color: white;
}

.btn-delete-table:hover {
  background-color: #c82333;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    justify-content: space-between;
  }

  .boat-table-container {
    margin: 0 -1rem;
    border-radius: 0;
  }
}
</style>
