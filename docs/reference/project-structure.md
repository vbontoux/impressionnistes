# Project Structure

## Overview

The Impressionnistes Registration System is organized into clear, logical directories with separation of concerns.

## Directory Structure

```
impressionnistes/
├── .github/              # GitHub Actions workflows
├── .kiro/                # Kiro IDE configuration and steering rules
├── docs/                 # Documentation
├── frontend/             # Vue.js frontend application
├── functions/            # AWS Lambda functions
├── infrastructure/       # AWS CDK infrastructure code
├── scripts/              # Operational scripts
├── tests/                # Integration and unit tests
└── raw-files/            # Reference files and requirements
```

## Detailed Structure

### Frontend (`frontend/`)

Vue.js single-page application.

```
frontend/
├── public/               # Static assets
├── src/
│   ├── assets/          # Images, styles, design tokens
│   ├── components/      # Reusable Vue components
│   ├── composables/     # Vue composition functions
│   ├── locales/         # i18n translations (fr, en)
│   ├── router/          # Vue Router configuration
│   ├── services/        # API service layer
│   ├── stores/          # Pinia state management
│   ├── styles/          # Global styles
│   ├── utils/           # Utility functions
│   ├── views/           # Page components
│   ├── App.vue          # Root component
│   └── main.js          # Application entry point
├── .env                 # Environment variables (local dev)
├── .env.production      # Production environment variables
├── index.html           # HTML template
├── package.json         # Dependencies
└── vite.config.js       # Vite configuration
```

### Backend Functions (`functions/`)

AWS Lambda functions organized by domain.

```
functions/
├── admin/               # Admin-only operations
├── auth/                # Authentication (register, login, profile)
├── boat/                # Boat registration management
├── club/                # Club data
├── crew/                # Crew member management
├── health/              # Health checks and public info
├── init/                # Database initialization
├── layer/               # Lambda layer (shared dependencies)
│   └── python/          # Python packages for all Lambdas
├── payment/             # Payment processing (Stripe)
├── race/                # Race definitions
└── shared/              # Shared utilities
    ├── access_control.py
    ├── auth_utils.py
    ├── database.py
    ├── email_utils.py
    ├── payment_*.py
    ├── pricing.py
    ├── race_eligibility.py
    ├── responses.py
    ├── secrets_manager.py
    ├── slack_utils.py
    ├── stripe_client.py
    └── validation.py
```

### Infrastructure (`infrastructure/`)

AWS CDK infrastructure as code.

```
infrastructure/
├── stacks/              # CDK stack definitions
│   ├── api_stack.py    # API Gateway + Lambda functions
│   ├── auth_stack.py   # Cognito user pools
│   ├── database_stack.py # DynamoDB tables
│   ├── frontend_stack.py # S3 + CloudFront
│   ├── monitoring_stack.py # CloudWatch alarms
│   └── secrets_stack.py # Secrets Manager
├── exports/             # Database exports (gitignored)
├── app.py               # CDK app entry point
├── config.py            # Environment configuration
├── Makefile             # Operational commands
└── requirements.txt     # Python dependencies
```

### Scripts (`scripts/`)

Operational scripts organized by purpose.

```
scripts/
├── deployment/          # Infrastructure deployment
│   ├── deploy.sh
│   ├── destroy.sh
│   ├── clean-all-aws.sh
│   ├── create-certificates.sh
│   └── clear-cloudfront-cache.sh
├── database/            # Database operations & migrations
│   ├── export-db.py
│   ├── compare_config_details.py
│   ├── delete_team_manager.py
│   ├── reinit_config.py
│   ├── add_*.py        # Migration scripts
│   ├── update_*.py     # Migration scripts
│   └── README.md
├── testing/             # Testing utilities
│   └── verify-receipt-email.sh
└── external/            # External tools
    └── license_checker.py
```

**See:** `scripts/README.md` for detailed script documentation.

### Tests (`tests/`)

Integration and unit tests.

```
tests/
├── integration/         # API integration tests
│   ├── test_admin_api.py
│   ├── test_auth_api.py
│   ├── test_boat_registration_api.py
│   ├── test_crew_member_api.py
│   ├── test_payment_*.py
│   └── ...
├── unit/                # Unit tests
│   ├── test_access_control_*.py
│   ├── test_payment_*.py
│   └── ...
├── conftest.py          # Pytest configuration
└── requirements.txt     # Test dependencies
```

### Documentation (`docs/`)

Project documentation.

```
docs/
├── guides/              # How-to guides
│   ├── admin/          # Admin guides
│   ├── development/    # Development guides
│   ├── operations/     # Operational guides (troubleshooting, etc.)
│   └── setup/          # Setup guides
├── reference/           # Technical reference
│   ├── api-endpoints.md
│   ├── auth.md
│   ├── commands.md
│   ├── project-structure.md (this file)
│   └── terminology.md
├── archived/            # Historical documentation
├── design-system.md     # UI/UX design system
└── README.md            # Documentation index
```

## Key Principles

### Separation of Concerns

- **Frontend:** User interface and client-side logic
- **Functions:** Business logic and API endpoints
- **Infrastructure:** AWS resource definitions
- **Scripts:** Operational utilities
- **Tests:** Quality assurance

### Shared Code

**Backend:**
- `functions/shared/` - Utilities used across Lambda functions
- `functions/layer/python/` - Dependencies for all Lambdas

**Frontend:**
- `frontend/src/utils/` - Pure utility functions
- `frontend/src/composables/` - Vue composition functions with state
- `frontend/src/services/` - API service layer

### Configuration

**Environment-specific:**
- `infrastructure/config.py` - Infrastructure configuration (dev/prod)
- `frontend/.env` - Frontend environment variables (local)
- `frontend/.env.production` - Frontend production variables

**Secrets:**
- `infrastructure/secrets.{env}.json` - Secrets (gitignored)
- AWS Secrets Manager - Runtime secrets

## File Naming Conventions

### Python Files

- **Lambda handlers:** `verb_noun.py` (e.g., `create_boat_registration.py`)
- **Utilities:** `noun_utils.py` (e.g., `email_utils.py`)
- **Tests:** `test_noun.py` (e.g., `test_pricing.py`)
- **Migrations:** `verb_noun.py` (e.g., `add_permission_matrix.py`)

### Vue Files

- **Components:** `PascalCase.vue` (e.g., `BaseButton.vue`)
- **Views:** `PascalCase.vue` (e.g., `BoatRegistrationView.vue`)
- **Composables:** `camelCase.js` (e.g., `useAuth.js`)
- **Utils:** `camelCase.js` (e.g., `formatters.js`)

### Shell Scripts

- **Lowercase with hyphens:** `deploy.sh`, `clean-all-aws.sh`

## Important Locations

### Configuration Files

- `infrastructure/config.py` - Infrastructure config
- `frontend/vite.config.js` - Frontend build config
- `infrastructure/Makefile` - Operational commands
- `.kiro/steering/*.md` - Development guidelines

### Entry Points

- `frontend/src/main.js` - Frontend application
- `infrastructure/app.py` - CDK infrastructure
- `functions/*/handler.py` - Lambda function handlers

### Documentation

- `docs/README.md` - Documentation index
- `scripts/README.md` - Script documentation
- `tests/README.md` - Testing guide

## Related Documentation

- Script organization: `scripts/README.md`
- API endpoints: `docs/reference/api-endpoints.md`
- Development setup: `docs/guides/setup/`
- Deployment guide: `docs/guides/operations/`
