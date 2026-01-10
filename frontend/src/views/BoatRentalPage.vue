<template>
  <div class="boat-rental-view">
    <div class="header">
      <div class="header-top">
        <div>
          <h1>{{ $t('boatRental.title') }}</h1>
          <p class="subtitle">{{ $t('boatRental.subtitle') }}</p>
        </div>
        <div class="header-actions">
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
          <button @click="showCreateDialog = true" class="btn-primary btn-create">
            {{ $t('boatRental.createRequestShort') }}
          </button>
        </div>
      </div>
    </div>

    <!-- My Rental Requests Section -->
    <div class="section">
      <div class="section-header">
        <h2>{{ $t('boatRental.myRequests') }}</h2>
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
                <th>{{ $t('admin.boatInventory.boatType') }}</th>
                <th>{{ $t('boatRental.desiredWeightRange') }}</th>
                <th>{{ $t('boatRental.requestComment') }}</th>
                <th>{{ $t('boatRental.statusLabel') }}</th>
                <th>{{ $t('boatRental.createdAt') }}</th>
                <th>{{ $t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="request in myRequests" :key="request.rental_request_id">
                <td>{{ $t(`boat.types.${request.boat_type}`) }}</td>
                <td>{{ request.desired_weight_range }}</td>
                <td>
                  <span 
                    class="comment-preview" 
                    :title="request.request_comment"
                  >
                    {{ truncateComment(request.request_comment) }}
                  </span>
                </td>
                <td>
                  <span class="status-badge" :class="request.status">
                    {{ $t(`boatRental.status.${request.status}`) }}
                  </span>
                </td>
                <td>{{ formatDate(request.created_at) }}</td>
                <td>
                  <div class="action-buttons">
                    <button 
                      v-if="canCancelRequest(request)"
                      @click="showCancelDialog(request)" 
                      class="btn-danger btn-sm"
                      :disabled="cancelling"
                    >
                      {{ $t('boatRental.cancelRequest') }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Card View -->
        <div v-else class="boats-grid">
          <div
            v-for="request in myRequests"
            :key="request.rental_request_id"
            class="boat-card"
            :class="`status-${request.status}`"
          >
            <div class="boat-header">
              <h3>{{ $t(`boat.types.${request.boat_type}`) }}</h3>
              <span class="status-badge" :class="request.status">
                {{ $t(`boatRental.status.${request.status}`) }}
              </span>
            </div>

            <div class="boat-details">
              <div class="detail-row">
                <span class="label">{{ $t('boatRental.desiredWeightRange') }}:</span>
                <span>{{ request.desired_weight_range }}</span>
              </div>
              <div class="detail-row">
                <span class="label">{{ $t('boatRental.requestComment') }}:</span>
                <span class="comment-text">{{ request.request_comment }}</span>
              </div>
              <div v-if="request.created_at" class="detail-row">
                <span class="label">{{ $t('boatRental.createdAt') }}:</span>
                <span>{{ formatDate(request.created_at) }}</span>
              </div>
              <div v-if="request.assignment_details" class="detail-row assignment-details">
                <span class="label">{{ $t('boatRental.assignmentDetails') }}:</span>
                <span class="assignment-text">{{ request.assignment_details }}</span>
              </div>
              <div v-if="request.accepted_at" class="detail-row">
                <span class="label">{{ $t('boatRental.acceptedAt') }}:</span>
                <span>{{ formatDate(request.accepted_at) }}</span>
              </div>
              <div v-if="request.paid_at" class="detail-row">
                <span class="label">{{ $t('boatRental.paidAt') }}:</span>
                <span>{{ formatDate(request.paid_at) }}</span>
              </div>
              <div v-if="request.rejection_reason" class="detail-row rejection-reason">
                <span class="label">{{ $t('boatRental.rejectionReason') }}:</span>
                <span class="rejection-text">{{ request.rejection_reason }}</span>
              </div>
            </div>

            <div class="boat-actions">
              <button 
                v-if="canCancelRequest(request)"
                @click="showCancelDialog(request)" 
                class="btn-danger"
                :disabled="cancelling"
              >
                {{ $t('boatRental.cancelRequest') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Request Dialog -->
    <div v-if="showCreateDialog" class="modal-overlay" @click.self="showCreateDialog = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ $t('boatRental.createRequest') }}</h3>
        </div>
        <div class="modal-body">
          <div class="request-form">
            <div class="form-group">
              <label for="boat-type">{{ $t('boatRental.boatType') }} *</label>
              <select 
                id="boat-type"
                v-model="newRequest.boat_type" 
                class="form-control"
                :disabled="submitting"
              >
                <option value="">{{ $t('boatRental.selectBoatType') }}</option>
                <option value="skiff">{{ $t('boat.types.skiff') }}</option>
                <option value="4-">{{ $t('boat.types.4-') }}</option>
                <option value="4+">{{ $t('boat.types.4+') }}</option>
                <option value="4x-">{{ $t('boat.types.4x-') }}</option>
                <option value="4x+">{{ $t('boat.types.4x+') }}</option>
                <option value="4+yolette">{{ $t('boat.types.4+yolette') }}</option>
                <option value="4x+yolette">{{ $t('boat.types.4x+yolette') }}</option>
                <option value="8+">{{ $t('boat.types.8+') }}</option>
                <option value="8x+">{{ $t('boat.types.8x+') }}</option>
              </select>
            </div>

            <div class="form-group">
              <label for="weight-range">{{ $t('boatRental.desiredWeightRange') }} *</label>
              <input 
                id="weight-range"
                type="text" 
                v-model="newRequest.desired_weight_range"
                class="form-control"
                :placeholder="$t('boatRental.weightRangePlaceholder')"
                maxlength="50"
                :disabled="submitting"
              />
              <small class="form-hint">{{ $t('boatRental.weightRangeHint') }}</small>
            </div>

            <div class="form-group">
              <label for="request-comment">{{ $t('boatRental.requestComment') }} *</label>
              <textarea 
                id="request-comment"
                v-model="newRequest.request_comment"
                class="form-control"
                :placeholder="$t('boatRental.requestCommentPlaceholder')"
                rows="4"
                maxlength="500"
                :disabled="submitting"
              ></textarea>
              <small class="form-hint">
                {{ newRequest.request_comment.length }}/500 {{ $t('boatRental.characters') }}
              </small>
            </div>

            <div v-if="formError" class="error-message">
              {{ formError }}
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="closeCreateDialog" class="btn-secondary" :disabled="submitting">
            {{ $t('common.cancel') }}
          </button>
          <button 
            @click="submitRequest" 
            class="btn-primary"
            :disabled="!isFormValid || submitting"
          >
            {{ submitting ? $t('boatRental.submitting') : $t('boatRental.submitRequest') }}
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
          <p>{{ $t('boatRental.confirmCancelRequestMessage') }}</p>
          <div class="boat-summary">
            <div><strong>{{ $t('boatRental.boatType') }}:</strong> {{ $t(`boat.types.${selectedRequestToCancel?.boat_type}`) }}</div>
            <div><strong>{{ $t('boatRental.statusLabel') }}:</strong> {{ $t(`boatRental.status.${selectedRequestToCancel?.status}`) }}</div>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { 
  createRentalRequest, 
  getMyRentalRequests, 
  cancelRentalRequest 
} from '../services/apiClient'

export default {
  name: 'BoatRentalPage',
  setup() {
    const { t } = useI18n()
    const router = useRouter()
    
    // Reactive data
    const myRequests = ref([])
    // Load view mode from localStorage or default to 'table'
    const viewMode = ref(localStorage.getItem('rentalRequestsViewMode') || 'table')
    const requestsLoading = ref(false)
    const submitting = ref(false)
    const cancelling = ref(false)
    const formError = ref('')
    const showCreateDialog = ref(false)
    const showCancelConfirmDialog = ref(false)
    const selectedRequestToCancel = ref(null)

    // New request form data
    const newRequest = ref({
      boat_type: '',
      desired_weight_range: '',
      request_comment: ''
    })

    // Computed properties
    const isFormValid = computed(() => {
      return newRequest.value.boat_type && 
             newRequest.value.desired_weight_range.trim() && 
             newRequest.value.request_comment.trim()
    })

    // Methods
    const loadMyRequests = async () => {
      requestsLoading.value = true
      
      try {
        const response = await getMyRentalRequests()
        myRequests.value = response.data.data?.rental_requests || []
      } catch (err) {
        console.error('Failed to load my requests:', err)
        // Don't show error for requests, just log it
      } finally {
        requestsLoading.value = false
      }
    }

    const submitRequest = async () => {
      if (!isFormValid.value) return
      
      formError.value = ''
      submitting.value = true
      
      try {
        await createRentalRequest({
          boat_type: newRequest.value.boat_type,
          desired_weight_range: newRequest.value.desired_weight_range.trim(),
          request_comment: newRequest.value.request_comment.trim()
        })
        
        // Close dialog and reset form
        showCreateDialog.value = false
        newRequest.value = {
          boat_type: '',
          desired_weight_range: '',
          request_comment: ''
        }
        
        // Reload requests
        await loadMyRequests()
        
      } catch (err) {
        console.error('Failed to create rental request:', err)
        formError.value = err.response?.data?.message || 
                         err.userMessage || 
                         t('boatRental.requestError')
      } finally {
        submitting.value = false
      }
    }

    const closeCreateDialog = () => {
      showCreateDialog.value = false
      formError.value = ''
      // Don't reset form data to preserve user input if they accidentally close
    }

    const truncateComment = (comment) => {
      if (!comment) return ''
      const maxLength = 50
      if (comment.length <= maxLength) return comment
      return comment.substring(0, maxLength) + '...'
    }

    const canCancelRequest = (request) => {
      // Can cancel if status is 'pending' or 'accepted', but not 'paid', 'cancelled', or 'rejected'
      return request.status === 'pending' || request.status === 'accepted'
    }

    const showCancelDialog = (request) => {
      selectedRequestToCancel.value = request
      showCancelConfirmDialog.value = true
    }

    const confirmCancel = async () => {
      if (!selectedRequestToCancel.value) return
      
      cancelling.value = true
      
      try {
        const requestId = selectedRequestToCancel.value.rental_request_id
        console.log('Cancelling rental request with ID:', requestId)
        
        await cancelRentalRequest(requestId)
        
        showCancelConfirmDialog.value = false
        selectedRequestToCancel.value = null
        
        // Refresh requests list
        await loadMyRequests()
        
      } catch (err) {
        console.error('Failed to cancel rental request:', err)
        alert(err.response?.data?.message || 
              err.userMessage || 
              t('boatRental.cancelError'))
      } finally {
        cancelling.value = false
      }
    }

    const goToPayment = () => {
      router.push('/payment')
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString()
    }

    // Watch for view mode changes and save to localStorage
    watch(viewMode, (newMode) => {
      localStorage.setItem('rentalRequestsViewMode', newMode)
    })

    // Lifecycle
    onMounted(() => {
      loadMyRequests()
    })

    return {
      myRequests,
      viewMode,
      requestsLoading,
      submitting,
      cancelling,
      formError,
      showCreateDialog,
      showCancelConfirmDialog,
      selectedRequestToCancel,
      newRequest,
      isFormValid,
      loadMyRequests,
      submitRequest,
      closeCreateDialog,
      truncateComment,
      canCancelRequest,
      showCancelDialog,
      confirmCancel,
      goToPayment,
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

.header-top {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}

.header-top > div:first-child {
  flex: 1;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
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
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
  color: #34495e;
  font-size: 1.25rem;
}

.view-toggle {
  display: flex;
  gap: 0.25rem;
  background-color: #e9ecef;
  border-radius: 4px;
  padding: 0.25rem;
  flex-shrink: 0;
}

.btn-view {
  padding: 0.5rem 0.75rem;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 1.25rem;
  transition: all 0.2s ease;
  min-height: 44px;
  min-width: 44px;
  touch-action: manipulation;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-view:hover {
  background: #dee2e6;
}

.btn-view.active {
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Request Form Styles */
.modal-content .request-form {
  background: transparent;
  padding: 0;
  box-shadow: none;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.95rem;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px; /* Prevent iOS zoom */
  min-height: 44px;
  touch-action: manipulation;
  font-family: inherit;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-control:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

textarea.form-control {
  resize: vertical;
  min-height: 100px;
}

.form-hint {
  display: block;
  margin-top: 0.25rem;
  color: #7f8c8d;
  font-size: 0.85rem;
}

.error-message {
  background: #fdf2f2;
  color: #e74c3c;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

/* Table Styles */
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
  min-width: 600px;
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

.comment-preview {
  display: inline-block;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: help;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-sm {
  padding: 0.5rem 1rem !important;
  font-size: 0.875rem !important;
  min-height: 44px;
  min-width: 44px;
  touch-action: manipulation;
  white-space: nowrap;
}

/* Card View Styles */
.boats-grid {
  display: grid;
  grid-template-columns: 1fr;
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

.boat-card.status-pending {
  border-left: 4px solid #f39c12;
}

.boat-card.status-accepted {
  border-left: 4px solid #27ae60;
}

.boat-card.status-paid {
  border-left: 4px solid #2874a6;
}

.boat-card.status-cancelled {
  border-left: 4px solid #e74c3c;
}

.boat-card.status-rejected {
  border-left: 4px solid #c0392b;
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

.comment-text {
  color: #555;
  font-size: 0.9rem;
  white-space: pre-wrap;
}

.assignment-details {
  background: #e8f5e9;
  padding: 0.75rem;
  border-radius: 4px;
  margin-top: 0.5rem;
}

.rejection-reason {
  background: #fdf2f2;
  padding: 0.75rem;
  border-radius: 4px;
  margin-top: 0.5rem;
  border-left: 3px solid #e74c3c;
}

.assignment-text {
  color: #2c3e50;
  font-size: 0.9rem;
  white-space: pre-wrap;
  font-weight: 500;
}

.rejection-text {
  color: #c0392b;
  font-size: 0.9rem;
  white-space: pre-wrap;
  font-weight: 500;
}

.status-badge {
  padding: 0.35rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  display: inline-block;
}

.status-badge.pending {
  background-color: #ffc107;
  color: #000;
}

.status-badge.accepted {
  background-color: #28a745;
  color: white;
}

.status-badge.paid {
  background-color: #007bff;
  color: white;
  font-weight: 600;
}

.status-badge.cancelled {
  background-color: #6c757d;
  color: white;
}

.status-badge.rejected {
  background-color: #dc3545;
  color: white;
  font-weight: 600;
}

.boat-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.boat-actions button {
  width: 100%;
}

.loading, .empty-state {
  text-align: center;
  padding: 1.5rem;
  color: #7f8c8d;
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
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
  padding: 0;
}

.modal-content {
  background: white;
  border-radius: 12px 12px 0 0;
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
  flex-direction: column;
  gap: 0.75rem;
  flex-shrink: 0;
}

/* Button styles - Mobile-first */
.btn-primary, .btn-secondary, .btn-danger {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  min-height: 40px;
  font-size: 0.875rem;
  touch-action: manipulation;
  white-space: nowrap;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-create {
  padding: 0.75rem 1.5rem !important;
  font-size: 1rem !important;
  min-height: 44px !important;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-primary:active:not(:disabled) {
  background: #004085;
}

.btn-primary:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
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

/* Mobile Responsive */
@media (max-width: 767px) {
  .header-top {
    flex-direction: column;
    gap: 1rem;
  }

  .header-actions {
    justify-content: space-between;
    width: 100%;
  }

  .view-toggle {
    flex-shrink: 0;
  }

  .btn-view {
    padding: 0.75rem;
  }

  .btn-primary {
    flex-shrink: 0;
    padding: 0.75rem 1rem;
    font-size: 0.9rem;
  }
}

/* Tablet and desktop enhancements */
@media (min-width: 768px) {
  .boat-rental-view {
    padding: 2rem;
  }

  .header-top {
    flex-direction: row;
    justify-content: space-between;
    align-items: flex-start;
  }

  .header h1 {
    font-size: 2rem;
  }

  .subtitle {
    font-size: 1rem;
  }

  .header-actions {
    width: auto;
  }

  .section-header h2 {
    font-size: 1.5rem;
  }

  .btn-view {
    padding: 0.5rem 0.75rem;
  }

  .btn-primary, .btn-secondary {
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
