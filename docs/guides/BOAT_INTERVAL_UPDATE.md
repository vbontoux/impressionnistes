# Boat Interval Update: 30s → 60s

## Summary

Changed the default boat interval for semi-marathon races from 30 seconds to 60 seconds (1 minute).

## Changes Made

### 1. Updated Default Configuration
**File:** `functions/init/init_config.py`
- Changed `semi_marathon_interval_seconds` from `30` to `60`
- This affects new database initializations

### 2. Created Migration Script
**File:** `functions/migrations/update_boat_interval.py`
- Updates existing databases (dev and prod)
- Changes the `RACE_TIMING` configuration record
- Safe to run multiple times (idempotent)

## Running the Migration

### For Dev Environment:
```bash
cd infrastructure
make db-migrate MIGRATION=update_boat_interval ENV=dev
```

### For Prod Environment:
```bash
cd infrastructure
make db-migrate MIGRATION=update_boat_interval ENV=prod
```

## What This Affects

- **Event Configuration Page**: The "Boat Interval (seconds)" field will show 60 instead of 30
- **Race Timing**: Boats will start 60 seconds apart instead of 30 seconds
- **Bow Number Calculation**: More time between boats for semi-marathon races

## Verification

After running the migration, verify in the admin panel:
1. Go to Event Configuration
2. Check "Boat Interval (seconds)" field
3. Should show: `60`

## Rollback

If needed, you can manually update the value back to 30 in the Event Configuration page, or create a reverse migration.

## Notes

- This only affects semi-marathon races (21km)
- Marathon races (42km) are not affected
- The change applies to bow number calculations and start time scheduling
