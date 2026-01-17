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

          <div v-if="getRaceName(boat)" class="race-name">
            <strong>{{ $t('boat.selectedRace') }}&nbsp;:</strong> {{ getRaceName(boat) }}
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
        <table class="boat-table">
          <thead>
            <tr>
              <th class="sortable-header" @click="sortBy('boat_number')">
                {{ $t('boat.boatNumber') }} {{ getSortIndicator('boat_number') }}
              </th>
              <th class="sortable-header" @click="sortBy('event_type')">
                {{ $t('boat.eventType') }} {{ getSortIndicator('event_type') }}
              </th>
              <th>{{ $t('boat.boatType') }}</th>
              <th>{{ $t('boat.firstRower') }}</th>
              <th>{{ $t('boat.gender') }}</th>
              <th>{{ $t('boat.averageAge') }}</th>
              <th class="sortable-header" @click="sortBy('boat_club_display')">
                {{ $t('admin.boats.club') }} {{ getSortIndicator('boat_club_display') }}
              </th>
              <th>{{ $t('boat.seats') }}</th>
              <th>{{ $t('boat.boatRequest.status') }}</th>
              <th>{{ $t('boat.status.label') }}</th>
              <th>{{ $t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="boat in displayBoats" :key="boat.boat_registration_id">
              <tr 
                :class="getRowClass(boat)"
              >
                <td>
                  <span v-if="boat.boat_number" class="boat-number-cell">{{ boat.boat_number }}</span>
                  <span v-else class="no-race-cell">-</span>
                </td>
                <td>{{ boat.event_type }}</td>
                <td>{{ boat.boat_type }}</td>
                <td>{{ getFirstRowerLastName(boat) }}</td>
                <td>{{ getCrewGenderCategory(boat) }}</td>
                <td>{{ getCrewAverageAge(boat) }}</td>
                <td>
                  <span class="club-box">{{ boat.boat_club_display }}</span>
                </td>
                <td>
                  {{ getFilledSeatsCount(boat) }} / {{ boat.seats?.length || 0 }}
                </td>
                <td>
                  <span v-if="!boat.boat_request_enabled" class="no-request">-</span>
                  <span 
                    v-else-if="boat.assigned_boat_identifier" 
                    class="boat-assigned-table"
                  >
                    ✓ {{ $t('boat.boatRequest.assigned') }}: {{ boat.assigned_boat_identifier }}
                  </span>
                  <span v-else class="boat-requested">
                    {{ $t('boat.boatRequest.waitingAssignment') }}
                  </span>
                </td>
                <td>
                  <StatusBadge :status="getBoatStatus(boat)" size="medium" />
                </td>
                <td class="actions-cell">
                  <BaseButton 
                    size="small"
                    variant="secondary"
                    :disabled="!canEditBoat(boat)"
                    :title="getEditTooltip(boat)"
                    @click="viewBoat(boat)"
                    fullWidth
                  >
                    {{ $t('common.edit') }}
                  </BaseButton>
                  <BaseButton 
                    size="small"
                    variant="danger"
                    :disabled="!canDeleteBoat(boat)"
                    :title="getDeleteTooltip(boat)"
                    @click="deleteBoat(boat)"
                    fullWidth
                  >
                    {{ $t('common.delete') }}
                  </BaseButton>
                </td>
              </tr>
              <tr v-if="getRaceName(boat)" class="race-row" :class="`row-status-${boat.registration_status}`">
                <td colspan="11" class="race-cell">
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

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useBoatStore } from '../stores/boatStore'
import { useRaceStore } from '../stores/raceStore'
import { useI18n } from 'vue-i18n'
import { useTableSort } from '../composables/useTableSort'
import { usePermissions } from '../composables/usePermissions'
import { useConfirm } from '../composables/useConfirm'
import BoatRegistrationForm from '../components/BoatRegistrationForm.vue'
import ListHeader from '../components/shared/ListHeader.vue'
import ListFilters from '../components/shared/ListFilters.vue'
import BaseButton from '../components/base/BaseButton.vue'
import StatusBadge from '../components/base/StatusBadge.vue'
import LoadingSpinner from '../components/base/LoadingSpinner.vue'
import EmptyState from '../components/base/EmptyState.vue'
import { formatAverageAge } from '../utils/formatters'

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
const boatRequestFilter = ref('all')
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

// Set up table sorting
const boatsForSorting = computed(() => boatRegistrations.value)
const { sortedData, sortBy, getSortIndicator } = useTableSort(boatsForSorting)

// Use sorted data for display
const displayBoats = computed(() => sortedData.value)

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

.filter-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.filter-group label {
  font-weight: var(--font-weight-medium);
  white-space: nowrap;
}

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
  border-radius: 0;
  overflow-x: auto;
  box-shadow: var(--card-shadow);
  margin: 0 -1rem;
  -webkit-overflow-scrolling: touch;
}

.boat-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1200px;
  table-layout: fixed;
}

.boat-table th:nth-child(1) { width: 90px; }  /* Boat Number */
.boat-table th:nth-child(2) { width: 70px; }  /* Event Type */
.boat-table th:nth-child(3) { width: 70px; }  /* Boat Type */
.boat-table th:nth-child(4) { width: 110px; } /* First Rower */
.boat-table th:nth-child(5) { width: 70px; }  /* Gender */
.boat-table th:nth-child(6) { width: 90px; }  /* Average Age */
.boat-table th:nth-child(7) { width: 180px; } /* Club */
.boat-table th:nth-child(8) { width: 60px; }  /* Seats - REDUCED */
.boat-table th:nth-child(9) { width: 160px; } /* Boat Request - INCREASED */
.boat-table th:nth-child(10) { width: 100px; } /* Status - INCREASED */
.boat-table th:nth-child(11) { width: 140px; } /* Actions - INCREASED */

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

/* Boat Request Section Styles */
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

.info-icon {
  margin-left: var(--spacing-xs);
  font-size: var(--font-size-base);
  cursor: help;
}

.boat-table thead {
  background-color: var(--table-header-bg);
}

.boat-table th {
  padding: var(--table-cell-padding-mobile);
  text-align: left;
  font-weight: var(--table-header-font-weight);
  color: #495057;
  border-bottom: 2px solid var(--table-border-color);
  font-size: var(--font-size-base);
}

.sortable-header {
  cursor: pointer;
  user-select: none;
  transition: background-color var(--transition-normal);
}

.sortable-header:hover {
  background-color: #e9ecef;
}

.boat-table td {
  padding: var(--table-cell-padding-mobile);
  border-bottom: 1px solid var(--table-border-color);
  font-size: var(--font-size-base);
}

.boat-table tbody tr.row-status-complete {
  border-left: 4px solid var(--color-success);
}

.boat-table tbody tr.row-status-free {
  border-left: 4px solid var(--color-primary);
}

.boat-table tbody tr.row-status-paid {
  border-left: 4px solid var(--color-primary);
}

.boat-table tbody tr.row-status-incomplete {
  border-left: 4px solid var(--color-warning);
}

.boat-table tbody tr.row-forfait {
  border-left: 4px solid var(--color-danger);
  background-color: #fff5f5;
}

.boat-table .race-row {
  background-color: var(--color-light);
  border-left-width: 4px;
}

.boat-table .race-cell {
  padding: var(--spacing-sm) var(--table-cell-padding-mobile);
  font-size: var(--font-size-sm);
  font-style: italic;
  color: #495057;
}

.boat-table .race-label {
  font-weight: var(--font-weight-semibold);
  font-style: normal;
  color: var(--color-dark);
}

.actions-cell {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  padding: var(--table-cell-padding-mobile) !important;
  min-width: 120px;
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

  .boat-table th {
    padding: var(--table-cell-padding-desktop);
    font-size: var(--font-size-md);
  }

  .boat-table td {
    padding: var(--table-cell-padding-desktop);
    font-size: var(--font-size-md);
  }

  .boat-table tbody tr:hover {
    background-color: var(--table-hover-bg);
  }

  .boat-table .race-cell {
    padding: var(--spacing-sm) var(--table-cell-padding-desktop);
    font-size: var(--font-size-base);
  }

  .actions-cell {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
}
</style>
