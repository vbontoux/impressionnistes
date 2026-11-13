"""
Database backup and restore service

Helpers for full-table JSON backups of the registration table:
constants, backup naming, consistent paginated scan, typed-JSON (DynamoDB JSON)
encoding of binary values, and the backup file envelope.

Items are kept in DynamoDB typed form (low-level client) so a round trip is
exact: numbers stay strings, sets stay sets. Only B/BS values are converted
to/from base64 so they can be stored in JSON.

Constants are mirrored in frontend/src/utils/backupNaming.js.
"""
import base64
import binascii
import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import boto3
from boto3.dynamodb.types import TypeSerializer

from responses import (
    error_response, get_path_parameter, parse_request_body, success_response,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Constants (mirrored in frontend/src/utils/backupNaming.js)
# ---------------------------------------------------------------------------
CATEGORY_MANUAL = "manual"
CATEGORY_SAFETY = "safety-pre-restore"
CONFIRMATION_PHRASE = "RESTAURER LA BASE"
SOURCE_MARKER = "_before-restore-of_"
FORMAT_VERSION = 1
AUDIT_PK = "AUDIT#DATABASE_BACKUP"

CATEGORIES = (CATEGORY_MANUAL, CATEGORY_SAFETY)

TIMESTAMP_FORMAT = "%Y-%m-%dT%H-%M-%SZ"
_TS = r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z"
_STEM = rf"(?:manual|safety-pre-restore)_{_TS}"
BACKUP_ID_PATTERN = re.compile(
    rf"^(?P<category>manual|safety-pre-restore)_(?P<timestamp>{_TS})"
    rf"(?:{re.escape(SOURCE_MARKER)}(?P<source>{_STEM}))?\.json\Z"
)


class InvalidBackupId(ValueError):
    """Raised when a backup identifier does not match the naming rules"""


class InvalidBackupEnvelope(ValueError):
    """Raised when a backup file fails envelope validation"""


# ---------------------------------------------------------------------------
# Lazy AWS clients (avoid import-time issues in test environments)
# ---------------------------------------------------------------------------
_dynamodb_client = None
_s3_client = None


def _get_dynamodb_client():
    """Get or create the low-level DynamoDB client (lazy initialization)"""
    global _dynamodb_client
    if _dynamodb_client is None:
        _dynamodb_client = boto3.client('dynamodb')
    return _dynamodb_client


def _get_s3_client():
    """Get or create the S3 client (lazy initialization)"""
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client('s3')
    return _s3_client


def _get_table_name() -> str:
    """Registration table name from the environment"""
    return os.environ.get('TABLE_NAME', '')


def _get_bucket_name() -> str:
    """Backup bucket name from the environment"""
    return os.environ.get('BACKUP_BUCKET', '')


# ---------------------------------------------------------------------------
# Naming
# ---------------------------------------------------------------------------
def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_timestamp(moment: Optional[datetime] = None) -> str:
    """Format a UTC moment as YYYY-MM-DDTHH-MM-SSZ (sortable, no ':')"""
    moment = moment or _utc_now()
    if moment.tzinfo is not None:
        moment = moment.astimezone(timezone.utc)
    return moment.strftime(TIMESTAMP_FORMAT)


def make_backup_id(category: str, moment: Optional[datetime] = None,
                   source_id: Optional[str] = None) -> str:
    """
    Build a backup id (also the S3 key).

    manual: manual_{timestamp}.json
    safety: safety-pre-restore_{timestamp}_before-restore-of_{source_category}_{source_timestamp}.json

    The embedded source reference is always {source_category}_{source_timestamp}
    (never the full source id), so ids stay short at any chain depth. The full
    real source id is kept in the object metadata, envelope and audit record.

    Raises:
        InvalidBackupId: unknown category, safety without source,
        manual with source, or invalid source id
    """
    if category not in CATEGORIES:
        raise InvalidBackupId(f"Unknown backup category: {category}")

    timestamp = format_timestamp(moment)

    if category == CATEGORY_MANUAL:
        if source_id:
            raise InvalidBackupId("A manual backup cannot have a source backup")
        backup_id = f"{category}_{timestamp}.json"
    else:
        if not source_id:
            raise InvalidBackupId("A safety backup requires a source backup")
        source = parse_backup_id(source_id)
        source_ref = f"{source['category']}_{source['timestamp']}"
        backup_id = f"{category}_{timestamp}{SOURCE_MARKER}{source_ref}.json"

    # Validate what we built (defense in depth)
    parse_backup_id(backup_id)
    return backup_id


def parse_backup_id(backup_id: Any) -> Dict[str, Optional[str]]:
    """
    Validate and parse a backup id.

    Returns:
        dict with category, timestamp, created_at (ISO-8601 UTC),
        source_ref ({source_category}_{source_timestamp}, None for manual)
        and source_stem (same value, kept for compatibility). The full real
        source id is not derivable from the key; it lives in the metadata.

    Raises:
        InvalidBackupId: if the id does not match the naming rules
    """
    if not isinstance(backup_id, str):
        raise InvalidBackupId("Backup id must be a string")

    match = BACKUP_ID_PATTERN.match(backup_id)
    if not match:
        raise InvalidBackupId(f"Invalid backup id: {backup_id!r}")

    category = match.group('category')
    timestamp = match.group('timestamp')
    source_stem = match.group('source')

    # A safety id must contain the source part, a manual id must not
    if category == CATEGORY_SAFETY and not source_stem:
        raise InvalidBackupId("A safety backup id must contain its source")
    if category == CATEGORY_MANUAL and source_stem:
        raise InvalidBackupId("A manual backup id cannot contain a source")

    try:
        created = datetime.strptime(timestamp, TIMESTAMP_FORMAT)
    except ValueError:
        raise InvalidBackupId(f"Invalid timestamp in backup id: {backup_id!r}")

    return {
        'category': category,
        'timestamp': timestamp,
        'created_at': created.strftime("%Y-%m-%dT%H:%M:%SZ"),
        'source_ref': source_stem,
        'source_stem': source_stem,
    }


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------
def scan_table(table_name: Optional[str] = None, client=None) -> List[Dict[str, Any]]:
    """
    Consistent, paginated, full-item scan with the low-level client.

    Items are returned in DynamoDB typed form (e.g. {"PK": {"S": "x"}}).

    Args:
        table_name: defaults to env TABLE_NAME
        client: defaults to the lazy DynamoDB client
    """
    client = client or _get_dynamodb_client()
    table_name = table_name or _get_table_name()

    params: Dict[str, Any] = {'TableName': table_name, 'ConsistentRead': True}

    items: List[Dict[str, Any]] = []
    while True:
        response = client.scan(**params)
        items.extend(response.get('Items', []))
        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break
        params['ExclusiveStartKey'] = last_key
    return items


# ---------------------------------------------------------------------------
# Typed-JSON helpers (B/BS <-> base64, recursive over M/L)
# ---------------------------------------------------------------------------
def _convert_attribute(attr: Any, to_json: bool) -> Any:
    """Convert one typed attribute value; binary <-> base64, recursing M/L"""
    if not isinstance(attr, dict) or len(attr) != 1:
        raise ValueError(f"Invalid DynamoDB typed value: {attr!r}")

    (type_code, value), = attr.items()

    if type_code == 'B':
        return {'B': _b64(value, to_json)}
    if type_code == 'BS':
        return {'BS': [_b64(v, to_json) for v in value]}
    if type_code == 'M':
        return {'M': {k: _convert_attribute(v, to_json) for k, v in value.items()}}
    if type_code == 'L':
        return {'L': [_convert_attribute(v, to_json) for v in value]}
    # S, N, SS, NS, BOOL, NULL are JSON-compatible as-is
    return {type_code: value}


def _b64(value: Any, to_json: bool) -> Any:
    if to_json:
        if isinstance(value, str):
            value = value.encode('utf-8')
        return base64.b64encode(bytes(value)).decode('ascii')
    if not isinstance(value, str):
        raise ValueError("Base64 value must be a string")
    try:
        return base64.b64decode(value.encode('ascii'), validate=True)
    except (binascii.Error, UnicodeEncodeError) as e:
        raise ValueError(f"Invalid base64 value: {e}")


def encode_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Typed items (bytes for B/BS) -> JSON-serializable typed items (base64)"""
    return [{k: _convert_attribute(v, True) for k, v in item.items()} for item in items]


def decode_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """JSON typed items (base64 for B/BS) -> typed items ready for batch_write_item"""
    return [{k: _convert_attribute(v, False) for k, v in item.items()} for item in items]


# ---------------------------------------------------------------------------
# Envelope
# ---------------------------------------------------------------------------
def build_envelope(encoded_items: List[Dict[str, Any]], backup_id: str,
                   created_by: str, created_at: Optional[str] = None,
                   table_name: Optional[str] = None,
                   environment: Optional[str] = None,
                   source_backup_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Build the backup file envelope from already-encoded items.

    Category is derived from backup_id. source_backup_id is the full real id
    of the source backup (safety backups); it is passed explicitly because it
    cannot be derived from the id.
    """
    parsed = parse_backup_id(backup_id)

    metadata: Dict[str, Any] = {
        'backup_id': backup_id,
        'category': parsed['category'],
        'created_at': created_at or parsed['created_at'],
        'created_by': created_by,
        'item_count': len(encoded_items),
        'table_name': table_name or _get_table_name(),
        'environment': environment if environment is not None
        else os.environ.get('ENVIRONMENT', ''),
    }
    if parsed['category'] == CATEGORY_SAFETY and source_backup_id:
        metadata['source_backup_id'] = source_backup_id

    return {
        'format_version': FORMAT_VERSION,
        'metadata': metadata,
        'items': encoded_items,
    }


def validate_envelope(envelope: Any) -> List[Dict[str, Any]]:
    """
    Validate a backup envelope and return the decoded items.

    Checks: format_version, items is a list, every item has string PK and SK,
    no duplicate (PK, SK), metadata.item_count matches, base64 decodes.

    Raises:
        InvalidBackupEnvelope: on any violation
    """
    if not isinstance(envelope, dict):
        raise InvalidBackupEnvelope("Backup content must be a JSON object")

    if envelope.get('format_version') != FORMAT_VERSION:
        raise InvalidBackupEnvelope(
            f"Unsupported format_version: {envelope.get('format_version')!r}")

    items = envelope.get('items')
    if not isinstance(items, list):
        raise InvalidBackupEnvelope("'items' must be a list")

    metadata = envelope.get('metadata')
    if not isinstance(metadata, dict):
        raise InvalidBackupEnvelope("'metadata' must be an object")

    seen: set = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise InvalidBackupEnvelope(f"Item {index} is not an object")
        key = _item_key(item, index)
        if key in seen:
            raise InvalidBackupEnvelope(f"Duplicate key {key} at item {index}")
        seen.add(key)

    item_count = metadata.get('item_count')
    if isinstance(item_count, bool) or item_count != len(items):
        raise InvalidBackupEnvelope(
            f"item_count {item_count!r} does not match {len(items)} items")

    try:
        return decode_items(items)
    except ValueError as e:
        raise InvalidBackupEnvelope(f"Invalid item content: {e}")


def _item_key(item: Dict[str, Any], index: int) -> Tuple[str, str]:
    """Extract (PK, SK) string values from a typed item"""
    values = []
    for name in ('PK', 'SK'):
        attr = item.get(name)
        if not (isinstance(attr, dict) and len(attr) == 1
                and isinstance(attr.get('S'), str)):
            raise InvalidBackupEnvelope(f"Item {index} has no string {name}")
        values.append(attr['S'])
    return values[0], values[1]


# ---------------------------------------------------------------------------
# Errors (carry code, HTTP status and details for the handle_* adapters)
# ---------------------------------------------------------------------------
class BackupError(Exception):
    """Base class: error_response(status, code, message, details)"""
    code = "INTERNAL_ERROR"
    status = 500

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class JsonBackupFailed(BackupError):
    code, status = "JSON_BACKUP_FAILED", 500


class NativeBackupFailed(BackupError):
    code, status = "NATIVE_BACKUP_FAILED", 502


class SafetyBackupFailed(BackupError):
    code, status = "SAFETY_BACKUP_FAILED", 500


class BackupNotFound(BackupError):
    code, status = "BACKUP_NOT_FOUND", 404


class BackupInvalid(BackupError):
    code, status = "BACKUP_INVALID", 422


class ListFailed(BackupError):
    code, status = "LIST_FAILED", 500


_NOT_FOUND_CODES = ('NoSuchKey', 'NotFound', '404')


def _is_not_found(error: Exception) -> bool:
    code = getattr(error, 'response', {}).get('Error', {}).get('Code')
    return code in _NOT_FOUND_CODES


def _ascii(value: Any) -> str:
    """S3 user metadata must be ASCII"""
    return str(value if value is not None else '').encode('ascii', 'replace').decode('ascii')


def _user_email(user: Optional[Dict[str, Any]]) -> str:
    user = user or {}
    return user.get('email') or user.get('user_id') or 'unknown'


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------
def create_backup(category: str, user: Optional[Dict[str, Any]],
                  source_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a JSON backup in S3, then a native DynamoDB backup.

    Raises:
        InvalidBackupId: bad category/source combination
        JsonBackupFailed: scan or S3 write failed (nothing stored)
        NativeBackupFailed: native backup failed (JSON backup remains)
    """
    moment = _utc_now()
    backup_id = make_backup_id(category, moment, source_id)
    parsed = parse_backup_id(backup_id)
    created_by = _user_email(user)
    table_name = _get_table_name()

    try:
        items = encode_items(scan_table(table_name))
        envelope = build_envelope(items, backup_id, created_by, parsed['created_at'],
                                  table_name, source_backup_id=source_id)
        body = json.dumps(envelope, separators=(",", ":"),
                          ensure_ascii=False).encode('utf-8')
        metadata = {
            'category': category,
            'created-at': parsed['created_at'],
            'created-by': _ascii(created_by),
            'item-count': str(len(items)),
        }
        if source_id:
            metadata['source-backup-id'] = _ascii(source_id)
        _get_s3_client().put_object(
            Bucket=_get_bucket_name(), Key=backup_id, Body=body,
            ContentType='application/json', Metadata=metadata)
    except Exception as e:
        logger.error(f"JSON backup {backup_id} failed: {e}", exc_info=True)
        raise JsonBackupFailed("The JSON backup could not be created",
                               {'failed_artifact': 'json'})

    native_name = f"{table_name}-{category}_{parsed['timestamp']}"
    try:
        response = _get_dynamodb_client().create_backup(
            TableName=table_name, BackupName=native_name)
        details = response.get('BackupDetails', {})
        native = {
            'name': native_name,
            'arn': details.get('BackupArn'),
            'status': details.get('BackupStatus'),
        }
    except Exception as e:
        logger.error(f"Native backup {native_name} failed: {e}", exc_info=True)
        raise NativeBackupFailed(
            "The native DynamoDB backup could not be created",
            {'failed_artifact': 'aws_native', 'backup_id': backup_id})

    return {
        'backup_id': backup_id,
        'category': category,
        'item_count': len(items),
        'size_bytes': len(body),
        'created_at': parsed['created_at'],
        'source_backup_id': source_id,
        'native_backup': native,
    }


# ---------------------------------------------------------------------------
# List / read / delete
# ---------------------------------------------------------------------------
def list_backups() -> List[Dict[str, Any]]:
    """
    List JSON backups, newest first. Ids that are not valid backups are skipped.

    Each row has: backup_id, category, created_at, item_count, size_bytes,
    created_by, source_backup_id (full real source id from S3 metadata, None
    if missing) and source_ref ({category}_{timestamp} parsed from the key).
    """
    s3 = _get_s3_client()
    bucket = _get_bucket_name()
    backups = []
    try:
        params: Dict[str, Any] = {'Bucket': bucket}
        while True:
            page = s3.list_objects_v2(**params)
            for obj in page.get('Contents', []):
                key = obj['Key']
                try:
                    parsed = parse_backup_id(key)
                except InvalidBackupId:
                    continue
                try:
                    meta = s3.head_object(Bucket=bucket, Key=key).get('Metadata', {})
                except Exception as e:
                    if _is_not_found(e):  # deleted since listing
                        continue
                    raise
                count = meta.get('item-count')
                backups.append({
                    'backup_id': key,
                    'category': parsed['category'],
                    'created_at': parsed['created_at'],
                    'item_count': int(count) if str(count).isdigit() else None,
                    'size_bytes': obj.get('Size'),
                    'created_by': meta.get('created-by'),
                    # Full real source id: from S3 metadata (null if missing)
                    'source_backup_id': meta.get('source-backup-id'),
                    # {category}_{timestamp} parsed from the key (authoritative for display)
                    'source_ref': parsed['source_ref'],
                    '_sort': (parsed['timestamp'], key),
                })
            if not page.get('IsTruncated'):
                break
            params['ContinuationToken'] = page['NextContinuationToken']
    except Exception as e:
        logger.error(f"Listing backups failed: {e}", exc_info=True)
        raise ListFailed("The backups could not be listed")

    backups.sort(key=lambda b: b['_sort'], reverse=True)
    for b in backups:
        del b['_sort']
    return backups


def read_backup(backup_id: str) -> Dict[str, Any]:
    """
    Load and validate a backup envelope.

    Raises:
        InvalidBackupId, BackupNotFound, BackupInvalid
    """
    parse_backup_id(backup_id)
    try:
        response = _get_s3_client().get_object(Bucket=_get_bucket_name(), Key=backup_id)
        raw = response['Body'].read()
    except Exception as e:
        if _is_not_found(e):
            raise BackupNotFound("Backup not found", {'backup_id': backup_id})
        raise

    try:
        envelope = json.loads(raw.decode('utf-8'))
    except ValueError:  # includes UnicodeDecodeError and JSONDecodeError
        raise BackupInvalid("Backup is not valid JSON", {'backup_id': backup_id})
    try:
        validate_envelope(envelope)
    except InvalidBackupEnvelope as e:
        raise BackupInvalid(str(e), {'backup_id': backup_id})
    return envelope


def delete_backup(backup_id: str) -> None:
    """
    Delete a backup object (the native backup is kept).

    Raises:
        InvalidBackupId, BackupNotFound
    """
    parse_backup_id(backup_id)
    s3 = _get_s3_client()
    bucket = _get_bucket_name()
    try:
        s3.head_object(Bucket=bucket, Key=backup_id)
    except Exception as e:
        if _is_not_found(e):
            raise BackupNotFound("Backup not found", {'backup_id': backup_id})
        raise
    s3.delete_object(Bucket=bucket, Key=backup_id)


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------
def write_audit(action: str, user: Optional[Dict[str, Any]],
                details: Optional[Dict[str, Any]] = None) -> bool:
    """
    Write an AUDIT#DATABASE_BACKUP record. Never raises.

    Returns:
        True if written, False if it failed (logged)
    """
    try:
        user = user or {}
        user_id = user.get('user_id') or 'unknown'
        timestamp = _utc_now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        item = {
            'PK': AUDIT_PK,
            'SK': f"{timestamp}#{user_id}",
            'action': action,
            'user_id': user_id,
            'user_email': user.get('email') or 'unknown',
            'timestamp': timestamp,
            'details': {k: v for k, v in (details or {}).items() if v is not None},
        }
        serializer = TypeSerializer()
        _get_dynamodb_client().put_item(
            TableName=_get_table_name(),
            Item={k: serializer.serialize(v) for k, v in item.items()})
        return True
    except Exception as e:
        logger.error(f"Audit write failed for {action}: {e}", exc_info=True)
        return False


# ---------------------------------------------------------------------------
# Batch write, purge, write, count
# ---------------------------------------------------------------------------
BATCH_SIZE = 25
MAX_BATCH_ATTEMPTS = 8
BACKOFF_START_S = 0.05
BACKOFF_CAP_S = 1.0

# Patchable in tests so retries do not wait
_sleep = time.sleep


class BatchWriteError(BackupError):
    code, status = "BATCH_WRITE_FAILED", 500


class InvalidConfirmation(BackupError):
    code, status = "INVALID_CONFIRMATION", 400


class RestorePartial(BackupError):
    code, status = "RESTORE_PARTIAL", 500


def batch_write_with_retry(request_items: Dict[str, List[Dict[str, Any]]]) -> None:
    """
    batch_write_item for one chunk (max 25 requests), retrying UnprocessedItems.

    Up to 8 attempts, backoff 50 ms doubling, capped at 1 s.

    Raises:
        BatchWriteError: items still unprocessed after the last attempt
    """
    client = _get_dynamodb_client()
    delay = BACKOFF_START_S
    pending = request_items
    for attempt in range(1, MAX_BATCH_ATTEMPTS + 1):
        response = client.batch_write_item(RequestItems=pending)
        pending = response.get('UnprocessedItems') or {}
        if not pending:
            return
        if attempt < MAX_BATCH_ATTEMPTS:
            _sleep(delay)
            delay = min(delay * 2, BACKOFF_CAP_S)
    remaining = sum(len(v) for v in pending.values())
    raise BatchWriteError("Some items could not be written",
                          {'unprocessed_count': remaining})


def _write_requests(requests: List[Dict[str, Any]]) -> int:
    """Send requests in chunks of 25 with retry; return how many were sent"""
    table_name = _get_table_name()
    for start in range(0, len(requests), BATCH_SIZE):
        batch_write_with_retry({table_name: requests[start:start + BATCH_SIZE]})
    return len(requests)


def purge_table(preserve_pk: Optional[str] = None) -> Tuple[int, Set[Tuple[str, str]]]:
    """
    Delete every item except those whose PK equals `preserve_pk`.

    Full consistent scan; only PK/SK are used for the deletes. A keys-only
    projection is avoided on purpose: it is unnecessary for a small table and
    is broken in moto for binary sets.

    Returns:
        (purged_count, preserved_keys): the number of deleted items (preserved
        items are not counted) and the set of (PK, SK) string keys that were kept.
    """
    to_delete = []
    preserved_keys: Set[Tuple[str, str]] = set()
    for index, item in enumerate(scan_table()):
        key = _item_key(item, index)
        if preserve_pk is not None and key[0] == preserve_pk:
            preserved_keys.add(key)
        else:
            to_delete.append({'DeleteRequest': {'Key': {'PK': item['PK'], 'SK': item['SK']}}})
    return _write_requests(to_delete), preserved_keys


def write_items(decoded_items: List[Dict[str, Any]]) -> int:
    """Put every typed item. Returns the written count."""
    return _write_requests([{'PutRequest': {'Item': item}} for item in decoded_items])


def count_items() -> int:
    """Consistent, paginated Select='COUNT' scan"""
    client = _get_dynamodb_client()
    params: Dict[str, Any] = {'TableName': _get_table_name(),
                              'Select': 'COUNT', 'ConsistentRead': True}
    total = 0
    while True:
        response = client.scan(**params)
        total += response.get('Count', 0)
        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            return total
        params['ExclusiveStartKey'] = last_key


# ---------------------------------------------------------------------------
# Restore
# ---------------------------------------------------------------------------
def restore_backup(backup_id: str, phrase: Any, user: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Replace the whole table with the content of a backup.

    Order: validate id, validate phrase, load/validate source, safety backup
    (abort before any change on failure), purge, write, verify, audit.

    The AUDIT_PK partition (backup audit history) is never purged: it is kept
    and merged with the source's own AUDIT_PK records (same key: source wins).
    `purged_count` excludes preserved records; the verify step expects the
    union of source keys and preserved audit keys.

    Raises:
        InvalidBackupId, InvalidConfirmation, BackupNotFound, BackupInvalid,
        SafetyBackupFailed (table untouched), RestorePartial (after purge started)
    """
    started = time.monotonic()
    parse_backup_id(backup_id)
    if phrase != CONFIRMATION_PHRASE:
        raise InvalidConfirmation("The confirmation phrase is incorrect")

    envelope = read_backup(backup_id)
    try:
        items = validate_envelope(envelope)
    except InvalidBackupEnvelope as e:
        raise BackupInvalid(str(e), {'backup_id': backup_id})

    try:
        safety = create_backup(CATEGORY_SAFETY, user, source_id=backup_id)
    except Exception as e:
        logger.error(f"Safety backup failed for {backup_id}: {e}", exc_info=True)
        details = dict(getattr(e, 'details', None) or {})
        details.setdefault('failed_artifact', 'unknown')
        details['source_backup_id'] = backup_id
        raise SafetyBackupFailed(
            "The safety backup could not be created; the database was not modified",
            details)

    safety_id = safety['backup_id']
    native = safety.get('native_backup') or {}
    steps = {name: {'name': name, 'status': 'skipped', 'count': None}
             for name in ('purge', 'write', 'verify')}
    steps['safety_backup'] = {'name': 'safety_backup', 'status': 'ok',
                              'count': safety['item_count']}
    ordered = lambda: [steps[n] for n in ('safety_backup', 'purge', 'write', 'verify')]  # noqa: E731

    purged = written = preserved_audit_count = 0
    stage = 'purge'
    try:
        purged, preserved_keys = purge_table(preserve_pk=AUDIT_PK)
        preserved_audit_count = len(preserved_keys)
        # Computed before the write: source items overwrite preserved keys that coincide
        expected = len({_item_key(item, i) for i, item in enumerate(items)} | preserved_keys)
        steps['purge'].update(status='ok', count=purged)
        stage = 'write'
        written = write_items(items)
        steps['write'].update(status='ok', count=written)
        stage = 'verify'
        actual = count_items()
        if actual != expected:
            raise BackupError(f"Expected {expected} items, found {actual}")
        steps['verify'].update(status='ok', count=actual)
    except Exception as e:
        logger.error(f"Restore of {backup_id} failed at {stage}: {e}", exc_info=True)
        steps[stage]['status'] = 'failed'
        raise RestorePartial(
            "The restore failed after the purge started; restore the safety backup",
            {
                'safety_backup_id': safety_id,
                'safety_native_backup': {'name': native.get('name'), 'arn': native.get('arn')},
                'source_backup_id': backup_id,
                'stage': stage,
                'purged_count': purged,
                'preserved_audit_count': preserved_audit_count,
                'written_count': written,
                'steps': ordered(),
            })

    audit_written = write_audit('restore_backup', user, {
        'source_backup_id': backup_id,
        'safety_backup_id': safety_id,
        'purged_count': purged,
        'restored_count': written,
    })
    return {
        'source_backup_id': backup_id,
        'purged_count': purged,
        'preserved_audit_count': preserved_audit_count,
        'restored_count': written,
        'safety_backup': {
            'backup_id': safety_id,
            'native_backup': {'name': native.get('name'), 'arn': native.get('arn')},
        },
        'steps': ordered(),
        'audit_written': audit_written,
        'duration_ms': int((time.monotonic() - started) * 1000),
    }


# ---------------------------------------------------------------------------
# API adapters
# ---------------------------------------------------------------------------
def _backup_id_from_event(event: Dict[str, Any]) -> str:
    return get_path_parameter({'pathParameters': event.get('pathParameters') or {}},
                              'backup_id')


def _run(action):
    """Run action(); map backup errors to error_response (no stack traces)"""
    try:
        return action()
    except InvalidBackupId as e:
        logger.warning(f"Invalid backup id: {e}")
        return error_response(400, "INVALID_BACKUP_ID", "Invalid backup id")
    except BackupError as e:
        logger.error(f"{e.code}: {e.message}", exc_info=True)
        return error_response(e.status, e.code, e.message, e.details or None)


def handle_create(event: Dict[str, Any], user: Dict[str, Any]):
    def action():
        result = create_backup(CATEGORY_MANUAL, user)
        write_audit('create_backup', user, {
            'backup_id': result['backup_id'],
            'item_count': result['item_count'],
            'source_backup_id': None,
        })
        return success_response(result, 201)
    return _run(action)


def handle_list(event: Dict[str, Any], user: Dict[str, Any]):
    return _run(lambda: success_response({'backups': list_backups()}))


def handle_download(event: Dict[str, Any], user: Dict[str, Any]):
    def action():
        backup_id = _backup_id_from_event(event)
        content = read_backup(backup_id)
        return success_response({'backup_id': backup_id, 'filename': backup_id,
                                 'content': content})
    return _run(action)


def handle_delete(event: Dict[str, Any], user: Dict[str, Any]):
    def action():
        backup_id = _backup_id_from_event(event)
        delete_backup(backup_id)
        write_audit('delete_backup', user, {'backup_id': backup_id})
        return success_response({'backup_id': backup_id, 'deleted': True})
    return _run(action)


def handle_restore(event: Dict[str, Any], user: Dict[str, Any]):
    def action():
        backup_id = _backup_id_from_event(event)
        try:
            body = parse_request_body(event)
        except ValueError:
            body = None
        if not isinstance(body, dict) or not body.get('confirmation_phrase'):
            parse_backup_id(backup_id)  # keep the id error first
            raise InvalidConfirmation("The confirmation phrase is missing")
        return success_response(
            restore_backup(backup_id, body['confirmation_phrase'], user))
    return _run(action)
