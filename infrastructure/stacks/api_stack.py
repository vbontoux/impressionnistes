"""
API Stack - API Gateway and Lambda Functions
Course des Impressionnistes Registration System
"""
from aws_cdk import (
    Stack,
    Duration,
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_logs as logs,
)
from constructs import Construct
import os
from pathlib import Path


class ApiStack(Stack):
    """
    Stack for API Gateway REST API and Lambda function integrations.
    Handles authentication, crew management, boat registration, payments, and admin operations.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        database_stack,
        auth_stack,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.database_stack = database_stack
        self.auth_stack = auth_stack
        
        # Get environment from context
        env_name = self.node.try_get_context("env") or "dev"
        
        # Get the project root directory (parent of infrastructure/)
        project_root = Path(__file__).parent.parent.parent
        functions_path = project_root / "functions"
        
        # Create Lambda layer for shared dependencies
        # The shared directory contains both our code and installed dependencies
        # Lambda layers require a python/ subdirectory, so we create it
        layer_path = project_root / "functions" / "layer"
        
        self.shared_layer = lambda_.LayerVersion(
            self,
            "SharedLayer",
            code=lambda_.Code.from_asset(str(layer_path)),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_11],
            description="Shared utilities and dependencies for Lambda functions"
        )
        
        # Common Lambda environment variables
        self.common_env = {
            'TABLE_NAME': database_stack.table.table_name,
            'USER_POOL_ID': auth_stack.user_pool.user_pool_id,
            'USER_POOL_CLIENT_ID': auth_stack.user_pool_client.user_pool_client_id,
            'ENVIRONMENT': env_name
        }
        
        # Lambda functions dictionary
        self.lambda_functions = {}
        
        # Create auth Lambda functions
        self._create_auth_functions()
        
        # API Gateway REST API
        # Will be fully implemented in task 18.1
        self.api = None
        
        # TODO: Task 18.1 - Create API Gateway REST API with:
        # - CORS configuration
        # - API Gateway stages (dev, prod)
        # - Cognito authorizers
        # - Request/response transformations
        # - Logging and monitoring
        
        # TODO: Task 18.3 - Implement API Gateway routes:
        # - /auth/* endpoints
        # - /crew/* endpoints
        # - /boat/* endpoints
        # - /payment/* endpoints
        # - /admin/* endpoints
        # - /contact endpoint
    
    def _create_lambda_function(self, function_id, handler_path, description, timeout=30):
        """
        Create a Lambda function with common configuration
        
        Args:
            function_id: CDK construct ID
            handler_path: Path to handler (e.g., 'auth/register')
            description: Function description
            timeout: Function timeout in seconds
            
        Returns:
            Lambda function
        """
        # Get project root for functions path
        project_root = Path(__file__).parent.parent.parent
        functions_path = project_root / "functions"
        
        function = lambda_.Function(
            self,
            function_id,
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler=f"{handler_path.replace('/', '.')}.lambda_handler",
            code=lambda_.Code.from_asset(str(functions_path)),
            layers=[self.shared_layer],
            environment=self.common_env,
            timeout=Duration.seconds(timeout),
            memory_size=256,
            description=description,
            log_retention=logs.RetentionDays.ONE_WEEK
        )
        
        # Grant DynamoDB permissions
        self.database_stack.table.grant_read_write_data(function)
        
        # Grant Cognito permissions
        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    'cognito-idp:AdminCreateUser',
                    'cognito-idp:AdminUpdateUserAttributes',
                    'cognito-idp:AdminAddUserToGroup',
                    'cognito-idp:AdminGetUser',
                    'cognito-idp:ListUsers'
                ],
                resources=[self.auth_stack.user_pool.user_pool_arn]
            )
        )
        
        return function
    
    def _create_auth_functions(self):
        """Create authentication Lambda functions"""
        
        # Register function
        self.lambda_functions['register'] = self._create_lambda_function(
            'RegisterFunction',
            'auth/register',
            'Team manager registration'
        )
        
        # Update profile function
        self.lambda_functions['update_profile'] = self._create_lambda_function(
            'UpdateProfileFunction',
            'auth/update_profile',
            'Update team manager profile'
        )
        
        # Get profile function
        self.lambda_functions['get_profile'] = self._create_lambda_function(
            'GetProfileFunction',
            'auth/get_profile',
            'Get team manager profile'
        )
        
        # Forgot password function
        self.lambda_functions['forgot_password'] = self._create_lambda_function(
            'ForgotPasswordFunction',
            'auth/forgot_password',
            'Initiate password reset'
        )
        
        # Confirm password reset function
        self.lambda_functions['confirm_password_reset'] = self._create_lambda_function(
            'ConfirmPasswordResetFunction',
            'auth/confirm_password_reset',
            'Confirm password reset with code'
        )
