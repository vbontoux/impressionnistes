# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### 1. Setup (One Time)

```bash
# Clone and enter directory
git clone <repo-url>
cd impressionnistes-registration-system

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
./deploy.sh dev
```

### 3. Run Frontend

```bash
cd frontend
npm run dev
```

## 📋 Daily Development Commands

### Backend Testing
```bash
cd backend
make test
# or
source venv/bin/activate && pytest
```

### Infrastructure Changes
```bash
cd infrastructure
make diff        # See what will change
make deploy-dev  # Deploy changes
```

### Frontend Development
```bash
cd frontend
npm run dev      # Start dev server
npm run build    # Build for production
```

## 🔧 Common Tasks

### Add Python Package
```bash
cd backend  # or infrastructure
source venv/bin/activate
pip install package-name
pip freeze > requirements.txt
deactivate
```

### Update Dependencies
```bash
# Backend
cd backend && make install

# Infrastructure
cd infrastructure && make install

# Frontend
cd frontend && npm install
```

### Clean Everything
```bash
# Backend
cd backend && make clean

# Infrastructure
cd infrastructure && make clean

# Frontend
cd frontend && rm -rf node_modules dist
```

## 🆘 Troubleshooting

### "Virtual environment not found"
```bash
./setup-venv.sh  # Run setup again
```

### "AWS credentials not configured"
```bash
aws configure
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

## 📚 More Information

- **Full Setup Guide**: [SETUP.md](SETUP.md)
- **Project Overview**: [README.md](README.md)
- **Infrastructure Details**: [infrastructure/README.md](infrastructure/README.md)
- **CDK Commands**: [infrastructure/COMMANDS.md](infrastructure/COMMANDS.md)
- **Tasks**: [.kiro/specs/impressionnistes-registration-system/tasks.md](.kiro/specs/impressionnistes-registration-system/tasks.md)

## ✅ Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] AWS CLI installed and configured
- [ ] AWS CDK CLI installed
- [ ] Virtual environments created (`./setup-venv.sh`)
- [ ] Frontend dependencies installed (`cd frontend && npm install`)
- [ ] Infrastructure deployed (`cd infrastructure && ./deploy.sh dev`)
- [ ] Frontend running (`cd frontend && npm run dev`)

**You're ready to develop! 🎉**
