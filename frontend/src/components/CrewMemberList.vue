<template>
  <div class="crew-member-list">
    <ListHeader
      :title="$t('crew.list.title')"
      :subtitle="$t('crew.list.subtitle')"
      v-model:viewMode="viewMode"
      :actionLabel="$t('crew.list.addNew')"
      @action="showCreateForm = true"
    />

    <ListFilters
      v-model:searchQuery="searchQuery"
      :searchPlaceholder="$t('crew.list.search')"
      @clear="clearFilters"
    >
      <template #filters>
        <div class="filter-group">
          <label>{{ $t('crew.list.status') }}&nbsp;:</label>
          <select v-model="filter" class="filter-select">
            <option value="all">{{ $t('crew.list.all') }} ({{ crewStore.crewMembers.length }})</option>
            <option value="assigned">{{ $t('crew.list.assigned') }} ({{ crewStore.assignedCrewMembers.length }})</option>
            <option value="unassigned">{{ $t('crew.list.unassigned') }} ({{ unassignedCount }})</option>
          </select>
        </div>

        <div class="filter-group">
          <label>{{ $t('crew.list.gender') }}&nbsp;:</label>
          <select v-model="genderFilter" class="filter-select">
            <option value="all">{{ $t('crew.list.allGenders') }}</option>
            <option value="M">{{ $t('crew.form.male') }}</option>
            <option value="F">{{ $t('crew.form.female') }}</option>
          </select>
        </div>

        <div class="filter-group">
          <label>{{ $t('crew.list.category') }}&nbsp;:</label>
          <select v-model="categoryFilter" class="filter-select">
            <option value="all">{{ $t('crew.list.allCategories') }}</option>
            <option value="junior">{{ $t('crew.list.junior') }}</option>
            <option value="senior">{{ $t('boat.senior') }}</option>
            <option value="master">{{ $t('boat.master') }}</option>
          </select>
        </div>

        <div class="filter-group">
          <label>{{ $t('crew.list.sortBy') }}&nbsp;:</label>
          <select v-model="sortBy" class="sort-select">
            <option value="last_name">{{ $t('crew.list.lastName') }}</option>
            <option value="first_name">{{ $t('crew.list.firstName') }}</option>
            <option value="date_of_birth">{{ $t('crew.list.age') }}</option>
            <option value="created_at">{{ $t('crew.list.dateAdded') }}</option>
          </select>
        </div>
      </template>
    </ListFilters>

    <!-- Loading State -->
    <div v-if="crewStore.loading" class="loading">
      {{ $t('common.loading') }}
    </div>

    <!-- Error State -->
    <div v-else-if="crewStore.error" class="alert alert-error">
      {{ crewStore.error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredCrewMembers.length === 0" class="empty-state">
      <p>{{ $t('crew.list.noMembers') }}</p>
      <button class="btn btn-primary" @click="showCreateForm = true">
        {{ $t('crew.list.addFirst') }}
      </button>
    </div>

    <!-- Card View -->
    <div v-else-if="viewMode === 'cards'" class="crew-grid">
      <CrewMemberCard
        v-for="member in filteredCrewMembers"
        :key="member.crew_member_id"
        :crew-member="member"
        @edit="handleEdit"
        @delete="handleDelete"
      />
    </div>

    <!-- Table View -->
    <div v-else class="crew-table-container">
      <table class="crew-table">
        <thead>
          <tr>
            <th>{{ $t('crew.form.firstName') }}</th>
            <th>{{ $t('crew.form.lastName') }}</th>
            <th>{{ $t('crew.list.age') }}</th>
            <th>{{ $t('crew.form.gender') }}</th>
            <th>{{ $t('crew.card.category') }}</th>
            <th>{{ $t('crew.card.club') }}</th>
            <th>{{ $t('crew.card.assigned') }}</th>
            <th>{{ $t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="member in filteredCrewMembers" 
            :key="member.crew_member_id"
            :class="{ 'row-assigned': member.assigned_boat_id, 'row-flagged': member.flagged_issues?.length }"
          >
            <td>{{ member.first_name }}</td>
            <td>{{ member.last_name }}</td>
            <td>{{ calculateAge(member.date_of_birth) }}</td>
            <td>{{ member.gender === 'M' ? $t('crew.form.male') : $t('crew.form.female') }}</td>
            <td>
              <span class="category-badge" :class="`category-${getAgeCategoryForMember(member.date_of_birth)}`">
                {{ $t(`boat.${getAgeCategoryForMember(member.date_of_birth)}`) }}
                <span v-if="getAgeCategoryForMember(member.date_of_birth) === 'master'" class="master-letter">
                  {{ getMasterCategoryLetter(member.date_of_birth) }}
                </span>
              </span>
            </td>
            <td><span class="club-box">{{ member.club_affiliation }}</span></td>
            <td>
              <span v-if="member.assigned_boat_id" class="assigned-badge">✓</span>
              <span v-else>-</span>
            </td>
            <td class="actions-cell">
              <button @click="handleEdit(member)" class="btn-table btn-edit-table">
                {{ $t('common.edit') }}
              </button>
              <button @click="handleDelete(member)" class="btn-table btn-delete-table">
                {{ $t('common.delete') }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateForm || editingMember" class="modal-overlay" @click.self="closeForm">
      <div class="modal-content">
        <CrewMemberForm
          :crew-member="editingMember"
          @success="handleFormSuccess"
          @cancel="closeForm"
        />
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deletingMember" class="modal-overlay" @click.self="deletingMember = null">
      <div class="modal-content modal-small">
        <h3>{{ $t('crew.list.confirmDelete') }}</h3>
        <p>{{ $t('crew.list.confirmDeleteMessage', { name: `${deletingMember.first_name} ${deletingMember.last_name}` }) }}</p>
        <div class="button-group">
          <button class="btn btn-danger" @click="confirmDelete" :disabled="deleting">
            {{ deleting ? $t('common.loading') : $t('common.delete') }}
          </button>
          <button class="btn btn-secondary" @click="deletingMember = null" :disabled="deleting">
            {{ $t('common.cancel') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useCrewStore } from '../stores/crewStore';
import { calculateAge, getAgeCategory, getMasterCategory } from '../utils/raceEligibility';
import CrewMemberCard from './CrewMemberCard.vue';
import CrewMemberForm from './CrewMemberForm.vue';
import ListHeader from './shared/ListHeader.vue';
import ListFilters from './shared/ListFilters.vue';

const { t } = useI18n();
const crewStore = useCrewStore();

const searchQuery = ref('');
const filter = ref('all');
const genderFilter = ref('all');
const categoryFilter = ref('all');

// Computed: count of unassigned crew members
const unassignedCount = computed(() => {
  return crewStore.crewMembers.filter(member => !member.assigned_boat_id).length;
});
const sortBy = ref('last_name');
// Load view mode from localStorage or default to 'cards'
const viewMode = ref(localStorage.getItem('crewViewMode') || 'cards');
const showCreateForm = ref(false);
const editingMember = ref(null);
const deletingMember = ref(null);
const deleting = ref(false);

// Watch for view mode changes and save to localStorage
watch(viewMode, (newMode) => {
  localStorage.setItem('crewViewMode', newMode);
});

const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString();
};

const getAgeCategoryForMember = (dateOfBirth) => {
  const age = calculateAge(dateOfBirth);
  return getAgeCategory(age);
};

const getMasterCategoryLetter = (dateOfBirth) => {
  const age = calculateAge(dateOfBirth);
  return getMasterCategory(age);
};

// Load crew members on mount
onMounted(async () => {
  // Check authentication
  const token = localStorage.getItem('access_token');
  console.log('Auth token exists:', !!token);
  console.log('Auth token (first 20 chars):', token ? token.substring(0, 20) + '...' : 'NO TOKEN');
  console.log('API URL:', import.meta.env.VITE_API_URL);
  
  try {
    console.log('Fetching crew members...');
    await crewStore.fetchCrewMembers();
    console.log('Crew members loaded successfully');
    console.log('Crew members data:', crewStore.crewMembers);
    if (crewStore.crewMembers.length > 0) {
      console.log('First crew member:', crewStore.crewMembers[0]);
    }
  } catch (error) {
    console.error('Failed to load crew members:', error);
    console.error('Error details:', {
      message: error.message,
      response: error.response,
      request: error.request,
      config: error.config
    });
    
    // If it's a network error, it might be CORS
    if (error.message === 'Network Error') {
      console.error('This is likely a CORS issue or the API is not accessible');
    }
  }
});

// Filtered and sorted crew members
const filteredCrewMembers = computed(() => {
  let members = crewStore.crewMembers;

  // Apply filter
  switch (filter.value) {
    case 'assigned':
      members = crewStore.assignedCrewMembers;
      break;
    case 'unassigned':
      members = crewStore.crewMembers.filter(member => !member.assigned_boat_id);
      break;
  }

  // Apply gender filter
  if (genderFilter.value !== 'all') {
    members = members.filter(member => member.gender === genderFilter.value);
  }

  // Apply category filter
  if (categoryFilter.value !== 'all') {
    members = members.filter(member => {
      const age = calculateAge(member.date_of_birth);
      const category = getAgeCategory(age);
      
      if (categoryFilter.value === 'junior') {
        return category === 'j16' || category === 'j18';
      } else if (categoryFilter.value === 'senior') {
        return category === 'senior';
      } else if (categoryFilter.value === 'master') {
        return category === 'master';
      }
      return true;
    });
  }

  // Apply search
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    members = members.filter(member =>
      member.first_name.toLowerCase().includes(query) ||
      member.last_name.toLowerCase().includes(query) ||
      member.license_number.toLowerCase().includes(query)
    );
  }

  // Apply sort
  return [...members].sort((a, b) => {
    const aVal = a[sortBy.value];
    const bVal = b[sortBy.value];
    
    if (typeof aVal === 'string') {
      return aVal.localeCompare(bVal);
    }
    return aVal > bVal ? 1 : -1;
  });
});

const handleEdit = (member) => {
  editingMember.value = member;
};

const handleDelete = (member) => {
  deletingMember.value = member;
};

const confirmDelete = async () => {
  deleting.value = true;
  try {
    await crewStore.deleteCrewMember(deletingMember.value.crew_member_id);
    deletingMember.value = null;
  } catch (error) {
    console.error('Failed to delete crew member:', error);
    alert(t('crew.list.deleteError'));
  } finally {
    deleting.value = false;
  }
};

const handleFormSuccess = () => {
  closeForm();
};

const closeForm = () => {
  showCreateForm.value = false;
  editingMember.value = null;
  // Clear any errors from the store when closing the form
  crewStore.clearError();
};

const clearFilters = () => {
  filter.value = 'all';
  genderFilter.value = 'all';
  categoryFilter.value = 'all';
  searchQuery.value = '';
};
</script>

<style scoped>
.crew-member-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0;
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
}

.sort-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.alert-error {
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ef5350;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 8px;
}

.empty-state p {
  color: #666;
  margin-bottom: 1rem;
}

.crew-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.modal-small {
  max-width: 500px;
  padding: 2rem;
}

.modal-small h3 {
  margin-top: 0;
  color: #333;
}

.button-group {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  min-height: 44px;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background-color: #45a049;
}

.btn-secondary {
  background-color: #fff;
  color: #666;
  border: 1px solid #ddd;
}

.btn-secondary:hover {
  background-color: #f5f5f5;
}

.btn-danger {
  background-color: #f44336;
  color: white;
  flex: 1;
}

.btn-danger:hover:not(:disabled) {
  background-color: #d32f2f;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Table View Styles */
.crew-table-container {
  background-color: white;
  border-radius: 8px;
  overflow-x: auto;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.crew-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.crew-table thead {
  background-color: #f8f9fa;
}

.crew-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
}

.crew-table td {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.crew-table tbody tr:hover {
  background-color: #f8f9fa;
}

.crew-table tbody tr.row-assigned {
  border-left: 4px solid #4CAF50;
}

.crew-table tbody tr.row-flagged {
  border-left: 4px solid #ffc107;
}

.assigned-badge {
  color: #4CAF50;
  font-size: 1.25rem;
  font-weight: bold;
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
  min-height: 44px;
  min-width: 44px;
}

.btn-edit-table {
  background-color: #6c757d;
  color: white;
}

.btn-edit-table:hover {
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
  .crew-member-list {
    padding: 0;
  }

  .filter-group {
    width: 100%;
    min-width: auto;
  }

  .filter-select,
  .sort-select {
    width: 100%;
    font-size: 16px; /* Prevents iOS zoom */
    min-height: 44px; /* Touch target */
  }

  /* Card grid - single column on mobile */
  .crew-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  /* Table - horizontal scroll with indicators */
  .crew-table-container {
    margin: 0 -1rem;
    border-radius: 0;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    position: relative;
  }

  .crew-table {
    min-width: 800px;
  }

  /* Action buttons - reduce padding on mobile */
  .actions-cell {
    padding: 0.5rem;
  }

  .btn-table {
    padding: 0.5rem;
    font-size: 0.75rem;
    min-height: 44px;
    min-width: 44px;
  }

  /* Modals - bottom sheet style on mobile */
  .modal-overlay {
    align-items: flex-end;
    padding: 0;
  }

  .modal-content {
    border-radius: 12px 12px 0 0;
    width: 100%;
    max-width: 100%;
    max-height: 90vh;
  }

  .modal-small {
    border-radius: 12px 12px 0 0;
    padding: 1.5rem;
    max-width: 100%;
    width: 100%;
  }

  .button-group {
    flex-direction: column;
  }

  .button-group .btn {
    width: 100%;
    min-height: 44px;
  }
}

/* Tablet adjustments */
@media (min-width: 768px) and (max-width: 1023px) {
  .crew-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .filter-row {
    flex-wrap: wrap;
  }

  .filter-group {
    flex: 1 1 calc(50% - 0.5rem);
    min-width: 150px;
  }
}

.category-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.category-j14 {
  background-color: #E3F2FD;
  color: #1976D2;
}

.category-j16 {
  background-color: #E3F2FD;
  color: #1976D2;
}

.category-j18 {
  background-color: #E8F5E9;
  color: #388E3C;
}

.category-senior {
  background-color: #FFF3E0;
  color: #F57C00;
}

.category-master {
  background-color: #F3E5F5;
  color: #7B1FA2;
}

.master-letter {
  margin-left: 0.25rem;
  font-weight: 700;
}

.club-box {
  display: inline-block;
  max-width: 200px;
  padding: 0.25rem 0.5rem;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.75rem;
  line-height: 1.3;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
</style>
