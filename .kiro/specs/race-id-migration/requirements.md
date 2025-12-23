# Requirements Document: Race ID Migration

## Introduction

This specification defines the requirements for migrating race_id values in the DynamoDB database to enable proper sorting during exports. The current race_id values do not follow a logical order for export purposes, and need to be reorganized to group races by age category, gender, and boat type.

## Glossary

- **Race**: A competition category defined by distance, boat type, age category, gender category, and master category
- **race_id**: The unique identifier for a race (e.g., M01, SM01A)
- **SK (Sort Key)**: The DynamoDB sort key, which is the race_id
- **Migration**: A one-time database transformation script
- **init_config.py**: The Lambda function that initializes race definitions during deployment
- **Export**: CSV export of race data for reporting and analysis

## Requirements

### Requirement 1: Update Race IDs in Database

**User Story:** As a system administrator, I want to update race_id values in the database, so that races are properly ordered during exports.

#### Acceptance Criteria

1. WHEN the migration runs on dev environment, THE System SHALL update all race records with new race_id values according to the mapping
2. WHEN the migration runs on prod environment, THE System SHALL update all race records with new race_id values according to the mapping
3. WHEN a race_id is updated, THE System SHALL preserve all other race attributes (name, boat_type, age_category, gender_category, etc.)
4. WHEN the migration completes, THE System SHALL report the number of races updated successfully
5. IF a race_id does not exist in the database, THEN THE System SHALL log a warning and continue with other races
6. WHEN the migration runs, THE System SHALL update all boat registration (TEAM) records that reference old race_id values
7. WHEN a boat registration race_id is updated, THE System SHALL preserve all other boat registration attributes
8. WHEN the migration completes, THE System SHALL report the number of boat registrations updated successfully

### Requirement 2: Update init_config.py

**User Story:** As a developer, I want the init_config.py to use the new race_id values, so that future deployments create races with the correct IDs.

#### Acceptance Criteria

1. WHEN init_config.py is updated, THE System SHALL use the new race_id values for all marathon races (42km)
2. WHEN init_config.py is updated, THE System SHALL use the new race_id values for all semi-marathon races (21km)
3. WHEN init_config.py runs on a fresh database, THE System SHALL create races with the new race_id values
4. WHEN init_config.py runs on an existing database, THE System SHALL skip races that already exist (idempotent behavior)

### Requirement 3: Create Migration Script

**User Story:** As a system administrator, I want a migration script that can be run via Makefile, so that I can safely migrate both dev and prod environments.

#### Acceptance Criteria

1. WHEN the migration script is created, THE System SHALL follow the migration template from functions/migrations/README.md
2. WHEN the migration is executed, THE System SHALL use the Makefile command: `make db-migrate MIGRATION=update_race_ids ENV=dev`
3. WHEN the migration runs, THE System SHALL prompt for confirmation before making changes
4. WHEN the migration runs, THE System SHALL log each race_id update for audit purposes
5. WHEN the migration encounters an error, THE System SHALL handle it gracefully and report the issue

### Requirement 4: Preserve Data Integrity

**User Story:** As a system administrator, I want to ensure no data is lost during migration, so that all race information and boat registrations remain intact.

#### Acceptance Criteria

1. WHEN a race record is updated, THE System SHALL preserve the PK (RACE) value
2. WHEN a race record is updated, THE System SHALL update the SK to the new race_id
3. WHEN a race record is updated, THE System SHALL update the race_id attribute to match the new SK
4. WHEN a race record is updated, THE System SHALL preserve all GSI keys (GSI2PK, GSI2SK)
5. WHEN a race record is updated, THE System SHALL preserve all other attributes (name, boat_type, distance, etc.)
6. WHEN a race record is updated, THE System SHALL update the updated_at timestamp
7. WHEN a boat registration is updated, THE System SHALL preserve the PK (TEAM) value
8. WHEN a boat registration is updated, THE System SHALL preserve the SK (team_id) value
9. WHEN a boat registration is updated, THE System SHALL update only the race_id attribute
10. WHEN a boat registration is updated, THE System SHALL preserve all other attributes (team_name, members, payment_status, etc.)
11. WHEN a boat registration is updated, THE System SHALL update the updated_at timestamp

### Requirement 5: Migration Execution Plan

**User Story:** As a system administrator, I want a clear execution plan, so that I can safely migrate both environments without errors.

#### Acceptance Criteria

1. WHEN the migration plan is created, THE System SHALL define steps for dev environment migration
2. WHEN the migration plan is created, THE System SHALL define steps for prod environment migration
3. WHEN the migration plan is created, THE System SHALL include verification steps after each migration
4. WHEN the migration plan is created, THE System SHALL include rollback procedures in case of failure
5. WHEN the migration is complete, THE System SHALL include steps to deploy updated init_config.py

## Race ID Mapping

### Marathon Races (42km)

| Old race_id | New race_id | Race Name |
|-------------|-------------|-----------|
| M01 | M13 | 1X SENIOR WOMAN |
| M02 | M14 | 1X SENIOR MAN |
| M03 | M11 | 1X MASTER A WOMAN |
| M04 | M12 | 1X MASTER A MAN |
| M05 | M09 | 1X MASTER B WOMAN |
| M06 | M10 | 1X MASTER B MAN |
| M07 | M07 | 1X MASTER C WOMAN (no change) |
| M08 | M08 | 1X MASTER C MAN (no change) |
| M09 | M05 | 1X MASTER D WOMAN |
| M10 | M06 | 1X MASTER D MAN |
| M11 | M03 | 1X MASTER E WOMAN |
| M12 | M04 | 1X MASTER E MAN |
| M13 | M01 | 1X MASTER F WOMAN |
| M14 | M02 | 1X MASTER F MAN |

### Semi-Marathon Races (21km)

| Old race_id | New race_id | Race Name |
|-------------|-------------|-----------|
| SM01A | SM08 | WOMEN-JUNIOR J16-COXED SWEEP FOUR |
| SM01B | SM09 | WOMEN-JUNIOR J16-COXED QUAD SCULL |
| SM02A | SM11 | MEN-JUNIOR J16-COXED SWEEP FOUR |
| SM02B | SM12 | MEN-JUNIOR J16-COXED QUAD SCULL |
| SM03B | SM10 | MIXED-GENDER-JUNIOR J16-COXED QUAD SCULL |
| SM04 | SM28 | WOMEN-JUNIOR J16-SWEEP EIGHT WITH COXSWAIN |
| SM05 | SM29 | MEN-JUNIOR J16-SWEEP EIGHT WITH COXSWAIN |
| SM06A | SM18 | WOMEN-JUNIOR J18-SWEEP FOUR WITHOUT COXSWAIN |
| SM06B | SM19 | WOMEN-JUNIOR J18-QUAD SCULL WITHOUT COXSWAIN |
| SM07A | SM21 | MEN-JUNIOR J18-SWEEP FOUR WITHOUT COXSWAIN |
| SM07B | SM22 | MEN-JUNIOR J18-QUAD SCULL WITHOUT COXSWAIN |
| SM08B | SM20 | MIXED-GENDER-JUNIOR J18-QUAD SCULL WITHOUT COXSWAIN |
| SM10 | SM36 | WOMEN-JUNIOR J18-SWEEP EIGHT WITH COXSWAIN |
| SM11 | SM38 | MEN-JUNIOR J18-SWEEP EIGHT WITH COXSWAIN |
| SM12 | SM37 | MIXED-GENDER-JUNIOR J18-SWEEP EIGHT WITH COXSWAIN |
| SM13A | SM23 | WOMEN-SENIOR-SWEEP FOUR WITHOUT COXSWAIN |
| SM13B | SM24 | WOMEN-SENIOR-QUAD SCULL WITHOUT COXSWAIN |
| SM14A | SM26 | MEN-SENIOR-SWEEP FOUR WITHOUT COXSWAIN |
| SM14B | SM27 | MEN-SENIOR-QUAD SCULL WITHOUT COXSWAIN |
| SM15B | SM25 | MIXED-GENDER-SENIOR-QUAD SCULL WITHOUT COXSWAIN |
| SM16 | SM39 | WOMEN-SENIOR-SWEEP EIGHT WITH COXSWAIN |
| SM17 | SM41 | MEN-SENIOR-SWEEP EIGHT WITH COXSWAIN |
| SM18 | SM40 | MIXED-GENDER-SENIOR-SWEEP EIGHT WITH COXSWAIN |
| SM19A | SM01 | WOMEN-MASTER-COXED QUAD SCULL YOLETTE |
| SM19B | SM03 | MEN-MASTER-COXED QUAD SCULL YOLETTE |
| SM19C | SM02 | MIXED-GENDER-MASTER-COXED QUAD SCULL YOLETTE |
| SM20A | SM04 | WOMEN-MASTER-COXED QUAD SCULL |
| SM20B | SM07 | MEN-MASTER-COXED QUAD SCULL |
| SM20C | SM05 | MIXED-GENDER-MASTER-COXED QUAD SCULL |
| SM21A | SM33 | WOMEN-MASTER-OCTUPLE SCULL WITH COXSWAIN |
| SM21B | SM35 | MEN-MASTER-OCTUPLE SCULL WITH COXSWAIN |
| SM21C | SM34 | MIXED-GENDER-MASTER-OCTUPLE SCULL WITH COXSWAIN |
| SM22A | SM06 | MEN-MASTER-COXED SWEEP FOUR |
| SM23A | SM14 | WOMEN-MASTER-QUAD SCULL WITHOUT COXSWAIN |
| SM23B | SM17 | MEN-MASTER-QUAD SCULL WITHOUT COXSWAIN |
| SM23C | SM15 | MIXED-GENDER-MASTER-QUAD SCULL WITHOUT COXSWAIN |
| SM24A | SM16 | MEN-MASTER-SWEEP FOUR WITHOUT COXSWAIN |
| SM24B | SM13 | WOMEN-MASTER-SWEEP FOUR WITHOUT COXSWAIN |
| SM25A | SM30 | MEN-MASTER-SWEEP EIGHT WITH COXSWAIN |
| SM25B | SM32 | WOMEN-MASTER-SWEEP EIGHT WITH COXSWAIN |
| SM25C | SM31 | MIXED-GENDER-MASTER-SWEEP EIGHT WITH COXSWAIN |
