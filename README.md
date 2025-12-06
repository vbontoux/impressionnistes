# Course des Impressionnistes Registration System

A serverless web application for managing rowing competition registrations, built on AWS with Vue.js frontend and Python backend.

## Overview

The Course des Impressionnistes Registration System enables rowing club team managers to register crews and boats for the RCPM Competition. The system provides:

- **Team Manager Portal**: Register crews, manage boat entries, process payments
- **Admin Dashboard**: Validate registrations, manage configuration, export reports
- **Multilingual Support**: French and English interfaces
- **Payment Processing**: Secure payments via Stripe
- **Notification System**: Email and Slack notifications
- **Boat Rental Management**: RCPM boat rental with priority system

## Architecture

- **Frontend**: Vue.js 3 with Vite, served via S3/CloudFront
- **Backend**: Python Lambda functions
- **Database**: Amazon DynamoDB (single-table design)
- **API**: AWS API Gateway (REST)
- **Authentication**: Amazon Cognito
- **Payments**: Stripe integration
- **Infrastructure**: AWS CDK (Python)
- **Monitoring**: CloudWatch logs and alarms

## Project Structure

```
.
├── frontend/              # Vue.js 3 frontend application
│   ├── src/
│   │   ├── components/   # Vue components
│   │   ├── views/        # Page views
│   │   ├── stores/       # Pinia state management
│   │   ├── services/     # API services
│   │   └── locales/      # i18n translations
│   └── package.json
│
├── backend/              # Python backend
│   ├── functions/        # Lambda function handlers
│   │   ├── auth/
│   │   ├── crew/
│   │   ├── boat/
│   │   ├── payment/
│   │   ├── admin/
│   │   └── notifications/
│   ├── shared/           # Shared utilities
│   │   ├── database.py
│   │   ├── configuration.py
│   │   ├── validation.py
│   │   └── notifications.py
│   └── requirements.txt
│
└── infrastructure/       # AWS CDK infrastructure
    ├── stacks/
    │   ├── database_stack.py
    │   ├── api_stack.py
    │   ├── frontend_stack.py
    │   └── monitoring_stack.py
    ├── app.py
    └── requirements.txt
```

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- AWS CLI configured with credentials
- AWS CDK CLI (`npm install -g aws-cdk`)
- Stripe account (test mode for development)

**📖 For detailed setup instructions, see [SETUP.md](SETUP.md)**

**🚀 For deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**

## Getting Started

### 1. Set Up Python Virtual Environments

**Automated setup (recommended):**
```bash
# macOS/Linux
./setup-venv.sh

# Windows PowerShell
.\setup-venv.ps1
```

**Manual setup:**
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
deactivate

# Infrastructure
cd infrastructure
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
deactivate
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Configure Environment

Create `.env` files for local development:

**Frontend (.env.local):**
```
VITE_API_URL=https://your-api-gateway-url
VITE_STRIPE_PUBLIC_KEY=pk_test_...
```

**Backend:**
Environment variables are managed through CDK deployment.

### 4. Deploy Infrastructure

```bash
cd infrastructure
source venv/bin/activate  # Activate virtual environment
cdk bootstrap --context env=dev  # First time only
cdk deploy --all --context env=dev

# Or use the deployment script (handles venv automatically)
./deploy.sh dev
```

See [infrastructure/README.md](infrastructure/README.md) for detailed deployment instructions.

### 5. Run Frontend Locally

```bash
cd frontend
npm run dev
```

## Development

### Frontend Development
```bash
cd frontend
npm run dev          # Start dev server
npm run build        # Build for production
npm run lint         # Lint code
```

### Backend Testing
```bash
cd backend
source venv/bin/activate  # Activate virtual environment
pytest               # Run tests
pytest --cov         # Run with coverage
deactivate           # Deactivate when done
```

### Infrastructure Deployment
```bash
cd infrastructure
source venv/bin/activate  # Activate virtual environment
cdk diff --context env=dev             # Preview changes
cdk deploy --all --context env=dev     # Deploy to AWS
cdk destroy --all --context env=dev    # Remove all resources
deactivate           # Deactivate when done

# Or use deployment scripts (handle venv automatically)
./deploy.sh dev
./destroy.sh dev
```

## Key Features

### For Team Managers
- Register and manage crew members
- Create boat registrations with seat assignments
- Request boat rentals from RCPM
- Process payments securely via Stripe
- Receive notifications about registration status

### For Administrators
- Validate and manage all registrations
- Configure system parameters (dates, pricing, races)
- Flag issues and grant editing exceptions
- Export data for competition management
- View real-time dashboard statistics

### Technical Features
- Serverless architecture with auto-scaling
- Single-table DynamoDB design for efficiency
- Multilingual support (French/English)
- GDPR compliant data handling
- Comprehensive monitoring and logging
- Automated backup and recovery

## Configuration

System configuration is managed through DynamoDB and can be updated via the admin interface:

- Registration and payment periods
- Pricing (base seat price, rental fees)
- Notification settings
- Race categories
- Boat inventory

## Monitoring

- **CloudWatch Logs**: All Lambda function logs
- **CloudWatch Alarms**: Error rates, throttling
- **Slack Notifications**: Real-time alerts for admins and DevOps
- **Email Notifications**: User notifications via SES

## Security

- All data encrypted at rest (DynamoDB)
- HTTPS/TLS for all communications
- Cognito authentication with MFA support
- Role-based access control
- Input sanitization and validation
- GDPR compliance features

## Support

For questions or issues, contact the RCPM organization:
- Email: contact@impressionnistes.rcpm.fr
- Website: [Course des Impressionnistes](https://impressionnistes.rcpm.fr)

## License

Copyright © 2025 RCPM - Rowing Club de Port Marly
