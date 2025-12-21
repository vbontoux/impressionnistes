# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### 1. Setup (One Time)

```bash
# Clone and enter directory
git clone <repo-url>
cd impressionnistes

# Setup Python virtual environments
./setup-venv.sh  # macOS/Linux
# or
.\setup-venv.ps1  # Windows

# Install frontend dependencies
cd frontend && npm install && cd ..

# Configure AWS
aws configure
```

### 2. Deploy Infrastructure

```bash
cd infrastructure
make deploy-dev
```

### 3. Run Frontend

```bash
cd frontend
npm run dev
```

## 📋 Daily Development Commands

### Backend Testing
```bash
cd infrastructure
make test              # Run all tests
make test-backend      # Backend tests only
make test-coverage     # With coverage report
```

### Infrastructure Changes
```bash
cd infrastructure
make diff              # See what will change
make deploy-dev        # Deploy changes
make describe-infra    # Show API URLs and config
```

### Frontend Development
```bash
cd frontend
npm run dev            # Start dev server
npm run build          # Build for production
```

## 🔧 Common Tasks

### Database Operations
```bash
cd infrastructure
make db-view           # View database contents
make db-export         # Export to CSV
make db-backup         # Create AWS backup
make db-list-backups   # List all backups
```

### User Management
```bash
cd infrastructure
make cognito-list-users                                    # List all users
make cognito-create-admin EMAIL=admin@example.com          # Create admin
make cognito-add-to-group EMAIL=user@example.com GROUP=admins  # Add to group
```

### Monitoring
```bash
cd infrastructure
make costs             # Show AWS costs
make list              # List all stacks
```

### Update Dependencies
```bash
# Infrastructure
cd infrastructure
make install

# Frontend
cd frontend
npm install
```

### Clean Everything
```bash
# Infrastructure
cd infrastructure
make clean

# Tests
cd infrastructure
make test-clean

# Frontend
cd frontend
rm -rf node_modules dist
```

## 🆘 Troubleshooting

### "Virtual environment not found"
```bash
./setup-venv.sh  # Run setup again
```

### "AWS credentials not configured"
```bash
aws configure
# or check prerequisites
cd infrastructure && make check-prereqs
```

### "CDK command not found"
```bash
npm install -g aws-cdk
```

### "Python version too old"
```bash
python3 --version  # Should be 3.11+
# Install Python 3.11+ and recreate venv
```

### "Stack deployment failed"
```bash
cd infrastructure
make fix-stuck-stack  # Fix stuck CloudFormation stack
```

## 📚 More Information

- **Full Setup Guide**: [setup.md](setup.md)
- **Deployment Guide**: [deployment.md](deployment.md)
- **Infrastructure Quickstart**: [../operations/infrastructure-quickstart.md](../operations/infrastructure-quickstart.md)
- **All Commands**: [../../reference/commands.md](../../reference/commands.md)

## ✅ Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] AWS CLI installed and configured
- [ ] AWS CDK CLI installed (`npm install -g aws-cdk`)
- [ ] Virtual environments created (`./setup-venv.sh`)
- [ ] Frontend dependencies installed (`cd frontend && npm install`)
- [ ] Infrastructure deployed (`cd infrastructure && make deploy-dev`)
- [ ] Frontend running (`cd frontend && npm run dev`)

**You're ready to develop! 🎉**

## 💡 Pro Tips

- Use `make help` in infrastructure/ to see all available commands
- Use `make describe-infra` to get frontend .env configuration
- Use `make test` before deploying to catch issues early
- Use `make db-view` to inspect database contents
- Use `make costs` to monitor AWS spending
