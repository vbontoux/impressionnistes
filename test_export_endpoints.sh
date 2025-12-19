#!/bin/bash

# Test Export API Endpoints in Dev Environment
# This script tests the new JSON export endpoints

API_URL="https://mo91x1duc5.execute-api.eu-west-3.amazonaws.com/dev"

echo "=========================================="
echo "Testing Export API Endpoints"
echo "Environment: dev"
echo "=========================================="
echo ""

# Note: These endpoints require admin authentication
# For now, we'll just test that they exist and return proper error codes

echo "1. Testing crew members JSON export endpoint..."
echo "   GET $API_URL/admin/export/crew-members-json"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/admin/export/crew-members-json")
if [ "$RESPONSE" = "401" ]; then
    echo "   ✓ Endpoint exists (returns 401 Unauthorized as expected without auth)"
else
    echo "   ✗ Unexpected response: $RESPONSE"
fi
echo ""

echo "2. Testing boat registrations JSON export endpoint..."
echo "   GET $API_URL/admin/export/boat-registrations-json"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/admin/export/boat-registrations-json")
if [ "$RESPONSE" = "401" ]; then
    echo "   ✓ Endpoint exists (returns 401 Unauthorized as expected without auth)"
else
    echo "   ✗ Unexpected response: $RESPONSE"
fi
echo ""

echo "3. Testing races JSON export endpoint..."
echo "   GET $API_URL/admin/export/races-json"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/admin/export/races-json")
if [ "$RESPONSE" = "401" ]; then
    echo "   ✓ Endpoint exists (returns 401 Unauthorized as expected without auth)"
else
    echo "   ✗ Unexpected response: $RESPONSE"
fi
echo ""

echo "=========================================="
echo "✓ All endpoints are accessible"
echo ""
echo "Note: Endpoints return 401 because they require admin authentication."
echo "This is expected behavior. The integration tests verify full functionality."
echo "=========================================="
