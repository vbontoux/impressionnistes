"""
Tests for the database backup & restore feature (functions/shared/backup_service.py)

Sections (extended by later tasks):
  1. Shared fixtures and helpers
  2. Naming (task 1.2)
  3. Typed DynamoDB JSON round trip and envelope (task 1.2)
  4. Restore then undo through backup_service (task 1.2)
  5. Create / list / download / delete / audit (task 1.4)
  6. Restore (task 1.6)
  7. Handler (task 2.2)
  8. Frontend/backend constants alignment (task 5.8)

No Hypothesis: explicit parametrized cases only.
"""
import base64
import json
import os
import re
from datetime import datetime, timedelta, timezone

import boto3
import pytest
from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError
from moto import mock_s3

import backup_service
from backup_service import (
    CATEGORY_MANUAL, CATEGORY_SAFETY, CONFIRMATION_PHRASE, FORMAT_VERSION,
    SOURCE_MARKER, InvalidBackupEnvelope, InvalidBackupId, AUDIT_PK,
)

REGION = 'eu-west-3'
BUCKET_NAME = 'test-backups'
PROD_TABLE_NAME = 'impressionnistes-registration-prod'
NATIVE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_.-]{3,255}$')
ADMIN_USER = {'user_id': 'u1', 'email': 'a@b.c'}

MANUAL_ID = 'manual_2026-11-01T14-30-00Z.json'
SAFETY_OF_MANUAL_ID = (
    'safety-pre-restore_2026-11-02T09-00-00Z_before-restore-of_manual_2026-11-01T14-30-00Z.json')
SAFETY_OF_SAFETY_ID = (
    'safety-pre-restore_2026-11-02T09-05-00Z_before-restore-of_'
    'safety-pre-restore_2026-11-02T09-00-00Z.json')


# ---------------------------------------------------------------------------
# 1. Shared fixtures and helpers
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_backup_clients():
    """Cached boto3 clients must be rebuilt inside each test's moto mock"""
    backup_service._dynamodb_client = None
    backup_service._s3_client = None
    yield
    backup_service._dynamodb_client = None
    backup_service._s3_client = None


@pytest.fixture
def backup_bucket(dynamodb_table):
    """Moto S3 bucket for backups (BACKUP_BUCKET); DynamoDB table comes from dynamodb_table"""
    with mock_s3():
        backup_service._dynamodb_client = None
        backup_service._s3_client = None
        s3 = boto3.client('s3', region_name=REGION)
        s3.create_bucket(Bucket=BUCKET_NAME,
                         CreateBucketConfiguration={'LocationConstraint': REGION})
        os.environ['BACKUP_BUCKET'] = BUCKET_NAME
        try:
            yield BUCKET_NAME
        finally:
            os.environ.pop('BACKUP_BUCKET', None)
            backup_service._dynamodb_client = None
            backup_service._s3_client = None


def clear_table(table):
    """Delete the items seeded by dynamodb_table (exact-count / empty-table assertions)"""
    keys = [{'PK': i['PK'], 'SK': i['SK']}
            for i in table.scan(ConsistentRead=True)['Items']]
    for key in keys:
        table.delete_item(Key=key)


def put_typed_items(items):
    """Put typed (low-level) items, e.g. {'PK': {'S': 'x'}, 'n': {'N': '1'}}"""
    client = boto3.client('dynamodb', region_name=REGION)
    for item in items:
        client.put_item(TableName=os.environ['TABLE_NAME'], Item=item)


def _normalize(attr):
    """Sort set members so comparisons ignore set ordering"""
    (code, value), = attr.items()
    if code in ('SS', 'NS', 'BS'):
        return {code: sorted(value)}
    if code == 'M':
        return {code: {k: _normalize(v) for k, v in value.items()}}
    if code == 'L':
        return {code: [_normalize(v) for v in value]}
    return attr


def items_by_key(items, include_audit=True):
    """Typed items as {(PK, SK): normalized item}"""
    result = {}
    for item in items:
        key = (item['PK']['S'], item['SK']['S'])
        if not include_audit and key[0] == backup_service.AUDIT_PK:
            continue
        result[key] = {k: _normalize(v) for k, v in item.items()}
    return result


def table_state(include_audit=False):
    """Current table content (typed), keyed by (PK, SK)"""
    return items_by_key(backup_service.scan_table(), include_audit=include_audit)


def utc(minutes=0):
    return datetime(2026, 11, 1, 14, 30, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)


# ---------------------------------------------------------------------------
# 2. Naming
# ---------------------------------------------------------------------------
@pytest.mark.parametrize('category, source_id', [
    (CATEGORY_MANUAL, None),
    (CATEGORY_SAFETY, MANUAL_ID),
    (CATEGORY_SAFETY, SAFETY_OF_MANUAL_ID),
])
def test_backup_id_roundtrip(category, source_id):
    """Property 2: id encodes category and time and parses back"""
    moment = datetime(2026, 11, 2, 9, 0, 0, tzinfo=timezone.utc)
    backup_id = backup_service.make_backup_id(category, moment, source_id)

    parsed = backup_service.parse_backup_id(backup_id)
    assert parsed['category'] == category
    assert parsed['timestamp'] == '2026-11-02T09-00-00Z'
    assert parsed['created_at'] == '2026-11-02T09:00:00Z'
    assert backup_id.startswith(f'{category}_2026-11-02T09-00-00Z')
    assert backup_id.endswith('.json')

    if category == CATEGORY_MANUAL:
        assert SOURCE_MARKER not in backup_id
        assert parsed['source_ref'] is None
        assert parsed['source_stem'] is None
    else:
        source = backup_service.parse_backup_id(source_id)
        expected_ref = f"{source['category']}_{source['timestamp']}"
        assert backup_id.endswith(f'{SOURCE_MARKER}{expected_ref}.json')
        assert parsed['source_ref'] == expected_ref
        assert parsed['source_stem'] == expected_ref


@pytest.mark.parametrize('bad_id', [
    '../x.json',
    '../manual_2026-11-01T14-30-00Z.json',
    'a/manual_2026-11-01T14-30-00Z.json',
    '/',
    '',
    'manual_2026-11-01T14-30-00Z.json/',
    'manual_2026-11-01T14-30-00Z.json\n',
    'manual_2026-11-01T14-30-00Z',
    'weekly_2026-11-01T14-30-00Z.json',
    # safety without source
    'safety-pre-restore_2026-11-02T09-00-00Z.json',
    # manual with source
    'manual_2026-11-02T09-00-00Z_before-restore-of_manual_2026-11-01T14-30-00Z.json',
    # nested chain id (source part is itself a safety id with a source)
    ('safety-pre-restore_2026-11-03T09-00-00Z_before-restore-of_'
     'safety-pre-restore_2026-11-02T09-00-00Z_before-restore-of_'
     'manual_2026-11-01T14-30-00Z.json'),
    # bad timestamps
    'manual_2026-13-01T14-30-00Z.json',
    'manual_2026-11-31T14-30-00Z.json',
    'manual_2026-11-01T25-30-00Z.json',
    'manual_2026-11-01T14:30:00Z.json',
    # non-strings
    None,
    123,
    b'manual_2026-11-01T14-30-00Z.json',
    ['manual_2026-11-01T14-30-00Z.json'],
])
def test_backup_id_rejects_invalid(bad_id):
    with pytest.raises(InvalidBackupId):
        backup_service.parse_backup_id(bad_id)


@pytest.mark.parametrize('category, source_id', [
    ('weekly', None),
    (CATEGORY_SAFETY, None),
    (CATEGORY_MANUAL, MANUAL_ID),
    (CATEGORY_SAFETY, '../x.json'),
    (CATEGORY_SAFETY, 'not-a-backup'),
])
def test_make_backup_id_rejects_invalid_combinations(category, source_id):
    with pytest.raises(InvalidBackupId):
        backup_service.make_backup_id(category, utc(), source_id)


def test_make_backup_id_with_fixed_moment_is_deterministic():
    moment = utc()
    first = backup_service.make_backup_id(CATEGORY_MANUAL, moment)
    assert first == backup_service.make_backup_id(CATEGORY_MANUAL, moment)
    assert first == MANUAL_ID

    safety = backup_service.make_backup_id(
        CATEGORY_SAFETY, datetime(2026, 11, 2, 9, 0, 0, tzinfo=timezone.utc), MANUAL_ID)
    assert safety == SAFETY_OF_MANUAL_ID


def test_timestamp_converted_to_utc():
    paris = timezone(timedelta(hours=1))
    moment = datetime(2026, 11, 1, 15, 30, 0, tzinfo=paris)
    assert backup_service.make_backup_id(CATEGORY_MANUAL, moment) == MANUAL_ID


@pytest.mark.parametrize('source_id, expected_ref', [
    (MANUAL_ID, 'manual_2026-11-01T14-30-00Z'),
    (SAFETY_OF_MANUAL_ID, 'safety-pre-restore_2026-11-02T09-00-00Z'),
])
def test_safety_id_uses_bounded_source_reference(source_id, expected_ref):
    """The id embeds {source_category}_{source_timestamp}, never the full source id"""
    moment = datetime(2026, 11, 3, 8, 0, 0, tzinfo=timezone.utc)
    backup_id = backup_service.make_backup_id(CATEGORY_SAFETY, moment, source_id)

    assert backup_id == (
        f'safety-pre-restore_2026-11-03T08-00-00Z{SOURCE_MARKER}{expected_ref}.json')
    if source_id == SAFETY_OF_MANUAL_ID:
        # A manual source's bounded ref (manual_<ts>) is legitimately a substring of its
        # full id, so only a SAFETY source (longer than its ref) must not be embedded.
        assert source_id not in backup_id
    assert backup_id.count(SOURCE_MARKER) == 1


@pytest.mark.parametrize('backup_id', [MANUAL_ID, SAFETY_OF_MANUAL_ID, SAFETY_OF_SAFETY_ID])
def test_parse_backup_id_returns_source_ref_not_source_backup_id(backup_id):
    parsed = backup_service.parse_backup_id(backup_id)
    assert 'source_ref' in parsed
    assert 'source_stem' in parsed
    assert parsed['source_stem'] == parsed['source_ref']
    assert 'source_backup_id' not in parsed


@pytest.mark.parametrize('depth', [1, 2, 3, 4, 5, 6])
def test_restore_undo_repeatedly_keeps_valid_ids(depth):
    """Property 2: restore then undo repeated keeps ids valid and bounded"""
    previous_id = backup_service.make_backup_id(CATEGORY_MANUAL, utc(0))
    chain = [(previous_id, CATEGORY_MANUAL, None)]

    for step in range(1, depth + 1):
        # restore of previous_id takes a safety backup; undo restores that one, etc.
        new_id = backup_service.make_backup_id(CATEGORY_SAFETY, utc(step), previous_id)
        parsed_prev = backup_service.parse_backup_id(previous_id)
        chain.append((new_id, CATEGORY_SAFETY,
                      f"{parsed_prev['category']}_{parsed_prev['timestamp']}"))
        previous_id = new_id

    assert len(chain) == depth + 1
    for index, (backup_id, category, source_ref) in enumerate(chain):
        parsed = backup_service.parse_backup_id(backup_id)
        assert backup_service.BACKUP_ID_PATTERN.match(backup_id)
        assert parsed['category'] == category
        assert parsed['timestamp'] == backup_service.format_timestamp(utc(index))
        assert parsed['source_ref'] == source_ref
        assert len(backup_id) < 150

        native_name = f"{PROD_TABLE_NAME}-{category}_{parsed['timestamp']}"
        assert len(native_name) < 100
        assert NATIVE_NAME_PATTERN.match(native_name)
        assert SOURCE_MARKER not in native_name


# ---------------------------------------------------------------------------
# 3. Typed DynamoDB JSON round trip and envelope
# ---------------------------------------------------------------------------
BINARY = b'\x00\x01\xfe\xff'

SPECIAL_ITEMS = {
    'numbers': {
        'PK': {'S': 'TEAM#t1'}, 'SK': {'S': 'NUM'},
        'decimal': {'N': '12.50'}, 'exponent': {'N': '1E+3'},
        'negative': {'N': '-0.001'}, 'zero': {'N': '0'},
    },
    'string_set': {
        'PK': {'S': 'TEAM#t1'}, 'SK': {'S': 'SS'}, 'tags': {'SS': ['a', 'b', 'c']},
    },
    'number_set': {
        'PK': {'S': 'TEAM#t1'}, 'SK': {'S': 'NS'}, 'nums': {'NS': ['1', '2.5', '-3']},
    },
    'binary_set': {
        'PK': {'S': 'TEAM#t1'}, 'SK': {'S': 'BS'}, 'blobs': {'BS': [BINARY, b'hello']},
    },
    'binary': {
        'PK': {'S': 'TEAM#t1'}, 'SK': {'S': 'B'}, 'blob': {'B': BINARY},
    },
    'nested': {
        'PK': {'S': 'TEAM#t1'}, 'SK': {'S': 'NESTED'},
        'crew': {'L': [
            {'M': {'name': {'S': 'x'}, 'age': {'N': '54'}, 'photo': {'B': b'\xde\xad'}}},
            {'L': [{'N': '1'}, {'NULL': True}, {'BS': [b'a', b'b']}]},
            {'M': {'inner': {'M': {'deep': {'B': BINARY}}}}},
        ]},
    },
    'bool_null': {
        'PK': {'S': 'TEAM#t1'}, 'SK': {'S': 'FLAGS'},
        'yes': {'BOOL': True}, 'no': {'BOOL': False}, 'nothing': {'NULL': True},
    },
    'unicode': {
        'PK': {'S': 'CLUB#é'}, 'SK': {'S': 'NAME'},
        'name': {'S': 'Éléonore 漕艇 🚣 "quotes" \\ \n tab\t'},
    },
}


@pytest.mark.parametrize('name', list(SPECIAL_ITEMS))
def test_special_dynamodb_types_roundtrip(name):
    """Property 1 and 3 (types part): encode -> JSON -> envelope -> decode is exact"""
    item = SPECIAL_ITEMS[name]

    encoded = backup_service.encode_items([item])
    text = json.dumps(encoded, separators=(',', ':'), ensure_ascii=False)
    loaded = json.loads(text)

    backup_id = backup_service.make_backup_id(CATEGORY_MANUAL, utc())
    envelope = backup_service.build_envelope(
        loaded, backup_id, 'admin@example.org', table_name='t', environment='test')
    decoded = backup_service.validate_envelope(json.loads(json.dumps(envelope)))

    assert decoded == [item]


def test_binary_values_are_stored_as_base64_in_json():
    item = SPECIAL_ITEMS['nested']
    encoded = backup_service.encode_items([item])
    text = json.dumps(encoded)

    assert base64.b64encode(BINARY).decode('ascii') in text
    assert base64.b64encode(b'\xde\xad').decode('ascii') in text
    # nothing but str/list/dict/bool/None survives in the encoded form
    assert json.loads(text) == encoded

    binary_item = backup_service.encode_items([SPECIAL_ITEMS['binary']])[0]
    assert binary_item['blob'] == {'B': base64.b64encode(BINARY).decode('ascii')}
    set_item = backup_service.encode_items([SPECIAL_ITEMS['binary_set']])[0]
    assert set_item['blobs'] == {'BS': [base64.b64encode(BINARY).decode('ascii'),
                                        base64.b64encode(b'hello').decode('ascii')]}


def test_encode_items_does_not_alter_originals():
    item = SPECIAL_ITEMS['nested']
    before = json.dumps(item, default=lambda b: b.hex())
    backup_service.encode_items([item])
    assert json.dumps(item, default=lambda b: b.hex()) == before


def test_scan_table_roundtrip_through_moto(dynamodb_table, backup_bucket):
    """Items written with the low-level client come back from scan_table and survive encode/decode"""
    put_typed_items([
        {'PK': {'S': 'TEAM#bin'}, 'SK': {'S': 'B'},
         'blob': {'B': BINARY}, 'nums': {'NS': ['1', '2.5']},
         'blobs': {'BS': [b'a', b'b']}, 'tags': {'SS': ['x', 'y']},
         'nested': {'M': {'raw': {'B': b'\x00\x01'}, 'list': {'L': [{'N': '3'}, {'BOOL': True}]}}},
         'nothing': {'NULL': True}, 'text': {'S': 'Éléonore 漕艇'}},
    ])

    scanned = backup_service.scan_table()
    by_key = {(i['PK']['S'], i['SK']['S']): i for i in scanned}
    ours = by_key[('TEAM#bin', 'B')]

    assert ours['blob']['B'] == BINARY
    assert isinstance(ours['blob']['B'], bytes)
    assert set(ours['nums']['NS']) == {'1', '2.5'}
    assert set(ours['blobs']['BS']) == {b'a', b'b'}
    assert set(ours['tags']['SS']) == {'x', 'y'}
    assert ours['nested']['M']['raw']['B'] == b'\x00\x01'
    assert ours['text']['S'] == 'Éléonore 漕艇'
    # seeded configuration items are included too
    assert ('CONFIG', 'SYSTEM') in by_key

    encoded = backup_service.encode_items(scanned)
    decoded = backup_service.decode_items(json.loads(json.dumps(encoded, ensure_ascii=False)))
    assert decoded == scanned


def test_purge_handles_binary_sets_and_nested_items(dynamodb_table, backup_bucket):
    """Regression: purge must work on items holding B / BS / nested binary sets"""
    clear_table(dynamodb_table)
    items = [SPECIAL_ITEMS['binary_set'], SPECIAL_ITEMS['nested'], SPECIAL_ITEMS['binary']]
    items += [_item(f'TEAM#t{i}', f'BOAT#b{i}', seats={'N': str(i)}) for i in range(3)]
    put_typed_items(items)

    assert backup_service.purge_table() == (len(items), set())
    assert backup_service.scan_table() == []


def _encoded(*keys):
    return [{'PK': {'S': pk}, 'SK': {'S': sk}} for pk, sk in keys]


def _valid_envelope(items=None, backup_id=MANUAL_ID):
    items = items if items is not None else _encoded(('A', '1'), ('A', '2'))
    return backup_service.build_envelope(
        items, backup_id, 'admin@example.org', table_name='t', environment='test')


def test_build_envelope_manual_metadata():
    envelope = _valid_envelope()

    assert envelope['format_version'] == FORMAT_VERSION
    assert len(envelope['items']) == 2
    metadata = envelope['metadata']
    assert metadata['backup_id'] == MANUAL_ID
    assert metadata['category'] == CATEGORY_MANUAL
    assert metadata['created_at'] == '2026-11-01T14:30:00Z'
    assert metadata['created_by'] == 'admin@example.org'
    assert metadata['item_count'] == 2
    assert metadata['table_name'] == 't'
    assert metadata['environment'] == 'test'
    assert 'source_backup_id' not in metadata


def test_build_envelope_manual_ignores_source_backup_id():
    envelope = backup_service.build_envelope(
        [], MANUAL_ID, 'admin', table_name='t', environment='test',
        source_backup_id=SAFETY_OF_MANUAL_ID)
    assert 'source_backup_id' not in envelope['metadata']
    assert envelope['metadata']['item_count'] == 0


def test_build_envelope_safety_keeps_full_real_source_id():
    envelope = backup_service.build_envelope(
        _encoded(('A', '1')), SAFETY_OF_SAFETY_ID, 'admin', table_name='t',
        environment='test', source_backup_id=SAFETY_OF_MANUAL_ID)

    metadata = envelope['metadata']
    assert metadata['category'] == CATEGORY_SAFETY
    assert metadata['source_backup_id'] == SAFETY_OF_MANUAL_ID
    assert metadata['item_count'] == 1


def test_validate_envelope_accepts_valid_and_empty():
    assert len(backup_service.validate_envelope(_valid_envelope())) == 2
    assert backup_service.validate_envelope(_valid_envelope(items=[])) == []


def _mutated(mutate):
    envelope = _valid_envelope()
    mutate(envelope)
    return envelope


@pytest.mark.parametrize('envelope', [
    pytest.param(_mutated(lambda e: e.update(format_version=2)), id='wrong_version'),
    pytest.param(_mutated(lambda e: e.pop('format_version')), id='missing_version'),
    pytest.param(_mutated(lambda e: e.update(items={'A': 1})), id='items_not_list'),
    pytest.param(_mutated(lambda e: e.pop('items')), id='items_missing'),
    pytest.param(_mutated(lambda e: e['items'].append('x')), id='item_not_object'),
    pytest.param(_mutated(lambda e: e['items'][0].pop('PK')), id='missing_pk'),
    pytest.param(_mutated(lambda e: e['items'][0].update(SK={'N': '1'})), id='non_string_sk'),
    pytest.param(_mutated(lambda e: e['items'][0].pop('SK')), id='missing_sk'),
    pytest.param(_mutated(lambda e: e['items'][1].update(SK={'S': '1'})), id='duplicate_key'),
    pytest.param(_mutated(lambda e: e['metadata'].update(item_count=3)), id='count_mismatch'),
    pytest.param(_mutated(lambda e: e['metadata'].pop('item_count')), id='count_missing'),
    pytest.param(_mutated(lambda e: e['metadata'].update(item_count=True)), id='count_bool'),
    pytest.param(_mutated(lambda e: e['metadata'].update(item_count='2')), id='count_string'),
    pytest.param(_mutated(lambda e: e['items'][0].update(blob={'B': 'not base64!'})),
                 id='invalid_base64'),
    pytest.param(_mutated(lambda e: e['items'][0].update(blob={'B': 5})), id='base64_not_string'),
    pytest.param(_mutated(lambda e: e['items'][0].update(blob={'BS': ['@@@']})),
                 id='invalid_base64_in_set'),
    pytest.param(_mutated(lambda e: e['items'][0].update(blob='x')), id='attribute_not_typed'),
    pytest.param(_mutated(lambda e: e.update(metadata='x')), id='metadata_not_object'),
    pytest.param(_mutated(lambda e: e.pop('metadata')), id='metadata_missing'),
    pytest.param([], id='content_list'),
    pytest.param('x', id='content_string'),
    pytest.param(None, id='content_none'),
    pytest.param(42, id='content_number'),
])
def test_validate_envelope_rejects_invalid(envelope):
    with pytest.raises(InvalidBackupEnvelope):
        backup_service.validate_envelope(envelope)


# ---------------------------------------------------------------------------
# 4. Restore then undo through backup_service (uses tasks 1.3 and 1.5)
# ---------------------------------------------------------------------------
@pytest.fixture
def fake_clock(monkeypatch):
    """Distinct UTC moments (one second apart): ids have 1 s resolution"""
    state = {'moment': utc(0)}

    def _now():
        state['moment'] = state['moment'] + timedelta(seconds=1)
        return state['moment']

    monkeypatch.setattr(backup_service, '_utc_now', _now)
    return _now


def _item(pk, sk, **attrs):
    return {'PK': {'S': pk}, 'SK': {'S': sk}, **attrs}


def test_restore_then_undo_returns_original_items(dynamodb_table, backup_bucket, fake_clock):
    clear_table(dynamodb_table)
    original = [
        _item('TEAM#t1', 'BOAT#b1', price={'N': '12.50'}, blob={'B': BINARY},
              tags={'SS': ['a', 'b']}),
        _item('CLUB', 'c1', name={'S': 'Éléonore'}),
    ]
    changed = [
        _item('TEAM#t1', 'BOAT#b1', price={'N': '99'}),
        _item('RACE', 'r1', name={'S': 'new'}),
        _item('RACE', 'r2', name={'S': 'new2'}),
    ]
    put_typed_items(original)
    original_state = table_state()

    manual = backup_service.create_backup(CATEGORY_MANUAL, ADMIN_USER)
    manual_id = manual['backup_id']
    assert manual['item_count'] == 2

    clear_table(dynamodb_table)
    put_typed_items(changed)
    changed_state = table_state()

    # Restore the manual backup: table returns to the original items
    first = backup_service.restore_backup(manual_id, CONFIRMATION_PHRASE, ADMIN_USER)
    assert table_state() == original_state
    assert first['purged_count'] == 3
    assert first['restored_count'] == 2

    safety_id = first['safety_backup']['backup_id']
    safety = backup_service.parse_backup_id(safety_id)
    manual_parsed = backup_service.parse_backup_id(manual_id)
    assert safety['category'] == CATEGORY_SAFETY
    assert safety['source_ref'] == f"{CATEGORY_MANUAL}_{manual_parsed['timestamp']}"
    assert safety_id.endswith(f"{SOURCE_MARKER}{safety['source_ref']}.json")

    # The full real source id is kept in the envelope metadata
    safety_envelope = backup_service.read_backup(safety_id)
    assert safety_envelope['metadata']['source_backup_id'] == manual_id

    # Undo: restore the safety backup; the pre-restore items are back
    second = backup_service.restore_backup(safety_id, CONFIRMATION_PHRASE, ADMIN_USER)
    assert table_state() == changed_state

    undo_id = second['safety_backup']['backup_id']
    undo = backup_service.parse_backup_id(undo_id)
    assert undo['category'] == CATEGORY_SAFETY
    assert undo['source_ref'] == f"{CATEGORY_SAFETY}_{safety['timestamp']}"
    assert len({manual_id, safety_id, undo_id}) == 3
    for backup_id in (manual_id, safety_id, undo_id):
        assert len(backup_id) < 150
        parsed = backup_service.parse_backup_id(backup_id)
        native = f"{PROD_TABLE_NAME}-{parsed['category']}_{parsed['timestamp']}"
        assert NATIVE_NAME_PATTERN.match(native)


# ---------------------------------------------------------------------------
# 5. Create / list / download / delete / audit
# ---------------------------------------------------------------------------
class FaultyClient:
    """Thin wrapper around a real boto3 client: only the named methods raise ClientError"""

    def __init__(self, real, failing):
        self._real = real
        self._failing = set(failing)

    def __getattr__(self, name):
        if name in self._failing:
            def fail(*args, **kwargs):
                raise ClientError(
                    {'Error': {'Code': 'InternalFailure', 'Message': 'injected failure'}}, name)
            return fail
        return getattr(self._real, name)


def inject_dynamodb_faults(*methods):
    backup_service._dynamodb_client = FaultyClient(
        backup_service._get_dynamodb_client(), methods)


def inject_s3_faults(*methods):
    backup_service._s3_client = FaultyClient(backup_service._get_s3_client(), methods)


def s3_client():
    return boto3.client('s3', region_name=REGION)


def bucket_keys():
    return [o['Key'] for o in s3_client().list_objects_v2(Bucket=BUCKET_NAME).get('Contents', [])]


def native_backups():
    client = boto3.client('dynamodb', region_name=REGION)
    return client.list_backups(TableName=os.environ['TABLE_NAME'])['BackupSummaries']


def batch_put_typed_items(items):
    """Fast load of typed items through batch_write_item (chunks of 25)"""
    client = boto3.client('dynamodb', region_name=REGION)
    for start in range(0, len(items), 25):
        chunk = items[start:start + 25]
        response = client.batch_write_item(RequestItems={
            os.environ['TABLE_NAME']: [{'PutRequest': {'Item': i}} for i in chunk]})
        assert not response.get('UnprocessedItems')


def audit_records():
    """AUDIT#DATABASE_BACKUP items as plain dicts, oldest first"""
    deserializer = TypeDeserializer()
    records = [
        {k: deserializer.deserialize(v) for k, v in item.items()}
        for item in backup_service.scan_table()
        if item['PK']['S'] == backup_service.AUDIT_PK
    ]
    return sorted(records, key=lambda r: r['SK'])


def response_body(response):
    return json.loads(response['body'])


def api_event(backup_id=None, method='GET', resource='/admin/backups'):
    return {
        'httpMethod': method,
        'resource': resource,
        'pathParameters': {'backup_id': backup_id} if backup_id is not None else None,
    }


BULK_ITEMS = [_item(f'TEAM#t{i}', f'BOAT#b{i}', seats={'N': str(i)}) for i in range(1250)]

CAPTURE_CASES = [
    pytest.param([], id='empty_table'),
    pytest.param([_item('USER#u1', 'PROFILE', email={'S': 'x@y.z'})], id='one_item'),
    pytest.param(BULK_ITEMS, id='1250_items'),
    pytest.param([_item('USER#u1', 'PROFILE', email={'S': 'x@y.z'})], id='USER'),
    pytest.param([_item('CONFIG', 'SYSTEM', open={'BOOL': True})], id='CONFIG'),
    pytest.param([_item('RACE', 'r1', name={'S': 'Semi'})], id='RACE'),
    pytest.param([_item('CLUB', 'c1', name={'S': 'RCPM'})], id='CLUB'),
    pytest.param([_item('TEAM#t1', 'BOAT#b1', price={'N': '12.50'})], id='TEAM_BOAT'),
    pytest.param([_item('TEAM#t1', 'CREW_MEMBER#m1', blob={'B': BINARY})], id='TEAM_CREW_MEMBER'),
    pytest.param([_item('TEAM#t1', 'PAYMENT#p1', amount={'N': '30'})], id='TEAM_PAYMENT'),
    pytest.param([_item('TEMP_ACCESS#x', '2026-11-01', code={'S': 'abc'})], id='TEMP_ACCESS'),
    pytest.param([_item('AUDIT#SOMETHING', '2026-11-01T00:00:00.000000Z#u1')], id='AUDIT'),
]


@pytest.mark.parametrize('items', CAPTURE_CASES)
def test_create_backup_captures_items(dynamodb_table, backup_bucket, items):
    """Property 1: the backup holds every table item faithfully (S3 object, envelope, native backup)"""
    clear_table(dynamodb_table)
    batch_put_typed_items(items)
    expected = items_by_key(backup_service.scan_table())
    assert len(expected) == len(items)

    result = backup_service.create_backup(CATEGORY_MANUAL, ADMIN_USER)

    backup_id = result['backup_id']
    parsed = backup_service.parse_backup_id(backup_id)
    assert backup_id in bucket_keys()
    assert result['category'] == CATEGORY_MANUAL
    assert result['item_count'] == len(items)
    assert result['source_backup_id'] is None
    assert result['created_at'] == parsed['created_at']

    # S3 object: content type, ASCII metadata, size
    head = s3_client().head_object(Bucket=BUCKET_NAME, Key=backup_id)
    assert head['ContentType'] == 'application/json'
    assert head['Metadata'] == {
        'category': CATEGORY_MANUAL,
        'created-at': parsed['created_at'],
        'created-by': 'a@b.c',
        'item-count': str(len(items)),
    }
    for value in head['Metadata'].values():
        value.encode('ascii')
    assert result['size_bytes'] == head['ContentLength']

    # Envelope: decoded items equal the table items keyed by (PK, SK)
    body = s3_client().get_object(Bucket=BUCKET_NAME, Key=backup_id)['Body'].read()
    assert len(body) == result['size_bytes']
    envelope = json.loads(body)
    assert envelope['format_version'] == FORMAT_VERSION
    assert envelope['metadata']['item_count'] == len(items) == len(envelope['items'])
    assert envelope['metadata']['backup_id'] == backup_id
    assert 'source_backup_id' not in envelope['metadata']
    assert items_by_key(backup_service.decode_items(envelope['items'])) == expected

    # Native backup
    table_name = os.environ['TABLE_NAME']
    native = result['native_backup']
    assert native['name'] == f"{table_name}-{CATEGORY_MANUAL}_{parsed['timestamp']}"
    assert NATIVE_NAME_PATTERN.match(native['name'])
    assert native['arn'] and native['status']
    summaries = native_backups()
    assert [s['BackupName'] for s in summaries] == [native['name']]
    assert summaries[0]['BackupArn'] == native['arn']
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    described = dynamodb.describe_backup(BackupArn=native['arn'])['BackupDescription']
    assert described['BackupDetails']['BackupName'] == native['name']


@pytest.mark.parametrize('user, expected', [
    ({'user_id': 'u1', 'email': 'a@b.c'}, 'a@b.c'),
    ({'user_id': 'u1'}, 'u1'),
    ({'user_id': 'u1', 'email': ''}, 'u1'),
    ({}, 'unknown'),
    (None, 'unknown'),
])
def test_create_backup_created_by(dynamodb_table, backup_bucket, user, expected):
    result = backup_service.create_backup(CATEGORY_MANUAL, user)
    head = s3_client().head_object(Bucket=BUCKET_NAME, Key=result['backup_id'])
    assert head['Metadata']['created-by'] == expected
    envelope = json.loads(
        s3_client().get_object(Bucket=BUCKET_NAME, Key=result['backup_id'])['Body'].read())
    assert envelope['metadata']['created_by'] == expected


def test_create_backup_non_ascii_user_is_ascii_in_metadata(dynamodb_table, backup_bucket):
    user = {'user_id': 'u1', 'email': 'éléonore@b.c'}
    result = backup_service.create_backup(CATEGORY_MANUAL, user)
    head = s3_client().head_object(Bucket=BUCKET_NAME, Key=result['backup_id'])
    head['Metadata']['created-by'].encode('ascii')
    envelope = json.loads(
        s3_client().get_object(Bucket=BUCKET_NAME, Key=result['backup_id'])['Body'].read())
    assert envelope['metadata']['created_by'] == 'éléonore@b.c'


def test_create_safety_backup_stores_full_source_id(dynamodb_table, backup_bucket, fake_clock):
    """The full real source id is in S3 metadata, envelope metadata and the return value"""
    manual = backup_service.create_backup(CATEGORY_MANUAL, ADMIN_USER)
    safety = backup_service.create_backup(
        CATEGORY_SAFETY, ADMIN_USER, source_id=manual['backup_id'])

    safety_id = safety['backup_id']
    parsed = backup_service.parse_backup_id(safety_id)
    assert safety['category'] == CATEGORY_SAFETY
    assert safety['source_backup_id'] == manual['backup_id']
    manual_parsed = backup_service.parse_backup_id(manual['backup_id'])
    assert parsed['source_ref'] == f"{CATEGORY_MANUAL}_{manual_parsed['timestamp']}"

    head = s3_client().head_object(Bucket=BUCKET_NAME, Key=safety_id)
    assert head['Metadata']['source-backup-id'] == manual['backup_id']
    assert head['Metadata']['category'] == CATEGORY_SAFETY
    envelope = json.loads(
        s3_client().get_object(Bucket=BUCKET_NAME, Key=safety_id)['Body'].read())
    assert envelope['metadata']['source_backup_id'] == manual['backup_id']

    table_name = os.environ['TABLE_NAME']
    assert safety['native_backup']['name'] == (
        f"{table_name}-{CATEGORY_SAFETY}_{parsed['timestamp']}")
    assert NATIVE_NAME_PATTERN.match(safety['native_backup']['name'])


def test_create_backup_s3_failure(dynamodb_table, backup_bucket):
    """Failing put_object: JSON_BACKUP_FAILED, no native backup, nothing in the bucket"""
    inject_s3_faults('put_object')

    with pytest.raises(backup_service.JsonBackupFailed) as caught:
        backup_service.create_backup(CATEGORY_MANUAL, ADMIN_USER)

    assert caught.value.code == 'JSON_BACKUP_FAILED'
    assert caught.value.details == {'failed_artifact': 'json'}
    assert native_backups() == []
    assert bucket_keys() == []


def test_create_backup_scan_failure(dynamodb_table, backup_bucket):
    """Failing scan: JSON_BACKUP_FAILED, no native backup, nothing in the bucket"""
    inject_dynamodb_faults('scan')

    with pytest.raises(backup_service.JsonBackupFailed) as caught:
        backup_service.create_backup(CATEGORY_MANUAL, ADMIN_USER)

    assert caught.value.code == 'JSON_BACKUP_FAILED'
    assert caught.value.details['failed_artifact'] == 'json'
    assert native_backups() == []
    assert bucket_keys() == []


def test_create_backup_native_failure(dynamodb_table, backup_bucket):
    """Failing native backup: NATIVE_BACKUP_FAILED (502); the JSON object remains"""
    inject_dynamodb_faults('create_backup')

    with pytest.raises(backup_service.NativeBackupFailed) as caught:
        backup_service.create_backup(CATEGORY_MANUAL, ADMIN_USER)

    error = caught.value
    assert error.code == 'NATIVE_BACKUP_FAILED'
    assert error.status == 502
    assert error.details['failed_artifact'] == 'aws_native'
    kept = bucket_keys()
    assert kept == [error.details['backup_id']]
    assert backup_service.read_backup(kept[0])['metadata']['item_count'] >= 0
    assert native_backups() == []


def test_list_backups_empty_bucket(dynamodb_table, backup_bucket):
    assert backup_service.list_backups() == []


def _create_three(fake_clock):
    """manual, safety (of the first manual), manual: three distinct ids, oldest first"""
    first = backup_service.create_backup(CATEGORY_MANUAL, ADMIN_USER)
    safety = backup_service.create_backup(
        CATEGORY_SAFETY, {'user_id': 'u2', 'email': 'c@d.e'}, source_id=first['backup_id'])
    last = backup_service.create_backup(CATEGORY_MANUAL, ADMIN_USER)
    assert len({first['backup_id'], safety['backup_id'], last['backup_id']}) == 3
    return first, safety, last


def test_list_backups_rows_newest_first(dynamodb_table, backup_bucket, fake_clock):
    """Property 11: list reflects the bucket, with metadata and key-derived fields"""
    clear_table(dynamodb_table)
    put_typed_items([_item('CLUB', 'c1'), _item('CLUB', 'c2')])
    first, safety, last = _create_three(fake_clock)

    rows = backup_service.list_backups()

    assert [r['backup_id'] for r in rows] == [
        last['backup_id'], safety['backup_id'], first['backup_id']]
    by_id = {r['backup_id']: r for r in rows}
    for created in (first, safety, last):
        row = by_id[created['backup_id']]
        assert set(row) == {'backup_id', 'category', 'created_at', 'item_count',
                            'size_bytes', 'created_by', 'source_backup_id', 'source_ref'}
        assert row['category'] == created['category']
        assert row['created_at'] == created['created_at']
        assert row['item_count'] == 2
        assert row['size_bytes'] == created['size_bytes']
    assert by_id[first['backup_id']]['created_by'] == 'a@b.c'
    assert by_id[safety['backup_id']]['created_by'] == 'c@d.e'

    # Manual: no source. Safety: full source id from metadata, bounded ref from the key
    for manual in (first, last):
        assert by_id[manual['backup_id']]['source_backup_id'] is None
        assert by_id[manual['backup_id']]['source_ref'] is None
    safety_row = by_id[safety['backup_id']]
    assert safety_row['source_backup_id'] == first['backup_id']
    first_parsed = backup_service.parse_backup_id(first['backup_id'])
    assert safety_row['source_ref'] == f"{CATEGORY_MANUAL}_{first_parsed['timestamp']}"


def test_list_backups_skips_invalid_keys_and_tolerates_missing_metadata(
        dynamodb_table, backup_bucket, fake_clock):
    first, _, _ = _create_three(fake_clock)
    s3 = s3_client()
    for key in ('notes.txt', 'manual_bad.json', 'other/' + MANUAL_ID,
                'manual_2026-11-01T14-30-00Z.json.bak'):
        s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=b'x')
    hand_made = 'manual_2030-01-01T00-00-00Z.json'
    s3.put_object(Bucket=BUCKET_NAME, Key=hand_made, Body=b'{}')

    rows = backup_service.list_backups()

    ids = [r['backup_id'] for r in rows]
    assert len(ids) == 4
    assert ids[0] == hand_made
    assert first['backup_id'] in ids
    row = rows[0]
    assert row['item_count'] is None
    assert row['created_by'] is None
    assert row['source_backup_id'] is None
    assert row['category'] == CATEGORY_MANUAL
    assert row['created_at'] == '2030-01-01T00:00:00Z'
    assert row['size_bytes'] == 2


def test_read_backup_returns_stored_envelope(dynamodb_table, backup_bucket):
    clear_table(dynamodb_table)
    put_typed_items([_item('TEAM#t1', 'BOAT#b1', blob={'B': BINARY}, price={'N': '1.50'})])
    result = backup_service.create_backup(CATEGORY_MANUAL, ADMIN_USER)

    stored = json.loads(
        s3_client().get_object(Bucket=BUCKET_NAME, Key=result['backup_id'])['Body'].read())

    assert backup_service.read_backup(result['backup_id']) == stored


def test_delete_backup_removes_only_that_entry(dynamodb_table, backup_bucket, fake_clock):
    first, safety, last = _create_three(fake_clock)
    natives_before = sorted(s['BackupName'] for s in native_backups())
    assert len(natives_before) == 3

    assert backup_service.delete_backup(safety['backup_id']) is None

    assert sorted(bucket_keys()) == sorted([first['backup_id'], last['backup_id']])
    assert [r['backup_id'] for r in backup_service.list_backups()] == [
        last['backup_id'], first['backup_id']]
    assert sorted(s['BackupName'] for s in native_backups()) == natives_before


MISSING_ID = 'manual_2031-01-01T00-00-00Z.json'


def test_read_and_delete_missing_backup_raise_not_found(dynamodb_table, backup_bucket):
    for action in (backup_service.read_backup, backup_service.delete_backup):
        with pytest.raises(backup_service.BackupNotFound) as caught:
            action(MISSING_ID)
        assert caught.value.code == 'BACKUP_NOT_FOUND'
        assert caught.value.status == 404


@pytest.mark.parametrize('bad_id', ['../x.json', 'x', '', 'manual_2026-11-01T14-30-00Z', None])
def test_read_and_delete_invalid_id_raise_invalid_backup_id(dynamodb_table, backup_bucket, bad_id):
    for action in (backup_service.read_backup, backup_service.delete_backup):
        with pytest.raises(InvalidBackupId):
            action(bad_id)


@pytest.mark.parametrize('content', [
    pytest.param(b'not json', id='not_json'),
    pytest.param(b'\xff\xfe\x00', id='not_utf8'),
    pytest.param(json.dumps(_mutated(lambda e: e.update(format_version=2))).encode(),
                 id='wrong_version'),
    pytest.param(json.dumps(_mutated(lambda e: e['metadata'].update(item_count=99))).encode(),
                 id='count_mismatch'),
    pytest.param(b'[]', id='not_an_object'),
])
def test_read_corrupted_backup_raises_invalid(dynamodb_table, backup_bucket, content):
    s3_client().put_object(Bucket=BUCKET_NAME, Key=MANUAL_ID, Body=content)

    with pytest.raises(backup_service.BackupInvalid) as caught:
        backup_service.read_backup(MANUAL_ID)

    assert caught.value.code == 'BACKUP_INVALID'
    assert caught.value.status == 422


# ---- API adapters ----------------------------------------------------------
def test_handle_create_returns_201_contract_and_audits(dynamodb_table, backup_bucket):
    response = backup_service.handle_create(
        api_event(method='POST'), ADMIN_USER)

    assert response['statusCode'] == 201
    data = response_body(response)['data']
    assert set(data) == {'backup_id', 'category', 'item_count', 'size_bytes',
                         'created_at', 'source_backup_id', 'native_backup'}
    assert data['category'] == CATEGORY_MANUAL
    assert data['source_backup_id'] is None
    assert set(data['native_backup']) == {'name', 'arn', 'status'}
    assert data['backup_id'] in bucket_keys()
    assert len(audit_records()) == 1


def test_handle_list_returns_backups(dynamodb_table, backup_bucket, fake_clock):
    empty = backup_service.handle_list(api_event(), ADMIN_USER)
    assert empty['statusCode'] == 200
    assert response_body(empty)['data'] == {'backups': []}

    first, safety, last = _create_three(fake_clock)
    response = backup_service.handle_list(api_event(), ADMIN_USER)

    assert response['statusCode'] == 200
    backups = response_body(response)['data']['backups']
    assert [b['backup_id'] for b in backups] == [
        last['backup_id'], safety['backup_id'], first['backup_id']]


def test_handle_download_returns_content(dynamodb_table, backup_bucket):
    created = backup_service.create_backup(CATEGORY_MANUAL, ADMIN_USER)
    stored = json.loads(
        s3_client().get_object(Bucket=BUCKET_NAME, Key=created['backup_id'])['Body'].read())

    response = backup_service.handle_download(
        api_event(created['backup_id'], resource='/admin/backups/{backup_id}/download'),
        ADMIN_USER)

    assert response['statusCode'] == 200
    data = response_body(response)['data']
    assert data == {'backup_id': created['backup_id'],
                    'filename': created['backup_id'], 'content': stored}


def test_handle_delete_removes_and_audits(dynamodb_table, backup_bucket):
    created = backup_service.create_backup(CATEGORY_MANUAL, ADMIN_USER)

    response = backup_service.handle_delete(
        api_event(created['backup_id'], method='DELETE', resource='/admin/backups/{backup_id}'),
        ADMIN_USER)

    assert response['statusCode'] == 200
    assert response_body(response)['data'] == {'backup_id': created['backup_id'], 'deleted': True}
    assert bucket_keys() == []
    assert [r['action'] for r in audit_records()] == ['delete_backup']


@pytest.mark.parametrize('handler', ['handle_download', 'handle_delete'])
@pytest.mark.parametrize('backup_id, status, code', [
    (MISSING_ID, 404, 'BACKUP_NOT_FOUND'),
    ('../x.json', 400, 'INVALID_BACKUP_ID'),
    ('x', 400, 'INVALID_BACKUP_ID'),
    (None, 400, 'INVALID_BACKUP_ID'),
])
def test_handle_download_and_delete_errors(dynamodb_table, backup_bucket,
                                           handler, backup_id, status, code):
    """Missing id -> 404, invalid id -> 400; pathParameters None must not crash; no audit"""
    response = getattr(backup_service, handler)(api_event(backup_id), ADMIN_USER)

    assert response['statusCode'] == status
    assert response_body(response)['error']['code'] == code
    assert audit_records() == []


def test_handle_download_corrupted_backup_returns_422(dynamodb_table, backup_bucket):
    s3_client().put_object(Bucket=BUCKET_NAME, Key=MANUAL_ID, Body=b'not json')

    response = backup_service.handle_download(api_event(MANUAL_ID), ADMIN_USER)

    assert response['statusCode'] == 422
    assert response_body(response)['error']['code'] == 'BACKUP_INVALID'


@pytest.mark.parametrize('faulty, kind, status, code', [
    ('put_object', 's3', 500, 'JSON_BACKUP_FAILED'),
    ('create_backup', 'dynamodb', 502, 'NATIVE_BACKUP_FAILED'),
])
def test_handle_create_failures_map_to_error_responses(dynamodb_table, backup_bucket,
                                                       faulty, kind, status, code):
    (inject_s3_faults if kind == 's3' else inject_dynamodb_faults)(faulty)

    response = backup_service.handle_create(api_event(method='POST'), ADMIN_USER)

    assert response['statusCode'] == status
    error = response_body(response)['error']
    assert error['code'] == code
    assert error['details']['failed_artifact'] == ('json' if kind == 's3' else 'aws_native')
    assert audit_records() == []


# ---- Audit -----------------------------------------------------------------
AUDIT_SK_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z#u1$')


def test_audit_records(dynamodb_table, backup_bucket, fake_clock):
    """Property 12: create and delete are audited, one record per action"""
    clear_table(dynamodb_table)
    put_typed_items([_item('CLUB', 'c1'), _item('CLUB', 'c2'), _item('CLUB', 'c3')])

    created = response_body(backup_service.handle_create(
        api_event(method='POST'), ADMIN_USER))['data']

    records = audit_records()
    assert len(records) == 1
    record = records[0]
    assert record['PK'] == 'AUDIT#DATABASE_BACKUP'
    assert AUDIT_SK_PATTERN.match(record['SK'])
    assert record['SK'].split('#')[0] == record['timestamp']
    assert record['action'] == 'create_backup'
    assert record['user_id'] == 'u1'
    assert record['user_email'] == 'a@b.c'
    assert record['details']['backup_id'] == created['backup_id']
    assert record['details']['item_count'] == 3
    assert 'source_backup_id' not in record['details']

    backup_service.handle_delete(
        api_event(created['backup_id'], method='DELETE'), ADMIN_USER)

    records = audit_records()
    assert [r['action'] for r in records] == ['create_backup', 'delete_backup']
    deleted = records[1]
    assert deleted['PK'] == 'AUDIT#DATABASE_BACKUP'
    assert AUDIT_SK_PATTERN.match(deleted['SK'])
    assert deleted['user_id'] == 'u1'
    assert deleted['user_email'] == 'a@b.c'
    assert deleted['timestamp'] == deleted['SK'].split('#')[0]
    assert deleted['details']['backup_id'] == created['backup_id']
    assert records[0]['SK'] < deleted['SK']


def test_write_audit_returns_true_when_written(dynamodb_table, backup_bucket):
    assert backup_service.write_audit('create_backup', ADMIN_USER, {'backup_id': MANUAL_ID}) is True
    assert len(audit_records()) == 1


def test_write_audit_never_raises_and_handle_create_still_succeeds(dynamodb_table, backup_bucket):
    inject_dynamodb_faults('put_item')

    assert backup_service.write_audit('create_backup', ADMIN_USER, {'backup_id': MANUAL_ID}) is False

    response = backup_service.handle_create(api_event(method='POST'), ADMIN_USER)
    assert response['statusCode'] == 201
    assert response_body(response)['data']['backup_id'] in bucket_keys()
    backup_service._dynamodb_client = None  # drop the faulty wrapper
    assert audit_records() == []


# ---------------------------------------------------------------------------
# 6. Restore (task 1.6)
# ---------------------------------------------------------------------------
from contextlib import contextmanager  # noqa: E402
from unittest import mock  # noqa: E402

RESTORE_RESOURCE = '/admin/backups/{backup_id}/restore'
STEP_NAMES = ['safety_backup', 'purge', 'write', 'verify']
NO_BODY = object()


def generic_items(count, tag, prefix='TEAM#t'):
    return [_item(f'{prefix}{i}', f'BOAT#b{i}', tag={'S': tag}, seats={'N': str(i)})
            for i in range(count)]


def special_items(*names):
    return [SPECIAL_ITEMS[n] for n in names]


def seed(table, source_items, current_items):
    """
    Create a manual backup holding source_items, then leave current_items in the table.

    Returns (source_id, source_state, current_state); states are keyed by (PK, SK)
    and include audit records (none exist yet).
    """
    clear_table(table)
    batch_put_typed_items(source_items)
    source_state = table_state(include_audit=True)
    source_id = backup_service.create_backup(CATEGORY_MANUAL, ADMIN_USER)['backup_id']
    clear_table(table)
    batch_put_typed_items(current_items)
    return source_id, source_state, table_state(include_audit=True)


def safety_keys():
    return [k for k in bucket_keys() if k.startswith(CATEGORY_SAFETY)]


def safety_native_names():
    return [s['BackupName'] for s in native_backups() if CATEGORY_SAFETY in s['BackupName']]


def assert_no_safety_backup():
    assert safety_keys() == []
    assert safety_native_names() == []


@contextmanager
def forbid_mutation():
    """Fail the test if the table would be modified (purge / write) or a backup created"""
    with mock.patch.object(backup_service, 'purge_table') as purge, \
            mock.patch.object(backup_service, 'write_items') as write, \
            mock.patch.object(backup_service, 'create_backup') as create:
        yield
        purge.assert_not_called()
        write.assert_not_called()
        create.assert_not_called()


# ---- Property 3 and 4: replace the table, accurate counts -------------------
REPLACE_CASES = [
    pytest.param(special_items('numbers', 'string_set', 'binary'), generic_items(6, 'cur'),
                 id='source_smaller'),
    pytest.param(generic_items(5, 'src'), generic_items(5, 'cur'), id='source_equal_same_keys'),
    pytest.param(special_items(*SPECIAL_ITEMS) + generic_items(30, 'src'),
                 generic_items(3, 'cur'), id='source_larger_with_special_types'),
    pytest.param(generic_items(4, 'src', 'SRC#'), generic_items(4, 'cur', 'CUR#'),
                 id='disjoint_keys'),
    pytest.param([], generic_items(4, 'cur'), id='empty_source'),
    pytest.param(generic_items(3, 'src') + special_items('binary_set', 'nested'), [],
                 id='empty_current_table'),
]


@pytest.mark.parametrize('source_items, current_items', REPLACE_CASES)
def test_restore_replaces_table(dynamodb_table, backup_bucket, fake_clock,
                                source_items, current_items):
    """Properties 3 and 4: final table == source exactly, counts and steps are accurate"""
    source_id, source_state, current_state = seed(dynamodb_table, source_items, current_items)
    assert len(source_state) == len(source_items)

    result = backup_service.restore_backup(source_id, CONFIRMATION_PHRASE, ADMIN_USER)

    assert table_state() == source_state
    assert len(table_state()) == len(source_items)
    assert result['source_backup_id'] == source_id
    assert result['purged_count'] == len(current_state)
    assert result['restored_count'] == len(source_items)
    assert result['preserved_audit_count'] == 0  # no backup audit record before the restore
    assert [s['name'] for s in result['steps']] == STEP_NAMES
    assert [s['status'] for s in result['steps']] == ['ok'] * 4
    assert [s['count'] for s in result['steps']] == [
        len(current_state), len(current_state), len(source_items), len(source_items)]
    assert result['audit_written'] is True
    assert isinstance(result['duration_ms'], int) and result['duration_ms'] >= 0
    assert set(result) == {'source_backup_id', 'purged_count', 'preserved_audit_count',
                           'restored_count', 'safety_backup', 'steps', 'audit_written',
                           'duration_ms'}


# ---- Property 5: safety backup precedes the purge ---------------------------
def test_restore_creates_safety_backup_first(dynamodb_table, backup_bucket, fake_clock,
                                             monkeypatch):
    source_id, source_state, current_state = seed(
        dynamodb_table, generic_items(3, 'src') + special_items('binary', 'string_set'),
        generic_items(5, 'cur') + special_items('numbers'))
    table_name = os.environ['TABLE_NAME']

    observed = {}
    real_purge = backup_service.purge_table

    def spy_purge(preserve_pk=None):
        if not observed:
            observed['keys'] = bucket_keys()
            observed['natives'] = {s['BackupName']: s['BackupArn'] for s in native_backups()}
            observed['table'] = table_state(include_audit=True)
            observed['preserve_pk'] = preserve_pk
        return real_purge(preserve_pk=preserve_pk)

    monkeypatch.setattr(backup_service, 'purge_table', spy_purge)

    result = backup_service.restore_backup(source_id, CONFIRMATION_PHRASE, ADMIN_USER)

    safety_id = result['safety_backup']['backup_id']
    parsed = backup_service.parse_backup_id(safety_id)
    source_parsed = backup_service.parse_backup_id(source_id)
    native_name = f"{table_name}-safety-pre-restore_{parsed['timestamp']}"

    # At the first purge call the safety artifacts already existed, table untouched
    assert safety_id in observed['keys']
    assert native_name in observed['natives']
    assert observed['table'] == current_state
    assert observed['preserve_pk'] == AUDIT_PK

    # Safety object content == pre-restore table
    envelope = backup_service.read_backup(safety_id)
    assert items_by_key(backup_service.decode_items(envelope['items'])) == current_state

    # Key carries the bounded source_ref; full real id is in metadata/envelope/audit
    source_ref = f"{CATEGORY_MANUAL}_{source_parsed['timestamp']}"
    assert safety_id.endswith(f'{SOURCE_MARKER}{source_ref}.json')
    assert parsed['category'] == CATEGORY_SAFETY
    head = s3_client().head_object(Bucket=BUCKET_NAME, Key=safety_id)
    assert head['Metadata']['source-backup-id'] == source_id
    assert head['Metadata']['category'] == CATEGORY_SAFETY
    assert envelope['metadata']['source_backup_id'] == source_id

    # Native backup name and result shape
    summaries = {s['BackupName']: s['BackupArn'] for s in native_backups()}
    assert result['safety_backup'] == {
        'backup_id': safety_id,
        'native_backup': {'name': native_name, 'arn': summaries[native_name]},
    }
    assert NATIVE_NAME_PATTERN.match(native_name)

    # Audit record carries the full ids and counts
    records = audit_records()
    assert len(records) == 1
    details = records[0]['details']
    assert records[0]['action'] == 'restore_backup'
    assert details['source_backup_id'] == source_id
    assert details['safety_backup_id'] == safety_id
    assert details['purged_count'] == len(current_state)
    assert details['restored_count'] == len(source_state)
    assert table_state() == source_state


# ---- Property 6: failed safety backup aborts without purge ------------------
@pytest.mark.parametrize('artifact, inject', [
    pytest.param('json', lambda: inject_s3_faults('put_object'), id='json_write_fails'),
    pytest.param('aws_native', lambda: inject_dynamodb_faults('create_backup'),
                 id='native_backup_fails'),
])
def test_restore_aborts_when_safety_fails(dynamodb_table, backup_bucket, fake_clock,
                                          artifact, inject):
    source_id, _, current_state = seed(
        dynamodb_table, generic_items(3, 'src'), generic_items(5, 'cur'))
    inject()  # after the source exists

    with mock.patch.object(backup_service, 'purge_table') as purge, \
            mock.patch.object(backup_service, 'write_items') as write:
        with pytest.raises(backup_service.SafetyBackupFailed) as caught:
            backup_service.restore_backup(source_id, CONFIRMATION_PHRASE, ADMIN_USER)

    error = caught.value
    assert error.code == 'SAFETY_BACKUP_FAILED'
    assert error.status == 500
    assert error.details['failed_artifact'] == artifact
    assert error.details['source_backup_id'] == source_id
    purge.assert_not_called()
    write.assert_not_called()
    assert table_state(include_audit=True) == current_state
    assert audit_records() == []


# ---- Property 7: invalid source leaves the table untouched ------------------
def _corrupt(mutate):
    return json.dumps(_mutated(mutate)).encode()


INVALID_SOURCES = [
    pytest.param(None, backup_service.BackupNotFound, 404, id='missing_object'),
    pytest.param(b'not json', backup_service.BackupInvalid, 422, id='bad_json'),
    pytest.param(b'\xff\xfe\x00', backup_service.BackupInvalid, 422, id='not_utf8'),
    pytest.param(_corrupt(lambda e: e.update(format_version=2)),
                 backup_service.BackupInvalid, 422, id='wrong_format_version'),
    pytest.param(_corrupt(lambda e: e['items'][0].pop('PK')),
                 backup_service.BackupInvalid, 422, id='item_without_pk'),
    pytest.param(_corrupt(lambda e: e['items'][1].update(SK={'S': '1'})),
                 backup_service.BackupInvalid, 422, id='duplicate_keys'),
    pytest.param(_corrupt(lambda e: e['metadata'].update(item_count=99)),
                 backup_service.BackupInvalid, 422, id='item_count_mismatch'),
]


@pytest.mark.parametrize('content, error_class, status', INVALID_SOURCES)
def test_restore_rejects_invalid_source(dynamodb_table, backup_bucket, fake_clock,
                                        content, error_class, status):
    clear_table(dynamodb_table)
    put_typed_items(generic_items(4, 'cur'))
    before = table_state(include_audit=True)
    if content is not None:
        s3_client().put_object(Bucket=BUCKET_NAME, Key=MANUAL_ID, Body=content)

    with forbid_mutation():
        with pytest.raises(error_class) as caught:
            backup_service.restore_backup(MANUAL_ID, CONFIRMATION_PHRASE, ADMIN_USER)

    assert caught.value.status == status
    assert table_state(include_audit=True) == before
    assert_no_safety_backup()
    assert native_backups() == []
    assert bucket_keys() == ([] if content is None else [MANUAL_ID])
    assert audit_records() == []


# ---- Property 8: wrong confirmation phrase ----------------------------------
@pytest.mark.parametrize('phrase', [
    pytest.param('', id='empty'),
    pytest.param(CONFIRMATION_PHRASE.lower(), id='lowercase'),
    pytest.param(CONFIRMATION_PHRASE + ' ', id='trailing_space'),
    pytest.param(' ' + CONFIRMATION_PHRASE, id='leading_space'),
    pytest.param(None, id='none'),
    pytest.param('RESTAURER', id='partial'),
    pytest.param('RESTORE THE DATABASE', id='other_language'),
    pytest.param(123, id='not_a_string'),
])
def test_restore_rejects_wrong_phrase(dynamodb_table, backup_bucket, fake_clock, phrase):
    source_id, _, current_state = seed(
        dynamodb_table, generic_items(3, 'src'), generic_items(5, 'cur'))
    keys_before = bucket_keys()

    with forbid_mutation():
        with pytest.raises(backup_service.InvalidConfirmation) as caught:
            backup_service.restore_backup(source_id, phrase, ADMIN_USER)

    assert caught.value.code == 'INVALID_CONFIRMATION'
    assert caught.value.status == 400
    assert table_state(include_audit=True) == current_state
    assert bucket_keys() == keys_before == [source_id]
    assert_no_safety_backup()
    assert audit_records() == []


@pytest.mark.parametrize('phrase', [CONFIRMATION_PHRASE, '', 'wrong', None])
@pytest.mark.parametrize('bad_id', ['../x.json', 'x', '', None, 'manual_2026-11-01T14-30-00Z'])
def test_restore_invalid_backup_id_is_checked_first(dynamodb_table, backup_bucket,
                                                    bad_id, phrase):
    with forbid_mutation():
        with pytest.raises(InvalidBackupId):
            backup_service.restore_backup(bad_id, phrase, ADMIN_USER)
    assert bucket_keys() == []


# ---- Property 9: partial failure reports the safety backup ------------------
def _fail(*args, **kwargs):
    raise RuntimeError('injected failure')


PARTIAL_CASES = [
    pytest.param('purge', 'purge_table', {'side_effect': _fail},
                 ['ok', 'failed', 'skipped', 'skipped'], id='purge_fails'),
    pytest.param('write', 'write_items', {'side_effect': _fail},
                 ['ok', 'ok', 'failed', 'skipped'], id='write_fails'),
    pytest.param('verify', 'count_items', {'side_effect': _fail},
                 ['ok', 'ok', 'ok', 'failed'], id='verify_raises'),
    pytest.param('verify', 'count_items', {'return_value': 1},
                 ['ok', 'ok', 'ok', 'failed'], id='verify_count_mismatch'),
]


@pytest.mark.parametrize('stage, target, patch_args, statuses', PARTIAL_CASES)
def test_restore_partial_failure(dynamodb_table, backup_bucket, fake_clock,
                                 stage, target, patch_args, statuses):
    source_items = generic_items(4, 'src') + special_items('binary', 'number_set')
    current_items = generic_items(7, 'cur') + special_items('nested')
    source_id, source_state, original_state = seed(dynamodb_table, source_items, current_items)
    table_name = os.environ['TABLE_NAME']

    with mock.patch.object(backup_service, target, **patch_args):
        with pytest.raises(backup_service.RestorePartial) as caught:
            backup_service.restore_backup(source_id, CONFIRMATION_PHRASE, ADMIN_USER)

    error = caught.value
    details = error.details
    assert error.code == 'RESTORE_PARTIAL'
    assert error.status == 500
    assert details['stage'] == stage
    assert details['source_backup_id'] == source_id
    assert details['safety_backup_id'] in bucket_keys()
    safety_parsed = backup_service.parse_backup_id(details['safety_backup_id'])
    native_name = f"{table_name}-safety-pre-restore_{safety_parsed['timestamp']}"
    native = {s['BackupName']: s['BackupArn'] for s in native_backups()}
    assert details['safety_native_backup'] == {'name': native_name, 'arn': native[native_name]}

    purge_done = statuses[1] == 'ok'
    write_done = statuses[2] == 'ok'
    assert details['purged_count'] == (len(original_state) if purge_done else 0)
    assert details['written_count'] == (len(source_items) if write_done else 0)
    assert [s['name'] for s in details['steps']] == STEP_NAMES
    assert [s['status'] for s in details['steps']] == statuses
    steps = {s['name']: s for s in details['steps']}
    assert steps['safety_backup']['count'] == len(original_state)
    if purge_done:
        assert steps['purge']['count'] == len(original_state)
    if write_done:
        assert steps['write']['count'] == len(source_items)

    # No restore audit record on failure
    assert audit_records() == []

    # Recovery: restoring the safety backup brings back the original item set
    restored = backup_service.restore_backup(
        details['safety_backup_id'], CONFIRMATION_PHRASE, ADMIN_USER)
    assert table_state() == original_state
    assert restored['restored_count'] == len(original_state)
    assert [r['action'] for r in audit_records()] == ['restore_backup']


# ---- Batch write: retries, backoff, chunking --------------------------------
class BatchClient:
    """
    Wrapper recording batch_write_item chunk sizes. The first `fail_first` calls
    (all calls when fail_first is None) write nothing and return the whole
    request as UnprocessedItems.
    """

    def __init__(self, real, fail_first=0):
        self._real = real
        self.fail_first = fail_first
        self.sizes = []

    def batch_write_item(self, RequestItems, **kwargs):
        self.sizes.append(sum(len(v) for v in RequestItems.values()))
        if self.fail_first is None or len(self.sizes) <= self.fail_first:
            return {'UnprocessedItems': RequestItems}
        return self._real.batch_write_item(RequestItems=RequestItems, **kwargs)

    def __getattr__(self, name):
        return getattr(self._real, name)


def install_batch_client(fail_first=0):
    client = BatchClient(backup_service._get_dynamodb_client(), fail_first)
    backup_service._dynamodb_client = client
    return client


@pytest.fixture
def sleeps(monkeypatch):
    recorded = []
    monkeypatch.setattr(backup_service, '_sleep', recorded.append)
    return recorded


@pytest.mark.parametrize('failures, expected_delays', [
    (1, [0.05]),
    (3, [0.05, 0.1, 0.2]),
    (7, [0.05, 0.1, 0.2, 0.4, 0.8, 1.0, 1.0]),
])
def test_batch_write_retries_unprocessed_items(dynamodb_table, backup_bucket, sleeps,
                                               failures, expected_delays):
    clear_table(dynamodb_table)
    items = generic_items(3, 'src')
    client = install_batch_client(fail_first=failures)

    assert backup_service.write_items(items) == 3

    assert client.sizes == [3] * (failures + 1)
    assert sleeps == pytest.approx(expected_delays)
    assert table_state() == items_by_key(items)


def test_batch_write_gives_up_after_eight_attempts(dynamodb_table, backup_bucket, sleeps):
    clear_table(dynamodb_table)
    client = install_batch_client(fail_first=None)

    with pytest.raises(backup_service.BatchWriteError) as caught:
        backup_service.write_items(generic_items(3, 'src'))

    assert caught.value.code == 'BATCH_WRITE_FAILED'
    assert caught.value.details == {'unprocessed_count': 3}
    assert len(client.sizes) == 8
    assert sleeps == pytest.approx([0.05, 0.1, 0.2, 0.4, 0.8, 1.0, 1.0])
    assert table_state() == {}


def test_batch_write_failure_only_retries_current_chunk(dynamodb_table, backup_bucket, sleeps):
    clear_table(dynamodb_table)
    client = install_batch_client(fail_first=None)

    with pytest.raises(backup_service.BatchWriteError) as caught:
        backup_service.write_items(generic_items(30, 'src'))

    assert caught.value.details == {'unprocessed_count': 25}
    assert client.sizes == [25] * 8


def test_write_and_purge_use_chunks_of_25(dynamodb_table, backup_bucket, sleeps):
    clear_table(dynamodb_table)
    items = generic_items(60, 'src')
    client = install_batch_client()

    assert backup_service.write_items(items) == 60
    assert client.sizes == [25, 25, 10]
    assert len(table_state()) == 60

    client.sizes.clear()
    assert backup_service.purge_table() == (60, set())
    assert client.sizes == [25, 25, 10]
    assert table_state() == {}
    assert sleeps == []


def test_purge_preserve_pk_keeps_audit_items_and_returns_their_keys(dynamodb_table,
                                                                     backup_bucket, sleeps):
    clear_table(dynamodb_table)
    audit_sks = [f'2026-01-0{i}T00:00:00.000000Z#u1' for i in range(1, 4)]
    put_typed_items(
        generic_items(30, 'cur') + special_items('binary_set', 'nested')
        + [_item(AUDIT_PK, sk, action={'S': 'create_backup'}) for sk in audit_sks]
        + [_item('AUDIT#PERMISSION_DENIAL', 'PD#1', tag={'S': 'x'})])
    client = install_batch_client()

    purged, preserved = backup_service.purge_table(preserve_pk=AUDIT_PK)

    # 30 + 2 + the other AUDIT# partition are deleted; only AUDIT_PK is kept
    assert purged == 33
    assert preserved == {(AUDIT_PK, sk) for sk in audit_sks}
    assert client.sizes == [25, 8]
    assert set(table_state(include_audit=True)) == preserved


def test_write_and_purge_empty_make_no_calls(dynamodb_table, backup_bucket):
    clear_table(dynamodb_table)
    client = install_batch_client()

    assert backup_service.write_items([]) == 0
    assert backup_service.purge_table() == (0, set())
    assert backup_service.purge_table(preserve_pk=AUDIT_PK) == (0, set())
    assert client.sizes == []


class PagedScanClient:
    """Fake client returning scan pages linked by LastEvaluatedKey"""

    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def scan(self, **kwargs):
        self.calls.append(dict(kwargs))  # params dict is reused by the caller
        index = len(self.calls) - 1
        page = dict(self.pages[index])
        if index < len(self.pages) - 1:
            page['LastEvaluatedKey'] = {'PK': {'S': f'page{index}'}, 'SK': {'S': 'k'}}
        return page


def test_scan_table_follows_pagination():
    pages = [{'Items': [_item('A', '1'), _item('A', '2')]},
             {'Items': [_item('B', '1')]},
             {'Items': []},
             {'Items': [_item('C', '1')]}]
    client = PagedScanClient(pages)

    items = backup_service.scan_table('some-table', client=client)

    assert [(i['PK']['S'], i['SK']['S']) for i in items] == [
        ('A', '1'), ('A', '2'), ('B', '1'), ('C', '1')]
    assert len(client.calls) == 4
    assert 'ExclusiveStartKey' not in client.calls[0]
    assert [c['ExclusiveStartKey']['PK']['S'] for c in client.calls[1:]] == [
        'page0', 'page1', 'page2']
    assert all(c['ConsistentRead'] is True and c['TableName'] == 'some-table'
               for c in client.calls)


def test_count_items_sums_all_pages(dynamodb_table):
    client = PagedScanClient([{'Count': 10}, {'Count': 20}, {'Count': 0}, {'Count': 5}])
    backup_service._dynamodb_client = client

    assert backup_service.count_items() == 35

    assert len(client.calls) == 4
    assert all(c['Select'] == 'COUNT' and c['ConsistentRead'] is True for c in client.calls)
    assert 'ExclusiveStartKey' not in client.calls[0]
    assert all('ExclusiveStartKey' in c for c in client.calls[1:])


# ---- Property 12: restore is audited ----------------------------------------
def test_audit_records_restore(dynamodb_table, backup_bucket, fake_clock):
    """One restore_backup audit item, present in the table after the rewrite"""
    source_id, source_state, _ = seed(
        dynamodb_table, generic_items(3, 'src'), generic_items(5, 'cur'))
    assert audit_records() == []

    result = backup_service.restore_backup(source_id, CONFIRMATION_PHRASE, ADMIN_USER)

    assert result['audit_written'] is True
    records = audit_records()
    assert len(records) == 1
    record = records[0]
    assert record['PK'] == 'AUDIT#DATABASE_BACKUP'
    assert AUDIT_SK_PATTERN.match(record['SK'])
    assert record['action'] == 'restore_backup'
    assert record['user_id'] == 'u1'
    assert record['user_email'] == 'a@b.c'
    assert record['details'] == {
        'source_backup_id': source_id,
        'safety_backup_id': result['safety_backup']['backup_id'],
        'purged_count': 5 + 0,
        'restored_count': 3,
    }
    # The data is the source plus the audit record written after the rewrite
    assert table_state() == source_state
    assert len(table_state(include_audit=True)) == len(source_state) + 1


def test_restore_succeeds_when_audit_fails(dynamodb_table, backup_bucket, fake_clock):
    source_id, source_state, _ = seed(
        dynamodb_table, generic_items(3, 'src'), generic_items(5, 'cur'))

    with mock.patch.object(backup_service, 'write_audit', return_value=False) as audit:
        result = backup_service.restore_backup(source_id, CONFIRMATION_PHRASE, ADMIN_USER)

    audit.assert_called_once()
    assert audit.call_args.args[0] == 'restore_backup'
    assert result['audit_written'] is False
    assert result['restored_count'] == 3
    assert table_state(include_audit=True) == source_state
    assert audit_records() == []


# ---- handle_restore adapter -------------------------------------------------
def restore_event(backup_id, body=NO_BODY):
    event = api_event(backup_id, method='POST', resource=RESTORE_RESOURCE)
    if body is not NO_BODY:
        event['body'] = body
    return event


def phrase_body(phrase=CONFIRMATION_PHRASE):
    return json.dumps({'confirmation_phrase': phrase})


def error_of(response):
    return response_body(response)['error']


def test_handle_restore_success(dynamodb_table, backup_bucket, fake_clock):
    source_id, source_state, current_state = seed(
        dynamodb_table, generic_items(3, 'src'), generic_items(5, 'cur'))

    response = backup_service.handle_restore(
        restore_event(source_id, phrase_body()), ADMIN_USER)

    assert response['statusCode'] == 200
    data = response_body(response)['data']
    assert set(data) == {'source_backup_id', 'purged_count', 'preserved_audit_count',
                         'restored_count', 'safety_backup', 'steps', 'audit_written',
                         'duration_ms'}
    assert data['source_backup_id'] == source_id
    assert data['purged_count'] == len(current_state)
    assert data['preserved_audit_count'] == 0
    assert data['restored_count'] == 3
    assert data['safety_backup']['backup_id'] in bucket_keys()
    assert set(data['safety_backup']['native_backup']) == {'name', 'arn'}
    assert [s['status'] for s in data['steps']] == ['ok'] * 4
    assert data['audit_written'] is True
    assert table_state() == source_state


@pytest.mark.parametrize('body', [
    pytest.param(NO_BODY, id='missing_body'),
    pytest.param(None, id='null_body'),
    pytest.param('not json', id='invalid_json'),
    pytest.param('[]', id='json_list'),
    pytest.param('{}', id='missing_phrase'),
    pytest.param(json.dumps({'confirmation_phrase': ''}), id='empty_phrase'),
    pytest.param(json.dumps({'confirmation_phrase': 'restaurer la base'}), id='wrong_case'),
    pytest.param(json.dumps({'confirmation_phrase': CONFIRMATION_PHRASE + ' '}),
                 id='trailing_space'),
    pytest.param(json.dumps({'confirmation_phrase': 123}), id='not_a_string'),
])
def test_handle_restore_invalid_confirmation_returns_400(dynamodb_table, backup_bucket,
                                                         fake_clock, body):
    source_id, _, current_state = seed(
        dynamodb_table, generic_items(3, 'src'), generic_items(5, 'cur'))

    with forbid_mutation():
        response = backup_service.handle_restore(restore_event(source_id, body), ADMIN_USER)

    assert response['statusCode'] == 400
    assert error_of(response)['code'] == 'INVALID_CONFIRMATION'
    assert table_state(include_audit=True) == current_state
    assert_no_safety_backup()


@pytest.mark.parametrize('body', [NO_BODY, 'not json', '{}', phrase_body()])
@pytest.mark.parametrize('backup_id', ['../x.json', 'x', None])
def test_handle_restore_invalid_id_returns_400(dynamodb_table, backup_bucket, backup_id, body):
    with forbid_mutation():
        response = backup_service.handle_restore(restore_event(backup_id, body), ADMIN_USER)

    assert response['statusCode'] == 400
    assert error_of(response)['code'] == 'INVALID_BACKUP_ID'


def test_handle_restore_missing_source_returns_404(dynamodb_table, backup_bucket):
    with forbid_mutation():
        response = backup_service.handle_restore(
            restore_event(MISSING_ID, phrase_body()), ADMIN_USER)

    assert response['statusCode'] == 404
    assert error_of(response)['code'] == 'BACKUP_NOT_FOUND'


def test_handle_restore_corrupted_source_returns_422(dynamodb_table, backup_bucket):
    clear_table(dynamodb_table)
    put_typed_items(generic_items(2, 'cur'))
    before = table_state(include_audit=True)
    s3_client().put_object(Bucket=BUCKET_NAME, Key=MANUAL_ID, Body=b'not json')

    with forbid_mutation():
        response = backup_service.handle_restore(
            restore_event(MANUAL_ID, phrase_body()), ADMIN_USER)

    assert response['statusCode'] == 422
    assert error_of(response)['code'] == 'BACKUP_INVALID'
    assert table_state(include_audit=True) == before
    assert_no_safety_backup()


def test_handle_restore_safety_failure_returns_500(dynamodb_table, backup_bucket, fake_clock):
    source_id, _, current_state = seed(
        dynamodb_table, generic_items(3, 'src'), generic_items(5, 'cur'))
    inject_s3_faults('put_object')

    response = backup_service.handle_restore(restore_event(source_id, phrase_body()), ADMIN_USER)

    assert response['statusCode'] == 500
    error = error_of(response)
    assert error['code'] == 'SAFETY_BACKUP_FAILED'
    assert error['details']['failed_artifact'] == 'json'
    assert error['details']['source_backup_id'] == source_id
    assert table_state(include_audit=True) == current_state


def test_handle_restore_partial_returns_500_with_safety_details(dynamodb_table, backup_bucket,
                                                                fake_clock):
    source_id, _, current_state = seed(
        dynamodb_table, generic_items(3, 'src'), generic_items(5, 'cur'))

    with mock.patch.object(backup_service, 'write_items', side_effect=_fail):
        response = backup_service.handle_restore(
            restore_event(source_id, phrase_body()), ADMIN_USER)

    assert response['statusCode'] == 500
    error = error_of(response)
    assert error['code'] == 'RESTORE_PARTIAL'
    details = error['details']
    assert details['safety_backup_id'] in bucket_keys()
    assert set(details['safety_native_backup']) == {'name', 'arn'}
    assert details['source_backup_id'] == source_id
    assert details['stage'] == 'write'
    assert details['purged_count'] == len(current_state)
    assert details['written_count'] == 0
    assert details['preserved_audit_count'] == 0
    assert [s['status'] for s in details['steps']] == ['ok', 'ok', 'failed', 'skipped']
    assert audit_records() == []


# ---- Property 3, 4, 12: backup audit records survive restore and undo -------
AUDIT_A = '2026-01-01T00:00:00.000000Z#u0'
AUDIT_B = '2026-01-02T00:00:00.000000Z#u0'


def backup_audit_item(sk, action):
    return _item(AUDIT_PK, sk, action={'S': action}, user_id={'S': 'u0'})


def audit_actions():
    """{SK: action} of the AUDIT#DATABASE_BACKUP partition"""
    return {r['SK']: r['action'] for r in audit_records()}


def other_audit_item(sk):
    return _item('AUDIT#PERMISSION_DENIAL', sk, tag={'S': sk})


PRESERVE_CASES = [
    pytest.param({}, {AUDIT_B: 'create_backup'}, id='no_audit_in_backup'),
    pytest.param({AUDIT_A: 'create_backup'}, {AUDIT_B: 'create_backup'},
                 id='backup_audit_merged_disjoint'),
    pytest.param({AUDIT_A: 'create_backup'},
                 {AUDIT_A: 'delete_backup', AUDIT_B: 'create_backup'},
                 id='same_key_in_both_source_wins'),
    pytest.param({AUDIT_A: 'create_backup'}, {}, id='no_audit_in_table'),
]


@pytest.mark.parametrize('backup_audit, table_audit', PRESERVE_CASES)
def test_restore_preserves_backup_audit_records(dynamodb_table, backup_bucket, fake_clock,
                                                backup_audit, table_audit):
    """Audit records written after the source backup survive the restore and the undo"""
    clear_table(dynamodb_table)
    batch_put_typed_items(
        generic_items(3, 'src') + [other_audit_item('in-backup')]
        + [backup_audit_item(sk, a) for sk, a in backup_audit.items()])
    source_id = backup_service.create_backup(CATEGORY_MANUAL, ADMIN_USER)['backup_id']
    source_data = table_state()  # includes AUDIT#PERMISSION_DENIAL, excludes backup audit
    assert len(source_data) == 4

    # After the backup: data changes, another partition changes, audit records are written
    clear_table(dynamodb_table)
    current_items = generic_items(4, 'cur') + [other_audit_item('added-later')]
    batch_put_typed_items(current_items + [backup_audit_item(sk, a)
                                           for sk, a in table_audit.items()])
    current_data = table_state()
    assert len(current_data) == 5

    # ---- restore ----
    result = backup_service.restore_backup(source_id, CONFIRMATION_PHRASE, ADMIN_USER)

    assert table_state() == source_data  # added-later is gone, in-backup is back
    assert result['purged_count'] == len(current_data)  # preserved records not counted
    assert result['preserved_audit_count'] == len(table_audit)
    assert result['restored_count'] == len(source_data) + len(backup_audit)
    assert [s['status'] for s in result['steps']] == ['ok'] * 4  # verify == union
    union = {**table_audit, **backup_audit}  # same key: the source wins
    assert result['steps'][3]['count'] == len(source_data) + len(union)
    assert result['audit_written'] is True

    after_restore = audit_actions()
    restore_sks = set(after_restore) - set(union)
    assert len(restore_sks) == 1
    assert after_restore.pop(restore_sks.pop()) == 'restore_backup'
    assert after_restore == union
    assert len(audit_records()) == len(union) + 1  # no duplicates

    # ---- undo: restore the safety backup of the first restore ----
    safety_id = result['safety_backup']['backup_id']
    full_history = audit_actions()
    undo = backup_service.restore_backup(safety_id, CONFIRMATION_PHRASE, ADMIN_USER)

    assert table_state() == current_data  # data back to before the first restore
    assert undo['purged_count'] == len(source_data)
    assert undo['preserved_audit_count'] == len(full_history)  # incl. the first restore record
    assert [s['status'] for s in undo['steps']] == ['ok'] * 4

    # The safety backup holds table_audit: it wins on shared keys, others are kept
    expected = {**full_history, **table_audit}
    after_undo = audit_actions()
    undo_sks = set(after_undo) - set(expected)
    assert len(undo_sks) == 1
    assert after_undo.pop(undo_sks.pop()) == 'restore_backup'
    assert after_undo == expected
    # History keeps the records of both restores
    assert list(full_history.values()).count('restore_backup') == 1
    assert list(audit_actions().values()).count('restore_backup') == 2
    assert len(audit_records()) == len(expected) + 1


@pytest.mark.parametrize('stage, target, patch_args', [
    pytest.param('write', 'write_items', {'side_effect': _fail}, id='write_fails'),
    pytest.param('verify', 'count_items', {'return_value': 1}, id='verify_mismatch'),
])
def test_restore_partial_keeps_preserved_audit_records(dynamodb_table, backup_bucket,
                                                       fake_clock, stage, target, patch_args):
    clear_table(dynamodb_table)
    batch_put_typed_items(generic_items(3, 'src') + [backup_audit_item(AUDIT_A, 'create_backup')])
    source_id = backup_service.create_backup(CATEGORY_MANUAL, ADMIN_USER)['backup_id']
    clear_table(dynamodb_table)
    batch_put_typed_items(generic_items(4, 'cur') + [
        backup_audit_item(AUDIT_B, 'create_backup'), backup_audit_item(
            '2026-01-03T00:00:00.000000Z#u0', 'delete_backup')])
    current_data = table_state()

    with mock.patch.object(backup_service, target, **patch_args):
        with pytest.raises(backup_service.RestorePartial) as caught:
            backup_service.restore_backup(source_id, CONFIRMATION_PHRASE, ADMIN_USER)

    details = caught.value.details
    assert details['stage'] == stage
    assert details['preserved_audit_count'] == 2
    assert details['purged_count'] == len(current_data)  # excludes preserved records
    # Preserved audit records are still in the table; no restore record on failure
    kept = audit_actions()
    assert {AUDIT_B, '2026-01-03T00:00:00.000000Z#u0'} <= set(kept)
    assert 'restore_backup' not in kept.values()
    if stage == 'verify':  # the source rewrite happened: its audit record is merged
        assert kept[AUDIT_A] == 'create_backup'
    else:
        assert AUDIT_A not in kept


# ---------------------------------------------------------------------------
# 7. Handler (task 2.2): functions/admin/manage_backups.py
# ---------------------------------------------------------------------------
ROUTE_CREATE = ('POST', '/admin/backups')
ROUTE_LIST = ('GET', '/admin/backups')
ROUTE_DOWNLOAD = ('GET', '/admin/backups/{backup_id}/download')
ROUTE_DELETE = ('DELETE', '/admin/backups/{backup_id}')
ROUTE_RESTORE = ('POST', '/admin/backups/{backup_id}/restore')
ALL_ROUTES = [ROUTE_CREATE, ROUTE_LIST, ROUTE_DOWNLOAD, ROUTE_DELETE, ROUTE_RESTORE]
ROUTES_WITH_BACKUP_ID = {ROUTE_DOWNLOAD, ROUTE_DELETE, ROUTE_RESTORE}

HANDLER_ADMIN_ID = 'admin-1'
HANDLER_ADMIN_EMAIL = f'{HANDLER_ADMIN_ID}@test.com'  # mock_api_gateway_event builds the email


@pytest.fixture
def call_handler(mock_api_gateway_event, mock_lambda_context):
    """
    Call manage_backups.lambda_handler with an API Gateway proxy event.

    mock_api_gateway_event does not set `resource`, so it is set explicitly here.
    Default caller is an admin (groups=['admins']); pass user_id=None for no claims.
    """
    from admin.manage_backups import lambda_handler

    def _call(route, backup_id=None, body=None, user_id=HANDLER_ADMIN_ID, groups=('admins',)):
        method, resource = route
        event = mock_api_gateway_event(
            http_method=method,
            path=resource.replace('{backup_id}', backup_id or 'x'),
            body=body,
            path_parameters={'backup_id': backup_id} if backup_id is not None else None,
            user_id=user_id,
            groups=list(groups),
        )
        event['resource'] = resource
        return lambda_handler(event, mock_lambda_context)

    return _call


def call_raw(event, mock_lambda_context):
    from admin.manage_backups import lambda_handler
    return lambda_handler(event, mock_lambda_context)


def side_effect_snapshot():
    """Everything a backup route could change: S3 objects, native backups, table, audit"""
    objects = {key: s3_client().get_object(Bucket=BUCKET_NAME, Key=key)['Body'].read()
               for key in bucket_keys()}
    return {
        'objects': objects,
        'natives': sorted((s['BackupName'], s['BackupArn']) for s in native_backups()),
        'table': table_state(include_audit=True),
        'audit': audit_records(),
    }


def prepare_target_backup(table):
    """
    Create a manual backup with the service, then change the table, so that a
    delete or a restore would visibly have an effect. Returns the backup id.
    """
    clear_table(table)
    put_typed_items(generic_items(3, 'src'))
    backup_id = backup_service.create_backup(CATEGORY_MANUAL, ADMIN_USER)['backup_id']
    clear_table(table)
    put_typed_items(generic_items(5, 'cur'))
    return backup_id


# ---- Routes table -----------------------------------------------------------
def test_routes_table_matches_design():
    from admin import manage_backups

    assert manage_backups.ROUTES == {
        ROUTE_CREATE: backup_service.handle_create,
        ROUTE_LIST: backup_service.handle_list,
        ROUTE_DOWNLOAD: backup_service.handle_download,
        ROUTE_DELETE: backup_service.handle_delete,
        ROUTE_RESTORE: backup_service.handle_restore,
    }
    assert len(manage_backups.ROUTES) == 5


# ---- Property 10: non-admin requests are rejected without effect ------------
NON_ADMIN_CALLERS = [
    pytest.param({'user_id': 'tm-1', 'groups': ('team_managers',)}, 403, 'FORBIDDEN',
                 id='team_manager'),
    pytest.param({'user_id': 'nogroup-1', 'groups': ()}, 403, 'FORBIDDEN', id='no_groups'),
    pytest.param({'user_id': 'devops-1', 'groups': ('devops',)}, 403, 'FORBIDDEN', id='devops'),
    pytest.param({'user_id': None, 'groups': ()}, 401, 'UNAUTHORIZED', id='unauthenticated'),
]


@pytest.mark.parametrize('route', ALL_ROUTES, ids=lambda r: f'{r[0]} {r[1]}')
@pytest.mark.parametrize('caller, status, code', NON_ADMIN_CALLERS)
def test_non_admin_rejected(dynamodb_table, backup_bucket, fake_clock, call_handler,
                            route, caller, status, code):
    """Property 10: 403 (401 without claims) and no S3, native backup, table or audit change"""
    backup_id = prepare_target_backup(dynamodb_table)
    before = side_effect_snapshot()
    assert before['audit'] == []

    response = call_handler(
        route,
        backup_id=backup_id if route in ROUTES_WITH_BACKUP_ID else None,
        body=phrase_body() if route == ROUTE_RESTORE else None,
        **caller)

    assert response['statusCode'] == status
    body = response_body(response)
    assert body['success'] is False
    assert body['error']['code'] == code
    assert side_effect_snapshot() == before
    assert bucket_keys() == [backup_id]
    assert len(native_backups()) == 1
    assert audit_records() == []


# ---- Restore body validation through the handler ----------------------------
@pytest.mark.parametrize('body', [
    pytest.param(None, id='body_none'),
    pytest.param('', id='body_empty'),
    pytest.param('not json', id='body_not_json'),
    pytest.param('[]', id='body_json_list'),
    pytest.param('{}', id='body_no_phrase'),
    pytest.param(phrase_body('wrong phrase'), id='wrong_phrase'),
    pytest.param(phrase_body(CONFIRMATION_PHRASE.lower()), id='lowercase_phrase'),
])
def test_handler_restore_invalid_body_returns_400(dynamodb_table, backup_bucket, fake_clock,
                                                  call_handler, body):
    backup_id = prepare_target_backup(dynamodb_table)
    before = side_effect_snapshot()

    with forbid_mutation():
        response = call_handler(ROUTE_RESTORE, backup_id=backup_id, body=body)

    assert response['statusCode'] == 400
    assert response_body(response)['error']['code'] == 'INVALID_CONFIRMATION'
    assert side_effect_snapshot() == before
    assert_no_safety_backup()


# ---- Routing ----------------------------------------------------------------
@pytest.mark.parametrize('method, resource', [
    pytest.param('PUT', '/admin/backups', id='unsupported_method'),
    pytest.param('DELETE', '/admin/backups', id='delete_on_collection'),
    pytest.param('GET', '/admin/other', id='unknown_resource'),
    pytest.param('GET', '/admin/backups/{backup_id}', id='get_on_item'),
    pytest.param('POST', '/admin/backups/{backup_id}/download', id='post_download'),
    pytest.param('GET', '/admin/backups/{backup_id}/restore', id='get_restore'),
    pytest.param('OPTIONS', '/admin/backups', id='options_not_routed'),
    pytest.param('OPTIONS', '/admin/backups/{backup_id}/restore', id='options_item_not_routed'),
])
def test_unknown_route_returns_404_for_admin(dynamodb_table, backup_bucket, fake_clock,
                                             call_handler, method, resource):
    backup_id = prepare_target_backup(dynamodb_table)
    before = side_effect_snapshot()

    response = call_handler((method, resource), backup_id=backup_id, body=phrase_body())

    assert response['statusCode'] == 404
    assert response_body(response)['error']['code'] == 'NOT_FOUND'
    assert side_effect_snapshot() == before


@pytest.mark.parametrize('missing', ['resource', 'httpMethod', 'both'])
def test_missing_route_fields_return_404_not_500(dynamodb_table, backup_bucket,
                                                 mock_api_gateway_event, mock_lambda_context,
                                                 missing):
    event = mock_api_gateway_event(
        http_method='GET', path='/admin/backups', user_id=HANDLER_ADMIN_ID, groups=['admins'])
    assert 'resource' not in event  # the fixture does not set it
    if missing == 'httpMethod':
        event['resource'] = '/admin/backups'
    if missing in ('httpMethod', 'both'):
        event.pop('httpMethod')

    response = call_raw(event, mock_lambda_context)

    assert response['statusCode'] == 404
    assert response_body(response)['error']['code'] == 'NOT_FOUND'


# ---- End to end through the handler as admin --------------------------------
def test_handler_end_to_end_create_list_download_restore_delete(
        dynamodb_table, backup_bucket, fake_clock, call_handler):
    clear_table(dynamodb_table)
    original_items = generic_items(3, 'src') + special_items('binary', 'string_set')
    batch_put_typed_items(original_items)
    original_state = table_state()

    # POST create -> 201 with the contract fields
    response = call_handler(ROUTE_CREATE)
    assert response['statusCode'] == 201
    body = response_body(response)
    assert body['success'] is True
    created = body['data']
    assert {'backup_id', 'category', 'item_count', 'size_bytes', 'created_at',
            'native_backup'} <= set(created)
    assert created['category'] == CATEGORY_MANUAL
    assert created['item_count'] == len(original_items)
    assert created['size_bytes'] > 0
    assert created['created_at'] == backup_service.parse_backup_id(
        created['backup_id'])['created_at']
    assert set(created['native_backup']) == {'name', 'arn', 'status'}
    manual_id = created['backup_id']
    assert manual_id in bucket_keys()

    # Change the data after the backup (the create audit record is kept)
    for key in table_state():
        dynamodb_table.delete_item(Key={'PK': key[0], 'SK': key[1]})
    put_typed_items(generic_items(5, 'cur'))
    changed_state = table_state()
    assert changed_state != original_state
    assert [r['action'] for r in audit_records()] == ['create_backup']

    # GET list -> 200 with the new backup
    response = call_handler(ROUTE_LIST)
    assert response['statusCode'] == 200
    backups = response_body(response)['data']['backups']
    assert [b['backup_id'] for b in backups] == [manual_id]
    assert backups[0]['category'] == CATEGORY_MANUAL
    assert backups[0]['item_count'] == len(original_items)
    assert backups[0]['created_by'] == HANDLER_ADMIN_EMAIL

    # GET download -> 200 with the content envelope
    response = call_handler(ROUTE_DOWNLOAD, backup_id=manual_id)
    assert response['statusCode'] == 200
    data = response_body(response)['data']
    assert data['backup_id'] == manual_id
    assert data['filename'] == manual_id
    assert data['content']['format_version'] == FORMAT_VERSION
    assert data['content']['metadata']['item_count'] == len(original_items)
    assert items_by_key(backup_service.decode_items(data['content']['items'])) == original_state

    # POST restore with the correct phrase -> 200 RestoreResult, table restored
    response = call_handler(ROUTE_RESTORE, backup_id=manual_id, body=phrase_body())
    assert response['statusCode'] == 200
    result = response_body(response)['data']
    assert result['source_backup_id'] == manual_id
    assert result['purged_count'] == len(changed_state)
    assert result['preserved_audit_count'] == 1  # the create record
    assert result['restored_count'] == len(original_items)
    assert [s['status'] for s in result['steps']] == ['ok'] * 4
    assert result['audit_written'] is True
    assert table_state() == original_state
    safety_id = result['safety_backup']['backup_id']

    # The safety backup is listed afterwards, with its source reference
    response = call_handler(ROUTE_LIST)
    assert response['statusCode'] == 200
    rows = {b['backup_id']: b for b in response_body(response)['data']['backups']}
    assert set(rows) == {manual_id, safety_id}
    safety_row = rows[safety_id]
    manual_parsed = backup_service.parse_backup_id(manual_id)
    assert safety_row['category'] == CATEGORY_SAFETY
    assert safety_row['source_ref'] == f"{CATEGORY_MANUAL}_{manual_parsed['timestamp']}"
    assert safety_row['source_backup_id'] == manual_id
    assert safety_row['item_count'] == len(changed_state) + 1  # + the create audit record

    # DELETE -> 200 {backup_id, deleted: True}; the list no longer has it
    response = call_handler(ROUTE_DELETE, backup_id=manual_id)
    assert response['statusCode'] == 200
    assert response_body(response)['data'] == {'backup_id': manual_id, 'deleted': True}
    assert bucket_keys() == [safety_id]
    assert [r['action'] for r in audit_records()] == [
        'create_backup', 'restore_backup', 'delete_backup']

    response = call_handler(ROUTE_LIST)
    assert [b['backup_id'] for b in response_body(response)['data']['backups']] == [safety_id]

    # Deleting again, or downloading the deleted backup -> 404 BACKUP_NOT_FOUND
    for route in (ROUTE_DELETE, ROUTE_DOWNLOAD):
        response = call_handler(route, backup_id=manual_id)
        assert response['statusCode'] == 404
        assert response_body(response)['error']['code'] == 'BACKUP_NOT_FOUND'

    # Undo through the handler: restoring the safety backup brings back the changed data
    response = call_handler(ROUTE_RESTORE, backup_id=safety_id, body=phrase_body())
    assert response['statusCode'] == 200
    assert table_state() == changed_state
    assert response_body(response)['data']['preserved_audit_count'] == 3

    # The backup audit history survives both restores, in chronological order
    assert [r['action'] for r in audit_records()] == [
        'create_backup', 'restore_backup', 'delete_backup', 'restore_backup']


def test_handler_invalid_backup_id_returns_400(dynamodb_table, backup_bucket, call_handler):
    for route in sorted(ROUTES_WITH_BACKUP_ID):
        response = call_handler(route, backup_id='../x.json', body=phrase_body())
        assert response['statusCode'] == 400
        assert response_body(response)['error']['code'] == 'INVALID_BACKUP_ID'
    assert bucket_keys() == []


# ---- Admin identity comes from the claims -----------------------------------
def test_created_by_comes_from_claims_not_body(dynamodb_table, backup_bucket, fake_clock,
                                               call_handler):
    forged = json.dumps({'created_by': 'evil@x.y', 'email': 'evil@x.y', 'user_id': 'evil'})

    response = call_handler(ROUTE_CREATE, body=forged)

    assert response['statusCode'] == 201
    backup_id = response_body(response)['data']['backup_id']
    head = s3_client().head_object(Bucket=BUCKET_NAME, Key=backup_id)
    assert head['Metadata']['created-by'] == HANDLER_ADMIN_EMAIL
    envelope = backup_service.read_backup(backup_id)
    assert envelope['metadata']['created_by'] == HANDLER_ADMIN_EMAIL
    records = audit_records()
    assert len(records) == 1
    assert records[0]['user_id'] == HANDLER_ADMIN_ID
    assert records[0]['user_email'] == HANDLER_ADMIN_EMAIL
    assert 'evil' not in json.dumps(records, default=str)


def test_safety_backup_created_by_comes_from_claims(dynamodb_table, backup_bucket, fake_clock,
                                                    call_handler):
    backup_id = prepare_target_backup(dynamodb_table)

    response = call_handler(ROUTE_RESTORE, backup_id=backup_id, body=phrase_body(),
                            user_id='admin-2')

    assert response['statusCode'] == 200
    safety_id = response_body(response)['data']['safety_backup']['backup_id']
    head = s3_client().head_object(Bucket=BUCKET_NAME, Key=safety_id)
    assert head['Metadata']['created-by'] == 'admin-2@test.com'


# ---------------------------------------------------------------------------
# 8. Frontend/backend constants alignment (task 5.8)
# Validates: Requirements 3.8, 7.7, 8.2
# The frontend file is read as TEXT (no node needed).
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
_FRONTEND_NAMING_PATH = os.path.join(_REPO_ROOT, 'frontend', 'src', 'utils', 'backupNaming.js')
_LOCALES_DIR = os.path.join(_REPO_ROOT, 'frontend', 'src', 'locales')


def _frontend_naming_source():
    with open(_FRONTEND_NAMING_PATH, encoding='utf-8') as handle:
        return handle.read()


def _frontend_string_constant(name):
    match = re.search(r"export const %s = '([^']*)';" % re.escape(name), _frontend_naming_source())
    assert match, f'export const {name} not found in backupNaming.js'
    return match.group(1)


def _load_locale(lang):
    with open(os.path.join(_LOCALES_DIR, f'{lang}.json'), encoding='utf-8') as handle:
        return json.load(handle)


@pytest.mark.parametrize('name, backend_value', [
    ('CONFIRMATION_PHRASE', CONFIRMATION_PHRASE),
    ('CATEGORY_MANUAL', CATEGORY_MANUAL),
    ('CATEGORY_SAFETY', CATEGORY_SAFETY),
    ('SOURCE_MARKER', SOURCE_MARKER),
])
def test_frontend_backend_constants_aligned(name, backend_value):
    """backupNaming.js and backup_service.py define exactly the same constants"""
    assert _frontend_string_constant(name) == backend_value


def test_frontend_backup_id_regex_has_same_structure_as_backend_pattern():
    """The JS regex literal carries the same category alternation, marker and extension"""
    match = re.search(r"const BACKUP_ID_REGEX =\s*/(.*)/;", _frontend_naming_source())
    assert match, 'BACKUP_ID_REGEX literal not found in backupNaming.js'
    js_source = match.group(1)
    alternation = f'{CATEGORY_MANUAL}|{CATEGORY_SAFETY}'
    assert alternation == 'manual|safety-pre-restore'
    # Category alternation used for the id and for the optional source reference
    assert js_source.count(f'({alternation})') == 2
    assert SOURCE_MARKER in js_source
    assert js_source.startswith('^') and js_source.endswith(r'\.json$')
    # Same timestamp shape on both sides
    timestamp = r'\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z'
    assert timestamp in js_source
    assert timestamp in backup_service.BACKUP_ID_PATTERN.pattern


# Shared contract samples: frontend/src/utils/backupNaming.test.js uses the same ids
_SHARED_MANUAL_STEM = 'manual_2026-11-01T14-30-00Z'
_SHARED_VALID_IDS = [
    f'{_SHARED_MANUAL_STEM}.json',
    f'safety-pre-restore_2026-11-02T09-15-45Z_before-restore-of_{_SHARED_MANUAL_STEM}.json',
    'safety-pre-restore_2026-11-03T10-00-00Z_before-restore-of_'
    'safety-pre-restore_2026-11-02T09-15-45Z.json',
]
_SHARED_INVALID_IDS = [
    '../x.json',
    f'../{_SHARED_MANUAL_STEM}.json',
    '/',
    f'dir/{_SHARED_MANUAL_STEM}.json',
    'auto_2026-11-01T14-30-00Z.json',
    'safety-pre-restore_2026-11-02T09-15-45Z.json',
    f'manual_2026-11-02T09-15-45Z_before-restore-of_{_SHARED_MANUAL_STEM}.json',
    'safety-pre-restore_2026-11-03T10-00-00Z_before-restore-of_safety-pre-restore_'
    f'2026-11-02T09-15-45Z_before-restore-of_{_SHARED_MANUAL_STEM}.json',
    _SHARED_MANUAL_STEM,
    f'{_SHARED_MANUAL_STEM}.txt',
    'manual_2026-11-01T14:30:00Z.json',
    'manual_2026-11-01.json',
    '',
    None,
    42,
    {},
]


@pytest.mark.parametrize('backup_id', _SHARED_VALID_IDS)
def test_shared_valid_ids_parse_in_backend(backup_id):
    parsed = backup_service.parse_backup_id(backup_id)
    assert parsed['category'] in (CATEGORY_MANUAL, CATEGORY_SAFETY)


@pytest.mark.parametrize('backup_id', _SHARED_INVALID_IDS)
def test_shared_invalid_ids_rejected_by_backend(backup_id):
    with pytest.raises(InvalidBackupId):
        backup_service.parse_backup_id(backup_id)


@pytest.mark.parametrize('lang', ['fr', 'en'])
def test_locale_has_category_label_for_each_category(lang):
    """categoryBadge labelKey is admin.database.category.<category id>"""
    categories = _load_locale(lang)['admin']['database']['category']
    for category in (CATEGORY_MANUAL, CATEGORY_SAFETY):
        assert isinstance(categories.get(category), str) and categories[category]


_API_ERROR_CODES = [
    'JSON_BACKUP_FAILED', 'NATIVE_BACKUP_FAILED', 'SAFETY_BACKUP_FAILED',
    'BACKUP_NOT_FOUND', 'BACKUP_INVALID', 'LIST_FAILED', 'RESTORE_PARTIAL',
    'INVALID_CONFIRMATION', 'INVALID_BACKUP_ID', 'NOT_FOUND', 'INTERNAL_ERROR',
    'FORBIDDEN', 'UNAUTHORIZED',
]


@pytest.mark.parametrize('lang', ['fr', 'en'])
@pytest.mark.parametrize('code', _API_ERROR_CODES)
def test_locale_has_message_for_each_error_code(lang, code):
    errors = _load_locale(lang)['admin']['database']['errors']
    assert isinstance(errors.get(code), str) and errors[code]


def test_backend_error_classes_codes_are_in_checked_list():
    """The api-facing codes of the BackupError classes are all covered by the locale check"""
    class_codes = {
        backup_service.JsonBackupFailed.code, backup_service.NativeBackupFailed.code,
        backup_service.SafetyBackupFailed.code, backup_service.BackupNotFound.code,
        backup_service.BackupInvalid.code, backup_service.ListFailed.code,
        backup_service.RestorePartial.code, backup_service.InvalidConfirmation.code,
        backup_service.BackupError.code,
    }
    assert class_codes <= set(_API_ERROR_CODES)
