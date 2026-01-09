<template>
  <div class="admin-rental-requests">
    <div class="page-header">
      <router-link to="/admin" class="back-link">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        {{ $t('common.back') }}
      </router-link>
      <ListHeader
        :title="$t('admin.boatInventory.title')"
        :subtitle="$t('admin.boatInventory.subtitle')"
        v-model:viewMode="viewMode"
      />
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="loadRequests" class="btn-secondary">{{ $t('common.retry') }}</button>
    </div>

    <div v-else>
      <!-- Filters -->
      <ListFilters
        v-model:searchQuery="searchQuery"
        :searchPlaceholder="$t('admin.boatInventory.searchPlaceholder')"
        @clear="clearFilters"
      >
        <template #filters>
          <div class="filter-group">
            <label>{{ $t('admin.boatInventory.filterByStatus') }}&nbsp;:</label>
            <select v-model="filterStatus" class="filter-select">
              <option value="">{{ $t('admin.boatInventory.allStatuses') }}</option>
              <option value="pending">{{ $t('boatRental.status.pending') }}</option>
              <option value="accepted">{{ $t('boatRental.status.accepted') }}</option>
              <option value="paid">{{ $t('boatRental.status.paid') }}</option>
              <option value="cancelled">{{ $t('boatRental.status.cancelled') }}</option>
              <option value="rejected">{{ $t('boatRental.status.rejected') }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>{{ $t('admin.boatInventory.filterByType') }}&nbsp;:</label>
            <select v-model="filterBoatType" class="filter-select">
              <option value="">{{ $t('admin.boatInventory.allTypes') }}</option>
              <option v-for="type in boatTypes" :key="type" :value="type">{{ type }}</option>
            </select>
          </div>

          <div class="filter-stats">
            {{ $t('admin.boatInventory.showing') }}: {{ filteredRequests.length }} {{ $t('admin.boatInventory.boats') }}
          </div>
        </template>
      </ListFilters>

      <!-- Card View -->
      <div v-if="viewMode === 'cards'" class="requests-grid">
        <div v-if="filteredRequests.length === 0" class="empty-state">
          {{ $t('admin.boatInventory.noBoats') }}
        </div>
        <div
          v-for="request in filteredRequests"
          :key="request.rental_request_id"
          class="request-card"
          :class="`status-${request.status}`"
        >
          <div class="request-header">
            <h3>{{ request.boat_type }}</h3>
            <span :class="['status-badge', `status-${request.status}`]">
              {{ $t(`boatRental.status.${request.status}`) }}
            </span>
          </div>

          <div class="request-details">
            <div class="detail-row">
              <span class="label">{{ $t('boatRental.desiredWeightRange') }}:</span>
              <span>{{ request.desired_weight_range }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('admin.boatInventory.requester') }}:</span>
              <span>{{ request.requester_email }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('boatRental.requestComment') }}:</span>
              <span class="comment-text">{{ request.request_comment }}</span>
            </div>
            <div v-if="request.assignment_details" class="detail-row">
              <span class="label">{{ $t('boatRental.assignmentDetails') }}:</span>
              <span class="assignment-text">{{ request.assignment_details }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('boatRental.createdAt') }}:</span>
              <span>{{ formatDate(request.created_at) }}</span>
            </div>
          </div>

          <div class="request-actions">
            <button
              v-if="request.status === 'pending'"
              @click="openAcceptModal(request)"
              class="btn-table btn-accept"
            >
              {{ $t('admin.boatInventory.acceptRequest') }}
            </button>
            <button
              v-if="request.status === 'accepted'"
              @click="openEditAssignmentModal(request)"
              class="btn-table btn-edit"
            >
              {{ $t('admin.boatInventory.editAssignment') }}
            </button>
            <button
              v-if="request.status === 'accepted'"
              @click="resetRequest(request)"
              class="btn-table btn-warning"
            >
              {{ $t('admin.boatInventory.resetRequest') }}
            </button>
            <button
              v-if="request.status === 'pending' || request.status === 'accepted'"
              @click="openRejectModal(request)"
              class="btn-table btn-reject"
            >
              {{ $t('admin.boatInventory.rejectRequest') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Table View -->
      <div v-else class="requests-table-container">
        <table class="requests-table">
          <thead>
            <tr>
              <th>{{ $t('admin.boatInventory.boatType') }}</th>
              <th>{{ $t('boatRental.desiredWeightRange') }}</th>
              <th>{{ $t('admin.boatInventory.requester') }}</th>
              <th>{{ $t('admin.boatInventory.statusLabel') }}</th>
              <th>{{ $t('boatRental.createdAt') }}</th>
              <th>{{ $t('admin.boatInventory.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredRequests.length === 0">
              <td colspan="6" class="no-data">{{ $t('admin.boatInventory.noBoats') }}</td>
            </tr>
            <tr v-for="request in filteredRequests" :key="request.rental_request_id" class="request-row" :class="`status-${request.status}`">
              <td>
                <span :class="['boat-type-badge', `boat-type-${getBoatCategory(request.boat_type)}`]">
                  {{ request.boat_type }}
                </span>
              </td>
              <td>{{ request.desired_weight_range }}</td>
              <td>{{ request.requester_email }}</td>
              <td>
                <span :class="['status-badge', `status-${request.status}`]">
                  {{ $t(`boatRental.status.${request.status}`) }}
                </span>
              </td>
              <td>{{ formatDate(request.created_at) }}</td>
              <td>
                <div class="action-buttons">
                  <button
                    v-if="request.status === 'pending'"
                    @click="openAcceptModal(request)"
                    class="btn-table btn-accept"
                  >
                    {{ $t('admin.boatInventory.acceptRequest') }}
                  </button>
                  <button
                    v-if="request.status === 'accepted'"
                    @click="openEditAssignmentModal(request)"
                    class="btn-table btn-edit"
                  >
                    {{ $t('common.edit') }}
                  </button>
                  <button
                    v-if="request.status === 'accepted'"
                    @click="resetRequest(request)"
                    class="btn-table btn-warning"
                  >
                    {{ $t('admin.boatInventory.resetRequestShort') }}
                  </button>
                  <button
                    v-if="request.status === 'pending' || request.status === 'accepted'"
                    @click="openRejectModal(request)"
                    class="btn-table btn-reject"
                  >
                    {{ $t('admin.boatInventory.rejectRequest') }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Accept Modal -->
    <div v-if="showAcceptModal" class="modal-overlay" @click.self="closeAcceptModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ $t('admin.boatInventory.acceptRequestTitle') }}</h2>
          <button @click="closeAcceptModal" class="modal-close">✕</button>
        </div>

        <form @submit.prevent="acceptRequest" class="modal-form">
          <div class="request-summary">
            <p><strong>{{ $t('admin.boatInventory.boatType') }}:</strong> {{ selectedRequest?.boat_type }}</p>
            <p><strong>{{ $t('boatRental.desiredWeightRange') }}:</strong> {{ selectedRequest?.desired_weight_range }}</p>
            <p><strong>{{ $t('admin.boatInventory.requester') }}:</strong> {{ selectedRequest?.requester_email }}</p>
            <p><strong>{{ $t('boatRental.requestComment') }}:</strong> {{ selectedRequest?.request_comment }}</p>
          </div>

          <div class="form-group">
            <label for="assignment_details">{{ $t('admin.boatInventory.assignmentDetailsLabel') }} *</label>
            <textarea
              id="assignment_details"
              v-model="assignmentForm.assignment_details"
              class="form-control"
              :class="{ 'error': assignmentError }"
              :placeholder="$t('admin.boatInventory.assignmentDetailsPlaceholder')"
              rows="5"
              required
            ></textarea>
            <small class="form-help">{{ $t('admin.boatInventory.assignmentDetailsHint') }}</small>
            <span v-if="assignmentError" class="error-text">{{ assignmentError }}</span>
          </div>

          <div v-if="acceptError" class="error-message">
            {{ acceptError }}
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeAcceptModal" class="btn-secondary" :disabled="accepting">
              {{ $t('common.cancel') }}
            </button>
            <button type="submit" class="btn-primary" :disabled="accepting">
              {{ accepting ? $t('admin.boatInventory.accepting') : $t('admin.boatInventory.acceptButton') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Assignment Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ $t('admin.boatInventory.editAssignmentTitle') }}</h2>
          <button @click="closeEditModal" class="modal-close">✕</button>
        </div>

        <form @submit.prevent="updateAssignment" class="modal-form">
          <div class="form-group">
            <label for="edit_assignment_details">{{ $t('admin.boatInventory.assignmentDetailsLabel') }} *</label>
            <textarea
              id="edit_assignment_details"
              v-model="assignmentForm.assignment_details"
              class="form-control"
              :class="{ 'error': assignmentError }"
              :placeholder="$t('admin.boatInventory.assignmentDetailsPlaceholder')"
              rows="5"
              required
            ></textarea>
            <small class="form-help">{{ $t('admin.boatInventory.assignmentDetailsHint') }}</small>
            <span v-if="assignmentError" class="error-text">{{ assignmentError }}</span>
          </div>

          <div v-if="editError" class="error-message">
            {{ editError }}
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeEditModal" class="btn-secondary" :disabled="editing">
              {{ $t('common.cancel') }}
            </button>
            <button type="submit" class="btn-primary" :disabled="editing">
              {{ editing ? $t('common.saving') : $t('common.save') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Reject Modal -->
    <div v-if="showRejectModal" class="modal-overlay" @click.self="closeRejectModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ $t('admin.boatInventory.rejectRequestTitle') }}</h2>
          <button @click="closeRejectModal" class="modal-close">✕</button>
        </div>

        <form @submit.prevent="rejectRequest" class="modal-form">
          <p>{{ $t('admin.boatInventory.rejectRequestMessage') }}</p>

          <div class="form-group">
            <label for="rejection_reason">{{ $t('admin.boatInventory.rejectionReasonLabel') }}</label>
            <textarea
              id="rejection_reason"
              v-model="rejectForm.rejection_reason"
              class="form-control"
              :placeholder="$t('admin.boatInventory.rejectionReasonPlaceholder')"
              rows="3"
            ></textarea>
          </div>

          <div v-if="rejectError" class="error-message">
            {{ rejectError }}
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeRejectModal" class="btn-secondary" :disabled="rejecting">
              {{ $t('common.cancel') }}
            </button>
            <button type="submit" class="btn-danger" :disabled="rejecting">
              {{ rejecting ? $t('admin.boatInventory.rejecting') : $t('admin.boatInventory.rejectButton') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import apiClient from '../../services/apiClient';
import ListHeader from '../../components/shared/ListHeader.vue';
import ListFilters from '../../components/shared/ListFilters.vue';

const { t } = useI18n();

const loading = ref(true);
const error = ref(null);
const requests = ref([]);
const viewMode = ref(localStorage.getItem('adminRentalRequestsViewMode') || 'table');
const searchQuery = ref('');

const boatTypes = ['skiff', '4-', '4+', '4x-', '4x+', '8+', '8x+'];

// Filters
const filterStatus = ref('');
const filterBoatType = ref('');

// Modals
const showAcceptModal = ref(false);
const showEditModal = ref(false);
const showRejectModal = ref(false);
const selectedRequest = ref(null);

// Form states
const accepting = ref(false);
const editing = ref(false);
const rejecting = ref(false);
const acceptError = ref(null);
const editError = ref(null);
const rejectError = ref(null);
const assignmentError = ref(null);

const assignmentForm = ref({
  assignment_details: ''
});

const rejectForm = ref({
  rejection_reason: ''
});

const filteredRequests = computed(() => {
  let result = requests.value;

  // Apply search filter
  if (searchQuery.value) {
    const search = searchQuery.value.toLowerCase();
    result = result.filter(request =>
      request.boat_type?.toLowerCase().includes(search) ||
      request.requester_email?.toLowerCase().includes(search) ||
      request.desired_weight_range?.toLowerCase().includes(search) ||
      request.request_comment?.toLowerCase().includes(search)
    );
  }

  if (filterStatus.value) {
    result = result.filter(r => r.status === filterStatus.value);
  }

  if (filterBoatType.value) {
    result = result.filter(r => r.boat_type === filterBoatType.value);
  }

  return result;
});

const getBoatCategory = (boatType) => {
  if (boatType === 'skiff') return 'skiff';
  if (boatType.startsWith('4')) return 'four';
  if (boatType.startsWith('8')) return 'eight';
  return 'skiff';
};

const formatDate = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const loadRequests = async () => {
  loading.value = true;
  error.value = null;

  try {
    const response = await apiClient.get('/admin/rental-requests');
    requests.value = response.data.data.rental_requests || [];
  } catch (err) {
    console.error('Failed to load rental requests:', err);
    error.value = t('admin.boatInventory.loadError');
  } finally {
    loading.value = false;
  }
};

const clearFilters = () => {
  filterStatus.value = '';
  filterBoatType.value = '';
  searchQuery.value = '';
};

// Accept request
const openAcceptModal = (request) => {
  selectedRequest.value = request;
  assignmentForm.value.assignment_details = '';
  assignmentError.value = null;
  acceptError.value = null;
  showAcceptModal.value = true;
};

const closeAcceptModal = () => {
  showAcceptModal.value = false;
  selectedRequest.value = null;
  assignmentForm.value.assignment_details = '';
  assignmentError.value = null;
  acceptError.value = null;
};

const acceptRequest = async () => {
  assignmentError.value = null;
  acceptError.value = null;

  if (!assignmentForm.value.assignment_details || !assignmentForm.value.assignment_details.trim()) {
    assignmentError.value = t('admin.boatInventory.errors.assignmentDetailsRequired');
    return;
  }

  if (assignmentForm.value.assignment_details.length > 1000) {
    assignmentError.value = t('admin.boatInventory.errors.assignmentDetailsTooLong');
    return;
  }

  accepting.value = true;

  try {
    const requestId = selectedRequest.value.rental_request_id;
    const response = await apiClient.put(
      `/admin/rental-requests/${encodeURIComponent(requestId)}/accept`,
      { assignment_details: assignmentForm.value.assignment_details }
    );

    // Update local request
    const index = requests.value.findIndex(r => r.rental_request_id === requestId);
    if (index !== -1) {
      requests.value[index] = response.data.data;
    }

    closeAcceptModal();
  } catch (err) {
    console.error('Failed to accept request:', err);
    acceptError.value = err.response?.data?.error?.message || 'Failed to accept request';
  } finally {
    accepting.value = false;
  }
};

// Edit assignment
const openEditAssignmentModal = (request) => {
  selectedRequest.value = request;
  assignmentForm.value.assignment_details = request.assignment_details || '';
  assignmentError.value = null;
  editError.value = null;
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
  selectedRequest.value = null;
  assignmentForm.value.assignment_details = '';
  assignmentError.value = null;
  editError.value = null;
};

const updateAssignment = async () => {
  assignmentError.value = null;
  editError.value = null;

  if (!assignmentForm.value.assignment_details || !assignmentForm.value.assignment_details.trim()) {
    assignmentError.value = t('admin.boatInventory.errors.assignmentDetailsRequired');
    return;
  }

  if (assignmentForm.value.assignment_details.length > 1000) {
    assignmentError.value = t('admin.boatInventory.errors.assignmentDetailsTooLong');
    return;
  }

  editing.value = true;

  try {
    const requestId = selectedRequest.value.rental_request_id;
    const response = await apiClient.put(
      `/admin/rental-requests/${encodeURIComponent(requestId)}/assignment`,
      { assignment_details: assignmentForm.value.assignment_details }
    );

    // Update local request
    const index = requests.value.findIndex(r => r.rental_request_id === requestId);
    if (index !== -1) {
      requests.value[index].assignment_details = response.data.data.assignment_details;
    }

    closeEditModal();
  } catch (err) {
    console.error('Failed to update assignment:', err);
    editError.value = err.response?.data?.error?.message || 'Failed to update assignment';
  } finally {
    editing.value = false;
  }
};

// Reject request
const openRejectModal = (request) => {
  selectedRequest.value = request;
  rejectForm.value.rejection_reason = '';
  rejectError.value = null;
  showRejectModal.value = true;
};

const closeRejectModal = () => {
  showRejectModal.value = false;
  selectedRequest.value = null;
  rejectForm.value.rejection_reason = '';
  rejectError.value = null;
};

const rejectRequest = async () => {
  rejectError.value = null;
  rejecting.value = true;

  try {
    const requestId = selectedRequest.value.rental_request_id;
    const payload = rejectForm.value.rejection_reason 
      ? { rejection_reason: rejectForm.value.rejection_reason }
      : {};

    await apiClient.delete(
      `/admin/rental-requests/${encodeURIComponent(requestId)}`,
      { data: payload }
    );

    // Update local request
    const index = requests.value.findIndex(r => r.rental_request_id === requestId);
    if (index !== -1) {
      requests.value[index].status = 'cancelled';
      requests.value[index].cancelled_at = new Date().toISOString();
      if (rejectForm.value.rejection_reason) {
        requests.value[index].rejection_reason = rejectForm.value.rejection_reason;
      }
    }

    closeRejectModal();
  } catch (err) {
    console.error('Failed to reject request:', err);
    rejectError.value = err.response?.data?.error?.message || 'Failed to reject request';
  } finally {
    rejecting.value = false;
  }
};

// Reset request to pending
const resetRequest = async (request) => {
  if (!confirm('Are you sure you want to reset this request to pending? This will clear the assignment details.')) {
    return;
  }

  try {
    const response = await apiClient.put(
      `/admin/rental-requests/${encodeURIComponent(request.rental_request_id)}/reset`
    );

    // Update local request
    const index = requests.value.findIndex(r => r.rental_request_id === request.rental_request_id);
    if (index !== -1) {
      requests.value[index].status = 'pending';
      requests.value[index].assignment_details = null;
      requests.value[index].accepted_at = null;
      requests.value[index].accepted_by = null;
    }
  } catch (err) {
    console.error('Failed to reset request:', err);
    alert(err.response?.data?.error?.message || 'Failed to reset request');
  }
};

// Watch for view mode changes and save to localStorage
watch(viewMode, (newMode) => {
  localStorage.setItem('adminRentalRequestsViewMode', newMode);
});

onMounted(() => {
  loadRequests();
});
</script>

<style scoped>
.admin-rental-requests {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #3498db;
  text-decoration: none;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.back-link:hover {
  text-decoration: underline;
}

.loading {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto 1rem;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 1rem;
  border-radius: 4px;
  margin: 1rem 0;
}

/* Filters */
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

.filter-stats {
  flex: 1;
  text-align: right;
  color: #7f8c8d;
  font-size: 0.9rem;
  min-width: 200px;
}

/* Card View */
.requests-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 3rem;
  color: #7f8c8d;
  font-size: 1.1rem;
}

.request-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  border-left: 4px solid #dee2e6;
}

.request-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Status-based left border colors for cards */
.request-card.status-pending {
  border-left-color: #ffc107;
}

.request-card.status-accepted {
  border-left-color: #28a745;
}

.request-card.status-paid {
  border-left-color: #007bff;
}

.request-card.status-cancelled {
  border-left-color: #6c757d;
  background-color: #f8f9fa;
}

.request-card.status-rejected {
  border-left-color: #dc3545;
  background-color: #fff5f5;
}

.request-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f0f0f0;
}

.request-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.request-details {
  margin-bottom: 1rem;
}

.detail-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.detail-row .label {
  font-weight: 600;
  color: #7f8c8d;
  min-width: 140px;
}

.comment-text,
.assignment-text {
  color: #2c3e50;
  font-style: italic;
  line-height: 1.5;
}

.request-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Table View */
.requests-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.requests-table {
  width: 100%;
  border-collapse: collapse;
}

.requests-table thead {
  background-color: #f8f9fa;
}

.requests-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #e0e0e0;
}

.requests-table td {
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.request-row {
  border-left: 4px solid #dee2e6;
}

.request-row:hover {
  background-color: #f8f9fa;
}

/* Status-based left border colors for table rows */
.request-row.status-pending {
  border-left-color: #ffc107;
}

.request-row.status-accepted {
  border-left-color: #28a745;
}

.request-row.status-paid {
  border-left-color: #007bff;
}

.request-row.status-cancelled {
  border-left-color: #6c757d;
  background-color: #f8f9fa;
}

.request-row.status-rejected {
  border-left-color: #dc3545;
  background-color: #fff5f5;
}

.no-data {
  text-align: center;
  color: #7f8c8d;
  padding: 3rem !important;
}

.boat-type-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  color: white;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

.boat-type-skiff {
  background-color: #3498db;
}

.boat-type-four {
  background-color: #e67e22;
}

.boat-type-eight {
  background-color: #9b59b6;
}

.status-badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-badge.status-pending {
  background-color: #ffc107;
  color: #000;
}

.status-badge.status-accepted {
  background-color: #28a745;
  color: white;
}

.status-badge.status-paid {
  background-color: #007bff;
  color: white;
  font-weight: 600;
}

.status-badge.status-cancelled {
  background-color: #6c757d;
  color: white;
}

.status-badge.status-rejected {
  background-color: #dc3545;
  color: white;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-table {
  padding: 0.4rem 0.8rem !important;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-table.btn-accept {
  background-color: #28a745;
  color: white;
}

.btn-table.btn-accept:hover {
  background-color: #218838;
}

.btn-table.btn-edit {
  background-color: #007bff;
  color: white;
}

.btn-table.btn-edit:hover {
  background-color: #0056b3;
}

.btn-table.btn-warning {
  background-color: #ffc107;
  color: #212529;
}

.btn-table.btn-warning:hover {
  background-color: #e0a800;
}

.btn-table.btn-reject {
  background-color: #dc3545;
  color: white;
}

.btn-table.btn-reject:hover {
  background-color: #c82333;
}

/* Modals */
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

.modal {
  background: white;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #2c3e50;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.modal-close:hover {
  background-color: #f0f0f0;
  color: #2c3e50;
}

.modal-form {
  padding: 1.5rem;
}

.request-summary {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.request-summary p {
  margin: 0.5rem 0;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.form-control.error {
  border-color: #dc3545;
}

.form-help {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.85rem;
  color: #7f8c8d;
}

.error-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.85rem;
  color: #dc3545;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-primary,
.btn-secondary,
.btn-danger,
.btn-warning {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #545b62;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #c82333;
}

.btn-warning {
  background-color: #ffc107;
  color: #212529;
}

.btn-warning:hover:not(:disabled) {
  background-color: #e0a800;
}

.btn-primary:disabled,
.btn-secondary:disabled,
.btn-danger:disabled,
.btn-warning:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-rental-requests {
    padding: 1rem;
  }

  .requests-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .request-card {
    padding: 1rem;
  }

  .request-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .request-header h3 {
    font-size: 1.1rem;
  }

  .detail-row {
    flex-direction: column;
    gap: 0.25rem;
    margin-bottom: 0.5rem;
  }

  .detail-row .label {
    min-width: auto;
    font-size: 0.8rem;
  }

  .comment-text,
  .assignment-text {
    font-size: 0.85rem;
  }

  .request-actions {
    flex-direction: column;
  }

  .request-actions .btn-table {
    width: 100%;
    justify-content: center;
  }

  .requests-table-container {
    overflow-x: auto;
  }

  .requests-table {
    min-width: 800px;
  }

  .modal {
    width: 95%;
  }
}
</style>
