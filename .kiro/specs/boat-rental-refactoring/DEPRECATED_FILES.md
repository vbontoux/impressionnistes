# Deprecated Rental Boat Files

This document tracks files from the old inventory-based rental system that are being replaced by the new request-based system.

## Status: Deprecated (Pending Removal After Migration)

These files are part of the old RENTAL_BOAT inventory system and will be removed once the migration to RENTAL_REQUEST is complete.

### Admin Functions (Old Inventory Management)

| File | Purpose | Replacement |
|------|---------|-------------|
| `functions/admin/create_rental_boat.py` | Create rental boat inventory | Admins now accept requests and provide assignment details |
| `functions/admin/list_rental_boats.py` | List rental boat inventory | `functions/admin/list_rental_requests.py` |
| `functions/admin/update_rental_boat.py` | Update rental boat | `functions/admin/accept_rental_request.py` and `functions/admin/update_assignment_details.py` |
| `functions/admin/delete_rental_boat.py` | Delete rental boat | `functions/admin/reject_rental_request.py` |

### Team Manager Functions (Old Inventory Browsing)

| File | Purpose | Replacement |
|------|---------|-------------|
| `functions/rental/list_available_rental_boats.py` | Browse available boats | Team managers create requests directly |
| `functions/rental/request_rental_boat.py` | Request from inventory | `functions/rental/create_rental_request.py` |

### Other Files Affected

| File | Status | Notes |
|------|--------|-------|
| `functions/rental/cancel_rental_request.py` | ✅ Updated | Updated to use RENTAL_REQUEST model (Task 8) |
| `functions/rental/get_rentals_for_payment.py` | ✅ Updated | Updated to use RENTAL_REQUEST instead of RENTAL_BOAT (Task 11.1) |
| `functions/payment/confirm_payment_webhook.py` | ✅ Updated | Updated to handle RENTAL_REQUEST instead of RENTAL_BOAT (Task 11.2) |
| `functions/payment/create_payment_intent.py` | ✅ Updated | Updated to handle RENTAL_REQUEST instead of RENTAL_BOAT (Task 11.2) |
| `tests/integration/test_rental_api.py` | ⚠️ Partially Updated | Old inventory tests marked as skipped, new request tests active |

## API Endpoints to be Deprecated

According to the design document, these endpoints will be removed:

| Method | Endpoint | Replacement |
|--------|----------|-------------|
| POST | `/admin/rental-boats` | N/A - Admins accept requests instead |
| GET | `/admin/rental-boats` | GET `/admin/rental-requests` |
| PUT | `/admin/rental-boats/{id}` | PUT `/admin/rental-requests/{id}/accept` or `/admin/rental-requests/{id}/assignment` |
| DELETE | `/admin/rental-boats/{id}` | DELETE `/admin/rental-requests/{id}` |
| GET | `/rental/boats` | N/A - Team managers create requests directly |
| POST | `/rental/request` | POST `/rental/request` (updated implementation) |

## Migration Plan

1. ✅ **Phase 1**: Create new RENTAL_REQUEST endpoints (Tasks 1-4)
2. **Phase 2**: Update payment integration (Task 11)
3. **Phase 3**: Run data migration script (Task 18)
4. **Phase 4**: Update frontend to use new endpoints (Tasks 15-17)
5. **Phase 5**: Remove old RENTAL_BOAT endpoints and files
6. **Phase 6**: Clean up deprecated code

## Removal Checklist

Before removing these files, ensure:
- [ ] All RENTAL_BOAT records migrated to RENTAL_REQUEST
- [ ] Frontend updated to use new endpoints
- [ ] API Gateway routes updated
- [ ] No references to old endpoints in documentation
- [ ] Old Lambda functions removed from CDK stack
- [ ] Database verified to have no remaining RENTAL_BOAT records

## References

- Design Document: `.kiro/specs/boat-rental-refactoring/design.md`
- Requirements: `.kiro/specs/boat-rental-refactoring/requirements.md`
- Tasks: `.kiro/specs/boat-rental-refactoring/tasks.md`
