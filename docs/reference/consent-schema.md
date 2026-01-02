# Consent Storage Schema

## Overview

This document describes the DynamoDB schema for storing user consent records as required by GDPR. Consent records provide proof that users have agreed to the Privacy Policy and Terms & Conditions.

## Table Design

**Table**: Same table as user data (single-table design)

**Access Pattern**: Query all consents for a user, or query specific consent type

## Schema

### Keys

**Partition Key (PK)**: `USER#{user_id}`

**Sort Key (SK)**: `CONSENT#{consent_type}#{timestamp}`

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `PK` | String | Yes | Partition key: `USER#{user_id}` |
| `SK` | String | Yes | Sort key: `CONSENT#{consent_type}#{timestamp}` |
| `user_id` | String | Yes | User identifier (UUID from Cognito) |
| `consent_type` | String | Yes | Type of consent: `privacy_policy` or `terms_conditions` |
| `consent_version` | String | Yes | Version of legal document (e.g., "1.0") |
| `consented` | Boolean | Yes | Always `true` for consent records |
| `consented_at` | String | Yes | ISO 8601 timestamp when consent was given |
| `ip_address` | String | No | IP address of user (for audit trail) |
| `created_at` | String | Yes | ISO 8601 timestamp when record was created |

## Consent Types

### privacy_policy

User has read and accepted the Privacy Policy.

**Example SK**: `CONSENT#PRIVACY#2025-01-02T10:00:00Z`

### terms_conditions

User has read and accepted the Terms & Conditions.

**Example SK**: `CONSENT#TERMS#2025-01-02T10:00:00Z`

## Example Records

### Privacy Policy Consent

```json
{
  "PK": "USER#123e4567-e89b-12d3-a456-426614174000",
  "SK": "CONSENT#PRIVACY#2025-01-02T10:00:00.000Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "consent_type": "privacy_policy",
  "consent_version": "1.0",
  "consented": true,
  "consented_at": "2025-01-02T10:00:00.000Z",
  "ip_address": "192.168.1.1",
  "created_at": "2025-01-02T10:00:00.000Z"
}
```

### Terms & Conditions Consent

```json
{
  "PK": "USER#123e4567-e89b-12d3-a456-426614174000",
  "SK": "CONSENT#TERMS#2025-01-02T10:00:00.000Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "consent_type": "terms_conditions",
  "consent_version": "1.0",
  "consented": true,
  "consented_at": "2025-01-02T10:00:00.000Z",
  "ip_address": "192.168.1.1",
  "created_at": "2025-01-02T10:00:00.000Z"
}
```

## Query Patterns

### Get All Consents for a User

```python
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('your-table-name')

response = table.query(
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
    ExpressionAttributeValues={
        ':pk': f'USER#{user_id}',
        ':sk': 'CONSENT#'
    }
)

consents = response['Items']
```

### Get Privacy Policy Consents

```python
response = table.query(
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
    ExpressionAttributeValues={
        ':pk': f'USER#{user_id}',
        ':sk': 'CONSENT#PRIVACY#'
    }
)

privacy_consents = response['Items']
```

### Get Terms & Conditions Consents

```python
response = table.query(
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
    ExpressionAttributeValues={
        ':pk': f'USER#{user_id}',
        ':sk': 'CONSENT#TERMS#'
    }
)

terms_consents = response['Items']
```

### Get Latest Consent for Each Type

```python
# Get all consents
response = table.query(
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
    ExpressionAttributeValues={
        ':pk': f'USER#{user_id}',
        ':sk': 'CONSENT#'
    },
    ScanIndexForward=False  # Sort descending (newest first)
)

# Group by consent type and take first (latest) of each
latest_consents = {}
for item in response['Items']:
    consent_type = item['consent_type']
    if consent_type not in latest_consents:
        latest_consents[consent_type] = item
```

## Record Creation

### When Records Are Created

Consent records are created during user registration:

1. User submits registration form with consent checkboxes checked
2. Backend validates consent fields are `true`
3. Backend creates Cognito user
4. Backend stores two consent records in DynamoDB:
   - One for Privacy Policy
   - One for Terms & Conditions

### Code Location

`functions/auth/register.py`

### Creation Logic

```python
from datetime import datetime

def create_consent_records(user_id, consent_version, ip_address):
    """Create consent records for a new user."""
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Privacy Policy consent
    privacy_consent = {
        'PK': f'USER#{user_id}',
        'SK': f'CONSENT#PRIVACY#{timestamp}',
        'user_id': user_id,
        'consent_type': 'privacy_policy',
        'consent_version': consent_version,
        'consented': True,
        'consented_at': timestamp,
        'ip_address': ip_address,
        'created_at': timestamp
    }
    table.put_item(Item=privacy_consent)
    
    # Terms & Conditions consent
    terms_consent = {
        'PK': f'USER#{user_id}',
        'SK': f'CONSENT#TERMS#{timestamp}',
        'user_id': user_id,
        'consent_type': 'terms_conditions',
        'consent_version': consent_version,
        'consented': True,
        'consented_at': timestamp,
        'ip_address': ip_address,
        'created_at': timestamp
    }
    table.put_item(Item=terms_consent)
```

## Immutability

**Important**: Consent records are **immutable** (never updated).

### Why Immutable?

- Provides audit trail of consent history
- Proves when consent was given
- Allows tracking consent for different document versions
- Meets GDPR requirement to prove consent

### Re-Consent

If legal documents are updated and users need to re-consent:

1. Increment `consent_version` (e.g., "1.0" → "2.0")
2. Prompt users to review and accept new version
3. Create new consent records with new version
4. Old consent records remain for audit trail

### Multiple Consents

A user may have multiple consent records for the same type:
- Different timestamps (re-consent events)
- Different versions (document updates)
- All records preserved for audit trail

## IP Address Capture

### Purpose

IP address provides additional proof of consent for audit trail.

### Source

Extracted from API Gateway request context:

```python
ip_address = event.get('requestContext', {}).get('identity', {}).get('sourceIp')
```

### Privacy Considerations

- IP addresses are personal data under GDPR
- Subject to same protections as other personal data
- Included in data export requests
- Deleted when user exercises Right to Erasure

### Optional

System functions without IP address if not available (e.g., in testing).

## Consent Versions

### Current Version

**Version**: `1.0`

**Date**: January 2, 2026

### Version Tracking

- Version stored in each consent record
- Allows tracking which version user consented to
- Enables re-consent requests if documents change materially

### Updating Versions

When legal documents are updated:

1. Review changes with legal counsel
2. Determine if re-consent is required
3. If yes, increment version number
4. Update `consent_version` in registration code
5. Implement re-consent flow for existing users (Phase 2)

## Data Retention

### Retention Period

**Duration**: Duration of processing plus 3 years

**Reason**: Proof of consent must be retained to demonstrate compliance

### Deletion

Consent records are deleted when:
- User exercises Right to Erasure (account deletion)
- Retention period expires
- Legal requirement to delete

## Security

### Encryption

- Data encrypted at rest in DynamoDB
- Data encrypted in transit (HTTPS)

### Access Control

- Only authenticated users can access their own consent records
- Admin access requires appropriate IAM permissions
- Audit logging enabled for access

## Compliance

### GDPR Requirements

This schema meets GDPR requirements for:
- **Article 7**: Proof of consent
- **Article 30**: Records of processing activities
- **Article 5**: Data accuracy and integrity

### Audit Trail

Consent records provide audit trail showing:
- When consent was given
- What version was consented to
- Where consent was given (IP address)
- That consent was freely given

## Related Documentation

- [GDPR Compliance Guide](../guides/GDPR_COMPLIANCE.md)
- [API Endpoints](./api-endpoints.md#post-authregister)
- [Project Structure](./project-structure.md#gdpr-compliance)
- [Requirements](../../.kiro/specs/gdpr-compliance/requirements.md)
- [Design](../../.kiro/specs/gdpr-compliance/design.md)

---

**Last Updated**: January 2, 2026

**Schema Version**: 1.0
