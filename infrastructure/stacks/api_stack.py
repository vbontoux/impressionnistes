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
        self.env_name = env_name
        
        # Get environment configuration for removal policy
        env_config = self.node.try_get_context(env_name) or {}
        removal_policy_str = env_config.get("removal_policy", "DESTROY" if env_name == "dev" else "RETAIN")
        self.api_removal_policy = RemovalPolicy.DESTROY if removal_policy_str == "DESTROY" else RemovalPolicy.RETAIN
        
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
            'ENVIRONMENT': self.env_name
        }
        
        # Lambda functions dictionary
        self.lambda_functions = {}
        
        # Create auth Lambda functions
        self._create_auth_functions()
        
        # Create crew member Lambda functions
        self._create_crew_functions()
        
        # Create club Lambda functions
        self._create_club_functions()
        
        # Create boat registration Lambda functions
        self._create_boat_functions()
        
        # Create race Lambda functions
        self._create_race_functions()
        
        # Create payment Lambda functions
        self._create_payment_functions()
        
        # Create admin Lambda functions
        self._create_admin_functions()
        
        # Create public Lambda functions (no auth required)
        self._create_public_functions()
        
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
    
    def _create_club_functions(self):
        """Create club management Lambda functions"""
        
        # List clubs function
        self.lambda_functions['list_clubs'] = self._create_lambda_function(
            'ListClubsFunction',
            'club/list_clubs',
            'List all rowing clubs'
        )
    
    def _create_boat_functions(self):
        """Create boat registration Lambda functions"""
        
        # Create boat registration function
        self.lambda_functions['create_boat_registration'] = self._create_lambda_function(
            'CreateBoatRegistrationFunction',
            'boat/create_boat_registration',
            'Create a new boat registration'
        )
        
        # List boat registrations function
        self.lambda_functions['list_boat_registrations'] = self._create_lambda_function(
            'ListBoatRegistrationsFunction',
            'boat/list_boat_registrations',
            'List all boat registrations for team manager'
        )
        
        # Get boat registration function
        self.lambda_functions['get_boat_registration'] = self._create_lambda_function(
            'GetBoatRegistrationFunction',
            'boat/get_boat_registration',
            'Get a specific boat registration'
        )
        
        # Update boat registration function
        self.lambda_functions['update_boat_registration'] = self._create_lambda_function(
            'UpdateBoatRegistrationFunction',
            'boat/update_boat_registration',
            'Update boat registration information'
        )
        
        # Delete boat registration function
        self.lambda_functions['delete_boat_registration'] = self._create_lambda_function(
            'DeleteBoatRegistrationFunction',
            'boat/delete_boat_registration',
            'Delete a boat registration'
        )
        
        # Assign seat function
        self.lambda_functions['assign_seat'] = self._create_lambda_function(
            'AssignSeatFunction',
            'boat/assign_seat',
            'Assign crew member to boat seat'
        )
        
        # Get coxswain substitutes function
        self.lambda_functions['get_cox_substitutes'] = self._create_lambda_function(
            'GetCoxSubstitutesFunction',
            'boat/get_cox_substitutes',
            'Get eligible coxswain substitutes'
        )
    
    def _create_race_functions(self):
        """Create race management Lambda functions"""
        
        # List races function (no auth required - public data)
        self.lambda_functions['list_races'] = self._create_lambda_function(
            'ListRacesFunction',
            'race/list_races',
            'List all available races'
        )
    
    def _create_payment_functions(self):
        """Create payment Lambda functions"""
        
        # Create payment intent function
        payment_intent_function = self._create_lambda_function(
            'CreatePaymentIntentFunction',
            'payment/create_payment_intent',
            'Create Stripe payment intent for boat registrations',
            timeout=30
        )
        
        # Grant Secrets Manager permissions for Stripe API key
        payment_intent_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=['secretsmanager:GetSecretValue'],
                resources=[
                    f'arn:aws:secretsmanager:{self.region}:{self.account}:secret:impressionnistes/stripe/*'
                ]
            )
        )
        
        self.lambda_functions['create_payment_intent'] = payment_intent_function
        
        # Confirm payment webhook function
        webhook_function = self._create_lambda_function(
            'ConfirmPaymentWebhookFunction',
            'payment/confirm_payment_webhook',
            'Handle Stripe webhook events for payment confirmation',
            timeout=30
        )
        
        # Grant Secrets Manager permissions for webhook secret
        webhook_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=['secretsmanager:GetSecretValue'],
                resources=[
                    f'arn:aws:secretsmanager:{self.region}:{self.account}:secret:impressionnistes/stripe/*'
                ]
            )
        )
        
        self.lambda_functions['confirm_payment_webhook'] = webhook_function
        
        # Get payment receipt function
        self.lambda_functions['get_payment_receipt'] = self._create_lambda_function(
            'GetPaymentReceiptFunction',
            'payment/get_payment_receipt',
            'Get payment receipt details'
        )
    
    def _create_admin_functions(self):
        """Create admin configuration Lambda functions"""
        
        # Get event configuration function
        self.lambda_functions['get_event_config'] = self._create_lambda_function(
            'GetEventConfigFunction',
            'admin/get_event_config',
            'Get event dates and registration period configuration'
        )
        
        # Update event configuration function
        self.lambda_functions['update_event_config'] = self._create_lambda_function(
            'UpdateEventConfigFunction',
            'admin/update_event_config',
            'Update event dates and registration period configuration'
        )
        
        # Get pricing configuration function
        self.lambda_functions['get_pricing_config'] = self._create_lambda_function(
            'GetPricingConfigFunction',
            'admin/get_pricing_config',
            'Get pricing configuration'
        )
        
        # Update pricing configuration function
        self.lambda_functions['update_pricing_config'] = self._create_lambda_function(
            'UpdatePricingConfigFunction',
            'admin/update_pricing_config',
            'Update pricing configuration'
        )
        
        # Rental boat inventory management functions
        self.lambda_functions['create_rental_boat'] = self._create_lambda_function(
            'CreateRentalBoatFunction',
            'admin/create_rental_boat',
            'Create a new rental boat hull in inventory'
        )
        
        self.lambda_functions['list_rental_boats'] = self._create_lambda_function(
            'ListRentalBoatsFunction',
            'admin/list_rental_boats',
            'List all rental boat hulls with filtering'
        )
        
        self.lambda_functions['update_rental_boat'] = self._create_lambda_function(
            'UpdateRentalBoatFunction',
            'admin/update_rental_boat',
            'Update rental boat name, status, or requester'
        )
        
        self.lambda_functions['delete_rental_boat'] = self._create_lambda_function(
            'DeleteRentalBoatFunction',
            'admin/delete_rental_boat',
            'Delete a rental boat hull from inventory'
        )
        
        self.lambda_functions['get_stats'] = self._create_lambda_function(
            'GetStatsFunction',
            'admin/get_stats',
            'Get admin dashboard statistics'
        )
        
        # Admin crew member management functions (bypass date restrictions)
        self.lambda_functions['admin_list_all_crew_members'] = self._create_lambda_function(
            'AdminListAllCrewMembersFunction',
            'admin/admin_list_all_crew_members',
            'Admin list all crew members across all team managers'
        )
        
        self.lambda_functions['admin_create_crew_member'] = self._create_lambda_function(
            'AdminCreateCrewMemberFunction',
            'admin/admin_create_crew_member',
            'Admin create crew member for any team manager'
        )
        
        self.lambda_functions['admin_update_crew_member'] = self._create_lambda_function(
            'AdminUpdateCrewMemberFunction',
            'admin/admin_update_crew_member',
            'Admin update crew member for any team manager'
        )
        
        self.lambda_functions['admin_delete_crew_member'] = self._create_lambda_function(
            'AdminDeleteCrewMemberFunction',
            'admin/admin_delete_crew_member',
            'Admin delete crew member for any team manager'
        )
        
        # Admin boat management functions (bypass date restrictions)
        self.lambda_functions['admin_list_all_boats'] = self._create_lambda_function(
            'AdminListAllBoatsFunction',
            'admin/admin_list_all_boats',
            'Admin list all boat registrations across all team managers'
        )
        
        self.lambda_functions['admin_create_boat'] = self._create_lambda_function(
            'AdminCreateBoatFunction',
            'admin/admin_create_boat',
            'Admin create boat registration for any team manager'
        )
        
        self.lambda_functions['admin_update_boat'] = self._create_lambda_function(
            'AdminUpdateBoatFunction',
            'admin/admin_update_boat',
            'Admin update boat registration for any team manager'
        )
        
        self.lambda_functions['admin_delete_boat'] = self._create_lambda_function(
            'AdminDeleteBoatFunction',
            'admin/admin_delete_boat',
            'Admin delete boat registration for any team manager'
        )
        
        # Team manager rental functions
        self.lambda_functions['list_available_rental_boats'] = self._create_lambda_function(
            'ListAvailableRentalBoatsFunction',
            'rental/list_available_rental_boats',
            'List available rental boats for team managers'
        )
        
        self.lambda_functions['request_rental_boat'] = self._create_lambda_function(
            'RequestRentalBoatFunction',
            'rental/request_rental_boat',
            'Request a rental boat for team manager'
        )
        
        self.lambda_functions['get_my_rental_requests'] = self._create_lambda_function(
            'GetMyRentalRequestsFunction',
            'rental/get_my_rental_requests',
            'Get rental requests for authenticated team manager'
        )
        
        self.lambda_functions['cancel_rental_request'] = self._create_lambda_function(
            'CancelRentalRequestFunction',
            'rental/cancel_rental_request',
            'Cancel a rental request for team manager'
        )
        
        self.lambda_functions['get_rentals_for_payment'] = self._create_lambda_function(
            'GetRentalsForPaymentFunction',
            'rental/get_rentals_for_payment',
            'Get confirmed rental boats ready for payment'
        )
        
        # Export functions (JSON)
        self.lambda_functions['export_crew_members_json'] = self._create_lambda_function(
            'ExportCrewMembersJsonFunction',
            'admin/export_crew_members_json',
            'Export all crew members as JSON for frontend formatting',
            timeout=60
        )
        
        self.lambda_functions['export_boat_registrations_json'] = self._create_lambda_function(
            'ExportBoatRegistrationsJsonFunction',
            'admin/export_boat_registrations_json',
            'Export all boat registrations as JSON for frontend formatting',
            timeout=60
        )
        
        self.lambda_functions['export_races_json'] = self._create_lambda_function(
            'ExportRacesJsonFunction',
            'admin/export_races_json',
            'Export races with all related data as JSON for frontend formatting',
            timeout=60
        )
    
    def _create_public_functions(self):
        """Create public Lambda functions (no authentication required)"""
        
        # Get public event info function
        self.lambda_functions['get_public_event_info'] = self._create_lambda_function(
            'GetPublicEventInfoFunction',
            'health/get_public_event_info',
            'Get public event information including dates for home page'
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
        
        # Create REST API
        self.api = apigateway.RestApi(
            self,
            "ImpressionnistesApi",
            rest_api_name=f"impressionnistes-api-{self.env_name}",
            description="Course des Impressionnistes Registration System API",
            cloud_watch_role=True,
            cloud_watch_role_removal_policy=self.api_removal_policy,
            
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
            ),
            
            # Binary media types for file downloads
            binary_media_types=[
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # Excel
                'application/octet-stream',  # Generic binary
                'text/csv'  # CSV files
            ]
        )
        
        # Add Gateway Responses for CORS on error responses
        # This ensures CORS headers are present even on 401, 403, 500 errors
        self.api.add_gateway_response(
            "Unauthorized",
            type=apigateway.ResponseType.UNAUTHORIZED,
            response_headers={
                "Access-Control-Allow-Origin": "'*'",
                "Access-Control-Allow-Headers": "'Content-Type,Authorization'",
                "Access-Control-Allow-Methods": "'GET,POST,PUT,DELETE,OPTIONS'"
            }
        )
        
        self.api.add_gateway_response(
            "AccessDenied",
            type=apigateway.ResponseType.ACCESS_DENIED,
            response_headers={
                "Access-Control-Allow-Origin": "'*'",
                "Access-Control-Allow-Headers": "'Content-Type,Authorization'",
                "Access-Control-Allow-Methods": "'GET,POST,PUT,DELETE,OPTIONS'"
            }
        )
        
        self.api.add_gateway_response(
            "Default4XX",
            type=apigateway.ResponseType.DEFAULT_4_XX,
            response_headers={
                "Access-Control-Allow-Origin": "'*'",
                "Access-Control-Allow-Headers": "'Content-Type,Authorization'",
                "Access-Control-Allow-Methods": "'GET,POST,PUT,DELETE,OPTIONS'"
            }
        )
        
        self.api.add_gateway_response(
            "Default5XX",
            type=apigateway.ResponseType.DEFAULT_5_XX,
            response_headers={
                "Access-Control-Allow-Origin": "'*'",
                "Access-Control-Allow-Headers": "'Content-Type,Authorization'",
                "Access-Control-Allow-Methods": "'GET,POST,PUT,DELETE,OPTIONS'"
            }
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
        
        # Create /public resource (public endpoints - no auth required)
        public_resource = self.api.root.add_resource('public')
        
        # GET /public/event-info - Get public event information (no auth required)
        event_info_resource = public_resource.add_resource('event-info')
        get_public_event_info_integration = apigateway.LambdaIntegration(
            self.lambda_functions['get_public_event_info'],
            proxy=True
        )
        event_info_resource.add_method(
            'GET',
            get_public_event_info_integration
        )
        
        # Create /clubs resource
        clubs_resource = self.api.root.add_resource('clubs')
        
        # GET /clubs - List all clubs (public - no auth required for registration)
        list_clubs_integration = apigateway.LambdaIntegration(
            self.lambda_functions['list_clubs'],
            proxy=True
        )
        clubs_resource.add_method(
            'GET',
            list_clubs_integration
        )
        
        # Create /boat resource
        boat_resource = self.api.root.add_resource('boat')
        
        # POST /boat - Create boat registration (auth required)
        create_boat_integration = apigateway.LambdaIntegration(
            self.lambda_functions['create_boat_registration'],
            proxy=True
        )
        boat_resource.add_method(
            'POST',
            create_boat_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # GET /boat - List boat registrations (auth required)
        list_boat_integration = apigateway.LambdaIntegration(
            self.lambda_functions['list_boat_registrations'],
            proxy=True
        )
        boat_resource.add_method(
            'GET',
            list_boat_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # /boat/{boat_registration_id} resource
        boat_registration_resource = boat_resource.add_resource('{boat_registration_id}')
        
        # GET /boat/{boat_registration_id} - Get boat registration (auth required)
        get_boat_integration = apigateway.LambdaIntegration(
            self.lambda_functions['get_boat_registration'],
            proxy=True
        )
        boat_registration_resource.add_method(
            'GET',
            get_boat_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # PUT /boat/{boat_registration_id} - Update boat registration (auth required)
        update_boat_integration = apigateway.LambdaIntegration(
            self.lambda_functions['update_boat_registration'],
            proxy=True
        )
        boat_registration_resource.add_method(
            'PUT',
            update_boat_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # DELETE /boat/{boat_registration_id} - Delete boat registration (auth required)
        delete_boat_integration = apigateway.LambdaIntegration(
            self.lambda_functions['delete_boat_registration'],
            proxy=True
        )
        boat_registration_resource.add_method(
            'DELETE',
            delete_boat_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # POST /boat/{boat_registration_id}/assign-seat - Assign seat (auth required)
        assign_seat_resource = boat_registration_resource.add_resource('assign-seat')
        assign_seat_integration = apigateway.LambdaIntegration(
            self.lambda_functions['assign_seat'],
            proxy=True
        )
        assign_seat_resource.add_method(
            'POST',
            assign_seat_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # GET /boat/{boat_registration_id}/cox-substitutes - Get cox substitutes (auth required)
        cox_substitutes_resource = boat_registration_resource.add_resource('cox-substitutes')
        cox_substitutes_integration = apigateway.LambdaIntegration(
            self.lambda_functions['get_cox_substitutes'],
            proxy=True
        )
        cox_substitutes_resource.add_method(
            'GET',
            cox_substitutes_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # Create /races resource (public - no auth required)
        races_resource = self.api.root.add_resource('races')
        
        # GET /races - List all races (no auth required)
        list_races_integration = apigateway.LambdaIntegration(
            self.lambda_functions['list_races'],
            proxy=True
        )
        races_resource.add_method(
            'GET',
            list_races_integration
        )
        
        # Create /payment resource
        payment_resource = self.api.root.add_resource('payment')
        
        # POST /payment/create-intent - Create payment intent (auth required)
        create_intent_resource = payment_resource.add_resource('create-intent')
        create_intent_integration = apigateway.LambdaIntegration(
            self.lambda_functions['create_payment_intent'],
            proxy=True
        )
        create_intent_resource.add_method(
            'POST',
            create_intent_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # POST /payment/webhook - Stripe webhook (no auth - verified by signature)
        webhook_resource = payment_resource.add_resource('webhook')
        webhook_integration = apigateway.LambdaIntegration(
            self.lambda_functions['confirm_payment_webhook'],
            proxy=True
        )
        webhook_resource.add_method(
            'POST',
            webhook_integration
            # No authorizer - Stripe webhooks use signature verification
        )
        
        # GET /payment/receipt/{payment_id} - Get payment receipt (auth required)
        receipt_resource = payment_resource.add_resource('receipt')
        payment_id_resource = receipt_resource.add_resource('{payment_id}')
        receipt_integration = apigateway.LambdaIntegration(
            self.lambda_functions['get_payment_receipt'],
            proxy=True
        )
        payment_id_resource.add_method(
            'GET',
            receipt_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # Create /admin resource (admin only)
        admin_resource = self.api.root.add_resource('admin')
        
        # GET /admin/event-config - Get event configuration (admin only)
        event_config_resource = admin_resource.add_resource('event-config')
        get_event_config_integration = apigateway.LambdaIntegration(
            self.lambda_functions['get_event_config'],
            proxy=True
        )
        event_config_resource.add_method(
            'GET',
            get_event_config_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # PUT /admin/event-config - Update event configuration (admin only)
        update_event_config_integration = apigateway.LambdaIntegration(
            self.lambda_functions['update_event_config'],
            proxy=True
        )
        event_config_resource.add_method(
            'PUT',
            update_event_config_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # GET /admin/pricing-config - Get pricing configuration (admin only)
        pricing_config_resource = admin_resource.add_resource('pricing-config')
        get_pricing_config_integration = apigateway.LambdaIntegration(
            self.lambda_functions['get_pricing_config'],
            proxy=True
        )
        pricing_config_resource.add_method(
            'GET',
            get_pricing_config_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # PUT /admin/pricing-config - Update pricing configuration (admin only)
        update_pricing_config_integration = apigateway.LambdaIntegration(
            self.lambda_functions['update_pricing_config'],
            proxy=True
        )
        pricing_config_resource.add_method(
            'PUT',
            update_pricing_config_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # Rental boat inventory management routes
        rental_boats_resource = admin_resource.add_resource('rental-boats')
        
        # GET /admin/rental-boats - List all rental boats (admin only)
        list_rental_boats_integration = apigateway.LambdaIntegration(
            self.lambda_functions['list_rental_boats'],
            proxy=True
        )
        rental_boats_resource.add_method(
            'GET',
            list_rental_boats_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # POST /admin/rental-boats - Create a new rental boat (admin only)
        create_rental_boat_integration = apigateway.LambdaIntegration(
            self.lambda_functions['create_rental_boat'],
            proxy=True
        )
        rental_boats_resource.add_method(
            'POST',
            create_rental_boat_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # Single rental boat resource /admin/rental-boats/{rental_boat_id}
        rental_boat_resource = rental_boats_resource.add_resource('{rental_boat_id}')
        
        # PUT /admin/rental-boats/{rental_boat_id} - Update a rental boat (admin only)
        update_rental_boat_integration = apigateway.LambdaIntegration(
            self.lambda_functions['update_rental_boat'],
            proxy=True
        )
        rental_boat_resource.add_method(
            'PUT',
            update_rental_boat_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # DELETE /admin/rental-boats/{rental_boat_id} - Delete a rental boat (admin only)
        delete_rental_boat_integration = apigateway.LambdaIntegration(
            self.lambda_functions['delete_rental_boat'],
            proxy=True
        )
        rental_boat_resource.add_method(
            'DELETE',
            delete_rental_boat_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # GET /admin/stats - Get admin dashboard statistics (admin only)
        stats_resource = admin_resource.add_resource('stats')
        get_stats_integration = apigateway.LambdaIntegration(
            self.lambda_functions['get_stats'],
            proxy=True
        )
        stats_resource.add_method(
            'GET',
            get_stats_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # Export routes
        # GET /admin/export/crewtimer - Export races and boats in CrewTimer format (admin only)
        # JSON export endpoints
        export_resource = admin_resource.add_resource('export')
        # GET /admin/export/crew-members-json - Export all crew members as JSON (admin only)
        crew_members_json_export_resource = export_resource.add_resource('crew-members-json')
        export_crew_members_json_integration = apigateway.LambdaIntegration(
            self.lambda_functions['export_crew_members_json'],
            proxy=True
        )
        crew_members_json_export_resource.add_method(
            'GET',
            export_crew_members_json_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # GET /admin/export/boat-registrations-json - Export all boat registrations as JSON (admin only)
        boat_registrations_json_export_resource = export_resource.add_resource('boat-registrations-json')
        export_boat_registrations_json_integration = apigateway.LambdaIntegration(
            self.lambda_functions['export_boat_registrations_json'],
            proxy=True
        )
        boat_registrations_json_export_resource.add_method(
            'GET',
            export_boat_registrations_json_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # GET /admin/export/races-json - Export races with all related data as JSON (admin only)
        races_json_export_resource = export_resource.add_resource('races-json')
        export_races_json_integration = apigateway.LambdaIntegration(
            self.lambda_functions['export_races_json'],
            proxy=True
        )
        races_json_export_resource.add_method(
            'GET',
            export_races_json_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # Admin crew member management routes (bypass date restrictions)
        # GET /admin/crew - List all crew members across all team managers (admin only)
        admin_crew_resource = admin_resource.add_resource('crew')
        admin_list_crew_integration = apigateway.LambdaIntegration(
            self.lambda_functions['admin_list_all_crew_members'],
            proxy=True
        )
        admin_crew_resource.add_method(
            'GET',
            admin_list_crew_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # POST /admin/crew - Create crew member for any team manager (admin only)
        admin_create_crew_integration = apigateway.LambdaIntegration(
            self.lambda_functions['admin_create_crew_member'],
            proxy=True
        )
        admin_crew_resource.add_method(
            'POST',
            admin_create_crew_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # /admin/crew/{team_manager_id}/{crew_member_id} resource
        admin_crew_tm_resource = admin_crew_resource.add_resource('{team_manager_id}')
        admin_crew_member_resource = admin_crew_tm_resource.add_resource('{crew_member_id}')
        
        # PUT /admin/crew/{team_manager_id}/{crew_member_id} - Update crew member (admin only)
        admin_update_crew_integration = apigateway.LambdaIntegration(
            self.lambda_functions['admin_update_crew_member'],
            proxy=True
        )
        admin_crew_member_resource.add_method(
            'PUT',
            admin_update_crew_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # DELETE /admin/crew/{team_manager_id}/{crew_member_id} - Delete crew member (admin only)
        admin_delete_crew_integration = apigateway.LambdaIntegration(
            self.lambda_functions['admin_delete_crew_member'],
            proxy=True
        )
        admin_crew_member_resource.add_method(
            'DELETE',
            admin_delete_crew_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # Admin boat management routes (bypass date restrictions)
        # GET /admin/boats - List all boat registrations across all team managers (admin only)
        admin_boats_resource = admin_resource.add_resource('boats')
        admin_list_boats_integration = apigateway.LambdaIntegration(
            self.lambda_functions['admin_list_all_boats'],
            proxy=True
        )
        admin_boats_resource.add_method(
            'GET',
            admin_list_boats_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # POST /admin/boats - Create boat registration for any team manager (admin only)
        admin_create_boat_integration = apigateway.LambdaIntegration(
            self.lambda_functions['admin_create_boat'],
            proxy=True
        )
        admin_boats_resource.add_method(
            'POST',
            admin_create_boat_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # /admin/boats/{team_manager_id}/{boat_registration_id} resource
        admin_boats_tm_resource = admin_boats_resource.add_resource('{team_manager_id}')
        admin_boat_resource = admin_boats_tm_resource.add_resource('{boat_registration_id}')
        
        # PUT /admin/boats/{team_manager_id}/{boat_registration_id} - Update boat (admin only)
        admin_update_boat_integration = apigateway.LambdaIntegration(
            self.lambda_functions['admin_update_boat'],
            proxy=True
        )
        admin_boat_resource.add_method(
            'PUT',
            admin_update_boat_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # DELETE /admin/boats/{team_manager_id}/{boat_registration_id} - Delete boat (admin only)
        admin_delete_boat_integration = apigateway.LambdaIntegration(
            self.lambda_functions['admin_delete_boat'],
            proxy=True
        )
        admin_boat_resource.add_method(
            'DELETE',
            admin_delete_boat_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # Create /rental resource (team manager accessible)
        rental_resource = self.api.root.add_resource('rental')
        
        # GET /rental/boats - List available rental boats (team manager accessible)
        rental_boats_resource = rental_resource.add_resource('boats')
        list_available_rental_boats_integration = apigateway.LambdaIntegration(
            self.lambda_functions['list_available_rental_boats'],
            proxy=True
        )
        rental_boats_resource.add_method(
            'GET',
            list_available_rental_boats_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # POST /rental/request - Request a rental boat (team manager accessible)
        rental_request_resource = rental_resource.add_resource('request')
        request_rental_boat_integration = apigateway.LambdaIntegration(
            self.lambda_functions['request_rental_boat'],
            proxy=True
        )
        rental_request_resource.add_method(
            'POST',
            request_rental_boat_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # GET /rental/my-requests - Get my rental requests (team manager accessible)
        my_requests_resource = rental_resource.add_resource('my-requests')
        get_my_rental_requests_integration = apigateway.LambdaIntegration(
            self.lambda_functions['get_my_rental_requests'],
            proxy=True
        )
        my_requests_resource.add_method(
            'GET',
            get_my_rental_requests_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # DELETE /rental/cancel/{rental_boat_id} - Cancel a rental request (team manager accessible)
        cancel_resource = rental_resource.add_resource('cancel')
        cancel_rental_id_resource = cancel_resource.add_resource('{rental_boat_id}')
        cancel_rental_request_integration = apigateway.LambdaIntegration(
            self.lambda_functions['cancel_rental_request'],
            proxy=True
        )
        cancel_rental_id_resource.add_method(
            'DELETE',
            cancel_rental_request_integration,
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # GET /rental/for-payment - Get confirmed rentals ready for payment (team manager accessible)
        for_payment_resource = rental_resource.add_resource('for-payment')
        get_rentals_for_payment_integration = apigateway.LambdaIntegration(
            self.lambda_functions['get_rentals_for_payment'],
            proxy=True
        )
        for_payment_resource.add_method(
            'GET',
            get_rentals_for_payment_integration,
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
