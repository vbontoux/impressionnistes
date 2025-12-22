<template>
  <div class="admin-crew-members">
    <div class="list-header">
      <div>
        <h1>{{ $t('admin.crewMembers.title') }}</h1>
        <p class="subtitle">{{ $t('admin.crewMembers.subtitle') }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="search-box">
        <input
          v-model="searchTerm"
          type="text"
          :placeholder="$t('admin.crewMembers.searchPlaceholder')"
          class="search-input"
        />
      </div>

      <div class="filter-row">
        <button 
          :class="['filter-btn', { active: assignedFilter === 'all' }]"
          @click="assignedFilter = 'all'"
        >
          {{ $t('crew.list.all') }} ({{ crewMembers.length }})
        </button>
        <button 
          :class="['filter-btn', { active: assignedFilter === 'assigned' }]"
          @click="assignedFilter = 'assigned'"
        >
          {{ $t('crew.list.assigned') }} ({{ assignedCrewCount }})
        </button>
        <button 
          :class="['filter-btn', { active: assignedFilter === 'unassigned' }]"
          @click="assignedFilter = 'unassigned'"
        >
          {{ $t('crew.list.unassigned') }} ({{ unassignedCrewCount }})
        </button>

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

        <button @click="clearFilters" class="filter-btn">
          {{ $t('admin.crewMembers.clearFilters') }}
        </button>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <!-- Error state -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- Crew members table -->
    <div v-if="!loading && !error" class="crew-table-container">
      <p class="count">{{ $t('admin.crewMembers.totalCount', { count: filteredCrewMembers.length }) }}</p>
      
      <table class="crew-table">
        <thead>
          <tr>
            <th @click="sortBy('last_name')">
              Nom
              <span v-if="sortField === 'last_name'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
            </th>
            <th>{{ $t('crew.list.age') }} / {{ $t('crew.card.category') }}</th>
            <th>{{ $t('crew.form.gender') }}</th>
            <th>{{ $t('crew.form.licenseNumber') }}</th>
            <th @click="sortBy('club_affiliation')">
              {{ $t('crew.card.club') }}
              <span v-if="sortField === 'club_affiliation'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
            </th>
            <th>{{ $t('crew.card.assigned') }}</th>
            <th @click="sortBy('team_manager_name')">
              {{ $t('admin.crewMembers.teamManager') }}
              <span v-if="sortField === 'team_manager_name'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
            </th>
            <th>{{ $t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="crew in paginatedCrewMembers" :key="crew.crew_member_id">
            <td>
              <div class="name-cell">
                <strong>{{ crew.first_name }} {{ crew.last_name }}</strong>
              </div>
            </td>
            <td>
              <div class="age-category-cell">
                <span class="age">{{ crew._age }} ans</span>
                <span class="category-badge" :class="`category-${crew._category}`">
                  {{ $t(`boat.${crew._category}`) }}
                  <span v-if="crew._category === 'master'" class="master-letter">
                    {{ crew._masterLetter }}
                  </span>
                </span>
              </div>
            </td>
            <td>{{ crew.gender === 'M' ? $t('crew.form.male') : $t('crew.form.female') }}</td>
            <td>{{ crew.license_number }}</td>
            <td><span class="club-box">{{ crew.club_affiliation || crew.team_manager_club }}</span></td>
            <td>
              <span v-if="crew.assigned_boat_id" class="assigned-badge">✓</span>
              <span v-else>-</span>
            </td>
            <td>
              <div class="team-manager-info">
                <div>{{ crew.team_manager_name }}</div>
                <div class="email">{{ crew.team_manager_email }}</div>
              </div>
            </td>
            <td class="actions-cell">
              <button @click="editCrewMember(crew)" class="btn-table btn-edit-table">
                {{ $t('common.edit') }}
              </button>
              <!-- Delete button hidden to prevent accidental deletions -->
              <!-- <button @click="confirmDelete(crew)" class="btn-table btn-delete-table">
                {{ $t('common.delete') }}
              </button> -->
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button @click="currentPage--" :disabled="currentPage === 1" class="btn-secondary">
          {{ $t('common.previous') }}
        </button>
        <span class="page-info">
          {{ $t('common.pageInfo', { current: currentPage, total: totalPages }) }}
        </span>
        <button @click="currentPage++" :disabled="currentPage === totalPages" class="btn-secondary">
          {{ $t('common.next') }}
        </button>
      </div>
    </div>

    <!-- Edit Crew Member Modal -->
    <div v-if="showEditCrewModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ $t('admin.crewMembers.editCrewMember') }}</h2>
          <button @click="closeModals" class="close-btn">&times;</button>
        </div>

        <div class="modal-body">
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
              <input v-model="crewForm.license_number" type="text" required class="form-control" maxlength="12" placeholder="ABC123456" />
            </div>

            <div class="form-group">
              <label>{{ $t('crew.form.clubAffiliation') }}</label>
              <input v-model="crewForm.club_affiliation" type="text" class="form-control" />
              <small class="form-text">{{ $t('crew.form.clubHint') }}</small>
            </div>

            <div class="modal-footer">
              <button type="button" @click="closeModals" class="btn-secondary">{{ $t('common.cancel') }}</button>
              <button type="submit" class="btn-primary" :disabled="saving">
                {{ saving ? $t('common.saving') : $t('common.save') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal modal-small">
        <div class="modal-header">
          <h2>{{ $t('admin.crewMembers.confirmDelete') }}</h2>
          <button @click="showDeleteModal = false" class="close-btn">&times;</button>
        </div>

        <div class="modal-body">
          <p>{{ $t('admin.crewMembers.confirmDeleteMessage', { name: `${crewToDelete?.first_name} ${crewToDelete?.last_name}` }) }}</p>
          <div v-if="modalError" class="error-message">{{ modalError }}</div>
        </div>

        <div class="modal-footer">
          <button @click="showDeleteModal = false" class="btn-secondary">{{ $t('common.cancel') }}</button>
          <button @click="deleteCrewMember" class="btn-danger" :disabled="deleting">
            {{ deleting ? $t('common.deleting') : $t('common.delete') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import apiClient from '../../services/apiClient';
import { calculateAge, getAgeCategory, getMasterCategory } from '../../utils/raceEligibility';

export default {
  name: 'AdminCrewMembers',
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
    const sortField = ref('team_manager_name');
    const sortDirection = ref('asc');
    const currentPage = ref(1);
    const itemsPerPage = 50;

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

      // Apply sorting - create a copy to avoid mutating the original array
      const sorted = [...filtered].sort((a, b) => {
        let aVal = a[sortField.value] || '';
        let bVal = b[sortField.value] || '';
        
        if (typeof aVal === 'string') {
          aVal = aVal.toLowerCase();
          bVal = bVal.toLowerCase();
        }

        if (sortDirection.value === 'asc') {
          return aVal > bVal ? 1 : -1;
        } else {
          return aVal < bVal ? 1 : -1;
        }
      });

      return sorted;
    });

    const totalPages = computed(() => {
      return Math.ceil(filteredCrewMembers.value.length / itemsPerPage);
    });

    const paginatedCrewMembers = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage;
      const end = start + itemsPerPage;
      const paginated = filteredCrewMembers.value.slice(start, end);
      
      // Pre-calculate age and category for each crew member to avoid repeated calculations in template
      return paginated.map(crew => ({
        ...crew,
        _age: calculateAge(crew.date_of_birth),
        _category: getAgeCategory(calculateAge(crew.date_of_birth)),
        _masterLetter: getMasterCategory(calculateAge(crew.date_of_birth))
      }));
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

    const sortBy = (field) => {
      if (sortField.value === field) {
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
      } else {
        sortField.value = field;
        sortDirection.value = 'asc';
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
      sortField,
      sortDirection,
      currentPage,
      totalPages,
      assignedCrewCount,
      unassignedCrewCount,
      filteredCrewMembers,
      paginatedCrewMembers,
      showEditCrewModal,
      showDeleteModal,
      crewToDelete,
      crewForm,
      modalError,
      saving,
      deleting,
      fetchCrewMembers,
      sortBy,
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
.admin-crew-members {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.list-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.subtitle {
  color: #7f8c8d;
  font-size: 1rem;
  margin: 0;
}

.filters {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.search-box {
  margin-bottom: 0.75rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.filter-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.filter-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-btn:hover {
  background: #f5f5f5;
}

.filter-btn.active {
  background: #4CAF50;
  color: white;
  border-color: #4CAF50;
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

.filter-select,
.filter-input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  min-width: 120px;
}

.loading {
  text-align: center;
  padding: 3rem;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
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
  margin-bottom: 1rem;
}

.crew-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.count {
  padding: 1rem;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  font-weight: 600;
  color: #495057;
}

.crew-table {
  width: 100%;
  border-collapse: collapse;
}

.crew-table thead {
  background: #f8f9fa;
}

.crew-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
  cursor: pointer;
  user-select: none;
}

.crew-table th:hover {
  background: #e9ecef;
}

.crew-table td {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.crew-table tbody tr:hover {
  background: #f8f9fa;
}

.team-manager-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.email {
  font-size: 0.85rem;
  color: #6c757d;
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid #dee2e6;
}

.page-info {
  color: #495057;
}

.btn-primary,
.btn-secondary,
.btn-danger {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

.btn-danger {
  background: #dc3545;
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
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.modal {
  background: white;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.modal-small {
  max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #dee2e6;
  flex-shrink: 0;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #6c757d;
  line-height: 1;
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.close-btn:hover {
  color: #495057;
}

.modal-body {
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #6c757d;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #dee2e6;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .admin-crew-members {
    padding: 1rem;
  }

  .list-header {
    flex-direction: column;
    align-items: stretch;
    margin-bottom: 1rem;
  }

  .filters {
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .search-input {
    font-size: 16px;
    min-height: 44px;
  }

  .filter-row {
    flex-direction: column;
    gap: 0.75rem;
  }

  .filter-group {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }

  .filter-group label {
    margin-bottom: 0.5rem;
  }

  .filter-select,
  .filter-input {
    width: 100%;
    font-size: 16px;
    min-height: 44px;
  }

  .filter-btn {
    width: 100%;
    min-height: 44px;
  }

  .crew-table-container {
    padding: 1rem;
  }

  .crew-table {
    min-width: 900px;
  }

  .crew-table th,
  .crew-table td {
    white-space: nowrap;
  }

  .actions-cell {
    flex-wrap: nowrap;
  }

  .btn-table {
    min-height: 44px;
    min-width: 44px;
    padding: 0.5rem;
    font-size: 0.75rem;
  }

  .pagination {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .pagination .btn-secondary {
    flex: 1;
    min-width: 100px;
    min-height: 44px;
  }

  .page-info {
    width: 100%;
    text-align: center;
  }

  .modal-overlay {
    align-items: flex-end;
    padding: 0;
  }

  .modal-content,
  .modal {
    border-radius: 12px 12px 0 0;
    width: 100%;
    max-width: 100%;
    max-height: 90vh;
  }

  .modal-header {
    padding: 1rem;
  }

  .modal-header h2 {
    font-size: 1.25rem;
  }

  .modal-body {
    padding: 1rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .form-control {
    font-size: 16px;
    min-height: 44px;
  }

  .modal-footer {
    padding: 1rem;
    flex-direction: column;
  }

  .modal-footer .btn-primary,
  .modal-footer .btn-secondary,
  .modal-footer .btn-danger {
    width: 100%;
    min-height: 44px;
  }
}

/* Mobile card styles */
.card-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.crew-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #dee2e6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e0e0e0;
  gap: 0.5rem;
}

.card-title {
  font-size: 1rem;
  color: #212529;
  flex: 1;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0.5rem 0;
  gap: 1rem;
}

.card-label {
  font-weight: 600;
  color: #6c757d;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.card-value {
  color: #212529;
  font-size: 0.875rem;
  text-align: right;
  word-break: break-word;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.btn-card {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
  min-height: 44px;
}

.btn-edit-card {
  background-color: #6c757d;
  color: white;
}

.btn-edit-card:hover {
  background-color: #545b62;
}

@media (min-width: 768px) {
  .crew-table {
    min-width: auto;
  }

  .crew-table td,
  .crew-table th {
    white-space: normal;
  }
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

.name-cell strong {
  color: #2c3e50;
}

.age-category-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.age {
  color: #666;
  font-size: 0.9rem;
  white-space: nowrap;
}

.assigned-badge {
  color: #4CAF50;
  font-size: 1.25rem;
  font-weight: bold;
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


/* Mobile card styles */
.card-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.crew-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #dee2e6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e0e0e0;
  gap: 0.5rem;
}

.card-title {
  font-size: 1rem;
  color: #212529;
  flex: 1;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0.5rem 0;
  gap: 1rem;
}

.card-label {
  font-weight: 600;
  color: #6c757d;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.card-value {
  color: #212529;
  font-size: 0.875rem;
  text-align: right;
  word-break: break-word;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.btn-card {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
  min-height: 44px;
}

.btn-edit-card {
  background-color: #6c757d;
  color: white;
}

.btn-edit-card:hover {
  background-color: #545b62;
}

/* Mobile responsive styles */
@media (max-width: 768px) {
  .admin-crew-members {
    padding: 1rem;
  }

  .list-header {
    flex-direction: column;
    align-items: stretch;
    margin-bottom: 1rem;
  }

  .filters {
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .search-input {
    font-size: 16px;
    min-height: 44px;
  }

  .filter-row {
    flex-direction: column;
    gap: 0.75rem;
  }

  .filter-group {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }

  .filter-group label {
    margin-bottom: 0.25rem;
  }

  .filter-select,
  .filter-input {
    width: 100%;
    font-size: 16px;
    min-height: 44px;
  }

  .filter-btn {
    width: 100%;
    min-height: 44px;
  }

  .crew-table-container {
    padding: 1rem;
  }

  .crew-table {
    min-width: 900px;
  }

  .crew-table th,
  .crew-table td {
    white-space: nowrap;
  }

  .actions-cell {
    flex-wrap: nowrap;
  }

  .btn-table {
    min-height: 44px;
    min-width: 44px;
    padding: 0.5rem;
    font-size: 0.75rem;
  }

  .pagination {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .pagination .btn-secondary {
    flex: 1;
    min-width: 100px;
    min-height: 44px;
  }

  .page-info {
    width: 100%;
    text-align: center;
  }
}

@media (min-width: 768px) {
  .crew-table {
    min-width: auto;
  }

  .crew-table td,
  .crew-table th {
    white-space: normal;
  }
}
