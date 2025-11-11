#!/bin/bash
# Pre-commit safety check for credentials

if git diff --cached --name-only | grep -E "(credentials\.json|token\.json|\.env$)"; then
    echo "ERROR: Attempting to commit sensitive files!"
    echo "Files blocked: credentials.json, token.json, .env"
    exit 1
fi
