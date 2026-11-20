<template>
  <div class="reset-result">
    <!-- Success -->
    <template v-if="state === 'success' && result">
      <MessageAlert
        type="success"
        :dismissible="false"
        :message="`${$t('admin.database.reset.result.successTitle')} : ${$t('admin.database.reset.result.total', { total: result.total_deleted ?? 0 })}`"
      />

      <ul class="reset-result__list">
        <li v-for="line in countLines(result.deleted)" :key="line.id">{{ line.text }}</li>
      </ul>

      <p v-if="boatsPurged" class="reset-result__text">{{ $t('admin.database.reset.result.boatNumbering') }}</p>

      <DataCard
        v-if="cognito.requested"
        :title="$t('admin.database.reset.result.cognitoTitle')"
        :status-badge="false"
      >
        <ul class="reset-result__list">
          <li>{{ $t('admin.database.reset.result.cognitoDeleted', { count: cognito.deleted ?? 0 }) }}</li>
          <li v-if="failedSubs.length" class="reset-result__failed">
            {{ $t('admin.database.reset.result.cognitoFailed', { count: failedSubs.length, subs: failedSubs.join(', ') }) }}
          </li>
          <li v-if="cognito.skipped_admins">
            {{ $t('admin.database.reset.result.cognitoSkippedAdmins', { count: cognito.skipped_admins }) }}
          </li>
          <li v-if="cognito.not_found">
            {{ $t('admin.database.reset.result.cognitoNotFound', { count: cognito.not_found }) }}
          </li>
        </ul>
        <p class="reset-result__text">{{ $t('admin.database.reset.result.cognitoNotRestored') }}</p>
      </DataCard>

      <DataCard :title="$t('admin.database.reset.result.backupTitle')" :status-badge="false" class="reset-result__backup">
        <template v-if="backupId">
          <div class="reset-result__row">
            <span>{{ $t('admin.database.reset.result.backupId', { id: backupId }) }}</span>
            <StatusBadge status="incomplete" size="medium">{{ $t('admin.database.category.safety-pre-reset') }}</StatusBadge>
          </div>
          <p class="reset-result__text">{{ $t('admin.database.reset.result.backupHint') }}</p>
        </template>
        <p v-else class="reset-result__text">{{ $t('admin.database.reset.result.noBackup') }}</p>
        <template v-if="backupId" #actions>
          <BaseButton size="small" variant="warning" @click="$emit('restore-backup', backupId)">
            {{ $t('admin.database.reset.actions.restoreBackup') }}
          </BaseButton>
        </template>
      </DataCard>

      <DataCard :title="$t('admin.database.reset.result.reminderTitle')" :status-badge="false">
        <p class="reset-result__text">{{ $t('admin.database.reset.result.reminder') }}</p>
      </DataCard>

      <div class="reset-result__footer">
        <BaseButton size="medium" variant="secondary" @click="$emit('dismiss')">
          {{ $t('admin.database.reset.actions.finish') }}
        </BaseButton>
      </div>
    </template>

    <!-- Error: database not modified, or outcome unknown -->
    <template v-else-if="state === 'error' && error">
      <MessageAlert type="error" :dismissible="false" :message="errorMessage" />
      <template v-if="error.outcomeUnknown">
        <p class="reset-result__text reset-result__title">{{ $t('admin.database.reset.error.unknownOutcomeTitle') }}</p>
        <p class="reset-result__text">{{ $t('admin.database.reset.error.unknownOutcomeSteps') }}</p>
        <p class="reset-result__text">{{ $t('admin.database.reset.error.sessionExpired') }}</p>
      </template>
      <p v-else class="reset-result__text">{{ $t('admin.database.reset.error.unchanged') }}</p>
      <div class="reset-result__footer">
        <BaseButton size="medium" variant="secondary" @click="$emit('dismiss')">
          {{ $t('admin.database.reset.actions.retry') }}
        </BaseButton>
      </div>
    </template>

    <!-- Partial: deletion started, purge incomplete -->
    <template v-else-if="state === 'partial' && error">
      <MessageAlert
        type="error"
        :dismissible="false"
        :message="`${$t('admin.database.reset.states.partial')}. ${$t('admin.database.reset.partial.message')}`"
      />
      <p v-if="details.stage" class="reset-result__text">
        {{ $t('admin.database.reset.partial.stage', { stage: setLabel(details.stage) }) }}
      </p>
      <template v-if="partialLines.length">
        <p class="reset-result__text">{{ $t('admin.database.reset.partial.counts') }}</p>
        <ul class="reset-result__list">
          <li v-for="line in partialLines" :key="line.id">{{ line.text }}</li>
        </ul>
      </template>
      <p class="reset-result__text">{{ $t('admin.database.reset.partial.cognitoNotAttempted') }}</p>

      <DataCard :title="$t('admin.database.reset.partial.instructionsTitle')" :status-badge="false">
        <div v-if="backupId" class="reset-result__row">
          <span>{{ $t('admin.database.reset.partial.backupId', { id: backupId }) }}</span>
          <StatusBadge status="incomplete" size="medium">{{ $t('admin.database.category.safety-pre-reset') }}</StatusBadge>
        </div>
        <p v-else class="reset-result__text">{{ $t('admin.database.reset.partial.noBackup') }}</p>
        <ol class="reset-result__list reset-result__list--ordered">
          <li>{{ $t('admin.database.reset.partial.step1') }}</li>
          <li>{{ $t('admin.database.reset.partial.step2') }}</li>
          <li>{{ $t('admin.database.reset.partial.step3') }}</li>
        </ol>
        <template #actions>
          <BaseButton v-if="backupId" size="small" variant="danger" @click="$emit('restore-backup', backupId)">
            {{ $t('admin.database.reset.actions.restoreBackup') }}
          </BaseButton>
          <BaseButton size="small" variant="secondary" @click="$emit('retry')">
            {{ $t('admin.database.reset.actions.retry') }}
          </BaseButton>
        </template>
      </DataCard>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { PURGE_SET_IDS } from '../../utils/resetRules'
import DataCard from '../composite/DataCard.vue'
import MessageAlert from '../composite/MessageAlert.vue'
import BaseButton from '../base/BaseButton.vue'
import StatusBadge from '../base/StatusBadge.vue'

const props = defineProps({
  state: { type: String, required: true },
  result: { type: Object, default: null },
  error: { type: Object, default: null }
})

defineEmits(['restore-backup', 'dismiss', 'retry'])

const { t } = useI18n()

const details = computed(() => props.error?.details || {})
const cognito = computed(() => props.result?.cognito || { requested: false })
const failedSubs = computed(() => (cognito.value.failed || []).map((f) => f.sub))
const boatsPurged = computed(() => (props.result?.deleted?.boats ?? 0) > 0 || 'boats' in (props.result?.deleted || {}))

const backupId = computed(() => {
  if (props.state === 'success') {
    const backup = props.result?.pre_reset_backup
    return backup?.backup_id || backup?.id || null
  }
  return details.value.pre_reset_backup_id || null
})

// Same message for every unknown outcome: purge-specific, never mentions a restore operation
const errorMessage = computed(() =>
  props.error.outcomeUnknown
    ? t('admin.database.reset.error.unknownOutcome')
    : t(props.error.messageKey)
)

const setLabel = (id) => t(`admin.database.reset.sets.${id}.label`)

const countLines = (counts) =>
  PURGE_SET_IDS.filter((id) => counts && id in counts).map((id) => ({
    id,
    text: t('admin.database.reset.result.countLine', { label: setLabel(id), count: counts[id] })
  }))

const partialLines = computed(() =>
  countLines(details.value.deleted).map((line) => ({
    ...line,
    text: t('admin.database.reset.partial.countLine', {
      label: setLabel(line.id),
      count: details.value.deleted[line.id]
    })
  }))
)
</script>

<style scoped>
.reset-result {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.reset-result__text {
  margin: 0;
}

.reset-result__title {
  font-weight: var(--font-weight-semibold);
}

.reset-result__list {
  margin: 0;
  padding-left: var(--spacing-xl);
}

.reset-result__list--ordered {
  margin-top: var(--spacing-md);
}

.reset-result__failed {
  color: var(--color-danger);
}

.reset-result__backup {
  border: 1px solid var(--color-primary);
  background: var(--color-light);
}

.reset-result__row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-sm);
}

.reset-result__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
}
</style>
