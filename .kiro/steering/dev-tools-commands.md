# Development Tools and Commands

## Infrastructure Management

All infrastructure and database tools are located in `infrastructure/Makefile`.

### Common Commands

**Deployment:**
```bash
cd infrastructure
make deploy-dev          # Deploy backend to dev environment
make deploy-prod         # Deploy backend to production (with confirmation)
make deploy-frontend-dev # Deploy frontend to dev environment
make deploy-frontend-prod # Deploy frontend to production
make describe-infra      # Show API URLs and Cognito config
```

**Database:**
```bash
cd infrastructure
make db-view             # View database contents
make db-export           # Export database to CSV
make db-migrate MIGRATION=script_name ENV=dev  # Run database migration
```

**Cognito User Management:**
```bash
cd infrastructure
make cognito-list-users                                    # List all users
make cognito-create-admin EMAIL=admin@example.com          # Create admin user
make cognito-add-to-group EMAIL=user@example.com GROUP=admins  # Add to group
```

**Monitoring:**
```bash
cd infrastructure
make costs               # Show AWS costs
make list                # List all stacks
```

### Full Command Reference

Run `make help` in the infrastructure directory to see all available commands:
```bash
cd infrastructure
make help
```

## Script Organization

All operational scripts are now organized in `/scripts/`:

```
scripts/
├── deployment/     # Infrastructure deployment (deploy.sh, destroy.sh, etc.)
├── database/       # Database operations and migrations
├── testing/        # Testing utilities
└── external/       # External tools (license checker)
```

**See:** `scripts/README.md` for detailed documentation.

## Database Migrations

Database migrations are one-time scripts for data updates. They are located in `scripts/database/`.

### When Needed

Migrations are only created when you need to:
- Update existing data to match new schema
- Backfill calculated fields
- Fix data inconsistencies

### Running Migrations

```bash
cd infrastructure
make db-migrate MIGRATION=migration_name ENV=dev
```

### Creating New Migrations

See `scripts/database/MIGRATIONS.md` for:
- Migration template
- Best practices
- Troubleshooting guide

**Note:** Delete migrations after running them in all environments (dev/prod).

## Frontend Development

**Local Development:**
```bash
cd frontend
npm run dev              # Start dev server
npm run build            # Build for production
npm run lint             # Lint code
```

**Frontend Deployment:**
All frontend deployment commands are also available in the infrastructure Makefile:
```bash
cd infrastructure
make deploy-frontend-dev  # Deploy frontend to dev environment
make deploy-frontend-prod # Deploy frontend to production
```

## Backend Testing

```bash
cd infrastructure
make test                # Run all tests
make test-backend        # Run backend integration tests
make test-coverage       # Run tests with coverage report
```

## Important Notes

- Always use the Makefile commands instead of running scripts directly
- The Makefile handles virtual environment activation automatically
- Test on dev environment before deploying to production
- Use `make describe-infra` to get configuration for frontend .env file
- All scripts are now organized in `/scripts/` directory with clear categorization

