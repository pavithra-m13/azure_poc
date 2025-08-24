#!/bin/bash
set -euo pipefail

# Path to the .env file inside app directory
ENV_FILE="../app/.env"

# Load env vars from .env if it exists
if [ -f "$ENV_FILE" ]; then
  export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Request token from Azure AD
RESPONSE=$(curl -s -X POST "https://login.microsoftonline.com/${AZURE_AD_TENANT_ID}/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=${AZURE_AD_CLIENT_ID}" \
  -d "client_secret=${AZURE_AD_CLIENT_SECRET}" \
  -d "scope=${AZURE_AD_SCOPE}/.default" \
  -d "grant_type=client_credentials")

# Extract access token
ACCESS_TOKEN=$(echo "$RESPONSE" | jq -r '.access_token')

echo "Full Response: $RESPONSE"
echo "Access Token: $ACCESS_TOKEN"

# Save token to .env (overwrite or append)
if grep -q "^AZURE_AD_ACCESS_TOKEN=" "$ENV_FILE"; then
  # Update existing line
  sed -i "s|^AZURE_AD_ACCESS_TOKEN=.*|AZURE_AD_ACCESS_TOKEN=${ACCESS_TOKEN}|" "$ENV_FILE"
else
  # Append new variable
  echo "AZURE_AD_ACCESS_TOKEN=${ACCESS_TOKEN}" >> "$ENV_FILE"
fi
