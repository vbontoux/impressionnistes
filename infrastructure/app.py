#!/usr/bin/env python3
"""
AWS CDK App Entry Point
Course des Impressionnistes Registration System
"""
import os
from aws_cdk import App, Environment, Tags

# Import stacks
from stacks.database_stack import DatabaseStack
from stacks.api_stack import ApiStack
from stacks.frontend_stack import FrontendStack
from stacks.monitoring_stack import MonitoringStack
from stacks.auth_stack import AuthStack
from stacks.secrets_stack import SecretsStack

app = App()

# Get environment from context or default to 'dev'
env_name = app.node.try_get_context("env") or "dev"

# AWS environment configuration
aws_env = Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "eu-west-3")
)

# Create stacks with dependencies

# Secrets stack - independent, can be deployed separately
secrets_stack = SecretsStack(
    app,
    f"ImpressionnistesSecrets-{env_name}",
    env=aws_env,
    description="AWS Secrets Manager secrets (Stripe, Slack, etc.)"
)

database_stack = DatabaseStack(
    app,
    f"ImpressionnistesDatabase-{env_name}",
    env=aws_env,
    description="DynamoDB table and database infrastructure"
)

monitoring_stack = MonitoringStack(
    app,
    f"ImpressionnistesMonitoring-{env_name}",
    database_stack=database_stack,
    env=aws_env,
    description="CloudWatch logs, alarms, and SNS topics"
)

auth_stack = AuthStack(
    app,
    f"ImpressionnistesAuth-{env_name}",
    env=aws_env,
    description="Cognito user pool and authentication"
)

api_stack = ApiStack(
    app,
    f"ImpressionnistesApi-{env_name}",
    database_stack=database_stack,
    auth_stack=auth_stack,
    env=aws_env,
    description="API Gateway and Lambda functions"
)

frontend_stack = FrontendStack(
    app,
    f"ImpressiornistesFrontend-{env_name}",
    api_stack=api_stack,
    env=aws_env,
    description="S3 and CloudFront for frontend hosting"
)

# Add common tags to all stacks
for stack in [secrets_stack, database_stack, monitoring_stack, auth_stack, api_stack, frontend_stack]:
    Tags.of(stack).add("Project", "CourseDesImpressionnistes")
    Tags.of(stack).add("Environment", env_name)
    Tags.of(stack).add("ManagedBy", "CDK")
    Tags.of(stack).add("CostCenter", "RCPM")  # Optional: for cost allocation

app.synth()
