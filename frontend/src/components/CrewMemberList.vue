<template>
  <div class="crew-member-list">
    <ListHeader
      :title="$t('crew.list.title')"
      :subtitle="$t('crew.list.subtitle')"
      v-model:viewMode="viewMode"
    >
      <template #action>
        <BaseButton 
          variant="primary"
          :disabled="!canCreateCrewMember"
          :title="createCrewMemberTooltip"
          @click="showCreateForm = true"
        >
          {{ $t('crew.list.addNew') }}
        </BaseButton>
      </template>
    </ListHeader>

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
      </template>
    </ListFilters>

    <!-- Loading State -->
    <LoadingSpinner v-if="crewStore.loading" :message="$t('common.loading')" />

    <!-- Error State -->
    <div v-else-if="crewStore.error" class="alert alert-error">
      {{ crewStore.error }}
    </div>

    <!-- Empty State -->
    <EmptyState 
      v-else-if="filteredCrewMembers.length === 0" 
      :message="$t('crew.list.noMembers')"
    >
      <template #action>
        <BaseButton 
          variant="primary"
          :disabled="!canCreateCrewMember"
          :title="createCrewMemberTooltip"
          @click="showCreateForm = true"
        >
          {{ $t('crew.list.addFirst') }}
        </BaseButton>
      </template>
    </EmptyState>

    <!-- Card View -->
    <div v-else-if="viewMode === 'cards'" class="crew-grid">
      <CrewMemberCard
        v-for="member in sortedCrewMembers"
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
            <th class="sortable-header" @click="handleSort('first_name')">
              {{ $t('crew.form.firstName') }} {{ getSortIndicator('first_name') }}
            </th>
            <th class="sortable-header" @click="handleSort('last_name')">
              {{ $t('crew.form.lastName') }} {{ getSortIndicator('last_name') }}
            </th>
            <th class="sortable-header" @click="handleSort('date_of_birth')">
              {{ $t('crew.list.age') }} {{ getSortIndicator('date_of_birth') }}
            </th>
            <th class="sortable-header" @click="handleSort('gender')">
              {{ $t('crew.form.gender') }} {{ getSortIndicator('gender') }}
            </th>
            <th>{{ $t('crew.card.category') }}</th>
            <th class="sortable-header" @click="handleSort('club_affiliation')">
              {{ $t('crew.card.club') }} {{ getSortIndicator('club_affiliation') }}
            </th>
            <th class="sortable-header" @click="handleSort('assigned_boat_id')">
              {{ $t('crew.card.assigned') }} {{ getSortIndicator('assigned_boat_id') }}
            </th>
            <th>{{ $t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="member in sortedCrewMembers" 
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
              <span v-if="member.assigned_boat_id" class="badge badge-assigned">{{ $t('crew.card.assigned') }}</span>
              <span v-else class="badge badge-unassigned">{{ $t('crew.card.unassigned') }}</span>
            </td>
            <td class="actions-cell">
              <BaseButton 
                size="small" 
                variant="secondary"
                :disabled="!canEditMember(member)"
                :title="getEditTooltip(member)"
                @click="handleEdit(member)"
              >
                {{ $t('common.edit') }}
              </BaseButton>
              <BaseButton 
                size="small" 
                variant="danger"
                :disabled="!canDeleteMember(member)"
                :title="getDeleteTooltip(member)"
                @click="handleDelete(member)"
              >
                {{ $t('common.delete') }}
              </BaseButton>
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

    <!-- Delete Error Message (shown after confirmation dialog) -->
    <MessageAlert
      v-if="deleteError"
      type="error"
      :message="deleteError"
      :dismissible="true"
      @dismiss="deleteError = ''"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useCrewStore } from '../stores/crewStore';
import { calculateAge, getAgeCategory, getMasterCategory } from '../utils/raceEligibility';
import { useTableSort } from '../composables/useTableSort';
import { usePermissions } from '../composables/usePermissions';
import { useConfirm } from '../composables/useConfirm';
import CrewMemberCard from './CrewMemberCard.vue';
import CrewMemberForm from './CrewMemberForm.vue';
import ListHeader from './shared/ListHeader.vue';
import ListFilters from './shared/ListFilters.vue';
import BaseButton from './base/BaseButton.vue';
import LoadingSpinner from './base/LoadingSpinner.vue';
import EmptyState from './base/EmptyState.vue';
import MessageAlert from './composite/MessageAlert.vue';

const { t } = useI18n();
const crewStore = useCrewStore();
const { canPerformAction, getPermissionMessage, initialize: initializePermissions, loading: permissionsLoading } = usePermissions();
const { confirm } = useConfirm();

const searchQuery = ref('');
const filter = ref('all');
const genderFilter = ref('all');
const categoryFilter = ref('all');

// Computed: count of unassigned crew members
const unassignedCount = computed(() => {
  return crewStore.crewMembers.filter(member => !member.assigned_boat_id).length;
});
// Load view mode from localStorage or default to 'cards'
const viewMode = ref(localStorage.getItem('crewViewMode') || 'cards');
const showCreateForm = ref(false);
const editingMember = ref(null);
const deleting = ref(false);
const deleteError = ref('');

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

// Permission check helper for table rows
const canEditMember = (member) => {
  if (permissionsLoading.value) return false;
  const resourceContext = {
    resource_type: 'crew_member',
    resource_id: member.crew_member_id,
    resource_state: {
      assigned: !!member.assigned_boat_id
    }
  };
  return canPerformAction('edit_crew_member', resourceContext);
};

const canDeleteMember = (member) => {
  if (permissionsLoading.value) return false;
  const resourceContext = {
    resource_type: 'crew_member',
    resource_id: member.crew_member_id,
    resource_state: {
      assigned: !!member.assigned_boat_id
    }
  };
  return canPerformAction('delete_crew_member', resourceContext);
};

const getEditTooltip = (member) => {
  if (canEditMember(member)) return '';
  const resourceContext = {
    resource_type: 'crew_member',
    resource_id: member.crew_member_id,
    resource_state: {
      assigned: !!member.assigned_boat_id
    }
  };
  return getPermissionMessage('edit_crew_member', resourceContext);
};

const getDeleteTooltip = (member) => {
  if (canDeleteMember(member)) return '';
  const resourceContext = {
    resource_type: 'crew_member',
    resource_id: member.crew_member_id,
    resource_state: {
      assigned: !!member.assigned_boat_id
    }
  };
  return getPermissionMessage('delete_crew_member', resourceContext);
};

// Load crew members on mount
onMounted(async () => {
  // Initialize permissions
  await initializePermissions();
  
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

// Filtered crew members (without sorting - sorting handled by useTableSort)
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

  return members;
});

// Use table sort composable for sorting
const filteredCrewMembersRef = computed(() => filteredCrewMembers.value);
const { sortedData: sortedCrewMembers, sortBy: handleSort, getSortIndicator } = useTableSort(
  filteredCrewMembersRef,
  'last_name',
  'asc'
);

const handleEdit = (member) => {
  editingMember.value = member;
};

const handleDelete = async (member) => {
  // Prevent multiple simultaneous delete operations
  if (deleting.value) {
    console.log('Delete already in progress, ignoring duplicate request');
    return;
  }

  const confirmed = await confirm({
    title: t('crew.delete.title'),
    message: t('crew.delete.message', { name: `${member.first_name} ${member.last_name}` }),
    confirmText: t('crew.delete.confirm'),
    cancelText: t('common.cancel'),
    variant: 'danger'
  });

  if (!confirmed) {
    return;
  }

  deleteError.value = '';
  deleting.value = true;
  
  try {
    await crewStore.deleteCrewMember(member.crew_member_id);
  } catch (error) {
    console.error('Failed to delete crew member:', error);
    deleteError.value = t('crew.list.deleteError');
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

// Permission check for creating crew members
const canCreateCrewMember = computed(() => {
  if (permissionsLoading.value) return false;
  return canPerformAction('create_crew_member', {
    resource_type: 'crew_member'
  });
});

const createCrewMemberTooltip = computed(() => {
  if (canCreateCrewMember.value) return '';
  return getPermissionMessage('create_crew_member', {
    resource_type: 'crew_member'
  });
});
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
  gap: var(--spacing-sm, 0.5rem);
}

.filter-group label {
  font-weight: var(--font-weight-medium, 500);
  white-space: nowrap;
}

.filter-select {
  padding: var(--spacing-sm, 0.5rem);
  border: 1px solid var(--color-border, #ddd);
  border-radius: 4px;
  background: white;
  cursor: pointer;
  min-width: 120px;
}

.sort-select {
  padding: var(--spacing-sm, 0.5rem);
  border: 1px solid var(--color-border, #ddd);
  border-radius: 4px;
}

.loading {
  text-align: center;
  padding: var(--spacing-2xl, 2rem);
  color: var(--color-muted, #666);
}

.alert-error {
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ef5350;
  padding: var(--spacing-lg, 1rem);
  border-radius: 4px;
  margin-bottom: var(--spacing-lg, 1rem);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl, 2rem);
  background: white;
  border-radius: 8px;
}

.empty-state p {
  color: var(--color-muted, #666);
  margin-bottom: var(--spacing-lg, 1rem);
}

.crew-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--spacing-xl, 1.5rem);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--modal-overlay-bg, rgba(0,0,0,0.5));
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-index-modal-backdrop, 900);
  padding: var(--spacing-lg, 1rem);
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
  padding: var(--spacing-2xl, 2rem);
}

.modal-small h3 {
  margin-top: 0;
  color: var(--color-dark, #333);
}

.button-group {
  display: flex;
  gap: var(--spacing-lg, 1rem);
  margin-top: var(--spacing-xl, 1.5rem);
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
  background-color: var(--color-light, #f8f9fa);
}

.crew-table th {
  padding: var(--spacing-lg, 1rem);
  text-align: left;
  font-weight: var(--font-weight-semibold, 600);
  color: #495057;
  border-bottom: 2px solid var(--color-border, #dee2e6);
}

.sortable-header {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease;
}

.sortable-header:hover {
  background-color: var(--color-bg-hover, rgba(0, 0, 0, 0.05));
}

.crew-table td {
  padding: var(--spacing-lg, 1rem);
  border-bottom: 1px solid var(--color-border, #dee2e6);
}

.crew-table tbody tr:hover {
  background-color: var(--color-light, #f8f9fa);
}

.crew-table tbody tr.row-assigned {
  border-left: 4px solid var(--color-success, #4CAF50);
}

.crew-table tbody tr.row-flagged {
  border-left: 4px solid var(--color-warning, #ffc107);
}

.badge {
  display: inline-block;
  padding: var(--badge-padding, 0.25rem 0.75rem);
  border-radius: var(--badge-border-radius, 12px);
  font-size: var(--badge-font-size, 0.75rem);
  font-weight: var(--badge-font-weight, 500);
}

.badge-assigned {
  background-color: var(--color-success, #28a745);
  color: white;
}

.badge-unassigned {
  background-color: var(--color-warning, #ffc107);
  color: var(--color-dark, #212529);
}

.actions-cell {
  display: flex;
  gap: var(--spacing-sm, 0.5rem);
  flex-direction: column;
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
    gap: var(--spacing-lg, 1rem);
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
    padding: var(--spacing-sm, 0.5rem);
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
    padding: var(--spacing-xl, 1.5rem);
    max-width: 100%;
    width: 100%;
  }

  .button-group {
    flex-direction: column;
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
  padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
  border-radius: 8px;
  font-size: var(--font-size-sm, 0.7rem);
  font-weight: var(--font-weight-semibold, 600);
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
  margin-left: var(--spacing-xs, 0.25rem);
  font-weight: 700;
}

.club-box {
  display: inline-block;
  max-width: 200px;
  padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
  background-color: var(--color-light, #f5f5f5);
  border: 1px solid var(--color-border, #ddd);
  border-radius: 4px;
  font-size: var(--font-size-sm, 0.75rem);
  line-height: 1.3;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
</style>
