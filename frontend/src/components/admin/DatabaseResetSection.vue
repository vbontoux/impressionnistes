<template>
  <section v-if="isAdmin" class="reset-section">
    <h2 class="reset-section__title">{{ $t('admin.database.reset.title') }}</h2>
    <p class="reset-section__subtitle">{{ $t('admin.database.reset.subtitle') }}</p>

    <!-- State banner -->
    <MessageAlert :type="bannerType" :dismissible="false" :message="bannerMessage" />

    <!-- Outcome panel -->
    <DatabaseResetResultPanel
      v-if="['success', 'error', 'partial'].includes(state)"
      :state="state"
      :result="result"
      :error="error"
      @restore-backup="(id) => $emit('restore-backup', id)"
      @dismiss="dismiss"
      @retry="focusPhrase"
    />

    <!-- Toolbar -->
    <div class="reset-section__toolbar">
      <BaseButton
        variant="secondary"
        size="medium"
        :disabled="!actions.selectAll"
        @click="selectAll"
      >
        {{ $t('admin.database.reset.selectAll') }}
      </BaseButton>
      <BaseButton
        variant="secondary"
        size="medium"
        :disabled="!actions.refresh"
        :loading="busyLabel === 'loading'"
        @click="load"
      >
        {{ $t('admin.database.reset.actions.refresh') }}
      </BaseButton>
    </div>

    <p v-if="locked.includes('payments')" class="reset-section__hint">
      {{ $t('admin.database.reset.paymentsAuto') }}
    </p>

    <!-- One card per purge set -->
    <div class="reset-section__sets">
      <DataCard v-for="id in PURGE_SET_IDS" :key="id" :class="{ 'reset-section__set--effective': effective.includes(id) }">
        <template #header>
          <div class="reset-section__card-header">
            <label class="reset-section__check">
              <input
                type="checkbox"
                :checked="effective.includes(id)"
                :disabled="!actions.checkboxes || locked.includes(id)"
                @change="toggle(id)"
              />
              <span class="reset-section__label">{{ $t(`admin.database.reset.sets.${id}.label`) }}</span>
            </label>
            <span class="boat-number-text">{{ countText(id) }}</span>
          </div>
        </template>
        <p class="reset-section__text">{{ $t(`admin.database.reset.sets.${id}.description`) }}</p>
        <p v-if="locked.includes(id)" class="reset-section__lock">
          {{ $t('admin.database.reset.lockedBy', { labels: lockedByLabels(id) }) }}
        </p>
      </DataCard>
    </div>

    <!-- Options -->
    <DataCard :title="$t('admin.database.reset.backup.label')" :status-badge="false">
      <label class="reset-section__check">
        <input
          type="checkbox"
          :checked="backupRequired || backupBefore"
          :disabled="!actions.options || backupRequired"
          @change="setBackup($event.target.checked)"
        />
        <span>{{ $t('admin.database.reset.backup.label') }}</span>
      </label>
      <p v-if="backupRequired" class="reset-section__text">{{ $t('admin.database.reset.backup.prodLocked') }}</p>
      <p v-else-if="!backupBefore" class="reset-section__warning">{{ $t('admin.database.reset.backup.noUndo') }}</p>
    </DataCard>

    <DataCard v-if="cognitoVisible" :title="$t('admin.database.reset.cognito.label')" :status-badge="false">
      <label class="reset-section__check">
        <input
          type="checkbox"
          :checked="cognitoOption"
          :disabled="!actions.options"
          @change="setCognito($event.target.checked)"
        />
        <span>{{ $t('admin.database.reset.cognito.label') }}</span>
      </label>
      <p class="reset-section__warning">{{ $t('admin.database.reset.cognito.irreversible') }}</p>
      <p class="reset-section__text">{{ $t('admin.database.reset.cognito.notRestored') }}</p>
      <p class="reset-section__text">{{ $t('admin.database.reset.cognito.adminsExcluded') }}</p>
      <p v-if="!cognitoOption" class="reset-section__text">{{ $t('admin.database.reset.cognito.loginWithoutProfile') }}</p>
    </DataCard>

    <!-- Confirmation phrase and purge button -->
    <FormGroup
      :label="$t('admin.database.reset.phrase.label')"
      :help-text="$t('admin.database.reset.phrase.help', { phrase: confirmationPhrase })"
      input-id="reset-phrase"
    >
      <input
        id="reset-phrase"
        ref="phraseInput"
        type="text"
        autocomplete="off"
        :value="phrase"
        :disabled="!actions.phraseInput"
        :placeholder="$t('admin.database.reset.phrase.placeholder', { phrase: confirmationPhrase })"
        @input="setPhrase($event.target.value)"
      />
    </FormGroup>

    <div class="reset-section__footer">
      <BaseButton
        variant="danger"
        size="medium"
        :disabled="!actions.purge"
        :loading="busyLabel === 'purging'"
        @click="showModal = true"
      >
        {{ $t('admin.database.reset.button') }}
      </BaseButton>
    </div>

    <!-- Confirmation modal -->
    <BaseModal :show="showModal" size="medium" :title="$t('admin.database.reset.modal.title')" @close="showModal = false">
      <div class="reset-section__modal-body">
        <p class="reset-section__text">{{ $t('admin.database.reset.modal.intro') }}</p>
        <ul class="reset-section__list">
          <li v-for="id in effective" :key="id">
            {{ $t('admin.database.reset.modal.setLine', { label: setLabel(id), count: counts[id] ?? 0 }) }}
            <span v-if="locked.includes(id)" class="reset-section__implied">({{ $t('admin.database.reset.implied') }})</span>
          </li>
        </ul>

        <p v-if="keptLabels" class="reset-section__text">
          <strong>{{ $t('admin.database.reset.modal.keptTitle') }}</strong> :
          {{ $t('admin.database.reset.modal.keptSets', { labels: keptLabels }) }}
        </p>
        <p class="reset-section__text">
          <strong>{{ $t('admin.database.reset.modal.protectedTitle') }}</strong> : {{ protectedLabels }}
        </p>

        <p v-if="cognitoVisible && cognitoOption" class="reset-section__warning">
          {{ $t('admin.database.reset.modal.cognito', { count: cognitoAccountsMax }) }}
        </p>
        <p v-else-if="cognitoVisible" class="reset-section__text">{{ $t('admin.database.reset.modal.cognitoNo') }}</p>

        <p v-if="backupRequired || backupBefore" class="reset-section__text">{{ $t('admin.database.reset.modal.backupYes') }}</p>
        <p v-else class="reset-section__warning">{{ $t('admin.database.reset.modal.backupNo') }}</p>
      </div>
      <template #footer>
        <BaseButton variant="secondary" size="medium" @click="showModal = false">
          {{ $t('admin.database.reset.modal.cancel') }}
        </BaseButton>
        <BaseButton variant="danger" size="medium" @click="confirmPurge">
          {{ $t('admin.database.reset.modal.confirm') }}
        </BaseButton>
      </template>
    </BaseModal>
  </section>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../../stores/authStore'
import { useDatabaseReset } from '../../composables/useDatabaseReset'
import { PURGE_SET_IDS } from '../../utils/resetRules'
import BaseButton from '../base/BaseButton.vue'
import BaseModal from '../base/BaseModal.vue'
import DataCard from '../composite/DataCard.vue'
import FormGroup from '../composite/FormGroup.vue'
import MessageAlert from '../composite/MessageAlert.vue'
import DatabaseResetResultPanel from './DatabaseResetResultPanel.vue'

const props = defineProps({
  // True while the backup section is busy (disables Purger)
  externalBusy: { type: Boolean, default: false }
})

// restore-backup(id): restore the Pre_Reset_Backup; busy-change(bool): purge in progress; purged: purge succeeded
const emit = defineEmits(['restore-backup', 'busy-change', 'purged'])

const { t } = useI18n()
const authStore = useAuthStore()
const isAdmin = computed(() => authStore.isAdmin)

const {
  state, busyLabel, busyLabelKey, counts, backupRequired, cognitoAccountsMax,
  effective, locked, cognitoOption, cognitoVisible, backupBefore, phrase,
  result, error, actions, confirmationPhrase, lockedBy, externalBusy: busyFromPage,
  load, toggle, selectAll, setCognito, setBackup, setPhrase, purge, dismiss
} = useDatabaseReset()

const showModal = ref(false)
const phraseInput = ref(null)

onMounted(() => {
  if (isAdmin.value) load()
})

watch(() => props.externalBusy, (value) => { busyFromPage.value = value }, { immediate: true })
watch(() => state.value === 'busy', (busy) => emit('busy-change', busy))
watch(state, (next, previous) => {
  if (next === 'success' && previous === 'busy') emit('purged')
})

const setLabel = (id) => t(`admin.database.reset.sets.${id}.label`)
const lockedByLabels = (id) => lockedBy(id).map(setLabel).join(', ')
const countText = (id) =>
  counts.value[id] === undefined
    ? t('admin.database.reset.countUnavailable')
    : t('admin.database.reset.count', { count: counts.value[id] })

const keptLabels = computed(() =>
  PURGE_SET_IDS.filter((id) => !effective.value.includes(id)).map(setLabel).join(', ')
)
const protectedLabels = computed(() =>
  ['config', 'races', 'clubs', 'backupHistory']
    .map((key) => t(`admin.database.reset.modal.protected.${key}`))
    .join(', ')
)

const confirmPurge = () => {
  showModal.value = false
  purge()
}

const focusPhrase = () => phraseInput.value?.focus()

const bannerType = computed(() => {
  if (state.value === 'partial' || state.value === 'error') return 'error'
  if (state.value === 'success') return 'success'
  if (state.value === 'ready_to_purge') return 'warning'
  return 'info'
})

const bannerMessage = computed(() => {
  switch (state.value) {
    case 'busy': {
      const base = t('admin.database.reset.states.busy', { operation: t(busyLabelKey.value) })
      return busyLabel.value === 'purging' ? `${base} ${t('admin.database.reset.states.busyPurgeHint')}` : base
    }
    case 'ready_to_purge':
      return t('admin.database.reset.states.readyToPurge', { labels: effective.value.map(setLabel).join(', ') })
    case 'success':
      return t('admin.database.reset.states.success', { total: result.value?.total_deleted ?? 0 })
    case 'error':
      return error.value?.outcomeUnknown
        ? t('admin.database.reset.error.unknownOutcome')
        : t('admin.database.reset.states.error')
    case 'partial':
      return t('admin.database.reset.states.partial')
    default:
      return t('admin.database.reset.states.idle')
  }
})

defineExpose({ reload: load })
</script>

<style scoped>
.reset-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.reset-section__title,
.reset-section__subtitle {
  margin: 0;
}

.reset-section__subtitle,
.reset-section__hint {
  color: var(--color-secondary);
}

.reset-section__hint,
.reset-section__text,
.reset-section__warning,
.reset-section__lock {
  margin: 0;
}

.reset-section__toolbar,
.reset-section__footer {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.reset-section__footer {
  justify-content: flex-end;
}

.reset-section__sets {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.reset-section__set--effective {
  border: 1px solid var(--color-danger);
}

.reset-section__card-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.reset-section__check {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  min-height: var(--button-min-height-md);
  cursor: pointer;
}

.reset-section__check input[type='checkbox'] {
  width: auto;
  min-height: auto;
}

.reset-section__label {
  font-weight: var(--font-weight-semibold);
}

.reset-section__lock,
.reset-section__implied {
  color: var(--color-secondary);
  font-style: italic;
}

.reset-section__warning {
  color: var(--color-danger);
  font-weight: var(--font-weight-medium);
}

.reset-section__modal-body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.reset-section__list {
  margin: 0;
  padding-left: var(--spacing-xl);
}
</style>
