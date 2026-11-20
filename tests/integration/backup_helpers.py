"""
Plain helpers shared by the backup/restore and database reset integration tests.

Fixtures live in tests/integration/conftest.py. Import with:
    from tests.integration.backup_helpers import clear_table, table_state, ...
"""
import os
from datetime import datetime, timedelta, timezone

import boto3

import backup_service

REGION = 'eu-west-3'
BUCKET_NAME = 'test-backups'
ADMIN_USER = {'user_id': 'u1', 'email': 'a@b.c'}


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
