# Frontend Setup Guide

## Quick Start

### 1. Get Infrastructure Details

```bash
cd infrastructure
make describe-infra ENV=dev
```

This will display:
- API Gateway URL
- Cognito User Pool ID
- Cognito Client ID
- Cognito Domain
- Ready-to-copy `.env` configuration

### 2. Configure Frontend

Copy the output from `describe-infra` to `frontend/.env`:

```bash
cd frontend
cp .env.example .env
# Paste the configuration from describe-infra
```

Or use this one-liner:

```bash
cd infrastructure
make describe-infra ENV=dev | grep "VITE_" > ../frontend/.env
```

### 3. Install Dependencies

```bash
cd frontend
npm install
```

### 4. Start Development Server

```bash
npm run dev
```

Visit: http://localhost:3000

## Test Registration

1. Go to http://localhost:3000/register
2. Fill in the form:
   - Email: your-email@example.com
   - Password: TestPass123!
   - First Name: Jean
   - Last Name: Dupont
   - Club: Test Club
   - Mobile: +33612345678
3. Click "Register"
4. Check for success message
5. Verify email in Cognito Console

## Test Login

1. Go to http://localhost:3000/login
2. Click "Login with Cognito"
3. You'll be redirected to Cognito Hosted UI
4. Enter your credentials
5. After login, you'll be redirected to dashboard

## Makefile Commands

```bash
# Show infrastructure details
make describe-infra ENV=dev

# Deploy API Gateway
make deploy-api ENV=dev

# Deploy Auth stack
make deploy-auth ENV=dev

# List Cognito users
make cognito-list-users ENV=dev

# Create admin user
make cognito-create-admin EMAIL=admin@example.com ENV=dev
```

## Troubleshooting

### "Stacks not fully deployed"

Run:
```bash
cd infrastructure
make deploy ENV=dev
```

### CORS Errors

Make sure the API URL in `.env` matches the deployed API Gateway URL.

### Cognito Redirect Issues

Ensure `VITE_COGNITO_REDIRECT_URI` matches the callback URL configured in Cognito.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── LoginForm.vue
│   │   └── RegisterForm.vue
│   ├── views/
│   │   ├── Home.vue
│   │   ├── Login.vue
│   │   ├── Register.vue
│   │   └── Dashboard.vue
│   ├── stores/
│   │   └── authStore.js
│   ├── services/
│   │   └── authService.js
│   ├── router/
│   │   └── index.js
│   ├── locales/
│   │   ├── en.json
│   │   └── fr.json
│   ├── App.vue
│   └── main.js
├── .env
├── index.html
├── vite.config.js
└── package.json
```

## Next Steps

- Complete password reset component
- Add profile editing
- Implement crew member management
- Add boat registration forms
