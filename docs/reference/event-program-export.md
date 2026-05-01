# Event Program Export

## Overview

The Event Program Export generates a 4-sheet Excel file for race day operations. It provides comprehensive crew member data, race schedules, crew-by-race listings, and club manager summaries suitable for printing.

**Spec Reference:** FR-22 (Event Program Export)

## Export Sheets

### Sheet 1: Crew Member List

Enhanced listing of all crew members from eligible boats with detailed personal and race information.

**Columns:**

| # | Column | Description | Example |
|---|--------|-------------|---------|
| 1 | Race # | Sequential race number based on display_order | 1, 2, 3... |
| 2 | Race Name | Full translated race name | WOMEN-MASTER-COXED QUAD SCULL YOLETTE |
| 3 | Crew # | Boat number (`[M/SM].[display_order].[sequence]`) | SM.15.1 |
| 4 | Last Name | Crew member last name | Martin |
| 5 | First Name | Crew member first name | Alice |
| 6 | Club | Crew member club affiliation | RCPM |
| 7 | Age | Crew member age at competition date | 35 |
| 8 | Gender | Crew member gender | F |
| 9 | License # | FFA license number | 123456A |
| 10 | Place in Boat | Seat position | Rower 1, Cox |
| 11 | Bow Number | Global sequential bow number | 1, 2, 3... |
| 12 | Assigned Boat | Physical boat assignment | Skiff 3 - Dock B |

**Notes:**
- When a crew member has no assigned boat, the Assigned Boat column is empty
- Assigned boat is formatted as `"boat_name - comment"` when both are available
- Sorted by race number, then crew number, then seat position

### Sheet 2: Race Schedule

Preserved from existing format. Contains race timing information.

**Columns:**
- Race number
- Race name
- Start time
- Race order

This sheet is unchanged from the previous 2-sheet export.

### Sheet 3: Crews in Races

All crews organized by race with full member details for each crew.

**Structure:**
- Grouped by race (race name as section header)
- Within each race, lists all eligible crews
- For each crew, lists all crew members with their details

**Data per crew:**
- Crew number (boat number)
- Club display (comma-separated clubs)
- Registration status
- All crew members with: name, age, gender, license, seat position

### Sheet 4: Synthesis

Club manager summary providing operational overview for race day coordination.

**Columns:**

| Column | Description | Example |
|--------|-------------|---------|
| Club Manager | Full name | Jean Dupont |
| Email | Contact email | jean@club.com |
| Club | Club affiliation | RCPM |
| Total Boats | Number of eligible boats | 5 |
| Total Crew Members | Number of crew members in eligible boats | 32 |
| Payment Balance | Outstanding balance (paid vs registered) | €0 / €-40 |

## Eligibility Rules

Only boats meeting these criteria are included in the export:

| Status | Included | Reason |
|--------|----------|--------|
| `complete` | ✅ | Registration complete, awaiting payment |
| `paid` | ✅ | Payment received |
| `free` | ✅ | Free registration (RCPM members) |
| `incomplete` | ❌ | Registration not finished |
| `forfait: true` | ❌ | Boat has forfeited |

## Numbering Logic

### Race Numbers
- Assigned sequentially based on the race's `display_order` field (1–55)
- Only races with at least one eligible boat receive a race number
- Marathon races: display_order 1–14
- Semi-marathon races: display_order 15–55

### Bow Numbers
- Assigned sequentially within each race
- Global sequential numbering across all races (1, 2, 3... continuing across races)
- Within a race, boats are ordered by average age (oldest first)

## Localization

The export supports both French and English:

| Element | English | French |
|---------|---------|--------|
| Sheet 1 name | Crew Members | Équipiers |
| Sheet 2 name | Race Schedule | Programme des courses |
| Sheet 3 name | Crews in Races | Équipages par course |
| Sheet 4 name | Synthesis | Synthèse |
| Column headers | English headers | French headers |

Language is determined by the admin's current locale setting.

## Implementation

### Backend API

**Endpoint:** `GET /admin/export/races-json`

The export reuses the existing races JSON endpoint which returns all races, boats, crew members, and system configuration.

### Frontend Formatter

**File:** `frontend/src/utils/exportFormatters/eventProgramFormatter.js`

The frontend formatter:
1. Fetches JSON data from the races export endpoint
2. Filters eligible boats (complete, paid, free; excludes forfait)
3. Assigns race numbers and bow numbers
4. Generates 4-sheet Excel file using the xlsx library
5. Applies professional formatting (bold headers, column widths, borders)
6. Triggers download

### Usage

```javascript
import { downloadEventProgram } from '@/utils/exportFormatters'

// Export with current locale
downloadEventProgram(response.data, locale.value, t)
```

## Formatting

The Excel file uses professional formatting suitable for printing:
- Bold headers with background color
- Auto-sized column widths
- Borders on all cells
- Race name sections in bold
- Page breaks between races (Sheet 3)
- Print-friendly margins

## Related Documentation

- [CrewTimer Export](./crewtimer-export.md) — Different export format for timing software
- [Terminology](./terminology.md) — Boat number format and club display
- [API Endpoints](./api-endpoints.md) — Export API endpoints
