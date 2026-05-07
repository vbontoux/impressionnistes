"""
Unit tests for S3-based secrets manager module
Tests secret retrieval, caching, and error handling
"""
import json
import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO

# Test constants
TEST_BUCKET = 'test-secrets-bucket'


def _make_s3_response(body_dict):
    """Create a mock S3 GetObject response"""
    body_bytes = json.dumps(body_dict).encode('utf-8')
    return {'Body': BytesIO(body_bytes)}


@pytest.fixture(autouse=True)
def setup_env_and_module():
    """Set up environment and reset module state for each test"""
    os.environ['SECRETS_BUCKET'] = TEST_BUCKET
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-3'
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'

    # Remove cached module to force fresh import
    for mod_name in list(sys.modules.keys()):
        if mod_name == 'secrets_manager':
            del sys.modules[mod_name]

    yield

    os.environ.pop('SECRETS_BUCKET', None)
    for mod_name in list(sys.modules.keys()):
        if mod_name == 'secrets_manager':
            del sys.modules[mod_name]


def _get_module_with_mock():
    """Import secrets_manager and inject a mock S3 client"""
    import secrets_manager
    mock_s3 = MagicMock()
    secrets_manager._s3_client = mock_s3
    secrets_manager.clear_cache()
    return secrets_manager, mock_s3


class TestGetStripeApiKey:
    """Test get_stripe_api_key function"""

    def test_returns_correct_value(self):
        sm, mock_s3 = _get_module_with_mock()
        mock_s3.get_object.return_value = _make_s3_response({'api_key': 'sk_test_abc123'})

        result = sm.get_stripe_api_key()

        assert result == 'sk_test_abc123'
        mock_s3.get_object.assert_called_once_with(Bucket=TEST_BUCKET, Key='stripe/api_key')


class TestGetStripeWebhookSecret:
    """Test get_stripe_webhook_secret function"""

    def test_returns_correct_value(self):
        sm, mock_s3 = _get_module_with_mock()
        mock_s3.get_object.return_value = _make_s3_response({'webhook_secret': 'whsec_xyz789'})

        result = sm.get_stripe_webhook_secret()

        assert result == 'whsec_xyz789'
        mock_s3.get_object.assert_called_once_with(Bucket=TEST_BUCKET, Key='stripe/webhook_secret')


class TestGetSlackAdminWebhook:
    """Test get_slack_admin_webhook function"""

    def test_returns_correct_value(self):
        sm, mock_s3 = _get_module_with_mock()
        mock_s3.get_object.return_value = _make_s3_response(
            {'webhook_url': 'https://hooks.slack.com/services/T00/B00/admin'}
        )

        result = sm.get_slack_admin_webhook()

        assert result == 'https://hooks.slack.com/services/T00/B00/admin'
        mock_s3.get_object.assert_called_once_with(Bucket=TEST_BUCKET, Key='slack/admin_webhook')

    def test_returns_empty_string_on_error(self):
        sm, mock_s3 = _get_module_with_mock()
        mock_s3.get_object.side_effect = Exception('NoSuchKey')

        result = sm.get_slack_admin_webhook()

        assert result == ''


class TestGetSlackDevopsWebhook:
    """Test get_slack_devops_webhook function"""

    def test_returns_correct_value(self):
        sm, mock_s3 = _get_module_with_mock()
        mock_s3.get_object.return_value = _make_s3_response(
            {'webhook_url': 'https://hooks.slack.com/services/T00/B00/devops'}
        )

        result = sm.get_slack_devops_webhook()

        assert result == 'https://hooks.slack.com/services/T00/B00/devops'
        mock_s3.get_object.assert_called_once_with(Bucket=TEST_BUCKET, Key='slack/devops_webhook')

    def test_returns_empty_string_on_error(self):
        sm, mock_s3 = _get_module_with_mock()
        mock_s3.get_object.side_effect = Exception('NoSuchKey')

        result = sm.get_slack_devops_webhook()

        assert result == ''


class TestCaching:
    """Test caching behavior"""

    def test_caching_prevents_duplicate_s3_calls(self):
        sm, mock_s3 = _get_module_with_mock()
        mock_s3.get_object.return_value = _make_s3_response({'api_key': 'sk_test_cached'})

        # First call — hits S3
        result1 = sm.get_stripe_api_key()
        assert result1 == 'sk_test_cached'

        # Second call — should use cache, not call S3 again
        result2 = sm.get_stripe_api_key()
        assert result2 == 'sk_test_cached'

        # S3 should only have been called once
        assert mock_s3.get_object.call_count == 1

    def test_clear_cache_resets_state(self):
        sm, mock_s3 = _get_module_with_mock()

        # First call returns v1
        mock_s3.get_object.return_value = _make_s3_response({'api_key': 'sk_test_v1'})
        result1 = sm.get_stripe_api_key()
        assert result1 == 'sk_test_v1'

        # Update mock to return v2
        mock_s3.get_object.return_value = _make_s3_response({'api_key': 'sk_test_v2'})

        # Without clearing cache, still returns v1
        result_cached = sm.get_stripe_api_key()
        assert result_cached == 'sk_test_v1'

        # Clear cache and call again — should get v2
        sm.clear_cache()
        result2 = sm.get_stripe_api_key()
        assert result2 == 'sk_test_v2'


class TestErrorHandling:
    """Test error handling"""

    def test_s3_error_raises_exception_for_stripe(self):
        sm, mock_s3 = _get_module_with_mock()
        mock_s3.get_object.side_effect = Exception('NoSuchKey')

        with pytest.raises(Exception):
            sm.get_stripe_api_key()

    def test_reads_bucket_from_env_var(self):
        sm, mock_s3 = _get_module_with_mock()
        mock_s3.get_object.return_value = _make_s3_response({'api_key': 'sk_from_bucket'})

        # Change env var
        os.environ['SECRETS_BUCKET'] = 'other-bucket'
        sm.clear_cache()

        sm.get_stripe_api_key()

        mock_s3.get_object.assert_called_with(Bucket='other-bucket', Key='stripe/api_key')


class TestPublicApi:
    """Test that the public API surface is correct"""

    def test_public_api_unchanged(self):
        sm, _ = _get_module_with_mock()
        assert callable(sm.get_stripe_api_key)
        assert callable(sm.get_stripe_webhook_secret)
        assert callable(sm.get_slack_admin_webhook)
        assert callable(sm.get_slack_devops_webhook)
        assert callable(sm.clear_cache)
        assert callable(sm.get_secret)

    def test_uses_lazy_s3_client(self):
        sm, mock_s3 = _get_module_with_mock()
        # The _get_s3_client function should exist
        assert callable(sm._get_s3_client)


class TestSecretRoundTrip:
    """Test round-trip property: store → retrieve → parse = original value"""

    @pytest.mark.parametrize("secret_value", [
        "sk_test_abc123",
        "whsec_xyz789",
        "https://hooks.slack.com/services/T00/B00/xxx",
        "value with spaces and spécial chars: é à ü ñ 中文",
        'value with "quotes" and \\backslashes',
        "value with JSON chars: {\"key\": \"val\"}",
        "a" * 10000,
        "simple",
    ])
    def test_round_trip_with_various_values(self, secret_value):
        sm, mock_s3 = _get_module_with_mock()

        # Simulate what the Makefile secrets-sync would store
        stored_json = json.dumps({"test_field": secret_value})
        mock_s3.get_object.return_value = {
            'Body': BytesIO(stored_json.encode('utf-8'))
        }

        result = sm.get_secret("test/key", "test_field")

        assert result == secret_value
