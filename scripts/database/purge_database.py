#!/usr/bin/env python3
"""
Fallback command-line purge of the registration table.

Applies the same rules as the admin page "Database reset": same purge sets,
dependency closure, protected data, Pre_Reset_Backup, Cognito admin exclusion,
partial-failure handling and `reset_database` audit record. All the logic lives
in functions/shared/reset_service.py (imported, not duplicated).

Run through the Makefile:
    cd infrastructure
    make db-purge ENV=dev SETS=boats
    make db-purge ENV=dev SETS=crew,temp_access DELETE_COGNITO=1
    make db-purge ENV=dev DRY_RUN=1

Sets: boats, payments, crew, managers, temp_access, audit_logs (default: boats).
Required sets are added automatically (e.g. boats implies payments).
"""
import argparse
import getpass
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'functions', 'shared'))

import boto3  # noqa: E402
from botocore.exceptions import ClientError  # noqa: E402

import backup_service  # noqa: E402
import reset_service  # noqa: E402

REGION = 'eu-west-3'


def cli_user():
    """Identity recorded in the backup and audit records"""
    return {'user_id': 'cli', 'email': f'cli:{getpass.getuser()}'}


def get_user_pool_id(env):
    """UserPoolId output of the ImpressionnistesAuth-{env} stack"""
    stack_name = f'ImpressionnistesAuth-{env}'
    cfn = boto3.client('cloudformation', region_name=REGION)
    try:
        stacks = cfn.describe_stacks(StackName=stack_name).get('Stacks', [])
    except ClientError as e:
        raise RuntimeError(
            f"Cannot read stack {stack_name} ({e}). Is the {env} environment deployed?")
    if not stacks:
        raise RuntimeError(f'Stack {stack_name} not found')
    for output in stacks[0].get('Outputs', []):
        if output['OutputKey'] == 'UserPoolId':
            return output['OutputValue']
    raise RuntimeError('UserPoolId output not found in stack')


def configure_environment(env, need_cognito=False):
    """Set the environment variables read by backup_service and reset_service"""
    os.environ['ENVIRONMENT'] = env
    os.environ['TABLE_NAME'] = f'impressionnistes-registration-{env}'
    os.environ['BACKUP_BUCKET'] = f'rcpm-impressionnistes-backups-{env}'
    os.environ['AWS_DEFAULT_REGION'] = REGION
    if need_cognito:
        os.environ['USER_POOL_ID'] = get_user_pool_id(env)


def parse_sets(value):
    """'a,b' -> list of known ids (SystemExit on unknown id)"""
    ids = [s.strip() for s in value.split(',') if s.strip()]
    unknown = sorted(set(ids) - set(reset_service.PURGE_SETS))
    if not ids or unknown:
        raise SystemExit(
            f"Invalid --sets (unknown: {unknown or 'none given'}). "
            f"Valid: {', '.join(reset_service.PURGE_ORDER)}")
    return ids


def resolve_selection(ids):
    """Closure of the requested ids, in purge order, and the ids added"""
    closed = reset_service.resolve_closure(ids)
    ordered = [s for s in reset_service.PURGE_ORDER if s in closed]
    added = [s for s in ordered if s not in set(ids)]
    return ordered, added


def print_counts(selection, counts):
    print('\nItems per set:')
    for set_id in selection:
        label = reset_service.PURGE_SETS[set_id]['label']
        print(f'  {set_id:<12} {label:<20} {counts.get(set_id, 0)}')
    print(f'  {"total":<33}{sum(counts.get(s, 0) for s in selection)}')


def print_error(e):
    print(f'\n❌ {getattr(e, "code", "ERROR")}: {e}')
    details = getattr(e, 'details', None)
    if details:
        print(f'   details: {details}')


def run(args):
    ids = parse_sets(args.sets)
    selection, added = resolve_selection(ids)

    if args.delete_cognito and not args.backup_only and 'managers' not in selection:
        print("❌ --delete-cognito requires the 'managers' set")
        return 1

    configure_environment(args.env, need_cognito=args.delete_cognito and not args.dry_run)

    print(f"\n{'=' * 60}")
    print(f'Database purge - environment: {args.env}')
    print(f"Table: {os.environ['TABLE_NAME']}")
    print(f"{'=' * 60}")

    if args.backup_only:
        try:
            result = backup_service.create_backup(backup_service.CATEGORY_RESET, cli_user())
        except backup_service.BackupError as e:
            print_error(e)
            return 1
        print(f"✅ Backup created: {result['backup_id']}")
        return 0

    if added:
        print(f"Sets added by dependency rules: {', '.join(added)}")
    print(f"Selection: {', '.join(selection)}")

    counts, cognito_max = reset_service.compute_item_counts()
    print_counts(selection, counts)
    if args.delete_cognito:
        print(f'Cognito accounts: up to {cognito_max} (admins are never deleted)')

    if args.dry_run:
        print('\nDry run: nothing backed up, deleted or audited.')
        return 0

    print('\n⚠️  This permanently deletes the items above. '
          'A safety-pre-reset backup is taken first.')
    typed = input(f"Type '{reset_service.CONFIRMATION_PHRASE}' to confirm: ")
    if typed != reset_service.CONFIRMATION_PHRASE:
        print('Cancelled. No backup taken, nothing deleted.')
        return 0

    body = {
        'sets': selection,
        'delete_cognito': args.delete_cognito,
        'backup_before': True,
        'confirmation_phrase': typed,
    }
    try:
        result = reset_service.execute_reset(body, cli_user())
    except backup_service.BackupError as e:
        print_error(e)
        return 1

    print('\n✅ Purge complete')
    for set_id, n in result['deleted'].items():
        print(f'  {set_id:<12} {n}')
    print(f"  total        {result['total_deleted']}")
    if result['pre_reset_backup']:
        print(f"Backup: {result['pre_reset_backup']['backup_id']}")
    cog = result['cognito']
    if cog['requested']:
        print(f"Cognito: deleted={cog['deleted']} skipped_admins={cog['skipped_admins']} "
              f"not_found={cog['not_found']} failed={len(cog['failed'])}")
    if not result['audit_written']:
        print('⚠ Audit record could not be written')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description='Selective purge of the registration table')
    parser.add_argument('--env', choices=['dev', 'prod'], default='dev')
    parser.add_argument('--sets', default='boats',
                        help='Comma-separated purge sets (default: boats)')
    parser.add_argument('--delete-cognito', action='store_true',
                        help="Also delete the managers' Cognito accounts (admins excluded)")
    parser.add_argument('--dry-run', action='store_true',
                        help='Show item counts only; change nothing')
    parser.add_argument('--backup-only', action='store_true',
                        help='Only create a safety-pre-reset backup')
    args = parser.parse_args(argv)
    try:
        return run(args)
    except RuntimeError as e:
        print(f'❌ {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
