import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { flushPromises } from '@vue/test-utils'

const confirmMock = vi.hoisted(() => vi.fn())

vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key) => key })
}))

vi.mock('./useConfirm', () => ({
  useConfirm: () => ({ confirm: confirmMock })
}))

vi.mock('../services/apiClient', () => ({
  default: { get: vi.fn(), post: vi.fn(), delete: vi.fn() }
}))

import apiClient from '../services/apiClient'
import { useBackupRestore, nextStateFromRestoreError } from './useBackupRestore'
import { CONFIRMATION_PHRASE } from '../utils/backupNaming'

const MANUAL_ID = 'manual_2026-11-01T14-30-00Z.json'
const OTHER_ID = 'manual_2026-10-01T10-00-00Z.json'
const SAFETY_ID =
  'safety-pre-restore_2026-11-01T14-31-00Z_before-restore-of_manual_2026-11-01T14-30-00Z.json'

const manual = { backup_id: MANUAL_ID, category: 'manual' }
const other = { backup_id: OTHER_ID, category: 'manual' }
const safety = { backup_id: SAFETY_ID, category: 'safety-pre-restore' }

const listResponse = (list) => ({ data: { data: { backups: list } } })

const httpError = (status, code, details, message = 'msg') => ({
  response: { status, data: { error: { code, message, details } } }
})

// Driving helpers: reach each state through real transitions
const deferred = () => {
  let resolve
  let reject
  const promise = new Promise((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve, reject }
}

async function toIdle(list = [manual, other]) {
  apiClient.get.mockResolvedValue(listResponse(list))
  const c = useBackupRestore()
  await c.load()
  return c
}

async function toReady(list = [manual, other]) {
  const c = await toIdle(list)
  c.select(manual)
  return c
}

async function toBusy() {
  const c = await toIdle()
  const d = deferred()
  apiClient.get.mockReturnValue(d.promise)
  c.load() // intentionally not awaited
  return { c, d }
}

async function toSuccess() {
  const c = await toReady()
  c.setPhrase(CONFIRMATION_PHRASE)
  apiClient.post.mockResolvedValue({
    data: { data: { purged: 3, restored: 5, safety_backup: { backup_id: SAFETY_ID } } }
  })
  apiClient.get.mockResolvedValue(listResponse([manual, other, safety]))
  await c.confirmRestore()
  await flushPromises()
  return c
}

async function toErrorWithSelection() {
  const c = await toReady()
  c.setPhrase(CONFIRMATION_PHRASE)
  apiClient.post.mockRejectedValue(httpError(400, 'BACKUP_INVALID'))
  await c.confirmRestore()
  return c
}

async function toErrorNoSelection() {
  const c = await toIdle()
  apiClient.get.mockRejectedValue(httpError(500, 'LIST_FAILED'))
  await c.load()
  return c
}

async function toPartial() {
  const c = await toReady()
  c.setPhrase(CONFIRMATION_PHRASE)
  apiClient.post.mockRejectedValue(
    httpError(500, 'RESTORE_PARTIAL', {
      safety_backup_id: SAFETY_ID,
      source_backup_id: MANUAL_ID
    })
  )
  apiClient.get.mockResolvedValue(listResponse([manual, other, safety]))
  await c.confirmRestore()
  return c
}

beforeEach(() => {
  vi.clearAllMocks()
  apiClient.get.mockReset()
  apiClient.post.mockReset()
  apiClient.delete.mockReset()
  confirmMock.mockReset()
})

describe('useBackupRestore transitions', () => {
  it('starts idle with nothing selected', () => {
    const c = useBackupRestore()
    expect(c.state.value).toBe('idle')
    expect(c.selected.value).toBeNull()
    expect(c.phrase.value).toBe('')
  })

  it('load ok: busy(loading) then idle with the list', async () => {
    const d = deferred()
    apiClient.get.mockReturnValue(d.promise)
    const c = useBackupRestore()
    const p = c.load()
    expect(c.state.value).toBe('busy')
    expect(c.busyLabel.value).toBe('loading')
    expect(c.busyLabelKey.value).toBe('admin.database.states.operations.loading')
    d.resolve(listResponse([manual]))
    await p
    expect(c.state.value).toBe('idle')
    expect(c.busyLabel.value).toBeNull()
    expect(c.backups.value).toEqual([manual])
    expect(apiClient.get).toHaveBeenCalledWith('/admin/backups')
  })

  it('load fail: error with the envelope code, database untouched (not outcomeUnknown)', async () => {
    const c = await toErrorNoSelection()
    expect(c.state.value).toBe('error')
    expect(c.error.value.code).toBe('LIST_FAILED')
    expect(c.error.value.messageKey).toBe('admin.database.errors.LIST_FAILED')
    expect(c.error.value.outcomeUnknown).toBe(false)
  })

  it('load fail without envelope: INTERNAL_ERROR; unknown code falls back to DEFAULT key', async () => {
    const c = await toIdle()
    apiClient.get.mockRejectedValue(new Error('boom'))
    await c.load()
    expect(c.error.value.code).toBe('INTERNAL_ERROR')

    apiClient.get.mockRejectedValue(httpError(500, 'SOMETHING_NEW'))
    await c.load()
    expect(c.error.value.code).toBe('SOMETHING_NEW')
    expect(c.error.value.messageKey).toBe('admin.database.errors.DEFAULT')
  })

  it('create ok: posts, reloads, returns to idle', async () => {
    const c = await toIdle([manual])
    apiClient.post.mockResolvedValue({ data: { data: {} } })
    apiClient.get.mockResolvedValue(listResponse([manual, other]))
    await c.create()
    expect(apiClient.post).toHaveBeenCalledWith('/admin/backups')
    expect(c.state.value).toBe('idle')
    expect(c.backups.value).toHaveLength(2)
  })

  it('create fail: error state', async () => {
    const c = await toIdle()
    apiClient.post.mockRejectedValue(httpError(500, 'JSON_BACKUP_FAILED'))
    await c.create()
    expect(c.state.value).toBe('error')
    expect(c.error.value.code).toBe('JSON_BACKUP_FAILED')
  })

  describe('download', () => {
    beforeEach(() => {
      URL.createObjectURL = vi.fn(() => 'blob:test')
      URL.revokeObjectURL = vi.fn()
      vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
    })
    afterEach(() => {
      vi.restoreAllMocks()
    })

    it('ok: triggers a file download and returns to idle', async () => {
      const c = await toIdle()
      apiClient.get.mockResolvedValue({ data: { data: { content: { items: [] }, filename: 'f.json' } } })
      await c.download(manual)
      expect(apiClient.get).toHaveBeenLastCalledWith(`/admin/backups/${encodeURIComponent(MANUAL_ID)}/download`)
      expect(URL.createObjectURL).toHaveBeenCalled()
      expect(c.state.value).toBe('idle')
    })

    it('fail: error state carries the backup id', async () => {
      const c = await toIdle()
      apiClient.get.mockRejectedValue(httpError(404, 'BACKUP_NOT_FOUND'))
      await c.download(manual)
      expect(c.state.value).toBe('error')
      expect(c.error.value.code).toBe('BACKUP_NOT_FOUND')
      expect(c.error.value.details.backup_id).toBe(MANUAL_ID)
    })
  })

  describe('remove', () => {
    it('cancelled: no request, state unchanged', async () => {
      const c = await toIdle()
      confirmMock.mockResolvedValue(false)
      await c.remove(manual)
      expect(apiClient.delete).not.toHaveBeenCalled()
      expect(c.state.value).toBe('idle')
    })

    it('confirmed ok: deletes, reloads, idle', async () => {
      const c = await toIdle()
      confirmMock.mockResolvedValue(true)
      apiClient.delete.mockResolvedValue({ data: {} })
      apiClient.get.mockResolvedValue(listResponse([other]))
      await c.remove(manual)
      expect(apiClient.delete).toHaveBeenCalledWith(`/admin/backups/${encodeURIComponent(MANUAL_ID)}`)
      expect(c.state.value).toBe('idle')
      expect(c.backups.value).toEqual([other])
    })

    it('confirmed fail: error state', async () => {
      const c = await toIdle()
      confirmMock.mockResolvedValue(true)
      apiClient.delete.mockRejectedValue(httpError(404, 'BACKUP_NOT_FOUND'))
      await c.remove(manual)
      expect(c.state.value).toBe('error')
      expect(c.error.value.code).toBe('BACKUP_NOT_FOUND')
    })

    it('the selected row cannot be deleted (no confirm asked)', async () => {
      const c = await toReady()
      await c.remove(manual)
      expect(confirmMock).not.toHaveBeenCalled()
      expect(apiClient.delete).not.toHaveBeenCalled()
      expect(c.state.value).toBe('ready_to_restore')
    })

    it('another row can be deleted while ready_to_restore, selection kept', async () => {
      const c = await toReady()
      confirmMock.mockResolvedValue(true)
      apiClient.delete.mockResolvedValue({ data: {} })
      apiClient.get.mockResolvedValue(listResponse([manual]))
      await c.remove(other)
      expect(c.state.value).toBe('ready_to_restore')
      expect(c.selected.value).toEqual(manual)
    })
  })

  it('select -> ready_to_restore with an empty phrase; cancel (select null) -> idle', async () => {
    const c = await toIdle()
    c.select(manual)
    expect(c.state.value).toBe('ready_to_restore')
    expect(c.selected.value).toEqual(manual)
    expect(c.phrase.value).toBe('')
    c.select(null)
    expect(c.state.value).toBe('idle')
    expect(c.selected.value).toBeNull()
  })

  it('dismiss in ready_to_restore cancels the selection', async () => {
    const c = await toReady()
    await c.dismiss()
    expect(c.state.value).toBe('idle')
    expect(c.selected.value).toBeNull()
  })

  it('changing the choice resets the phrase', async () => {
    const c = await toReady()
    c.setPhrase(CONFIRMATION_PHRASE)
    c.select(other)
    expect(c.selected.value).toEqual(other)
    expect(c.phrase.value).toBe('')
  })

  describe('setPhrase / canRestore (Property 13)', () => {
    const cases = [
      [CONFIRMATION_PHRASE, true],
      ['', false],
      [CONFIRMATION_PHRASE.toLowerCase(), false],
      [`${CONFIRMATION_PHRASE} `, false],
      [` ${CONFIRMATION_PHRASE}`, false],
      ['RESTAURER LA', false]
    ]
    it.each(cases)('phrase %j -> canRestore %s', async (value, expected) => {
      const c = await toReady()
      c.setPhrase(value)
      expect(c.phrase.value).toBe(value)
      expect(c.canRestore.value).toBe(expected)
      expect(c.actions.value.restore).toBe(expected)
    })

    it('valid phrase without a selection cannot restore', async () => {
      const c = await toIdle()
      c.setPhrase(CONFIRMATION_PHRASE)
      expect(c.phrase.value).toBe('') // input hidden in idle: ignored
      expect(c.canRestore.value).toBe(false)
    })

    it('confirmRestore does nothing when the phrase is invalid', async () => {
      const c = await toReady()
      c.setPhrase('restaurer la base')
      await c.confirmRestore()
      expect(apiClient.post).not.toHaveBeenCalled()
      expect(c.state.value).toBe('ready_to_restore')
    })
  })

  describe('confirmRestore ok -> success', () => {
    it('clears selection and phrase, exposes result, reloads the list', async () => {
      const c = await toSuccess()
      expect(apiClient.post).toHaveBeenCalledWith(
        `/admin/backups/${encodeURIComponent(MANUAL_ID)}/restore`,
        { confirmation_phrase: CONFIRMATION_PHRASE }
      )
      expect(c.state.value).toBe('success')
      expect(c.selected.value).toBeNull()
      expect(c.phrase.value).toBe('')
      expect(c.result.value.safety_backup.backup_id).toBe(SAFETY_ID)
      expect(c.error.value).toBeNull()
      expect(c.backups.value).toHaveLength(3)
    })

    it('shows busy(restoring) during the request', async () => {
      const c = await toReady()
      c.setPhrase(CONFIRMATION_PHRASE)
      const d = deferred()
      apiClient.post.mockReturnValue(d.promise)
      const p = c.confirmRestore()
      expect(c.state.value).toBe('busy')
      expect(c.busyLabel.value).toBe('restoring')
      d.reject(httpError(400, 'BACKUP_INVALID'))
      await p
    })

    it('a background reload failure does not leave success', async () => {
      const c = await toReady()
      c.setPhrase(CONFIRMATION_PHRASE)
      apiClient.post.mockResolvedValue({ data: { data: { safety_backup: { backup_id: SAFETY_ID } } } })
      apiClient.get.mockRejectedValue(new Error('x'))
      await c.confirmRestore()
      await flushPromises()
      expect(c.state.value).toBe('success')
    })

    it('undoRestore selects the safety backup and the phrase is still required (Property 14)', async () => {
      const c = await toSuccess()
      c.undoRestore()
      expect(c.state.value).toBe('ready_to_restore')
      expect(c.selected.value).toEqual(safety)
      expect(c.phrase.value).toBe('')
      expect(c.canRestore.value).toBe(false)
      expect(c.result.value).toBeNull()
      c.setPhrase(CONFIRMATION_PHRASE)
      expect(c.canRestore.value).toBe(true)
    })

    it('undoRestore falls back to a minimal safety row when the list lacks it', async () => {
      const c = await toReady()
      c.setPhrase(CONFIRMATION_PHRASE)
      apiClient.post.mockResolvedValue({ data: { data: { safety_backup: { backup_id: SAFETY_ID } } } })
      apiClient.get.mockResolvedValue(listResponse([manual]))
      await c.confirmRestore()
      await flushPromises()
      c.undoRestore()
      expect(c.selected.value.backup_id).toBe(SAFETY_ID)
      expect(c.selected.value.category).toBe('safety-pre-restore')
    })

    it('restores a safety-pre-reset backup with the same phrase and flow', async () => {
      const RESET_ID = 'safety-pre-reset_2026-11-04T08-00-00Z.json'
      const reset = { backup_id: RESET_ID, category: 'safety-pre-reset', source_ref: null }
      const c = await toIdle([manual, reset])
      expect(c.canSelect(reset)).toBe(true)
      c.select(reset)
      expect(c.state.value).toBe('ready_to_restore')
      c.setPhrase(CONFIRMATION_PHRASE)
      expect(c.canRestore.value).toBe(true)
      apiClient.post.mockResolvedValue({ data: { data: { safety_backup: { backup_id: SAFETY_ID } } } })
      await c.confirmRestore()
      expect(apiClient.post).toHaveBeenCalledWith(
        `/admin/backups/${encodeURIComponent(RESET_ID)}/restore`,
        { confirmation_phrase: CONFIRMATION_PHRASE }
      )
      expect(c.state.value).toBe('success')
    })

    it('undoRestore is a no-op outside success', async () => {
      const c = await toIdle()
      c.undoRestore()
      expect(c.state.value).toBe('idle')
    })

    it('dismiss (Close) returns to idle and clears the outcome', async () => {
      const c = await toSuccess()
      apiClient.get.mockResolvedValue(listResponse([manual]))
      await c.dismiss()
      expect(c.state.value).toBe('idle')
      expect(c.result.value).toBeNull()
    })
  })

  describe('restore failures', () => {
    it('RESTORE_PARTIAL -> partial, selection cleared, safety id exposed', async () => {
      const c = await toPartial()
      expect(c.state.value).toBe('partial')
      expect(c.selected.value).toBeNull()
      expect(c.phrase.value).toBe('')
      expect(c.error.value.code).toBe('RESTORE_PARTIAL')
      expect(c.error.value.details.safety_backup_id).toBe(SAFETY_ID)
      expect(c.error.value.details.source_backup_id).toBe(MANUAL_ID)
      expect(c.error.value.outcomeUnknown).toBe(false)
    })

    it('partial -> select safety -> ready_to_restore, keeps the error context; refresh -> idle', async () => {
      const c = await toPartial()
      c.select(safety)
      expect(c.state.value).toBe('ready_to_restore')
      expect(c.selected.value).toEqual(safety)
      expect(c.error.value.code).toBe('RESTORE_PARTIAL')

      const p = await toPartial()
      apiClient.get.mockResolvedValue(listResponse([manual]))
      await p.load()
      expect(p.state.value).toBe('idle')
      expect(p.error.value).toBeNull()
    })

    it('other restore error -> error, selection and phrase kept, retry possible', async () => {
      const c = await toErrorWithSelection()
      expect(c.state.value).toBe('error')
      expect(c.error.value.code).toBe('BACKUP_INVALID')
      expect(c.error.value.outcomeUnknown).toBe(false)
      expect(c.selected.value).toEqual(manual)
      expect(c.phrase.value).toBe(CONFIRMATION_PHRASE)
      expect(c.canRestore.value).toBe(true)

      apiClient.post.mockResolvedValue({ data: { data: { safety_backup: { backup_id: SAFETY_ID } } } })
      apiClient.get.mockResolvedValue(listResponse([manual]))
      await c.confirmRestore()
      expect(c.state.value).toBe('success')
    })

    it('outcome unknown (504) -> error with outcomeUnknown flag', async () => {
      const c = await toReady()
      c.setPhrase(CONFIRMATION_PHRASE)
      apiClient.post.mockRejectedValue({ response: { status: 504, data: 'Gateway Timeout' } })
      await c.confirmRestore()
      expect(c.state.value).toBe('error')
      expect(c.error.value.code).toBe('UNKNOWN_OUTCOME')
      expect(c.error.value.messageKey).toBe('admin.database.errors.UNKNOWN_OUTCOME')
      expect(c.error.value.outcomeUnknown).toBe(true)
    })

    it('error + dismiss -> idle (and refresh reloads)', async () => {
      const c = await toErrorWithSelection()
      apiClient.get.mockResolvedValue(listResponse([manual]))
      await c.dismiss()
      expect(c.state.value).toBe('idle')
      expect(c.error.value).toBeNull()
      expect(c.selected.value).toBeNull()
      expect(c.phrase.value).toBe('')
    })

    it('load after a restore error with a still-listed selection from ready keeps no stale outcome', async () => {
      const c = await toErrorNoSelection()
      apiClient.get.mockResolvedValue(listResponse([manual]))
      await c.dismiss()
      expect(c.state.value).toBe('idle')
    })
  })

  it('a selection that vanishes from the list is dropped on reload', async () => {
    const c = await toReady()
    apiClient.get.mockResolvedValue(listResponse([other]))
    await c.load()
    expect(c.selected.value).toBeNull()
    expect(c.state.value).toBe('idle')
  })

  it('error with selection -> Create ok -> back to ready_to_restore (Retry restore path)', async () => {
    const c = await toErrorWithSelection()
    apiClient.post.mockResolvedValue({ data: { data: {} } })
    apiClient.get.mockResolvedValue(listResponse([manual, other]))
    await c.create()
    expect(c.state.value).toBe('ready_to_restore')
    expect(c.error.value).toBeNull()
  })
})

describe('useBackupRestore enabled actions per state', () => {
  const none = {
    create: false, refresh: false, download: false, delete: false,
    select: false, phraseInput: false, restore: false
  }
  const rows = [
    ['idle', () => toIdle(), {
      create: true, refresh: true, download: true, delete: true,
      select: true, phraseInput: false, restore: false
    }],
    ['busy', async () => (await toBusy()).c, none],
    ['ready_to_restore (no phrase)', () => toReady(), {
      create: true, refresh: true, download: true, delete: true,
      select: true, phraseInput: true, restore: false
    }],
    ['success', () => toSuccess(), {
      create: false, refresh: true, download: false, delete: false,
      select: true, phraseInput: false, restore: false
    }],
    ['error (list failure, no selection)', () => toErrorNoSelection(), {
      create: true, refresh: true, download: true, delete: true,
      select: true, phraseInput: false, restore: false
    }],
    ['error (restore retry, valid phrase)', () => toErrorWithSelection(), {
      create: true, refresh: true, download: true, delete: true,
      select: true, phraseInput: true, restore: true
    }],
    ['partial', () => toPartial(), {
      create: false, refresh: true, download: true, delete: false,
      select: true, phraseInput: true, restore: false
    }]
  ]

  it.each(rows)('%s', async (_name, build, expected) => {
    const c = await build()
    expect(c.actions.value).toEqual(expected)
  })

  it('ready_to_restore with a valid phrase enables Restore', async () => {
    const c = await toReady()
    c.setPhrase(CONFIRMATION_PHRASE)
    expect(c.actions.value.restore).toBe(true)
  })

  it('busy blocks every operation call (no extra requests)', async () => {
    const { c, d } = await toBusy()
    apiClient.get.mockClear()
    await c.load()
    await c.create()
    await c.download(manual)
    await c.remove(manual)
    c.select(manual)
    await c.confirmRestore()
    await c.dismiss()
    expect(apiClient.get).not.toHaveBeenCalled()
    expect(apiClient.post).not.toHaveBeenCalled()
    expect(apiClient.delete).not.toHaveBeenCalled()
    expect(confirmMock).not.toHaveBeenCalled()
    expect(c.selected.value).toBeNull()
    expect(c.state.value).toBe('busy')
    d.resolve(listResponse([manual]))
    await flushPromises()
    expect(c.state.value).toBe('idle')
  })

  describe('row rules: canSelect / canDelete', () => {
    it('idle: everything selectable and deletable', async () => {
      const c = await toIdle([manual, other, safety])
      for (const b of [manual, other, safety]) {
        expect(c.canSelect(b)).toBe(true)
        expect(c.canDelete(b)).toBe(true)
      }
    })

    it('busy: nothing selectable or deletable', async () => {
      const { c } = await toBusy()
      expect(c.canSelect(manual)).toBe(false)
      expect(c.canDelete(manual)).toBe(false)
    })

    it('ready_to_restore: delete disabled only on the selected row', async () => {
      const c = await toReady()
      expect(c.canDelete(manual)).toBe(false)
      expect(c.canDelete(other)).toBe(true)
      expect(c.canSelect(manual)).toBe(true)
      expect(c.canSelect(other)).toBe(true)
    })

    it('success: only the safety backup is selectable, nothing deletable', async () => {
      const c = await toSuccess()
      expect(c.canSelect(safety)).toBe(true)
      expect(c.canSelect(manual)).toBe(false)
      expect(c.canSelect(other)).toBe(false)
      for (const b of [manual, other, safety]) expect(c.canDelete(b)).toBe(false)
      c.select(manual) // ignored
      expect(c.state.value).toBe('success')
    })

    it('partial: only safety and source are selectable, nothing deletable', async () => {
      const c = await toPartial()
      expect(c.canSelect(safety)).toBe(true)
      expect(c.canSelect(manual)).toBe(true)
      expect(c.canSelect(other)).toBe(false)
      for (const b of [manual, other, safety]) expect(c.canDelete(b)).toBe(false)
      c.select(other) // ignored
      expect(c.state.value).toBe('partial')
      expect(c.selected.value).toBeNull()
    })

    it('error: all selectable and deletable', async () => {
      const c = await toErrorNoSelection()
      expect(c.canSelect(other)).toBe(true)
      expect(c.canDelete(other)).toBe(true)
    })
  })
})

describe('nextStateFromRestoreError (Property 14)', () => {
  const envelope = (status, code, details) => ({ response: { status, data: { error: { code, details } } } })

  const cases = [
    ['RESTORE_PARTIAL', envelope(500, 'RESTORE_PARTIAL', { safety_backup_id: 's' }), 'partial', 'RESTORE_PARTIAL', false],
    ['BACKUP_INVALID', envelope(422, 'BACKUP_INVALID'), 'error', 'BACKUP_INVALID', false],
    ['SAFETY_BACKUP_FAILED', envelope(500, 'SAFETY_BACKUP_FAILED'), 'error', 'SAFETY_BACKUP_FAILED', false],
    ['INVALID_CONFIRMATION', envelope(400, 'INVALID_CONFIRMATION'), 'error', 'INVALID_CONFIRMATION', false],
    ['envelope on a 5xx other than 504', envelope(502, 'INTERNAL_ERROR'), 'error', 'INTERNAL_ERROR', false],
    ['HTTP 504', { response: { status: 504, data: {} } }, 'error', 'UNKNOWN_OUTCOME', true],
    ['HTTP 504 even with an envelope body', envelope(504, 'INTERNAL_ERROR'), 'error', 'UNKNOWN_OUTCOME', true],
    ['no response (network error)', new Error('Network Error'), 'error', 'UNKNOWN_OUTCOME', true],
    ['undefined error', undefined, 'error', 'UNKNOWN_OUTCOME', true],
    ['ECONNABORTED', { code: 'ECONNABORTED', response: { status: 500, data: {} } }, 'error', 'UNKNOWN_OUTCOME', true],
    ['ECONNABORTED without response', { code: 'ECONNABORTED' }, 'error', 'UNKNOWN_OUTCOME', true],
    ['HTTP 401', envelope(401, 'UNAUTHORIZED'), 'error', 'UNKNOWN_OUTCOME', true],
    ['non-envelope body (string)', { response: { status: 500, data: 'oops' } }, 'error', 'UNKNOWN_OUTCOME', true],
    ['non-envelope body (missing error)', { response: { status: 500, data: { message: 'x' } } }, 'error', 'UNKNOWN_OUTCOME', true],
    ['envelope with non-string code', { response: { status: 500, data: { error: { code: 42 } } } }, 'error', 'UNKNOWN_OUTCOME', true]
  ]

  it.each(cases)('%s', (_name, err, state, code, outcomeUnknown) => {
    const next = nextStateFromRestoreError(err)
    expect(next.state).toBe(state)
    expect(next.code).toBe(code)
    expect(next.outcomeUnknown).toBe(outcomeUnknown)
  })

  it('passes envelope details through', () => {
    const next = nextStateFromRestoreError(envelope(500, 'RESTORE_PARTIAL', { safety_backup_id: 's' }))
    expect(next.details).toEqual({ safety_backup_id: 's' })
  })
})
