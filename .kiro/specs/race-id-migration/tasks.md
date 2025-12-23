# Implementation Plan: Race ID Migration

## Overview

This implementation plan provides step-by-step tasks for migrating race_id values in the DynamoDB database and updating the init_config.py initialization script. The plan follows a safe, incremental approach with verification at each step.

## Tasks

- [x] 1. Create migration script
  - Create `functions/migrations/update_race_ids.py` following the migration template
  - Include the complete race_id mapping dictionary (55 races total)
  - Implement `get_race_id_mapping()` function to return the mapping
  - Implement `update_race_id()` function to handle delete-and-recreate logic for races
  - Implement `update_boat_registrations()` function to update race_id in TEAM records
  - Implement `run_migration()` function with logging and error handling
  - Add confirmation prompt and dry-run support
  - _Requirements: 1.6, 1.7, 1.8, 3.1, 3.3, 3.4, 3.5_

- [x] 2. Update init_config.py with new race IDs
  - Update marathon_races list (14 races) with new race_id values
  - Update semi_marathon_races list (41 races) with new race_id values
  - Verify all race names and attributes remain unchanged
  - Ensure idempotent behavior is preserved
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 3. Create database backups
  - Run `make db-backup ENV=dev` to create dev backup
  - Run `make db-backup ENV=prod` to create prod backup
  - Note backup ARNs for potential rollback
  - _Requirements: 5.4_

- [x] 4. Export current database state
  - Run `make db-export ENV=dev` to export dev database
  - Run `make db-export ENV=prod` to export prod database
  - Save exports for comparison after migration
  - _Requirements: 5.3_

- [x] 5. Checkpoint - Review migration script and backups
  - Ensure migration script is complete and tested
  - Verify backups are created successfully
  - Verify exports show current race_id values
  - Ask the user if questions arise

- [x] 6. Run migration on dev environment
  - Execute: `cd infrastructure && make db-migrate MIGRATION=update_race_ids ENV=dev`
  - Confirm when prompted
  - Monitor output for errors
  - Verify success message and count of updated races
  - _Requirements: 1.1, 3.2, 3.3_

- [x] 7. Verify dev migration results
  - Run `make db-export ENV=dev` to export migrated database
  - Compare race_id values with expected new values
  - Verify race count remains 55 (14 marathon + 41 semi-marathon)
  - Verify all race names and attributes unchanged
  - Verify races sort correctly by new race_id
  - Verify boat registrations reference new race_id values
  - Verify boat registration count unchanged
  - Verify all boat registration attributes unchanged (except race_id)
  - _Requirements: 1.4, 1.6, 1.7, 1.8, 4.5, 4.7, 4.8, 4.9, 4.10, 5.3_

- [x] 8. Deploy updated init_config.py to dev
  - Execute: `cd infrastructure && make deploy-dev`
  - Monitor deployment progress
  - Check CloudWatch logs for init_config execution
  - Verify no errors during race initialization
  - _Requirements: 2.3, 5.5_

- [x] 9. Checkpoint - Verify dev environment
  - Ensure all dev migration steps completed successfully
  - Verify database exports show correct race_id values
  - Verify deployment completed without errors
  - Ask the user if ready to proceed to prod

- [x] 10. Run migration on prod environment
  - Execute: `cd infrastructure && make db-migrate MIGRATION=update_race_ids ENV=prod`
  - Confirm when prompted (will use AWS profile 'rcpm')
  - Monitor output for errors
  - Verify success message and count of updated races
  - _Requirements: 1.2, 3.2, 3.3_

- [x] 11. Verify prod migration results
  - Run `make db-export ENV=prod` to export migrated database
  - Compare race_id values with expected new values
  - Verify race count remains 55 (14 marathon + 41 semi-marathon)
  - Verify all race names and attributes unchanged
  - Verify races sort correctly by new race_id
  - Verify boat registrations reference new race_id values
  - Verify boat registration count unchanged
  - Verify all boat registration attributes unchanged (except race_id)
  - _Requirements: 1.4, 1.6, 1.7, 1.8, 4.5, 4.7, 4.8, 4.9, 4.10, 5.3_

- [x] 12. Deploy updated init_config.py to prod
  - Execute: `cd infrastructure && make deploy-prod`
  - Confirm when prompted
  - Monitor deployment progress
  - Check CloudWatch logs for init_config execution
  - Verify no errors during race initialization
  - _Requirements: 2.3, 5.5_

- [x] 13. Final verification and cleanup
  - Verify both dev and prod databases have correct race_id values
  - Test race exports to ensure proper sorting
  - Delete migration script: `rm functions/migrations/update_race_ids.py`
  - Document migration completion date and results
  - Archive backup ARNs for reference
  - _Requirements: 5.3_

## Notes

- All tasks must be executed in order
- Do not proceed to prod migration until dev is verified
- Keep backups until migration is fully verified in both environments
- The migration script will be deleted after successful completion
- Each checkpoint ensures safe progression through the migration
- The Makefile will automatically use the 'rcpm' AWS profile for prod environment
