# Course des Impressionnistes Registration System

A serverless web application for managing rowing competition registrations, built on AWS with Vue.js frontend and Python backend.

## 🚀 Quick Start

New to the project? Start here:

1. **[Quick Start Guide](docs/guides/setup/quick-start.md)** - Get up and running in minutes
2. **[Setup Guide](docs/guides/setup/setup.md)** - Detailed setup instructions
3. **[Deployment Guide](docs/guides/setup/deployment.md)** - Deploy to AWS

## 📖 Overview

The Course des Impressionnistes Registration System enables rowing club managers to register crews and boats for the RCPM Competition.

### Key Features

**For Club Managers:**
- Register and manage crew members
- Create boat registrations with seat assignments
- Request boat rentals from RCPM
- Process payments securely via Stripe
- Receive notifications about registration status

**For Administrators:**
- Validate and manage all registrations
- Configure system parameters (dates, pricing, races)
- Flag issues and grant editing exceptions
- Export data for competition management (CSV, Excel/CrewTimer)
- View real-time dashboard statistics

**Technical Highlights:**
- Serverless architecture with auto-scaling
- Single-table DynamoDB design for efficiency
- Multilingual support (French/English)
- Custom domains with SSL certificates
- **GDPR compliant with Privacy Policy, Terms & Conditions, and Cookie Consent**
- Comprehensive monitoring and logging

## 🏗️ Architecture

- **Frontend**: Vue.js 3 with Vite, served via S3/CloudFront
- **Backend**: Python Lambda functions
- **Database**: Amazon DynamoDB (single-table design)
- **API**: AWS API Gateway (REST)
- **Authentication**: Amazon Cognito
- **Payments**: Stripe integration
- **Infrastructure**: AWS CDK (Python)
- **Monitoring**: CloudWatch logs and alarms

**[→ Detailed Project Structure](docs/reference/project-structure.md)**

## 📚 Documentation

### Setup & Deployment

- **[Quick Start](docs/guides/setup/quick-start.md)** - Get started quickly
- **[Setup Guide](docs/guides/setup/setup.md)** - Complete setup instructions
- **[Deployment Guide](docs/guides/setup/deployment.md)** - Deploy to AWS environments
- **[Custom Domains](docs/guides/setup/custom-domains.md)** - Configure custom domains and SSL
- **[Stripe Setup](docs/guides/setup/stripe-setup.md)** - Configure payment processing
- **[Secrets Management](docs/guides/setup/secrets-management.md)** - Manage sensitive configuration

### Development

- **[Development Workflow](docs/guides/development/dev-workflow.md)** - Day-to-day development process
- **[Testing Guide](docs/guides/development/testing-guide.md)** - Testing strategy and practices
- **[Lambda Testing](docs/guides/development/lambda-testing.md)** - Test Lambda functions locally
- **[Frontend Testing](docs/guides/development/frontend-testing.md)** - Frontend testing guide
- **[Frontend Setup](docs/guides/development/frontend-setup.md)** - Frontend development setup
- **[Mobile Responsiveness Guide](docs/guides/development/mobile-responsiveness-guide.md)** - Complete mobile responsiveness patterns and best practices
- **[Mobile Testing Checklist](docs/guides/development/mobile-testing-checklist.md)** - Checklist for testing mobile responsiveness
- **[Responsive Design](docs/guides/development/responsive-design.md)** - Mobile-first responsive design guide
- **[Responsive Table Patterns](docs/guides/development/responsive-table-patterns.md)** - Table responsiveness strategies

### Operations

- **[Infrastructure Quickstart](docs/guides/operations/infrastructure-quickstart.md)** - Quick infrastructure commands
- **[Database Export](docs/guides/operations/database-export.md)** - Export and backup database
- **[Monitoring](docs/guides/operations/monitoring.md)** - Monitor system health
- **[DNS Records](docs/guides/operations/dns-records.md)** - DNS configuration reference

### Reference

- **[API Endpoints](docs/reference/api-endpoints.md)** - Complete API reference
- **[Auth API](docs/reference/auth-api.md)** - Authentication endpoints
- **[Consent Schema](docs/reference/consent-schema.md)** - GDPR consent storage schema
- **[Commands](docs/reference/commands.md)** - CLI commands reference
- **[Project Structure](docs/reference/project-structure.md)** - Codebase organization

### Compliance & Legal

- **[GDPR Compliance Guide](docs/guides/GDPR_COMPLIANCE.md)** - Privacy Policy, Terms & Conditions, Cookie Consent implementation

### Component-Specific Docs

- **[Frontend Environment Files](frontend/ENV_FILES_GUIDE.md)** - Frontend .env configuration
- **[Payment Testing](frontend/PAYMENT_TESTING.md)** - Test Stripe integration
- **[Infrastructure README](infrastructure/README.md)** - Infrastructure module overview
- **[Auth Test Events](functions/auth/TEST_EVENTS.md)** - Lambda test payloads
- **[Migrations Guide](functions/migrations/README.md)** - Database migration instructions
- **[Tests README](tests/README.md)** - Test suite documentation

## 🛠️ Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- AWS CLI configured with credentials
- AWS CDK CLI (`npm install -g aws-cdk`)
- Stripe account (test mode for development)

## ⚡ Getting Started

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd impressionnistes

# Set up Python virtual environments (automated)
./setup-venv.sh  # macOS/Linux
# or
.\setup-venv.ps1  # Windows PowerShell

# Install frontend dependencies
cd frontend
npm install
```

### 2. Configure Environment

See **[Setup Guide](docs/guides/setup/setup.md)** for detailed configuration instructions.

### 3. Deploy Infrastructure

```bash
cd infrastructure
make deploy-dev
```

See **[Deployment Guide](docs/guides/setup/deployment.md)** for complete deployment instructions.

### 4. Run Frontend Locally

```bash
cd frontend
npm run dev
```

## 🔧 Common Commands

### Infrastructure (use Makefile)

```bash
cd infrastructure

# Deployment
make deploy-dev          # Deploy to dev environment
make deploy-prod         # Deploy to production
make describe-infra      # Show API URLs and config

# Database
make db-view             # View database contents
make db-export           # Export database to CSV
make db-migrate          # Run database migrations

# Testing
make test                # Run integration tests
make test-coverage       # Run tests with coverage

# Monitoring
make costs               # Show AWS costs
make list                # List all stacks
```

**[→ Full Commands Reference](docs/reference/commands.md)**

### Frontend Development

```bash
cd frontend
npm run dev              # Start dev server
npm run build            # Build for production
npm run lint             # Lint code
```

### Backend Testing

```bash
cd infrastructure
make test                # Run all integration tests
make test ARGS="tests/integration/test_crew_member_api.py"  # Run specific test
```

## 🌐 Environments

### Development
- **Domain**: `impressionnistes-dev.aviron-rcpm.fr`
- **Purpose**: Testing and development

### Production
- **Domain**: `impressionnistes.aviron-rcpm.fr`
- **Purpose**: Live competition registration

**[→ Custom Domains Setup](docs/guides/setup/custom-domains.md)**

## 🔐 Security

- All data encrypted at rest (DynamoDB)
- HTTPS/TLS for all communications
- Cognito authentication with MFA support
- Role-based access control (Club Managers, Admins)
- Input sanitization and validation
- **GDPR compliance with explicit user consent, Privacy Policy, and Terms & Conditions**
- **Cookie consent management with user preferences**
- **Immutable consent audit trail in DynamoDB**

**[→ GDPR Compliance Guide](docs/guides/GDPR_COMPLIANCE.md)**

## 📊 Monitoring

- **CloudWatch Logs**: All Lambda function logs
- **CloudWatch Alarms**: Error rates, throttling
- **Slack Notifications**: Real-time alerts for admins and DevOps
- **Email Notifications**: User notifications via SES

**[→ Monitoring Guide](docs/guides/operations/monitoring.md)**

## 🤝 Contributing

### Development Workflow

1. Create a feature branch
2. Make changes following the coding standards
3. Run tests: `cd infrastructure && make test`
4. Deploy to dev: `make deploy-dev`
5. Test your changes
6. Create a pull request

**[→ Development Workflow Guide](docs/guides/development/dev-workflow.md)**

### Testing

- **Integration Tests**: 24 tests covering all API endpoints
- **Frontend Tests**: Component and E2E tests
- **Lambda Tests**: Local testing with moto

**[→ Testing Guide](docs/guides/development/testing-guide.md)**

## 📞 Support

For questions or issues, contact the RCPM organization:
- **Email**: contact@impressionnistes.rcpm.fr
- **Website**: [Course des Impressionnistes](https://impressionnistes.aviron-rcpm.fr)

## 📄 License

Copyright © 2025 RCPM - Rowing Club de Port Marly

---

## 📁 Documentation Structure

```
docs/
├── guides/
│   ├── setup/              # Setup and deployment guides
│   ├── development/        # Development guides
│   └── operations/         # Operations and maintenance
├── reference/              # Technical reference documentation
└── archived/               # Historical documentation

Component-specific docs stay with their components:
├── frontend/               # Frontend-specific guides
├── infrastructure/         # Infrastructure-specific guides
├── functions/              # Lambda function documentation
└── tests/                  # Test documentation
```

**[→ Complete Documentation Index](docs/)**
