# Bugfix Requirements Document

## Introduction

The CrewTimer export has two formatting issues that need correction for proper compatibility with CrewTimer timing software:
1. The "Race Info" column header should be renamed to "Race Type"
2. For marathon races (42km), the Event column should display "1x Marathon" for all skiffs (instead of individual race names), and the Race Type column should display "Sprint" (instead of "Head")

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the CrewTimer export is generated THEN the system outputs a column header named "Race Info" instead of "Race Type"

1.2 WHEN a marathon race (42km) boat is exported to CrewTimer THEN the system outputs the individual race name in the Event column (e.g., "1X MASTER F WOMAN", "1X SENIOR MAN") instead of the unified "1x Marathon" value

1.3 WHEN a marathon race (42km) boat is exported to CrewTimer THEN the system outputs "Head" in the Race Type column instead of "Sprint"

### Expected Behavior (Correct)

2.1 WHEN the CrewTimer export is generated THEN the system SHALL output the column header as "Race Type" (renamed from "Race Info")

2.2 WHEN a marathon race (42km) boat is exported to CrewTimer THEN the system SHALL output "1x Marathon" in the Event column for all marathon boats regardless of their specific race category

2.3 WHEN a marathon race (42km) boat is exported to CrewTimer THEN the system SHALL output "Sprint" in the Race Type column

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a semi-marathon race (21km) boat is exported to CrewTimer THEN the system SHALL CONTINUE TO display the full translated race name in the Event column (e.g., "WOMEN-MASTER-COXED QUAD SCULL YOLETTE")

3.2 WHEN a semi-marathon race (21km) boat is exported to CrewTimer THEN the system SHALL CONTINUE TO display "Head" in the Race Type column

3.3 WHEN any boat is exported to CrewTimer THEN the system SHALL CONTINUE TO correctly populate all other columns (Event Time, Event Num, Event Abbrev, Crew, Crew Abbrev, Stroke, Bow, Status, Age, Handicap, Note)

3.4 WHEN the CrewTimer export is generated THEN the system SHALL CONTINUE TO sort races by display_order and boats by average age within each race

3.5 WHEN the CrewTimer export is generated THEN the system SHALL CONTINUE TO filter only eligible boats (complete, paid, or free status, not forfait)
