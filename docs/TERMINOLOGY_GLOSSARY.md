# Terminology Glossary

## Purpose
This document defines the standard terminology used throughout the Course des Impressionnistes registration system. It provides a mapping between internal code names and user-facing terms to ensure consistency across documentation, UI, and communication.

---

## Pricing Terminology

### Internal Code → User-Facing Term → Definition

| Internal Code Name | User-Facing Term (EN) | User-Facing Term (FR) | Definition |
|-------------------|----------------------|----------------------|------------|
| `base_seat_price` | **Participation Fee** | **Frais de participation** | Cost per team member to participate in the event. This covers registration, insurance, and organizational costs. Applied to external club members only (RCPM members = €0). |
| `rental_price` / `boat_rental_price_crew` | **Boat Rental (per seat)** | **Location bateau (par place)** | Additional cost per seat for non-RCPM members using an RCPM-owned boat. This is the equipment rental fee for using a physical seat in a club boat. |
| `boat_rental_multiplier_skiff` | **Skiff Rental Multiplier** | **Multiplicateur location skiff** | Multiplier applied to participation fee for single-person boats (skiffs). Default: 2.5x the participation fee. |

---

## Key Concepts

### Participation Fee (`base_seat_price`)
- **What it covers**: Event registration, insurance, organization, timing services
- **Who pays**: External club members only
- **Who doesn't pay**: RCPM members (€0)
- **Default value**: €20 per person
- **Applied to**: All crew member registrations

### Boat Rental Fee (`rental_price`)
- **What it covers**: Use of RCPM-owned boat equipment (hull, oars, etc.)
- **Who pays**: Non-RCPM members using RCPM boats
- **Who doesn't pay**: RCPM members, or anyone using their own boat
- **Default value**: €20 per seat (crew boats), €50 for skiffs (2.5x multiplier)
- **Applied to**: Physical seats in RCPM boats assigned to crews

---

## Usage Guidelines

### In Code
- Keep existing variable names (`base_seat_price`, `rental_price`, etc.)
- Add clarifying comments where pricing logic is implemented
- Use descriptive names for new fields

### In UI/Documentation
- Always use user-facing terms: "Participation Fee" and "Boat Rental"
- Be explicit about what each fee covers
- Clearly state who pays and who doesn't

### In Requirements/Specs
- Use user-facing terms in narrative descriptions
- Include internal code names in parentheses when referencing implementation
- Example: "The Participation Fee (`base_seat_price`) is charged per external club member..."

---

## Examples

### Pricing Scenarios

**Scenario 1: RCPM crew in RCPM boat**
- Participation Fee: €0 (all RCPM members)
- Boat Rental: €0 (RCPM members don't pay rental)
- **Total: €0**

**Scenario 2: External club crew (4 rowers) in their own boat**
- Participation Fee: 4 × €20 = €80
- Boat Rental: €0 (using own boat)
- **Total: €80**

**Scenario 3: External club crew (4 rowers) in RCPM boat**
- Participation Fee: 4 × €20 = €80
- Boat Rental: 4 × €20 = €80
- **Total: €160**

**Scenario 4: Mixed crew (2 RCPM + 2 external) in RCPM boat**
- Participation Fee: 2 × €20 = €40 (only external members)
- Boat Rental: 2 × €20 = €40 (only external members)
- **Total: €80**

**Scenario 5: External club member in skiff (RCPM boat)**
- Participation Fee: 1 × €20 = €20
- Boat Rental: 1 × €50 = €50 (2.5x multiplier for skiffs)
- **Total: €70**

---

## Related Documentation

- [Requirements](.kiro/specs/impressionnistes-registration-system/requirements.md)
- [Design](.kiro/specs/impressionnistes-registration-system/design.md)
- [Pricing Configuration Guide](guides/admin/pricing-configuration.md) *(if exists)*

---

## Changelog

- **2026-01-10**: Initial glossary created to clarify pricing terminology
