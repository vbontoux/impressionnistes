import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import apiClient from '../services/apiClient'
import { useConfirm } from './useConfirm'
import { isPhraseValid, CATEGORY_SAFETY } from '../utils/backupNaming'

/**
 * Backup & restore state machine (single source of truth for the UI).
 * States: idle | busy | ready_to_restore | success | error | partial
 * Transitions happen only in this file. Labels are returned as i18n keys.
 */

const ERRORS_KEY = 'admin.database.errors'
const OPERATIONS_KEY = 'admin.database.states.operations'

// Codes with an i18n entry under admin.database.errors (plus UNKNOWN_OUTCOME / DEFAULT)
const KNOWN_CODES = [
  'NOT_FOUND', 'INVALID_BACKUP_ID', 'INVALID_CONFIRMATION', 'BACKUP_NOT_FOUND',
  'BACKUP_INVALID', 'JSON_BACKUP_FAILED', 'NATIVE_BACKUP_FAILED',
  'SAFETY_BACKUP_FAILED', 'RESTORE_PARTIAL', 'LIST_FAILED', 'INTERNAL_ERROR',
  'FORBIDDEN', 'UNAUTHORIZED'
]

const RESTORE_STATES = ['ready_to_restore', 'error', 'partial']

/**
 * Classify a failed restore request.
 * @param {Object} err - axios error
 * @returns {{state: string, code: string, outcomeUnknown: boolean, details: Object|null}}
 */
export function nextStateFromRestoreError(err) {
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
    state: envelope.code === 'RESTORE_PARTIAL' ? 'partial' : 'error',
    code: envelope.code,
    outcomeUnknown: false,
    details: envelope.details || null
  }
}

/**
 * Build the error object stored in `error` (code, i18n key, message, details).
 */
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

/** Error for list/create/download/delete: the database was not modified. */
function buildOperationError(err, backupId = null) {
  const envelope = err?.response?.data?.error
  return buildError({
    code: envelope?.code || 'INTERNAL_ERROR',
    message: envelope?.message || err?.message || '',
    details: { ...(envelope?.details || {}), ...(backupId ? { backup_id: backupId } : {}) }
  })
}

export function useBackupRestore() {
  const { t } = useI18n()
  const { confirm } = useConfirm()

  const state = ref('idle')
  const busyLabel = ref(null) // loading | creating | downloading | deleting | restoring
  const backups = ref([])
  const selected = ref(null)
  const phrase = ref('')
  const result = ref(null)
  const error = ref(null)

  const safetyId = computed(() => result.value?.safety_backup?.backup_id || error.value?.details?.safety_backup_id || null)
  const sourceId = computed(() => error.value?.details?.source_backup_id || null)

  const canRestore = computed(
    () => RESTORE_STATES.includes(state.value) && !!selected.value && isPhraseValid(phrase.value)
  )

  // Enabled actions per state (design: "Enabled actions per state")
  const actions = computed(() => {
    const s = state.value
    const notBusy = s !== 'busy'
    return {
      create: notBusy && s !== 'partial' && s !== 'success',
      refresh: notBusy,
      download: notBusy && s !== 'success',
      delete: notBusy && s !== 'partial' && s !== 'success',
      select: notBusy,
      phraseInput: s === 'ready_to_restore' || s === 'partial' || (s === 'error' && !!selected.value),
      restore: canRestore.value
    }
  })

  /** Row-level rules: which backups can be chosen / deleted in the current state. */
  const canSelect = (backup) => {
    if (!actions.value.select) return false
    if (state.value === 'success') return backup.backup_id === safetyId.value
    if (state.value === 'partial') return [safetyId.value, sourceId.value].includes(backup.backup_id)
    return true
  }
  const canDelete = (backup) => actions.value.delete && backup.backup_id !== selected.value?.backup_id

  const clearSelection = () => {
    selected.value = null
    phrase.value = ''
  }

  const clearOutcome = () => {
    result.value = null
    error.value = null
  }

  const startBusy = (label) => {
    state.value = 'busy'
    busyLabel.value = label
  }

  const fail = (err, backupId) => {
    busyLabel.value = null
    error.value = buildOperationError(err, backupId)
    state.value = 'error'
  }

  // Back to the list, keeping a still-valid restore selection
  const settle = () => {
    busyLabel.value = null
    if (selected.value && !backups.value.some((b) => b.backup_id === selected.value.backup_id)) {
      clearSelection()
    }
    state.value = selected.value ? 'ready_to_restore' : 'idle'
  }

  const fetchBackups = async () => {
    const response = await apiClient.get('/admin/backups')
    backups.value = response.data.data.backups || []
  }

  const load = async () => {
    if (!actions.value.refresh) return
    if (['error', 'success', 'partial'].includes(state.value)) {
      clearOutcome()
      clearSelection()
    }
    startBusy('loading')
    try {
      await fetchBackups()
      settle()
    } catch (err) {
      fail(err)
    }
  }

  const create = async () => {
    if (!actions.value.create) return
    startBusy('creating')
    try {
      await apiClient.post('/admin/backups')
      await fetchBackups()
      clearOutcome()
      settle()
    } catch (err) {
      fail(err)
    }
  }

  const download = async (backup) => {
    if (!actions.value.download) return
    startBusy('downloading')
    try {
      const response = await apiClient.get(`/admin/backups/${encodeURIComponent(backup.backup_id)}/download`)
      const { content, filename } = response.data.data
      const blob = new Blob([JSON.stringify(content)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename || backup.backup_id
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      clearOutcome()
      settle()
    } catch (err) {
      fail(err, backup.backup_id)
    }
  }

  const remove = async (backup) => {
    if (!canDelete(backup)) return
    // Confirm BEFORE entering busy; cancelled -> nothing happens
    const confirmed = await confirm({
      title: t('admin.database.list.deleteConfirmTitle'),
      message: t('admin.database.list.deleteConfirmMessage', { id: backup.backup_id }),
      confirmText: t('admin.database.actions.delete'),
      cancelText: t('admin.database.actions.cancel'),
      variant: 'danger'
    })
    if (!confirmed) return

    startBusy('deleting')
    try {
      await apiClient.delete(`/admin/backups/${encodeURIComponent(backup.backup_id)}`)
      await fetchBackups()
      clearOutcome()
      settle()
    } catch (err) {
      fail(err, backup.backup_id)
    }
  }

  // Choose a backup to restore (null cancels). The phrase always starts empty.
  const select = (backup) => {
    if (!backup) {
      clearSelection()
      if (state.value === 'ready_to_restore') state.value = 'idle'
      return
    }
    if (!canSelect(backup)) return
    selected.value = backup
    phrase.value = ''
    if (state.value !== 'error' && state.value !== 'partial') clearOutcome()
    state.value = 'ready_to_restore'
  }

  const setPhrase = (value) => {
    if (actions.value.phraseInput) phrase.value = value
  }

  const confirmRestore = async () => {
    if (!canRestore.value) return
    const backupId = selected.value.backup_id
    startBusy('restoring')
    try {
      const response = await apiClient.post(
        `/admin/backups/${encodeURIComponent(backupId)}/restore`,
        { confirmation_phrase: phrase.value }
      )
      result.value = response.data.data
      error.value = null
      clearSelection()
      busyLabel.value = null
      state.value = 'success'
      // Refresh the list in the background without leaving 'success'
      fetchBackups().catch(() => {})
    } catch (err) {
      const next = nextStateFromRestoreError(err)
      const envelope = err?.response?.data?.error
      busyLabel.value = null
      error.value = buildError({
        code: next.code,
        outcomeUnknown: next.outcomeUnknown,
        message: envelope?.message || '',
        details: { ...(next.details || {}), backup_id: backupId }
      })
      if (next.state === 'partial') {
        clearSelection() // must pick the safety/source backup and retype the phrase
      }
      state.value = next.state
    }
  }

  // Select the safety backup of the last successful restore (phrase still required)
  const undoRestore = () => {
    const id = result.value?.safety_backup?.backup_id
    if (state.value !== 'success' || !id) return
    select(backups.value.find((b) => b.backup_id === id) || { backup_id: id, category: CATEGORY_SAFETY })
  }

  // Close an outcome panel (reload the list) or cancel a restore selection
  const dismiss = async () => {
    if (state.value === 'busy') return
    if (state.value === 'ready_to_restore') {
      select(null)
      return
    }
    await load()
  }

  return {
    state, busyLabel, backups, selected, phrase, result, error,
    canRestore, actions, canSelect, canDelete,
    load, create, download, remove, select, setPhrase,
    confirmRestore, undoRestore, dismiss,
    // i18n key helper for the busy label
    busyLabelKey: computed(() => (busyLabel.value ? `${OPERATIONS_KEY}.${busyLabel.value}` : null))
  }
}
