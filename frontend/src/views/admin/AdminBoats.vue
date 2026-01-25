<template>
  <div class="admin-boats">
    <ListHeader
      :title="$t('admin.boats.title')"
      :subtitle="$t('admin.boats.subtitle')"
      v-model:viewMode="viewMode"
      :actionLabel="$t('admin.boats.addBoat')"
      @action="showCreateModal = true"
    />

    <ListFilters
      v-model:searchQuery="searchTerm"
      :searchPlaceholder="$t('admin.boats.searchPlaceholder')"
      @clear="clearFilters"
    >
      <template #filters>
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

        <div class="filter-group">
          <label>{{ $t('admin.boats.filterByRace') }}&nbsp;:</label>
          <select v-model="filterRace" class="filter-select">
            <option value="">{{ $t('admin.boats.allRaces') }}</option>
            <option v-for="race in availableRaces" :key="race.race_id" :value="race.race_id">
              {{ formatRaceName(race, $t) }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>{{ $t('boat.filter.boatRequest') }}&nbsp;:</label>
          <select v-model="filterBoatRequest" class="filter-select">
            <option value="">{{ $t('boat.filter.allRequests') }}</option>
            <option value="with">{{ $t('boat.filter.withRequest') }}</option>
            <option value="without">{{ $t('boat.filter.withoutRequest') }}</option>
            <option value="pending">{{ $t('boat.filter.requestPending') }}</option>
            <option value="fulfilled">{{ $t('boat.filter.requestFulfilled') }}</option>
          </select>
        </div>
      </template>
    </ListFilters>

    <!-- Loading state -->
    <LoadingSpinner 
      v-if="loading"
      :message="$t('common.loading')"
    />

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
            <StatusBadge :status="getBoatStatus(boat)" size="medium" />
          </div>

          <div class="boat-details">
            <div class="detail-row">
              <span class="label">{{ $t('admin.boats.boatNumber') }}&nbsp;:</span>
              <span v-if="boat.boat_number" class="boat-number-text">{{ boat.boat_number }}</span>
              <span v-else class="no-race-text">-</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('boat.selectedRace') }}&nbsp;:</span>
              <span v-if="getRaceName(boat)" class="race-name-cell">{{ getRaceName(boat) }}</span>
              <span v-else class="no-race-text">-</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('boat.firstRower') }}&nbsp;:</span>
              <span>{{ boat.first_rower }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('boat.filledSeats') }}&nbsp;:</span>
              <span>{{ getFilledSeatsCount(boat) }} / {{ boat.seats?.length || 0 }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('boat.averageAge') }}&nbsp;:</span>
              <span>{{ getCrewAverageAge(boat) }}</span>
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
              <span class="club-box">{{ boat.boat_club_display }}</span>
            </div>
            <div v-if="boat.registration_status === 'paid' && boat.paid_at" class="detail-row">
              <span class="label">{{ $t('boat.paidOn') }}&nbsp;:</span>
              <span>{{ formatDate(boat.paid_at) }}</span>
            </div>
          </div>

          <div v-if="boat.boat_request_enabled" class="boat-actions">
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

          <div class="boat-actions">
            <BaseButton 
              variant="secondary"
              size="small"
              @click="editBoat(boat)"
            >
              {{ $t('admin.boats.assignBoat') }}
            </BaseButton>
            <BaseButton 
              size="small"
              :variant="boat.forfait ? 'secondary' : 'warning'"
              @click="toggleForfait(boat)"
            >
              {{ boat.forfait ? $t('admin.boats.removeForfait') : $t('admin.boats.setForfait') }}
            </BaseButton>
            <BaseButton 
              variant="danger"
              size="small"
              @click="deleteBoat(boat)"
            >
              {{ $t('common.delete') }}
            </BaseButton>
          </div>
        </div>
      </div>

      <!-- Table View -->
      <div v-else class="boats-table-container">
        <SortableTable
          :columns="tableColumns"
          :data="paginatedBoats"
          :initial-sort-field="'team_manager_name'"
          :initial-sort-direction="'asc'"
          aria-label="Boats table"
        >
          <!-- Custom cell: Boat Number -->
          <template #cell-boat_number="{ value }">
            <span v-if="value" class="boat-number-text">{{ value }}</span>
            <span v-else class="no-race-text">-</span>
          </template>

          <!-- Custom cell: Race Name -->
          <template #cell-race_name="{ value }">
            <span v-if="value && value !== '-'" class="race-name-cell">{{ value }}</span>
            <span v-else class="no-race-text">-</span>
          </template>

          <!-- Custom cell: Club Display -->
          <template #cell-boat_club_display="{ value }">
            <span class="club-box">{{ value }}</span>
          </template>

          <!-- Custom cell: Boat Request Status -->
          <template #cell-boat_request_status="{ row }">
            <span v-if="!row._original.boat_request_enabled" class="no-request">-</span>
            <span 
              v-else-if="row._original.assigned_boat_identifier" 
              class="boat-assigned-admin"
            >
              ✓ {{ $t('boat.boatRequest.assigned') }}: {{ row._original.assigned_boat_identifier }}
            </span>
            <span v-else class="boat-requested-admin">
              {{ $t('boat.boatRequest.waitingAssignment') }}
            </span>
          </template>

          <!-- Custom cell: Status Badge -->
          <template #cell-status="{ row }">
            <StatusBadge :status="getBoatStatus(row._original)" size="medium" />
          </template>

          <!-- Custom cell: Actions -->
          <template #cell-actions="{ row }">
            <div class="actions-cell">
              <BaseButton 
                size="small"
                variant="secondary"
                @click="editBoat(row._original)"
                :title="$t('admin.boats.assignBoat')"
                fullWidth
              >
                {{ $t('admin.boats.assignBoat') }}
              </BaseButton>
              <BaseButton 
                size="small"
                :variant="row._original.forfait ? 'secondary' : 'warning'"
                @click="toggleForfait(row._original)"
                :title="row._original.forfait ? $t('admin.boats.removeForfait') : $t('admin.boats.setForfait')"
                fullWidth
              >
                {{ row._original.forfait ? $t('admin.boats.removeForfait') : $t('admin.boats.setForfait') }}
              </BaseButton>
              <BaseButton 
                size="small"
                variant="danger"
                @click="deleteBoat(row._original)"
                :disabled="row._original.registration_status === 'paid'"
                :title="row._original.registration_status === 'paid' ? $t('boat.cannotDeletePaid') : ''"
                fullWidth
              >
                {{ $t('common.delete') }}
              </BaseButton>
            </div>
          </template>
        </SortableTable>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <BaseButton 
          variant="primary"
          @click="currentPage--"
          :disabled="currentPage === 1"
        >
          {{ $t('common.previous') }}
        </BaseButton>
        <span class="page-info">
          {{ $t('common.pageInfo', { current: currentPage, total: totalPages }) }}
        </span>
        <BaseButton 
          variant="primary"
          @click="currentPage++"
          :disabled="currentPage === totalPages"
        >
          {{ $t('common.next') }}
        </BaseButton>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <BaseModal
      :show="showCreateModal || showEditModal"
      :title="showEditModal ? $t('admin.boats.editBoat') : $t('admin.boats.addBoat')"
      @close="closeModals"
    >
      <template #default>
        <!-- Edit Modal Content -->
        <div v-if="showEditModal && editingBoat">
          <!-- Boat Assignment Section (only if boat_request_enabled) -->
          <div v-if="editingBoat.boat_request_enabled" class="boat-assignment-section">
            <h3>{{ $t('boat.boatRequest.title') }}</h3>
            
            <div v-if="editingBoat.boat_request_comment" class="request-comment">
              <label>{{ $t('admin.boats.teamManagerRequest') }}:</label>
              <p>{{ editingBoat.boat_request_comment }}</p>
            </div>
            
            <div class="form-group">
              <label for="assigned_boat_identifier">{{ $t('admin.boats.assignBoatLabel') }}:</label>
              <input
                id="assigned_boat_identifier"
                v-model="editForm.assigned_boat_identifier"
                type="text"
                maxlength="100"
                :placeholder="$t('admin.boats.assignBoatPlaceholder')"
                class="form-input"
              />
              <p class="help-text">
                {{ $t('admin.boats.assignBoatHelp') }}
              </p>
            </div>
            
            <div class="form-group">
              <label for="assigned_boat_comment">{{ $t('admin.boats.assignmentDetailsLabel') }} ({{ $t('admin.boats.optional') }}):</label>
              <textarea
                id="assigned_boat_comment"
                v-model="editForm.assigned_boat_comment"
                maxlength="500"
                rows="3"
                :placeholder="$t('admin.boats.assignmentDetailsPlaceholder')"
                class="form-textarea"
              ></textarea>
              <span class="char-count">
                {{ editForm.assigned_boat_comment?.length || 0 }} / 500
              </span>
              <p class="help-text">
                {{ $t('admin.boats.assignmentDetailsHelp') }}
              </p>
            </div>
          </div>
          
          <div v-else class="info-message">
            <p>{{ $t('admin.boats.noBoatRequest') }}</p>
          </div>
        </div>
        
        <!-- Create Modal Content -->
        <div v-if="showCreateModal">
          <p class="info-text">{{ $t('admin.boats.modalInfo') }}</p>
          <p>{{ $t('admin.boats.useTeamManagerInterface') }}</p>
        </div>
      </template>
      
      <template #footer>
        <BaseButton variant="secondary" @click="closeModals">
          {{ $t('common.cancel') }}
        </BaseButton>
        <BaseButton 
          v-if="showEditModal"
          variant="primary"
          @click="saveBoatAssignment"
          :disabled="saving"
          :loading="saving"
        >
          {{ $t('common.save') }}
        </BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useConfirm } from '../../composables/useConfirm'
import apiClient from '../../services/apiClient'
import { useRaceStore } from '../../stores/raceStore'
import SortableTable from '../../components/composite/SortableTable.vue'
import ListHeader from '../../components/shared/ListHeader.vue'
import ListFilters from '../../components/shared/ListFilters.vue'
import BaseButton from '../../components/base/BaseButton.vue'
import StatusBadge from '../../components/base/StatusBadge.vue'
import LoadingSpinner from '../../components/base/LoadingSpinner.vue'
import BaseModal from '../../components/base/BaseModal.vue'
import { formatAverageAge, formatRaceName } from '../../utils/formatters'

export default {
  name: 'AdminBoats',
  components: {
    SortableTable,
    ListHeader,
    ListFilters,
    BaseButton,
    StatusBadge,
    LoadingSpinner,
    BaseModal
  },
  setup() {
    const { t } = useI18n()
    const { confirm } = useConfirm()
    const raceStore = useRaceStore()

    const boats = ref([])
    const loading = ref(false)
    const error = ref(null)
    
    const searchTerm = ref('')
    const filterTeamManager = ref('')
    const filterClub = ref('')
    const filterStatus = ref('')
    const filterRace = ref('')
    const filterBoatRequest = ref('')
    
    const currentPage = ref(1)
    const itemsPerPage = 50
    const viewMode = ref(localStorage.getItem('adminBoatsViewMode') || 'table')
    
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const editingBoat = ref(null)
    const editForm = ref({
      assigned_boat_identifier: '',
      assigned_boat_comment: ''
    })
    const saving = ref(false)
    const forfaitProcessing = ref(false)

    // Column definitions for SortableTable
    const tableColumns = computed(() => [
      {
        key: 'boat_number',
        label: t('admin.boats.boatNumber'),
        sortable: true,
        width: '120px',
        sticky: 'left',
        responsive: 'always'
      },
      {
        key: 'event_type',
        label: t('boat.eventType'),
        sortable: true,
        // No width - shrinks to content (42km/21km)
        responsive: 'always'
      },
      {
        key: 'boat_type',
        label: t('boat.boatType'),
        sortable: false,
        // No width - shrinks to content (skiff, 4+, 8+, etc.)
        responsive: 'always'
      },
      {
        key: 'race_name',
        label: t('boat.selectedRace'),
        sortable: true,
        minWidth: '100px', // Reduced from 150px
        responsive: 'always'
      },
      {
        key: 'first_rower',
        label: t('boat.firstRower'),
        sortable: false,
        minWidth: '100px', // Reduced from 120px
        responsive: 'hide-below-1024'
      },
      {
        key: 'average_age',
        label: t('boat.averageAge'),
        sortable: false,
        width: '80px', // Reduced from 100px
        align: 'center',
        responsive: 'always'
      },
      {
        key: 'seats',
        label: t('boat.seats'),
        sortable: false,
        width: '80px', // Reduced from 100px
        align: 'center',
        responsive: 'always'
      },
      {
        key: 'team_manager_name',
        label: t('admin.boats.teamManager'),
        sortable: true,
        minWidth: '120px', // Reduced from 150px
        responsive: 'hide-below-1024'
      },
      {
        key: 'boat_club_display',
        label: t('admin.boats.club'),
        sortable: true,
        minWidth: '100px', // Reduced from 120px
        responsive: 'always'
      },
      {
        key: 'boat_request_status',
        label: t('boat.boatRequest.status'),
        sortable: false,
        minWidth: '120px', // Reduced from 150px
        responsive: 'hide-below-1024'
      },
      {
        key: 'status',
        label: t('boat.status.label'),
        sortable: false,
        width: '100px', // Reduced from 120px
        align: 'center',
        responsive: 'always'
      },
      {
        key: 'actions',
        label: t('common.actions'),
        sortable: false,
        width: '250px',
        align: 'right',
        sticky: 'right',
        responsive: 'always'
      }
    ])

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

    // Computed: available races for filter (from raceStore)
    const availableRaces = computed(() => {
      return raceStore.races.sort((a, b) => {
        // Sort by event_type first (42km before 21km), then by short_name
        if (a.event_type !== b.event_type) {
          return a.event_type === '42km' ? -1 : 1
        }
        return (a.short_name || a.name).localeCompare(b.short_name || b.name)
      })
    })

    // Computed: filtered boats (without sorting - handled by SortableTable)
    const filteredBoats = computed(() => {
      let result = boats.value

      // Apply search filter
      if (searchTerm.value) {
        const search = searchTerm.value.toLowerCase()
        result = result.filter(boat => {
          // Search in basic fields
          const basicMatch = boat.event_type?.toLowerCase().includes(search) ||
            boat.boat_type?.toLowerCase().includes(search) ||
            boat.team_manager_name?.toLowerCase().includes(search) ||
            boat.boat_club_display?.toLowerCase().includes(search) ||
            boat.boat_registration_id?.toLowerCase().includes(search) ||
            boat.boat_number?.toLowerCase().includes(search)
          
          // Also search in club_list array
          const clubListMatch = boat.club_list?.some(club => 
            club.toLowerCase().includes(search)
          )
          
          // Search in stroke seat (first rower) name
          const strokeSeatMatch = getFirstRowerLastName(boat).toLowerCase().includes(search) ||
            getFirstRowerName(boat).toLowerCase().includes(search)
          
          return basicMatch || clubListMatch || strokeSeatMatch
        })
      }

      // Apply team manager filter
      if (filterTeamManager.value) {
        result = result.filter(boat => boat.team_manager_id === filterTeamManager.value)
      }

      // Apply club filter
      if (filterClub.value && filterClub.value.trim()) {
        const club = filterClub.value.toLowerCase().trim()
        result = result.filter(boat => {
          // Check boat_club_display
          const clubDisplay = (boat.boat_club_display || '').toLowerCase().trim()
          if (clubDisplay.includes(club)) return true
          
          // Also check club_list array
          if (boat.club_list?.some(c => c.toLowerCase().includes(club))) return true
          
          return false
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

      // Apply race filter
      if (filterRace.value) {
        result = result.filter(boat => boat.race_id === filterRace.value)
      }

      // Apply boat request filter
      if (filterBoatRequest.value) {
        result = result.filter(boat => {
          const hasRequest = boat.boat_request_enabled === true
          const hasFulfilled = hasRequest && boat.assigned_boat_identifier
          
          switch (filterBoatRequest.value) {
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

      return result
    })

    // Computed: table data with computed columns
    const tableData = computed(() => {
      return filteredBoats.value.map(boat => ({
        ...boat,
        // Add computed columns for table display
        first_rower: getFirstRowerLastName(boat),
        average_age: getCrewAverageAge(boat),
        seats: `${getFilledSeatsCount(boat)} / ${boat.seats?.length || 0}`,
        race_name: getRaceName(boat) || '-',
        boat_request_status: getBoatRequestStatus(boat),
        status: getBoatStatus(boat),
        // Keep original boat object for actions
        _original: boat
      }))
    })

    // Computed: paginated boats
    const paginatedBoats = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      return tableData.value.slice(start, end)
    })

    const totalPages = computed(() => {
      return Math.ceil(tableData.value.length / itemsPerPage)
    })

    // Helper functions
    const getFilledSeatsCount = (boat) => {
      if (!boat.seats || !Array.isArray(boat.seats)) return 0
      return boat.seats.filter(seat => seat.crew_member_id).length
    }

    const getFirstRowerLastName = (boat) => {
      if (!boat.seats || !Array.isArray(boat.seats) || boat.seats.length === 0) return '-'
      const rowers = boat.seats.filter(seat => seat.type === 'rower')
      if (rowers.length === 0) return '-'
      const strokeSeat = rowers.reduce((max, seat) => seat.position > max.position ? seat : max, rowers[0])
      return strokeSeat?.crew_member_last_name || '-'
    }

    const getFirstRowerName = (boat) => {
      if (!boat.seats || !Array.isArray(boat.seats) || boat.seats.length === 0) return '-'
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

    const getRaceName = (boat) => {
      if (!boat.race_id) return null
      const race = raceStore.races.find(r => r.race_id === boat.race_id)
      return formatRaceName(race, t)
    }

    const getBoatStatus = (boat) => {
      if (boat.forfait) return 'forfait'
      return boat.registration_status || 'incomplete'
    }

    const getRowClass = (boat) => {
      if (boat.forfait) return 'row-forfait'
      return `row-status-${boat.registration_status || 'incomplete'}`
    }

    const getCrewAverageAge = (boat) => {
      if (!boat.crew_composition || !boat.crew_composition.avg_age) return '-'
      return formatAverageAge(boat.crew_composition.avg_age)
    }

    const getBoatRequestStatus = (boat) => {
      if (!boat.boat_request_enabled) return '-'
      if (boat.assigned_boat_identifier) {
        return `✓ ${t('boat.boatRequest.assigned')}: ${boat.assigned_boat_identifier}`
      }
      return t('boat.boatRequest.waitingAssignment')
    }

    // Actions
    const clearFilters = () => {
      searchTerm.value = ''
      filterTeamManager.value = ''
      filterClub.value = ''
      filterStatus.value = ''
      filterRace.value = ''
      filterBoatRequest.value = ''
      currentPage.value = 1
    }

    const toggleForfait = async (boat) => {
      // Prevent double-execution
      if (forfaitProcessing.value) {
        return
      }
      
      const confirmed = await confirm({
        title: t(boat.forfait ? 'admin.boats.confirmRemoveForfaitTitle' : 'admin.boats.confirmSetForfaitTitle'),
        message: t(boat.forfait ? 'admin.boats.confirmRemoveForfait' : 'admin.boats.confirmSetForfait'),
        confirmText: t(boat.forfait ? 'admin.boats.removeForfait' : 'admin.boats.setForfait'),
        cancelText: t('common.cancel'),
        variant: 'warning'
      })
      
      if (!confirmed) {
        return
      }

      forfaitProcessing.value = true
      
      try {
        await apiClient.put(`/admin/boats/${boat.team_manager_id}/${boat.boat_registration_id}`, {
          forfait: !boat.forfait
        })
        
        // Update local state without refreshing the entire list (preserves scroll position)
        boat.forfait = !boat.forfait
        
        // Update registration_status based on forfait state
        if (boat.forfait) {
          boat.registration_status = 'forfait'
        } else {
          // Recalculate status based on seats
          const filledSeats = getFilledSeatsCount(boat)
          boat.registration_status = filledSeats === boat.seats?.length ? 'complete' : 'incomplete'
        }
      } catch (err) {
        console.error('Failed to toggle forfait:', err)
        error.value = t('admin.boats.updateError')
      } finally {
        forfaitProcessing.value = false
      }
    }

    const deleteBoat = async (boat) => {
      const confirmed = await confirm({
        title: t('admin.boats.confirmDeleteTitle'),
        message: t('admin.boats.confirmDelete', { boat: `${boat.event_type} ${boat.boat_type}` }),
        confirmText: t('common.delete'),
        cancelText: t('common.cancel'),
        variant: 'danger'
      })
      
      if (!confirmed) {
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
      editForm.value = {
        assigned_boat_identifier: '',
        assigned_boat_comment: ''
      }
    }

    const editBoat = (boat) => {
      editingBoat.value = boat
      editForm.value = {
        assigned_boat_identifier: boat.assigned_boat_identifier || '',
        assigned_boat_comment: boat.assigned_boat_comment || ''
      }
      showEditModal.value = true
    }

    const saveBoatAssignment = async () => {
      if (!editingBoat.value) return
      
      saving.value = true
      error.value = null
      
      try {
        const updates = {
          assigned_boat_identifier: editForm.value.assigned_boat_identifier.trim() || null,
          assigned_boat_comment: editForm.value.assigned_boat_comment.trim() || null
        }
        
        await apiClient.put(
          `/admin/boats/${editingBoat.value.team_manager_id}/${editingBoat.value.boat_registration_id}`,
          updates
        )
        
        // Update local state
        editingBoat.value.assigned_boat_identifier = updates.assigned_boat_identifier
        editingBoat.value.assigned_boat_comment = updates.assigned_boat_comment
        
        // Refresh boats to get updated status
        await fetchBoats()
        
        closeModals()
      } catch (err) {
        console.error('Failed to save boat assignment:', err)
        error.value = t('admin.boats.updateError')
      } finally {
        saving.value = false
      }
    }

    onMounted(async () => {
      // Load races if not already loaded
      if (raceStore.races.length === 0) {
        await raceStore.fetchRaces()
      }
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
      filterRace,
      filterBoatRequest,
      currentPage,
      totalPages,
      viewMode,
      showCreateModal,
      showEditModal,
      editingBoat,
      teamManagers,
      availableRaces,
      filteredBoats,
      tableColumns,
      tableData,
      paginatedBoats,
      getFilledSeatsCount,
      getFirstRowerLastName,
      getFirstRowerName,
      getBoatStatus,
      getRowClass,
      getRaceName,
      getCrewAverageAge,
      getBoatRequestStatus,
      clearFilters,
      toggleForfait,
      deleteBoat,
      closeModals,
      editBoat,
      saveBoatAssignment,
      editForm,
      saving,
      formatRaceName,
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
  max-width: 100%;
  margin: 0 auto;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  min-width: 200px;
}

.filter-group label {
  font-weight: var(--font-weight-medium);
  color: var(--color-dark);
  font-size: var(--font-size-base);
}

.filter-select,
.filter-input {
  padding: var(--form-input-padding);
  border: 1px solid var(--form-input-border-color);
  border-radius: var(--form-input-border-radius);
  font-size: var(--font-size-base);
  min-height: var(--form-input-min-height);
}

.loading {
  text-align: center;
  padding: 3rem;
}

.error-message {
  padding: var(--spacing-lg);
  background-color: var(--color-danger-light);
  border: 1px solid var(--color-danger-border);
  border-radius: var(--button-border-radius);
  color: var(--color-danger-text);
  margin-bottom: var(--spacing-lg);
}

.boats-table-container {
  background-color: var(--color-bg-white);
  border-radius: var(--card-border-radius);
  padding: var(--card-padding-desktop);
  box-shadow: var(--card-shadow);
}

.count {
  margin: 0 0 var(--spacing-lg) 0;
  color: var(--color-secondary);
  font-size: var(--font-size-base);
}

.no-request {
  color: var(--color-secondary);
}

.boat-requested-admin {
  color: var(--color-warning);
  font-weight: var(--font-weight-semibold);
}

.boat-assigned-admin {
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
  color: var(--color-warning-text);
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

.actions-cell {
  display: flex;
  gap: var(--spacing-sm);
  flex-direction: column;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-xl);
}

.page-info {
  color: var(--color-secondary);
}

/* Form styles for modal */
.boat-assignment-section {
  margin-bottom: var(--spacing-xl);
}

.boat-assignment-section h3 {
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-xl);
  color: var(--color-dark);
}

.boat-assignment-section .request-comment {
  padding: var(--spacing-lg);
  background-color: var(--color-bg-light);
  border-left: 4px solid var(--color-primary);
  margin-bottom: var(--spacing-xl);
  border-radius: var(--button-border-radius);
}

.boat-assignment-section .request-comment label {
  font-weight: var(--font-weight-semibold);
  display: block;
  margin-bottom: var(--spacing-sm);
  color: var(--color-dark);
}

.boat-assignment-section .request-comment p {
  margin: 0;
  white-space: pre-wrap;
  color: var(--color-dark);
}

.form-group {
  margin-bottom: var(--form-group-gap);
}

.form-group label {
  display: block;
  margin-bottom: var(--form-label-gap);
  font-weight: var(--font-weight-medium);
  color: var(--color-dark);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: var(--spacing-md);
  border: 1px solid var(--form-input-border-color);
  border-radius: var(--form-input-border-radius);
  font-family: inherit;
  font-size: var(--font-size-lg);
  min-height: var(--form-input-min-height);
}

.form-textarea {
  resize: vertical;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.char-count {
  display: block;
  text-align: right;
  font-size: var(--font-size-base);
  color: var(--color-secondary);
  margin-top: var(--spacing-xs);
}

.help-text {
  margin-top: var(--spacing-sm);
  font-size: var(--font-size-base);
  color: var(--color-muted);
}

.info-message {
  padding: var(--spacing-lg);
  background-color: var(--color-info-light);
  border-left: 4px solid var(--color-info);
  border-radius: var(--button-border-radius);
}

.info-message p {
  margin: 0;
  color: var(--color-info-text);
}

@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
  }
}

.boat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-xl);
  padding: var(--spacing-lg) 0;
}

.boat-card {
  background: var(--color-bg-white);
  border: var(--card-border-width) solid var(--card-border-color);
  border-radius: var(--card-border-radius);
  padding: var(--card-padding-desktop);
  transition: var(--transition-normal);
}

.boat-card:hover {
  box-shadow: var(--card-shadow-hover);
}

.boat-card.status-paid {
  border-left: 4px solid var(--color-primary);
}

.boat-card.status-complete {
  border-left: 4px solid var(--color-success);
}

.boat-card.status-incomplete {
  border-left: 4px solid var(--color-warning);
}

.boat-card.status-forfait {
  border-left: 4px solid var(--color-danger);
  background-color: var(--color-danger-light);
}

@media (max-width: 768px) {
  .boat-card {
    padding: var(--card-padding-mobile);
  }
}

.boat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
  gap: var(--spacing-lg);
}

.boat-header h3 {
  margin: 0;
  color: var(--color-dark);
  font-size: var(--font-size-xl);
  flex: 1;
}

.boat-details {
  margin-bottom: var(--spacing-lg);
}

.boat-details .detail-row {
  display: flex;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-bg-light);
  align-items: flex-start;
}

.boat-details .detail-row:last-child {
  border-bottom: none;
}

.boat-details .label {
  font-weight: var(--font-weight-medium);
  color: var(--color-muted);
  min-width: 100px;
  max-width: 100px;
  flex-shrink: 0;
  word-wrap: break-word;
  line-height: var(--line-height-normal);
}

.boat-details .detail-row span:not(.label) {
  color: var(--color-dark);
  flex: 1;
}

.team-manager-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.team-manager-info .email {
  font-size: var(--font-size-sm);
  color: var(--color-secondary);
  word-break: break-all;
  overflow-wrap: break-word;
}

.club-box {
  display: inline-block;
  max-width: 200px;
  padding: var(--spacing-xs) var(--spacing-sm);
  background-color: var(--color-bg-light);
  border: 1px solid var(--form-input-border-color);
  border-radius: var(--button-border-radius);
  font-size: var(--font-size-xs);
  line-height: var(--line-height-tight);
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
  background-color: var(--table-header-bg);
  padding: var(--spacing-md);
  border-radius: var(--button-border-radius);
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-base);
}

.assignment-comment-admin {
  background-color: var(--color-info-light);
  border-left: 4px solid var(--color-info);
  padding: var(--spacing-md);
  border-radius: var(--button-border-radius);
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-base);
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
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

/* Mobile card styles */
.card-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  gap: var(--spacing-sm);
}

.card-title {
  font-size: var(--font-size-lg);
  color: var(--color-dark);
  flex: 1;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.card-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--spacing-sm) 0;
  gap: var(--spacing-lg);
}

.card-label {
  font-weight: var(--font-weight-semibold);
  color: var(--color-secondary);
  font-size: var(--font-size-base);
  flex-shrink: 0;
}

.card-value {
  color: var(--color-dark);
  font-size: var(--font-size-base);
  text-align: right;
  word-break: break-word;
}

.card-actions {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

/* Mobile responsive styles */
@media (max-width: 768px) {
  .admin-boats {
    padding: 0;
  }

  .filter-row {
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .filter-group {
    min-width: 100%;
  }

  .filter-select,
  .filter-input {
    font-size: var(--form-input-font-size-mobile);
    min-height: var(--touch-target-min-size);
  }

  .boats-table-container {
    padding: var(--card-padding-mobile);
  }

  .actions-cell {
    flex-wrap: nowrap;
  }

  .pagination {
    flex-wrap: wrap;
    gap: var(--spacing-sm);
  }

  .page-info {
    width: 100%;
    text-align: center;
  }
}
</style>
