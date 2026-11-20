/**
 * Reset Rules Tests
 * Feature: database-reset
 *
 * Table-driven tests (explicit inputs) for the dependency closure, the
 * "required by" lookup and the confirmation phrase.
 * Validates: Requirements 3.1, 3.2, 4.1, 4.2, 4.3, 4.5, 4.6, 9.1
 */
import { describe, test, expect } from 'vitest';
import {
  PURGE_SET_IDS,
  DEPENDENCIES,
  DEFAULT_SELECTION,
  CONFIRMATION_PHRASE,
  closure,
  requiredBy,
  isPhraseValid,
} from './resetRules';

describe('constants', () => {
  test('match the backend values', () => {
    expect(PURGE_SET_IDS).toEqual(['boats', 'payments', 'crew', 'managers', 'temp_access', 'audit_logs']);
    expect(CONFIRMATION_PHRASE).toBe('PURGER LA BASE');
    expect(DEPENDENCIES).toEqual({
      boats: ['payments'],
      crew: ['boats', 'payments'],
      managers: ['boats', 'payments', 'crew', 'temp_access'],
    });
  });

  test('default selection is boats only', () => {
    expect(DEFAULT_SELECTION).toEqual(['boats']);
    expect(closure(DEFAULT_SELECTION)).toEqual(['boats', 'payments']);
  });
});

describe('closure - explicit cases', () => {
  const cases = [
    { name: 'empty', input: [], expected: [] },
    { name: 'boats', input: ['boats'], expected: ['boats', 'payments'] },
    { name: 'payments', input: ['payments'], expected: ['payments'] },
    { name: 'crew', input: ['crew'], expected: ['boats', 'payments', 'crew'] },
    {
      name: 'managers',
      input: ['managers'],
      expected: ['boats', 'payments', 'crew', 'managers', 'temp_access'],
    },
    { name: 'temp_access', input: ['temp_access'], expected: ['temp_access'] },
    { name: 'audit_logs', input: ['audit_logs'], expected: ['audit_logs'] },
    { name: 'unknown ids ignored', input: ['nope', 'boats'], expected: ['boats', 'payments'] },
    { name: 'duplicates removed', input: ['boats', 'boats'], expected: ['boats', 'payments'] },
    { name: 'non-array input', input: null, expected: [] },
  ];

  test.each(cases)('$name', ({ input, expected }) => {
    expect(closure(input)).toEqual(expected);
  });
});

describe('closure - all 64 subsets', () => {
  const subsets = [];
  for (let mask = 0; mask < 1 << PURGE_SET_IDS.length; mask++) {
    subsets.push(PURGE_SET_IDS.filter((_, i) => mask & (1 << i)));
  }

  // Independent expected computation written from the rules, not from closure()
  function expectedClosure(subset) {
    const out = new Set(subset);
    if (out.has('managers')) {
      ['boats', 'payments', 'crew', 'temp_access'].forEach((x) => out.add(x));
    }
    if (out.has('crew')) {
      ['boats', 'payments'].forEach((x) => out.add(x));
    }
    if (out.has('boats')) {
      out.add('payments');
    }
    return PURGE_SET_IDS.filter((id) => out.has(id));
  }

  test('there are 64 subsets', () => {
    expect(subsets).toHaveLength(64);
  });

  test.each(subsets.map((s) => [s.join(',') || '(empty)', s]))('closure of %s', (_label, subset) => {
    const result = closure(subset);
    expect(result).toEqual(expectedClosure(subset));
    subset.forEach((id) => expect(result).toContain(id));
    expect(closure(result)).toEqual(result);
  });
});

describe('requiredBy', () => {
  const cases = [
    { name: 'payments by boats', id: 'payments', selection: ['boats'], expected: ['boats'] },
    { name: 'payments by boats and crew', id: 'payments', selection: ['crew', 'boats'], expected: ['boats', 'crew'] },
    { name: 'boats by crew', id: 'boats', selection: ['crew'], expected: ['crew'] },
    { name: 'crew by managers', id: 'crew', selection: ['managers'], expected: ['managers'] },
    { name: 'temp_access by managers', id: 'temp_access', selection: ['managers', 'boats'], expected: ['managers'] },
    { name: 'audit_logs never required', id: 'audit_logs', selection: PURGE_SET_IDS, expected: [] },
    { name: 'nothing selected', id: 'payments', selection: [], expected: [] },
    { name: 'non-array selection', id: 'payments', selection: undefined, expected: [] },
    { name: 'unselected sets ignored', id: 'payments', selection: ['audit_logs'], expected: [] },
  ];

  test.each(cases)('$name', ({ id, selection, expected }) => {
    expect(requiredBy(id, selection)).toEqual(expected);
  });
});

describe('isPhraseValid', () => {
  const cases = [
    { name: 'exact phrase', text: 'PURGER LA BASE', expected: true },
    { name: 'lowercase', text: 'purger la base', expected: false },
    { name: 'mixed case', text: 'Purger la base', expected: false },
    { name: 'trailing space', text: 'PURGER LA BASE ', expected: false },
    { name: 'leading space', text: ' PURGER LA BASE', expected: false },
    { name: 'empty', text: '', expected: false },
    { name: 'partial', text: 'PURGER LA', expected: false },
    { name: 'restore phrase', text: 'RESTAURER LA BASE', expected: false },
    { name: 'undefined', text: undefined, expected: false },
    { name: 'null', text: null, expected: false },
  ];

  test.each(cases)('$name', ({ text, expected }) => {
    expect(isPhraseValid(text)).toBe(expected);
  });
});
