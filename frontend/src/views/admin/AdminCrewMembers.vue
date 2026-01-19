<template>
  <div class="admin-crew-members">
    <ListHeader
      :title="$t('admin.crewMembers.title')"
      :subtitle="$t('admin.crewMembers.subtitle')"
      v-model:viewMode="viewMode"
    />

    <ListFilters
      v-model:searchQuery="searchTerm"
      :searchPlaceholder="$t('admin.crewMembers.searchPlaceholder')"
      @clear="clearFilters"
    >
      <template #filters>
        <div class="filter-group">
          <label>{{ $t('crew.list.status') }}&nbsp;:</label>
          <select v-model="assignedFilter" class="filter-select">
            <option value="all">{{ $t('crew.list.all') }} ({{ crewMembers.length }})</option>
            <option value="assigned">{{ $t('crew.list.assigned') }} ({{ assignedCrewCount }})</option>
            <option value="unassigned">{{ $t('crew.list.unassigned') }} ({{ unassignedCrewCount }})</option>
          </select>
        </div>

        <div class="filter-group">
          <label>{{ $t('admin.crewMembers.filterByTeamManager') }}&nbsp;:</label>
          <select v-model="filterTeamManager" class="filter-select">
            <option value="">{{ $t('admin.crewMembers.allTeamManagers') }}</option>
            <option v-for="tm in teamManagers" :key="tm.id" :value="tm.id">
              {{ tm.name }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>{{ $t('admin.crewMembers.filterByClub') }}&nbsp;:</label>
          <input
            v-model="filterClub"
            type="text"
            :placeholder="$t('admin.crewMembers.clubPlaceholder')"
            class="filter-input"
          />
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

    <!-- Loading state -->
    <LoadingSpinner v-if="loading" :message="$t('common.loading')" />

    <!-- Error state -->
    <MessageAlert v-if="error" type="error" :message="error" />

    <!-- Crew members table -->
    <div v-if="!loading && !error && viewMode === 'table'" class="crew-table-container">
      <p class="count">{{ $t('admin.crewMembers.totalCount', { count: filteredCrewMembers.length }) }}</p>
      
      <SortableTable
        :columns="tableColumns"
        :data="paginatedCrewMembers"
        :initial-sort-field="'team_manager_name'"
        :initial-sort-direction="'asc'"
        aria-label="Crew members table"
      >
        <!-- Custom cell: Name -->
        <template #cell-name="{ row }">
          <div class="name-cell">
            <strong>{{ row._original.first_name }} {{ row._original.last_name }}</strong>
          </div>
        </template>

        <!-- Custom cell: Age / Category -->
        <template #cell-age_category="{ row }">
          <div class="age-category-cell">
            <span class="age">{{ row._age }} ans</span>
            <span class="category-badge" :class="`category-${row._category}`">
              {{ $t(`boat.${row._category}`) }}
              <span v-if="row._category === 'master'" class="master-letter">
                {{ row._masterLetter }}
              </span>
            </span>
          </div>
        </template>

        <!-- Custom cell: Club -->
        <template #cell-club_affiliation="{ value }">
          <span class="club-box">{{ value }}</span>
        </template>

        <!-- Custom cell: Assigned Status -->
        <template #cell-assigned="{ row }">
          <span v-if="row._original.assigned_boat_id" class="badge badge-assigned">{{ $t('crew.card.assigned') }}</span>
          <span v-else class="badge badge-unassigned">{{ $t('crew.card.unassigned') }}</span>
        </template>

        <!-- Custom cell: Team Manager -->
        <template #cell-team_manager_name="{ row }">
          <div class="team-manager-info">
            <div>{{ row._original.team_manager_name }}</div>
            <div class="email">{{ row._original.team_manager_email }}</div>
          </div>
        </template>

        <!-- Custom cell: Actions -->
        <template #cell-actions="{ row }">
          <BaseButton size="small" variant="secondary" @click="editCrewMember(row._original)">
            {{ $t('common.edit') }}
          </BaseButton>
        </template>
      </SortableTable>
    </div>

    <!-- Card View -->
    <div v-if="!loading && !error && viewMode === 'cards'" class="crew-grid">
      <div v-for="crew in paginatedCrewMembers" :key="crew.crew_member_id" class="crew-card" :class="{ 'assigned': crew.assigned_boat_id }">
        <div class="card-header">
          <div class="member-info">
            <h4>{{ crew.first_name }} {{ crew.last_name }}</h4>
            <span class="license">{{ crew.license_number }}</span>
          </div>
          <div class="badges">
            <span v-if="crew.assigned_boat_id" class="badge badge-assigned">{{ $t('crew.card.assigned') }}</span>
            <span v-else class="badge badge-unassigned">{{ $t('crew.card.unassigned') }}</span>
          </div>
        </div>

        <div class="card-body">
          <div class="detail-row">
            <span class="label">{{ $t('crew.list.age') }}&nbsp;:</span>
            <span class="value">{{ crew._age }} {{ $t('crew.card.years') }}</span>
          </div>
          <div class="detail-row">
            <span class="label">{{ $t('crew.card.category') }}&nbsp;:</span>
            <span class="value">
              <span class="category-badge" :class="`category-${crew._category}`">
                {{ $t(`boat.${crew._category}`) }}
                <span v-if="crew._category === 'master'" class="master-letter">
                  {{ crew._masterLetter }}
                </span>
              </span>
            </span>
          </div>
          <div class="detail-row">
            <span class="label">{{ $t('crew.form.gender') }}&nbsp;:</span>
            <span class="value">{{ crew.gender === 'M' ? $t('crew.form.male') : $t('crew.form.female') }}</span>
          </div>
          <div class="detail-row">
            <span class="label">{{ $t('crew.card.club') }}&nbsp;:</span>
            <span class="value">
              <span class="club-box">{{ crew.club_affiliation || crew.team_manager_club }}</span>
            </span>
          </div>
          <div class="detail-row">
            <span class="label">{{ $t('admin.crewMembers.teamManager') }}&nbsp;:</span>
            <span class="value">
              <div class="team-manager-info">
                <div>{{ crew.team_manager_name }}</div>
                <div class="email">{{ crew.team_manager_email }}</div>
              </div>
            </span>
          </div>
        </div>

        <div class="card-actions">
          <BaseButton size="small" variant="secondary" @click="editCrewMember(crew)">
            {{ $t('common.edit') }}
          </BaseButton>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && !error && totalPages > 1" class="pagination">
      <BaseButton size="small" variant="secondary" @click="currentPage--" :disabled="currentPage === 1">
        {{ $t('common.previous') }}
      </BaseButton>
      <span class="page-info">
        {{ $t('common.pageInfo', { current: currentPage, total: totalPages }) }}
      </span>
      <BaseButton size="small" variant="secondary" @click="currentPage++" :disabled="currentPage === totalPages">
        {{ $t('common.next') }}
      </BaseButton>
    </div>

    <!-- Edit Crew Member Modal -->
    <BaseModal :show="showEditCrewModal" :title="$t('admin.crewMembers.editCrewMember')" @close="closeModals">
      <template #default>
        <div v-if="modalError" class="error-message">{{ modalError }}</div>

        <form @submit.prevent="saveCrewMember">
          <div class="form-row">
            <div class="form-group">
              <label>{{ $t('crew.form.firstName') }} *</label>
              <input v-model="crewForm.first_name" type="text" required class="form-control" />
            </div>

            <div class="form-group">
              <label>{{ $t('crew.form.lastName') }} *</label>
              <input v-model="crewForm.last_name" type="text" required class="form-control" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>{{ $t('crew.card.dateOfBirth') }} *</label>
              <input v-model="crewForm.date_of_birth" type="date" required class="form-control" />
            </div>

            <div class="form-group">
              <label>{{ $t('crew.form.gender') }} *</label>
              <select v-model="crewForm.gender" required class="form-control">
                <option value="">{{ $t('crew.form.selectGender') }}</option>
                <option value="M">{{ $t('crew.form.male') }}</option>
                <option value="F">{{ $t('crew.form.female') }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>{{ $t('crew.form.licenseNumber') }} *</label>
            <input v-model="crewForm.license_number" type="text" required class="form-control" maxlength="24" placeholder="ABC123456" />
          </div>

          <div class="form-group">
            <label>{{ $t('crew.form.clubAffiliation') }}</label>
            <input v-model="crewForm.club_affiliation" type="text" class="form-control" />
            <small class="form-text">{{ $t('crew.form.clubHint') }}</small>
          </div>
        </form>
      </template>
      
      <template #footer>
        <BaseButton variant="secondary" @click="closeModals">{{ $t('common.cancel') }}</BaseButton>
        <BaseButton variant="primary" @click="saveCrewMember" :disabled="saving">
          {{ saving ? $t('common.saving') : $t('common.save') }}
        </BaseButton>
      </template>
    </BaseModal>

    <!-- Delete Confirmation Modal -->
    <BaseModal v-if="showDeleteModal" :show="showDeleteModal" :title="$t('admin.crewMembers.confirmDelete')" size="small" @close="showDeleteModal = false">
      <template #default>
        <p>{{ $t('admin.crewMembers.confirmDeleteMessage', { name: `${crewToDelete?.first_name} ${crewToDelete?.last_name}` }) }}</p>
        <div v-if="modalError" class="error-message">{{ modalError }}</div>
      </template>
      
      <template #footer>
        <BaseButton variant="secondary" @click="showDeleteModal = false">{{ $t('common.cancel') }}</BaseButton>
        <BaseButton variant="danger" @click="deleteCrewMember" :disabled="deleting">
          {{ deleting ? $t('common.deleting') : $t('common.delete') }}
        </BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import apiClient from '../../services/apiClient';
import { calculateAge, getAgeCategory, getMasterCategory } from '../../utils/raceEligibility';
import SortableTable from '../../components/composite/SortableTable.vue';
import ListHeader from '../../components/shared/ListHeader.vue';
import ListFilters from '../../components/shared/ListFilters.vue';
import BaseButton from '../../components/base/BaseButton.vue';
import BaseModal from '../../components/base/BaseModal.vue';
import LoadingSpinner from '../../components/base/LoadingSpinner.vue';
import MessageAlert from '../../components/composite/MessageAlert.vue';

export default {
  name: 'AdminCrewMembers',
  components: {
    SortableTable,
    ListHeader,
    ListFilters,
    BaseButton,
    BaseModal,
    LoadingSpinner,
    MessageAlert
  },
  setup() {
    const { t } = useI18n();

    // State
    const crewMembers = ref([]);
    const teamManagers = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const searchTerm = ref('');
    const filterClub = ref('');
    const filterTeamManager = ref('');
    const categoryFilter = ref('all');
    const assignedFilter = ref('all');
    const currentPage = ref(1);
    const itemsPerPage = 50;
    const viewMode = ref(localStorage.getItem('adminCrewViewMode') || 'table');

    // Modal state
    const showEditCrewModal = ref(false);
    const showDeleteModal = ref(false);
    const crewToDelete = ref(null);
    const crewToEdit = ref(null);
    const modalError = ref(null);
    const saving = ref(false);
    const deleting = ref(false);

    // Form state
    const crewForm = ref({
      first_name: '',
      last_name: '',
      date_of_birth: '',
      gender: '',
      license_number: '',
      club_affiliation: ''
    });

    // Computed
    const assignedCrewCount = computed(() => {
      return crewMembers.value.filter(crew => crew.assigned_boat_id).length;
    });

    const unassignedCrewCount = computed(() => {
      return crewMembers.value.filter(crew => !crew.assigned_boat_id).length;
    });

    const filteredCrewMembers = computed(() => {
      let filtered = crewMembers.value;

      // Apply assigned filter
      if (assignedFilter.value === 'assigned') {
        filtered = filtered.filter(crew => crew.assigned_boat_id);
      } else if (assignedFilter.value === 'unassigned') {
        filtered = filtered.filter(crew => !crew.assigned_boat_id);
      }

      // Apply search filter
      if (searchTerm.value) {
        const search = searchTerm.value.toLowerCase();
        filtered = filtered.filter(crew =>
          crew.first_name?.toLowerCase().includes(search) ||
          crew.last_name?.toLowerCase().includes(search) ||
          crew.license_number?.toLowerCase().includes(search) ||
          crew.team_manager_name?.toLowerCase().includes(search)
        );
      }

      // Apply club filter - only filter by crew member's club affiliation
      if (filterClub.value && filterClub.value.trim()) {
        const club = filterClub.value.toLowerCase().trim();
        
        filtered = filtered.filter(crew => {
          // Only check the crew member's own club affiliation
          const crewClub = (crew.club_affiliation || '').toLowerCase().trim();
          
          // Match if search term appears anywhere in the crew member's club name
          return crewClub.includes(club);
        });
      }

      // Apply team manager filter
      if (filterTeamManager.value) {
        filtered = filtered.filter(crew =>
          crew.team_manager_id === filterTeamManager.value
        );
      }

      // Apply category filter
      if (categoryFilter.value !== 'all') {
        filtered = filtered.filter(crew => {
          const age = calculateAge(crew.date_of_birth);
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

      return filtered;
    });

    // Column definitions for SortableTable
    const tableColumns = computed(() => [
      {
        key: 'name',
        label: 'Nom',
        sortable: true,
        minWidth: '150px',
        sticky: 'left',
        responsive: 'always'
      },
      {
        key: 'age_category',
        label: `${t('crew.list.age')} / ${t('crew.card.category')}`,
        sortable: false,
        width: '150px',
        responsive: 'always'
      },
      {
        key: 'gender',
        label: t('crew.form.gender'),
        sortable: false,
        width: '100px',
        responsive: 'hide-below-1024'
      },
      {
        key: 'license_number',
        label: t('crew.form.licenseNumber'),
        sortable: false,
        minWidth: '120px',
        responsive: 'hide-below-1024'
      },
      {
        key: 'club_affiliation',
        label: t('crew.card.club'),
        sortable: true,
        minWidth: '150px',
        responsive: 'always'
      },
      {
        key: 'assigned',
        label: t('crew.card.assigned'),
        sortable: false,
        width: '120px',
        align: 'center',
        responsive: 'always'
      },
      {
        key: 'team_manager_name',
        label: t('admin.crewMembers.teamManager'),
        sortable: true,
        minWidth: '180px',
        responsive: 'hide-below-1024'
      },
      {
        key: 'actions',
        label: t('common.actions'),
        sortable: false,
        width: '120px',
        align: 'right',
        sticky: 'right',
        responsive: 'always'
      }
    ]);

    // Prepare data for SortableTable with computed fields
    const tableData = computed(() => {
      return filteredCrewMembers.value.map(crew => ({
        ...crew,
        _original: crew,
        name: `${crew.first_name} ${crew.last_name}`,
        _age: calculateAge(crew.date_of_birth),
        _category: getAgeCategory(calculateAge(crew.date_of_birth)),
        _masterLetter: getMasterCategory(calculateAge(crew.date_of_birth)),
        age_category: `${calculateAge(crew.date_of_birth)} ans`,
        gender: crew.gender === 'M' ? t('crew.form.male') : t('crew.form.female'),
        club_affiliation: crew.club_affiliation || crew.team_manager_club,
        assigned: crew.assigned_boat_id ? 'assigned' : 'unassigned'
      }));
    });

    // Use table sort composable - removed, now handled by SortableTable

    const totalPages = computed(() => {
      return Math.ceil(tableData.value.length / itemsPerPage);
    });

    const paginatedCrewMembers = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage;
      const end = start + itemsPerPage;
      return tableData.value.slice(start, end);
    });

    // Methods
    const fetchCrewMembers = async () => {
      loading.value = true;
      error.value = null;

      try {
        const response = await apiClient.get('/admin/crew');
        crewMembers.value = response.data.data.crew_members || [];
        
        // Extract unique team managers
        const tmMap = new Map();
        crewMembers.value.forEach(crew => {
          if (crew.team_manager_id && !tmMap.has(crew.team_manager_id)) {
            tmMap.set(crew.team_manager_id, {
              id: crew.team_manager_id,
              name: crew.team_manager_name,
              email: crew.team_manager_email
            });
          }
        });
        teamManagers.value = Array.from(tmMap.values()).sort((a, b) => 
          a.name.localeCompare(b.name)
        );
      } catch (err) {
        console.error('Failed to fetch crew members:', err);
        error.value = t('admin.crewMembers.fetchError');
      } finally {
        loading.value = false;
      }
    };

    const clearFilters = () => {
      searchTerm.value = '';
      filterClub.value = '';
      filterTeamManager.value = '';
      categoryFilter.value = 'all';
      assignedFilter.value = 'all';
      currentPage.value = 1;
    };

    const getAgeCategoryForMember = (dateOfBirth) => {
      const age = calculateAge(dateOfBirth);
      return getAgeCategory(age);
    };

    const getMasterCategoryLetter = (dateOfBirth) => {
      const age = calculateAge(dateOfBirth);
      return getMasterCategory(age);
    };

    const formatDate = (dateStr) => {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return date.toLocaleDateString();
    };

    const editCrewMember = (crew) => {
      crewToEdit.value = crew;
      crewForm.value = {
        first_name: crew.first_name,
        last_name: crew.last_name,
        date_of_birth: crew.date_of_birth,
        gender: crew.gender,
        license_number: crew.license_number,
        club_affiliation: crew.club_affiliation || ''
      };
      showEditCrewModal.value = true;
      modalError.value = null;
    };

    const confirmDelete = (crew) => {
      crewToDelete.value = crew;
      showDeleteModal.value = true;
      modalError.value = null;
    };

    const closeModals = () => {
      showEditCrewModal.value = false;
      showDeleteModal.value = false;
      crewToEdit.value = null;
      crewToDelete.value = null;
      modalError.value = null;
      crewForm.value = {
        first_name: '',
        last_name: '',
        date_of_birth: '',
        gender: '',
        license_number: '',
        club_affiliation: ''
      };
    };

    const saveCrewMember = async () => {
      modalError.value = null;
      saving.value = true;

      try {
        // Update existing crew member
        await apiClient.put(
          `/admin/crew/${crewToEdit.value.team_manager_id}/${crewToEdit.value.crew_member_id}`,
          crewForm.value
        );

        closeModals();
        await fetchCrewMembers();
      } catch (err) {
        console.error('Failed to save crew member:', err);
        modalError.value = err.response?.data?.error?.message || t('admin.crewMembers.saveError');
      } finally {
        saving.value = false;
      }
    };

    const deleteCrewMember = async () => {
      modalError.value = null;
      deleting.value = true;

      try {
        await apiClient.delete(
          `/admin/crew/${crewToDelete.value.team_manager_id}/${crewToDelete.value.crew_member_id}`
        );
        closeModals();
        await fetchCrewMembers();
      } catch (err) {
        console.error('Failed to delete crew member:', err);
        modalError.value = err.response?.data?.error?.message || t('admin.crewMembers.deleteError');
      } finally {
        deleting.value = false;
      }
    };

    // Lifecycle
    onMounted(() => {
      fetchCrewMembers();
    });

    // Watch for view mode changes and save to localStorage
    watch(viewMode, (newMode) => {
      localStorage.setItem('adminCrewViewMode', newMode);
    });

    return {
      crewMembers,
      teamManagers,
      loading,
      error,
      searchTerm,
      filterClub,
      filterTeamManager,
      categoryFilter,
      assignedFilter,
      currentPage,
      totalPages,
      viewMode,
      assignedCrewCount,
      unassignedCrewCount,
      filteredCrewMembers,
      paginatedCrewMembers,
      tableColumns,
      tableData,
      showEditCrewModal,
      showDeleteModal,
      crewToDelete,
      crewForm,
      modalError,
      saving,
      deleting,
      fetchCrewMembers,
      clearFilters,
      formatDate,
      editCrewMember,
      confirmDelete,
      closeModals,
      saveCrewMember,
      deleteCrewMember,
      calculateAge,
      getAgeCategoryForMember,
      getMasterCategoryLetter
    };
  }
};
</script>

<style scoped>
@import '@/assets/design-tokens.css';

.admin-crew-members {
  padding: var(--spacing-xl);
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
  color: var(--color-muted);
  font-size: var(--font-size-sm);
}

.filter-select,
.filter-input {
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: var(--font-size-sm);
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: var(--spacing-lg);
  border-radius: 4px;
  margin-bottom: var(--spacing-lg);
}

.crew-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.count {
  padding: var(--spacing-lg);
  background: var(--color-light);
  border-bottom: 1px solid var(--color-border);
  font-weight: var(--font-weight-semibold);
  color: var(--color-muted);
}

/* Custom cell styling */
.name-cell strong {
  color: var(--color-dark, #2c3e50);
}

.age-category-cell {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 0.5rem);
}

.age {
  color: var(--color-muted, #666);
  font-size: var(--font-size-base, 0.9rem);
  white-space: nowrap;
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

.team-manager-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.email {
  font-size: var(--font-size-sm);
  color: var(--color-secondary);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

.page-info {
  color: var(--color-muted);
}

.btn-primary,
.btn-secondary,
.btn-danger {
  padding: var(--spacing-sm) var(--spacing-lg);
  border: none;
  border-radius: 4px;
  font-size: var(--font-size-base);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-secondary {
  background: var(--color-secondary);
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

.btn-danger {
  background: var(--color-danger);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c82333;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal styles */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-muted);
}

.form-control {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: var(--font-size-base);
}

.form-control:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-text {
  display: block;
  margin-top: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--color-secondary);
}

@media (max-width: 768px) {
  .admin-crew-members {
    padding: var(--spacing-lg);
  }

  .filter-group {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }

  .filter-group label {
    margin-bottom: var(--spacing-xs);
  }

  .filter-select,
  .filter-input {
    width: 100%;
    font-size: 16px;
    min-height: 44px;
  }

  .pagination {
    flex-wrap: wrap;
    gap: var(--spacing-sm);
  }

  .page-info {
    width: 100%;
    text-align: center;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .form-control {
    font-size: 16px;
    min-height: 44px;
  }
}

@media (min-width: 768px) {
  /* Table view handled by SortableTable component */
}

.team-manager-select {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
  border: 2px solid #dee2e6;
}

.checkbox-group {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
}

.checkbox-group input[type="checkbox"] {
  width: auto;
  margin-right: 0.5rem;
}

.checkbox-label {
  margin-bottom: 0;
  font-weight: normal;
  cursor: pointer;
}

.autocomplete-wrapper {
  position: relative;
}

.autocomplete-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 300px;
  overflow-y: auto;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  z-index: 1000;
}

.autocomplete-item {
  padding: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
}

.autocomplete-item:hover {
  background-color: #f5f5f5;
}

.autocomplete-item:last-child {
  border-bottom: none;
}

.club-name {
  font-weight: 500;
  color: #333;
}

.autocomplete-no-results {
  padding: 0.75rem;
  color: #666;
  font-style: italic;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 4px 4px;
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

.name-cell strong {
  color: var(--color-dark, #2c3e50);
}

.age-category-cell {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 0.5rem);
}

.age {
  color: var(--color-muted, #666);
  font-size: var(--font-size-base, 0.9rem);
  white-space: nowrap;
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

/* Card View Styles */
.crew-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-xl, 1.5rem);
  padding: var(--spacing-lg, 1rem) 0;
}

.crew-card {
  background: white;
  border: 2px solid var(--color-border, #e0e0e0);
  border-radius: 8px;
  padding: var(--spacing-xl, 1.5rem);
  transition: all 0.3s;
}

.crew-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.crew-card.assigned {
  border-left: 4px solid var(--color-success, #4CAF50);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-lg, 1rem);
  padding-bottom: var(--spacing-lg, 1rem);
  border-bottom: 1px solid var(--color-border, #e0e0e0);
}

.member-info h4 {
  margin: 0 0 var(--spacing-xs, 0.25rem) 0;
  color: var(--color-dark, #333);
  font-size: var(--font-size-xl, 1.25rem);
}

.license {
  color: var(--color-muted, #666);
  font-size: var(--font-size-sm, 0.875rem);
  font-family: monospace;
}

.badges {
  display: flex;
  gap: var(--spacing-sm, 0.5rem);
  flex-wrap: wrap;
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

.card-body {
  margin-bottom: var(--spacing-lg, 1rem);
}

.detail-row {
  display: flex;
  padding: var(--spacing-sm, 0.5rem) 0;
  border-bottom: 1px solid var(--color-light, #f5f5f5);
  align-items: flex-start;
}

.detail-row:last-child {
  border-bottom: none;
}

.label {
  font-weight: var(--font-weight-medium, 500);
  color: var(--color-muted, #666);
  min-width: 120px;
  max-width: 120px;
  flex-shrink: 0;
  word-wrap: break-word;
  line-height: 1.4;
}

.value {
  color: var(--color-dark, #333);
  flex: 1;
}

.card-actions {
  display: flex;
  gap: var(--spacing-sm, 0.5rem);
  padding-top: var(--spacing-lg, 1rem);
  border-top: 1px solid var(--color-border, #e0e0e0);
}

.team-manager-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs, 0.25rem);
}

.team-manager-info .email {
  font-size: var(--font-size-sm, 0.85rem);
  color: var(--color-secondary, #6c757d);
  word-break: break-all;
  overflow-wrap: break-word;
}
</style>
