# Documentation

Welcome to the Course des Impressionnistes Registration System documentation.

## Quick Links

### Getting Started
- [Quick Start Guide](guides/setup/quick-start.md) - Get up and running quickly
- [Frontend Setup](guides/setup/frontend-setup.md) - Set up the Vue.js frontend
- [Deployment Guide](guides/setup/deployment.md) - Deploy to AWS

### Reference
- [API Endpoints](reference/api-endpoints.md) - Complete API documentation
- [Project Structure](reference/project-structure.md) - Codebase organization
- [Consent Schema](reference/consent-schema.md) - GDPR consent storage
- [Terminology](reference/terminology.md) - Standard terminology and pricing definitions

### Design System
- [Design System Setup](design-system-setup.md) - Design tokens implementation guide
- [Design System Showcase Guide](design-system-showcase-guide.md) - Living style guide maintenance
- [Design System Documentation](design-system.md) - Complete design system reference (coming in Task 22)

### Guides
- [GDPR Compliance](guides/GDPR_COMPLIANCE.md) - **NEW** Privacy and consent implementation
- [Email System](guides/EMAIL_SYSTEM_SUMMARY.md) - Email configuration and usage
- [Payment Testing](guides/PAYMENT_TESTING.md) - Test payment flows

## Documentation Structure

```
docs/
├── README.md                    # This file
├── guides/                      # How-to guides and tutorials
│   ├── GDPR_COMPLIANCE.md      # GDPR compliance guide
│   ├── development/            # Development guides
│   ├── operations/             # Operations and maintenance
│   └── setup/                  # Setup and deployment
├── reference/                   # Technical reference
│   ├── api-endpoints.md        # API documentation
│   ├── consent-schema.md       # Consent storage schema
│   ├── terminology.md          # Standard terminology and pricing definitions
│   └── project-structure.md    # Codebase structure
└── archived/                    # Archived documentation
    └── PRICING_TERMINOLOGY_UPDATE_SUMMARY.md  # Pricing terminology update (Jan 2026)
```

## What's New

### GDPR Compliance (January 2026)

The system now includes comprehensive GDPR compliance features:

- **Legal Pages**: Privacy Policy and Terms & Conditions (bilingual)
- **Cookie Consent**: Banner and preferences management
- **Registration Consent**: Explicit consent collection during registration
- **Consent Storage**: Immutable audit trail in DynamoDB

See the [GDPR Compliance Guide](guides/GDPR_COMPLIANCE.md) for complete documentation.

## Key Features

### Authentication & Authorization
- AWS Cognito for user management
- JWT token-based authentication
- Role-based access control (team managers, admins)

### Registration System
- Crew member management
- Boat registration (crew registration in UI)
- Race assignment and eligibility
- Payment processing with Stripe

### GDPR Compliance
- Privacy Policy and Terms & Conditions
- Cookie consent management
- Explicit user consent collection
- Consent audit trail

### Internationalization
- Fully bilingual (French and English)
- Dynamic language switching
- Localized content and dates

## Development

### Prerequisites
- Node.js 18+ (frontend)
- Python 3.11+ (backend)
- AWS CLI configured
- AWS CDK installed

### Local Development

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

**Backend**:
```bash
cd infrastructure
make deploy-dev
```

### Testing

**Frontend Tests**:
```bash
cd frontend
npm test
```

**Backend Tests**:
```bash
cd infrastructure
make test
```

## Deployment

### Development Environment
```bash
cd infrastructure
make deploy-dev
```

### Production Environment
```bash
cd infrastructure
make deploy-prod
```

See [Deployment Guide](guides/setup/deployment.md) for detailed instructions.

## Architecture

### Frontend
- **Framework**: Vue.js 3 with Composition API
- **State Management**: Pinia
- **Routing**: Vue Router
- **UI**: Custom components with responsive design
- **i18n**: vue-i18n for bilingual support

### Backend
- **Compute**: AWS Lambda (Python 3.11)
- **API**: API Gateway with REST API
- **Database**: DynamoDB (single-table design)
- **Authentication**: AWS Cognito
- **Payments**: Stripe
- **Email**: AWS SES

### Infrastructure
- **IaC**: AWS CDK (Python)
- **Hosting**: S3 + CloudFront (frontend)
- **Monitoring**: CloudWatch
- **Secrets**: AWS Secrets Manager

## Common Tasks

### View Database Contents
```bash
cd infrastructure
make db-view
```

### Export Database
```bash
cd infrastructure
make db-export
```

### Create Admin User
```bash
cd infrastructure
make cognito-create-admin EMAIL=admin@example.com
```

### Get API URL
```bash
cd infrastructure
make describe-infra
```

## Troubleshooting

### Frontend Issues
- Check browser console for errors
- Verify API URL in `.env` file
- Clear browser cache and localStorage
- Check network tab for failed requests

### Backend Issues
- Check CloudWatch logs for Lambda errors
- Verify IAM permissions
- Check DynamoDB for data issues
- Verify Cognito configuration

### GDPR Issues
- Cookie banner not appearing: Clear localStorage
- Consent validation failing: Check request payload
- Legal pages not loading: Verify routes and translations

## Support

### Documentation
- Browse guides in `docs/guides/`
- Check reference docs in `docs/reference/`
- Review spec files in `.kiro/specs/`

### Development
- Check CloudWatch logs for errors
- Use `make help` in infrastructure directory
- Review test results for failures

### Legal
- Consult legal counsel for GDPR questions
- Review [GDPR Compliance Guide](guides/GDPR_COMPLIANCE.md)
- Check requirements in `.kiro/specs/gdpr-compliance/`

## Contributing

### Code Style
- Follow existing patterns in codebase
- Use ESLint for JavaScript/Vue
- Use Black for Python
- Write tests for new features

### Documentation
- Update relevant docs when making changes
- Keep examples up to date
- Add new guides for significant features
- Update this README when adding new docs

### Testing
- Write unit tests for components
- Write integration tests for APIs
- Test in both languages (French and English)
- Test on mobile devices

## Resources

### External Documentation
- [Vue.js 3](https://vuejs.org/)
- [AWS CDK](https://docs.aws.amazon.com/cdk/)
- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [DynamoDB](https://docs.aws.amazon.com/dynamodb/)
- [Stripe](https://stripe.com/docs)
- [GDPR](https://gdpr-info.eu/)

### Internal Specs
- [Main Requirements](.kiro/specs/impressionnistes-registration-system/requirements.md)
- [GDPR Requirements](.kiro/specs/gdpr-compliance/requirements.md)
- [Design Documents](.kiro/specs/)

## License

[Add license information]

## Contact

[Add contact information]

---

**Last Updated**: January 2, 2026

**Documentation Version**: 2.0 (Added GDPR compliance)
