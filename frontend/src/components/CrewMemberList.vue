<template>
  <div class="crew-member-list">
    <div class="list-header">
      <h2>{{ $t('crew.list.title') }}</h2>
      <button class="btn btn-primary" @click="showCreateForm = true">
        {{ $t('crew.list.addNew') }}
      </button>
    </div>

    <!-- Filters and Search -->
    <div class="filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="$t('crew.list.search')"
          class="search-input"
        />
      </div>
      
      <div class="filter-buttons">
        <button 
          :class="['filter-btn', { active: filter === 'all' }]"
          @click="filter = 'all'"
        >
          {{ $t('crew.list.all') }} ({{ crewStore.crewMembers.length }})
        </button>
        <button 
          :class="['filter-btn', { active: filter === 'rcpm' }]"
          @click="filter = 'rcpm'"
        >
          RCPM ({{ crewStore.rcpmMembers.length }})
        </button>
        <button 
          :class="['filter-btn', { active: filter === 'external' }]"
          @click="filter = 'external'"
        >
          {{ $t('crew.list.external') }} ({{ crewStore.externalMembers.length }})
        </button>
        <button 
          :class="['filter-btn', { active: filter === 'assigned' }]"
          @click="filter = 'assigned'"
        >
          {{ $t('crew.list.assigned') }} ({{ crewStore.assignedCrewMembers.length }})
        </button>
        <button 
          :class="['filter-btn', { active: filter === 'flagged' }]"
          @click="filter = 'flagged'"
        >
          {{ $t('crew.list.flagged') }} ({{ crewStore.flaggedCrewMembers.length }})
        </button>
      </div>

      <div class="sort-controls">
        <label>{{ $t('crew.list.sortBy') }}:</label>
        <select v-model="sortBy" class="sort-select">
          <option value="last_name">{{ $t('crew.list.lastName') }}</option>
          <option value="first_name">{{ $t('crew.list.firstName') }}</option>
          <option value="date_of_birth">{{ $t('crew.list.age') }}</option>
          <option value="created_at">{{ $t('crew.list.dateAdded') }}</option>
        </select>
      </div>
    </div>

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

    <!-- Crew Member Cards -->
    <div v-else class="crew-grid">
      <CrewMemberCard
        v-for="member in filteredCrewMembers"
        :key="member.crew_member_id"
        :crew-member="member"
        @edit="handleEdit"
        @delete="handleDelete"
      />
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
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useCrewStore } from '../stores/crewStore';
import CrewMemberCard from './CrewMemberCard.vue';
import CrewMemberForm from './CrewMemberForm.vue';

const { t } = useI18n();
const crewStore = useCrewStore();

const searchQuery = ref('');
const filter = ref('all');
const sortBy = ref('last_name');
const showCreateForm = ref(false);
const editingMember = ref(null);
const deletingMember = ref(null);
const deleting = ref(false);

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
    case 'rcpm':
      members = crewStore.rcpmMembers;
      break;
    case 'external':
      members = crewStore.externalMembers;
      break;
    case 'assigned':
      members = crewStore.assignedCrewMembers;
      break;
    case 'flagged':
      members = crewStore.flaggedCrewMembers;
      break;
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
};
</script>

<style scoped>
.crew-member-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.list-header h2 {
  margin: 0;
  color: #333;
}

.filters {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.search-box {
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.filter-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
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

.sort-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
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
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
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
</style>
