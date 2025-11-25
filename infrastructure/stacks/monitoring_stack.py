"""
Monitoring Stack - CloudWatch Logs, Alarms, and SNS Topics
Course des Impressionnistes Registration System
"""
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions,
    aws_logs as logs,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
)
from constructs import Construct
import os


class MonitoringStack(Stack):
    """
    Stack for monitoring, logging, and alerting infrastructure.
    Includes CloudWatch logs, alarms, and SNS topics for notifications.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        database_stack=None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get environment from context
        env_name = self.node.try_get_context("env") or "dev"
        env_config = self.node.try_get_context(env_name) or {}
    
    def _get_logs_removal_policy(self, env_name: str) -> RemovalPolicy:
        """Get removal policy for CloudWatch logs based on environment configuration"""
        env_config = self.node.try_get_context(env_name) or {}
        
        # Use specific logs policy if available, otherwise default based on environment
        logs_policy_str = env_config.get("removal_policy_logs")
        
        if logs_policy_str:
            return RemovalPolicy.DESTROY if logs_policy_str == "DESTROY" else RemovalPolicy.RETAIN
        
        # Default: RETAIN for prod, DESTROY for dev
        return RemovalPolicy.RETAIN if env_name == 'prod' else RemovalPolicy.DESTROY
        
        # Create SNS topic for DevOps notifications
        self.devops_topic = sns.Topic(
            self,
            "DevOpsTopic",
            topic_name=f"impressionnistes-devops-{env_name}",
            display_name="Impressionnistes DevOps Notifications"
        )
        
        # Create SNS topic for Admin notifications
        self.admin_topic = sns.Topic(
            self,
            "AdminTopic",
            topic_name=f"impressionnistes-admin-{env_name}",
            display_name="Impressionnistes Admin Notifications"
        )
        
        # Add email subscriptions (can be configured via environment variables)
        # Note: Email subscriptions require confirmation
        # devops_email = env_config.get('devops_email')
        # if devops_email:
        #     self.devops_topic.add_subscription(
        #         sns_subscriptions.EmailSubscription(devops_email)
        #     )
        
        # Create CloudWatch log groups for Lambda functions
        self.log_groups = {}
        
        # Log group for init function
        self.log_groups['init'] = logs.LogGroup(
            self,
            "InitFunctionLogGroup",
            log_group_name=f"/aws/lambda/ImpressionnistesDatabase-{env_name}-InitConfigFunction",
            retention=logs.RetentionDays.ONE_WEEK if env_name == 'dev' else logs.RetentionDays.ONE_MONTH,
            removal_policy=self._get_logs_removal_policy(env_name)
        )
        
        # Create CloudWatch alarms for Lambda errors
        if database_stack and database_stack.table:
            # Alarm for DynamoDB read throttling
            read_throttle_alarm = cloudwatch.Alarm(
                self,
                "DynamoDBReadThrottleAlarm",
                alarm_name=f"impressionnistes-{env_name}-dynamodb-read-throttle",
                metric=database_stack.table.metric_user_errors(
                    statistic="Sum",
                    period=Duration.minutes(5)
                ),
                threshold=10,
                evaluation_periods=2,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
                alarm_description="DynamoDB read throttling detected",
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING
            )
            read_throttle_alarm.add_alarm_action(cw_actions.SnsAction(self.devops_topic))
            
            # Alarm for DynamoDB throttled requests (combined read/write)
            throttle_alarm = cloudwatch.Alarm(
                self,
                "DynamoDBThrottleAlarm",
                alarm_name=f"impressionnistes-{env_name}-dynamodb-throttle",
                metric=cloudwatch.Metric(
                    namespace="AWS/DynamoDB",
                    metric_name="UserErrors",
                    dimensions_map={
                        "TableName": database_stack.table.table_name
                    },
                    statistic="Sum",
                    period=Duration.minutes(5)
                ),
                threshold=10,
                evaluation_periods=2,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
                alarm_description="DynamoDB throttling detected (read or write)",
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING
            )
            throttle_alarm.add_alarm_action(cw_actions.SnsAction(self.devops_topic))
        
        # Create CloudWatch dashboard
        self.dashboard = cloudwatch.Dashboard(
            self,
            "SystemDashboard",
            dashboard_name=f"Impressionnistes-{env_name}",
        )
        
        # Add DynamoDB metrics to dashboard
        if database_stack and database_stack.table:
            self.dashboard.add_widgets(
                cloudwatch.GraphWidget(
                    title="DynamoDB Read/Write Capacity",
                    left=[
                        database_stack.table.metric_consumed_read_capacity_units(),
                        database_stack.table.metric_consumed_write_capacity_units()
                    ],
                    width=12
                ),
                cloudwatch.GraphWidget(
                    title="DynamoDB Throttled Requests",
                    left=[
                        database_stack.table.metric_user_errors()
                    ],
                    width=12
                )
            )
        
        # Store alarms for reference
        self.alarms = {}
        if database_stack and database_stack.table:
            self.alarms['dynamodb_read_throttle'] = read_throttle_alarm
            self.alarms['dynamodb_throttle'] = throttle_alarm
        
        # Create health check Lambda function
        if database_stack and database_stack.table:
            self.health_check_function = lambda_.Function(
                self,
                "HealthCheckFunction",
                runtime=lambda_.Runtime.PYTHON_3_11,
                handler="health_check.lambda_handler",
                code=lambda_.Code.from_asset(
                    os.path.join(os.path.dirname(__file__), "../../functions/health")
                ),
                timeout=Duration.seconds(30),
                environment={
                    'TABLE_NAME': database_stack.table.table_name,
                    'ENVIRONMENT': env_name,
                },
                description="Health check endpoint for system monitoring"
            )
            
            # Grant read permissions to DynamoDB
            database_stack.table.grant_read_data(self.health_check_function)
            
            # Create log group for health check function
            self.log_groups['health_check'] = logs.LogGroup(
                self,
                "HealthCheckLogGroup",
                log_group_name=f"/aws/lambda/{self.health_check_function.function_name}",
                retention=logs.RetentionDays.ONE_WEEK if env_name == 'dev' else logs.RetentionDays.ONE_MONTH,
                removal_policy=self._get_logs_removal_policy(env_name)
            )
            
            # Create CloudWatch alarm for health check failures
            health_check_alarm = cloudwatch.Alarm(
                self,
                "HealthCheckAlarm",
                alarm_name=f"impressionnistes-{env_name}-health-check-failed",
                metric=self.health_check_function.metric_errors(
                    statistic="Sum",
                    period=Duration.minutes(5)
                ),
                threshold=3,
                evaluation_periods=2,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
                alarm_description="Health check function is failing",
                treat_missing_data=cloudwatch.TreatMissingData.BREACHING
            )
            health_check_alarm.add_alarm_action(cw_actions.SnsAction(self.devops_topic))
            self.alarms['health_check'] = health_check_alarm
            
            # Schedule health check to run every 5 minutes
            health_check_rule = events.Rule(
                self,
                "HealthCheckSchedule",
                schedule=events.Schedule.rate(Duration.minutes(5)),
                description="Run health check every 5 minutes"
            )
            health_check_rule.add_target(targets.LambdaFunction(self.health_check_function))
            
            # Add Lambda metrics to dashboard
            self.dashboard.add_widgets(
                cloudwatch.GraphWidget(
                    title="Health Check Function",
                    left=[
                        self.health_check_function.metric_invocations(),
                        self.health_check_function.metric_errors()
                    ],
                    width=12
                ),
                cloudwatch.GraphWidget(
                    title="Health Check Duration",
                    left=[self.health_check_function.metric_duration()],
                    width=12
                )
            )
