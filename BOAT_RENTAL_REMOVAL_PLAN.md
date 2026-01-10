# Boat Rental Feature Removal Plan

**Date:** 2026-01-10
**Reason:** Boat rental feature (both old inventory-based and new request-based) will be replaced by a different approach: boat assignment with cost per seat.

**Git Tag:** `archive/boat-rental-implementation` (created before removal for historical reference)

---

## Phase 1: Git Tag ✅

- [x] Create git tag `archive/boat-rental-implementation`
- [x] Verify tag was created successfully

---

## Phase 2: Backend Lambda Functions ✅

### Old Rental System (Inventory-based) ✅
- [x] `functions/admin/create_rental_boat.py`
- [x] `functions/admin/list_rental_boats.py`
- [x] `functions/admin/update_rental_boat.py`
- [x] `functions/admin/delete_rental_boat.py`
- [x] `functions/rental/list_available_rental_boats.py`
- [x] `functions/rental/request_rental_boat.py`

### New Rental System (Request-based) ✅
- [x] `functions/rental/create_rental_request.py`
- [x] `functions/rental/get_my_rental_requests.py`
- [x] `functions/rental/cancel_rental_request.py`
- [x] `functions/rental/get_rentals_for_payment.py`
- [x] `functions/admin/accept_rental_request.py`
- [x] `functions/admin/reject_rental_request.py`
- [x] `functions/admin/update_assignment_details.py`
- [x] `functions/admin/list_rental_requests.py`
- [x] `functions/admin/reset_rental_request.py`

### Shared Utilities ✅
- [x] `functions/shared/rental_request_state.py`
- [x] `functions/layer/python/rental_request_state.py`

---

## Phase 3: Backend Tests ✅

### Integration Tests ✅
- [x] All test_rental_request_*.py files deleted

### E2E Tests ✅
- [x] `tests/e2e/test_admin_rental_workflow.py`
- [x] `tests/e2e/test_team_manager_rental_workflow.py`

---

## Phase 4: Infrastructure ✅

### API Stack ✅
- [x] Removed rental Lambda function definitions from `infrastructure/stacks/api_stack.py`
- [x] Removed all rental API Gateway routes

---

## Phase 5: Frontend Views & Components ✅

### Views ✅
- [x] `frontend/src/views/BoatRentalPage.vue`
- [x] `frontend/src/views/admin/AdminBoatInventory.vue`

### Components ✅
- [x] `frontend/src/components/RentalPaymentCard.vue`

### Utilities ✅
- [x] `frontend/src/utils/rentalPricing.js`

### Router ✅
- [x] Removed rental routes from `frontend/src/router/index.js`

---

## Phase 6: Frontend Services & Stores ✅

### API Client ✅
- [x] Removed all rental methods from `frontend/src/services/apiClient.js`

### Payment Store ✅
- [x] Removed rental logic from `frontend/src/stores/paymentStore.js`

### Payment View ✅
- [x] Removed rental references from `frontend/src/views/Payment.vue`

---

## Phase 7: Frontend Translations 🔄

Translation cleanup can be done later as it won't break functionality.

---

## Phase 8: Payment Integration Cleanup ✅

### Payment Functions ✅
- [x] Updated `functions/payment/confirm_payment_webhook.py` - deprecated rental handling
- [x] Updated `functions/payment/create_payment_intent.py` - deprecated rental handling

---

## Phase 9: Documentation & Specs ✅

### Specs ✅
- [x] `.kiro/specs/boat-rental-refactoring/` (entire directory deleted)

---

## Phase 10: Admin Dashboard & Event Config ✅

- [x] Removed rental stats from `frontend/src/views/admin/AdminDashboard.vue`
- [x] Removed rental settings from `frontend/src/views/admin/AdminEventConfig.vue`
- [x] Removed boat inventory link from admin dashboard

---

## Phase 11: Verification 🔄

- [ ] Run backend tests: `cd infrastructure && make test`
- [ ] Build frontend: `cd frontend && npm run build`
- [ ] Search codebase for orphaned references
- [ ] Review git diff
- [ ] Deploy to dev environment and verify

---

## Phase 12: Git Commit 🔄

- [ ] Commit all changes with message: "Remove boat rental feature (both old and new implementations)"
- [ ] Reference the archive tag in commit message

---

## Summary

**Completed:**
- ✅ Git tag created: `archive/boat-rental-implementation`
- ✅ All backend Lambda functions deleted (17 files)
- ✅ All backend tests deleted (14 files)
- ✅ API Gateway routes removed
- ✅ Payment functions updated to deprecate rental handling
- ✅ All frontend views and components deleted (4 files)
- ✅ Router updated (rental routes removed)
- ✅ API client cleaned (all rental methods removed)
- ✅ Payment store cleaned
- ✅ Payment view cleaned
- ✅ Admin dashboard cleaned
- ✅ Admin event config cleaned

**Remaining (Optional):**
- Translation strings cleanup (won't break functionality)
- Final testing and deployment

---

## Phase 2: Backend Lambda Functions

### Old Rental System (Inventory-based)
- [ ] `functions/admin/create_rental_boat.py`
- [ ] `functions/admin/list_rental_boats.py`
- [ ] `functions/admin/update_rental_boat.py`
- [ ] `functions/admin/delete_rental_boat.py`
- [ ] `functions/rental/list_available_rental_boats.py`
- [ ] `functions/rental/request_rental_boat.py`

### New Rental System (Request-based)
- [ ] `functions/rental/create_rental_request.py`
- [ ] `functions/rental/get_my_rental_requests.py`
- [ ] `functions/rental/cancel_rental_request.py`
- [ ] `functions/rental/get_rentals_for_payment.py`
- [ ] `functions/admin/accept_rental_request.py`
- [ ] `functions/admin/reject_rental_request.py`
- [ ] `functions/admin/update_assignment_details.py`
- [ ] `functions/admin/list_rental_requests.py`
- [ ] `functions/admin/reset_rental_request.py` (if exists)

### Shared Utilities
- [ ] `functions/shared/rental_request_state.py`
- [ ] Check and remove rental-specific code from `functions/shared/validation.py`

---

## Phase 3: Backend Tests

### Integration Tests
- [ ] `tests/integration/test_rental_request_validation.py`
- [ ] `tests/integration/test_rental_request_pricing.py`
- [ ] `tests/integration/test_rental_request_creation.py`
- [ ] `tests/integration/test_rental_request_listing.py`
- [ ] `tests/integration/test_rental_request_admin_listing.py`
- [ ] `tests/integration/test_rental_request_acceptance.py`
- [ ] `tests/integration/test_rental_request_assignment_update.py`
- [ ] `tests/integration/test_rental_request_cancellation.py`
- [ ] `tests/integration/test_rental_request_rejection.py`
- [ ] `tests/integration/test_rental_request_payment.py`
- [ ] `tests/integration/test_rental_request_state_transitions.py`
- [ ] `tests/integration/test_rental_api.py` (if exists)

### E2E Tests
- [ ] `tests/e2e/test_admin_rental_workflow.py`
- [ ] `tests/e2e/test_team_manager_rental_workflow.py`

---

## Phase 4: Infrastructure

### Scripts
- [ ] `infrastructure/delete_old_rental_boats.py`
- [ ] Check `functions/migrations/` for rental-related migrations

### API Stack
- [ ] Remove rental endpoints from `infrastructure/stacks/api_stack.py`
  - [ ] `/rental/request` (POST)
  - [ ] `/rental/my-requests` (GET)
  - [ ] `/rental/requests-for-payment` (GET)
  - [ ] `/rental/request/{id}` (DELETE)
  - [ ] `/admin/rental-requests` (GET)
  - [ ] `/admin/rental-requests/{id}/accept` (PUT)
  - [ ] `/admin/rental-requests/{id}/assignment` (PUT)
  - [ ] `/admin/rental-requests/{id}` (DELETE)
  - [ ] Any old inventory endpoints

---

## Phase 5: Frontend Views & Components

### Views
- [ ] `frontend/src/views/BoatRentalPage.vue` (or similar - find actual name)
- [ ] `frontend/src/views/admin/AdminBoatInventory.vue`

### Components
- [ ] Search for rental-specific components and remove

### Router
- [ ] Remove rental routes from `frontend/src/router/index.js`

---

## Phase 6: Frontend Services & Stores

### API Client
- [ ] Remove rental methods from `frontend/src/services/apiClient.js`
  - [ ] createRentalRequest
  - [ ] getMyRentalRequests
  - [ ] cancelRentalRequest
  - [ ] getRentalsForPayment
  - [ ] listRentalRequests (admin)
  - [ ] acceptRentalRequest (admin)
  - [ ] updateAssignmentDetails (admin)
  - [ ] rejectRentalRequest (admin)

### Payment Store
- [ ] Remove rental logic from `frontend/src/stores/paymentStore.js`

---

## Phase 7: Frontend Translations

### English
- [ ] Remove rental strings from `frontend/src/locales/en.json`

### French
- [ ] Remove rental strings from `frontend/src/locales/fr.json`

---

## Phase 8: Payment Integration Cleanup

### Payment Functions
- [ ] Update `functions/payment/confirm_payment_webhook.py` - remove RENTAL_REQUEST handling
- [ ] Update `functions/payment/create_payment_intent.py` - remove rental pricing logic

---

## Phase 9: Documentation & Specs

### Specs (Complete Directories)
- [ ] `.kiro/specs/boat-rental-refactoring/` (entire directory)

### Docs
- [ ] Search `docs/` for rental-related guides and remove

### Keep Unchanged
- ✅ `.kiro/specs/impressionnistes-registration-system/requirements.md` (no changes)

---

## Phase 10: Database Cleanup

### DynamoDB
- [ ] Delete all RENTAL_BOAT records (if any)
- [ ] Delete all RENTAL_REQUEST records (if any)
- [ ] Document cleanup script or manual process

---

## Phase 11: Verification

- [ ] Run backend tests: `cd infrastructure && make test`
- [ ] Build frontend: `cd frontend && npm run build`
- [ ] Search codebase for orphaned references:
  - [ ] Search for "rental" (case-insensitive)
  - [ ] Search for "RENTAL_BOAT"
  - [ ] Search for "RENTAL_REQUEST"
  - [ ] Search for "rental_request"
- [ ] Review git diff to ensure nothing critical was removed
- [ ] Deploy to dev environment and verify

---

## Phase 12: Git Commit

- [ ] Commit all changes with message: "Remove boat rental feature (both old and new implementations)"
- [ ] Reference the archive tag in commit message

---

## Notes

- The boat rental feature will be replaced by a boat assignment system with cost per seat
- All rental code is preserved in git tag `archive/boat-rental-implementation`
- Main requirements document remains unchanged as requested
- New boat rental requirements will be created separately when the new approach is designed

