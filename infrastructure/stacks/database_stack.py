"""
Database Stack - DynamoDB Table and Configuration
Course des Impressionnistes Registration System
"""
from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    CustomResource,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_iam as iam,
)
from constructs import Construct
from aws_cdk.custom_resources import Provider
import os


class DatabaseStack(Stack):
    """
    Stack for DynamoDB table with single-table design pattern.
    Includes GSI indexes for efficient querying.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get environment from context
        env_name = self.node.try_get_context("env") or "dev"
        env_config = self.node.try_get_context(env_name) or {}
        
        # Determine removal policy based on environment
        removal_policy = (
            RemovalPolicy.DESTROY if env_config.get("removal_policy") == "DESTROY"
            else RemovalPolicy.RETAIN
        )
        
        # Create DynamoDB table with single-table design
        self.table = dynamodb.Table(
            self,
            "RegistrationTable",
            table_name=env_config.get("table_name", f"impressionnistes-registration-{env_name}"),
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            point_in_time_recovery=env_config.get("enable_point_in_time_recovery", False),
            removal_policy=removal_policy,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
        )
        
        # GSI1: Registration Status Index
        # Used by admins to query registrations by status
        self.table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=dynamodb.Attribute(
                name="GSI1PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="GSI1SK",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL,
        )
        
        # GSI2: Race Lookup Index
        # Used for filtering races by event type, boat type, age, and gender
        self.table.add_global_secondary_index(
            index_name="GSI2",
            partition_key=dynamodb.Attribute(
                name="GSI2PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="GSI2SK",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL,
        )
        
        # Create Lambda function for table initialization
        init_function = lambda_.Function(
            self,
            "InitConfigFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="init_config.lambda_handler",
            code=lambda_.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "../../functions/init")
            ),
            timeout=Duration.seconds(60),
            environment={
                "TABLE_NAME": self.table.table_name,
                "ENVIRONMENT": env_name,
            },
        )
        
        # Grant permissions to Lambda
        self.table.grant_read_write_data(init_function)
        
        # Create custom resource provider
        provider = Provider(
            self,
            "InitConfigProvider",
            on_event_handler=init_function,
        )
        
        # Create custom resource to initialize configuration
        CustomResource(
            self,
            "InitConfigResource",
            service_token=provider.service_token,
            properties={
                "Timestamp": str(self.node.addr),  # Force update on each deployment
            },
        )
