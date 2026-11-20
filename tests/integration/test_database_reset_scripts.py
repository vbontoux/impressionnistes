"""
Tests for the command-line tools of the database reset feature (task 6.7).

purge_database.py is loaded with importlib from scripts/database and run against moto
(table `impressionnistes-registration-{env}`, bucket `rcpm-impressionnistes-backups-{env}`,
the names configure_environment sets), so nothing reaches real AWS.

No Hypothesis: explicit cases only.
"""
import importlib.util
import json
import os

import boto3
import pytest

import backup_service
import reset_service
from tests.integration.backup_helpers import REGION, clear_table, items_by_key, put_typed_items
from tests.integration.test_database_reset import (  # noqa: F401  (fake_clock is a fixture)
    SET_IDS, _audit_records, _native_names, _s3_keys, _seed_items, fake_clock,
)

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, 'scripts', 'database')

_ENV_VARS = ('ENVIRONMENT', 'TABLE_NAME', 'BACKUP_BUCKET', 'AWS_DEFAULT_REGION', 'USER_POOL_ID')


def _load_script(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_SCRIPTS_DIR, f'{name}.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def purge_cli():
    return _load_script('purge_database')


def _prepare_env(cli, monkeypatch, env):
    """Create the table and bucket named as configure_environment expects, then seed the table"""
    for var in _ENV_VARS:  # restored at teardown
        monkeypatch.setenv(var, os.environ.get(var, ''))
    table_name = f'impressionnistes-registration-{env}'
    boto3.client('dynamodb', region_name=REGION).create_table(
        TableName=table_name,
        KeySchema=[{'AttributeName': 'PK', 'KeyType': 'HASH'},
                   {'AttributeName': 'SK', 'KeyType': 'RANGE'}],
        AttributeDefinitions=[{'AttributeName': 'PK', 'AttributeType': 'S'},
                              {'AttributeName': 'SK', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST')
    boto3.client('s3', region_name=REGION).create_bucket(
        Bucket=f'rcpm-impressionnistes-backups-{env}',
        CreateBucketConfiguration={'LocationConstraint': REGION})
    cli.configure_environment(env)
    assert os.environ['TABLE_NAME'] == table_name
    items, _, _ = _seed_items()
    put_typed_items(items)
    backup_service._dynamodb_client = None
    backup_service._s3_client = None


@pytest.fixture
def cli_env(purge_cli, backup_bucket, dynamodb_table, fake_clock, monkeypatch):
    _prepare_env(purge_cli, monkeypatch, 'dev')
    return purge_cli


@pytest.fixture
def cli_prod_env(purge_cli, backup_bucket, dynamodb_table, fake_clock, monkeypatch):
    _prepare_env(purge_cli, monkeypatch, 'prod')
    return purge_cli


def _no_prompt(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('input() must not be called')
    monkeypatch.setattr('builtins.input', forbidden)


def _type(monkeypatch, text):
    prompts = []

    def fake_input(prompt=''):
        prompts.append(prompt)
        return text
    monkeypatch.setattr('builtins.input', fake_input)
    return prompts


def _state():
    return items_by_key(backup_service.scan_table(), include_audit=True)


def _snapshot():
    return _state(), _s3_keys(), _native_names()


def _keys_of(prefix):
    return {k for k in _state() if k[0].startswith(prefix)}


# ---------------------------------------------------------------------------
# Selection and closure
# ---------------------------------------------------------------------------
@pytest.mark.parametrize('value, expected', [
    ('boats', ['boats']),
    ('crew,temp_access,audit_logs', ['crew', 'temp_access', 'audit_logs']),
    (' boats , payments ', ['boats', 'payments']),
])
def test_cli_parse_sets(purge_cli, value, expected):
    assert purge_cli.parse_sets(value) == expected


@pytest.mark.parametrize('value', ['', ',', 'nope', 'boats,nope'])
def test_cli_parse_sets_rejects_unknown(purge_cli, value):
    with pytest.raises(SystemExit):
        purge_cli.parse_sets(value)


@pytest.mark.parametrize('ids, selection, added', [
    (['boats'], ['payments', 'boats'], ['payments']),
    (['crew'], ['payments', 'boats', 'crew'], ['payments', 'boats']),
    (['payments'], ['payments'], []),
    (['managers'], ['payments', 'boats', 'crew', 'temp_access', 'managers'],
     ['payments', 'boats', 'crew', 'temp_access']),
    (['audit_logs'], ['audit_logs'], []),
    (SET_IDS, ['payments', 'boats', 'crew', 'temp_access', 'managers', 'audit_logs'], []),
])
def test_cli_resolves_closure(purge_cli, ids, selection, added):
    assert purge_cli.resolve_selection(ids) == (selection, added)


def test_cli_default_sets_is_boats_plus_payments(cli_env, capsys, monkeypatch):
    _no_prompt(monkeypatch)
    assert cli_env.main(['--env', 'dev', '--dry-run']) == 0
    out = capsys.readouterr().out
    assert 'Sets added by dependency rules: payments' in out
    assert 'Selection: payments, boats' in out


def test_cli_prints_added_sets_and_counts(cli_env, capsys, monkeypatch):
    _no_prompt(monkeypatch)
    assert cli_env.main(['--env', 'dev', '--sets', 'crew', '--dry-run']) == 0
    out = capsys.readouterr().out
    assert 'Sets added by dependency rules: payments, boats' in out
    # seed: 2 payments, 3 boats, 5 crew
    assert any(line.split()[:1] == ['payments'] and line.split()[-1] == '2'
               for line in out.splitlines())
    assert any(line.split()[:1] == ['boats'] and line.split()[-1] == '3'
               for line in out.splitlines())
    assert any(line.split()[:1] == ['crew'] and line.split()[-1] == '5'
               for line in out.splitlines())


# ---------------------------------------------------------------------------
# Property 14: a dry run changes nothing
# ---------------------------------------------------------------------------
@pytest.mark.parametrize('argv', [
    ['--dry-run'],
    ['--sets', 'crew,temp_access,audit_logs', '--dry-run'],
    ['--sets', 'managers', '--delete-cognito', '--dry-run'],
    ['--sets', 'payments,boats,crew,managers,temp_access,audit_logs', '--dry-run'],
], ids=['default', 'alias', 'managers-cognito', 'all'])
def test_cli_dry_run_changes_nothing(cli_env, cognito_pool, monkeypatch, argv):
    _no_prompt(monkeypatch)
    for sub in ('u1', 'u2'):
        cognito_pool.add_user(sub)
    monkeypatch.setattr(cli_env, 'get_user_pool_id', lambda env: os.environ['USER_POOL_ID'])
    before = _snapshot()
    users_before = cognito_pool.usernames()

    assert cli_env.main(['--env', 'dev'] + argv) == 0

    assert _snapshot() == before
    assert cognito_pool.usernames() == users_before
    assert _audit_records('reset_database') == []
    assert _s3_keys() == [] and _native_names() == []


def test_cli_dry_run_does_not_need_cognito_lookup(cli_env, monkeypatch):
    """--dry-run with --delete-cognito never resolves the user pool (no CloudFormation call)"""
    _no_prompt(monkeypatch)

    def forbidden(env):
        raise AssertionError('CloudFormation must not be called in a dry run')
    monkeypatch.setattr(cli_env, 'get_user_pool_id', forbidden)
    assert cli_env.main(['--env', 'dev', '--sets', 'managers', '--delete-cognito',
                         '--dry-run']) == 0


# ---------------------------------------------------------------------------
# Property 5 (CLI part): only the exact phrase authorizes a purge
# ---------------------------------------------------------------------------
@pytest.mark.parametrize('typed', ['', 'purger la base', 'PURGER LA BASE ', 'PURGE',
                                   'RESTAURER LA BASE', 'y'])
def test_cli_wrong_phrase_takes_no_backup_and_deletes_nothing(cli_env, monkeypatch, capsys, typed):
    prompts = _type(monkeypatch, typed)
    before = _snapshot()

    assert cli_env.main(['--env', 'dev', '--sets', 'crew']) == 0

    assert len(prompts) == 1 and 'PURGER LA BASE' in prompts[0]
    assert _snapshot() == before
    assert _s3_keys() == [] and _native_names() == []
    assert _audit_records('reset_database') == []
    assert 'Cancelled' in capsys.readouterr().out


def test_cli_exact_phrase_purges_with_backup(cli_env, monkeypatch, capsys):
    _type(monkeypatch, 'PURGER LA BASE')
    before = _state()

    assert cli_env.main(['--env', 'dev']) == 0

    after = _state()
    removed = {k for k in before if k not in after
               if k[0] != backup_service.AUDIT_PK}
    assert {k for k in removed if k[1].startswith('BOAT#')} == {
        ('TEAM#t1', 'BOAT#b1'), ('TEAM#t1', 'BOAT#b2'), ('TEAM#t2', 'BOAT#b3')}
    assert {k for k in removed if k[1].startswith('PAYMENT#')} == {
        ('TEAM#t1', 'PAYMENT#p1'), ('TEAM#t2', 'PAYMENT#p2')}
    assert len(removed) == 5  # nothing else was deleted
    backups = [k for k in _s3_keys() if k.startswith('safety-pre-reset_')]
    assert len(backups) == 1 and len(_native_names()) == 1
    assert 'Purge complete' in capsys.readouterr().out


# ---------------------------------------------------------------------------
# --backup-only
# ---------------------------------------------------------------------------
def test_cli_backup_only_creates_reset_backup_and_nothing_else(cli_env, monkeypatch, capsys):
    _no_prompt(monkeypatch)
    before_items = {k: v for k, v in _state().items() if k[0] != backup_service.AUDIT_PK}

    assert cli_env.main(['--env', 'dev', '--backup-only']) == 0

    keys = _s3_keys()
    assert len(keys) == 1 and keys[0].startswith('safety-pre-reset_')
    assert len(_native_names()) == 1
    assert 'safety-pre-reset_' in capsys.readouterr().out
    assert {k: v for k, v in _state().items() if k[0] != backup_service.AUDIT_PK} == before_items
    assert _audit_records('reset_database') == []


# ---------------------------------------------------------------------------
# Audit record
# ---------------------------------------------------------------------------
def test_cli_audit_record_has_lambda_fields_and_cli_identity(cli_env, monkeypatch):
    _type(monkeypatch, 'PURGER LA BASE')
    assert cli_env.main(['--env', 'dev', '--sets', 'crew']) == 0

    audit, = _audit_records('reset_database')
    assert audit['user_id'] == 'cli'
    assert audit['user_email'].startswith('cli:') and len(audit['user_email']) > 4
    details = audit['details']
    assert set(details) == {'outcome', 'sets', 'deleted', 'delete_cognito', 'cognito_deleted',
                            'cognito_failed', 'backup_taken', 'pre_reset_backup_id',
                            'environment'}
    assert details['outcome'] == 'success'
    assert details['sets'] == ['payments', 'boats', 'crew']
    assert details['deleted'] == {'payments': 2, 'boats': 3, 'crew': 5}
    assert details['backup_taken'] is True
    assert details['pre_reset_backup_id'].startswith('safety-pre-reset_')
    assert details['environment'] == 'dev'


def test_cli_audit_fields_match_lambda_execution(cli_env, monkeypatch):
    """Same code path: the CLI audit record has the same keys as one written for an admin user"""
    _type(monkeypatch, 'PURGER LA BASE')
    cli_env.main(['--env', 'dev', '--sets', 'temp_access'])
    reset_service.execute_reset(
        {'confirmation_phrase': 'PURGER LA BASE', 'sets': ['audit_logs']},
        {'user_id': 'u1', 'email': 'a@b.c'})
    records = _audit_records('reset_database')
    assert len(records) == 2
    assert set(records[0]['details']) == set(records[1]['details'])
    assert {r['user_id'] for r in records} == {'cli', 'u1'}


# ---------------------------------------------------------------------------
# Production: the backup is mandatory
# ---------------------------------------------------------------------------
def test_prod_without_backup_is_refused(cli_prod_env):
    assert os.environ['ENVIRONMENT'] == 'prod'
    assert os.environ['TABLE_NAME'] == 'impressionnistes-registration-prod'
    before = _snapshot()
    with pytest.raises(reset_service.BackupRequired) as raised:
        reset_service.execute_reset(
            {'confirmation_phrase': 'PURGER LA BASE', 'sets': ['boats', 'payments'],
             'backup_before': False},
            cli_prod_env.cli_user())
    assert raised.value.code == 'BACKUP_REQUIRED'
    assert _snapshot() == before
    assert _audit_records('reset_database') == []


def test_cli_prod_purge_always_takes_the_backup(cli_prod_env, monkeypatch):
    _type(monkeypatch, 'PURGER LA BASE')
    assert cli_prod_env.main(['--env', 'prod']) == 0

    assert [k for k in _s3_keys() if k.startswith('safety-pre-reset_')]
    audit, = _audit_records('reset_database')
    assert audit['details']['environment'] == 'prod'
    assert audit['details']['backup_taken'] is True


def test_cli_prod_wrong_phrase_changes_nothing(cli_prod_env, monkeypatch):
    _type(monkeypatch, 'PURGE')
    before = _snapshot()
    assert cli_prod_env.main(['--env', 'prod']) == 0
    assert _snapshot() == before


# ---------------------------------------------------------------------------
# Alias delete-all-data-keep-managers: SETS=crew,temp_access,audit_logs
# ---------------------------------------------------------------------------
def test_alias_set_list_keeps_managers(cli_env, monkeypatch):
    _type(monkeypatch, 'PURGER LA BASE')
    managers_before = {k: v for k, v in _state().items()
                       if k[0].startswith('USER#') and (k[1] == 'PROFILE'
                                                        or k[1].startswith('CONSENT#'))}
    assert len(managers_before) == 5

    assert cli_env.main(['--env', 'dev', '--sets', 'crew,temp_access,audit_logs']) == 0

    state = _state()
    for key, value in managers_before.items():
        assert state[key] == value
    assert not [k for k in state if k[1].startswith(('BOAT#', 'PAYMENT#', 'CREW#'))]
    assert not [k for k in state if k[0] == 'TEMP_ACCESS']
    assert not [k for k in state if k[0].startswith('AUDIT#') and k[0] != backup_service.AUDIT_PK]
    audit, = _audit_records('reset_database')
    assert audit['details']['sets'] == ['payments', 'boats', 'crew', 'temp_access', 'audit_logs']


# ---------------------------------------------------------------------------
# Cognito option
# ---------------------------------------------------------------------------
def test_cli_delete_cognito_requires_managers(cli_env, monkeypatch, capsys):
    _no_prompt(monkeypatch)
    before = _snapshot()
    assert cli_env.main(['--env', 'dev', '--sets', 'boats', '--delete-cognito']) == 1
    assert 'managers' in capsys.readouterr().out
    assert _snapshot() == before


def test_cli_delete_cognito_keeps_admins(cli_env, cognito_pool, monkeypatch):
    cognito_pool.add_user('u1')
    cognito_pool.add_user('u2')
    cognito_pool.add_user('u3', admin=True)
    monkeypatch.setattr(cli_env, 'get_user_pool_id', lambda env: os.environ['USER_POOL_ID'])
    _type(monkeypatch, 'PURGER LA BASE')

    assert cli_env.main(['--env', 'dev', '--sets', 'managers', '--delete-cognito']) == 0

    assert cognito_pool.usernames() == ['u3']
    audit, = _audit_records('reset_database')
    assert audit['details']['delete_cognito'] is True
    assert audit['details']['cognito_deleted'] == 2
    assert not _keys_of('USER#u1') - {('USER#u1', 'OTHER')}


def test_cli_wrong_phrase_with_cognito_deletes_no_account(cli_env, cognito_pool, monkeypatch):
    cognito_pool.add_user('u1')
    monkeypatch.setattr(cli_env, 'get_user_pool_id', lambda env: os.environ['USER_POOL_ID'])
    _type(monkeypatch, 'nope')
    before = _snapshot()

    assert cli_env.main(['--env', 'dev', '--sets', 'managers', '--delete-cognito']) == 0

    assert cognito_pool.usernames() == ['u1']
    assert _snapshot() == before


# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------
@pytest.mark.parametrize('env', ['dev', 'prod'])
def test_configure_environment_names(purge_cli, monkeypatch, env):
    for var in _ENV_VARS:
        monkeypatch.setenv(var, '')
    purge_cli.configure_environment(env)
    assert os.environ['ENVIRONMENT'] == env
    assert os.environ['TABLE_NAME'] == f'impressionnistes-registration-{env}'
    assert os.environ['BACKUP_BUCKET'] == f'rcpm-impressionnistes-backups-{env}'
    assert os.environ['AWS_DEFAULT_REGION'] == 'eu-west-3'


def test_configure_environment_reads_user_pool_only_when_needed(purge_cli, monkeypatch):
    for var in _ENV_VARS:
        monkeypatch.setenv(var, '')
    monkeypatch.setattr(purge_cli, 'get_user_pool_id', lambda env: f'pool-{env}')
    purge_cli.configure_environment('dev')
    assert os.environ['USER_POOL_ID'] == ''
    purge_cli.configure_environment('dev', need_cognito=True)
    assert os.environ['USER_POOL_ID'] == 'pool-dev'
# ---------------------------------------------------------------------------
# delete_team_manager.py and delete_admin.py (task 6.8)
# ---------------------------------------------------------------------------
_s = lambda value: {'S': value}  # noqa: E731


@pytest.fixture
def delete_admin_cli():
    return _load_script('delete_admin')


@pytest.fixture
def delete_tm_cli():
    return _load_script('delete_team_manager')


def _add_account(pool, email, admin=False):
    """Account whose Username is the email (as the scripts look it up); returns its sub"""
    pool.client.admin_create_user(
        UserPoolId=pool.pool_id, Username=email,
        UserAttributes=[{'Name': 'email', 'Value': email}], MessageAction='SUPPRESS')
    if admin:
        pool.client.admin_add_user_to_group(
            UserPoolId=pool.pool_id, Username=email, GroupName='admins')
    user = pool.client.admin_get_user(UserPoolId=pool.pool_id, Username=email)
    return next(a['Value'] for a in user['UserAttributes'] if a['Name'] == 'sub')


def _seed_account_items(sub):
    put_typed_items([
        {'PK': _s(f'USER#{sub}'), 'SK': _s('PROFILE')},
        {'PK': _s(f'USER#{sub}'), 'SK': _s('CONSENT#privacy')},
        {'PK': _s(f'TEAM#{sub}'), 'SK': _s('BOAT#mine')},
    ])


def _usernames(pool):
    return pool.usernames()


@pytest.fixture
def admin_env(purge_cli, cognito_pool, backup_bucket, dynamodb_table, fake_clock,
              delete_admin_cli, monkeypatch):
    """Dev table seeded, two admins (admin1 is the one deleted), one team manager"""
    _prepare_env(purge_cli, monkeypatch, 'dev')
    monkeypatch.setattr(delete_admin_cli.purge_database, 'configure_environment',
                        lambda *a, **k: None)
    subs = {
        'admin1': _add_account(cognito_pool, 'admin1@test.com', admin=True),
        'admin2': _add_account(cognito_pool, 'admin2@test.com', admin=True),
        'manager': _add_account(cognito_pool, 'manager@test.com'),
    }
    for sub in subs.values():
        _seed_account_items(sub)
    return cognito_pool, subs


def _run_admin(cli, monkeypatch, email, typed=None, extra=()):
    if typed is None:
        _no_prompt(monkeypatch)
    else:
        _type(monkeypatch, typed)
    return cli.main([email, '--env', 'dev', *extra])


def _no_delete_admin_audit():
    assert _audit_records('delete_admin') == []


def test_delete_admin_guards_unknown_email(delete_admin_cli, admin_env, monkeypatch, capsys):
    pool, subs = admin_env
    before = _snapshot()
    assert _run_admin(delete_admin_cli, monkeypatch, 'nobody@test.com') == 1
    assert 'No Cognito account' in capsys.readouterr().out
    assert _snapshot() == before
    assert len(_usernames(pool)) == 3
    _no_delete_admin_audit()


def test_delete_admin_guards_not_an_admin(delete_admin_cli, admin_env, monkeypatch, capsys):
    pool, subs = admin_env
    before = _snapshot()
    assert _run_admin(delete_admin_cli, monkeypatch, 'manager@test.com') == 1
    assert 'delete-team-manager' in capsys.readouterr().out
    assert _snapshot() == before
    assert 'manager@test.com' in _usernames(pool)
    _no_delete_admin_audit()


def test_delete_admin_guards_last_admin(delete_admin_cli, admin_env, monkeypatch, capsys):
    pool, subs = admin_env
    pool.client.admin_delete_user(UserPoolId=pool.pool_id, Username='admin2@test.com')
    before = _snapshot()
    assert _run_admin(delete_admin_cli, monkeypatch, 'admin1@test.com',
                      extra=['--with-profile']) == 1
    assert 'last administrator' in capsys.readouterr().out
    assert _snapshot() == before
    assert 'admin1@test.com' in _usernames(pool)
    _no_delete_admin_audit()


@pytest.mark.parametrize('with_profile', [False, True])
def test_delete_admin_guards_wrong_email_typed(delete_admin_cli, admin_env, monkeypatch, capsys,
                                               with_profile):
    pool, subs = admin_env
    before = _snapshot()
    extra = ['--with-profile'] if with_profile else []
    assert _run_admin(delete_admin_cli, monkeypatch, 'admin1@test.com',
                      typed='admin2@test.com', extra=extra) == 0
    assert 'No backup taken' in capsys.readouterr().out
    assert _snapshot() == before  # no backup object, no native backup, no item change
    assert 'admin1@test.com' in _usernames(pool)
    _no_delete_admin_audit()


def test_delete_admin_guards_group_check_failure(delete_admin_cli, admin_env, monkeypatch, capsys):
    pool, subs = admin_env
    before = _snapshot()

    def boom(*args, **kwargs):
        raise RuntimeError('cognito unavailable')
    monkeypatch.setattr(delete_admin_cli, 'is_admin', boom)
    assert _run_admin(delete_admin_cli, monkeypatch, 'admin1@test.com') == 1
    assert 'cognito unavailable' in capsys.readouterr().out
    assert _snapshot() == before
    assert len(_usernames(pool)) == 3
    _no_delete_admin_audit()


def test_delete_admin_guards_backup_failure(delete_admin_cli, admin_env, monkeypatch, capsys):
    pool, subs = admin_env
    before = _snapshot()

    def failing(*args, **kwargs):
        raise delete_admin_cli.backup_service.JsonBackupFailed('s3 down')
    monkeypatch.setattr(delete_admin_cli.backup_service, 'create_backup', failing)
    assert _run_admin(delete_admin_cli, monkeypatch, 'admin1@test.com',
                      typed='admin1@test.com', extra=['--with-profile']) == 1
    assert 'Nothing was modified' in capsys.readouterr().out
    assert _snapshot() == before
    assert 'admin1@test.com' in _usernames(pool)
    _no_delete_admin_audit()


def test_delete_admin_default_keeps_profile(delete_admin_cli, admin_env, monkeypatch):
    pool, subs = admin_env
    before_items = _state()
    s3_before = _s3_keys()
    prompts = _type(monkeypatch, 'admin1@test.com')
    assert delete_admin_cli.main(['Admin1@Test.com', '--env', 'dev']) == 0
    assert prompts
    assert _usernames(pool) == ['admin2@test.com', 'manager@test.com']
    after = _state()
    sub = subs['admin1']
    assert {k for k in after if k[0] == f'USER#{sub}'} == {
        (f'USER#{sub}', 'PROFILE'), (f'USER#{sub}', 'CONSENT#privacy')}
    assert _s3_keys() == s3_before  # no backup without --with-profile
    # only the audit record is new
    assert {k for k in after if k not in before_items and k[0] != backup_service.AUDIT_PK} == set()
    (record,) = _audit_records('delete_admin')
    assert record['details']['profile_deleted'] is False
    assert record['details']['sub'] == sub
    assert 'pre_reset_backup_id' not in record['details']


def test_delete_admin_with_profile(delete_admin_cli, admin_env, monkeypatch):
    pool, subs = admin_env
    sub = subs['admin1']
    before_items = _state()
    order = []
    real_create = backup_service.create_backup
    real_delete = delete_admin_cli.delete_profile_items

    def spy_create(*args, **kwargs):
        order.append('backup')
        return real_create(*args, **kwargs)

    def spy_delete(*args, **kwargs):
        # the backup exists before anything is deleted
        assert order == ['backup'] and len(_s3_keys()) == 1
        assert 'admin1@test.com' in _usernames(pool)
        order.append('profile')
        return real_delete(*args, **kwargs)
    monkeypatch.setattr(backup_service, 'create_backup', spy_create)
    monkeypatch.setattr(delete_admin_cli, 'delete_profile_items', spy_delete)
    _type(monkeypatch, 'admin1@test.com')
    assert delete_admin_cli.main(['admin1@test.com', '--env', 'dev', '--with-profile']) == 0
    assert order == ['backup', 'profile']
    (backup_id,) = _s3_keys()
    assert backup_id.startswith('safety-pre-reset')
    backed_up = items_by_key(backup_service.decode_items(
        json.loads(boto3.client('s3', region_name=REGION).get_object(
            Bucket=os.environ['BACKUP_BUCKET'], Key=backup_id)['Body'].read())['items']),
        include_audit=True)
    assert (f'USER#{sub}', 'PROFILE') in backed_up
    assert (f'USER#{sub}', 'CONSENT#privacy') in backed_up
    after = _state()
    assert _keys_of(f'USER#{sub}') == set()
    # everything else is untouched (TEAM# items of the admin included)
    expected = {k: v for k, v in before_items.items() if k[0] != f'USER#{sub}'}
    assert {k: v for k, v in after.items() if k[0] != backup_service.AUDIT_PK} == {
        k: v for k, v in expected.items() if k[0] != backup_service.AUDIT_PK}
    assert _usernames(pool) == ['admin2@test.com', 'manager@test.com']
    (record,) = _audit_records('delete_admin')
    assert record['details'] == {
        'sub': sub, 'email': 'admin1@test.com', 'environment': 'dev',
        'profile_deleted': True, 'profile_items_deleted': 2,
        'pre_reset_backup_id': backup_id}
    assert record['user_id'] == 'cli'


# --- delete_team_manager ----------------------------------------------------
@pytest.fixture
def tm_env(purge_cli, cognito_pool, backup_bucket, dynamodb_table, fake_clock,
           delete_tm_cli, monkeypatch):
    """Dev table seeded, CloudFormation faked, one admin and one team manager"""
    _prepare_env(purge_cli, monkeypatch, 'dev')
    pool_id = cognito_pool.pool_id

    class FakeCfn:
        def describe_stacks(self, StackName):
            return {'Stacks': [{'Outputs': [
                {'OutputKey': 'UserPoolId', 'OutputValue': pool_id}]}]}
    real_client = boto3.client

    def client(service, *args, **kwargs):
        return FakeCfn() if service == 'cloudformation' else real_client(service, *args, **kwargs)
    monkeypatch.setattr(boto3, 'client', client)
    subs = {'admin': _add_account(cognito_pool, 'boss@test.com', admin=True),
            'manager': _add_account(cognito_pool, 'manager@test.com')}
    for sub in subs.values():
        _seed_account_items(sub)
    return cognito_pool, subs


def _run_tm(cli, monkeypatch, email):
    monkeypatch.setattr('sys.argv', ['delete_team_manager.py', email, '--yes'])
    with pytest.raises(SystemExit) as exc:
        cli.main()
        raise SystemExit(0)
    return exc.value.code


def test_delete_team_manager_refuses_admin(delete_tm_cli, tm_env, monkeypatch, capsys):
    pool, subs = tm_env
    before = _snapshot()
    assert _run_tm(delete_tm_cli, monkeypatch, 'boss@test.com') == 1
    assert 'cognito-delete-admin' in capsys.readouterr().out
    assert _snapshot() == before
    assert 'boss@test.com' in _usernames(pool)


def test_delete_team_manager_fails_closed_when_group_check_fails(delete_tm_cli, tm_env,
                                                                  monkeypatch, capsys):
    pool, subs = tm_env
    before = _snapshot()

    def boom(*args, **kwargs):
        raise RuntimeError('cognito unavailable')
    monkeypatch.setattr(delete_tm_cli, 'is_admin', boom)
    assert _run_tm(delete_tm_cli, monkeypatch, 'manager@test.com') == 1
    assert 'Nothing was deleted' in capsys.readouterr().out
    assert _snapshot() == before
    assert 'manager@test.com' in _usernames(pool)


def test_delete_team_manager_still_deletes_plain_manager(delete_tm_cli, tm_env, monkeypatch):
    pool, subs = tm_env
    sub = subs['manager']
    before = _state()
    assert _run_tm(delete_tm_cli, monkeypatch, 'manager@test.com') == 0
    assert _usernames(pool) == ['boss@test.com']
    after = _state()
    assert _keys_of(f'USER#{sub}') == set() and _keys_of(f'TEAM#{sub}') == set()
    assert after == {k: v for k, v in before.items()
                     if k[0] not in (f'USER#{sub}', f'TEAM#{sub}')}


def test_is_admin_paginates_and_raises(delete_tm_cli):
    class Client:
        def __init__(self):
            self.calls = 0

        def admin_list_groups_for_user(self, **kwargs):
            self.calls += 1
            if self.calls == 1:
                assert 'NextToken' not in kwargs
                return {'Groups': [{'GroupName': 'x'}], 'NextToken': 't'}
            assert kwargs['NextToken'] == 't'
            return {'Groups': [{'GroupName': 'admins'}]}
    assert delete_tm_cli.is_admin(Client(), 'pool', 'a@b.c') is True

    class Broken:
        def admin_list_groups_for_user(self, **kwargs):
            raise RuntimeError('x')
    with pytest.raises(RuntimeError):
        delete_tm_cli.is_admin(Broken(), 'pool', 'a@b.c')
