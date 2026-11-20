"""
Database reset (selective purge) tests for functions/shared/reset_service.py.

Sections:
  1. Classification, closure, counts (task 2.3)
  2. Backend/frontend rules alignment

No Hypothesis: explicit parametrized cases only.
"""
import itertools
import json
import os
import re

import pytest

import backup_service
import reset_service
from reset_service import (
    CONFIRMATION_PHRASE, DEPENDENCIES, PURGE_ORDER, PURGE_SETS,
    classify, compute_item_counts, resolve_closure,
)
from tests.integration.backup_helpers import clear_table, put_typed_items

SET_IDS = ['boats', 'payments', 'crew', 'managers', 'temp_access', 'audit_logs']
AUDIT_PARTITIONS = [
    'AUDIT#PERMISSION_BYPASS', 'AUDIT#PERMISSION_DENIAL', 'AUDIT#PERMISSION_CONFIG',
    'AUDIT#TEMP_ACCESS_GRANT', 'AUDIT#TEMP_ACCESS_REVOKE',
]


# ---------------------------------------------------------------------------
# 1. Classification
# ---------------------------------------------------------------------------
@pytest.mark.parametrize('pk, sk, expected', [
    # boats / payments / crew: any TEAM# owner
    ('TEAM#abc', 'BOAT#b1', 'boats'),
    ('TEAM#xyz', 'BOAT#b2', 'boats'),
    ('TEAM#abc', 'PAYMENT#p1', 'payments'),
    ('TEAM#abc', 'CREW#c1', 'crew'),
    ('TEAM#xyz', 'CREW#c9', 'crew'),
    # managers
    ('USER#sub1', 'PROFILE', 'managers'),
    ('USER#sub1', 'CONSENT#2026-01-01', 'managers'),
    # temp access
    ('TEMP_ACCESS', 'USER#sub1', 'temp_access'),
    # audit logs (any SK)
    ('AUDIT#PERMISSION_BYPASS', '2026-01-01T00:00:00#1', 'audit_logs'),
    ('AUDIT#PERMISSION_DENIAL', 'x', 'audit_logs'),
    ('AUDIT#PERMISSION_CONFIG', 'x', 'audit_logs'),
    ('AUDIT#TEMP_ACCESS_GRANT', 'x', 'audit_logs'),
    ('AUDIT#TEMP_ACCESS_REVOKE', 'x', 'audit_logs'),
    # decoys: CREW_MEMBER# is not CREW#
    ('TEAM#abc', 'CREW_MEMBER#m1', None),
    ('CREW#c1', 'METADATA', None),
    # protected data
    ('CONFIG', 'SYSTEM', None),
    ('CONFIG', 'PERMISSION_MATRIX', None),
    ('RACE', 'R1', None),
    ('RACE', 'BOAT#b1', None),
    ('CLUB', 'C1', None),
    ('AUDIT#DATABASE_BACKUP', '2026-01-01T00:00:00#1', None),
    # no rule matches: kept
    ('TEAM#abc', 'METADATA', None),
    ('USER#sub1', 'OTHER', None),
    ('TEMP_ACCESS', 'OTHER', None),
    ('TEAM', 'BOAT#b1', None),
    ('USER', 'PROFILE', None),
    ('AUDIT#UNKNOWN', 'x', None),
    ('', '', None),
])
def test_classify_keys(pk, sk, expected):
    assert classify(pk, sk) == expected


@pytest.mark.parametrize('pk, sk', [
    ('CONFIG', 'x'), ('RACE', 'x'), ('CLUB', 'x'), ('AUDIT#DATABASE_BACKUP', 'x'),
])
def test_protected_data_never_classified(pk, sk):
    assert classify(pk, sk) is None


def test_purge_sets_definition():
    assert list(PURGE_SETS) == ['boats', 'payments', 'crew', 'managers', 'temp_access',
                                'audit_logs']
    assert sorted(PURGE_ORDER) == sorted(SET_IDS)
    audit_pks = sorted(pk for pk, sk in PURGE_SETS['audit_logs']['rules'])
    assert audit_pks == sorted(AUDIT_PARTITIONS)
    assert all(sk == '*' for _, sk in PURGE_SETS['audit_logs']['rules'])


def test_rules_are_disjoint():
    """A key matches at most one set: sample keys of every set match only their own"""
    samples = {
        'boats': [('TEAM#a', 'BOAT#1')],
        'payments': [('TEAM#a', 'PAYMENT#1')],
        'crew': [('TEAM#a', 'CREW#1')],
        'managers': [('USER#s', 'PROFILE'), ('USER#s', 'CONSENT#1')],
        'temp_access': [('TEMP_ACCESS', 'USER#s')],
        'audit_logs': [(pk, 'sk') for pk in AUDIT_PARTITIONS],
    }
    for owner, keys in samples.items():
        for pk, sk in keys:
            matching = [
                set_id for set_id, definition in PURGE_SETS.items()
                if any(_rule_matches(p, pk) and _rule_matches(s, sk)
                       for p, s in definition['rules'])
            ]
            assert matching == [owner], (pk, sk, matching)


def _rule_matches(pattern, value):
    return value.startswith(pattern[:-1]) if pattern.endswith('*') else value == pattern


# ---------------------------------------------------------------------------
# 1. Closure: all 64 subsets against an independent expectation
# ---------------------------------------------------------------------------
# Written by hand from the requirements (not derived from DEPENDENCIES)
_IMPLIED = {
    'boats': {'payments'},
    'crew': {'boats', 'payments'},
    'managers': {'boats', 'payments', 'crew', 'temp_access'},
}


def _expected_closure(subset):
    expected = set(subset)
    for set_id in subset:
        expected |= _IMPLIED.get(set_id, set())
    return expected


_ALL_SUBSETS = [
    frozenset(combo)
    for size in range(len(SET_IDS) + 1)
    for combo in itertools.combinations(SET_IDS, size)
]


def test_all_subsets_enumerated():
    assert len(_ALL_SUBSETS) == 64


def test_dependencies_value():
    assert DEPENDENCIES == _IMPLIED


@pytest.mark.parametrize('subset', _ALL_SUBSETS, ids=lambda s: '+'.join(sorted(s)) or 'empty')
def test_closure_all_subsets(subset):
    closed = resolve_closure(subset)
    assert closed == _expected_closure(subset)
    assert subset <= closed
    assert resolve_closure(closed) == closed  # idempotent


def test_closure_ignores_input_order_and_accepts_lists():
    assert resolve_closure(['crew']) == {'crew', 'boats', 'payments'}
    assert resolve_closure(['payments', 'managers']) == resolve_closure(['managers', 'payments'])
    assert resolve_closure([]) == set()


# ---------------------------------------------------------------------------
# 1. Counts
# ---------------------------------------------------------------------------
def _s(value):
    return {'S': value}


def _seed_items():
    """(typed items, expected counts, expected cognito_accounts_max)"""
    keys = []
    keys += [('TEAM#t1', 'BOAT#b1'), ('TEAM#t1', 'BOAT#b2'), ('TEAM#t2', 'BOAT#b3')]
    keys += [('TEAM#t1', 'PAYMENT#p1'), ('TEAM#t2', 'PAYMENT#p2')]
    keys += [('TEAM#t1', f'CREW#c{i}') for i in range(4)] + [('TEAM#t2', 'CREW#c9')]
    keys += [('USER#u1', 'PROFILE'), ('USER#u2', 'PROFILE'), ('USER#u3', 'PROFILE')]
    keys += [('USER#u1', 'CONSENT#a'), ('USER#u1', 'CONSENT#b')]
    keys += [('TEMP_ACCESS', 'USER#u1'), ('TEMP_ACCESS', 'USER#u2')]
    keys += [(pk, f'{i}') for i, pk in enumerate(AUDIT_PARTITIONS)]
    keys += [('AUDIT#PERMISSION_DENIAL', 'extra')]
    # decoys and protected data
    keys += [('TEAM#t1', 'CREW_MEMBER#m1'), ('TEAM#t1', 'CREW_MEMBER#m2'),
             ('TEAM#t1', 'METADATA'), ('USER#u1', 'OTHER'),
             ('CONFIG', 'SYSTEM'), ('RACE', 'R1'), ('RACE', 'R2'), ('CLUB', 'C1'),
             ('AUDIT#DATABASE_BACKUP', 'b1'), ('AUDIT#DATABASE_BACKUP', 'b2')]
    items = [{'PK': _s(pk), 'SK': _s(sk)} for pk, sk in keys]
    expected = {
        'boats': 3, 'payments': 2, 'crew': 5, 'managers': 5,
        'temp_access': 2, 'audit_logs': 6,
    }
    return items, expected, 3


@pytest.fixture
def reset_table(dynamodb_table):
    clear_table(dynamodb_table)
    items, expected, cognito_max = _seed_items()
    put_typed_items(items)
    return expected, cognito_max


def test_counts_match_seed(reset_table):
    expected, cognito_max = reset_table
    counts, cognito_accounts_max = compute_item_counts()
    assert counts == expected
    assert set(counts) == set(SET_IDS)
    assert cognito_accounts_max == cognito_max


def test_counts_exclude_backup_audit_records(reset_table):
    counts, _ = compute_item_counts()
    # two AUDIT#DATABASE_BACKUP items are seeded; audit_logs counts only the five partitions
    assert counts['audit_logs'] == 6


def test_counts_empty_table(dynamodb_table):
    clear_table(dynamodb_table)
    counts, cognito_accounts_max = compute_item_counts()
    assert counts == {set_id: 0 for set_id in SET_IDS}
    assert cognito_accounts_max == 0


def test_counts_ignore_seeded_config_items(dynamodb_table):
    """Items seeded by dynamodb_table (config, ...) are protected or unclassified"""
    counts, cognito_accounts_max = compute_item_counts()
    assert counts['audit_logs'] == 0 and counts['boats'] == 0
    assert cognito_accounts_max == 0


def test_cognito_accounts_max_counts_profiles_only(dynamodb_table):
    clear_table(dynamodb_table)
    put_typed_items([
        {'PK': _s('USER#a'), 'SK': _s('CONSENT#1')},
        {'PK': _s('USER#a'), 'SK': _s('CONSENT#2')},
    ])
    counts, cognito_accounts_max = compute_item_counts()
    assert counts['managers'] == 2
    assert cognito_accounts_max == 0


# ---------------------------------------------------------------------------
# 2. Backend / frontend alignment (frontend file read as text)
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
_RESET_RULES_JS = os.path.join(_REPO_ROOT, 'frontend', 'src', 'utils', 'resetRules.js')


def _js_source():
    with open(_RESET_RULES_JS, encoding='utf-8') as handle:
        return handle.read()


def _js_string_list(body):
    return re.findall(r"'([^']*)'", body)


_LOCALES_DIR = os.path.join(_REPO_ROOT, 'frontend', 'src', 'locales')


def _locale_database_section(lang):
    with open(os.path.join(_LOCALES_DIR, f'{lang}.json'), encoding='utf-8') as handle:
        return json.load(handle)['admin']['database']


def _backend_error_codes():
    """Codes of every error class defined in reset_service, plus generic envelope codes"""
    codes = {'INTERNAL_ERROR', 'FORBIDDEN', 'UNAUTHORIZED'}
    for value in vars(reset_service).values():
        if (isinstance(value, type) and issubclass(value, backup_service.BackupError)
                and getattr(value, 'code', None)):
            codes.add(value.code)
    return codes


def test_frontend_backend_reset_rules_aligned():
    """resetRules.js (read as text) matches reset_service; i18n has every set and error code"""
    source = _js_source()

    # Set ids and order
    match = re.search(r"export const PURGE_SET_IDS = Object\.freeze\(\[(.*?)\]\)", source, re.S)
    assert match, 'PURGE_SET_IDS not found in resetRules.js'
    frontend_ids = _js_string_list(match.group(1))
    assert frontend_ids == list(PURGE_SETS)

    # Dependencies
    match = re.search(r"export const DEPENDENCIES = Object\.freeze\(\{(.*?)\}\);", source, re.S)
    assert match, 'DEPENDENCIES not found in resetRules.js'
    frontend_deps = {
        key: set(_js_string_list(values))
        for key, values in re.findall(r"(\w+):\s*Object\.freeze\(\[(.*?)\]\)", match.group(1))
    }
    assert frontend_deps == DEPENDENCIES

    # Confirmation phrase
    match = re.search(r"export const CONFIRMATION_PHRASE = '([^']*)';", source)
    assert match, 'CONFIRMATION_PHRASE not found in resetRules.js'
    assert match.group(1) == CONFIRMATION_PHRASE == 'PURGER LA BASE'
    assert CONFIRMATION_PHRASE != backup_service.CONFIRMATION_PHRASE

    # Default selection holds known ids only (the UI adds the implied sets itself)
    match = re.search(r"export const DEFAULT_SELECTION = Object\.freeze\(\[(.*?)\]\)", source,
                      re.S)
    assert match, 'DEFAULT_SELECTION not found in resetRules.js'
    default_selection = _js_string_list(match.group(1))
    assert default_selection
    assert set(default_selection) <= set(PURGE_SETS)

    # i18n: set labels/descriptions and one message per backend error code, in both languages
    for lang in ('fr', 'en'):
        section = _locale_database_section(lang)
        for set_id in frontend_ids:
            entry = section['reset']['sets'][set_id]
            assert entry['label'] and entry['description'], f'{lang}: {set_id}'
        for code in _backend_error_codes():
            assert section['errors'].get(code), f'{lang}: missing admin.database.errors.{code}'


# ---------------------------------------------------------------------------
# 3. Request validation (task 2.5)
# ---------------------------------------------------------------------------
import boto3

from reset_service import BackupRequired, InvalidSelection, validate_request
from tests.integration.backup_helpers import REGION, items_by_key


def _body(**overrides):
    """A valid purge request; keys set to None are removed"""
    body = {'confirmation_phrase': CONFIRMATION_PHRASE, 'sets': ['boats', 'payments']}
    body.update(overrides)
    return {k: v for k, v in body.items() if v is not None}


_REAL_SCAN_TABLE = backup_service.scan_table


def _side_effects_snapshot():
    """Table content, S3 backup objects and native backups"""
    s3 = boto3.client('s3', region_name=REGION)
    objects = sorted(o['Key'] for o in
                     s3.list_objects_v2(Bucket=os.environ['BACKUP_BUCKET']).get('Contents', []))
    native = boto3.client('dynamodb', region_name=REGION).list_backups(
        TableName=os.environ['TABLE_NAME'])['BackupSummaries']
    state = items_by_key(_REAL_SCAN_TABLE(), include_audit=True)
    return state, objects, sorted(b['BackupName'] for b in native)


@pytest.fixture
def validation_env(backup_bucket, dynamodb_table, monkeypatch):
    """Seeded table + backup bucket; any database access during validation fails the test"""
    clear_table(dynamodb_table)
    items, _, _ = _seed_items()
    put_typed_items(items)

    def forbidden(*args, **kwargs):
        raise AssertionError('validate_request must not touch the database')

    monkeypatch.setattr(backup_service, 'scan_table', forbidden)
    monkeypatch.setattr(backup_service, 'create_backup', forbidden)
    monkeypatch.setattr(backup_service, 'batch_write_with_retry', forbidden)
    monkeypatch.setattr(backup_service, 'write_audit', forbidden)
    monkeypatch.setattr(reset_service, '_get_cognito_client', forbidden)
    monkeypatch.setenv('ENVIRONMENT', 'dev')
    return _side_effects_snapshot


def _assert_rejected(error_class, code, body, snapshot, status=400):
    before = snapshot()
    with pytest.raises(error_class) as raised:
        validate_request(body)
    assert raised.value.code == code
    assert raised.value.status == status
    assert snapshot() == before
    return raised.value


# -- selection ---------------------------------------------------------------
@pytest.mark.parametrize('sets', [
    [], None, 'boats', {'boats': True}, 42, [None], ['boats', 3], [['boats']],
], ids=['empty', 'missing', 'string', 'dict', 'int', 'null-member', 'int-member', 'nested'])
def test_invalid_selection_rejected_shape(validation_env, sets):
    _assert_rejected(InvalidSelection, 'INVALID_SELECTION', _body(sets=sets), validation_env)


@pytest.mark.parametrize('sets, unknown', [
    (['nope'], ['nope']),
    (['boats', 'payments', 'cognito'], ['cognito']),
    (['Boats'], ['Boats']),
    (['zzz', 'aaa'], ['aaa', 'zzz']),
])
def test_invalid_selection_unknown_ids(validation_env, sets, unknown):
    error = _assert_rejected(InvalidSelection, 'INVALID_SELECTION', _body(sets=sets),
                             validation_env)
    assert error.details['unknown'] == unknown


@pytest.mark.parametrize('sets, missing', [
    (['boats'], ['payments']),
    (['crew'], ['boats', 'payments']),
    (['crew', 'boats'], ['payments']),
    (['managers'], ['boats', 'crew', 'payments', 'temp_access']),
    (['managers', 'boats', 'payments', 'crew'], ['temp_access']),
])
def test_invalid_selection_not_closed_reports_missing(validation_env, sets, missing):
    error = _assert_rejected(InvalidSelection, 'INVALID_SELECTION', _body(sets=sets),
                             validation_env)
    assert error.details['missing'] == missing


def test_selection_is_never_auto_closed(validation_env):
    with pytest.raises(InvalidSelection):
        validate_request(_body(sets=['crew']))


@pytest.mark.parametrize('delete_cognito', [True, 'true', 1, 'yes', None, 0, 'false'])
def test_cognito_flag_validation(validation_env, delete_cognito):
    """True needs `managers`; anything non-boolean is rejected (None is a JSON null)"""
    body = _body(sets=['boats', 'payments'])
    body['delete_cognito'] = delete_cognito
    _assert_rejected(InvalidSelection, 'INVALID_SELECTION', body, validation_env)


def test_cognito_without_managers_names_managers(validation_env):
    error = _assert_rejected(InvalidSelection, 'INVALID_SELECTION',
                             _body(delete_cognito=True), validation_env)
    assert error.details['missing'] == ['managers']


def test_cognito_with_managers_accepted(validation_env):
    selection = resolve_closure(['managers'])
    assert validate_request(_body(sets=sorted(selection), delete_cognito=True)) == (
        selection, True, True)
    assert validate_request(_body(sets=sorted(selection), delete_cognito=False))[1] is False


@pytest.mark.parametrize('backup_before', ['true', 'false', 0, 1, None, 'no'])
def test_non_boolean_backup_before_rejected(validation_env, backup_before):
    body = _body()
    body['backup_before'] = backup_before
    _assert_rejected(InvalidSelection, 'INVALID_SELECTION', body, validation_env)


@pytest.mark.parametrize('subset', _ALL_SUBSETS,
                         ids=lambda s: '+'.join(sorted(s)) or 'empty')
def test_selection_accepted_iff_closed(validation_env, subset):
    body = _body(sets=sorted(subset))
    before = validation_env()
    closed = bool(subset) and resolve_closure(subset) == set(subset)
    if closed:
        assert validate_request(body) == (set(subset), False, True)
    else:
        with pytest.raises(InvalidSelection):
            validate_request(body)
    assert validation_env() == before


def test_exactly_the_closed_nonempty_subsets_are_accepted():
    accepted = [s for s in _ALL_SUBSETS if s and _expected_closure(s) == set(s)]
    # every accepted subset is closed under the hand-written dependency table
    assert accepted and len(accepted) < 63


# -- phrase ------------------------------------------------------------------
@pytest.mark.parametrize('phrase', [
    '', 'purger la base', 'Purger La Base', 'PURGER LA BASE ', ' PURGER LA BASE',
    'PURGER  LA BASE', 'PURGER LA BASE\n', 'RESTAURER LA BASE', 'PURGER', None, 42, True,
    ['PURGER LA BASE'],
], ids=['empty', 'lower', 'title', 'trailing-space', 'leading-space', 'double-space',
        'newline', 'restore-phrase', 'partial', 'null', 'int', 'bool', 'list'])
def test_wrong_phrase_rejected(validation_env, phrase):
    body = _body()
    body['confirmation_phrase'] = phrase
    _assert_rejected(reset_service.InvalidConfirmation, 'INVALID_CONFIRMATION', body,
                     validation_env)


def test_missing_phrase_rejected(validation_env):
    _assert_rejected(reset_service.InvalidConfirmation, 'INVALID_CONFIRMATION',
                     _body(confirmation_phrase=None), validation_env)


@pytest.mark.parametrize('body', [None, '', 'not json', '{"sets": ["boats"]}', [], 42, {}],
                         ids=['none', 'empty-str', 'non-json', 'json-text', 'list', 'int',
                              'empty-dict'])
def test_non_object_body_rejected(validation_env, body):
    _assert_rejected(reset_service.InvalidConfirmation, 'INVALID_CONFIRMATION', body,
                     validation_env)


def test_phrase_is_checked_before_selection(validation_env):
    """An invalid selection with a wrong phrase reports the phrase"""
    _assert_rejected(reset_service.InvalidConfirmation, 'INVALID_CONFIRMATION',
                     {'confirmation_phrase': 'x', 'sets': [], 'delete_cognito': True,
                      'backup_before': False}, validation_env)


def test_selection_is_checked_before_backup_rule(validation_env, monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'prod')
    _assert_rejected(InvalidSelection, 'INVALID_SELECTION',
                     _body(sets=['crew'], backup_before=False), validation_env)


def test_cognito_flag_is_checked_before_backup_rule(validation_env, monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'prod')
    _assert_rejected(InvalidSelection, 'INVALID_SELECTION',
                     _body(delete_cognito=True, backup_before=False), validation_env)


# -- production backup rule --------------------------------------------------
@pytest.mark.parametrize('body_environment', [None, 'prod', 'dev', 'staging', ''],
                         ids=['no-field', 'body-prod', 'body-dev', 'body-staging', 'body-empty'])
@pytest.mark.parametrize('backup_before, expected_backup', [
    (True, True), (False, False), (None, True),
], ids=['true', 'false', 'missing'])
@pytest.mark.parametrize('environment', ['prod', 'dev'])
def test_prod_backup_rule(validation_env, monkeypatch, environment, backup_before,
                          expected_backup, body_environment):
    monkeypatch.setenv('ENVIRONMENT', environment)
    body = _body(backup_before=backup_before)
    if body_environment is not None:
        body['environment'] = body_environment
    before = validation_env()

    if environment == 'prod' and backup_before is False:
        _assert_rejected(BackupRequired, 'BACKUP_REQUIRED', body, validation_env)
        return
    selection, delete_cognito, backup = validate_request(body)
    assert (selection, delete_cognito, backup) == ({'boats', 'payments'}, False, expected_backup)
    assert validation_env() == before


def test_environment_variable_unset_allows_no_backup(validation_env, monkeypatch):
    monkeypatch.delenv('ENVIRONMENT', raising=False)
    assert validate_request(_body(backup_before=False))[2] is False


def test_prod_backup_required_message_and_status(validation_env, monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'prod')
    error = _assert_rejected(BackupRequired, 'BACKUP_REQUIRED', _body(backup_before=False),
                             validation_env)
    assert 'production' in error.message.lower()


# -- accepted request returns the normalized triple ---------------------------
def test_valid_request_returns_triple(validation_env):
    body = _body(sets=['payments', 'boats', 'audit_logs'], backup_before=False)
    assert validate_request(body) == ({'boats', 'payments', 'audit_logs'}, False, False)


def test_valid_request_defaults(validation_env):
    assert validate_request(_body(sets=['audit_logs'])) == ({'audit_logs'}, False, True)


# ---------------------------------------------------------------------------
# 4. Execution (task 2.7)
# ---------------------------------------------------------------------------
import json
from datetime import timedelta

from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError

from reset_service import PreResetBackupFailed, ResetPartial, execute_reset
from tests.integration.backup_helpers import ADMIN_USER, table_state, utc

# Hand-written, independent of PURGE_SETS: which keys belong to which set
_PREDICATES = {
    'boats': lambda pk, sk: pk.startswith('TEAM#') and sk.startswith('BOAT#'),
    'payments': lambda pk, sk: pk.startswith('TEAM#') and sk.startswith('PAYMENT#'),
    'crew': lambda pk, sk: pk.startswith('TEAM#') and sk.startswith('CREW#'),
    'managers': lambda pk, sk: pk.startswith('USER#') and (
        sk == 'PROFILE' or sk.startswith('CONSENT#')),
    'temp_access': lambda pk, sk: pk == 'TEMP_ACCESS' and sk.startswith('USER#'),
    'audit_logs': lambda pk, sk: pk in AUDIT_PARTITIONS,
}
_PROTECTED_KEYS = [('CONFIG', 'SYSTEM'), ('RACE', 'R1'), ('RACE', 'R2'), ('CLUB', 'C1')]

_EXPECTED_COUNTS = _seed_items()[1]


@pytest.fixture
def fake_clock(monkeypatch):
    """Distinct UTC moments (one second apart): backup ids have 1 s resolution"""
    state = {'moment': utc(0)}

    def _now():
        state['moment'] = state['moment'] + timedelta(seconds=1)
        return state['moment']

    monkeypatch.setattr(backup_service, '_utc_now', _now)
    return _now


@pytest.fixture
def purge_env(backup_bucket, dynamodb_table, fake_clock, monkeypatch):
    """Seeded table (every key kind), backup bucket, dev environment"""
    clear_table(dynamodb_table)
    items, _, _ = _seed_items()
    put_typed_items(items)
    monkeypatch.setenv('ENVIRONMENT', 'dev')


class _Faulty:
    """Wrapper over a boto3 client: named methods raise; every call is recorded"""

    def __init__(self, real, failing=()):
        self._real = real
        self._failing = set(failing)
        self.calls = []

    def __getattr__(self, name):
        if name in self._failing:
            def fail(*args, **kwargs):
                raise ClientError(
                    {'Error': {'Code': 'InternalFailure', 'Message': 'injected'}}, name)
            return fail
        method = getattr(self._real, name)

        def call(*args, **kwargs):
            self.calls.append((name, kwargs))
            return method(*args, **kwargs)
        return call


class _DeleteFault(_Faulty):
    """Fails batch_write_item for chunks deleting `fail_set` (after `skip` good chunks)"""

    def __init__(self, real, fail_set, skip=0):
        super().__init__(real)
        self.fail_set, self.skip = fail_set, skip

    def batch_write_item(self, RequestItems):
        for requests in RequestItems.values():
            key = requests[0]['DeleteRequest']['Key']
            if classify(key['PK']['S'], key['SK']['S']) == self.fail_set:
                if self.skip > 0:
                    self.skip -= 1
                else:
                    raise ClientError(
                        {'Error': {'Code': 'InternalFailure', 'Message': 'injected'}},
                        'BatchWriteItem')
        self.calls.append(('batch_write_item', {'RequestItems': RequestItems}))
        return self._real.batch_write_item(RequestItems=RequestItems)


def _install(client):
    backup_service._dynamodb_client = client
    return client


def _forbid_cognito(monkeypatch):
    calls = []

    def forbidden(*args, **kwargs):
        calls.append(1)
        raise AssertionError('Cognito must not be called')

    monkeypatch.setattr(reset_service, '_get_cognito_client', forbidden)
    return calls


def _full_state():
    return items_by_key(_REAL_SCAN_TABLE(), include_audit=True)


def _s3_keys():
    s3 = boto3.client('s3', region_name=REGION)
    return sorted(o['Key'] for o in
                  s3.list_objects_v2(Bucket=os.environ['BACKUP_BUCKET']).get('Contents', []))


def _native_names():
    client = boto3.client('dynamodb', region_name=REGION)
    return sorted(b['BackupName'] for b in
                  client.list_backups(TableName=os.environ['TABLE_NAME'])['BackupSummaries'])


def _audit_records(action):
    deserializer = TypeDeserializer()
    records = []
    for item in _REAL_SCAN_TABLE():
        if item['PK']['S'] == backup_service.AUDIT_PK:
            record = {k: deserializer.deserialize(v) for k, v in item.items()}
            if record.get('action') == action:
                records.append(record)
    return records


def _backup_items(backup_id):
    body = boto3.client('s3', region_name=REGION).get_object(
        Bucket=os.environ['BACKUP_BUCKET'], Key=backup_id)['Body'].read()
    envelope = json.loads(body)
    return items_by_key(backup_service.decode_items(envelope['items']), include_audit=True)


def _expected_remaining(before, selected):
    return {key: value for key, value in before.items()
            if not any(_PREDICATES[s](*key) for s in selected)}


def _ordered(selected):
    return [s for s in PURGE_ORDER if s in selected]


_SELECTIONS = {
    'default': ['boats', 'payments'],
    'all': SET_IDS,
    'boats': ['boats', 'payments'],
    'payments': ['payments'],
    'crew': ['crew', 'boats', 'payments'],
    'managers': ['managers', 'boats', 'payments', 'crew', 'temp_access'],
    'temp_access': ['temp_access'],
    'audit_logs': ['audit_logs'],
    'all_but_audit': [s for s in SET_IDS if s != 'audit_logs'],
}


# ---- Property 3: scope and counts -------------------------------------------
@pytest.mark.parametrize('selection', list(_SELECTIONS.values()), ids=list(_SELECTIONS))
def test_purge_scope_and_counts(purge_env, selection):
    selected = set(selection)
    before = table_state()
    result = execute_reset(_body(sets=selection), ADMIN_USER)

    expected_deleted = {s: _EXPECTED_COUNTS[s] for s in _ordered(selected)}
    assert result['deleted'] == expected_deleted
    assert result['sets'] == _ordered(selected)
    assert result['total_deleted'] == sum(expected_deleted.values())
    assert result['cognito'] == {'requested': False, 'deleted': 0, 'skipped_admins': 0,
                                 'not_found': 0, 'failed': []}
    assert result['audit_written'] is True
    assert isinstance(result['duration_ms'], int) and result['duration_ms'] >= 0
    assert set(result) == {'sets', 'deleted', 'total_deleted', 'cognito',
                           'pre_reset_backup', 'audit_written', 'duration_ms'}

    after = table_state()
    assert after == _expected_remaining(before, selected)
    for key in _PROTECTED_KEYS:
        assert key in after
    for key, value in before.items():  # unselected sets are untouched
        if not any(_PREDICATES[s](*key) for s in selected):
            assert after[key] == value


def test_purge_everything_leaves_only_unclassified_and_protected(purge_env):
    execute_reset(_body(sets=SET_IDS), ADMIN_USER)
    remaining = set(table_state())
    assert remaining == {
        ('TEAM#t1', 'CREW_MEMBER#m1'), ('TEAM#t1', 'CREW_MEMBER#m2'),
        ('TEAM#t1', 'METADATA'), ('USER#u1', 'OTHER'),
        ('CONFIG', 'SYSTEM'), ('RACE', 'R1'), ('RACE', 'R2'), ('CLUB', 'C1'),
    }


def test_purge_of_empty_set_reports_zero(purge_env, dynamodb_table):
    for key in [('TEMP_ACCESS', 'USER#u1'), ('TEMP_ACCESS', 'USER#u2')]:
        dynamodb_table.delete_item(Key={'PK': key[0], 'SK': key[1]})
    result = execute_reset(_body(sets=['temp_access']), ADMIN_USER)
    assert result['deleted'] == {'temp_access': 0}
    assert result['total_deleted'] == 0


def test_deletion_in_chunks_of_25(purge_env):
    put_typed_items([{'PK': _s('TEAM#big'), 'SK': _s(f'BOAT#{i:03d}')} for i in range(60)])
    client = _install(_Faulty(backup_service._get_dynamodb_client()))
    result = execute_reset(_body(sets=['boats', 'payments'], backup_before=False), ADMIN_USER)
    sizes = [len(next(iter(kw['RequestItems'].values())))
             for name, kw in client.calls if name == 'batch_write_item']
    assert result['deleted']['boats'] == 63
    assert sizes == [2, 25, 25, 13]  # payments first, then 63 boats in chunks of 25


def test_single_scan_without_backup(purge_env):
    client = _install(_Faulty(backup_service._get_dynamodb_client()))
    execute_reset(_body(sets=['boats', 'payments'], backup_before=False), ADMIN_USER)
    assert [n for n, _ in client.calls].count('scan') == 1


def test_no_boat_number_counter_created(purge_env):
    execute_reset(_body(sets=SET_IDS), ADMIN_USER)
    assert not [k for k in table_state() if 'COUNTER' in k[0] or 'COUNTER' in k[1]]


# ---- Property 6: backup before deletion -------------------------------------
def test_backup_taken_before_first_delete(purge_env):
    before = _full_state()
    seen = {}

    class Spy(_Faulty):
        def batch_write_item(self, RequestItems):
            if 'checked' not in seen:
                seen['checked'] = True
                keys = [k for k in _s3_keys() if k.startswith('safety-pre-reset_')]
                seen['keys'] = keys
                seen['native'] = _native_names()
                seen['items'] = _backup_items(keys[0]) if keys else None
                seen['table'] = _full_state()
            return self._real.batch_write_item(RequestItems=RequestItems)

    _install(Spy(backup_service._get_dynamodb_client()))
    result = execute_reset(_body(sets=['boats', 'payments']), ADMIN_USER)

    backup_id = result['pre_reset_backup']['backup_id']
    assert seen['keys'] == [backup_id]
    assert re.match(r'^safety-pre-reset_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z\.json$', backup_id)
    assert len(seen['native']) == 1 and 'safety-pre-reset_' in seen['native'][0]
    assert seen['items'] == before            # full pre-purge table
    assert seen['table'] == before            # nothing deleted yet
    assert result['pre_reset_backup']['native_backup']['name'] == seen['native'][0]
    # protected data and unselected sets are inside the backup
    for key in _PROTECTED_KEYS + [('TEAM#t1', 'CREW#c0'), ('USER#u1', 'PROFILE')]:
        assert key in seen['items']


@pytest.mark.parametrize('inject, artifact', [
    (lambda: backup_service.__setattr__(
        '_s3_client', _Faulty(backup_service._get_s3_client(), ['put_object'])), 'json'),
    (lambda: _install(_Faulty(backup_service._get_dynamodb_client(), ['scan'])), 'json'),
    (lambda: _install(_Faulty(backup_service._get_dynamodb_client(), ['create_backup'])),
     'aws_native'),
], ids=['s3_put_fails', 'scan_fails', 'native_fails'])
def test_backup_failure_aborts(purge_env, inject, artifact):
    before = _full_state()
    inject()
    with pytest.raises(PreResetBackupFailed) as raised:
        execute_reset(_body(sets=SET_IDS), ADMIN_USER)
    error = raised.value
    assert error.code == 'PRE_RESET_BACKUP_FAILED' and error.status == 500
    assert error.details['failed_artifact'] == artifact
    assert error.details['database_modified'] is False
    backup_service._dynamodb_client = None
    backup_service._s3_client = None
    assert _full_state() == before
    assert _audit_records('reset_database') == []


def test_prod_takes_backup_even_when_backup_before_true(purge_env, monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'prod')
    result = execute_reset(_body(sets=['audit_logs'], backup_before=True), ADMIN_USER)
    assert result['pre_reset_backup']['backup_id'].startswith('safety-pre-reset_')
    assert len(_s3_keys()) == 1


def test_prod_without_backup_refused_and_nothing_done(purge_env, monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'prod')
    before = _full_state()
    with pytest.raises(BackupRequired):
        execute_reset(_body(sets=SET_IDS, backup_before=False), ADMIN_USER)
    assert _full_state() == before and _s3_keys() == []


def test_dev_purge_without_backup(purge_env):
    result = execute_reset(_body(sets=['boats', 'payments'], backup_before=False), ADMIN_USER)
    assert result['pre_reset_backup'] is None
    assert _s3_keys() == [] and _native_names() == []
    audit, = _audit_records('reset_database')
    assert audit['details']['backup_taken'] is False
    assert 'pre_reset_backup_id' not in audit['details']


def test_invalid_request_takes_no_backup_and_changes_nothing(purge_env):
    before = _full_state()
    with pytest.raises(InvalidSelection):
        execute_reset(_body(sets=['crew']), ADMIN_USER)
    assert _full_state() == before and _s3_keys() == [] and _native_names() == []


# ---- Undo path ---------------------------------------------------------------
def test_pre_reset_backup_restores_pre_purge_state(purge_env):
    before = table_state()
    result = execute_reset(_body(sets=SET_IDS), ADMIN_USER)
    assert table_state() != before
    backup_id = result['pre_reset_backup']['backup_id']

    restored = backup_service.restore_backup(
        backup_id, backup_service.CONFIRMATION_PHRASE, ADMIN_USER)
    assert restored['safety_backup']['backup_id'].startswith('safety-pre-restore_')
    assert table_state() == before


# ---- Property 10: partial failure -------------------------------------------
@pytest.mark.parametrize('fail_set', list(PURGE_ORDER))
def test_partial_failure_at_each_set(purge_env, monkeypatch, fail_set):
    cognito_calls = _forbid_cognito(monkeypatch)
    before = table_state()
    _install(_DeleteFault(backup_service._get_dynamodb_client(), fail_set))

    with pytest.raises(ResetPartial) as raised:
        execute_reset(_body(sets=SET_IDS, delete_cognito=True), ADMIN_USER)
    error = raised.value
    assert error.code == 'RESET_PARTIAL' and error.status == 500

    done = PURGE_ORDER[:PURGE_ORDER.index(fail_set)]
    expected_deleted = {s: (_EXPECTED_COUNTS[s] if s in done else 0) for s in PURGE_ORDER}
    assert error.details['stage'] == fail_set
    assert error.details['deleted'] == expected_deleted
    assert error.details['cognito'] == 'not_attempted'
    backup_id = error.details['pre_reset_backup_id']
    assert backup_id.startswith('safety-pre-reset_')
    assert cognito_calls == []

    backup_service._dynamodb_client = None
    assert table_state() == _expected_remaining(before, set(done))

    audit, = _audit_records('reset_database')
    assert audit['details']['outcome'] == 'partial'
    assert audit['details']['deleted'] == {k: v for k, v in expected_deleted.items()}
    assert audit['details']['pre_reset_backup_id'] == backup_id

    backup_service.restore_backup(backup_id, backup_service.CONFIRMATION_PHRASE, ADMIN_USER)
    assert table_state() == before


def test_partial_failure_midway_through_a_set(purge_env):
    put_typed_items([{'PK': _s('TEAM#big'), 'SK': _s(f'BOAT#{i:03d}')} for i in range(60)])
    before = table_state()
    _install(_DeleteFault(backup_service._get_dynamodb_client(), 'boats', skip=1))
    with pytest.raises(ResetPartial) as raised:
        execute_reset(_body(sets=['boats', 'payments']), ADMIN_USER)
    assert raised.value.details['stage'] == 'boats'
    assert raised.value.details['deleted']['boats'] == 25
    assert raised.value.details['deleted']['payments'] == _EXPECTED_COUNTS['payments']
    backup_service._dynamodb_client = None
    boats_left = [k for k in table_state() if _PREDICATES['boats'](*k)]
    assert len(boats_left) == 63 - 25
    backup_service.restore_backup(raised.value.details['pre_reset_backup_id'],
                                  backup_service.CONFIRMATION_PHRASE, ADMIN_USER)
    assert table_state() == before


def test_partial_failure_without_backup_has_null_backup_id(purge_env):
    _install(_DeleteFault(backup_service._get_dynamodb_client(), 'payments'))
    with pytest.raises(ResetPartial) as raised:
        execute_reset(_body(sets=['boats', 'payments'], backup_before=False), ADMIN_USER)
    assert raised.value.details['pre_reset_backup_id'] is None
    assert raised.value.details['deleted'] == {'payments': 0, 'boats': 0}


def test_scan_failure_before_deletion_changes_nothing(purge_env):
    before = _full_state()
    _install(_Faulty(backup_service._get_dynamodb_client(), ['scan']))
    with pytest.raises(backup_service.BackupError) as raised:
        execute_reset(_body(sets=['boats', 'payments'], backup_before=False), ADMIN_USER)
    assert raised.value.code == 'INTERNAL_ERROR'
    assert raised.value.details['database_modified'] is False
    backup_service._dynamodb_client = None
    assert _full_state() == before


# ---- Cognito: never called when not requested (task 2.9 covers the rest) ----
@pytest.mark.parametrize('selection', [SET_IDS, _SELECTIONS['managers']], ids=['all', 'managers'])
def test_cognito_not_called_when_option_unchecked(purge_env, monkeypatch, selection):
    calls = _forbid_cognito(monkeypatch)
    for body in (_body(sets=selection), _body(sets=selection, delete_cognito=False)):
        result = execute_reset(body, ADMIN_USER)
        assert result['cognito']['requested'] is False
        assert result['cognito']['deleted'] == 0
    assert calls == []


# ---- Property 11: audit ------------------------------------------------------
def test_audit_record_fields(purge_env, monkeypatch):
    selection = _SELECTIONS['crew']
    real_write = backup_service.write_audit
    at_audit = {}

    def spy(action, user, details=None):
        at_audit['remaining'] = [k for k in table_state()
                                 if any(_PREDICATES[s](*k) for s in selection)]
        return real_write(action, user, details)

    monkeypatch.setattr(backup_service, 'write_audit', spy)
    result = execute_reset(_body(sets=['payments', 'crew', 'boats']), ADMIN_USER)

    assert at_audit['remaining'] == []  # written after the purge
    audit, = _audit_records('reset_database')
    assert audit['user_id'] == 'u1' and audit['user_email'] == 'a@b.c'
    assert re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$', audit['timestamp'])
    details = audit['details']
    assert details['outcome'] == 'success'
    assert details['sets'] == ['payments', 'boats', 'crew']
    assert details['deleted'] == {'payments': 2, 'boats': 3, 'crew': 5}
    assert details['delete_cognito'] is False
    assert details['cognito_deleted'] == 0 and details['cognito_failed'] == 0
    assert details['backup_taken'] is True
    assert details['pre_reset_backup_id'] == result['pre_reset_backup']['backup_id']
    assert details['environment'] == 'dev'


def test_backup_audit_history_preserved(purge_env):
    history = {k: v for k, v in _full_state().items() if k[0] == backup_service.AUDIT_PK}
    assert len(history) == 2
    execute_reset(_body(sets=SET_IDS), ADMIN_USER)
    after = _full_state()
    for key, value in history.items():
        assert after[key] == value
    assert len(_audit_records('reset_database')) == 1


def test_two_purges_write_two_audit_records(purge_env):
    execute_reset(_body(sets=['audit_logs']), ADMIN_USER)
    execute_reset(_body(sets=['temp_access']), ADMIN_USER)
    assert len(_audit_records('reset_database')) == 2


def test_audit_failure_is_reported_not_fatal(purge_env):
    _install(_Faulty(backup_service._get_dynamodb_client(), ['put_item']))
    result = execute_reset(_body(sets=['boats', 'payments'], backup_before=False), ADMIN_USER)
    assert result['audit_written'] is False
    assert result['deleted']['boats'] == 3
    backup_service._dynamodb_client = None
    assert _audit_records('reset_database') == []
    assert not [k for k in table_state() if _PREDICATES['boats'](*k)]


# ---------------------------------------------------------------------------
# 5. Cognito step (task 2.9) - Property 9
# ---------------------------------------------------------------------------
from reset_service import delete_cognito_accounts


class _CognitoFault:
    """Wrapper over the moto cognito client: named methods raise for chosen usernames"""

    def __init__(self, real, fail=None):
        """fail: {method_name: {username: error_code}}"""
        self._real = real
        self._fail = fail or {}
        self.calls = []

    def __getattr__(self, name):
        method = getattr(self._real, name)

        def call(*args, **kwargs):
            self.calls.append((name, kwargs.get('Username')))
            code = self._fail.get(name, {}).get(kwargs.get('Username'))
            if code:
                raise ClientError({'Error': {'Code': code, 'Message': 'injected'}}, name)
            return method(*args, **kwargs)
        return call


def test_team_managers_deleted(cognito_pool):
    cognito_pool.add_user('m1')
    cognito_pool.add_user('m2')
    result = delete_cognito_accounts(['m1', 'm2'])
    assert result == {'requested': True, 'deleted': 2, 'skipped_admins': 0,
                      'not_found': 0, 'failed': []}
    assert cognito_pool.usernames() == []


def test_admins_are_never_deleted(cognito_pool):
    cognito_pool.add_user('a1', admin=True)
    cognito_pool.add_user('a2', admin=True)
    result = delete_cognito_accounts(['a1', 'a2'])
    assert result['deleted'] == 0 and result['skipped_admins'] == 2
    assert result['failed'] == [] and result['not_found'] == 0
    assert cognito_pool.usernames() == ['a1', 'a2']


def test_admin_never_deleted_even_when_listed_among_managers_and_failures(cognito_pool):
    """An admin survives whatever happens to the other accounts"""
    cognito_pool.add_user('a1', admin=True)
    cognito_pool.add_user('m1')
    cognito_pool.add_user('m2')
    client = _CognitoFault(cognito_pool.client,
                           {'admin_delete_user': {'m1': 'InternalErrorException'}})
    reset_service._cognito_client = client
    result = delete_cognito_accounts(['m1', 'a1', 'm2'])
    assert 'a1' in cognito_pool.usernames()
    assert ('admin_delete_user', 'a1') not in client.calls


def test_mixed_set_counts(cognito_pool):
    cognito_pool.add_user('a1', admin=True)
    cognito_pool.add_user('m1')
    cognito_pool.add_user('m2')
    result = delete_cognito_accounts(['a1', 'm1', 'ghost', 'm2'])
    assert result == {'requested': True, 'deleted': 2, 'skipped_admins': 1,
                      'not_found': 1, 'failed': []}
    assert cognito_pool.usernames() == ['a1']


def test_empty_subs(cognito_pool):
    assert delete_cognito_accounts([]) == {'requested': True, 'deleted': 0,
                                           'skipped_admins': 0, 'not_found': 0, 'failed': []}


def test_group_check_user_not_found_counts_not_found(cognito_pool):
    cognito_pool.add_user('m1')
    client = _CognitoFault(cognito_pool.client, {
        'admin_list_groups_for_user': {'m1': 'UserNotFoundException'}})
    reset_service._cognito_client = client
    result = delete_cognito_accounts(['m1'])
    assert result['not_found'] == 1 and result['deleted'] == 0 and result['failed'] == []
    assert ('admin_delete_user', 'm1') not in client.calls


def test_group_check_failure_fails_closed(cognito_pool):
    """A failed group check never leads to a deletion; the loop goes on"""
    cognito_pool.add_user('m1')
    cognito_pool.add_user('m2')
    cognito_pool.add_user('m3')
    client = _CognitoFault(cognito_pool.client, {
        'admin_list_groups_for_user': {'m2': 'InternalErrorException'}})
    reset_service._cognito_client = client
    result = delete_cognito_accounts(['m1', 'm2', 'm3'])
    assert result['deleted'] == 2
    assert result['failed'] == [{'sub': 'm2', 'code': 'InternalErrorException'}]
    assert cognito_pool.usernames() == ['m2']
    assert ('admin_delete_user', 'm2') not in client.calls


def test_group_check_failure_on_an_admin_does_not_delete_it(cognito_pool):
    cognito_pool.add_user('a1', admin=True)
    client = _CognitoFault(cognito_pool.client, {
        'admin_list_groups_for_user': {'a1': 'TooManyRequestsException'}})
    reset_service._cognito_client = client
    result = delete_cognito_accounts(['a1'])
    assert result['deleted'] == 0
    assert result['failed'] == [{'sub': 'a1', 'code': 'TooManyRequestsException'}]
    assert cognito_pool.usernames() == ['a1']


def test_delete_failure_reported_and_rest_processed(cognito_pool):
    for sub in ['m1', 'm2', 'm3', 'm4']:
        cognito_pool.add_user(sub)
    cognito_pool.add_user('a1', admin=True)
    client = _CognitoFault(cognito_pool.client, {
        'admin_delete_user': {'m1': 'InternalErrorException',
                              'm3': 'NotAuthorizedException'}})
    reset_service._cognito_client = client
    result = delete_cognito_accounts(['m1', 'm2', 'm3', 'm4', 'a1'])
    assert result['deleted'] == 2 and result['skipped_admins'] == 1
    assert result['failed'] == [{'sub': 'm1', 'code': 'InternalErrorException'},
                                {'sub': 'm3', 'code': 'NotAuthorizedException'}]
    assert cognito_pool.usernames() == ['a1', 'm1', 'm3']


def test_delete_user_not_found_counts_not_found(cognito_pool):
    """Account removed between the group check and the deletion"""
    cognito_pool.add_user('m1')
    client = _CognitoFault(cognito_pool.client, {
        'admin_delete_user': {'m1': 'UserNotFoundException'}})
    reset_service._cognito_client = client
    result = delete_cognito_accounts(['m1'])
    assert result['not_found'] == 1 and result['deleted'] == 0 and result['failed'] == []


def test_group_pagination_is_followed(cognito_pool):
    """`admins` on a later page still protects the account"""
    class Paged:
        def __init__(self):
            self.deleted = []

        def admin_list_groups_for_user(self, UserPoolId, Username, NextToken=None):
            if NextToken is None:
                return {'Groups': [{'GroupName': 'other'}], 'NextToken': 'page2'}
            return {'Groups': [{'GroupName': 'admins'}]}

        def admin_delete_user(self, UserPoolId, Username):
            self.deleted.append(Username)

    paged = Paged()
    reset_service._cognito_client = paged
    result = delete_cognito_accounts(['a1'])
    assert result['skipped_admins'] == 1 and result['deleted'] == 0
    assert paged.deleted == []


def test_missing_user_pool_id_fails_all_without_raising(cognito_pool, monkeypatch):
    cognito_pool.add_user('m1')
    monkeypatch.delenv('USER_POOL_ID')
    result = delete_cognito_accounts(['m1', 'm2'])
    assert result['deleted'] == 0
    assert result['failed'] == [{'sub': 'm1', 'code': 'CognitoUnavailable'},
                                {'sub': 'm2', 'code': 'CognitoUnavailable'}]
    assert cognito_pool.usernames() == ['m1']


def test_client_creation_failure_fails_all_without_raising(cognito_pool, monkeypatch):
    def broken():
        raise RuntimeError('no client')

    monkeypatch.setattr(reset_service, '_get_cognito_client', broken)
    result = delete_cognito_accounts(['m1'])
    assert result['failed'] == [{'sub': 'm1', 'code': 'CognitoUnavailable'}]
    assert result['requested'] is True


# ---- end to end through execute_reset ---------------------------------------
_MANAGER_SELECTION = _SELECTIONS['managers']  # seeded manager subs: u1, u2, u3


def test_execute_reset_deletes_managers_and_audits(purge_env, cognito_pool):
    cognito_pool.add_user('u1', admin=True)   # admin with a profile: skipped
    cognito_pool.add_user('u2')               # team manager: deleted
    cognito_pool.add_user('other')            # not a purged profile: untouched
    # u3 has a profile but no Cognito account: not_found
    result = execute_reset(_body(sets=_MANAGER_SELECTION, delete_cognito=True), ADMIN_USER)

    assert result['cognito'] == {'requested': True, 'deleted': 1, 'skipped_admins': 1,
                                 'not_found': 1, 'failed': []}
    assert cognito_pool.usernames() == ['other', 'u1']
    assert not [k for k in table_state() if _PREDICATES['managers'](*k)]

    audit, = _audit_records('reset_database')
    assert audit['details']['delete_cognito'] is True
    assert audit['details']['cognito_deleted'] == 1
    assert audit['details']['cognito_failed'] == 0
    assert audit['details']['outcome'] == 'success'


def test_execute_reset_cognito_failures_are_audited_not_fatal(purge_env, cognito_pool):
    cognito_pool.add_user('u1')
    cognito_pool.add_user('u2')
    cognito_pool.add_user('u3')
    reset_service._cognito_client = _CognitoFault(cognito_pool.client, {
        'admin_delete_user': {'u2': 'InternalErrorException'},
        'admin_list_groups_for_user': {'u3': 'InternalErrorException'}})
    result = execute_reset(_body(sets=_MANAGER_SELECTION, delete_cognito=True), ADMIN_USER)

    assert result['cognito']['deleted'] == 1
    assert sorted(f['sub'] for f in result['cognito']['failed']) == ['u2', 'u3']
    assert result['total_deleted'] > 0
    assert cognito_pool.usernames() == ['u2', 'u3']
    audit, = _audit_records('reset_database')
    assert audit['details']['cognito_deleted'] == 1
    assert audit['details']['cognito_failed'] == 2
    assert audit['details']['outcome'] == 'success'


def test_execute_reset_without_option_leaves_cognito_untouched(purge_env, cognito_pool):
    for sub in ['u1', 'u2', 'u3']:
        cognito_pool.add_user(sub)
    result = execute_reset(_body(sets=_MANAGER_SELECTION), ADMIN_USER)
    assert result['cognito']['requested'] is False and result['cognito']['deleted'] == 0
    assert cognito_pool.usernames() == ['u1', 'u2', 'u3']
    audit, = _audit_records('reset_database')
    assert audit['details']['delete_cognito'] is False
    assert audit['details']['cognito_deleted'] == 0


def test_cognito_runs_after_dynamodb(purge_env, cognito_pool):
    """Every managers item is already gone when the first Cognito call happens"""
    cognito_pool.add_user('u2')
    seen = {}
    real = cognito_pool.client

    class Spy(_CognitoFault):
        def __getattr__(self, name):
            if 'remaining' not in seen:
                seen['remaining'] = [k for k in table_state()
                                     if any(_PREDICATES[s](*k) for s in _MANAGER_SELECTION)]
            return super().__getattr__(name)

    reset_service._cognito_client = Spy(real)
    execute_reset(_body(sets=_MANAGER_SELECTION, delete_cognito=True), ADMIN_USER)
    assert seen['remaining'] == []


@pytest.mark.parametrize('fail_set', [s for s in PURGE_ORDER if s in _MANAGER_SELECTION])
def test_cognito_not_attempted_when_dynamodb_fails(purge_env, cognito_pool, fail_set):
    for sub in ['u1', 'u2', 'u3']:
        cognito_pool.add_user(sub)
    client = _CognitoFault(cognito_pool.client)
    reset_service._cognito_client = client
    _install(_DeleteFault(backup_service._get_dynamodb_client(), fail_set))

    with pytest.raises(ResetPartial) as raised:
        execute_reset(_body(sets=_MANAGER_SELECTION, delete_cognito=True), ADMIN_USER)
    assert raised.value.details['cognito'] == 'not_attempted'
    assert client.calls == []
    assert cognito_pool.usernames() == ['u1', 'u2', 'u3']
    backup_service._dynamodb_client = None
    audit, = _audit_records('reset_database')
    assert audit['details']['outcome'] == 'partial'
    assert audit['details']['cognito_deleted'] == 0
    assert audit['details']['cognito_failed'] == 0


# ---------------------------------------------------------------------------
# 6. API adapters (task 2.11)
# ---------------------------------------------------------------------------
_SEED_COGNITO_MAX = _seed_items()[2]


def _reset_event(method='GET', body=None, raw_body=None):
    event = {'httpMethod': method, 'resource': '/admin/reset', 'pathParameters': None}
    if raw_body is not None:
        event['body'] = raw_body
    elif body is not None:
        event['body'] = json.dumps(body)
    return event


def _envelope(response):
    return json.loads(response['body'])


def _assert_error(response, status, code):
    assert response['statusCode'] == status
    payload = _envelope(response)
    assert payload['error']['code'] == code
    assert 'Traceback' not in response['body'] and 'File "' not in response['body']
    return payload['error']


@pytest.mark.parametrize('environment, backup_required', [
    ('prod', True), ('dev', False), ('', False),
], ids=['prod', 'dev', 'unset'])
def test_handle_counts_payload(purge_env, monkeypatch, environment, backup_required):
    if environment:
        monkeypatch.setenv('ENVIRONMENT', environment)
    else:
        monkeypatch.delenv('ENVIRONMENT')
    response = reset_service.handle_counts(_reset_event(), ADMIN_USER)
    assert response['statusCode'] == 200
    data = _envelope(response)['data']
    assert set(data) == {'environment', 'backup_required', 'counts', 'cognito_accounts_max'}
    assert data['environment'] == environment
    assert data['backup_required'] is backup_required
    assert data['counts'] == _EXPECTED_COUNTS
    assert set(data['counts']) == set(SET_IDS)
    assert data['cognito_accounts_max'] == _SEED_COGNITO_MAX


def test_handle_counts_changes_nothing(purge_env):
    before = _full_state()
    reset_service.handle_counts(_reset_event(), ADMIN_USER)
    assert _full_state() == before
    assert _s3_keys() == []


def test_handle_reset_success_envelope(purge_env):
    selection = _SELECTIONS['default']
    response = reset_service.handle_reset(
        _reset_event('POST', _body(sets=selection)), ADMIN_USER)
    assert response['statusCode'] == 200
    data = _envelope(response)['data']
    assert set(data) == {'sets', 'deleted', 'total_deleted', 'cognito', 'pre_reset_backup',
                         'audit_written', 'duration_ms'}
    assert data['sets'] == _ordered(selection)
    assert data['deleted'] == {s: _EXPECTED_COUNTS[s] for s in _ordered(selection)}
    assert data['total_deleted'] == sum(data['deleted'].values())
    assert data['cognito']['requested'] is False
    assert data['pre_reset_backup']['backup_id'].startswith('safety-pre-reset_')
    assert data['audit_written'] is True


def test_handle_reset_without_backup_in_dev(purge_env):
    response = reset_service.handle_reset(
        _reset_event('POST', _body(backup_before=False)), ADMIN_USER)
    assert _envelope(response)['data']['pre_reset_backup'] is None


@pytest.mark.parametrize('event', [
    _reset_event('POST'),
    _reset_event('POST', raw_body=''),
    _reset_event('POST', raw_body='not json'),
    _reset_event('POST', raw_body='[1, 2]'),
    _reset_event('POST', raw_body='"PURGER LA BASE"'),
    _reset_event('POST', raw_body='null'),
    _reset_event('POST', raw_body='{}'),
], ids=['missing', 'empty', 'non-json', 'list', 'string', 'null', 'empty-object'])
def test_handle_reset_bad_body_is_400_without_effect(purge_env, event):
    before = _full_state()
    _assert_error(reset_service.handle_reset(event, ADMIN_USER), 400, 'INVALID_CONFIRMATION')
    assert _full_state() == before
    assert _s3_keys() == []


def test_handle_reset_invalid_selection_details(purge_env):
    before = _full_state()
    error = _assert_error(reset_service.handle_reset(
        _reset_event('POST', _body(sets=['crew'])), ADMIN_USER), 400, 'INVALID_SELECTION')
    assert error['details']['missing'] == ['boats', 'payments']
    assert _full_state() == before


def test_handle_reset_backup_required_in_prod(purge_env, monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'prod')
    before = _full_state()
    _assert_error(reset_service.handle_reset(
        _reset_event('POST', _body(backup_before=False)), ADMIN_USER), 400, 'BACKUP_REQUIRED')
    assert _full_state() == before
    assert _s3_keys() == []


def test_handle_reset_backup_failure_is_500_with_details(purge_env):
    before = _full_state()
    _install(_Faulty(backup_service._get_dynamodb_client(), ['create_backup']))
    response = reset_service.handle_reset(_reset_event('POST', _body()), ADMIN_USER)
    backup_service._dynamodb_client = None
    error = _assert_error(response, 500, 'PRE_RESET_BACKUP_FAILED')
    assert error['details']['failed_artifact'] == 'aws_native'
    assert error['details']['database_modified'] is False
    assert _full_state() == before


def test_handle_reset_partial_failure_is_500_with_details(purge_env):
    _install(_DeleteFault(backup_service._get_dynamodb_client(), 'boats'))
    response = reset_service.handle_reset(_reset_event('POST', _body()), ADMIN_USER)
    backup_service._dynamodb_client = None
    error = _assert_error(response, 500, 'RESET_PARTIAL')
    details = error['details']
    assert details['cognito'] == 'not_attempted'
    assert details['pre_reset_backup_id'].startswith('safety-pre-reset_')
    assert set(details) >= {'stage', 'deleted', 'pre_reset_backup_id', 'cognito'}


# ---------------------------------------------------------------------------
# 7. Handler routing and access control (task 3.2) - Property 12
# ---------------------------------------------------------------------------
HANDLER_ADMIN_ID = 'admin-1'
RESET_RESOURCE = '/admin/reset'
RESET_ROUTES = [('GET', RESET_RESOURCE), ('POST', RESET_RESOURCE)]
NON_ADMIN_CALLERS = [
    pytest.param({'user_id': 'tm-1', 'groups': ('team_managers',)}, 403, 'FORBIDDEN',
                 id='team_manager'),
    pytest.param({'user_id': 'nogroup-1', 'groups': ()}, 403, 'FORBIDDEN', id='no_groups'),
    pytest.param({'user_id': None, 'groups': ()}, 401, 'UNAUTHORIZED', id='unauthenticated'),
]


@pytest.fixture
def call_handler(mock_api_gateway_event, mock_lambda_context):
    """
    Call manage_backups.lambda_handler with an API Gateway proxy event.

    mock_api_gateway_event does not set `resource`, so it is set explicitly here.
    Default caller is an admin; pass user_id=None for no claims.
    """
    from admin.manage_backups import lambda_handler

    def _call(method, resource, body=None, user_id=HANDLER_ADMIN_ID, groups=('admins',)):
        event = mock_api_gateway_event(
            http_method=method,
            path=resource,
            body=json.dumps(body) if body is not None else None,
            user_id=user_id,
            groups=list(groups),
        )
        event['resource'] = resource
        return lambda_handler(event, mock_lambda_context)

    return _call


@pytest.mark.parametrize('method, resource', RESET_ROUTES, ids=lambda v: v)
@pytest.mark.parametrize('caller, status, code', NON_ADMIN_CALLERS)
def test_non_admin_rejected(purge_env, cognito_pool, call_handler, method, resource, caller,
                            status, code):
    """Property 12: 403 (401 without claims) and no S3, native backup, table or Cognito change"""
    cognito_pool.add_user('u1')
    cognito_pool.add_user('u2', admin=True)
    body = _body(sets=SET_IDS, delete_cognito=True, backup_before=False) \
        if method == 'POST' else None
    before = (_full_state(), _s3_keys(), _native_names(), cognito_pool.usernames())

    response = call_handler(method, resource, body=body, **caller)

    assert response['statusCode'] == status
    payload = _envelope(response)
    assert payload['success'] is False
    assert payload['error']['code'] == code
    assert (_full_state(), _s3_keys(), _native_names(), cognito_pool.usernames()) == before
    assert _audit_records('reset_database') == []


def test_handler_routes_reset(purge_env, call_handler):
    response = call_handler('GET', RESET_RESOURCE)
    assert response['statusCode'] == 200
    data = _envelope(response)['data']
    assert data['counts'] == _EXPECTED_COUNTS
    assert data['environment'] == 'dev'
    assert data['backup_required'] is False

    selection = _SELECTIONS['default']
    response = call_handler('POST', RESET_RESOURCE, body=_body(sets=selection))
    assert response['statusCode'] == 200
    data = _envelope(response)['data']
    assert data['sets'] == _ordered(selection)
    assert data['deleted'] == {s: _EXPECTED_COUNTS[s] for s in _ordered(selection)}
    assert data['pre_reset_backup']['backup_id'].startswith('safety-pre-reset_')
    remaining = table_state()
    assert not [k for k in remaining if _PREDICATES['boats'](*k) or _PREDICATES['payments'](*k)]
    for key in _PROTECTED_KEYS:
        assert key in remaining
    audit, = _audit_records('reset_database')
    assert audit['user_id'] == HANDLER_ADMIN_ID


@pytest.mark.parametrize('method', ['PUT', 'DELETE', 'PATCH'])
def test_unknown_method_on_reset_returns_404(purge_env, call_handler, method):
    before = (_full_state(), _s3_keys(), _native_names())
    response = call_handler(method, RESET_RESOURCE, body=_body())
    assert response['statusCode'] == 404
    assert _envelope(response)['error']['code'] == 'NOT_FOUND'
    assert (_full_state(), _s3_keys(), _native_names()) == before


def test_handler_reset_invalid_body_through_handler_is_400(purge_env, call_handler):
    before = _full_state()
    response = call_handler('POST', RESET_RESOURCE, body=_body(confirmation_phrase='nope'))
    assert response['statusCode'] == 400
    assert _envelope(response)['error']['code'] == 'INVALID_CONFIRMATION'
    assert _full_state() == before
    assert _s3_keys() == []


def test_backup_routes_still_routed(purge_env, call_handler):
    response = call_handler('GET', '/admin/backups')
    assert response['statusCode'] == 200
    response = call_handler('GET', '/admin/other')
    assert response['statusCode'] == 404
