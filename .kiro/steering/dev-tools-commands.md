# Development Tools and Commands

## 🚨 MANDATORY: Everything Goes Through the Makefile

Every test, build, deployment, database operation, script, and utility MUST be
run via the `infrastructure/Makefile`. This is not optional.

**The agent MUST NOT run any of the following directly:**
- `npm` / `npx` / `yarn` / `pnpm` (build, test, lint, dev server, install)
- `pytest` / `python` on test files or scripts
- `cdk` (synth, deploy, diff, destroy)
- Any shell script in `/scripts/` (`.sh` or `.py`)
- Any ad-hoc build/test/deploy command

**Instead, always use the corresponding `make` target** (run `make help` in
`infrastructure/` to discover them). If the operation you need has no Makefile
target, STOP and propose adding one to the Makefile — never bypass it with a raw
command.

The user runs `make` commands themselves whenever they choose. When a change
requires a build/test/deploy, the agent's job is to tell the user which `make`
command to run, not to run bypassing commands.

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

## Frontend

All frontend build, test, and deploy operations MUST go through the Makefile:

```bash
cd infrastructure
make build-frontend ENV=dev    # Build the frontend
make test-frontend             # Run frontend formatter/unit tests
make lint-frontend             # Lint frontend code (ESLint, auto-fix)
make deploy-frontend-dev       # Build + deploy frontend to dev
make deploy-frontend-prod      # Build + deploy frontend to production
```

**The local dev server (`npm run dev`) is a long-running process that YOU run
manually in your own terminal.** The agent must never start it.

The agent must never run `npm`, `npx`, `pytest`, `cdk`, or any project script
directly. If a needed operation has no Makefile target yet, the agent must
propose adding a Makefile target rather than bypassing it with a raw command.

## Backend Testing

```bash
cd infrastructure
make test                # Run all tests
make test-backend        # Run backend integration tests
make test-coverage       # Run tests with coverage report
```

## Important Notes

- ALWAYS use the Makefile commands. Never run `npm`, `pytest`, `cdk`, or scripts directly (see the mandatory rule at the top of this file).
- The Makefile handles virtual environment activation automatically
- Test on dev environment before deploying to production
- Use `make describe-infra` to get configuration for frontend .env file
- All scripts are organized in the `/scripts/` directory with clear categorization
- If you need an operation with no Makefile target, propose adding the target instead of bypassing the Makefile

