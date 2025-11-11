# Secrets Management

## Current Approach (Development)

For development and initial deployment, secrets are stored in `secrets.json` file.

### Setup

1. **Copy the example file:**
   ```bash
   cd infrastructure
   cp secrets.json.example secrets.json
   ```

2. **Edit with your values:**
   ```bash
   # Edit secrets.json
   nano secrets.json
   ```

3. **Add your secrets:**
   ```json
   {
     "slack_webhook_admin": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
     "slack_webhook_devops": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
     "stripe_secret_key_dev": "sk_test_...",
     "stripe_secret_key_prod": "sk_live_...",
     "stripe_webhook_secret_dev": "whsec_...",
     "stripe_webhook_secret_prod": "whsec_..."
   }
   ```

### Security

✅ **File is gitignored** - Never committed to repository  
✅ **Only used during deployment** - Loaded by init Lambda  
✅ **Local only** - Stays on your machine  

⚠️ **Important:**
- Never commit `secrets.json` to git
- Keep backups in a secure location (password manager, encrypted drive)
- Rotate secrets regularly
- Use different secrets for dev and prod

### How It Works

1. **During deployment**, the init Lambda function reads `secrets.json`
2. **Secrets are stored** in DynamoDB configuration
3. **Application reads** secrets from DynamoDB at runtime

### Verify Secrets Are Loaded

```bash
# After deployment, check configuration
make db-view

# Or query directly
aws dynamodb get-item \
  --table-name impressionnistes-registration-dev \
  --key '{"PK":{"S":"CONFIG"},"SK":{"S":"NOTIFICATION"}}' \
  --query 'Item.slack_webhook_admin.S'
```

## Future Approach (Production)

For production, we'll migrate to **AWS Secrets Manager**.

### Why Secrets Manager?

- ✅ Automatic rotation
- ✅ Encryption at rest
- ✅ Fine-grained access control
- ✅ Audit logging
- ✅ Cross-region replication
- ✅ Integration with Lambda

### Migration Plan

When implementing the security stack (future task):

1. **Create Secrets Manager stack**
2. **Store secrets in Secrets Manager**
3. **Update Lambda to read from Secrets Manager**
4. **Remove secrets.json dependency**

### Secrets Manager Structure

```json
{
  "slack": {
    "webhook_admin": "https://...",
    "webhook_devops": "https://..."
  },
  "stripe": {
    "secret_key": "sk_...",
    "webhook_secret": "whsec_..."
  }
}
```

## Current Secrets

### Slack Webhooks

**Purpose:** Send notifications to Slack channels

**How to get:**
1. Go to your Slack workspace
2. Apps → Incoming Webhooks
3. Add to channel
4. Copy webhook URL

**Format:** `https://hooks.slack.com/services/T.../B.../...`

### Stripe Keys

**Purpose:** Process payments

**How to get:**
1. Go to Stripe Dashboard
2. Developers → API Keys
3. Copy Secret Key (starts with `sk_test_` or `sk_live_`)
4. Copy Webhook Secret (starts with `whsec_`)

**Dev vs Prod:**
- Dev: Use test mode keys (`sk_test_...`)
- Prod: Use live mode keys (`sk_live_...`)

## Troubleshooting

### Secrets not loading

**Check file exists:**
```bash
ls -la infrastructure/secrets.json
```

**Check file format:**
```bash
cat infrastructure/secrets.json | python3 -m json.tool
```

### Secrets not in DynamoDB

**Redeploy:**
```bash
make redeploy
```

**Check Lambda logs:**
```bash
aws logs tail /aws/lambda/ImpressionnistesDatabase-dev-InitConfigFunction --follow
```

### Wrong secrets deployed

**Update secrets.json and redeploy:**
```bash
# Edit secrets
nano infrastructure/secrets.json

# Redeploy
make redeploy
```

## Best Practices

### Development

1. **Use test credentials** - Never use production secrets in dev
2. **Rotate regularly** - Change secrets every 90 days
3. **Limit access** - Only share with team members who need them
4. **Backup securely** - Store in password manager

### Production

1. **Use Secrets Manager** - Migrate when implementing security stack
2. **Enable rotation** - Automatic secret rotation
3. **Monitor access** - CloudTrail logging
4. **Separate environments** - Different secrets for dev/prod

## Secret Rotation

### Manual Rotation (Current)

1. **Generate new secret** (e.g., new Slack webhook)
2. **Update secrets.json**
3. **Redeploy:** `make redeploy`
4. **Verify:** `make db-view`
5. **Revoke old secret**

### Automatic Rotation (Future with Secrets Manager)

```python
# Lambda function for automatic rotation
def rotate_secret(event, context):
    # Generate new secret
    # Update Secrets Manager
    # Update application
    # Revoke old secret
    pass
```

## Security Checklist

- [ ] `secrets.json` is in `.gitignore`
- [ ] Never commit secrets to git
- [ ] Use different secrets for dev and prod
- [ ] Store backup in password manager
- [ ] Rotate secrets every 90 days
- [ ] Monitor secret usage in CloudWatch
- [ ] Plan migration to Secrets Manager for production

## Related Commands

```bash
# View current configuration
make db-view

# Export configuration (includes secrets!)
make db-export

# Redeploy with new secrets
make redeploy

# Check Lambda logs
aws logs tail /aws/lambda/ImpressionnistesDatabase-dev-InitConfigFunction
```

## Migration to Secrets Manager

When ready to implement (future task):

```bash
# 1. Create secrets in Secrets Manager
aws secretsmanager create-secret \
  --name impressionnistes/slack \
  --secret-string file://secrets.json

# 2. Update Lambda to read from Secrets Manager
# 3. Deploy new code
# 4. Remove secrets.json
# 5. Update documentation
```

## Support

For questions about secrets management:
- Check CloudWatch logs for init Lambda
- Verify secrets.json format
- Ensure file is not committed to git
- Contact DevOps team for production secrets
