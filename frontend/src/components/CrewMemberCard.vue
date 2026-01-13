<template>
  <DataCard>
    <template #header>
      <div class="card-header">
        <div class="member-info">
          <h4>{{ crewMember.first_name }} {{ crewMember.last_name }}</h4>
          <span class="license">{{ crewMember.license_number }}</span>
        </div>
        <div class="badges">
          <span v-if="isAssigned" class="badge badge-assigned">{{ $t('crew.card.assigned') }}</span>
          <span v-else class="badge badge-unassigned">{{ $t('crew.card.unassigned') }}</span>
        </div>
      </div>
    </template>

    <template #default>
      <div class="card-body">
        <div class="detail-row">
          <span class="label">{{ $t('crew.card.dateOfBirth') }}&nbsp;:</span>
          <span class="value">{{ formatDate(crewMember.date_of_birth) }}</span>
        </div>
        <div class="detail-row">
          <span class="label">{{ $t('crew.card.age') }}&nbsp;:</span>
          <span class="value">{{ calculateAge(crewMember.date_of_birth) }} {{ $t('crew.card.years') }}</span>
        </div>
        <div class="detail-row">
          <span class="label">{{ $t('crew.card.category') }}&nbsp;:</span>
          <span class="value category-badge" :class="`category-${getAgeCategory(crewMember.date_of_birth)}`">
            {{ $t(`boat.${getAgeCategory(crewMember.date_of_birth)}`) }}
            <span v-if="getAgeCategory(crewMember.date_of_birth) === 'master'" class="master-letter">
              {{ getMasterCategoryLetter(crewMember.date_of_birth) }}
            </span>
          </span>
        </div>
        <div class="detail-row">
          <span class="label">{{ $t('crew.card.gender') }}&nbsp;:</span>
          <span class="value">{{ crewMember.gender === 'M' ? $t('crew.form.male') : $t('crew.form.female') }}</span>
        </div>
        <div class="detail-row">
          <span class="label">{{ $t('crew.card.club') }}&nbsp;:</span>
          <span class="value club-box">{{ crewMember.club_affiliation }}</span>
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
    </template>

    <template #actions>
      <BaseButton 
        variant="secondary" 
        size="small"
        @click="$emit('edit', crewMember)"
      >
        {{ $t('common.edit') }}
      </BaseButton>
      <BaseButton 
        variant="danger" 
        size="small"
        :disabled="isAssigned"
        :title="isAssigned ? $t('crew.card.cannotDeleteAssigned') : ''"
        @click="$emit('delete', crewMember)"
      >
        {{ $t('common.delete') }}
      </BaseButton>
    </template>
  </DataCard>
</template>

<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { calculateAge, getAgeCategory as getAgeCategoryUtil, getMasterCategory } from '../utils/raceEligibility';
import DataCard from './composite/DataCard.vue';
import BaseButton from './base/BaseButton.vue';

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
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
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
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
  padding-bottom: var(--spacing-lg, 1rem);
  border-bottom: 1px solid var(--color-border, #e0e0e0);
  margin-bottom: var(--spacing-lg, 1rem);
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
}

.detail-row:last-child {
  border-bottom: none;
}

.label {
  font-weight: var(--font-weight-medium, 500);
  color: var(--color-muted, #666);
  min-width: 120px;
}

.value {
  color: var(--color-dark, #333);
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

.category-badge {
  display: inline-block;
  padding: var(--spacing-xs, 0.25rem) var(--spacing-md, 0.75rem);
  border-radius: 12px;
  font-size: var(--font-size-sm, 0.75rem);
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
  font-size: 0.85rem;
}

.flagged-issues {
  background-color: #fff3e0;
  border: 1px solid var(--color-warning, #ff9800);
  border-radius: 4px;
  padding: var(--spacing-lg, 1rem);
  margin-top: var(--spacing-lg, 1rem);
}

.issue-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 0.5rem);
  margin-bottom: var(--spacing-sm, 0.5rem);
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
  margin-bottom: var(--spacing-xs, 0.25rem);
}
</style>
