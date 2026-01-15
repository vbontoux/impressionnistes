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
              <span class="label">{{ $t('boat.firstRower') }}&nbsp;:</span>
              <span>{{ getFirstRowerName(boat) }}</span>
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

          <div v-if="getRaceName(boat)" class="race-name">
            <strong>{{ $t('boat.selectedRace') }}&nbsp;:</strong> {{ getRaceName(boat) }}
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

          <div class="boat-actions">
            <BaseButton 
              variant="secondary"
              size="small"
              @click="editBoat(boat)"
            >
              {{ $t('common.edit') }}
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
        <TableScrollIndicator aria-label="Boats table">
          <table class="boats-table">
            <thead>
              <tr>
                <th @click="sortBy('boat_number')">
                  {{ $t('admin.boats.boatNumber') }}
                  <span v-if="sortField === 'boat_number'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
                </th>
                <th @click="sortBy('event_type')">
                  {{ $t('boat.eventType') }}
                  <span v-if="sortField === 'event_type'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
                </th>
                <th>{{ $t('boat.boatType') }}</th>
                <th>{{ $t('boat.firstRower') }}</th>
                <th>{{ $t('boat.averageAge') }}</th>
                <th>{{ $t('boat.seats') }}</th>
                <th @click="sortBy('team_manager_name')">
                  {{ $t('admin.boats.teamManager') }}
                  <span v-if="sortField === 'team_manager_name'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
                </th>
                <th @click="sortBy('boat_club_display')">
                  {{ $t('admin.boats.club') }}
                  <span v-if="sortField === 'boat_club_display'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
                </th>
                <th>{{ $t('boat.boatRequest.status') }}</th>
                <th>{{ $t('boat.status.label') }}</th>
                <th>{{ $t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="boat in paginatedBoats" :key="boat.boat_registration_id">
                <tr :class="getRowClass(boat)">
                  <td>
                    <span v-if="boat.boat_number" class="boat-number-cell">{{ boat.boat_number }}</span>
                    <span v-else class="no-race-cell">-</span>
                  </td>
                  <td>{{ boat.event_type }}</td>
                  <td>{{ boat.boat_type }}</td>
                  <td>{{ getFirstRowerLastName(boat) }}</td>
                  <td>{{ getCrewAverageAge(boat) }}</td>
                  <td>
                    {{ getFilledSeatsCount(boat) }} / {{ boat.seats?.length || 0 }}
                    <!-- RCPM+ badge hidden - club info now shown in club name display -->
                    <!-- <span v-if="boat.is_multi_club_crew" class="multi-club-badge-small">{{ $t('boat.multiClub') }}</span> -->
                  </td>
                  <td>{{ boat.team_manager_name }}</td>
                  <td><span class="club-box">{{ boat.boat_club_display }}</span></td>
                  <td>
                    <span v-if="!boat.boat_request_enabled" class="no-request">-</span>
                    <span 
                      v-else-if="boat.assigned_boat_identifier" 
                      class="boat-assigned-admin"
                    >
                      ✓ {{ $t('boat.boatRequest.assigned') }}: {{ boat.assigned_boat_identifier }}
                    </span>
                    <span v-else class="boat-requested-admin">
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
                      @click="editBoat(boat)"
                      :title="$t('common.edit')"
                      fullWidth
                    >
                      {{ $t('common.edit') }}
                    </BaseButton>
                    <BaseButton 
                      size="small"
                      :variant="boat.forfait ? 'secondary' : 'warning'"
                      @click="toggleForfait(boat)"
                      :title="boat.forfait ? $t('admin.boats.removeForfait') : $t('admin.boats.setForfait')"
                      fullWidth
                    >
                      {{ boat.forfait ? $t('admin.boats.removeForfait') : $t('admin.boats.setForfait') }}
                    </BaseButton>
                    <BaseButton 
                      size="small"
                      variant="danger"
                      @click="deleteBoat(boat)"
                      :disabled="boat.registration_status === 'paid'"
                      :title="boat.registration_status === 'paid' ? $t('boat.cannotDeletePaid') : ''"
                      fullWidth
                    >
                      {{ $t('common.delete') }}
                    </BaseButton>
                  </td>
                </tr>
                <tr v-if="getRaceName(boat)" class="race-row" :class="getRowClass(boat)">
                  <td colspan="11" class="race-cell">
                    <span class="race-label">{{ $t('boat.selectedRace') }}&nbsp;:</span> {{ getRaceName(boat) }}
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </TableScrollIndicator>
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
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useConfirm } from '../../composables/useConfirm'
import apiClient from '../../services/apiClient'
import { useRaceStore } from '../../stores/raceStore'
import { useTableSort } from '../../composables/useTableSort'
import TableScrollIndicator from '../../components/TableScrollIndicator.vue'
import ListHeader from '../../components/shared/ListHeader.vue'
import ListFilters from '../../components/shared/ListFilters.vue'
import BaseButton from '../../components/base/BaseButton.vue'
import StatusBadge from '../../components/base/StatusBadge.vue'
import LoadingSpinner from '../../components/base/LoadingSpinner.vue'
import BaseModal from '../../components/base/BaseModal.vue'
import { formatAverageAge } from '../../utils/formatters'

export default {
  name: 'AdminBoats',
  components: {
    TableScrollIndicator,
    ListHeader,
    ListFilters,
    BaseButton,
    StatusBadge,
    LoadingSpinner,
    BaseModal
  },
  setup() {
    const router = useRouter()
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
    const filterBoatRequest = ref('')
    
    const sortField = ref('team_manager_name')
    const sortDirection = ref('asc')
    
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

      // Apply sorting
      result.sort((a, b) => {
        // Special handling for boat_number (alphanumeric sorting)
        if (sortField.value === 'boat_number') {
          const aNum = a.boat_number || ''
          const bNum = b.boat_number || ''
          
          // Empty values go to the end
          if (!aNum && !bNum) return 0
          if (!aNum) return 1
          if (!bNum) return -1
          
          // Parse boat number components: [M/SM].[display_order].[sequence]
          const parseBoatNumber = (num) => {
            const parts = num.split('.')
            if (parts.length !== 3) return { prefix: '', order: 0, seq: 0 }
            return {
              prefix: parts[0],
              order: parseInt(parts[1]) || 0,
              seq: parseInt(parts[2]) || 0
            }
          }
          
          const aParsed = parseBoatNumber(aNum)
          const bParsed = parseBoatNumber(bNum)
          
          // Sort by prefix (M before SM)
          if (aParsed.prefix !== bParsed.prefix) {
            const prefixOrder = { 'M': 1, 'SM': 2 }
            const aOrder = prefixOrder[aParsed.prefix] || 999
            const bOrder = prefixOrder[bParsed.prefix] || 999
            return sortDirection.value === 'asc' ? aOrder - bOrder : bOrder - aOrder
          }
          
          // Then by display order
          if (aParsed.order !== bParsed.order) {
            return sortDirection.value === 'asc' ? aParsed.order - bParsed.order : bParsed.order - aParsed.order
          }
          
          // Finally by sequence
          return sortDirection.value === 'asc' ? aParsed.seq - bParsed.seq : bParsed.seq - aParsed.seq
        }
        
        // Default sorting for other fields
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
      filterBoatRequest,
      sortField,
      sortDirection,
      currentPage,
      totalPages,
      viewMode,
      showCreateModal,
      showEditModal,
      editingBoat,
      teamManagers,
      filteredBoats,
      paginatedBoats,
      getFilledSeatsCount,
      getFirstRowerLastName,
      getFirstRowerName,
      getBoatStatus,
      getRowClass,
      getRaceName,
      getCrewAverageAge,
      sortBy,
      clearFilters,
      toggleForfait,
      deleteBoat,
      closeModals,
      editBoat,
      saveBoatAssignment,
      editForm,
      saving,
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

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  flex: 1;
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

.boats-table {
  width: 100%;
  border-collapse: collapse;
}

.boats-table thead {
  background-color: var(--table-header-bg);
}

.boats-table th {
  padding: var(--table-cell-padding-mobile);
  text-align: left;
  font-weight: var(--table-header-font-weight);
  color: var(--color-dark);
  border-bottom: 2px solid var(--table-border-color);
  cursor: pointer;
  user-select: none;
}

.boats-table th:hover {
  background-color: var(--color-bg-hover);
}

.boats-table td {
  padding: var(--table-cell-padding-mobile);
  border-bottom: 1px solid var(--table-border-color);
}

.boats-table tbody tr:hover {
  background-color: var(--table-hover-bg);
}

@media (min-width: 768px) {
  .boats-table th,
  .boats-table td {
    padding: var(--table-cell-padding-desktop);
  }
}

.boats-table tbody tr.row-status-complete {
  border-left: 4px solid var(--color-success);
}

.boats-table tbody tr.row-status-paid {
  border-left: 4px solid var(--color-primary);
}

.boats-table tbody tr.row-status-free {
  border-left: 4px solid var(--color-primary);
}

.boats-table tbody tr.row-status-incomplete {
  border-left: 4px solid var(--color-warning);
}

.boats-table tbody tr.row-forfait {
  border-left: 4px solid var(--color-danger);
  background-color: var(--color-danger-light);
}

.boats-table .race-row {
  background-color: var(--table-header-bg);
  border-left-width: 4px;
}

.boats-table .race-cell {
  padding: var(--spacing-sm) var(--table-cell-padding-mobile);
  font-size: var(--font-size-sm);
  font-style: italic;
  color: var(--color-dark);
}

.boats-table .race-label {
  font-weight: var(--font-weight-semibold);
  font-style: normal;
  color: var(--color-dark);
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

  .pagination {
    flex-wrap: wrap;
    gap: var(--spacing-sm);
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
</style>
