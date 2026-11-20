#!/usr/bin/env python3
"""
Delete an admin account (Cognito) from the command line.

Checks, in order (each one stops without modifying anything):
  1. the Cognito account exists
  2. it is a member of the `admins` group (team managers: use delete-team-manager)
  3. it is not the last member of `admins`
  4. the operator types the email address exactly

By default only the Cognito account is deleted and the admin's profile items
(USER#<sub>: PROFILE and CONSENT#...) stay in the table. With --with-profile a
safety-pre-reset backup is taken first (failure aborts everything), then the
USER#<sub> items are deleted, then the Cognito account.
A `delete_admin` audit record is written at the end.

The production confirmation ('DELETE ADMIN PROD') is asked by the Makefile target.

Run through the Makefile:
    cd infrastructure
    make cognito-delete-admin EMAIL=admin@example.com ENV=dev
    make cognito-delete-admin EMAIL=admin@example.com ENV=dev WITH_PROFILE=1
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import boto3  # noqa: E402
from botocore.exceptions import ClientError  # noqa: E402

import purge_database  # noqa: E402  (configure_environment, cli_user)
from delete_team_manager import is_admin  # noqa: E402

import backup_service  # noqa: E402  (functions/shared is put on sys.path by purge_database)

ADMINS_GROUP = 'admins'


def get_account(cognito, pool_id, username):
    """(sub, email) of the account, or None when it does not exist"""
    try:
        response = cognito.admin_get_user(UserPoolId=pool_id, Username=username)
    except ClientError as e:
        if e.response['Error']['Code'] == 'UserNotFoundException':
            return None
        raise
    attrs = {a['Name']: a['Value'] for a in response.get('UserAttributes', [])}
    return attrs.get('sub'), attrs.get('email', username)


def get_groups(cognito, pool_id, username):
    """Names of the groups of the account"""
    groups = []
    kwargs = {'UserPoolId': pool_id, 'Username': username}
    while True:
        response = cognito.admin_list_groups_for_user(**kwargs)
        groups.extend(g['GroupName'] for g in response.get('Groups', []))
        token = response.get('NextToken')
        if not token:
            return groups
        kwargs['NextToken'] = token


def count_admins(cognito, pool_id):
    """Number of members of the admins group (paginated)"""
    total = 0
    kwargs = {'UserPoolId': pool_id, 'GroupName': ADMINS_GROUP}
    while True:
        response = cognito.list_users_in_group(**kwargs)
        total += len(response.get('Users', []))
        token = response.get('NextToken')
        if not token:
            return total
        kwargs['NextToken'] = token


def delete_profile_items(table, sub):
    """Delete every item with PK = USER#<sub> in chunks of 25; return the count"""
    pk = f'USER#{sub}'
    keys = []
    kwargs = {'KeyConditionExpression': 'PK = :pk', 'ExpressionAttributeValues': {':pk': pk}}
    while True:
        response = table.query(**kwargs)
        keys.extend({'PK': {'S': i['PK']}, 'SK': {'S': i['SK']}} for i in response.get('Items', []))
        last = response.get('LastEvaluatedKey')
        if not last:
            break
        kwargs['ExclusiveStartKey'] = last
    table_name = table.name
    for start in range(0, len(keys), backup_service.BATCH_SIZE):
        chunk = keys[start:start + backup_service.BATCH_SIZE]
        backup_service.batch_write_with_retry(
            {table_name: [{'DeleteRequest': {'Key': k}} for k in chunk]})
    return len(keys)


def run(args):
    email = args.email.strip().lower()
    env = args.env

    purge_database.configure_environment(env, need_cognito=True)
    pool_id = os.environ['USER_POOL_ID']
    cognito = boto3.client('cognito-idp', region_name=purge_database.REGION)

    print(f"\n{'=' * 60}")
    print(f'Delete admin account - environment: {env}')
    print(f"{'=' * 60}")

    account = get_account(cognito, pool_id, email)
    if account is None:
        print(f'❌ No Cognito account for {email}. Nothing was modified.')
        return 1
    sub, account_email = account

    if not is_admin(cognito, pool_id, email):
        print(f'❌ {account_email} is not an administrator. Refusing.')
        print('   Team managers are deleted with `make delete-team-manager`. Nothing was modified.')
        return 1

    if count_admins(cognito, pool_id) <= 1:
        print(f'❌ {account_email} is the last administrator. Deleting it would leave '
              'no admin able to log in. Nothing was modified.')
        return 1

    groups = get_groups(cognito, pool_id, email)
    print(f'Email:       {account_email}')
    print(f"Groups:      {', '.join(groups)}")
    print(f'Environment: {env}')
    print(f"Profile items: {'will be deleted (after a backup)' if args.with_profile else 'kept'}")

    typed = input('\nType the email address exactly to confirm: ')
    if typed != account_email:
        print('Cancelled. No backup taken, nothing deleted.')
        return 0

    backup_id = None
    items_deleted = 0
    if args.with_profile:
        try:
            result = backup_service.create_backup(backup_service.CATEGORY_RESET,
                                                  purge_database.cli_user())
        except backup_service.BackupError as e:
            print(f'❌ Backup failed ({getattr(e, "code", "ERROR")}): {e}')
            print('   Nothing was modified.')
            return 1
        backup_id = result['backup_id']
        print(f'Backup created: {backup_id}')
        table = boto3.resource('dynamodb', region_name=purge_database.REGION).Table(
            os.environ['TABLE_NAME'])
        items_deleted = delete_profile_items(table, sub)

    cognito.admin_delete_user(UserPoolId=pool_id, Username=email)

    written = backup_service.write_audit('delete_admin', purge_database.cli_user(), {
        'sub': sub,
        'email': account_email,
        'environment': env,
        'profile_deleted': bool(args.with_profile),
        'profile_items_deleted': items_deleted,
        'pre_reset_backup_id': backup_id,
    })
    if not written:
        print('⚠ Audit record could not be written')

    print(f'\n✅ Cognito account deleted: {account_email}')
    print(f'Profile items deleted: {items_deleted}')
    if backup_id:
        print(f'Backup: {backup_id}')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description='Delete an admin account')
    parser.add_argument('email', help='Email address of the admin account')
    parser.add_argument('--env', choices=['dev', 'prod'], default='dev')
    parser.add_argument('--with-profile', action='store_true',
                        help='Back up, then also delete the USER#<sub> profile items')
    args = parser.parse_args(argv)
    try:
        return run(args)
    except (RuntimeError, ClientError) as e:
        print(f'❌ {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
