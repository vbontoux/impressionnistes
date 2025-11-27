<template>
  <div class="crew-member-card" :class="{ 'has-issues': hasFlaggedIssues, 'assigned': isAssigned }">
    <div class="card-header">
      <div class="member-info">
        <h4>{{ crewMember.first_name }} {{ crewMember.last_name }}</h4>
        <span class="license">{{ crewMember.license_number }}</span>
      </div>
      <div class="badges">
        <span v-if="isAssigned" class="badge badge-assigned">{{ $t('crew.card.assigned') }}</span>
      </div>
    </div>

    <div class="card-body">
      <div class="detail-row">
        <span class="label">{{ $t('crew.card.dateOfBirth') }}:</span>
        <span class="value">{{ formatDate(crewMember.date_of_birth) }}</span>
      </div>
      <div class="detail-row">
        <span class="label">{{ $t('crew.card.age') }}:</span>
        <span class="value">{{ calculateAge(crewMember.date_of_birth) }} {{ $t('crew.card.years') }}</span>
      </div>
      <div class="detail-row">
        <span class="label">{{ $t('crew.card.category') }}:</span>
        <span class="value category-badge" :class="`category-${getAgeCategory(crewMember.date_of_birth)}`">
          {{ $t(`boat.${getAgeCategory(crewMember.date_of_birth)}`) }}
          <span v-if="getAgeCategory(crewMember.date_of_birth) === 'master'" class="master-letter">
            {{ getMasterCategoryLetter(crewMember.date_of_birth) }}
          </span>
        </span>
      </div>
      <div class="detail-row">
        <span class="label">{{ $t('crew.card.gender') }}:</span>
        <span class="value">{{ crewMember.gender === 'M' ? $t('crew.form.male') : $t('crew.form.female') }}</span>
      </div>
      <div class="detail-row">
        <span class="label">{{ $t('crew.card.club') }}:</span>
        <span class="value">{{ crewMember.club_affiliation }}</span>
      </div>
    </div>

    <!-- Flagged Issues -->
    <div v-if="hasFlaggedIssues" class="flagged-issues">
      <div class="issue-header">
        <span class="icon">⚠️</span>
        <strong>{{ $t('crew.card.flaggedIssues') }}</strong>
      </div>
      <ul class="issue-list">
        <li v-for="(issue, index) in crewMember.flagged_issues" :key="index">
          {{ issue }}
        </li>
      </ul>
    </div>

    <!-- Actions -->
    <div class="card-actions">
      <button class="btn btn-small btn-edit" @click="$emit('edit', crewMember)">
        {{ $t('common.edit') }}
      </button>
      <button 
        class="btn btn-small btn-delete" 
        @click="$emit('delete', crewMember)"
        :disabled="isAssigned"
        :title="isAssigned ? $t('crew.card.cannotDeleteAssigned') : ''"
      >
        {{ $t('common.delete') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { getAgeCategory as getAgeCategoryUtil, getMasterCategory } from '../utils/raceEligibility';

const props = defineProps({
  crewMember: {
    type: Object,
    required: true
  }
});

defineEmits(['edit', 'delete']);

const { t } = useI18n();

const isAssigned = computed(() => !!props.crewMember.assigned_boat_id);
const hasFlaggedIssues = computed(() => 
  props.crewMember.flagged_issues && props.crewMember.flagged_issues.length > 0
);

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString(undefined, { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
};

const calculateAge = (dateOfBirth) => {
  const today = new Date();
  const birthDate = new Date(dateOfBirth);
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  
  // Adjust if birthday hasn't occurred this year
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  
  return age;
};

const getAgeCategory = (dateOfBirth) => {
  const age = calculateAge(dateOfBirth);
  return getAgeCategoryUtil(age);
};

const getMasterCategoryLetter = (dateOfBirth) => {
  const age = calculateAge(dateOfBirth);
  return getMasterCategory(age);
};
</script>

<style scoped>
.crew-member-card {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: all 0.3s;
}

.crew-member-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.crew-member-card.has-issues {
  border-color: #ff9800;
  background-color: #fff3e0;
}

.crew-member-card.assigned {
  border-left: 4px solid #4CAF50;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.member-info h4 {
  margin: 0 0 0.25rem 0;
  color: #333;
  font-size: 1.25rem;
}

.license {
  color: #666;
  font-size: 0.875rem;
  font-family: monospace;
}

.badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-assigned {
  background-color: #9C27B0;
  color: white;
}

.card-body {
  margin-bottom: 1rem;
}

.detail-row {
  display: flex;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f5f5f5;
}

.detail-row:last-child {
  border-bottom: none;
}

.label {
  font-weight: 500;
  color: #666;
  min-width: 120px;
}

.value {
  color: #333;
}

.category-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
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
  font-size: 0.85rem;
}

.flagged-issues {
  background-color: #fff3e0;
  border: 1px solid #ff9800;
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.issue-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  color: #e65100;
}

.icon {
  font-size: 1.25rem;
}

.issue-list {
  margin: 0;
  padding-left: 2rem;
  color: #e65100;
}

.issue-list li {
  margin-bottom: 0.25rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-small {
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
}

.btn-edit {
  background-color: #2196F3;
  color: white;
}

.btn-edit:hover {
  background-color: #1976D2;
}

.btn-delete {
  background-color: #f44336;
  color: white;
}

.btn-delete:hover:not(:disabled) {
  background-color: #d32f2f;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
