# DNS Records to Add

## Step 1: Certificate Validation Records (Add These Now)

### For DEV Certificate (impressionnistes-dev.aviron-rcpm.fr)

**Record Type:** CNAME  
**Name:** `_97251b65e9052cb8c43073ad952dbe40.impressionnistes-dev.aviron-rcpm.fr`  
**Value:** `_e3368ce41044d0305d347d68e5b44eb5.jkddzztszm.acm-validations.aws.`  
**TTL:** 300 (5 minutes)

### For PROD Certificate (impressionnistes.aviron-rcpm.fr)

**Record Type:** CNAME  
**Name:** `_188612ced7299259a0df5f6049667f52.impressionnistes.aviron-rcpm.fr`  
**Value:** `_b54c7ac4132429955f1e426691b727d9.jkddzztszm.acm-validations.aws.`  
**TTL:** 300 (5 minutes)

---

## Step 2: CloudFront CNAME Records (Add After Deployment)

These will be added AFTER you deploy the stacks. The CloudFront domain names will be shown in the deployment output.

### For DEV (impressionnistes-dev.aviron-rcpm.fr)

**Record Type:** CNAME  
**Name:** `impressionnistes-dev.aviron-rcpm.fr`  
**Value:** `<cloudfront-domain-from-deployment-output>`  
**TTL:** 300 (5 minutes)

Example: `d1234567890abc.cloudfront.net`

### For PROD (impressionnistes.aviron-rcpm.fr)

**Record Type:** CNAME  
**Name:** `impressionnistes.aviron-rcpm.fr`  
**Value:** `<cloudfront-domain-from-deployment-output>`  
**TTL:** 300 (5 minutes)

Example: `d0987654321xyz.cloudfront.net`

---

## Certificate ARNs (Already Added to config.py)

✅ **DEV:** `arn:aws:acm:us-east-1:458847123929:certificate/79f8324b-b1e9-4416-ab5d-2b8e28969dae`  
✅ **PROD:** `arn:aws:acm:us-east-1:458847123929:certificate/e489019f-7fb8-461e-8174-a4334808eb01`

---

## Next Steps

1. ✅ **DONE:** Certificates created
2. ✅ **DONE:** Certificate ARNs added to config.py
3. ⏳ **TODO:** Add certificate validation CNAME records to DNS (Step 1 above)
4. ⏳ **TODO:** Wait for certificate validation (5-10 minutes)
5. ⏳ **TODO:** Deploy dev stack: `cd infrastructure && make deploy-dev`
6. ⏳ **TODO:** Add CloudFront CNAME record for dev (Step 2 above)
7. ⏳ **TODO:** Test dev domain
8. ⏳ **TODO:** Deploy prod stack: `cd infrastructure && make deploy-prod`
9. ⏳ **TODO:** Add CloudFront CNAME record for prod (Step 2 above)
10. ⏳ **TODO:** Test prod domain

---

## Check Certificate Validation Status

```bash
# Check DEV certificate
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:458847123929:certificate/79f8324b-b1e9-4416-ab5d-2b8e28969dae \
  --region us-east-1 \
  --query 'Certificate.Status' \
  --output text

# Check PROD certificate
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:458847123929:certificate/e489019f-7fb8-461e-8174-a4334808eb01 \
  --region us-east-1 \
  --query 'Certificate.Status' \
  --output text
```

Wait until both show `ISSUED` before deploying.

---

## Troubleshooting

### Certificates Stuck in "Pending Validation"

1. Verify DNS records are added correctly
2. Check DNS propagation: `dig _97251b65e9052cb8c43073ad952dbe40.impressionnistes-dev.aviron-rcpm.fr`
3. Wait up to 30 minutes
4. If still stuck, delete and recreate certificates

### DNS Records Not Propagating

1. Check TTL is set to 300 seconds (5 minutes)
2. Flush local DNS cache
3. Try from different network/location
4. Use online DNS checker: https://dnschecker.org/
