# License Verification Persistence - Design

## Overview

This document describes the technical design for persisting license verification results to the database, enabling both automatic verification via FFAviron and manual verification as a fallback.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Vue.js)                        │
├─────────────────────────────────────────────────────────────┤
│  AdminLicenseChecker.vue                                     │
│  - Check licenses (existing)                                 │
│  - Mark as Valid/Invalid (new)                              │
│  - Save Verification Results (new)                          │
│  - Display verification status from DB (new)                │
├─────────────────────────────────────────────────────────────┤
│  CrewMemberList.vue (Team Manager)                          │
│  - Display verification status (new)                        │
│  - Read-only view                                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (AWS Lambda)                        │
├─────────────────────────────────────────────────────────────┤
│  New Endpoints:                                             │
│  - PATCH /admin/crew-members/{id}/license-verification     │
│  - POST /admin/crew-members/bulk-license-verification      │
│                                                             │
│  Modified Endpoints:                                        │
│  - GET /admin/crew-members (include verification fields)   │
│  - GET /crew-members (include verification fields)         │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ AWS SDK
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Database (DynamoDB)                         │
├─────────────────────────────────────────────────────────────┤
│  Crew Member Items (Extended Schema):                       │
│  - license_verification_status                              │
│  - license_verification_date                                │
│  - license_verification_details                             │
│  - license_verified_by                                      │
└─────────────────────────────────────────────────────────────┘
```

## Data Model

### Crew Member Schema Extension

No migration needed - DynamoDB is schema-less. New fields will be added on update.

```python
crew_member_item = {
    # Existing fields
    'PK': 'TEAM#{team_manager_id}',
    'SK': 'CREW#{crew_member_id}',
    'crew_member_id': 'uuid',
    'first_name': 'string',
    'last_name': 'string',
    # ... other existing fields ...
    
    # New verification fields
    'license_verification_status': 'verified_valid' | 'verified_invalid' | 
                                   'manually_verified_valid' | 'manually_verified_invalid' | None,
    'license_verification_date': '2026-01-27T10:30:00Z' | None,
    'license_verification_details': 'Valid: John Doe - 123456 - Active - Compétition' | None,
    'license_verified_by': 'admin_user_id' | None
}
```

### Verification Status Values


| Status | Description | Set By |
|--------|-------------|--------|
| `null` | Not verified | Default |
| `verified_valid` | Automatically verified as valid via FFAviron | Automatic check |
| `verified_invalid` | Automatically verified as invalid via FFAviron | Automatic check |
| `manually_verified_valid` | Manually marked as valid by admin | Manual action |
| `manually_verified_invalid` | Manually marked as invalid by admin | Manual action |

## Backend Implementation

### New Lambda Functions

#### 1. Update License Verification (Single)
**File**: `functions/admin/update_crew_member_license_verification.py`

**Purpose**: Update verification status for a single crew member

**Handler**: `lambda_handler(event, context)`

**Decorators**:
- `@handle_exceptions`
- `@require_admin`
- `@require_permission('verify_crew_member_license')`

**Request**:
```json
PATCH /admin/crew-members/{crew_member_id}/license-verification
{
  "team_manager_id": "uuid",
  "status": "verified_valid",
  "details": "Valid: John Doe - 123456 - Active - Compétition"
}
```

**Logic**:
1. Validate request body
2. Check admin has permission
3. Verify crew member exists
4. Update crew member with verification fields
5. Set `license_verified_by` to admin user ID
6. Set `license_verification_date` to current timestamp
7. Return updated crew member

**Response**:
```json
{
  "crew_member_id": "uuid",
  "license_verification_status": "verified_valid",
  "license_verification_date": "2026-01-27T10:30:00Z",
  "license_verified_by": "admin_user_id",
  "license_verification_details": "Valid: John Doe - 123456 - Active - Compétition"
}
```

#### 2. Bulk License Verification
**File**: `functions/admin/bulk_update_license_verification.py`

**Purpose**: Update verification status for multiple crew members

**Handler**: `lambda_handler(event, context)`

**Decorators**:
- `@handle_exceptions`
- `@require_admin`
- `@require_permission('verify_crew_member_license')`

**Request**:
```json
POST /admin/crew-members/bulk-license-verification
{
  "verifications": [
    {
      "crew_member_id": "uuid1",
      "team_manager_id": "uuid",
      "status": "verified_valid",
      "details": "Valid: John Doe - 123456 - Active - Compétition"
    },
    {
      "crew_member_id": "uuid2",
      "team_manager_id": "uuid",
      "status": "verified_invalid",
      "details": "Invalid: Jane Smith - 789012 - Inactive - Loisir"
    }
  ]
}
```

**Logic**:
1. Validate request body
2. Check admin has permission
3. For each verification:
   - Verify crew member exists
   - Update crew member with verification fields
   - Track success/failure
4. Return summary with results

**Response**:
```json
{
  "success_count": 1,
  "failure_count": 1,
  "results": [
    {
      "crew_member_id": "uuid1",
      "success": true
    },
    {
      "crew_member_id": "uuid2",
      "success": false,
      "error": "Crew member not found"
    }
  ]
}
```

### Modified Lambda Functions

#### 1. List All Crew Members (Admin)
**File**: `functions/admin/admin_list_all_crew_members.py`

**Changes**: Include verification fields in response

**Response** (modified):
```json
{
  "crew_members": [
    {
      "crew_member_id": "uuid",
      "first_name": "John",
      "last_name": "Doe",
      // ... existing fields ...
      "license_verification_status": "verified_valid",
      "license_verification_date": "2026-01-27T10:30:00Z",
      "license_verified_by": "admin_user_id",
      "license_verification_details": "Valid: John Doe - 123456 - Active - Compétition"
    }
  ]
}
```

#### 2. List Crew Members (Team Manager)
**File**: `functions/crew/list_crew_members.py`

**Changes**: Include verification fields in response (same as admin)

### Permission Configuration

Add new permission to permission matrix:

```python
'verify_crew_member_license': {
    'description': 'Verify crew member rowing licenses',
    'resource_type': 'crew_member',
    'roles': {
        'admin': {
            'allowed': True,
            'phases': ['all']
        },
        'team_manager': {
            'allowed': False,
            'phases': []
        }
    }
}
```

## Frontend Implementation

### AdminLicenseChecker.vue Changes

#### New State Variables
```javascript
const saving = ref(false)
const saveError = ref('')
```

#### New Computed Properties
```javascript
// Check if any selected members have verification results to save
const hasUnsavedResults = computed(() => {
  return Array.from(selectedMembers.value).some(id => {
    const member = crewMembers.value.find(m => m.crew_member_id === id)
    return member && member._licenseStatus && !member.license_verification_status
  })
})
```

#### New Methods

**1. Mark Selected as Valid**
```javascript
const markSelectedAsValid = async () => {
  if (selectedCount.value === 0) return
  
  const confirmed = await confirm({
    title: t('admin.licenseChecker.markValidTitle'),
    message: t('admin.licenseChecker.markValidMessage', { count: selectedCount.value })
  })
  
  if (!confirmed) return
  
  await bulkUpdateVerification('manually_verified_valid')
}
```

**2. Mark Selected as Invalid**
```javascript
const markSelectedAsInvalid = async () => {
  if (selectedCount.value === 0) return
  
  const confirmed = await confirm({
    title: t('admin.licenseChecker.markInvalidTitle'),
    message: t('admin.licenseChecker.markInvalidMessage', { count: selectedCount.value })
  })
  
  if (!confirmed) return
  
  await bulkUpdateVerification('manually_verified_invalid')
}
```

**3. Save Verification Results**
```javascript
const saveVerificationResults = async () => {
  if (selectedCount.value === 0) return
  
  const selectedWithResults = Array.from(selectedMembers.value)
    .map(id => crewMembers.value.find(m => m.crew_member_id === id))
    .filter(m => m && m._licenseStatus)
  
  if (selectedWithResults.length === 0) {
    errorMessage.value = t('admin.licenseChecker.noResultsToSave')
    return
  }
  
  const verifications = selectedWithResults.map(crew => ({
    crew_member_id: crew.crew_member_id,
    team_manager_id: crew.team_manager_id,
    status: crew._licenseStatus === 'valid' ? 'verified_valid' : 'verified_invalid',
    details: crew._licenseDetails
  }))
  
  await bulkUpdateVerification(null, verifications)
}
```

**4. Bulk Update Verification (Helper)**
```javascript
const bulkUpdateVerification = async (manualStatus = null, verifications = null) => {
  saving.value = true
  saveError.value = ''
  
  try {
    let payload
    
    if (manualStatus) {
      // Manual verification
      const selectedCrew = Array.from(selectedMembers.value)
        .map(id => crewMembers.value.find(m => m.crew_member_id === id))
        .filter(m => m)
      
      payload = {
        verifications: selectedCrew.map(crew => ({
          crew_member_id: crew.crew_member_id,
          team_manager_id: crew.team_manager_id,
          status: manualStatus,
          details: `Manually marked as ${manualStatus.includes('valid') ? 'valid' : 'invalid'}`
        }))
      }
    } else {
      // Save automatic check results
      payload = { verifications }
    }
    
    const response = await adminService.bulkUpdateLicenseVerification(payload)
    
    // Update local state
    response.results.forEach(result => {
      if (result.success) {
        const crew = crewMembers.value.find(m => m.crew_member_id === result.crew_member_id)
        if (crew) {
          crew.license_verification_status = result.status
          crew.license_verification_date = result.date
          crew.license_verified_by = result.verified_by
          crew.license_verification_details = result.details
        }
      }
    })
    
    successMessage.value = t('admin.licenseChecker.saveSuccess', {
      success: response.success_count,
      failure: response.failure_count
    })
    
  } catch (error) {
    console.error('Failed to save verification:', error)
    saveError.value = t('admin.licenseChecker.saveError')
  } finally {
    saving.value = false
  }
}
```

**5. Load Verification Status on Mount**
```javascript
// Modify loadCrewMembers to include verification status
const loadCrewMembers = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await adminService.listAllCrewMembers()
    
    crewMembers.value = response.crew_members.map(crew => ({
      ...crew,
      // Keep existing verification status from DB
      // Add temporary UI state for new checks
      _licenseStatus: null,
      _licenseDetails: null,
      _checking: false
    }))
    
  } catch (err) {
    console.error('Failed to load crew members:', err)
    error.value = err.response?.data?.message || t('admin.licenseChecker.loadError')
  } finally {
    loading.value = false
  }
}
```

#### New UI Elements

**Bulk Actions Section** (modified):
```vue
<div class="bulk-actions-section">
  <div class="selection-info">
    <!-- Existing selection checkbox -->
  </div>

  <div class="action-buttons">
    <!-- Existing "Check Selected" button -->
    
    <!-- NEW: Mark as Valid -->
    <BaseButton
      variant="success"
      size="medium"
      :disabled="selectedCount === 0 || saving"
      :loading="saving"
      @click="markSelectedAsValid"
    >
      {{ $t('admin.licenseChecker.markAsValid') }}
    </BaseButton>
    
    <!-- NEW: Mark as Invalid -->
    <BaseButton
      variant="danger"
      size="medium"
      :disabled="selectedCount === 0 || saving"
      :loading="saving"
      @click="markSelectedAsInvalid"
    >
      {{ $t('admin.licenseChecker.markAsInvalid') }}
    </BaseButton>
    
    <!-- NEW: Save Results -->
    <BaseButton
      variant="primary"
      size="medium"
      :disabled="selectedCount === 0 || !hasUnsavedResults || saving"
      :loading="saving"
      @click="saveVerificationResults"
    >
      {{ $t('admin.licenseChecker.saveResults') }}
    </BaseButton>
    
    <!-- Existing "Clear Selection" button -->
  </div>
</div>
```

**Status Column** (modified):
```vue
<td>
  <!-- Show DB status if exists, otherwise show temporary check status -->
  <span v-if="crew.license_verification_status" class="status-badge" 
        :class="`status-${getVerificationStatusClass(crew.license_verification_status)}`">
    {{ getVerificationStatusLabel(crew.license_verification_status) }}
    <span class="verification-method">
      {{ crew.license_verification_status.includes('manually') ? '(Manual)' : '(Auto)' }}
    </span>
  </span>
  <span v-else-if="crew._licenseStatus" class="status-badge status-unsaved">
    {{ crew._licenseStatus === 'valid' ? '✓ Valid (Unsaved)' : '✗ Invalid (Unsaved)' }}
  </span>
  <span v-else class="status-badge status-unchecked">
    {{ $t('admin.licenseChecker.unchecked') }}
  </span>
</td>
```

**Details Column** (modified):
```vue
<td>
  <div class="details-cell">
    <!-- Show DB details if exists -->
    <div v-if="crew.license_verification_date">
      <div>{{ crew.license_verification_details || '-' }}</div>
      <div class="verification-meta">
        {{ formatDate(crew.license_verification_date) }}
      </div>
    </div>
    <!-- Show temporary check details -->
    <div v-else-if="crew._licenseDetails">
      {{ crew._licenseDetails }}
    </div>
    <div v-else>-</div>
  </div>
</td>
```

### CrewMemberList.vue Changes (Team Manager)

#### Modified Table Columns
Add verification status column:

```javascript
const tableColumns = computed(() => [
  // ... existing columns ...
  {
    key: 'license_verification',
    label: t('crew.list.licenseVerification'),
    sortable: true,
    width: '150px',
    responsive: 'hide-below-1024'
  },
  // ... existing columns ...
])
```

#### New Template Slot
```vue
<template #cell-license_verification="{ row }">
  <span v-if="row.license_verification_status" 
        class="badge"
        :class="getVerificationBadgeClass(row.license_verification_status)">
    {{ getVerificationLabel(row.license_verification_status) }}
  </span>
  <span v-else class="badge badge-unchecked">
    {{ $t('crew.list.notVerified') }}
  </span>
</template>
```

#### New Helper Methods
```javascript
const getVerificationBadgeClass = (status) => {
  if (!status) return 'badge-unchecked'
  if (status.includes('valid')) return 'badge-verified'
  return 'badge-invalid'
}

const getVerificationLabel = (status) => {
  if (!status) return t('crew.list.notVerified')
  if (status.includes('valid')) return t('crew.list.verified')
  return t('crew.list.invalid')
}
```

### Admin Service Updates

**File**: `frontend/src/services/adminService.js`

Add new methods:

```javascript
// Update single crew member license verification
async updateCrewMemberLicenseVerification(crewMemberId, teamManagerId, data) {
  const response = await apiClient.patch(
    `/admin/crew-members/${crewMemberId}/license-verification`,
    {
      team_manager_id: teamManagerId,
      ...data
    }
  )
  return response.data
}

// Bulk update license verifications
async bulkUpdateLicenseVerification(data) {
  const response = await apiClient.post(
    '/admin/crew-members/bulk-license-verification',
    data
  )
  return response.data
}
```

## API Routes

### CDK Stack Updates

**File**: `infrastructure/stacks/api_stack.py`

Add new routes:

```python
# Single crew member license verification
admin_update_license_verification = _lambda.Function(
    self, "AdminUpdateLicenseVerification",
    runtime=_lambda.Runtime.PYTHON_3_11,
    handler="admin_update_crew_member_license_verification.lambda_handler",
    code=_lambda.Code.from_asset("../functions/admin"),
    layers=[shared_layer],
    environment=env_vars,
    timeout=Duration.seconds(30)
)

api.root.add_resource("admin").add_resource("crew-members").add_resource("{crew_member_id}") \
    .add_resource("license-verification").add_method(
        "PATCH",
        _apigateway.LambdaIntegration(admin_update_license_verification),
        authorizer=authorizer
    )

# Bulk license verification
admin_bulk_license_verification = _lambda.Function(
    self, "AdminBulkLicenseVerification",
    runtime=_lambda.Runtime.PYTHON_3_11,
    handler="bulk_update_license_verification.lambda_handler",
    code=_lambda.Code.from_asset("../functions/admin"),
    layers=[shared_layer],
    environment=env_vars,
    timeout=Duration.seconds(60)  # Longer timeout for bulk operations
)

api.root.add_resource("admin").add_resource("crew-members") \
    .add_resource("bulk-license-verification").add_method(
        "POST",
        _apigateway.LambdaIntegration(admin_bulk_license_verification),
        authorizer=authorizer
    )
```

## Internationalization (i18n)

### English Translations

**File**: `frontend/src/locales/en.json`

```json
{
  "admin": {
    "licenseChecker": {
      "markAsValid": "Mark as Valid",
      "markAsInvalid": "Mark as Invalid",
      "saveResults": "Save Verification Results",
      "markValidTitle": "Mark Licenses as Valid",
      "markValidMessage": "Mark {count} selected crew member(s) as having valid licenses?",
      "markInvalidTitle": "Mark Licenses as Invalid",
      "markInvalidMessage": "Mark {count} selected crew member(s) as having invalid licenses?",
      "saveSuccess": "{success} verification(s) saved successfully. {failure} failed.",
      "saveError": "Failed to save verification results. Please try again.",
      "noResultsToSave": "No verification results to save. Please check licenses first.",
      "verificationStatus": "Verification Status",
      "verifiedValid": "Verified Valid",
      "verifiedInvalid": "Verified Invalid",
      "manuallyVerified": "Manually Verified",
      "autoVerified": "Auto Verified"
    }
  },
  "crew": {
    "list": {
      "licenseVerification": "License",
      "notVerified": "Not Verified",
      "verified": "Verified",
      "invalid": "Invalid"
    }
  }
}
```

### French Translations

**File**: `frontend/src/locales/fr.json`

```json
{
  "admin": {
    "licenseChecker": {
      "markAsValid": "Marquer comme Valide",
      "markAsInvalid": "Marquer comme Invalide",
      "saveResults": "Enregistrer les Résultats",
      "markValidTitle": "Marquer les Licences comme Valides",
      "markValidMessage": "Marquer {count} membre(s) d'équipage sélectionné(s) comme ayant des licences valides ?",
      "markInvalidTitle": "Marquer les Licences comme Invalides",
      "markInvalidMessage": "Marquer {count} membre(s) d'équipage sélectionné(s) comme ayant des licences invalides ?",
      "saveSuccess": "{success} vérification(s) enregistrée(s) avec succès. {failure} échouée(s).",
      "saveError": "Échec de l'enregistrement des résultats de vérification. Veuillez réessayer.",
      "noResultsToSave": "Aucun résultat de vérification à enregistrer. Veuillez d'abord vérifier les licences.",
      "verificationStatus": "Statut de Vérification",
      "verifiedValid": "Vérifié Valide",
      "verifiedInvalid": "Vérifié Invalide",
      "manuallyVerified": "Vérifié Manuellement",
      "autoVerified": "Vérifié Auto"
    }
  },
  "crew": {
    "list": {
      "licenseVerification": "Licence",
      "notVerified": "Non Vérifié",
      "verified": "Vérifié",
      "invalid": "Invalide"
    }
  }
}
```

## Error Handling

### Backend Error Responses

```python
# Validation error
{
    "statusCode": 400,
    "body": {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Invalid verification status",
            "details": {
                "status": "Must be one of: verified_valid, verified_invalid, manually_verified_valid, manually_verified_invalid"
            }
        }
    }
}

# Permission error
{
    "statusCode": 403,
    "body": {
        "error": {
            "code": "PERMISSION_DENIED",
            "message": "You do not have permission to verify crew member licenses"
        }
    }
}

# Not found error
{
    "statusCode": 404,
    "body": {
        "error": {
            "code": "NOT_FOUND",
            "message": "Crew member not found",
            "details": {
                "crew_member_id": "uuid"
            }
        }
    }
}
```

### Frontend Error Handling

```javascript
try {
  await bulkUpdateVerification(...)
} catch (error) {
  if (error.response?.status === 403) {
    errorMessage.value = t('errors.permissionDenied')
  } else if (error.response?.status === 404) {
    errorMessage.value = t('errors.crewMemberNotFound')
  } else if (error.response?.status === 400) {
    errorMessage.value = error.response.data.error.message
  } else {
    errorMessage.value = t('admin.licenseChecker.saveError')
  }
}
```

## Testing Strategy

### Backend Tests

**File**: `tests/integration/test_license_verification.py`

Test cases:
1. Update single crew member verification (success)
2. Update single crew member verification (not found)
3. Update single crew member verification (permission denied)
4. Bulk update verification (all success)
5. Bulk update verification (partial failure)
6. Bulk update verification (all failure)
7. Verification status persists after update
8. Verification date is set correctly
9. Verified by admin ID is recorded

### Frontend Tests

Manual testing checklist:
1. Load page - verification status from DB displayed
2. Check licenses - temporary status shown
3. Save results - status persisted to DB
4. Mark as valid - status saved immediately
5. Mark as invalid - status saved immediately
6. Selection persists through actions
7. Error handling - network errors
8. Error handling - permission errors
9. Team manager view - status displayed (read-only)
10. Filter by verification status

## Deployment Plan

### Phase 1: Backend
1. Add new Lambda functions
2. Update existing Lambda functions to include verification fields
3. Add API routes to CDK stack
4. Update permission matrix
5. Deploy backend
6. Test API endpoints

### Phase 2: Frontend
1. Update AdminLicenseChecker.vue
2. Update CrewMemberList.vue
3. Add i18n translations
4. Update admin service
5. Deploy frontend
6. Test UI functionality

### Phase 3: Validation
1. Test automatic verification + save
2. Test manual verification
3. Test team manager view
4. Test error handling
5. Test bulk operations
6. Verify data persistence

## Security Considerations

1. **Authorization**: Only admins can verify licenses
2. **Audit Trail**: Record who verified and when
3. **Input Validation**: Validate all inputs on backend
4. **Rate Limiting**: Consider rate limiting bulk operations
5. **Data Privacy**: Team managers see verification status but not admin details

## Performance Considerations

1. **Bulk Operations**: Batch size limited to 100 crew members
2. **Database Queries**: Single query to load all crew members with verification status
3. **UI Responsiveness**: Show progress during bulk operations
4. **Caching**: Consider caching verification status in frontend store

## Monitoring and Logging

1. **CloudWatch Logs**: Log all verification operations
2. **Metrics**: Track verification success/failure rates
3. **Alerts**: Alert on high failure rates
4. **Audit**: Log admin actions for compliance

## Future Enhancements (Out of Scope)

1. Verification history tracking
2. Automatic re-verification after time period
3. Email notifications for verification status changes
4. Verification approval workflow
5. Integration with FFAviron API (if available)
6. Verification required phase (block payments)

## Correctness Properties

### Property 1: Verification Status Persistence
**Validates: Requirements US-1, US-2, US-3**

For any crew member with a saved verification status:
- The status must persist after page refresh
- The status must be one of the allowed values
- The verification date must be set
- The verified by admin ID must be set

### Property 2: Selection Persistence
**Validates: Requirements US-7**

For any bulk operation (check, mark valid, mark invalid):
- Selected crew members remain selected after operation
- Only selected crew members are affected by save operation
- Selection can be cleared manually

### Property 3: Error Handling
**Validates: Requirements US-6**

For any verification operation that fails:
- Error message is displayed to user
- Verification status remains unchanged in database
- UI state reflects database state (not temporary state)
- User can retry the operation

### Property 4: Authorization
**Validates: Requirements FR-3**

For any verification operation:
- Only admins can modify verification status
- Team managers can view but not modify
- Permission checks are enforced on backend
- Unauthorized attempts return 403 error

### Property 5: Data Integrity
**Validates: Requirements NFR-3**

For any verification update:
- Status, date, and verified_by are set atomically
- Partial updates are not allowed
- Bulk operations handle failures gracefully
- Database state is consistent after operation
