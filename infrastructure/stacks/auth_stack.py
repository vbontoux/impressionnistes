"""
Authentication Stack - Amazon Cognito User Pool
Course des Impressionnistes Registration System
"""
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_cognito as cognito,
    aws_iam as iam,
    aws_lambda as lambda_,
    custom_resources as cr,
    CfnOutput,
)
from constructs import Construct
import json
import os


class AuthStack(Stack):
    """
    Stack for authentication using Amazon Cognito.
    Includes user pool, app client, and social login configuration.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        frontend_stack=None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get environment from context
        env_name = self.node.try_get_context("env") or "dev"
        self.frontend_stack = frontend_stack
        
        # Get environment configuration
        env_config = self.node.try_get_context(env_name) or {}
        
        # Determine removal policy for Cognito
        # Use the general removal_policy from config, defaulting to DESTROY for dev
        removal_policy_str = env_config.get("removal_policy", "DESTROY" if env_name == "dev" else "RETAIN")
        cognito_removal_policy = RemovalPolicy.DESTROY if removal_policy_str == "DESTROY" else RemovalPolicy.RETAIN
        
        # Create Cognito User Pool
        self.user_pool = cognito.UserPool(
            self,
            "UserPool",
            user_pool_name=f"impressionnistes-users-{env_name}",
            
            # Sign-in configuration
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                username=False  # Only email sign-in
            ),
            
            # Self sign-up configuration
            self_sign_up_enabled=True,
            
            # User verification
            user_verification=cognito.UserVerificationConfig(
                email_subject="Verify your email for Course des Impressionnistes",
                email_body="Hello,\n\nThank you for registering for Course des Impressionnistes.\n\nYour verification code is: {####}\n\nPlease enter this code on the verification page to complete your registration.\n\nIf you did not create an account, please ignore this email.",
                email_style=cognito.VerificationEmailStyle.CODE,
            ),
            
            # Password policy
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True,  # Required for better security
                temp_password_validity=Duration.days(3)
            ),
            
            # Account recovery
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            
            # Standard attributes
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(
                    required=True,
                    mutable=True
                ),
                given_name=cognito.StandardAttribute(
                    required=True,
                    mutable=True
                ),
                family_name=cognito.StandardAttribute(
                    required=True,
                    mutable=True
                ),
                phone_number=cognito.StandardAttribute(
                    required=False,
                    mutable=True
                )
            ),
            
            # Custom attributes
            custom_attributes={
                'club_affiliation': cognito.StringAttribute(
                    min_len=1,
                    max_len=100,
                    mutable=True
                ),
                'role': cognito.StringAttribute(
                    min_len=1,
                    max_len=50,
                    mutable=True
                )
            },
            
            # MFA configuration (optional, can be enabled by users)
            mfa=cognito.Mfa.OPTIONAL,
            mfa_second_factor=cognito.MfaSecondFactor(
                sms=True,
                otp=True
            ),
            
            # Advanced security
            advanced_security_mode=cognito.AdvancedSecurityMode.ENFORCED if env_name == 'prod' else cognito.AdvancedSecurityMode.AUDIT,
            
            # Removal policy
            removal_policy=cognito_removal_policy
        )
        
        # Create user pool domain for hosted UI
        self.user_pool_domain = self.user_pool.add_domain(
            "UserPoolDomain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=f"impressionnistes-{env_name}"
            )
        )
        
        # Cognito UI Customization will be configured after frontend stack is deployed
        # The logo URL will be available from the frontend CloudFront distribution
        
        # Build callback URLs list
        callback_urls = [
            "http://localhost:3000/callback",  # Development
        ]
        logout_urls = [
            "http://localhost:3000/",  # Development
        ]
        
        # Add CloudFront URL if frontend stack is provided
        if self.frontend_stack:
            cloudfront_url = f"https://{self.frontend_stack.distribution.distribution_domain_name}"
            callback_urls.append(f"{cloudfront_url}/callback")
            logout_urls.append(f"{cloudfront_url}/")
        
        # Add custom domain if configured
        custom_domain = f"https://impressionnistes-{env_name}.rcpm-aviron.fr"
        callback_urls.append(f"{custom_domain}/callback")
        logout_urls.append(f"{custom_domain}/")
        
        # Create app client for web application
        self.user_pool_client = self.user_pool.add_client(
            "WebAppClient",
            user_pool_client_name=f"impressionnistes-web-{env_name}",
            
            # OAuth configuration
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=False  # More secure
                ),
                scopes=[
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.PROFILE
                ],
                callback_urls=callback_urls,
                logout_urls=logout_urls
            ),
            
            # Token validity
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
                custom=False,
                admin_user_password=True
            ),
            
            # Session configuration (5 hours max, 30 min inactivity handled by frontend)
            access_token_validity=Duration.hours(5),
            id_token_validity=Duration.hours(5),
            refresh_token_validity=Duration.days(30),
            
            # Prevent user existence errors (security)
            prevent_user_existence_errors=True,
            
            # Enable token revocation
            enable_token_revocation=True
        )
        
        # Create Cognito Groups for role-based access control
        self.admin_group = cognito.CfnUserPoolGroup(
            self,
            "AdminGroup",
            user_pool_id=self.user_pool.user_pool_id,
            group_name="admins",
            description="RCPM administrators with full access to system configuration and validation",
            precedence=1  # Highest priority
        )
        
        self.team_manager_group = cognito.CfnUserPoolGroup(
            self,
            "TeamManagerGroup",
            user_pool_id=self.user_pool.user_pool_id,
            group_name="team_managers",
            description="Team managers from rowing clubs who can register boats and crews",
            precedence=10
        )
        
        self.devops_group = cognito.CfnUserPoolGroup(
            self,
            "DevOpsGroup",
            user_pool_id=self.user_pool.user_pool_id,
            group_name="devops",
            description="DevOps team with system access and configuration management",
            precedence=5
        )
        
        # Configure social identity providers (Google, Facebook)
        # Note: These require external configuration and secrets
        # Will be configured manually or via secrets in production
        
        # Google Identity Provider (requires Google OAuth credentials)
        # Uncomment and configure when Google OAuth credentials are available
        # google_provider = cognito.UserPoolIdentityProviderGoogle(
        #     self,
        #     "GoogleProvider",
        #     user_pool=self.user_pool,
        #     client_id="YOUR_GOOGLE_CLIENT_ID",
        #     client_secret="YOUR_GOOGLE_CLIENT_SECRET",
        #     scopes=["email", "profile", "openid"],
        #     attribute_mapping=cognito.AttributeMapping(
        #         email=cognito.ProviderAttribute.GOOGLE_EMAIL,
        #         given_name=cognito.ProviderAttribute.GOOGLE_GIVEN_NAME,
        #         family_name=cognito.ProviderAttribute.GOOGLE_FAMILY_NAME
        #     )
        # )
        
        # Facebook Identity Provider (requires Facebook App credentials)
        # Uncomment and configure when Facebook App credentials are available
        # facebook_provider = cognito.UserPoolIdentityProviderFacebook(
        #     self,
        #     "FacebookProvider",
        #     user_pool=self.user_pool,
        #     client_id="YOUR_FACEBOOK_APP_ID",
        #     client_secret="YOUR_FACEBOOK_APP_SECRET",
        #     scopes=["email", "public_profile"],
        #     attribute_mapping=cognito.AttributeMapping(
        #         email=cognito.ProviderAttribute.FACEBOOK_EMAIL,
        #         given_name=cognito.ProviderAttribute.FACEBOOK_GIVEN_NAME,
        #         family_name=cognito.ProviderAttribute.FACEBOOK_FAMILY_NAME
        #     )
        # )
        
        # Outputs for reference
        CfnOutput(
            self,
            "UserPoolId",
            value=self.user_pool.user_pool_id,
            description="Cognito User Pool ID",
            export_name=f"ImpressionnistesUserPoolId-{env_name}"
        )
        
        CfnOutput(
            self,
            "UserPoolClientId",
            value=self.user_pool_client.user_pool_client_id,
            description="Cognito User Pool Client ID",
            export_name=f"ImpressionnistesUserPoolClientId-{env_name}"
        )
        
        CfnOutput(
            self,
            "UserPoolDomain",
            value=f"https://{self.user_pool_domain.domain_name}.auth.{self.region}.amazoncognito.com",
            description="Cognito Hosted UI Domain",
            export_name=f"ImpressionnistesUserPoolDomain-{env_name}"
        )
    
    def configure_ui_customization(self, logo_url: str):
        """
        Configure Cognito Hosted UI customization with logo and CSS.
        This should be called after the frontend stack is created.
        """
        # Custom CSS for Cognito Hosted UI
        custom_css = """
        .logo-customizable {
            max-width: 200px;
            max-height: 100px;
        }
        .banner-customizable {
            background-color: #1976d2;
        }
        .submitButton-customizable {
            background-color: #1976d2;
        }
        .submitButton-customizable:hover {
            background-color: #1565c0;
        }
        """
        
        # Create a Lambda function to set UI customization
        ui_customization_lambda = lambda_.Function(
            self,
            "CognitoUICustomization",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=lambda_.Code.from_inline(f"""
import boto3
import json
import urllib.request
import cfnresponse

cognito = boto3.client('cognito-idp')

def handler(event, context):
    try:
        request_type = event['RequestType']
        user_pool_id = event['ResourceProperties']['UserPoolId']
        client_id = event['ResourceProperties']['ClientId']
        logo_url = event['ResourceProperties']['LogoUrl']
        css = event['ResourceProperties']['CSS']
        
        if request_type in ['Create', 'Update']:
            # Try to download logo from URL
            logo_data = None
            try:
                with urllib.request.urlopen(logo_url, timeout=10) as response:
                    logo_data = response.read()
                print(f"Successfully downloaded logo from {{logo_url}}")
            except Exception as logo_error:
                print(f"Warning: Could not download logo from {{logo_url}}: {{str(logo_error)}}")
                print("Proceeding with CSS-only customization")
            
            # Set UI customization (with or without logo)
            if logo_data:
                cognito.set_ui_customization(
                    UserPoolId=user_pool_id,
                    ClientId=client_id,
                    CSS=css,
                    ImageFile=logo_data
                )
                print("UI customization applied with logo and CSS")
            else:
                cognito.set_ui_customization(
                    UserPoolId=user_pool_id,
                    ClientId=client_id,
                    CSS=css
                )
                print("UI customization applied with CSS only (logo will be added on next update)")
            
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {{}})
        elif request_type == 'Delete':
            # Remove UI customization on stack deletion
            try:
                cognito.set_ui_customization(
                    UserPoolId=user_pool_id,
                    ClientId=client_id
                )
            except:
                pass  # Ignore errors on deletion
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {{}})
    except Exception as e:
        print(f"Error: {{str(e)}}")
        # Don't fail the stack - just log the error
        print("Warning: UI customization failed but not blocking stack deployment")
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {{}})
"""),
            timeout=Duration.seconds(60),
            initial_policy=[
                iam.PolicyStatement(
                    actions=[
                        "cognito-idp:SetUICustomization",
                        "cognito-idp:GetUICustomization"
                    ],
                    resources=[self.user_pool.user_pool_arn]
                )
            ]
        )
        
        # Create custom resource to trigger the Lambda
        cr.AwsCustomResource(
            self,
            "CognitoUICustomizationResource",
            on_create=cr.AwsSdkCall(
                service="Lambda",
                action="invoke",
                parameters={
                    "FunctionName": ui_customization_lambda.function_name,
                    "Payload": json.dumps({
                        "RequestType": "Create",
                        "ResourceProperties": {
                            "UserPoolId": self.user_pool.user_pool_id,
                            "ClientId": self.user_pool_client.user_pool_client_id,
                            "LogoUrl": logo_url,
                            "CSS": custom_css
                        }
                    })
                },
                physical_resource_id=cr.PhysicalResourceId.of("CognitoUICustomization")
            ),
            on_update=cr.AwsSdkCall(
                service="Lambda",
                action="invoke",
                parameters={
                    "FunctionName": ui_customization_lambda.function_name,
                    "Payload": json.dumps({
                        "RequestType": "Update",
                        "ResourceProperties": {
                            "UserPoolId": self.user_pool.user_pool_id,
                            "ClientId": self.user_pool_client.user_pool_client_id,
                            "LogoUrl": logo_url,
                            "CSS": custom_css
                        }
                    })
                }
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    actions=["lambda:InvokeFunction"],
                    resources=[ui_customization_lambda.function_arn]
                )
            ])
        )
