# Scripts Directory

This directory contains all operational scripts for the Impressionnistes Registration System.

## Directory Structure

```
scripts/
├── deployment/     # Infrastructure deployment and AWS management
├── database/       # Database operations, utilities, and migrations
├── testing/        # Testing and verification utilities
└── external/       # External tools (license checker, etc.)
```

## Quick Reference

### Deployment Scripts
Located in `deployment/`
- `deploy.sh` - Deploy infrastructure to AWS
- `destroy.sh` - Destroy infrastructure stacks
- `clean-all-aws.sh` - Complete AWS cleanup
- `create-certificates.sh` - Create SSL certificates for CloudFront
- `clear-cloudfront-cache.sh` - Invalidate CloudFront cache

**Usage:** See `deployment/README.md`

### Database Scripts
Located in `database/`
- **Utilities:** Export, compare, list, delete operations
- **Migrations:** One-time database updates (add_*, update_*, migrate_*)

**Usage:** See `database/README.md` and `database/MIGRATIONS.md`

### Testing Scripts
Located in `testing/`
- `verify-receipt-email.sh` - Verify Stripe receipt email configuration

**Usage:** See `testing/README.md`

### External Tools
Located in `external/`
- `license_checker.py` - French Rowing Federation license validation

**Usage:** See `external/README.md`

## Running Scripts

Most scripts are designed to be run via the Makefile in `infrastructure/`:

```bash
cd infrastructure

# Deployment
make deploy-dev
make deploy-prod
make destroy-dev

# Database operations
make db-export
make db-view
make db-migrate MIGRATION=script_name

# Testing
make test-email EMAIL=your@email.com
```

For direct script execution, see individual README files in each subdirectory.

## Important Notes

- **Always run from project root or infrastructure directory**
- **Use Makefile commands when available** (handles environment setup)
- **Test on dev before prod** for any destructive operations
- **Migrations are one-time scripts** - delete after running on all environments

## Getting Help

- Deployment issues: See `deployment/README.md`
- Database operations: See `database/README.md`
- Migration help: See `database/MIGRATIONS.md`
- Makefile commands: Run `make help` in `infrastructure/`
