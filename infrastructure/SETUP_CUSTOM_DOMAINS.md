# Quick Setup Guide: Custom Domains for CloudFront

## Your Domains

✅ **Dev:** `impressionnistes-dev.aviron-rcpm.fr`  
✅ **Prod:** `impressionnistes.aviron-rcpm.fr`

## Step-by-Step Setup

### Step 1: Create SSL Certificates

Run the automated script:

```bash
cd infrastructure
chmod +x create-certificates.sh
./create-certificates.sh
```

This will:
- Create certificates in ACM (us-east-1 region)
- Show you the DNS validation records
- Display the certificate ARNs

**Alternative (Manual):**

```bash
# Dev certificate
aws acm request-certificate \
  --domain-name impressionnistes-dev.aviron-rcpm.fr \
  --validation-method DNS \
  --region us-east-1

# Prod certificate
aws acm request-certificate \
  --domain-name impressionnistes.aviron-rcpm.fr \
  --validation-method DNS \
  --region us-east-1
```

### Step 2: Add DNS Validation Records

The script will show you CNAME records like:

```
Name: _abc123.impressionnistes-dev.aviron-rcpm.fr
Value: _xyz789.acm-validations.aws.
```

Add these records to your DNS (in your domain registrar or Route53).

### Step 3: Wait for Validation

Check certificate status:

```bash
aws acm describe-certificate \
  --certificate-arn <your-cert-arn> \
  --region us-east-1 \
  --query 'Certificate.Status'
```

Wait until status is `ISSUED` (usually 5-10 minutes).

### Step 4: Update Config with Certificate ARNs

Edit `infrastructure/config.py` and replace the `None` values:

```python
DEV_CONFIG = {
    # ... existing config ...
    "custom_domain": "impressionnistes-dev.aviron-rcpm.fr",
    "certificate_arn": "arn:aws:acm:us-east-1:ACCOUNT:certificate/CERT_ID",  # ← Add your dev cert ARN
}

PROD_CONFIG = {
    # ... existing config ...
    "custom_domain": "impressionnistes.aviron-rcpm.fr",
    "certificate_arn": "arn:aws:acm:us-east-1:ACCOUNT:certificate/CERT_ID",  # ← Add your prod cert ARN
}
```

### Step 5: Deploy the Stacks

```bash
cd infrastructure

# Deploy dev
make deploy-dev

# Deploy prod (when ready)
make deploy-prod
```

The deployment will output the CloudFront domain names.

### Step 6: Update DNS with CNAME Records

After deployment, create CNAME records in your DNS:

**For Dev:**
- **Name:** `impressionnistes-dev.aviron-rcpm.fr`
- **Type:** CNAME
- **Value:** `d1234567890abc.cloudfront.net` (from deployment output)

**For Prod:**
- **Name:** `impressionnistes.aviron-rcpm.fr`
- **Type:** CNAME
- **Value:** `d0987654321xyz.cloudfront.net` (from deployment output)

### Step 7: Test

Wait for DNS propagation (5-30 minutes), then test:

```bash
# Test dev
curl -I https://impressionnistes-dev.aviron-rcpm.fr

# Test prod
curl -I https://impressionnistes.aviron-rcpm.fr
```

You should see `200 OK` responses.

## Current Status

✅ Domain names configured in `config.py`  
✅ Frontend stack updated to support custom domains  
⏳ **TODO:** Create SSL certificates and add ARNs to config  
⏳ **TODO:** Deploy stacks  
⏳ **TODO:** Update DNS records  

## Troubleshooting

### Certificate Validation Stuck

**Problem:** Certificate stays in "Pending validation" status.

**Solution:**
1. Verify DNS records are correct
2. Check DNS propagation: `dig _abc123.impressionnistes-dev.aviron-rcpm.fr`
3. Wait up to 30 minutes

### 403 Error After Deployment

**Problem:** Getting 403 error when accessing custom domain.

**Solution:**
1. Verify certificate ARN is in `config.py`
2. Redeploy the stack
3. Check CloudFront distribution in AWS Console shows your domain

### DNS Not Resolving

**Problem:** Domain doesn't resolve to CloudFront.

**Solution:**
1. Verify CNAME record exists: `dig impressionnistes-dev.aviron-rcpm.fr`
2. Wait for DNS propagation (up to 48 hours, usually much faster)
3. Clear your DNS cache: `sudo dscacheutil -flushcache` (macOS)

## Need Help?

Check the detailed guide: `infrastructure/CUSTOM_DOMAIN_SETUP.md`
