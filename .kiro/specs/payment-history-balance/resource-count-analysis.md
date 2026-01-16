# CloudFormation Resource Count Analysis

## Current State (Dev Environment)

```
Stack Name                        Resources
─────────────────────────────────────────────
ImpressionnistesSecrets-dev            5
ImpressionnistesApi-dev              100
ImpressionnistesMonitoring-dev         1
ImpressionnistesAuth-dev              15
ImpressionnistesDatabase-dev           9
─────────────────────────────────────────────
TOTAL                                130
LIMIT                                500
REMAINING                            370
```

## New Resources for Payment History Feature

### Backend Lambda Functions (4 new functions)

Each Lambda function creates approximately 4-5 resources:
- Lambda Function
- Lambda Permission (API Gateway invoke)
- CloudWatch Log Group
- IAM Role (if not shared)
- IAM Policy attachments

**New Lambda Functions:**
1. `list_payments` - List payments for team manager
2. `get_payment_summary` - Get payment summary + outstanding balance
3. `list_all_payments` (admin) - List all payments
4. `get_payment_analytics` (admin) - Get payment analytics
5. `get_payment_invoice` - Generate PDF invoice

**Estimated resources per Lambda:** 4-5
**Total Lambda resources:** 5 functions × 4.5 avg = **~23 resources**

### API Gateway Routes (5 new routes)

Each API Gateway route creates approximately 2-3 resources:
- API Gateway Route
- API Gateway Integration
- API Gateway Integration Response (optional)

**New Routes:**
1. `GET /payments` - List payments
2. `GET /payments/summary` - Payment summary
3. `GET /payments/{payment_id}/invoice` - Download invoice PDF
4. `GET /admin/payments` - Admin list all payments
5. `GET /admin/payments/analytics` - Admin analytics

**Estimated resources per route:** 2-3
**Total API Gateway resources:** 5 routes × 2.5 avg = **~13 resources**

### IAM Permissions (minimal)

- Shared IAM role for Lambda functions (if not already shared)
- DynamoDB read permissions (already exists)
- CloudWatch Logs permissions (already exists)

**Estimated IAM resources:** **~2 resources** (if new role needed)

### Total New Resources

```
Component                    Resources
─────────────────────────────────────────
Lambda Functions                  ~23
API Gateway Routes                ~13
IAM Permissions                    ~2
─────────────────────────────────────────
TOTAL NEW RESOURCES               ~38
```

## Projected Total After Implementation

```
Current Resources:     130
New Resources:        +38
─────────────────────────────
Projected Total:       168
Limit:                 500
Remaining:             332
```

## Conclusion

✅ **SAFE TO PROCEED**

The payment history feature will add approximately **38 new CloudFormation resources**, bringing the total from **130 to ~168 resources**.

This leaves **332 resources remaining** (66% of the 500 limit), providing ample headroom for future features.

## Notes

- Resource count is conservative estimate (actual may be slightly lower if IAM roles are shared)
- Each environment (dev/prod) has separate stacks, so this applies per environment
- The 500 resource limit is per CloudFormation stack, not per account
- ImpressionnistesApi-dev stack currently has 100 resources and will grow to ~138 resources
- This is well within safe operating limits
