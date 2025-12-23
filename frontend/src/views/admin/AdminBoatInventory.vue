<template>
  <div class="admin-boat-inventory">
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
        :actionLabel="$t('admin.boatInventory.addBoat')"
        @action="showAddBoatModal = true"
      />
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="loadBoats" class="btn-secondary">{{ $t('common.retry') }}</button>
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
            <label>{{ $t('admin.boatInventory.filterByType') }}&nbsp;:</label>
            <select v-model="filterType" class="filter-select">
              <option value="">{{ $t('admin.boatInventory.allTypes') }}</option>
              <option v-for="type in boatTypes" :key="type" :value="type">{{ type }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>{{ $t('admin.boatInventory.filterByStatus') }}&nbsp;:</label>
            <select v-model="filterStatus" class="filter-select">
              <option value="">{{ $t('admin.boatInventory.allStatuses') }}</option>
              <option v-for="status in allStatuses" :key="status" :value="status">
                {{ $t(`admin.boatInventory.status.${status}`) }}
              </option>
            </select>
          </div>

          <div class="filter-stats">
            {{ $t('admin.boatInventory.showing') }}: {{ filteredBoats.length }} {{ $t('admin.boatInventory.boats') }}
          </div>
        </template>
      </ListFilters>

      <!-- Card View -->
      <div v-if="viewMode === 'cards'" class="boats-grid">
        <div v-if="filteredBoats.length === 0" class="empty-state">
          {{ $t('admin.boatInventory.noBoats') }}
        </div>
        <div
          v-for="boat in filteredBoats"
          :key="boat.rental_boat_id || boat.PK"
          class="boat-card"
          :class="`status-${boat.status}`"
        >
          <div class="boat-header">
            <input
              v-if="editingBoat === (boat.rental_boat_id || boat.PK)"
              v-model="editForm.boat_name"
              type="text"
              class="inline-edit-input"
              @keyup.enter="saveEdit(boat)"
              @keyup.esc="cancelEdit"
            />
            <h3 v-else 
              :class="{ 'editable': boat.status !== 'paid' }" 
              @click="boat.status !== 'paid' && startEdit(boat)"
            >
              {{ boat.boat_name }}
              <svg v-if="boat.status !== 'paid'" class="edit-hint" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M18.5 2.50001C18.8978 2.10219 19.4374 1.87869 20 1.87869C20.5626 1.87869 21.1022 2.10219 21.5 2.50001C21.8978 2.89784 22.1213 3.4374 22.1213 4.00001C22.1213 4.56262 21.8978 5.10219 21.5 5.50001L12 15L8 16L9 12L18.5 2.50001Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </h3>
            <span class="boat-type">{{ boat.boat_type }}</span>
          </div>

          <div class="boat-details">
            <div class="detail-row">
              <span class="label">{{ $t('admin.boatInventory.weightCapacity') }}:</span>
              <input
                v-if="editingBoat === (boat.rental_boat_id || boat.PK)"
                v-model="editForm.rower_weight_range"
                type="text"
                class="inline-edit-input"
                :placeholder="$t('admin.boatInventory.weightPlaceholder')"
                @keyup.enter="saveEdit(boat)"
                @keyup.esc="cancelEdit"
              />
              <span v-else 
                :class="{ 'editable': boat.status !== 'paid' }" 
                @click="boat.status !== 'paid' && startEdit(boat)"
              >
                {{ boat.rower_weight_range || '-' }}
                <svg v-if="boat.status !== 'paid'" class="edit-hint" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M18.5 2.50001C18.8978 2.10219 19.4374 1.87869 20 1.87869C20.5626 1.87869 21.1022 2.10219 21.5 2.50001C21.8978 2.89784 22.1213 3.4374 22.1213 4.00001C22.1213 4.56262 21.8978 5.10219 21.5 5.50001L12 15L8 16L9 12L18.5 2.50001Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
            </div>
            <div class="detail-row">
              <span class="label">{{ $t('admin.boatInventory.statusLabel') }}:</span>
              <select
                v-if="editingBoat === (boat.rental_boat_id || boat.PK)"
                v-model="editForm.status"
                class="inline-edit-select"
                @change="saveEdit(boat)"
              >
                <option v-for="status in getAvailableStatuses(boat)" :key="status" :value="status">
                  {{ $t(`admin.boatInventory.status.${status}`) }}
                </option>
              </select>
              <span v-else 
                class="status-badge" 
                :class="[boat.status, { 'editable': boat.status !== 'paid' }]"
                @click="boat.status !== 'paid' && startEdit(boat)"
              >
                {{ $t(`admin.boatInventory.status.${boat.status}`) }}
                <svg v-if="boat.status !== 'paid'" class="edit-hint" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M18.5 2.50001C18.8978 2.10219 19.4374 1.87869 20 1.87869C20.5626 1.87869 21.1022 2.10219 21.5 2.50001C21.8978 2.89784 22.1213 3.4374 22.1213 4.00001C22.1213 4.56262 21.8978 5.10219 21.5 5.50001L12 15L8 16L9 12L18.5 2.50001Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
            </div>
            <div v-if="boat.requester" class="detail-row">
              <span class="label">{{ $t('admin.boatInventory.requester') }}:</span>
              <span>{{ boat.requester }}</span>
            </div>
          </div>

          <div class="boat-actions">
            <button
              v-if="editingBoat === (boat.rental_boat_id || boat.PK)"
              @click="saveEdit(boat)"
              class="btn-save"
            >
              ✓ {{ $t('common.save') }}
            </button>
            <button
              v-if="editingBoat === (boat.rental_boat_id || boat.PK)"
              @click="cancelEdit"
              class="btn-cancel"
            >
              ✕ {{ $t('common.cancel') }}
            </button>
            <button
              v-if="editingBoat !== (boat.rental_boat_id || boat.PK) && boat.status !== 'paid' && boat.status !== 'confirmed'"
              @click="deleteBoat(boat)"
              class="btn-danger"
            >
              {{ $t('common.delete') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Boats Table -->
      <div v-else class="boats-table-container">
        <table class="boats-table">
          <thead>
            <tr>
              <th>{{ $t('admin.boatInventory.boatType') }}</th>
              <th>{{ $t('admin.boatInventory.boatName') }}</th>
              <th>{{ $t('admin.boatInventory.weightCapacity') }}</th>
              <th>{{ $t('admin.boatInventory.statusLabel') }}</th>
              <th>{{ $t('admin.boatInventory.requester') }}</th>
              <th>{{ $t('admin.boatInventory.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredBoats.length === 0">
              <td colspan="6" class="no-data">{{ $t('admin.boatInventory.noBoats') }}</td>
            </tr>
            <tr v-for="boat in filteredBoats" :key="boat.rental_boat_id || boat.PK" class="boat-row">
              <td>
                <span :class="['boat-type-badge', `boat-type-${getBoatCategory(boat.boat_type)}`]">{{ boat.boat_type }}</span>
              </td>
              <td>
                <input
                  v-if="editingBoat === (boat.rental_boat_id || boat.PK)"
                  v-model="editForm.boat_name"
                  type="text"
                  class="inline-edit-input"
                  @keyup.enter="saveEdit(boat)"
                  @keyup.esc="cancelEdit"
                />
                <span v-else class="boat-name" :class="{ 'no-edit': boat.status === 'paid' }" @click="boat.status !== 'paid' && startEdit(boat)">
                  {{ boat.boat_name }}
                  <svg v-if="boat.status !== 'paid'" class="edit-hint" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M18.5 2.50001C18.8978 2.10219 19.4374 1.87869 20 1.87869C20.5626 1.87869 21.1022 2.10219 21.5 2.50001C21.8978 2.89784 22.1213 3.4374 22.1213 4.00001C22.1213 4.56262 21.8978 5.10219 21.5 5.50001L12 15L8 16L9 12L18.5 2.50001Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </span>
              </td>
              <td>
                <input
                  v-if="editingBoat === (boat.rental_boat_id || boat.PK)"
                  v-model="editForm.rower_weight_range"
                  type="text"
                  class="inline-edit-input"
                  :placeholder="$t('admin.boatInventory.weightPlaceholder')"
                  @keyup.enter="saveEdit(boat)"
                  @keyup.esc="cancelEdit"
                />
                <span v-else class="weight-range" :class="{ 'no-edit': boat.status === 'paid' }" @click="boat.status !== 'paid' && startEdit(boat)">
                  {{ boat.rower_weight_range || '-' }}
                  <svg v-if="boat.status !== 'paid'" class="edit-hint" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M18.5 2.50001C18.8978 2.10219 19.4374 1.87869 20 1.87869C20.5626 1.87869 21.1022 2.10219 21.5 2.50001C21.8978 2.89784 22.1213 3.4374 22.1213 4.00001C22.1213 4.56262 21.8978 5.10219 21.5 5.50001L12 15L8 16L9 12L18.5 2.50001Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </span>
              </td>
              <td>
                <select
                  v-if="editingBoat === (boat.rental_boat_id || boat.PK)"
                  v-model="editForm.status"
                  class="inline-edit-select"
                  @change="saveEdit(boat)"
                >
                  <option v-for="status in getAvailableStatuses(boat)" :key="status" :value="status">
                    {{ $t(`admin.boatInventory.status.${status}`) }}
                  </option>
                </select>
                <span v-else :class="['status-badge', `status-${boat.status}`, { 'no-edit': boat.status === 'paid' }]" @click="boat.status !== 'paid' && startEdit(boat)">
                  {{ $t(`admin.boatInventory.status.${boat.status}`) }}
                  <svg v-if="boat.status !== 'paid'" class="edit-hint" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M18.5 2.50001C18.8978 2.10219 19.4374 1.87869 20 1.87869C20.5626 1.87869 21.1022 2.10219 21.5 2.50001C21.8978 2.89784 22.1213 3.4374 22.1213 4.00001C22.1213 4.56262 21.8978 5.10219 21.5 5.50001L12 15L8 16L9 12L18.5 2.50001Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </span>
              </td>
              <td>
                <span v-if="boat.requester" class="requester">{{ boat.requester }}</span>
                <span v-else class="no-requester">-</span>
              </td>
              <td>
                <div class="action-buttons">
                  <button
                    v-if="editingBoat === (boat.rental_boat_id || boat.PK)"
                    @click="saveEdit(boat)"
                    class="btn-icon-small btn-save"
                    :title="$t('common.save')"
                  >
                    ✓
                  </button>
                  <button
                    v-if="editingBoat === (boat.rental_boat_id || boat.PK)"
                    @click="cancelEdit"
                    class="btn-icon-small btn-cancel"
                    :title="$t('common.cancel')"
                  >
                    ✕
                  </button>
                  <button
                    v-if="editingBoat !== (boat.rental_boat_id || boat.PK) && boat.status !== 'paid'"
                    @click="deleteBoat(boat)"
                    class="btn-table btn-delete-table"
                    :disabled="boat.status === 'paid' || boat.status === 'confirmed'"
                    :title="boat.status === 'paid' ? $t('admin.boatInventory.cannotDeletePaid') : boat.status === 'confirmed' ? $t('admin.boatInventory.cannotDeleteConfirmed') : ''"
                  >
                    {{ $t('common.delete') }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Boat Modal -->
    <div v-if="showAddBoatModal" class="modal-overlay" @click.self="closeAddBoatModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ $t('admin.boatInventory.addBoat') }}</h2>
          <button @click="closeAddBoatModal" class="modal-close">✕</button>
        </div>

        <form @submit.prevent="createBoat" class="modal-form">
          <div class="form-group">
            <label for="boat_type">{{ $t('admin.boatInventory.boatType') }} *</label>
            <select
              id="boat_type"
              v-model="newBoat.boat_type"
              class="form-control"
              :class="{ 'error': validationErrors.boat_type }"
              required
            >
              <option value="">{{ $t('admin.boatInventory.selectType') }}</option>
              <option v-for="type in boatTypes" :key="type" :value="type">{{ type }}</option>
            </select>
            <span v-if="validationErrors.boat_type" class="error-text">
              {{ validationErrors.boat_type }}
            </span>
          </div>

          <div class="form-group">
            <label for="boat_name">{{ $t('admin.boatInventory.boatName') }} *</label>
            <input
              id="boat_name"
              v-model="newBoat.boat_name"
              type="text"
              class="form-control"
              :class="{ 'error': validationErrors.boat_name }"
              :placeholder="$t('admin.boatInventory.boatNamePlaceholder')"
              required
            />
            <span v-if="validationErrors.boat_name" class="error-text">
              {{ validationErrors.boat_name }}
            </span>
          </div>

          <div class="form-group">
            <label for="rower_weight_range">{{ $t('admin.boatInventory.weightCapacity') }}</label>
            <input
              id="rower_weight_range"
              v-model="newBoat.rower_weight_range"
              type="text"
              class="form-control"
              :placeholder="$t('admin.boatInventory.weightPlaceholder')"
            />
            <small class="form-help">{{ $t('admin.boatInventory.weightHelp') }}</small>
          </div>

          <div v-if="createError" class="error-message">
            {{ createError }}
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeAddBoatModal" class="btn-secondary" :disabled="creating">
              {{ $t('common.cancel') }}
            </button>
            <button type="submit" class="btn-primary" :disabled="creating">
              {{ creating ? $t('common.creating') : $t('common.create') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import apiClient from '../../services/apiClient';
import ListHeader from '../../components/shared/ListHeader.vue';
import ListFilters from '../../components/shared/ListFilters.vue';

const router = useRouter();
const { t } = useI18n();

const loading = ref(true);
const error = ref(null);
const boats = ref([]);
const viewMode = ref(localStorage.getItem('adminBoatInventoryViewMode') || 'table');
const searchQuery = ref('');

const boatTypes = ['skiff', '4-', '4+', '4x-', '4x+', '8+', '8x+'];
// All possible statuses (for filtering)
const allStatuses = ['new', 'available', 'requested', 'confirmed', 'paid'];
// Statuses that admin can manually set (excluding 'requested' and 'paid' which are system-only)
const statuses = ['new', 'available', 'confirmed'];

// Get available statuses for a specific boat based on its current state
const getAvailableStatuses = (boat) => {
  // If no requester, cannot select 'confirmed'
  if (!boat.requester) {
    return statuses.filter(s => s !== 'confirmed');
  }
  return statuses;
};

// Get boat category for color coding
const getBoatCategory = (boatType) => {
  if (boatType === 'skiff') return 'skiff';
  if (boatType.startsWith('4')) return 'four';
  if (boatType.startsWith('8')) return 'eight';
  return 'skiff'; // default
};

// Filters
const filterType = ref('');
const filterStatus = ref('');

// Add boat modal
const showAddBoatModal = ref(false);
const creating = ref(false);
const createError = ref(null);
const newBoat = ref({
  boat_type: '',
  boat_name: '',
  rower_weight_range: '',
  status: 'new'
});
const validationErrors = ref({});

// Inline editing
const editingBoat = ref(null);
const editForm = ref({
  boat_name: '',
  rower_weight_range: '',
  status: ''
});

const filteredBoats = computed(() => {
  let result = boats.value;

  // Apply search filter
  if (searchQuery.value) {
    const search = searchQuery.value.toLowerCase();
    result = result.filter(boat =>
      boat.boat_name?.toLowerCase().includes(search) ||
      boat.boat_type?.toLowerCase().includes(search) ||
      boat.requester?.toLowerCase().includes(search)
    );
  }

  if (filterType.value) {
    result = result.filter(b => b.boat_type === filterType.value);
  }

  if (filterStatus.value) {
    result = result.filter(b => b.status === filterStatus.value);
  }

  return result;
});

const loadBoats = async () => {
  loading.value = true;
  error.value = null;

  try {
    const response = await apiClient.get('/admin/rental-boats');
    boats.value = response.data.data.rental_boats || [];
  } catch (err) {
    console.error('Failed to load boats:', err);
    error.value = t('admin.boatInventory.loadError');
  } finally {
    loading.value = false;
  }
};

const clearFilters = () => {
  filterType.value = '';
  filterStatus.value = '';
  searchQuery.value = '';
};

const closeAddBoatModal = () => {
  showAddBoatModal.value = false;
  newBoat.value = {
    boat_type: '',
    boat_name: '',
    rower_weight_range: '',
    status: 'new'
  };
  validationErrors.value = {};
  createError.value = null;
};

const validateNewBoat = () => {
  validationErrors.value = {};

  if (!newBoat.value.boat_type) {
    validationErrors.value.boat_type = t('admin.boatInventory.errors.typeRequired');
  }

  if (!newBoat.value.boat_name || !newBoat.value.boat_name.trim()) {
    validationErrors.value.boat_name = t('admin.boatInventory.errors.nameRequired');
  } else if (newBoat.value.boat_name.length > 100) {
    validationErrors.value.boat_name = t('admin.boatInventory.errors.nameTooLong');
  }

  return Object.keys(validationErrors.value).length === 0;
};

const createBoat = async () => {
  createError.value = null;

  if (!validateNewBoat()) {
    return;
  }

  creating.value = true;

  try {
    const response = await apiClient.post('/admin/rental-boats', newBoat.value);
    boats.value.push(response.data.data);
    closeAddBoatModal();
    // Reload to ensure consistency
    await loadBoats();
  } catch (err) {
    console.error('Failed to create boat:', err);
    createError.value = err.response?.data?.error?.message || t('admin.boatInventory.createError');
  } finally {
    creating.value = false;
  }
};

const startEdit = (boat) => {
  const boatId = boat.rental_boat_id || boat.PK;
  console.log('Starting edit for boat:', boatId, boat);
  editingBoat.value = boatId;
  editForm.value = {
    boat_name: boat.boat_name,
    rower_weight_range: boat.rower_weight_range || '',
    status: boat.status
  };
};

const cancelEdit = () => {
  editingBoat.value = null;
  editForm.value = {
    boat_name: '',
    rower_weight_range: '',
    status: ''
  };
};

const saveEdit = async (boat) => {
  try {
    const updates = {};

    if (editForm.value.boat_name !== boat.boat_name) {
      updates.boat_name = editForm.value.boat_name;
    }

    if (editForm.value.rower_weight_range !== (boat.rower_weight_range || '')) {
      updates.rower_weight_range = editForm.value.rower_weight_range;
    }

    if (editForm.value.status !== boat.status) {
      updates.status = editForm.value.status;
    }

    if (Object.keys(updates).length === 0) {
      cancelEdit();
      return;
    }

    // Use rental_boat_id or fall back to PK
    const boatId = boat.rental_boat_id || boat.PK;
    console.log('Updating boat with ID:', boatId, 'Updates:', updates, 'Full boat object:', boat);
    // URL-encode the ID to handle special characters like #
    const response = await apiClient.put(`/admin/rental-boats/${encodeURIComponent(boatId)}`, updates);
    
    // Update local boat object
    const index = boats.value.findIndex(b => (b.rental_boat_id || b.PK) === boatId);
    if (index !== -1) {
      boats.value[index] = response.data.data;
    }

    cancelEdit();
  } catch (err) {
    console.error('Failed to update boat:', err);
    alert(err.response?.data?.error?.message || t('admin.boatInventory.updateError'));
    cancelEdit();
  }
};

const deleteBoat = async (boat) => {
  if (boat.status === 'paid') {
    alert(t('admin.boatInventory.cannotDeletePaid'));
    return;
  }
  
  if (boat.status === 'confirmed') {
    alert(t('admin.boatInventory.cannotDeleteConfirmed'));
    return;
  }

  if (!confirm(t('admin.boatInventory.confirmDelete', { name: boat.boat_name }))) {
    return;
  }

  try {
    // Use rental_boat_id or fall back to PK
    const boatId = boat.rental_boat_id || boat.PK;
    console.log('Deleting boat with ID:', boatId, 'Full boat object:', boat);
    // URL-encode the ID to handle special characters like #
    await apiClient.delete(`/admin/rental-boats/${encodeURIComponent(boatId)}`);
    boats.value = boats.value.filter(b => (b.rental_boat_id || b.PK) !== boatId);
  } catch (err) {
    console.error('Failed to delete boat:', err);
    alert(err.response?.data?.error?.message || t('admin.boatInventory.deleteError'));
  }
};

// Watch for view mode changes and save to localStorage
watch(viewMode, (newMode) => {
  localStorage.setItem('adminBoatInventoryViewMode', newMode);
});

onMounted(() => {
  loadBoats();
});
</script>

<style scoped>
.admin-boat-inventory {
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

/* Table */
.boats-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.boats-table {
  width: 100%;
  border-collapse: collapse;
}

.boats-table thead {
  background-color: #f8f9fa;
}

.boats-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #e0e0e0;
}

.boats-table td {
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.boat-row:hover {
  background-color: #f8f9fa;
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
  background-color: #3498db; /* Blue for skiffs */
}

.boat-type-four {
  background-color: #e67e22; /* Orange for fours */
}

.boat-type-eight {
  background-color: #9b59b6; /* Purple for eights */
}

.boat-name,
.weight-range {
  cursor: pointer;
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border: 1px dashed transparent;
  transition: all 0.2s;
}

.boat-name:hover,
.weight-range:hover {
  background-color: #f0f0f0;
  border-color: #3498db;
}

.boat-name.no-edit,
.weight-range.no-edit,
.status-badge.no-edit {
  cursor: not-allowed;
  opacity: 0.7;
}

.boat-name.no-edit:hover,
.weight-range.no-edit:hover,
.status-badge.no-edit:hover {
  background-color: transparent;
  border-color: transparent;
}

.weight-range {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.edit-hint {
  opacity: 0.4;
  margin-left: 0.5rem;
  vertical-align: middle;
  transition: opacity 0.2s;
  display: inline-block;
}

.boat-name:hover .edit-hint,
.status-badge:hover .edit-hint {
  opacity: 1;
}

.status-badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px dashed transparent;
  transition: all 0.2s;
}

.status-badge:hover {
  opacity: 0.9;
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status-new {
  background-color: #e8f4f8;
  color: #2980b9;
}

.status-available {
  background-color: #d4edda;
  color: #155724;
}

.status-requested {
  background-color: #fff3cd;
  color: #856404;
}

.status-confirmed {
  background-color: #f8d7da;
  color: #721c24;
}

.status-paid {
  background-color: #cce5ff;
  color: #004085;
  font-weight: 600;
}

.requester {
  color: #2c3e50;
  font-size: 0.9rem;
}

.no-requester {
  color: #bdc3c7;
}

.inline-edit-input,
.inline-edit-select {
  padding: 0.35rem 0.5rem;
  border: 2px solid #3498db;
  border-radius: 4px;
  font-size: 0.95rem;
  width: 100%;
  max-width: 250px;
}

.inline-edit-input:focus,
.inline-edit-select:focus {
  outline: none;
  border-color: #2980b9;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-icon-small {
  padding: 0.35rem 0.6rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-save {
  background-color: #27ae60;
  color: white;
}

.btn-save:hover {
  background-color: #229954;
}

.btn-cancel {
  background-color: #95a5a6;
  color: white;
}

.btn-cancel:hover {
  background-color: #7f8c8d;
}

.btn-delete {
  background-color: #e74c3c;
  color: white;
}

.btn-delete:hover {
  background-color: #c0392b;
}

.btn-table {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
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

.boat-card.status-new {
  border-left: 4px solid #2980b9;
}

.boat-card.status-available {
  border-left: 4px solid #27ae60;
}

.boat-card.status-requested {
  border-left: 4px solid #f39c12;
}

.boat-card.status-confirmed {
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

.boat-header h3.editable {
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border: 1px dashed transparent;
  transition: all 0.2s;
}

.boat-header h3.editable:hover {
  background-color: #f0f0f0;
  border-color: #3498db;
}

.boat-header h3.editable:hover .edit-hint {
  opacity: 1;
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

.detail-row span:not(.label):not(.status-badge) {
  color: #2c3e50;
}

.detail-row span.editable {
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border: 1px dashed transparent;
  transition: all 0.2s;
  display: inline-block;
}

.detail-row span.editable:hover {
  background-color: #f0f0f0;
  border-color: #3498db;
}

.detail-row span.editable:hover .edit-hint {
  opacity: 1;
}

.edit-hint {
  opacity: 0.4;
  margin-left: 0.5rem;
  vertical-align: middle;
  transition: opacity 0.2s;
  display: inline-block;
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
  display: inline-block;
}

.status-badge.editable {
  cursor: pointer;
  border: 1px dashed transparent;
  transition: all 0.2s;
}

.status-badge.editable:hover {
  opacity: 0.9;
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status-badge.editable:hover .edit-hint {
  opacity: 1;
}

.status-badge.new {
  background: #e8f4f8;
  color: #2980b9;
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
  background: #f8d7da;
  color: #721c24;
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

.boat-actions .btn-save {
  background-color: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.boat-actions .btn-save:hover {
  background-color: #229954;
}

.boat-actions .btn-cancel {
  background-color: #95a5a6;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.boat-actions .btn-cancel:hover {
  background-color: #7f8c8d;
}

.boat-actions .btn-danger {
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.boat-actions .btn-danger:hover {
  background-color: #c82333;
}

.inline-edit-input,
.inline-edit-select {
  padding: 0.35rem 0.5rem;
  border: 2px solid #3498db;
  border-radius: 4px;
  font-size: 0.95rem;
  width: 100%;
}

.inline-edit-input:focus,
.inline-edit-select:focus {
  outline: none;
  border-color: #2980b9;
}

.empty-state {
  text-align: center;
  padding: 1.5rem;
  color: #7f8c8d;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Modal */
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

.modal {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.modal-header h2 {
  margin: 0;
  color: #2c3e50;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
  padding: 0;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.modal-close:hover {
  background-color: #f0f0f0;
}

.modal-form {
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
}

.form-control.error {
  border-color: #e74c3c;
}

.form-help {
  display: block;
  color: #7f8c8d;
  font-size: 0.85rem;
  margin-top: 0.25rem;
  font-style: italic;
}

.error-text {
  display: block;
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.form-help {
  display: block;
  color: #7f8c8d;
  font-size: 0.85rem;
  margin-top: 0.25rem;
  font-style: italic;
}

.error-message {
  background-color: #fee;
  border: 1px solid #e74c3c;
  color: #c0392b;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  flex-shrink: 0;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  min-height: 44px;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn-primary:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #ecf0f1;
  color: #2c3e50;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #d5dbdb;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .admin-boat-inventory {
    padding: 1rem;
  }

  .page-header {
    margin-bottom: 1rem;
  }

  .modal-overlay {
    align-items: flex-end;
    padding: 0;
  }

  .modal {
    border-radius: 12px 12px 0 0;
    width: 100%;
    max-width: 100%;
    max-height: 90vh;
  }

  .modal-header {
    padding: 1rem;
  }

  .modal-form {
    padding: 1rem;
  }

  .form-control {
    font-size: 16px;
    min-height: 44px;
  }

  .modal-actions {
    flex-direction: column;
  }

  .modal-actions .btn-primary,
  .modal-actions .btn-secondary {
    width: 100%;
  }

  .filter-select {
    font-size: 16px;
    min-height: 44px;
  }

  .btn-table {
    min-height: 44px;
    min-width: 44px;
  }
}

@media (min-width: 768px) {
  .boats-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
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
    flex: 1;
  }
}
</style>
