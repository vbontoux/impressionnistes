/**
 * Backup Naming Tests
 * Feature: database-backup-restore
 *
 * Table-driven tests (explicit inputs) for backup id parsing, category badges
 * and restore phrase validation.
 * Validates: Requirements 4.5, 8.2, 8.4, 8.8
 */
import { describe, test, expect } from 'vitest';
import {
  CONFIRMATION_PHRASE,
  CATEGORY_MANUAL,
  CATEGORY_SAFETY,
  CATEGORY_RESET,
  SOURCE_MARKER,
  parseBackupId,
  categoryBadge,
  isPhraseValid,
} from './backupNaming';

const MANUAL_STEM = 'manual_2026-11-01T14-30-00Z';
const SAFETY_STEM = `safety-pre-restore_2026-11-02T09-15-45Z${SOURCE_MARKER}${MANUAL_STEM}`;

describe('constants', () => {
  test('match the backend values', () => {
    expect(CONFIRMATION_PHRASE).toBe('RESTAURER LA BASE');
    expect(CATEGORY_MANUAL).toBe('manual');
    expect(CATEGORY_SAFETY).toBe('safety-pre-restore');
    expect(CATEGORY_RESET).toBe('safety-pre-reset');
    expect(SOURCE_MARKER).toBe('_before-restore-of_');
  });
});

describe('parseBackupId - valid ids', () => {
  const cases = [
    {
      name: 'manual id',
      id: `${MANUAL_STEM}.json`,
      expected: {
        category: 'manual',
        timestamp: '2026-11-01T14-30-00Z',
        sourceRef: null,
        sourceStem: null,
      },
    },
    {
      name: 'safety id with manual source',
      id: `${SAFETY_STEM}.json`,
      expected: {
        category: 'safety-pre-restore',
        timestamp: '2026-11-02T09-15-45Z',
        sourceRef: MANUAL_STEM,
        sourceStem: MANUAL_STEM,
      },
    },
    {
      name: 'safety whose source is another safety backup',
      id: 'safety-pre-restore_2026-11-03T10-00-00Z_before-restore-of_safety-pre-restore_2026-11-02T09-15-45Z.json',
      expected: {
        category: 'safety-pre-restore',
        timestamp: '2026-11-03T10-00-00Z',
        sourceRef: 'safety-pre-restore_2026-11-02T09-15-45Z',
        sourceStem: 'safety-pre-restore_2026-11-02T09-15-45Z',
      },
    },
    {
      name: 'safety-pre-reset id without source',
      id: 'safety-pre-reset_2026-11-04T08-00-00Z.json',
      expected: {
        category: 'safety-pre-reset',
        timestamp: '2026-11-04T08-00-00Z',
        sourceRef: null,
        sourceStem: null,
      },
    },
    {
      name: 'safety-pre-restore whose source is a safety-pre-reset backup',
      id: 'safety-pre-restore_2026-11-05T10-00-00Z_before-restore-of_safety-pre-reset_2026-11-04T08-00-00Z.json',
      expected: {
        category: 'safety-pre-restore',
        timestamp: '2026-11-05T10-00-00Z',
        sourceRef: 'safety-pre-reset_2026-11-04T08-00-00Z',
        sourceStem: 'safety-pre-reset_2026-11-04T08-00-00Z',
      },
    },
  ];

  test.each(cases)('$name', ({ id, expected }) => {
    expect(parseBackupId(id)).toEqual(expected);
  });
});

describe('parseBackupId - invalid ids', () => {
  const cases = [
    { name: 'path traversal', id: '../x.json' },
    { name: 'traversal prefixed to a valid id', id: `../${MANUAL_STEM}.json` },
    { name: 'slash only', id: '/' },
    { name: 'nested path', id: `dir/${MANUAL_STEM}.json` },
    { name: 'wrong category', id: 'auto_2026-11-01T14-30-00Z.json' },
    { name: 'safety without source', id: 'safety-pre-restore_2026-11-02T09-15-45Z.json' },
    {
      name: 'manual with source',
      id: `manual_2026-11-02T09-15-45Z${SOURCE_MARKER}${MANUAL_STEM}.json`,
    },
    {
      name: 'safety whose source itself has a source (nested marker)',
      id: `safety-pre-restore_2026-11-03T10-00-00Z${SOURCE_MARKER}${SAFETY_STEM}.json`,
    },
    {
      name: 'nested chain safety -> safety -> manual',
      id: 'safety-pre-restore_2026-11-03T10-00-00Z_before-restore-of_safety-pre-restore_2026-11-02T09-15-45Z_before-restore-of_manual_2026-11-01T14-30-00Z.json',
    },
    {
      name: 'safety-pre-reset with source',
      id: `safety-pre-reset_2026-11-04T08-00-00Z_before-restore-of_${MANUAL_STEM}.json`,
    },
    {
      name: 'safety-pre-reset with source (reset-sourced)',
      id: 'safety-pre-reset_2026-11-05T08-00-00Z_before-restore-of_safety-pre-reset_2026-11-04T08-00-00Z.json',
    },
    { name: 'safety-pre-reset bad timestamp', id: 'safety-pre-reset_2026-11-04.json' },
    { name: 'safety-pre-reset wrong extension', id: 'safety-pre-reset_2026-11-04T08-00-00Z.txt' },
    { name: 'missing .json extension', id: MANUAL_STEM },
    { name: 'wrong extension', id: `${MANUAL_STEM}.txt` },
    { name: 'bad timestamp (colons)', id: 'manual_2026-11-01T14:30:00Z.json' },
    { name: 'bad timestamp (truncated)', id: 'manual_2026-11-01.json' },
    { name: 'empty string', id: '' },
    { name: 'null', id: null },
    { name: 'undefined', id: undefined },
    { name: 'number', id: 42 },
    { name: 'object', id: {} },
  ];

  test.each(cases)('$name returns null', ({ id }) => {
    expect(parseBackupId(id)).toBeNull();
  });
});

describe('categoryBadge', () => {
  const cases = [
    {
      name: 'manual',
      category: CATEGORY_MANUAL,
      expected: { status: 'paid', labelKey: 'admin.database.category.manual' },
    },
    {
      name: 'safety-pre-restore',
      category: CATEGORY_SAFETY,
      expected: { status: 'incomplete', labelKey: 'admin.database.category.safety-pre-restore' },
    },
    {
      name: 'safety-pre-reset',
      category: CATEGORY_RESET,
      expected: { status: 'forfait', labelKey: 'admin.database.category.safety-pre-reset' },
    },
    { name: 'unknown category', category: 'auto', expected: null },
    { name: 'empty string', category: '', expected: null },
    { name: 'undefined', category: undefined, expected: null },
  ];

  test.each(cases)('$name', ({ category, expected }) => {
    expect(categoryBadge(category)).toEqual(expected);
  });
});

describe('isPhraseValid', () => {
  const cases = [
    { name: 'exact phrase', phrase: 'RESTAURER LA BASE', expected: true },
    { name: 'lowercase', phrase: 'restaurer la base', expected: false },
    { name: 'mixed case', phrase: 'Restaurer La Base', expected: false },
    { name: 'trailing space', phrase: 'RESTAURER LA BASE ', expected: false },
    { name: 'leading space', phrase: ' RESTAURER LA BASE', expected: false },
    { name: 'empty string', phrase: '', expected: false },
    { name: 'undefined', phrase: undefined, expected: false },
    { name: 'null', phrase: null, expected: false },
    { name: 'partial phrase', phrase: 'RESTAURER', expected: false },
    { name: 'partial phrase (prefix)', phrase: 'RESTAURER LA BAS', expected: false },
    { name: 'phrase with extra word', phrase: 'RESTAURER LA BASE X', expected: false },
  ];

  test.each(cases)('$name -> $expected', ({ phrase, expected }) => {
    expect(isPhraseValid(phrase)).toBe(expected);
  });
});
