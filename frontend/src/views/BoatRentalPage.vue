<template>
  <div class="boat-rental-view">
    <div class="header">
      <h1>{{ $t('boatRental.title') }}</h1>
      <p class="subtitle">{{ $t('boatRental.subtitle') }}</p>
    </div>

    <!-- Available Boats Section -->
    <div class="section">
      <div class="section-header">
        <h2>{{ $t('boatRental.availableBoats') }}</h2>
        <div class="header-actions">
          <select v-model="boatTypeFilter" class="filter-select">
            <option value="">{{ $t('boatRental.allTypes') }}</option>
            <option value="skiff">{{ $t('boat.types.skiff') }}</option>
            <option value="4-">{{ $t('boat.types.fourWithoutCox') }}</option>
            <option value="4+">{{ $t('boat.types.fourWithCox') }}</option>
            <option value="4x-">{{ $t('boat.types.quadWithoutCox') }}</option>
            <option value="4x+">{{ $t('boat.types.quadWithCox') }}</option>
            <option value="8+">{{ $t('boat.types.eightWithCox') }}</option>
            <option value="8x+">{{ $t('boat.types.octaWithCox') }}</option>
          </select>
          <div class="view-toggle">
            <button 
              @click="viewMode = 'table'" 
              :class="{ active: viewMode === 'table' }"
              class="btn-view"
              :title="$t('common.tableView')"
            >
              ☰
            </button>
            <button 
              @click="viewMode = 'cards'" 
              :class="{ active: viewMode === 'cards' }"
              class="btn-view"
              :title="$t('common.cardView')"
            >
              ⊞
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading">
        {{ $t('common.loading') }}
      </div>

      <!-- Error State -->
      <div v-if="error" class="error-message">
        {{ error }}
        <button @click="loadAvailableBoats" class="btn-secondary">
          {{ $t('common.retry') }}
        </button>
      </div>

      <!-- Available Boats List -->
      <div v-if="!loading && !error">
        <div v-if="filteredAvailableBoats.length === 0" class="empty-state">
          <p>{{ $t('boatRental.noAvailableBoats') }}</p>
        </div>

        <!-- Table View -->
        <div v-else-if="viewMode === 'table'" class="boats-table">
          <table>
            <thead>
              <tr>
                <th>{{ $t('admin.boatInventory.boatName') }}</th>
                <th>{{ $t('admin.boatInventory.boatType') }}</th>
                <th>{{ $t('boatRental.weightCapacity') }}</th>
                <th>{{ $t('boatRental.status') }}</th>
                <th>{{ $t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="boat in filteredAvailableBoats" :key="boat.rental_boat_id">
                <td class="boat-name">{{ boat.boat_name }}</td>
                <td>{{ $t(`boat.types.${boat.boat_type}`) }}</td>
                <td>{{ boat.rower_weight_range || $t('boatRental.notSpecified') }}</td>
                <td>
                  <span class="status-badge available">{{ $t('boatRental.statusAvailable') }}</span>
                </td>
                <td>
                  <button 
                    @click="requestBoat(boat)" 
                    class="btn-primary btn-sm"
                    :disabled="requesting"
                  >
                    {{ requesting ? $t('boatRental.requesting') : $t('boatRental.requestBoat') }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Card View -->
        <div v-else class="boats-grid">
          <div
            v-for="boat in filteredAvailableBoats"
            :key="boat.rental_boat_id"
            class="boat-card available"
          >
            <div class="boat-header">
              <h3>{{ boat.boat_name }}</h3>
              <span class="boat-type">{{ $t(`boat.types.${boat.boat_type}`) }}</span>
            </div>

            <div class="boat-details">
              <div class="detail-row">
                <span class="label">{{ $t('boatRental.weightCapacity') }}:</span>
                <span>{{ boat.rower_weight_range || $t('boatRental.notSpecified') }}</span>
              </div>
              <div class="detail-row">
                <span class="label">{{ $t('boatRental.status') }}:</span>
                <span class="status-badge available">{{ $t('boatRental.statusAvailable') }}</span>
              </div>
            </div>

            <div class="boat-actions">
              <button 
                @click="requestBoat(boat)" 
                class="btn-primary"
                :disabled="requesting"
              >
                {{ requesting ? $t('boatRental.requesting') : $t('boatRental.requestBoat') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- My Rental Requests Section -->
    <div class="section">
      <div class="section-header">
        <h2>{{ $t('boatRental.myRequests') }}</h2>
        <div class="header-actions">
          <button @click="loadMyRequests" class="btn-secondary">
            {{ $t('boatRental.refresh') }}
          </button>
          <div class="view-toggle">
            <button 
              @click="viewMode = 'table'" 
              :class="{ active: viewMode === 'table' }"
              class="btn-view"
              :title="$t('common.tableView')"
            >
              ☰
            </button>
            <button 
              @click="viewMode = 'cards'" 
              :class="{ active: viewMode === 'cards' }"
              class="btn-view"
              :title="$t('common.cardView')"
            >
              ⊞
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State for Requests -->
      <div v-if="requestsLoading" class="loading">
        {{ $t('common.loading') }}
      </div>

      <!-- My Requests List -->
      <div v-if="!requestsLoading">
        <div v-if="myRequests.length === 0" class="empty-state">
          <p>{{ $t('boatRental.noRequests') }}</p>
        </div>

        <!-- Table View -->
        <div v-else-if="viewMode === 'table'" class="boats-table">
          <table>
            <thead>
              <tr>
                <th>{{ $t('admin.boatInventory.boatName') }}</th>
                <th>{{ $t('admin.boatInventory.boatType') }}</th>
                <th>{{ $t('boatRental.weightCapacity') }}</th>
                <th>{{ $t('boatRental.status') }}</th>
                <th>{{ $t('boatRental.requestedAt') }}</th>
                <th>{{ $t('boatRental.confirmedAt') }}</th>
                <th>{{ $t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="request in myRequests" :key="request.rental_boat_id">
                <td class="boat-name">{{ request.boat_name }}</td>
                <td>{{ $t(`boat.types.${request.boat_type}`) }}</td>
                <td>{{ request.rower_weight_range || $t('boatRental.notSpecified') }}</td>
                <td>
                  <span class="status-badge" :class="request.status">
                    {{ $t(`boatRental.status.${request.status}`) }}
                  </span>
                </td>
                <td>{{ request.requested_at ? formatDate(request.requested_at) : '-' }}</td>
                <td>{{ request.confirmed_at ? formatDate(request.confirmed_at) : '-' }}</td>
                <td>
                  <button 
                    v-if="canCancelRequest(request)"
                    @click="showCancelDialog(request)" 
                    class="btn-danger btn-sm"
                    :disabled="cancelling"
                  >
                    {{ $t('boatRental.cancelRequest') }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Card View -->
        <div v-else class="boats-grid">
          <div
            v-for="request in myRequests"
            :key="request.rental_boat_id"
            class="boat-card"
            :class="`status-${request.status}`"
          >
            <div class="boat-header">
              <h3>{{ request.boat_name }}</h3>
              <span class="boat-type">{{ $t(`boat.types.${request.boat_type}`) }}</span>
            </div>

            <div class="boat-details">
              <div class="detail-row">
                <span class="label">{{ $t('boatRental.weightCapacity') }}:</span>
                <span>{{ request.rower_weight_range || $t('boatRental.notSpecified') }}</span>
              </div>
              <div class="detail-row">
                <span class="label">{{ $t('boatRental.status') }}:</span>
                <span class="status-badge" :class="request.status">
                  {{ $t(`boatRental.status.${request.status}`) }}
                </span>
              </div>
              <div v-if="request.requested_at" class="detail-row">
                <span class="label">{{ $t('boatRental.requestedAt') }}:</span>
                <span>{{ formatDate(request.requested_at) }}</span>
              </div>
              <div v-if="request.confirmed_at" class="detail-row">
                <span class="label">{{ $t('boatRental.confirmedAt') }}:</span>
                <span>{{ formatDate(request.confirmed_at) }}</span>
              </div>
            </div>

            <div class="boat-actions" v-if="canCancelRequest(request)">
              <button 
                @click="showCancelDialog(request)" 
                class="btn-danger"
                :disabled="cancelling"
              >
                {{ $t('boatRental.cancelRequest') }}
              </button>
            </div>

            <div class="status-indicator">
              <div v-if="request.status === 'requested'" class="status-icon pending">⏳</div>
              <div v-else-if="request.status === 'confirmed'" class="status-icon confirmed">✅</div>
              <div v-else-if="request.status === 'available'" class="status-icon rejected">❌</div>
              <div v-else-if="request.status === 'paid'" class="status-icon paid">💳</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Request Confirmation Dialog -->
    <div v-if="showConfirmDialog" class="modal-overlay" @click.self="showConfirmDialog = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ $t('boatRental.confirmRequest') }}</h3>
        </div>
        <div class="modal-body">
          <p>{{ $t('boatRental.confirmRequestMessage', { boatName: selectedBoat?.boat_name }) }}</p>
          <div class="boat-summary">
            <div><strong>{{ $t('boatRental.boatType') }}:</strong> {{ $t(`boat.types.${selectedBoat?.boat_type}`) }}</div>
            <div><strong>{{ $t('boatRental.weightCapacity') }}:</strong> {{ selectedBoat?.rower_weight_range || $t('boatRental.notSpecified') }}</div>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="showConfirmDialog = false" class="btn-secondary">
            {{ $t('common.cancel') }}
          </button>
          <button @click="confirmRequest" class="btn-primary" :disabled="requesting">
            {{ requesting ? $t('boatRental.requesting') : $t('boatRental.confirmRequestButton') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Cancel Confirmation Dialog -->
    <div v-if="showCancelConfirmDialog" class="modal-overlay" @click.self="showCancelConfirmDialog = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ $t('boatRental.confirmCancel') }}</h3>
        </div>
        <div class="modal-body">
          <p>{{ $t('boatRental.confirmCancelMessage', { boatName: selectedBoatToCancel?.boat_name }) }}</p>
          <div class="boat-summary">
            <div><strong>{{ $t('boatRental.boatType') }}:</strong> {{ $t(`boat.types.${selectedBoatToCancel?.boat_type}`) }}</div>
            <div><strong>{{ $t('boatRental.status') }}:</strong> {{ $t(`boatRental.status.${selectedBoatToCancel?.status}`) }}</div>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="showCancelConfirmDialog = false" class="btn-secondary">
            {{ $t('common.cancel') }}
          </button>
          <button @click="confirmCancel" class="btn-danger" :disabled="cancelling">
            {{ cancelling ? $t('boatRental.cancelling') : $t('boatRental.confirmCancel') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import apiClient from '../services/apiClient'

export default {
  name: 'BoatRentalPage',
  setup() {
    const { t } = useI18n()
    
    // Reactive data
    const availableBoats = ref([])
    const myRequests = ref([])
    const boatTypeFilter = ref('')
    const viewMode = ref('table') // 'table' or 'cards'
    const loading = ref(false)
    const requestsLoading = ref(false)
    const requesting = ref(false)
    const cancelling = ref(false)
    const error = ref('')
    const showConfirmDialog = ref(false)
    const showCancelConfirmDialog = ref(false)
    const selectedBoat = ref(null)
    const selectedBoatToCancel = ref(null)

    // Computed properties
    const filteredAvailableBoats = computed(() => {
      if (!boatTypeFilter.value) {
        return availableBoats.value
      }
      return availableBoats.value.filter(boat => boat.boat_type === boatTypeFilter.value)
    })

    // Methods
    const loadAvailableBoats = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await apiClient.get('/rental/boats')
        availableBoats.value = response.data.data?.rental_boats || []
      } catch (err) {
        console.error('Failed to load available boats:', err)
        error.value = err.response?.data?.message || t('boatRental.loadError')
      } finally {
        loading.value = false
      }
    }

    const loadMyRequests = async () => {
      requestsLoading.value = true
      
      try {
        const response = await apiClient.get('/rental/my-requests')
        myRequests.value = response.data.data?.rental_requests || []
      } catch (err) {
        console.error('Failed to load my requests:', err)
        // Don't show error for requests, just log it
      } finally {
        requestsLoading.value = false
      }
    }

    const requestBoat = (boat) => {
      selectedBoat.value = boat
      showConfirmDialog.value = true
    }

    const confirmRequest = async () => {
      if (!selectedBoat.value) return
      
      requesting.value = true
      
      try {
        await apiClient.post('/rental/request', {
          rental_boat_id: selectedBoat.value.rental_boat_id
        })
        
        showConfirmDialog.value = false
        selectedBoat.value = null
        
        // Refresh both lists
        await Promise.all([loadAvailableBoats(), loadMyRequests()])
        
      } catch (err) {
        console.error('Failed to request boat:', err)
        alert(err.response?.data?.message || t('boatRental.requestError'))
      } finally {
        requesting.value = false
      }
    }

    const canCancelRequest = (request) => {
      // Can cancel if status is 'requested' or 'confirmed', but not 'paid'
      return request.status === 'requested' || request.status === 'confirmed'
    }

    const showCancelDialog = (request) => {
      selectedBoatToCancel.value = request
      showCancelConfirmDialog.value = true
    }

    const confirmCancel = async () => {
      if (!selectedBoatToCancel.value) return
      
      cancelling.value = true
      
      try {
        const rentalId = selectedBoatToCancel.value.rental_boat_id
        console.log('Cancelling rental with ID:', rentalId)
        
        await apiClient.delete(`/rental/cancel/${encodeURIComponent(rentalId)}`)
        
        showCancelConfirmDialog.value = false
        selectedBoatToCancel.value = null
        
        // Refresh both lists
        await Promise.all([loadAvailableBoats(), loadMyRequests()])
        
      } catch (err) {
        console.error('Failed to cancel rental request:', err)
        alert(err.response?.data?.message || t('boatRental.cancelError'))
      } finally {
        cancelling.value = false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString()
    }

    // Lifecycle
    onMounted(() => {
      loadAvailableBoats()
      loadMyRequests()
    })

    return {
      availableBoats,
      myRequests,
      boatTypeFilter,
      viewMode,
      loading,
      requestsLoading,
      requesting,
      cancelling,
      error,
      showConfirmDialog,
      showCancelConfirmDialog,
      selectedBoat,
      selectedBoatToCancel,
      filteredAvailableBoats,
      loadAvailableBoats,
      loadMyRequests,
      requestBoat,
      confirmRequest,
      canCancelRequest,
      showCancelDialog,
      confirmCancel,
      formatDate
    }
  }
}
</script>

<style scoped>
/* Mobile-first base styles */
.boat-rental-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.header {
  margin-bottom: 1.5rem;
}

.header h1 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

.subtitle {
  color: #7f8c8d;
  margin: 0;
  font-size: 0.9rem;
}

.section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
  color: #34495e;
  font-size: 1.25rem;
}

.header-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
  align-items: stretch;
}

.view-toggle {
  display: flex;
  gap: 0.25rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  width: 100%;
  flex-shrink: 0;
}

.btn-view {
  flex: 1;
  padding: 0.75rem;
  border: none;
  background: white;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.2s ease;
  min-height: 44px;
  min-width: 44px;
  touch-action: manipulation;
}

.btn-view:hover {
  background: #f8f9fa;
}

.btn-view.active {
  background: #3498db;
  color: white;
}

.filter-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  font-size: 16px; /* Prevent iOS zoom */
  min-height: 44px;
  touch-action: manipulation;
}

.boats-table {
  overflow-x: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  -webkit-overflow-scrolling: touch;
  touch-action: pan-x;
}

.boats-table table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px; /* Ensure horizontal scroll on mobile */
}

.boats-table th {
  background: #f8f9fa;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #e1e8ed;
  font-size: 0.9rem;
  white-space: nowrap;
}

.boats-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #e1e8ed;
  font-size: 0.9rem;
}

.boats-table tr:hover {
  background: #f8f9fa;
}

.boats-table .boat-name {
  font-weight: 500;
  color: #2c3e50;
}

.btn-sm {
  padding: 0.5rem 1rem !important;
  font-size: 0.875rem !important;
  min-height: 44px;
  min-width: 44px;
  touch-action: manipulation;
  white-space: nowrap;
}

.boats-grid {
  display: grid;
  grid-template-columns: 1fr; /* Single column on mobile */
  gap: 1rem;
}

.boat-card {
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 1rem;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.2s ease;
  position: relative;
}

.boat-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.boat-card.available {
  border-left: 4px solid #27ae60;
}

.boat-card.status-requested {
  border-left: 4px solid #f39c12;
}

.boat-card.status-confirmed {
  border-left: 4px solid #27ae60;
}

.boat-card.status-available {
  border-left: 4px solid #e74c3c;
}

.boat-card.status-paid {
  border-left: 4px solid #2874a6;
}

.boat-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.boat-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.boat-type {
  font-size: 0.85rem;
  color: #7f8c8d;
  font-weight: 500;
}

.boat-details {
  margin-bottom: 1rem;
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
}

.label {
  font-weight: 500;
  color: #34495e;
  font-size: 0.85rem;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.available {
  background: #d5f4e6;
  color: #27ae60;
}

.status-badge.requested {
  background: #fef9e7;
  color: #f39c12;
}

.status-badge.confirmed {
  background: #d5f4e6;
  color: #27ae60;
}

.status-badge.paid {
  background: #d6eaf8;
  color: #2874a6;
}

.boat-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.boat-actions button {
  width: 100%;
}

.status-indicator {
  position: absolute;
  top: 1rem;
  right: 1rem;
}

.status-icon {
  font-size: 1.5rem;
}

.loading, .empty-state {
  text-align: center;
  padding: 1.5rem;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.error-message {
  background: #fdf2f2;
  color: #e74c3c;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

/* Modal styles - Mobile-first */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end; /* Slide from bottom on mobile */
  justify-content: center;
  z-index: 1000;
  padding: 0;
}

.modal-content {
  background: white;
  border-radius: 12px 12px 0 0; /* Rounded top corners only on mobile */
  padding: 1.5rem;
  width: 100%;
  max-width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.modal-header h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.modal-body {
  margin-bottom: 1.5rem;
  flex: 1;
  overflow-y: auto;
  font-size: 0.95rem;
}

.boat-summary {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.boat-summary div {
  margin-bottom: 0.5rem;
}

.modal-actions {
  display: flex;
  flex-direction: column; /* Stack vertically on mobile */
  gap: 0.75rem;
  flex-shrink: 0;
}

/* Button styles - Mobile-first */
.btn-primary, .btn-secondary, .btn-danger {
  width: 100%; /* Full-width on mobile */
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  min-height: 44px;
  font-size: 16px; /* Prevent iOS zoom */
  touch-action: manipulation;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-primary:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.btn-secondary {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-secondary:hover {
  background: #d5dbdb;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c0392b;
}

.btn-danger:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

/* Tablet and desktop enhancements */
@media (min-width: 768px) {
  .boat-rental-view {
    padding: 2rem;
  }

  .header h1 {
    font-size: 2rem;
  }

  .subtitle {
    font-size: 1rem;
  }

  .section-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }

  .section-header h2 {
    font-size: 1.5rem;
  }

  .header-actions {
    flex-direction: row;
    align-items: center;
    width: auto;
  }

  .filter-select {
    width: auto;
    min-width: 200px;
  }

  .view-toggle {
    width: auto;
  }

  .btn-view {
    flex: 0 0 auto;
    padding: 0.5rem 1rem;
  }

  .boats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .boat-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }

  .detail-row {
    flex-direction: row;
    justify-content: space-between;
  }

  .boat-actions {
    flex-direction: row;
  }

  .boat-actions button {
    width: auto;
  }

  .modal-overlay {
    align-items: center;
    padding: 1rem;
  }

  .modal-content {
    border-radius: 12px;
    width: 90%;
    max-width: 600px;
    padding: 2rem;
  }

  .modal-actions {
    flex-direction: row;
    justify-content: flex-end;
  }

  .modal-actions .btn-primary,
  .modal-actions .btn-secondary,
  .modal-actions .btn-danger {
    width: auto;
    min-width: 120px;
  }

  .btn-primary:hover:not(:disabled),
  .btn-secondary:hover,
  .btn-danger:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }

  .boats-table {
    overflow-x: visible;
  }

  .boats-table table {
    min-width: auto;
  }
}

@media (min-width: 1024px) {
  .boats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>