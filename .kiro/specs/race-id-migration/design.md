# Design Document: Race ID Migration

## Overview

This design document outlines the approach for migrating race_id values in the DynamoDB database and updating the init_config.py initialization script. The migration will reorder race IDs to enable logical sorting during exports, grouping races by age category, gender, and boat type.

The solution consists of three main components:
1. A migration script to update existing race records and boat registration records in dev and prod databases
2. Updates to init_config.py to use new race_id values for future deployments
3. A step-by-step execution plan with verification and rollback procedures

**Critical Note:** Boat registrations (TEAM records) contain a `race_id` attribute that references races. When race_id values change, all boat registrations must also be updated to maintain referential integrity.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Migration Workflow                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Create Migration Script (update_race_ids.py)            │
│     - Load race_id mapping from CSV comparison              │
│     - Query existing races from DynamoDB                    │
│     - Update SK and race_id for each race                   │
│     - Query all boat registrations (TEAM records)           │
│     - Update race_id attribute in boat registrations        │
│     - Log all changes for audit                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Update init_config.py                                   │
│     - Replace old race_id values with new values            │
│     - Maintain all other race attributes                    │
│     - Ensure idempotent behavior                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Execute Migration                                       │
│     - Run on dev: make db-migrate MIGRATION=update_race_ids │
│     - Verify results with db-export                         │
│     - Run on prod: make db-migrate MIGRATION=update_race_ids│
│     - Verify results with db-export                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Deploy Updated init_config.py                           │
│     - Deploy to dev: make deploy-dev                        │
│     - Deploy to prod: make deploy-prod                      │
└─────────────────────────────────────────────────────────────┘
```

### DynamoDB Data Model

**Race Record Structure:**
```python
{
    'PK': 'RACE',                    # Partition key (unchanged)
    'SK': 'M01',                     # Sort key (race_id) - TO BE UPDATED
    'GSI2PK': '42km#skiff',          # GSI partition key (unchanged)
    'GSI2SK': 'master#women',        # GSI sort key (unchanged)
    'race_id': 'M01',                # Race ID attribute - TO BE UPDATED
    'name': '1X MASTER F WOMAN',     # Race name (unchanged)
    'event_type': '42km',            # Event type (unchanged)
    'boat_type': 'skiff',            # Boat type (unchanged)
    'age_category': 'master',        # Age category (unchanged)
    'gender_category': 'women',      # Gender category (unchanged)
    'master_category': 'F',          # Master category (unchanged)
    'distance': 42,                  # Distance (unchanged)
    'created_at': '2025-11-20...',   # Created timestamp (unchanged)
    'updated_at': '2025-12-23...'    # Updated timestamp - TO BE UPDATED
}
```

**Boat Registration Record Structure:**
```python
{
    'PK': 'TEAM',                    # Partition key (unchanged)
    'SK': 'TEAM#uuid',               # Sort key (team_id) - UNCHANGED
    'team_id': 'uuid',               # Team ID (unchanged)
    'race_id': 'M01',                # Race ID reference - TO BE UPDATED
    'team_name': 'Team Name',        # Team name (unchanged)
    'members': [...],                # Members list (unchanged)
    'payment_status': 'pending',     # Payment status (unchanged)
    'created_at': '2025-11-20...',   # Created timestamp (unchanged)
    'updated_at': '2025-12-23...'    # Updated timestamp - TO BE UPDATED
    # ... other attributes unchanged
}
```

## Components and Interfaces

### 1. Migration Script (update_race_ids.py)

**Location:** `functions/migrations/update_race_ids.py`

**Purpose:** Update race_id values in DynamoDB for both SK and race_id attribute

**Key Functions:**

```python
def get_race_id_mapping():
    """
    Returns a dictionary mapping old race_id to new race_id
    
    Returns:
        dict: {old_race_id: new_race_id}
    """
    pass

def update_race_id(db, old_race_id, new_race_id):
    """
    Update a single race record with new race_id
    
    Steps:
    1. Get existing race record using PK='RACE', SK=old_race_id
    2. Delete old record
    3. Create new record with SK=new_race_id and race_id=new_race_id
    4. Preserve all other attributes
    5. Update updated_at timestamp
    
    Args:
        db: Database client
        old_race_id: Current race_id (e.g., 'M01')
        new_race_id: New race_id (e.g., 'M13')
    
    Returns:
        bool: True if successful, False otherwise
    """
    pass

def update_boat_registrations(db, old_race_id, new_race_id):
    """
    Update all boat registrations that reference old race_id
    
    Steps:
    1. Query all TEAM records with race_id=old_race_id
    2. For each boat registration:
       a. Update race_id attribute to new_race_id
       b. Update updated_at timestamp
       c. Preserve all other attributes
    3. Return count of updated registrations
    
    Args:
        db: Database client
        old_race_id: Current race_id (e.g., 'M01')
        new_race_id: New race_id (e.g., 'M13')
    
    Returns:
        int: Number of boat registrations updated
    """
    pass

def run_migration():
    """
    Main migration logic
    
    Steps:
    1. Load race_id mapping
    2. For each mapping:
       a. Check if old race exists
       b. Update race to new race_id
       c. Update all boat registrations referencing old race_id
       d. Log the changes
    3. Report summary of changes (races and boat registrations)
    """
    pass
```

**Migration Strategy:**

Since DynamoDB does not allow updating the sort key (SK) directly, we must:

**For Race Records:**
1. Read the existing race record
2. Delete the old record (with old SK)
3. Create a new record with the new SK
4. Preserve all attributes except SK and race_id

**For Boat Registration Records:**
1. Query all TEAM records with the old race_id
2. For each boat registration, use UpdateItem to change the race_id attribute
3. Preserve all other attributes (PK, SK, team_id, etc. remain unchanged)

**Safety Measures:**
- Dry-run mode to preview changes
- Confirmation prompt before execution
- Detailed logging of each update (races and boat registrations)
- Error handling to prevent partial updates
- Verification step after migration

### 2. init_config.py Updates

**Location:** `functions/init/init_config.py`

**Changes Required:**

Update the `initialize_race_definitions()` function to use new race_id values:

```python
def initialize_race_definitions(table):
    """Initialize race definitions for marathon and semi-marathon events"""
    
    # Marathon races (42km) - WITH NEW RACE IDs
    marathon_races = [
        {'race_id': 'M13', 'name': '1X SENIOR WOMAN', ...},      # was M01
        {'race_id': 'M14', 'name': '1X SENIOR MAN', ...},        # was M02
        {'race_id': 'M11', 'name': '1X MASTER A WOMAN', ...},    # was M03
        {'race_id': 'M12', 'name': '1X MASTER A MAN', ...},      # was M04
        {'race_id': 'M09', 'name': '1X MASTER B WOMAN', ...},    # was M05
        {'race_id': 'M10', 'name': '1X MASTER B MAN', ...},      # was M06
        {'race_id': 'M07', 'name': '1X MASTER C WOMAN', ...},    # unchanged
        {'race_id': 'M08', 'name': '1X MASTER C MAN', ...},      # unchanged
        {'race_id': 'M05', 'name': '1X MASTER D WOMAN', ...},    # was M09
        {'race_id': 'M06', 'name': '1X MASTER D MAN', ...},      # was M10
        {'race_id': 'M03', 'name': '1X MASTER E WOMAN', ...},    # was M11
        {'race_id': 'M04', 'name': '1X MASTER E MAN', ...},      # was M12
        {'race_id': 'M01', 'name': '1X MASTER F WOMAN', ...},    # was M13
        {'race_id': 'M02', 'name': '1X MASTER F MAN', ...},      # was M14
    ]
    
    # Semi-marathon races (21km) - WITH NEW RACE IDs
    semi_marathon_races = [
        # J16 races
        {'race_id': 'SM08', 'name': 'WOMEN-JUNIOR J16-COXED SWEEP FOUR', ...},  # was SM01A
        {'race_id': 'SM09', 'name': 'WOMEN-JUNIOR J16-COXED QUAD SCULL', ...},  # was SM01B
        # ... (all other races with new IDs)
    ]
    
    # Rest of function remains unchanged
```

### 3. Makefile Integration

**Command:** `make db-migrate MIGRATION=update_race_ids ENV=dev`

The existing Makefile db-migrate target will:
1. Validate migration file exists
2. Set environment variables (table name, AWS profile)
3. Prompt for confirmation
4. Execute the migration script
5. Report results

## Data Models

### Race ID Mapping

The migration uses a hardcoded mapping dictionary:

```python
RACE_ID_MAPPING = {
    # Marathon races (42km)
    'M01': 'M13',  # 1X SENIOR WOMAN
    'M02': 'M14',  # 1X SENIOR MAN
    'M03': 'M11',  # 1X MASTER A WOMAN
    'M04': 'M12',  # 1X MASTER A MAN
    'M05': 'M09',  # 1X MASTER B WOMAN
    'M06': 'M10',  # 1X MASTER B MAN
    'M07': 'M07',  # 1X MASTER C WOMAN (no change)
    'M08': 'M08',  # 1X MASTER C MAN (no change)
    'M09': 'M05',  # 1X MASTER D WOMAN
    'M10': 'M06',  # 1X MASTER D MAN
    'M11': 'M03',  # 1X MASTER E WOMAN
    'M12': 'M04',  # 1X MASTER E MAN
    'M13': 'M01',  # 1X MASTER F WOMAN
    'M14': 'M02',  # 1X MASTER F MAN
    
    # Semi-marathon races (21km)
    'SM01A': 'SM08',   # WOMEN-JUNIOR J16-COXED SWEEP FOUR
    'SM01B': 'SM09',   # WOMEN-JUNIOR J16-COXED QUAD SCULL
    'SM02A': 'SM11',   # MEN-JUNIOR J16-COXED SWEEP FOUR
    'SM02B': 'SM12',   # MEN-JUNIOR J16-COXED QUAD SCULL
    'SM03B': 'SM10',   # MIXED-GENDER-JUNIOR J16-COXED QUAD SCULL
    'SM04': 'SM28',    # WOMEN-JUNIOR J16-SWEEP EIGHT WITH COXSWAIN
    'SM05': 'SM29',    # MEN-JUNIOR J16-SWEEP EIGHT WITH COXSWAIN
    'SM06A': 'SM18',   # WOMEN-JUNIOR J18-SWEEP FOUR WITHOUT COXSWAIN
    'SM06B': 'SM19',   # WOMEN-JUNIOR J18-QUAD SCULL WITHOUT COXSWAIN
    'SM07A': 'SM21',   # MEN-JUNIOR J18-SWEEP FOUR WITHOUT COXSWAIN
    'SM07B': 'SM22',   # MEN-JUNIOR J18-QUAD SCULL WITHOUT COXSWAIN
    'SM08B': 'SM20',   # MIXED-GENDER-JUNIOR J18-QUAD SCULL WITHOUT COXSWAIN
    'SM10': 'SM36',    # WOMEN-JUNIOR J18-SWEEP EIGHT WITH COXSWAIN
    'SM11': 'SM38',    # MEN-JUNIOR J18-SWEEP EIGHT WITH COXSWAIN
    'SM12': 'SM37',    # MIXED-GENDER-JUNIOR J18-SWEEP EIGHT WITH COXSWAIN
    'SM13A': 'SM23',   # WOMEN-SENIOR-SWEEP FOUR WITHOUT COXSWAIN
    'SM13B': 'SM24',   # WOMEN-SENIOR-QUAD SCULL WITHOUT COXSWAIN
    'SM14A': 'SM26',   # MEN-SENIOR-SWEEP FOUR WITHOUT COXSWAIN
    'SM14B': 'SM27',   # MEN-SENIOR-QUAD SCULL WITHOUT COXSWAIN
    'SM15B': 'SM25',   # MIXED-GENDER-SENIOR-QUAD SCULL WITHOUT COXSWAIN
    'SM16': 'SM39',    # WOMEN-SENIOR-SWEEP EIGHT WITH COXSWAIN
    'SM17': 'SM41',    # MEN-SENIOR-SWEEP EIGHT WITH COXSWAIN
    'SM18': 'SM40',    # MIXED-GENDER-SENIOR-SWEEP EIGHT WITH COXSWAIN
    'SM19A': 'SM01',   # WOMEN-MASTER-COXED QUAD SCULL YOLETTE
    'SM19B': 'SM03',   # MEN-MASTER-COXED QUAD SCULL YOLETTE
    'SM19C': 'SM02',   # MIXED-GENDER-MASTER-COXED QUAD SCULL YOLETTE
    'SM20A': 'SM04',   # WOMEN-MASTER-COXED QUAD SCULL
    'SM20B': 'SM07',   # MEN-MASTER-COXED QUAD SCULL
    'SM20C': 'SM05',   # MIXED-GENDER-MASTER-COXED QUAD SCULL
    'SM21A': 'SM33',   # WOMEN-MASTER-OCTUPLE SCULL WITH COXSWAIN
    'SM21B': 'SM35',   # MEN-MASTER-OCTUPLE SCULL WITH COXSWAIN
    'SM21C': 'SM34',   # MIXED-GENDER-MASTER-OCTUPLE SCULL WITH COXSWAIN
    'SM22A': 'SM06',   # MEN-MASTER-COXED SWEEP FOUR
    'SM23A': 'SM14',   # WOMEN-MASTER-QUAD SCULL WITHOUT COXSWAIN
    'SM23B': 'SM17',   # MEN-MASTER-QUAD SCULL WITHOUT COXSWAIN
    'SM23C': 'SM15',   # MIXED-GENDER-MASTER-QUAD SCULL WITHOUT COXSWAIN
    'SM24A': 'SM16',   # MEN-MASTER-SWEEP FOUR WITHOUT COXSWAIN
    'SM24B': 'SM13',   # WOMEN-MASTER-SWEEP FOUR WITHOUT COXSWAIN
    'SM25A': 'SM30',   # MEN-MASTER-SWEEP EIGHT WITH COXSWAIN
    'SM25B': 'SM32',   # WOMEN-MASTER-SWEEP EIGHT WITH COXSWAIN
    'SM25C': 'SM31',   # MIXED-GENDER-MASTER-SWEEP EIGHT WITH COXSWAIN
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Race ID Mapping Completeness

*For any* race in the database, if it has an old race_id in the mapping, then after migration it should have the corresponding new race_id.

**Validates: Requirements 1.1, 1.2**

### Property 2: Attribute Preservation

*For any* race record, after migration all attributes except SK, race_id, and updated_at should remain unchanged.

*For any* boat registration record, after migration all attributes except race_id and updated_at should remain unchanged.

**Validates: Requirements 1.3, 1.7, 4.1, 4.4, 4.5, 4.7, 4.8, 4.9, 4.10**

### Property 3: SK and race_id Consistency

*For any* race record, the SK value should always equal the race_id attribute value.

**Validates: Requirements 4.2, 4.3**

### Property 4: Migration Idempotency

*For any* migration execution, running the migration multiple times should produce the same final state as running it once.

**Validates: Requirements 3.3**

### Property 5: No Data Loss

*For any* race in the database before migration, there should be a corresponding race after migration with the same name and attributes.

*For any* boat registration in the database before migration, there should be a corresponding boat registration after migration with the same team_id and attributes (except race_id).

**Validates: Requirements 4.1, 4.5, 4.7, 4.8, 4.10**

### Property 6: Boat Registration Referential Integrity

*For any* boat registration after migration, the race_id attribute should reference a valid race that exists in the database with the new race_id values.

**Validates: Requirements 1.6, 1.7, 4.9**

## Error Handling

### Migration Script Error Handling

1. **Race Not Found:**
   - Log warning: "Race {old_race_id} not found in database"
   - Continue with next race
   - Include in summary report

2. **DynamoDB Error:**
   - Catch boto3 exceptions
   - Log error details
   - Abort migration to prevent partial updates
   - Provide rollback instructions

3. **Validation Error:**
   - Verify new race_id doesn't already exist before creating
   - If conflict detected, log error and skip
   - Report conflicts in summary

4. **Confirmation Declined:**
   - Exit gracefully without changes
   - Display "Migration cancelled" message

5. **Boat Registration Update Error:**
   - Log error with team_id and race_id details
   - Continue with other boat registrations
   - Report failed updates in summary

### init_config.py Error Handling

The existing error handling in init_config.py will handle:
- ConditionalCheckFailedException: Race already exists (skip)
- General exceptions: Log and report to CloudFormation

## Testing Strategy

### Manual Testing

**Pre-Migration Verification:**
1. Export current database state: `make db-export ENV=dev`
2. Count races: Should be 55 total (14 marathon + 41 semi-marathon)
3. Verify race_id values match old mapping

**Post-Migration Verification:**
1. Export migrated database: `make db-export ENV=dev`
2. Verify all race_id values match new mapping
3. Verify race count remains 55
4. Verify all race names and attributes unchanged
5. Verify races sort correctly by race_id
6. Verify boat registrations reference new race_id values
7. Verify boat registration count unchanged
8. Verify all boat registration attributes unchanged (except race_id)

**init_config.py Testing:**
1. Deploy to dev environment
2. Check CloudWatch logs for initialization
3. Verify no errors during race creation
4. Export database and verify race_id values

### Rollback Procedure

If migration fails or produces incorrect results:

1. **Restore from backup:**
   ```bash
   make db-list-backups ENV=dev
   make db-restore-backup BACKUP_ARN=<arn> ENV=dev
   ```

2. **Re-run migration with fixes:**
   - Fix migration script
   - Re-run on dev
   - Verify results
   - Then run on prod

3. **Manual correction:**
   - If only a few races affected, manually update via AWS Console
   - Document changes for audit trail

## Execution Plan

### Phase 1: Preparation

1. **Create migration script**
   - Write `functions/migrations/update_race_ids.py`
   - Include race_id mapping
   - Add logging and error handling
   - Test locally with dry-run mode

2. **Update init_config.py**
   - Update marathon_races list with new race_ids
   - Update semi_marathon_races list with new race_ids
   - Verify no syntax errors

3. **Create backup**
   - Run: `make db-backup ENV=dev`
   - Run: `make db-backup ENV=prod`
   - Note backup ARNs for rollback

### Phase 2: Dev Environment Migration

1. **Export current state**
   ```bash
   cd infrastructure
   make db-export ENV=dev
   ```

2. **Run migration**
   ```bash
   cd infrastructure
   make db-migrate MIGRATION=update_race_ids ENV=dev
   ```

3. **Verify results**
   ```bash
   make db-export ENV=dev
   # Compare with expected race_id values
   ```

4. **Deploy updated init_config.py**
   ```bash
   make deploy-dev
   ```

5. **Verify deployment**
   - Check CloudWatch logs
   - Verify no errors

### Phase 3: Prod Environment Migration

1. **Export current state**
   ```bash
   cd infrastructure
   make db-export ENV=prod
   ```

2. **Run migration**
   ```bash
   cd infrastructure
   make db-migrate MIGRATION=update_race_ids ENV=prod
   ```

3. **Verify results**
   ```bash
   make db-export ENV=prod
   # Compare with expected race_id values
   ```

4. **Deploy updated init_config.py**
   ```bash
   make deploy-prod
   ```

5. **Verify deployment**
   - Check CloudWatch logs
   - Verify no errors

### Phase 4: Cleanup

1. **Delete migration script**
   ```bash
   rm functions/migrations/update_race_ids.py
   ```

2. **Document completion**
   - Update project documentation
   - Note migration date and results
   - Archive backup ARNs

## Design Decisions

### Why Delete and Recreate Instead of Update?

DynamoDB does not allow updating the sort key (SK) of an existing item. The only way to change the SK is to:
1. Delete the old item
2. Create a new item with the new SK

This is a DynamoDB limitation, not a design choice.

### Why Hardcode the Mapping?

The race_id mapping is a one-time transformation based on a specific business requirement. Hardcoding the mapping in the migration script:
- Makes the migration self-contained
- Provides clear audit trail
- Prevents accidental changes
- Simplifies execution

### Why Update init_config.py?

Updating init_config.py ensures that:
- Future deployments use correct race_ids
- Fresh databases start with correct values
- System remains consistent across environments
- No manual intervention needed for new environments

### Why Use Makefile Command?

The Makefile provides:
- Consistent execution pattern
- Environment variable management
- Confirmation prompts
- Error handling
- Integration with existing tooling
