#!/bin/bash

# Database configuration
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/bankstatements"

# Print confirmation
echo "Environment variables set:"
echo "DATABASE_URL=$DATABASE_URL"

# Run the command passed as arguments
if [ $# -gt 0 ]; then
    exec "$@"
fi
