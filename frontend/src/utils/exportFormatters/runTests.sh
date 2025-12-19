#!/bin/bash
# Run all export formatter tests

echo "Running Export Formatter Tests..."
echo "=================================="
echo ""

# Run crew members formatter tests
echo "1. Crew Members Formatter Tests"
echo "--------------------------------"
node crewMembersFormatter.test.js
if [ $? -ne 0 ]; then
  echo "❌ Crew Members tests failed"
  exit 1
fi
echo ""

# Run boat registrations formatter tests
echo "2. Boat Registrations Formatter Tests"
echo "--------------------------------------"
node boatRegistrationsFormatter.test.js
if [ $? -ne 0 ]; then
  echo "❌ Boat Registrations tests failed"
  exit 1
fi
echo ""

# Run crew timer formatter tests
echo "3. CrewTimer Formatter Tests"
echo "----------------------------"
node crewTimerFormatter.test.js
if [ $? -ne 0 ]; then
  echo "❌ CrewTimer tests failed"
  exit 1
fi
echo ""

echo "=================================="
echo "✅ All export formatter tests passed!"
echo "=================================="
