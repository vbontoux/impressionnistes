# Lambda Testing Guide

Quick guide for testing Lambda functions in the AWS Console.

## Test Files

- **`functions/auth/TEST_EVENTS.md`** - Detailed guide with all test events and explanations
- **`functions/auth/test-events.json`** - JSON file with all test payloads

## Quick Start

### 1. Find Your Lambda Functions

Go to AWS Lambda Console and look for:
- `ImpressionnistesApi-dev-RegisterFunction`
- `ImpressionnistesApi-dev-GetProfileFunction`
- `ImpressionnistesApi-dev-UpdateProfileFunction`
- `ImpressionnistesApi-dev-ForgotPasswordFunction`
- `ImpressionnistesApi-dev-ConfirmPasswordResetFunction`

### 2. Test Registration

1. Open `RegisterFunction`
2. Click "Test" tab
3. Create new test event named "register-test"
4. Paste this JSON:

```json
{
  "body": "{\"email\":\"your-email@example.com\",\"password\":\"TestPass123!\",\"first_name\":\"Jean\",\"last_name\":\"Dupont\",\"club_affiliation\":\"Test Club\",\"mobile_number\":\"+33612345678\"}"
}
```

5. Click "Test"
6. Check the response - should be 201 Created

### 3. Verify User in Cognito

1. Go to Amazon Cognito Console
2. Select your User Pool (`impressionnistes-users-dev`)
3. Find the user you just created
4. Click "Confirm user" (or use the verification code from email)
5. Copy the user's `sub` (user ID) - you'll need this for other tests

### 4. Test Get Profile

1. Open `GetProfileFunction`
2. Create test event with your user's `sub`:

```json
{
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com",
        "given_name": "Jean",
        "family_name": "Dupont",
        "custom:club_affiliation": "Test Club",
        "custom:role": "team_manager",
        "cognito:groups": "team_managers"
      }
    }
  }
}
```

3. Click "Test"
4. Should return your profile data

### 5. Test Update Profile

1. Open `UpdateProfileFunction`
2. Create test event:

```json
{
  "body": "{\"first_name\":\"Pierre\",\"club_affiliation\":\"New Club\"}",
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com"
      }
    }
  }
}
```

3. Click "Test"
4. Should return updated profile

### 6. Test Password Reset

1. Open `ForgotPasswordFunction`
2. Create test event:

```json
{
  "body": "{\"email\":\"your-email@example.com\"}"
}
```

3. Click "Test"
4. Check your email for verification code
5. Open `ConfirmPasswordResetFunction`
6. Create test event with the code:

```json
{
  "body": "{\"email\":\"your-email@example.com\",\"code\":\"123456\",\"new_password\":\"NewPass123!\"}"
}
```

7. Click "Test"
8. Password should be reset

## Getting User IDs

### Option 1: From Cognito Console
1. Go to Cognito User Pool
2. Click on Users
3. Click on a user
4. Copy the `sub` attribute

### Option 2: Using AWS CLI

```bash
aws cognito-idp list-users \
  --user-pool-id $(aws cloudformation describe-stacks \
    --stack-name ImpressionnistesAuth-dev \
    --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
    --output text) \
  --query 'Users[].{Email:Attributes[?Name==`email`].Value|[0],Sub:Attributes[?Name==`sub`].Value|[0]}'
```

### Option 3: Using Makefile

```bash
cd infrastructure
make cognito-list-users ENV=dev
```

## Checking Logs

View function logs in CloudWatch:

```bash
# View logs for a specific function
aws logs tail /aws/lambda/ImpressionnistesApi-dev-RegisterFunction --follow

# Or in the Lambda Console
# Click on "Monitor" tab → "View CloudWatch logs"
```

## Common Issues

### "User already exists"
- Email is already registered
- Use a different email or delete the user from Cognito

### "Profile not found"
- User wasn't created via Register function
- Check DynamoDB table: `impressionnistes-registration-dev`
- Look for item with PK=`USER#{user-id}` and SK=`PROFILE`

### "Invalid verification code"
- Code expired (24 hours)
- Request new password reset

### "Authentication required"
- Missing `requestContext.authorizer.claims`
- Make sure to include full auth context in test event

## Verify in DynamoDB

Check if profile was created:

```bash
aws dynamodb get-item \
  --table-name impressionnistes-registration-dev \
  --key '{"PK":{"S":"USER#your-user-id"},"SK":{"S":"PROFILE"}}'
```

Or use the Makefile:

```bash
cd infrastructure
make db-view ENV=dev
```

## Success Indicators

✅ **Register**: Returns 201 with user_id and success message
✅ **Get Profile**: Returns 200 with complete profile data
✅ **Update Profile**: Returns 200 with updated fields
✅ **Forgot Password**: Returns 200 (always, for security)
✅ **Confirm Reset**: Returns 200 with success message

## Next Steps

After testing individual functions:
1. Test the complete registration flow
2. Test error cases (invalid data, missing fields)
3. Test with multiple users
4. Verify data in DynamoDB
5. Check CloudWatch logs for any warnings

## Full Test Event Reference

See `functions/auth/TEST_EVENTS.md` for:
- All test event variations
- Error case testing
- Expected responses
- Troubleshooting guide
- CLI testing commands


## Crew Member Management Testing

### Lambda Functions
- `ImpressionnistesApi-dev-CreateCrewMemberFunction`
- `ImpressionnistesApi-dev-ListCrewMembersFunction`
- `ImpressionnistesApi-dev-GetCrewMemberFunction`
- `ImpressionnistesApi-dev-UpdateCrewMemberFunction`
- `ImpressionnistesApi-dev-DeleteCrewMemberFunction`

### Test Create Crew Member

```json
{
  "body": "{\"first_name\":\"Marie\",\"last_name\":\"Martin\",\"date_of_birth\":\"1995-06-15\",\"gender\":\"F\",\"license_number\":\"ABC123\",\"club_affiliation\":\"RCPM\"}",
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com",
        "custom:club_affiliation": "RCPM"
      }
    }
  }
}
```

### Test List Crew Members

```json
{
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com"
      }
    }
  }
}
```

### Test Update Crew Member

```json
{
  "pathParameters": {
    "crew_member_id": "PASTE-CREW-MEMBER-ID-HERE"
  },
  "body": "{\"first_name\":\"Marie-Claire\",\"license_number\":\"ABC456\"}",
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com"
      }
    }
  }
}
```

## Boat Registration Testing

### Lambda Functions
- `ImpressionnistesApi-dev-CreateBoatRegistrationFunction`
- `ImpressionnistesApi-dev-ListBoatRegistrationsFunction`
- `ImpressionnistesApi-dev-GetBoatRegistrationFunction`
- `ImpressionnistesApi-dev-UpdateBoatRegistrationFunction`
- `ImpressionnistesApi-dev-DeleteBoatRegistrationFunction`

### Test Create Boat Registration (Skiff - 42km)

```json
{
  "body": "{\"event_type\":\"42km\",\"boat_type\":\"skiff\"}",
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com"
      }
    }
  }
}
```

**Expected Response:**
```json
{
  "statusCode": 201,
  "body": {
    "boat_registration_id": "uuid-here",
    "event_type": "42km",
    "boat_type": "skiff",
    "seats": [
      {"position": 1, "type": "rower", "crew_member_id": null}
    ],
    "registration_status": "incomplete",
    "is_boat_rental": false,
    "is_multi_club_crew": false
  }
}
```

### Test Create Boat Registration (Four with Cox - 21km)

```json
{
  "body": "{\"event_type\":\"21km\",\"boat_type\":\"4+\"}",
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com"
      }
    }
  }
}
```

**Expected Response:**
```json
{
  "statusCode": 201,
  "body": {
    "boat_registration_id": "uuid-here",
    "event_type": "21km",
    "boat_type": "4+",
    "seats": [
      {"position": 1, "type": "rower", "crew_member_id": null},
      {"position": 2, "type": "rower", "crew_member_id": null},
      {"position": 3, "type": "rower", "crew_member_id": null},
      {"position": 4, "type": "rower", "crew_member_id": null},
      {"position": 5, "type": "cox", "crew_member_id": null}
    ],
    "registration_status": "incomplete"
  }
}
```

### Test Create Boat Registration (Eight - 21km)

```json
{
  "body": "{\"event_type\":\"21km\",\"boat_type\":\"8+\"}",
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com"
      }
    }
  }
}
```

### Test List Boat Registrations

```json
{
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com"
      }
    }
  }
}
```

**Expected Response:**
```json
{
  "statusCode": 200,
  "body": {
    "boat_registrations": [
      {
        "boat_registration_id": "uuid-1",
        "event_type": "42km",
        "boat_type": "skiff",
        "registration_status": "incomplete"
      },
      {
        "boat_registration_id": "uuid-2",
        "event_type": "21km",
        "boat_type": "4+",
        "registration_status": "complete"
      }
    ]
  }
}
```

### Test Get Boat Registration

```json
{
  "pathParameters": {
    "boat_registration_id": "PASTE-BOAT-REGISTRATION-ID-HERE"
  },
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com"
      }
    }
  }
}
```

### Test Update Boat Registration (Assign Crew Members)

```json
{
  "pathParameters": {
    "boat_registration_id": "PASTE-BOAT-REGISTRATION-ID-HERE"
  },
  "body": "{\"seats\":[{\"position\":1,\"type\":\"rower\",\"crew_member_id\":\"crew-member-id-1\"},{\"position\":2,\"type\":\"rower\",\"crew_member_id\":\"crew-member-id-2\"},{\"position\":3,\"type\":\"rower\",\"crew_member_id\":\"crew-member-id-3\"},{\"position\":4,\"type\":\"rower\",\"crew_member_id\":\"crew-member-id-4\"},{\"position\":5,\"type\":\"cox\",\"crew_member_id\":\"crew-member-id-5\"}]}",
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com"
      }
    }
  }
}
```

### Test Update Boat Registration (Select Race)

```json
{
  "pathParameters": {
    "boat_registration_id": "PASTE-BOAT-REGISTRATION-ID-HERE"
  },
  "body": "{\"race_id\":\"SM01\"}",
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com"
      }
    }
  }
}
```

### Test Update Boat Registration (Mark as Boat Rental)

```json
{
  "pathParameters": {
    "boat_registration_id": "PASTE-BOAT-REGISTRATION-ID-HERE"
  },
  "body": "{\"is_boat_rental\":true}",
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com"
      }
    }
  }
}
```

### Test Delete Boat Registration

```json
{
  "pathParameters": {
    "boat_registration_id": "PASTE-BOAT-REGISTRATION-ID-HERE"
  },
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE",
        "email": "your-email@example.com"
      }
    }
  }
}
```

**Expected Response:**
```json
{
  "statusCode": 200,
  "body": {
    "message": "Boat registration deleted successfully"
  }
}
```

## Boat Registration Testing Workflow

### Complete Registration Flow

1. **Create crew members** (at least 1 for skiff, 4-5 for 4+, 8-9 for 8+)
2. **Create boat registration** with event and boat type
3. **Update boat registration** to assign crew members to seats
4. **Update boat registration** to select a race (based on crew eligibility)
5. **Verify registration status** changes to "complete"
6. **Test payment** (future task)

### Test Validation Rules

**Invalid Boat Type for Event:**
```json
{
  "body": "{\"event_type\":\"42km\",\"boat_type\":\"4+\"}",
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE"
      }
    }
  }
}
```
**Expected:** 400 error - "Boat type '4+' is not valid for event '42km'"

**Valid Combinations:**
- 42km: skiff only
- 21km: 4-, 4+, 8+

### Registration Status States

- **incomplete**: Missing crew assignments or race selection
- **complete**: All seats filled and race selected
- **paid**: Payment processed (future)

### Multi-Club Crew Detection

When crew members from different clubs are assigned:
```json
{
  "body": "{\"seats\":[{\"position\":1,\"type\":\"rower\",\"crew_member_id\":\"rcpm-member\"},{\"position\":2,\"type\":\"rower\",\"crew_member_id\":\"external-member\"},...]}",
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "PASTE-YOUR-USER-ID-HERE"
      }
    }
  }
}
```
**Expected:** `is_multi_club_crew` automatically set to `true`

## Verify in DynamoDB

### Check Boat Registration
```bash
aws dynamodb query \
  --table-name impressionnistes-registration-dev \
  --key-condition-expression "PK = :pk AND begins_with(SK, :sk)" \
  --expression-attribute-values '{":pk":{"S":"TEAM#your-user-id"},":sk":{"S":"BOAT#"}}'
```

### Check Crew Member Assignment
```bash
aws dynamodb get-item \
  --table-name impressionnistes-registration-dev \
  --key '{"PK":{"S":"TEAM#your-user-id"},"SK":{"S":"CREW#crew-member-id"}}'
```

Look for `assigned_boat_id` field.

## Common Boat Registration Issues

### "Boat type not valid for event"
- Check valid combinations: 42km=skiff, 21km=4-/4+/8+

### "Crew member already assigned"
- A crew member can only be in one boat
- Delete or update the other boat registration first

### Registration stays "incomplete"
- Ensure all seats have crew_member_id assigned
- Ensure race_id is selected

### "Boat registration not found"
- Check the boat_registration_id is correct
- Verify it belongs to the authenticated user

## Success Indicators

✅ **Create Boat**: Returns 201 with boat_registration_id and seat structure
✅ **List Boats**: Returns 200 with array of registrations
✅ **Get Boat**: Returns 200 with complete boat details
✅ **Update Boat**: Returns 200 with updated fields and recalculated status
✅ **Delete Boat**: Returns 200 and unassigns crew members
✅ **Multi-Club Detection**: Automatically sets is_multi_club_crew flag
✅ **Status Calculation**: Automatically updates registration_status
