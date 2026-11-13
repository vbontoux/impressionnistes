/**
 * Backup Naming Utility
 * Parse backup ids, map categories to badges, validate the restore phrase.
 *
 * The constants and the id format MUST stay identical to
 * functions/shared/backup_service.py.
 */

export const CONFIRMATION_PHRASE = 'RESTAURER LA BASE';
export const CATEGORY_MANUAL = 'manual';
export const CATEGORY_SAFETY = 'safety-pre-restore';
export const SOURCE_MARKER = '_before-restore-of_';

// Same pattern as the backend design (validated before any S3 access)
const BACKUP_ID_REGEX =
  /^(manual|safety-pre-restore)_(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)(_before-restore-of_(manual|safety-pre-restore)_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)?\.json$/;

/**
 * Parse a backup id.
 * A safety id must contain the source part, a manual id must not.
 *
 * The source reference embedded in a safety id is always bounded to
 * `{source_category}_{source_timestamp}`. It identifies the source but is NOT
 * the full source backup id (a safety source has a longer real id). The real
 * source id comes from the `source_backup_id` field of the list API, never
 * from the key.
 * @param {string} backupId - e.g. "manual_2026-11-01T14-30-00Z.json"
 * @returns {Object|null} - { category, timestamp, sourceRef, sourceStem } or null if invalid.
 *   sourceRef and sourceStem are both `{category}_{timestamp}` of the source
 *   (null for manual).
 */
export function parseBackupId(backupId) {
  if (typeof backupId !== 'string') {
    return null;
  }

  const match = BACKUP_ID_REGEX.exec(backupId);
  if (!match) {
    return null;
  }

  const category = match[1];
  const hasSource = match[3] !== undefined;

  if (category === CATEGORY_MANUAL && hasSource) {
    return null;
  }
  if (category === CATEGORY_SAFETY && !hasSource) {
    return null;
  }

  const sourceStem = hasSource ? match[3].slice(SOURCE_MARKER.length) : null;

  return {
    category,
    timestamp: match[2],
    sourceRef: sourceStem,
    sourceStem,
  };
}

/**
 * Get the StatusBadge status and i18n label key for a backup category.
 * The label key is `admin.database.category.<category id>`
 * (i.e. ...category.manual or ...category.safety-pre-restore).
 * @param {string} category - CATEGORY_MANUAL or CATEGORY_SAFETY
 * @returns {Object|null} - { status, labelKey } or null for unknown category
 */
export function categoryBadge(category) {
  if (category === CATEGORY_MANUAL) {
    return { status: 'paid', labelKey: `admin.database.category.${category}` };
  }
  if (category === CATEGORY_SAFETY) {
    return { status: 'incomplete', labelKey: `admin.database.category.${category}` };
  }
  return null;
}

/**
 * Check the restore confirmation phrase (exact, case-sensitive, no trimming)
 * @param {string} phrase - Typed phrase
 * @returns {boolean}
 */
export function isPhraseValid(phrase) {
  return phrase === CONFIRMATION_PHRASE;
}
