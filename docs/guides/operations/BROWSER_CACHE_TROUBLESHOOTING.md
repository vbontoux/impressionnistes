# Browser Cache Troubleshooting

## Problem: Changes Not Appearing After Deployment

When you deploy frontend changes but users still see the old version, this is typically a browser caching issue.

## Symptoms

- Deployment successful, CloudFront cache cleared
- Files on S3 are correct and current
- But browser still shows old version
- Works in incognito mode or different browser

## Root Cause

Browsers aggressively cache JavaScript and CSS assets. Even after CloudFront invalidation, the browser may continue using its locally cached version.

## Solutions (Try in Order)

### Solution 1: Hard Refresh with DevTools

**Most effective method:**

1. Open the deployed site
2. Press **F12** to open Developer Tools
3. Go to the **Network** tab
4. Check **"Disable cache"** at the top
5. Keep DevTools open
6. Press **Cmd+Shift+R** (Mac) or **Ctrl+Shift+R** (Windows/Linux)

### Solution 2: Clear Browser Cache

**Chrome/Edge:**
1. Press **Cmd+Shift+Delete** (Mac) or **Ctrl+Shift+Delete** (Windows)
2. Select "Cached images and files"
3. Time range: "All time"
4. Click "Clear data"

**Firefox:**
1. Press **Cmd+Shift+Delete** (Mac) or **Ctrl+Shift+Delete** (Windows)
2. Select "Cache"
3. Time range: "Everything"
4. Click "Clear Now"

**Safari:**
1. Safari → Preferences → Advanced
2. Check "Show Develop menu in menu bar"
3. Develop → Empty Caches

### Solution 3: Incognito/Private Mode

Open a new incognito/private window and test. This confirms it's a caching issue since private mode has no cache.

### Solution 4: Different Browser

Try a browser you haven't used before. If it works there, it's definitely a cache issue.

### Solution 5: Wait for Natural Expiry

Browser cache typically expires within 24 hours. The issue will resolve itself.

## Verification Commands

Check that deployed files are correct:

```bash
# Check JavaScript file referenced in HTML
aws s3 cp s3://rcpm-impressionnistes-frontend-dev/index.html - | grep "index-.*\.js"

# Verify code is in deployed JavaScript
aws s3 cp s3://rcpm-impressionnistes-frontend-dev/assets/index-XXXXX.js - | grep -c "searchTerm"

# Check CloudFront invalidation status
aws cloudfront list-invalidations --distribution-id DISTRIBUTION_ID --max-items 5
```

## Prevention

### For Developers

**Use cache-busting filenames:**
- Vite automatically adds content hashes to filenames (e.g., `index-BsFVSMVL.js`)
- This ensures new deployments get new filenames
- Browsers fetch new files automatically

**Set proper cache headers:**
- HTML files: Short cache (1 hour)
- JS/CSS with hashes: Long cache (1 year)
- Already configured in CloudFront distribution

### For Users

**Educate users:**
- Hard refresh after major updates: Cmd+Shift+R / Ctrl+Shift+R
- Clear cache if issues persist
- Use incognito mode to test

## Related Issues

### Issue: Translation Changes Not Appearing

**Cause:** Translation files cached by browser

**Solution:** Same as above - hard refresh or clear cache

### Issue: CSS Changes Not Appearing

**Cause:** Stylesheet cached by browser

**Solution:** Same as above - hard refresh or clear cache

### Issue: Works Locally But Not Deployed

**Cause:** Local dev server doesn't cache aggressively

**Solution:** Verify deployment is correct, then clear browser cache

## Debugging Steps

If cache clearing doesn't work:

1. **Check browser console** (F12 → Console)
   - Look for JavaScript errors
   - Check for failed network requests

2. **Check Network tab** (F12 → Network)
   - Verify correct files are loaded
   - Check file sizes match deployed versions
   - Look for 304 (cached) vs 200 (fresh) responses

3. **Verify CloudFront**
   ```bash
   # Check invalidation completed
   aws cloudfront get-invalidation \
     --distribution-id DISTRIBUTION_ID \
     --id INVALIDATION_ID
   ```

4. **Verify S3 files**
   ```bash
   # List files with timestamps
   aws s3 ls s3://bucket-name/assets/ --recursive
   ```

## When to Escalate

If after trying all solutions:
- Issue persists in multiple browsers
- Issue persists in incognito mode
- CloudFront invalidation shows "Completed"
- S3 files are verified correct

Then it may be a deployment issue, not a cache issue. Check:
- Build process completed successfully
- Correct environment variables used
- Files uploaded to correct S3 bucket
- CloudFront distribution points to correct origin

## Related Documentation

- CloudFront cache clearing: `scripts/deployment/README.md`
- Frontend deployment: `docs/guides/development/frontend-deployment.md`
- Troubleshooting guide: `docs/guides/operations/troubleshooting.md`
