<template>
  <DataCard class="restore-panel" :title="$t('admin.database.restore.title')" :status-badge="false">
    <div class="restore-panel__body">
      <div class="restore-panel__selected">
        <span class="restore-panel__label">{{ $t('admin.database.restore.selected') }} :</span>
        <span class="boat-number-text">{{ selected.backup_id }}</span>
        <StatusBadge v-if="badge" :status="badge.status" size="medium">{{ $t(badge.labelKey) }}</StatusBadge>
      </div>
      <p v-if="sourceRef" class="restore-panel__text">
        {{ $t('admin.database.restore.source', { source: sourceRef }) }}
      </p>
      <p class="restore-panel__text">
        {{ $t('admin.database.restore.impact', { count: itemCountLabel }) }}
      </p>
      <p class="restore-panel__text">{{ $t('admin.database.restore.duration') }}</p>

      <FormGroup
        :label="$t('admin.database.restore.phraseLabel')"
        :help-text="$t('admin.database.restore.phraseHelp', { phrase: CONFIRMATION_PHRASE })"
        input-id="restore-phrase"
      >
        <input
          id="restore-phrase"
          type="text"
          autocomplete="off"
          :value="phrase"
          :disabled="!phraseEnabled"
          :placeholder="$t('admin.database.restore.phrasePlaceholder', { phrase: CONFIRMATION_PHRASE })"
          @input="$emit('update:phrase', $event.target.value)"
        />
      </FormGroup>
    </div>

    <template #actions>
      <BaseButton variant="secondary" size="medium" @click="$emit('cancel')">
        {{ $t('admin.database.actions.cancel') }}
      </BaseButton>
      <BaseButton
        variant="danger"
        size="medium"
        :disabled="!canRestore"
        :loading="busy"
        @click="showModal = true"
      >
        {{ $t('admin.database.restore.button') }}
      </BaseButton>
    </template>
  </DataCard>

  <BaseModal :show="showModal" size="medium" :title="$t('admin.database.restore.modal.title')" @close="showModal = false">
    <div class="restore-panel__body">
      <p class="restore-panel__text">
        {{ $t('admin.database.restore.modal.replaceAll', {
          id: selected.backup_id,
          count: itemCountLabel,
          category: badge ? $t(badge.labelKey) : ''
        }) }}
      </p>
      <p class="restore-panel__text">
        {{ $t('admin.database.restore.modal.safetyBefore', { safetyName }) }}
      </p>
      <p class="restore-panel__text">{{ $t('admin.database.restore.modal.undoHint') }}</p>
      <p class="restore-panel__text">{{ $t('admin.database.restore.modal.cognito') }}</p>
    </div>
    <template #footer>
      <BaseButton variant="secondary" size="medium" @click="showModal = false">
        {{ $t('admin.database.restore.modal.cancel') }}
      </BaseButton>
      <BaseButton variant="danger" size="medium" @click="confirm">
        {{ $t('admin.database.restore.modal.confirm') }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import DataCard from '../composite/DataCard.vue'
import FormGroup from '../composite/FormGroup.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseModal from '../base/BaseModal.vue'
import StatusBadge from '../base/StatusBadge.vue'
import { CONFIRMATION_PHRASE, SOURCE_MARKER, categoryBadge, parseBackupId } from '../../utils/backupNaming'

const props = defineProps({
  selected: { type: Object, required: true },
  phrase: { type: String, default: '' },
  canRestore: { type: Boolean, default: false },
  phraseEnabled: { type: Boolean, default: false },
  busy: { type: Boolean, default: false }
})

const emit = defineEmits(['update:phrase', 'restore', 'cancel'])

const { t } = useI18n()
const showModal = ref(false)

const badge = computed(() => categoryBadge(props.selected.category))
const parsed = computed(() => parseBackupId(props.selected.backup_id))
const sourceRef = computed(() => props.selected.source_ref || null)
const itemCountLabel = computed(() => props.selected.item_count ?? t('admin.database.list.unknown'))

// `{category}_{timestamp}` of the selected backup, used in the future safety backup name
const selectedRef = computed(() =>
  parsed.value ? `${parsed.value.category}_${parsed.value.timestamp}` : props.selected.backup_id
)
const safetyName = computed(() => `safety-pre-restore_<horodatage>${SOURCE_MARKER}${selectedRef.value}.json`)

const confirm = () => {
  showModal.value = false
  emit('restore')
}
</script>

<style scoped>
.restore-panel {
  border: 1px solid var(--color-danger);
}

.restore-panel__body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.restore-panel__selected {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-sm);
}

.restore-panel__label {
  font-weight: var(--font-weight-semibold);
}

.restore-panel__text {
  margin: 0;
}
</style>
