# Email Deliverability Guide

## Problem: Emails Going to Junk/Spam

If your test emails are landing in junk folders and marked as "unverified" in Outlook, this is a common deliverability issue caused by missing email authentication.

### Why This Happens

Email providers (Gmail, Outlook, etc.) check for authentication signals:

1. **SPF (Sender Policy Framework)** - Verifies the sending server is authorized
2. **DKIM (DomainKeys Identified Mail)** - Cryptographic signature proving authenticity
3. **DMARC (Domain-based Message Authentication)** - Policy for handling failed authentication
4. **Domain Reputation** - New/unverified domains have low trust scores

When you only verify an email address (not the full domain), AWS SES:
- ✅ Allows sending from that address
- ❌ Doesn't add DKIM signatures
- ❌ Doesn't configure SPF records
- ❌ Results in "unverified" labels and spam folder placement

## Solutions (Ranked by Effectiveness)

### Solution 1: Verify Full Domain with DKIM (Recommended)

This is the best long-term solution for production use.

**Benefits:**
- ✅ Automatic DKIM signatures on all emails
- ✅ Better deliverability (inbox instead of spam)
- ✅ Professional appearance (no "unverified" warnings)
- ✅ Can send from any address @yourdomain.com
- ✅ Builds domain reputation over time

**Requirements:**
- Access to your domain's DNS settings
- Ability to add TXT and CNAME records

**Steps:**

1. **Initiate domain verification:**
   ```bash
   cd infrastructure
   make ses-verify-domain DOMAIN=rcpm-aviron.fr ENV=dev
   ```

2. **Get the verification token:**
   ```bash
   cd infrastructure
   make ses-get-domain-token DOMAIN=rcpm-aviron.fr ENV=dev
   ```

3. **Add TXT record to your DNS:**
   - Name: `_amazonses.rcpm-aviron.fr`
   - Type: `TXT`
   - Value: `[token from step 2]`
   - TTL: `300` (or your DNS provider's default)

4. **Wait for DNS propagation** (5-30 minutes)

5. **Enable DKIM signing:**
   ```bash
   cd infrastructure
   make ses-enable-dkim DOMAIN=rcpm-aviron.fr ENV=dev
   ```

6. **Add the 3 DKIM CNAME records to your DNS:**
   
   For each token returned, create a CNAME record:
   - Name: `[token]._domainkey.rcpm-aviron.fr`
   - Type: `CNAME`
   - Value: `[token].dkim.amazonses.com`
   - TTL: `300`

7. **Verify everything is working:**
   ```bash
   cd infrastructure
   make ses-check-domain DOMAIN=rcpm-aviron.fr ENV=dev
   ```

8. **Test email delivery:**
   ```bash
   cd infrastructure
   make test-email EMAIL=your-email@example.com ENV=dev
   ```

**Expected Result:**
- Emails arrive in inbox (not junk)
- No "unverified" warnings
- DKIM signature visible in email headers

---

### Solution 2: Add SPF Record (Quick Improvement)

If you can't do full domain verification yet, adding an SPF record helps.

**Add this TXT record to your DNS:**
- Name: `rcpm-aviron.fr` (or `@` depending on DNS provider)
- Type: `TXT`
- Value: `v=spf1 include:amazonses.com ~all`
- TTL: `300`

This tells email providers that Amazon SES is authorized to send emails for your domain.

**Improvement:** Moderate (helps but not as much as DKIM)

---

### Solution 3: Request SES Production Access

Moving out of sandbox mode improves reputation.

```bash
cd infrastructure
make ses-request-production ENV=dev
```

Follow the instructions to request production access through AWS Console.

**Benefits:**
- Better sending reputation
- Can send to any email (not just verified ones)
- Higher sending limits

**Note:** This alone won't fix the "unverified" issue - you still need DKIM.

---

### Solution 4: Use a Dedicated Email Service (Alternative)

If DNS configuration is not possible, consider using a dedicated transactional email service:

- **SendGrid** - Easy setup, good deliverability
- **Mailgun** - Developer-friendly API
- **Postmark** - Excellent deliverability focus

These services handle all authentication automatically.

---

## Checking Your Current Setup

### Check Email Verification Status

```bash
cd infrastructure
make ses-list-verified ENV=dev
```

### Check Domain Verification Status

```bash
cd infrastructure
make ses-check-domain DOMAIN=rcpm-aviron.fr ENV=dev
```

### Check Email Headers

After receiving a test email, view the full headers to see:
- **SPF:** Should show `PASS`
- **DKIM:** Should show `PASS` (only if domain verified with DKIM)
- **DMARC:** Should show `PASS` (if you have DMARC policy)

**In Gmail:**
1. Open the email
2. Click the three dots (⋮)
3. Select "Show original"
4. Look for `SPF`, `DKIM`, and `DMARC` results

**In Outlook:**
1. Open the email
2. File → Properties
3. Look at the headers in the "Internet headers" box

---

## DNS Configuration Examples

### For Cloudflare

1. Go to your domain in Cloudflare
2. Click "DNS" tab
3. Add records as shown above
4. Set Proxy status to "DNS only" (gray cloud)

### For OVH

1. Go to your domain management
2. Click "DNS Zone"
3. Add TXT and CNAME records
4. Wait for propagation (can take up to 24 hours)

### For AWS Route 53

1. Go to Route 53 console
2. Select your hosted zone
3. Create record sets for TXT and CNAME records
4. Propagation is usually instant

---

## Testing Deliverability

### Test with Mail-Tester

1. Send a test email to the address provided by [mail-tester.com](https://www.mail-tester.com/)
2. Check your score (aim for 8/10 or higher)
3. Review the detailed report for issues

### Test with Multiple Providers

Send test emails to:
- Gmail account
- Outlook/Hotmail account
- Yahoo account
- Your organization's email

Check if they arrive in inbox or spam folder.

---

## Troubleshooting

### "Domain verification pending"

**Cause:** DNS records not propagated yet

**Solution:**
- Wait 5-30 minutes for DNS propagation
- Check DNS records with: `dig TXT _amazonses.rcpm-aviron.fr`
- Verify you added the record correctly

### "DKIM not enabled"

**Cause:** DKIM CNAME records not added or incorrect

**Solution:**
- Verify you added all 3 CNAME records
- Check with: `dig CNAME [token]._domainkey.rcpm-aviron.fr`
- Ensure CNAME values end with `.dkim.amazonses.com`

### Still going to spam after domain verification

**Possible causes:**
1. **New domain** - Needs time to build reputation
2. **Missing DMARC** - Add DMARC policy (see below)
3. **Content triggers** - Avoid spam trigger words
4. **Low engagement** - Recipients not opening emails

**Add DMARC policy:**
- Name: `_dmarc.rcpm-aviron.fr`
- Type: `TXT`
- Value: `v=DMARC1; p=none; rua=mailto:dmarc@rcpm-aviron.fr`

### Emails still marked "unverified" in Outlook

**Cause:** Outlook is very strict about authentication

**Solution:**
1. Ensure DKIM is fully configured and passing
2. Add DMARC policy
3. Build sender reputation by sending to engaged users
4. Consider using Microsoft 365 for sending if you have it

---

## Production Checklist

Before going to production:

- [ ] Domain verified in SES
- [ ] DKIM enabled and all 3 CNAME records added
- [ ] SPF record added to DNS
- [ ] DMARC policy added (optional but recommended)
- [ ] Test emails arriving in inbox (not spam)
- [ ] No "unverified" warnings in major email clients
- [ ] Mail-tester.com score is 8/10 or higher
- [ ] SES production access approved
- [ ] Bounce and complaint handling configured

---

## Quick Reference

```bash
# Verify domain
make ses-verify-domain DOMAIN=rcpm-aviron.fr ENV=dev

# Get verification token
make ses-get-domain-token DOMAIN=rcpm-aviron.fr ENV=dev

# Enable DKIM
make ses-enable-dkim DOMAIN=rcpm-aviron.fr ENV=dev

# Check domain status
make ses-check-domain DOMAIN=rcpm-aviron.fr ENV=dev

# Test email
make test-email EMAIL=your@email.com ENV=dev
```

---

## Additional Resources

- [AWS SES Domain Verification](https://docs.aws.amazon.com/ses/latest/dg/verify-domain-procedure.html)
- [AWS SES DKIM Setup](https://docs.aws.amazon.com/ses/latest/dg/send-email-authentication-dkim-easy.html)
- [SPF Record Syntax](https://www.spf-record.com/)
- [DMARC Policy Generator](https://www.dmarcanalyzer.com/dmarc/dmarc-record-generator/)
- [Mail Tester](https://www.mail-tester.com/) - Test email deliverability

---

## Summary

**For immediate testing:** Accept that emails will go to spam until proper authentication is configured.

**For production:** Verify your full domain with DKIM enabled. This is the only reliable way to ensure good deliverability and avoid "unverified" warnings.

The DNS configuration takes about 30 minutes to set up and will dramatically improve your email deliverability.
