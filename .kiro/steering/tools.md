# Development Tools and Commands

## Infrastructure Management

All infrastructure and database tools are located in `infrastructure/Makefile`.

### Common Commands

**Deployment:**
```bash
cd infrastructure
make deploy-dev          # Deploy to dev environment
make deploy-prod         # Deploy to production (with confirmation)
make describe-infra      # Show API URLs and Cognito config
```

**Database:**
```bash
cd infrastructure
make db-view             # View database contents
make db-export           # Export database to CSV
make db-migrate          # Run database migrations (when needed)
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

## Database Migrations

Database migrations are one-time scripts for data updates. They are located in `functions/migrations/`.

### When Needed

Migrations are only created when you need to:
- Update existing data to match new schema
- Backfill calculated fields
- Fix data inconsistencies

### Running Migrations

```bash
cd infrastructure
make db-migrate MIGRATION=migration_name TEAM_MANAGER_ID=your-user-id
```

### Creating New Migrations

See `functions/migrations/README.md` for:
- Migration template
- Best practices
- Troubleshooting guide

**Note:** Delete migrations after running them in all environments (dev/prod).

## Frontend Development

```bash
cd frontend
npm run dev              # Start dev server
npm run build            # Build for production
npm run lint             # Lint code
```

## Backend Testing

```bash
cd functions/shared
python test_race_eligibility_gender.py    # Test race eligibility logic
```

## Important Notes

- Always use the Makefile commands instead of running CDK directly
- The Makefile handles virtual environment activation automatically
- Test on dev environment before deploying to production
- Use `make describe-infra` to get configuration for frontend .env file
