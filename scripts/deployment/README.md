# Deployment Scripts

Infrastructure deployment and AWS management scripts.

## Scripts

### deploy.sh
Deploy all infrastructure stacks to AWS.

**Usage:**
```bash
./deploy.sh [dev|prod]
```

**What it does:**
- Activates Python virtual environment
- Installs/updates dependencies
- Bootstraps CDK (if needed)
- Synthesizes CloudFormation templates
- Deploys all stacks

**Recommended:** Use Makefile instead:
```bash
cd infrastructure
make deploy-dev
make deploy-prod
```

---

### clean-all-aws.sh
Complete AWS cleanup: destroys stacks, retained resources, and orphaned resources.

**Usage:**
```bash
./clean-all-aws.sh --profile <aws-profile> [--env dev|prod]
```

**`--profile` is required** — no default profile is used.

**What it cleans (in order):**
1. CloudFormation stacks (handles stuck/failed stacks)
2. DynamoDB table (retained by RemovalPolicy)
3. Cognito User Pool + domain (retained by RemovalPolicy)
4. Secrets Manager secrets (retained by RemovalPolicy)
5. Orphaned Lambda functions
6. Orphaned CloudWatch log groups

Each destructive step prompts for confirmation. Production requires typing `DELETE PRODUCTION`.

**Recommended:** Use Makefile instead:
```bash
cd infrastructure
make clean-aws PROFILE=my-profile ENV=dev
```

---

### create-certificates.sh
Create SSL certificates for CloudFront custom domains.

**Usage:**
```bash
./create-certificates.sh
```

**What it does:**
- Creates ACM certificates in us-east-1 (required for CloudFront)
- Provides DNS validation records
- Shows certificate ARNs for config.py

**Note:** Certificates must be validated via DNS before use.

---

### clear-cloudfront-cache.sh
Invalidate CloudFront distribution cache.

**Usage:**
```bash
./clear-cloudfront-cache.sh [dev|prod]
```

**When to use:**
- After frontend deployment
- When users see stale content
- After configuration changes

**Recommended:** Use Makefile instead:
```bash
cd infrastructure
make clear-cache ENV=dev
```

## Best Practices

1. **Always use Makefile commands** when available
2. **Test on dev first** before deploying to prod
3. **Check AWS credentials** before running (`aws sts get-caller-identity`)
4. **Use correct AWS profile** — `clean-all-aws.sh` requires explicit `--profile`
5. **Wait for deployments to complete** before making changes

## Troubleshooting

**Error: "AWS credentials not configured"**
- Run `aws configure` or set AWS environment variables

**Error: "Virtual environment not found"**
- Run `make setup` in infrastructure directory

**Error: "Stack is in failed state"**
- Use `make fix-stuck-stack` or `make clean-aws PROFILE=<profile>`

**Deployment takes too long**
- Check CloudFormation console for stack status
- Look for resource creation issues

## Related Documentation

- Infrastructure setup: `infrastructure/README.md`
- Makefile commands: Run `make help` in `infrastructure/`
- AWS CDK docs: https://docs.aws.amazon.com/cdk/
