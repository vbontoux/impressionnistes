# Bugfix Requirements Document

## Introduction

When an administrator verifies FFAviron rowing licenses, the frontend license checker
(`frontend/src/utils/licenseChecker.js`) talks to the FFAviron intranet through the
`/admin/html-proxy` endpoint. If that call fails for any infrastructure reason — a network
outage, a proxy error, or an API failure — the error is thrown inside `searchByQuery(...)`
and swallowed into a generic `{ success: false }` result. Downstream, the Strategy 2
(search-by-license-number) branch in `checkLicense(...)` maps **every** `success === false`
outcome onto the same message, `searchFailed`, producing text like:

> "Échec de la recherche du numéro de licence 067741. No results table found"

As a result, a genuine connection/infrastructure failure is presented to the user in the
same way as a benign "the page loaded but had no results table" situation, with an
untranslated technical English string appended. The user cannot tell whether the license is
actually problematic or whether the verification simply could not be completed. The same
confusion appears in `checkLicensesBatch(...)`, where thrown errors are pushed as a raw,
untranslated `details: "Error: ..."` string.

The impact: a connection error is misreported as a license lookup failure, which can lead an
administrator to wrongly conclude a license is invalid or missing when in fact the check was
inconclusive. This fix makes connection/infrastructure errors clearly and distinctly
indicated as such, separate from a definitive "not found / no matching results" outcome.

In addition, the failure class is not uniform. The `/admin/html-proxy` backend
(`functions/admin/html_proxy.py`) already distinguishes several failure modes: a 401/403
from FFAviron is mapped to HTTP **401** with the message "Authentication failed. Cookies may
have expired."; a connection failure is mapped to HTTP **502** ("Failed to connect to
target: ..."); and a timeout is mapped to HTTP **504** ("Request timed out"). The 401 case
specifically indicates a **bad or expired FFAviron session cookie** — an authentication
problem the administrator can fix by re-authenticating and refreshing the cookie. Today this
authentication failure is collapsed into the same generic failure message as a true
connection outage, so the administrator gets no actionable hint that the cookie, rather than
the network, is the problem. This fix additionally separates the identifiable
authentication/bad-cookie case (proxy responded 401) from the generic connection error
whenever that distinction is available on the frontend.

## Bug Analysis

### Current Behavior (Defect)

When a connection, network, proxy, or API failure occurs during license verification, the
system surfaces a misleading message that conflates the failure with a license-not-found
outcome and leaks raw technical English text.

1.1 WHEN the `/admin/html-proxy` request thrown an error (network failure, proxy error, or API failure) during the search-by-license-number step THEN the system reports it using the `searchFailed` message, identical to a benign no-results-table parsing outcome
1.2 WHEN a connection/infrastructure error occurs THEN the system appends the raw, untranslated technical error string (for example "No results table found" or "Network Error") to the user-facing message
1.3 WHEN a connection/infrastructure error occurs THEN the system presents the result as a definitive lookup failure, giving no indication that the verification was inconclusive rather than that the license is invalid or absent
1.4 WHEN a thrown error reaches `checkLicensesBatch(...)` THEN the system records an untranslated `details` value of the form "Error: {message}" instead of a clearly identified connection error
1.5 WHEN the `/admin/html-proxy` request fails specifically because of a bad or expired FFAviron session cookie (the proxy responded with HTTP 401, "Authentication failed. Cookies may have expired.") THEN the system reports it with the same generic failure message as a true connection outage, giving no indication that re-authenticating or refreshing the cookie is required
1.6 WHEN the failure is an identifiable authentication/bad-cookie error (proxy HTTP 401) THEN the system makes no distinction between it and a generic connection error, so both the search-by-license-number step and `checkLicensesBatch(...)` collapse the two sub-cases into one indistinguishable outcome

### Expected Behavior (Correct)

The system distinguishes an inability to reach/verify the FFAviron service (a connection
error) from a definitive license outcome, and communicates it clearly in the user's language.

2.1 WHEN the `/admin/html-proxy` request fails with a connection error that is NOT identifiable as an authentication error (for example the proxy responded 502 or 504, or there was a network failure with no response) during the search-by-license-number step THEN the system SHALL display a dedicated, translated connection-error message that clearly identifies the problem as a connection/verification failure
2.2 WHEN a connection/infrastructure error occurs THEN the system SHALL NOT expose a raw, untranslated technical error string as the primary user-facing message (any technical detail MAY be included only as clearly labeled supplementary context)
2.3 WHEN a connection/infrastructure error occurs THEN the system SHALL make clear that the verification was inconclusive, so the result is not interpreted as a definitive "invalid" or "not found" license outcome
2.4 WHEN a thrown error reaches `checkLicensesBatch(...)` THEN the system SHALL record the dedicated, translated connection-error message as the `details` value rather than an untranslated "Error: {message}" string
2.5 WHEN the failure is identifiable as an authentication/bad-cookie error (the proxy responded with HTTP 401) during the search-by-license-number step THEN the system SHALL display a dedicated, translated authentication-error message indicating the FFAviron session cookie is invalid or expired and that re-authenticating or refreshing the cookie is needed, distinct from the generic connection-error message
2.6 WHEN the failure is an identifiable authentication/bad-cookie error (proxy HTTP 401) THEN the system SHALL present it as an inconclusive outcome (not a definitive "invalid" or "not found" license outcome) and SHALL NOT expose a raw, untranslated technical error string as the primary user-facing message
2.7 WHEN a thrown error reaches `checkLicensesBatch(...)` that is identifiable as an authentication/bad-cookie error (proxy HTTP 401) THEN the system SHALL record the dedicated, translated authentication-error message as the `details` value, distinct from the generic connection-error message
2.8 WHEN the failure is a connection error that is not identifiable as an authentication error THEN the system SHALL display the generic connection-error message (as specified in 2.1), applying the same authentication-versus-connection distinction in both the search-by-license-number step and `checkLicensesBatch(...)`

### Unchanged Behavior (Regression Prevention)

All non-error verification outcomes must behave exactly as before.

3.1 WHEN a license is found, active, and of competition type THEN the system SHALL CONTINUE TO report it as valid using the existing `validLicense` message
3.2 WHEN the search by license number returns results but no row matches the license number THEN the system SHALL CONTINUE TO report `notFoundInResults` (this is a definitive not-found outcome, not a connection error)
3.3 WHEN the search by license number returns no results at all THEN the system SHALL CONTINUE TO report `notFoundByLicense`
3.4 WHEN a license is found but the name does not match THEN the system SHALL CONTINUE TO report `nameMismatch`
3.5 WHEN a license is found but is not active and/or not competition type THEN the system SHALL CONTINUE TO report `invalidLicense` with the existing reasons
3.6 WHEN neither name nor license number is provided THEN the system SHALL CONTINUE TO report `noNameOrLicense`
3.7 WHEN verification completes successfully (no thrown connection/infrastructure error) THEN the system SHALL CONTINUE TO produce the same validity result and `details` text it produces today

## Bug Condition Derivation

### Bug Condition Function

Identifies the inputs/outcomes that trigger the misleading message. `X` represents the
outcome of a `searchByQuery(...)` call (or a thrown error caught by the batch runner).

```pascal
FUNCTION isBugCondition(X)
  INPUT: X of type SearchOutcome
  OUTPUT: boolean

  // True when the search could not be completed because the request itself failed
  // (the error originated from the thrown-error catch path: network / proxy / API failure),
  // as opposed to the HTML being successfully retrieved but yielding no matching results.
  RETURN X.success = false AND X.cause = CONNECTION_OR_INFRASTRUCTURE_ERROR
END FUNCTION
```

The connection/infrastructure error class is not uniform. The proxy exposes a signal that
splits it into two sub-cases that must be reported distinctly:

```pascal
FUNCTION errorClass(X)
  INPUT: X of type SearchOutcome WHERE isBugCondition(X)
  OUTPUT: {AUTHENTICATION_ERROR, GENERIC_CONNECTION_ERROR}

  // The proxy maps a 401/403 from FFAviron to HTTP 401 (bad/expired session cookie),
  // a connection failure to HTTP 502, and a timeout to HTTP 504. On the frontend the
  // rejected request's error.response.status === 401 identifies the authentication case.
  IF X.response IS PRESENT AND X.response.status = 401 THEN
    RETURN AUTHENTICATION_ERROR          // bad or expired FFAviron session cookie
  ELSE
    RETURN GENERIC_CONNECTION_ERROR      // 502 / 504 / network failure with no response
  END IF
END FUNCTION
```

### Property Specification (Fix Checking)

```pascal
// Property: Fix Checking - connection errors are clearly and distinctly indicated
FOR ALL X WHERE isBugCondition(X) DO
  result ← checkLicense'(X)   // F' = fixed function

  IF errorClass(X) = AUTHENTICATION_ERROR THEN
    ASSERT result.details = translatedAuthenticationErrorMessage  // dedicated, localized, bad/expired cookie
  ELSE
    ASSERT result.details = translatedConnectionErrorMessage      // dedicated, localized, generic connection
  END IF

  ASSERT translatedAuthenticationErrorMessage <> translatedConnectionErrorMessage  // distinct
     AND NOT result.details.contains(rawUntranslatedTechnicalString)
     AND result.conveysInconclusive = true                        // not a definitive "not found"
END FOR
```

### Preservation Specification (Preservation Checking)

```pascal
// Property: Preservation Checking - all non-connection-error outcomes are unchanged
FOR ALL X WHERE NOT isBugCondition(X) DO
  ASSERT checkLicense(X) = checkLicense'(X)   // F(X) == F'(X)
END FOR
```

**Key definitions:**
- **F** — the current `checkLicense` / `checkLicensesBatch` behavior before the fix.
- **F'** — the behavior after the fix.
- **C(X)** — `isBugCondition(X)`: the search failed due to a connection/infrastructure error (thrown-error path), not because results were retrieved but did not match. This splits into two sub-cases via `errorClass(X)`: `AUTHENTICATION_ERROR` (proxy HTTP 401, bad/expired cookie) and `GENERIC_CONNECTION_ERROR` (502 / 504 / network failure with no response), which must be reported with distinct, translated messages.
- **¬C(X)** — every other outcome: valid, invalid, name mismatch, not-found-by-license, not-found-in-results, no-name-or-license, and successful lookups.
