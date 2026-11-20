/**
 * Reset Rules Utility
 * Purge set ids, dependency rules, selection closure and confirmation phrase
 * for the database reset (selective purge).
 *
 * The values (set ids, dependencies, confirmation phrase) MUST stay identical
 * to functions/shared/reset_service.py (PURGE_SETS, DEPENDENCIES,
 * CONFIRMATION_PHRASE).
 */

/** Purge set ids in UI order. */
export const PURGE_SET_IDS = Object.freeze([
  'boats',
  'payments',
  'crew',
  'managers',
  'temp_access',
  'audit_logs',
]);

/**
 * Dependency rules: purging a key set also requires purging its values.
 * Already transitive, so the closure is a single union.
 */
export const DEPENDENCIES = Object.freeze({
  boats: Object.freeze(['payments']),
  crew: Object.freeze(['boats', 'payments']),
  managers: Object.freeze(['boats', 'payments', 'crew', 'temp_access']),
});

/** Selection applied when the section loads. */
export const DEFAULT_SELECTION = Object.freeze(['boats']);

/** Phrase the Admin must type to enable the purge. */
export const CONFIRMATION_PHRASE = 'PURGER LA BASE';

/**
 * Compute the closure of a selection: the ids plus all their dependencies.
 * Unknown ids are ignored. The result is deduplicated and in PURGE_SET_IDS order.
 * @param {string[]} ids - Chosen purge set ids
 * @returns {string[]} - Closed selection
 */
export function closure(ids) {
  const result = new Set();
  for (const id of Array.isArray(ids) ? ids : []) {
    if (!PURGE_SET_IDS.includes(id)) {
      continue;
    }
    result.add(id);
    for (const dep of DEPENDENCIES[id] || []) {
      result.add(dep);
    }
  }
  return PURGE_SET_IDS.filter((id) => result.has(id));
}

/**
 * Get the selected sets that imply a given set.
 * @param {string} id - Purge set id
 * @param {string[]} selection - Selected purge set ids
 * @returns {string[]} - Ids in the selection whose dependencies include id (PURGE_SET_IDS order)
 */
export function requiredBy(id, selection) {
  const selected = Array.isArray(selection) ? selection : [];
  return PURGE_SET_IDS.filter(
    (candidate) => selected.includes(candidate) && (DEPENDENCIES[candidate] || []).includes(id)
  );
}

/**
 * Check the purge confirmation phrase (exact, case-sensitive, no trimming)
 * @param {string} text - Typed phrase
 * @returns {boolean}
 */
export function isPhraseValid(text) {
  return text === CONFIRMATION_PHRASE;
}
