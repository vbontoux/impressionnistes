#!/bin/bash
# Build Lambda layer with dependencies and shared code

set -e

echo "Building Lambda layer..."

# Clean previous build
rm -rf layer/python
mkdir -p layer/python

# Install dependencies
echo "Installing dependencies..."
pip3 install -r shared/requirements.txt -t layer/python --quiet

# Copy shared code (excluding __init__.py to avoid relative import issues)
echo "Copying shared code..."
for file in shared/*.py; do
  if [[ $(basename "$file") != "__init__.py" ]]; then
    cp "$file" layer/python/
  fi
done

echo "✓ Lambda layer built successfully at functions/layer/"
echo "  Dependencies + shared code are in layer/python/"
