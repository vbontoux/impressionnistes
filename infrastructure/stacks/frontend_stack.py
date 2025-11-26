"""
Frontend Stack - S3, CloudFront, and Static Website Hosting
Course des Impressionnistes Registration System
"""
from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput,
    Duration,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3_deployment,
)
from constructs import Construct
import os


class FrontendStack(Stack):
    """
    Stack for frontend deployment with S3 and CloudFront CDN.
    Serves the Vue.js application with HTTPS.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        api_stack=None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.api_stack = api_stack
        env_name = self.node.try_get_context("env") or "dev"
        
        # S3 bucket for static website hosting
        self.website_bucket = s3.Bucket(
            self,
            "WebsiteBucket",
            bucket_name=f"rcpm-impressionnistes-frontend-{env_name}",
            public_read_access=False,  # CloudFront will access via OAI
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY if env_name == "dev" else RemovalPolicy.RETAIN,
            auto_delete_objects=True if env_name == "dev" else False,
            versioned=True,  # Enable versioning for rollback capability
            encryption=s3.BucketEncryption.S3_MANAGED,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldVersions",
                    noncurrent_version_expiration=Duration.days(30),
                    enabled=True
                )
            ]
        )
        
        # Origin Access Identity for CloudFront to access S3
        oai = cloudfront.OriginAccessIdentity(
            self,
            "OAI",
            comment=f"OAI for Impressionnistes Frontend {env_name}"
        )
        
        # Grant CloudFront read access to the bucket
        self.website_bucket.grant_read(oai)
        
        # CloudFront distribution
        self.distribution = cloudfront.Distribution(
            self,
            "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    self.website_bucket,
                    origin_access_identity=oai
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD_OPTIONS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                compress=True,
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(5)
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(5)
                )
            ],
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,  # Use only North America and Europe
            comment=f"Impressionnistes Frontend Distribution {env_name}"
        )
        
        # Deploy frontend files (if dist folder exists)
        frontend_dist_path = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
        if os.path.exists(frontend_dist_path):
            s3_deployment.BucketDeployment(
                self,
                "DeployWebsite",
                sources=[s3_deployment.Source.asset(frontend_dist_path)],
                destination_bucket=self.website_bucket,
                distribution=self.distribution,
                distribution_paths=["/*"],  # Invalidate all paths
                prune=True,  # Remove old files
            )
        
        # Outputs
        CfnOutput(
            self,
            "WebsiteBucketName",
            value=self.website_bucket.bucket_name,
            description="S3 bucket name for frontend"
        )
        
        CfnOutput(
            self,
            "DistributionId",
            value=self.distribution.distribution_id,
            description="CloudFront distribution ID"
        )
        
        CfnOutput(
            self,
            "DistributionDomainName",
            value=self.distribution.distribution_domain_name,
            description="CloudFront distribution domain name"
        )
        
        CfnOutput(
            self,
            "WebsiteURL",
            value=f"https://{self.distribution.distribution_domain_name}",
            description="Frontend website URL",
            export_name=f"ImpressiornistesFrontendURL-{env_name}"
        )
