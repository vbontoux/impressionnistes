<template>
  <div class="permission-matrix-table">
    <div class="table-wrapper">
      <table class="matrix-table">
        <thead>
          <tr>
            <th class="action-column">{{ $t('admin.permissions.action') }}</th>
            <th v-for="phase in phases" :key="phase.key" class="phase-column">
              {{ $t(`admin.permissions.phases.${phase.key}`) }}
            </th>
            <th class="restrictions-column">{{ $t('admin.permissions.restrictions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="action in actions" :key="action.key" class="action-row">
            <td class="action-name">
              <div class="action-label">
                {{ $t(`admin.permissions.actions.${action.key}`) }}
              </div>
              <div class="action-description">
                {{ $t(`admin.permissions.actionDescriptions.${action.key}`) }}
              </div>
            </td>
            
            <!-- Phase checkboxes -->
            <td v-for="phase in phases" :key="`${action.key}-${phase.key}`" class="phase-cell">
              <label class="checkbox-wrapper">
                <input
                  type="checkbox"
                  :checked="isPermitted(action.key, phase.key)"
                  :disabled="disabled"
                  @change="handlePermissionChange(action.key, phase.key, $event.target.checked)"
                />
                <span class="checkbox-label sr-only">
                  {{ $t('admin.permissions.togglePermission', { 
                    action: $t(`admin.permissions.actions.${action.key}`),
                    phase: $t(`admin.permissions.phases.${phase.key}`)
                  }) }}
                </span>
              </label>
            </td>
            
            <!-- Data state restrictions -->
            <td class="restrictions-cell">
              <div v-if="hasRestrictions(action.key)" class="restrictions-list">
                <label 
                  v-if="permissions[action.key]?.requires_not_assigned !== undefined"
                  class="restriction-item"
                >
                  <input
                    type="checkbox"
                    :checked="permissions[action.key].requires_not_assigned"
                    :disabled="disabled"
                    @change="handleRestrictionChange(action.key, 'requires_not_assigned', $event.target.checked)"
                  />
                  <span>{{ $t('admin.permissions.requiresNotAssigned') }}</span>
                </label>
                <label 
                  v-if="permissions[action.key]?.requires_not_paid !== undefined"
                  class="restriction-item"
                >
                  <input
                    type="checkbox"
                    :checked="permissions[action.key].requires_not_paid"
                    :disabled="disabled"
                    @change="handleRestrictionChange(action.key, 'requires_not_paid', $event.target.checked)"
                  />
                  <span>{{ $t('admin.permissions.requiresNotPaid') }}</span>
                </label>
              </div>
              <span v-else class="no-restrictions">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div class="legend">
      <h3>{{ $t('admin.permissions.legend') }}</h3>
      <ul>
        <li>
          <strong>{{ $t('admin.permissions.requiresNotAssigned') }}:</strong>
          {{ $t('admin.permissions.requiresNotAssignedHelp') }}
        </li>
        <li>
          <strong>{{ $t('admin.permissions.requiresNotPaid') }}:</strong>
          {{ $t('admin.permissions.requiresNotPaidHelp') }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  permissions: {
    type: Object,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:permissions'])

// Event phases in order
const phases = [
  { key: 'before_registration' },
  { key: 'during_registration' },
  { key: 'after_registration' },
  { key: 'after_payment_deadline' }
]

// Actions in logical order
const actions = [
  { key: 'create_crew_member' },
  { key: 'edit_crew_member' },
  { key: 'delete_crew_member' },
  { key: 'create_boat_registration' },
  { key: 'edit_boat_registration' },
  { key: 'delete_boat_registration' },
  { key: 'process_payment' },
  { key: 'view_data' },
  { key: 'export_data' }
]

const isPermitted = (actionKey, phaseKey) => {
  return props.permissions[actionKey]?.[phaseKey] === true
}

const hasRestrictions = (actionKey) => {
  const action = props.permissions[actionKey]
  return action?.requires_not_assigned !== undefined || action?.requires_not_paid !== undefined
}

const handlePermissionChange = (actionKey, phaseKey, value) => {
  const updated = { ...props.permissions }
  if (!updated[actionKey]) {
    updated[actionKey] = {}
  }
  updated[actionKey][phaseKey] = value
  emit('update:permissions', updated)
}

const handleRestrictionChange = (actionKey, restrictionKey, value) => {
  const updated = { ...props.permissions }
  if (!updated[actionKey]) {
    updated[actionKey] = {}
  }
  updated[actionKey][restrictionKey] = value
  emit('update:permissions', updated)
}
</script>

<style scoped>
.permission-matrix-table {
  width: 100%;
}

.table-wrapper {
  overflow-x: auto;
  margin-bottom: var(--spacing-xl);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--color-white);
}

.matrix-table thead {
  background-color: var(--color-bg-light);
  border-bottom: 2px solid var(--color-border);
}

.matrix-table th {
  padding: var(--spacing-lg);
  text-align: left;
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
  color: var(--color-dark);
  border-bottom: 1px solid var(--color-border);
}

.action-column {
  min-width: 200px;
  position: sticky;
  left: 0;
  background-color: var(--color-bg-light);
  z-index: 2;
}

.phase-column {
  min-width: 120px;
  text-align: center;
}

.restrictions-column {
  min-width: 200px;
}

.matrix-table tbody tr {
  border-bottom: 1px solid var(--color-border);
}

.matrix-table tbody tr:hover {
  background-color: var(--color-bg-hover);
}

.action-row td {
  padding: var(--spacing-lg);
}

.action-name {
  position: sticky;
  left: 0;
  background-color: var(--color-white);
  z-index: 1;
}

.matrix-table tbody tr:hover .action-name {
  background-color: var(--color-bg-hover);
}

.action-label {
  font-weight: var(--font-weight-medium);
  color: var(--color-dark);
  margin-bottom: var(--spacing-xs);
}

.action-description {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
}

.phase-cell {
  text-align: center;
  vertical-align: middle;
}

.checkbox-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.checkbox-wrapper input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: var(--color-primary);
}

.checkbox-wrapper input[type="checkbox"]:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.restrictions-cell {
  vertical-align: middle;
}

.restrictions-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.restriction-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  cursor: pointer;
}

.restriction-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--color-primary);
}

.restriction-item input[type="checkbox"]:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.no-restrictions {
  color: var(--color-muted);
  font-style: italic;
}

.legend {
  background-color: var(--color-bg-light);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-lg);
}

.legend h3 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-dark);
  margin-bottom: var(--spacing-md);
}

.legend ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.legend li {
  font-size: var(--font-size-sm);
  color: var(--color-muted);
  margin-bottom: var(--spacing-sm);
}

.legend li:last-child {
  margin-bottom: 0;
}

.legend strong {
  color: var(--color-dark);
  font-weight: var(--font-weight-medium);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .table-wrapper {
    border-radius: 0;
    margin-left: calc(-1 * var(--spacing-lg));
    margin-right: calc(-1 * var(--spacing-lg));
    border-left: none;
    border-right: none;
  }

  .matrix-table th,
  .matrix-table td {
    padding: var(--spacing-md);
    font-size: var(--font-size-sm);
  }

  .action-column {
    min-width: 150px;
  }

  .phase-column {
    min-width: 80px;
  }

  .restrictions-column {
    min-width: 150px;
  }

  .action-label {
    font-size: var(--font-size-sm);
  }

  .action-description {
    font-size: var(--font-size-xs);
  }

  .legend {
    margin-left: calc(-1 * var(--spacing-lg));
    margin-right: calc(-1 * var(--spacing-lg));
    border-radius: 0;
    border-left: none;
    border-right: none;
  }
}
</style>
