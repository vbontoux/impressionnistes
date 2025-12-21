# Frontend Testing Guide

## Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Configure environment**:
```bash
cp .env.example .env
```

Edit `.env` with your actual values:
- Get API URL from: `aws cloudformation describe-stacks --stack-name ImpressionnistesApi-dev`
- Get Cognito details from: `aws cloudformation describe-stacks --stack-name ImpressionnistesAuth-dev`

3. **Start development server**:
```bash
npm run dev
```

Visit: http://localhost:3000

## Test the Registration Flow

1. Go to http://localhost:3000/register
2. Fill in the form with valid data
3. Click "Register"
4. Check for success message
5. Verify email was sent (check Cognito console)

## Test the Login Flow

1. Go to http://localhost:3000/login
2. Click "Login with Cognito"
3. You'll be redirected to Cognito Hosted UI
4. Login with your credentials
5. After successful login, you'll be redirected back

## Components Created

- `RegisterForm.vue` - Registration form with validation
- `LoginForm.vue` - Login with Cognito/Social options
- `authStore.js` - Pinia store for auth state
- `authService.js` - API integration
- Router guards for protected routes

## Next Steps

- Deploy API Gateway to get real API URL
- Configure Cognito domain and client ID
- Test end-to-end registration and login
- Add password reset component
