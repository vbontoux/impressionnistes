"""
Fixtures shared by the backup/restore and database reset integration tests.

tests/conftest.py (parent) still provides aws_credentials, dynamodb_table, etc.
"""
import os

import boto3
import pytest
from moto import mock_cognitoidp, mock_s3

import backup_service
import reset_service
from tests.integration.backup_helpers import BUCKET_NAME, REGION


@pytest.fixture(autouse=True)
def reset_backup_clients():
    """Cached boto3 clients must be rebuilt inside each test's moto mock"""
    backup_service._dynamodb_client = None
    backup_service._s3_client = None
    reset_service._cognito_client = None
    yield
    backup_service._dynamodb_client = None
    backup_service._s3_client = None
    reset_service._cognito_client = None


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


class CognitoPool:
    """Moto user pool with an `admins` group; users are created with Username=<sub>"""

    def __init__(self, client, pool_id):
        self.client = client
        self.pool_id = pool_id

    def add_user(self, sub, email=None, admin=False):
        self.client.admin_create_user(
            UserPoolId=self.pool_id, Username=sub,
            UserAttributes=[{'Name': 'email', 'Value': email or f'{sub}@test.com'}],
            MessageAction='SUPPRESS')
        if admin:
            self.client.admin_add_user_to_group(
                UserPoolId=self.pool_id, Username=sub, GroupName='admins')
        return sub

    def usernames(self):
        users = self.client.list_users(UserPoolId=self.pool_id)['Users']
        return sorted(u['Username'] for u in users)


@pytest.fixture
def cognito_pool(aws_credentials):
    """Moto Cognito pool with the `admins` group; sets USER_POOL_ID"""
    with mock_cognitoidp():
        client = boto3.client('cognito-idp', region_name=REGION)
        pool_id = client.create_user_pool(PoolName='test-pool')['UserPool']['Id']
        client.create_group(UserPoolId=pool_id, GroupName='admins')
        os.environ['USER_POOL_ID'] = pool_id
        try:
            yield CognitoPool(client, pool_id)
        finally:
            os.environ.pop('USER_POOL_ID', None)
