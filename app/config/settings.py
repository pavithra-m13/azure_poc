import os
from dotenv import load_dotenv

# Load env variables from .env file
load_dotenv()

# Cosmos DB Configuration
COSMOS_URL = os.getenv("COSMOS_URL")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = os.getenv("COSMOS_DB")
CONTAINER_NAME = os.getenv("COSMOS_CONTAINER")

# Azure AD Configuration
TENANT_ID = os.getenv("AZURE_AD_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_AD_CLIENT_ID")
SCOPE = os.getenv("AZURE_AD_SCOPE")

# JWT Configuration
ISSUER = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"
AUDIENCE = os.getenv("AZURE_AD_SCOPE")
JWKS_URL = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"