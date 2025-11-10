#!/usr/bin/env python3
"""
AWS CDK App Entry Point
Course des Impressionnistes Registration System
"""
import os
from aws_cdk import App, Environment

# Import stacks (will be created in subsequent tasks)
# from stacks.database_stack import DatabaseStack
# from stacks.api_stack import ApiStack
# from stacks.frontend_stack import FrontendStack
# from stacks.monitoring_stack import MonitoringStack

app = App()

# Get environment from context or default to 'dev'
env_name = app.node.try_get_context("env") or "dev"

# AWS environment configuration
aws_env = Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "eu-west-3")
)

# TODO: Create and configure stacks in subsequent tasks
# database_stack = DatabaseStack(app, f"ImpressionnistesDatabase-{env_name}", env=aws_env)
# api_stack = ApiStack(app, f"ImpressionnistesApi-{env_name}", database=database_stack, env=aws_env)
# frontend_stack = FrontendStack(app, f"ImpressiornistesFrontend-{env_name}", api=api_stack, env=aws_env)
# monitoring_stack = MonitoringStack(app, f"ImpressionnistesMonitoring-{env_name}", env=aws_env)

app.synth()
