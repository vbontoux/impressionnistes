# Setup Guide - Course des Impressionnistes Registration System

This guide will help you set up the development environment with proper Python virtual environments.

## Prerequisites

- **Python 3.11+** - Check with `python3 --version`
- **Node.js 18+** - Check with `node --version`
- **AWS CLI** - Check with `aws --version`
- **AWS CDK CLI** - Install with `npm install -g aws-cdk`
- **Git** - Check with `git --version`

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd impressionnistes-registration-system
```

### 2. Set Up Python Virtual Environments

**Option A: Automated Setup (Recommended)**

```bash
# macOS/Linux
./setup-venv.sh

# Windows PowerShell
.\setup-venv.ps1
```

**Option B: Manual Setup**

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Infrastructure
cd ../infrastructure
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

**Option C: Using Make (macOS/Linux)**

```bash
# Backend
cd backend
make setup

# Infrastructure
cd ../infrastructure
make setup
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4. Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: eu-west-3
# Default output format: json
```

## Working with Virtual Environments

### Activating Virtual Environments

**Backend:**
```bash
cd backend
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

**Infrastructure:**
```bash
cd infrastructure
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Deactivating

```bash
deactivate
```

### Checking Active Environment

```bash
which python  # macOS/Linux - should show path to venv
where python  # Windows - should show path to venv
```

## Development Workflow

### Backend Development

```bash
cd backend
source venv/bin/activate

# Run tests
pytest

# Run tests with coverage
pytest --cov

# When done
deactivate
```

**Or using Make:**
```bash
cd backend
make test
make test-cov
```

### Infrastructure Development

```bash
cd infrastructure
source venv/bin/activate

# Synthesize templates
cdk synth --context env=dev

# Show differences
cdk diff --context env=dev

# Deploy
cdk deploy --all --context env=dev

# When done
deactivate
```

**Or using Make:**
```bash
cd infrastructure
make synth
make diff
make deploy-dev
```

**Or using deployment scripts:**
```bash
cd infrastructure
./deploy.sh dev
```

### Frontend Development

```bash
cd frontend
npm run dev     # Start dev server
npm run build   # Build for production
npm run lint    # Lint code
```

## IDE Configuration

### VS Code

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "backend"
  ]
}
```

### PyCharm

1. Open Project Settings
2. Go to Project > Python Interpreter
3. Click gear icon > Add
4. Select "Existing environment"
5. Choose `backend/venv/bin/python` or `infrastructure/venv/bin/python`

## Troubleshooting

### Virtual Environment Not Found

```bash
# Recreate virtual environment
cd backend  # or infrastructure
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Permission Denied on Scripts

```bash
# Make scripts executable (macOS/Linux)
chmod +x setup-venv.sh
chmod +x infrastructure/deploy.sh
chmod +x infrastructure/destroy.sh
```

### Python Version Issues

```bash
# Check Python version
python3 --version

# If using pyenv
pyenv install 3.11
pyenv local 3.11

# Recreate venv with correct version
python3.11 -m venv venv
```

### AWS Credentials Not Configured

```bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=eu-west-3
```

### CDK Bootstrap Issues

```bash
# Bootstrap with explicit account/region
cdk bootstrap aws://ACCOUNT-ID/eu-west-3
```

### Package Installation Fails

```bash
# Upgrade pip first
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Clear pip cache
pip cache purge
```

## Best Practices

### Always Use Virtual Environments

✅ **DO:**
```bash
cd backend
source venv/bin/activate
pip install package-name
```

❌ **DON'T:**
```bash
cd backend
pip install package-name  # Installs globally!
```

### Keep Dependencies Updated

```bash
# Update requirements.txt after installing new packages
pip freeze > requirements.txt

# Or manually add with version
echo "package-name==1.2.3" >> requirements.txt
```

### Separate Environments

- Backend and infrastructure have **separate** virtual environments
- This prevents dependency conflicts
- Each can have different package versions if needed

### Use Scripts and Makefiles

- Deployment scripts handle virtual environment activation automatically
- Makefiles provide convenient shortcuts
- Reduces chance of forgetting to activate venv

## Environment Variables

### Backend

Create `backend/.env` (not committed to git):
```
AWS_REGION=eu-west-3
TABLE_NAME=impressionnistes-registration-dev
```

### Frontend

Create `frontend/.env.local` (not committed to git):
```
VITE_API_URL=https://your-api-gateway-url
VITE_STRIPE_PUBLIC_KEY=pk_test_...
```

### Infrastructure

Environment variables are managed through CDK context in `cdk.json`.

## Next Steps

1. ✅ Set up virtual environments
2. ✅ Install dependencies
3. ✅ Configure AWS credentials
4. 📝 Deploy infrastructure (see [infrastructure/README.md](infrastructure/README.md))
5. 📝 Run frontend locally (see main [README.md](README.md))
6. 📝 Start implementing features (see [tasks.md](.kiro/specs/impressionnistes-registration-system/tasks.md))

## Getting Help

- Check [README.md](README.md) for project overview
- Check [infrastructure/README.md](infrastructure/README.md) for deployment details
- Check [infrastructure/COMMANDS.md](infrastructure/COMMANDS.md) for CDK commands
- Review [.kiro/specs/](. kiro/specs/) for requirements and design

## Clean Slate

If you need to start fresh:

```bash
# Remove all virtual environments
rm -rf backend/venv
rm -rf infrastructure/venv

# Remove all caches
rm -rf backend/__pycache__
rm -rf infrastructure/cdk.out
rm -rf frontend/node_modules
rm -rf frontend/dist

# Start over
./setup-venv.sh
cd frontend && npm install
```
