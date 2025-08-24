#!/bin/bash
set -euo pipefail

# ==============================
# Azure Cosmos DB Setup Script
# ==============================

# Variables (pass as ENV or override when running)
RESOURCE_GROUP=${RESOURCE_GROUP:-"graphql-api-rg"}
LOCATION=${LOCATION:-"eastus"}
COSMOS_ACCOUNT=${COSMOS_ACCOUNT:-"pavi2003420251"}
DATABASE_NAME=${DATABASE_NAME:-"ProjectsDB"}
CONTAINER_NAME=${CONTAINER_NAME:-"projects"}
PARTITION_KEY=${PARTITION_KEY:-"/id"}
THROUGHPUT=${THROUGHPUT:-400}
ENV_FILE=${ENV_FILE:-"../app/.env"}



# Create Resource Group
echo "Creating resource group: $RESOURCE_GROUP in $LOCATION"
az group create --name "$RESOURCE_GROUP" --location "$LOCATION"





# Create Cosmos DB Account
echo "Creating Cosmos DB account: $COSMOS_ACCOUNT"
az cosmosdb create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$COSMOS_ACCOUNT" \
  --kind GlobalDocumentDB \
  --default-consistency-level Eventual \
  --locations regionName=centralus  failoverPriority=0 isZoneRedundant=false 

# Get Endpoint
COSMOS_ENDPOINT=$(az cosmosdb show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$COSMOS_ACCOUNT" \
  --query documentEndpoint \
  --output tsv)

# Get Primary Key
COSMOS_KEY=$(az cosmosdb keys list \
  --resource-group "$RESOURCE_GROUP" \
  --name "$COSMOS_ACCOUNT" \
  --query primaryMasterKey \
  --output tsv)

echo "Cosmos DB endpoint: $COSMOS_ENDPOINT"
echo "Cosmos DB primary key: $COSMOS_KEY"

# Save credentials to .env
echo "Writing credentials to $ENV_FILE"
cat > "$ENV_FILE" <<EOF
COSMOS_URL=$COSMOS_ENDPOINT
COSMOS_KEY=$COSMOS_KEY
COSMOS_DB=$DATABASE_NAME
COSMOS_CONTAINER=$CONTAINER_NAME
EOF

# Create Database
echo "Creating database: $DATABASE_NAME"
az cosmosdb sql database create \
  --account-name "$COSMOS_ACCOUNT" \
  --name "$DATABASE_NAME" \
  --throughput "$THROUGHPUT" \
  --resource-group "$RESOURCE_GROUP"

# Create Container
echo "Creating container: $CONTAINER_NAME"
az cosmosdb sql container create \
  --account-name "$COSMOS_ACCOUNT" \
  --database-name "$DATABASE_NAME" \
  --name "$CONTAINER_NAME" \
  --partition-key-path "$PARTITION_KEY" \
  --throughput "$THROUGHPUT" \
  --resource-group "$RESOURCE_GROUP"

echo "Cosmos DB setup completed successfully!"
echo "Credentials stored in $ENV_FILE"
