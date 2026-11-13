<template>
  <div class="result-panel">
    <!-- Success -->
    <template v-if="state === 'success' && result">
      <MessageAlert
        type="success"
        :dismissible="false"
        :message="`${$t('admin.database.restore.result.successTitle')} : ${$t('admin.database.restore.result.counts', { purged: result.purged_count, restored: result.restored_count })}`"
      />
      <ul class="result-panel__steps">
        <li v-for="step in result.steps || []" :key="step.name">{{ stepLabel(step) }}</li>
      </ul>

      <DataCard
        v-if="safety"
        class="result-panel__undo"
        :title="$t('admin.database.restore.undo.title')"
        :status-badge="false"
      >
        <p class="result-panel__text">{{ $t('admin.database.restore.undo.description') }}</p>
        <div class="result-panel__row">
          <span class="boat-number-text">{{ safety.backup_id }}</span>
          <StatusBadge status="incomplete" size="medium">{{ $t('admin.database.category.safety-pre-restore') }}</StatusBadge>
          <span v-if="safetyCount !== null">
            {{ $t('admin.database.restore.steps.count', { count: safetyCount }) }}
          </span>
        </div>
        <template #actions>
          <BaseButton size="small" variant="warning" @click="$emit('undo')">
            {{ $t('admin.database.restore.undo.button') }}
          </BaseButton>
        </template>
      </DataCard>

      <div class="result-panel__footer">
        <BaseButton size="medium" variant="secondary" @click="$emit('dismiss')">
          {{ $t('admin.database.actions.close') }}
        </BaseButton>
      </div>
    </template>

    <!-- Error: database not modified (or outcome unknown) -->
    <template v-else-if="state === 'error' && error">
      <MessageAlert type="error" :dismissible="false" :message="errorMessage" />
      <template v-if="error.outcomeUnknown">
        <p class="result-panel__text result-panel__title">{{ $t('admin.database.restore.error.unknownOutcomeTitle') }}</p>
        <p class="result-panel__text">{{ $t('admin.database.restore.error.unknownOutcomeSteps') }}</p>
      </template>
      <p v-else class="result-panel__text">{{ $t('admin.database.restore.error.unchanged') }}</p>
      <div class="result-panel__footer">
        <BaseButton size="medium" variant="secondary" @click="$emit('dismiss')">
          {{ $t('admin.database.actions.refresh') }}
        </BaseButton>
      </div>
    </template>

    <!-- Partial: purge started, restore incomplete -->
    <template v-else-if="state === 'partial' && error">
      <MessageAlert
        type="error"
        :dismissible="false"
        :message="`${$t('admin.database.restore.partial.title')} : ${$t('admin.database.restore.partial.message')}`"
      />
      <p v-if="details.stage" class="result-panel__text">
        {{ $t('admin.database.restore.partial.stage', { stage: stageLabel }) }}
      </p>
      <p class="result-panel__text">
        {{ $t('admin.database.restore.partial.counts', { purged: details.purged_count ?? 0, written: details.written_count ?? 0 }) }}
      </p>
      <ul class="result-panel__steps">
        <li v-for="step in details.steps || []" :key="step.name">{{ stepLabel(step) }}</li>
      </ul>
      <p v-if="details.safety_backup_id" class="result-panel__text">
        {{ $t('admin.database.restore.partial.safetyBackup', { id: details.safety_backup_id }) }}
      </p>
      <p v-if="nativeName" class="result-panel__text">
        {{ $t('admin.database.restore.partial.nativeBackup', { name: nativeName }) }}
      </p>

      <DataCard :title="$t('admin.database.restore.partial.instructionsTitle')" :status-badge="false">
        <ol class="result-panel__instructions">
          <li>{{ $t('admin.database.restore.partial.step1') }}</li>
          <li>{{ $t('admin.database.restore.partial.step2') }}</li>
          <li>{{ $t('admin.database.restore.partial.step3') }}</li>
        </ol>
        <template #actions>
          <BaseButton
            v-if="details.safety_backup_id"
            size="small"
            variant="danger"
            @click="$emit('select', details.safety_backup_id)"
          >
            {{ $t('admin.database.restore.partial.restoreSafety') }}
          </BaseButton>
          <BaseButton
            v-if="details.source_backup_id"
            size="small"
            variant="secondary"
            @click="$emit('select', details.source_backup_id)"
          >
            {{ $t('admin.database.restore.partial.retrySource') }}
          </BaseButton>
          <BaseButton size="small" variant="secondary" @click="$emit('dismiss')">
            {{ $t('admin.database.actions.refresh') }}
          </BaseButton>
        </template>
      </DataCard>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import DataCard from '../composite/DataCard.vue'
import MessageAlert from '../composite/MessageAlert.vue'
import BaseButton from '../base/BaseButton.vue'
import StatusBadge from '../base/StatusBadge.vue'

const props = defineProps({
  state: { type: String, required: true },
  result: { type: Object, default: null },
  error: { type: Object, default: null },
  backups: { type: Array, default: () => [] }
})

defineEmits(['undo', 'dismiss', 'select'])

const { t, te } = useI18n()

const details = computed(() => props.error?.details || {})
const safety = computed(() => props.result?.safety_backup || null)
const safetyCount = computed(() => {
  const row = props.backups.find((b) => b.backup_id === safety.value?.backup_id)
  return row?.item_count ?? props.result?.steps?.find((s) => s.name === 'safety_backup')?.count ?? null
})

const nativeName = computed(() => {
  const native = details.value.safety_native_backup
  return typeof native === 'string' ? native : native?.name || native?.arn || null
})

const errorMessage = computed(() =>
  t(props.error.messageKey, { backupId: props.error.details?.backup_id || '' })
)

const stepName = (name) => (te(`admin.database.restore.steps.${name}`) ? t(`admin.database.restore.steps.${name}`) : name)
const stageLabel = computed(() => stepName(details.value.stage))

const STEP_ICONS = { ok: '✔', failed: '✖', skipped: '–' }

const stepLabel = (step) => {
  const status = STEP_ICONS[step.status] ? step.status : 'skipped'
  const count = step.count != null ? ` (${t('admin.database.restore.steps.count', { count: step.count })})` : ''
  return `${STEP_ICONS[status]} ${stepName(step.name)} ${t(`admin.database.restore.steps.${status}`)}${count}`
}
</script>

<style scoped>
.result-panel {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.result-panel__text {
  margin: 0;
}

.result-panel__title {
  font-weight: var(--font-weight-semibold);
}

.result-panel__steps,
.result-panel__instructions {
  margin: 0;
  padding-left: var(--spacing-xl);
}

.result-panel__steps {
  list-style: none;
  padding-left: 0;
}

.result-panel__undo {
  border: 1px solid var(--color-primary);
  background: var(--color-light);
}

.result-panel__row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-sm);
}

.result-panel__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
}
</style>
