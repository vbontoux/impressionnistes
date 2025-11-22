"""
Secrets Stack - AWS Secrets Manager
Course des Impressionnistes Registration System

This stack creates and manages all secrets in AWS Secrets Manager.
Secrets are read from secrets.json file (not committed to git).
"""
from aws_cdk import (
    Stack,
    RemovalPolicy,
    SecretValue,
    aws_secretsmanager as secretsmanager,
    CfnOutput
)
from constructs import Construct
import json
from pathlib import Path


class SecretsStack(Stack):
    """
    Stack for managing application secrets in AWS Secrets Manager.
    Reads secrets from secrets.json and creates corresponding AWS secrets.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get environment from context
        env_name = self.node.try_get_context("env") or "dev"
        
        # Load secrets from secrets.json
        secrets_data = self._load_secrets()
        
        # Create Stripe API key secret
        self._create_stripe_api_key_secret(secrets_data, env_name)
        
        # Create Stripe webhook secret
        self._create_stripe_webhook_secret(secrets_data, env_name)
        
        # Create Slack webhook secrets
        self._create_slack_webhook_secrets(secrets_data)
        
        # Output summary
        CfnOutput(
            self,
            "SecretsCreated",
            value=f"Secrets created for environment: {env_name}",
            description="Secrets Stack Status"
        )
    
    def _load_secrets(self) -> dict:
        """
        Load secrets from secrets.json file
        
        Returns:
            Dictionary of secrets
        
        Raises:
            FileNotFoundError: If secrets.json doesn't exist
            json.JSONDecodeError: If secrets.json is invalid
        """
        secrets_file = Path(__file__).parent.parent / "secrets.json"
        
        if not secrets_file.exists():
            raise FileNotFoundError(
                f"secrets.json not found at {secrets_file}\n"
                "Please create secrets.json from secrets.json.example"
            )
        
        try:
            with open(secrets_file, 'r') as f:
                secrets = json.load(f)
            
            print(f"✓ Loaded secrets from {secrets_file}")
            return secrets
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in secrets.json: {str(e)}",
                e.doc,
                e.pos
            )
    
    def _create_stripe_api_key_secret(self, secrets_data: dict, env_name: str):
        """
        Create Stripe API key secret in AWS Secrets Manager
        
        Args:
            secrets_data: Dictionary of secrets from secrets.json
            env_name: Environment name (dev or prod)
        """
        # Get the appropriate key based on environment
        secret_key_name = f"stripe_secret_key_{env_name}"
        
        if secret_key_name not in secrets_data:
            print(f"⚠ Warning: {secret_key_name} not found in secrets.json")
            return
        
        stripe_api_key = secrets_data[secret_key_name]
        
        # Validate key format
        expected_prefix = "sk_test_" if env_name == "dev" else "sk_live_"
        if not stripe_api_key.startswith(expected_prefix):
            print(f"⚠ Warning: Stripe API key should start with {expected_prefix}")
        
        # Create secret
        self.stripe_api_key_secret = secretsmanager.Secret(
            self,
            "StripeApiKeySecret",
            secret_name=f"impressionnistes/stripe/api_key",
            description=f"Stripe API key for Course des Impressionnistes ({env_name})",
            secret_object_value={
                "api_key": SecretValue.unsafe_plain_text(stripe_api_key)
            },
            removal_policy=RemovalPolicy.RETAIN  # Keep secrets when stack is deleted
        )
        
        CfnOutput(
            self,
            "StripeApiKeySecretArn",
            value=self.stripe_api_key_secret.secret_arn,
            description="Stripe API Key Secret ARN",
            export_name=f"StripeApiKeySecretArn-{env_name}"
        )
        
        print(f"✓ Created Stripe API key secret for {env_name}")
    
    def _create_stripe_webhook_secret(self, secrets_data: dict, env_name: str):
        """
        Create Stripe webhook secret in AWS Secrets Manager
        
        Args:
            secrets_data: Dictionary of secrets from secrets.json
            env_name: Environment name (dev or prod)
        """
        # Get the appropriate webhook secret based on environment
        webhook_secret_name = f"stripe_webhook_secret_{env_name}"
        
        if webhook_secret_name not in secrets_data:
            print(f"⚠ Warning: {webhook_secret_name} not found in secrets.json")
            return
        
        webhook_secret = secrets_data[webhook_secret_name]
        
        # Validate webhook secret format
        if not webhook_secret.startswith("whsec_"):
            print(f"⚠ Warning: Stripe webhook secret should start with whsec_")
        
        # Create secret
        self.stripe_webhook_secret = secretsmanager.Secret(
            self,
            "StripeWebhookSecret",
            secret_name=f"impressionnistes/stripe/webhook_secret",
            description=f"Stripe webhook signing secret ({env_name})",
            secret_object_value={
                "webhook_secret": SecretValue.unsafe_plain_text(webhook_secret)
            },
            removal_policy=RemovalPolicy.RETAIN
        )
        
        CfnOutput(
            self,
            "StripeWebhookSecretArn",
            value=self.stripe_webhook_secret.secret_arn,
            description="Stripe Webhook Secret ARN",
            export_name=f"StripeWebhookSecretArn-{env_name}"
        )
        
        print(f"✓ Created Stripe webhook secret for {env_name}")
    
    def _create_slack_webhook_secrets(self, secrets_data: dict):
        """
        Create Slack webhook secrets in AWS Secrets Manager
        
        Args:
            secrets_data: Dictionary of secrets from secrets.json
        """
        # Admin Slack webhook
        if "slack_webhook_admin" in secrets_data:
            slack_admin_url = secrets_data["slack_webhook_admin"]
            
            if slack_admin_url and not slack_admin_url.startswith("https://hooks.slack.com/"):
                print(f"⚠ Warning: Slack admin webhook URL format looks incorrect")
            
            self.slack_admin_webhook_secret = secretsmanager.Secret(
                self,
                "SlackAdminWebhookSecret",
                secret_name="impressionnistes/slack/admin_webhook",
                description="Slack webhook URL for admin notifications",
                secret_object_value={
                    "webhook_url": SecretValue.unsafe_plain_text(slack_admin_url)
                },
                removal_policy=RemovalPolicy.RETAIN
            )
            
            CfnOutput(
                self,
                "SlackAdminWebhookSecretArn",
                value=self.slack_admin_webhook_secret.secret_arn,
                description="Slack Admin Webhook Secret ARN"
            )
            
            print(f"✓ Created Slack admin webhook secret")
        else:
            print(f"⚠ Warning: slack_webhook_admin not found in secrets.json")
        
        # DevOps Slack webhook
        if "slack_webhook_devops" in secrets_data:
            slack_devops_url = secrets_data["slack_webhook_devops"]
            
            if slack_devops_url and not slack_devops_url.startswith("https://hooks.slack.com/"):
                print(f"⚠ Warning: Slack devops webhook URL format looks incorrect")
            
            self.slack_devops_webhook_secret = secretsmanager.Secret(
                self,
                "SlackDevOpsWebhookSecret",
                secret_name="impressionnistes/slack/devops_webhook",
                description="Slack webhook URL for DevOps notifications",
                secret_object_value={
                    "webhook_url": SecretValue.unsafe_plain_text(slack_devops_url)
                },
                removal_policy=RemovalPolicy.RETAIN
            )
            
            CfnOutput(
                self,
                "SlackDevOpsWebhookSecretArn",
                value=self.slack_devops_webhook_secret.secret_arn,
                description="Slack DevOps Webhook Secret ARN"
            )
            
            print(f"✓ Created Slack devops webhook secret")
        else:
            print(f"⚠ Warning: slack_webhook_devops not found in secrets.json")
