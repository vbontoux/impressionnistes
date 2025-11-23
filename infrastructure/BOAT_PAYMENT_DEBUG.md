# Boat Payment Debug Commands

Quick reference for resetting boat payment status for testing and demos.

## Commands

### List Paid Boats

Show all paid boats for a team manager:

```bash
make boat-list-paid TEAM_MANAGER_ID=your-user-id
```

**Example:**
```bash
make boat-list-paid TEAM_MANAGER_ID=717940ae-6051-70cb-9437-fac29614d317
```

**Output:**
```
BoatID                                EventType      BoatType    Status  PaidAt
1c33fcfa-b13c-4f34-a1fe-c9abaddba6e3  semi-marathon  skiff       paid    2024-11-23T16:33:19Z
```

### Reset Single Boat to Unpaid

Reset a specific boat from "paid" to "complete" status:

```bash
make boat-unpay TEAM_MANAGER_ID=your-user-id BOAT_ID=boat-id
```

**Example:**
```bash
make boat-unpay \
  TEAM_MANAGER_ID=717940ae-6051-70cb-9437-fac29614d317 \
  BOAT_ID=1c33fcfa-b13c-4f34-a1fe-c9abaddba6e3
```

**What it does:**
- Changes `registration_status` from "paid" to "complete"
- Removes `paid_at` timestamp
- Removes `payment_id`
- Removes `stripe_payment_intent_id`
- Removes `locked_pricing`
- Updates `updated_at` timestamp

### Reset All Boats to Unpaid

Reset ALL paid boats for a team manager:

```bash
make boat-unpay-all TEAM_MANAGER_ID=your-user-id
```

**Example:**
```bash
make boat-unpay-all TEAM_MANAGER_ID=717940ae-6051-70cb-9437-fac29614d317
```

**What it does:**
- Finds all boats with status "paid"
- Shows count and list
- Asks for confirmation
- Resets each boat to "complete" status

## How to Get Your Team Manager ID

### Method 1: From Cognito

```bash
make cognito-list-users
```

Look for your email and copy the `sub` (user ID).

### Method 2: From DynamoDB Export

```bash
make db-view
```

Look for entries with `PK` starting with `TEAM#` and copy the ID after `TEAM#`.

### Method 3: From Browser Console

When logged in to the application:
1. Open browser console (F12)
2. Go to Application → Local Storage
3. Look for authentication data
4. Find `user_id` or `sub`

## Use Cases

### Testing Payment Flow

```bash
# 1. Make a payment in the app
# 2. Verify boat shows as "paid"
# 3. Reset boat to test again
make boat-unpay TEAM_MANAGER_ID=xxx BOAT_ID=xxx
# 4. Boat is now "complete" and can be paid again
```

### Demo Preparation

```bash
# Reset all boats before demo
make boat-unpay-all TEAM_MANAGER_ID=xxx

# Now all boats are ready to demonstrate payment flow
```

### Development Testing

```bash
# List paid boats
make boat-list-paid TEAM_MANAGER_ID=xxx

# Reset specific boat for testing
make boat-unpay TEAM_MANAGER_ID=xxx BOAT_ID=xxx
```

## Safety Features

- ✅ Requires confirmation before resetting
- ✅ Shows what will be changed
- ✅ Only affects specified team manager's boats
- ✅ Preserves all other boat data
- ✅ Updates timestamp for tracking

## Environment

All commands default to `dev` environment. To use production:

```bash
make boat-list-paid TEAM_MANAGER_ID=xxx ENV=prod
make boat-unpay TEAM_MANAGER_ID=xxx BOAT_ID=xxx ENV=prod
make boat-unpay-all TEAM_MANAGER_ID=xxx ENV=prod
```

⚠️ **Warning**: Be careful when using these commands in production!

## What Gets Reset

When you reset a boat to unpaid:

**Removed:**
- `paid_at` - Payment timestamp
- `payment_id` - Internal payment record ID
- `stripe_payment_intent_id` - Stripe payment intent ID
- `locked_pricing` - Locked pricing at payment time

**Changed:**
- `registration_status`: "paid" → "complete"
- `updated_at`: Updated to current timestamp

**Preserved:**
- All boat details (type, event, etc.)
- Crew assignments
- Seat assignments
- Race selection
- Pricing calculation (will be recalculated)
- Multi-club status
- Rental status

## Notes

- These commands are for **development and testing only**
- In production, paid boats should generally not be reset
- The Stripe payment record is NOT affected (remains in Stripe)
- The DynamoDB payment record is NOT deleted
- The boat simply becomes available for payment again

## Troubleshooting

### "No paid boats found"

- Verify the team manager ID is correct
- Check that boats are actually paid (use `make db-view`)
- Verify you're using the correct environment (dev/prod)

### "Operation cancelled"

- You must type exactly "yes" to confirm
- Any other input cancels the operation

### Permission denied

- Verify AWS credentials are configured
- Check IAM permissions for DynamoDB access

## Related Commands

```bash
# View all database contents
make db-view

# Export database to CSV
make db-export

# List Cognito users
make cognito-list-users
```

## Quick Reference

```bash
# List paid boats
make boat-list-paid TEAM_MANAGER_ID=xxx

# Reset one boat
make boat-unpay TEAM_MANAGER_ID=xxx BOAT_ID=xxx

# Reset all boats
make boat-unpay-all TEAM_MANAGER_ID=xxx
```

That's it! These commands make it easy to test the payment flow repeatedly. 🎉
