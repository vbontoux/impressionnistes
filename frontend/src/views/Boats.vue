<template>
  <div class="boats-view">
    <ListHeader
      :title="$t('nav.boats')"
      :subtitle="$t('boat.subtitle')"
      v-model:viewMode="viewMode"
    >
      <template #action>
        <BaseButton 
          variant="primary"
          :disabled="!canCreateBoatRegistration"
          :title="createBoatRegistrationTooltip"
          @click="showCreateForm = true"
        >
          {{ $t('boat.addNew') }}
        </BaseButton>
      </template>
    </ListHeader>

    <ListFilters
      v-model:searchQuery="searchQuery"
      :searchPlaceholder="$t('boat.searchPlaceholder')"
      @clear="clearFilters"
    >
      <template #filters>
        <div class="filter-group">
          <label>{{ $t('boat.status.label') }}&nbsp;:</label>
          <select v-model="statusFilter" class="filter-select">
            <option value="all">{{ $t('boat.filter.all') }}</option>
            <option value="incomplete">{{ $t('boat.status.incomplete') }}</option>
            <option value="complete">{{ $t('boat.status.complete') }}</option>
            <option value="paid">{{ $t('boat.status.paid') }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>{{ $t('admin.boats.filterByRace') }}&nbsp;:</label>
          <select v-model="raceFilter" class="filter-select">
            <option value="all">{{ $t('admin.boats.allRaces') }}</option>
            <option v-for="race in availableRaces" :key="race.race_id" :value="race.race_id">
              {{ formatRaceName(race, $t) }}
            </option>
          </select>
        </div>
        <div class="filter-group">
          <label>{{ $t('boat.filter.boatRequest') }}&nbsp;:</label>
          <select v-model="boatRequestFilter" class="filter-select">
            <option value="all">{{ $t('boat.filter.allRequests') }}</option>
            <option value="with">{{ $t('boat.filter.withRequest') }}</option>
            <option value="without">{{ $t('boat.filter.withoutRequest') }}</option>
            <option value="pending">{{ $t('boat.filter.requestPending') }}</option>
            <option value="fulfilled">{{ $t('boat.filter.requestFulfilled') }}</option>
          </select>
        </div>
      </template>
    </ListFilters>

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
    <LoadingSpinner 
      v-if="boatStore.loading && boatRegistrations.length === 0"
      :message="$t('common.loading')"
    />

    <!-- Error State -->
    <div v-else-if="boatStore.error" class="error-message">
      {{ boatStore.error }}
    </div>

    <!-- Boat Registrations List -->
    <div v-else-if="boatRegistrations.length > 0 || !boatStore.loading" class="boats-list">
      <EmptyState 
        v-if="boatRegistrations.length === 0 && !boatStore.loading"
        :message="$t('boat.noBoats')"
      />

      <!-- Card View -->
      <div v-else-if="viewMode === 'cards'" class="boat-cards">
        <div
          v-for="boat in displayBoats"
          :key="boat.boat_registration_id"
          class="boat-card"
          :class="`status-${boat.registration_status}`"
        >
          <div class="boat-header">
            <h3>{{ boat.event_type }} - {{ boat.boat_type }}</h3>
            <StatusBadge :status="getBoatStatus(boat)" size="medium" />
          </div>

          <div class="boat-details">
            <div class="detail-row">
              <span class="label">{{ $t('boat.boatNumber') }}&nbsp;:</span>
              <span v-if="boat.boat_number" class="boat-number-text">{{ boat.boat_number }}</span>
              <span v-else class="no-race-text">{{ $t('boat.noRaceAssigned') }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('boat.selectedRace') }}&nbsp;:</span>
              <span v-if="getRaceName(boat)" class="race-name-cell">{{ getRaceName(boat) }}</span>
              <span v-else class="no-race-text">-</span>
            </div>
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
              <span class="label">{{ $t('admin.boats.club') }}&nbsp;:</span>
              <span class="club-display">
                <span class="club-box">{{ boat.boat_club_display }}</span>
              </span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('boat.filledSeats') }}&nbsp;:</span>
              <span>
                {{ getFilledSeatsCount(boat) }} / {{ boat.seats?.length || 0 }}
              </span>
            </div>
            <div v-if="boat.registration_status === 'paid' && boat.paid_at" class="detail-row">
              <span class="label">{{ $t('boat.paidOn') }}&nbsp;:</span>
              <span>{{ formatDate(boat.paid_at) }}</span>
            </div>
            
            <!-- Boat Request Status -->
            <div v-if="boat.boat_request_enabled" class="boat-request-section">
              <!-- Pending: Show team manager's request -->
              <div v-if="!boat.assigned_boat_identifier" class="boat-request-pending">
                <div class="request-header">
                  <strong>{{ $t('boat.boatRequest.status') }}&nbsp;:</strong>
                  <span class="status-text">{{ $t('boat.boatRequest.waitingAssignment') }}</span>
                </div>
                <div v-if="boat.boat_request_comment" class="request-comment">
                  <strong>{{ $t('boat.boatRequest.yourRequest') }}&nbsp;:</strong>
                  <span>{{ boat.boat_request_comment }}</span>
                </div>
              </div>
              
              <!-- Fulfilled: Show assigned boat -->
              <div v-else class="boat-request-fulfilled">
                <div class="fulfilled-header">
                  <strong>✓ {{ $t('boat.boatRequest.assignedBoat') }}&nbsp;:</strong>
                  <span class="boat-name">{{ boat.assigned_boat_identifier }}</span>
                </div>
                <div v-if="boat.assigned_boat_comment" class="assignment-details">
                  <strong>{{ $t('boat.boatRequest.assignmentDetails') }}&nbsp;:</strong>
                  <span>{{ boat.assigned_boat_comment }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="boat-actions">
            <BaseButton 
              variant="secondary"
              size="small"
              :disabled="!canEditBoat(boat)"
              :title="getEditTooltip(boat)"
              @click="viewBoat(boat)"
            >
              {{ $t('common.edit') }}
            </BaseButton>
            <BaseButton 
              variant="danger"
              size="small"
              :disabled="!canDeleteBoat(boat)"
              :title="getDeleteTooltip(boat)"
              @click="deleteBoat(boat)"
            >
              {{ $t('common.delete') }}
            </BaseButton>
          </div>
        </div>
      </div>

      <!-- Table View -->
      <div v-else class="boat-table-container">
        <SortableTable
          :columns="tableColumns"
          :data="displayBoats"
          :initial-sort-field="'boat_number'"
          :initial-sort-direction="'asc'"
          aria-label="Boats table"
          @sort="handleSort"
        >
          <!-- Custom cell: Boat number -->
          <template #cell-boat_number="{ value }">
            <span v-if="value" class="boat-number-text">{{ value }}</span>
            <span v-else class="no-race-text">-</span>
          </template>

          <!-- Custom cell: Race name -->
          <template #cell-race_name="{ row }">
            <span v-if="getRaceName(row)" class="race-name-cell">{{ getRaceName(row) }}</span>
            <span v-else class="no-race-text">-</span>
          </template>

          <!-- Custom cell: First rower -->
          <template #cell-first_rower="{ row }">
            {{ getFirstRowerLastName(row) }}
          </template>

          <!-- Custom cell: Gender -->
          <template #cell-gender="{ row }">
            {{ getCrewGenderCategory(row) }}
          </template>

          <!-- Custom cell: Average age -->
          <template #cell-average_age="{ row }">
            {{ getCrewAverageAge(row) }}
          </template>

          <!-- Custom cell: Club -->
          <template #cell-boat_club_display="{ value }">
            <span class="club-box">{{ value }}</span>
          </template>

          <!-- Custom cell: Seats -->
          <template #cell-seats="{ row }">
            {{ getFilledSeatsCount(row) }} / {{ row.seats?.length || 0 }}
          </template>

          <!-- Custom cell: Boat request status -->
          <template #cell-boat_request_status="{ row }">
            <span v-if="!row.boat_request_enabled" class="no-request">-</span>
            <span 
              v-else-if="row.assigned_boat_identifier" 
              class="boat-assigned-table"
            >
              ✓ {{ $t('boat.boatRequest.assigned') }}: {{ row.assigned_boat_identifier }}
            </span>
            <span v-else class="boat-requested">
              {{ $t('boat.boatRequest.waitingAssignment') }}
            </span>
          </template>

          <!-- Custom cell: Status -->
          <template #cell-status="{ row }">
            <StatusBadge :status="getBoatStatus(row)" size="medium" />
          </template>

          <!-- Custom cell: Actions -->
          <template #cell-actions="{ row }">
            <div class="action-buttons">
              <BaseButton 
                size="small"
                variant="secondary"
                :disabled="!canEditBoat(row)"
                :title="getEditTooltip(row)"
                @click="viewBoat(row)"
              >
                {{ $t('common.edit') }}
              </BaseButton>
              <BaseButton 
                size="small"
                variant="danger"
                :disabled="!canDeleteBoat(row)"
                :title="getDeleteTooltip(row)"
                @click="deleteBoat(row)"
              >
                {{ $t('common.delete') }}
              </BaseButton>
            </div>
          </template>
        </SortableTable>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useBoatStore } from '../stores/boatStore'
import { useRaceStore } from '../stores/raceStore'
import { useI18n } from 'vue-i18n'
import { usePermissions } from '../composables/usePermissions'
import { useConfirm } from '../composables/useConfirm'
import BoatRegistrationForm from '../components/BoatRegistrationForm.vue'
import ListHeader from '../components/shared/ListHeader.vue'
import ListFilters from '../components/shared/ListFilters.vue'
import BaseButton from '../components/base/BaseButton.vue'
import StatusBadge from '../components/base/StatusBadge.vue'
import LoadingSpinner from '../components/base/LoadingSpinner.vue'
import EmptyState from '../components/base/EmptyState.vue'
import SortableTable from '../components/composite/SortableTable.vue'
import { formatAverageAge, formatRaceName } from '../utils/formatters'

const router = useRouter()
const boatStore = useBoatStore()
const raceStore = useRaceStore()
const { t } = useI18n()
const { canPerformAction, getPermissionMessage, initialize: initializePermissions, loading: permissionsLoading } = usePermissions()
const { confirm } = useConfirm()

const showCreateForm = ref(false)
// Load view mode from localStorage or default to 'cards'
const viewMode = ref(localStorage.getItem('boatsViewMode') || 'cards')
const statusFilter = ref('all')
const raceFilter = ref('all')
const boatRequestFilter = ref('all')
const searchQuery = ref('')

// Watch for view mode changes and save to localStorage
watch(viewMode, (newMode) => {
  localStorage.setItem('boatsViewMode', newMode)
})

// Computed: available races for filter (from raceStore)
const availableRaces = computed(() => {
  return raceStore.races.slice().sort((a, b) => {
    // Sort by event_type first (42km before 21km), then by short_name
    if (a.event_type !== b.event_type) {
      return a.event_type === '42km' ? -1 : 1
    }
    return (a.short_name || a.name).localeCompare(b.short_name || b.name)
  })
})

// Column definitions for SortableTable
const tableColumns = computed(() => [
  {
    key: 'boat_number',
    label: t('boat.boatNumber'),
    sortable: true,
    width: '100px',
    sticky: 'left',
    responsive: 'always'
  },
  {
    key: 'event_type',
    label: t('boat.eventType'),
    sortable: true,
    minWidth: '80px',
    responsive: 'always'
  },
  {
    key: 'boat_type',
    label: t('boat.boatType'),
    sortable: true,
    minWidth: '80px',
    responsive: 'hide-below-1024'
  },
  {
    key: 'race_name',
    label: t('boat.selectedRace'),
    sortable: true,
    minWidth: '100px',
    responsive: 'always'
  },
  {
    key: 'first_rower',
    label: t('boat.firstRower'),
    sortable: false,
    minWidth: '120px',
    responsive: 'hide-below-1024'
  },
  {
    key: 'gender',
    label: t('boat.gender'),
    sortable: false,
    minWidth: '80px',
    responsive: 'hide-below-1024'
  },
  {
    key: 'average_age',
    label: t('boat.averageAge'),
    sortable: false,
    minWidth: '100px',
    responsive: 'hide-below-1024'
  },
  {
    key: 'boat_club_display',
    label: t('admin.boats.club'),
    sortable: true,
    minWidth: '150px',
    responsive: 'always'
  },
  {
    key: 'seats',
    label: t('boat.seats'),
    sortable: false,
    width: '80px',
    responsive: 'hide-below-1024'
  },
  {
    key: 'boat_request_status',
    label: t('boat.boatRequest.status'),
    sortable: false,
    minWidth: '180px',
    responsive: 'hide-below-1024'
  },
  {
    key: 'status',
    label: t('boat.status.label'),
    sortable: false,
    width: '120px',
    align: 'center',
    responsive: 'always'
  },
  {
    key: 'actions',
    label: t('common.actions'),
    sortable: false,
    width: '180px',
    align: 'right',
    sticky: 'right',
    responsive: 'always'
  }
])

const boatRegistrations = computed(() => {
  let boats = boatStore.boatRegistrations
  
  // Apply status filter
  if (statusFilter.value !== 'all') {
    boats = boats.filter(boat => boat.registration_status === statusFilter.value)
  }

  // Apply race filter
  if (raceFilter.value !== 'all') {
    boats = boats.filter(boat => boat.race_id === raceFilter.value)
  }

  // Apply boat request filter
  if (boatRequestFilter.value !== 'all') {
    boats = boats.filter(boat => {
      const hasRequest = boat.boat_request_enabled === true
      const hasFulfilled = hasRequest && boat.assigned_boat_identifier
      
      switch (boatRequestFilter.value) {
        case 'with':
          return hasRequest
        case 'without':
          return !hasRequest
        case 'pending':
          return hasRequest && !hasFulfilled
        case 'fulfilled':
          return hasFulfilled
        default:
          return true
      }
    })
  }

  // Apply search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    boats = boats.filter(boat => {
      const firstRower = getFirstRowerLastName(boat).toLowerCase()
      const eventType = boat.event_type?.toLowerCase() || ''
      const boatType = boat.boat_type?.toLowerCase() || ''
      const raceName = getRaceName(boat)?.toLowerCase() || ''
      const boatNumber = boat.boat_number?.toLowerCase() || ''
      
      return firstRower.includes(query) ||
             eventType.includes(query) ||
             boatType.includes(query) ||
             raceName.includes(query) ||
             boatNumber.includes(query)
    })
  }

  return boats
})

// Sort handler for SortableTable
const handleSort = ({ field, direction }) => {
  console.log(`Sorted by ${field} ${direction}`)
  // SortableTable handles sorting internally
}

// Use filtered data for display
const displayBoats = computed(() => boatRegistrations.value)

// Permission check functions
const canEditBoat = (boat) => {
  if (permissionsLoading.value) return false
  const resourceContext = {
    resource_type: 'boat_registration',
    resource_id: boat.boat_registration_id,
    resource_state: {
      paid: boat.registration_status === 'paid'
    }
  }
  return canPerformAction('edit_boat_registration', resourceContext)
}

const canDeleteBoat = (boat) => {
  if (permissionsLoading.value) return false
  const resourceContext = {
    resource_type: 'boat_registration',
    resource_id: boat.boat_registration_id,
    resource_state: {
      paid: boat.registration_status === 'paid'
    }
  }
  return canPerformAction('delete_boat_registration', resourceContext)
}

const getEditTooltip = (boat) => {
  if (canEditBoat(boat)) return ''
  const resourceContext = {
    resource_type: 'boat_registration',
    resource_id: boat.boat_registration_id,
    resource_state: {
      paid: boat.registration_status === 'paid'
    }
  }
  return getPermissionMessage('edit_boat_registration', resourceContext)
}

const getDeleteTooltip = (boat) => {
  if (canDeleteBoat(boat)) return ''
  const resourceContext = {
    resource_type: 'boat_registration',
    resource_id: boat.boat_registration_id,
    resource_state: {
      paid: boat.registration_status === 'paid'
    }
  }
  return getPermissionMessage('delete_boat_registration', resourceContext)
}

const canCreateBoatRegistration = computed(() => {
  if (permissionsLoading.value) return false
  return canPerformAction('create_boat_registration', {
    resource_type: 'boat_registration'
  })
})

const createBoatRegistrationTooltip = computed(() => {
  if (canCreateBoatRegistration.value) return ''
  return getPermissionMessage('create_boat_registration', {
    resource_type: 'boat_registration'
  })
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
  return formatAverageAge(boat.crew_composition.avg_age)
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
  return formatRaceName(race, t)
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
  const confirmed = await confirm({
    title: t('boat.confirmDeleteTitle'),
    message: t('boat.confirmDelete', { name: `${boat.event_type} ${boat.boat_type}` }),
    confirmText: t('common.delete'),
    cancelText: t('common.cancel'),
    variant: 'danger'
  })

  if (!confirmed) {
    return
  }

  try {
    await boatStore.deleteBoatRegistration(boat.boat_registration_id)
  } catch (error) {
    console.error('Failed to delete boat:', error)
  }
}

const clearFilters = () => {
  statusFilter.value = 'all'
  raceFilter.value = 'all'
  boatRequestFilter.value = 'all'
  searchQuery.value = ''
}

onMounted(async () => {
  // Initialize permissions
  await initializePermissions()
  
  // Load races if not already loaded
  if (raceStore.races.length === 0) {
    await raceStore.fetchRaces()
  }
  await boatStore.fetchBoatRegistrations()
})

</script>

<style scoped>
/* Mobile-first base styles */
.boats-view {
  padding: 0;
  max-width: 1200px;
  margin: 0 auto;
}

/* Removed custom filter-group styles - now handled by ListFilters component */

.filter-select {
  padding: var(--form-input-padding);
  border: 1px solid var(--form-input-border-color);
  border-radius: var(--form-input-border-radius);
  background: var(--color-bg-white);
  cursor: pointer;
  min-width: 120px;
  min-height: var(--form-input-min-height);
}

.filter-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--modal-overlay-bg);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: var(--modal-z-index);
  padding: 0;
}

.modal-content {
  background-color: var(--color-bg-white);
  border-radius: var(--modal-border-radius-mobile);
  width: 100%;
  max-width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.error-message {
  padding: var(--spacing-lg);
  background-color: var(--color-danger-light);
  border: 1px solid var(--color-danger-border);
  border-radius: var(--button-border-radius);
  color: var(--color-danger-text);
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-base);
}

.boat-cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-lg);
}

.boat-card {
  background-color: var(--color-bg-white);
  border: 2px solid var(--color-border);
  border-radius: var(--card-border-radius);
  padding: var(--card-padding-mobile);
  transition: box-shadow var(--transition-normal);
}

.boat-card.status-complete {
  border-color: var(--color-success);
}

.boat-card.status-free {
  border-color: var(--color-primary);
  background: linear-gradient(to bottom, #f0f7ff 0%, white 100%);
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.15);
}

.boat-card.status-paid {
  border-color: var(--color-primary);
  background: linear-gradient(to bottom, #f0f7ff 0%, white 100%);
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.15);
}

.boat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
  gap: var(--spacing-sm);
}

.boat-header h3 {
  margin: 0;
  color: var(--color-dark);
  font-size: var(--font-size-lg);
  word-break: break-word;
  flex: 1;
}

.boat-details {
  margin-bottom: var(--spacing-lg);
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: var(--font-size-base);
  gap: var(--spacing-sm);
}

.detail-row .label {
  font-weight: var(--font-weight-medium);
  color: var(--color-muted);
  flex-shrink: 0;
}

.detail-row span:last-child {
  text-align: right;
  word-break: break-word;
}

.club-box {
  display: inline-block;
  max-width: 200px;
  padding: var(--spacing-xs) var(--spacing-sm);
  background-color: var(--color-bg-light);
  border: 1px solid var(--form-input-border-color);
  border-radius: var(--button-border-radius);
  font-size: var(--font-size-xs);
  line-height: 1.3;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.club-display {
  display: inline-flex;
  align-items: center;
}

.club-with-popover {
  display: inline-flex;
  align-items: center;
}

.race-name {
  margin-top: var(--spacing-lg);
  padding: var(--spacing-md);
  background-color: var(--color-light);
  border-radius: var(--button-border-radius);
  font-size: var(--font-size-base);
  line-height: 1.4;
  color: #495057;
  word-break: break-word;
}

.race-name strong {
  color: var(--color-dark);
}

.assignment-comment {
  margin-top: var(--spacing-md);
  padding: var(--spacing-md);
  background-color: var(--color-info-light);
  border-left: 4px solid var(--color-primary);
  border-radius: var(--button-border-radius);
  font-size: var(--font-size-base);
  line-height: 1.4;
  color: #495057;
  word-break: break-word;
}

.assignment-comment strong {
  color: var(--color-dark);
}

.boat-assigned {
  color: var(--color-success);
  font-weight: var(--font-weight-semibold);
}

.boat-pending {
  color: var(--color-warning);
  font-style: italic;
}

.boat-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}

/* Table View Styles */
.boat-table-container {
  background-color: var(--color-bg-white);
  border-radius: var(--card-border-radius);
  overflow-x: auto;
  box-shadow: var(--card-shadow);
  padding: var(--spacing-lg);
  -webkit-overflow-scrolling: touch;
}

/* Action buttons in table */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

/* Boat request status styles */
.no-request {
  color: var(--color-secondary);
}

.boat-requested {
  color: var(--color-warning);
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
}

.boat-assigned-table {
  color: var(--color-success);
  font-weight: var(--font-weight-semibold);
}

/* Boat Request Section Styles (for card view) */
.boat-request-section {
  margin-bottom: var(--spacing-lg);
}

.boat-request-pending {
  background-color: var(--color-warning-light);
  border-left: 4px solid var(--color-warning);
  padding: var(--spacing-md);
  border-radius: var(--button-border-radius);
}

.boat-request-pending .request-header {
  margin-bottom: var(--spacing-sm);
}

.boat-request-pending .status-text {
  color: var(--color-warning-text);
  font-weight: var(--font-weight-semibold);
}

.boat-request-pending .request-comment {
  margin-top: var(--spacing-sm);
  font-size: var(--font-size-base);
  color: var(--color-muted);
}

.boat-request-fulfilled {
  background-color: var(--color-success-light);
  border-left: 4px solid var(--color-success);
  padding: var(--spacing-md);
  border-radius: var(--button-border-radius);
}

.boat-request-fulfilled .fulfilled-header {
  margin-bottom: var(--spacing-sm);
}

.boat-request-fulfilled .boat-name {
  color: var(--color-success-text);
  font-weight: var(--font-weight-semibold);
}

.boat-request-fulfilled .assignment-details {
  margin-top: var(--spacing-sm);
  font-size: var(--font-size-base);
  color: var(--color-success-text);
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .filter-group {
    width: 100%;
  }

  .filter-select {
    width: 100%;
    font-size: var(--form-input-font-size-mobile); /* Prevents iOS zoom */
  }
}

/* Tablet and larger screens */
@media (min-width: 768px) {
  .filter-group {
    width: auto;
  }

  .modal-overlay {
    align-items: center;
    padding: var(--spacing-lg);
  }

  .modal-content {
    border-radius: var(--modal-border-radius-desktop);
    width: 90%;
    max-width: var(--modal-max-width);
  }

  .boat-cards {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: var(--spacing-xl);
  }

  .boat-card {
    padding: var(--card-padding-desktop);
  }

  .boat-card:hover {
    box-shadow: var(--card-shadow-hover);
  }

  .boat-header h3 {
    font-size: var(--font-size-xl);
  }

  .boat-table-container {
    border-radius: var(--card-border-radius);
    margin: 0;
  }
}
</style>
