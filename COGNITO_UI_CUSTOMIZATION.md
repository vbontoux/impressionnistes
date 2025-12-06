# Cognito Hosted UI Customization

## Overview

The Cognito Hosted UI is now automatically customized with the RCPM logo and custom branding colors.

## How It Works

1. **Logo Storage**: The logo from `frontend/src/assets/rcpm-logo.png` is deployed to the S3 bucket at `cognito-assets/rcpm-logo.png`
2. **Stable URL**: The logo is accessible via CloudFront at a stable URL that doesn't change with builds
3. **Automatic Configuration**: A custom Lambda resource automatically configures Cognito UI customization during deployment

## Deployment

Deploy the infrastructure as usual:

```bash
cd infrastructure
make deploy-dev
```

The deployment will:
- Upload the logo to S3 under `cognito-assets/`
- Configure Cognito UI with the logo and custom CSS
- Output the Cognito Hosted UI URL

## Customization

### Logo

To change the logo, replace `frontend/src/assets/rcpm-logo.png` and redeploy.

### CSS Styling

The custom CSS is defined in `infrastructure/stacks/auth_stack.py` in the `configure_ui_customization()` method.

Current customizations:
- Logo max size: 200px width, 100px height
- Banner background: Blue (#1976d2)
- Submit button: Blue with hover effect

To modify the styling, edit the `custom_css` variable in `auth_stack.py` and redeploy.

### Available CSS Classes

Cognito provides these customizable classes:
- `.logo-customizable` - Logo image
- `.banner-customizable` - Top banner
- `.label-customizable` - Form labels
- `.textDescription-customizable` - Description text
- `.inputField-customizable` - Input fields
- `.inputField-customizable:focus` - Focused input fields
- `.submitButton-customizable` - Submit button
- `.submitButton-customizable:hover` - Submit button hover state
- `.errorMessage-customizable` - Error messages
- `.idpButton-customizable` - Social login buttons

## Verification

After deployment:

1. Get the Cognito Hosted UI URL from the stack outputs:
   ```bash
   make describe-infra
   ```

2. Visit the login page - you should see the RCPM logo and blue branding

3. The logo URL is available in the CloudFormation outputs as `CognitoLogoURL`

## Troubleshooting

**Logo not showing:**
- Check that the logo was deployed to S3: Look for `cognito-assets/rcpm-logo.png` in the S3 bucket
- Verify the CloudFront distribution is serving the logo: Visit the `CognitoLogoURL` directly
- Check Lambda logs for the UI customization function

**CSS not applied:**
- Check CloudWatch logs for the `CognitoUICustomization` Lambda function
- Verify the custom resource completed successfully in CloudFormation

**To manually verify UI customization status:**
```bash
# Dev environment
aws cognito-idp get-ui-customization \
  --user-pool-id $(aws cloudformation describe-stacks --stack-name ImpressionnistesAuth-dev --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' --output text) \
  --client-id $(aws cloudformation describe-stacks --stack-name ImpressionnistesAuth-dev --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' --output text)

# Prod environment
aws cognito-idp get-ui-customization \
  --user-pool-id $(aws cloudformation describe-stacks --stack-name ImpressionnistesAuth-prod --profile rcpm --region eu-west-3 --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' --output text) \
  --client-id $(aws cloudformation describe-stacks --stack-name ImpressionnistesAuth-prod --profile rcpm --region eu-west-3 --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' --output text) \
  --profile rcpm --region eu-west-3
```

### Manual UI Customization (Workaround)

If the automatic CDK deployment doesn't apply the UI customization, you can apply it manually:

**Dev environment:**
```bash
# Download the logo
curl -s https://$(aws cloudformation describe-stacks --stack-name ImpressiornistesFrontend-dev --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' --output text | sed 's|https://||')/cognito-assets/rcpm-logo.png -o /tmp/rcpm-logo.png

# Apply UI customization
aws cognito-idp set-ui-customization \
  --user-pool-id $(aws cloudformation describe-stacks --stack-name ImpressionnistesAuth-dev --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' --output text) \
  --client-id $(aws cloudformation describe-stacks --stack-name ImpressionnistesAuth-dev --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' --output text) \
  --css '.logo-customizable { max-width: 200px; max-height: 100px; } .banner-customizable { background-color: #1976d2; } .submitButton-customizable { background-color: #1976d2; } .submitButton-customizable:hover { background-color: #1565c0; }' \
  --image-file fileb:///tmp/rcpm-logo.png
```

**Prod environment:**
```bash
# Download the logo
curl -s https://$(aws cloudformation describe-stacks --stack-name ImpressiornistesFrontend-prod --profile rcpm --region eu-west-3 --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' --output text | sed 's|https://||')/cognito-assets/rcpm-logo.png -o /tmp/rcpm-logo.png

# Apply UI customization
aws cognito-idp set-ui-customization \
  --user-pool-id $(aws cloudformation describe-stacks --stack-name ImpressionnistesAuth-prod --profile rcpm --region eu-west-3 --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' --output text) \
  --client-id $(aws cloudformation describe-stacks --stack-name ImpressionnistesAuth-prod --profile rcpm --region eu-west-3 --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' --output text) \
  --css '.logo-customizable { max-width: 200px; max-height: 100px; } .banner-customizable { background-color: #1976d2; } .submitButton-customizable { background-color: #1976d2; } .submitButton-customizable:hover { background-color: #1565c0; }' \
  --image-file fileb:///tmp/rcpm-logo.png \
  --profile rcpm --region eu-west-3
```
