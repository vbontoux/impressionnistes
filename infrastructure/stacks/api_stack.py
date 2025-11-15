"""
API Stack - API Gateway and Lambda Functions
Course des Impressionnistes Registration System
"""
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
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
        
        # Create crew member Lambda functions
        self._create_crew_functions()
        
        # Create API Gateway REST API
        self._create_api_gateway()
        
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
    
    def _create_crew_functions(self):
        """Create crew member management Lambda functions"""
        
        # Create crew member function
        self.lambda_functions['create_crew_member'] = self._create_lambda_function(
            'CreateCrewMemberFunction',
            'crew/create_crew_member',
            'Create a new crew member'
        )
        
        # List crew members function
        self.lambda_functions['list_crew_members'] = self._create_lambda_function(
            'ListCrewMembersFunction',
            'crew/list_crew_members',
            'List all crew members for team manager'
        )
        
        # Get crew member function
        self.lambda_functions['get_crew_member'] = self._create_lambda_function(
            'GetCrewMemberFunction',
            'crew/get_crew_member',
            'Get a specific crew member'
        )
        
        # Update crew member function
        self.lambda_functions['update_crew_member'] = self._create_lambda_function(
            'UpdateCrewMemberFunction',
            'crew/update_crew_member',
            'Update crew member information'
        )
        
        # Delete crew member function
        self.lambda_functions['delete_crew_member'] = self._create_lambda_function(
            'DeleteCrewMemberFunction',
            'crew/delete_crew_member',
            'Delete a crew member'
        )

    def _create_api_gateway(self):
        """Create API Gateway REST API with Cognito authorizer"""
        
        # Create CloudWatch role for API Gateway logging
        cloudwatch_role = iam.Role(
            self,
            "ApiGatewayCloudWatchRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonAPIGatewayPushToCloudWatchLogs"
                )
            ]
        )
        
        # Get environment name
        env_name = self.node.try_get_context('env') or 'dev'
        
        # Create REST API
        self.api = apigateway.RestApi(
            self,
            "ImpressionnistesApi",
            rest_api_name=f"impressionnistes-api-{env_name}",
            description="Course des Impressionnistes Registration System API",
            cloud_watch_role=True,
            cloud_watch_role_removal_policy=RemovalPolicy.DESTROY if env_name == 'dev' else RemovalPolicy.RETAIN,
            
            # CORS configuration
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,  # TODO: Restrict in production
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=[
                    'Content-Type',
                    'Authorization',
                    'X-Amz-Date',
                    'X-Api-Key',
                    'X-Amz-Security-Token'
                ],
                allow_credentials=True
            ),
            
            # Deploy options
            deploy_options=apigateway.StageOptions(
                stage_name=self.node.try_get_context('env') or 'dev',
                throttling_rate_limit=1000,
                throttling_burst_limit=2000,
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
                metrics_enabled=True
            )
        )
        
        # Create Cognito authorizer
        self.authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self,
            "CognitoAuthorizer",
            cognito_user_pools=[self.auth_stack.user_pool],
            authorizer_name="CognitoAuthorizer",
            identity_source="method.request.header.Authorization"
        )
        
        # Create /auth resource
        auth_resource = self.api.root.add_resource('auth')
        
        # POST /auth/register (no auth required)
        register_integration = apigateway.LambdaIntegration(
            self.lambda_functions['register'],
            proxy=True
        )
        auth_resource.add_resource('register').add_method(
            'POST',
            register_integration
        )
        
        # GET /auth/profile (auth required)
        profile_resource = auth_resource.add_resource('profile')
        profile_integration = apigateway.LambdaIntegration(
            self.lambda_functions['get_profile'],
            proxy=True
        )
        profile_resource.add_method(
            'GET',
            profile_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # PUT /auth/profile (auth required)
        update_profile_integration = apigateway.LambdaIntegration(
            self.lambda_functions['update_profile'],
            proxy=True
        )
        profile_resource.add_method(
            'PUT',
            update_profile_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # POST /auth/forgot-password (no auth required)
        forgot_password_integration = apigateway.LambdaIntegration(
            self.lambda_functions['forgot_password'],
            proxy=True
        )
        auth_resource.add_resource('forgot-password').add_method(
            'POST',
            forgot_password_integration
        )
        
        # POST /auth/reset-password (no auth required)
        reset_password_integration = apigateway.LambdaIntegration(
            self.lambda_functions['confirm_password_reset'],
            proxy=True
        )
        auth_resource.add_resource('reset-password').add_method(
            'POST',
            reset_password_integration
        )
        
        # Create /crew resource
        crew_resource = self.api.root.add_resource('crew')
        
        # POST /crew - Create crew member (auth required)
        create_crew_integration = apigateway.LambdaIntegration(
            self.lambda_functions['create_crew_member'],
            proxy=True
        )
        crew_resource.add_method(
            'POST',
            create_crew_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # GET /crew - List crew members (auth required)
        list_crew_integration = apigateway.LambdaIntegration(
            self.lambda_functions['list_crew_members'],
            proxy=True
        )
        crew_resource.add_method(
            'GET',
            list_crew_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # /crew/{crew_member_id} resource
        crew_member_resource = crew_resource.add_resource('{crew_member_id}')
        
        # GET /crew/{crew_member_id} - Get crew member (auth required)
        get_crew_integration = apigateway.LambdaIntegration(
            self.lambda_functions['get_crew_member'],
            proxy=True
        )
        crew_member_resource.add_method(
            'GET',
            get_crew_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # PUT /crew/{crew_member_id} - Update crew member (auth required)
        update_crew_integration = apigateway.LambdaIntegration(
            self.lambda_functions['update_crew_member'],
            proxy=True
        )
        crew_member_resource.add_method(
            'PUT',
            update_crew_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # DELETE /crew/{crew_member_id} - Delete crew member (auth required)
        delete_crew_integration = apigateway.LambdaIntegration(
            self.lambda_functions['delete_crew_member'],
            proxy=True
        )
        crew_member_resource.add_method(
            'DELETE',
            delete_crew_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # Output API URL
        from aws_cdk import CfnOutput
        CfnOutput(
            self,
            "ApiUrl",
            value=self.api.url,
            description="API Gateway URL",
            export_name=f"ImpressionnistesApiUrl-{self.node.try_get_context('env') or 'dev'}"
        )
