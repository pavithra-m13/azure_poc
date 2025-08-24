#!/bin/bash
set -e

# Path to .env file (change this if needed)
ENV_FILE="/mnt/c/mseone_poc/app/.env"

# Load environment variables from .env file
if [ -f "$ENV_FILE" ]; then
  export $(grep -v '^#' "$ENV_FILE" | xargs)
else
  echo ".env file not found at $ENV_FILE!"
  exit 1
fi


# Step 2: Create Azure Container Registry (skip if exists)
echo "2. Checking Azure Container Registry..."
if az acr show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP_NAME &>/dev/null; then
  echo "ACR '$REGISTRY_NAME' already exists. Skipping creation."
else
  echo "ACR '$REGISTRY_NAME' not found. Creating..."
  az acr create --resource-group $RESOURCE_GROUP_NAME --name $REGISTRY_NAME --sku Basic --admin-enabled true
fi
# Step 3: Get ACR login server
echo "3. Getting ACR login server..."
LOGIN_SERVER=$(az acr show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP_NAME --query loginServer --output tsv)
echo "Login Server: $LOGIN_SERVER"

# Step 4: Build and push Docker image
echo "4. Building and pushing Docker image..."

IMAGE_NAME="$LOGIN_SERVER/my-graphql-api:latest"

if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "$IMAGE_NAME"; then
    echo "Image $IMAGE_NAME already exists locally, skipping build..."
else
    echo "Building image..."
    docker build -t $IMAGE_NAME -f ../app/Dockerfile ../app
fi

echo "Pushing image to registry..."
# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP_NAME --query passwords[0].value --output tsv)

# Log in explicitly
echo $ACR_PASSWORD | docker login $LOGIN_SERVER -u $ACR_USERNAME --password-stdin

# Push image
docker push $IMAGE_NAME


# Step 6: Deploy to Azure Container Instance
echo "6. Deploying to Azure Container Instance..."
az container create \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $CONTAINER_GROUP_NAME \
    --image $IMAGE_NAME\
    --registry-login-server $LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --dns-name-label $CONTAINER_GROUP_NAME \
    --ports 8000 \
    --cpu 1 \
    --memory 1 \
    --os-type Linux \
    --environment-variables \
        COSMOS_URL=$COSMOS_URL \
        COSMOS_KEY=$COSMOS_KEY \
        COSMOS_DB=$COSMOS_DB \
        COSMOS_CONTAINER=$COSMOS_CONTAINER \
        AZURE_AD_TENANT_ID=$AZURE_AD_TENANT_ID \
        AZURE_AD_CLIENT_ID=$AZURE_AD_CLIENT_ID \
        AZURE_AD_SCOPE=$AZURE_AD_SCOPE \
    --restart-policy Always

# Step 7: Get container details
echo "7. Getting container details..."
FQDN=$(az container show --resource-group $RESOURCE_GROUP_NAME --name $CONTAINER_GROUP_NAME --query ipAddress.fqdn --output tsv)
IP_ADDRESS=$(az container show --resource-group $RESOURCE_GROUP_NAME --name $CONTAINER_GROUP_NAME --query ipAddress.ip --output tsv)

echo ""
echo "=== Deployment Complete ==="
echo "Container FQDN: http://$FQDN:8000"
echo "Container IP: http://$IP_ADDRESS:8000"
echo "GraphQL Endpoint: http://$FQDN:8000/graphql"
echo "Health Check: http://$FQDN:8000/health"
echo ""
echo "To check logs: az container logs --resource-group $RESOURCE_GROUP_NAME --name $CONTAINER_GROUP_NAME"
echo "To delete resources: az group delete --name $RESOURCE_GROUP_NAME --yes --no-wait"
