# Implementation Plan

- [ ] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Connection and Authentication Errors Are Clearly and Distinctly Indicated
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists (lossy `success:false` shape plus caller conflation / untranslated batch catch), including that the auth (401) and generic connection sub-cases currently collapse to one indistinguishable outcome
  - **Scoped PBT Approach**: Scope the property to concrete failing cases where `isBugCondition(X)` holds — i.e. `searchByQuery` rejects on the thrown-error path during Strategy 2. Split the generation into the two sub-cases from `errorClass(X)`: the **auth** case (rejection carries `error.response.status === 401`) and the **generic connection** case (no `response`, or a non-401 status such as 502 / 504). Generate over license numbers / rejection messages (e.g. "Network Error", "Request failed with status code 502") while holding each sub-case's thrown-error path fixed, to keep reproducibility.
  - Create the frontend test for `frontend/src/utils/licenseChecker.js` (co-locate with existing frontend tests, e.g. `frontend/src/utils/licenseChecker.test.js`); mock `@/services/apiClient` and pass a stub `t` that returns identifiable, distinct strings per key (so `connectionError` and `cookieError` are observably different)
  - Test case A — **Generic connection error in Strategy 2 (number only)**: mock `apiClient.post('/admin/html-proxy', ...)` to reject with a network-style error (no `response`), call `checkLicense(null, '067741', cookie, t)`, and assert `details` equals the translated `connectionError` message (not `searchFailed` with the raw error appended) — from Bug Condition in design
  - Test case B — **Auth error in Strategy 2 (401)**: mock the proxy to reject with an error carrying `response.status === 401`, call `checkLicense(null, '067741', cookie, t)`, and assert `details` equals the translated `cookieError` message — distinct from the `connectionError` text, with no raw technical string. On unfixed code this collapses to the same `searchFailed` text as case A (will fail the new assertion)
  - Test case C — **Connection error after name search**: provide a name whose proxy search rejects (no `response`), forcing Strategy 2 which also rejects; assert the translated `connectionError` message
  - Test case D — **Batch generic connection error vs batch auth error**: mock the proxy to reject once with a network error (no `response`) and once with `response.status === 401`; call `checkLicensesBatch([{ name, license }], cookie, t)` for each and assert `details` is the translated `connectionError` message for the network case and the translated `cookieError` message for the 401 case — NOT `"Error: ..."` / `"Error: Request error: ..."` and NOT identical to each other
  - **Distinctness + no-leak assertions**: assert the resolved `cookieError` and `connectionError` strings are DISTINCT from each other, and that neither surfaced `details` contains the raw untranslated technical string (e.g. "Network Error", "Request failed with status code 502", "No results table found") as the primary message
  - The test assertions must match the Expected Behavior: the auth sub-case maps to the dedicated translated `cookieError` message and the generic sub-case to the dedicated translated `connectionError` message, NO raw untranslated technical string as the primary message, and an inconclusive (not definitive invalid/not-found) signal
  - Run test on UNFIXED code via `make test-frontend`
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists). On unfixed code both the auth (401) and generic sub-cases collapse to `searchFailed` (Strategy 2) and to `"Error: Request error: ..."` (batch) — identical to each other
  - Document counterexamples found (e.g. unfixed `details` = `searchFailed` + "Network Error" for BOTH the 401 and network cases; batch `details` = `"Error: Request error: Network Error"` for both) to understand root cause
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

- [ ] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Non-Connection-Error Outcomes Are Unchanged
  - **IMPORTANT**: Follow observation-first methodology — run the UNFIXED code for each non-bug-condition outcome, record the actual `{ valid, details }`, then assert the recorded values
  - **Testing Approach**: Property-based testing is recommended here — generate many non-connection outcome shapes across the input domain so edge cases are caught (this is frontend JS; the Python no-Hypothesis rule does not apply)
  - Observe and capture UNFIXED behavior for each non-connection outcome, then assert the fixed code yields byte-for-byte identical `details` and `valid`:
    - **Valid license** → active + competition row returns the same `validLicense` text (Req 3.1)
    - **Not-found-in-results** → rows returned, no matching number → identical `notFoundInResults` (Req 3.2)
    - **Not-found-by-license** → Strategy 2 returns zero rows → identical `notFoundByLicense` (Req 3.3)
    - **Name mismatch** → found license, differing name → identical `nameMismatch` (Req 3.4)
    - **Invalid license** → found but not active and/or not competition → identical `invalidLicense` with same reasons (Req 3.5)
    - **No name or license** → identical `noNameOrLicense` (Req 3.6)
    - **Successful lookups** → identical `foundByNumber` / `notFoundByName` text (Req 3.7)
  - **Critical boundary case — "No results table found" (NOT the bug)**: mock the proxy to RESOLVE with table-less HTML so `searchByQuery` returns `{ success:false, rows:null, error:'No results table found' }` (no `errorType`); assert the `searchFailed` output is retained unchanged. This proves the fix does not misclassify a benign parse failure as a connection or auth error, and that `errorType` stays `undefined` on parse failures.
  - Property-based generation: generate random non-connection SearchOutcomes (valid/invalid/mismatch/not-found/no-input and the parse-based failures `'No results found in table'`, `'No data rows found'`, `'Could not extract license data from profile page'`) and assert fixed `checkLicense` output equals the captured original for all of them
  - Run tests on UNFIXED code via `make test-frontend`
  - **EXPECTED OUTCOME**: Tests PASS (this confirms the baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [ ] 3. Fix for connection/authentication errors being misreported as license lookup failures

  - [ ] 3.1 Add the `connectionError` and `cookieError` locale keys
    - In `frontend/src/locales/fr.json`, add TWO keys under `admin.licenseChecker.messages`, parallel to `searchFailed`:
      - `connectionError` (generic, interpolates `{license}`) — e.g. `"Impossible de vérifier la licence {license} : erreur de connexion au service FFAviron. La vérification n'a pas pu aboutir — réessayez plus tard."`
      - `cookieError` (authentication / bad-or-expired cookie, license-free) — e.g. `"Impossible de vérifier la licence : la session FFAviron est invalide ou expirée. Reconnectez-vous à l'intranet FFAviron et actualisez le cookie, puis relancez la vérification. La vérification n'a pas pu aboutir."`
    - In `frontend/src/locales/en.json`, add the parallel keys:
      - `connectionError` — e.g. `"Unable to verify license {license}: connection error reaching the FFAviron service. The verification could not be completed — please try again later."`
      - `cookieError` — e.g. `"Unable to verify the license: the FFAviron session is invalid or has expired. Sign in to the FFAviron intranet again, refresh the cookie, then retry. The verification could not be completed."`
    - Both messages MUST convey inconclusiveness, MUST NOT contain a raw technical string, and MUST be DISTINCT from each other (`cookieError` tells the admin to re-authenticate / refresh the FFAviron cookie; `connectionError` takes `{license}`, `cookieError` is license-free)
    - _Expected_Behavior: two translated, dedicated, distinct messages with no raw technical text (design "Add TWO keys")_
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

  - [ ] 3.2 Tag the thrown-error path with the HTTP-status discriminator in `searchByQuery`
    - In the `catch (error)` block of `searchByQuery`, derive the tag from the rejected request's status and attach it: `const errorType = error.response?.status === 401 ? 'auth' : 'connection'`, then `return { success: false, rows: null, error: error.message, errorType }`
    - `'auth'` is set only for the identifiable 401 case (bad/expired FFAviron cookie); `'connection'` for everything else (502 / 504 / network failure with no `response`). This is the single place the status→tag mapping lives
    - Leave ALL parse-failure returns unchanged (`'No results table found'`, `'No results found in table'`, `'No data rows found'`) and do NOT add `errorType` to `extractFromProfilePage` failures, so `errorType` stays `undefined` on every non-bug path
    - _Bug_Condition: isBugCondition(X) = X.success === false AND X.errorType IN { 'auth', 'connection' }_
    - _Expected_Behavior: errorClass(X) = 'auth' when response.status === 401, else 'connection' (design)_
    - _Preservation: parse-failure outcomes keep shape `{ success:false, rows:null, error }` with `errorType` absent_
    - _Requirements: 2.1, 2.5, 2.8_

  - [ ] 3.3 Branch on `errorType` (two-way) in `checkLicense` Strategy 2
    - In the Strategy 2 `else` branch that currently returns `searchFailed`, branch on the tag before the fall-through:
      - `if (licenseResult.errorType === 'auth')` return `{ valid: false, details: t('admin.licenseChecker.messages.cookieError') }`
      - `if (licenseResult.errorType === 'connection')` return `{ valid: false, details: t('admin.licenseChecker.messages.connectionError', { license: licenseNumber }) }`
      - otherwise fall through to the existing `searchFailed` return unchanged
    - Do NOT interpolate the raw `error` string into either message (keeps `valid: false` consistent with the surrounding contract)
    - _Bug_Condition: isBugCondition(input) where input.errorType IN { 'auth', 'connection' }_
    - _Expected_Behavior: expectedBehavior → cookieError for 'auth', connectionError for 'connection', inconclusive, no raw text (design)_
    - _Preservation: non-tagged `success === false` (parse failures) still returns `searchFailed`_
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 2.6_

  - [ ] 3.4 Carry `errorType` across the re-throw in `checkLicense` catch
    - In the `checkLicense` `catch (error)` block that re-throws as `new Error('Request error: ...')`, attach the discriminator to the wrapped Error so the batch path can branch: `const wrapped = new Error(\`Request error: ${error.message}\`)`, `wrapped.errorType = error.response?.status === 401 ? 'auth' : 'connection'`, `throw wrapped`
    - This re-uses the same status→tag rule as 3.2. It is strictly additive — adds a property to the Error object without altering the thrown value's message or any returned `{ valid, details }` — so every non-error outcome stays byte-for-byte unchanged
    - _Bug_Condition: thrown connection/infrastructure error wrapping the whole orchestration_
    - _Expected_Behavior: re-thrown Error carries errorType ('auth' for 401, else 'connection') (design)_
    - _Preservation: thrown value's identity/message and all non-error returns unchanged_
    - _Requirements: 2.7, 2.8_

  - [ ] 3.5 Branch on `error.errorType` (two-way) in `checkLicensesBatch` catch
    - In the `catch` block, replace `details: \`Error: ${error.message}\`` with a branch on the re-thrown `error.errorType`:
      - `error.errorType === 'auth'` → `details = t('admin.licenseChecker.messages.cookieError')`
      - otherwise → `details = t('admin.licenseChecker.messages.connectionError', { license: member.license || '' })`
    - Push `{ ...member, valid: false, details }`; `valid` stays `false`. Any Error reaching here without an `errorType` (e.g. the up-front `Cookie string is required` throw) falls into the generic `connectionError` branch, no longer leaking the raw string as the primary message
    - _Bug_Condition: thrown error reaching the batch runner (auth or generic connection)_
    - _Expected_Behavior: cookieError for 'auth', else connectionError recorded as details (design)_
    - _Preservation: `valid` stays false; non-error batch outcomes unchanged_
    - _Requirements: 2.4, 2.7, 2.8_

  - [ ] 3.6 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Connection and Authentication Errors Are Clearly and Distinctly Indicated
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior; passing confirms it is satisfied
    - Run the bug condition exploration test from step 1 via `make test-frontend`
    - **EXPECTED OUTCOME**: Test PASSES (confirms the bug is fixed — the auth sub-case surfaces the translated `cookieError` message, the generic sub-case the translated `connectionError` message, the two are distinct, and neither leaks a raw technical string)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

  - [ ] 3.7 Verify preservation tests still pass
    - **Property 2: Preservation** - Non-Connection-Error Outcomes Are Unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run the preservation property tests from step 2 via `make test-frontend`, including the "No results table found" boundary case (`errorType` stays `undefined` on parse failures)
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions across valid/invalid/mismatch/not-found/no-input and parse-based failures)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [ ] 4. Checkpoint - Ensure all tests pass
  - Run `make test-frontend` and `make lint-frontend` and confirm all tests and lint pass
  - Ensure all tests pass, ask the user if questions arise
