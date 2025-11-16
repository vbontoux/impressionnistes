"""
Authentication Stack - Amazon Cognito User Pool
Course des Impressionnistes Registration System
"""
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_cognito as cognito,
    CfnOutput,
)
from constructs import Construct


class AuthStack(Stack):
    """
    Stack for authentication using Amazon Cognito.
    Includes user pool, app client, and social login configuration.
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
                require_symbols=False,  # Optional for better UX
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
            removal_policy=RemovalPolicy.RETAIN if env_name == 'prod' else RemovalPolicy.DESTROY
        )
        
        # Create user pool domain for hosted UI
        self.user_pool_domain = self.user_pool.add_domain(
            "UserPoolDomain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=f"impressionnistes-{env_name}"
            )
        )
        
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
                callback_urls=[
                    "http://localhost:3000/callback",  # Development
                    f"https://impressionnistes-{env_name}.rcpm-aviron.fr/callback"  # Production
                ],
                logout_urls=[
                    "http://localhost:3000/",  # Development
                    f"https://impressionnistes-{env_name}.rcpm-aviron.fr/"  # Production
                ]
            ),
            
            # Token validity
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
                custom=False,
                admin_user_password=True
            ),
            
            # Session configuration (30 minutes as per requirements)
            access_token_validity=Duration.minutes(30),
            id_token_validity=Duration.minutes(30),
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
