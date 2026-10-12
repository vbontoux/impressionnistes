# License Verification Connection Error Bugfix Design

## Overview

When an administrator verifies FFAviron licenses, the frontend license checker
(`frontend/src/utils/licenseChecker.js`) reaches the FFAviron intranet through the
`/admin/html-proxy` endpoint. If that request throws (network outage, proxy error, API
failure), the error is caught inside `searchByQuery(...)` and collapsed into a generic
`{ success: false, rows: null, error: error.message }`. This is **indistinguishable** from
the other failure the same function returns when the HTML loads fine but contains no results
table (`{ success: false, rows: null, error: 'No results table found' }`).

Downstream, Strategy 2 in `checkLicense(...)` maps **every** `success === false` outcome onto
the single `searchFailed` message and appends the raw, untranslated `error` string. The batch
runner `checkLicensesBatch(...)` has an analogous problem: thrown errors become an untranslated
`details: "Error: {message}"`. The net effect is that a genuine connection/infrastructure
failure looks identical to a definitive "no matching license" outcome, misleading the admin.

The fix is targeted and minimal: tag the search outcome with the **cause** of failure so a
thrown-error (connection/infrastructure) path is distinguishable from a benign parse-but-no-
results path. Callers then route a connection error to a new dedicated, translated message
(`connectionError`) and signal that the result is inconclusive, while leaving every other
outcome byte-for-byte unchanged. This is a frontend-only change (Vue/JS plus locale JSON).

The thrown-error class is itself not uniform, and the proxy already distinguishes its
sub-cases. `functions/admin/html_proxy.py` maps a FFAviron 401/403 to HTTP **401** with the
message "Authentication failed. Cookies may have expired.", a connection failure to HTTP
**502** ("Failed to connect to target: ..."), and a timeout to HTTP **504** ("Request timed
out"). On the frontend the rejected request exposes `error.response?.status`, so a `401`
cleanly identifies a **bad or expired FFAviron session cookie** — an authentication problem
the admin fixes by re-authenticating / refreshing the cookie — while any other status (502,
504) or a pure network failure with no response is a **generic connection error**. The fix
therefore tags the thrown-error outcome with `errorType = 'auth'` when the rejection carries a
401, and `errorType = 'connection'` otherwise, and routes the two to **distinct** translated
messages (`cookieError` for auth, `connectionError` for the generic case). This distinction is
applied identically in both the search-by-license-number step and the batch runner.

## Glossary

- **Bug_Condition (C)**: The search could not be completed because the request itself threw —
  the outcome originated from the `catch` block in `searchByQuery(...)` (network / proxy / API
  failure) — as opposed to the HTML being retrieved successfully but yielding no matching rows.
- **Property (P)**: When the bug condition holds, `checkLicense`/`checkLicensesBatch` SHALL
  surface a dedicated, localized error message — the authentication/cookie message when the
  failure is an identifiable bad/expired-cookie case, otherwise the generic connection message —
  SHALL NOT leak a raw untranslated technical string as the primary message, and SHALL convey
  that the verification was inconclusive (not a definitive invalid/not-found verdict).
- **Preservation**: Every non-connection-error outcome — valid, invalid, name mismatch,
  not-found-by-license, not-found-in-results, not-found-by-name, no-name-or-license, and all
  successful lookups — must produce exactly the same validity and `details` text as today.
- **SearchOutcome**: The object returned by `searchByQuery(...)` /`extractFromProfilePage(...)`,
  currently `{ success, rows, error }` (profile path also adds `personName`). This design adds an
  `errorType` discriminator.
- **errorType**: New optional field on a failed SearchOutcome. Set on the thrown-error `catch`
  path only: `'auth'` when the rejection carries `error.response?.status === 401` (bad/expired
  FFAviron session cookie), `'connection'` for any other status (502 / 504) or a network failure
  with no response. Left absent/`null` for all parse-based failures.
- **AUTHENTICATION_ERROR / auth case**: The identifiable bad-or-expired FFAviron session-cookie
  failure, detected on the frontend by the proxy's HTTP 401 response. The admin resolves it by
  re-authenticating and refreshing the cookie.
- **GENERIC_CONNECTION_ERROR / connection case**: Any thrown-error failure that is NOT identifiable
  as an auth error — proxy HTTP 502 (connect failure), HTTP 504 (timeout), or a pure network
  failure where `error.response` is undefined.
- **cookieError**: New locale key (auth message) telling the admin the FFAviron session cookie is
  invalid/expired and to re-authenticate / refresh it.
- **connectionError**: New locale key (generic message) stating the service could not be reached
  and the verification is inconclusive.
- **searchByQuery**: Function in `frontend/src/utils/licenseChecker.js` that POSTs to
  `/admin/html-proxy` and parses the returned HTML into rows.
- **checkLicense**: Orchestrator in the same file that runs the name search (Strategy 1) and the
  license-number search (Strategy 2) and produces `{ valid, details }`.
- **checkLicensesBatch**: Loops over members calling `checkLicense`, catching any thrown error.

## Bug Details

### Bug Condition

The bug manifests when the `/admin/html-proxy` request fails during the search-by-license-number
step (Strategy 2) for an infrastructure reason — the `apiClient.post(...)` call (or response
access) throws and is caught by the `catch` block in `searchByQuery(...)`. That path returns a
generic `{ success: false, rows: null, error: error.message }`, which Strategy 2's `else` branch
cannot tell apart from a parse failure such as `'No results table found'`. Both become the
`searchFailed` message with the raw `error` string appended. The same confusion reaches
`checkLicensesBatch(...)` when `checkLicense` itself re-throws (`Request error: ...`), producing
an untranslated `details: "Error: {message}"`.

**Formal Specification:**
```
FUNCTION isBugCondition(X)
  INPUT: X of type SearchOutcome
  OUTPUT: boolean

  // True only when the search failed because the request threw (network/proxy/API),
  // i.e. the outcome came from the catch path — not from successfully retrieving HTML
  // that simply contained no matching results. Both thrown-error sub-cases (auth and
  // generic connection) satisfy the bug condition.
  RETURN X.success = false
         AND X.errorType IN { 'auth', 'connection' }
END FUNCTION
```

The thrown-error class splits into two sub-cases that must be reported with distinct messages.
The proxy exposes the signal (HTTP 401 for a bad/expired cookie) that the frontend reads from
the rejected request's `error.response.status`:

```
FUNCTION errorClass(X)
  INPUT: X of type SearchOutcome WHERE isBugCondition(X)
  OUTPUT: { AUTHENTICATION_ERROR, GENERIC_CONNECTION_ERROR }

  // searchByQuery sets X.errorType from the rejection: 'auth' when the proxy responded 401,
  // 'connection' otherwise (502 / 504 / network failure with error.response undefined).
  IF X.errorType = 'auth' THEN
    RETURN AUTHENTICATION_ERROR          // bad or expired FFAviron session cookie
  ELSE
    RETURN GENERIC_CONNECTION_ERROR      // 502 / 504 / network failure with no response
  END IF
END FUNCTION
```

### Examples

- **Network outage during Strategy 2** (no `error.response`) — Expected: a translated "connection
  error, verification could not be completed" message (`connectionError`). Actual: `"Échec de la
  recherche du numéro de licence 067741. Network Error"` (misreported as a lookup failure with raw
  English text).
- **Proxy connect failure (HTTP 502) or timeout (HTTP 504)** — Expected: translated generic
  `connectionError` message, inconclusive result. Actual: `searchFailed` with the raw thrown
  message appended.
- **Bad/expired cookie (proxy HTTP 401, `error.response.status === 401`)** — Expected: translated
  `cookieError` message telling the admin the FFAviron session cookie is invalid/expired and to
  re-authenticate / refresh it, distinct from `connectionError`, inconclusive result. Actual:
  collapsed into the same generic failure text as a true connection outage, with no hint that the
  cookie is the problem.
- **Thrown error reaching the batch runner** — Expected: `details` set to the translated
  `connectionError` message for a generic failure, or the translated `cookieError` message for a
  401 auth failure. Actual: `details: "Error: Request error: Network Error"` (raw, untranslated,
  and identical for both sub-cases).
- **Edge case — HTML retrieved but no `table` element found** (`'No results table found'`): this
  is NOT the bug condition. It is a benign parse outcome and must keep its current behavior
  (preservation).

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- A found/active/competition license still reports valid via `validLicense` (Req 3.1).
- Results returned but no row matching the number still reports `notFoundInResults` (Req 3.2).
- No results at all for the number still reports `notFoundByLicense` (Req 3.3).
- Found license with a differing name still reports `nameMismatch` (Req 3.4).
- Found but not active and/or not competition still reports `invalidLicense` with the same
  reasons (Req 3.5).
- Neither name nor license provided still reports `noNameOrLicense` (Req 3.6).
- Any successful verification (no thrown connection/infrastructure error) still produces the
  same validity result and `details` text as today, including `foundByNumber` and
  `notFoundByName` (Req 3.7).

**Scope:**
All outcomes where `isBugCondition(X)` is false must be completely unaffected by this fix. In
particular, parse-based failures (`'No results table found'`, `'No results found in table'`,
`'No data rows found'`, `'Could not extract license data from profile page'`) are NOT connection
errors and must continue to flow through the existing `searchFailed` / not-found paths exactly as
before. The `errorType` field is additive and defaults to absent for every one of these paths.

## Hypothesized Root Cause

Based on the bug description and the code, the root causes are:

1. **Lossy failure representation in `searchByQuery`**: The `catch (error)` block and the
   parse-failure returns all produce the same shape `{ success: false, rows: null, error }`.
   The cause of failure (thrown vs. parsed-empty) is discarded, so callers cannot branch on it.
   The HTTP status the proxy returned (`error.response?.status`) — which cleanly separates a 401
   bad-cookie case from a 502/504/network case — is likewise discarded.

2. **Caller conflation in `checkLicense` Strategy 2**: The `else` branch treats any
   `success === false` as `searchFailed` and interpolates the raw `error` string, both
   conflating the connection error with a definitive outcome and leaking untranslated text, and
   making no distinction between an auth failure and a generic connection failure.

3. **Untranslated batch error handling in `checkLicensesBatch`**: The `catch` block builds
   `details: "Error: " + error.message` with no translation and no connection-error semantics.
   Moreover `checkLicense` re-throws as `Request error: ${error.message}`, so the batch runner
   loses the HTTP status / `errorType` and cannot tell auth from generic connection unless the
   fix preserves that signal across the re-throw.

4. **No dedicated locale keys**: There is neither a `connectionError` nor a `cookieError` message
   in `fr.json`/`en.json`, so even a correctly-classified failure has nothing distinct and
   localized to display for either sub-case.

## Correctness Properties

Property 1: Bug Condition - Connection and authentication errors are clearly and distinctly indicated

_For any_ input where the bug condition holds (`isBugCondition` returns true — the search failed
on the thrown-error path), the fixed `checkLicense`/`checkLicensesBatch` SHALL set `details` to a
dedicated, translated message chosen by `errorClass`: the `cookieError` (authentication) message
when `errorClass(X) = AUTHENTICATION_ERROR` (proxy HTTP 401, bad/expired cookie), otherwise the
`connectionError` (generic) message when `errorClass(X) = GENERIC_CONNECTION_ERROR` (502 / 504 /
network failure with no response). The two messages SHALL be distinct from each other; neither
SHALL use a raw untranslated technical string as the primary user-facing message; and both SHALL
convey that the verification was inconclusive rather than a definitive invalid/not-found verdict.
This distinction SHALL be applied identically in the search-by-license-number step and in
`checkLicensesBatch`.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8**

Property 2: Preservation - Non-connection-error outcomes are unchanged

_For any_ input where the bug condition does NOT hold (`isBugCondition` returns false), the fixed
functions SHALL produce exactly the same `{ valid, details }` result as the original functions,
preserving every valid, invalid, name-mismatch, not-found, and no-input outcome including the
parse-based failures that currently flow through `searchFailed`.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**

## Fix Implementation

### Changes Required

Assuming the root cause analysis is correct, the fix tags connection failures at the source and
branches on that tag in both callers, then adds the localized message.

**File**: `frontend/src/utils/licenseChecker.js`

**Function**: `searchByQuery`
1. **Tag the thrown-error path with the HTTP-status discriminator**: In the `catch (error)` block,
   derive the tag from the rejected request's status and attach it to the returned object:
   ```js
   } catch (error) {
     const errorType = error.response?.status === 401 ? 'auth' : 'connection'
     return { success: false, rows: null, error: error.message, errorType }
   }
   ```
   The proxy maps a FFAviron 401/403 to HTTP 401 (bad/expired cookie), a connect failure to 502,
   and a timeout to 504; a pure network failure leaves `error.response` undefined. So `'auth'` is
   set only for the identifiable 401 case and `'connection'` for everything else (502 / 504 / no
   response). This is the single place the status→tag mapping lives.
2. **Leave all parse-failure returns unchanged**: Do not add `errorType` to the
   `'No results table found'`, `'No results found in table'`, or `'No data rows found'` returns,
   nor to `extractFromProfilePage` failures. Their shape stays `{ success:false, rows:null, error }`
   (so `errorType` is `undefined` there), preserving their classification as non-bug outcomes.

**Function**: `checkLicense` (Strategy 2 `else` branch)
3. **Branch on `errorType` before `searchFailed`**: In the `else` branch that currently returns
   `searchFailed`, branch on the tag:
   ```js
   if (licenseResult.errorType === 'auth') {
     return { valid: false, details: t('admin.licenseChecker.messages.cookieError') }
   }
   if (licenseResult.errorType === 'connection') {
     return { valid: false, details: t('admin.licenseChecker.messages.connectionError', { license: licenseNumber }) }
   }
   // else fall through to the existing searchFailed return, unchanged
   ```
   Both new messages are worded to signal an inconclusive verification (they do not assert
   invalid/not-found), satisfying Req 2.3/2.6 while keeping `valid: false` consistent with the
   surrounding contract. The `else`/`searchFailed` fall-through (parse failures, where `errorType`
   is `undefined`) is byte-for-byte unchanged, preserving the "No results table found" boundary.
4. **Do not leak raw technical text**: Neither `cookieError` nor `connectionError` interpolates the
   raw `error` string as the primary message (satisfies Req 2.2/2.6).

**Function**: `checkLicense` (`catch` block) — preserve the discriminator across the re-throw
5. **Attach `errorType` to the re-thrown Error so the batch path can branch**: `checkLicense`
   currently re-throws any thrown failure as `new Error('Request error: ...')`, which erases the
   HTTP status. To let `checkLicensesBatch` distinguish auth from connection without changing any
   non-error outcome, carry the discriminator on the thrown Error:
   ```js
   } catch (error) {
     const wrapped = new Error(`Request error: ${error.message}`)
     wrapped.errorType = error.response?.status === 401 ? 'auth' : 'connection'
     throw wrapped
   }
   ```
   This re-uses the same status→tag rule as step 1. It is strictly additive — it adds a property to
   the Error object and does not alter the thrown value's identity, message, or any returned
   `{ valid, details }` result — so every non-error outcome stays byte-for-byte unchanged
   (preservation). (This approach was chosen over "return instead of throw" because the thrown
   `catch` wraps the whole orchestration, including the Strategy 1 name search and any genuinely
   unexpected error; converting it to a return would change behavior for inputs beyond the
   connection sub-cases and risk breaking preservation.)

**Function**: `checkLicensesBatch` (`catch` block)
6. **Translate the batch error by sub-case**: Replace `details: `Error: ${error.message}`` with a
   branch on the re-thrown `error.errorType`:
   ```js
   } catch (error) {
     const details = error.errorType === 'auth'
       ? t('admin.licenseChecker.messages.cookieError')
       : t('admin.licenseChecker.messages.connectionError', { license: member.license || '' })
     results.push({ ...member, valid: false, details })
   }
   ```
   This records the dedicated translated `cookieError` for a 401 auth failure and the generic
   `connectionError` otherwise (Req 2.4/2.7/2.8). `valid` stays `false` as today. Any Error that
   reaches here without an `errorType` (e.g. the up-front `Cookie string is required` throw) falls
   into the generic branch, matching today's single untranslated-error behavior intent while no
   longer leaking the raw string as the primary message.

**File**: `frontend/src/locales/fr.json` and `frontend/src/locales/en.json`
7. **Add TWO keys** under `admin.licenseChecker.messages`, parallel to `searchFailed`:
   - **`connectionError`** (generic, interpolates `{license}`):
     - `fr`: e.g. `"connectionError": "Impossible de vérifier la licence {license} : erreur de connexion au service FFAviron. La vérification n'a pas pu aboutir — réessayez plus tard."`
     - `en`: e.g. `"connectionError": "Unable to verify license {license}: connection error reaching the FFAviron service. The verification could not be completed — please try again later."`
   - **`cookieError`** (authentication / bad-or-expired cookie — no raw string; tells the admin to
     re-authenticate / refresh the FFAviron cookie):
     - `fr`: e.g. `"cookieError": "Impossible de vérifier la licence : la session FFAviron est invalide ou expirée. Reconnectez-vous à l'intranet FFAviron et actualisez le cookie, puis relancez la vérification. La vérification n'a pas pu aboutir."`
     - `en`: e.g. `"cookieError": "Unable to verify the license: the FFAviron session is invalid or has expired. Sign in to the FFAviron intranet again, refresh the cookie, then retry. The verification could not be completed."`
   Both convey inconclusiveness, contain no raw technical string, and are distinct from each other.
   (`cookieError` takes no `{license}` placeholder because the batch path invokes it from the
   whole-orchestration `catch` without a per-row license in scope; keeping it license-free makes
   the same key reusable in both callers.)

## Testing Strategy

### Validation Approach

The strategy is two-phase: first surface counterexamples that demonstrate the bug on the UNFIXED
code, then verify the fix maps each bug-condition sub-case to its dedicated message (auth → 401 →
`cookieError`, generic → 502/504/no-response → `connectionError`), that the two messages are
distinct, and that every other outcome is unchanged (preservation). Tests exercise `checkLicense`
and `checkLicensesBatch` with a mocked `apiClient` and a `t` function; a generic connection error
is simulated by making the mocked `/admin/html-proxy` call reject with no (or a non-401) response,
and the auth error by making it reject with an error whose `response.status === 401`. Per
workspace rules, run frontend tests via `make test-frontend` and linting via `make lint-frontend`.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or
refute the root cause (lossy `success:false` shape plus caller conflation). If refuted, re-hypothesize.

**Test Plan**: Mock `apiClient.post('/admin/html-proxy', ...)` to reject during Strategy 2 — once
with a network-style error (no `response`) and once with an error carrying `response.status === 401`
— then assert the current `details`. Run against the UNFIXED code to observe the misleading output
and confirm both sub-cases currently collapse to the same text.

**Test Cases**:
1. **Generic connection error in Strategy 2 (number only)**: Mock the proxy to reject with a
   network error (no `response`); call `checkLicense(null, '067741', cookie, t)`. On unfixed code
   `details` equals the `searchFailed` message with the raw error appended (will fail the new
   assertion).
2. **Auth error in Strategy 2 (401)**: Mock the proxy to reject with `{ response: { status: 401 } }`;
   call `checkLicense(null, '067741', cookie, t)`. On unfixed code `details` is the same
   `searchFailed` text as case 1 — demonstrating the two sub-cases are indistinguishable today
   (will fail the new assertion that it equals the distinct `cookieError` message).
3. **Connection error after name search**: Provide a name whose search throws, forcing Strategy 2
   which also throws; assert the generic connection-error message (will fail on unfixed code).
4. **Batch connection error vs batch auth error**: Mock the proxy to reject (network, then 401);
   call `checkLicensesBatch([...], cookie, t)` and assert `details` is the translated
   `connectionError` for the network case and the translated `cookieError` for the 401 case, not
   `"Error: ..."` and not identical to each other (will fail on unfixed code).
5. **Edge case — no results table (NOT the bug)**: Mock the proxy to resolve with HTML lacking a
   table; assert current `searchFailed`/not-found behavior is retained (should pass before and
   after — confirms the boundary of the bug condition).

**Expected Counterexamples**:
- `details` on a thrown-error path contains the raw untranslated string and matches `searchFailed`.
- The 401 (auth) and network (connection) sub-cases produce identical `details` on the unfixed code.
- Batch `details` equals `"Error: Request error: ..."` for both sub-cases.
- Possible causes: missing failure-cause tag, dropped HTTP status, caller `else` conflation,
  untranslated batch catch, re-throw erasing the status.

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the
expected behavior (translated connection message, no raw primary text, inconclusive signal).

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition(input) DO
  result := checkLicense_fixed(input)

  IF errorClass(input) = AUTHENTICATION_ERROR THEN
    ASSERT result.details = t('admin.licenseChecker.messages.cookieError')
  ELSE
    ASSERT result.details = t('admin.licenseChecker.messages.connectionError', { license })
  END IF

  ASSERT t('admin.licenseChecker.messages.cookieError')
         <> t('admin.licenseChecker.messages.connectionError', { license })   // distinct
     AND NOT result.details.contains(rawUntranslatedTechnicalString)
     AND result.conveysInconclusive = true
END FOR
```

The same assertions apply to `checkLicensesBatch_fixed`: a 401 rejection yields the `cookieError`
`details`, a 502/504/network rejection yields the `connectionError` `details`, and the two differ.

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function
produces the same `{ valid, details }` result as the original function.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT checkLicense_original(input) = checkLicense_fixed(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation because it generates
many outcome shapes across the input domain (valid/invalid/mismatch/not-found/no-input and the
parse-based failures) and catches edge cases a few hand-written cases would miss, giving strong
confidence that behavior is unchanged for every non-connection outcome. (Note: this is frontend
JavaScript — property-based generation uses the JS test tooling; the Python no-Hypothesis rule
does not apply here.)

**Test Plan**: Observe behavior on UNFIXED code for each non-connection outcome, capture it, then
assert the fixed code yields byte-for-byte identical `details` and `valid`.

**Test Cases**:
1. **Valid license preservation**: Active + competition row returns the same `validLicense` text.
2. **Not-found-in-results preservation**: Rows returned, no match → identical `notFoundInResults`.
3. **No-results-table preservation**: Proxy resolves with table-less HTML → identical
   `searchFailed`/not-found output (the critical boundary case next to the bug condition).
4. **Name mismatch / invalid / no-input preservation**: Each returns its existing message unchanged.

### Unit Tests

- `searchByQuery` sets `errorType: 'auth'` when the rejection has `response.status === 401`,
  `errorType: 'connection'` for any other rejection (no response / 502 / 504), and leaves it
  absent on every parse-failure path.
- `checkLicense` Strategy 2 returns `cookieError` when `errorType === 'auth'`, `connectionError`
  when `errorType === 'connection'`, and `searchFailed` otherwise.
- `checkLicense`'s re-thrown Error carries `errorType` ('auth' for 401, 'connection' otherwise).
- `checkLicensesBatch` records the translated `cookieError` as `details` on a 401 auth error and
  the translated `connectionError` on a generic thrown error.
- `cookieError` and `connectionError` resolve to distinct, non-empty strings in both `fr` and `en`.

### Property-Based Tests

- Generate random non-connection SearchOutcomes and assert fixed `checkLicense` output equals the
  original for all of them (preservation).
- Generate random generic connection-error scenarios (non-401 / no response) and assert the fixed
  output is always the translated `connectionError` message with no raw technical string.
- Generate random auth-error scenarios (401) and assert the fixed output is always the translated
  `cookieError` message, distinct from `connectionError`, with no raw technical string.

### Integration Tests

- Full admin license-check flow with a simulated generic proxy failure shows the localized
  `connectionError` message in the UI rather than `searchFailed` with raw English text.
- Full admin license-check flow with a simulated 401 shows the localized `cookieError` message
  prompting the admin to refresh the FFAviron cookie, distinct from the generic connection message.
- Batch verification of multiple members where one triggers a 401 and another a generic connection
  failure reports each with its respective dedicated message while others keep their normal
  outcomes.
