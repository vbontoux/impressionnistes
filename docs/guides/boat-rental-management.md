# Boat Rental Management

## Overview

The boat rental system allows external club managers to request RCPM boats for the competition. RCPM members have priority access during the rental priority period, after which external clubs gain equal access.

**Spec Reference:** FR-8 (Boat Rental Management), FR-9 (Seat Rental for Multi_Club_Crews)

## For Club Managers

### Viewing Available Boats

Navigate to **Boat Rentals** from the main menu. The page displays all RCPM rental boats with:
- Boat type (skiff, four, eight)
- Boat name
- Recommended rower weight range (kg)
- Current availability status (available, requested, confirmed, paid)

Only boats with status "available" can be requested.

### Requesting a Boat

1. Browse available boats
2. Click "Request" on the desired boat
3. The system records your request and sets the boat status to "requested"
4. Other club managers cannot request the same boat while it's in "requested" status

### Rental Priority Period

- **From registration opening until 15 days before registration closure:** RCPM members have exclusive priority
- **Final 15 days:** External clubs have equal access to unreserved boats
- During the priority period, external club requests are marked as "pending"
- When the priority period expires, pending requests for unreserved boats are automatically confirmed

### Viewing Your Rentals

Confirmed boat rentals appear on the **Payment** page alongside your boat registrations. You can pay for rentals separately from crew registrations.

## For Administrators

### Managing Rental Requests

Navigate to **Admin → Boat Rentals** to view all rental boats and requests.

**Confirm a request:**
1. Find the boat with status "requested"
2. Click "Confirm"
3. Status changes to "confirmed" and the club manager is notified

**Reject a request:**
1. Find the boat with status "requested"
2. Click "Reject" (sets status back to "available")
3. The boat becomes available for other managers

### Managing Rental Boats

Administrators can create and update rental boats:
- Boat type
- Boat name
- Recommended rower weight range (text field, in kg)
- Availability status

## Pricing

### Boat Rental Fees

| Boat Type | Fee Calculation | Default |
|-----------|----------------|---------|
| Skiff (1X) | 2.5 × Participation Fee | €50 |
| Crew boats (4-, 4+, 8+) | Boat Rental fee per seat | €20/seat |

### Who Pays

- **RCPM members:** €0 (no participation fee, no rental fee)
- **External club members in own boat:** Participation Fee only (€20/seat)
- **External club members in RCPM boat:** Participation Fee + Boat Rental (€40/seat for crew boats)

### Payment Tracking

When a rental boat status changes to "paid", the system records the payment timestamp in the `paid_at` field.

## Seat Rental for Multi-Club Crews (FR-9)

When a crew contains both RCPM members and external club members:

- **RCPM members:** Pay nothing (€0)
- **External members:** Pay Participation Fee (€20) + Boat Rental fee (€20) = €40/seat

The system automatically:
1. Identifies external club members using club_affiliation detection (case-insensitive matching for "RCPM", "Port-Marly", "Port Marly")
2. Applies Boat Rental fees to external members only
3. Displays rental charges separately in payment summaries for transparency

### Payment Summary Example

```
Crew: 4+ Mixed Club (RCPM, SN Versailles)
  - 2 RCPM members:     2 × €0  = €0
  - 2 external members: 2 × €20 = €40  (Participation Fee)
  - 2 external members: 2 × €20 = €40  (Boat Rental)
  Total: €80
```

## Rental Boat Statuses

| Status | Meaning |
|--------|---------|
| `available` | Boat is available for request |
| `requested` | A club manager has requested this boat |
| `confirmed` | Admin has confirmed the rental |
| `paid` | Rental fee has been paid |

## Related Documentation

- [Terminology — Pricing](../reference/terminology.md) — Pricing definitions and examples
- [Hull Assignment](./hull-assignment.md) — Separate from boat rental (hull assignment is for crew registrations)
- [Payment History](./payment-history.md) — Payment tracking
