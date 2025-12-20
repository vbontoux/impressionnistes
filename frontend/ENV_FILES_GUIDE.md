# Environment Files Guide

## Overview

We use 3 environment files for different scenarios:

## Files

### 1. `.env.local` (gitignored)
**Purpose:** Local development with dev backend

**Usage:** Automatically used when running `npm run dev`

**Configuration:**
- Frontend: `http://localhost:3000`
- Backend: Dev API
- Cognito redirect: `http://localhost:3000/callback`

**When to use:** Daily development work on your local machine

---

### 2. `.env.dev` (committed to git)
**Purpose:** Dev deployment (both frontend and backend in dev)

**Usage:** Used when building for dev deployment with `npm run build`

**Configuration:**
- Frontend: `https://impressionnistes-dev.aviron-rcpm.fr`
- Backend: Dev API
- Cognito redirect: `https://impressionnistes-dev.aviron-rcpm.fr/callback`

**When to use:** Building and deploying to dev environment

---

### 3. `.env.prod` (committed to git)
**Purpose:** Production deployment

**Usage:** Used when building for prod with `npm run build -- --mode production`

**Configuration:**
- Frontend: `https://impressionnistes.aviron-rcpm.fr`
- Backend: Prod API
- Cognito redirect: `https://impressionnistes.aviron-rcpm.fr/callback`

**When to use:** Building and deploying to production

---

## Workflow Examples

### Local Development
```bash
cd frontend
npm run dev
# Uses .env.local automatically
# Runs on localhost:3000
# Connects to dev backend
# Cognito redirects to localhost
```

### Deploy to Dev
```bash
cd frontend
npm run build
# Uses .env.dev (default mode)
# Builds with dev CloudFront URL

cd ../infrastructure
make deploy-dev
# Deploys to dev environment
```

### Deploy to Prod
```bash
cd frontend
npm run build -- --mode production
# Uses .env.prod
# Builds with prod CloudFront URL

cd ../infrastructure
make deploy-prod
# Deploys to production
```

---

## File Priority (Vite)

Vite loads environment files in this order (later overrides earlier):

1. `.env` - Base configuration (if exists)
2. `.env.local` - Local overrides (gitignored)
3. `.env.[mode]` - Mode-specific (e.g., `.env.dev`, `.env.prod`)
4. `.env.[mode].local` - Mode-specific local overrides (gitignored)

---

## Important Notes

✅ **`.env.local` is gitignored** - Your local settings stay local  
✅ **`.env.dev` and `.env.prod` are committed** - Team shares deployment configs  
✅ **No Makefile changes needed** - Existing commands work as-is  
✅ **Automatic mode selection** - Vite picks the right file based on command  

---

## Troubleshooting

### "I'm getting redirected to the wrong environment after login"

**Problem:** Frontend is using wrong Cognito redirect URL

**Solution:** 
1. Check which env file is being used
2. Rebuild with correct mode: `npm run build` (dev) or `npm run build -- --mode production` (prod)
3. Redeploy

### "Local development redirects to CloudFront after login"

**Problem:** `.env.local` doesn't exist or has wrong redirect URL

**Solution:**
1. Verify `.env.local` exists in `frontend/` directory
2. Check `VITE_COGNITO_REDIRECT_URI=http://localhost:3000/callback`
3. Restart dev server: `npm run dev`

### "Changes to .env file not taking effect"

**Problem:** Vite caches environment variables

**Solution:**
1. Stop the dev server (Ctrl+C)
2. Delete `.vite` cache: `rm -rf .vite`
3. Restart: `npm run dev`

---

## Quick Reference

| Scenario | Command | File Used | Redirect URL |
|----------|---------|-----------|--------------|
| Local dev | `npm run dev` | `.env.local` | `localhost:3000/callback` |
| Build dev | `npm run build` | `.env.dev` | `impressionnistes-dev.../callback` |
| Build prod | `npm run build -- --mode production` | `.env.prod` | `impressionnistes.../callback` |
