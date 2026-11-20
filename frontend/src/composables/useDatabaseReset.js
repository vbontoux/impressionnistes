import { ref, computed } from 'vue'
import apiClient from '../services/apiClient'
import {
  PURGE_SET_IDS,
  DEFAULT_SELECTION,
  CONFIRMATION_PHRASE,
  closure,
  requiredBy,
  isPhraseValid
} from '../utils/resetRules'

/**
 * Database reset (selective purge) state machine, single source of truth for the UI.
 * States: idle | busy | ready_to_purge | success | error | partial
 * Transitions happen only in this file. Labels are returned as i18n keys.
 */

const ERRORS_KEY = 'admin.database.errors'
const OPERATIONS_KEY = 'admin.database.reset.states.operations'

// Codes with an i18n entry under admin.database.errors (plus UNKNOWN_OUTCOME / DEFAULT)
const KNOWN_CODES = [
  'INVALID_SELECTION', 'INVALID_CONFIRMATION', 'BACKUP_REQUIRED',
  'PRE_RESET_BACKUP_FAILED', 'RESET_PARTIAL', 'INTERNAL_ERROR',
  'FORBIDDEN', 'UNAUTHORIZED', 'NOT_FOUND'
]

// States where the selection and options can be edited
const EDITABLE_STATES = ['idle', 'ready_to_purge', 'error']

/**
 * Classify a failed purge request.
 * @param {Object} err - axios error
 * @returns {{state: string, code: string, outcomeUnknown: boolean, details: Object|null}}
 */
export function nextStateFromResetError(err) {
  const unknown = { state: 'error', code: 'UNKNOWN_OUTCOME', outcomeUnknown: true, details: null }
  const response = err?.response

  // Network error, CORS-masked 401, timeout (ECONNABORTED), 401 (redirected to login), 504
  if (!response || err?.code === 'ECONNABORTED' || response.status === 401 || response.status === 504) {
    return unknown
  }

  const envelope = response.data?.error
  if (!envelope || typeof envelope.code !== 'string') {
    return unknown
  }

  return {
    state: envelope.code === 'RESET_PARTIAL' ? 'partial' : 'error',
    code: envelope.code,
    outcomeUnknown: false,
    details: envelope.details || null
  }
}

/** Build the error object stored in `error` (code, i18n key, message, details). */
function buildError({ code, outcomeUnknown = false, details = null, message = '' }) {
  const known = code === 'UNKNOWN_OUTCOME' || KNOWN_CODES.includes(code)
  return {
    code,
    messageKey: `${ERRORS_KEY}.${known ? code : 'DEFAULT'}`,
    message,
    details,
    outcomeUnknown
  }
}

export function useDatabaseReset() {
  const state = ref('idle')
  const busyLabel = ref(null) // loading | purging
  const counts = ref({})
  const countsLoaded = ref(false)
  const environment = ref(null)
  const backupRequired = ref(false)
  const cognitoAccountsMax = ref(0)
  const chosen = ref([...DEFAULT_SELECTION])
  const cognitoOption = ref(false)
  const backupBefore = ref(true)
  const phrase = ref('')
  const result = ref(null)
  const error = ref(null)
  const externalBusy = ref(false) // set by the page while the backup section is busy

  const effective = computed(() => closure(chosen.value))
  // A set is locked (checked, not toggleable) iff another selected set requires it,
  // even when the user also chose it explicitly. DEPENDENCIES are transitive, so
  // checking `chosen` is equivalent to checking `effective`.
  const locked = computed(() =>
    effective.value.filter((id) => requiredBy(id, chosen.value).length > 0)
  )
  const lockedBy = (id) => requiredBy(id, effective.value)
  const cognitoVisible = computed(() => effective.value.includes('managers'))

  const preResetBackupId = computed(() => {
    const fromResult = result.value?.pre_reset_backup
    const fromError = error.value?.details?.pre_reset_backup_id
    return (fromResult && (fromResult.backup_id || fromResult.id)) || fromError || null
  })

  const canPurge = computed(
    () =>
      ['idle', 'ready_to_purge', 'error', 'partial'].includes(state.value) &&
      countsLoaded.value &&
      !externalBusy.value &&
      effective.value.length > 0 &&
      isPhraseValid(phrase.value)
  )

  // Enabled actions per state (design: "Enabled actions" table)
  const actions = computed(() => {
    const s = state.value
    const editable = EDITABLE_STATES.includes(s)
    return {
      checkboxes: editable,
      selectAll: editable,
      options: editable,
      phraseInput: s !== 'busy' && s !== 'success',
      purge: canPurge.value,
      refresh: s !== 'busy',
      restoreBackup: (s === 'success' || s === 'partial') && !!preResetBackupId.value,
      finish: s === 'success'
    }
  })

  // First change from idle or error moves to ready_to_purge
  const markChanged = () => {
    if (state.value === 'idle' || state.value === 'error') state.value = 'ready_to_purge'
  }

  // The Cognito option is only meaningful with `managers`
  const syncCognito = () => {
    if (!cognitoVisible.value) cognitoOption.value = false
  }

  const resetOptions = () => {
    chosen.value = [...DEFAULT_SELECTION]
    cognitoOption.value = false
    backupBefore.value = true
    phrase.value = ''
  }

  const applyCounts = (data) => {
    counts.value = data.counts || {}
    environment.value = data.environment || null
    backupRequired.value = !!data.backup_required
    cognitoAccountsMax.value = data.cognito_accounts_max || 0
    if (backupRequired.value) backupBefore.value = true
    countsLoaded.value = true
  }

  const fetchCounts = async () => {
    const response = await apiClient.get('/admin/reset')
    applyCounts(response.data.data)
  }

  const load = async () => {
    if (!actions.value.refresh) return
    const previous = state.value
    if (previous === 'success') {
      result.value = null
      resetOptions()
    } else if (previous === 'error') {
      error.value = null
    }
    state.value = 'busy'
    busyLabel.value = 'loading'
    try {
      await fetchCounts()
      busyLabel.value = null
      // Refresh in `partial` keeps the frozen selection and the banner
      state.value = previous === 'partial' ? 'partial' : 'idle'
    } catch (err) {
      countsLoaded.value = false
      busyLabel.value = null
      const envelope = err?.response?.data?.error
      error.value = buildError({
        code: envelope?.code || 'INTERNAL_ERROR',
        message: envelope?.message || err?.message || '',
        details: envelope?.details || null
      })
      state.value = 'error'
    }
  }

  const toggle = (id) => {
    if (!actions.value.checkboxes || !PURGE_SET_IDS.includes(id)) return
    if (locked.value.includes(id)) return
    chosen.value = chosen.value.includes(id)
      ? chosen.value.filter((x) => x !== id)
      : [...chosen.value, id]
    syncCognito()
    markChanged()
  }

  // "Tout purger": every set chosen, Cognito left unchecked
  const selectAll = () => {
    if (!actions.value.selectAll) return
    chosen.value = [...PURGE_SET_IDS]
    cognitoOption.value = false
    markChanged()
  }

  const setCognito = (value) => {
    if (!actions.value.options || !cognitoVisible.value) return
    cognitoOption.value = !!value
    markChanged()
  }

  const setBackup = (value) => {
    if (!actions.value.options || backupRequired.value) return
    backupBefore.value = !!value
    markChanged()
  }

  const setPhrase = (value) => {
    if (!actions.value.phraseInput) return
    phrase.value = value
    markChanged()
  }

  const purge = async () => {
    if (!canPurge.value) return
    const body = {
      sets: [...effective.value],
      delete_cognito: cognitoVisible.value && cognitoOption.value,
      backup_before: backupRequired.value ? true : backupBefore.value,
      confirmation_phrase: phrase.value
    }
    state.value = 'busy'
    busyLabel.value = 'purging'
    try {
      const response = await apiClient.post('/admin/reset', body)
      result.value = response.data.data
      error.value = null
      phrase.value = ''
      busyLabel.value = null
      state.value = 'success'
      // Reload the counts in the background without leaving `success`
      fetchCounts().catch(() => {})
    } catch (err) {
      const next = nextStateFromResetError(err)
      const envelope = err?.response?.data?.error
      busyLabel.value = null
      error.value = buildError({
        code: next.code,
        outcomeUnknown: next.outcomeUnknown,
        message: envelope?.message || '',
        details: next.details
      })
      phrase.value = '' // the phrase must be retyped for any new attempt
      state.value = next.state
    }
  }

  // "Terminer" (success), "Réessayer" (error) or close: reload the counts
  const dismiss = async () => {
    if (state.value === 'busy') return
    await load()
  }

  return {
    state, busyLabel, counts, countsLoaded, environment, backupRequired, cognitoAccountsMax,
    chosen, effective, locked, cognitoOption, cognitoVisible, backupBefore, phrase,
    result, error, externalBusy, preResetBackupId, canPurge, actions,
    confirmationPhrase: CONFIRMATION_PHRASE,
    lockedBy, load, toggle, selectAll, setCognito, setBackup, setPhrase, purge, dismiss,
    busyLabelKey: computed(() => (busyLabel.value ? `${OPERATIONS_KEY}.${busyLabel.value}` : null))
  }
}
