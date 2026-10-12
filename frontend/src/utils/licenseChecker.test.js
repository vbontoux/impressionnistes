/**
 * License Checker — connection / authentication error bugfix tests
 * Spec: license-verification-connection-error
 *
 * This file contains BOTH:
 *  - Property 1 (Bug Condition) exploration tests — encode the EXPECTED (post-fix)
 *    behavior. They MUST FAIL on the unfixed code (failure proves the bug).
 *  - Property 2 (Preservation) tests — observation-first baseline capture for every
 *    non-connection outcome. They MUST PASS on the unfixed code.
 *
 * The frontend uses vitest + fast-check. We mock `@/services/apiClient` and pass a
 * stub `t` that returns identifiable, distinct strings per key so that `connectionError`
 * and `cookieError` are observably different.
 */
import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest'
import * as fc from 'fast-check'

// Mock the apiClient module (default export with a `post` method)
vi.mock('@/services/apiClient', () => ({
  default: {
    post: vi.fn()
  }
}))

import apiClient from '@/services/apiClient'
import { checkLicense, checkLicensesBatch } from './licenseChecker.js'

/**
 * Stub translate function.
 * Returns a stable, key-identifiable string and appends interpolation params so that
 * different keys / params produce observably different strings. This mirrors how
 * vue-i18n would resolve distinct messages per key.
 */
function makeT() {
  return (key, params) => {
    const shortKey = key.replace('admin.licenseChecker.messages.', '')
    if (params && Object.keys(params).length > 0) {
      const paramStr = Object.entries(params)
        .map(([k, v]) => `${k}=${v}`)
        .join('|')
      return `[${shortKey}](${paramStr})`
    }
    return `[${shortKey}]`
  }
}

const COOKIE = 'session=abc123'

// A network-style rejection (no `response`) → generic connection error.
function networkError(message = 'Network Error') {
  return new Error(message)
}

// A 401 rejection carrying `response.status === 401` → authentication / bad-cookie error.
function authError(message = 'Request failed with status code 401') {
  const err = new Error(message)
  err.response = { status: 401 }
  return err
}

// A non-401 HTTP rejection (e.g. 502 / 504) → still a generic connection error.
function httpError(status, message) {
  const err = new Error(message || `Request failed with status code ${status}`)
  err.response = { status }
  return err
}

beforeEach(() => {
  vi.clearAllMocks()
})

afterEach(() => {
  vi.clearAllMocks()
})

/**
 * Property 1: Bug Condition — Connection and Authentication Errors Are Clearly
 * and Distinctly Indicated.
 *
 * These tests encode the EXPECTED (post-fix) behavior and MUST FAIL on unfixed code.
 * Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8
 */
describe('Property 1 (Bug Condition): connection and auth errors are distinct and translated', () => {
  const t = makeT()
  const connectionMsg = (license) =>
    t('admin.licenseChecker.messages.connectionError', { license })
  const cookieMsg = () => t('admin.licenseChecker.messages.cookieError')

  // Raw technical strings that must NOT leak as the primary user-facing message.
  const rawStrings = [
    'Network Error',
    'Request failed with status code 502',
    'Request failed with status code 504',
    'Request failed with status code 401',
    'No results table found',
    'Error:',
    'Request error:'
  ]

  function assertNoRawLeak(details) {
    for (const raw of rawStrings) {
      expect(details).not.toContain(raw)
    }
  }

  test('resolved cookieError and connectionError messages are distinct', () => {
    expect(cookieMsg()).not.toBe(connectionMsg('067741'))
  })

  test('Case A — generic connection error in Strategy 2 (number only) → connectionError', async () => {
    apiClient.post.mockRejectedValueOnce(networkError())

    const result = await checkLicense(null, '067741', COOKIE, t)

    // Expected (post-fix): dedicated translated connectionError, NOT searchFailed + raw error.
    expect(result.valid).toBe(false)
    expect(result.details).toBe(connectionMsg('067741'))
    assertNoRawLeak(result.details)
  })

  test('Case A2 — 502 / 504 in Strategy 2 → connectionError (generic)', async () => {
    for (const status of [502, 504]) {
      vi.clearAllMocks()
      apiClient.post.mockRejectedValueOnce(httpError(status))

      const result = await checkLicense(null, '067741', COOKIE, t)

      expect(result.valid).toBe(false)
      expect(result.details).toBe(connectionMsg('067741'))
      assertNoRawLeak(result.details)
    }
  })

  test('Case B — auth error in Strategy 2 (401) → cookieError, distinct from connectionError', async () => {
    apiClient.post.mockRejectedValueOnce(authError())

    const result = await checkLicense(null, '067741', COOKIE, t)

    // Expected (post-fix): dedicated translated cookieError, distinct from connectionError.
    expect(result.valid).toBe(false)
    expect(result.details).toBe(cookieMsg())
    expect(result.details).not.toBe(connectionMsg('067741'))
    assertNoRawLeak(result.details)
  })

  test('Case C — connection error after name search (both strategies) → connectionError', async () => {
    // Strategy 1 (name) rejects, then Strategy 2 (license number) also rejects.
    apiClient.post
      .mockRejectedValueOnce(networkError())
      .mockRejectedValueOnce(networkError())

    const result = await checkLicense('Jane Doe', '067741', COOKIE, t)

    expect(result.valid).toBe(false)
    expect(result.details).toBe(connectionMsg('067741'))
    assertNoRawLeak(result.details)
  })

  test('Case D — batch: generic connection error vs auth error map to distinct translated messages', async () => {
    // Generic connection (network) case. Persistent reject so BOTH Strategy 1
    // (name) and Strategy 2 (license number) searches fail the same way; the error
    // must propagate out of checkLicense to the batch catch with errorType tagged.
    apiClient.post.mockRejectedValue(networkError())
    const genericResults = await checkLicensesBatch(
      [{ name: 'Jane Doe', license: '067741' }],
      COOKIE,
      t
    )
    expect(genericResults).toHaveLength(1)
    expect(genericResults[0].valid).toBe(false)
    expect(genericResults[0].details).toBe(connectionMsg('067741'))
    assertNoRawLeak(genericResults[0].details)

    // Auth (401) case. Persistent 401 reject so both strategy calls fail with 401.
    vi.clearAllMocks()
    apiClient.post.mockRejectedValue(authError())
    const authResults = await checkLicensesBatch(
      [{ name: 'Jane Doe', license: '067741' }],
      COOKIE,
      t
    )
    expect(authResults).toHaveLength(1)
    expect(authResults[0].valid).toBe(false)
    expect(authResults[0].details).toBe(cookieMsg())
    assertNoRawLeak(authResults[0].details)

    // The two sub-cases must NOT be identical.
    expect(genericResults[0].details).not.toBe(authResults[0].details)
  })

  test('Case D2 — batch catch: a thrown Error without errorType falls into generic connectionError (no raw leak)', async () => {
    // The up-front "Cookie string is required" throw reaches the batch catch with
    // no errorType → generic connectionError, never leaking the raw message.
    const results = await checkLicensesBatch(
      [{ name: 'Jane Doe', license: '067741' }],
      '', // empty cookie forces checkLicense to throw before any proxy call
      t
    )
    expect(apiClient.post).not.toHaveBeenCalled()
    expect(results).toHaveLength(1)
    expect(results[0].valid).toBe(false)
    expect(results[0].details).toBe(connectionMsg('067741'))
    assertNoRawLeak(results[0].details)
  })

  test('Case D3 — batch end-to-end: a persistent 401 surfaces the auth cookieError, distinct from connectionError', async () => {
    // A 401 on every proxy call drives the auth sub-case through to the batch
    // result (Strategy 2 branch tags errorType 'auth' → cookieError). Confirms the
    // auth/connection distinction holds through checkLicensesBatch.
    vi.clearAllMocks()
    apiClient.post.mockRejectedValue(authError())
    const results = await checkLicensesBatch(
      [{ name: 'Jane Doe', license: '067741' }],
      COOKIE,
      t
    )
    expect(results[0].valid).toBe(false)
    expect(results[0].details).toBe(cookieMsg())
    expect(results[0].details).not.toBe(connectionMsg('067741'))
    assertNoRawLeak(results[0].details)
  })

  /**
   * Scoped property-based variant: across many license numbers and rejection
   * messages, the generic sub-case always maps to connectionError and the auth
   * sub-case always maps to cookieError, and the two stay distinct.
   */
  test('Property: generic sub-case → connectionError, auth sub-case → cookieError (scoped)', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.record({
          license: fc.string({ minLength: 1, maxLength: 10 }).filter((s) => s.trim().length > 0),
          message: fc.constantFrom(
            'Network Error',
            'Request failed with status code 502',
            'Request failed with status code 504',
            'timeout of 0ms exceeded'
          ),
          isAuth: fc.boolean()
        }),
        async ({ license, message, isAuth }) => {
          vi.clearAllMocks()
          const rejection = isAuth ? authError(message) : networkError(message)
          apiClient.post.mockRejectedValueOnce(rejection)

          const result = await checkLicense(null, license, COOKIE, t)

          if (isAuth) {
            expect(result.details).toBe(cookieMsg())
          } else {
            expect(result.details).toBe(connectionMsg(license))
          }
          expect(cookieMsg()).not.toBe(connectionMsg(license))
          assertNoRawLeak(result.details)
        }
      ),
      { numRuns: 60 }
    )
  })
})

/**
 * Helpers to build a resolved `/admin/html-proxy` response whose HTML parses into
 * search-result rows. `searchByQuery` reads `response.data.data.html` and
 * `response.data.data.final_url`, then parses a <table><tbody><tr> structure where
 * each row needs >= 6 <td> cells: [license, name, _, _, state, type].
 */
function proxyResponse(html, finalUrl = 'https://intranet.ffaviron.fr/licences/recherche') {
  return { data: { data: { html, final_url: finalUrl } } }
}

function row(license, name, state, type) {
  return `<tr><td>${license}</td><td>${name}</td><td></td><td></td><td>${state}</td><td>${type}</td></tr>`
}

function tableHtml(rows) {
  return `<html><body><table class="table-generated"><tbody>${rows.join('')}</tbody></table></body></html>`
}

// HTML that produces a <table> with NO <tbody> → 'No results found in table'
const TABLE_NO_TBODY = '<html><body><table class="table-generated"></table></body></html>'
// HTML with a <tbody> but no rows → 'No data rows found'
const TABLE_EMPTY_TBODY =
  '<html><body><table class="table-generated"><tbody></tbody></table></body></html>'
// HTML with no table at all → 'No results table found' (the critical boundary case)
const NO_TABLE = '<html><body><p>Rien</p></body></html>'

/**
 * Property 2: Preservation — Non-Connection-Error Outcomes Are Unchanged.
 *
 * Observation-first: each assertion encodes the ACTUAL unfixed-code output. These
 * tests MUST PASS on unfixed code (baseline) and MUST still pass after the fix.
 * Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7
 */
describe('Property 2 (Preservation): non-connection outcomes are unchanged', () => {
  const t = makeT()

  test('Req 3.1 — valid license (active + competition) → validLicense', async () => {
    apiClient.post.mockResolvedValueOnce(
      proxyResponse(tableHtml([row('067741', 'Jane Doe', 'Active', 'Annuelle compétition')]))
    )
    const result = await checkLicense('Jane Doe', '067741', COOKIE, t)
    expect(result.valid).toBe(true)
    expect(result.details).toBe(
      '[validLicense](name=Jane Doe|license=067741|state=Active|type=Annuelle compétition)'
    )
  })

  test('Req 3.2 — rows returned but none match the number → notFoundInResults', async () => {
    // Name search returns nothing matching, Strategy 2 returns rows that do not match.
    apiClient.post
      .mockResolvedValueOnce(
        proxyResponse(tableHtml([row('999999', 'Someone Else', 'Active', 'Annuelle compétition')]))
      )
      .mockResolvedValueOnce(
        proxyResponse(tableHtml([row('999999', 'Someone Else', 'Active', 'Annuelle compétition')]))
      )
    const result = await checkLicense('Jane Doe', '067741', COOKIE, t)
    expect(result.valid).toBe(false)
    expect(result.details).toBe('[notFoundInResults](license=067741|count=1)')
  })

  test('Req 3.3 — Strategy 2 returns empty tbody (no data rows) → searchFailed (parse failure, not connection)', async () => {
    // Number-only search; empty tbody yields { success:false, error:'No data rows found' }.
    apiClient.post.mockResolvedValueOnce(proxyResponse(TABLE_EMPTY_TBODY))
    const result = await checkLicense(null, '067741', COOKIE, t)
    expect(result.valid).toBe(false)
    // Unfixed behavior: parse failures flow through searchFailed with the raw error appended.
    expect(result.details).toBe('[searchFailed](license=067741|error=No data rows found)')
  })

  test('Req 3.4 — found license, differing name → nameMismatch', async () => {
    // Name search finds the number but name differs.
    apiClient.post.mockResolvedValueOnce(
      proxyResponse(tableHtml([row('067741', 'John Smith', 'Active', 'Annuelle compétition')]))
    )
    const result = await checkLicense('Jane Doe', '067741', COOKIE, t)
    expect(result.valid).toBe(false)
    expect(result.details).toBe(
      '[nameMismatch](foundName=John Smith|expectedName=Jane Doe|license=067741|state=Active|type=Annuelle compétition)'
    )
  })

  test('Req 3.5 — found but not active and/or not competition → invalidLicense with reasons', async () => {
    apiClient.post.mockResolvedValueOnce(
      proxyResponse(tableHtml([row('067741', 'Jane Doe', 'Inactive', 'Annuelle loisir')]))
    )
    const result = await checkLicense('Jane Doe', '067741', COOKIE, t)
    expect(result.valid).toBe(false)
    expect(result.details).toBe(
      "[invalidLicense](name=Jane Doe|license=067741|reason=[statusNotActive](state=Inactive) [and] [typeNotCompetition](type=Annuelle loisir))"
    )
  })

  test('Req 3.6 — neither name nor license provided → noNameOrLicense', async () => {
    const result = await checkLicense(null, null, COOKIE, t)
    expect(result.valid).toBe(false)
    expect(result.details).toBe('[noNameOrLicense]')
    expect(apiClient.post).not.toHaveBeenCalled()
  })

  test('Req 3.7 — successful lookup by number (name matches) → foundByNumber', async () => {
    // No Strategy-1 match (name search returns a different number), Strategy 2 matches.
    apiClient.post
      .mockResolvedValueOnce(
        proxyResponse(tableHtml([row('111111', 'Other Person', 'Active', 'Annuelle compétition')]))
      )
      .mockResolvedValueOnce(
        proxyResponse(tableHtml([row('067741', 'Jane Doe', 'Active', 'Annuelle compétition')]))
      )
    const result = await checkLicense('Jane Doe', '067741', COOKIE, t)
    expect(result.valid).toBe(true)
    expect(result.details).toBe(
      '[foundByNumber](details=[validLicense](name=Jane Doe|license=067741|state=Active|type=Annuelle compétition))'
    )
  })

  test('Req 3.7 — not found by name (name provided, nothing matches) → notFoundByName', async () => {
    // Name only (no license number). Name search returns a non-matching row → not found.
    apiClient.post.mockResolvedValueOnce(
      proxyResponse(tableHtml([row('999999', 'Someone Else', 'Active', 'Annuelle compétition')]))
    )
    const result = await checkLicense('Jane Doe', null, COOKIE, t)
    expect(result.valid).toBe(false)
    expect(result.details).toBe('[notFoundByName](name=Jane Doe|license=)')
  })

  /**
   * Critical boundary case — "No results table found" is NOT the bug condition.
   * The proxy RESOLVES with table-less HTML, so searchByQuery returns
   * { success:false, rows:null, error:'No results table found' } with NO errorType.
   * This must keep flowing through searchFailed, unchanged, after the fix.
   */
  test('Boundary — "No results table found" (parse failure, not connection) → searchFailed, errorType stays undefined', async () => {
    apiClient.post.mockResolvedValueOnce(proxyResponse(NO_TABLE))
    const result = await checkLicense(null, '067741', COOKIE, t)
    expect(result.valid).toBe(false)
    expect(result.details).toBe('[searchFailed](license=067741|error=No results table found)')
  })

  test('Boundary — "No results found in table" (no tbody) → searchFailed', async () => {
    apiClient.post.mockResolvedValueOnce(proxyResponse(TABLE_NO_TBODY))
    const result = await checkLicense(null, '067741', COOKIE, t)
    expect(result.valid).toBe(false)
    expect(result.details).toBe('[searchFailed](license=067741|error=No results found in table)')
  })

  /**
   * Property-based preservation: generate many non-connection SearchOutcomes by
   * varying the parse-failure error string the proxy resolves into, and assert the
   * fixed checkLicense still routes them through searchFailed with the raw error
   * appended (byte-for-byte identical to today). None of these carry an errorType.
   */
  test('Property: parse-based failures always map to searchFailed (preservation)', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.record({
          license: fc.string({ minLength: 1, maxLength: 10 }).filter((s) => s.trim().length > 0),
          kind: fc.constantFrom('no-table', 'no-tbody', 'empty-tbody')
        }),
        async ({ license, kind }) => {
          vi.clearAllMocks()
          const html =
            kind === 'no-table' ? NO_TABLE : kind === 'no-tbody' ? TABLE_NO_TBODY : TABLE_EMPTY_TBODY
          const expectedError =
            kind === 'no-table'
              ? 'No results table found'
              : kind === 'no-tbody'
                ? 'No results found in table'
                : 'No data rows found'
          apiClient.post.mockResolvedValueOnce(proxyResponse(html))

          const result = await checkLicense(null, license, COOKIE, t)

          expect(result.valid).toBe(false)
          expect(result.details).toBe(
            `[searchFailed](license=${license}|error=${expectedError})`
          )
        }
      ),
      { numRuns: 50 }
    )
  })

  /**
   * Property-based preservation: generate many valid / invalid / mismatch outcomes
   * from successfully-parsed rows and assert the output matches the original
   * (observation-first expectation computed from the same inputs).
   */
  test('Property: successfully-parsed rows preserve valid/invalid/mismatch outcomes', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.record({
          // Constrain to HTML-safe characters (digits/letters) so the injected
          // table markup parses cleanly — a stringAfter with '<', '>' or '&' would
          // corrupt the HTML, which is a generator artifact, not product behavior.
          license: fc.stringMatching(/^[A-Za-z0-9]{1,8}$/),
          name: fc.constantFrom('Jane Doe', 'John Smith', 'Marie Curie'),
          active: fc.boolean(),
          competition: fc.boolean()
        }),
        async ({ license, name, active, competition }) => {
          vi.clearAllMocks()
          const state = active ? 'Active' : 'Inactive'
          const type = competition ? 'Annuelle compétition' : 'Annuelle loisir'
          // Name search immediately matches by license number in Strategy 1.
          // Use a persistent mock so Strategy 2 (if reached) resolves identically.
          apiClient.post.mockResolvedValue(
            proxyResponse(tableHtml([row(license, name, state, type)]))
          )

          const result = await checkLicense(name, license, COOKIE, t)

          if (active && competition) {
            expect(result.valid).toBe(true)
            expect(result.details).toBe(
              `[validLicense](name=${name}|license=${license}|state=${state}|type=${type})`
            )
          } else {
            expect(result.valid).toBe(false)
            const reasons = []
            if (!active) reasons.push(`[statusNotActive](state=${state})`)
            if (!competition) reasons.push(`[typeNotCompetition](type=${type})`)
            const reasonText = reasons.join(' [and] ')
            expect(result.details).toBe(
              `[invalidLicense](name=${name}|license=${license}|reason=${reasonText})`
            )
          }
        }
      ),
      { numRuns: 60 }
    )
  })
})
