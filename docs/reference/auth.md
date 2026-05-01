## Authentication with Amazon Cognito

Complete guide for user authentication using Amazon Cognito with self-hosted authentication pages.

## Overview

The authentication system uses Amazon Cognito User Pool with:
- **Email/password authentication** via self-hosted custom pages
- **Self-hosted login, registration, forgot password, and password reset pages** (no Cognito Hosted UI)
- **30-minute inactivity timeout** and **5-hour maximum session duration**
- **MFA support** (optional for users)
- **Password policies** and security features
- **Real-time password strength indicator**

## Cognito User Pool

**User Pool Name**: `impressionnistes-users-{env}`

### Sign-in Configuration
- **Sign-in method**: Email only (no username)
- **Self sign-up**: Enabled
- **Email verification**: Required (verification code)

### Password Policy
- Minimum length: 12 characters
- Requires: lowercase, uppercase, digits, special characters
- Real-time password strength indicator in UI
- Temporary password validity: 3 days

### Session Configuration
- **Access token**: 30 minutes
- **ID token**: 30 minutes
- **Refresh token**: 30 days
- **Inactivity timeout**: 30 minutes (auto logout with clear message)
- **Maximum session duration**: 5 hours (auto logout with clear message)

### User Attributes

**Standard attributes:**
- Email (required)
- Given name (required)
- Family name (required)
- Phone number (optional)

**Custom attributes:**
- `club_affiliation` - User's rowing club
- `role` - User role (team_manager, admin, devops)

### MFA (Multi-Factor Authentication)
- **Mode**: Optional (users can enable)
- **Methods**: SMS, TOTP (authenticator app)

## Hosted UI (DEPRECATED)

> **⚠️ DEPRECATED:** The Cognito Hosted UI has been replaced by self-hosted authentication pages. The application now uses custom login, registration, forgot password, and password reset pages that communicate directly with Cognito via the AWS SDK. See the "Self-Hosted Authentication" section below for current implementation details.

**Domain**: `https://impressionnistes-{env}.auth.{region}.amazoncognito.com`

### Callback URLs
- Development: `http://localhost:3000/callback`
- Production: `https://impressionnistes-{env}.rcpm-aviron.fr/callback`

### Logout URLs
- Development: `http://localhost:3000/`
- Production: `https://impressionnistes-{env}.rcpm-aviron.fr/`

## Social Login Configuration (DEPRECATED)

> **⚠️ DEPRECATED:** Social login via Cognito Hosted UI is no longer used. Authentication is handled entirely through self-hosted email/password pages.

### Google OAuth (Optional)

**Setup steps:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials
3. Add authorized redirect URIs:
   ```
   https://impressionnistes-{env}.auth.{region}.amazoncognito.com/oauth2/idpresponse
   ```
4. Get Client ID and Client Secret
5. Uncomment Google provider in `auth_stack.py`
6. Add credentials to secrets.json or Secrets Manager

### Facebook Login (Optional)

**Setup steps:**
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a Facebook App
3. Add Facebook Login product
4. Configure OAuth redirect URIs:
   ```
   https://impressionnistes-{env}.auth.{region}.amazoncognito.com/oauth2/idpresponse
   ```
5. Get App ID and App Secret
6. Uncomment Facebook provider in `auth_stack.py`
7. Add credentials to secrets.json or Secrets Manager

## Self-Hosted Authentication

The application uses custom-built authentication pages that communicate directly with AWS Cognito via the AWS SDK. No redirect to Cognito Hosted UI occurs at any point.

### Authentication Pages

| Page | Route | Purpose |
|------|-------|---------|
| Login | `/login` | Email/password login with "Remember Me" option |
| Register | `/register` | New account creation with consent checkboxes |
| Email Verification | `/verify-email` | Enter verification code sent by email |
| Forgot Password | `/forgot-password` | Request password reset code |
| Reset Password | `/reset-password` | Enter code + new password |

### Authentication Flow

1. **Registration**: User fills custom form → Cognito `signUp` → verification email sent → user enters code on verify page → account confirmed
2. **Login**: User enters email/password on custom form → Cognito `signIn` via AWS SDK → JWT tokens stored → redirect to dashboard
3. **Forgot Password**: User enters email → Cognito `forgotPassword` → code sent → user enters code + new password on reset page → Cognito `confirmForgotPassword`

### Session Management

- **Default storage**: `sessionStorage` (cleared on browser close)
- **"Remember Me" checked**: `localStorage` (persists across browser sessions)
- **Inactivity timeout**: 30 minutes — displays message: "Votre session a expiré après 30 minutes d'inactivité"
- **Maximum duration**: 5 hours — displays message: "Votre session a expiré après 5 heures d'activité"
- **No countdown timer** is displayed for session timeout

### Password Strength Indicator

All password fields (registration and reset) display a real-time strength indicator:
- **Requirements**: 12+ characters, uppercase, lowercase, number, special character
- **Visual feedback**: Color-coded strength bar (weak → strong)
- **Inline validation**: Missing requirements listed as user types

### Error Handling

Cognito errors are mapped to user-friendly messages:
- Incorrect credentials → "Email ou mot de passe incorrect"
- Unverified account → Message with link to verification page
- Rate limiting → "Trop de tentatives. Veuillez réessayer plus tard"
- Network error → "Erreur de connexion. Veuillez vérifier votre connexion internet"

## Using Cognito in Your Application

### Frontend Integration

**Install AWS Amplify:**
```bash
npm install aws-amplify @aws-amplify/ui-react
```

**Configure Amplify:**
```javascript
import { Amplify } from 'aws-amplify';

Amplify.configure({
  Auth: {
    region: 'eu-west-3',
    userPoolId: 'YOUR_USER_POOL_ID',
    userPoolWebClientId: 'YOUR_CLIENT_ID',
    oauth: {
      domain: 'impressionnistes-dev.auth.eu-west-3.amazoncognito.com',
      scope: ['email', 'profile', 'openid'],
      redirectSignIn: 'http://localhost:3000/callback',
      redirectSignOut: 'http://localhost:3000/',
      responseType: 'code'
    }
  }
});
```

**Sign Up:**
```javascript
import { Auth } from 'aws-amplify';

async function signUp(email, password, firstName, lastName, clubAffiliation) {
  try {
    const { user } = await Auth.signUp({
      username: email,
      password,
      attributes: {
        email,
        given_name: firstName,
        family_name: lastName,
        'custom:club_affiliation': clubAffiliation,
        'custom:role': 'team_manager'
      }
    });
    console.log('Sign up success:', user);
  } catch (error) {
    console.error('Sign up error:', error);
  }
}
```

**Confirm Sign Up:**
```javascript
async function confirmSignUp(email, code) {
  try {
    await Auth.confirmSignUp(email, code);
    console.log('Email verified');
  } catch (error) {
    console.error('Verification error:', error);
  }
}
```

**Sign In:**
```javascript
async function signIn(email, password) {
  try {
    const user = await Auth.signIn(email, password);
    console.log('Sign in success:', user);
  } catch (error) {
    console.error('Sign in error:', error);
  }
}
```

**Sign Out:**
```javascript
async function signOut() {
  try {
    await Auth.signOut();
    console.log('Sign out success');
  } catch (error) {
    console.error('Sign out error:', error);
  }
}
```

**Get Current User:**
```javascript
async function getCurrentUser() {
  try {
    const user = await Auth.currentAuthenticatedUser();
    console.log('Current user:', user);
    return user;
  } catch (error) {
    console.log('Not authenticated');
    return null;
  }
}
```

**Get User Attributes:**
```javascript
async function getUserAttributes() {
  try {
    const user = await Auth.currentAuthenticatedUser();
    const attributes = await Auth.userAttributes(user);
    console.log('User attributes:', attributes);
    return attributes;
  } catch (error) {
    console.error('Error getting attributes:', error);
  }
}
```

### Backend Integration (Lambda)

**Verify JWT Token:**
```python
import json
import jwt
from jwt import PyJWKClient

def lambda_handler(event, context):
    # Get token from Authorization header
    token = event['headers'].get('Authorization', '').replace('Bearer ', '')
    
    # Verify token
    region = 'eu-west-3'
    user_pool_id = 'YOUR_USER_POOL_ID'
    
    jwks_url = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
    jwks_client = PyJWKClient(jwks_url)
    
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience='YOUR_CLIENT_ID'
        )
        
        # Token is valid
        user_id = decoded['sub']
        email = decoded['email']
        
        return {
            'statusCode': 200,
            'body': json.dumps({'user_id': user_id, 'email': email})
        }
    except Exception as e:
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Unauthorized'})
        }
```

## API Gateway Integration

**Add Cognito Authorizer to API Gateway:**
```python
# In api_stack.py
from aws_cdk import aws_apigateway as apigateway

authorizer = apigateway.CognitoUserPoolsAuthorizer(
    self,
    "CognitoAuthorizer",
    cognito_user_pools=[auth_stack.user_pool]
)

# Use in API methods
api.root.add_method(
    'GET',
    integration,
    authorizer=authorizer,
    authorization_type=apigateway.AuthorizationType.COGNITO
)
```

## AWS CLI Commands

### List Users
```bash
aws cognito-idp list-users \
  --user-pool-id YOUR_USER_POOL_ID
```

### Get User
```bash
aws cognito-idp admin-get-user \
  --user-pool-id YOUR_USER_POOL_ID \
  --username user@example.com
```

### Create User (Admin)
```bash
aws cognito-idp admin-create-user \
  --user-pool-id YOUR_USER_POOL_ID \
  --username user@example.com \
  --user-attributes Name=email,Value=user@example.com Name=given_name,Value=John Name=family_name,Value=Doe \
  --temporary-password TempPass123
```

### Delete User
```bash
aws cognito-idp admin-delete-user \
  --user-pool-id YOUR_USER_POOL_ID \
  --username user@example.com
```

### Reset Password
```bash
aws cognito-idp admin-reset-user-password \
  --user-pool-id YOUR_USER_POOL_ID \
  --username user@example.com
```

### Enable MFA for User
```bash
aws cognito-idp admin-set-user-mfa-preference \
  --user-pool-id YOUR_USER_POOL_ID \
  --username user@example.com \
  --software-token-mfa-settings Enabled=true,PreferredMfa=true
```

## Testing Authentication

### Test Self-Hosted Login
```bash
# Start the frontend dev server
cd frontend && npm run dev

# Navigate to http://localhost:3000/login
# Test login with valid credentials
# Test forgot password flow
# Test registration flow
```

### Test Sign Up via CLI
```bash
aws cognito-idp sign-up \
  --client-id YOUR_CLIENT_ID \
  --username test@example.com \
  --password TestPass123 \
  --user-attributes Name=email,Value=test@example.com Name=given_name,Value=Test Name=family_name,Value=User
```

## Security Best Practices

1. **Use HTTPS only** - Never send credentials over HTTP
2. **Enable MFA** - Encourage users to enable MFA
3. **Rotate secrets** - Regularly rotate OAuth credentials
4. **Monitor failed logins** - Set up CloudWatch alarms
5. **Use refresh tokens** - Don't store access tokens long-term
6. **Validate tokens** - Always verify JWT signatures
7. **Implement CSRF protection** - Use state parameter in OAuth
8. **Rate limiting** - Cognito has built-in rate limiting

## Troubleshooting

### User can't sign in
- Check if email is verified
- Check if user is enabled
- Check password policy compliance

### Token expired
- Tokens expire after 30 minutes
- Use refresh token to get new tokens
- Implement automatic token refresh

### Social login not working
- Verify OAuth credentials are correct
- Check redirect URIs match exactly
- Ensure identity provider is enabled

### MFA issues
- Verify phone number is confirmed
- Check TOTP time sync
- Use backup codes if available

## Cost Optimization

**Cognito Pricing:**
- First 50,000 MAUs: Free
- 50,001-100,000 MAUs: $0.0055 per MAU
- Advanced security: $0.05 per MAU

**Tips:**
- Use advanced security only in production
- Clean up test users regularly
- Monitor MAU usage

## Related Documentation

- [AWS Amplify Auth](https://docs.amplify.aws/lib/auth/getting-started/q/platform/js/)
- [Cognito User Pools](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html)
- [JWT Verification](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html)
