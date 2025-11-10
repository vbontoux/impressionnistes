"""
Database Stack - DynamoDB Table and Configuration
Course des Impressionnistes Registration System
"""
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
)
from constructs import Construct


class DatabaseStack(Stack):
    """
    Stack for DynamoDB table with single-table design pattern.
    Includes GSI indexes for efficient querying.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Main DynamoDB table with single-table design
        # Will be implemented in task 1.3
        self.table = None
        
        # TODO: Task 1.3 - Create DynamoDB table with:
        # - PK/SK structure
        # - GSI1 for registration status queries
        # - GSI2 for race lookup
        # - Encryption at rest
        # - Point-in-time recovery
        # - On-demand billing
