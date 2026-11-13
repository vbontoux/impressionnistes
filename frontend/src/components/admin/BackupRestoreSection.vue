<template>
  <section class="backup-section">
    <h2 class="backup-section__title">{{ $t('admin.database.backupSection') }}</h2>

    <!-- State banner: current state, what is possible, what is running -->
    <MessageAlert :type="bannerType" :dismissible="false" :message="bannerMessage" />

    <!-- Toolbar -->
    <div class="backup-section__toolbar">
      <BaseButton
        variant="primary"
        size="medium"
        :disabled="!actions.create"
        :loading="busyLabel === 'creating'"
        @click="create"
      >
        {{ $t('admin.database.actions.create') }}
      </BaseButton>
      <BaseButton
        variant="secondary"
        size="medium"
        :disabled="!actions.refresh"
        :loading="busyLabel === 'loading'"
        @click="load"
      >
        {{ $t('admin.database.actions.refresh') }}
      </BaseButton>
    </div>

    <!-- Outcome panels -->
    <RestoreResultPanel
      v-if="['success', 'error', 'partial'].includes(state)"
      :state="state"
      :result="result"
      :error="error"
      :backups="backups"
      @undo="undoRestore"
      @dismiss="dismiss"
      @select="selectById"
    />

    <RestorePanel
      v-if="selected && state !== 'success'"
      :selected="selected"
      :phrase="phrase"
      :can-restore="canRestore"
      :phrase-enabled="actions.phraseInput"
      :busy="busyLabel === 'restoring'"
      @update:phrase="setPhrase"
      @restore="confirmRestore"
      @cancel="select(null)"
    />

    <!-- List -->
    <h3 class="backup-section__subtitle">{{ $t('admin.database.list.title') }}</h3>
    <LoadingSpinner
      v-if="busyLabel === 'loading' && !backups.length"
      :message="$t('admin.database.list.loading')"
    />
    <EmptyState v-else-if="!backups.length && state !== 'busy'" :message="$t('admin.database.list.empty')" />
    <template v-else>
      <!-- Desktop: table -->
      <div class="backup-section__table-view">
        <SortableTable
          :columns="columns"
          :data="rows"
          initial-sort-field="created_at"
          initial-sort-direction="desc"
          :aria-label="$t('admin.database.list.title')"
        >
          <template #cell-id="{ row }">
            <span class="boat-number-text">{{ row.backup_id }}</span>
          </template>
          <template #cell-category="{ row }">
            <StatusBadge v-if="badgeOf(row)" :status="badgeOf(row).status" size="medium">
              {{ $t(badgeOf(row).labelKey) }}
            </StatusBadge>
          </template>
          <template #cell-created_at="{ row }">{{ formatDate(row.created_at) }}</template>
          <template #cell-item_count="{ row }">{{ row.item_count ?? unknown }}</template>
          <template #cell-size_bytes="{ row }">{{ formatSize(row.size_bytes) }}</template>
          <template #cell-created_by="{ row }">{{ row.created_by || unknown }}</template>
          <template #cell-source="{ row }">{{ sourceText(row) }}</template>
          <template #cell-actions="{ row }">
            <div class="backup-section__actions">
              <BaseButton size="small" variant="secondary" :disabled="!actions.download" @click="download(row)">
                {{ $t('admin.database.actions.download') }}
              </BaseButton>
              <BaseButton size="small" variant="danger" :disabled="!canDelete(row)" @click="remove(row)">
                {{ $t('admin.database.actions.delete') }}
              </BaseButton>
              <BaseButton size="small" variant="danger" :disabled="!canSelect(row)" @click="select(row)">
                {{ $t('admin.database.actions.restore') }}
              </BaseButton>
            </div>
          </template>
        </SortableTable>
      </div>

      <!-- Mobile: cards -->
      <div class="backup-section__card-view">
        <DataCard
          v-for="row in rows"
          :key="row.backup_id"
          :class="{ 'backup-section__card--selected': row.backup_id === selected?.backup_id }"
        >
          <template #header>
            <div class="backup-section__card-header">
              <span class="boat-number-text">{{ row.backup_id }}</span>
              <StatusBadge v-if="badgeOf(row)" :status="badgeOf(row).status" size="medium">
                {{ $t(badgeOf(row).labelKey) }}
              </StatusBadge>
            </div>
          </template>
          <div v-for="field in cardFields(row)" :key="field.label" class="card-field">
            <span class="label">{{ field.label }} :</span>
            <span class="value">{{ field.value }}</span>
          </div>
          <template #actions>
            <BaseButton size="small" variant="secondary" :disabled="!actions.download" @click="download(row)">
              {{ $t('admin.database.actions.download') }}
            </BaseButton>
            <BaseButton size="small" variant="danger" :disabled="!canDelete(row)" @click="remove(row)">
              {{ $t('admin.database.actions.delete') }}
            </BaseButton>
            <BaseButton size="small" variant="danger" :disabled="!canSelect(row)" @click="select(row)">
              {{ $t('admin.database.actions.restore') }}
            </BaseButton>
          </template>
        </DataCard>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useBackupRestore } from '../../composables/useBackupRestore'
import { categoryBadge } from '../../utils/backupNaming'
import BaseButton from '../base/BaseButton.vue'
import EmptyState from '../base/EmptyState.vue'
import LoadingSpinner from '../base/LoadingSpinner.vue'
import StatusBadge from '../base/StatusBadge.vue'
import DataCard from '../composite/DataCard.vue'
import MessageAlert from '../composite/MessageAlert.vue'
import SortableTable from '../composite/SortableTable.vue'
import RestorePanel from './RestorePanel.vue'
import RestoreResultPanel from './RestoreResultPanel.vue'

// The delete confirmation uses useConfirm; the global ConfirmDialog is rendered in App.vue.
const {
  state, busyLabel, busyLabelKey, backups, selected, phrase, result, error,
  canRestore, actions, canSelect, canDelete,
  load, create, download, remove, select, setPhrase,
  confirmRestore, undoRestore, dismiss
} = useBackupRestore()

const { t, locale } = useI18n()
const unknown = computed(() => t('admin.database.list.unknown'))

onMounted(load)

const rows = computed(() => backups.value.map((b) => ({ ...b, id: b.backup_id })))

const columns = computed(() => [
  { key: 'id', label: t('admin.database.list.id') },
  { key: 'category', label: t('admin.database.list.category') },
  { key: 'created_at', label: t('admin.database.list.createdAt') },
  { key: 'item_count', label: t('admin.database.list.itemCount'), align: 'right' },
  { key: 'size_bytes', label: t('admin.database.list.size'), align: 'right' },
  { key: 'created_by', label: t('admin.database.list.createdBy') },
  { key: 'source', label: t('admin.database.list.source'), sortable: false },
  { key: 'actions', label: t('admin.database.list.actions'), sortable: false }
])

const badgeOf = (row) => categoryBadge(row.category)

// Source comes from the list field source_ref, never derived from the key
const sourceText = (row) =>
  row.source_ref ? t('admin.database.list.sourceOf', { source: row.source_ref }) : unknown.value

const formatDate = (iso) => (iso ? new Date(iso).toLocaleString(locale.value) : unknown.value)

const formatSize = (bytes) => {
  if (bytes == null) return unknown.value
  return bytes < 1024 ? `${bytes} o` : `${(bytes / 1024).toFixed(1)} Ko`
}

// Same fields as the table columns (except id/category shown in the header, and actions)
const cardFields = (row) => [
  { label: t('admin.database.list.createdAt'), value: formatDate(row.created_at) },
  { label: t('admin.database.list.itemCount'), value: row.item_count ?? unknown.value },
  { label: t('admin.database.list.size'), value: formatSize(row.size_bytes) },
  { label: t('admin.database.list.createdBy'), value: row.created_by || unknown.value },
  { label: t('admin.database.list.source'), value: sourceText(row) }
]

// Partial state: pick the safety/source backup by id (may be absent from the list)
const selectById = (id) => {
  select(backups.value.find((b) => b.backup_id === id) || { backup_id: id, category: id.split('_')[0] })
}

const bannerType = computed(() => {
  if (state.value === 'partial' || state.value === 'error') return 'error'
  if (state.value === 'success') return 'success'
  if (state.value === 'ready_to_restore') return 'warning'
  return 'info'
})

const bannerMessage = computed(() => {
  switch (state.value) {
    case 'busy': {
      const operation = t(busyLabelKey.value)
      const hint = busyLabel.value === 'restoring' ? ` ${t('admin.database.states.busyRestoreHint')}` : ''
      return `${t('admin.database.states.busy', { operation })}${hint}`
    }
    case 'ready_to_restore':
      return t('admin.database.states.readyToRestore', { id: selected.value?.backup_id })
    case 'success':
      return t('admin.database.states.success', {
        purged: result.value?.purged_count ?? 0,
        restored: result.value?.restored_count ?? 0
      })
    case 'error':
      return error.value?.outcomeUnknown
        ? t('admin.database.errors.UNKNOWN_OUTCOME')
        : t('admin.database.states.error')
    case 'partial':
      return t('admin.database.states.partial')
    default:
      return t('admin.database.states.idle', { count: backups.value.length })
  }
})
</script>

<style scoped>
.backup-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.backup-section__title,
.backup-section__subtitle {
  margin: 0;
}

.backup-section__toolbar,
.backup-section__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.backup-section__card-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.backup-section__card--selected {
  border: 1px solid var(--color-primary);
}

.backup-section__card-view {
  display: none;
  flex-direction: column;
  gap: var(--spacing-lg);
}

@media (max-width: 767px) {
  .backup-section__table-view {
    display: none;
  }

  .backup-section__card-view {
    display: flex;
  }
}
</style>
