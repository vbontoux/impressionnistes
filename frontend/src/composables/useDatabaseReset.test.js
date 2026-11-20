import { describe, it, expect, vi } from 'vitest'
import { flushPromises } from '@vue/test-utils'

vi.mock('../services/apiClient', () => ({
  default: { get: vi.fn(), post: vi.fn(), delete: vi.fn() }
}))

import apiClient from '../services/apiClient'
import { useDatabaseReset, nextStateFromResetError } from './useDatabaseReset'
import { CONFIRMATION_PHRASE, PURGE_SET_IDS, requiredBy } from '../utils/resetRules'

const PRE_ID = 'safety-pre-reset_2026-11-01T14-30-00Z.json'

const countsResponse = (overrides = {}) => ({
  data: {
    data: {
      environment: 'dev',
      backup_required: false,
      counts: { boats: 3, payments: 2, crew: 5, managers: 1, temp_access: 0, audit_logs: 4 },
      cognito_accounts_max: 1,
      ...overrides
    }
  }
})

const httpError = (status, code, details, message = 'msg') => ({
  response: { status, data: { error: { code, message, details } } }
})

const deferred = () => {
  let resolve
  let reject
  const promise = new Promise((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve, reject }
}

async function toIdle(overrides) {
  apiClient.get.mockReset()
  apiClient.post.mockReset()
  apiClient.get.mockResolvedValue(countsResponse(overrides))
  const c = useDatabaseReset()
  await c.load()
  return c
}

async function toReady(overrides) {
  const c = await toIdle(overrides)
  c.setPhrase(CONFIRMATION_PHRASE)
  return c
}

const successResult = {
  data: {
    data: {
      sets: ['boats', 'payments'],
      deleted: { boats: 3, payments: 2 },
      total_deleted: 5,
      cognito: { requested: false },
      pre_reset_backup: { backup_id: PRE_ID }
    }
  }
}

describe('useDatabaseReset load', () => {
  it('starts idle with defaults after loading counts', async () => {
    const c = await toIdle()
    expect(c.state.value).toBe('idle')
    expect(c.chosen.value).toEqual(['boats'])
    expect(c.effective.value).toEqual(['boats', 'payments'])
    expect(c.locked.value).toEqual(['payments'])
    expect(c.lockedBy('payments')).toEqual(['boats'])
    expect(c.phrase.value).toBe('')
    expect(c.cognitoOption.value).toBe(false)
    expect(c.backupBefore.value).toBe(true)
    expect(c.counts.value.boats).toBe(3)
    expect(c.environment.value).toBe('dev')
  })

  it('goes busy while loading', async () => {
    const c = await toIdle()
    const d = deferred()
    apiClient.get.mockReturnValue(d.promise)
    const p = c.load()
    expect(c.state.value).toBe('busy')
    expect(c.busyLabel.value).toBe('loading')
    expect(c.actions.value.purge).toBe(false)
    expect(c.actions.value.checkboxes).toBe(false)
    expect(c.actions.value.refresh).toBe(false)
    d.resolve(countsResponse())
    await p
    expect(c.state.value).toBe('idle')
  })

  it('ends in error when counts fail to load', async () => {
    apiClient.get.mockReset()
    apiClient.get.mockRejectedValue(httpError(500, 'INTERNAL_ERROR'))
    const c = useDatabaseReset()
    await c.load()
    expect(c.state.value).toBe('error')
    expect(c.error.value.code).toBe('INTERNAL_ERROR')
    expect(c.actions.value.purge).toBe(false)
  })
})

describe('useDatabaseReset selection', () => {
  it('toggling moves idle to ready_to_purge and applies the closure', async () => {
    const c = await toIdle()
    c.toggle('crew')
    expect(c.state.value).toBe('ready_to_purge')
    expect(c.effective.value).toEqual(['boats', 'payments', 'crew'])
    expect(c.locked.value).toEqual(['boats', 'payments'])
  })

  it('locks an explicitly chosen set required by another, and unlocks it when that one is unchecked', async () => {
    const c = await toIdle()
    c.toggle('crew')
    expect(c.locked.value).toEqual(['boats', 'payments'])
    expect(c.lockedBy('boats')).toEqual(['crew'])

    c.toggle('boats') // no-op: locked
    expect(c.chosen.value).toEqual(['boats', 'crew'])
    expect(c.effective.value).toContain('boats')

    c.toggle('crew')
    expect(c.chosen.value).toEqual(['boats'])
    expect(c.effective.value).toEqual(['boats', 'payments'])
    expect(c.locked.value).toEqual(['payments'])

    c.toggle('boats') // now free to uncheck
    expect(c.chosen.value).toEqual([])
  })

  it('cascades the locks through managers', async () => {
    const c = await toIdle()
    c.toggle('managers')
    expect(c.effective.value).toEqual(['boats', 'payments', 'crew', 'managers', 'temp_access'])
    expect(c.locked.value).toEqual(['boats', 'payments', 'crew', 'temp_access'])
    c.toggle('crew') // locked: no-op
    expect(c.chosen.value).toEqual(['boats', 'managers'])
    c.toggle('managers')
    expect(c.effective.value).toEqual(['boats', 'payments'])
    expect(c.locked.value).toEqual(['payments'])
  })

  it('selectAll then successive unchecks unlock sets step by step', async () => {
    const c = await toIdle()
    c.selectAll()
    expect(c.locked.value).toEqual(['boats', 'payments', 'crew', 'temp_access'])

    c.toggle('crew') // locked: no-op
    c.toggle('boats') // locked: no-op
    expect(c.chosen.value).toHaveLength(6)

    c.toggle('managers')
    expect(c.locked.value).toEqual(['boats', 'payments'])
    expect(c.effective.value).toEqual(['boats', 'payments', 'crew', 'temp_access', 'audit_logs'])

    c.toggle('crew')
    expect(c.locked.value).toEqual(['payments'])
    c.toggle('boats')
    expect(c.locked.value).toEqual([])
    c.toggle('payments')
    c.toggle('temp_access')
    c.toggle('audit_logs')
    expect(c.chosen.value).toEqual([])
    expect(c.effective.value).toEqual([])
  })

  it('keeps locked/effective/chosen consistent for every starting subset and toggle sequence', async () => {
    const c = await toIdle()
    const ids = PURGE_SET_IDS
    const check = () => {
      for (const id of c.effective.value) {
        const required = requiredBy(id, c.chosen.value).length > 0
        expect(c.locked.value.includes(id)).toBe(required)
        if (!required) expect(c.chosen.value).toContain(id)
      }
      for (const id of c.locked.value) expect(c.effective.value).toContain(id)
    }
    for (let mask = 0; mask < 64; mask++) {
      c.chosen.value = ids.filter((_, i) => mask & (1 << i))
      check()
      for (const id of ids) {
        const before = [...c.chosen.value]
        const wasLocked = c.locked.value.includes(id)
        c.toggle(id)
        if (wasLocked) expect(c.chosen.value).toEqual(before)
        check()
      }
    }
  })

  it('ignores toggling a locked set', async () => {
    const c = await toIdle()
    c.toggle('payments')
    expect(c.chosen.value).toEqual(['boats'])
    expect(c.state.value).toBe('idle')
  })

  it('selectAll chooses every set and leaves Cognito unchecked', async () => {
    const c = await toIdle()
    c.selectAll()
    expect(c.chosen.value).toHaveLength(6)
    expect(c.cognitoVisible.value).toBe(true)
    expect(c.cognitoOption.value).toBe(false)
  })

  it('shows the Cognito option only with managers and resets it when managers leaves', async () => {
    const c = await toIdle()
    expect(c.cognitoVisible.value).toBe(false)
    c.setCognito(true)
    expect(c.cognitoOption.value).toBe(false)

    c.toggle('managers')
    expect(c.cognitoVisible.value).toBe(true)
    c.setCognito(true)
    expect(c.cognitoOption.value).toBe(true)

    c.toggle('managers')
    expect(c.cognitoVisible.value).toBe(false)
    expect(c.cognitoOption.value).toBe(false)
  })

  it('selectAll resets a checked Cognito option', async () => {
    const c = await toIdle()
    c.toggle('managers')
    c.setCognito(true)
    c.selectAll()
    expect(c.cognitoOption.value).toBe(false)
  })
})

describe('useDatabaseReset backup option', () => {
  it('can be unchecked in dev', async () => {
    const c = await toIdle()
    c.setBackup(false)
    expect(c.backupBefore.value).toBe(false)
  })

  it('is forced and locked when backup_required', async () => {
    const c = await toIdle({ environment: 'prod', backup_required: true })
    expect(c.backupBefore.value).toBe(true)
    c.setBackup(false)
    expect(c.backupBefore.value).toBe(true)
  })
})

describe('useDatabaseReset purge gating', () => {
  it('requires the exact phrase', async () => {
    const c = await toIdle()
    expect(c.actions.value.purge).toBe(false)
    for (const bad of ['purger la base', 'PURGER LA BASE ', 'RESTAURER LA BASE', '']) {
      c.setPhrase(bad)
      expect(c.actions.value.purge).toBe(false)
    }
    c.setPhrase(CONFIRMATION_PHRASE)
    expect(c.actions.value.purge).toBe(true)
  })

  it('is blocked while the backup section is busy', async () => {
    const c = await toReady()
    expect(c.actions.value.purge).toBe(true)
    c.externalBusy.value = true
    expect(c.actions.value.purge).toBe(false)
    await c.purge()
    expect(apiClient.post).not.toHaveBeenCalled()
  })

  it('does nothing without a valid phrase', async () => {
    const c = await toIdle()
    await c.purge()
    expect(apiClient.post).not.toHaveBeenCalled()
  })
})

describe('useDatabaseReset purge', () => {
  it('posts the documented body and reaches success', async () => {
    const c = await toReady()
    c.toggle('managers')
    c.setCognito(true)
    apiClient.post.mockResolvedValue(successResult)
    await c.purge()
    await flushPromises()

    expect(apiClient.post).toHaveBeenCalledWith('/admin/reset', {
      sets: ['boats', 'payments', 'crew', 'managers', 'temp_access'],
      delete_cognito: true,
      backup_before: true,
      confirmation_phrase: CONFIRMATION_PHRASE
    })
    expect(c.state.value).toBe('success')
    expect(c.phrase.value).toBe('')
    expect(c.preResetBackupId.value).toBe(PRE_ID)
    expect(c.actions.value.finish).toBe(true)
    expect(c.actions.value.restoreBackup).toBe(true)
    expect(c.actions.value.checkboxes).toBe(false)
  })

  it('sends delete_cognito false without managers and backup_before false in dev', async () => {
    const c = await toReady()
    c.setBackup(false)
    apiClient.post.mockResolvedValue({
      data: { data: { sets: ['boats', 'payments'], pre_reset_backup: null } }
    })
    await c.purge()
    const body = apiClient.post.mock.calls[0][1]
    expect(body.delete_cognito).toBe(false)
    expect(body.backup_before).toBe(false)
    expect(c.preResetBackupId.value).toBe(null)
    expect(c.actions.value.restoreBackup).toBe(false)
  })

  it('sends backup_before true in prod', async () => {
    const c = await toReady({ environment: 'prod', backup_required: true })
    apiClient.post.mockResolvedValue(successResult)
    await c.purge()
    expect(apiClient.post.mock.calls[0][1].backup_before).toBe(true)
  })

  it('accepts a backup id under the id key', async () => {
    const c = await toReady()
    apiClient.post.mockResolvedValue({ data: { data: { pre_reset_backup: { id: PRE_ID } } } })
    await c.purge()
    expect(c.preResetBackupId.value).toBe(PRE_ID)
  })

  it('is busy with the purging label during the request', async () => {
    const c = await toReady()
    const d = deferred()
    apiClient.post.mockReturnValue(d.promise)
    const p = c.purge()
    expect(c.state.value).toBe('busy')
    expect(c.busyLabel.value).toBe('purging')
    expect(c.actions.value.phraseInput).toBe(false)
    expect(c.actions.value.purge).toBe(false)
    d.resolve(successResult)
    await p
    await flushPromises()
    expect(c.state.value).toBe('success')
  })

  it('finish returns to idle with defaults', async () => {
    const c = await toReady()
    apiClient.post.mockResolvedValue(successResult)
    await c.purge()
    await flushPromises()
    await c.dismiss()
    expect(c.state.value).toBe('idle')
    expect(c.result.value).toBe(null)
    expect(c.chosen.value).toEqual(['boats'])
  })
})

describe('useDatabaseReset purge errors', () => {
  it('maps a validation error to error and clears the phrase', async () => {
    const c = await toReady()
    apiClient.post.mockRejectedValue(httpError(400, 'BACKUP_REQUIRED'))
    await c.purge()
    expect(c.state.value).toBe('error')
    expect(c.error.value.code).toBe('BACKUP_REQUIRED')
    expect(c.error.value.outcomeUnknown).toBe(false)
    expect(c.phrase.value).toBe('')
    expect(c.actions.value.purge).toBe(false)
    expect(c.actions.value.checkboxes).toBe(true)
  })

  it('maps RESET_PARTIAL to partial with the backup id from details', async () => {
    const c = await toReady()
    apiClient.post.mockRejectedValue(
      httpError(500, 'RESET_PARTIAL', { stage: 'crew', pre_reset_backup_id: PRE_ID })
    )
    await c.purge()
    expect(c.state.value).toBe('partial')
    expect(c.error.value.details.stage).toBe('crew')
    expect(c.preResetBackupId.value).toBe(PRE_ID)
    expect(c.actions.value.restoreBackup).toBe(true)
    expect(c.actions.value.checkboxes).toBe(false)
    expect(c.phrase.value).toBe('')
  })

  it('retyping the phrase after an error enables a new purge', async () => {
    const c = await toReady()
    apiClient.post.mockRejectedValueOnce(httpError(500, 'INTERNAL_ERROR'))
    await c.purge()
    c.setPhrase(CONFIRMATION_PHRASE)
    expect(c.state.value).toBe('ready_to_purge')
    expect(c.actions.value.purge).toBe(true)
  })

  it('treats a missing response as an unknown outcome', async () => {
    const c = await toReady()
    apiClient.post.mockRejectedValue(new Error('Network Error'))
    await c.purge()
    expect(c.state.value).toBe('error')
    expect(c.error.value.code).toBe('UNKNOWN_OUTCOME')
    expect(c.error.value.outcomeUnknown).toBe(true)
  })
})

describe('nextStateFromResetError', () => {
  it.each([
    ['no response', { message: 'Network Error' }],
    ['timeout', { code: 'ECONNABORTED', message: 'timeout' }],
    ['401', { response: { status: 401, data: { error: { code: 'UNAUTHORIZED' } } } }],
    ['504', { response: { status: 504, data: { error: { code: 'X' } } } }],
    ['non-envelope body', { response: { status: 500, data: '<html>' } }],
    ['envelope without code', { response: { status: 500, data: { error: {} } } }]
  ])('%s gives UNKNOWN_OUTCOME', (_name, err) => {
    expect(nextStateFromResetError(err)).toEqual({
      state: 'error',
      code: 'UNKNOWN_OUTCOME',
      outcomeUnknown: true,
      details: null
    })
  })

  it.each([
    [httpError(400, 'INVALID_SELECTION', { missing: ['boats'] }), 'error', 'INVALID_SELECTION'],
    [httpError(500, 'PRE_RESET_BACKUP_FAILED', { database_modified: false }), 'error', 'PRE_RESET_BACKUP_FAILED'],
    [httpError(500, 'RESET_PARTIAL', { stage: 'boats' }), 'partial', 'RESET_PARTIAL']
  ])('classifies envelope errors', (err, state, code) => {
    const next = nextStateFromResetError(err)
    expect(next.state).toBe(state)
    expect(next.code).toBe(code)
    expect(next.outcomeUnknown).toBe(false)
  })
})
